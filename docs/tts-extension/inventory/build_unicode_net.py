#!/usr/bin/env python3
"""Builds the Unicode net (DESIGN.md 1, the secondary coverage metric): every assigned code point of
ten Unicode blocks put in exactly one class, written to ipa/unicode_net.toml for
engine/ipa/coverage.py. MIT licence.

    python docs/tts-extension/inventory/build_unicode_net.py

Reads Unicode's own UnicodeData.txt and Blocks.txt (beside this file, in unicode/; Python's
unicodedata is too old), the checklist (IPA_CHECKLIST.json) and ipa/aliases.toml. Classes:

    A             a code point of a checklist entry's own spelling
    alias         another spelling of a Tier A or Tier B thing (ligature, precomposed letter, the
                  above-form of a below diacritic, a canonical equivalent, a checklist alternative)
    B             an extIPA (2015/2021) or VoQS (2016) symbol
    C             phonetic, but of another tradition (UPA, Americanist, Sinological, Teuthonista,
                  phonotypy, withdrawn IPA, superscript/subscript letters not used by the chart)
    not-phonetic  orthographic, palaeographic, editorial or typographic

The rules are in four layers, applied in this order: the checklist and aliases.toml (data), then
the explicit lists below (each with its reason), then name patterns for what the lists leave. The
data and explicit layers must agree where both speak; a pattern only speaks for a code point that
nothing above classified. A code point no rule reaches stops the build.
"""

import collections
import json
import os
import re
import sys

import tomli

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
UNICODE = os.path.join(HERE, 'unicode')
CHECKLIST = os.path.join(HERE, 'IPA_CHECKLIST.json')
ALIASES = os.path.join(ROOT, 'ipa', 'aliases.toml')
OUT = os.path.join(ROOT, 'ipa', 'unicode_net.toml')

BLOCKS = ['IPA Extensions', 'Spacing Modifier Letters', 'Combining Diacritical Marks',
          'Combining Diacritical Marks Extended', 'Combining Diacritical Marks Supplement',
          'Phonetic Extensions', 'Phonetic Extensions Supplement', 'Modifier Tone Letters',
          'Latin Extended-F', 'Latin Extended-G']
CLASSES = ['A', 'alias', 'B', 'C', 'not-phonetic']

# Where the Tier B list was checked (each page opened on 2026-10-06). Written into the output.
SOURCES = [
    'https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet'
    ' (and its raw wikitext, ?action=raw): extIPA 2015 and 2021 letters, diacritics, release letters',
    'https://en.wikipedia.org/wiki/Voice_Quality_Symbols: the VoQS chart (2016)',
    'https://www.unicode.org/Public/18.0.0/ucd/NamesList.txt: block section headers and annotations'
    ' (U+02B0..02FF, U+0300..036F; e.g. "IPA diacritics for disordered speech" U+034B..034E)',
    'https://en.wikipedia.org/wiki/Combining_Diacritical_Marks_Extended: which proposal each addition'
    ' came from (Teuthonista, extIPA and VoQS, Harrington, compound tones, IPA diacritics above)',
    'https://en.wikipedia.org/wiki/Combining_Diacritical_Marks_Supplement: UPA, medievalist, Teuthonista',
]


def R(a, b=None):
    """The code points a..b inclusive."""
    return range(a, (b if b is not None else a) + 1)


def table(*rows):
    """{code point: reason} from rows (code point or range, reason)."""
    out = {}
    for cps, why in rows:
        for cp in (cps if isinstance(cps, range) else [cps]):
            assert cp not in out, 'listed twice in one table: U+%04X' % cp
            out[cp] = why
    return out


