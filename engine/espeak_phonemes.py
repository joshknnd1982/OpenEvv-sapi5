"""eSpeak NG phonemes, said in the phones of an openevv language module.

An OpenEVV language pack made from an eSpeak NG language keeps eSpeak NG's
reading of the text and speaks it through one of openevv's own modules, the
pack's template. This is the translation between the two phoneme sets: every
phoneme eSpeak NG can produce for a language, as the template phones that come
closest to it, written into the pack as phonemes.map for OpenEvvFrontend to
read.

What each template's phones are was measured rather than assumed: every phone
was put through the module as a pronunciation annotation and read back with
eciGeneratePhonemes, and real words were read to see which phone the module
itself uses for which sound (German R is the vowel in `Bruder', X the ch of
`ich', Italian T the zz of `pizza', and so on).

The phone for a sound the template lacks is the nearest by place, manner and
voicing for a consonant and by height, backness and rounding for a vowel,
unless the template has a substitution of its own that its speakers would
use -- Spanish says h as its jota, Italian has no h at all and says nothing.
A diphthong is its most open vowel with the others as glides, except where the
template has the diphthong itself (German `aj', English `Y'). German marks
length by tense and lax vowels, so a long vowel is said tense and a short one
lax whatever its quality.

    python engine/espeak_phonemes.py report <phtables.json> <stats.json>...
"""
import json
import math
import os
import re
import sys
import unicodedata

# ---- the sounds of IPA, as features -----------------------------------------

# places, in order front to back, so a distance means something
P_BILAB, P_LABDENT, P_DENT, P_ALV, P_POSTALV, P_RETRO, P_ALVPAL, P_PAL, P_VEL, P_UVU, P_PHAR, P_GLOT = range(12)
P_LABVEL = 7.5  # w: counted between palatal and velar, and labial as well

# manners
STOP, AFFR, SIBF, FRIC, NAS, TRILL, TAP, APPR, LAT, LATFRIC, CLICK, IMPL = (
    "stop", "affr", "sibf", "fric", "nas", "trill", "tap", "appr", "lat", "latfric", "click", "impl")

CONS = {
    "p": (P_BILAB, STOP, 0), "b": (P_BILAB, STOP, 1), "t": (P_ALV, STOP, 0), "d": (P_ALV, STOP, 1),
    "ʈ": (P_RETRO, STOP, 0), "ɖ": (P_RETRO, STOP, 1), "c": (P_PAL, STOP, 0), "ɟ": (P_PAL, STOP, 1),
    "k": (P_VEL, STOP, 0), "ɡ": (P_VEL, STOP, 1), "g": (P_VEL, STOP, 1), "q": (P_UVU, STOP, 0),
    "ɢ": (P_UVU, STOP, 1), "ʔ": (P_GLOT, STOP, 0),
    "m": (P_BILAB, NAS, 1), "ɱ": (P_LABDENT, NAS, 1), "n": (P_ALV, NAS, 1), "ɳ": (P_RETRO, NAS, 1),
    "ɲ": (P_PAL, NAS, 1), "ŋ": (P_VEL, NAS, 1), "ɴ": (P_UVU, NAS, 1),
    "ʙ": (P_BILAB, TRILL, 1), "r": (P_ALV, TRILL, 1), "ʀ": (P_UVU, TRILL, 1),
    "ⱱ": (P_LABDENT, TAP, 1), "ɾ": (P_ALV, TAP, 1), "ɽ": (P_RETRO, TAP, 1), "ɺ": (P_ALV, TAP, 1),
    "ɸ": (P_BILAB, FRIC, 0), "β": (P_BILAB, FRIC, 1), "f": (P_LABDENT, FRIC, 0), "v": (P_LABDENT, FRIC, 1),
    "θ": (P_DENT, FRIC, 0), "ð": (P_DENT, FRIC, 1), "s": (P_ALV, SIBF, 0), "z": (P_ALV, SIBF, 1),
    "ʃ": (P_POSTALV, SIBF, 0), "ʒ": (P_POSTALV, SIBF, 1), "ʂ": (P_RETRO, SIBF, 0), "ʐ": (P_RETRO, SIBF, 1),
    "ɕ": (P_ALVPAL, SIBF, 0), "ʑ": (P_ALVPAL, SIBF, 1), "ç": (P_PAL, FRIC, 0), "ʝ": (P_PAL, FRIC, 1),
    "x": (P_VEL, FRIC, 0), "ɣ": (P_VEL, FRIC, 1), "χ": (P_UVU, FRIC, 0), "ʁ": (P_UVU, FRIC, 1),
    "ħ": (P_PHAR, FRIC, 0), "ʕ": (P_PHAR, FRIC, 1), "h": (P_GLOT, FRIC, 0), "ɦ": (P_GLOT, FRIC, 1),
    "ɧ": (P_POSTALV, SIBF, 0), "ʍ": (P_LABVEL, FRIC, 0),
    "ɬ": (P_ALV, LATFRIC, 0), "ɮ": (P_ALV, LATFRIC, 1),
    "ʋ": (P_LABDENT, APPR, 1), "ɹ": (P_ALV, APPR, 1), "ɻ": (P_RETRO, APPR, 1), "j": (P_PAL, APPR, 1),
    "ɰ": (P_VEL, APPR, 1), "w": (P_LABVEL, APPR, 1), "ɥ": (P_PAL, APPR, 1),
    "l": (P_ALV, LAT, 1), "ɭ": (P_RETRO, LAT, 1), "ʎ": (P_PAL, LAT, 1), "ʟ": (P_VEL, LAT, 1),
    "ɫ": (P_ALV, LAT, 1),
    "ʘ": (P_BILAB, CLICK, 0), "ǀ": (P_DENT, CLICK, 0), "ǃ": (P_ALV, CLICK, 0), "ǂ": (P_PAL, CLICK, 0),
    "ǁ": (P_ALV, CLICK, 0),
    "ɓ": (P_BILAB, IMPL, 1), "ɗ": (P_ALV, IMPL, 1), "ʄ": (P_PAL, IMPL, 1), "ɠ": (P_VEL, IMPL, 1),
    "ʛ": (P_UVU, IMPL, 1),
}
AFFRICATES = {
    ("t", "s"): (P_ALV, AFFR, 0), ("d", "z"): (P_ALV, AFFR, 1), ("t", "ʃ"): (P_POSTALV, AFFR, 0),
    ("d", "ʒ"): (P_POSTALV, AFFR, 1), ("p", "f"): (P_LABDENT, AFFR, 0), ("t", "ɕ"): (P_ALVPAL, AFFR, 0),
    ("d", "ʑ"): (P_ALVPAL, AFFR, 1), ("ʈ", "ʂ"): (P_RETRO, AFFR, 0), ("ɖ", "ʐ"): (P_RETRO, AFFR, 1),
    ("t", "ɬ"): (P_ALV, AFFR, 0), ("k", "x"): (P_VEL, AFFR, 0), ("t", "θ"): (P_DENT, AFFR, 0),
    ("d", "ð"): (P_DENT, AFFR, 1), ("b", "v"): (P_LABDENT, AFFR, 1), ("q", "χ"): (P_UVU, AFFR, 0),
    ("c", "ç"): (P_PAL, AFFR, 0), ("ɟ", "ʝ"): (P_PAL, AFFR, 1), ("t", "ʂ"): (P_RETRO, AFFR, 0),
    ("d", "ʐ"): (P_RETRO, AFFR, 1),
}

