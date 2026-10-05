"""The symbol-to-capability traceability table of DESIGN.md, section 4.

One decision for every entry of inventory/IPA_CHECKLIST.json: how it will be realised (as it is,
by composition, or only with a new mechanism), which capabilities it uses, the state it is meant
to end in, and how it will be proved. This file is the source; TRACEABILITY.md and
traceability.json are written from it and are never edited by hand.

    python docs/tts-extension/design/build_traceability.py          (PYTHONUTF8=1)

It fails, loudly, if a checklist entry has no decision, a decision names no checklist entry, a
capability or test is undefined, a capability to be built serves no symbol, two entries the chart
prints as the same thing are decided differently, or a decision contradicts its own list of needs.

These are plans, not results: nothing here has been rendered. Every state is still MISSING in the
checklist until Phase 4 proves it (playbook R19f).
"""

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKLIST = os.path.join(HERE, '..', 'inventory', 'IPA_CHECKLIST.json')

# What the engine can already do (ARCHITECTURE_MAP.md section 9; docs/SOUNDS.md).
EXISTING = collections.OrderedDict([
    ('X1', 'a phone of the speaking module'),
    ('X2', 'formants and bandwidths moved against the module phone (f1-f4, g1-g4, b1-b4, reach)'),
    ('X3', 'noise shaping (fric, a2-a6, ab, af)'),
    ('X4', 'stop timing and release (vot, asp, lead, bar, voi, burst, noburst, pre, ej, impl)'),
    ('X5', 'a sound the accent layer makes beside a vowel (<, >, ms, hush, whisper)'),
    ('X6', 'tap: brief closures cut into a sound (tap, tapms)'),
    ('X7', 'phonation keys (oq, tl, creak, whisper, brth)'),
    ('X8', 'nasal coupling, one knob (nas)'),
    ('X9', 'duration (dur, hold)'),
    ('X10', 'stress: the module\'s stress digits and the accent line'),
    ('X11', 'tone lines and the layer\'s own pitch (tone, f0=own)'),
    ('X12', 'phrase endings ({P}, punctuation)'),
    ('X13', 'syllables and pieces in the annotation; an affricate said as stop + fricative (says)'),
])

# What has to be built (DESIGN.md section 4.3, in priority order). C1-C4 are needed by every
# symbol (nothing can be entered, composed or proved without them) and are not repeated per row.
TO_BUILD = collections.OrderedDict([
    ('C1', 'never silent: a diagnostics channel and a strict mode'),
    ('C2', 'the IPA reader and segment model'),
    ('C3', 'the master table, its validator and the adapter (composition when a pack is built)'),
    ('C4', 'composition when speaking, with nearest-feature fallback and a loud warning'),
    ('C5', 'pitch: register steps, a slope per phrase, pitch moved by a consonant under own pitch'),
    ('C6', 'phonation held through a sound or at its edges; breath noise on voiced frames'),
    ('C7', 'syllabicity: a consonant as a syllable, a vowel as none'),
    ('C8', 'edge transforms on the neighbouring phone (spreading)'),
    ('C9', 'the nasal and the second pole/zero pair, set directly'),
    ('C10', 'timed events on a carrier phone'),
    ('C11', 'aperture modulation at a stated rate (trills)'),
    ('C12', 'transient excitation: an impulse into the resonators'),
])
UNIVERSAL = ('C1', 'C2', 'C3', 'C4')

# How each class is proved (DESIGN.md section 10.2 says what each measures and its pass mark).
TESTS = collections.OrderedDict([
    ('T-stop', 'closure length, burst spectrum, voice onset time, F2/F3 at the vowel edge, in a_a i_i u_u'),
    ('T-nasal', 'murmur F1, antiformant, F2 transitions'),
    ('T-fric', 'noise centre and band edges (0 to 5.5 kHz), length, voicing'),
    ('T-approx', 'F1-F3 mid-sound and their movement into the vowel'),
    ('T-tap', 'one brief amplitude dip'),
    ('T-trill', 'modulation rate in Hz, depth in dB, number of closures'),
    ('T-vowel', 'F1-F3 at the midpoint against the reference range; length'),
    ('T-click', 'silent closure, burst length and level against the vowel, spectrum by place, no breath'),
    ('T-airstream', 'implosive: voicing that grows through the closure, weak burst; ejective: silence after the burst, no breath'),
    ('T-phonation', 'H1-H2, harmonics-to-noise, period regularity, against the plain sound'),
    ('T-nasality', 'A1-P0, F1 bandwidth, against the plain vowel'),
    ('T-shift', 'the named formant or noise measure moves the stated way against the plain base'),
    ('T-length', 'length ratio against the plain base'),
    ('T-syllable', 'number of syllable peaks; length of the marked sound'),
    ('T-release', 'burst absent, or replaced by a murmur or a lateral, at the release'),
    ('T-stress', 'pitch, length and level of the marked syllable against an unmarked one'),
    ('T-tone', 'F0 contour against the points asked, in semitones; order of the levels'),
    ('T-register', 'the tones after the mark sit lower (or higher) by the step asked'),
    ('T-slope', 'slope of F0 across the phrase, against the unmarked phrase'),
    ('T-boundary', 'pause, final lengthening and boundary pitch; or their absence'),
    ('T-sequence', 'the two parts in order, one closure, length less than the two apart'),
    ('T-contrast', 'measurably different from its nearest neighbour, in the right direction'),
])

