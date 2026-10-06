"""Writes the first master table (ipa/table/*.toml) from the IPA checklist and the traceability
table, once (DESIGN.md 3, capability C3). MIT licence.

    python engine/ipa/seed_table.py [--force]

Each of the 175 checklist entries becomes an entry keyed by its stable id (its code points, D4),
with its features in the controlled vocabulary of ipa/features.toml, its plan from
docs/tts-extension/design/traceability.json (route, end state, capabilities, tests), and state
MISSING: nothing is mapped until the harness has rendered and measured it (R19f). The acoustic
specification is left empty; Phase 4 fills it, value by value, each with its provenance.

After this the table files are the source and are edited by hand; the script refuses to write
over them without --force. The checklist's free-text features are turned into the controlled
ones here by rule, with the irregular letters (clicks, double articulations, epiglottals) given
by hand below; the validator then checks that no two letters share a bundle.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKLIST = os.path.join(ROOT, 'docs', 'tts-extension', 'inventory', 'IPA_CHECKLIST.json')
TRACE = os.path.join(ROOT, 'docs', 'tts-extension', 'design', 'traceability.json')
TABLE = os.path.join(ROOT, 'ipa', 'table')

SECTIONS = ['pulmonic', 'non_pulmonic', 'other_symbols', 'vowels', 'diacritics', 'suprasegmentals', 'tones']

PLACES = ['bilabial', 'labiodental', 'linguolabial', 'dental', 'alveolar', 'postalveolar', 'retroflex',
          'alveolo-palatal', 'palatal', 'velar', 'uvular', 'pharyngeal', 'epiglottal', 'glottal']
SIBILANTS = {'s', 'z', 'ʃ', 'ʒ', 'ʂ', 'ʐ', 'ɕ', 'ʑ'}

# manner (the checklist's words) -> stricture, nasal, lateral
MANNER = {
    'plosive': ('closure', False, False),
    'nasal': ('closure', True, False),
    'trill': ('trill', False, False),
    'tap or flap': ('tap', False, False),
    'fricative': ('friction', False, False),
    'lateral fricative': ('friction', False, True),
    'approximant': ('approximation', False, False),
    'lateral approximant': ('approximation', False, True),
}

# letters the rules above do not cover: the checklist's description, in the controlled words
BY_HAND = {
    'ʘ': dict(place='bilabial', place2='velar', stricture='closure', airstream='click', voicing='unspecified'),
    'ǀ': dict(place='dental', place2='velar', stricture='closure', airstream='click', voicing='unspecified'),
    'ǃ': dict(place='postalveolar', place2='velar', stricture='closure', airstream='click', voicing='unspecified'),
    'ǂ': dict(place='palatal', place2='velar', stricture='closure', airstream='click', voicing='unspecified'),
    'ǁ': dict(place='alveolar', place2='velar', stricture='closure', lateral=True, airstream='click',
              voicing='unspecified'),
    'ɓ': dict(place='bilabial', stricture='closure', airstream='implosive', voicing='voiced'),
    'ɗ': dict(place='alveolar', stricture='closure', airstream='implosive', voicing='voiced'),
    'ʄ': dict(place='palatal', stricture='closure', airstream='implosive', voicing='voiced'),
    'ɠ': dict(place='velar', stricture='closure', airstream='implosive', voicing='voiced'),
    'ʛ': dict(place='uvular', stricture='closure', airstream='implosive', voicing='voiced'),
    'ʍ': dict(place='bilabial', place2='velar', stricture='friction', voicing='voiceless'),
    'w': dict(place='bilabial', place2='velar', stricture='approximation', voicing='voiced'),
    'ɥ': dict(place='bilabial', place2='palatal', stricture='approximation', voicing='voiced'),
    'ʜ': dict(place='epiglottal', stricture='friction', voicing='voiceless'),
    'ʢ': dict(place='epiglottal', stricture='friction', voicing='voiced'),
    'ʡ': dict(place='epiglottal', stricture='closure', voicing='unspecified'),
    'ɕ': dict(place='alveolo-palatal', stricture='friction', sibilant=True, voicing='voiceless'),
    'ʑ': dict(place='alveolo-palatal', stricture='friction', sibilant=True, voicing='voiced'),
    'ɺ': dict(place='alveolar', stricture='tap', lateral=True, voicing='voiced'),
    'ɧ': dict(place='postalveolar', place2='velar', stricture='friction', voicing='voiceless'),
}

# marks: (kind, what it does). A modifier's `edit` is per class of base.
C, V = 'consonant', 'vowel'
MARKS = {
    'U+02BC': ('modifier', {C: {'airstream': 'ejective'}}),
    'U+035C': ('tie', {}), 'U+0361': ('tie', {}),
    'U+0325': ('modifier', {C: {'voicing': 'voiceless'}, V: {'voicing': 'voiceless'}}),
    'U+030A': ('modifier', {C: {'voicing': 'voiceless'}, V: {'voicing': 'voiceless'}}),
    'U+032C': ('modifier', {C: {'voicing': 'voiced'}, V: {'voicing': 'voiced'}}),
    'U+02B0': ('modifier', {C: {'aspiration': 'after'}}),
    'U+0339': ('modifier', {V: {'rounding_shift': 'more'}}),
    'U+031C': ('modifier', {V: {'rounding_shift': 'less'}}),
    'U+031F': ('modifier', {C: {'place_shift': 'advanced'}, V: {'quality_shift': 'advanced'}}),
    'U+0320': ('modifier', {C: {'place_shift': 'retracted'}, V: {'quality_shift': 'retracted'}}),
    'U+0308': ('modifier', {V: {'quality_shift': 'centralized'}}),
    'U+033D': ('modifier', {V: {'quality_shift': 'mid-centralized'}}),
    'U+0329': ('modifier', {C: {'syllabic': 'syllabic'}, V: {'syllabic': 'syllabic'}}),
    'U+032F': ('modifier', {C: {'syllabic': 'non-syllabic'}, V: {'syllabic': 'non-syllabic'}}),
    'U+02DE': ('modifier', {V: {'rhotic': True}}),
    'U+0324': ('modifier', {C: {'voicing': 'breathy'}, V: {'voicing': 'breathy'}}),
    'U+0330': ('modifier', {C: {'voicing': 'creaky'}, V: {'voicing': 'creaky'}}),
    'U+033C': ('modifier', {C: {'place': 'linguolabial'}}),
    'U+02B7': ('modifier', {C: {'secondary': '+labialized'}}),
    'U+02B2': ('modifier', {C: {'secondary': '+palatalized'}}),
    'U+02E0': ('modifier', {C: {'secondary': '+velarized'}}),
    'U+02E4': ('modifier', {C: {'secondary': '+pharyngealized'}}),
    'U+0334': ('modifier', {C: {'secondary': '+velarized-or-pharyngealized'}}),
    'U+031D': ('modifier', {C: {'stricture_shift': 'raised'}, V: {'quality_shift': 'raised'}}),
    'U+031E': ('modifier', {C: {'stricture_shift': 'lowered'}, V: {'quality_shift': 'lowered'}}),
    'U+0318': ('modifier', {C: {'tongue_root': 'advanced'}, V: {'tongue_root': 'advanced'}}),
    'U+0319': ('modifier', {C: {'tongue_root': 'retracted'}, V: {'tongue_root': 'retracted'}}),
    'U+032A': ('modifier', {C: {'place': 'dental'}}),
    'U+033A': ('modifier', {C: {'tongue_part': 'apical'}}),
    'U+033B': ('modifier', {C: {'tongue_part': 'laminal'}}),
    'U+0303': ('modifier', {C: {'nasalized': True}, V: {'nasalized': True}}),
    'U+207F': ('modifier', {C: {'release': 'nasal'}}),
    'U+02E1': ('modifier', {C: {'release': 'lateral'}}),
    'U+031A': ('modifier', {C: {'release': 'none'}}),
    'U+02D0': ('modifier', {C: {'length': 'long'}, V: {'length': 'long'}}),
    'U+02D1': ('modifier', {C: {'length': 'half-long'}, V: {'length': 'half-long'}}),
    'U+0306': ('modifier', {C: {'length': 'extra-short'}, V: {'length': 'extra-short'}}),
    'U+02C8': ('syllable-mark', {'stress': 'primary'}),
    'U+02CC': ('syllable-mark', {'stress': 'secondary'}),
    'U+007C': ('boundary', {'boundary': 'minor'}),
    'U+2016': ('boundary', {'boundary': 'major'}),
    'U+002E': ('boundary', {'boundary': 'syllable'}),
    'U+203F': ('boundary', {'boundary': 'linked'}),
    'U+A71C': ('tone', {'register': 'down'}),
    'U+A71B': ('tone', {'register': 'up'}),
    'U+2197': ('tone', {'slope': 'rise'}),
    'U+2198': ('tone', {'slope': 'fall'}),
}

# where a mark sits: before what it marks, after it, or over it (a combining character)
BY_ID = {}

PLACEMENT = {'U+02C8': 'before', 'U+02CC': 'before', 'U+A71C': 'before', 'U+A71B': 'before',
             'U+2197': 'before', 'U+2198': 'before'}


def consonant(e):
    f = e['features']
    sym = e['symbol']
    if sym in BY_HAND:
        out = dict(class_='consonant', airstream='pulmonic')
        out.update(BY_HAND[sym])
        return out
    place = f['place'].split(' (')[0]
    assert place in PLACES, (sym, place)
    stricture, nasal, lateral = MANNER[f['manner']]
    voicing = 'voiceless' if f['voicing'].startswith('voiceless') else 'voiced'
    out = dict(class_='consonant', place=place, stricture=stricture, voicing=voicing, airstream='pulmonic')
    if nasal:
        out['nasal'] = True
    if lateral:
        out['lateral'] = True
    if sym in SIBILANTS:
        out['sibilant'] = True
    return out


def vowel(e):
    f = e['features']
    return dict(class_='vowel', height=f['height'], backness=f['backness'], rounding=f['rounding'])


def tone_levels(e, by_id=None):
    """Chao levels, 1 lowest to 5 highest; a contour diacritic's are its equivalent letters'."""
    f = e['features']
    if by_id and e.get('equivalent_to') and not any(k.startswith('chao') for k in f):
        return tone_levels(by_id[e['equivalent_to']])
    if 'chao_levels' in f:
        return list(f['chao_levels'])
    if 'chao_level' in f:
        return [f['chao_level']]
    if 'chao_level_on_chart_row' in f:
        return [f['chao_level_on_chart_row']]
    return None


def toml_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return '[' + ', '.join(toml_value(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{ ' + ', '.join('%s = %s' % (k.rstrip('_'), toml_value(x)) for k, x in v.items()) + ' }'
    raise TypeError(v)


def entry(e, row):
    sid = e['id']
    lines = ['[sound."%s"]' % sid,
             'ipa = %s' % toml_value(e['symbol']),
             'codepoints = %s' % toml_value(e['codepoints']),
             'name = %s' % toml_value(row['name']),
             'section = %s' % toml_value(e['section']),
             'tier = "A"']
    if e['kind'] == 'letter':
        feats = consonant(e) if e['section'] != 'vowels' else vowel(e)
        lines.append('kind = "base"')
        lines.append('features = %s' % toml_value(feats))
    else:
        kind, what = MARKS.get(sid, ('tone', None))
        lines.append('kind = %s' % toml_value(kind))
        if kind == 'modifier':
            lines.append('edit = %s' % toml_value(what))
        elif kind == 'tone' and what is None:
            lines.append('levels = %s' % toml_value(tone_levels(e, BY_ID)))
        elif kind != 'tie':
            for k, v in what.items():
                lines.append('%s = %s' % (k, toml_value(v)))
        lines.append('placement = %s' % toml_value(
            PLACEMENT.get(sid, 'over' if e['symbol'] and 0x300 <= ord(e['symbol'][0]) <= 0x36f
                          or e['symbol'] and 0x1dc0 <= ord(e['symbol'][0]) <= 0x1dff else
                          'between' if kind in ('boundary', 'tie') else 'after')))
    if e.get('equivalent_to'):
        lines.append('equivalent_to = %s' % toml_value(e['equivalent_to']))
    lines += ['state = "MISSING"', 'level = 1', 'approximate = false',
              'plan = %s' % toml_value(dict(decision=row['decision'], end_state=row['end_state'],
                                            uses=row.get('existing', []), builds=row.get('to_build', []))),
              '',
              '[sound."%s".spec]' % sid,
              '',
              '[sound."%s".tests]' % sid,
              'checks = %s' % toml_value(row.get('tests', [])),
              '']
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    with open(CHECKLIST, encoding='utf-8') as f:
        checklist = json.load(f)['symbols']
    BY_ID.update((e['id'], e) for e in checklist)
    with open(TRACE, encoding='utf-8') as f:
        rows = {r['id']: r for r in json.load(f)['rows']}
    os.makedirs(TABLE, exist_ok=True)
    counts = {}
    for sec in SECTIONS:
        path = os.path.join(TABLE, sec + '.toml')
        if os.path.exists(path) and not a.force:
            print('%s exists; not written (--force to write it again, losing hand edits)' % path)
            return 1
        es = [e for e in checklist if e['section'] == sec]
        head = ('# The master table (DESIGN.md 3): %s. MIT licence.\n'
                '# Written first by engine/ipa/seed_table.py from the IPA checklist; edited by hand from then on.\n'
                '# Facts are cited, never pasted (the chart is CC BY-SA); every value carries its provenance.\n\n'
                % es[0]['section_title'])
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(head + '\n'.join(entry(e, rows[e['id']]) for e in es))
        counts[sec] = len(es)
    print('written: %s; %d entries' % (', '.join('%s %d' % kv for kv in counts.items()), sum(counts.values())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
