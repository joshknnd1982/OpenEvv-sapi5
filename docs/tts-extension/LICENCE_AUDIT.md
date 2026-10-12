# Licence audit (Phase 10, 2026-10-11)

Every file git tracks is in exactly one licence class, by a rule. `engine/check_licences.py` holds the rules and fails on a file no rule takes, on a rule that takes no file, and on a file outside the two MIT classes that says `SPDX-License-Identifier: MIT`. With `--headers` it also fails on a code file of this project's own with no SPDX line. Run it from the repository root:

    python engine\check_licences.py              the classes and their counts, and the checks
    python engine\check_licences.py --rules      every rule in order, with how many files it took
    python engine\check_licences.py --list gpl   the files of one class

The rules are tried in order and the first that matches decides, so the exceptions come before the folders they are in (the BestSpeech files before `src/**`, the two IBM tables before `openevv/**`). Packs are the one rule that reads content: a `pack.toml` holding `[sounds]` or `[phonemes]` carries lines written from eSpeak NG's phoneme tables and is GPL; a pack without them (the 17 module packs, `nl-be`, which holds only overrides of its own) is this project's.

**What "everything MIT" can and cannot mean.** Everything this project **wrote** is under the MIT licence (`LICENSE`), and so is upstream openevv's own code (`openevv/LICENSE`). The other classes below are other people's work, kept under their own terms; no file was relabelled, and none can be by this project. This is not legal advice.

## The classes

| Class | Licence | What is in it |
|---|---|---|
| `mit-here` | MIT, `LICENSE` (Copyright (c) 2026 Josh Kennedy) | the SAPI wrapper, host, OpenEVV Configuration and tools (`src/`, except the BestSpeech files); the build and installer scripts; `engine/` (pack loader, accent-layer generator, IPA tools, doctor, profiles, measurements of the modules); the harness, its results and goldens (measurements, not audio); the IPA master table and every proof (`ipa/`); the packs' own data (module packs, overrides, measured targets, review lists); the skills and agent (`.claude/`); the GitHub issue forms (`.github/`, since 1.4.0); every document, this playbook included; `languages/*/language.ini`; the built host and utility. Also this project's additions inside `openevv/` (the accent layer `openevv/src/accent/`, the recipes `openevv/accents/`, `openevv/tools/module/clone.py`), which carry openevv's MIT terms (NOTICE.md) |
| `mit-openevv` | MIT, `openevv/LICENSE` (Copyright (c) 2026 Stanislaw Przedzinkowski) | upstream openevv's engine, romanizers, tools, tests, reference build and documents; the two Polish rules upstream wrote |
| `ibm` | not licensed here | `openevv/lang/` (transcribed out of IBM's Embedded ViaVoice objects), `openevv/src/klatt/klatt_tables.c` and `openevv/src/eci/ssml/eci_xmltok_tables.c` (data lifted from IBM's objects), and every language module in `languages/` (IBM's data compiled with openevv, the seven templates with this project's accent layer included). `openevv/NOTICE` and `NOTICE.md` explain who may hold the rights; the question is before a court (Cerence v. Microsoft and Nuance, D. Del. 1:25-cv-00553) |
| `gpl` | GPL-3.0-or-later | `frontend/` and the built `OpenEvvFrontend.exe` (it links eSpeak NG); `dist/espeak-ng-data/`; every `sounds.map`, `phonemes.map` and `sample.txt` of a language read by eSpeak NG (written from eSpeak NG's phoneme tables; some sample sentences come from eSpeak NG's tests); the packs that hold those lines; `docs/tts-extension/harness/praat_crosscheck.py` (it imports Parselmouth, which contains Praat, GPL v3; D9) |
| `bestspeech` | the BestSpeech SAPI 5 wrapper's author's terms (Gozaltech) | the 13 files of `src/sapi/` listed in `NOTICE.md` |
| `mixed-binary` | MIT and the BestSpeech terms together | `dist/x64/OpenEvvSAPI.dll`, `dist/x86/OpenEvvSAPI.dll`, built from both |
| `rendered` | not MIT-licensed here | speech the engine rendered: `samples/*.wav` and the review packets' `index.html` (audio embedded) and `items.json`. It is IBM's language data at work, so it is kept beside the modules' terms rather than claimed; the packets' text is Common Voice's (CC0) or this project's word lists |
| `sentences` | Common Voice CC0 1.0 and Tatoeba CC BY 2.0 FR, per sentence | `harness/asr/sentences.json` (each sentence's source, and for Tatoeba its id and author, recorded; `REFERENCES.md`), and `results/asr.json`, `results/asr_espeak.json`, which quote the sentences beside the recogniser's transcripts |
| `cc0` | CC0 1.0 | `dictionaries/community/` (IBMTTSDictionaries, byte for byte) and its two copies in `dist/docs/` |
| `cc-by-sa` | CC BY-SA 4.0, International Phonetic Association | `IPA_Kiel.pdf` and the seven official sub-chart images in `docs/tts-extension/inventory/ipa_chart_images/`, unchanged; nothing of them is copied into an MIT file |
| `unicode` | Unicode License v3 | `docs/tts-extension/inventory/unicode/` (`UnicodeData.txt`, `Blocks.txt`, and the licence itself) |
| `cmu` | CMU's notice, `third_party/cmu_arctic/cmu_us_awb_arctic/COPYING` (free for any purpose, notice kept) | CMU ARCTIC speaker awb, unchanged |

**CC0 text inside MIT files.** Some files of this project quote Common Voice sentences (CC0 1.0): the review lists (`review.toml`) and the packets' forms (`feedback.toml`). CC0 waives every right, so such text may sit in an MIT file without changing what the file may be used for; these files stay `mit-here`. A Tatoeba sentence (CC BY 2.0 FR, attribution required) is quoted only in the files of the `sentences` class, where its id and author are kept.

## The result

The output of `python engine\check_licences.py` at the end of Phase 10 is in `PROJECT_STATE.md` (Phase 10 at its end), with the count of every class.

## Headers

Every code file of this project's own outside `openevv/` (`.py .cpp .h .sh .cmd .bat .iss .ps1`) carries `SPDX-License-Identifier: MIT` and `Copyright (c) 2026 Josh Kennedy` in its first lines, in the file's own comment style (added in Phase 10). No header was put on IBM's data, on GPL, BestSpeech-derived, CC or CMU files, or on anything under `openevv/`, whose own rules (`openevv/CLAUDE.md`) govern it; `praat_crosscheck.py` keeps its GPL header.

## What cannot be MIT, and why

- **IBM's language data and every module built from it.** The engine cannot speak without it. Neither this project nor openevv can license it; who holds the rights is unsettled. Removing it would stop every voice and would break the project's rule never to delete original engine data (R1).
- **eSpeak NG and what is written from it** (the front-end, its data, the maps and the packs that hold them). eSpeak NG is GPL v3 or later; anything derived from its tables stays GPL. Its complete source is at https://github.com/joshknnd1982/espeak-ng, tag `openevv-1.2.0` (checked with `git ls-remote` in Phase 10).
- **The BestSpeech-derived files** stay under their author's terms, and so does the SAPI DLL built from them.
- **Other people's data kept whole**: the community dictionary (CC0), the IPA chart (CC BY-SA 4.0), the Unicode files, CMU ARCTIC, the test sentences (CC0 and CC BY 2.0 FR) and the engine's rendered speech.

The options, for the maintainer: leave them under their own terms, as now (recommended); or ask each rights holder for another licence. Relabelling is not an option.