# vowels: height 0 close .. 6 open, backness 0 front .. 2 back, rounded
VOWELS = {
    "i": (0, 0, 0), "y": (0, 0, 1), "ɨ": (0, 1, 0), "ʉ": (0, 1, 1), "ɯ": (0, 2, 0), "u": (0, 2, 1),
    "ɪ": (1, 0.3, 0), "ʏ": (1, 0.3, 1), "ʊ": (1, 1.7, 1),
    "e": (2, 0, 0), "ø": (2, 0, 1), "ɘ": (2, 1, 0), "ɵ": (2, 1, 1), "ɤ": (2, 2, 0), "o": (2, 2, 1),
    "ə": (3, 1, 0), "ɛ": (4, 0, 0), "œ": (4, 0, 1), "ɜ": (4, 1, 0), "ɞ": (4, 1, 1), "ʌ": (4, 2, 0),
    "ɔ": (4, 2, 1), "æ": (5, 0, 0), "ɐ": (5, 1, 0), "a": (6, 0.7, 0), "ɶ": (6, 0, 1), "ɑ": (6, 2, 0),
    "ɒ": (6, 2, 1), "ɚ": (3, 1, 0), "ɝ": (4, 1, 0), "ä": (6, 1, 0),
}
RHOTIC_VOWELS = {"ɚ", "ɝ"}

LONG = "ː"
HALF_LONG = "ˑ"
NASAL = "̃"
MOD_PALATAL = "ʲ"
MOD_LAB = "ʷ"
SYLLABIC = "̩"
NONSYLLABIC = "̯"
VOICELESS = ("̥", "̊")
TIES = ("͡", "͜")


def is_modifier(ch):
    o = ord(ch)
    if unicodedata.category(ch) in ("Mn", "Me"):
        return True
    if 0x2b0 <= o <= 0x2ff:
        return True
    if ch in "˥˦˧˨˩0123456789":
        return True
    return False


# eSpeak writes a phoneme it has no IPA for by converting its ASCII mnemonic a
# character at a time, which leaves some mnemonic marks behind: `s.' is a
# retroflex s, `ph' an aspirated p, `i[' and `i.' the apical vowels of Mandarin.
RETRO_OF = {"s": "ʂ", "z": "ʐ", "t": "ʈ", "d": "ɖ", "n": "ɳ", "l": "ɭ", "r": "ɽ", "ʃ": "ʂ", "ʒ": "ʐ"}


# Letters some phoneme tables use in place of IPA's own: the affricate
# ligatures, Greek letters, and the barred-i of dictionaries.
LETTER_EQUIVALENTS = {
    "ʦ": "ts", "ʣ": "dz", "ʧ": "tʃ", "ʤ": "dʒ", "ʨ": "tɕ", "ʥ": "dʑ", "ʪ": "ls", "ʫ": "lz",
    "Φ": "ɸ", "φ": "ɸ", "ε": "ɛ", "β": "β", "θ": "θ", "χ": "χ", "γ": "ɣ", "ᵻ": "ɨ", "ᵿ": "ʊ", "ɩ": "ɪ",
    "ʚ": "ɞ", "ɷ": "ʊ", "ɼ": "r", "ǝ": "ə",
}