A, C, N = 'as-is', 'composition', 'new mechanism'
M, K, R = 'mapped', 'composed', 'created'
# The end state of a letter is not a judgement, it is a rule (DESIGN.md section 4.1): `mapped` if one of
# the seven IBM modules the checklist read has the sound as a phone of its own (its "already"; frca, jajp
# and plpl were not consulted, so the created letters can only become fewer), `created` if none has,
# so that the sound is designed here under the Unmappable Sound Protocol and registered; `composed`
# only where the letter is a base plus a general rule (the implosives). L asks for the rule.
L = 'by rule'

# id: (decision, end state, existing used, to build ('?' = only if the measurement fails), how, tests)
D = {}


def row(ident, decision, state, existing, build, how, tests):
    if ident in D:
        raise SystemExit('decided twice: ' + ident)
    D[ident] = (decision, state, existing.split(), build.split(), how, tests.split())


# ---- Consonants (pulmonic) ----
row('U+0070', A, L, 'X1', '', 'the module\'s p', 'T-stop')
row('U+0062', A, L, 'X1 X4', '', 'the module\'s b, voiced through the closure where the module\'s is weak', 'T-stop')
row('U+0074', A, L, 'X1', '', 'the module\'s t', 'T-stop')
row('U+0064', A, L, 'X1 X4', '', 'the module\'s d, voiced through the closure where needed', 'T-stop')
row('U+0288', A, L, 'X1 X2 X3 X4', '', 't with a retroflex locus (F3 and F4 lowered) and its burst shaped', 'T-stop T-contrast')
row('U+0256', A, L, 'X1 X2 X3 X4', '', 'd with a retroflex locus', 'T-stop T-contrast')
row('U+0063', A, L, 'X1 X2 X3 X4', '', 't with a palatal locus (F2 raised) and a longer, noisier release', 'T-stop T-contrast')
row('U+025F', A, L, 'X1 X2 X3 X4', '', 'd with a palatal locus', 'T-stop T-contrast')
row('U+006B', A, L, 'X1', '', 'the module\'s k', 'T-stop')
row('U+0261', A, L, 'X1 X4', '', 'the module\'s g, voiced through the closure where needed', 'T-stop')
row('U+0071', A, L, 'X1 X2 X3 X4', '', 'k with a uvular locus (F2 lowered, F1 raised) and a lower burst', 'T-stop T-contrast')
row('U+0262', A, L, 'X1 X2 X3 X4', '', 'g with a uvular locus', 'T-stop T-contrast')
row('U+0294', A, L, 'X5', 'C6?', 'a silence the layer makes, with the vowel edges glottalised', 'T-stop T-phonation')
row('U+006D', A, L, 'X1', '', 'the module\'s m', 'T-nasal')
row('U+0271', A, L, 'X1 X2', 'C9?', 'm with a labiodental locus', 'T-nasal T-contrast')
row('U+006E', A, L, 'X1', '', 'the module\'s n', 'T-nasal')
row('U+0273', A, L, 'X1 X2', 'C9?', 'n with a retroflex locus (F3 lowered)', 'T-nasal T-contrast')
row('U+0272', A, L, 'X1 X2', 'C9?', 'the module\'s palatal nasal, or n with a palatal locus', 'T-nasal T-contrast')
row('U+014B', A, L, 'X1', '', 'the module\'s velar nasal', 'T-nasal')
row('U+0274', A, L, 'X1 X2', 'C9?', 'the velar nasal with a uvular locus', 'T-nasal T-contrast')
row('U+0299', N, L, 'X1 X2', 'C11', 'a bilabial carrier whose opening is modulated at a trill\'s rate', 'T-trill T-contrast')
row('U+0072', N, L, 'X1 X2 X6', 'C11', 'the module\'s trill, or a carrier modulated at a stated rate', 'T-trill')
row('U+0280', N, L, 'X1 X2 X3 X6', 'C11', 'a uvular carrier modulated at a stated rate, with some noise', 'T-trill T-contrast')
row('U+2C71', A, L, 'X1 X2 X6', '', 'a labiodental carrier with one brief closure', 'T-tap T-contrast')
row('U+027E', A, L, 'X1 X6', '', 'the module\'s tap, or a carrier with one brief closure', 'T-tap')
row('U+027D', A, L, 'X1 X2 X6', '', 'a tap with a retroflex locus (F3 lowered)', 'T-tap T-contrast')
row('U+0278', A, L, 'X1 X2 X3', '', 'f with a bilabial locus and weaker, flatter noise', 'T-fric T-contrast')
row('U+03B2', A, L, 'X1 X2 X3', '', 'v with a bilabial locus and weak friction', 'T-fric T-contrast')
row('U+0066', A, L, 'X1', '', 'the module\'s f', 'T-fric')
row('U+0076', A, L, 'X1', '', 'the module\'s v', 'T-fric')
row('U+03B8', A, L, 'X1 X2 X3', '', 'the module\'s dental fricative, or f with a dental locus and its noise', 'T-fric T-contrast')
row('U+00F0', A, L, 'X1 X2 X3', '', 'the module\'s voiced dental fricative, or v reshaped', 'T-fric T-contrast')
row('U+0073', A, L, 'X1', '', 'the module\'s s', 'T-fric')
row('U+007A', A, L, 'X1', '', 'the module\'s z', 'T-fric')
row('U+0283', A, L, 'X1', '', 'the module\'s sh', 'T-fric')
row('U+0292', A, L, 'X1', '', 'the module\'s zh', 'T-fric')
row('U+0282', A, L, 'X1 X2 X3', '', 'sh with a retroflex shape (lower noise peak, F3 lowered)', 'T-fric T-contrast')
row('U+0290', A, L, 'X1 X2 X3', '', 'zh with a retroflex shape', 'T-fric T-contrast')
row('U+00E7', A, L, 'X1 X2 X3', '', 'the module\'s palatal fricative, or sh/x reshaped', 'T-fric T-contrast')
row('U+029D', A, L, 'X1 X3 X4', '', 'the palatal fricative voiced', 'T-fric T-contrast')
row('U+0078', A, L, 'X1 X3', '', 'the module\'s velar fricative', 'T-fric')
row('U+0263', A, L, 'X1 X2 X3 X4', '', 'the velar fricative voiced', 'T-fric T-contrast')
row('U+03C7', A, L, 'X1 X2 X3', '', 'the velar fricative with a uvular shape', 'T-fric T-contrast')
row('U+0281', A, L, 'X1 X2 X3', '', 'the module\'s uvular r, or the velar fricative voiced and lowered', 'T-fric T-contrast')
row('U+0127', A, L, 'X5 X2', '', 'breath the layer makes beside the vowel, F1 raised and F2 lowered', 'T-fric T-contrast')
row('U+0295', A, L, 'X5 X2 X4', 'C6?', 'the same with voice', 'T-approx T-contrast')
row('U+0068', A, L, 'X5', '', 'breath the layer makes beside the vowel (or the module\'s h)', 'T-fric')
row('U+0266', A, L, 'X5 X4', 'C6?', 'the same with voice', 'T-phonation T-contrast')
row('U+026C', A, L, 'X1 X3 X7', '', 'l said without voice, with friction', 'T-fric T-contrast')
row('U+026E', A, L, 'X1 X3', '', 'l with friction', 'T-fric T-contrast')
row('U+028B', A, L, 'X1 X3', '', 'v without its friction', 'T-approx T-contrast')
row('U+0279', A, L, 'X1 X2', '', 'the module\'s English r, or an r reshaped (F3 lowered)', 'T-approx')
row('U+027B', A, L, 'X1 X2', '', 'the approximant r with F3 lower still', 'T-approx T-contrast')
row('U+006A', A, L, 'X1', '', 'the module\'s j', 'T-approx')
row('U+0270', A, L, 'X1 X2', '', 'w without its rounding (F2 raised)', 'T-approx T-contrast')
row('U+006C', A, L, 'X1', '', 'the module\'s l', 'T-approx')
row('U+026D', A, L, 'X1 X2', '', 'l with a retroflex shape (F3 lowered)', 'T-approx T-contrast')
row('U+028E', A, L, 'X1 X2', '', 'the module\'s palatal lateral, or l with F2 raised', 'T-approx T-contrast')
row('U+029F', A, L, 'X1 X2', '', 'l with a velar shape (F2 lowered)', 'T-approx T-contrast')

