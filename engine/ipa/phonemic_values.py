# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""The phonemic formants of the table's vowels (D98): a vowel as languages typically have it, beside the
value the entry chose (often a cardinal vowel, one phonetician's corner of the vowel space).

    python engine/ipa/phonemic_values.py [--write]

For each vowel letter with formants, F1 to F3: the median of the value chosen and every other candidate its
note lists ("Other candidates (F1, Hz): 574 (catalan2025 ...); ..."), leaving out those the note marks not
used (SECONDARY, unreliable). Each candidate was read from its source when the entry was made (Phase 4); the
median is `derived`, its rule naming the count and the sources. --write puts it into ipa/table/vowels.toml as
`phonemic_formants` on the line after the entry's `formants`; the master path's phonemic reading takes it for
a vowel the template lacks (adapter.realize, phonemic). IPA typed directly keeps `formants`.
"""
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import table as T  # noqa: E402

VOWELS = os.path.join(ROOT, 'ipa', 'table', 'vowels.toml')


def candidates(x):
    """[(Hz, source id)]: the value chosen and the note's other candidates still in use."""
    out = [(float(x['v']), x.get('ref') or x.get('tag'))]
    m = re.search(r'Other candidates \(F\d, Hz\):(.*)$', x.get('note', ''), re.S)
    if m:
        for part in re.split(r'\);\s*(?=\d)', m.group(1)):
            mm = re.match(r'\s*(\d+(?:\.\d+)?) \((\S+)(.*)', part, re.S)
            if mm and not re.search(r'not used|SECONDARY|unreliable', mm.group(3)):
                out.append((float(mm.group(1)), mm.group(2)))
    return out


def values(t):
    """{sid: {F1: (Hz, n, [sources])}} for every vowel letter with formants."""
    out = {}
    for sid, e in sorted(t.sounds.items()):
        if e.get('kind') != 'base' or e['features'].get('class') != 'vowel':
            continue
        fm = (e.get('spec') or {}).get('formants') or {}
        got = {}
        for k in ('F1', 'F2', 'F3'):
            if isinstance(fm.get(k), dict):
                c = candidates(fm[k])
                got[k] = (int(round(statistics.median(v for v, _ in c))), len(c), sorted(set(s for _, s in c)))
        if got:
            out[sid] = got
    return out


def toml_line(got):
    parts = []
    for k, (hz, n, srcs) in sorted(got.items()):
        rule = ('the median of the %d values the entry cites for %s (the one chosen and its note\'s other candidates: '
                '%s); a vowel as languages have it, for the phonemic reading (D98)' % (n, k, ', '.join(srcs)))
        parts.append('%s = { v = %d, tag = "derived", rule = "%s" }' % (k, hz, rule.replace('"', "'")))
    return 'phonemic_formants = { %s }' % ', '.join(parts)


def main():
    t = T.load()
    vals = values(t)
    for sid, got in vals.items():
        print('%-8s %-3s %s' % (sid, t.sounds[sid]['ipa'], '  '.join('%s %d (n=%d)' % (k, v[0], v[1]) for k, v in sorted(got.items()))))
    if '--write' not in sys.argv:
        return 0
    with open(VOWELS, encoding='utf-8') as f:
        lines = f.read().split('\n')
    out, cur, n = [], None, 0
    for line in lines:
        m = re.match(r'\[sound\."([^"]+)"\.spec\]$', line)
        if m:
            cur = m.group(1)
        elif line.startswith('['):
            cur = None
        if line.startswith('phonemic_formants = '):
            continue                       # written again below
        out.append(line)
        if cur in vals and line.startswith('formants = '):
            out.append(toml_line(vals[cur]))
            n += 1
    with open(VOWELS, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out))
    print('%s: phonemic_formants written for %d vowels' % (os.path.relpath(VOWELS, ROOT), n))
    return 0


if __name__ == '__main__':
    sys.exit(main())
