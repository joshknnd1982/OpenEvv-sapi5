# Symbol-to-capability traceability

Written by `design/build_traceability.py` from `inventory/IPA_CHECKLIST.json`; do not edit by hand. It belongs to `DESIGN.md`, section 4.

**These are plans, not results.** Nothing here has been rendered or measured; every entry is still `MISSING` in the checklist until Phase 4 proves it with the real engine (playbook R19f).

## How to read it

- **Decision**: `as-is` = what the engine has today can say it, and only data is needed; `composition` = a base sound plus a general rule, and only data and the composing machinery are needed; `new mechanism` = it cannot be said as specified until a capability the engine lacks is built.
- **Uses**: what the engine already has (X) and what must be built (C). `C6?` with a question mark means "only if the measurement fails without it". C1 to C4 are needed by every symbol and are not repeated.
- **Ends as**: `mapped` = the engine has it already: for a letter, one of the seven IBM modules the checklist read has the sound as a phone of its own (the checklist's "already"; Canadian French, Japanese and Polish were not consulted); for a mark, a control the engine has today does it. `composed` = a base plus a general rule. `created` = none of those modules has it: the sound (or, for four marks, the control) is designed here under the Unmappable Sound Protocol and registered in `CREATED_SOUNDS.md`, whether it needs a new mechanism or only the engine's present keys. For letters this is applied by rule from the checklist, not judged row by row.
- **Today**: the checklist's reading of the shipped product (already / partly / absent / unknown).

## Counts

| Section | Entries | as-is | composition | new mechanism |
|---|---|---|---|---|
| Consonants (pulmonic) | 59 | 56 | 0 | 3 |
| Consonants (non-pulmonic) | 11 | 0 | 6 | 5 |
| Other symbols | 12 | 9 | 2 | 1 |
| Vowels | 28 | 28 | 0 | 0 |
| Diacritics | 32 | 0 | 29 | 3 |
| Suprasegmentals | 9 | 6 | 3 | 0 |
| Tones and word accents | 24 | 10 | 10 | 4 |
| **All** | **175** | **109** | **50** | **16** |

Meant to end as: mapped 67, composed 53, created 55.

## Capabilities

| Id | Already there | Symbols using it |
|---|---|---|
| X1 | a phone of the speaking module | 99 |
| X2 | formants and bandwidths moved against the module phone (f1-f4, g1-g4, b1-b4, reach) | 89 |
| X3 | noise shaping (fric, a2-a6, ab, af) | 39 |
| X4 | stop timing and release (vot, asp, lead, bar, voi, burst, noburst, pre, ej, impl) | 29 |
| X5 | a sound the accent layer makes beside a vowel (<, >, ms, hush, whisper) | 9 |
| X6 | tap: brief closures cut into a sound (tap, tapms) | 6 |
| X7 | phonation keys (oq, tl, creak, whisper, brth) | 7 |
| X8 | nasal coupling, one knob (nas) | 1 |
| X9 | duration (dur, hold) | 38 |
| X10 | stress: the module's stress digits and the accent line | 2 |
| X11 | tone lines and the layer's own pitch (tone, f0=own) | 24 |
| X12 | phrase endings ({P}, punctuation) | 4 |
| X13 | syllables and pieces in the annotation; an affricate said as stop + fricative (says) | 8 |

| Id | To build | Symbols that need it | Symbols that need it only if a measurement fails |
|---|---|---|---|
| C1 | never silent: a diagnostics channel and a strict mode | all 175 | |
| C2 | the IPA reader and segment model | all 175 | |
| C3 | the master table, its validator and the adapter (composition when a pack is built) | all 175 | |
| C4 | composition when speaking, with nearest-feature fallback and a loud warning | all 175 | |
| C5 | pitch: register steps, a slope per phrase, pitch moved by a consonant under own pitch | 4 | 6 |
| C6 | phonation held through a sound or at its edges; breath noise on voiced frames | 1 | 9 |
| C7 | syllabicity: a consonant as a syllable, a vowel as none | 2 | 0 |
| C8 | edge transforms on the neighbouring phone (spreading) | 0 | 6 |
| C9 | the nasal and the second pole/zero pair, set directly | 0 | 5 |
| C10 | timed events on a carrier phone | 6 | 2 |
| C11 | aperture modulation at a stated rate (trills) | 3 | 2 |
| C12 | transient excitation: an impulse into the resonators | 0 | 2 |

## Tests

| Id | What is measured |
|---|---|
| T-stop | closure length, burst spectrum, voice onset time, F2/F3 at the vowel edge, in a_a i_i u_u |
| T-nasal | murmur F1, antiformant, F2 transitions |
| T-fric | noise centre and band edges (0 to 5.5 kHz), length, voicing |
| T-approx | F1-F3 mid-sound and their movement into the vowel |
| T-tap | one brief amplitude dip |
| T-trill | modulation rate in Hz, depth in dB, number of closures |
| T-vowel | F1-F3 at the midpoint against the reference range; length |
| T-click | silent closure, burst length and level against the vowel, spectrum by place, no breath |
| T-airstream | implosive: voicing that grows through the closure, weak burst; ejective: silence after the burst, no breath |
| T-phonation | H1-H2, harmonics-to-noise, period regularity, against the plain sound |
| T-nasality | A1-P0, F1 bandwidth, against the plain vowel |
| T-shift | the named formant or noise measure moves the stated way against the plain base |
| T-length | length ratio against the plain base |
| T-syllable | number of syllable peaks; length of the marked sound |
| T-release | burst absent, or replaced by a murmur or a lateral, at the release |
| T-stress | pitch, length and level of the marked syllable against an unmarked one |
| T-tone | F0 contour against the points asked, in semitones; order of the levels |
| T-register | the tones after the mark sit lower (or higher) by the step asked |
| T-slope | slope of F0 across the phrase, against the unmarked phrase |
| T-boundary | pause, final lengthening and boundary pitch; or their absence |
| T-sequence | the two parts in order, one closure, length less than the two apart |
| T-contrast | measurably different from its nearest neighbour, in the right direction |

## Consonants (pulmonic)

| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |
|---|---|---|---|---|---|---|---|---|
| 1 | p | `U+0070` | already | as-is | X1 | mapped | the module's p | T-stop |
| 2 | b | `U+0062` | already | as-is | X1 X4 | mapped | the module's b, voiced through the closure where the module's is weak | T-stop |
| 3 | t | `U+0074` | already | as-is | X1 | mapped | the module's t | T-stop |
| 4 | d | `U+0064` | already | as-is | X1 X4 | mapped | the module's d, voiced through the closure where needed | T-stop |
| 5 | ʈ | `U+0288` | partly | as-is | X1 X2 X3 X4 | created | t with a retroflex locus (F3 and F4 lowered) and its burst shaped | T-stop T-contrast |
| 6 | ɖ | `U+0256` | partly | as-is | X1 X2 X3 X4 | created | d with a retroflex locus | T-stop T-contrast |
| 7 | c | `U+0063` | partly | as-is | X1 X2 X3 X4 | created | t with a palatal locus (F2 raised) and a longer, noisier release | T-stop T-contrast |
| 8 | ɟ | `U+025F` | partly | as-is | X1 X2 X3 X4 | created | d with a palatal locus | T-stop T-contrast |
| 9 | k | `U+006B` | already | as-is | X1 | mapped | the module's k | T-stop |
| 10 | ɡ | `U+0261` | already | as-is | X1 X4 | mapped | the module's g, voiced through the closure where needed | T-stop |
| 11 | q | `U+0071` | partly | as-is | X1 X2 X3 X4 | created | k with a uvular locus (F2 lowered, F1 raised) and a lower burst | T-stop T-contrast |
| 12 | ɢ | `U+0262` | partly | as-is | X1 X2 X3 X4 | created | g with a uvular locus | T-stop T-contrast |
| 13 | ʔ | `U+0294` | already | as-is | X5 C6? | mapped | a silence the layer makes, with the vowel edges glottalised | T-stop T-phonation |
| 14 | m | `U+006D` | already | as-is | X1 | mapped | the module's m | T-nasal |
| 15 | ɱ | `U+0271` | partly | as-is | X1 X2 C9? | created | m with a labiodental locus | T-nasal T-contrast |
| 16 | n | `U+006E` | already | as-is | X1 | mapped | the module's n | T-nasal |
| 17 | ɳ | `U+0273` | partly | as-is | X1 X2 C9? | created | n with a retroflex locus (F3 lowered) | T-nasal T-contrast |
| 18 | ɲ | `U+0272` | already | as-is | X1 X2 C9? | mapped | the module's palatal nasal, or n with a palatal locus | T-nasal T-contrast |
| 19 | ŋ | `U+014B` | already | as-is | X1 | mapped | the module's velar nasal | T-nasal |
| 20 | ɴ | `U+0274` | partly | as-is | X1 X2 C9? | created | the velar nasal with a uvular locus | T-nasal T-contrast |
| 21 | ʙ | `U+0299` | partly | new mechanism | X1 X2 C11 | created | a bilabial carrier whose opening is modulated at a trill's rate | T-trill T-contrast |
| 22 | r | `U+0072` | already | new mechanism | X1 X2 X6 C11 | mapped | the module's trill, or a carrier modulated at a stated rate | T-trill |
| 23 | ʀ | `U+0280` | partly | new mechanism | X1 X2 X3 X6 C11 | created | a uvular carrier modulated at a stated rate, with some noise | T-trill T-contrast |
| 24 | ⱱ | `U+2C71` | partly | as-is | X1 X2 X6 | created | a labiodental carrier with one brief closure | T-tap T-contrast |
| 25 | ɾ | `U+027E` | already | as-is | X1 X6 | mapped | the module's tap, or a carrier with one brief closure | T-tap |
| 26 | ɽ | `U+027D` | partly | as-is | X1 X2 X6 | created | a tap with a retroflex locus (F3 lowered) | T-tap T-contrast |
| 27 | ɸ | `U+0278` | partly | as-is | X1 X2 X3 | created | f with a bilabial locus and weaker, flatter noise | T-fric T-contrast |
| 28 | β | `U+03B2` | partly | as-is | X1 X2 X3 | created | v with a bilabial locus and weak friction | T-fric T-contrast |
| 29 | f | `U+0066` | already | as-is | X1 | mapped | the module's f | T-fric |
| 30 | v | `U+0076` | already | as-is | X1 | mapped | the module's v | T-fric |
| 31 | θ | `U+03B8` | already | as-is | X1 X2 X3 | mapped | the module's dental fricative, or f with a dental locus and its noise | T-fric T-contrast |
| 32 | ð | `U+00F0` | already | as-is | X1 X2 X3 | mapped | the module's voiced dental fricative, or v reshaped | T-fric T-contrast |
| 33 | s | `U+0073` | already | as-is | X1 | mapped | the module's s | T-fric |
| 34 | z | `U+007A` | already | as-is | X1 | mapped | the module's z | T-fric |
| 35 | ʃ | `U+0283` | already | as-is | X1 | mapped | the module's sh | T-fric |
| 36 | ʒ | `U+0292` | already | as-is | X1 | mapped | the module's zh | T-fric |
| 37 | ʂ | `U+0282` | partly | as-is | X1 X2 X3 | created | sh with a retroflex shape (lower noise peak, F3 lowered) | T-fric T-contrast |
| 38 | ʐ | `U+0290` | partly | as-is | X1 X2 X3 | created | zh with a retroflex shape | T-fric T-contrast |
| 39 | ç | `U+00E7` | already | as-is | X1 X2 X3 | mapped | the module's palatal fricative, or sh/x reshaped | T-fric T-contrast |
| 40 | ʝ | `U+029D` | already | as-is | X1 X3 X4 | mapped | the palatal fricative voiced | T-fric T-contrast |
| 41 | x | `U+0078` | already | as-is | X1 X3 | mapped | the module's velar fricative | T-fric |
| 42 | ɣ | `U+0263` | partly | as-is | X1 X2 X3 X4 | created | the velar fricative voiced | T-fric T-contrast |
| 43 | χ | `U+03C7` | partly | as-is | X1 X2 X3 | created | the velar fricative with a uvular shape | T-fric T-contrast |
| 44 | ʁ | `U+0281` | already | as-is | X1 X2 X3 | mapped | the module's uvular r, or the velar fricative voiced and lowered | T-fric T-contrast |
| 45 | ħ | `U+0127` | partly | as-is | X5 X2 | created | breath the layer makes beside the vowel, F1 raised and F2 lowered | T-fric T-contrast |
| 46 | ʕ | `U+0295` | partly | as-is | X5 X2 X4 C6? | created | the same with voice | T-approx T-contrast |
| 47 | h | `U+0068` | already | as-is | X5 | mapped | breath the layer makes beside the vowel (or the module's h) | T-fric |
| 48 | ɦ | `U+0266` | partly | as-is | X5 X4 C6? | created | the same with voice | T-phonation T-contrast |
| 49 | ɬ | `U+026C` | partly | as-is | X1 X3 X7 | created | l said without voice, with friction | T-fric T-contrast |
| 50 | ɮ | `U+026E` | partly | as-is | X1 X3 | created | l with friction | T-fric T-contrast |
| 51 | ʋ | `U+028B` | partly | as-is | X1 X3 | created | v without its friction | T-approx T-contrast |
| 52 | ɹ | `U+0279` | already | as-is | X1 X2 | mapped | the module's English r, or an r reshaped (F3 lowered) | T-approx |
| 53 | ɻ | `U+027B` | partly | as-is | X1 X2 | created | the approximant r with F3 lower still | T-approx T-contrast |
| 54 | j | `U+006A` | already | as-is | X1 | mapped | the module's j | T-approx |
| 55 | ɰ | `U+0270` | partly | as-is | X1 X2 | created | w without its rounding (F2 raised) | T-approx T-contrast |
| 56 | l | `U+006C` | already | as-is | X1 | mapped | the module's l | T-approx |
| 57 | ɭ | `U+026D` | partly | as-is | X1 X2 | created | l with a retroflex shape (F3 lowered) | T-approx T-contrast |
| 58 | ʎ | `U+028E` | already | as-is | X1 X2 | mapped | the module's palatal lateral, or l with F2 raised | T-approx T-contrast |
| 59 | ʟ | `U+029F` | partly | as-is | X1 X2 | created | l with a velar shape (F2 lowered) | T-approx T-contrast |

## Consonants (non-pulmonic)

| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |
|---|---|---|---|---|---|---|---|---|
| 1 | ʘ | `U+0298` | partly | new mechanism | X1 X3 C10 | created | closure, a noisy low burst at the lips, a short silence, a weak velar release | T-click T-contrast |
| 2 | ǀ | `U+01C0` | partly | new mechanism | X1 X3 C10 | created | closure, a long noisy high burst, a short silence, a weak velar release | T-click T-contrast |
| 3 | ǃ | `U+01C3` | partly | new mechanism | X1 X3 C10 C12? | created | closure, one abrupt burst with low peaks, a short silence, a weak velar release | T-click T-contrast |
| 4 | ǂ | `U+01C2` | partly | new mechanism | X1 X3 C10 C12? | created | closure, one abrupt burst with high peaks, a short silence, a weak velar release | T-click T-contrast |
| 5 | ǁ | `U+01C1` | partly | new mechanism | X1 X3 C10 | created | closure, a long noisy low burst at the side, a short silence, a weak velar release | T-click T-contrast |
| 6 | ɓ | `U+0253` | partly | composition | X1 X4 C5? | composed | b + implosive: voicing that grows through the closure, a weak burst | T-airstream T-contrast |
| 7 | ɗ | `U+0257` | partly | composition | X1 X4 C5? | composed | d + implosive | T-airstream T-contrast |
| 8 | ʄ | `U+0284` | partly | composition | X1 X2 X4 C5? | composed | the palatal stop + implosive | T-airstream T-contrast |
| 9 | ɠ | `U+0260` | partly | composition | X1 X4 C5? | composed | g + implosive | T-airstream T-contrast |
| 10 | ʛ | `U+029B` | partly | composition | X1 X2 X4 C5? | composed | the uvular stop + implosive | T-airstream T-contrast |
| 11 | ʼ | `U+02BC` | partly | composition | X4 X5 X9 C5? C6? | composed | a voiceless stop, affricate or fricative + ejective: a harder burst, then silence before the voice (after an affricate or fricative the silence is made by the layer) | T-airstream T-contrast |

## Other symbols

| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |
|---|---|---|---|---|---|---|---|---|
| 1 | ʍ | `U+028D` | partly | as-is | X1 X7 | created | w said without voice | T-fric T-contrast |
| 2 | w | `U+0077` | already | as-is | X1 | mapped | the module's w | T-approx |
| 3 | ɥ | `U+0265` | already | as-is | X1 X2 | mapped | the module's rounded palatal glide, or j with its formants lowered | T-approx T-contrast |
| 4 | ʜ | `U+029C` | absent | as-is | X5 X2 X3 C11? C6? | created | strong breath the layer makes beside the vowel, F1 raised further than for the pharyngeal | T-fric T-contrast |
| 5 | ʢ | `U+02A2` | absent | as-is | X5 X2 X4 X7 C11? C6? | created | the same with voice and creak | T-approx T-phonation T-contrast |
| 6 | ʡ | `U+02A1` | absent | new mechanism | X5 X2 C10 | created | a silence the layer makes, then a burst, with F1 high at the vowel edge | T-stop T-contrast |
| 7 | ɕ | `U+0255` | partly | as-is | X1 X2 X3 | created | sh with a palatal shape (F2 raised, noise peak raised) | T-fric T-contrast |
| 8 | ʑ | `U+0291` | partly | as-is | X1 X2 X3 | created | zh with a palatal shape | T-fric T-contrast |
| 9 | ɺ | `U+027A` | partly | as-is | X1 X2 X6 | created | l with one brief closure | T-tap T-contrast |
| 10 | ɧ | `U+0267` | partly | as-is | X1 X2 X3 | created | the velar fricative with a second, sh-like noise peak and rounding (marked approximate) | T-fric T-contrast |
| 11 | ◌͜ | `U+035C` | partly | composition | X13 X4 X9 | composed | two letters as one sound: an affricate (stop released into its fricative) or a double closure | T-sequence |
| 12 | ◌͡ | `U+0361` | partly | composition | X13 X4 X9 | composed | two letters as one sound: an affricate (stop released into its fricative) or a double closure | T-sequence |

## Vowels

| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |
|---|---|---|---|---|---|---|---|---|
| 1 | i | `U+0069` | already | as-is | X1 X2 X9 | mapped | the module's i | T-vowel |
| 2 | y | `U+0079` | already | as-is | X1 X2 X9 | mapped | the module's front rounded vowel, or i with F2 and F3 lowered | T-vowel |
| 3 | ɨ | `U+0268` | partly | as-is | X1 X2 X9 | created | a central vowel placed by its formants | T-vowel |
| 4 | ʉ | `U+0289` | partly | as-is | X1 X2 X9 | created | a central rounded vowel placed by its formants | T-vowel |
| 5 | ɯ | `U+026F` | partly | as-is | X1 X2 X9 | created | u without rounding (F2 raised) | T-vowel |
| 6 | u | `U+0075` | already | as-is | X1 X2 X9 | mapped | the module's u | T-vowel |
| 7 | ɪ | `U+026A` | already | as-is | X1 X2 X9 | mapped | the module's lax i, or i moved | T-vowel |
| 8 | ʏ | `U+028F` | already | as-is | X1 X2 X9 | mapped | the module's lax front rounded vowel, or placed | T-vowel |
| 9 | ʊ | `U+028A` | already | as-is | X1 X2 X9 | mapped | the module's lax u, or u moved | T-vowel |
| 10 | e | `U+0065` | already | as-is | X1 X2 X9 | mapped | the module's e | T-vowel |
| 11 | ø | `U+00F8` | already | as-is | X1 X2 X9 | mapped | the module's front rounded mid vowel, or e rounded | T-vowel |
| 12 | ɘ | `U+0258` | partly | as-is | X1 X2 X9 | created | a central vowel placed by its formants | T-vowel |
| 13 | ɵ | `U+0275` | partly | as-is | X1 X2 X9 | created | a central rounded vowel placed by its formants | T-vowel |
| 14 | ɤ | `U+0264` | partly | as-is | X1 X2 X9 | created | o without rounding (F2 raised) | T-vowel |
| 15 | o | `U+006F` | already | as-is | X1 X2 X9 | mapped | the module's o | T-vowel |
| 16 | ə | `U+0259` | already | as-is | X1 X2 X9 | mapped | the module's schwa | T-vowel |
| 17 | ɛ | `U+025B` | already | as-is | X1 X2 X9 | mapped | the module's open e | T-vowel |
| 18 | œ | `U+0153` | already | as-is | X1 X2 X9 | mapped | the module's open front rounded vowel, or placed | T-vowel |
| 19 | ɜ | `U+025C` | already | as-is | X1 X2 X9 | mapped | a central vowel placed by its formants | T-vowel |
| 20 | ɞ | `U+025E` | partly | as-is | X1 X2 X9 | created | a central rounded vowel placed by its formants | T-vowel |
| 21 | ʌ | `U+028C` | already | as-is | X1 X2 X9 | mapped | the module's vowel of "cut", or placed | T-vowel |
| 22 | ɔ | `U+0254` | already | as-is | X1 X2 X9 | mapped | the module's open o | T-vowel |
| 23 | æ | `U+00E6` | already | as-is | X1 X2 X9 | mapped | the module's vowel of "cat", or open e lowered | T-vowel |
| 24 | ɐ | `U+0250` | partly | as-is | X1 X2 X9 | created | a low central vowel placed by its formants | T-vowel |
| 25 | a | `U+0061` | already | as-is | X1 X2 X9 | mapped | the module's a | T-vowel |
| 26 | ɶ | `U+0276` | partly | as-is | X1 X2 X9 | created | a rounded (F2 and F3 lowered) | T-vowel |
| 27 | ɑ | `U+0251` | already | as-is | X1 X2 X9 | mapped | the module's back a, or a with F2 lowered | T-vowel |
| 28 | ɒ | `U+0252` | already | as-is | X1 X2 X9 | mapped | back a rounded, or open o lowered | T-vowel |

## Diacritics

| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |
|---|---|---|---|---|---|---|---|---|
| 1 | ◌̥ | `U+0325` | partly | composition | X4 X7 | composed | base + voiceless: voicing off; a sonorant or vowel becomes breath through the same shape | T-shift |
| 2 | ◌̊ | `U+030A` | partly | composition | X4 X7 | composed | base + voiceless: voicing off; a sonorant or vowel becomes breath through the same shape | T-shift |
| 3 | ◌̬ | `U+032C` | partly | composition | X4 | composed | base + voiced: voicing through the closure or the friction | T-shift |
| 4 | ʰ | `U+02B0` | partly | composition | X4 | composed | base + aspirated: a longer voice onset time filled with breath | T-shift |
| 5 | ◌̹ | `U+0339` | absent | composition | X2 | composed | base + more rounded: F2 and F3 lowered one step | T-shift |
| 6 | ◌̜ | `U+031C` | absent | composition | X2 | composed | base + less rounded: F2 and F3 raised one step | T-shift |
| 7 | ◌̟ | `U+031F` | absent | composition | X2 X3 | composed | base + advanced: a vowel's F2 raised; a consonant moved part of the way to the next place forward | T-shift |
| 8 | ◌̠ | `U+0320` | absent | composition | X2 X3 | composed | base + retracted: the reverse | T-shift |
| 9 | ◌̈ | `U+0308` | partly | composition | X2 | composed | base + centralized: F2 moved part of the way to the central vowel of the same height | T-shift |
| 10 | ◌̽ | `U+033D` | absent | composition | X2 | composed | base + mid-centralized: F1 and F2 moved part of the way to schwa | T-shift |
| 11 | ◌̩ | `U+0329` | partly | new mechanism | X9 X13 C7 | composed | base + syllabic: the consonant carries the syllable, its stress and its tone, with no vowel put in | T-syllable |
| 12 | ◌̯ | `U+032F` | partly | new mechanism | X9 X13 C7 | composed | base + non-syllabic: the vowel is short, carries no syllable and glides into its neighbour | T-syllable |
| 13 | ˞ | `U+02DE` | partly | composition | X2 C8? | composed | base + rhotic: F3 lowered towards F2 | T-shift |
| 14 | ◌̤ | `U+0324` | partly | new mechanism | X7 C6 | composed | base + breathy: a longer open phase, more tilt and breath noise through the whole sound | T-phonation |
| 15 | ◌̰ | `U+0330` | partly | composition | X7 C6? | composed | base + creaky: a shorter open phase and alternating periods | T-phonation |
| 16 | ◌̼ | `U+033C` | absent | composition | X2 X3 | composed | base + linguolabial: locus and noise between the bilabial and the alveolar | T-shift |
| 17 | ʷ | `U+02B7` | partly | composition | X2 C8? | composed | base + labialized: F2 and F3 lowered at the release, a brief w-like glide | T-shift |
| 18 | ʲ | `U+02B2` | partly | composition | X2 C8? | composed | base + palatalized: F2 raised at the release, a brief j-like glide | T-shift |
| 19 | ˠ | `U+02E0` | absent | composition | X2 C8? | composed | base + velarized: F2 lowered | T-shift |
| 20 | ˤ | `U+02E4` | partly | composition | X2 C8? | composed | base + pharyngealized: F1 raised and F2 lowered, reaching into the vowels beside it | T-shift |
| 21 | ◌̴ | `U+0334` | partly | composition | X2 C8? | composed | base + velarized or pharyngealized (velarized unless a pack says otherwise) | T-shift |
| 22 | ◌̝ | `U+031D` | partly | composition | X2 X3 | composed | base + raised: a vowel's F1 lowered; an approximant gains friction | T-shift |
| 23 | ◌̞ | `U+031E` | absent | composition | X2 X3 | composed | base + lowered: a vowel's F1 raised; a fricative loses its friction | T-shift |
| 24 | ◌̘ | `U+0318` | absent | composition | X2 C6? | composed | base + advanced tongue root: F1 lowered | T-shift |
| 25 | ◌̙ | `U+0319` | absent | composition | X2 C6? | composed | base + retracted tongue root: F1 raised | T-shift |
| 26 | ◌̪ | `U+032A` | partly | composition | X2 X3 | composed | base + dental: locus and noise of the dental place | T-shift |
| 27 | ◌̺ | `U+033A` | partly | composition | X3 | composed | base + apical: a small shift of the noise or burst spectrum (marked approximate) | T-shift |
| 28 | ◌̻ | `U+033B` | partly | composition | X3 | composed | base + laminal: a small shift of the noise or burst spectrum (marked approximate) | T-shift |
| 29 | ◌̃ | `U+0303` | partly | composition | X8 C9? | composed | base + nasalized: the nose opened | T-nasality |
| 30 | ⁿ | `U+207F` | partly | composition | X4 X9 X13 C10? | composed | base + nasal release: the stop is not released by a burst but into a brief nasal of its own place | T-release |
| 31 | ˡ | `U+02E1` | absent | composition | X4 X9 X13 C10? | composed | base + lateral release: the stop is released into l | T-release |
| 32 | ◌̚ | `U+031A` | partly | composition | X4 | composed | base + no audible release: the burst left out | T-release |

## Suprasegmentals

| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |
|---|---|---|---|---|---|---|---|---|
| 1 | ˈ | `U+02C8` | already | as-is | X10 | mapped | main stress of the syllable that follows | T-stress |
| 2 | ˌ | `U+02CC` | already | as-is | X10 | mapped | secondary stress of the syllable that follows | T-stress |
| 3 | ː | `U+02D0` | partly | composition | X9 | composed | base + long: a vowel's length, a consonant's hold | T-length |
| 4 | ˑ | `U+02D1` | absent | composition | X9 | composed | base + half-long | T-length |
| 5 | ◌̆ | `U+0306` | partly | composition | X9 | composed | base + extra-short | T-length |
| 6 | \| | `U+007C` | partly | as-is | X12 | mapped | the end of a minor group: a continuation ending with little or no pause | T-boundary |
| 7 | ‖ | `U+2016` | partly | as-is | X12 | mapped | the end of a major group: a final ending and a pause | T-boundary |
| 8 | . | `U+002E` | already | as-is | X13 | mapped | a syllable break | T-syllable |
| 9 | ‿ | `U+203F` | unknown | as-is | X13 | mapped | two words said as one piece, with no break | T-boundary |

## Tones and word accents

| # | Symbol | Id | Today | Decision | Uses | Ends as | How | Proved by |
|---|---|---|---|---|---|---|---|---|
| 1 | ◌̋ | `U+030B` | partly | as-is | X11 | mapped | a level tone at 5 | T-tone |
| 2 | ˥ | `U+02E5` | partly | as-is | X11 | mapped | a level tone at 5 | T-tone |
| 3 | ◌́ | `U+0301` | partly | as-is | X11 | mapped | a level tone at 4 | T-tone |
| 4 | ˦ | `U+02E6` | partly | as-is | X11 | mapped | a level tone at 4 | T-tone |
| 5 | ◌̄ | `U+0304` | partly | as-is | X11 | mapped | a level tone at 3 | T-tone |
| 6 | ˧ | `U+02E7` | partly | as-is | X11 | mapped | a level tone at 3 | T-tone |
| 7 | ◌̀ | `U+0300` | partly | as-is | X11 | mapped | a level tone at 2 | T-tone |
| 8 | ˨ | `U+02E8` | partly | as-is | X11 | mapped | a level tone at 2 | T-tone |
| 9 | ◌̏ | `U+030F` | partly | as-is | X11 | mapped | a level tone at 1 | T-tone |
| 10 | ˩ | `U+02E9` | partly | as-is | X11 | mapped | a level tone at 1 | T-tone |
| 11 | ◌̌ | `U+030C` | partly | composition | X11 | composed | a contour made of level tones: levels 1 then 5 | T-tone |
| 12 | ˩˥ | `U+02E9+U+02E5` | partly | composition | X11 | composed | a contour made of level tones: levels 1 then 5 | T-tone |
| 13 | ◌̂ | `U+0302` | partly | composition | X11 | composed | a contour made of level tones: levels 5 then 1 | T-tone |
| 14 | ˥˩ | `U+02E5+U+02E9` | partly | composition | X11 | composed | a contour made of level tones: levels 5 then 1 | T-tone |
| 15 | ◌᷄ | `U+1DC4` | partly | composition | X11 | composed | a contour made of level tones: levels 3 then 5 | T-tone |
| 16 | ˧˥ | `U+02E7+U+02E5` | partly | composition | X11 | composed | a contour made of level tones: levels 3 then 5 | T-tone |
| 17 | ◌᷅ | `U+1DC5` | partly | composition | X11 | composed | a contour made of level tones: levels 1 then 3 | T-tone |
| 18 | ˩˧ | `U+02E9+U+02E7` | partly | composition | X11 | composed | a contour made of level tones: levels 1 then 3 | T-tone |
| 19 | ◌᷈ | `U+1DC8` | partly | composition | X11 | composed | a contour made of level tones: levels 3, 4, then 2 | T-tone |
| 20 | ˧˦˨ | `U+02E7+U+02E6+U+02E8` | partly | composition | X11 | composed | a contour made of level tones: levels 3, 4, then 2 | T-tone |
| 21 | ꜜ | `U+A71C` | absent | new mechanism | X11 C5 | created | a step down of the register: every later tone of the phrase is lower | T-register |
| 22 | ꜛ | `U+A71B` | absent | new mechanism | X11 C5 | created | a step up of the register | T-register |
| 23 | ↗ | `U+2197` | partly | new mechanism | X11 X12 C5 | created | the pitch of the whole group rises | T-slope |
| 24 | ↘ | `U+2198` | partly | new mechanism | X11 X12 C5 | created | the pitch of the whole group falls | T-slope |
