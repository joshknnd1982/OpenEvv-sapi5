#!/usr/bin/env python3
"""Sounds a module lacks, made out of the phones it has.

An openevv module has the phones of one language. A language eSpeak NG reads
has sounds of its own, and each of them is said here as the module's nearest
phone together with a definition of how the sound differs from that phone: so
many per cent in each formant, a voice onset so many milliseconds after the
release, a tap, a breath. The accent layer of the engine (openevv/src/accent)
reads the definitions and changes the frames the module asks the synthesiser
for. Nothing is said about a sound the module already has.

Where the numbers come from:

  vowels      formants a man's voice gives each vowel of the IPA chart, from
              the literature on many languages (VOWEL below), or what was
              published for the language itself where its profile has it;
              held against the module's own vowels as they were measured
              (engine/accent/chassis), and written as the ratio between them
  consonants  the place a consonant is made at moves the formants of what is
              beside it to a locus (LOCUS); the ratio between the locus of
              the sound and the locus of the module's phone is what is
              written. Voice onset times are Lisker and Abramson's (1964)
              and Cho and Ladefoged's (1999) for the kinds of stop, or the
              language's own from its profile
  noise       the module's own fricatives, as measured, moved towards the
              sound wanted

    python engine/accent/sounds.py show dedx  t`  ...     what a sound becomes
"""
import collections
import json
import math
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import espeak_phonemes as EP  # noqa: E402

# ---- vowels ------------------------------------------------------------------

# F1, F2, F3 of each vowel for an adult man, in hertz. These are the middle of
# what is reported across languages rather than the corners of the cardinal
# vowel chart, which nobody's speech reaches: Peterson and Barney (1952) and
# Hillenbrand et al. (1995) for the vowels English has, Catford (1988) for the
# shape of the chart, and single-language studies for the rest.
VOWEL = {
    'i': (280, 2250, 2950), 'y': (290, 1850, 2250), 'ɨ': (320, 1600, 2450), 'ʉ': (320, 1450, 2250),
    'ɯ': (340, 1350, 2450), 'u': (310, 800, 2350),
    'ɪ': (400, 1950, 2600), 'ʏ': (380, 1650, 2250), 'ʊ': (420, 1000, 2350),
    'e': (400, 2050, 2700), 'ø': (400, 1550, 2200), 'ɘ': (430, 1650, 2500), 'ɵ': (430, 1350, 2300),
    'ɤ': (460, 1250, 2450), 'o': (420, 800, 2450),
    'ə': (500, 1450, 2500),
    'ɛ': (560, 1800, 2550), 'œ': (530, 1500, 2350), 'ɜ': (560, 1450, 2500), 'ɞ': (560, 1300, 2350),
    'ʌ': (620, 1200, 2500), 'ɔ': (560, 900, 2500),
    'æ': (700, 1700, 2450), 'ɐ': (680, 1350, 2500),
    'a': (770, 1350, 2500), 'ä': (770, 1350, 2500), 'ɶ': (750, 1450, 2400), 'ɑ': (730, 1100, 2500),
    'ɒ': (680, 900, 2450),
    'ɚ': (480, 1350, 1700), 'ɝ': (500, 1350, 1700),
}

# What a module's vowel phones are, by the letter of the chart nearest each.
# The labels are EP's, put right where the measurement says otherwise: both
# German a's are the same open central vowel, one long and one short.
LABEL_FIX = {
    'dede': {'a': 'a', 'A': 'a', 'E:': 'ɛ', 'R': 'ɐ'},
    'frfr': {'a': 'a', 'A': 'a', 'x': 'ə'},
    'enus': {'a': 'ɑ', 'c': 'ɔ', 'x': 'ə', 'X': 'ɨ', 'H': 'ʌ', 'R': 'ɝ', 'e': 'e', 'o': 'o'},
    # the British module's c is the vowel of thought, which it says as a
    # close-mid [o] (440, 750 Hz), not as an open-mid one
    # and its u is the fronted vowel of goose (F2 1,480 Hz), a central [ʉ]
    'engb': {'a': 'ɑ', 'c': 'o', '@': 'ɒ', 'x': 'ə', 'X': 'ɪ', 'H': 'ʌ', 'R': 'ɜ', 'e': 'e', 'o': 'o', 'u': 'ʉ'},
}

# Vowel phones of a module that are not one steady vowel, or not a vowel of
# the module's own speech at all, and so are nothing to build on.
NOT_A_BASE = {
    'dede': ('aj', 'aw', 'oj', 'a~', 'E~', 'o~', 'oe~', 'R'),
    'frfr': ('a~', 'E~', 'o~', 'oe~', 'OE~', 'I', 'U', 'Y', 'x'),
    'enus': ('Y', 'W', 'O', 'Xx', 'Aa', 'H@', 'a@', 'c@', '@', 'e', 'o'),
    'engb': ('Y', 'W', 'O', 'Xx', 'Aa', 'H@', 'a@', 'c@', 'e', 'o'),
    'itit': (), 'eses': (), 'esus': (),
}

# How long a vowel lasts, against the vowel of a language that has only one
# length: a short vowel and a long one are as 1 to 1.8, which is the middle of
# what is reported for languages that tell them apart (Lehtonen 1970 for
# Finnish, 1 to 2.2; Fatima and Aden 2003 for Urdu, 1 to 1.8; and see each
# language's profile).
LENGTH = {'short': 0.72, 'half': 1.0, 'long': 1.3, 'plain': 1.0, 'brief': 0.45, 'over': 1.55}

# The modules IBM wrote for languages of the dental kind: their t, d and n
# are made with the tongue on the teeth already.
DENTAL_MODULES = ('itit', 'eses', 'esus', 'frfr')


def bark(hz):
    return 26.81 * hz / (1960.0 + hz) - 0.53


def vowel_far(a, b):
    """How far apart two vowels are to the ear, roughly: in barks, the first
    two formants counting for most."""
    return math.sqrt((bark(a[0]) - bark(b[0])) ** 2 + (bark(a[1]) - bark(b[1])) ** 2
                     + 0.3 * (bark(a[2]) - bark(b[2])) ** 2)


# ---- consonants ----------------------------------------------------------------

P = EP  # places and manners are EP's