# ---- Consonants (non-pulmonic) ----
row('U+0298', N, L, 'X1 X3', 'C10', 'closure, a noisy low burst at the lips, a short silence, a weak velar release', 'T-click T-contrast')
row('U+01C0', N, L, 'X1 X3', 'C10', 'closure, a long noisy high burst, a short silence, a weak velar release', 'T-click T-contrast')
row('U+01C3', N, L, 'X1 X3', 'C10 C12?', 'closure, one abrupt burst with low peaks, a short silence, a weak velar release', 'T-click T-contrast')
row('U+01C2', N, L, 'X1 X3', 'C10 C12?', 'closure, one abrupt burst with high peaks, a short silence, a weak velar release', 'T-click T-contrast')
row('U+01C1', N, L, 'X1 X3', 'C10', 'closure, a long noisy low burst at the side, a short silence, a weak velar release', 'T-click T-contrast')
row('U+0253', C, K, 'X1 X4', 'C5?', 'b + implosive: voicing that grows through the closure, a weak burst', 'T-airstream T-contrast')
row('U+0257', C, K, 'X1 X4', 'C5?', 'd + implosive', 'T-airstream T-contrast')
row('U+0284', C, K, 'X1 X2 X4', 'C5?', 'the palatal stop + implosive', 'T-airstream T-contrast')
row('U+0260', C, K, 'X1 X4', 'C5?', 'g + implosive', 'T-airstream T-contrast')
row('U+029B', C, K, 'X1 X2 X4', 'C5?', 'the uvular stop + implosive', 'T-airstream T-contrast')
row('U+02BC', C, K, 'X4 X5 X9', 'C5? C6?', 'a voiceless stop, affricate or fricative + ejective: a harder burst, then silence before the voice (after an affricate or fricative the silence is made by the layer)', 'T-airstream T-contrast')

