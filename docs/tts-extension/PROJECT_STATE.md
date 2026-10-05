# Project state

Read this at the start of every session, after Part 1 of `TTS_EXTENSION_PLAYBOOK.md` and your phase section.

## Phase

**Phase 1 (Headless rendering and measurement harness): complete, 2026-10-05**, on branch `tts-ext/phase-1` (made from `tts-ext/phase-0`). Next: **Phase 2, Architecture design (human approves)**: Fable 5.1, effort xhigh, permission Accept edits, on a new branch `tts-ext/phase-2` made from `tts-ext/phase-1`. Phase 2 must stop if it is not on Fable 5.1 at xhigh.

Phase 0 complete, 2026-10-05 (commit `53a830d`).

BLOCKED symbols: none (nothing has been mapped yet; all 175 checklist entries are `MISSING`, as they must be before Phase 4).

## What Phase 1 did

A harness that replaces listening with measurement, in `docs/tts-extension/harness/` (its `README.md` has every command). Nothing in the engine, the product or the language data changed; nothing was deleted or pushed.

- **Render** (`engine.py` + `src/tools/evv_render.cpp`, a new tool): text, IPA, eSpeak NG phoneme names, a module's own annotation or the front-end's output in; a WAV plus JSON of every frame the synthesiser received and every phone the engine meant out. Optional `sounds.map` overrides. Each case in a host of its own; the engine's existing logs, no new hook. `evv_render`'s audio is byte-identical to `evv_say`'s (enus, hi).
- **Analyse** (`analysis.py`, numpy/scipy, MIT): formants (Burg LPC) and trajectories, F0 and tone contours, intensity, fricative moments and band edges, stop closure/burst/VOT, nasal antiformant and murmur, F3 minimum; and what the frames requested per phone.
- **Self-tests** (`selftest.py`): 72 of 72 pass: the analyser on synthetic signals with known answers, and every engine fact the harness relies on. Praat agrees on 24 of 24 comparisons (`praat_crosscheck.py`, the only GPL file).
- **Reference store** (`reference/ranges.json`, `reference.py`): 956 cited values from 14 opened sources (US English, German, Spanish, Portuguese, French, Dutch, Australian English vowels; VOT; English fricatives; nasals; /ɹ/; Mandarin tones). Values not found are absent. Check B uses the vowel formants (and /ɹ/'s) and the general nasal ranges; it cannot use the VOT or fricative values (means without a spread, so no range) or the tone values (no tone cases until Phase 4).
- **ASR round trip** (`asr.py`): Whisper large-v3 on the GPU; sentences from Common Voice (CC0) and Tatoeba (CC BY 2.0 FR), 142 languages. 105 scored, 50 unavailable (reasons recorded).
- **Golden regression** (`golden.py`, `golden/*.json.gz`): every phoneme every pack maps (borrowed ones too) and every native phone, 16,472 cases, metrics and hashes, not audio; fails loudly on drift, in the frames or in the sound (proven by a planted change); 15 entries it cannot render are listed, not dropped.
- **Report** (`report.py`): `LANGUAGE_STATUS.md` baseline for all 155 languages and `reports/index.html` (tables, spectrograms with requested vs measured formants, vowel charts against references).
- **Smoke check** (`smoke.py`, 6 s with facts cached) and a Stop hook script (`stop_hook.py`), not installed: `OPEN_QUESTIONS.md` Q5.
- An independent review of the diff (R15) found nine problems; the real ones were fixed (D20), among them a VOT measurement bug and a golden that could not see synthesiser changes. The one re-review R15 allows found the VOT fix incomplete and two doc claims still wrong; fixed (D21).
- Decisions D9 to D21 in `DECISIONS.md`; Phase 1 sources and licences in `REFERENCES.md`; Q5 to Q7 and two measured findings in `OPEN_QUESTIONS.md`.

## Phase 1 results in numbers (preset 1, 64-bit, 11025 Hz)

| | |
|---|---|
| Level 1 draft | 1 (qu: a vowel the engine meant, made silent) |
| Level 2 engine-verified | 150 |
| Level 4 intelligibility-verified | 4 (enus, en-us-nyc, pt, pt-br) |
| Check A (engine fidelity) | 154 of 155 pass; no substitution anywhere (A0) |
| Check B (reference ranges) | 14 languages have enough references: 4 pass, 10 fail; 137 too few (nasals only), 4 none |
| ASR | 105 scored (median CER 0.33; 25 at or under 0.15), 50 unavailable |
| Golden | 155 packs, 16,472 cases, recorded and re-run: 0 failed, every frame and every sound identical |

Findings (measured, not fixed): nine native modules speak the accent markup instead of reading it (D13); the host's 1.5 s grace sometimes kills a host before it flushes its logs (D14); IPA tone letters and phones named with `:`/`~` cannot be given to the engine directly yet (harness README, "Known limits").

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

- Harness Python: venv at `%USERPROFILE%\OpenEvvBuild-ttsext\venv` (Python 3.10.11; numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.9, jiwer 4.0.0, soundfile 0.14.0, praat-parselmouth 0.4.7, faster-whisper 1.2.1, ctranslate2 4.8.2, nvidia-cublas-cu12 12.8.4.1). Not under `%LOCALAPPDATA%`: a folder the Claude app creates there is redirected into `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\` (a first venv landed there; it is unused).
- Whisper model: `%USERPROFILE%\OpenEvvBuild-ttsext\models\faster-whisper-large-v3` (3.09 GB).
- Hardware: AMD Ryzen 7 260 (8 cores, 16 threads), 31.3 GB RAM, NVIDIA GeForce RTX 5060 Laptop GPU (8 GB, compute capability 12.0, driver 572.97). Whisper runs on it in float16.
- Harness scratch: `%TEMP%\OpenEvvTests\harness` (outside OneDrive).

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

### Phase 1 (2026-10-05), venv python, `PYTHONUTF8=1`, from the repository root

    cmake --build build_x64 --config Release --target evv_render
        evv_render.vcxproj -> ...\build_x64\bin\Release\evv_render.exe
    evv_render vs evv_say, first case, SHA-256 of the WAV:
        say_en.wav 241135d6327dad97  en/a.wav 241135d6327dad97   say_hi.wav 9f2b8cdce8bcaee5  hi/a.wav 9f2b8cdce8bcaee5
    python docs/tts-extension/harness/selftest.py
        == 72 checks, 72 passed, 0 failed          exit 0   (after the review's fixes)
    python docs/tts-extension/harness/praat_crosscheck.py
        == 24 compared, 24 agree within 5 % (F1 60 Hz), 0 differ
    python docs/tts-extension/harness/golden.py --record
        recorded 155 packs in 562 s; 0 not recorded   (then enus engb dede eses esus frfr frca itit jajp plpl again
        with the vowel frame of D17: recorded 10 packs, 0 not recorded; frca plpl jajp once more for their classes)
    python docs/tts-extension/harness/golden.py
        golden: 155 packs, 13766 cases, 0 FAILED, 0 changed within tolerance, 632 s     exit 0   (before the review)
    after the review's fixes (D20), golden.py --record, then golden.py:
        recorded 155 packs in 795 s; 0 not recorded
        golden: 155 packs, 16472 cases, 0 FAILED, 0 changed within tolerance, 882 s     exit 0
    after the re-review's fixes (D21), the final baseline, golden.py --record, then golden.py:
        recorded 155 packs in 1123 s; 0 not recorded
        golden: 155 packs, 16472 cases, 0 FAILED, 0 changed within tolerance, 1216 s    exit 0
    voiceless stops /p t k c q/ in the golden: 909 cases, 2 with a negative VOT (hyw /p t/, which its map
    sends to the module's b and d: OPEN_QUESTIONS.md), 13 with no burst found (no VOT reported)
    python docs/tts-extension/harness/golden.py enus engb dede eses esus frfr frca itit jajp plpl   (after the last re-record)
        golden: 10 packs, 416 cases, 0 FAILED, 0 changed within tolerance, 18 s
    python docs/tts-extension/harness/smoke.py
        selftest --quick: exit 0 (60 checks, 60 passed); golden --smoke: 6 packs, 28 cases, 0 FAILED; smoke: passed in 7 s
    python docs/tts-extension/harness/asr.py     (then asr.py sr, after the Serbian transliteration)
        asr: 155 languages, 105 scored, 50 unavailable
    python docs/tts-extension/harness/report.py
        levels: 1 draft: 1, 2 engine-verified: 150, 4 intelligibility-verified: 4
        check A pass: 154 of 155
        check B: pass 4, fail 10, too few references 137, no reference 4
        failure layers: {'unknown': 72, 'stress-or-tone': 8, 'phoneme values': 11}

## Licence and origin of the engine (R4: flagged, not blocking)

The engine is IBM's Embedded ViaVoice (Eloquence) rebuilt as C from its 1999 Windows objects, that is, reverse-engineered. Its authors' code is MIT. **The language data in every module is IBM's and is licensed to no one here**; who holds those rights today is in litigation (Cerence v. Microsoft and Nuance, D. Del. 1:25-cv-00553). eSpeak NG and everything derived from its phoneme tables (the front-end, its data, the packs' maps) are GPL v3 or later. The wrapper is MIT. `NOTICE.md` is the authoritative statement. For this project: new sound definitions should live in files of our own; nothing GPL or ShareAlike may be pasted into MIT files.

## Things the next phase must know

1. **Measure with the harness, not by ear.** One render: `python docs/tts-extension/harness/engine.py <tag> ipa "<IPA>" out.wav` (venv python, `PYTHONUTF8=1`, from the repository root). Before committing anything that touches synthesis or data: `golden.py` (about 10 minutes, must say `0 FAILED`); after any such edit: `smoke.py`. An intended change: `golden.py --record <tags>` and a line in DECISIONS.md.
2. **Renders depend on history**: every case is spoken in a host of its own on purpose (D11). IPA and phoneme input give the product's frames but not its noise samples (D12).
3. **The native modules other than enus do not know the accent layer's markup** (D13, `OPEN_QUESTIONS.md` Q6). Giving native languages new sounds through the accent layer would mean rebuilding them, which overwrites `languages/`.
4. **Check B is thin**: vowel references exist for a handful of languages. Most of the "level 2" languages are there for lack of references, not because they failed anything.
5. **No way in for IPA tone letters, or for the module phones named with `:` or `~`**, yet; Phase 3/4 territory.
6. The DLLs built from source in Phase 0 (`%LOCALAPPDATA%\OpenEvvBuild-ttsext`) have still not been compared with the shipped ones; the golden is of the **shipped** DLLs in `languages/`. Compare by pointing a copy of `languages/` at the built DLLs and running `golden.py`.
7. Another Claude session may share this working tree. Check `git log -3` and `git status -sb` before every commit, and commit by path.
8. This project's scratch build folder is `%LOCALAPPDATA%\OpenEvvBuild-ttsext`; `build_x64` and `build_x86` in the repository are git-ignored. `build_x64` now also holds `evv_render.exe` (`cmake --build build_x64 --config Release`).

## Open questions

See `OPEN_QUESTIONS.md`. For the human: Q1 (the permissions file), Q5 (the Stop hook), Q6 (rebuilding native modules: Phase 2 decides), Q7 (ASR for the 46 languages Whisper lacks), and Q2 to Q4 from Phase 0.