# ---- alias: another spelling of a Tier A or Tier B thing -------------------------------------
ALIAS = table(
    (0x025A, 'ɚ = ə˞ (precomposed rhotic schwa)'),
    (0x025D, 'ɝ = ɜ˞ (precomposed rhotic vowel)'),
    (0x026B, 'ɫ = l̴ (the chart\'s own example of velarized or pharyngealized; also in aliases.toml)'),
    (0x02A3, 'ʣ = d͡z (withdrawn ligature)'),
    (0x02A4, 'ʤ = d͡ʒ (withdrawn ligature)'),
    (0x02A5, 'ʥ = d͡ʑ (withdrawn ligature)'),
    (0x02A6, 'ʦ = t͡s (withdrawn ligature)'),
    (0x02A7, 'ʧ = t͡ʃ (withdrawn ligature)'),
    (0x02A8, 'ʨ = t͡ɕ (withdrawn ligature)'),
    (0x02C1, 'ˁ = ˤ (typographic alternate of the pharyngealized mark; VoQS writes Vˁ)'),
    (0x02D2, '˒ = ◌̹ more rounded, spacing form (NamesList annotation)'),
    (0x02D3, '˓ = ◌̜ less rounded, spacing form'),
    (0x02D4, '˔ = ◌̝ raised, spacing form'),
    (0x02D5, '˕ = ◌̞ lowered, spacing form'),
    (0x02D6, '˖ = ◌̟ advanced, spacing form'),
    (0x02D7, '˗ = ◌̠ retracted, spacing form'),
    (0x030D, '◌̍ = ◌̩ syllabic, placed above (chart: diacritics may go above a letter with a descender)'),
    (0x0311, '◌̑ = ◌̯ non-syllabic, placed above'),
    (0x0340, '◌̀ grave tone mark: canonically equivalent to U+0300'),
    (0x0341, '◌́ acute tone mark: canonically equivalent to U+0301'),
    (0x0351, '◌͑ = ◌̜ less rounded, placed above'),
    (0x0357, '◌͗ = ◌̹ more rounded, placed above'),
    (0x1AC8, '◌᫈ = ◌̟ advanced, placed above'),
    (0x1ADB, '◌᫛ = ◌̞ lowered, placed above (encoded as a Harrington diacritic)'),
    (0x1AE0, '◌᫠ = ◌̘ advanced tongue root, placed above (IPA diacritics above, L2/24-080)'),
    (0x1AE1, '◌᫡ = ◌̙ retracted tongue root, placed above'),
    (0x1AE2, '◌᫢ = ◌̠ retracted, placed above'),
    (0x1AE3, '◌᫣ = ◌̺ apical, placed above'),
    (0x1AE4, '◌᫤ = ◌̻ laminal, placed above'),
    (0x1AE5, '◌᫥ = ◌̼ linguolabial, placed above'),
    (0x1AE8, '◌᫨ = ◌͇ extIPA alveolar, placed above'),
    (0x1AE9, '◌᫩ = ◌̚ no audible release, centred'),
    (0x1AEA, '◌᫪ = ◌͎ extIPA whistled, placed above'),
    (0x1AEB, '◌᫫ = ◌͢ extIPA sliding articulation, placed above'),
    (0x1DF5, '◌᷵ = ◌̝ raised, placed above'),
    (0x1DC6, '◌᷆ macron-grave: a contour tone the tone letters write (˧˩)'),
    (0x1DC7, '◌᷇ acute-macron: a contour tone the tone letters write (˥˧)'),
    (0x1DC9, '◌᷉ acute-grave-acute: a contour tone the tone letters write (˥˩˥)'),
    (R(0x1D6C, 0x1D76), 'letter with middle tilde = letter + ◌̴ (velarized or pharyngealized)'),
    (0x1D8F, 'ᶏ = a˞ (precomposed rhotic vowel)'),
    (0x1D90, 'ᶐ = ɑ˞ (precomposed rhotic vowel)'),
    (0x1D92, 'ᶒ = e˞ (precomposed rhotic vowel)'),
    (0x1D93, 'ᶓ = ɛ˞ (precomposed rhotic vowel)'),
    (0x1D94, 'ᶔ = ɜ˞ (precomposed rhotic vowel)'),
    (0x1D95, 'ᶕ = ə˞ (precomposed rhotic vowel)'),
    (0x1D96, 'ᶖ = i˞ (precomposed rhotic vowel)'),
    (0x1D97, 'ᶗ = ɔ˞ (precomposed rhotic vowel)'),
    (0x1D99, 'ᶙ = u˞ (precomposed rhotic vowel)'),
    (0x1DF1A, '𝼚 = ɨ˞ (precomposed rhotic vowel)'),
    (0x1DF1B, '𝼛 = o˞ (precomposed rhotic vowel)'),
    (0x1DF19, '𝼙 = ɖ͡ʐ (affricate ligature)'),
    (0x1DF1C, '𝼜 = ʈ͡ʂ (affricate ligature)'),
    (0x1DF1F, '𝼟 = d͡ð (affricate ligature)'),
    (0x1DF20, '𝼠 = d͡ɮ (affricate ligature)'),
    (0x1DF21, '𝼡 = ɖ͡𝼅 (affricate ligature; 𝼅 is extIPA)'),
    (0x1DF22, '𝼢 = t͡ɬ (affricate ligature)'),
    (0x1DF23, '𝼣 = ʈ͡ꞎ (affricate ligature; ꞎ is extIPA)'),
    (0x1DF24, '𝼤 = t͡θ (affricate ligature)'),
    (0x1DF2B, '𝼫 = d͡ʑ (affricate ligature)'),
    (0x1DF2C, '𝼬 = t͡ɕ (affricate ligature)'),
)