# Where each place of articulation sends the second and third formants of the
# sounds beside it, for a man's voice: the locus. Delattre, Liberman and
# Cooper (1955) for the three places English has, Stevens (1998) and
# Ladefoged and Maddieson (1996) for the others. A retroflex brings the third
# formant down to meet the second; a palatal sends the second up to the third.
LOCUS = {
    EP.P_BILAB: (900, 2300), EP.P_LABDENT: (1000, 2300), EP.P_DENT: (1550, 2650), EP.P_ALV: (1700, 2600),
    EP.P_POSTALV: (1850, 2450), EP.P_RETRO: (1550, 2050), EP.P_ALVPAL: (2200, 2850), EP.P_PAL: (2300, 2900),
    EP.P_VEL: (1700, 2200), EP.P_UVU: (1150, 2400), EP.P_PHAR: (1200, 2400), EP.P_GLOT: (1500, 2500),
    EP.P_LABVEL: (750, 2250),
}

# Voice onset time in milliseconds after the release, by place, for a stop
# that is not aspirated and for one that is. Medians of Cho and Ladefoged's
# (1999) eighteen languages, and Lisker and Abramson (1964).
VOT_PLAIN = {EP.P_BILAB: 13, EP.P_LABDENT: 13, EP.P_DENT: 16, EP.P_ALV: 17, EP.P_POSTALV: 20,
             EP.P_RETRO: 12, EP.P_ALVPAL: 30, EP.P_PAL: 32, EP.P_VEL: 28, EP.P_UVU: 30, EP.P_GLOT: 0,
             EP.P_LABVEL: 28, EP.P_PHAR: 20}
VOT_ASPIRATED = {EP.P_BILAB: 65, EP.P_LABDENT: 65, EP.P_DENT: 68, EP.P_ALV: 70, EP.P_POSTALV: 72,
                 EP.P_RETRO: 60, EP.P_ALVPAL: 75, EP.P_PAL: 75, EP.P_VEL: 85, EP.P_UVU: 85, EP.P_GLOT: 0,
                 EP.P_LABVEL: 85, EP.P_PHAR: 60}

# Sounds that carry their own formants: F1, F2, F3 for a man's voice.
SONORANT = {
    'm': (280, 1000, 2300), 'ɱ': (280, 1050, 2300), 'n': (280, 1600, 2600), 'ɳ': (300, 1500, 2050),
    'ɲ': (280, 2200, 2800), 'ŋ': (280, 1700, 2200), 'ɴ': (320, 1150, 2400),
    'l': (350, 1300, 2700), 'ɫ': (420, 900, 2700), 'ʎ': (300, 2000, 2800), 'ɭ': (400, 1400, 2100),
    'ʟ': (380, 1100, 2400),
    'j': (280, 2200, 2900), 'w': (300, 700, 2300), 'ɥ': (280, 1800, 2200), 'ʋ': (320, 1000, 2300),
    'ɰ': (320, 1300, 2300), 'ɹ': (420, 1250, 1650), 'ɻ': (450, 1300, 1500),
    'r': (490, 1370, 2300), 'ɾ': (500, 1400, 2300), 'ɽ': (480, 1400, 1950), 'ɺ': (420, 1450, 2500),
    'ʀ': (480, 1150, 2400), 'ʁ': (480, 1200, 2400),
}
NASALS = ('m', 'ɱ', 'n', 'ɳ', 'ɲ', 'ŋ', 'ɴ')
LATERALS = ('l', 'ɫ', 'ʎ', 'ɭ', 'ʟ')
GLIDES = ('j', 'w', 'ɥ', 'ʋ', 'ɰ', 'ɹ', 'ɻ')
TRILLS = ('r', 'ʀ')
TAPS = ('ɾ', 'ɽ', 'ɺ')

# Phones a module has that EP does not name, and what they are: allophones
# of the module's own language, which a pronunciation may ask for outright.
# The Italian and Spanish modules have a tap and a trill, each made as IBM
# made them: a voiced sound whose loudness dips once, or twice 40 ms apart.
EXTRA_CONS = {
    'itit': {'G': 'ŋ', 'r': 'ɾ', 'R': 'r'},
    'eses': {'B': 'β', 'D': 'ð', 'G': 'ɣ', 'r': 'ɾ', 'R': 'r'},
    'esus': {'B': 'β', 'D': 'ð', 'G': 'ɣ', 'r': 'ɾ', 'R': 'r'},
    'frfr': {'?': 'ʔ'},
    'enus': {'?': 'ʔ', 'F': 'ɾ', 'l': 'ɫ'},
    'engb': {'L': 'ɫ'},
}

# The module's phone to make a sound out of, in order of choice, where the
# nearest in formants is not the nearest to the ear: a palatal nasal is an n
# with the tongue further back, not the ng its formants look like.
MADE_OF = {
    'ɲ': ('ɲ', 'n', 'ŋ'), 'ɳ': ('ɳ', 'n'), 'ŋ': ('ŋ', 'n'), 'ɴ': ('ɴ', 'ŋ', 'n'), 'ɱ': ('ɱ', 'm'),
    'm': ('m',), 'n': ('n',),
    'ʎ': ('ʎ', 'l', 'ɫ'), 'ɭ': ('ɭ', 'l', 'ɫ'), 'ɫ': ('ɫ', 'l'), 'l': ('l', 'ɫ'), 'ʟ': ('ɫ', 'l'),
    'j': ('j', 'ʝ'), 'w': ('w',), 'ɥ': ('ɥ', 'j', 'w'), 'ɰ': ('ɰ', 'w', 'ɣ'),
    'ɹ': ('ɹ', 'ɻ', 'ʁ', 'l', 'w'), 'ɻ': ('ɻ', 'ɹ', 'ʁ', 'l', 'w'),
    'r': ('r', 'ɾ', 'l', 'ɫ'), 'ɾ': ('ɾ', 'r', 'l', 'ɫ'), 'ɽ': ('ɽ', 'ɾ', 'r', 'l', 'ɫ'),
    'ɺ': ('ɾ', 'l', 'r'), 'ʀ': ('ʀ', 'ʁ', 'r', 'ɣ', 'l'), 'ʁ': ('ʁ', 'ʀ', 'ɣ', 'r', 'l'),
}

