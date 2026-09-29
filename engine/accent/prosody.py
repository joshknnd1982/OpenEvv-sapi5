#!/usr/bin/env python3
"""The melody and the rhythm of each language, and its tones.

What a language's sentences sound like is said to the engine in one line of
the language's map, `accent ...', and its tones in `tone ...' lines. The
numbers here are the ones those lines carry. They come from the profile of
the language (engine/profiles/<tag>.json: what the literature says of its
stress, rhythm, intonation and tone) by way of a few kinds of melody that
languages share, each of which is a setting of the engine's pitch generator:

  peak    the stressed syllable is high and the pitch falls out of it
          (H*+L): German, Dutch, Hungarian, Finnish
  late    the pitch rises through the stressed syllable and is highest at its
          end or just after it (L+H*): Spanish, Italian, Arabic, Persian
  low     the stressed syllable is low and the rise comes after it (L*+H):
          Czech, Greek, Danish, Hindi and the languages of India, where the
          rise runs to the end of the phrase
  edge    no syllable is picked out by pitch; the phrase ends with a rise or
          a fall: French, Korean, Indonesian
  tone    every syllable has a tone of its own

A question that can be answered yes or no ends as the language ends it:
with a rise, with a rise and a fall after it, in a higher register with no
rise at all, or as a statement does where a particle has already said that
it is a question.

Pitch is in tenths of a semitone, tone levels in tenths of Chao's five
levels (10 the bottom of the voice, 50 the top), durations in per cent.
"""
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(os.path.dirname(HERE), 'profiles')

# ---- melody ------------------------------------------------------------------

MELODY = {
    #        shape accent accent2 unstressed
    'peak': dict(shape=0, accent=26, accent2=12, unstressed=-6),
    'late': dict(shape=2, accent=28, accent2=12, unstressed=-6),
    'low': dict(shape=1, accent=24, accent2=10, unstressed=-2),
    'edge': dict(shape=2, accent=14, accent2=6, unstressed=-2),
    'flat': dict(shape=0, accent=12, accent2=6, unstressed=-3),
}

QUESTION = {
    # a rise on the last syllables
    'rise': dict(fq=38, qreg=8, span=2),
    # up to the syllable before the last and down on the last
    'risefall': dict(fq=34, qreg=8, span=2, qfall=50),
    # no rise: the whole question is higher and its fall is smaller
    'register': dict(fq=4, qreg=22, span=2),
    # as a statement, a particle or the order of words having said it
    'fall': dict(fq=-8, qreg=14, span=2),
}

RANGE = {'narrow': 0.8, 'medium': 1.0, 'wide': 1.2}


def melody_of(profile):
    """The kind of melody, read out of what the profile says of the pitch
    accent. The order of the tests matters: a description names the usual
    accent first."""
    i = profile.get('intonation') or {}
    t = (profile.get('tone') or {}).get('type') or 'none'
    text = (i.get('accent_shape') or '')
    low = text.lower()
    if 'lexical tone' in t:
        return 'tone'
    first = {}
    for kind, marks in (
            ('low', ('L*+H', 'L* ', 'L*.', 'L*H', 'low on the stressed', 'low on the word-initial',
                     'low on the first', 'low on the prominent', 'low on the accented', 'LH per phrase',
                     'low at the start of the phrase', 'low stressed syllable', 'LH associated')),
            ('late', ('L+H*', 'L+<H*', 'LH*', 'rise through', 'rise to a high', 'rising accent', 'rise onto',
                      'rise to a peak', 'rising (L', 'rise on the stressed', 'high or rising')),
            ('peak', ('H*+L', 'H*L', 'H* L', 'peak on the accented', 'peak in the accented', 'peak on or just',
                      'high pitch on', 'higher pitch on', 'HL:', 'falling accents', 'nuclear fall', 'H* peak',
                      'high on the stressed', 'high or falling', 'pitch peak', 'high level on', 'LHL',
                      'a fall that', 'peak on the stressed', 'high pitch on the stressed')),
            ('edge', ('no pitch accent', 'last two syllables of a phrase', 'last syllable of the group',
                      'last full syllable', 'phrase-final', 'penultimate syllable of the phrase'))):
        at = [text.find(m) for m in marks if text.find(m) >= 0]
        if at:
            first[kind] = min(at)
    if not first:
        return 'flat'
    return min(first, key=lambda k: first[k])