# ---- Other symbols ----
row('U+028D', A, L, 'X1 X7', '', 'w said without voice', 'T-fric T-contrast')
row('U+0077', A, L, 'X1', '', 'the module\'s w', 'T-approx')
row('U+0265', A, L, 'X1 X2', '', 'the module\'s rounded palatal glide, or j with its formants lowered', 'T-approx T-contrast')
row('U+029C', A, L, 'X5 X2 X3', 'C11? C6?', 'strong breath the layer makes beside the vowel, F1 raised further than for the pharyngeal', 'T-fric T-contrast')
row('U+02A2', A, L, 'X5 X2 X4 X7', 'C11? C6?', 'the same with voice and creak', 'T-approx T-phonation T-contrast')
row('U+02A1', N, L, 'X5 X2', 'C10', 'a silence the layer makes, then a burst, with F1 high at the vowel edge', 'T-stop T-contrast')
row('U+0255', A, L, 'X1 X2 X3', '', 'sh with a palatal shape (F2 raised, noise peak raised)', 'T-fric T-contrast')
row('U+0291', A, L, 'X1 X2 X3', '', 'zh with a palatal shape', 'T-fric T-contrast')
row('U+027A', A, L, 'X1 X2 X6', '', 'l with one brief closure', 'T-tap T-contrast')
row('U+0267', A, L, 'X1 X2 X3', '', 'the velar fricative with a second, sh-like noise peak and rounding (marked approximate)', 'T-fric T-contrast')
row('U+035C', C, K, 'X13 X4 X9', '', 'two letters as one sound: an affricate (stop released into its fricative) or a double closure', 'T-sequence')
row('U+0361', C, K, 'X13 X4 X9', '', 'two letters as one sound: an affricate (stop released into its fricative) or a double closure', 'T-sequence')

