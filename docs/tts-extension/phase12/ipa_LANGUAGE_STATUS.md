# Language status

Status level and failure-layer triage for every language, dialect and accent (playbook 1.5). **Skeleton: Phase 1 fills in the baseline for all existing languages.**

Levels: 1 `draft` · 2 `engine-verified` (the harness shows the engine realizes the requested parameters) · 3 `reference-verified` (realized values fall within reference ranges) · 4 `intelligibility-verified` (speech-recognition round trip passes, where a recognizer supports the language) · 5 `native-validated` (a named native speaker or expert signed off the review packet). Only level 5 may be called "authentic".

## Phase 9 (2026-10-11): the completion review; the table below regenerated on the staged golden

- **The table below was regenerated** (`report.py`, 2026-10-11) on the staged modules' golden (`golden-staged/`, 29,237 cases, the modules Phase 10 would ship) with a fresh ASR run on the same stage and the reference lookup of D93. Levels now: **1 draft 3** (cmn, cmn-latn-pinyin, qu), **2 engine-verified 148**, **3 none**, **4 intelligibility-verified 4** (enus, en-us-nyc, pt, pt-br), **5 none**. Nothing is called authentic; nothing below level 5 is confirmed authentic.
- **Mandarin is level 1, not 2** (Q48): check A fails on the shipped golden as on the staged one (A2 1979 and 1983 of 2367: 83.6 % and 83.8 %, mark 90 %); the earlier "2" came from a status report run before the golden gained the `#`-named cases (D38a). Failure layer "phoneme values"; a `/diagnose-language cmn` session on Fable 5.1 is the next step.
- **Check B under D93** (a pack's own variety, then its parents, never a sibling): pass 4 (enus 34/38, en-us-nyc 82/94, pt 20/24, pt-br 22/27), fail 3 (dede 16/25, eses 6/14, ca-va 21/29 on its own Valencian ranges), too few references 144, no reference 4. en-029, en-gb-scotland, en-gb-x-gbclan, en-gb-x-gbcwmd, en-gb-x-rp, en-shaw, engb and esus were "FAIL" against another variety's ranges and are now "too few references"; ca, ca-ba and ca-nw are no longer judged by Valencian ranges. No level changed by the rule.
- **ASR re-run on the stage** (`results/asr.json`, 2026-10-11; 105 scored, 50 unavailable as before): against 2026-10-05 on the shipped modules, median CER 0.325 -> 0.307; 37 languages better by more than 0.02, 20 worse, 48 within 0.02. Now at or under 0.15 that were not: sl (0.35 -> 0.09), hy (0.18 -> 0.15); now above it that were not: **ca (0.12 -> 0.26), ca-nw (0.13 -> 0.18), ca-va (0.12 -> 0.16)**. Largest rises: si +0.28, el +0.23, cmn +0.20, vi-vn-x-south +0.18, fi +0.18, tr +0.18; largest falls: sl -0.26, fr-be and fr-ch -0.23, yue -0.23, vi-vn-x-central -0.22, mr -0.18. The native modules are unchanged (enus 0.006 -> 0.009, pt and pt-br identical). The rises are a Phase 10 note: the staged modules are what ships, and Catalan should be diagnosed (`/diagnose-language ca`) before or after, the human's call.
- **Finnish**: the long vowels add about 50 ms (Q47); an `/improve-language fi` item.
- **Trial packs of the completion review**: `packs-proposed/fi-x-evvtrial/` (a TEST copy of Finnish by the add-language skill, level 2, `trials/PHASE9_TRIAL_A_fi-x-evvtrial.md`; proposed, never shipped, no row below) and the real dialect below (shipped in 1.3.0).
- **Shipped in 1.3.0 (Phase 10, the human's choice Q50, `DECISIONS.md` D95): `nl-be`, now `packs/nl-be/` with its overrides applied; its row is in the table below. The Phase 9 note follows. Formerly proposed: `nl-be` (Southern Standard Dutch, Flanders), `packs-proposed/nl-be/`** (the /add-dialect trial, 2026-10-11, `docs/tts-extension/trials/PHASE9_TRIAL_B_nl-be.md`): 11 vowel overrides from adank2004 Table I, `derived`; level 2 engine-verified (check A pass, check B "too few references", CER 0.199 as its parent `nl`; with the overrides built in CER 0.293). Nothing called authentic; waits for the human's say-so.
- **Native review (D82) can start**: the ten items to put first are in `COMPLETION_REVIEW_PHASE9.md` section 4.

## Phase 8 (2026-10-11): no language's level changed

- **Every dialect pack is documented** (D91): the 20 dialects carry their variety, region, speaker group and a descriptive source each (`packs/<tag>/pack.toml` `[meta]`, three of the sources weak, said in the pack's note), and their `[meta] status` repeats the level below (2; en-us-nyc and pt-br 4). cmn-latn-pinyin, en-shaw, fa-latn, yue-latn-jyutping (spellings) and mn-f (a voice) are now `kind = "language"`. `validate_packs.py`: 21 packs, 21 accepted. No sound changed.
- **Valencian (ca-va) has check B references now** (jimenez2019 Table 1, Phase 8's improve-language test): check B, measured on the stage with `check_language.py`, went from "too few references (3/5 in range)" to **FAIL 21/29** (F1 of /ɛ ɔ/ 40-55 Hz under the range, /i u/ just under); level 2 unchanged; failure layer "phoneme values". The reference lookup lends these ranges to **ca, ca-ba and ca-nw** as well (each FAIL 21/29, level 2 unchanged): `OPEN_QUESTIONS.md` Q46, for Phase 9. The tables below were not regenerated (`report.py` waits for Q46 and a fresh `asr.py`); they still say "too few references" for these four.
- **Swahili (sw)**: diagnosed, not changed (`OPEN_QUESTIONS.md` Q45): its word error (0.75) against its character error (0.20) is mostly the metric on long words; an inserted "ya" at vowel-to-vowel word junctions is the main boundary fault, with a fix proposed.
- The worked examples and the skill tests (`docs/tts-extension/examples/`, tags `-x-evvdemo`, `-x-evvskill`) are TEST packs, never shipped, and have no row here.

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

Measured 2026-10-11 by `harness/report.py`. Preset 1 (adult male), 64-bit, 11025 Hz. Levels: 1 draft: 5, 2 engine-verified: 150, 4 intelligibility-verified: 1. Check A = engine fidelity (A1 frames, A2 sound vs frames), check B = against cited reference ranges, ASR = Whisper large-v3 character error rate. Pass marks: A2 >= 90 %, B >= 80 %, CER <= 0.15. A failure layer is a first-pass label, not a diagnosis.

| Tag | Language | Kind | Level | Check A (A0 substituted / A1 silent / A2) | No phone of its own | Check B | ASR | Failure layer |
|---|---|---|---|---|---|---|---|---|
| ab | Abkhaz | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (1/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| af | Afrikaans | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.52 WER 1.10 | unknown |
| am | Amharic | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 1.65 WER 1.68 | unknown |
| an | Aragonese | espeak | 1 draft | FAIL (0 / 0 / 90 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) | phoneme values |
| ar | Arabic | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 6 | too few references (4/10 in range) | CER 0.77 WER 1.00 | unknown |
| as | Assamese | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 1.14 WER 1.38 | unknown |
| az | Azerbaijani | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.70 WER 1.03 | unknown |
| ba | Bashkir | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 0.97 WER 1.40 | unknown |
| be | Belarusian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.41 WER 1.03 | unknown |
| bg | Bulgarian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (5/10 in range) | CER 0.44 WER 0.88 | unknown |
| bn | Bengali | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (4/5 in range) | CER 0.54 WER 1.12 | unknown |
| bpy | Bishnupriya Manipuri | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| bs | Bosnian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (5/5 in range) | CER 0.51 WER 0.91 | unknown |
| ca | Catalan | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.60 WER 1.01 | unknown |
| ca-ba | Catalan (Balearic) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.66 WER 1.04 | unknown |
| ca-nw | Catalan (North-western) | espeak | 2 engine-verified | pass (0 / 0 / 94 %) | 2 | too few references (3/5 in range) | CER 0.48 WER 0.87 | unknown |
| ca-va | Catalan (Valencian) | espeak | 2 engine-verified | pass (0 / 0 / 90 %) | 2 | FAIL 10/29 | CER 0.48 WER 0.87 | phoneme values |
| chr | Cherokee | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| cmn | Chinese (Mandarin, latin as English) | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 4 | too few references (2/10 in range) | CER 0.79 | stress-or-tone |
| cmn-latn-pinyin | Chinese (Mandarin, latin as Pinyin) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (1/5 in range) | ASR unavailable (Whisper writes another script; references not converted yet) |  |
| crh | Crimean Tatar | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| cs | Czech | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.38 WER 0.72 | unknown |
| cv | Chuvash | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| cy | Welsh | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 1.03 WER 1.39 | unknown |
| da | Danish | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 4 | too few references (2/5 in range) | CER 0.64 WER 1.16 | unknown |
| dede | German | native | 2 engine-verified | pass (0 / 0 / 98 %) | 11 | FAIL 16/25 | CER 0.03 WER 0.10 | phoneme values |
| el | Greek | espeak | 2 engine-verified | pass (0 / 0 / 95 %) | 2 | too few references (3/5 in range) | CER 0.72 WER 0.86 | unknown |
| en-029 | English (Caribbean) | espeak | 2 engine-verified | pass (0 / 0 / 97 %) | 2 | too few references (3/5 in range) | CER 0.47 WER 0.85 | unknown |
| en-gb-scotland | English (Scotland) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.25 WER 0.35 | unknown |
| en-gb-x-gbclan | English (Lancaster) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.23 WER 0.35 | unknown |
| en-gb-x-gbcwmd | English (West Midlands) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.39 WER 0.63 | unknown |
| en-gb-x-rp | English (Received Pronunciation) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.33 WER 0.56 | unknown |
| en-shaw | English (Shavian alphabet) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 6 | too few references (7/10 in range) | ASR unavailable (no CC0 / CC BY sentence set has this language) |  |
| en-us-nyc | English (America, New York City) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 6 | FAIL 63/94 | CER 0.38 WER 0.60 | phoneme values |
| engb | British English | native | 2 engine-verified | pass (0 / 0 / 100 %) | 39 | too few references (1/5 in range) | CER 0.00 WER 0.02 |  |
| enus | US English | native | 4 intelligibility-verified | pass (0 / 0 / 100 %) | 15 | pass 34/38 | CER 0.01 WER 0.03 |  |
| eo | Esperanto | espeak | 2 engine-verified | pass (0 / 0 / 90 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| eses | Castilian Spanish | native | 2 engine-verified | pass (0 / 0 / 96 %) | 30 | FAIL 6/14 | CER 0.04 WER 0.15 | phoneme values |
| esus | Latin American Spanish | native | 2 engine-verified | pass (0 / 0 / 97 %) | 7 | too few references (1/4 in range) | CER 0.03 WER 0.10 |  |
| et | Estonian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.45 WER 1.20 | unknown |
| eu | Basque | espeak | 1 draft | FAIL (0 / 0 / 89 %) | 2 | too few references (4/7 in range) | CER 0.33 WER 0.91 | phoneme values |
| fa | Persian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (4/10 in range) | CER 0.65 WER 1.07 | unknown |
| fa-latn | Persian (Pinglish) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | ASR unavailable (no CC0 / CC BY sentence set has this language) |  |
| fi | Finnish | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.53 WER 0.94 | unknown |
| fo | Faroese | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (1/5 in range) | CER 0.91 WER 1.73 | unknown |
| fr-be | French (Belgium) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 6 | too few references (10/12 in range) | CER 0.27 WER 0.58 | unknown |
| fr-ch | French (Switzerland) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 6 | too few references (10/12 in range) | CER 0.27 WER 0.58 | unknown |
| frca | Canadian French | native | 2 engine-verified | pass (0 / 0 / 99 %) | 12 | no reference | CER 0.11 WER 0.30 |  |
| frfr | French | native | 2 engine-verified | pass (0 / 0 / 100 %) | 30 | too few references (0/4 in range) | CER 0.09 WER 0.25 |  |
| ga | Gaelic (Irish) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (8/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| gd | Gaelic (Scottish) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| gn | Guarani | espeak | 1 draft | FAIL (0 / 0 / 89 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) | phoneme values |
| grc | Greek (Ancient) | espeak | 2 engine-verified | pass (0 / 0 / 92 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| gu | Gujarati | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.66 WER 1.02 | unknown |
| hak | Hakka Chinese | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 4 | too few references (6/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| haw | Hawaiian | espeak | 2 engine-verified | pass (0 / 0 / 93 %) | 2 | too few references (4/5 in range) | CER 0.47 WER 1.05 | unknown |
| he | Hebrew | espeak | 2 engine-verified | pass (0 / 0 / 91 %) | 4 | too few references (8/10 in range) | CER 0.76 WER 1.26 | unknown |
| hi | Hindi | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.56 WER 0.97 | unknown |
| hr | Croatian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (5/5 in range) | CER 0.29 WER 0.67 | unknown |
| ht | Haitian Creole | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (4/7 in range) | CER 0.39 WER 0.91 | unknown |
| hu | Hungarian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.52 WER 0.94 | unknown |
| hy | Armenian (East Armenia) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.34 WER 1.16 | unknown |
| hyw | Armenian (West Armenia) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.54 WER 0.99 | unknown |
| ia | Interlingua | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| id | Indonesian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.90 WER 1.04 | unknown |
| io | Ido | espeak | 2 engine-verified | pass (0 / 0 / 90 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| is | Icelandic | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.82 WER 1.57 | unknown |
| itit | Italian | native | 2 engine-verified | pass (0 / 0 / 94 %) | 9 | too few references (1/4 in range) | CER 0.01 WER 0.05 |  |
| jajp | Japanese | native | 2 engine-verified | pass (0 / 0 / 100 %) | 27 | no reference | CER 0.15 | stress-or-tone |
| jbo | Lojban | espeak | 2 engine-verified | pass (0 / 0 / 96 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ka | Georgian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.39 WER 1.06 | unknown |
| kaa | Karakalpak | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| kk | Kazakh | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 0.70 WER 1.04 | unknown |
| kl | Greenlandic | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| kn | Kannada | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 5 | too few references (6/10 in range) | CER 0.47 WER 1.00 | unknown |
| ko | Korean | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.95 WER 1.09 | unknown |
| kok | Konkani | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ku | Kurdish | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ky | Kyrgyz | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/4 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| la | Latin | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (5/5 in range) | CER 0.32 WER 0.84 | unknown |
| lb | Luxembourgish | espeak | 2 engine-verified | pass (0 / 0 / 97 %) | 2 | too few references (2/4 in range) | CER 0.78 WER 1.41 | unknown |
| lfn | Lingua Franca Nova | espeak | 1 draft | FAIL (0 / 0 / 90 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) | phoneme values |
| lij | Ligurian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| lt | Lithuanian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 6 | too few references (6/10 in range) | CER 0.43 WER 1.00 | unknown |
| ltg | Latgalian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| lv | Latvian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.56 WER 1.00 | unknown |
| mi | Māori | espeak | 2 engine-verified | pass (0 / 0 / 95 %) | 2 | too few references (4/5 in range) | CER 0.36 WER 0.89 | unknown |
| mk | Macedonian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (5/5 in range) | CER 0.26 WER 0.73 | unknown |
| ml | Malayalam | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (3/5 in range) | CER 1.00 WER 1.57 | unknown |
| mn | Mongolian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.70 WER 1.15 | unknown |
| mn-f | Ankhmaa | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.69 WER 1.20 | unknown |
| mr | Marathi | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.60 WER 1.19 | unknown |
| ms | Malay | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.46 WER 0.75 | unknown |
| mt | Maltese | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.66 WER 1.20 | unknown |
| mto | Totontepec Mixe | espeak | 2 engine-verified | pass (0 / 0 / 96 %) | 2 | no reference | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| my | Myanmar (Burmese) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 1.09 | stress-or-tone |
| nb | Norwegian Bokmål | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (2/10 in range) | CER 0.63 WER 1.11 | unknown |
| nci | Nahuatl (Classical) | espeak | 2 engine-verified | pass (0 / 0 / 96 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ne | Nepali | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.66 WER 1.12 | unknown |
| nl | Dutch | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (1/5 in range) | CER 0.54 WER 1.02 | unknown |
| nl-be | Dutch (Southern Standard, Flanders) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (1/5 in range) | CER 0.65 WER 1.37 | unknown |
| nog | Nogai | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (5/12 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| om | Oromo | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| or | Oriya | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pa | Punjabi | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (2/5 in range) | CER 0.86 WER 1.09 | stress-or-tone |
| pap | Papiamento | espeak | 2 engine-verified | pass (0 / 0 / 95 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pdc | Pennsylvania Dutch (Lancaster) | espeak | 2 engine-verified | pass (0 / 0 / 95 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pdc-x-lehigh | Pennsylvania Dutch (Lehigh) | espeak | 2 engine-verified | pass (0 / 0 / 95 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| pdc-x-midwest | Pennsylvania Dutch (Midwest) | espeak | 2 engine-verified | pass (0 / 0 / 95 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| piqd | Klingon | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (1/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| plpl | Polish (experimental) | native | 2 engine-verified | pass (0 / 0 / 98 %) | 11 | no reference | CER 0.08 WER 0.29 |  |
| ps | Pashto | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.73 WER 1.09 | unknown |
| ps-x-northwest | Pashto (Northwestern) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.73 WER 1.09 | unknown |
| ps-x-southeast | Pashto (Southeastern) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.77 WER 1.12 | unknown |
| ps-x-yusufzai | Pashto (Yusufzai) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.73 WER 1.09 | unknown |
| pt | Portuguese (Portugal) | espeak | 2 engine-verified | pass (0 / 0 / 93 %) | 2 | FAIL 13/24 | CER 0.15 WER 0.34 | phoneme values |
| pt-br | Portuguese (Brazil) | espeak | 2 engine-verified | pass (0 / 0 / 90 %) | 2 | FAIL 16/27 | CER 0.11 WER 0.21 | phoneme values |
| py | Pyash | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| qdb | Lang Belta | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| qu | Quechua | espeak | 1 draft | FAIL (0 / 0 / 90 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) | phoneme values |
| quc | K'iche' | espeak | 2 engine-verified | pass (0 / 0 / 90 %) | 4 | too few references (6/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| qya | Quenya | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| ro | Romanian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | CER 0.23 WER 0.54 | unknown |
| ru | Russian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (5/12 in range) | CER 0.76 WER 0.91 | unknown |
| ru-cl | Russian (Classic) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (5/12 in range) | CER 0.75 WER 0.98 | unknown |
| ru-lv | Russian (Latvia) | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 4 | too few references (5/12 in range) | CER 0.49 WER 0.83 | unknown |
| rup | Aromanian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (4/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| sd | Sindhi | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 1.41 WER 1.67 | unknown |
| shn | Shan (Tai Yai) | espeak | 2 engine-verified | pass (0 / 0 / 92 %) | 4 | too few references (2/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| si | Sinhala | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.98 WER 1.05 | unknown |
| sjn | Sindarin | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| sk | Slovak | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.44 WER 0.67 | unknown |
| sl | Slovenian | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | CER 0.35 WER 0.85 | unknown |
| smj | Lule Saami | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 4 | too few references (6/10 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| sq | Albanian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (5/5 in range) | CER 0.40 WER 0.86 | unknown |
| sr | Serbian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 3 | too few references (5/5 in range) | CER 0.22 WER 0.51 | unknown |
| sv | Swedish | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 4 | too few references (2/10 in range) | CER 0.49 WER 0.87 | unknown |
| sw | Swahili | espeak | 2 engine-verified | pass (0 / 0 / 90 %) | 2 | too few references (3/5 in range) | CER 0.41 WER 1.00 | unknown |
| ta | Tamil | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 5 | too few references (6/10 in range) | CER 0.85 WER 1.00 | unknown |
| te | Telugu | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.65 WER 1.08 | unknown |
| th | Thai | espeak | 2 engine-verified | pass (0 / 0 / 96 %) | 2 | too few references (3/5 in range) | CER 1.27 | unknown |
| ti | Tigrinya | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| tk | Turkmen | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.84 WER 1.67 | unknown |
| tn | Setswana | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| tr | Turkish | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 2 | too few references (2/5 in range) | CER 0.78 WER 0.98 | unknown |
| tt | Tatar | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 0.56 WER 1.11 | unknown |
| ug | Uyghur | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| uk | Ukrainian | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 0.29 WER 0.77 | unknown |
| ur | Urdu | espeak | 2 engine-verified | pass (0 / 0 / 99 %) | 3 | too few references (3/5 in range) | CER 0.73 WER 1.10 | unknown |
| uz | Uzbek | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/5 in range) | CER 0.61 WER 1.31 | unknown |
| vi | Vietnamese (Northern) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 1.42 WER 1.47 | stress-or-tone |
| vi-vn-x-central | Vietnamese (Central) | espeak | 2 engine-verified | pass (0 / 0 / 97 %) | 2 | too few references (2/5 in range) | CER 1.46 WER 1.47 | stress-or-tone |
| vi-vn-x-south | Vietnamese (Southern) | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (2/5 in range) | CER 1.55 WER 1.56 | stress-or-tone |
| xex | xextan-test | espeak | 2 engine-verified | pass (0 / 0 / 100 %) | 2 | too few references (3/6 in range) | ASR unavailable (Whisper large-v3 has no language for this tag) |  |
| yue | Chinese (Cantonese) | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 4 | too few references (2/10 in range) | CER 1.31 | stress-or-tone |
| yue-latn-jyutping | Chinese (Cantonese, latin as Jyutping) | espeak | 2 engine-verified | pass (0 / 0 / 98 %) | 2 | too few references (1/5 in range) | ASR unavailable (Whisper writes another script; references not converted yet) |  |

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

## Phase 7 (2026-10-11): the authenticity pipeline, shown on Scottish English

No language's level changed. `en-gb-scotland` stays at level 2 (check B fails against references for other varieties; ASR CER 0.13). What it gained: authenticity metadata that passes the validator (variety, region, speaker group, sources `scobbie1999` and `cmu_arctic`, recordings `cmu_arctic/awb`, date, status); 10 measured vowel overrides (formants and lengths) from one Scottish speaker, **proposed, not applied** (the human's choice), which bring the engine's vowels to within 0.6 per cent (median) of the measured formant targets; and a native review packet, `review_packets/en-gb-scotland/index.html` (86 items, the A/B blind), waiting for a reviewer. Nothing is called authentic: level 5 needs a named native reviewer's sign-off, recorded by `engine/review/ingest_feedback.py` in the "Native-speaker sign-offs" section. 25 dialect packs fail the validator for missing metadata (`OPEN_QUESTIONS.md` Q41).
