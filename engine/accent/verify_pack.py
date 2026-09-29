#!/usr/bin/env python3
"""Measures the sounds of a language pack, one by one.

Every phoneme of the language that the map gives a sound of its own is said
twice, by the pack (eSpeak NG's reading, the map, the module) and by eSpeak
NG's own synthesiser, in the same small word: a consonant before the
language's open vowel, a vowel after p. Both sounds are measured the same
way (engine/accent/verify.py), and the numbers are set beside what the sound
was meant to be:

  a vowel        its first three formants in the middle of it, and how long
                 the voice lasts
  a stop         the time from its release to the voice, and the second and
                 third formants where the voice begins, which is where the
                 place of a consonant is heard
  a fricative    how long the noise lasts and where its weight lies
                 (the centre of gravity of its spectrum)
  anything else  the formants where the vowel begins

    python engine/accent/verify_pack.py <pack folder> [report.md] [--all]

--all measures every phoneme of the language's tables, not only those the map
has given a sound.
"""
import json
import os
import re
import sys
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import espeak_phonemes as EP  # noqa: E402
import sounds as S  # noqa: E402
import verify  # noqa: E402
from say import Pack  # noqa: E402


def read_map(path, every=False):
    """The phonemes of a map's own tables: (table, name, phones, ipa). Those
    the language was not seen to use are left out unless all are wanted."""
    out = []
    table = None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        m = re.match(r'# eSpeak NG phoneme table (\S+)', line)
        if m:
            table = m.group(1)
            continue
        if line.startswith('# by IPA'):
            table = None
        if table is None or not line.startswith('@'):
            continue
        key, _, rest = line.partition(' ')
        phones, _, note = rest.partition('  # ')
        if '(not met)' in note and not every:
            continue
        out.append((table, key[1:].split(':', 1)[1], phones.split(), note.replace('(not met)', '').strip()))
    return out


def open_vowel(entries):
    """The name of the language's most open vowel in its first table."""
    best, how = None, None
    for table, name, phones, ipa in entries:
        us = EP.units(ipa)
        if len(us) != 1 or not us[0].vowel or us[0].nasal:
            continue
        h = EP.VOWELS[us[0].base][0]
        score = (h, 1 if us[0].long else 0)
        if how is None or score > how:
            best, how = (table, name, ipa), score
    return best


def centre_of_gravity(x, rate, t0, t1):
    a, b = int(t0 * rate), int(t1 * rate)
    if b - a < 32:
        return 0.0
    seg = x[a:b] * np.hanning(b - a)
    spec = np.abs(np.fft.rfft(seg)) ** 2
    f = np.fft.rfftfreq(len(seg), 1.0 / rate)
    keep = f > 500
    if spec[keep].sum() <= 0:
        return 0.0
    return float((f[keep] * spec[keep]).sum() / spec[keep].sum())


def voiced_span(x, rate, after=0.0):
    v, dt, win = verify.voiced_track(x, rate)
    start = None
    best = (0, 0)
    for i, b in enumerate(v):
        t = i * dt + win / 2
        if t < after:
            continue
        if b and start is None:
            start = t
        elif not b and start is not None:
            if t - start > best[1] - best[0]:
                best = (start, t)
            start = None
    if start is not None and len(v) * dt - start > best[1] - best[0]:
        best = (start, len(v) * dt)
    return best


def measure(x, rate, vowel):
    """What a small word sounds like: a consonant and a vowel, or a vowel
    after p."""
    out = {}
    x = x.astype(np.float64)
    first, voice = verify.release_and_voice(x, rate, 0.0, min(len(x) / float(rate), 0.6))
    v0, v1 = voiced_span(x, rate, after=(first or 0.0))
    if v1 - v0 < 0.03:
        return out
    out['voiced_ms'] = int(round((v1 - v0) * 1000))
    if first is not None and voice is not None:
        out['lag_ms'] = int(round((voice - first) * 1000))
        if voice - first > 0.015:
            out['noise_hz'] = int(round(centre_of_gravity(x, rate, first, voice)))
    onset = voice if voice is not None and voice >= v0 - 0.01 else v0
    out['onset'] = [int(round(f)) for f in verify.formants_at(x, rate, onset + 0.015)[:3]]
    mid = (v0 + v1) / 2.0 if vowel else min(v1 - 0.03, onset + 0.09)
    out['mid'] = [int(round(f)) for f in verify.formants_at(x, rate, mid)[:3]]
    return out


def kind_of(ipa):
    us = EP.units(ipa)
    if not us:
        return 'other'
    if all(u.vowel for u in us):
        return 'vowel'
    f = EP.cons_features(us[0].base)
    if f is None:
        return 'other'
    if f[1] in (EP.STOP, EP.IMPL, EP.CLICK):
        return 'stop'
    if f[1] == EP.AFFR:
        return 'affricate'
    if f[1] in (EP.FRIC, EP.SIBF, EP.LATFRIC):
        return 'fricative'
    return 'sonorant'