def normalise(ipa):
    s = unicodedata.normalize("NFD", ipa)
    # the c with a cedilla is a letter of the IPA and not a c with a mark on it:
    # taken apart, the palatal fricative was read as the palatal stop
    s = s.replace("c\u0327", "\u00e7")
    s = s.replace("ɡ", "ɡ")
    s = "".join(LETTER_EQUIVALENTS.get(ch, ch) for ch in s)
    if s == "?":
        s = "ʔ"
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if ch in RETRO_OF and nxt == ".":
            out.append(RETRO_OF[ch]); i += 2; continue
        if ch in "iɨ" and nxt and nxt in ".[":
            out.append("ɨ"); i += 2; continue
        if ch in "ptkc" and nxt == "h":
            out.append(ch + "ʰ"); i += 2; continue
        if ch in MNEMONIC_LETTERS:
            out.append(MNEMONIC_LETTERS[ch]); i += 1; continue
        # A backquote after a stop or an affricate is an ejective in the
        # tables that write one so (Amharic, Tigrinya, Oromo, Quechua: p` t`
        # tS` k` q`); after anything else it is a shorter variant (Latvian),
        # which is nothing to say.
        if ch == "`" and out and out[-1] in ("p", "t", "k", "q", "c", "ʃ", "s", "ʈ", "ɕ"):
            out.append("ʼ"); i += 1; continue
        if ch in ".#^%\"-/[]!`~;_':=,+*<>|{}()?" and not (ch == "?" and not out):
            if ch == ";":
                out.append(MOD_PALATAL)
            elif ch == "~":
                out.append(NASAL)
            elif ch == ":":
                out.append(LONG)
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


# The rest of eSpeak NG's ASCII phoneme names, where a table gives no IPA:
# its capitals and digits are, mostly, X-SAMPA's.
MNEMONIC_LETTERS = {
    "A": "ɑ", "B": "β", "C": "ç", "D": "ð", "E": "ɛ", "G": "ɣ", "I": "ɪ", "J": "ɟ", "K": "ɬ", "L": "ɫ", "M": "ɯ",
    "N": "ŋ", "O": "ɔ", "Q": "ɣ", "R": "ʁ", "S": "ʃ", "T": "θ", "U": "ʊ", "V": "ʌ", "W": "œ", "X": "χ", "Y": "ʏ",
    "Z": "ʒ", "0": "ɒ", "1": "ɨ", "2": "ø", "3": "ɜ", "4": "ɐ", "5": "ɫ", "6": "ɐ", "7": "ɤ", "8": "ɵ", "9": "œ",
    "&": "æ", "@": "ə",
}


class Unit(object):
    """One sound in an IPA string: a base letter and what modifies it."""

    def __init__(self, base, mods):
        self.base = base
        self.mods = mods
        self.long = LONG in mods or HALF_LONG in mods
        self.nasal = NASAL in mods
        self.palatal = MOD_PALATAL in mods
        self.syllabic = SYLLABIC in mods
        self.nonsyllabic = NONSYLLABIC in mods
        self.voiceless = any(v in mods for v in VOICELESS)

    @property
    def vowel(self):
        return self.base in VOWELS

    def __repr__(self):
        return self.base + self.mods


def units(ipa):
    s = normalise(ipa)
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if is_modifier(ch) and ch not in TIES:
            if out:
                out[-1] = Unit(out[-1].base, out[-1].mods + ch)
            i += 1
            continue
        if ch in TIES:
            i += 1
            continue
        out.append(Unit(ch, ""))
        i += 1
    # affricates, tied or not
    merged = []
    for u in out:
        if merged and (merged[-1].base, u.base) in AFFRICATES and not merged[-1].mods.replace(LONG, ""):
            prev = merged.pop()
            merged.append(Unit(prev.base + u.base, prev.mods + u.mods))
            continue
        # a vowel written twice is one long vowel
        if merged and u.vowel and merged[-1].vowel and u.base == merged[-1].base:
            prev = merged.pop()
            merged.append(Unit(prev.base, prev.mods + u.mods + (LONG if LONG not in prev.mods + u.mods else "")))
            continue
        merged.append(u)
    return merged


def cons_features(base):
    if base in CONS:
        return CONS[base]
    if len(base) == 2 and (base[0], base[1]) in AFFRICATES:
        return AFFRICATES[(base[0], base[1])]
    return None


def manner_distance(a, b):
    if a == b:
        return 0
    pairs = {
        frozenset((SIBF, FRIC)): 1.0, frozenset((STOP, AFFR)): 1.2, frozenset((AFFR, SIBF)): 1.5,
        frozenset((TRILL, TAP)): 0.3, frozenset((TAP, APPR)): 1.5, frozenset((TRILL, APPR)): 1.5,
        frozenset((LAT, APPR)): 2.0, frozenset((LATFRIC, LAT)): 1.5, frozenset((LATFRIC, SIBF)): 1.5,
        frozenset((LATFRIC, FRIC)): 1.5, frozenset((STOP, IMPL)): 0.5, frozenset((STOP, CLICK)): 1.5,
        frozenset((STOP, FRIC)): 2.0, frozenset((STOP, SIBF)): 2.5, frozenset((FRIC, APPR)): 1.5,
        frozenset((TRILL, FRIC)): 2.0, frozenset((TAP, STOP)): 2.0, frozenset((NAS, STOP)): 3.0,
    }
    return pairs.get(frozenset((a, b)), 4.0)


def cons_distance(fa, fb):
    pa, ma, va = fa
    pb, mb, vb = fb
    d = manner_distance(ma, mb) + 0.6 * abs(pa - pb) + (0.8 if va != vb else 0)
    return d