# ---- B: extIPA (ICPLA 2015, IPA 2021) and VoQS (2016) ------------------------------------------
B = table(
    (0x02A9, 'ʩ extIPA: voiceless velopharyngeal fricative'),
    (0x02AA, 'ʪ extIPA: voiceless grooved lateral (lateral+median) alveolar fricative, not ls'),
    (0x02AB, 'ʫ extIPA: voiced grooved lateral (lateral+median) alveolar fricative, not lz'),
    (0x02AC, 'ʬ extIPA: bilabial percussive'),
    (0x02AD, 'ʭ extIPA: bidental percussive'),
    (0x02B6, 'ʶ VoQS: uvularized voice'),
    (0x02EC, 'ˬ extIPA: pre-/post-voicing'),
    (0x02ED, '˭ extIPA: unaspirated'),
    (0x02F3, '˳ extIPA: extended voicelessness (p˳)'),
    (0x02F7, '˷ extIPA: creaky offglide (a˷)'),
    (0x0323, '◌̣ VoQS: whispery voice (Ṿ)'),
    (0x033E, '◌̾ extIPA: nareal fricative, nasal fricative escape'),
    (0x0346, '◌͆ extIPA: dentolabial (with ◌̪, interdental)'),
    (0x0347, '◌͇ extIPA: alveolar; VoQS alveolarized voice'),
    (0x0348, '◌͈ extIPA: strong articulation; VoQS pressed voice'),
    (0x0349, '◌͉ extIPA: weak articulation; VoQS slack voice'),
    (0x034A, '◌͊ extIPA: denasal; VoQS denasalized voice'),
    (0x034B, '◌͋ extIPA 2015: nasal escape'),
    (0x034C, '◌͌ extIPA 2015: velopharyngeal friction'),
    (0x034D, '◌͍ extIPA: labial spreading; VoQS spread-lip voice'),
    (0x034E, '◌͎ extIPA: whistled articulation'),
    (0x0354, '◌͔ extIPA: offset (left/right); VoQS offset jaw'),
    (0x0355, '◌͕ extIPA: offset (left/right); VoQS offset jaw'),
    (0x0362, '◌͢ extIPA: sliding (slurred) articulation'),
    (0x1ABB, '◌᪻ extIPA 2021: partial voicing/devoicing, above'),
    (0x1ABD, '◌᪽ extIPA 2021: partial voicing/devoicing, below'),
    (R(0x1AC1, 0x1AC4), 'extIPA 2021: initial/final partial voicing, above and below'),
    (0x1DB9, 'ᶹ VoQS: labiodentalized voice'),
    (0x10780, '𐞀 VoQS: aryepiglottic phonation'),
    (0x10790, '𐞐 extIPA 2021: velopharyngeal frication'),
    (0x10799, '𐞙 extIPA 2021: grooved lateral fricative release'),
    (0x1079A, '𐞚 extIPA 2021: voiced grooved lateral fricative release'),
    (0x1079C, '𐞜 extIPA 2021: velar lateral fricative release'),
    (0x1079D, '𐞝 extIPA 2021: retroflex lateral fricative release'),
    (0x1079F, '𐞟 extIPA 2021: voiced retroflex lateral fricative release'),
    (0x107A1, '𐞡 extIPA 2021: palatal lateral fricative release'),
    (0x107AA, '𐞪 extIPA 2021: with 𐞐, velopharyngeal trill'),
    (0x1DF00, '𝼀 extIPA 2021: velopharyngeal trill (snort)'),
    (0x1DF01, '𝼁 extIPA 2021: voiced velodorsal plosive'),
    (0x1DF02, '𝼂 extIPA 2021: voiced upper-pharyngeal plosive'),
    (0x1DF03, '𝼃 extIPA 2021: voiceless velodorsal plosive'),
    (0x1DF04, '𝼄 extIPA 2021: velar lateral fricative'),
    (0x1DF05, '𝼅 extIPA 2021: voiced retroflex lateral fricative'),
    (0x1DF06, '𝼆 extIPA 2021: palatal lateral fricative'),
    (0x1DF07, '𝼇 extIPA 2021: velodorsal nasal'),
)