def target_of(designer, ipa):
    """What the sound was meant to be, as far as it is a number."""
    us = EP.units(ipa)
    out = {}
    if not us:
        return out
    u = us[0]
    if u.vowel and len(us) == 1:
        t, published = designer.vowel_target(u.base, u.long)
        if t:
            out['mid'] = [int(round(v)) for v in t]
            out['from'] = 'the language' if published else 'the chart'
        return out
    f = EP.cons_features(u.base)
    if f and f[1] == EP.STOP and not f[2]:
        aspirated = 'ʰ' in u.mods
        key = unicodedata.normalize('NFD', u.base + ('ʰ' if aspirated else ''))
        v = designer.lang.vot.get(key)
        if v is not None:
            out['lag_ms'] = int(round(v))
            out['from'] = 'the language'
        else:
            out['lag_ms'] = (S.VOT_ASPIRATED if aspirated else S.VOT_PLAIN)[f[0]]
            out['from'] = 'the kind of stop'
    if f and f[0] in S.LOCUS and f[1] in (EP.STOP, EP.NAS, EP.LAT, EP.AFFR):
        out['locus'] = [int(round(v * designer.c.scale)) for v in S.LOCUS[f[0]]]
    return out


def main(argv):
    every = '--all' in argv
    argv = [a for a in argv if not a.startswith('--')]
    if not argv:
        print(__doc__)
        return 2
    pack = Pack(argv[0])
    entries = read_map(pack.map, every)
    if not entries:
        print('the map has no tables of its own')
        return 1
    table = entries[0][0]
    a = open_vowel([e for e in entries if e[0] == table])
    if a is None:
        print('no open vowel found')
        return 1
    import prosody
    profile = prosody.load_profile(pack.tag)
    template = dict((v, k) for k, v in {'dede': 'dedx', 'itit': 'itix', 'eses': 'esex', 'esus': 'esux',
                                         'engb': 'engx', 'enus': 'enux', 'frfr': 'frfx'}.items()).get(
        pack.template, pack.template)
    designer = S.Designer(S.Chassis(pack.template, template),
                          S.Language(pack.tag, profile, [e[3] for e in entries]))
    rows = []
    seen = set()
    for t, name, phones, ipa in entries:
        if t != table or not ipa or ipa in seen:
            continue
        given = any('=' in p for p in phones)
        if not given and not every:
            continue
        kind = kind_of(ipa)
        if kind == 'other':
            continue
        seen.add(ipa)
        if kind == 'vowel':
            text = "[[p'%s]]" % name
        else:
            text = "[[%s'%s]]" % (name, a[1])
        try:
            w = pack.written(text, phonemes=True)
            r = pack.probe.speak('`vb65 `vf30 ' + w)
            ours = measure(r.samples, r.rate, kind == 'vowel')
            ex, erate = verify.espeak_wav(pack.voice, text)
            ex, erate = verify.at_rate(ex, erate)
            theirs = measure(ex, erate, kind == 'vowel')
        except Exception as e:  # one sound that cannot be said is not the end of the rest
            ours, theirs = {'error': str(e)[:60]}, {}
        rows.append(dict(ipa=ipa, name=name, kind=kind, phones=' '.join(phones), ours=ours, espeak=theirs,
                         target=target_of(designer, ipa)))
    lines = ['| sound | kind | said with | meant | OpenEVV | eSpeak NG |', '|---|---|---|---|---|---|']

    def show(m, kind):
        if not m:
            return '-'
        if 'error' in m:
            return m['error']
        bits = []
        if kind == 'vowel':
            if 'mid' in m:
                bits.append('F %s' % ' '.join(str(v) for v in m['mid']))
            if 'voiced_ms' in m:
                bits.append('%d ms' % m['voiced_ms'])
        else:
            if 'lag_ms' in m:
                bits.append('lag %d ms' % m['lag_ms'])
            if 'noise_hz' in m:
                bits.append('noise %d Hz' % m['noise_hz'])
            if 'onset' in m:
                bits.append('F at onset %s' % ' '.join(str(v) for v in m['onset']))
            if 'locus' in m:
                bits.append('F2 F3 locus %s' % ' '.join(str(v) for v in m['locus']))
        if 'from' in m:
            bits.append('(%s)' % m['from'])
        return ', '.join(bits) or '-'

    for r in rows:
        lines.append('| %s | %s | %s | %s | %s | %s |' % (r['ipa'], r['kind'], r['phones'],
                                                         show(r['target'], r['kind']),
                                                         show(r['ours'], r['kind']),
                                                         show(r['espeak'], r['kind'])))
    text = '\n'.join(lines)
    print(text)
    if len(argv) > 1:
        with open(argv[1], 'w', encoding='utf-8', newline='\n') as f:
            f.write(text + '\n')
        with open(os.path.splitext(argv[1])[0] + '.json', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