# The modules were not all given the same noise for the same sound, so noise
# is said by the module's own s and sh and what lies between them. For each
# fricative: the sibilant it is nearest, how far it is from that towards the
# other (0 the module's s, 1 its sh), and its formants.
HISS = {
    's': (0.0, None), 'z': (0.0, None),
    'ʃ': (1.0, None), 'ʒ': (1.0, None),
    'ɕ': (0.55, (300, 2200, 2850)), 'ʑ': (0.55, (300, 2200, 2850)),
    'ʂ': (1.25, (320, 1600, 2050)), 'ʐ': (1.25, (320, 1600, 2050)),
}


class Language(object):
    """What is known of the language the sounds are for."""

    def __init__(self, tag, profile=None, ipas=()):
        self.tag = tag
        self.profile = profile or {}
        self.formants = {}
        self.vot = {}
        vf = self.profile.get('vowel_formants') or {}
        for k, v in (vf.get('values') or {}).items():
            if isinstance(v, (list, tuple)) and len(v) >= 2 and v[0] and v[1]:
                f3 = v[2] if len(v) > 2 and v[2] else None
                self.formants[unicodedata.normalize('NFD', k)] = (float(v[0]), float(v[1]), f3)
        vo = self.profile.get('voice_onset_time_ms') or {}
        for k, v in (vo.get('values') or {}).items():
            if isinstance(v, (int, float)):
                self.vot[unicodedata.normalize('NFD', k)] = float(v)
        # whether the language tells long vowels from short, and aspirated
        # stops from plain ones, by what eSpeak NG writes for it
        length = (self.profile.get('length') or {}).get('vowel')
        self.long_vowels = bool(length)
        # a language of tones gives every syllable the time its tone wants
        self.tonal = 'lexical tone' in ((self.profile.get('tone') or {}).get('type') or '')
        self.aspirates = False
        self.ejectives = False
        n_long = n_asp = 0
        for ipa in ipas:
            for u in EP.units(ipa):
                if u.vowel and u.long:
                    n_long += 1
                if not u.vowel and 'ʰ' in u.mods and u.base in ('p', 't', 'k', 'ʈ', 'c', 'q', 't̪'):
                    n_asp += 1
        if ipas and 'length' not in self.profile:
            # nobody has said: what eSpeak NG writes is all there is to go by
            self.long_vowels = n_long >= 2
        self.aspirates = n_asp >= 2
        # a language whose plain p t k are aspirated, as English and German are
        self.aspirating = tag.split('-')[0] in ASPIRATING and not self.aspirates
        # whether t, d and n are made on the teeth: the profile writes them so
        cons = [unicodedata.normalize('NFD', c) for c in (self.profile.get('consonants') or [])]
        self.dental = any(c.startswith('t̪') for c in cons)

    def published(self, base, long_):
        """The language's own formants for a vowel, if its profile has them."""
        if not self.formants:
            return None
        keys = [base + 'ː', base] if long_ else [base, base + 'ː']
        for k in keys:
            k = unicodedata.normalize('NFD', k)
            if k in self.formants:
                return self.formants[k]
        return None


# Languages whose voiceless stops are aspirated before a stressed vowel
# without eSpeak NG writing the aspiration: Germanic but for Dutch and
# Afrikaans, the Celtic languages, Persian, Kurdish, the Turkic languages,
# Mongolian. Not Swahili, whose aspiration is a matter of some coastal
# varieties; not Setswana, whose plain stops are unaspirated or ejective
# beside the aspirated ones; not Greenlandic, whose stops are unaspirated.
ASPIRATING = set('''en da nb no sv is fo lb pdc cy ga gd fa ku tr az tk uz kk ky tt ba cv crh kaa nog ug
                    mn'''.split())