def vowel_distance(a, b):
    ha, ba, ra = VOWELS[a]
    hb, bb, rb = VOWELS[b]
    return 1.0 * abs(ha - hb) + 1.2 * abs(ba - bb) + 1.5 * abs(ra - rb)


# ---- the templates, measured ------------------------------------------------

class Template(object):
    def __init__(self, tag, name, lang_id, vowels, consonants, glides, schwa, french=False, bias=0.0,
                 subs=None, diphthongs=None, tense=None, nasals=None, longs=None, drop_h=False,
                 secondary="2"):
        self.tag = tag
        self.name = name
        self.lang_id = lang_id
        self.vowels = vowels            # engine phone -> IPA vowel
        self.consonants = consonants    # engine phone -> IPA consonant (or affricate)
        self.glides = glides            # engine phones that may follow an obstruent in an onset
        self.schwa = schwa
        self.french = french
        self.bias = bias                # a small cost per phoneme, for accents the templates bring
        self.subs = subs or {}          # IPA base -> engine phones, a substitution speakers use
        self.diphthongs = diphthongs or {}  # IPA vowel string -> engine phone
        self.tense = tense or {}        # lax phone -> tense phone, for templates that say length so
        self.nasals = nasals or {}      # engine phone -> its nasal vowel
        self.longs = longs or {}        # IPA long vowel -> engine phone, where length is a quality
        self.drop_h = drop_h
        self.secondary = secondary      # the digit for secondary stress; Italian and Spanish have none

    def glide_j(self):
        return "y" if "y" in self.consonants else "j"

    def all_vowel_phones(self):
        v = list(self.vowels) + list(self.diphthongs.values()) + list(self.nasals.values()) + \
            list(self.tense.values()) + list(self.longs.values())
        seen = []
        for p in v:
            if p not in seen:
                seen.append(p)
        return seen


TEMPLATES = {}


def _t(*a, **k):
    t = Template(*a, **k)
    TEMPLATES[t.tag] = t


_t("itit", "Italian", 0x50000,
   vowels={"i": "i", "e": "e", "E": "ɛ", "a": "a", "o": "o", "c": "ɔ", "u": "u"},
   consonants={"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "ɡ", "f": "f", "v": "v", "s": "s",
               "z": "z", "S": "ʃ", "Z": "ʒ", "T": "ts", "D": "dz", "C": "tʃ", "J": "dʒ", "m": "m", "n": "n",
               "N": "ɲ", "r": "r", "l": "l", "L": "ʎ", "y": "j", "w": "w"},
   glides=["r", "l", "L", "y", "w"], schwa="e", secondary="0",
   subs={"h": [], "ɦ": [], "ħ": [], "ʕ": [], "ʔ": [], "x": ["k"], "χ": ["k"], "ɣ": ["g"], "ʁ": ["r"],
         "ɾ": ["r"],
         "ʀ": ["r"], "θ": ["t"], "ð": ["d"], "ŋ": ["n"], "ç": ["S"], "ʝ": ["y"], "ɕ": ["S"], "ʑ": ["Z"],
         "ʂ": ["S"], "ʐ": ["Z"], "c": ["C"], "ɟ": ["J"], "ɬ": ["S"], "ɹ": ["r"], "ɻ": ["r"], "ɥ": ["y"],
         "ʋ": ["v"], "β": ["v"], "ɸ": ["f"], "ɰ": ["w"], "q": ["k"], "ɢ": ["g"]},
   drop_h=True)

_t("eses", "Castilian Spanish", 0x20000, secondary="0",
   vowels={"i": "i", "e": "e", "a": "a", "o": "o", "u": "u"},
   consonants={"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "ɡ", "f": "f", "v": "v", "s": "s",
               "z": "z", "T": "θ", "j": "x", "S": "ʃ", "Z": "ʒ", "C": "tʃ", "J": "dʒ", "Y": "ʝ", "m": "m",
               "n": "n", "N": "ɲ", "ng": "ŋ", "r": "ɾ", "R": "r", "l": "l", "L": "ʎ", "y": "j", "w": "w"},
   glides=["r", "R", "l", "L", "y", "w"], schwa="e",
   subs={"h": ["j"], "ɦ": ["j"], "ħ": ["j"], "ʕ": [], "ʔ": [], "χ": ["j"], "ʁ": ["j"], "ʀ": ["R"],
         "ɣ": ["g"], "ð": ["d"], "β": ["b"], "ç": ["j"], "ɕ": ["S"], "ʑ": ["Z"], "ʂ": ["S"], "ʐ": ["Z"],
         "c": ["C"], "ɟ": ["J"], "ɬ": ["j", "l"], "ts": ["t", "s"], "dz": ["d", "z"], "ɹ": ["r"],
         "ɻ": ["r"], "ɥ": ["y"], "ʋ": ["b"], "ɸ": ["f"], "ɰ": ["w"], "q": ["k"], "ɢ": ["g"], "pf": ["p", "f"]})

