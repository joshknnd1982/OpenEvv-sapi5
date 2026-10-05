# Decisions

Dated design decisions, newest last. An intentional change to what the engine says is recorded here before it is committed (R8).

## 2026-10-05 (Phase 0)

**D1. Baseline.** Tag `tts-ext-baseline` is commit `10542ae` on `main` (release 1.2.4 plus the licence commits). Work happens on `tts-ext/phase-N` branches. Nothing is pushed unless the human asks.

**D2. Builds that prove the toolchain must not touch tracked files.** The wrapper is built with plain `cmake` into the git-ignored `build_x64`/`build_x86`. Engine modules are built with `engine/build_modules.sh` into `%LOCALAPPDATA%\OpenEvvBuild-ttsext`, a work folder of this project's own, so that the maintainer's release cache (`%LOCALAPPDATA%\OpenEvvBuild`) and the DLLs in `languages/` are left alone. `build_all.bat`, `engine\build_modules.cmd` and `build_all.bat packs` overwrite tracked files and were not run.

**D3. How the checklist counts.** One entry for every representation the chart prints: 175. Where the chart prints the same thing twice (a tone as diacritic and as tone letter, ring above and below, tie bar above and below) each form is an entry, linked by `equivalent_to`, because each is a different input the engine must accept: 163 distinct things. The chart's example ejectives (pʼ tʼ kʼ sʼ) and example diacritic combinations are not entries; the ejective mark is one entry.

**D4. A symbol's stable id is its codepoints** (`U+0288`, or `U+02E9+U+02E5` for a sequence). Codepoints never change; names and numbers have typos and variants across sources.

**D5. What "engine today" means in the checklist.** It is read from code and from the packs' maps only: `already` (one of the seven IBM modules whose phones have an IPA value in `engine/espeak_phonemes.py` has the sound as a phone of its own; frca, jajp and plpl have no such table and were not consulted, so the column can under-report but not over-report), `partly` (said as another phone, reshaped or not; or a mechanism that covers some cases), `absent`, `unknown`. It is a statement of what the engine attempts, not of whether it is right; nothing was measured in Phase 0.

**D6. A correlate stated from memory is tagged `recalled-unverified`** in the research files and the checklist. It is not one of the playbook's provenance tags on purpose: it marks text that must be looked up before any number is taken from it, and any value derived from it enters the master table as `estimated`.

**D7. The official chart PDF is not copied into the repository.** It is CC BY-SA; the project is MIT. It is cited by URL, issue and SHA-256 of the human's copy.

**D8. The research helpers' raw files are kept** (`inventory/research/*.json`, with the brief they were given), because they hold the per-claim sources and the list of what could not be verified. The checklist is generated from them and is never edited by hand.
