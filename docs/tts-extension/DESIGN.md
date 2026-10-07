# Design (Phase 2)

Written 2026-10-05 on branch `tts-ext/phase-2`. **No implementation: this file decides, it builds nothing.** It rests on `ARCHITECTURE_MAP.md`, `inventory/IPA_CHECKLIST.json`, the Phase 1 results (`LANGUAGE_STATUS.md`, `harness/results/`) and a fresh reading of the code in this phase. The per-symbol table that belongs to section 4 is `design/TRACEABILITY.md`.

**Status: APPROVED by the human on 2026-10-05** (section 15), with the five answers of section 14.

## Summary for the human

In plain words, this is what is proposed.

1. **Extend the engine; do not rewrite it.** The part that turns numbers into sound stays exactly as it is, so every language that speaks today keeps speaking the same way, sample for sample. New abilities are added beside it and are switched off unless a language asks for them.
2. **One table of all the sounds.** Every symbol of the IPA chart gets one entry that says what the sound *is*, in ordinary physical units (hertz, milliseconds, decibels), each number tagged with where it came from. Today that knowledge is scattered through Python code and 145 generated files, and every sound is defined seven times over, once for each borrowed IBM module.
3. **A translator from that table to this engine.** A program (the "adapter") turns each entry into the instructions this engine understands. If the engine is ever changed, the table stays.
4. **Sounds are built from parts.** A base sound plus marks (long, nasal, breathy, and so on) is worked out by rule, not listed by hand. An unknown combination is said as the nearest thing the engine can do, **with a loud warning, never silently**.
5. **Nothing may be dropped silently any more.** Today a sound the engine has no answer for is simply left out, and nobody is told. That is the first thing to fix.
6. **Of the 175 chart entries: 109 need only data, 50 need only the composing rules, 16 need something new built** (clicks, trills at a proper rate, one throat stop, breathy voice, syllabic consonants, two tone steps, two phrase melodies). Section 4 lists what must be built, in order, and how each will be tested.
7. **A language becomes a small text file.** A dialect or accent names its parent and lists only what differs. A build step turns that file into what the product loads today, so the installer, the voices and screen readers notice nothing.
8. **Every claim is measured.** The harness from Phase 1 is the judge. Section 10 says what must pass before a sound or a language may be called verified.
9. **Old and new live side by side.** Each existing language keeps its present sound until the new route is shown to be at least as good for it, language by language, with every difference shown to you.
10. **A defect in the released product was found on the way** and is not fixed here, because this phase builds nothing: in the 145 languages read by eSpeak NG, a voiceless sound or a pause that follows certain stops is given voice by mistake. It is described under "A defect found on the way" below. You decided it is fixed first thing in Phase 3 (question 5).

Approved on 2026-10-05; the five questions of section 14 are answered.

What is **not** proposed: no replacement of the synthesiser, no change to the SAPI interface, no change to the ten native languages. New abilities live inside the module files in `languages/`, so shipping them means rebuilding those files; that is done only at stated points, after proof, and each time with your say-so (question 4).

## The facts this design rests on

Found or confirmed in this phase. "Measured" means rendered with the real engine through the Phase 1 harness on 2026-10-05; "code" means read from the source at the line given; "data" means counted from files in the repository. Items marked (helper) were established by a research helper and not re-run by me; the others I checked myself.