def question_of(profile):
    i = profile.get('intonation') or {}
    text = (i.get('yes_no_question') or '').lower()
    if not text or 'not described' in text or 'unknown' in text or 'not recoverable' in text:
        return 'register'
    for m in ('rise-fall', 'falls again', 'falls sharply', 'followed by a fall', 'then a fall', 'and a fall on',
              'final fall when', 'then low', 'followed by a low'):
        if m in text:
            return 'risefall'
    for m in ('no final rise', 'ends low', 'end low', 'ending low', 'falling contour', 'falls as in',
              'mostly falling', 'ends with low', 'end in a fall', 'no separate rising', 'no special melody',
              'fall to low'):
        if m in text:
            return 'fall'
    for m in ('rise', 'rising', 'high boundary', 'high final', 'stays high'):
        if m in text:
            return 'rise'
    if 'register' in text or 'higher' in text or 'high' in text:
        return 'register'
    return 'register'


# Put right by hand where the words of a profile mislead the tests above, or
# where there is no profile.
MELODY_BY_HAND = {
    'fr-be': 'edge', 'fr-ch': 'edge', 'ht': 'edge', 'ko': 'edge', 'id': 'edge', 'ms': 'edge',
    'tr': 'late', 'az': 'late', 'hy': 'late', 'hyw': 'late', 'fa': 'late', 'fa-latn': 'late',
    'hu': 'peak', 'fi': 'peak', 'et': 'peak', 'sv': 'peak', 'nb': 'low', 'da': 'low',
    'ru': 'late', 'ru-cl': 'late', 'ru-lv': 'late', 'uk': 'late', 'be': 'late', 'bg': 'late',
    'eo': 'late', 'ia': 'late', 'io': 'late', 'lfn': 'late', 'jbo': 'peak', 'piqd': 'peak', 'py': 'flat',
    'qdb': 'peak', 'qya': 'late', 'sjn': 'late', 'xex': 'flat',
    'kl': 'edge', 'ka': 'low', 'mn': 'low', 'mn-f': 'low',
}
QUESTION_BY_HAND = {
    'ru': 'risefall', 'ru-cl': 'risefall', 'ru-lv': 'risefall', 'hu': 'risefall', 'ro': 'risefall',
    'el': 'risefall', 'fi': 'fall', 'et': 'fall', 'eo': 'rise', 'ia': 'rise', 'io': 'rise', 'lfn': 'rise',
    'jbo': 'fall', 'piqd': 'rise', 'py': 'rise', 'qdb': 'rise', 'qya': 'rise', 'sjn': 'rise', 'xex': 'rise',
    'pdc': 'risefall', 'pdc-x-lehigh': 'risefall', 'pdc-x-midwest': 'risefall',
}

# How the modules themselves time their syllables: the three IBM wrote for
# languages that are timed by stress, and the four for languages timed by the
# syllable.
STRESS_TIMED_MODULES = ('dede', 'dedx', 'enus', 'enux', 'engb', 'engx')


def rhythm_of(profile, chassis):
    r = profile.get('rhythm') or {}
    kind = (r.get('class') or '').lower()
    out = collections.OrderedDict()
    module_stress = chassis in STRESS_TIMED_MODULES
    if 'syllable' in kind or 'mora' in kind:
        if module_stress:
            out['stressed'] = 88
            out['weak'] = 112
    elif 'stress' in kind:
        if not module_stress:
            out['stressed'] = 112
            out['weak'] = 85
    else:
        # between the two
        if module_stress:
            out['stressed'] = 94
            out['weak'] = 106
        else:
            out['stressed'] = 106
            out['weak'] = 94
    fl = (r.get('final_lengthening') or '').lower()
    if fl.startswith('weak'):
        out['last'] = 88
    elif fl.startswith('strong'):
        out['last'] = 118
    return out


# The number each module's table gives the manner of a stop, as the engine's
# trace shows it (EVV_ACCENT_TRACE): the German module counts its manners
# from one and the others from nought.
STOP_MANNER = {'dede': 1, 'dedx': 1}


