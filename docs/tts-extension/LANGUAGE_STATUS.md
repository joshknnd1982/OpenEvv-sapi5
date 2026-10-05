# Language status

Status level and failure-layer triage for every language, dialect and accent (playbook 1.5). **Skeleton: Phase 1 fills in the baseline for all existing languages.**

Levels: 1 `draft` · 2 `engine-verified` (the harness shows the engine realizes the requested parameters) · 3 `reference-verified` (realized values fall within reference ranges) · 4 `intelligibility-verified` (speech-recognition round trip passes, where a recognizer supports the language) · 5 `native-validated` (a named native speaker or expert signed off the review packet). Only level 5 may be called "authentic".

## Where things stand on 2026-10-05 (end of Phase 0)

Nothing has been measured by this project yet, so **no language has a level**. What exists is an inventory, not a verdict: `inventory/languages.json`.

| Group | Count | Spoken by | Level | Note |
|---|---|---|---|---|
| Native modules lifted from IBM | 9 (enus, engb, dede, eses, esus, frfr, frca, itit, jajp) | their own module | not assessed | held by openevv's own 979-case hash gate (`openevv/test/matrix.sh`), not yet run on this machine |
| Polish (plpl) | 1 | its own module, begun as a copy of Italian | not assessed | marked experimental by its authors |
| Read by eSpeak NG | 145 | a template module: dedx 87, esex 21, itix 16, engx 9, esux 7, frfx 3, enux 2 | not assessed | 52 are marked experimental in `language.ini`; no golden audio regression exists for any of them |
| **Languages in all** | **155** | 17 modules (10 native + 7 hidden templates) | | |

## Per-language table (to be generated in Phase 1)

| Tag | Name | Kind | Template | Level | Failure layer | Evidence |
|---|---|---|---|---|---|---|
| | | | | | | |

Failure layers, for a language that does not pass: text analysis (G2P, numbers) · phoneme mapping (a phoneme dropped or substituted) · segment realization (formants, timing, noise) · prosody (stress, melody, tone) · engine capability missing.

## Native-speaker sign-offs

None yet.