| # | Fact | Evidence |
|---|---|---|
| F1 | A phoneme with no line in the map is dropped and nothing is reported. The front-end's error output is thrown away by the host, so there is no channel for a warning today. | code: `frontend/src/frontend_main.c:482-483`; (helper) `src/host/frontend_client.cpp:71-85` |
| F2 | In all 145 packs the length mark `ː` and the palatalisation mark `ʲ` are mapped to nothing. So a long consonant is said short, although the generator can design a long one. | data: 145 of 145 `sounds.map` hold `ː -` and `ʲ -`; code: `frontend_main.c:475-481` |
| F3 | The pack generator silently ignores these marks: advanced, retracted, centralized, mid-centralized, lowered, raised (except on r), tongue root, more and less rounded, linguolabial, apical, laminal, lateral release, nasal release, prenasalisation; and nasal, creaky and voiceless marks on consonants. The epiglottal letters have no entry at all. | (helper) ran `engine/accent/sounds.py` on the German-based template |
| F4 | The per-sound pitch key `f0` works only when a pack does **not** use the layer's own pitch. All 145 packs use it. Their 196 `f0=` keys do nothing. | code: `openevv/src/accent/evv_accent.c:2157-2158`; data: 145 of 145, 196 keys |
| F5 | A stop's release keys (voice onset, breath, burst, ejective gap) are applied to the frames of whatever comes *next*, a pause included. **And two of them, the voice-onset key (`vot`) and the breathy-release key (`brth`), switch voicing on there whether or not the next sound is voiced.** This is a defect in the shipped packs; see "A defect found on the way" below. | code: `evv_accent.c:2110-2120` (voicing is forced from the voice onset time until the module's next voiced frame, and if there is none, to the end of the stretch) and `2142-2155` (voicing for the length of the breathy release); measured, below |
| F6 | The synthesiser has no burst or impulse source: a burst is only noise. Noise through the formant branch is quantised coarsely: by a helper's model of the integer arithmetic (not a measurement) its gain is 0 or 1 count below about 78 dB of combined level and saturates at 121 dB. No frame can ask for a formant above 5000 Hz. With the product's default resampler, speech is synthesised at 11025 Hz and upsampled, so nothing above 5512 Hz is produced at any output rate. (The user setting `Resampler=none` makes the engine synthesise at the output rate instead; upstream documents that mode as wrong in several ways, and the 5000 Hz formant limit holds there too. The harness renders at 11025 Hz.) | code: no match for burst, impulse or plstep in `openevv/src/klatt`; (helper) `klatt_synth.c:215, 264-300`, `klatt_fx.c:94-111`, `eci_env.c:325-352`, `openevv/docs/building.md:76`; code: `src/common/settings.cpp:37` |
| F7 | Eleven of the 62 frame words are always zero and are read by nothing (`db1` and `anv` to `atv`). Six filter slots are spare. So new per-frame controls fit without changing the frame's size. | (helper) measured on enus, hi, dede and enus presets 2 to 8 |
| F8 | An independent rewrite of the synthesiser cannot give today's samples. About 1,490 lines of integer signal code hold fifteen behaviours that no textbook describes, two tables have no known formula, and the engine's own gate compares SHA-256 of the samples. | (helper) `openevv/src/klatt/*`; `openevv/docs/status.md:355` |
| F9 | Head size multiplies F1 to F5 by (125 minus half the head size) per cent, and touches nothing else: 1.25 at head size 0, 0.75 at 100. Bandwidths and the nasal pair do not move. Gender is not a single factor: it applies different factors in different frequency ranges. | measured (enus, the vowel of `` `[.1tat] ``: 750/1232/2440/3600/3900 at 50, 937/1540/3050/4500/4875 at 0, 562/924/1830/2700/2925 at 100; B1 120 and nasal pole 200 throughout); gender (helper) `us_filtr.dr:145-373` |
| F10 | Nine native modules, and also the **32-bit** US English module, were built before the accent layer existed and have never been rebuilt. They read its markup aloud. Only 64-bit US English and the seven templates understand it. | data: the strings `EVV_ACCENT_TRACE` and `{A v=1` are in 15 of the 34 module DLLs |
| F11 | A phone name longer than one letter can be written in an annotation if it is put in single quotes. `DECISIONS.md` D17 said the German and French `E:` and `a~` could not be written. | measured (dede): `` `[.1a'E:'a] `` 9,482 samples, unquoted 62,051 (spelled out as text); `` `[.1t'a~'t] `` 9,339 against 59,609 |
| F12 | A module can be asked for the phonemes of a text (`eciGeneratePhonemes`), and saying those phonemes back gives the same frames as saying the text, except for pitch. | (helper) `openevv/docs/api.md:255-274`, `openevv/docs/authoring.md:930-940`; `engine/check_espeak_packs.py:73` uses it |
| F13 | Speech-recognition error depends strongly on which module speaks: native modules 0.00 to 0.15; English-based templates median 0.06; Italian-based 0.17; Spanish-based 0.20; French-based 0.40; German-based 0.46 (61 languages, none at or under 0.15). Not yet a diagnosis: the German-based template also carries the languages Whisper knows least, and the defect of F5 falls hardest on it (in 61 of its 87 packs the plain p, t and k all carry the key that triggers it). Whether that explains part of the gap has not been tested. | data: `harness/results/status.json` |
| F14 | Adding a tone language, question words, or a melody the keyword matcher misreads needs an edit to Python tables keyed by language tag (12 tone tables, 115 question-word lists, 39 melodies by hand, and more). | (helper) `engine/accent/prosody.py:118-342`, `questions.py:37-137` |
| F15 | One module's rules are 183,000 to 393,000 lines; a phoneme's name is tested in about 500 places in a module, so a phoneme added to a module is invisible to the rules around it. | (helper) counted; `openevv/docs/notes/polish.md:65` |
| F16 | Packs are found by scanning folders each time voices are listed; a pack that reuses an installed eSpeak NG voice with a new map needs no recompiling. A pack's template may not itself have a template. The data folder (`OPENEVV_DATA`, or the machine's program-data folder) is scanned before the shipped `languages/`, and the first pack read with a tag wins, so a pack or a template module staged there replaces the shipped one without touching it. | code: `src/common/languages.cpp:131-175`, `src/common/paths.cpp:97-118` |
| F17 | Current Unicode is 18.0.0. This machine's Python knows Unicode 13 and none of the two newest phonetic blocks. | (helper) unicode.org; `unicodedata.unidata_version` |

Corrections these make to earlier documents are listed in `DECISIONS.md` D30.

### A defect found on the way (in the released product; not fixed in this phase)

Found by the independent reviewer of this design, then measured again by me. Claude cannot hear: what follows is read from the frames and from the level of the signal.

**What happens.** A sound definition may carry a voice onset time (`vot`): how long after a stop's release the voice begins. The accent layer applies it by switching the voice on at that moment and holding it until the module's own voicing takes over, fading out breath and friction as the voice comes up. It never asks whether what follows the stop is voiced at all. So when a stop with that key is followed by a voiceless consonant, the consonant is voiced and loses most of its own noise; and when it is followed by a pause, the pause is voiced to its end (`evv_accent.c:2110-2120`). The breathy-release key (`brth`, on the breathy-voiced stops of languages such as Hindi) does the same for as long as the breathy release lasts, 90 ms in the shipped packs (`evv_accent.c:2142-2155`).

**Measured** (shipped modules, preset 1, the product's default settings; "voiced" counts frames whose voicing amplitude is above zero):

| Pack and text | What follows the stop | Voiced frames there | Same thing where the stop has no such key |
|---|---|---|---|
| Russian "кто." | t, voiceless | 15 of 21 | Romanian "pta.": 0 of 11 |
| Russian "псы." | s, voiceless | 25 of 27; friction left in 4 of 27 | Romanian "taxa.": 0 of 18; friction in 18 of 18 |
| Russian "такса." | s, voiceless | 11 of 17 | |
| Hindi "आप." | the final pause (457 ms) | 92 of 92, at a level about 7 dB under the loudest 20 ms of the word | Hindi "आपा." (ends in a vowel): 12 of 92, the vowel dying away |
| Russian "кот." | the final pause | 90 of 92, about 7 dB under | Romanian "pot.": 0 of 90, 54 dB under |
| English (New York City) "cat." | the final pause | 85 of 96, about 7 dB under | |
| Hindi "दूधसा." (breathy release) | s, voiceless | 17 of 20; friction left in 3 of 20 | Hindi "दूदसा." (plain d): 0 of 20; friction in 20 of 20 |
| Hindi "दूध." (breathy release) | the final pause | 17 of 83 | Hindi "दूद.": 0 of 83 |

The same was seen with the product's own `evv_say` at default settings: the last 300 ms after Hindi "आप.", Russian "кот." and New York English "cat." lie 6 to 7 dB under the loudest part of the word, where Hindi "आपा.", Romanian "pot." and native German "Kot." end in digital silence.

**How far it reaches.** Every one of the 145 packs has sounds with these keys: 930 definitions with `vot` (542 of them in the 87 packs on the German-based template) and 196 with `brth`. How often it is heard depends on which stops carry them. The plain p, t and k all carry `vot` in 61 of the 87 packs on the German-based template, in both packs on the American English one and in one of the nine on the British one; there it happens after every such stop that stands before a voiceless sound or a pause. In the other packs only the aspirated, breathy or otherwise marked stops carry a key, and it happens after those. The ten native languages are not affected: they carry no markup. A user whose settings shorten pauses gets less of the pause part (this machine's own settings do, `PauseMode=2`, which cut the final pause from the test files); the consonant part is not a pause, and nothing in the code makes it depend on that setting (not measured with it).

**Why nobody saw it.** The golden regression says each consonant between two vowels, where the next sound is always voiced. Check A asks whether everything meant to sound did sound; nothing asks whether what was meant to be voiceless or silent stayed so.

**What this design does about it.**

1. A new check, A3 (section 10.1): what is meant voiceless has no voicing, and a pause is silent. The golden regression gains word-final and cluster cases.
2. It is listed as a defect to fix first (section 4.4), not as a capability. The fix is small (in both places voicing is switched on only if a voiced sound follows), but it lives in the accent layer inside the seven template modules, so it reaches users only when those are rebuilt and released.
3. It is **not** covered by the promise that old packs keep their sound (section 11.1). A fix changes what 145 languages say, on purpose, for the better. It is therefore measured before and after, shown, and recorded as an intended change (R8), with the human's say-so.
4. The template comparison (section 13.2) is run with the defect fixed, or its result means nothing.

The human decided on 2026-10-05 that it is fixed as the first act of Phase 3 and released with the next release (question 5, `DECISIONS.md` D34).

## 1. Scope tiers and the coverage metric

| Tier | What | Rule |
|---|---|---|
| **A** | The 175 entries of `inventory/IPA_CHECKLIST.json` (163 distinct things) | Every one must end `mapped`, `composed` or `created`, each with a rendered, measured proof. `unsupported` is not available. The project is not complete while one is `MISSING` or `BLOCKED`. |
| **B** | extIPA (the chart "revised to 2015" published by ICPLA, and the 2021 issue on the IPA's site) and VoQS (the chart ICPLA lists as updated in 2016) | After Tier A is complete. An inventory is researched the same way as the checklist. A Tier B symbol that is an IPA letter plus an IPA mark composes for free. The rest end `composed`, `created`, or, rarely and with the human's acknowledgement, `unsupported-with-justification`. |
| **C** | Symbols a pack or a user defines: other traditions (Americanist, Uralic, Sinological letters), private-use characters, ASCII aliases | A pack may declare a symbol as an alias of a composition or as a created sound with an id of its own. Never required for completion. |

**Primary metric: checklist coverage.** A script, driven by `IPA_CHECKLIST.json`, joins each entry to its master-table entry and its proof file and prints: how many are mapped, composed, created, MISSING, BLOCKED; the status level of each; how many are marked `approximate`. Completion needs 175 of 175 in the first three.

**Secondary metric: the Unicode net.** It catches what the checklist cannot: other ways of writing a chart symbol, and Tier B and C characters. Every assigned code point in these blocks of Unicode 18.0.0 is put in exactly one class:

| Block | Range | Assigned |
|---|---|---|
| IPA Extensions | U+0250 to 02AF | 96 |
| Spacing Modifier Letters (the tone letters U+02E5 to 02E9 are here) | U+02B0 to 02FF | 80 |
| Combining Diacritical Marks | U+0300 to 036F | 112 |
| Combining Diacritical Marks Extended | U+1AB0 to 1AFF | 65 |
| Combining Diacritical Marks Supplement | U+1DC0 to 1DFF | 64 |
| Phonetic Extensions | U+1D00 to 1D7F | 128 |
| Phonetic Extensions Supplement | U+1D80 to 1DBF | 64 |
| Modifier Tone Letters | U+A700 to A71F | 32 |
| Latin Extended-F | U+10780 to 107BF | 62 |
| Latin Extended-G | U+1DF00 to 1DFFF | 188 |
| **Total** | | **891** |

Classes: `A` (a checklist entry), `alias` (another spelling of a Tier A or B thing: a ligature such as ʧ, a precomposed letter, ɚ for ə˞), `B`, `C` (phonetic, another tradition), `not-phonetic`. Two numbers are reported. **Classified** must be 891 of 891: nothing unknown. **Handled** is the share of `A` and `alias` code points that the reader accepts and the engine says; it must be 100 %. `B` and `C` are counted and reported, not required. Chart symbols outside these blocks (the plain Latin letters, æ ç ð ø ħ ŋ œ β θ χ, the click letters, ⱱ, ‖, ‿, ↗, ↘, ⁿ) are in Tier A through the checklist itself.

Because Python 3.10 knows only Unicode 13, the script reads Unicode's own data files (`UnicodeData.txt`, `Blocks.txt`, Unicode License v3, which permits copying with its notice) and not Python's built-in tables. The counts in the table were computed by a research helper from Unicode 18.0.0's `UnicodeData.txt`; the three blocks that changed after Unicode 13 (65, 62 and 188) could not be counted again on this machine, and the script will recount them all.

## 2. The sound model

### 2.1 What a sound is

An utterance is a line of **segments** with **syllable-level marks** over them. A segment is one base letter and a set of modifiers. Each segment has a bundle of features. The features follow the chart's own rows and columns, not a binary system, so that every chart letter has a bundle of its own and every chart mark is one edit to a bundle. That makes two things checkable by machine: no two letters share a bundle, and every mark has a defined effect.

| For | Feature | Values |
|---|---|---|
| Consonant | place | bilabial, labiodental, linguolabial, dental, alveolar, postalveolar, retroflex, alveolo-palatal, palatal, velar, uvular, pharyngeal, epiglottal, glottal (a scale with distances) |
| | second place | none, or a second place for a double articulation (w, ʍ, ɥ, ɧ, k͡p) |
| | stricture | closure, trill, tap, friction, approximation |
| | nasal, lateral, sibilant | yes or no each (a nasal is a closure with the nose open; a lateral fricative is friction with lateral) |
| | airstream | pulmonic, ejective, implosive, click |
| | voicing | voiceless, voiced, breathy, creaky |
| | aspiration | none, after, before |
| | release | plain, none, nasal, lateral |
| | secondary | any of labialized, palatalized, velarized, pharyngealized |
| | tongue part | unspecified, apical, laminal |
| | shift | advanced or retracted (part of a step along the place scale); raised or lowered (towards closer or more open stricture) |
| Vowel | height | seven steps, close to open |
| | backness | five steps, front to back |
| | rounding | unrounded or rounded, with less and more |
| | nasalized, rhotic, tongue root | yes or no; neutral, advanced, retracted |
| | shift | raised, lowered, advanced, retracted, centralized, mid-centralized: each moves height or backness by part of a step |
| | voicing | voiced, voiceless, breathy, creaky |
| Both | length | extra-short, short, half-long, long |
| | syllabic | yes or no |
| Syllable | stress | none, secondary, main |
| | tone | a sequence of levels 1 to 5; a register step up or down before it |
| Between | boundary | syllable, word, linked, minor group, major group; a group may rise or fall as a whole |

The feature names and scales live in one file of the master table (`ipa/features.toml`). PanPhon (MIT; 24 feature columns in its current table) may be used to cross-check our bundles; PHOIBLE's and Hayes's tables are read as references only (ShareAlike or no licence: not copied).

### 2.2 Composition: base plus transforms

A **modifier** is two things at once: an edit to the feature bundle, and a transform on the engine-neutral specification of section 3. A transform is defined per class of base (vowel, stop, fricative, nasal, approximant), and names the classes it applies to. It is made of four operations only:

| Operation | Example |
|---|---|
| scale a value | labialized: F2 and F3 at the release times a factor |
| move a value part of the way to a target | centralized: F2 half-way to the central vowel of the same height |
| add | aspirated: milliseconds added to the voice onset time; decibels of breath |
| set or insert | no audible release: the burst set to none; palatalized: a brief j-like glide inserted |

When several modifiers apply, they are applied in one fixed order whatever order they were typed in: place edits, stricture edits, vowel quality, secondary articulation, airstream, voicing and aspiration, nasality and release, length and syllabicity. Scales multiply, additions add. If two modifiers set the same value, the later in that order wins and the validator lists the pair, so a conflict is visible when the table is built, not when it is spoken. Stress and tone are not composed into a sound: they belong to the syllable.

This is rule R6: the table holds base sounds and rules, and a combination is computed. Every checklist symbol still has its own entry and its own rendered test.

### 2.3 Where composition happens, and what happens to the unknown

Composition happens in two places, from one source.

- **When a pack is built** (the adapter, section 3.3). The pack's whole inventory is composed in engine-neutral units and realised exactly. This is the accurate path.
- **When speaking** (the front-end). eSpeak NG can produce any IPA string for a phoneme, and IPA can be typed in directly, so combinations no pack listed do arrive. The front-end looks a segment up in this order:

  1. **Exact**: the pack's own line for the whole segment.
  2. **Composed**: the base letter's line, merged with one modifier line for each mark. The modifier lines are written by the adapter, one per modifier and class of base, already in the engine's own terms, so merging is only multiplying ratios and adding milliseconds and decibels. The transforms that are not a plain ratio ("part of the way to a target") are written out by the adapter per base letter and are found by step 1.
  3. **Fallback**: if a mark has no line for this class of base, it is left off; if the base letter has no line, the nearest letter by weighted feature distance is used; if the character has no features at all, it is skipped. **Each of these writes a warning** naming the code point, what was said instead, and what was lost.

In the product a warning goes to the log and the nearest sound is spoken. In the harness, in the pack build and in every test, a warning is a failure ("strict mode"). So a silent drop, a silent substitution and a crash are all impossible by construction, which is what R7 and R19 ask.

A test holds the two places together: for a sample of combinations, what the front-end composes must equal what the adapter composes, within rounding.

The feature distance starts from the cost function the pack generator already uses to choose a template (`engine/espeak_phonemes.py:241-259`: stricture mismatch dearest, then place by steps, then voicing; for vowels height, backness, rounding). Its weights are `estimated` and are revisited in Phase 4.

### 2.4 Affricates, double articulations, ligatures, equal spellings

| Case | Rule |
|---|---|
| Affricate (t͡s, d͡ʒ; a tie bar above or below; or a pair a pack declares) | One segment: the stop's closure released straight into the fricative, with no burst of the stop's own and the friction shorter than a plain fricative's. A length mark lengthens the closure. Ejective and aspiration apply to the release. Without a tie bar and without a pack's declaration, two segments. |
| Double articulation (k͡p, ɡ͡b, ŋ͡m) | One closure with two places: the movement into it from the first, the release from the second. The letters w, ʍ, ɥ, ɧ have entries of their own. |
| Any other tied pair | Two vowels: one syllable, the second a glide. Stop and nasal: nasal release. Anything else: said as a tight sequence, with a warning. |
| Ligature letters (ʦ ʣ ʧ ʤ ʨ ʥ and the like) | Aliases of the tied pair. |
| Equal spellings | The reader normalises: Unicode decomposition (NFD), then `c` plus cedilla is put back together as ç, the one chart letter that decomposition would break. `g` is ɡ. Canonically equal inputs must give equal output; a test says so. |
| Loose typing (`:` for ː, `'` for ˈ, `!` for ǃ) | A small alias table, off in strict mode. |

## 3. The master table

### 3.1 Where it lives

New files of our own, under the MIT licence. Nothing is copied into them from eSpeak NG (GPL), from the IPA chart or from other ShareAlike sources: facts are cited, not pasted.

| Path | What |
|---|---|
| `ipa/features.toml` | feature names, scales, distance weights |
| `ipa/table/*.toml` | the entries, one file per chart section, keyed by stable id |
| `ipa/aliases.toml` | equal spellings and loose typing |
| `ipa/sources.toml` | every source an entry may cite: id, citation, URL, licence, opened or not, date. `REFERENCES.md` is written from it. |
| `ipa/realized/<template>.map` | generated: each entry as this engine's definitions for one template module. Committed, so a change shows in a diff. |
| `ipa/proofs/<id>.json` | generated: the harness measurements that prove an entry |
| `engine/ipa/` | the validator, the adapter, the coverage script (Python, MIT) |

### 3.2 An entry

Angle brackets stand for values Phase 4 will fill; this shows the shape, not data.

```toml
[sound."U+0288"]                      # the stable id is the code points (DECISIONS D4)
ipa = "ʈ"
codepoints = ["U+0288"]
name = "voiceless retroflex plosive"
tier = "A"
kind = "base"                         # base | modifier | syllable-mark | tone | boundary
features = { class = "consonant", place = "retroflex", stricture = "closure", voicing = "voiceless", airstream = "pulmonic" }
state = "MISSING"                     # MISSING | mapped | composed | created | BLOCKED
level = 1                             # 1 draft .. 5 native-validated (playbook 1.5)
approximate = false                   # true needs a `deviation` sentence

[sound."U+0288".spec]                 # engine-neutral; reference speaker: adult male
closure_ms = { v = <ms>, tag = "literature", ref = "<source id>" }
vot_ms     = { v = <ms>, tag = "literature", ref = "<source id>" }
burst      = { ms = { v = <ms>, tag = "estimated" }, level_db = { v = <dB>, tag = "estimated" } }
burst_bands = [ { hz = { v = <Hz>, tag = "literature", ref = "<id>" }, bw = { v = <Hz>, tag = "estimated" }, db = { v = <dB>, tag = "estimated" } } ]
locus      = { f2 = { v = <Hz>, tag = "literature", ref = "<id>" }, f3 = { v = <Hz>, tag = "literature", ref = "<id>" } }
transition = { into_ms = { v = <ms>, tag = "estimated" }, out_ms = { v = <ms>, tag = "estimated" } }
duration   = { inherent_ms = { v = <ms>, tag = "literature", ref = "<id>" }, min_ms = { v = <ms>, tag = "estimated" } }
f0_onset_st = { v = <semitones>, tag = "literature", ref = "<id>" }

[sound."U+0288".realization.openevv]  # what this engine needs; never mixed into the spec
carrier = "t"                         # the module phone to start from; default: nearest by features
trim.dedx = [ { key = "f3", v = <per cent>, tag = "measured", proof = "ipa/proofs/U+0288.json" } ]

[sound."U+0288".tests]
contexts = ["alone", "a_a", "i_i", "u_u"]
checks = ["T-stop", "T-contrast: F3 at the vowel edge lower than U+0074"]
proof = "ipa/proofs/U+0288.json"
```

**What the specification can hold**, by kind of sound. Every number is a small table `{ v, tag, ref, note }`.

| Group | Fields | Unit |
|---|---|---|
| Resonances | `formants` F1 to F5 and bandwidths B1 to B5 (the steady targets of a vowel or sonorant); `locus` F1 to F3 (where a neighbouring vowel's formants point at an obstruent's edge); `glide` (end targets and when they are reached) | Hz, per cent of the sound |
| Voice source | kind (none, modal, breathy, creaky, whisper); level; open quotient; tilt; breath noise; alternate-period difference | dB against the reference vowel, per cent, dB |
| Noise | friction level; its spectrum as a list of bands (centre, width, level); unfiltered part | dB against the reference vowel, Hz |
| Nasal | pole and zero with bandwidths; how far the nose is open | Hz, per cent |
| Stop | closure length; burst length, level, bands, and whether it is one transient or noise; voice onset time; breath in it; voicing lead; voice level behind the closure | ms, dB, Hz |
| Modulation | rate, depth, number of closures, closed time (trills) | Hz, dB, count, ms |
| Events | an ordered list for sounds that are a sequence (a click: closure, burst, silence, second release) | ms, dB, Hz |
| Time | inherent and minimum duration; transition times in and out and their shape | ms |
| Pitch | the sound's own offset; the push it gives the next vowel's onset | semitones, ms |

**Units.** Hertz are for one reference speaker, an adult man, as in the sources cited (the engine's preset 1 is the nearest voice). Levels are decibels **against the peak level of an open vowel in the same voice**, because that is measurable in any engine; this engine's own frame units never appear in the specification. Pitch is in semitones against the voice's middle, or in Chao's levels 1 to 5 across the voice's range.

**Provenance.** Each value carries one of `measured`, `literature`, `derived`, `estimated`, `created`, `approximate`. `literature` needs a `ref` that exists in `ipa/sources.toml` and was opened. `measured` names its proof. `derived` names its rule. `estimated` is listed automatically in a verification queue. `approximate` needs a sentence saying what deviates. A correlate tagged `recalled-unverified` in the checklist may enter only as `estimated` (D6).

**The validator** refuses a table with an unknown field, a number without a tag, a `literature` value without an opened source, two letters with one feature bundle, a modifier with no class, an entry without tests, or a `proof` that does not exist for an entry whose state is not `MISSING`.

### 3.3 The adapter: from the specification to this engine

The adapter is the "engine adapter" of the playbook. For one entry and one template module it does this:

1. Compose, if the entry is a base plus modifiers (section 2.2).
2. Choose the carrier: the module phone nearest by features, unless the entry names one.
3. Turn every target in hertz into a ratio against what that carrier measures in the module (`engine/accent/chassis/<module>.json`, re-measured with the voice recorded). A ratio is right for every head size (F9), which is why the engine's definitions stay ratios and no head size has to be passed to the engine.
4. Turn times into milliseconds or ratios of the carrier's measured time, and levels into the engine's decibel words through the carrier's measured levels.
5. Add the entry's `trim` for this template: corrections found by measuring.
6. Write a `sound` line (and `mod` lines for modifiers) in the map format the product already reads.

It also reports what it could **not** realise as specified (for example a noise band above 5 kHz, F6): those become `approximate` with the deviation stated, never a silent loss.

This is what `engine/accent/sounds.py` does today, with three differences: the knowledge is data with provenance and not code; composition is general and not a dozen special cases; and the template is an argument, so the same language can be built for any module and the results compared.

### 3.4 One reference template for the proofs

R19 asks that every symbol be rendered by the real engine and measured. With seven template modules that would be seven proofs a symbol. The design: **one reference template** carries the proof of every Tier A symbol (alone and in three vowel contexts, marks on base sounds). For the other six, the same test set runs automatically and its results are recorded per symbol and template; a failure there is shown in the status of the packs that use that template, but does not block the checklist.

The reference template is chosen by measurement at the start of Phase 3 (the "bake-off", section 13.2), not here. If the result is unclear, it is the German-based one: about 50 phones (49 measured in its chassis file), the most steady vowels to start from of any template (16), and the one 87 packs already use.

### 3.5 Tier B in the master table (added in Phase 4, `DECISIONS.md` D68)

Tier B was left by the approval as "a decision of its own" (section 15). Decided in Phase 4 under the human's standing answer (D60), and recorded here so that a later reader finds it in the design:

- **Where and under what id.** `ipa/table/tierb.toml`, one entry per record of `inventory/tierb/TIERB_CHECKLIST.json`, under that record's id (`B:` and its code points; `#pre`, `#post`, `#voqs` where the inventory adds them, which the validator accepts; the ids written with `/` or as a term, such as `B:term:allegro`, get their rule when those records are mapped). `tier = "B"`, `section = "tierb"`, `chart` = the record's chart and section. A proof file is named by the id with `:` and `/` made `_` (Windows forbids them): `ipa/proofs/B_U+0074+U+033C.json`.
- **A composite** (`kind = "composite"`) is a Tier B spelling made of table entries in their own meaning (`parts`, base first). It has no values of its own: every value is its parts', so it adds nothing to the verification queue. It is said exactly as written, through the front-end, which composes it as it composes any letter and marks (C4); it is judged against its plain base (or the plain spelling its tests name, such as `n̊` for `n̼̊`) in the same three vowel contexts, by the test of the mark that makes the difference (`judged_by`), and every marked case must have been composed, never taken apart. It ends `composed`.
- **A new letter that stands for a Tier A spelling** (`said_as`, the inventory's `composes-via-alias`: ꞯ for q̠) is a composite whose parts spell `said_as`. The adapter writes, into the realised map, the spelling's composition as the letter's own line and a `letter` line with its base's features, so that marks after it compose on it like on any letter. Nothing in the front-end changes for it: a whole spelling's own line is found before composition is tried. The reader (C2) reads it as `said_as`. Where the source's equation is loose, the entry is `approximate` with the deviation stated.
- **A record the composition does not carry** (its Tier A parts do not make its sound in this engine) is a letter of its own (`kind = "base"`, `tier = "B"`), with features, a specification with provenance, its own proof, and `created` as its end, through the USP (section 5), like any created Tier A letter. A composite may then be built on it (`𝼆̬` on `𝼆`).
- **Coverage** (`coverage.py`): a Tier B record is done only when its entry's state is mapped, composed or created and its proof passed; for a composite, only while each of its parts is. How many Tier B records are done does not decide the project's exit, which is the Tier A checklist's (section 1); but a Tier B entry the inventory lacks, or one whose state or proof disagrees with the map as it stands, fails coverage like a Tier A one. The validator also refuses a composite not judged against its first part, by one of its own marks with that mark's own test, or one carrying values of its own. `notation-only` records are listed for the human's acknowledgement as `unsupported-with-justification`.
- **Readings that differ from Tier A** (Q18): strict IPA keeps the Tier A readings; a pack or a text that declares extIPA or VoQS gets theirs, built when those records are mapped.
- **Not decided yet**: the braces of extIPA and VoQS (a label over a stretch of speech: loudness, tempo, a voice quality) and the VoQS settings that need them; the 132 `needs-new` records. Each is designed when it is mapped, and recorded in `DECISIONS.md`.

## 4. Capability gaps

### 4.1 Every symbol, decided

`design/TRACEABILITY.md` decides all 175 entries: the route, the capabilities used, the state each is meant to end in, and the test. Its builder refuses to write the table if any entry is undecided, if any capability serves no symbol, or if two entries the chart prints as one thing are decided differently. Its output on 2026-10-05:

    entries 175 = 59 pulmonic + 11 non_pulmonic + 12 other_symbols + 28 vowels + 32 diacritics + 9 suprasegmentals + 24 tones
    decision: {'as-is': 109, 'new mechanism': 16, 'composition': 50}
    meant to end as: {'mapped': 67, 'created': 55, 'composed': 53}
    needed by (to build): {'C5': 4, 'C6': 1, 'C7': 2, 'C8': 0, 'C9': 0, 'C10': 6, 'C11': 3, 'C12': 0}
    needed only if a measurement fails: {'C5': 6, 'C6': 9, 'C7': 0, 'C8': 6, 'C9': 5, 'C10': 2, 'C11': 2, 'C12': 2}
    orphans: 0; capabilities serving no symbol: 0; equivalent pairs decided alike: yes

Two questions are answered for each entry, and they are independent.

**The route: what has to be built before it can be said.** `as-is`: the engine's present phones and keys can say it, and only data is missing. `composition`: a base plus a general rule; only data and the composing machinery are missing. `new mechanism`: it cannot be said as specified until a capability the engine lacks is built.

**The end state: what it will be once proved** (the three the playbook allows). `mapped`: the engine has it already. For a letter that means one of the seven IBM modules the checklist read has the sound as a phone of its own (the checklist's "already"; it did not consult Canadian French, Japanese or Polish, so a letter only they have is counted as created until they are read, and the 55 can only shrink); for a mark, that a control the engine has today does it (stress digits, tone lines, phrase endings, syllable breaks). `composed`: a base plus a general rule. `created`: no module has it, so the sound, or for four marks the control, is designed here under the Unmappable Sound Protocol and registered (section 5), whether it needs a new mechanism or only the present keys. For letters the builder applies this from the checklist's own data; it is not judged row by row. So ʈ, which today is t with its formants moved, ends `created`: it is a sound IBM's engine never had, designed here, and it will carry provenance, tests and a register number like any other.

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

Meant to end: 67 mapped, 53 composed, 55 created (51 sounds and 4 controls).

"As-is" does not mean it is right today: nothing has been measured against this design yet. The sixteen that need something built: the three trills (ʙ r ʀ), the five clicks, the epiglottal plosive, breathy voice, syllabic and non-syllabic, downstep and upstep, global rise and fall.

### 4.2 What the engine cannot make today

| Class | Today | What is missing |
|---|---|---|
| Clicks | said as p or t with a harder burst | a burst inside the closure and a second, weaker release; a single-transient burst for the two abrupt clicks |
| Ejectives | silence after the burst (after an affricate or fricative, a silence the layer makes) | nothing essential; a glottalised start of the next vowel, if measured wanting |
| Implosives | voicing that swells, a weak burst | nothing essential; pitch at the release (dead today, F4) |
| Trills | amplitude dips counted across the sound, so the rate changes with the sound's length and with the speaking speed | a stated rate |
| Breathy voice | only after a stop's release or inside a tone | breath noise and a longer open phase held through a vowel or consonant |
| Creaky voice | a key exists for whole vowels | irregular or lowered pitch, if the measurement asks for it |
| Whispery voice (Tier B) | not attempted | the same controls as breathy voice, with weaker voicing |
| Voiceless nasals and other voiceless sonorants | breath through the same shape | nothing essential |
| Secondary articulations (labialized, palatalized, velarized, pharyngealized) | four rules inside the generator, for phonemes a pack lists; a mark met on an unlisted phoneme is lost (F2) | a general transform (composition); reaching into the next vowel exists through the `reach` time |
| Nasalised vowels | one knob | nothing essential; direct control of the nasal pair if the measurement asks |
| Tone contours and registers | contours of up to 8 points on 5 levels; no register | steps of register; tones typed directly in IPA |
| Global rise and fall | per language only | a slope for one phrase |
| Tongue root, raised, lowered, advanced, retracted, centralized, rounding marks, linguolabial, apical, laminal | ignored (F3) | composition only |
| Syllabic consonants | a schwa is put in before them | the consonant itself as the syllable |
| Lengths | long vowels only (F2) | the length marks as modifiers of any sound |
| Epiglottals | nothing | two new made sounds, and a stop made by the layer with a burst |
| Anything above 5.5 kHz | nothing, with the default resampler (F6) | not planned: a limit of the synthesiser's formant range and of its tuned sample rate, stated in every entry it touches |

### 4.3 What must be built, in order

Effort: S is one session or less, M two or three, L four to eight. Every item is switched off for existing packs (section 11.1), and each is finished only when its test passes **and** the full golden regression still says every existing case is identical.

**First: the foundations. Every symbol needs them.**

| Id | What | Where | Test | Effort |
|---|---|---|---|---|
| **C1** | **Never silent.** Every dropped phoneme, unknown key, unknown sound or tone id, fallback, overflow and truncation produces a diagnostic. The front-end sends them to the host after its result (the host already tolerates extra bytes); the host writes them to the product log; the accent layer writes them to its trace. A strict mode makes any diagnostic a failure. | front-end, accent layer, host log, harness | Plant each kind of fault: each must be reported. Count what the present packs lose silently over the 16,472 golden cases: that count is a baseline, then a target of zero for migrated packs. | M |
| **C2** | **The IPA reader.** IPA in: normalise, split into segments with their modifiers, tie bars, stress, length, tone letters and tone marks, syllable and group boundaries. Tones typed in IPA become tone lines on the fly (the existing tone machinery says them). Multi-letter phone names are quoted (F11). Available at the command line, to the harness, and as an optional request to the serving front-end. | front-end; harness `ipa.py` | All 175 entries are read to the feature bundle the checklist gives. Canonically equal inputs give equal output. Random input never crashes and never drops silently. | M |
| **C3** | **The master table, its validator and the adapter** (section 3). | `ipa/`, `engine/ipa/` | The validator's own tests. The loop "realise, render, measure" runs for one vowel, one stop, one fricative. | L |
| **C4** | **Composition when speaking** (section 2.3): modifier lines, the lookup order, the fallback with its warning; the fixed limits raised where a full table would hit them (384 sound definitions, 1,024-byte map lines, 48-byte keys). | front-end, map format, accent layer constants | Front-end composition equals adapter composition on a sample. Each fallback warns. | M |

**Second: wide reach.**

| Id | What | Symbols | Test | Effort |
|---|---|---|---|---|
| **C5** | **Pitch.** A register step that lasts to the end of the phrase; a slope for one phrase; a consonant's push on the next vowel's pitch under the layer's own pitch, under a **new** key so that the 196 inert `f0=` keys of the present packs stay inert (F4). | downstep, upstep, global rise, global fall; the five implosives and the ejective mark if measured wanting | The tones after a step are lower or higher by the step asked. The slope of F0 across the phrase differs from the unmarked phrase by the amount asked. F0 at the vowel onset moves by the amount asked. | M |
| **C6** | **Phonation.** Breath noise on voiced frames from nothing; phonation held through a whole sound, or over a window at its start or end (a glottalised vowel onset after an ejective or a glottal stop). New keys are **offsets from the voice's own setting**, so a breathy sound stays breathier than the voice whatever the voice is (section 7). | breathy; creaky, the ejective mark, glottal stop, ɦ, ʕ, the two tongue-root marks, ʜ and ʢ if measured wanting | H1 minus H2 rises for breathy and falls for creaky against the plain sound; harmonics-to-noise falls for breathy. Two new harness measures. | M |
| **C7** | **Syllabicity.** A consonant as the syllable's centre, carrying its stress and tone, without a vowel heard before it; a vowel marked non-syllabic as a short glide. | syllabic, non-syllabic | Number of syllable peaks; length of the marked sound; no vowel formant pattern before a syllabic consonant. | M |

**Third: particular classes.**

| Id | What | Symbols | Test | Effort |
|---|---|---|---|---|
| **C10** | **Timed events on a carrier phone.** A definition may hold a short list of events, each with a time measured from the closure's start or from the release, a length, source levels, a noise spectrum and formant ratios. | the five clicks, the epiglottal plosive; nasal and lateral release if measured wanting | Silent closure; burst length and level against the vowel; burst spectrum ordered by place as the sources say (labial, dental and lateral long and noisy, alveolar and palatal abrupt; alveolar and lateral low, dental and palatal high); no breath after it; the second release present and weaker. | L |
| **C11** | **Aperture modulation at a stated rate.** A trill is given as closures per second, depth and closed time, computed on linear amplitude, on any carrier, voiced or voiceless. The present `tap` stays for single taps. Reason: a count spread over the sound's length makes the rate follow the speaking speed, which a trill's does not. | ʙ, r, ʀ; ʜ and ʢ if measured wanting | The modulation rate of the level envelope lies in the range a source calls canonical for trills (18 to 40 Hz: `literature`, `trills2026` in `REFERENCES.md`, read by a helper; that paper searches within this range and its own medians are 23 to 28 Hz, so the pass mark is confirmed against a second source in Phase 4); depth and number of closures as asked; the rate holds when the speed setting changes. | S |

**Only if a measurement fails without them.** Each has its trigger written down now, so that it is built on evidence and not on expectation.

| Id | What | Trigger | Test once built | Effort |
|---|---|---|---|---|
| **C8** | Transforms on the edge of the neighbouring phone (spreading), beyond what the `reach` time already gives | a secondary articulation or rhoticity fails its formant test in the vowel beside it | the neighbouring vowel's formants at its edge move the stated way and are back at their own values by the time asked; the vowel's midpoint is unchanged | S |
| **C9** | The nasal pole and zero, and the second (tracheal) pole and zero, set directly in hertz | a nasalised vowel fails A1 minus P0, or a nasal's antiformant lies outside its cited range | the frames carry the pole and zero asked; the measured antiformant (or the extra peak) lies where asked, within the nasal measure's tolerance; the same sound without the keys is unchanged | S |
| **C12** | Transient excitation: one impulse into resonators (a damped ringing), for a click that is a single transient and not noise. Either inside the synthesiser behind a switch that is zero for everything existing, using the unused frame words (F7), or as a small generator of our own added to the output. Integer arithmetic, so 32-bit and 64-bit give the same samples. | the abrupt clicks ǃ and ǂ fail burst length or spectrum after the five rounds the USP allows with noise alone | the burst is one decaying oscillation at the frequencies asked, with no noise floor between its peaks; its length and level are as asked; every golden case is identical with the switch at zero; 32-bit and 64-bit samples are equal | M |

**For languages, not for symbols** (sections 6, 8, 9, 11): L1 the pack compiler with `extends`; L2 rewrite rules between reading and speaking (allophony, dialect mergers); L3 the tone, melody and question-word tables moved from Python into pack data; L4 the native modules rebuilt so that they accept the accent layer, and accent packs over IBM's own reading; L5 a reader defined by a pack, for languages eSpeak NG lacks; L6 IPA accepted through SAPI.

### 4.4 Defects to fix first

These are not capabilities. They are things the shipped engine does wrong or does not do although a pack asks. Each fix changes what existing packs say, so each is measured before and after, shown to the human, and recorded as an intended change (R8); none hides behind the version line of section 11.1.

| # | Defect | Fix | Proof |
|---|---|---|---|
| X-1 | Voicing is switched on after a stop with a voice-onset key or a breathy-release key even when a voiceless sound or a pause follows, and the following consonant's noise is faded out (F5 and "A defect found on the way"). | In both places the voice is switched on, and the noise faded, only where the module itself voices what follows; before a pause or a voiceless sound the burst, the breath and the ejective silence still apply, the voicing does not. An aspirated stop before a voiced sound keeps its delayed voice exactly as now. | Check A3 passes on the word-final and cluster cases; the between-vowels golden cases do not move. |
| X-2 | The tone key `av` is read and never applied (eight tone lines in the Mandarin packs carry it). | Apply it, or remove it from the format and the packs. | The level of a syllable with that tone moves by the amount asked, or the packs are rebuilt without the key and nothing moves. |

The inert pitch key `f0` (F4) is not on this list on purpose: making it work would move 196 definitions in 145 packs at once, with values nobody has measured. It stays inert, and a new key does the work for sounds that come from the master table (C5).

## 5. The Unmappable Sound Protocol in this design

- **Which entries are created:** by the rule of section 4.1, the 51 letters that none of the seven IBM modules the checklist read has as a phone of its own, and 4 controls (the two register steps and the two phrase slopes). Most need only the engine's present keys. Twelve also need a new mechanism: ʙ, ʀ, the five clicks, ʡ and the four controls.
- **Where created sounds live:** in the master table, as entries like any other, with `state = "created"`. There is no second table.
- **Stable ids:** a chart symbol's entry is keyed by its code points (D4), which never change. Every created sound also gets a registry number, `CS-0001` onward, in `CREATED_SOUNDS.md`: given once, never reused, never renumbered, kept even if the sound is later superseded. A Tier C sound with no code point of its own is keyed `X-<name>`.
- **The registry line** holds what the playbook asks: symbol, code points, why existing sounds were not enough, the specification (by pointing at the entry), provenance, test and proof files, status, open questions, revision.
- **Rounds:** each of the up to five design rounds is written into the entry's `history` (what changed, what was measured). After five, the entry is marked `approximate` with its deviation and joins the native-review queue; if a stronger model would likely do better, a model-switch pause is raised.
- **Override and promotion.** Values are resolved in this order: a pack's override, then its parents' (section 6.3), then the master table. When better data arrives:

  | What arrives | What changes |
  |---|---|
  | A published value for something `estimated` | the master value, its tag becomes `literature`, revision plus one, the proof is run again |
  | A correction that only this engine needs | the entry's `trim` for that template; the specification is untouched |
  | A native speaker's or expert's correction | the value, with a review record naming who and when |
  | A pack's override that proves right for two or more varieties | promoted to the master default by a recorded decision |

  Every one of these moves the golden regression for the packs that use the sound; the list of what moved is shown and recorded in `DECISIONS.md` before the commit (R8).
- **Demotion:** if a later mechanism lets a created sound be composed instead, its state becomes `composed`; the registry line stays, marked superseded.

## 6. Language packs

### 6.1 The format: TOML

| | TOML | YAML | JSON |
|---|---|---|---|
| Comments | yes | yes | no |
| Types | explicit; strings are always quoted | guessed: with the common Python reader an unquoted `no` becomes *false*, and `no` is the code for Norwegian | explicit |
| Structure | named headers; indentation means nothing | indentation is the structure | brackets; no trailing comma, so adding a line touches its neighbour |
| IPA characters such as `ǀ`, `‖`, `ː`, `#` | safe: always inside quotes | several have a meaning unless quoted | safe |
| Reading it in Python 3.10 | `tomli`, MIT, pure Python, one package (standard from 3.11) | PyYAML, MIT | standard |
| Diffs | one value a line | one value a line | one value a line if written so |

**Decision: TOML 1.0.** It carries comments and provenance on the same line as a value, it cannot misread a language code or a symbol, and its structure is spelled out in headers and not in spacing, which also makes it the easiest of the three to follow line by line with a screen reader. Its weak point is deep nesting, which packs do not need. The product never reads TOML: a build step compiles it to the files the product loads today, so no parser is added to the engine. (The human is asked to confirm: question 1.)

### 6.2 What a pack holds

A pack is a folder `packs/<tag>/` with `pack.toml` and, where needed, a word list, reader rules and tests. This shows the shape:

```toml
[pack]
tag = "en-us-x-south"                # lower case, as the existing tags
name = "English (America, Southern)"
kind = "dialect"                     # language | dialect | accent
extends = "en-us"                    # one parent; holds only what differs
format = 1

[meta]                               # authenticity is documented, not asserted (R14)
variety = "<which variety>"
region = "<where>"
speaker_group = "<who the sources describe>"
sources = ["<source id>", "<source id>"]
licence = "MIT"
status = { level = 1, validated_by = "" }

[engine]                             # how this engine says it; the only engine-specific part
reader = "espeak:en-us"              # espeak:<voice> | module | rules
template = "enux"                    # which module speaks; may be changed and re-measured
realization = "master"               # master | legacy (section 11)

[inventory]                          # references into the master table
add = ["<ipa>"]
remove = ["<ipa>"]
affricates = ["tʃ", "dʒ"]

[[override]]                         # a shifted target, with provenance
sound = "<ipa>"
formants = { f1 = { v = <Hz>, tag = "literature", ref = "<source id>" }, f2 = { v = <Hz>, tag = "literature", ref = "<source id>" } }

[[rule]]                             # allophony and mergers: section 8.3
id = "pin-pen"
replace = "<ipa>"
with = "<ipa>"
when_before = "<class or ipa>"       # the context: also when_after, stress, position in the syllable or word

[stress]                             # section 9; every number carries provenance like any other
kind = "lexical"                     # lexical (from the reader) | fixed | weight | none
position = "<for fixed: first | last | penultimate>"
secondary = true
cues = { pitch_st = <semitones>, length = <ratio>, level_db = <dB> }

[tone]                               # only for a language of tones
bearing = "syllable"                 # syllable | mora
words_apart = false                  # every syllable a word of its own
source = "espeak"                    # where each syllable's tone and its changes come from: espeak | lexicon

[[tone.inventory]]
id = "35"                            # the name the reader gives the tone
points = [[0, <level>], [100, <level>]]   # per cent of the rhyme, Chao level 1 to 5
length = <ratio>
voice = { kind = "modal", from = 0, to = 100 }   # modal | creaky | breathy, over which part
weak = false                         # a light tone

[duration]
long_to_short = <ratio>
stressed = <ratio>
weak = <ratio>
phrase_final = <ratio>

[intonation]
accent_shape = "peak"                # peak | low-then-rise | late-peak | flat
declination_st_per_s = <semitones a second>
endings = { statement = <semitones>, yes_no = <semitones>, wh = <semitones>, continuation = <semitones>, exclamation = <semitones> }
question = "rise"                    # rise | rise-fall | fall | register

[questions]
words = ["<question word>", "<question word>"]
position = "first"                   # first (among the first three words) | any

[g2p]                                # section 8; only what the pack brings itself
rules = "g2p.toml"                   # for reader = "rules"
lexicon = "lexicon.tsv"              # word, IPA: exceptions, and the words of a split
tests = "tests.toml"                 # word, IPA expected
```

Contents, as the playbook lists them: **inventory** (references into the master table, with affricates and allophones named); **overrides** with provenance on every value; **G2P** (which reader, and any rules or word list of the pack's own); **allophony and context rules**; **stress and tone rules**; **duration tendencies**; **intonation**; **metadata** (variety, region, speaker group, sources, licence, status level).

The build writes `languages/<tag>/language.ini`, `sounds.map`, `phonemes.map` and `sample.txt` in today's formats (with additions only), so the loader, the installer, the 1.1 programs that read `phonemes.map`, and a pack dropped into the user's folder all work as now. Packs whose lines name eSpeak NG's phonemes are GPL like today's maps; a pack written in IPA alone is the licence its `meta` says.

### 6.3 Inheritance, precisely

- A pack has at most one parent. Chains are allowed (language, regional variety, dialect, accent); a cycle or a missing parent is an error. Inheritance is resolved when the pack is built: the product only ever sees a complete, flat pack, so the product's rule that a template may not have a template (F16) is not touched.
- Resolution starts at the root and applies each descendant in turn.
- **Tables merge key by key**, at every depth. **A plain value replaces** the parent's.
- **A plain list replaces** the parent's whole list: `inventory.affricates`, `questions.words`, `meta.sources`, a tone's `points`. Four lists grow instead and have their own rules. `inventory` has `add` and `remove`. `override` entries are keyed by `sound` and merge field by field. `rule` and `tone.inventory` entries are keyed by `id`.
- **Overrides.** A child's override for a sound the parent also overrides changes only the fields it names. `drop = ["formants.f2"]` inside it gives those fields back to the master table's value. `remove_overrides = ["<sound>"]` drops the inherited override for that sound whole.
- **Rules are ordered.** A child's rule with a parent's `id` replaces it in place. A new rule goes at the end, or where `place_before = "<id>"` or `place_after = "<id>"` says. `remove_rules = ["<id>"]` deletes. Tones are not ordered; `remove_tones = ["<id>"]` deletes one.
- **To delete** any other inherited key there is `remove = ["<dotted.key>"]`; TOML has no null.
- A merger is a rule (`replace` X `with` Y everywhere); a split needs the words it applies to (section 8.3).
- An override must carry provenance. An override tagged `approximate` needs its deviation.
- The build can print, for any value of the finished pack, which pack in the chain it came from.
- Anything unknown, a key, a symbol not in the master table, a rule naming a missing id, stops the build.

## 7. Voice and language: the boundary

What the code does (F9, and the helper's reading of the rules): all eight voice settings are applied inside the module's rules, before frames exist. Head size is one multiplier on F1 to F5. Gender switches to another set of defaults and applies range-dependent factors. Roughness sets the alternate-period difference. Breathiness sets tilt, breath noise and open quotient (at 100 the voice is a whisper). Pitch baseline and fluctuation set the middle and the range. Speed stretches time. Volume is an output gain.

| Belongs to the **voice** | Belongs to the **language** |
|---|---|
| Size of the vocal tract (head size, gender) | The *pattern* of formants: where each sound sits relative to the others |
| Middle and range of pitch | Tones and melody, as levels within the range and semitones around the middle |
| Habitual voice quality (rough, breathy) | Phonation *contrasts*: this vowel is breathier than that one |
| Speaking rate, loudness | Relative lengths, rhythm, lengthening at phrase ends |

Rules that follow:

1. A pack never sets a voice setting, and a specification never contains one. The eight presets stay the template module's; a pack inherits them.
2. The specification is in hertz for one reference speaker. The engine receives **ratios** against the module's own phone, which the module's voice scaling then carries to any head size exactly. For the female and child presets the module's range-dependent factors make the result approximate; that is stated, and measured on preset 2 in Phase 7 against women's reference values where they exist.
3. New phonation keys are offsets from the voice's own setting (C6). The two existing keys that set absolute values (`oq`, `tl`) stay for compatibility and are not used by the adapter.
4. Pitch in a pack is never in hertz.
5. A cheap check proves the boundary: the same sound on presets 1 to 8 must show the same ratios in the frames.

## 8. G2P: from spelling to phonemes

### 8.1 Three readers

| Reader | Languages | Decision |
|---|---|---|
| IBM's rules inside a module | the ten native languages | Keep. Not editable as data (and not ours to license). |
| eSpeak NG, through the front-end | 145 today; any language eSpeak NG has | Keep. A pack names the voice. Its rules and dictionaries stay in eSpeak NG's own format in the GPL fork; they are never copied into MIT files. |
| A reader defined by the pack (L5) | languages and varieties neither has | New, later, and only for regular spellings at first. |

**Honest limit.** A language that eSpeak NG lacks is not a data-only change today: it needs a voice added to the eSpeak NG fork and the front-end rebuilt. L5 removes that limit for languages with regular spelling. For irregular spelling (English, French, Danish) a word list is needed, and eSpeak NG or IBM remain the practical readers.

### 8.2 The pack's own reader (L5), in outline

Ordered rewrite rules with a left and right context from letters to IPA; character classes; a stress rule (fixed position, by syllable weight, or from the word list); a word list of exceptions in IPA; number words. Number spell-out rules can be taken from Unicode CLDR, whose licence (Unicode License v3) permits it with its notice. It is interpreted by a new source file of ours inside the front-end program. It needs one small change in the wrapper, which today accepts only the reader name `espeak`.

### 8.3 Dialects and accents: rewrite rules after any reader (L2)

A dialect mostly differs from its parent after the reading: mergers, shifted vowels, a different r, flapping, glottalisation, final devoicing. So the design adds one stage **between reading and the map lookup**: ordered rules over the phoneme line, each with a context (neighbouring sounds or classes, stress, position in the syllable and word).

- With eSpeak NG as the reader, the rules run in the front-end on what eSpeak NG returns.
- With an IBM module as the reader (L4), the text is first turned into the module's phonemes (F12), the rules run, and the result is spoken as an annotation with the accent layer's markup. This needs the native modules rebuilt (F10) and is why question 4 is asked.
- A **split** (some words go one way, some the other) cannot be done by rule: the pack lists the words.

### 8.4 Testing and imports

- Every pack has a list of words with the IPA expected. The harness asks the reader what it will say and compares: a G2P error rate, separate from the sound. This is what lets Phase 6 tell a reading fault from a sound fault.
- The ASR round trip stays as the end-to-end check.
- **Licence before import (R4).** Recorded now, from the licence texts opened in this phase:

  | Source | Licence | May enter an MIT file | Otherwise |
  |---|---|---|---|
  | CMUdict | BSD-style, 2 clauses | yes, with its notice | |
  | Unicode CLDR | Unicode License v3 | yes, with its notice | |
  | Epitran's own maps | MIT | yes, with its notice | |
  | ipa-dict | differs by language (some ShareAlike, some non-commercial) | only the permissive sets | non-commercial sets: not at all |
  | WikiPron, Wiktionary | CC BY-SA | no | a separate pack that says so |
  | PHOIBLE | CC BY-SA 3.0 (site); CC BY 4.0 (repository data) | no | cited as fact; never relabelled |
  | eSpeak NG | GPL v3 or later | no | stays in the front-end's data |

  A pack names its sources and its licence, and the build refuses a source whose licence is not recorded.

## 9. Prosody and timing

| Level | Holds | Where |
|---|---|---|
| **Phoneme** | inherent and minimum duration; voice onset time, closure and burst times; transition times; the vowel's own pitch offset; a consonant's push on the next vowel's pitch; own loudness | master table |
| **Language** | long to short ratio; what marks stress (pitch, length, loudness, and how much); stressed and weak vowel lengths; lengthening at the end of a phrase; the tone inventory with each tone's contour, length and voice quality; where tone changes come from; the accent's shape; how fast pitch sinks; how each kind of clause ends; how questions are marked; question words; syllable-per-word and onset rules | pack |
| **Voice** | rate, pitch middle and range | voice (section 7) |

- **Pack data, not Python tables (L3).** The tone tables, the melodies by hand, the question-word lists and the syllable rules that today sit in Python keyed by language tag (F14) move into the packs. A new language then needs no code edit. The move is proved by building every pack and getting today's `accent`, `tone` and `whwords` lines back, byte for byte.
- **Durations are ratios too.** The engine's timing is the template module's own duration rules; the layer stretches them between 0.2 and 4 times. So a duration in the specification is realised as a ratio against what the carrier measures, and what the module does in context stays the module's. This is a stated limit, measured by the length test, and one of the things the template comparison (section 13.2) looks at.
- **Not there, and not solved by this design:** the word accents of Swedish, Norwegian, Serbo-Croatian, Slovenian, Lithuanian and Latvian, and Thai tones, which eSpeak NG does not supply. The mechanism to *say* them exists once a tone can be attached to a word (C2, C5); *knowing* which word has which accent needs a word list (L5).

## 10. Verification

### 10.1 The checks

| Check | Question | Evidence | Pass |
|---|---|---|---|
| **A0** | Was anything substituted or dropped? | the engine's trace; the diagnostics (C1) | no substitution; no diagnostic |
| **A1** | Did every sound the engine meant actually sound? | frames | 100 % |
| **A2** | Does the signal carry what the frames asked for? | signal against frames | at least 90 % of comparisons |
| **A3** (new) | Did what was meant to be voiceless or silent stay so? | frames of each phone meant voiceless and of each pause, with and without the pack's sound definitions | the definitions add no voiced frame there: no more than the module gives by itself |
| **B1** | Is the measured value inside a cited range? | signal against `harness/reference/ranges.json` | at least 80 % of checks, with at least three vowel references for a language |
| **B2** | Is it different from its nearest neighbour, in the right direction? | signal of two sounds | every stated contrast holds |
| **B3** | For a created sound: does the signal match its own specification? | signal against the master entry | within the tolerance of its test |
| **ASR** | Does a recogniser hear the words? | Whisper large-v3, character error rate | at or under 0.15 |
| **Golden** | Did anything else move? | all recorded cases | identical, or every difference explained and recorded |
| **Native** | Does a speaker accept it? | a signed review packet | named person, date |

Checks A use the frames as ground truth, as the playbook asks for a parametric engine; trackers on synthetic speech are the secondary signal, and the harness's known error (a low F1 near a harmonic, D15) stays in its tolerances.

**The bandwidth rule.** With its default resampler the engine produces nothing above 5512 Hz, and it can never place a formant above 5000 Hz (F6). Every spectral reference is therefore evaluated from 0 to 5.5 kHz. A source that measured with a wider band is used only if its figure can be restated for that band; otherwise the value is `approximate` and says so.

### 10.2 What each test measures

| Test | Measures | Harness today |
|---|---|---|
| T-stop | closure, burst spectrum, voice onset, formants at the vowel edge, three vowel contexts | yes |
| T-nasal | murmur F1, antiformant, F2 movement | yes |
| T-fric | noise centre and band edges, length, voicing | yes |
| T-approx | F1 to F3 and their movement | yes |
| T-vowel | F1 to F3 at the midpoint, length | yes |
| T-tone | F0 contour against the points asked | yes (contour); cases come with C2 |
| T-tap, T-trill | dips in the level envelope: count, depth, rate | **to add** |
| T-click | burst length, level against the vowel, spectrum, silence before and after | **to add** (from the stop measures) |
| T-airstream | slope of voicing level through a closure; silence after a burst | **to add** |
| T-phonation | H1 minus H2, harmonics-to-noise, period regularity | **to add** |
| T-nasality | A1 minus P0, F1 bandwidth | **to add** |
| T-shift, T-length, T-contrast | one named measure of two renders compared | **to add** (a comparison of existing measures) |
| T-syllable, T-release, T-sequence, T-stress, T-register, T-slope, T-boundary | counts, presence and absence, and F0 or pause comparisons | **to add** |

Every measure added gets a self-test on a synthetic signal with a known answer first, as in Phase 1.

### 10.3 From checks to status levels

| Level | A symbol reaches it when | A language reaches it when |
|---|---|---|
| 1 draft | it has an entry and renders | it speaks |
| 2 engine-verified | A0 to A3 pass on the reference template, alone and in three vowel contexts (a mark: on base sounds) | A0 to A3 pass over its golden cases |
| 3 reference-verified | level 2, and B1 passes for its main measure | level 2, and B1 passes |
| 4 intelligibility-verified | (not used for single symbols) | level 3, and ASR passes |
| 5 native-validated | a named speaker or expert has signed for it | a named speaker or expert has signed its packet |

- **The contrast test B2 and the specification test B3 never give level 3 by themselves.** R5 reserves "verified" for values inside cited ranges. A symbol with no cited range for its main measure stays at level 2, is marked `no reference`, and is queued for an expert. This will be common: of 477 correlates in the checklist, 129 were not found in an opened source.
- R19 is separate from the levels: a symbol is `mapped`, `composed` or `created` when its proof exists (rendered, measured, shown), whatever its level.

**What blocks promotion:** any diagnostic; an unexplained golden difference; an `estimated` value behind the main measure; a missing or stale proof; for a language, any sound of its inventory that is `MISSING` or `BLOCKED`; for level 4, no recogniser for the language ("ASR unavailable" is recorded, never a score).

**On the ASR pass mark.** Whisper's own error differs enormously by language (the averages reported for large-v3 on natural speech run from about 2 % character error on eight well-resourced languages to about 22 % over 81: Omnilingual ASR paper, Table 5), so 0.15 is fair to some languages and impossible for others. The design keeps 0.15 as the mark for now, as D16 set it, and adds one rule: a language may also pass if its error is no more than 0.05 above the same recogniser's error on *natural* recordings of the same sentences. Common Voice's recordings are CC0 and its sentences are the ones already used. Getting those recordings is a download that needs the human's say-so, so it is proposed for Phase 7 and not assumed. (Question 2 asks how strict to be.)

### 10.4 Regression

- **The golden regression** of Phase 1 stays the gate before every commit that touches synthesis or data: 16,472 cases, frames and sound identical. It grows by: every master-table proof case; the composition-agreement cases; for every new mechanism, a case that the 32-bit and 64-bit modules give the same samples; and **each consonant at the end of a word before a pause and in a cluster with a voiceless consonant**, because today's cases put every consonant between two vowels and so could not see defect X-1.
- **The engine's own gate**, `openevv/test/matrix.sh` (979 cases, six builds), has never been run on this machine. Its scripts say they support MSYS2. Phase 3 tries that first. If it runs, it is required for any change under `openevv/src`. If it does not, that is said plainly, and the golden's native-module cases (sound hashes) are what stands in.
- `openevv/CLAUDE.md` applies to every change under `openevv/`: say which cases moved and why; show that the new code is the code that ran (break it on purpose, see the sound change, put it back).

## 11. Migration: no regression

### 11.1 The switch that keeps old packs identical

Every change of behaviour in the front-end or the accent layer is tied to **a version line in the map**. A map without it, which is all 145 today, is read and spoken exactly as now. Diagnostics (C1) apply to old maps too, because they change what is reported and not what is said. The ten native languages carry no markup at all, and without markup the accent layer does nothing.

**The one exception is a listed defect** (section 4.4). Keeping old packs "exactly as now" would keep X-1 in 145 languages for good. A defect's fix therefore applies to every pack, and is handled as R8 asks for any intended change: measured before and after, the differences shown to the human, approved, recorded in `DECISIONS.md`, the golden recorded again.

### 11.2 The module files

The accent layer is compiled into every module. So none of C5, C6, C10, C11, the accent layer's part of C1 (its diagnostics), the raised limits of C4, C12 if it is built inside the synthesiser, or a defect's fix reaches the product until the seven template modules (fourteen files in `languages/`) are rebuilt and replaced. Three rules keep that safe:

- **A baseline first.** The modules built from today's unchanged source have never been compared with the shipped ones (their files differ; whether their sound does is unknown). Before the first change to the engine, the seven templates are rebuilt from unchanged source into a scratch folder and the whole golden regression is run on them: frames and sound must be identical to the shipped modules'. If they are not, that is reported and settled before anything else is built on them.
- **Development never touches `languages/`.** Rebuilt modules are staged in a scratch data folder, which the product and the harness already read before the shipped packs (F16). Files in `languages/` are replaced only at a stated point (the end of a phase, or a release), after the proofs of that point, and each time with the human's say-so (question 4: granted on 2026-10-05 on exactly these terms).
- **Two goldens, never mixed.** The golden regression committed in `harness/golden/` always describes the modules that are in `languages/`. The staged modules have a golden of their own, recorded beside them, which is the one that moves when a change is approved. At a replacement point the staged modules and their golden replace the shipped ones in the same commit.

### 11.3 Stages

| Stage | What | Proof of no regression |
|---|---|---|
| M0 | Freeze. The present generator, tables and maps stay as they are. The baseline of 11.2: the seven templates rebuilt from unchanged source. | the golden as recorded, identical on the rebuilt templates |
| M0x | The listed defects are fixed (section 4.4), in the staged modules. | what moved is exactly what the defect explains, shown and approved; everything else in the golden is identical; the golden is then recorded again |
| M1 | Pack sources. A `pack.toml` is written by a script for each of the 145 packs from what exists (profile, hand tables, template choice, `language.ini`), with `realization = "legacy"`: the compiler calls the present sound designer unchanged. | building every pack gives files **byte-identical** to those in `languages/` |
| M2 | The master table grows beside it (Phase 4). Nothing shipped uses it. | the golden does not move |
| M3 | One language at a time is switched to `realization = "master"` on a branch. Before and after are shown: which sounds moved and by how much, checks A and B, ASR, silent losses. | it is switched only if no measure is worse, or the human approves the difference; recorded in `DECISIONS.md`; `legacy` stays selectable |
| M4 | The tables in Python become pack data (L3). | byte-identical maps again |
| M5 | The native modules (and the 32-bit US English one), if approved, are rebuilt with the accent layer (L4). | every native golden case identical in frames and sound; `sapi_test` 72 of 72; the engine's own gate if it runs here; only then are files in `languages/` replaced |
| M6 | The old generator is retired. | only after Phase 9 and with the human's agreement (R18e) |

Each stage is a rebuild from sources and is tagged in git, so going back is a checkout. Nothing is deleted before M6 (R1).

Known traps, from the wrapper's tests: three places expect exactly the present counts ("All 155 languages", at least 155 items, ten native packs). A change that adds a language updates them in the same commit.

## 12. Rewrite scope and compatibility

How the parts hang together, new parts included:

```
ipa/table  (what each sound is)  --adapter-->  ipa/realized/<template>.map --+
chassis measurements of each module  --------^                               |
packs/<tag>/pack.toml  --pack compiler---------------------------------------+-->  languages/<tag>/ (what the product loads)

text --> reader (eSpeak NG | IBM's rules | a pack's rules) --> rewrite rules --> map lookup and composition --> markup
markup --> module rules (frames) --> accent layer (reshapes frames) --> synthesiser (samples) --> host --> SAPI
harness  <--  frames, trace, diagnostics, sound
```

What a change forces to be checked again:

| A change to | Forces |
|---|---|
| a module (rebuilt, or another template) | its chassis measurements, then every realised map for that template, then the golden of every pack on it |
| a master-table entry | the realised maps of all templates, the proof of that entry, the golden of every pack that uses the sound |
| the map format or the markup | front-end, pack compiler and accent layer together; old maps must still read the same (section 11.1) |
| a frame word's meaning | accent layer, synthesiser, the taps, the harness |
| the pack compiler | every pack, by the byte-identical proof of section 11.3 |
| the accent layer or anything else under `openevv/src` | the seven template modules rebuilt and staged (section 11.2); the whole golden; the engine's own gate if it runs here |

### 12.1 Component by component

| Component | Decision | Why | Coupled to | Effort | Risk |
|---|---|---|---|---|---|
| **Synthesis core** (`openevv/src/klatt`: resonators, sources, tables) | **Keep.** Extended only if C12 is triggered, behind a switch that is zero for everything existing. | An exact rewrite is not feasible (F8). It is what the ten native languages sound like, and upstream's rule is that it "stays exactly as it is". Its limits (5.5 kHz, coarse noise levels) are accepted and labelled. | every module; the 979-case gate; the 16,472-case golden | none, or M for C12 | low while untouched |
| **Sources and noise** | **Keep.** Breathy and creaky voice use the open quotient, tilt, breath and alternate-period words that exist. A transient only under C12. | The existing words are enough for every Tier A voice quality on paper; measurement decides. | the frame | S to M | low |
| **The frame** (62 words) | **Keep its size and layout.** New per-frame controls, if any, use the eleven dead words (F7). | Its size is assumed in about fifteen places, among them the modules' rule interface, which is exactly full. | rules, layer, taps, harness | none | medium if ever resized: so it is not |
| **Timing model and frame generation** (the modules' rules) | **Keep; extend from outside** through the accent layer (events C10, modulation C11, ratios of time). | Writing rules of our own for a module is hundreds of thousands of lines of someone else's design (F15). Phase 1 shows the IBM rules are very good where they fit (native error 0.00 to 0.15). | modules, chassis measurements | L (C10, C11) | medium |
| **Phoneme tables of the modules** | **Keep. Add no phonemes to modules.** | A new phoneme is invisible to the roughly 500 places that test neighbours by name (F15). New sounds are definitions on a carrier phone instead. | rules, dictionaries | none | low |
| **Accent layer** (`openevv/src/accent`) | **Extend.** This is where most new engine work goes: the defect fixes, C5, C6, C10, C11, limits, diagnostics. | Ours, MIT, built for exactly this, and inert without markup. | front-end markup, map keys, frame words; **compiled into every module, so it ships only in rebuilt module files** (section 11.2) | L | medium: a sound definition is a flat record today; events change its shape |
| **Front-end** (`frontend/`) | **Extend:** C1, C2, C4, C7, L2, later L5. | It is where a phoneme becomes phones, and where the silent losses are. New files of ours inside the GPL program. | eSpeak NG's internal structures; the map format; the host protocol | L | medium |
| **Sound knowledge** (`engine/accent/sounds.py`, `prosody.py`, `questions.py`, profiles, generated maps) | **Replace, beside the old**, with the master table, the adapter and pack sources. Not a synthesis component. The old path stays until M6. | No provenance per value; every sound designed afresh per template; combinations by special case; languages by code edit. | all 145 maps | L (tools) plus Phase 4's content | medium; held by the byte-identical proof of M1 |
| **G2P** | **Keep** IBM's and eSpeak NG's. **Add** rewrite rules (L2) and, later, a pack reader (L5). | Both work; neither is ours to turn into data. | front-end; modules | M, later L | low now |
| **Language loading** (`src/common/languages.cpp`, `language.ini`, installer lists) | **Keep.** Pack sources compile to today's layout. Additions only. | Data-only packs already load (F16). | installer, tests | S | low |
| **Voice scaling** | **Keep** (it is in the modules' rules). Document the boundary (section 7). | Ratios already survive it. | every sound definition | none | low |
| **Public integration layer** (SAPI DLL, host, protocols) | **Keep unchanged.** Optional later addition L6: IPA through SAPI's pronunciation action, which today is spoken as plain text. | Screen readers depend on it. | everything a user has installed | none now; M for L6 | high if touched carelessly: so additions only |
| **Harness** | **Extend:** new measures, proofs, coverage. | It is the judge. | reference store, golden | M | low |

### 12.2 What must not change

The two COM class ids; the registry path of the voice list; every voice's token id (`...\TokenEnums\OpenEVV\<tag>-<n>`), name and attributes; the existing tags, names and locale numbers; eight presets a pack; the settings file, its keys and location; the data folders; the layout of a pack folder and the keys of `language.ini`, with `phonemes.map` kept beside `sounds.map`; the pipe protocol (version 1, every message and item number, every structure's layout and size) and the front-end protocol; the installer's identity, component names and upgrade behaviour; and the sound of every existing language while its map has no version line, with the one exception of a listed defect's fix (sections 4.4 and 11.1). The places are listed with file and line in the wrapper helper's report, summarised in `DECISIONS.md` D31.

Additions that the code is known to tolerate: new keys in `language.ini` (unknown keys are ignored); a block after the front-end's result text (extra bytes are ignored); a new message type or a new item kind **without** trailing bytes; a new flag bit to the front-end; fields added at the end of the host's ready and done messages. Not tolerated: a larger speak request, a new parameter number, a version bump.

### 12.3 Would a clean re-implementation be better? An honest answer in three parts

1. **The synthesiser core: no.** A clean one could not reproduce today's samples (F8), so it would mean either re-recording all 979 of the engine's own baselines and all 16,472 of ours and ending "identical to IBM" for the ten native languages, or running two synthesisers side by side. What it would buy, a burst source, a second noise path, a wider band, either fits into the present one behind a switch (F7) or is not needed for Tier A. The one real gain, cleaner licensing of the tables, is not reached while the modules themselves are IBM's.
2. **The frame generator (the modules' rules): not now; ask again with evidence.** A generator of our own that reads the master table directly would be the natural home for an engine-neutral table: one definition a sound and not seven, no borrowed habits of German or Spanish. But it would discard duration and coarticulation rules that Phase 1 shows work very well where they fit, it is very large, and its quality could only be judged by measurement. The same Phase 1 numbers also carry a warning: languages on the German-based template score far worse than those on the others (F13), and nobody yet knows whether the template, the languages or the recogniser is the cause. So the design does two things. It makes the template an argument of the build, so the question can be *measured* (section 13.2). And it sets a trigger: if, after Phase 6's triage, the main fault of the template languages is timing or coarticulation that data cannot fix, a prototype generator for those languages is proposed to the human under R18, built beside the modules and judged by ASR and the reference checks. Nothing in this design blocks that later, because the master table, the packs and the tests do not depend on how frames are made.
3. **The sound knowledge: yes, replace it,** beside the old, as section 12.1 says. This is the rewrite that pays: it is ours, it is not a synthesis component, and its proof of equality is exact (byte-identical maps).

**No core synthesis component is proposed for replacement**, so no approval of that kind is asked for.

### 12.4 The safest order

The module baseline (11.2) → the defect fixes (4.4) → C1 (see the losses) → C2, C3 (enter and realise sounds) → the template comparison → C4 → the 159 symbols that need no new mechanism, proved on the reference template → C5, C6, C7 → C10, C11 → the triggered ones, if triggered → L1 and L3 with the byte-identical proof → languages switched one at a time → L2 → L4 → L5, L6.

## 13. Risks, and changes to the phase plan

### 13.1 Risk register

| # | Risk | Likely | Hurts | What is done about it |
|---|---|---|---|---|
| 1 | The template modules' own rules cap the quality of 145 languages (F13), and data cannot fix it. | medium | high | Measure first (13.2). Choose templates by measurement. The trigger of 12.3 part 2. |
| 2 | The 5.5 kHz ceiling and coarse noise levels (F6) make sibilants, dental clicks and bursts approximate. | certain | medium | The bandwidth rule (10.1); `approximate` with the deviation stated; no promise beyond it. |
| 3 | The engine's own gate cannot be run here, so a change under `openevv/src` is checked only by our golden. | medium | high | Try the MSYS2 route first in Phase 3. Keep every change behind markup or a zero switch. Say plainly which gate ran. |
| 4 | Reshaping the accent layer's sound record for events breaks present packs. | low | high | The version line (11.1); the golden; additions only. |
| 5 | New signal code gives different samples on 32-bit and 64-bit. | medium | medium | Integer arithmetic; a test of equal hashes for each mechanism. |
| 6 | Few cited ranges exist: most symbols stop at level 2. | certain | medium | Say so (10.3). Contrast tests. A research step per class in Phase 4. The expert queue. |
| 7 | The recogniser is a weak judge for many languages. | certain | medium | The natural-speech rule (10.3). Never promote or demote on ASR alone where it is weak. |
| 8 | Licences. The modules' data is IBM's and unlicensed (flag, unchanged). GPL and ShareAlike material leaking into MIT files. | low | high | The master table is written from cited facts only. The import table (8.4). Packs carry their licence. |
| 9 | The adapter and the front-end compose differently. | medium | medium | One source: the adapter writes the modifier lines the front-end merges. The agreement test. |
| 10 | Building more than is needed. | medium | medium | Three mechanisms are built only on a written trigger. Each of the others names the symbols that need it. |
| 11 | The human cannot check foreign sounds by ear, and neither can Claude. | certain | high | Everything is accepted by measurement; "authentic" only at level 5. |
| 12 | Rebuilt modules are not byte-identical files to the shipped ones, and whether they sound identical has never been tested. Every engine change must ship through rebuilt template modules. The 32-bit English module is older than the 64-bit one (F10). | certain | high | The baseline of section 11.2 before the first change. Development in a staging folder. Files in `languages/` replaced only at stated points, after proof, with the human's approval. |
| 13 | Unicode moves on (the checklist was checked against 18.0.0; Python here knows 13). | low | low | The coverage script reads Unicode's own files. |
| 14 | Hard-coded counts in the installer's tests break when a language is added. | certain | low | Listed (11.3); changed in the same commit. |
| 15 | Another session edits the same working tree. | medium | medium | Check the log and status before each commit; commit by path. |
| 16 | Defect X-1 is in the released product: voiceless sounds and pauses after certain stops are voiced in 145 languages. Until it is fixed, every measurement of those languages, the template comparison and the ASR scores included, is of a faulty baseline. And there may be more of its kind: it was missed because no check looked for it. | certain | high | Fix first (4.4). Check A3 and the new golden contexts (10.1, 10.4). Decided: fixed as the first act of Phase 3 (question 5). |

### 13.2 Recommended changes to phases 3 to 9

Only the phase titles are known to this session. These are recommendations for the human to accept or refuse.

1. **Split Phase 3.** *3A, foundations:* the module baseline of section 11.2; the defect fixes of section 4.4 with check A3 and the new golden contexts; C1 to C4; the new harness measures; the trial of the engine's own gate; and, **after defect X-1 is fixed**, **the template comparison**: a handful of languages that Whisper knows well, each built for all seven templates with the present generator into a scratch folder, and measured (checks A and B, ASR). It costs little, it uses only what exists, and it settles two things this design leaves open on purpose: which template carries the proofs, and how much of F13 is the template's doing. *3B, mechanisms:* C5, C6, C7, C10, C11, each with its test.
2. **Start Phase 4 after 3A, not after 3B.** 159 of the 175 symbols need no new mechanism. Proving them first calibrates the adapter and the tests on easy cases. Each mechanism of 3B is then followed at once by the symbols that need it, which is the loop the USP describes anyway. The three conditional mechanisms can only be triggered inside Phase 4.
3. **Phase 6 (packs, migration, triage)** takes M1, M3, M4, L1, L2 and L3.
4. **Later, each a decision of its own:** L4 (accents over IBM's reading; needs question 4), L5 (the pack's own reader), L6 (IPA through SAPI; question 5), Tier B.
5. **Phase 5 (independent audit)** should include re-running a sample of proofs from nothing, and reading every `approximate` and every `estimated` that is left.

## 14. Questions for the human

Asked on 2026-10-05; the answers are recorded in `DECISIONS.md` D34 and repeated here.

| # | Question | Recommended | Answer |
|---|---|---|---|
| 1 | Which file format for language packs and the sound table? | TOML | **TOML** |
| 2 | How strict should "verified" be? | Standard: the Phase 1 pass marks | **Standard**: 90 % of signal checks, 80 % inside published ranges, speech-recognition error at or under 0.15 |
| 3 | Which English varieties first? | General American as the reference, then Southern American | **Southern American** |
| 4 | May module files in `languages/` be rebuilt and replaced: the seven templates when a proven change needs it, and the native ones so they accept the accent layer? | Yes, each at a stated point, after proof, shown to you first | **Yes, when proven**: work in a scratch folder; files replaced only at a stated point, after the measurements pass, the differences shown first; the seven templates now, the native ones later when accents for them are wanted |
| 5 | The defect found on the way: fix it at once in a release of its own, or as the first act of Phase 3? | First act of Phase 3 | **First thing in Phase 3**; it reaches users with the next release the human chooses to make |

Not asked, and decided by default: IPA through SAPI (L6) is an addition for later, after the chart is covered; it changes nothing that exists, and it is proposed again when its time comes.

What the answers settle in the design:

- Sections 3 and 6 stand as written (TOML). `tomli` is added to the harness's Python environment in Phase 3.
- Section 10's pass marks stand as written. The natural-speech rule for the recogniser stays a proposal for Phase 7 (`OPEN_QUESTIONS.md` Q9).
- The first dialect pack is Southern American English, as a child of a General American pack. No General American pack read by eSpeak NG exists today (US English is a native module), so Phase 6 first decides, by measuring both, whether the parent is read by eSpeak NG (possible at once) or by IBM's own reader (needs L4, which answer 4 allows). The pack's sources, speaker group and status level are documented as R14 asks; it is not called authentic before a native speaker signs for it.
- Sections 11.2 and 11.3 stand as written, with the permission of answer 4 on exactly the terms stated there.
- Defect X-1 (and X-2) are the first work of Phase 3, after the module baseline.

## 15. Approval

**APPROVED.** The human replied "APPROVED" on 2026-10-05, after answering the five questions of section 14 and after being shown the defect, what the two reviews changed, what rests on helpers' reading only, and that approving accepts the changes to the phase plan in section 13.2. No change was asked for. Recorded in `DECISIONS.md` D35 and `PROJECT_STATE.md`.

What the approval covers: the direction (extend, do not rewrite; no core synthesis component replaced); the master table, the adapter and composition; the twelve capabilities in their order and the two defects fixed first; TOML packs with inheritance; the verification rules; the migration stages; what must not change; the split of Phase 3 and the earlier start of Phase 4. What it does not cover: any replacement of files in `languages/` (each is shown first, answer 4), any release, any push, and any later proposal named in the design as a decision of its own (a frame generator of our own, L4, L5, L6, Tier B).
