# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""The reference-range store (Phase 1, step 3) and check B: does a realised value fall in range?

reference/ranges.json holds cited values keyed by IPA, variety (a BCP 47 tag such as en-US),
speaker group and metric, each with its source and provenance. A range is made from what the
source gave, in this order:

    mean and sd          mean - 2 sd .. mean + 2 sd
    median, q1, q3       q1 - 1.5 IQR .. q3 + 1.5 IQR (Tukey's fences)
    geometric_sd_ratio   mean / r^2 .. mean * r^2
    min and max          min .. max

and nothing else: a mean alone is not a range, and an entry without one is not used.

A pack matches entries of its own variety, else of each parent variety in turn (en-GB-x-gbclan ->
en-GB -> en; a bare language such as pt also its standard region, pt-PT, named in DEFAULT_REGION),
else an entry its source states for languages in general ('cross-language': the nasal ranges);
never a sibling variety's (Valencian ranges do not judge Central Catalan: Q46, D93) and never
another language's. Preset 1 of every pack is an adult male voice and preset 2 an adult
female one (language.ini); other presets have no reference group. An entry for the voice's own
group is preferred; one pooled over speakers ('mixed') is used when there is none. In practice
the only consonant entries that give a range are the five general nasal ones (min..max): the VOT
and fricative sources give means without a spread, which by the rule above are not ranges. The
tone entries have no measure mapped to them yet: tones are checked from Phase 4.
"""

import json
import os
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

# the harness's measure -> the store's metric
METRIC = {'F1_50_hz': 'F1_hz', 'F2_50_hz': 'F2_hz', 'F3_50_hz': 'F3_hz', 'duration_ms': 'duration_ms',
          'f0_50_hz': 'f0_hz', 'vot_ms': 'vot_ms', 'centroid_hz': 'spectral_centroid_hz',
          'peak_hz': 'spectral_peak_hz', 'F3_min_hz': 'F3_min_hz', 'antiformant_hz': 'antiformant_hz',
          'murmur_F1_hz': 'nasal_murmur_F1_hz'}
GROUP = {1: 'adult male', 2: 'adult female'}

_store = None


def store():
    global _store
    if _store is None:
        with open(os.path.join(HERE, 'reference', 'ranges.json'), encoding='utf-8') as f:
            _store = json.load(f)
        for e in _store['entries']:
            e['ipa'] = unicodedata.normalize('NFC', e['ipa'])
    return _store


def bounds(e):
    if e.get('mean') is not None and e.get('sd') is not None:
        return e['mean'] - 2 * e['sd'], e['mean'] + 2 * e['sd'], 'mean +- 2 sd'
    if e.get('q1') is not None and e.get('q3') is not None:
        iqr = e['q3'] - e['q1']
        return e['q1'] - 1.5 * iqr, e['q3'] + 1.5 * iqr, 'quartiles +- 1.5 IQR'
    if e.get('mean') is not None and e.get('geometric_sd_ratio'):
        r = e['geometric_sd_ratio']
        return e['mean'] / r ** 2, e['mean'] * r ** 2, 'geometric mean x/ ratio^2'
    if e.get('min') is not None and e.get('max') is not None:
        return e['min'], e['max'], 'min .. max'
    return None


# A pack whose locale names no region is judged against its language's standard region (the pt pack
# is European Portuguese; its references are keyed pt-PT). A pack with a region never borrows a
# sibling region's references (Q46, D93).
DEFAULT_REGION = {'pt': 'pt-PT', 'en': 'en-US', 'de': 'de-DE', 'es': 'es-ES', 'fr': 'fr-FR', 'it': 'it-IT',
                  'pl': 'pl-PL', 'ja': 'ja-JP'}


def varieties(locale):
    """The varieties a pack may be judged against, most specific first: its own, then each parent
    (en-GB-x-gbclan -> en-GB -> en; a private-use part, x-..., falls away in one piece), then, for a
    bare language, its standard region (DEFAULT_REGION). Never a sibling: ca-BA -> ca, not ca-VA."""
    loc = (locale or '').replace('_', '-')
    parts = [p for p in loc.split('-') if p]
    lower = [p.lower() for p in parts]
    base = parts[:lower.index('x')] if 'x' in lower else parts
    chain = [loc] + ['-'.join(base[:k]) for k in range(len(base), 0, -1)]
    out = []
    for c in chain:
        if c and c.lower() not in [o.lower() for o in out]:
            out.append(c)
    if len(base) == 1 and base[0].lower() in DEFAULT_REGION:
        out.append(DEFAULT_REGION[base[0].lower()])
    return out


def lookup(ipa, locale, preset, measure):
    """The best entry for one value: the pack's own variety first, then its parents (varieties()),
    then the cross-language entries. None if none."""
    metric = METRIC.get(measure)
    group = GROUP.get(preset)
    if not metric or not group or not ipa:
        return None
    ipa = unicodedata.normalize('NFC', ipa)
    chain = [v.lower() for v in varieties(locale)]
    by_rank = {}
    for e in store()['entries']:
        if e['ipa'] != ipa or e['metric'] != metric or e['speaker_group'] not in (group, 'mixed') or bounds(e) is None:
            continue
        v = e['variety']
        if v.lower() in chain:
            by_rank.setdefault(chain.index(v.lower()), []).append(e)
        elif v == 'cross-language':
            by_rank.setdefault(len(chain), []).append(e)
    if not by_rank:
        return None
    pick = by_rank[min(by_rank)]
    # the voice's own group before a pooled one, then the source with the most tokens
    return sorted(pick, key=lambda e: (e['speaker_group'] != group, -(e.get('n') or 0)))[0]


def check(ipa, locale, preset, measure, value):
    """{'verdict': 'in range' | 'out of range', ...} or None when there is no reference."""
    if value is None:
        return None
    e = lookup(ipa, locale, preset, measure)
    if e is None:
        return None
    lo, hi, how = bounds(e)
    return dict(verdict='in range' if lo <= value <= hi else 'out of range', value=round(value, 1),
                lo=round(lo, 1), hi=round(hi, 1), how=how, source=e['source'], variety=e['variety'],
                where=e.get('where_in_source'), provenance=e.get('provenance'))


def selftest():
    """The lookup rule on the store as it stands (Q46, D93). Exit 1 on any failure."""
    cases = [
        ("varieties en-GB-x-gbclan", varieties('en-GB-x-gbclan'), ['en-GB-x-gbclan', 'en-GB', 'en']),
        ("varieties en-US-nyc", varieties('en-US-nyc'), ['en-US-nyc', 'en-US', 'en']),
        ("varieties pt (bare: its standard region)", varieties('pt'), ['pt', 'pt-PT']),
        ("varieties ca-BA (never ca-VA)", varieties('ca-BA'), ['ca-BA', 'ca']),
        ("varieties chr-US-Qaaa-x-West", varieties('chr-US-Qaaa-x-West'),
         ['chr-US-Qaaa-x-West', 'chr-US-Qaaa', 'chr-US', 'chr']),
    ]

    def var(ipa, loc, measure='F1_50_hz'):
        e = lookup(ipa, loc, 1, measure)
        return e['variety'] if e else None
    cases += [
        ("ca-VA judged by its own ranges", var('i', 'ca-VA'), 'ca-VA'),
        ("ca-BA not judged by Valencian ranges", var('i', 'ca-BA') == 'ca-VA', False),
        ("ca not judged by Valencian ranges", var('i', 'ca') == 'ca-VA', False),
        ("pt judged by pt-PT, not pt-BR", var('i', 'pt'), 'pt-PT'),
        ("pt-BR judged by its own", var('i', 'pt-BR'), 'pt-BR'),
        ("en-US-nyc falls back to its parent en-US", var('i', 'en-US-nyc'), 'en-US'),
        ("en-GB not judged by en-US or en-AU", var('i', 'en-GB') in ('en-US', 'en-AU'), False),
        ("es-MX not judged by es-ES or es-PE", var('i', 'es-MX') in ('es-ES', 'es-PE'), False),
        ("another language's entries never lent", var('i', 'xx'), None),
    ]
    general = [e for e in store()['entries'] if e['variety'] == 'cross-language' and bounds(e)]
    if general:
        g = general[0]
        measure = next((m for m, k in METRIC.items() if k == g['metric']), None)
        cases.append(("cross-language entry reaches any language (%s %s)" % (g['ipa'], g['metric']),
                      var(g['ipa'], 'xx', measure), 'cross-language'))
    failed = 0
    for name, got, want in cases:
        ok = got == want
        failed += not ok
        print('  %s  %s: got %r, wanted %r' % ('ok  ' if ok else 'FAIL', name, got, want))
    print('reference selftest: %d of %d pass' % (len(cases) - failed, len(cases)))
    return 1 if failed else 0


if __name__ == '__main__':
    import sys
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    for loc in sys.argv[1:]:
        print(loc, '->', varieties(loc))

