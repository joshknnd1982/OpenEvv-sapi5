"""The reference-range store (Phase 1, step 3) and check B: does a realised value fall in range?

reference/ranges.json holds cited values keyed by IPA, variety (a BCP 47 tag such as en-US),
speaker group and metric, each with its source and provenance. A range is made from what the
source gave, in this order:

    mean and sd          mean - 2 sd .. mean + 2 sd
    median, q1, q3       q1 - 1.5 IQR .. q3 + 1.5 IQR (Tukey's fences)
    geometric_sd_ratio   mean / r^2 .. mean * r^2
    min and max          min .. max

and nothing else: a mean alone is not a range, and an entry without one is not used.

A pack matches entries of its own variety, else of the same language (en-US for enus, de-DE for
de), else an entry its source states for languages in general ('cross-language': the nasal
ranges); never another language's. Preset 1 of every pack is an adult male voice and preset 2 an adult
female one (language.ini); other presets have no reference group. An entry for the voice's own
group is preferred; one pooled over speakers ('mixed': the VOT, fricative and nasal sources) is
used when there is none. The store's tone entries (Chao numbers, F0 turning points) have no
measure mapped to them yet: tones are checked from Phase 4, when tone cases exist.
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


def varieties(locale):
    """The varieties a pack's locale may use, most specific first: en-US -> en-US, en."""
    loc = (locale or '').replace('_', '-')
    lang = loc.split('-')[0].lower()
    return loc, lang


def lookup(ipa, locale, preset, measure):
    """The best entry for one value: same variety first, then same language. None if none."""
    metric = METRIC.get(measure)
    group = GROUP.get(preset)
    if not metric or not group or not ipa:
        return None
    ipa = unicodedata.normalize('NFC', ipa)
    loc, lang = varieties(locale)
    exact, same_lang, general = [], [], []
    for e in store()['entries']:
        if e['ipa'] != ipa or e['metric'] != metric or e['speaker_group'] not in (group, 'mixed') or bounds(e) is None:
            continue
        v = e['variety']
        if v.lower() == loc.lower():
            exact.append(e)
        elif v.split('-')[0].lower() == lang:
            same_lang.append(e)
        elif v == 'cross-language':
            general.append(e)
    pick = exact or same_lang or general
    if not pick:
        return None
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
