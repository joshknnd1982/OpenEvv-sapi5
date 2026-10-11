# Language status

Status level and failure-layer triage for every language, dialect and accent (playbook 1.5). **Skeleton: Phase 1 fills in the baseline for all existing languages.**

Levels: 1 `draft` · 2 `engine-verified` (the harness shows the engine realizes the requested parameters) · 3 `reference-verified` (realized values fall within reference ranges) · 4 `intelligibility-verified` (speech-recognition round trip passes, where a recognizer supports the language) · 5 `native-validated` (a named native speaker or expert signed off the review packet). Only level 5 may be called "authentic".

## Phase 5 (2026-10-10): no language's status changed

The independent audit (`AUDIT_PHASE5.md`) touched the master table (z, ʝ, ɣ, ɞ) and the sweep's checks, not the packs or the shipped modules; every table entry stays at level 2 (engine-verified on the reference template dedx), none is called authentic. The 155 languages below stand as Phase 1 measured them, with the Phase 3 defect fixes and Q28's rule in the staged modules only (D87); Phase 6 moves them to packs and triages them.

## Baseline, 2026-10-05 (end of Phase 1)

Every language was rendered and measured by the harness (`harness/README.md`); nothing was fixed (playbook Phase 1, step 9). The table below is written by `harness/report.py`; do not edit it by hand.

| Level | Languages | What it means here |
|---|---|---|
| 1 draft | 1 (qu) | check A fails: in one case the engine meant a vowel and made it silent |
| 2 engine-verified | 150 | the engine realised what it asked for; too few reference values to go further, or check B fails |
| 3 reference-verified | 0 | (the four that pass check B also pass ASR, so they are at 4) |
| 4 intelligibility-verified | 4 (enus, en-us-nyc, pt, pt-br) | check A, check B and ASR (CER <= 0.15) all pass |
| 5 native-validated | 0 | needs a named native speaker or expert |

Why most languages stop at level 2: check B needs cited reference values for at least three vowels, and the store has vowel values for English, German, Spanish and Portuguese only (`harness/reference/ranges.json`, 956 values from 14 sources). For 137 more languages only the general nasal ranges apply, which is too little to judge; 4 have no reference at all. So 141 languages cannot reach level 3 whatever their ASR score (21 of them pass ASR). Of the 14 with enough references, 10 fail check B, on vowel F1/F2 and nasal antiformants (`reports/index.html`, "values out of range").

ASR: 105 languages scored, 50 unavailable: 46 that Whisper large-v3 does not know, 2 more with no CC0 or CC BY sentence set (en-shaw, fa-latn), and 2 whose text is in a script Whisper does not write for them (cmn-latn-pinyin, yue-latn-jyutping). Serbian is scored after both sides are put in Latin letters. Median CER 0.33. A high CER is not yet a diagnosis: Whisper is weak on some languages, and a synthetic voice is far from its training data; the failure layer column is a first guess for Phase 6.

The failure layers used: `phoneme values` (check A or B fails), `stress-or-tone` (only ASR fails, and the pack has tones), `unknown` (only ASR fails; G2P, duration and coarticulation cannot be told apart yet). The earlier categories of this file (text analysis, phoneme mapping, segment realization, prosody, capability) are the finer split Phase 6 triage will use.

**Found in Phase 2 (2026-10-05), and true of every number below for the 145 languages read by eSpeak NG:** the shipped engine voices a voiceless consonant or a pause that follows a stop with a voice-onset or breathy-release setting (`DESIGN.md`, "A defect found on the way"). The checks of this baseline could not see it: the golden cases put each consonant between two vowels, and check A asks only whether what was meant to sound did. The speech-recognition scores were taken with the defect present; how much of them it explains is not known. The ten native languages are not affected.

## Native-speaker sign-offs

None yet.

<!-- STATUS BEGIN (written by harness/report.py) -->

Measured 2026-10-05 by `harness/report.py`. Preset 1 (adult male), 64-bit, 11025 Hz. Levels: 1 draft: 1, 2 engine-verified: 150, 4 intelligibility-verified: 4. Check A = engine fidelity (A1 frames, A2 sound vs frames), check B = against cited reference ranges, ASR = Whisper large-v3 character error rate. Pass marks: A2 >= 90 %, B >= 80 %, CER <= 0.15. A failure layer is a first-pass label, not a diagnosis.

