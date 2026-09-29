#!/usr/bin/env python3
"""Writes a language pack's sounds.map: its phonemes as a module's phones,
with the sounds, the tones and the melody the language has of its own.

phonemes.map, which packs have had since 1.1.0, says which of a module's
phones is nearest each of a language's phonemes and nothing more, so that the
language is spoken with the module's accent. sounds.map says the same and
then how each sound differs from the phone that stands for it, and the
engine's accent layer makes the difference. The file is the same kind of
file with more kinds of line in it:

    template dedx                     the module that speaks
    accent f0=own shape=1 ...         the melody and rhythm of the language
    sound s4 f2=91 f3=79 vot=12       a sound, as it differs from its phone
    tone 35 p=0:31,30:29,100:50       a tone
    tonename 2 35                     eSpeak NG's name for a tone, and ours
    says C t S                        the module says C as t and then S
    words apart                       every syllable is a word
    @hi:t.   t=s4                     a phoneme: the phone, and the sound

A phone written `<h=s9' is not in the module at all and is made by the
engine, out of the vowel beside it.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import espeak_phonemes as EP  # noqa: E402
import prosody  # noqa: E402
import questions  # noqa: E402
import sounds as S  # noqa: E402

# The module that speaks in place of each of IBM's: the same module with the
# rules of its own language's phonology taken out, so that it says the phones
# it is given (openevv/accents).
CLONE = {'dede': 'dedx', 'itit': 'itix', 'eses': 'esex', 'esus': 'esux', 'engb': 'engx', 'enus': 'enux',
         'frfr': 'frfx'}

# Where eSpeak NG's name for a phoneme misleads: the phoneme by its table and
# name, and the sound it is. Found by reading what eSpeak NG says against
# what the literature says the language has.
MEANT = {
    # Hindi and its relatives: eSpeak NG writes the breathy voiced stops with
    # the mark of aspiration, and they are taken so by their voicing
}


def phones_text(parts):
    return ' '.join(p.text() for p in parts) or '-'


def english_like():
    return S.Language('en')


def write_map(path, tag, template, table_names, tables, stats, voice, lang_name, profile=None):
    t = EP.TEMPLATES[template]
    clone = CLONE.get(template, template)
    chassis = S.Chassis(clone, template)
    ipas = [s['ipa'] for s in stats if s['type'] >= 2 and s.get('ipa')]
    for tn in table_names:
        tab = tables.get(tn)
        if tab:
            ipas += [ph['ipa'] for ph in tab['phonemes'] if ph['type'] >= 2 and ph.get('ipa')]
    language = S.Language(tag, profile, ipas)
    d = S.Designer(chassis, language)
    foreign = S.Designer(chassis, english_like())
    foreign.defs = d.defs
    foreign.notes = d.notes
    foreign.says = d.says

    entries = []
    unsaid = []
    met = set((s['table'], s['mnemonic']) for s in stats)
    seen_keys = set()

    def entry(key, ipa, is_vowel, designer, note):
        if key in seen_keys:
            return
        seen_keys.add(key)
        try:
            parts = designer.phoneme(ipa, is_vowel)
        except Exception as e:  # a sound the designer cannot take apart
            parts = []
            unsaid.append('%s (%s): %s' % (key, ipa, e))
        if not parts:
            old, _cost = EP.map_phoneme(t, ipa, is_vowel)
            parts = [S.Part(p) for p in old]
            d.finish(parts, ipa)
        entries.append((key, phones_text(parts), note))

    own = collections.OrderedDict()
    for tn in table_names:
        tab = tables.get(tn)
        if not tab:
            continue
        entries.append((None, None, '# eSpeak NG phoneme table %s' % tn))
        for ph in tab['phonemes']:
            if ph['type'] < 2 or not ph['mnemonic']:
                continue
            key = '@%s:%s' % (tn, ph['mnemonic'])
            ipa = MEANT.get(key, ph['ipa'])
            # a table has more phonemes than a language uses: those that were
            # met in the language's own sentences are told from the rest
            entry(key, ipa, ph['type'] == 2, d, ph['ipa'] + ('' if (tn, ph['mnemonic']) in met else '  (not met)'))
            own[ipa] = ph['type'] == 2
        entries.append((None, None, ''))
    entries.append((None, None, '# by IPA: this language\'s sounds in words eSpeak NG reads in another'))
    for ipa, v in own.items():
        if ipa and ' ' not in ipa:
            entry(ipa, ipa, v, d, '')
    entries.append((None, None, ''))
    entries.append((None, None, '# by IPA: English, for the English words a text has in it'))
    for tn in ('en', 'en-us'):
        tab = tables.get(tn)
        if not tab or tn in table_names:
            continue
        for ph in tab['phonemes']:
            if ph['type'] < 2 or not ph['ipa'] or ' ' in ph['ipa']:
                continue
            entry(ph['ipa'], ph['ipa'], ph['type'] == 2, foreign, '')
    entries.append((None, None, ''))
    entries.append((None, None, '# by IPA: every letter of it, so that anything can be taken apart'))
    for base in list(EP.CONS) + list(EP.VOWELS):
        entry(base, base, base in EP.VOWELS, foreign, '')

    tones = prosody.tones_of(tag)
    accent, kind, question = prosody.accent_line(tag, profile, clone, tones)

    # Where every syllable is a word, only what is a glide in earnest may
    # stand second in a syllable's beginning: not the r and l that follow a
    # stop in the languages the modules were written for.
    apart = tag in prosody.WORDS_APART
    glides = [g for g in t.glides if g in ('j', 'y', 'w', 'H')] if apart else t.glides
    lines = [
        '# OpenEVV sound map: %s (eSpeak NG voice %s), spoken by openevv\'s %s module' % (lang_name, voice, t.name),
        '# with the sounds, the melody and the tones of the language itself.',
        '# Written by engine/accent/mapwriter.py; OpenEvvFrontend reads it, and docs/LANGUAGES.md',
        '# says what each line means. Edit freely: the file is read each time a voice starts.',
        '',
        'template %s' % clone,
        'style %s' % ('french' if t.french else 'standard'),
        'vowels %s' % ' '.join(t.all_vowel_phones() + (['R'] if template == 'dede' else [])),
        'glides %s' % ' '.join(glides),
        'schwa %s' % t.schwa,
        'secondary %s' % t.secondary,
    ]
    if apart:
        lines.append('words apart')
        lines.append('onset %d' % prosody.ONSET.get(tag, 2))
        for x, y in prosody.CLUSTERS.get(tag, ()):
            lines.append('cluster %s %s' % (x, y))
    lines += ['', '# the melody: %s; a question that wants yes or no: %s' % (kind, question),
              'accent %s' % ' '.join('%s=%s' % kv for kv in accent.items()), '']
    asked = questions.of(tag)
    if asked:
        where, words = asked
        lines.append('# the words a question is asked with, which is not the question that wants yes or no')
        for i in range(0, len(words), 8):
            lines.append('whwords %s %s' % (where, ' '.join(words[i:i + 8])))
        lines.append('')
    if tones:
        lines.append('# the tones, under eSpeak NG\'s names for them')
        for name, tone in tones.items():
            lines.append('tone %s %s' % (name, ' '.join('%s=%s' % kv for kv in tone.items())))
        weak = prosody.weak_tones_of(tag)
        if weak:
            lines.append('weaktones %s' % ' '.join(weak))
        lines.append('')
    # what the module says in place of what it is given, used or not
    says = set(d.says)
    for ph, m in chassis.phones.items():
        said = m.get('said')
        if m.get('kind') == 'consonant' and said and said != [ph] and len(said) <= 4:
            says.add((ph, tuple(said)))
    if says:
        lines.append('# what the module says in place of a phone it is given')
        for given, said in sorted(says):
            lines.append('says %s %s' % (given, ' '.join(said)))
        lines.append('')
    if d.defs:
        lines.append('# the sounds of the language that the module has not, each as it differs from the phone')
        lines.append('# that stands for it: formants and lengths in per cent, times in milliseconds')
        for keys, sid in d.defs.items():
            lines.append('%-40s # %s' % ('sound %s %s' % (sid, keys), d.notes.get(sid, '')))
        lines.append('')
    for key, phones, note in entries:
        if key is None:
            lines.append(note)
        else:
            lines.append(('%-16s %-22s%s' % (key, phones, ('  # ' + note) if note else '')).rstrip())
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    return dict(sounds=len(d.defs), kind=kind, question=question, tones=len(tones or ()), unsaid=unsaid,
                clone=clone)


if __name__ == '__main__':
    print(__doc__)