def accent_line(tag, profile, chassis, tones):
    """The words of a map's accent line."""
    profile = profile or {}
    kind = MELODY_BY_HAND.get(tag) or melody_of(profile)
    if tones:
        kind = 'tone'
    elif kind == 'tone':
        kind = 'flat'
    q = QUESTION_BY_HAND.get(tag) or question_of(profile)
    i = profile.get('intonation') or {}
    wide = RANGE.get(((i.get('pitch_range') or 'medium').split() or ['medium'])[0].strip(',:;').lower(), 1.0)
    out = collections.OrderedDict()
    out['f0'] = 'own'
    if kind == 'tone':
        out['range'] = int(round(100 * wide))
        out['level'] = 30
        out['decl'] = 6
        out['declmax'] = 25
        out['lag'] = 70
        out['lead'] = 15
        out['fs'] = -6
        out['fq'] = 6
        out['qreg'] = 18
        out['fc'] = 4
        out['fe'] = 0
        out['fw'] = -4
        out['span'] = 1
    else:
        m = MELODY[kind]
        out['range'] = int(round(90 * wide))
        out['shape'] = m['shape']
        out['accent'] = int(round(m['accent'] * wide))
        out['accent2'] = int(round(m['accent2'] * wide))
        out['unstressed'] = m['unstressed']
        out['decl'] = 8
        out['declmax'] = 30
        out['fs'] = -18 if kind != 'edge' else -22
        out['fw'] = -12
        out['fc'] = 14 if kind != 'peak' else 10
        out['fe'] = -12
        qq = QUESTION[q]
        out['fq'] = int(round(qq['fq'] * (wide if qq['fq'] > 0 else 1.0)))
        out['qreg'] = qq['qreg']
        out['span'] = qq['span']
        if 'qfall' in qq:
            out['qfall'] = qq['qfall']
    out.update(rhythm_of(profile, chassis))
    out['stop'] = STOP_MANNER.get(chassis, 0)
    return out, kind, q


# ---- tones ---------------------------------------------------------------------

def T(points, **more):
    d = collections.OrderedDict()
    d['p'] = ','.join('%d:%d' % p for p in points)
    d.update(more)
    return d


# Each tone as eSpeak NG names it, and the pitch it is given: where in the
# syllable's vowel (per cent) the voice is to be at which level. The shapes
# are the citation shapes of the literature with their timing: Xu (1997) for
# Mandarin, where the rise of the second tone waits for the first third of
# the syllable and the fourth tone's peak comes just after its start; Bauer
# and Benedict (1997) for Cantonese; Brunelle (2009) and Kirby (2011) for
# Vietnamese, north, centre and south; Watkins (2001) for Burmese.
TONES = {
    'cmn': collections.OrderedDict([
        ('55', T([(0, 48), (100, 50)])),
        ('35', T([(0, 31), (30, 29), (100, 50)], dur=106)),
        ('214', T([(0, 23), (45, 10), (100, 38)], dur=125, creak=40, cfrom=30, cto=65)),
        ('21', T([(0, 23), (65, 11), (100, 10)], dur=92, creak=25, cfrom=55, cto=100)),
        ('51', T([(0, 50), (12, 52), (100, 12)], dur=90)),
        ('53', T([(0, 50), (12, 52), (100, 30)], dur=85)),
        ('11', T([(0, 22), (100, 12)], dur=62, weak=75, av=-3)),
        ('22', T([(0, 32), (100, 22)], dur=62, weak=75, av=-3)),
        ('33', T([(0, 36), (100, 30)], dur=62, weak=75, av=-3)),
        ('44', T([(0, 30), (100, 40)], dur=62, weak=75, av=-3)),
    ]),
    'yue': collections.OrderedDict([
        ('1', T([(0, 50), (100, 50)])),
        ('7', T([(0, 50), (100, 32)])),
        ('2', T([(0, 22), (35, 22), (100, 50)], dur=108)),
        ('3', T([(0, 30), (100, 30)])),
        ('4', T([(0, 22), (100, 10)], creak=25, cfrom=60, cto=100)),
        ('5', T([(0, 20), (35, 20), (100, 32)], dur=108)),
        ('6', T([(0, 22), (100, 21)])),
    ]),
    'hak': collections.OrderedDict([
        ('1', T([(0, 20), (30, 20), (100, 40)])),
        ('2', T([(0, 12), (100, 10)])),
        ('3', T([(0, 32), (100, 11)])),
        ('4', T([(0, 49), (100, 50)])),
        ('5', T([(0, 22), (100, 20)], dur=60, stop=30)),
        ('6', T([(0, 50), (100, 48)], dur=60, stop=30)),
    ]),
    'vi': collections.OrderedDict([
        ('1', T([(0, 33), (100, 32)])),
        ('7', T([(0, 33), (100, 26)])),
        ('2', T([(0, 22), (100, 11)], brth=20)),
        ('3', T([(0, 32), (35, 32), (100, 50)])),
        ('4', T([(0, 30), (50, 11), (100, 30)], creak=25, cfrom=35, cto=65, dur=110)),
        ('5', T([(0, 32), (40, 26), (60, 30), (100, 52)], creak=70, cfrom=35, cto=60)),
        ('6', T([(0, 30), (100, 12)], dur=65, creak=60, cfrom=50, cto=100, stop=35)),
    ]),
    'vi-vn-x-central': collections.OrderedDict([
        ('1', T([(0, 32), (100, 48)])),
        ('7', T([(0, 32), (100, 40)])),
        ('2', T([(0, 33), (100, 30)])),
        ('3', T([(0, 12), (60, 12), (100, 30)], creak=20, cfrom=0, cto=40)),
        ('4', T([(0, 30), (60, 11), (100, 20)], creak=30, cfrom=40, cto=80, dur=110)),
        ('5', T([(0, 30), (60, 11), (100, 20)], creak=30, cfrom=40, cto=80, dur=110)),
        ('6', T([(0, 22), (60, 11), (100, 20)], creak=50, cfrom=40, cto=100, dur=80)),
    ]),
    'vi-vn-x-south': collections.OrderedDict([
        ('1', T([(0, 34), (100, 33)])),
        ('7', T([(0, 34), (100, 27)])),
        ('2', T([(0, 22), (100, 11)])),
        ('3', T([(0, 32), (30, 32), (100, 50)])),
        ('4', T([(0, 22), (50, 10), (100, 40)], dur=112)),
        ('5', T([(0, 22), (50, 10), (100, 40)], dur=112)),
        ('6', T([(0, 22), (60, 11), (100, 20)], dur=90)),
    ]),
    'my': collections.OrderedDict([
        ('1', T([(0, 12), (80, 12), (100, 16)], dur=105)),
        ('2', T([(0, 47), (70, 50), (100, 34)], dur=115, brth=15)),
        ('3', T([(0, 52), (100, 30)], dur=72, creak=60, cfrom=40, cto=100, stop=25)),
        ('4', T([(0, 50), (100, 47)], dur=48, stop=40)),
    ]),
    'shn': collections.OrderedDict([
        ('1', T([(0, 20), (30, 20), (100, 40)])),
        ('2', T([(0, 12), (100, 10)])),
        ('3', T([(0, 32), (70, 31), (100, 22)])),
        ('4', T([(0, 49), (100, 50)])),
        ('5', T([(0, 42), (100, 20)], dur=70, creak=60, cfrom=40, cto=100, stop=25)),
        ('6', T([(0, 30), (50, 42), (100, 30)], dur=110)),
    ]),
    'pa': collections.OrderedDict([
        # the low tone: the pitch falls steeply from high and comes part of the way back
        ('+', T([(0, 45), (35, 12), (100, 30)], dur=110)),
    ]),
    'chr': collections.OrderedDict([
        ('2', T([(0, 22), (100, 21)])),
        ('3', T([(0, 33), (100, 35)])),
        ('23', T([(0, 22), (100, 35)], dur=110)),
        ('32', T([(0, 38), (100, 20)], dur=110)),
        ('1', T([(0, 22), (100, 10)], dur=110)),
        ('4', T([(0, 34), (100, 50)], dur=110)),
        ('43', T([(0, 48), (100, 30)])),
    ]),
}
TONES['cmn-latn-pinyin'] = TONES['cmn']
TONES['yue-latn-jyutping'] = TONES['yue']