# ---- C: phonetic, another tradition ----------------------------------------------------------
C = table(
    (0x0269, 'ɩ withdrawn IPA (1989), for ɪ'),
    (0x0277, 'ɷ withdrawn IPA (1989), for ʊ'),
    (0x027C, 'ɼ withdrawn IPA (1989): strident apical r'),
    (0x027F, 'ɿ Sinological apical vowel'),
    (0x0285, 'ʅ Sinological apical vowel'),
    (0x0286, 'ʆ withdrawn IPA (1989), for ʃʲ'),
    (0x0287, 'ʇ withdrawn IPA (1989) dental click'),
    (0x0293, 'ʓ withdrawn IPA (1989), for ʒʲ'),
    (0x0296, 'ʖ withdrawn IPA (1989) lateral click'),
    (0x0297, 'ʗ withdrawn IPA (1989) postalveolar click'),
    (0x029A, 'ʚ withdrawn IPA (an error for ɞ)'),
    (0x029E, 'ʞ withdrawn IPA (1989) velar click'),
    (0x02A0, 'ʠ withdrawn IPA (1993) voiceless uvular implosive'),
    (R(0x02AE, 0x02AF), 'Sinological apical vowels'),
    (0x02B1, 'ʱ breathy-voiced release; common, but not a chart diacritic'),
    (R(0x02B3, 0x02B5), 'superscript r letters (rhotic release, older rhotacization)'),
    (0x02B8, 'ʸ superscript y'),
    (R(0x02B9, 0x02BA), 'prime, double prime: stress (Americanist), Slavist palatalization'),
    (0x02BD, 'ʽ weak aspiration (older IPA)'),
    (R(0x02BE, 0x02BF), 'half rings: Semitist transcription of hamza and ain'),
    (0x02C0, 'ˀ glottalized (Americanist and others)'),
    (R(0x02C2, 0x02C5), 'arrowheads: fronted, backed, raised, lowered (UPA and others)'),
    (R(0x02C6, 0x02C7), 'spacing circumflex, caron: tone and stress in other traditions'),
    (R(0x02C9, 0x02CB), 'spacing macron, acute, grave: tone marks (Bopomofo, Sinological)'),
    (R(0x02CD, 0x02CF), 'low macron, grave, acute: tone marks (Sinological)'),
    (0x02D9, '˙ Mandarin neutral tone (Bopomofo)'),
    (0x02DF, '˟ Swedish grave accent (prosodic transcription)'),
    (R(0x02E2, 0x02E3), 'superscript s, x (fricative release; not a chart diacritic)'),
    (R(0x02EA, 0x02EB), 'Bopomofo departing tone marks'),
    (R(0x02EF, 0x02F2), 'UPA modifiers: low arrowheads'),
    (R(0x02F4, 0x02F6), 'UPA modifiers: middle accents'),
    (R(0x02F8, 0x02FF), 'UPA modifiers: raised colon, begin/end tone, shelves, low arrow'),
    (0x0307, '◌̇ IPA palatalization, withdrawn 1976 (NamesList)'),
    (0x0310, '◌̐ candrabindu: Indological transcription of nasality'),
    (0x0313, '◌̓ Americanist: ejective or glottalization'),
    (0x0315, '◌̕ Americanist: ejective'),
    (R(0x0316, 0x0317), 'grave/acute below: tone marking in other traditions'),
    (R(0x0321, 0x0322), 'palatalized and retroflex hooks below: withdrawn IPA'),
    (0x0328, '◌̨ Americanist: nasalization'),
    (0x032B, '◌̫ IPA labialization, withdrawn'),
    (0x032D, '◌̭ Americanist: fronted articulation'),
    (0x032E, '◌̮ Hittite and Indo-Europeanist transcription'),
    (0x0331, '◌̱ Americanist and Semitist transcription'),
    (0x0350, '◌͐ UPA'),
    (R(0x0352, 0x0353), 'UPA'),
    (0x0356, '◌͖ UPA'),
    (0x0358, '◌͘ Southern Min transcription'),
    (0x0359, '◌͙ phonetic notation (asterisk below)'),
    (0x035B, '◌͛ Lithuanian phonetics, medievalist transcription'),
    (R(0x035D, 0x0360), 'double breve, macron, macron below, tilde: dictionary respelling, Americanist'),
    (R(0x0363, 0x036F), 'superscript letter diacritics (medievalist; Teuthonista dialect transcription)'),
    (R(0x1AB0, 0x1ABA), 'Teuthonista (German dialectology)'),
    (0x1ABC, '◌᪼ Teuthonista double parentheses'),
    (0x1ABE, '◌᪾ Teuthonista parentheses overlay'),
    (R(0x1ABF, 0x1AC0), 'Scots phonetic notation'),
    (0x1AC5, '◌᫅ phonetic punctuation (square brackets above)'),
    (0x1AC6, '◌᫆ Harrington diacritic'),
    (0x1AC7, '◌᫇ phonetic diacritic (inverted double arch above)'),
    (R(0x1AC9, 0x1ACA), 'phonetic diacritics (double plus above/below)'),
    (R(0x1ACF, 0x1AD8), 'compound tone diacritics beyond the chart (Africanist and other tone transcription)'),
    (R(0x1AD9, 0x1ADA), 'Harrington diacritics (sharp, flat)'),
    (R(0x1ADC, 0x1ADD), 'Harrington diacritics'),
    (R(0x1ADE, 0x1ADF), 'compound tone diacritics beyond the chart'),
    (R(0x1AE6, 0x1AE7), 'double arch below/above (no chart counterpart)'),
    (R(0x1AEC, 0x1AF0), 'compound tone diacritics beyond the chart'),
    (R(0x1DCA, 0x1DCD), 'UPA and Teuthonista marks'),
    (R(0x1DE7, 0x1DF4), 'Teuthonista superscript letters'),
    (0x1DF9, '◌᷹ phonetic (wide inverted bridge below)'),
    (R(0x1DFC, 0x1DFF), 'UPA and other phonetic marks'),
    (R(0x1D00, 0x1D2B), 'UPA letters: small capitals, turned and sideways letters'),
    (0x1D6B, 'ᵫ UPA ue ligature'),
    (0x1D77, 'ᵷ turned g (Celticist, Americanist)'),
    (0x1D79, 'ᵹ insular g (Celticist phonetic)'),
    (0x1D7A, 'ᵺ dictionary respelling th'),
    (R(0x1D7B, 0x1D7F), 'barred small capitals, iota, upsilon, p (American and other dictionary and phonetic use)'),
    (0x1D91, 'ᶑ retroflex implosive: used, but not a chart letter'),
    (0x1D98, 'ᶘ esh with retroflex hook (Sinological)'),
    (0x1D9A, 'ᶚ ezh with retroflex hook (Sinological)'),
    (R(0xA700, 0xA707), 'Chinese tone marks (Sinological)'),
    (R(0xA708, 0xA716), 'dotted and left-stem tone bars (Sinological)'),
    (R(0xA717, 0xA71A), 'Chinese and other tone notation'),
    (0xA71F, 'ꜟ low inverted exclamation mark (Africanist tone notation)'),
    (R(0x1DF08, 0x1DF18), 'Latin Extended-G phonetic letters outside the chart and extIPA'),
    (0x1DF1D, '𝼝 c with retroflex hook (other traditions)'),
    (0x1DF1E, '𝼞 s with curl (Sinological)'),
    (R(0x1DF25, 0x1DF2A), 'letters with mid-height left hook (other traditions)'),
    (R(0x1DF2D, 0x1DF3D), 'letters with palatal hook (withdrawn IPA style)'),
    (R(0x1DF3E, 0x1DF81), 'barred, split and phonotypic letters (other phonetic alphabets)'),
)

