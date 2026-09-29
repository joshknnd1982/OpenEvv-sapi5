#!/usr/bin/env python3
"""The first proof: sounds the German module has not, in Hindi.

Hindi tells a t made on the teeth from one made with the tip of the tongue
curled back, each of them plain, aspirated, voiced and breathy voiced. German
has one t and one d. The words below are said by the Hindi pack through the
German module, and measured:

  the voice onset time of each stop, against Lisker and Abramson's (1964)
  measurements of Hindi and against eSpeak NG's rendering of the same word;

  the second and third formants where the voice begins after the stop, where
  a retroflex shows itself: its third formant is low and close to the second
  (Stevens and Blumstein 1975), where a dental's is high.

    python engine/accent/proof_hindi.py <pack folder> [report.md]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify  # noqa: E402
from say import Pack  # noqa: E402

# word, its sounds in the IPA, the stop that is measured, Lisker and Abramson's voice onset time
WORDS = [
    ('ताल', 't̪aːl', 't̪', 15),
    ('टाल', 'ʈaːl', 'ʈ', 9),
    ('थाल', 't̪ʰaːl', 't̪ʰ', 67),
    ('ठाठ', 'ʈʰaːʈʰ', 'ʈʰ', 60),
    ('दाल', 'd̪aːl', 'd̪', -87),
    ('डाल', 'ɖaːl', 'ɖ', -76),
    ('पाल', 'paːl', 'p', 13),
    ('फाल', 'pʰaːl', 'pʰ', 70),
    ('काल', 'kaːl', 'k', 18),
    ('खाल', 'kʰaːl', 'kʰ', 92),
]


def measure_word(pack, word, keep=None):
    r = pack.say(word + '.', keep=keep)
    tr = [t for t in r.trace if t['name'] not in ('#', '-')]
    if len(tr) < 2:
        return None
    stop, vowel = tr[0], tr[1]
    rel, voice = verify.frame_release(r.frames, stop, vowel)
    out = {'sound': stop['sound'], 'phone': stop['name']}
    out['asked_vot'] = (voice - rel) if rel is not None and voice is not None else None
    fr = verify.frames_between(r.frames, vowel['out_a'], vowel['out_b'])
    voiced = [f for f in fr if f['av'] >= 30]
    if voiced:
        out['asked_onset'] = [voiced[0]['f1'], voiced[0]['f2'], voiced[0]['f3'], voiced[0]['f4']]
        mid = voiced[len(voiced) // 2]
        out['asked_mid'] = [mid['f1'], mid['f2'], mid['f3'], mid['f4']]
    # and in the sound
    x = r.samples.astype(np.float64)
    a, v = verify.release_and_voice(x, r.rate, 0.0, min(len(x) / float(r.rate), 0.45))
    out['heard_vot'] = (v - a) * 1000 if a is not None and v is not None else None
    if v is not None:
        out['heard_onset'] = verify.formants_at(x, r.rate, v + 0.015)
        out['heard_mid'] = verify.formants_at(x, r.rate, v + 0.080)
    return out


def measure_espeak(voice, word):
    x, rate = verify.espeak_wav(voice, word + '.')
    x, rate = verify.at_rate(x, rate)
    a, v = verify.release_and_voice(x, rate, 0.0, min(len(x) / float(rate), 0.45))
    out = {}
    out['heard_vot'] = (v - a) * 1000 if a is not None and v is not None else None
    if v is not None:
        out['heard_onset'] = verify.formants_at(x, rate, v + 0.015)
        out['heard_mid'] = verify.formants_at(x, rate, v + 0.080)
    return out


def fmt(v, what='%d'):
    if v is None:
        return '-'
    if isinstance(v, (list, tuple)):
        return ' '.join('%d' % round(x) for x in v[:3])
    return what % round(v)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    pack = Pack(argv[0])
    rows = []
    for word, ipa, stop, published in WORDS:
        ours = measure_word(pack, word)
        theirs = measure_espeak(pack.voice, word)
        rows.append((word, ipa, stop, published, ours, theirs))
    lines = []
    lines.append('| word | sounds | stop | sound | VOT published | VOT asked | VOT heard | VOT eSpeak NG | '
                 'F1 F2 F3 at voice onset, asked | heard | eSpeak NG |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for word, ipa, stop, published, o, e in rows:
        if o is None:
            continue
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            word, ipa, stop, o['sound'], published, fmt(o.get('asked_vot')), fmt(o.get('heard_vot')),
            fmt(e.get('heard_vot')), fmt(o.get('asked_onset')), fmt(o.get('heard_onset')),
            fmt(e.get('heard_onset'))))
    text = '\n'.join(lines)
    print(text)
    if len(argv) > 1:
        with open(argv[1], 'w', encoding='utf-8', newline='\n') as f:
            f.write(text + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
