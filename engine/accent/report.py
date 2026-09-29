#!/usr/bin/env python3
"""Writes docs/LANGUAGE-REPORT.md: for every language read by eSpeak NG, what
the literature says the language sounds like, what eSpeak NG reads, and what
OpenEVV says.

It is put together from what is already written down elsewhere and adds
nothing of its own: the language's profile (engine/profiles/<tag>.json), its
pack (languages/<tag>/language.ini and sounds.map), and the melody
engine/accent/prosody.py gives it.

    python engine/accent/report.py [docs/LANGUAGE-REPORT.md]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import prosody  # noqa: E402
import questions  # noqa: E402

MODULE = {'dedx': 'German', 'itix': 'Italian', 'esex': 'Castilian Spanish', 'esux': 'Latin American Spanish',
          'engx': 'British English', 'enux': 'US English', 'frfx': 'French'}
MELODY = {
    'peak': 'the stressed syllable is high and the pitch falls out of it',
    'late': 'the pitch rises through the stressed syllable to a peak at its end',
    'low': 'the stressed syllable is low and the rise comes after it',
    'edge': 'no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall',
    'flat': 'little movement on the stressed syllable, since none is described',
    'tone': 'every syllable has its tone',
}
QUESTION = {
    'rise': 'rises at the end',
    'risefall': 'rises to the syllable before the last and falls on the last',
    'register': 'is said higher as a whole, with little or no rise at the end',
    'fall': 'ends as a statement does, in a higher register',
}
# What OpenEVV cannot say because eSpeak NG does not read it, by language.
NOT_READ = {
    'sv': 'The two word accents are not in eSpeak NG\'s reading, so words are told apart by stress alone.',
    'nb': 'The two word accents are not in eSpeak NG\'s reading, so words are told apart by stress alone.',
    'hr': 'The four accents are not in eSpeak NG\'s reading: stress is spoken, the rising and falling accents '
          'are not.',
    'sr': 'The four accents are not in eSpeak NG\'s reading: stress is spoken, the rising and falling accents '
          'are not.',
    'bs': 'The four accents are not in eSpeak NG\'s reading: stress is spoken, the rising and falling accents '
          'are not.',
    'sl': 'The tonemes are not in eSpeak NG\'s reading.',
    'lt': 'The acute and the circumflex are not in eSpeak NG\'s reading.',
    'lv': 'The three syllable tones are not in eSpeak NG\'s reading.',
    'ltg': 'The syllable tones are not in eSpeak NG\'s reading.',
    'th': 'eSpeak NG reads Thai without tones, and its Thai voice is a beginning: the language is not yet '
          'intelligible.',
    'my': 'eSpeak NG\'s Burmese voice is a beginning.',
    'tn': 'Tone is not in eSpeak NG\'s reading.',
    'om': 'The pitch accent is not in eSpeak NG\'s reading.',
    'pap': 'The tone patterns of words are not in eSpeak NG\'s reading.',
    'gd': 'The word accent of Lewis is not in eSpeak NG\'s reading.',
    'grc': 'eSpeak NG reads Ancient Greek with stress in place of its pitch accent.',
    'ko': 'The pitch that follows from the first consonant of a phrase is not spoken.',
    'pa': 'eSpeak NG marks one of the three tones, the low one after the letters that were breathy stops; the '
          'high tone is not read.',
    'da': 'Stød is not in eSpeak NG\'s reading.',
    'chr': 'Tone is read only where the text marks it; the syllabary is read without tone.',
}


def read_ini(path):
    out, sec = {}, None
    for line in open(path, encoding='utf-8-sig'):
        line = line.strip()
        if line.startswith('['):
            sec = line.strip('[]')
        elif '=' in line and not line.startswith(';'):
            k, v = line.split('=', 1)
            out[(sec, k.strip())] = v.strip()
    return out


def own_sounds(path):
    """The sounds the language's own phonemes are given, as (ipa, phones,
    definition)."""
    defs = {}
    used = []
    own = False
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        m = re.match(r'sound (\S+) (.*?)\s*# (.*)$', line)
        if m:
            defs[m.group(1)] = m.group(2).strip()
            continue
        if line.startswith('# eSpeak NG phoneme table'):
            own = True
            continue
        if line.startswith('# by IPA'):
            own = False
        if own and line.startswith('@'):
            key, _, rest = line.partition(' ')
            phones, _, ipa = rest.partition('  # ')
            if '(not met)' in ipa:
                continue
            ids = re.findall(r'=(s\d+)', phones)
            if ids and ipa.strip():
                used.append((ipa.strip(), phones.strip(), [defs.get(i, '') for i in ids]))
    return used


def sentence(text):
    text = (text or '').strip()
    if text and text[-1] not in '.!?':
        text += '.'
    return text


def one(tag, out):
    pack = os.path.join(ROOT, 'languages', tag)
    ini = read_ini(os.path.join(pack, 'language.ini'))
    prof = prosody.load_profile(tag) or {}
    name = ini.get(('Language', 'Name'), tag)
    module = ini.get(('Language', 'Template'), '')
    tones = prosody.tones_of(tag)
    accent, kind, question = prosody.accent_line(tag, prof, module, tones)
    sounds = own_sounds(os.path.join(pack, ini.get(('Frontend', 'Sounds'), 'sounds.map')))
    out.append('## %s (`%s`)' % (name, tag))
    out.append('')
    if prof.get('family') or prof.get('variety'):
        out.append('%s. Described: %s.' % (prof.get('family', '').rstrip('.'),
                                           (prof.get('variety') or 'not said').rstrip('.')))
        out.append('')
    if prof.get('contrasts'):
        out.append('**What the language has.** ' + ' '.join(sentence(c[0].upper() + c[1:])
                                                          for c in prof['contrasts'][:8] if c))
        out.append('')
    st = prof.get('stress') or {}
    rh = prof.get('rhythm') or {}
    bits = []
    if st.get('type'):
        bits.append('Stress: %s' % sentence(st['type']))
    if rh.get('class'):
        bits.append('Rhythm: %s' % sentence(rh['class']))
    tn = prof.get('tone') or {}
    if tn.get('type') and tn['type'] != 'none':
        inv = tn.get('inventory') or []
        bits.append('Tone: %s, %d in number.' % (tn['type'], len(inv)) if inv else 'Tone: %s.' % tn['type'])
    if bits:
        out.append(' '.join(bits))
        out.append('')
    problems = (prof.get('espeak') or {}).get('problems') or []
    if problems:
        out.append('**What eSpeak NG reads otherwise than the literature has it.**')
        out.append('')
        for p in problems[:8]:
            out.append('- ' + sentence(p))
        out.append('')
    out.append('**What OpenEVV says.** Spoken by the module made from %s (`%s`). ' % (
        MODULE.get(module, module), module) + (
        '%d of the language\'s phonemes are given a sound of their own' % len(sounds) if sounds else
        'Every phoneme is one of the module\'s phones as it stands') + '.')
    shown = []
    seen = set()
    for ipa, phones, d in sounds:
        if ipa in seen:
            continue
        seen.add(ipa)
        shown.append('%s (%s: %s)' % (ipa, phones, '; '.join(x for x in d if x)))
    if shown:
        out.append('')
        out.append('The sounds, each with the phone it is made of and how it differs from it: ' +
                   ', '.join(shown[:60]) + ('.' if len(shown) <= 60 else ', and %d more.' % (len(shown) - 60)))
    out.append('')
    if tones:
        out.append('Tones: %s. The pitch is made from them, syllable by syllable.' % ', '.join(
            '%s (%s)' % (n, t['p']) for n, t in tones.items()))
    else:
        out.append('Melody: %s. A question that wants yes or no %s.' % (MELODY[kind], QUESTION[question]))
    asked = questions.of(tag)
    if asked and not tones:
        out.append('A question asked with a question word (%s ...) ends as a statement does, from a high '
                   'question word.' % ', '.join(w.lstrip('~') for w in asked[1][:4]))
    if 'stressed' in accent or 'last' in accent:
        out.append('Timing: ' + ', '.join('%s %s per cent' % (k, accent[k]) for k in ('stressed', 'weak', 'last')
                                          if k in accent) + ' of the module\'s own.')
    out.append('')
    if tag in NOT_READ:
        out.append('**Not yet.** ' + NOT_READ[tag])
        out.append('')
    src = prof.get('sources') or []
    if src:
        out.append('Sources: ' + ' '.join(sentence(s) for s in src[:6]) + (
            ' And %d more in the profile.' % (len(src) - 6) if len(src) > 6 else ''))
        out.append('')


def main(argv):
    path = argv[0] if argv else os.path.join(ROOT, 'docs', 'LANGUAGE-REPORT.md')
    langs = os.path.join(ROOT, 'languages')
    tags = []
    for t in sorted(os.listdir(langs)):
        ini = os.path.join(langs, t, 'language.ini')
        if os.path.exists(ini) and '[Frontend]' in open(ini, encoding='utf-8-sig').read():
            tags.append(t)
    out = [
        '# The languages, one by one',
        '',
        'For each of the %d languages read by eSpeak NG: what the literature says the language sounds like, '
        'what eSpeak NG reads otherwise, and what OpenEVV says. The first two are summaries of the language\'s '
        'profile in `engine\\profiles`, which names its sources and marks every number with how sure it is; '
        'the third is read off the language\'s pack. `docs\\SOUNDS.md` says what the numbers in a sound mean.'
        % len(tags),
        '',
        'This page is written by `engine\\accent\\report.py`.',
        '',
    ]
    for t in tags:
        one(t, out)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('%d languages: %s' % (len(tags), path))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