| Tag | Language | Kind | Level | Check A (A0 substituted / A1 silent / A2) | No phone of its own | Check B | ASR | Failure layer |
|---|---|---|---|---|---|---|---|---|
| ab | Abkhaz | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 2 | too few references (2/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| af | Afrikaans | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.32 WER 0.67 | unknown |
| am | Amharic | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 1.43 WER 1.42 | unknown |
| an | Aragonese | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ar | Arabic | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 6 | too few references (6/10 in range) | CER 0.65 WER 0.87 | unknown |
| as | Assamese | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 0.98 WER 1.11 | unknown |
| az | Azerbaijani | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.49 WER 0.83 | unknown |
| ba | Bashkir | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.92 WER 1.10 | unknown |
| be | Belarusian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.28 WER 0.68 | unknown |
| bg | Bulgarian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (7/10 in range) | CER 0.23 WER 0.64 | unknown |
| bn | Bengali | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (2/4 in range) | CER 0.45 WER 1.00 | unknown |
| bpy | Bishnupriya Manipuri | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| bs | Bosnian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/4 in range) | CER 0.26 WER 0.70 | unknown |
| ca | Catalan | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.12 WER 0.24 |  |
| ca-ba | Catalan (Balearic) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.19 WER 0.42 | unknown |
| ca-nw | Catalan (North-western) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.13 WER 0.31 |  |
| ca-va | Catalan (Valencian) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.12 WER 0.28 |  |
| chr | Cherokee | espeak | 2 engine-verified | pass (0 / 0 / 97 %) | 3 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| cmn | Chinese (Mandarin, latin as English) | espeak | 2 engine-verified | pass (0 / 0 / 90 %) | 4 | too few references (0/10 in range) | CER 0.66 | stress-or-tone |
| cmn-latn-pinyin | Chinese (Mandarin, latin as Pinyin) | espeak | 2 engine-verified | pass (0 / 0 / 92 %) | 2 | too few references (0/5 in range) | ASR unavailable (Whisper writes another script; references not converted yet) |  |
| crh | Crimean Tatar | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| cs | Czech | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.21 WER 0.48 | unknown |
| cv | Chuvash | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| cy | Welsh | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | too few references (2/5 in range) | CER 0.66 WER 1.20 | unknown |
| da | Danish | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | too few references (4/5 in range) | CER 0.38 WER 0.77 | unknown |
| dede | German | native | 2 engine-verified | pass (0 / 0 / 99 %) | 1 | FAIL 16/25 | CER 0.03 WER 0.10 | phoneme values |
| el | Greek | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.47 WER 0.70 | unknown |
| en-029 | English (Caribbean) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | FAIL 25/44 | CER 0.07 WER 0.11 | phoneme values |
| en-gb-scotland | English (Scotland) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | FAIL 41/56 | CER 0.13 WER 0.21 | phoneme values |
| en-gb-x-gbclan | English (Lancaster) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | FAIL 21/44 | CER 0.04 WER 0.07 | phoneme values |
| en-gb-x-gbcwmd | English (West Midlands) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | FAIL 22/44 | CER 0.04 WER 0.04 | phoneme values |
| en-gb-x-rp | English (Received Pronunciation) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | FAIL 23/47 | CER 0.03 WER 0.07 | phoneme values |
| en-shaw | English (Shavian alphabet) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 7 | FAIL 47/76 | ASR unavailable (no CC0 / CC BY sentence set has this language) | phoneme values |
| en-us-nyc | English (America, New York City) | espeak | 4 intelligibility-verified | pass (0 / 0 / 99 %) | 5 | pass 72/82 | CER 0.05 WER 0.07 |  |
| engb | British English | native | 2 engine-verified | pass (0 / 0 / 100 %) | 0 | FAIL 25/35 | CER 0.00 WER 0.00 | phoneme values |
| enus | US English | native | 4 intelligibility-verified | pass (0 / 0 / 100 %) | 1 | pass 34/38 | CER 0.01 WER 0.01 |  |
| eo | Esperanto | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| eses | Castilian Spanish | native | 2 engine-verified | pass (0 / 0 / 93 %) | 0 | FAIL 6/14 | CER 0.04 WER 0.15 | phoneme values |
| esus | Latin American Spanish | native | 2 engine-verified | pass (0 / 0 / 91 %) | 0 | FAIL 6/14 | CER 0.03 WER 0.10 | phoneme values |
| et | Estonian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.23 WER 0.81 | unknown |
| eu | Basque | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/7 in range) | CER 0.15 WER 0.69 | unknown |
| fa | Persian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (6/10 in range) | CER 0.53 WER 0.92 | unknown |
| fa-latn | Persian (Pinglish) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | ASR unavailable (no CC0 / CC BY sentence set has this language) |  |
| fi | Finnish | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.31 WER 0.81 | unknown |
| fo | Faroese | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | too few references (4/5 in range) | CER 0.54 WER 1.10 | unknown |
| fr-be | French (Belgium) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 5 | too few references (7/12 in range) | CER 0.40 WER 0.70 | unknown |
| fr-ch | French (Switzerland) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 5 | too few references (7/12 in range) | CER 0.40 WER 0.70 | unknown |
| frca | Canadian French | native | 2 engine-verified | pass (0 / 0 / 99 %) | 0 | no reference | CER 0.14 WER 0.24 |  |
| frfr | French | native | 2 engine-verified | pass (0 / 0 / 100 %) | 0 | too few references (0/4 in range) | CER 0.12 WER 0.30 |  |
| ga | Gaelic (Irish) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 6 | too few references (4/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| gd | Gaelic (Scottish) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| gn | Guarani | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| grc | Greek (Ancient) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| gu | Gujarati | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 0.44 WER 0.86 | unknown |
| hak | Hakka Chinese | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (6/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| haw | Hawaiian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.42 WER 0.89 | unknown |
| he | Hebrew | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (6/10 in range) | CER 0.65 WER 1.26 | unknown |
| hi | Hindi | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 0.37 WER 0.69 | unknown |
| hr | Croatian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/4 in range) | CER 0.08 WER 0.32 |  |
| ht | Haitian Creole | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (4/7 in range) | CER 0.25 WER 0.82 | unknown |
| hu | Hungarian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.24 WER 0.69 | unknown |
| hy | Armenian (East Armenia) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.18 WER 0.92 | unknown |
| hyw | Armenian (West Armenia) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | CER 0.32 WER 0.88 | unknown |
| ia | Interlingua | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| id | Indonesian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | CER 0.10 WER 0.20 |  |
| io | Ido | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| is | Icelandic | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | CER 0.58 WER 1.37 | unknown |
| itit | Italian | native | 2 engine-verified | pass (0 / 0 / 100 %) | 0 | too few references (1/4 in range) | CER 0.01 WER 0.05 |  |
| jajp | Japanese | native | 2 engine-verified | pass (0 / 0 / 100 %) | 8 | no reference | CER 0.15 | stress-or-tone |
| jbo | Lojban | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ka | Georgian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | CER 0.36 WER 1.03 | unknown |
| kaa | Karakalpak | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| kk | Kazakh | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 0.39 WER 0.88 | unknown |
| kl | Greenlandic | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| kn | Kannada | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 5 | too few references (7/10 in range) | CER 0.35 WER 1.03 | unknown |
| ko | Korean | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | CER 0.56 WER 1.07 | unknown |
| kok | Konkani | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ku | Kurdish | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ky | Kyrgyz | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| la | Latin | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | CER 0.11 WER 0.45 |  |
| lb | Luxembourgish | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/4 in range) | CER 0.57 WER 1.05 | unknown |
| lfn | Lingua Franca Nova | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| lij | Ligurian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| lt | Lithuanian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 5 | too few references (8/10 in range) | CER 0.42 WER 0.86 | unknown |
| ltg | Latgalian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| lv | Latvian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.36 WER 0.78 | unknown |
| mi | Māori | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.33 WER 0.81 | unknown |
| mk | Macedonian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/4 in range) | CER 0.20 WER 0.68 | unknown |
| ml | Malayalam | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.94 WER 1.46 | unknown |
| mn | Mongolian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.42 WER 1.03 | unknown |
| mn-f | Ankhmaa | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.42 WER 1.03 | unknown |
| mr | Marathi | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 0.73 WER 1.31 | unknown |
| ms | Malay | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | CER 0.15 WER 0.32 |  |
| mt | Maltese | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.51 WER 1.05 | unknown |
| mto | Totontepec Mixe | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | no reference | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| my | Myanmar (Burmese) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 1.13 | stress-or-tone |
| nb | Norwegian Bokmål | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (8/10 in range) | CER 0.31 WER 0.68 | unknown |
| nci | Nahuatl (Classical) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ne | Nepali | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 0.42 WER 1.00 | unknown |
| nl | Dutch | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.27 WER 0.60 | unknown |
| nog | Nogai | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (9/12 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| om | Oromo | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| or | Oriya | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (2/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pa | Punjabi | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (3/5 in range) | CER 0.66 WER 0.98 | stress-or-tone |
| pap | Papiamento | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pdc | Pennsylvania Dutch (Lancaster) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pdc-x-lehigh | Pennsylvania Dutch (Lehigh) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pdc-x-midwest | Pennsylvania Dutch (Midwest) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| piqd | Klingon | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| plpl | Polish (experimental) | native | 2 engine-verified | pass (0 / 0 / 100 %) | 0 | no reference | CER 0.09 WER 0.32 |  |
| ps | Pashto | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.61 WER 1.10 | unknown |
| ps-x-northwest | Pashto (Northwestern) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.59 WER 1.10 | unknown |
| ps-x-southeast | Pashto (Southeastern) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.62 WER 1.12 | unknown |
| ps-x-yusufzai | Pashto (Yusufzai) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.62 WER 1.08 | unknown |
| pt | Portuguese (Portugal) | espeak | 4 intelligibility-verified | pass (0 / 0 / 98 %) | 2 | pass 21/24 | CER 0.06 WER 0.14 |  |
| pt-br | Portuguese (Brazil) | espeak | 4 intelligibility-verified | pass (0 / 0 / 98 %) | 2 | pass 22/27 | CER 0.06 WER 0.13 |  |
| py | Pyash | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| qdb | Lang Belta | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| qu | Quechua | espeak | 1 draft | FAIL (0 / 1 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) | phoneme values |
| quc | K'iche' | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (6/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| qya | Quenya | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ro | Romanian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | CER 0.13 WER 0.35 |  |
| ru | Russian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (10/12 in range) | CER 0.22 WER 0.58 | unknown |
| ru-cl | Russian (Classic) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (10/12 in range) | CER 0.22 WER 0.58 | unknown |
| ru-lv | Russian (Latvia) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (10/12 in range) | CER 0.27 WER 0.61 | unknown |
| rup | Aromanian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| sd | Sindhi | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 1.05 WER 1.33 | unknown |
| shn | Shan (Tai Yai) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (4/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| si | Sinhala | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (3/5 in range) | CER 1.03 WER 1.16 | unknown |
| sjn | Sindarin | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| sk | Slovak | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.25 WER 0.60 | unknown |
| sl | Slovenian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.35 WER 0.42 | unknown |
| smj | Lule Saami | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (6/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| sq | Albanian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (1/4 in range) | CER 0.20 WER 0.56 | unknown |
| sr | Serbian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/4 in range) | CER 0.17 WER 0.43 | unknown |
| sv | Swedish | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (6/10 in range) | CER 0.27 WER 0.74 | unknown |
| sw | Swahili | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.20 WER 0.75 | unknown |
| ta | Tamil | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 5 | too few references (8/10 in range) | CER 0.48 WER 1.02 | unknown |
| te | Telugu | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 0.47 WER 1.10 | unknown |
| th | Thai | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 1.22 | unknown |
| ti | Tigrinya | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| tk | Turkmen | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.57 WER 1.17 | unknown |
| tn | Setswana | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| tr | Turkish | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.28 WER 0.49 | unknown |
| tt | Tatar | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.59 WER 1.31 | unknown |
| ug | Uyghur | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| uk | Ukrainian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.24 WER 0.58 | unknown |
| ur | Urdu | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 3 | too few references (4/5 in range) | CER 0.65 WER 1.00 | unknown |
| uz | Uzbek | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.46 WER 1.12 | unknown |
| vi | Vietnamese (Northern) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 1.27 WER 1.33 | stress-or-tone |
| vi-vn-x-central | Vietnamese (Central) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 1.63 WER 1.61 | stress-or-tone |
| vi-vn-x-south | Vietnamese (Southern) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 1.49 WER 1.50 | stress-or-tone |
| xex | xextan-test | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 2 | too few references (4/6 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| yue | Chinese (Cantonese) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (2/10 in range) | CER 1.29 | stress-or-tone |
| yue-latn-jyutping | Chinese (Cantonese, latin as Jyutping) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (1/5 in range) | ASR unavailable (Whisper writes another script; references not converted yet) |  |

<!-- STATUS END -->

## Phase 6 (2026-10-11): failure-layer triage of every language

<!-- TRIAGE BEGIN (written by harness/triage.py) -->
Written by `harness/triage.py` from the measurements named in its header; the rules that give a layer are there too. Levels are those of the Phase 1 baseline: this phase measured no language afresh against references, so none changed. A3 on the final stage (`stage-dev`): 145 packs, 0 failures (20 packs failed it on the Phase 3 stage).

| Failure layer | Languages |
|---|---|
| phoneme values | 21 |
| G2P | 68 |
| stress-or-tone | 0 |
| unknown | 11 |
| not measured | 41 |
| passes ASR | 14 |
| all | 155 |

| Tag | Language | Template | Level | ASR CER | eSpeak NG own voice | Layer | Evidence |
|---|---|---|---|---|---|---|---|
| ab | Abkhaz | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| af | Afrikaans | dedx | 2 | 0.32 | 0.21 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.21 against 0.32 here); this engine is further 0.11 behind it |
| am | Amharic | dedx | 2 | 1.43 | 1.34 | G2P | eSpeak NG's own voice fails these sentences too (CER 1.34 against 1.43 here) |
| an | Aragonese | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| ar | Arabic | dedx | 2 | 0.65 | 0.57 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.57 against 0.65 here) |
| as | Assamese | dedx | 2 | 0.98 | 0.99 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.99 against 0.98 here) |
| az | Azerbaijani | dedx | 2 | 0.49 | 0.22 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.22 against 0.49 here); this engine is further 0.27 behind it |
| ba | Bashkir | dedx | 2 | 0.92 | 0.95 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.95 against 0.92 here) |
| be | Belarusian | dedx | 2 | 0.28 | 0.37 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.37 against 0.28 here) |
| bg | Bulgarian | dedx | 2 | 0.23 | 0.22 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.22 against 0.23 here) |
| bn | Bengali | itix | 2 | 0.45 | 0.42 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.42 against 0.45 here) |
| bpy | Bishnupriya Manipuri | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| bs | Bosnian | itix | 2 | 0.26 | 0.18 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.18 against 0.26 here) |
| ca | Catalan | esex | 2 | 0.12 | 0.15 |  | ASR passes |
| ca-ba | Catalan (Balearic) | esex | 2 | 0.19 | 0.27 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.27 against 0.19 here) |
| ca-nw | Catalan (North-western) | esex | 2 | 0.13 | 0.27 |  | ASR passes |
| ca-va | Catalan (Valencian) | esex | 2 | 0.12 | 0.17 |  | ASR passes |
| chr | Cherokee | enux | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| cmn | Chinese (Mandarin, latin as English) | dedx | 2 | 0.66 | 0.39 | G2P (then stress-or-tone) | eSpeak NG's own voice fails these sentences too (CER 0.39 against 0.66 here); this engine is further 0.27 behind it |
| cmn-latn-pinyin | Chinese (Mandarin, latin as Pinyin) | dedx | 2 |  |  | not measured | Whisper writes another script; references not converted yet |
| crh | Crimean Tatar | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| cs | Czech | dedx | 2 | 0.21 | 0.05 | unknown | eSpeak NG's own voice reads the sentences (CER 0.05), this engine does not (0.21): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| cv | Chuvash | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| cy | Welsh | engx | 2 | 0.66 | 0.29 | phoneme values (then G2P) | 4 phone(s) the engine meant had no sound (phone-unsounded) |
| da | Danish | dedx | 2 | 0.38 | 0.43 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.43 against 0.38 here) |
| dede | German | dede | 2 | 0.03 |  | phoneme values | check B fails: 16 of 25 values in range |
| el | Greek | esex | 2 | 0.47 | 0.31 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.31 against 0.47 here); this engine is further 0.16 behind it |
| en-029 | English (Caribbean) | engx | 2 | 0.07 | 0.07 | phoneme values | check B fails: 25 of 44 values in range; 4 phone(s) the engine meant had no sound (phone-unsounded) |
| en-gb-scotland | English (Scotland) | engx | 2 | 0.13 | 0.00 | phoneme values | check B fails: 41 of 56 values in range; 4 phone(s) the engine meant had no sound (phone-unsounded) |
| en-gb-x-gbclan | English (Lancaster) | engx | 2 | 0.04 | 0.00 | phoneme values | check B fails: 21 of 44 values in range; 4 phone(s) the engine meant had no sound (phone-unsounded) |
| en-gb-x-gbcwmd | English (West Midlands) | engx | 2 | 0.04 | 0.02 | phoneme values | check B fails: 22 of 44 values in range; 4 phone(s) the engine meant had no sound (phone-unsounded) |
| en-gb-x-rp | English (Received Pronunciation) | engx | 2 | 0.03 | 0.01 | phoneme values | check B fails: 23 of 47 values in range; 4 phone(s) the engine meant had no sound (phone-unsounded) |
| en-shaw | English (Shavian alphabet) | engx | 2 |  |  | phoneme values | check B fails: 47 of 76 values in range; 8 phone(s) the engine meant had no sound (phone-unsounded) |
| en-us-nyc | English (America, New York City) | enux | 4 | 0.05 | 0.09 | phoneme values | 9 phone(s) the engine meant had no sound (phone-unsounded) |
| engb | British English | engb | 2 | 0.00 |  | phoneme values | check B fails: 25 of 35 values in range |
| enus | US English | enus | 4 | 0.01 |  |  | ASR passes |
| eo | Esperanto | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| eses | Castilian Spanish | eses | 2 | 0.04 |  | phoneme values | check B fails: 6 of 14 values in range |
| esus | Latin American Spanish | esus | 2 | 0.03 |  | phoneme values | check B fails: 6 of 14 values in range |
| et | Estonian | dedx | 2 | 0.23 | 0.20 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.20 against 0.23 here) |
| eu | Basque | esex | 2 | 0.15 | 0.15 | unknown | eSpeak NG's own voice reads the sentences (CER 0.15), this engine does not (0.15): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| fa | Persian | dedx | 2 | 0.53 | 0.31 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.31 against 0.53 here); this engine is further 0.21 behind it |
| fa-latn | Persian (Pinglish) | dedx | 2 |  |  | not measured | no CC0 / CC BY sentence set has this language |
| fi | Finnish | dedx | 2 | 0.31 | 0.17 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.17 against 0.31 here); this engine is further 0.14 behind it |
| fo | Faroese | dedx | 2 | 0.54 | 0.53 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.53 against 0.54 here) |
| fr-be | French (Belgium) | frfx | 2 | 0.40 | 0.23 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.23 against 0.40 here); this engine is further 0.18 behind it |
| fr-ch | French (Switzerland) | frfx | 2 | 0.40 | 0.23 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.23 against 0.40 here); this engine is further 0.18 behind it |
| frca | Canadian French | frca | 2 | 0.14 |  |  | ASR passes |
| frfr | French | frfr | 2 | 0.12 |  |  | ASR passes |
| ga | Gaelic (Irish) | engx | 2 |  |  | phoneme values | 8 phone(s) the engine meant had no sound (phone-unsounded) |
| gd | Gaelic (Scottish) | engx | 2 |  |  | phoneme values | 4 phone(s) the engine meant had no sound (phone-unsounded) |
| gn | Guarani | esux | 2 |  |  | phoneme values | 1 phone(s) the engine meant had no sound (phone-unsounded) |
| grc | Greek (Ancient) | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| gu | Gujarati | dedx | 2 | 0.44 | 0.48 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.48 against 0.44 here) |
| hak | Hakka Chinese | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| haw | Hawaiian | esex | 2 | 0.42 | 0.30 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.30 against 0.42 here); this engine is further 0.12 behind it |
| he | Hebrew | esex | 2 | 0.65 | 0.63 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.63 against 0.65 here) |
| hi | Hindi | dedx | 2 | 0.37 | 0.31 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.31 against 0.37 here) |
| hr | Croatian | itix | 2 | 0.08 | 0.08 |  | ASR passes |
| ht | Haitian Creole | frfx | 2 | 0.25 | 0.23 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.23 against 0.25 here) |
| hu | Hungarian | dedx | 2 | 0.24 | 0.10 | unknown | eSpeak NG's own voice reads the sentences (CER 0.10), this engine does not (0.24): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| hy | Armenian (East Armenia) | dedx | 2 | 0.18 | 0.16 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.16 against 0.18 here) |
| hyw | Armenian (West Armenia) | dedx | 2 | 0.32 | 0.33 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.33 against 0.32 here) |
| ia | Interlingua | itix | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| id | Indonesian | itix | 2 | 0.10 | 0.08 |  | ASR passes |
| io | Ido | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| is | Icelandic | dedx | 2 | 0.58 | 0.42 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.42 against 0.58 here); this engine is further 0.16 behind it |
| itit | Italian | itit | 2 | 0.01 |  |  | ASR passes |
| jajp | Japanese | jajp | 2 | 0.15 |  | unknown | ASR fails; eSpeak NG own-voice score missing |
| jbo | Lojban | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| ka | Georgian | dedx | 2 | 0.36 | 0.22 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.22 against 0.36 here); this engine is further 0.14 behind it |
| kaa | Karakalpak | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| kk | Kazakh | dedx | 2 | 0.39 | 0.30 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.30 against 0.39 here) |
| kl | Greenlandic | itix | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| kn | Kannada | dedx | 2 | 0.35 | 0.36 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.36 against 0.35 here) |
| ko | Korean | itix | 2 | 0.56 | 0.42 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.42 against 0.56 here); this engine is further 0.14 behind it |
| kok | Konkani | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| ku | Kurdish | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| ky | Kyrgyz | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| la | Latin | itix | 2 | 0.11 | 0.05 |  | ASR passes |
| lb | Luxembourgish | dedx | 2 | 0.57 | 0.55 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.55 against 0.57 here) |
| lfn | Lingua Franca Nova | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| lij | Ligurian | itix | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| lt | Lithuanian | dedx | 2 | 0.42 | 0.22 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.22 against 0.42 here); this engine is further 0.20 behind it |
| ltg | Latgalian | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| lv | Latvian | dedx | 2 | 0.36 | 0.43 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.43 against 0.36 here) |
| mi | Māori | esex | 2 | 0.33 | 0.28 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.28 against 0.33 here) |
| mk | Macedonian | itix | 2 | 0.20 | 0.19 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.19 against 0.20 here) |
| ml | Malayalam | dedx | 2 | 0.94 | 0.96 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.96 against 0.94 here) |
| mn | Mongolian | dedx | 2 | 0.42 | 0.46 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.46 against 0.42 here) |
| mn-f | Ankhmaa | dedx | 2 | 0.42 | 0.43 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.43 against 0.42 here) |
| mr | Marathi | dedx | 2 | 0.73 | 0.39 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.39 against 0.73 here); this engine is further 0.34 behind it |
| ms | Malay | itix | 2 | 0.15 | 0.08 |  | ASR passes |
| mt | Maltese | dedx | 2 | 0.51 | 0.44 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.44 against 0.51 here) |
| mto | Totontepec Mixe | esux | 2 |  |  | phoneme values | 2 phone(s) the engine meant had no sound (phone-unsounded) |
| my | Myanmar (Burmese) | dedx | 2 | 1.13 | 0.99 | G2P (then stress-or-tone) | eSpeak NG's own voice fails these sentences too (CER 0.99 against 1.13 here); this engine is further 0.15 behind it |
| nb | Norwegian Bokmål | dedx | 2 | 0.31 | 0.15 | unknown | eSpeak NG's own voice reads the sentences (CER 0.15), this engine does not (0.31): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| nci | Nahuatl (Classical) | esux | 2 |  |  | phoneme values | 2 phone(s) the engine meant had no sound (phone-unsounded) |
| ne | Nepali | dedx | 2 | 0.42 | 0.28 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.28 against 0.42 here); this engine is further 0.13 behind it |
| nl | Dutch | dedx | 2 | 0.27 | 0.09 | unknown | eSpeak NG's own voice reads the sentences (CER 0.09), this engine does not (0.27): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| nog | Nogai | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| om | Oromo | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| or | Oriya | itix | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| pa | Punjabi | dedx | 2 | 0.66 | 0.55 | G2P (then stress-or-tone) | eSpeak NG's own voice fails these sentences too (CER 0.55 against 0.66 here); this engine is further 0.11 behind it |
| pap | Papiamento | esux | 2 |  |  | phoneme values | 2 phone(s) the engine meant had no sound (phone-unsounded) |
| pdc | Pennsylvania Dutch (Lancaster) | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| pdc-x-lehigh | Pennsylvania Dutch (Lehigh) | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| pdc-x-midwest | Pennsylvania Dutch (Midwest) | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| piqd | Klingon | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| plpl | Polish (experimental) | plpl | 2 | 0.09 |  |  | ASR passes |
| ps | Pashto | dedx | 2 | 0.61 | 0.67 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.67 against 0.61 here) |
| ps-x-northwest | Pashto (Northwestern) | dedx | 2 | 0.59 | 0.68 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.68 against 0.59 here) |
| ps-x-southeast | Pashto (Southeastern) | dedx | 2 | 0.62 | 0.67 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.67 against 0.62 here) |
| ps-x-yusufzai | Pashto (Yusufzai) | dedx | 2 | 0.62 | 0.68 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.68 against 0.62 here) |
| pt | Portuguese (Portugal) | esex | 4 | 0.06 | 0.05 |  | ASR passes |
| pt-br | Portuguese (Brazil) | esux | 4 | 0.06 | 0.05 | phoneme values | 2 phone(s) the engine meant had no sound (phone-unsounded) |
| py | Pyash | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| qdb | Lang Belta | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| qu | Quechua | esux | 1 |  |  | phoneme values | check A fails: s/?: a F0 measured 132.45, frames 126.0125; 1 phone(s) the engine meant had no sound (phone-unsounded) |
| quc | K'iche' | esux | 2 |  |  | phoneme values | 2 phone(s) the engine meant had no sound (phone-unsounded) |
| qya | Quenya | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| ro | Romanian | itix | 2 | 0.13 | 0.13 |  | ASR passes |
| ru | Russian | dedx | 2 | 0.22 | 0.25 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.25 against 0.22 here) |
| ru-cl | Russian (Classic) | dedx | 2 | 0.22 | 0.27 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.27 against 0.22 here) |
| ru-lv | Russian (Latvia) | dedx | 2 | 0.27 | 0.15 | unknown | eSpeak NG's own voice reads the sentences (CER 0.15), this engine does not (0.27): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| rup | Aromanian | itix | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| sd | Sindhi | dedx | 2 | 1.05 | 1.12 | G2P | eSpeak NG's own voice fails these sentences too (CER 1.12 against 1.05 here) |
| shn | Shan (Tai Yai) | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| si | Sinhala | dedx | 2 | 1.03 | 1.15 | G2P | eSpeak NG's own voice fails these sentences too (CER 1.15 against 1.03 here) |
| sjn | Sindarin | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| sk | Slovak | dedx | 2 | 0.25 | 0.14 | unknown | eSpeak NG's own voice reads the sentences (CER 0.14), this engine does not (0.25): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| sl | Slovenian | dedx | 2 | 0.35 | 0.08 | unknown | eSpeak NG's own voice reads the sentences (CER 0.08), this engine does not (0.35): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| smj | Lule Saami | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| sq | Albanian | itix | 2 | 0.20 | 0.23 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.23 against 0.20 here) |
| sr | Serbian | itix | 2 | 0.17 | 0.19 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.19 against 0.17 here) |
| sv | Swedish | dedx | 2 | 0.27 | 0.12 | unknown | eSpeak NG's own voice reads the sentences (CER 0.12), this engine does not (0.27): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| sw | Swahili | esex | 2 | 0.20 | 0.21 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.21 against 0.20 here) |
| ta | Tamil | dedx | 2 | 0.48 | 0.34 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.34 against 0.48 here); this engine is further 0.14 behind it |
| te | Telugu | dedx | 2 | 0.47 | 0.31 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.31 against 0.47 here); this engine is further 0.15 behind it |
| th | Thai | esex | 2 | 1.22 | 1.31 | G2P | eSpeak NG's own voice fails these sentences too (CER 1.31 against 1.22 here) |
| ti | Tigrinya | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| tk | Turkmen | dedx | 2 | 0.57 | 0.45 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.45 against 0.57 here); this engine is further 0.11 behind it |
| tn | Setswana | esex | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| tr | Turkish | dedx | 2 | 0.28 | 0.07 | unknown | eSpeak NG's own voice reads the sentences (CER 0.07), this engine does not (0.28): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart |
| tt | Tatar | dedx | 2 | 0.59 | 0.37 | G2P (then unknown) | eSpeak NG's own voice fails these sentences too (CER 0.37 against 0.59 here); this engine is further 0.22 behind it |
| ug | Uyghur | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| uk | Ukrainian | dedx | 2 | 0.24 | 0.16 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.16 against 0.24 here) |
| ur | Urdu | dedx | 2 | 0.65 | 0.57 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.57 against 0.65 here) |
| uz | Uzbek | dedx | 2 | 0.46 | 0.54 | G2P | eSpeak NG's own voice fails these sentences too (CER 0.54 against 0.46 here) |
| vi | Vietnamese (Northern) | dedx | 2 | 1.27 | 0.98 | G2P (then stress-or-tone) | eSpeak NG's own voice fails these sentences too (CER 0.98 against 1.27 here); this engine is further 0.29 behind it |
| vi-vn-x-central | Vietnamese (Central) | dedx | 2 | 1.63 | 1.28 | G2P (then stress-or-tone) | eSpeak NG's own voice fails these sentences too (CER 1.28 against 1.63 here); this engine is further 0.35 behind it |
| vi-vn-x-south | Vietnamese (Southern) | dedx | 2 | 1.49 | 1.42 | G2P | eSpeak NG's own voice fails these sentences too (CER 1.42 against 1.49 here) |
| xex | xextan-test | dedx | 2 |  |  | not measured | Whisper large-v3 has no language for this tag |
| yue | Chinese (Cantonese) | dedx | 2 | 1.29 | 0.85 | G2P (then stress-or-tone) | eSpeak NG's own voice fails these sentences too (CER 0.85 against 1.29 here); this engine is further 0.44 behind it |
| yue-latn-jyutping | Chinese (Cantonese, latin as Jyutping) | dedx | 2 |  |  | not measured | Whisper writes another script; references not converted yet |
<!-- TRIAGE END -->