# A syllable to a word, each with its own tone, where the language's words
# are its syllables.
WORDS_APART = ('cmn', 'cmn-latn-pinyin', 'yue', 'yue-latn-jyutping', 'hak', 'vi', 'vi-vn-x-central',
               'vi-vn-x-south', 'my', 'shn')


# How many phones may begin a syllable there: two where a consonant may have
# a glide after it (Mandarin nia, gua), one where it may not, and then the
# pairs that may all the same (Cantonese kw).
ONSET = {'yue': 1, 'yue-latn-jyutping': 1, 'hak': 1, 'vi': 1, 'vi-vn-x-central': 1, 'vi-vn-x-south': 1,
         'my': 2, 'shn': 2, 'cmn': 2, 'cmn-latn-pinyin': 2}
CLUSTERS = {'yue': (('k', 'w'), ('g', 'w')), 'yue-latn-jyutping': (('k', 'w'), ('g', 'w')),
            'vi': (('k', 'w'),), 'vi-vn-x-central': (('k', 'w'),), 'vi-vn-x-south': (('k', 'w'),)}


def tones_of(tag):
    return TONES.get(tag)


def weak_tones_of(tag):
    """The tones a light syllable has: those said to give way."""
    return [name for name, t in (TONES.get(tag) or {}).items() if int(t.get('weak', 100)) < 100]


def load_profile(tag):
    p = os.path.join(PROFILES, tag + '.json')
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding='utf-8'))
    except ValueError:
        return None


def main(argv):
    import glob
    tags = argv or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(PROFILES, '*.json')))
    for tag in tags:
        prof = load_profile(tag)
        line, kind, q = accent_line(tag, prof, 'dedx', tones_of(tag))
        print('%-18s %-5s %-9s %s' % (tag, kind, q, ' '.join('%s=%s' % kv for kv in line.items())))
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))