# ---- Vowels ----
for ident, how in [
    ('U+0069', 'the module\'s i'), ('U+0079', 'the module\'s front rounded vowel, or i with F2 and F3 lowered'),
    ('U+0268', 'a central vowel placed by its formants'), ('U+0289', 'a central rounded vowel placed by its formants'),
    ('U+026F', 'u without rounding (F2 raised)'), ('U+0075', 'the module\'s u'),
    ('U+026A', 'the module\'s lax i, or i moved'), ('U+028F', 'the module\'s lax front rounded vowel, or placed'),
    ('U+028A', 'the module\'s lax u, or u moved'), ('U+0065', 'the module\'s e'),
    ('U+00F8', 'the module\'s front rounded mid vowel, or e rounded'), ('U+0258', 'a central vowel placed by its formants'),
    ('U+0275', 'a central rounded vowel placed by its formants'), ('U+0264', 'o without rounding (F2 raised)'),
    ('U+006F', 'the module\'s o'), ('U+0259', 'the module\'s schwa'),
    ('U+025B', 'the module\'s open e'), ('U+0153', 'the module\'s open front rounded vowel, or placed'),
    ('U+025C', 'a central vowel placed by its formants'), ('U+025E', 'a central rounded vowel placed by its formants'),
    ('U+028C', 'the module\'s vowel of "cut", or placed'), ('U+0254', 'the module\'s open o'),
    ('U+00E6', 'the module\'s vowel of "cat", or open e lowered'), ('U+0250', 'a low central vowel placed by its formants'),
    ('U+0061', 'the module\'s a'), ('U+0276', 'a rounded (F2 and F3 lowered)'),
    ('U+0251', 'the module\'s back a, or a with F2 lowered'), ('U+0252', 'back a rounded, or open o lowered'),
]:
    row(ident, A, L, 'X1 X2 X9', '', how, 'T-vowel')

# ---- Diacritics ----
row('U+0325', C, K, 'X4 X7', '', 'base + voiceless: voicing off; a sonorant or vowel becomes breath through the same shape', 'T-shift')
row('U+030A', C, K, 'X4 X7', '', 'base + voiceless: voicing off; a sonorant or vowel becomes breath through the same shape', 'T-shift')
row('U+032C', C, K, 'X4', '', 'base + voiced: voicing through the closure or the friction', 'T-shift')
row('U+02B0', C, K, 'X4', '', 'base + aspirated: a longer voice onset time filled with breath', 'T-shift')
row('U+0339', C, K, 'X2', '', 'base + more rounded: F2 and F3 lowered one step', 'T-shift')
row('U+031C', C, K, 'X2', '', 'base + less rounded: F2 and F3 raised one step', 'T-shift')
row('U+031F', C, K, 'X2 X3', '', 'base + advanced: a vowel\'s F2 raised; a consonant moved part of the way to the next place forward', 'T-shift')
row('U+0320', C, K, 'X2 X3', '', 'base + retracted: the reverse', 'T-shift')
row('U+0308', C, K, 'X2', '', 'base + centralized: F2 moved part of the way to the central vowel of the same height', 'T-shift')
row('U+033D', C, K, 'X2', '', 'base + mid-centralized: F1 and F2 moved part of the way to schwa', 'T-shift')
row('U+0329', N, K, 'X9 X13', 'C7', 'base + syllabic: the consonant carries the syllable, its stress and its tone, with no vowel put in', 'T-syllable')
row('U+032F', N, K, 'X9 X13', 'C7', 'base + non-syllabic: the vowel is short, carries no syllable and glides into its neighbour', 'T-syllable')
row('U+02DE', C, K, 'X2', 'C8?', 'base + rhotic: F3 lowered towards F2', 'T-shift')
row('U+0324', N, K, 'X7', 'C6', 'base + breathy: a longer open phase, more tilt and breath noise through the whole sound', 'T-phonation')
row('U+0330', C, K, 'X7', 'C6?', 'base + creaky: a shorter open phase and alternating periods', 'T-phonation')
row('U+033C', C, K, 'X2 X3', '', 'base + linguolabial: locus and noise between the bilabial and the alveolar', 'T-shift')
row('U+02B7', C, K, 'X2', 'C8?', 'base + labialized: F2 and F3 lowered at the release, a brief w-like glide', 'T-shift')
row('U+02B2', C, K, 'X2', 'C8?', 'base + palatalized: F2 raised at the release, a brief j-like glide', 'T-shift')
row('U+02E0', C, K, 'X2', 'C8?', 'base + velarized: F2 lowered', 'T-shift')
row('U+02E4', C, K, 'X2', 'C8?', 'base + pharyngealized: F1 raised and F2 lowered, reaching into the vowels beside it', 'T-shift')
row('U+0334', C, K, 'X2', 'C8?', 'base + velarized or pharyngealized (velarized unless a pack says otherwise)', 'T-shift')
row('U+031D', C, K, 'X2 X3', '', 'base + raised: a vowel\'s F1 lowered; an approximant gains friction', 'T-shift')
row('U+031E', C, K, 'X2 X3', '', 'base + lowered: a vowel\'s F1 raised; a fricative loses its friction', 'T-shift')
row('U+0318', C, K, 'X2', 'C6?', 'base + advanced tongue root: F1 lowered', 'T-shift')
row('U+0319', C, K, 'X2', 'C6?', 'base + retracted tongue root: F1 raised', 'T-shift')
row('U+032A', C, K, 'X2 X3', '', 'base + dental: locus and noise of the dental place', 'T-shift')
row('U+033A', C, K, 'X3', '', 'base + apical: a small shift of the noise or burst spectrum (marked approximate)', 'T-shift')
row('U+033B', C, K, 'X3', '', 'base + laminal: a small shift of the noise or burst spectrum (marked approximate)', 'T-shift')
row('U+0303', C, K, 'X8', 'C9?', 'base + nasalized: the nose opened', 'T-nasality')
row('U+207F', C, K, 'X4 X9 X13', 'C10?', 'base + nasal release: the stop is not released by a burst but into a brief nasal of its own place', 'T-release')
row('U+02E1', C, K, 'X4 X9 X13', 'C10?', 'base + lateral release: the stop is released into l', 'T-release')
row('U+031A', C, K, 'X4', '', 'base + no audible release: the burst left out', 'T-release')