_t("esus", "Latin American Spanish", 0x20001, secondary="0",
   vowels={"i": "i", "e": "e", "a": "a", "o": "o", "u": "u"},
   consonants={"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "ɡ", "f": "f", "v": "v", "s": "s",
               "z": "z", "j": "x", "S": "ʃ", "Z": "ʒ", "C": "tʃ", "J": "dʒ", "m": "m", "n": "n", "N": "ɲ",
               "ng": "ŋ", "r": "ɾ", "R": "r", "l": "l", "L": "ʎ", "y": "j", "w": "w"},
   glides=["r", "R", "l", "L", "y", "w"], schwa="e", bias=0.02,
   subs={"h": ["j"], "ɦ": ["j"], "ħ": ["j"], "ʕ": [], "ʔ": [], "χ": ["j"], "ʁ": ["j"], "ʀ": ["R"],
         "ɣ": ["g"], "ð": ["d"], "θ": ["s"], "β": ["b"], "ʝ": ["y"], "ç": ["j"], "ɕ": ["S"], "ʑ": ["Z"],
         "ʂ": ["S"], "ʐ": ["Z"], "c": ["C"], "ɟ": ["J"], "ɬ": ["j", "l"], "ts": ["t", "s"],
         "dz": ["d", "z"], "ɹ": ["r"], "ɻ": ["r"], "ɥ": ["y"], "ʋ": ["b"], "ɸ": ["f"], "ɰ": ["w"],
         "q": ["k"], "ɢ": ["g"], "pf": ["p", "f"]})

_t("dede", "German", 0x40000,
   vowels={"i": "i", "I": "ɪ", "e": "e", "E": "ɛ", "a": "a", "A": "ä", "u": "u", "U": "ʊ", "o": "o",
           "O": "ɔ", "y": "y", "Y": "ʏ", "oe": "ø", "OE": "œ", "@": "ə"},
   consonants={"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "ɡ", "f": "f", "v": "v", "s": "s",
               "z": "z", "S": "ʃ", "Z": "ʒ", "X": "ç", "x": "x", "r": "ʁ", "P": "pf", "T": "ts", "C": "tʃ",
               "J": "dʒ", "h": "h", "m": "m", "n": "n", "G": "ŋ", "l": "l", "j": "j", "w": "w"},
   glides=["r", "l", "j", "w"], schwa="@",
   subs={"ʔ": [], "ħ": ["h"], "ʕ": ["h"], "θ": ["s"], "ð": ["d"], "ɣ": ["g"], "χ": ["x"], "ʀ": ["r"],
         "ɾ": ["r"], "ɹ": ["r"], "ɻ": ["r"], "ɲ": ["n", "j"], "ʎ": ["l", "j"], "ʝ": ["j"], "ɕ": ["S"],
         "ʑ": ["Z"], "ʂ": ["S"], "ʐ": ["Z"], "c": ["C"], "ɟ": ["J"], "ɬ": ["S", "l"], "dz": ["d", "z"],
         "ɥ": ["j"], "ʋ": ["v"], "β": ["v"], "ɸ": ["f"], "ɰ": ["w"], "q": ["k"], "ɢ": ["g"],
         "ʍ": ["w"]},
   diphthongs={"ai": "aj", "aɪ": "aj", "ae": "aj", "äɪ": "aj", "au": "aw", "aʊ": "aw", "äʊ": "aw",
               "ɔʏ": "oj", "ɔɪ": "oj", "ɔy": "oj", "ɔø": "oj", "oi": "oj", "ɔi": "oj"},
   tense={"I": "i", "E": "e", "A": "a", "U": "u", "O": "o", "Y": "y", "OE": "oe"},
   nasals={"A": "a~", "a": "a~", "E": "E~", "e": "E~", "i": "E~", "I": "E~", "O": "o~", "o": "o~",
           "u": "o~", "U": "o~", "OE": "oe~", "oe": "oe~", "y": "oe~", "Y": "oe~", "@": "a~"},
   longs={"ɛː": "E:", "æː": "E:"})

_t("frfr", "French", 0x30000, french=True,
   vowels={"i": "i", "e": "e", "E": "ɛ", "a": "a", "o": "o", "c": "ɔ", "u": "u", "y": "y", "eu": "ø",
           "oe": "œ", "x": "ə"},
   consonants={"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "ɡ", "f": "f", "v": "v", "s": "s",
               "z": "z", "S": "ʃ", "Z": "ʒ", "m": "m", "n": "n", "nj": "ɲ", "ng": "ŋ", "l": "l", "r": "ʁ",
               "j": "j", "w": "w", "H": "ɥ"},
   glides=["r", "l", "j", "w", "H"], schwa="x", bias=0.05,
   subs={"h": [], "ɦ": [], "ħ": [], "ʕ": [], "ʔ": [], "x": ["r"], "χ": ["r"], "ɣ": ["r"], "ʀ": ["r"],
         "ɾ": ["r"], "r": ["r"], "ɹ": ["r"], "ɻ": ["r"], "θ": ["s"], "ð": ["z"], "ts": ["t", "s"],
         "dz": ["d", "z"], "tʃ": ["t", "S"], "dʒ": ["d", "Z"], "ʎ": ["l", "j"], "ʝ": ["j"],
         "ç": ["S"], "ɕ": ["S"], "ʑ": ["Z"], "ʂ": ["S"], "ʐ": ["Z"], "c": ["t", "S"], "ɟ": ["d", "Z"],
         "tɕ": ["t", "S"], "dʑ": ["d", "Z"], "ʈʂ": ["t", "S"], "ɖʐ": ["d", "Z"], "ɬ": ["S", "l"],
         "ʋ": ["v"], "β": ["v"], "ɸ": ["f"], "ɰ": ["w"], "q": ["k"], "ɢ": ["g"], "pf": ["p", "f"],
         "ʍ": ["w"]},
   nasals={"a": "a~", "E": "E~", "e": "E~", "i": "E~", "o": "o~", "c": "o~", "u": "o~", "oe": "oe~",
           "eu": "oe~", "y": "oe~", "x": "a~"},
   drop_h=True)

