# Project state

Read this at the start of every session, after Part 1 of `TTS_EXTENSION_PLAYBOOK.md` and your phase section.

## Phase

**Phase 0 (Orientation and safety net): complete, 2026-10-05.** Next: **Phase 1, Headless rendering and measurement harness** (Opus 5.5, effort high, permission Auto), on a new branch `tts-ext/phase-1` made from `tts-ext/phase-0`.

BLOCKED symbols: none (nothing has been mapped yet; all 175 checklist entries are `MISSING`, as they must be before Phase 4).

## What Phase 0 did

- Tagged the start: `tts-ext-baseline` = `10542ae` (main, release 1.2.4). Branch `tts-ext/phase-0`. No engine file was changed; nothing was deleted; nothing was pushed.
- `ARCHITECTURE_MAP.md`: what the engine is (a hybrid whose every sounding part is parametric: IBM's rule machine and a Klatt formant synthesiser, an accent layer on its frames, eSpeak NG for reading text), the 62-word frame, how phonemes and languages are defined, how the 155 languages were added, the tests, 21 gaps (each confirmed by code or suspected), 10 rewrite candidates.
- Built and ran from the command line (outputs below).
- Root `CLAUDE.md` (53 lines).
- `inventory/languages.json`: all 162 pack folders = 155 languages (10 native, 145 read by eSpeak NG) + 7 hidden template modules, with every phoneme each declares or maps.
- `inventory/IPA_CHECKLIST.md` and `.json`: the whole official chart, researched by seven helpers with web sources, **175 entries (163 distinct)**, checked symbol by symbol against the human's own PDF of the chart and against Unicode. For each: codepoints, names, definition, expected acoustic correlates with sources, and what the engine does today (read from code and pack data, not measured).
- Skeletons: `DECISIONS.md` (8 decisions), `REFERENCES.md`, `OPEN_QUESTIONS.md`, `LANGUAGE_STATUS.md`, `CREATED_SOUNDS.md`. `DESIGN.md` belongs to Phase 2 and does not exist yet.

**Not done:** `.claude/settings.json` (step 4b). The app refused to let Claude write its own permission settings. The proposed content is in `OPEN_QUESTIONS.md` Q1 for the human to create or approve.

## The checklist in numbers

| Section | Entries | already | partly | absent | unknown |
|---|---|---|---|---|---|
| Consonants (pulmonic) | 59 | 30 | 29 | 0 | 0 |
| Consonants (non-pulmonic) | 11 | 0 | 11 | 0 | 0 |
| Other symbols | 12 | 2 | 7 | 3 | 0 |
| Vowels | 28 | 19 | 9 | 0 | 0 |
| Diacritics | 32 | 0 | 21 | 11 | 0 |
| Suprasegmentals | 9 | 3 | 4 | 1 | 1 |
| Tones and word accents | 24 | 0 | 22 | 2 | 0 |
| **All** | **175** | **54** | **103** | **17** | **1** |

"already" = an IBM module has the sound as a phone of its own; "partly" = said as another phone, reshaped or not, or a mechanism that covers some cases; see `DECISIONS.md` D5. Of the 477 acoustic correlates recorded, 348 come from a source a helper opened and 129 are from memory and tagged `recalled-unverified`.

## Environment

- Windows 11 Home 10.0.26300, 64-bit. Repository at `C:\Users\joshk\OneDrive\dev\espeakproject\OpenEvv-sapi5` (inside a OneDrive folder: tests write outside the tree for that reason).
- Visual Studio 2022 Build Tools 17.14 (MSVC x86 + x64), CMake, Python 3.10 64-bit, MSYS2 at `C:\msys64` (make, python3, both mingw-w64 GCCs), Inno Setup 6. Ninja and bash are not on PATH.
- Public integration interface: SAPI 5 (COM). Lower interface: IBM's ECI API on each module DLL.
- Engine output: 16-bit mono PCM, 11025 Hz by default; 200 frames a second.
- eSpeak NG data in `dist/espeak-ng-data` is from `joshknnd1982/espeak-ng` at tag `openevv-1.2.0`.

## Commands that were run, and what they printed (2026-10-05)

Wrapper, 64-bit and 32-bit:

    cmake -G "Visual Studio 17 2022" -A x64 -S . -B build_x64      -> configure exit: 0
    cmake --build build_x64 --config Release                         -> build exit: 0
        OpenEvvSAPI.dll 445952  OpenEvvHost.exe 337408  OpenEvvConfig.exe 535040  evv_say.exe 385024  sapi_test.exe 448512 ...
    cmake -G "Visual Studio 17 2022" -A Win32 -S . -B build_x86 ; cmake --build build_x86 --config Release
        -> configure exit: 0, build exit: 0

Engine modules from source (MSYS2 GCC, outside the repository):

    engine/build_modules.sh with TAGS='enus dedx', OPENEVV_WORK=%LOCALAPPDATA%\OpenEvvBuild-ttsext
        === enus built in 250 s
        clone: lang/dedx made from lang/dede, 1 rule files of ours, 0 edits
        === dedx built in 174 s
        exit: 0   (openevv-enus-x64.dll 9867960, openevv-enus-x86.dll 7869098, openevv-dedx-x64.dll 7970515, openevv-dedx-x86.dll 6305728)

Speaking from the command line, with the modules shipped in `languages/`:

    evv_say.exe enus 1 "The quick brown fox jumps over the lazy dog." enus.wav 64
        enus: 34045 samples at 11025 Hz, first audio 165.5 ms, 183.6 ms in all
    evv_say.exe hi 1 "नमस्ते दुनिया" hi.wav 64
        hi: 11451 samples at 11025 Hz, first audio 69.4 ms, 70.8 ms in all
    evv_say.exe (32-bit) enus 1 <same sentence> enus32.wav 32
        enus: 34045 samples at 11025 Hz      (the 32-bit and 64-bit WAV files have the same SHA-256, EEE4CA40D578ADD1...)

The existing SAPI test suite on the unchanged engine (the baseline before any change):

    build_x64\bin\Release\sapi_test.exe --out %TEMP%\OpenEvvTests\ttsext_phase0_x64
        72 passed, 0 failed      exit: 0

The front-end, asked what it tells the engine for two Hindi words with retroflex stops:

    dist\x64\OpenEvvFrontend.exe --data dist\espeak-ng-data --voice inc/hi --map languages\hi\sounds.map --text "टमाटर ठंडा"
        {A v=1 f0=own range=90 shape=1 ...}{D s71 f2=91 f3=79 f4=88 a4=52 a5=42 vot=9} ... {W .0 t=s71 @=s1^- .1 m a=s50^- .0 t=s71 @=s1^- l=s2}`[.0t@.1ma.0t@l] ...

Inventories:

    python docs\tts-extension\inventory\build_language_inventory.py
        "pack_folders": 162, "espeak": 145, "native": 10, "template": 7, "languages": 155
        "espeak_packs_by_template": dedx 87, esex 21, itix 16, engx 9, esux 7, frfx 3, enux 2
    python docs\tts-extension\inventory\build_ipa_checklist.py
        entries 175 = 59 pulmonic + 11 non_pulmonic + 12 other_symbols + 28 vowels + 32 diacritics + 9 suprasegmentals + 24 tones
        equivalent pairs 12, distinct 163; letters 107, marks 68
        engine today: {'already': 54, 'partly': 103, 'absent': 17, 'unknown': 1}
        acoustic correlates by provenance: {'literature': 348, 'recalled-unverified': 129}
        references: 112 opened, 4 named but not opened
        agrees with the PDF and with Unicode: yes

Not run: `build_all.bat`, `engine\build_modules.cmd`, the front-end build, the installer, openevv's `test/matrix.sh` (see `DECISIONS.md` D2 and `OPEN_QUESTIONS.md`).

## Licence and origin of the engine (R4: flagged, not blocking)

The engine is IBM's Embedded ViaVoice (Eloquence) rebuilt as C from its 1999 Windows objects, that is, reverse-engineered. Its authors' code is MIT. **The language data in every module is IBM's and is licensed to no one here**; who holds those rights today is in litigation (Cerence v. Microsoft and Nuance, D. Del. 1:25-cv-00553). eSpeak NG and everything derived from its phoneme tables (the front-end, its data, the packs' maps) are GPL v3 or later. The wrapper is MIT. `NOTICE.md` is the authoritative statement. For this project: new sound definitions should live in files of our own; nothing GPL or ShareAlike may be pasted into MIT files.

## Things the next phase must know

1. **There is no way to hand the product an IPA string today** (`ARCHITECTURE_MAP.md` section 4). The harness needs its own path in: the front-end's `--phonemes` option (eSpeak NG phoneme names, command line only), engine annotations through `evv_say` with `Annotations=1` in a settings file named by `OPENEVV_SETTINGS`, or the modules' `evv-<tag>.exe -A`.
2. **Every frame the synthesiser receives can be logged** with `EVV_KLATT_TAP=file` (62 integers a frame, after the accent layer), and what each phone was meant to be with `EVV_ACCENT_TRACE=file`. That is "check A" (did the engine realize the requested parameters) almost for free.
3. `evv_say` reads the user's real settings unless `OPENEVV_SETTINGS` and `OPENEVV_DATA` point elsewhere; a harness must set both, as `sapi_test` does.
4. The engine's second utterance on one instance differs from its first, by design. Render each regression case with the same history.
5. The DLLs built from source today differ in bytes from the ones in `languages/`. Compare their audio before trusting either as the golden reference.
6. Another Claude session may share this working tree (the maintainer releases from it). Check `git log -3` and `git status -sb` before every commit, and commit by path.
7. This project's scratch build folder is `%LOCALAPPDATA%\OpenEvvBuild-ttsext`; `build_x64` and `build_x86` in the repository are git-ignored.

## Open questions

See `OPEN_QUESTIONS.md`. One needs the human: Q1 (the permissions file).