# ---- Suprasegmentals ----
row('U+02C8', A, M, 'X10', '', 'main stress of the syllable that follows', 'T-stress')
row('U+02CC', A, M, 'X10', '', 'secondary stress of the syllable that follows', 'T-stress')
row('U+02D0', C, K, 'X9', '', 'base + long: a vowel\'s length, a consonant\'s hold', 'T-length')
row('U+02D1', C, K, 'X9', '', 'base + half-long', 'T-length')
row('U+0306', C, K, 'X9', '', 'base + extra-short', 'T-length')
row('U+007C', A, M, 'X12', '', 'the end of a minor group: a continuation ending with little or no pause', 'T-boundary')
row('U+2016', A, M, 'X12', '', 'the end of a major group: a final ending and a pause', 'T-boundary')
row('U+002E', A, M, 'X13', '', 'a syllable break', 'T-syllable')
row('U+203F', A, M, 'X13', '', 'two words said as one piece, with no break', 'T-boundary')

# ---- Tones and word accents ----
for ident, how in [('U+030B', 'a level tone at 5'), ('U+02E5', 'a level tone at 5'),
                   ('U+0301', 'a level tone at 4'), ('U+02E6', 'a level tone at 4'),
                   ('U+0304', 'a level tone at 3'), ('U+02E7', 'a level tone at 3'),
                   ('U+0300', 'a level tone at 2'), ('U+02E8', 'a level tone at 2'),
                   ('U+030F', 'a level tone at 1'), ('U+02E9', 'a level tone at 1')]:
    row(ident, A, M, 'X11', '', how, 'T-tone')
for ident, how in [('U+030C', 'levels 1 then 5'), ('U+02E9+U+02E5', 'levels 1 then 5'),
                   ('U+0302', 'levels 5 then 1'), ('U+02E5+U+02E9', 'levels 5 then 1'),
                   ('U+1DC4', 'levels 3 then 5'), ('U+02E7+U+02E5', 'levels 3 then 5'),
                   ('U+1DC5', 'levels 1 then 3'), ('U+02E9+U+02E7', 'levels 1 then 3'),
                   ('U+1DC8', 'levels 3, 4, then 2'), ('U+02E7+U+02E6+U+02E8', 'levels 3, 4, then 2')]:
    row(ident, C, K, 'X11', '', 'a contour made of level tones: ' + how, 'T-tone')
row('U+A71C', N, R, 'X11', 'C5', 'a step down of the register: every later tone of the phrase is lower', 'T-register')
row('U+A71B', N, R, 'X11', 'C5', 'a step up of the register', 'T-register')
row('U+2197', N, R, 'X11 X12', 'C5', 'the pitch of the whole group rises', 'T-slope')
row('U+2198', N, R, 'X11 X12', 'C5', 'the pitch of the whole group falls', 'T-slope')