# eSpeak NG's English vowels, as both English modules say them
ENGLISH_VOWELS = {"eɪ": "e", "ei": "e", "oʊ": "o", "ou": "o", "əʊ": "o", "aɪ": "Y", "ai": "Y", "ɑɪ": "Y",
                  "aʊ": "W", "au": "W", "ɔɪ": "O", "ɔi": "O", "oɪ": "O", "oi": "O", "e": "e", "o": "o", "eː": "e",
                  "oː": "o", "ɚ": "R", "ɝ": "R", "ə": "x", "ɪ": "I", "ʊ": "U", "ʌ": "H", "æ": "A", "i": "i", "u": "u",
                  "ɛ": "E"}

_t("enus", "US English", 0x10000, bias=0.25,
   vowels={"i": "i", "I": "ɪ", "E": "ɛ", "A": "æ", "a": "ɑ", "c": "ɔ", "U": "ʊ", "u": "u", "H": "ʌ",
           "x": "ə", "R": "ɝ"},
   consonants={"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "ɡ", "f": "f", "v": "v", "T": "θ",
               "D": "ð", "s": "s", "z": "z", "S": "ʃ", "Z": "ʒ", "C": "tʃ", "J": "dʒ", "h": "h", "m": "m",
               "n": "n", "G": "ŋ", "r": "ɹ", "l": "l", "y": "j", "w": "w", "?": "ʔ"},
   glides=["r", "l", "y", "w"], schwa="x",
   subs={"x": ["h"], "χ": ["h"], "ħ": ["h"], "ʕ": ["h"], "ɣ": ["g"], "ʁ": ["r"], "ʀ": ["r"], "ɾ": ["r"],
         "r": ["r"], "ɻ": ["r"], "ɲ": ["n", "y"], "ʎ": ["l", "y"], "ʝ": ["y"], "ç": ["h"], "ɕ": ["S"],
         "ʑ": ["Z"], "ʂ": ["S"], "ʐ": ["Z"], "c": ["C"], "ɟ": ["J"], "ɬ": ["S", "l"], "ts": ["t", "s"],
         "dz": ["d", "z"], "ɥ": ["y"], "ʋ": ["v"], "β": ["v"], "ɸ": ["f"], "ɰ": ["w"], "q": ["k"],
         "ɢ": ["g"], "pf": ["p", "f"], "e": ["e"], "o": ["o"]},
   diphthongs=dict(ENGLISH_VOWELS, **{"ɾ": "F", "ɒ": "a", "ɔ": "c", "ɐ": "x", "ɜ": "R", "ɪə": "I x",
                                      "eə": "E x", "ɛə": "E x", "ʊə": "U x", "ɪɹ": "i r", "ɛɹ": "E r",
                                      "ʊɹ": "U r", "ɑɹ": "a r", "ɔɹ": "c r", "oɹ": "o r", "aɪə": "Y x",
                                      "aʊə": "W x", "ɑ": "a"}),
   longs={"iː": "i", "uː": "u", "ɑː": "a", "ɔː": "c", "ɜː": "R", "aː": "a"})

_t("engb", "British English", 0x10001, bias=0.25,
   vowels={"i": "i", "I": "ɪ", "E": "ɛ", "A": "æ", "a": "ɑ", "@": "ɒ", "c": "ɔ", "U": "ʊ", "u": "u",
           "H": "ʌ", "x": "ə", "R": "ɜ"},
   consonants={"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "ɡ", "f": "f", "v": "v", "T": "θ",
               "D": "ð", "s": "s", "z": "z", "S": "ʃ", "Z": "ʒ", "C": "tʃ", "J": "dʒ", "h": "h", "m": "m",
               "n": "n", "G": "ŋ", "r": "ɹ", "l": "l", "y": "j", "w": "w"},
   glides=["r", "l", "y", "w"], schwa="x",
   subs={"x": ["h"], "χ": ["h"], "ħ": ["h"], "ʕ": ["h"], "ʔ": [], "ɣ": ["g"], "ʁ": ["r"], "ʀ": ["r"],
         "ɾ": ["r"], "r": ["r"], "ɻ": ["r"], "ɲ": ["n", "y"], "ʎ": ["l", "y"], "ʝ": ["y"], "ç": ["h"],
         "ɕ": ["S"], "ʑ": ["Z"], "ʂ": ["S"], "ʐ": ["Z"], "c": ["C"], "ɟ": ["J"], "ɬ": ["S", "l"],
         "ts": ["t", "s"], "dz": ["d", "z"], "ɥ": ["y"], "ʋ": ["v"], "β": ["v"], "ɸ": ["f"], "ɰ": ["w"],
         "q": ["k"], "ɢ": ["g"], "pf": ["p", "f"]},
   diphthongs=dict(ENGLISH_VOWELS, **{"ɒ": "@", "ɔ": "c", "ɐ": "x", "ɜ": "R", "ɪə": "I x", "eə": "E x",
                                      "ɛə": "E x", "ʊə": "U x", "aɪə": "Y x", "aʊə": "W x", "ɑ": "a"}),
   longs={"iː": "i", "uː": "u", "ɑː": "a", "ɔː": "c", "ɜː": "R", "aː": "a"})

CANDIDATES = ["itit", "eses", "esus", "dede", "frfr", "enus", "engb"]


# ---- one phoneme -------------------------------------------------------------

def nearest_consonant(t, feats):
    best, bd = None, 1e9
    for ph, ipa in t.consonants.items():
        f = cons_features(ipa)
        if f is None:
            continue
        d = cons_distance(feats, f)
        if d < bd:
            best, bd = ph, d
    return best, bd


