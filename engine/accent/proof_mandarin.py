#!/usr/bin/env python3
"""The second proof: tone. Mandarin's four tones and its neutral tone, and
what the third tone becomes before another third tone.

Every syllable is said by the Mandarin pack through the German module, which
knows nothing of tone, and the pitch of what comes out is tracked in the
sound itself (autocorrelation, engine/accent/measure.py). eSpeak NG's own
rendering of the same text is tracked the same way.

Pitch is given in Chao's five levels, as the tones are in the literature:
the level is worked out from the hertz with the middle of the voice as 3 and
the range the language's map gives the voice (twelve semitones for Mandarin)
from 1 to 5. For eSpeak NG's voice, whose range nobody has said, the first
tone is taken to be 5 and the bottom of its third tone 1.

    python engine/accent/proof_mandarin.py <pack folder> [report.md]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure  # noqa: E402
import verify  # noqa: E402
from say import Pack  # noqa: E402

# text, what it is, the tones that are to be heard (Chao), syllable by syllable
TEXTS = [
    ('妈', 'mā, tone 1', ['55']),
    ('麻', 'má, tone 2', ['35']),
    ('马', 'mǎ, tone 3', ['214']),
    ('骂', 'mà, tone 4', ['51']),
    ('你好', 'nǐ hǎo: third tone before third', ['35', '214']),
    ('很好', 'hěn hǎo: third tone before third', ['35', '214']),
    ('老师', 'lǎo shī: third tone before first', ['21', '55']),
    ('妈妈', 'māma: neutral after first', ['55', '2']),
    ('爷爷', 'yéye: neutral after second', ['35', '3']),
    ('姐姐', 'jiějie: neutral after third', ['21', '4']),
    ('爸爸', 'bàba: neutral after fourth', ['51', '1']),
]

MIDDLE = [400, 427, 468, 533, 632, 786, 1025, 1394, 1966, 2851, 4221]


def middle_hz(vb):
    i = vb // 10
    w = (vb % 10) / 10.0
    lo, hi = MIDDLE[i], MIDDLE[min(10, i + 1)]
    return lo * (hi / float(lo)) ** w / 10.0


def chao(hz, mid, range_st):
    st = 12.0 * np.log2(hz / mid)
    return 3.0 + 4.0 * st / range_st


def contour(times, f0, t0, t1, n=5):
    """The pitch at n moments evenly through the voiced part of a stretch."""
    pts = [(t, f) for t, f in zip(times, f0) if t0 <= t <= t1 and f > 0]
    if len(pts) < 3:
        return []
    ts = np.array([p[0] for p in pts])
    fs = np.array([p[1] for p in pts])
    out = []
    for k in range(n):
        t = ts[0] + (ts[-1] - ts[0]) * k / (n - 1.0)
        out.append(float(np.interp(t, ts, fs)))
    return out


def syllables_of(trace):
    """The stretches of each syllable: from its first phone to its last."""
    out = []
    cur = None
    for t in trace:
        if t['name'] in ('#', '-'):
            continue
        if t['flags'] >= 0 and (t['flags'] & 1):
            cur = {'a': t['out_a'], 'b': t['out_b'], 'tone': t['tone'], 'nucleus': None}
            out.append(cur)
        elif cur is not None:
            cur['b'] = t['out_b']
        if cur is not None and t['flags'] >= 0 and (t['flags'] & 4):
            cur['nucleus'] = (t['out_a'], t['out_b'])
            cur['tone'] = t['tone']
    return out


def voiced_runs(times, f0, least=0.06):
    """Stretches of voice in eSpeak NG's sound, where no trace says which
    syllable is which."""
    runs = []
    start = None
    for t, f in zip(times, f0):
        if f > 0 and start is None:
            start = t
        elif f <= 0 and start is not None:
            if t - start >= least:
                runs.append((start, t))
            start = None
    if start is not None and times[-1] - start >= least:
        runs.append((start, times[-1]))
    return runs


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    pack = Pack(argv[0])
    mid = middle_hz(65)
    range_st = 12.0
    lines = ['| text | what | tones meant | tone said | pitch heard, Chao levels at five moments | '
             'hertz | eSpeak NG, Chao levels |', '|---|---|---|---|---|---|---|']
    worst = 0.0
    for text, what, want in TEXTS:
        r = pack.say(text + '。')
        x = r.samples.astype(np.float64)
        times, f0 = measure.track_f0(x, r.rate, window=0.025, fmin=55, fmax=300)
        syl = syllables_of(r.trace)
        ex, erate = verify.espeak_wav(pack.voice, text + '。')
        ex, erate = verify.at_rate(ex, erate)
        et, ef = measure.track_f0(ex, erate, window=0.025, fmin=55, fmax=300)
        runs = voiced_runs(et, ef)
        voiced = ef[ef > 0]
        etop = np.percentile(voiced, 95) if len(voiced) else 0
        ebot = np.percentile(voiced, 3) if len(voiced) else 0
        for i, s in enumerate(syl):
            # a syllable's voice goes on until the next syllable begins, or
            # until it stops: the engine lets the voice die away after the
            # last stretch it names
            until = syl[i + 1]['a'] if i + 1 < len(syl) else s['b'] + 150
            hz = contour(times, f0, s['a'] / 1000.0, until / 1000.0)
            levels = [chao(h, mid, range_st) for h in hz]
            theirs = ''
            if i < len(runs) and etop > ebot > 0:
                eh = contour(et, ef, runs[i][0], runs[i][1])
                span = 12.0 * np.log2(etop / ebot)
                theirs = ' '.join('%.1f' % (1.0 + 4.0 * 12.0 * np.log2(h / ebot) / span) for h in eh)
            meant = want[i] if i < len(want) else '?'
            lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                text if i == 0 else '', what if i == 0 else '', meant, s['tone'],
                ' '.join('%.1f' % v for v in levels), ' '.join('%d' % round(h) for h in hz), theirs))
    out = '\n'.join(lines)
    print(out)
    if len(argv) > 1:
        with open(argv[1], 'w', encoding='utf-8', newline='\n') as f:
            f.write(out + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
