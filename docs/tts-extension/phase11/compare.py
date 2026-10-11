# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 11's pilot, before and after: the legacy pack (harness/golden/, the golden of what ships) against
the master pack (the pilot's scratch golden), as measured.

    python docs/tts-extension/phase11/compare.py <scratch folder> <tag ...> [--md FILE]

Per pack: check A (A0 substituted, A1 silent, A2 checks passed), check B, CER, from check_language.py's
JSON (before_<tag>.json, after_<tag>.json in the scratch folder); the to_master counts (R21f); and which
sounds moved, measured in the sound: for each golden case, the phone the case is about (its first sound
after the context vowel: `'aCa`'s C, `t'Vta`'s V), F1 and F2 at its middle for a vowel or an approximant,
the noise centroid for a fricative, the VOT for a stop; a sound moved when one of them moved by more than
10 per cent (or 15 ms of VOT).
"""
import gzip
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GOLDEN = os.path.join(ROOT, 'docs', 'tts-extension', 'harness', 'golden')


def load(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def target(case):
    """The measured phone the case is about: the first phone after the first one (the context vowel)."""
    ph = [p for p in case['phones'] if p['cls'] != 'silence']
    return ph[1] if len(ph) > 1 else (ph[0] if ph else None)


def measures(p):
    m = p.get('meas') or {}
    out = {}
    if p['cls'] in ('vowel', 'approximant', 'nasal', 'lateral'):
        for k in ('F1_50_hz', 'F2_50_hz'):
            if m.get(k):
                out[k[:2]] = m[k]
    if p['cls'] == 'fricative' and m.get('centroid_hz'):
        out['centroid'] = m['centroid_hz']
    if m.get('vot_ms') is not None:
        out['VOT'] = m['vot_ms']
    return out


def moved(before, after):
    rows = []
    for cid, cb in before['cases'].items():
        ca = after['cases'].get(cid)
        if not ca or cid.startswith('x|'):
            continue
        pb, pa = target(cb), target(ca)
        if not pb or not pa:
            continue
        mb, ma = measures(pb), measures(pa)
        for k in sorted(set(mb) & set(ma)):
            d = ma[k] - mb[k]
            rel = 100.0 * d / mb[k] if mb[k] and k != 'VOT' else None
            if (k == 'VOT' and abs(d) > 15) or (rel is not None and abs(rel) > 10):
                rows.append((cid, pb.get('meant') or pb['name'], k, mb[k], ma[k], rel, d))
    return rows


def vot(g, cid):
    """The VOT measured in a case (its first stop with one), or None."""
    c = g['cases'].get(cid)
    for p in (c or {}).get('phones', []):
        if (p.get('meas') or {}).get('vot_ms') is not None:
            return p['meas']['vot_ms']
    return None


def main(argv):
    scratch = argv[0]
    md = argv[argv.index('--md') + 1] if '--md' in argv else None
    tags = [a for a in argv[1:] if not a.startswith('--') and a != md]
    lines = ['| Pack | Template | Check A before | Check A after | Check B before / after | CER before | CER after | '
             'Cases | Sounds moved (cases) | Largest moves |', '|---|---|---|---|---|---|---|---|---|---|']
    for tag in tags:
        b = json.load(open(os.path.join(scratch, 'before_%s.json' % tag), encoding='utf-8'))
        a = json.load(open(os.path.join(scratch, 'after_%s.json' % tag), encoding='utf-8'))
        gb = load(os.path.join(GOLDEN, '%s.json.gz' % tag))
        ga = load(os.path.join(scratch, 'golden', '%s.json.gz' % tag))
        frames_same = sum(1 for c in gb['cases'] if c in ga['cases'] and gb['cases'][c]['frames_sha256'] == ga['cases'][c]['frames_sha256'])
        rows = moved(gb, ga)
        cases = sorted(set(r[0] for r in rows))
        big = sorted(rows, key=lambda r: -abs(r[5] if r[5] is not None else r[6] * 2))[:3]

        def fa(s):
            x = s['a']
            return '%s (A0 %d, A1 %d silent, A2 %d/%d)' % ('pass' if x['passed'] else 'FAIL', x['substituted'],
                                                           x['a1_silent'], x['a2_ok'], x['a2_checks'])

        def fb(s):
            x = s['b']
            return '%s %d/%d' % ({True: 'pass', False: 'FAIL'}.get(x.get('passed'), 'too few'), x.get('in_range', 0),
                                 x.get('checks', 0))

        def cer(s):
            return '%.3f' % s['asr']['cer'] if s['asr'].get('cer') is not None else s['asr'].get('status', '-')
        lines.append('| %s | %s | %s | %s | %s / %s | %s | %s | %d (%d frames identical) | %d | %s |' % (
            tag, a['module'], fa(b), fa(a), fb(b), fb(a), cer(b), cer(a), len(ga['cases']), frames_same,
            len(cases), '; '.join('%s %s %s %.0f -> %.0f' % (r[0], r[1], r[2], r[3], r[4]) for r in big)))
        print('%s: %d cases, %d with frames identical to the legacy golden; %d cases whose sound moved' % (
            tag, len(ga['cases']), frames_same, len(cases)))
        # the voicing contrast between vowels ('aCa, the golden's s| cases), as measured (Q55): a voiced stop's VOT at least 20 ms below its
        # voiceless partner's
        for g, label in ((gb, 'before'), (ga, 'after')):
            pairs = []
            for vl, vd in (('p', 'b'), ('t', 'd'), ('k', 'g')):
                x, y = (vot(g, 's|' + vl), vot(g, 's|' + vd))
                if x is not None and y is not None:
                    pairs.append('%s %+.0f / %s %+.0f ms%s' % (vl, x, vd, y, '' if x - y >= 20 else ' MERGED'))
            if pairs:
                print('    voicing between vowels %s: %s' % (label, '; '.join(pairs)))
        by = {}
        for r in rows:
            by.setdefault(r[2], []).append(r[5] if r[5] is not None else r[6])
        for k, v in sorted(by.items()):
            print('    %-8s %3d moved, median %+.1f%s, largest %+.1f' % (k, len(v), statistics.median(v),
                                                                     ' ms' if k == 'VOT' else ' %',
                                                                     max(v, key=abs)))
    print('\n'.join(lines))
    if md:
        with open(md, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