# ---- not-phonetic -----------------------------------------------------------------------------
NOT_PHONETIC = table(
    (0x02BB, 'ʻ Polynesian orthography (okina)'),
    (0x02D8, '˘ spacing clone of a diacritic'),
    (R(0x02DA, 0x02DD), 'spacing clones of diacritics'),
    (0x02EE, 'ˮ Nenets orthography'),
    (0x0305, '◌̅ overline'),
    (0x0309, '◌̉ Vietnamese tone mark'),
    (0x030E, '◌̎ Marshallese orthography'),
    (0x0312, '◌̒ Latvian cedilla above'),
    (0x0314, '◌̔ Greek rough breathing'),
    (0x031B, '◌̛ Vietnamese horn'),
    (0x0326, '◌̦ Romanian, Latvian comma below'),
    (R(0x0332, 0x0333), 'underline'),
    (R(0x0335, 0x0338), 'stroke and solidus overlays (typographic)'),
    (0x033F, '◌̿ double overline'),
    (R(0x0342, 0x0345), 'Greek accents'),
    (0x034F, 'combining grapheme joiner (invisible)'),
    (0x035A, '◌͚ Kharoshthi transliteration'),
    (R(0x1ACB, 0x1ACE), 'Middle English letters (Ormulum)'),
    (R(0x1DC0, 0x1DC3), 'Greek editorial and Glagolitic marks'),
    (R(0x1DCE, 0x1DE6), 'medievalist abbreviation marks and superscript letters'),
    (R(0x1DF6, 0x1DF7), 'Cyrillic kavyka'),
    (0x1DF8, '◌᷸ dot above left (transliteration)'),
    (R(0x1DFA, 0x1DFB), 'dot below left, deletion mark (transliteration, editorial)'),
    (R(0x1DF90, 0x1DF96), 'medieval scribal letters'),
)