def main():
    with open(CHECKLIST, encoding='utf-8') as f:
        check = json.load(f)
    symbols = check['symbols']
    ids = [s['id'] for s in symbols]
    problems = []
    for i in ids:
        if i not in D:
            problems.append('no decision for checklist entry ' + i)
    for i in D:
        if i not in ids:
            problems.append('decision for something not in the checklist: ' + i)
    by_id = {x['id']: x for x in symbols}
    for i in list(D):
        if i not in by_id:
            continue
        decision, state, existing, build, how, tests = D[i]
        letter = by_id[i]['kind'] == 'letter'
        if letter and decision != C:
            if state != L:
                problems.append('%s: a letter\'s end state is given by the rule, not by hand' % i)
            state = M if by_id[i]['engine_today']['status'] == 'already' else R
        elif letter and state != K:
            problems.append('%s: a letter decided as composition ends composed' % i)
        elif state == L:
            problems.append('%s: only a letter may ask for the rule' % i)
        D[i] = (decision, state, existing, build, how, tests)
    served = collections.Counter()
    conditional = collections.Counter()
    used = collections.Counter()
    for i, (decision, state, existing, build, how, tests) in D.items():
        for x in existing:
            if x not in EXISTING:
                problems.append('%s: unknown existing capability %s' % (i, x))
            used[x] += 1
        required = [b for b in build if not b.endswith('?')]
        for b in build:
            name = b.rstrip('?')
            if name not in TO_BUILD or name in UNIVERSAL:
                problems.append('%s: unknown capability %s' % (i, b))
            (conditional if b.endswith('?') else served)[name] += 1
        for t in tests:
            if t not in TESTS:
                problems.append('%s: unknown test %s' % (i, t))
        if not existing and not required:
            problems.append('%s: an orphan, it uses nothing' % i)
        if not tests:
            problems.append('%s: no test' % i)
        if (decision == N) != bool(required):
            problems.append('%s: decision "%s" contradicts its needs %s' % (i, decision, build))
        if state not in (M, K, R):
            problems.append('%s: state %s' % (i, state))
    for name in TO_BUILD:
        if name not in UNIVERSAL and not served[name] and not conditional[name]:
            problems.append('capability %s serves no symbol' % name)
    for x in EXISTING:
        if not used[x]:
            problems.append('existing capability %s is used by no symbol' % x)
    for t in TESTS:
        if not any(t in d[5] for d in D.values()):
            problems.append('test %s proves no symbol' % t)
    for s in symbols:
        e = s.get('equivalent_to')
        if e and e in D and s['id'] in D and D[e][:4] != D[s['id']][:4]:
            problems.append('%s and %s are the same thing on the chart but are decided differently' % (s['id'], e))
    if problems:
        print('\n'.join(problems))
        raise SystemExit('%d problems' % len(problems))

    rows = []
    for s in symbols:
        decision, state, existing, build, how, tests = D[s['id']]
        rows.append({'id': s['id'], 'symbol': s['symbol'], 'section': s['section'], 'n': s['n'],
                     'name': s['articulatory'], 'engine_today': s['engine_today']['status'],
                     'decision': decision, 'end_state': state, 'existing': existing,
                     'to_build': build, 'how': how, 'tests': tests})
    by_decision = collections.Counter(r['decision'] for r in rows)
    by_state = collections.Counter(r['end_state'] for r in rows)
    by_section = collections.OrderedDict()
    for r in rows:
        by_section.setdefault(r['section'], collections.Counter())[r['decision']] += 1
    out = {'what': 'Symbol-to-capability traceability (DESIGN.md section 4). Written by '
                   'build_traceability.py; do not edit by hand. Plans, not results.',
           'existing': EXISTING, 'to_build': TO_BUILD, 'universal': UNIVERSAL, 'tests': TESTS,
           'counts': {'entries': len(rows), 'by_decision': by_decision, 'by_end_state': by_state,
                      'by_section': by_section, 'needed_by': served, 'needed_only_if': conditional},
           'rows': rows}
    with open(os.path.join(HERE, 'traceability.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')

    titles = collections.OrderedDict((s['section'], s['section_title']) for s in symbols)
    md = ['# Symbol-to-capability traceability', '',
          'Written by `design/build_traceability.py` from `inventory/IPA_CHECKLIST.json`; do not edit by hand. '
          'It belongs to `DESIGN.md`, section 4.', '',
          '**These are plans, not results.** Nothing here has been rendered or measured; every entry is still '
          '`MISSING` in the checklist until Phase 4 proves it with the real engine (playbook R19f).', '',
          '## How to read it', '',
          '- **Decision**: `as-is` = what the engine has today can say it, and only data is needed; '
          '`composition` = a base sound plus a general rule, and only data and the composing machinery are needed; '
          '`new mechanism` = it cannot be said as specified until a capability the engine lacks is built.',
          '- **Uses**: what the engine already has (X) and what must be built (C). `C6?` with a question mark means '
          '"only if the measurement fails without it". C1 to C4 are needed by every symbol and are not repeated.',
          '- **Ends as**: `mapped` = the engine has it already: for a letter, one of the seven IBM modules the '
          'checklist read has the sound as a phone of its own (the checklist\'s "already"; Canadian French, '
          'Japanese and Polish were not consulted); for a mark, a control the engine has today does it. '
          '`composed` = a base plus a general rule. `created` = none of those modules has it: the sound (or, for four marks, '
          'the control) is designed here under the Unmappable Sound Protocol and registered in '
          '`CREATED_SOUNDS.md`, whether it needs a new mechanism or only the engine\'s present keys. For letters '
          'this is applied by rule from the checklist, not judged row by row.',
          '- **Today**: the checklist\'s reading of the shipped product (already / partly / absent / unknown).', '',
          '## Counts', '',
          '| Section | Entries | as-is | composition | new mechanism |', '|---|---|---|---|---|']
    for sec, c in by_section.items():
        md.append('| %s | %d | %d | %d | %d |' % (titles[sec], sum(c.values()), c[A], c[C], c[N]))
    md.append('| **All** | **%d** | **%d** | **%d** | **%d** |'
              % (len(rows), by_decision[A], by_decision[C], by_decision[N]))
    md += ['', 'Meant to end as: mapped %d, composed %d, created %d.' % (by_state[M], by_state[K], by_state[R]), '',
           '## Capabilities', '', '| Id | Already there | Symbols using it |', '|---|---|---|']
    for x, text in EXISTING.items():
        md.append('| %s | %s | %d |' % (x, text, used[x]))
    md += ['', '| Id | To build | Symbols that need it | Symbols that need it only if a measurement fails |',
           '|---|---|---|---|']
    for name, text in TO_BUILD.items():
        if name in UNIVERSAL:
            md.append('| %s | %s | all %d | |' % (name, text, len(rows)))
        else:
            md.append('| %s | %s | %d | %d |' % (name, text, served[name], conditional[name]))
    md += ['', '## Tests', '', '| Id | What is measured |', '|---|---|']
    for t, text in TESTS.items():
        md.append('| %s | %s |' % (t, text))
    for sec, title in titles.items():
        md += ['', '## ' + title, '',
               '| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |',
               '|---|---|---|---|---|---|---|---|---|']
        for r in rows:
            if r['section'] != sec:
                continue
            sym = r['symbol']
            if r['id'] in ('U+007C',):
                sym = '\\|'
            if any(0x0300 <= ord(ch) <= 0x036F or 0x1DC0 <= ord(ch) <= 0x1DFF for ch in sym):
                sym = '◌' + sym
            md.append('| %d | %s | `%s` | %s | %s | %s | %s | %s | %s |'
                      % (r['n'], sym, r['id'], r['engine_today'], r['decision'],
                         ' '.join(r['existing'] + r['to_build']), r['end_state'], r['how'], ' '.join(r['tests'])))
    with open(os.path.join(HERE, 'TRACEABILITY.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(md) + '\n')

    print('entries %d = %s' % (len(rows), ' + '.join('%d %s' % (sum(c.values()), s) for s, c in by_section.items())))
    print('decision:', dict(by_decision))
    print('meant to end as:', dict(by_state))
    print('needed by (to build):', {k: served[k] for k in TO_BUILD if k not in UNIVERSAL})
    print('needed only if a measurement fails:', {k: conditional[k] for k in TO_BUILD if k not in UNIVERSAL})
    print('orphans: 0; capabilities serving no symbol: 0; equivalent pairs decided alike: yes')


if __name__ == '__main__':
    sys.exit(main())