class Chassis(object):
    """A module, as it was measured."""

    def __init__(self, tag, template=None):
        self.tag = tag
        self.template = template or tag
        path = os.path.join(HERE, 'chassis', tag + '.json')
        if not os.path.exists(path):
            path = os.path.join(HERE, 'chassis', self.template + '.json')
        self.phones = json.load(open(path, encoding='utf-8'))['phones']
        t = EP.TEMPLATES[self.template]
        self.t = t
        self.labels = dict(t.vowels)
        self.labels.update(LABEL_FIX.get(self.template, {}))
        self.cons = dict(t.consonants)
        self.cons.update(EXTRA_CONS.get(self.template, {}))
        self.vowels = {}
        for ph, ipa in self.labels.items():
            m = self.phones.get(ph)
            if m and m.get('kind') == 'vowel' and ph not in NOT_A_BASE.get(self.template, ()):
                self.vowels[ph] = dict(ipa=ipa, f=m['f'][:3], ms=m.get('ms') or 100,
                                       sound=m.get('ms_sound') or (m.get('ms') or 100) + 30,
                                       steady=(m.get('ms_steady') or 60) / float(m.get('ms') or 100))
        # How long the module's vowels sound. A module for a language with
        # lax vowels and tense ones has short vowels and long; the length of
        # a vowel that is neither is between the two.
        lengths = sorted(v['sound'] for v in self.vowels.values())
        if lengths:
            middle = lengths[len(lengths) // 2]
            low = [x for x in lengths if x < middle * 0.8]
            high = [x for x in lengths if x >= middle * 0.8]
            if len(low) >= 3 and len(high) >= 3:
                self.plain_ms = (low[len(low) // 2] + high[len(high) // 2]) / 2.0
            else:
                self.plain_ms = float(middle)
        else:
            self.plain_ms = 120.0
        self.dental = self.template in DENTAL_MODULES
        # how much smaller or larger than the reference the module's voice is
        logs = []
        for ph, v in self.vowels.items():
            ref = VOWEL.get(v['ipa'])
            if ref and v['ipa'] in ('i', 'e', 'a', 'o', 'u', 'ɛ', 'ɔ'):
                for k in (0, 1, 2):
                    logs.append(math.log(v['f'][k] / float(ref[k])))
        self.scale = math.exp(sum(logs) / len(logs)) if logs else 1.0

    def measured(self, phone):
        return self.phones.get(phone) or {}

    def has(self, phone):
        return phone in self.phones

    def consonant_for(self, ipa):
        for ph, i in self.cons.items():
            if i == ipa or (ipa == 'ɡ' and i == 'g') or (ipa == 'g' and i == 'ɡ'):
                if self.has(ph):
                    return ph
        return None


def percent(x):
    return int(round(100.0 * x))


def near(p, tolerance=6):
    """A ratio so near to none that it is not worth saying."""
    return abs(p - 100) <= tolerance


class Part(object):
    def __init__(self, name, params=None, made=''):
        self.name = name
        self.params = collections.OrderedDict(params or {})
        self.made = made
        self.sound = None

    def text(self):
        return '%s%s%s' % (self.made, self.name, '=' + self.sound if self.sound else '')


class Designer(object):
    def __init__(self, chassis, language):
        self.c = chassis
        self.lang = language
        self.defs = collections.OrderedDict()     # text of a definition -> id
        self.notes = {}                           # id -> what it is
        self.says = set()

    # ---- definitions ----

    def _id(self, params, note):
        keys = ' '.join('%s=%s' % kv for kv in params.items())
        if keys not in self.defs:
            sid = 's%d' % (len(self.defs) + 1)
            self.defs[keys] = sid
            self.notes[sid] = note
        return self.defs[keys]

    def finish(self, parts, note):
        """Gives every part that differs from its phone a definition, and
        notes what the module says in place of a phone it is given."""
        out = []
        for p in parts:
            if p.params:
                p.sound = self._id(p.params, note)
            m = self.c.measured(p.name)
            said = m.get('said')
            if not p.made and said and said != [p.name] and len(said) <= 4:
                self.says.add((p.name, tuple(said)))
            out.append(p)
        return out

    # ---- vowels ----

    def vowel_target(self, base, long_):
        pub = self.lang.published(base, long_)
        ref = VOWEL.get(base)
        if pub is not None:
            f3 = pub[2] if pub[2] else (ref[2] if ref else 2500)
            t = (pub[0], pub[1], f3)
            # what was published is held to within a fifth of what the vowel
            # usually is, against a slip in a table
            if ref:
                t = tuple(min(max(t[k], ref[k] * 0.8), ref[k] * 1.25) for k in (0, 1, 2))
            return tuple(x * self.c.scale for x in t), True
        if ref is None:
            return None, False
        return tuple(x * self.c.scale for x in ref), False

    def vowel_base(self, base, target, long_):
        """The module's vowel to build on: the one of the same name if there
        is one, else the nearest, a long one for a long vowel where two are
        as near."""
        same = [ph for ph, v in self.c.vowels.items() if v['ipa'] == base]
        if same:
            # a steady vowel before one that is mostly movement, then the
            # longer for a long vowel and the shorter for a short one
            same.sort(key=lambda ph: (self.c.vowels[ph]['steady'] < 0.45,
                                      -self.c.vowels[ph]['sound'] if long_ else self.c.vowels[ph]['sound']))
            return same[0], True
        best, how = None, None
        for ph, v in self.c.vowels.items():
            if v['ipa'] in EP.RHOTIC_VOWELS and base not in EP.RHOTIC_VOWELS:
                continue
            d = vowel_far(v['f'], target)
            # a vowel of the wrong length costs a little: the length can be
            # put right but the module's own timing is the better for it
            if long_ != (v['sound'] >= self.c.plain_ms):
                d += 0.35
            # a vowel that is mostly movement (a reduced vowel, as English
            # has) does not hold a target when it is made longer
            if v['steady'] < 0.45:
                d += 1.0
            if how is None or d < how:
                best, how = ph, d
        return best, False

    def vowel_ms(self, u, long_=False):
        """How long the vowel is to sound, in the module's own measure."""
        if 'ˑ' in u.mods:
            k = 'half'
        elif '̆' in u.mods or u.nonsyllabic:
            k = 'brief'
        elif u.long or long_:
            k = 'long'
        else:
            k = 'short' if self.lang.long_vowels else 'plain'
        return self.c.plain_ms * LENGTH[k] * (1.25 if self.lang.tonal else 1.0)

    def lasting(self, ph, want, params, tolerance=12):
        """The length of the phone's stretch, in per cent, that makes the
        vowel sound for `want' milliseconds: what is outside the stretch,
        the movement into the consonant after it, stays as long as it was."""
        m = self.c.vowels[ph]
        stretch = float(m['ms'])
        r = percent((stretch + want - m['sound']) / stretch)
        if not near(r, tolerance):
            params['dur'] = max(40, min(300, r))

    def vowel(self, u, long_=False, note=None):
        base = u.base
        long_ = long_ or u.long
        target, published = self.vowel_target(base, long_)
        if target is None:
            return []
        ph, same = self.vowel_base(base, target, long_)
        if ph is None:
            return []
        m = self.c.vowels[ph]
        params = collections.OrderedDict()
        # A vowel of the module's with the same name is left as it is, since
        # one letter of the IPA covers a range and the module's is a real
        # language's -- unless it is far from where the letter is anywhere
        # (more than 1.3 barks: the fronted u of American English).
        if not same or published or vowel_far(m['f'], target) > 1.3:
            for k in (0, 1, 2):
                r = percent(target[k] / float(m['f'][k]))
                tol = 8 if same else 5
                if not near(r, tol):
                    params['f%d' % (k + 1)] = max(50, min(200, r))
        self.lasting(ph, self.vowel_ms(u, long_), params)
        if u.nasal:
            params['nas'] = 100
        if u.voiceless:
            params['whisper'] = 44
        if '̤' in u.mods:
            params['oq'] = 75
            params['tl'] = 14
            params['ah'] = 6
        if '̰' in u.mods:
            params['creak'] = 60
        if '˞' in u.mods and base not in EP.RHOTIC_VOWELS:
            params['f3'] = min(params.get('f3', 100), 70)
        return [Part(ph, params)]

    def glide_vowel(self, first, last, long_, note):
        """A diphthong that falls: one vowel of the module, moving from
        where the first vowel is to where the last is."""
        t1, _ = self.vowel_target(first.base, False)
        t2, _ = self.vowel_target(last.base, False)
        if t1 is None or t2 is None:
            return None
        ph, same = self.vowel_base(first.base, t1, True)
        if ph is None:
            return None
        m = self.c.vowels[ph]
        params = collections.OrderedDict()
        for k in (0, 1, 2):
            r = percent(t1[k] / float(m['f'][k]))
            if not same and not near(r, 5):
                params['f%d' % (k + 1)] = max(50, min(200, r))
        for k in (0, 1, 2):
            # a diphthong sets out for its second vowel and stops short of it
            goal = t1[k] + (t2[k] - t1[k]) * 0.85
            params['g%d' % (k + 1)] = max(40, min(250, percent(goal / float(m['f'][k]))))
        params['glide'] = 1
        self.lasting(ph, self.c.plain_ms * (LENGTH['over'] if long_ else LENGTH['long']), params)
        if first.nasal or last.nasal:
            params['nas'] = 100
        return [Part(ph, params)]

    # ---- consonants ----

    def place_ratio(self, base_place, place, params, palatal=False, labial=False, pharyngeal=False, velar=False):
        b2, b3 = LOCUS[base_place]
        t2, t3 = LOCUS[place]
        if palatal:
            t2, t3 = max(t2, 2000 if place in (EP.P_BILAB, EP.P_LABDENT) else 2200), max(t3, 2800)
        if labial:
            t2, t3 = t2 * 0.8, t3 * 0.92
        if pharyngeal or velar:
            t2 = t2 * 0.75
        r2, r3 = percent(t2 / float(b2)), percent(t3 / float(b3))
        if not near(r2, 5):
            params['f2'] = max(50, min(220, r2))
        if not near(r3, 5):
            params['f3'] = max(60, min(140, r3))
        if place == EP.P_RETRO and base_place != EP.P_RETRO:
            params['f4'] = 88
        if pharyngeal or place == EP.P_UVU and base_place != EP.P_UVU or place == EP.P_PHAR:
            params['f1'] = 118

    def nearest_stop(self, place, voiced):
        """The module's stop nearest a place, of the voicing wanted."""
        best, how = None, None
        for ph, ipa in self.c.cons.items():
            f = EP.cons_features(ipa)
            if f is None or f[1] != EP.STOP or f[0] == EP.P_GLOT or not self.c.has(ph):
                continue
            if f[2] != voiced:
                continue
            said = self.c.measured(ph).get('said')
            if said and said != [ph]:
                continue
            d = abs(f[0] - place)
            # a palatal stop is a tongue-blade sound: t, not k
            if place in (EP.P_PAL, EP.P_ALVPAL) and f[0] == EP.P_ALV:
                d = 0.5
            if how is None or d < how:
                best, how = (ph, f[0]), d
        return best

    def stop(self, u, feats):
        place, _m, voiced = feats
        mods = u.mods
        aspirated = 'ʰ' in mods and not voiced
        breathy = ('ʱ' in mods) or ('ʰ' in mods and voiced) or ('̤' in mods)
        ejective = 'ʼ' in mods or "'" in mods
        if place == EP.P_ALV and ('̪' in mods or self.lang.dental):
            place = EP.P_DENT
        got = self.nearest_stop(place, voiced)
        if got is None:
            got = self.nearest_stop(place, 1 - voiced)
            if got is None:
                return []
        ph, base_place = got
        if base_place == EP.P_ALV and self.c.dental:
            base_place = EP.P_DENT
        m = self.c.measured(ph)
        params = collections.OrderedDict()
        if place != base_place or u.palatal or 'ʷ' in mods or 'ˤ' in mods or 'ˠ' in mods:
            self.place_ratio(base_place, place, params, palatal=u.palatal, labial='ʷ' in mods,
                             pharyngeal='ˤ' in mods, velar='ˠ' in mods)
        # the burst
        if place == EP.P_RETRO and base_place != EP.P_RETRO:
            params['a4'] = 52
            params['a5'] = 42
        elif place in (EP.P_PAL, EP.P_ALVPAL) and base_place not in (EP.P_PAL, EP.P_ALVPAL):
            params['a3'] = 56
            params['a4'] = 56
        elif place == EP.P_DENT and base_place == EP.P_ALV:
            params['burst'] = -4
        elif place == EP.P_ALV and base_place == EP.P_DENT and not (
                u.palatal or 'ʷ' in mods or 'ˤ' in mods or 'ˠ' in mods):
            # too near to be worth saying
            params.pop('f2', None)
            params.pop('f3', None)
        elif place == EP.P_UVU and base_place != EP.P_UVU:
            params['burst'] = 3
        # the larynx
        own = m.get('vot')
        own0 = m.get('vot_initial')
        if not voiced:
            key = unicodedata.normalize('NFD', u.base + ('ʰ' if aspirated else ''))
            want = self.lang.vot.get(key)
            if want is None and '̪' not in u.base:
                want = self.lang.vot.get(unicodedata.normalize('NFD', u.base + '̪' + ('ʰ' if aspirated else '')))
            leave = False
            if want is None:
                if aspirated:
                    want = VOT_ASPIRATED[place]
                elif self.lang.aspirating and not ejective:
                    # as the module has it, if the module's stops are
                    # aspirated as well: where in the word a stop stands
                    # changes how much, and the module knows where
                    want = int(VOT_ASPIRATED[place] * 0.85)
                    leave = own0 is not None and own0 >= 45
                else:
                    want = VOT_PLAIN[place]
                if u.palatal and not aspirated:
                    want += 8
            want = int(round(max(0, want)))
            if ejective:
                params['ej'] = 60
                params['burst'] = params.get('burst', 0) + 6
            elif not leave:
                has = [x for x in (own, own0) if x is not None]
                if not has or max(abs(x - want) for x in has) > 9:
                    params['vot'] = want
                    if want >= 40:
                        params['asp'] = 50
        else:
            # A voiced stop. Where the language's b, d and g are voiced in
            # earnest, the voice is going behind the closure, and after a
            # silence it begins well before the stop lets go: Lisker and
            # Abramson's voicing lead, 60 to 110 ms in the languages they
            # measured. German and English begin the voice at the release,
            # and so do the modules written for them.
            key = unicodedata.normalize('NFD', u.base + ('ʱ' if breathy else ''))
            lead = self.lang.vot.get(key)
            if lead is None and breathy:
                lead = self.lang.vot.get(unicodedata.normalize('NFD', u.base + 'ʰ'))
            if lead is None:
                lead = self.lang.vot.get(unicodedata.normalize('NFD', u.base + '̪' + ('ʱ' if breathy else '')))
            weak = (m.get('shut_av') or 0) < 30
            if lead is not None and lead < 0:
                # measured in the language itself: whatever its voiceless
                # stops do, its voiced ones begin their voice this early
                params['voi'] = 1
                if -lead >= 20:
                    params['lead'] = int(min(110, -lead))
            elif (not self.lang.aspirating or breathy) and weak:
                params['voi'] = 1
                params['lead'] = 75
            if breathy:
                params['voi'] = 1
                params['brth'] = 90
                params['f0'] = -15
            if 'ɓɗʄɠʛ'.find(u.base) >= 0:
                params['impl'] = 1
                params['voi'] = 1
                params['burst'] = -8
        if '̚' in mods:
            params['noburst'] = 1
        if u.long:
            params['hold'] = 190
        elif 'ˑ' in mods:
            params['hold'] = 145
        parts = [Part(ph, params)]
        if 'ʷ' in mods:
            w = self.sonorant(EP.Unit('w', ''), brief=True)
            parts += w
        return parts

    def sonorant_base(self, base):
        for ipa in MADE_OF.get(base, (base,)):
            ph = self.c.consonant_for(ipa)
            if ph is None:
                continue
            said = self.c.measured(ph).get('said')
            if said and said != [ph]:
                continue
            if self.c.measured(ph).get('f'):
                return ph, ipa
        return None, None

    def sonorant(self, u, brief=False):
        base = u.base
        mods = u.mods
        if base not in SONORANT:
            return []
        params = collections.OrderedDict()
        if base == 'ʋ':
            # a v with the friction taken out of it
            v = self.c.consonant_for('v')
            if v is not None and self.c.consonant_for('ʋ') is None:
                params['af'] = -14
                if brief:
                    params['hold'] = 55
                return [Part(v, params)]
        target = [x * self.c.scale for x in SONORANT[base]]
        if u.palatal:
            target[1] = max(target[1], 2100 * self.c.scale)
            target[2] = max(target[2], 2750 * self.c.scale)
        if 'ˠ' in mods or 'ˤ' in mods:
            target[1] *= 0.72
        if 'ʷ' in mods:
            target[1] *= 0.85
            target[2] *= 0.93
        plain = not (u.palatal or 'ˠ' in mods or 'ˤ' in mods or 'ʷ' in mods)
        ph, made_of = self.sonorant_base(base)
        if ph is None:
            return []
        if made_of != base or not plain:
            if made_of != base:
                # a tap or a trill made out of something that is neither:
                # the loudness dips as the tongue shuts the mouth
                if base in TRILLS and made_of not in TRILLS:
                    params['tap'] = 2 if made_of in TAPS else 3
                    params['tapms'] = 18
                    if made_of in TAPS:
                        params['hold'] = 200
                elif base in TAPS and made_of not in TAPS and made_of not in TRILLS:
                    params['tap'] = 1
                    params['tapms'] = 24
                    params['hold'] = 60
                elif base in TAPS and made_of in TRILLS:
                    params['hold'] = 55
            f = self.c.measured(ph).get('f') or target
            first = 1 if base in NASALS or base in LATERALS else 0
            for k in range(first, 3):
                if made_of in TRILLS + TAPS and base in TRILLS + TAPS and k < 2 and plain:
                    continue
                r = percent(target[k] / float(f[k]))
                if not near(r, 7) and (k > 0 or not near(r, 20)):
                    params['f%d' % (k + 1)] = max(50, min(220, r))
        if u.voiceless:
            params['whisper'] = 44
            if base in TRILLS or base in TAPS or base in LATERALS:
                params['fric'] = 38
        if '̝' in mods and base == 'r':
            # the Czech r that is a trill and a fricative at once
            params['fric'] = 46
            params['a3'] = 58
            params['a4'] = 54
        if u.long:
            params['hold'] = max(params.get('hold', 100), 100) * 185 // 100
            if base in TAPS and 'tap' in params:
                params['tap'] = 3
        elif 'ˑ' in mods:
            params['hold'] = 140
        if brief:
            params['hold'] = 55
        return [Part(ph, params)]

    def sibilants(self, voiced):
        s = self.c.consonant_for('z' if voiced else 's')
        sh = self.c.consonant_for('ʒ' if voiced else 'ʃ')
        return s, sh

    def hiss(self, u, feats):
        """s, sh and the sibilants between and beyond them."""
        place, _m, voiced = feats
        base = u.base
        where, formants = HISS[base]
        s, sh = self.sibilants(voiced)
        unvoice = False
        if s is None and sh is None:
            s, sh = self.sibilants(1 - voiced)
            unvoice = True
        if s is None and sh is None:
            return []
        params = collections.OrderedDict()
        ph = self.c.consonant_for(base)
        if ph is None:
            ph = sh if (where >= 0.5 and sh is not None) or s is None else s
            ms, msh = self.c.measured(s) if s else None, self.c.measured(sh) if sh else None
            mine = self.c.measured(ph)
            if ms and msh and ms.get('amp') and msh.get('amp'):
                names = ('a2', 'a3', 'a4', 'a5', 'a6', 'ab')
                for k in range(6):
                    v = ms['amp'][k] + (msh['amp'][k] - ms['amp'][k]) * min(where, 1.0)
                    if where > 1.0 and k >= 2:
                        v -= 8 * (where - 1.0) * 4
                    v = int(round(max(0, v)))
                    if abs(v - mine['amp'][k]) >= 4:
                        params[names[k]] = v
            if formants and mine.get('f'):
                for k in (1, 2):
                    r = percent(formants[k] * self.c.scale / float(mine['f'][k]))
                    if not near(r, 6):
                        params['f%d' % (k + 1)] = max(60, min(180, r))
            if place == EP.P_RETRO:
                params['f4'] = 88
        if unvoice:
            params['voi'] = voiced
        self.secondary(u, params, place)
        if u.long:
            params['hold'] = 180
        elif 'ˑ' in u.mods:
            params['hold'] = 140
        return [Part(ph, params)]

    def secondary(self, u, params, place):
        """Palatalised, rounded, pharyngealised: what a second articulation
        does to the formants beside the sound."""
        mods = u.mods
        if u.palatal:
            t2 = 2000 if place in (EP.P_BILAB, EP.P_LABDENT) else 2200
            b2 = LOCUS.get(place, (1700, 2600))[0]
            params['f2'] = max(params.get('f2', 100), min(220, percent(max(t2, b2 * 1.2) / float(b2))))
            params['f3'] = max(params.get('f3', 100), 108)
        if 'ʷ' in mods:
            params['f2'] = int(params.get('f2', 100) * 0.82)
            params['f3'] = int(params.get('f3', 100) * 0.93)
        if 'ˤ' in mods or 'ˠ' in mods:
            params['f2'] = int(params.get('f2', 100) * 0.75)
            if 'ˤ' in mods:
                params['f1'] = 118

    def fricative(self, u, feats):
        place, manner, voiced = feats
        base = u.base
        params = collections.OrderedDict()
        ph = self.c.consonant_for(base)
        if ph is not None:
            said = self.c.measured(ph).get('said')
            if said and said != [ph]:
                ph = None
        made = None
        if ph is None:
            ph, made = self.fricative_from(base, place, voiced, params)
            if ph is None:
                return made or []
        self.secondary(u, params, place)
        if u.long:
            params['hold'] = 180
        elif 'ˑ' in u.mods:
            params['hold'] = 140
        return [Part(ph, params)]

    def fricative_from(self, base, place, voiced, params):
        """A fricative the module lacks, out of one it has."""
        c = self.c
        find = c.consonant_for

        def first(*ipas):
            for i in ipas:
                p = find(i)
                if p is not None:
                    said = c.measured(p).get('said')
                    if not said or said == [p]:
                        return p, i
            return None, None

        def move(ph, target):
            f = c.measured(ph).get('f')
            if not f:
                return
            for k in (0, 1, 2):
                r = percent(target[k] * c.scale / float(f[k]))
                if not near(r, 6) and (k > 0 or not near(r, 20)):
                    params['f%d' % (k + 1)] = max(55, min(200, r))

        def voice(ipa_of_base):
            fb = EP.cons_features(ipa_of_base)
            if fb is not None and fb[2] != voiced:
                params['voi'] = voiced
                if voiced:
                    params['af'] = -5

        if base in ('θ', 'ð'):
            ph, i = first('θ' if not voiced else 'ð', 'ð' if not voiced else 'θ', 'f' if not voiced else 'v',
                          'v' if not voiced else 'f')
            if ph is None:
                return None, None
            if i in ('f', 'v'):
                move(ph, (350, 1450, 2600))
                params['a6'] = 28
                params['ab'] = 48
            voice(i)
            return ph, None
        if base in ('ɸ', 'β'):
            ph, i = first('β' if voiced else 'ɸ', 'v' if voiced else 'f', 'f' if voiced else 'v')
            if ph is None:
                return None, None
            if base == 'β':
                params['af'] = -8
            voice(i)
            return ph, None
        if base in ('f', 'v'):
            ph, i = first('v' if voiced else 'f', 'f' if voiced else 'v', 'β', 'ɸ')
            if ph is None:
                return None, None
            voice(i)
            return ph, None
        if base in ('ç', 'ʝ'):
            # a fricative of the same voicing first: a voiced palatal in a
            # module may be an approximant with no noise in it at all
            if voiced:
                ph, i = first('ʝ', 'ç', 'ʒ', 'ʃ', 'j', 'x')
            else:
                ph, i = first('ç', 'ʃ', 'x', 'ʝ', 'j')
            if ph is None:
                return None, None
            if i in ('ʃ', 'ʒ'):
                move(ph, (300, 2250, 3000))
                params['a4'] = 0
            elif i == 'x':
                move(ph, (300, 2250, 3000))
                params['a2'] = 52
                params['a3'] = 56
                params['a4'] = 0
            elif i == 'j':
                params['fric'] = 40
                params['a2'] = 50
                params['a3'] = 54
            voice(i) if i != 'j' else None
            if i == 'j' and not voiced:
                params['whisper'] = 40
            return ph, None
        if base in ('x', 'ɣ', 'χ', 'ʁ', 'ɧ'):
            uvular = base in ('χ', 'ʁ')
            order = ['x', 'ɣ', 'χ', 'ʁ', 'ç', 'ʃ', 'k']
            if voiced:
                order = ['ɣ', 'ʁ', 'x', 'χ', 'ʒ', 'ʃ', 'ɡ']
            if uvular:
                order = (['ʁ', 'ɣ', 'χ', 'x'] if voiced else ['χ', 'x', 'ʁ']) + ['ʃ', 'ʒ']
            ph, i = first(*order)
            if ph is None:
                return None, None
            want = (330, 1150, 2400) if uvular else (300, 1350, 2500)
            if base == 'ɧ':
                want = (300, 1200, 2250)
            if i in ('ʃ', 'ʒ', 'ç'):
                move(ph, want)
                params['a2'] = 68
                params['a3'] = 0
                params['a4'] = 52
                params['af'] = -4
            elif i in ('k', 'ɡ'):
                return None, None
            elif (i in ('x', 'ɣ')) == uvular or base == 'ɧ':
                move(ph, want)
            voice(i)
            return ph, None
        if base in ('ɬ', 'ɮ'):
            ph, i = first('l', 'ɫ')
            if ph is None:
                return None, None
            params['fric'] = 52
            params['a3'] = 54
            params['a4'] = 58
            params['a5'] = 44
            if not voiced:
                params['whisper'] = 30
                # a fricative, and as long as one: the modules' l is short
                params['hold'] = 190
            return ph, None
        if base == 'ʍ':
            ph, i = first('w')
            if ph is None:
                return None, None
            params['whisper'] = 46
            return ph, None
        return None, None

    def breath(self, u, feats):
        """h and its kin, and the glottal stop: the module's own where it has
        one, and made in the engine where it has not."""
        base = u.base
        if base == 'ʔ':
            return [Part('q', {'ms': 50, 'hush': 1}, made='<')]
        if base == 'h':
            return [Part('h', {'ms': 70, 'whisper': 44}, made='<')]
        if base == 'ɦ':
            return [Part('h', {'ms': 70, 'whisper': 38, 'voi': 1}, made='<')]
        if base == 'ħ':
            return [Part('h', {'ms': 85, 'whisper': 48, 'f1': 125, 'f2': 88}, made='<')]
        if base == 'ʕ':
            return [Part('h', {'ms': 80, 'whisper': 30, 'voi': 1, 'f1': 125, 'f2': 86}, made='<')]
        return []

    def affricate(self, u, feats):
        place, _m, voiced = feats
        base = u.base
        mods = u.mods
        ph = self.c.consonant_for(base)
        plain = not (u.palatal or 'ʷ' in mods or 'ʼ' in mods or u.long or 'ˑ' in mods)
        aspirated = 'ʰ' in mods and not voiced
        breathy = ('ʱ' in mods) or ('ʰ' in mods and voiced)
        parts = None
        if ph is not None and plain:
            parts = [Part(ph)]
        else:
            rest = mods.replace('ʰ', '').replace('ʱ', '')
            a = self.consonant(EP.Unit(base[0], rest))
            b = self.consonant(EP.Unit(base[1], rest))
            if not a or not b:
                return a + b
            # the stop of an affricate lets go into its fricative, not into breath
            a[0].params.pop('vot', None)
            a[0].params.pop('asp', None)
            a[0].params['hold'] = min(a[0].params.get('hold', 100), 85)
            if not (u.long or 'ˑ' in mods):
                b[-1].params['hold'] = 70
            if place == EP.P_ALVPAL or place == EP.P_RETRO or place == EP.P_POSTALV:
                # the stop is made where the fricative is
                for k in ('f2', 'f3', 'f4'):
                    if k in b[-1].params:
                        a[0].params[k] = b[-1].params[k]
            parts = a + b
        if 'ʼ' in mods or "'" in mods:
            # an ejective affricate: the glottis stays shut through the
            # friction, which is short, and opens after it
            for p in parts:
                p.params.pop('ej', None)
            parts[-1].params['hold'] = 60
            parts.append(Part('q', {'ms': 40, 'hush': 1}, made='>'))
        if aspirated:
            parts.append(Part('h', {'ms': 45, 'whisper': 46}, made='>'))
        if breathy:
            parts.append(Part('h', {'ms': 55, 'whisper': 40, 'voi': 1}, made='>'))
        return parts

    def consonant(self, u):
        base = u.base
        feats = EP.cons_features(base)
        if base in SONORANT and (feats is None or feats[1] not in (EP.FRIC, EP.SIBF) or base == 'ʁ' and
                                 self.c.consonant_for('ʁ') and not self.c.measured(
                    self.c.consonant_for('ʁ')).get('af')):
            return self.sonorant(u)
        if feats is None:
            return []
        place, manner, voiced = feats
        if manner == EP.AFFR:
            return self.affricate(u, feats)
        if manner in (EP.STOP, EP.IMPL):
            if base == 'ʔ':
                return self.breath(u, feats)
            if manner == EP.IMPL:
                plain = {'ɓ': 'b', 'ɗ': 'd', 'ʄ': 'ɟ', 'ɠ': 'ɡ', 'ʛ': 'ɢ'}[base]
                v = EP.Unit(plain, u.mods)
                pf = EP.cons_features(plain)
                got = self.stop(v, pf)
                for p in got[:1]:
                    p.params['impl'] = 1
                    p.params['voi'] = 1
                    p.params['burst'] = -8
                return got
            return self.stop(u, feats)
        if manner == EP.CLICK:
            # a click, as the stop nearest it, let go hard
            v = EP.Unit({'ʘ': 'p', 'ǀ': 't', 'ǃ': 't', 'ǂ': 'c', 'ǁ': 't'}[base], '')
            got = self.stop(v, EP.cons_features(v.base))
            for p in got[:1]:
                p.params['burst'] = 8
                p.params['ej'] = 25
            return got
        if base in HISS:
            return self.hiss(u, feats)
        if base in ('h', 'ɦ', 'ħ', 'ʕ'):
            return self.breath(u, feats)
        return self.fricative(u, feats)

    # ---- a phoneme ----

    def phoneme(self, ipa, is_vowel=None):
        """The parts that say one eSpeak NG phoneme, with their definitions."""
        us = EP.units(ipa)
        if not us:
            return []
        vs = [u for u in us if u.vowel]
        note = ipa
        parts = []
        if len(vs) >= 2 and len(vs) == len(us):
            long_all = any(u.long for u in vs)
            heights = [EP.VOWELS[u.base][0] for u in vs]
            if len(vs) == 2 and not vs[0].nonsyllabic and (heights[0] > heights[1] or vs[1].nonsyllabic or
                                                           heights[0] == heights[1]):
                got = self.glide_vowel(vs[0], vs[1], long_all, note)
                if got:
                    return self.finish(got, note)
            # a diphthong that rises, or three vowels: the most open is the
            # vowel and the rest are glides beside it
            nucleus = max(vs, key=lambda u: (EP.VOWELS[u.base][0], -vs.index(u)))
            for u in vs:
                if u is nucleus:
                    parts += self.vowel(u, long_all)
                else:
                    h, b, r = EP.VOWELS[u.base]
                    g = 'w' if (b >= 1.5 or (r and b >= 1)) else ('ɥ' if r else 'j')
                    parts += self.sonorant(EP.Unit(g, ''), brief=True)
            return self.finish(parts, note)
        for u in us:
            if u.vowel:
                if u.nonsyllabic and len(us) > 1:
                    h, b, r = EP.VOWELS[u.base]
                    g = 'w' if (b >= 1.5 or (r and b >= 1)) else ('ɥ' if r else 'j')
                    parts += self.sonorant(EP.Unit(g, ''), brief=True)
                else:
                    parts += self.vowel(u)
            else:
                parts += self.consonant(u)
        return self.finish(parts, note)


def main(argv):
    if len(argv) >= 3 and argv[0] == 'show':
        tag = argv[1]
        template = tag
        recipe = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'openevv', 'accents', tag, 'recipe')
        if os.path.exists(recipe):
            for line in open(recipe, encoding='utf-8'):
                w = line.split()
                if len(w) >= 2 and w[0] == 'template':
                    template = w[1]
        c = Chassis(tag, template)
        d = Designer(c, Language('x'))
        print('scale %.3f' % c.scale)
        for ipa in argv[2:]:
            parts = d.phoneme(ipa)
            print(ipa, '->', ' '.join(p.text() for p in parts))
        for keys, sid in d.defs.items():
            print('  sound %s %s    # %s' % (sid, keys, d.notes[sid]))
        for given, said in sorted(d.says):
            print('  says %s %s' % (given, ' '.join(said)))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