# ---- name patterns, for what nothing above classified -----------------------------------------
PATTERNS = [
    (r'^MODIFIER LETTER ', 'C', 'superscript letter used in phonetic transcription, not a chart diacritic'),
    (r'SUBSCRIPT', 'C', 'subscript letter used in phonetic transcription'),
    (r'WITH PALATAL HOOK', 'C', 'palatal hook: withdrawn IPA (1989)'),
]


def cp_list(spec):
    """Code points from 'U+0063', ['U+0063', 'U+0327'], 'U+2197 U+FE0E' or 'U+02E9+U+02E5'."""
    if isinstance(spec, list):
        return [c for s in spec for c in cp_list(s)]
    return [int(t[2:], 16) for t in re.split(r'[\s+]+(?=U)', spec.strip()) if t]


def main():
    with open(os.path.join(UNICODE, 'Blocks.txt'), encoding='utf-8') as f:
        first = f.readline().strip()
        blocks = {}
        for line in f:
            line = line.split('#')[0].strip()
            if ';' in line:
                rng, name = line.split(';')
                a, b = (int(x, 16) for x in rng.split('..'))
                blocks[name.strip()] = (a, b)
    version = re.search(r'Blocks-([\d.]+)\.txt', first).group(1)
    names = {}
    with open(os.path.join(UNICODE, 'UnicodeData.txt'), encoding='utf-8') as f:
        for line in f:
            fld = line.split(';')
            names[int(fld[0], 16)] = (fld[1], fld[2])
    block_of = {}
    for bn in BLOCKS:
        a, b = blocks[bn]
        for cp in R(a, b):
            if cp in names:
                assert not names[cp][0].startswith('<'), 'a range entry inside %s' % bn
                block_of[cp] = bn

    with open(CHECKLIST, encoding='utf-8') as f:
        symbols = json.load(f)['symbols']
    with open(ALIASES, 'rb') as f:
        aliases = tomli.load(f)

    hits = collections.defaultdict(list)  # cp -> [(class, reason)] from data and explicit lists
    for e in symbols:
        for cp in cp_list(e['codepoints']):
            hits[cp].append(('A', 'checklist %s %s' % (e['id'], e['symbol'])))
        for alt in e.get('alt_codepoints') or []:
            for cp in cp_list(alt):
                if cp not in cp_list(e['codepoints']):
                    hits[cp].append(('alias', 'checklist alternative spelling of %s' % e['symbol']))
    for mode in aliases.values():
        for k, v in mode.items():
            if len(k) == 1:
                hits[ord(k)].append(('alias', 'aliases.toml: %s for %s' % (k, v)))
    for cls, tab in (('alias', ALIAS), ('B', B), ('C', C), ('not-phonetic', NOT_PHONETIC)):
        for cp, why in tab.items():
            hits[cp].append((cls, why))

    stray = sorted(cp for cp in set(ALIAS) | set(B) | set(C) | set(NOT_PHONETIC) if cp not in block_of)
    assert not stray, 'listed but not assigned in the ten blocks: %s' % ' '.join('U+%04X' % c for c in stray)

    result, problems = {}, []
    for cp in sorted(block_of):
        name = names[cp][0]
        h = hits.get(cp) or [(c, why) for pat, c, why in PATTERNS if re.search(pat, name)]
        classes = {c for c, _ in h}
        if len(classes) != 1:
            problems.append('U+%04X %s: %s' % (cp, name, h or 'no rule'))
            continue
        result[cp] = (classes.pop(), h[0][1])
    if problems:
        sys.exit('not classified exactly once:\n  ' + '\n  '.join(problems))
    assert set(result) == set(block_of)

    by_block = collections.OrderedDict((bn, collections.Counter()) for bn in BLOCKS)
    for cp, (cls, _) in result.items():
        by_block[block_of[cp]][cls] += 1
    total = collections.Counter(cls for cls, _ in result.values())
    print('Unicode %s (%s)' % (version, first.lstrip('# ')))
    print('%-40s %5s  %s' % ('block', 'cps', '  '.join('%5s' % c[:5] for c in CLASSES)))
    for bn, cnt in by_block.items():
        print('%-40s %5d  %s' % (bn, sum(cnt.values()), '  '.join('%5d' % cnt[c] for c in CLASSES)))
    print('%-40s %5d  %s' % ('total', len(result), '  '.join('%5d' % total[c] for c in CLASSES)))

    out = ['# The Unicode net (DESIGN.md 1): every assigned code point of ten blocks in exactly one class.',
           '# GENERATED by docs/tts-extension/inventory/build_unicode_net.py; do not edit by hand.',
           '# Read by engine/ipa/coverage.py. Unicode version: %s (from Blocks.txt: %s).' % (version, first.lstrip('# ')),
           '# Assigned code points: %d (%s).' % (len(result), ', '.join('%s %d' % (c, total[c]) for c in CLASSES)),
           '#',
           '# Classes: A = a checklist entry; alias = another spelling of a Tier A or B thing;',
           '# B = extIPA (2015/2021) or VoQS (2016); C = phonetic, another tradition; not-phonetic.',
           '#',
           '# The Tier B list was checked against:']
    out += ['#   %s' % s for s in SOURCES]
    out += ['', '[class]']
    for cls in CLASSES:
        out.append('%s = [' % (cls if re.match(r'^[A-Za-z]+$', cls) else '"%s"' % cls))
        run = []
        cps = sorted(cp for cp, (c, _) in result.items() if c == cls)

        def flush():
            if not run:
                return
            a, b = run[0], run[-1]
            rng = 'U+%04X' % a if a == b else 'U+%04X..U+%04X' % (a, b)
            chars = ' '.join(('◌' + chr(c)) if names[c][1].startswith('M') else chr(c) for c in run[:12])
            more = ' ...' if len(run) > 12 else ''
            out.append('  %-26s # %s%s: %s' % ('"%s",' % rng, chars, more, result[a][1]))
        for cp in cps:
            # One line a run of consecutive code points with the same reason (unassigned gaps break runs).
            if run and (cp != run[-1] + 1 or result[cp][1] != result[run[0]][1]):
                flush()
                run = []
            run.append(cp)
        flush()
        out.append(']')
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('wrote %s' % os.path.relpath(OUT, ROOT))


if __name__ == '__main__':
    main()