RHOTICS = ("r", "ɾ", "ɹ", "ɻ", "ʀ", "ʁ", "ɽ", "ɺ")


# affricates of other places, said as the template's own ch and j where it has them
AFFRICATE_KIN = {"ʈʂ": "tʃ", "tʂ": "tʃ", "tɕ": "tʃ", "cç": "tʃ", "ɖʐ": "dʒ", "dʐ": "dʒ", "dʑ": "dʒ", "ɟʝ": "dʒ"}


def map_consonant(t, u):
    """Engine phones for one consonant unit, and how far from it they are."""
    base = u.base
    if base in AFFRICATE_KIN and base not in t.consonants.values() and base not in t.subs:
        kin = [p for p, ipa in t.consonants.items() if ipa == AFFRICATE_KIN[base]]
        if kin:
            return [kin[0]], 0.4
    if base in RHOTICS and base not in t.subs and base not in t.consonants.values():
        own = [p for p, ipa in t.consonants.items() if ipa in RHOTICS]
        if own:
            return [own[0]], 0.5
    if u.palatal and base in ("n",) and "ɲ" in t.consonants.values():
        base = "ɲ"
    if u.palatal and base in ("l", "ɫ") and "ʎ" in t.consonants.values():
        base = "ʎ"
    exact = [p for p, ipa in t.consonants.items() if ipa == base]
    if exact:
        return [exact[0]], 0.0
    if base == "ɡ":
        exact = [p for p, ipa in t.consonants.items() if ipa in ("ɡ", "g")]
        if exact:
            return [exact[0]], 0.0
    if base in t.subs:
        cost = 0.6 if t.subs[base] else 1.5
        return list(t.subs[base]), cost
    feats = cons_features(base)
    if feats is None:
        return [], 3.0
    if feats[1] == AFFR and len(base) == 2:
        # an affricate the template lacks: its two halves
        a, ca = map_consonant(t, Unit(base[0], ""))
        b, cb = map_consonant(t, Unit(base[1], ""))
        return a + b, 0.8 + (ca + cb) / 2
    ph, d = nearest_consonant(t, feats)
    return ([ph] if ph else []), d


def nearest_vowel(t, v):
    best, bd = None, 1e9
    for ph, ipa in t.vowels.items():
        if ipa in RHOTIC_VOWELS and v not in RHOTIC_VOWELS:
            continue
        d = vowel_distance(v, ipa)
        if d < bd:
            best, bd = ph, d
    return best, bd


def glide_for(t, u):
    """A vowel said as a glide beside the nucleus: front ones as j, round ones as w."""
    h, b, r = VOWELS[u.base]
    if b >= 1.5 or (r and b >= 1):
        return "w"
    if r and "H" in t.consonants:
        return "H"
    return t.glide_j()


def map_vowel(t, u, long_=False):
    v = u.base
    long_ = long_ or u.long
    if v in RHOTIC_VOWELS and "R" in t.vowels and t.vowels["R"] in ("ɝ", "ɜ"):
        return ["R"], 0.0
    key = v + (LONG if long_ else "")
    if key in t.longs:
        ph = t.longs[key]
        d = 0.0
    else:
        exact = [p for p, ipa in t.vowels.items() if ipa == v]
        if exact:
            ph, d = exact[0], 0.0
        elif v in ("ɨ", "ɯ", "ɘ", "ɤ") and t.schwa in t.vowels and t.vowels.get(t.schwa) == "ə":
            ph, d = t.schwa, 1.0
        else:
            ph, d = nearest_vowel(t, v)
    if t.tense:
        # length said as tense and lax
        lax_of = dict((tv, lv) for lv, tv in t.tense.items())
        if long_ and ph in t.tense:
            ph = t.tense[ph]
        elif not long_ and ph in lax_of:
            ph = lax_of[ph]
    final_ipa = t.vowels.get(ph)
    if final_ipa is not None and final_ipa in VOWELS:
        d = vowel_distance(v, final_ipa) * (0.5 if t.tense else 1.0)
    if long_ and not t.tense and key not in t.longs:
        d += 0.3  # the length is lost
    if u.nasal and t.nasals:
        if ph in t.nasals:
            return [t.nasals[ph]], d
    elif u.nasal:
        d += 0.7
    extra = []
    if v in RHOTIC_VOWELS:
        extra = ["r"] if "r" in t.consonants else []
    return [ph] + extra, d


def map_phoneme(t, ipa, is_vowel):
    """The engine phones for one eSpeak phoneme's IPA, and a cost: nought when
    the template has it exactly, more the further it had to go."""
    us = units(ipa)
    if not us:
        return [], 0.0
    vs = [u for u in us if u.vowel]
    whole = unicodedata.normalize("NFD", normalise(ipa))
    plain = "".join(u.base for u in us)
    long_all = any(u.long for u in vs)
    # a template's own diphthong
    for key in (whole, plain, plain + (LONG if long_all else "")):
        if key in t.diphthongs:
            ph = t.diphthongs[key]
            if vs and vs[0].nasal and ph in t.nasals:
                ph = t.nasals[ph]
            return ph.split(), 0.0
    out, cost = [], 0.0
    if len(vs) >= 2:
        # the most open vowel is the nucleus, the rest glides
        nucleus = max(vs, key=lambda u: (VOWELS[u.base][0], -vs.index(u)))
        for u in us:
            if not u.vowel:
                p, c = map_consonant(t, u)
                out += p
                cost += c
            elif u is nucleus:
                p, c = map_vowel(t, u, long_all)
                out += p
                cost += c
            else:
                h = VOWELS[u.base][0]
                if h <= 2:
                    out.append(glide_for(t, u))
                    cost += 0.3
                else:
                    p, c = map_vowel(t, u)
                    out += p
                    cost += c + 0.5
        return out, cost
    for u in us:
        if u.vowel:
            p, c = map_vowel(t, u)
        else:
            p, c = map_consonant(t, u)
        out += p
        cost += c
    return out, cost


# ---- a language ----------------------------------------------------------------

def load_tables(path):
    tables = json.load(open(path, encoding="utf-8"))
    return dict((t["table"], t) for t in tables)


def language_cost(t, stats):
    """The frequency-weighted cost of saying a language's phonemes with template t.

    Two things are counted: how far each phoneme had to go to reach the
    template's phones, and every pair of the language's sounds that the
    template can only say the same way -- a contrast lost, which a listener
    notices far more than a sound slightly off (Finnish y said as i is also
    Finnish i). A pair costs by the rarer of its two sounds."""
    total, weight = 0.0, 0
    said = {}
    for s in stats:
        if s["type"] < 2:
            continue
        p, c = map_phoneme(t, s["ipa"], s["type"] == 2)
        total += s["count"] * (c + t.bias)
        weight += s["count"]
        quality = "".join(u.base for u in units(s["ipa"])) + ("ː" if any(u.long for u in units(s["ipa"])) else "")
        key = " ".join(p)
        said.setdefault(key, {})
        said[key][quality] = said[key].get(quality, 0) + s["count"]
    for key, qualities in said.items():
        if len(qualities) < 2:
            continue
        counts = sorted(qualities.values(), reverse=True)
        # every sound but the commonest is said as that one
        total += 1.2 * sum(counts[1:])
    return total / max(weight, 1)


def choose_template(stats, candidates=CANDIDATES):
    scored = sorted((language_cost(TEMPLATES[c], stats), c) for c in candidates)
    return scored[0][1], scored


def write_map(path, t, table_names, tables, stats, espeak_voice, lang_name):
    """phonemes.map: the template, and every phoneme of the language's tables."""
    lines = [
        "# OpenEVV phoneme map: %s (eSpeak NG voice %s), said with openevv's %s." % (lang_name, espeak_voice, t.name),
        "# Written by engine/espeak_phonemes.py; OpenEvvFrontend reads it.",
        "#",
        "# Each line is an eSpeak NG phoneme and the %s phones that say it." % t.name,
        "# `@table:name' is a phoneme by its eSpeak NG name in that phoneme table,",
        "# and a line that starts with IPA is used for any phoneme with that IPA,",
        "# from any table -- a word eSpeak NG reads in another language, say.",
        "# A phoneme with nothing after it is not said. Edit freely: the file is",
        "# read each time a voice starts.",
        "",
        "template %s" % t.tag,
        "style %s" % ("french" if t.french else "standard"),
        "vowels %s" % " ".join(t.all_vowel_phones() + (["R"] if t.tag == "dede" else [])),
        "glides %s" % " ".join(t.glides),
        "schwa %s" % t.schwa,
        "secondary %s" % t.secondary,
        "",
    ]
    used = set((s["table"], s["mnemonic"]) for s in stats)
    for tn in table_names:
        tab = tables.get(tn)
        if not tab:
            continue
        lines.append("# eSpeak NG phoneme table %s" % tn)
        for ph in tab["phonemes"]:
            if ph["type"] < 2 or not ph["mnemonic"]:
                continue
            phones, cost = map_phoneme(t, ph["ipa"], ph["type"] == 2)
            note = "  # %s%s" % (ph["ipa"], "" if (tn, ph["mnemonic"]) in used else "")
            lines.append("%-16s %-14s%s" % ("@%s:%s" % (tn, ph["mnemonic"]), " ".join(phones) or "-", note))
        lines.append("")
    # any IPA at all, for phonemes of tables not listed above
    lines.append("# by IPA, for phonemes from any other table")
    seen = set()
    for tn, tab in sorted(tables.items()):
        for ph in tab["phonemes"]:
            if ph["type"] < 2 or not ph["ipa"] or ph["ipa"] in seen or " " in ph["ipa"]:
                continue
            seen.add(ph["ipa"])
            phones, cost = map_phoneme(t, ph["ipa"], ph["type"] == 2)
            lines.append("%-16s %s" % (ph["ipa"], " ".join(phones) or "-"))
    # the plain IPA letters too, so that anything can be taken apart
    for base in list(CONS) + list(VOWELS):
        if base in seen:
            continue
        seen.add(base)
        phones, cost = map_phoneme(t, base, base in VOWELS)
        lines.append("%-16s %s" % (base, " ".join(phones) or "-"))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def main(argv):
    if len(argv) >= 3 and argv[0] == "report":
        tables = load_tables(argv[1])
        for p in argv[2:]:
            stats = json.load(open(p, encoding="utf-8"))
            best, scored = choose_template(stats)
            print("%-24s %s   %s" % (os.path.basename(p), best,
                                     "  ".join("%s %.2f" % (c, s) for s, c in scored)))
        return 0
    if len(argv) >= 3 and argv[0] == "show":
        t = TEMPLATES[argv[1]]
        for ipa in argv[2:]:
            print(ipa, "->", map_phoneme(t, ipa, any(u.vowel for u in units(ipa))))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
