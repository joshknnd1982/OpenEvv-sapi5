# Project state

Read this at the start of every session, after Part 1 of `TTS_EXTENSION_PLAYBOOK.md` and your phase section.

## Phase

**Phase 3 (Engine capability extensions), part 3A: IN PROGRESS** on branch `tts-ext/phase-3` (made from `tts-ext/phase-2`). Session of 2026-10-05/06: Opus 5.5. The fix is commit `428faa0`; see `git log` for what came after.

**The defect fixes X-1 and X-2 are approved** (the human, 2026-10-06, `DECISIONS.md` D43). They live in the staged modules: committed in `openevv/src/accent/evv_accent.c` (`428faa0`), but nothing in `languages/` has changed. Replacing the 14 template module files there is a separate step, shown to the human and done only with their say-so (D34 answer 4).

### Part 3A: where it stands

| Step (`DESIGN.md` 13.2, D35) | State |
|---|---|
| (a) rebuild the seven templates from unchanged source, prove the golden identical | **done** (D39): 29,237 of 29,237 cases identical in frames and sound |
| (b) try `openevv/test/matrix.sh` under MSYS2 | **done** (D37, D42): runs with `probe.exe`, `RULES=c`, one language a probe; 979 of 979 as they were on the fixed source. Not tried: `RULES=bytecode`, `probe`, `probe32` |
| (c) fix X-1, then X-2, with check A3 and the word-final and cluster golden cases; show the human what moved | **done and approved** (D38, D38a, D40, D41, D43) |
| (d) C1 to C4 and the new harness measures | **in progress (session of 2026-10-06).** **C1** front-end and host: done, `0b809c0`, D44. C1 accent layer (`openevv/src/accent/evv_accent.c`, not yet committed): built into `build3c1\modules`, staged in `%USERPROFILE%\OpenEvvBuild-ttsext\stage-c1` (with the C1 front-end in `x64\`); `diag.py --plant-accent` 18 of 18 reported on stage-c1, 0 of 18 on the old stage (the new code ran). Running when this was written: the staged golden on stage-c1 (log `golden_c1.log`; must say 0 FAILED against `golden-staged/`; it also writes `harness/results/diag-golden-staged.json`, the accent layer's baseline count) and the engine gate (`matrix_c1.log`; must say 10 languages, 0 failed). Then: commit the layer, `golden.py` change and results as D46; make stage-c1 the stage. **C2** reader: done, `3b65642`, D45 (the serving front-end's IPA request moved to C4). **C3**: done for its test, `3b65642`, `3592b4e`, `f415d0e`, D45, D47 (/i/ and /ʃ/ pass; /t/ cannot: `vot` cannot shorten, Q13). **C4** not started: modifier lines from the adapter, the front-end's lookup exact → composed → nearest with a warning, behind a version line in the map; the raised limits (384 definitions, 1,024-byte lines, 48-byte keys); the IPA request to the serving front-end; test: front-end composition equals adapter composition on a sample, each fallback warns. **New harness measures** of `DESIGN.md` 10.2 (T-tap/trill, T-click, T-airstream, T-phonation, T-nasality, comparisons): not started. |
| (e) template comparison, with the defect fixed; choose the reference template | not started |
| then: the R15 review of the whole of 3A, and the pause protocol | |

Small items queued for 3A: Q12 (make a template buildable without its parent, in `engine/build_modules.sh`); `docs/SOUNDS.md` must say how `vot` and `brth` now behave and document the tone key `av`, at the point the fixed modules replace the shipped ones (not before: it describes the shipped product).

### How to work in 3A (learned in this session)

- Build: `%USERPROFILE%\OpenEvvBuild-ttsext\build_in_place.sh <work copy> <out folder> <tags>` (run with MSYS2 `bash -l`): the loop of `engine/build_modules.sh` without its refresh of the copy. Work copy: `%USERPROFILE%\OpenEvvBuild-ttsext\build3a\openevv`, whose `src/` equals the repository's (fixed) `openevv/src`; copy a changed source file in by hand and check with `diff -rq --strip-trailing-cr openevv/src <work>/src`. Seven templates: 20 to 25 minutes. Latest fixed build: `...\build3z\modules`.
- Stage: `python docs/tts-extension/harness/stage.py <out folder> %USERPROFILE%\OpenEvvBuild-ttsext\stage` (the fixed modules; `stage-base` holds the unchanged rebuild). Measure with `EVV_STAGE=C:\Users\joshk\OpenEvvBuild-ttsext\stage`.
- Golden: `golden/` = the shipped modules (29,237 cases); `golden-staged/` = the staged fixed modules (recorded at the end of this session; check that it is committed). A full run takes 50 to 75 minutes; `--only-missing-from <folder>` renders only cases that folder lacks. A3: `a3.py`, about 45 minutes for all packs.
- **Background jobs are stopped at 2 hours**, and a stop mid-run makes the last packs fail with "front-end failed" and no message: one long run per job. The engine gate: `%USERPROFILE%\OpenEvvBuild-ttsext\matrix_each.sh <work copy> c <langs>` (about 15 minutes for ten).
- Front-end: built from the tree into a scratch copy with `%USERPROFILE%\OpenEvvBuild-ttsext\fe\build_fe.cmd <copy>\frontend <build dir>` (a copy holding `frontend\` and `src\common\`, against eSpeak NG at `%LOCALAPPDATA%\OpenEvvBuild\dev\espeak-ng`, tag `openevv-1.2.0`; the release cache's own path to a checkout is stale). `fe\base-x64` = the unchanged front-end, `fe\new-x64` = with C1. The new one is staged as `stage\x64\OpenEvvFrontend.exe`, which `engine.py` uses under `EVV_STAGE`. `dist\` is untouched.
- Heredocs in the Bash tool collapse `\\` to `\`: write edit scripts with the file tool (this broke one edit, caught by the compiler).
- The harness's known flake (D14) happened once (`ru-cl`, "frame log cut short" in 5 attempts); a re-run of that pack passed.

**The human's answers in Phase 2** (D34): TOML; the standard pass marks; Southern American English first; module files in `languages/` may be rebuilt and replaced when proven, at stated points, the differences shown first; the defect fixed first thing in Phase 3.

Phase 2 complete and the design APPROVED, 2026-10-05 (commit `7713bfc`). Phase 1 complete, 2026-10-05 (`cdcd70f`). Phase 0 complete, 2026-10-05 (`53a830d`).

BLOCKED symbols: none (nothing has been mapped yet; all 175 checklist entries are `MISSING`, as they must be before Phase 4).

## What Phase 2 did

- Read the engine again for the design, with six research helpers (accent layer, synthesiser, front-end and pack generator, native modules, wrapper, and the web), and checked by hand the findings the design leans on. The findings are in `DESIGN.md` ("The facts this design rests on"); those that correct earlier documents are in `DECISIONS.md` D30 and `ARCHITECTURE_MAP.md` 13.
- **`DESIGN.md`**: scope tiers and the coverage metric; the sound model (features, composition, fallback with a warning); the master table's format; capability gaps; the USP in this design; the pack format (TOML) and inheritance; voice against language; G2P; prosody and timing; verification; migration; keep, extend or replace for every component, and what must not change; risks and changes proposed to the phase plan.
- **`design/TRACEABILITY.md`** (written by `design/build_traceability.py`): a decision for every one of the 175 checklist entries. 109 as-is, 50 composition, 16 new mechanism; meant to end 67 mapped, 53 composed, 55 created (by rule, a letter is `created` when none of the seven IBM modules the checklist read has it as a phone of its own). Plans, not results.
- The direction, in one line: **extend, do not rewrite.** The synthesiser and the modules stay; one engine-neutral table of sounds with provenance replaces the scattered tables; an adapter turns it into what this engine reads; two defects are fixed first; twelve capabilities are to be built (four foundations, five mechanisms, three only if a measurement fails without them); the module files in `languages/` are rebuilt only at stated points, after proof, with the human's say-so.
- An independent review of the diff (R15) found the defect above, a gap in the migration plan (no place for rebuilding the template modules) and smaller things; the one re-review R15 allows found the defect described too narrowly (the breathy-release key does it too; 61 of the 87 German-template packs, not all) and a few loose ends. All fixed in the design (D33).
- Decisions D22 to D35 in `DECISIONS.md`; the Phase 2 sources and licences in `REFERENCES.md`; Q8 to Q11 and a list for Phase 3 in `OPEN_QUESTIONS.md`; the register's rules in `CREATED_SOUNDS.md`.

### Phase 2 commands and what they printed (2026-10-05)

    python docs\tts-extension\design\build_traceability.py
        entries 175 = 59 pulmonic + 11 non_pulmonic + 12 other_symbols + 28 vowels + 32 diacritics + 9 suprasegmentals + 24 tones
        decision: {'as-is': 109, 'new mechanism': 16, 'composition': 50}
        meant to end as: {'mapped': 67, 'created': 55, 'composed': 53}
        needed by (to build): {'C5': 4, 'C6': 1, 'C7': 2, 'C8': 0, 'C9': 0, 'C10': 6, 'C11': 3, 'C12': 0}
        needed only if a measurement fails: {'C5': 6, 'C6': 9, 'C7': 0, 'C8': 6, 'C9': 5, 'C10': 2, 'C11': 2, 'C12': 2}
        orphans: 0; capabilities serving no symbol: 0; equivalent pairs decided alike: yes
    head size, harness render of enus `[.1tat] (mid voiced frame, F1-F5; B1; nasal pole):
        default (50): 750 1232 2440 3600 3900; 120; 200
        `vh0:         937 1540 3050 4500 4875; 120; 200      (x 1.25)
        `vh100:       562  924 1830 2700 2925; 120; 200      (x 0.75)
    quoted phone names, evv_render dede preset 1, Annotations=1 (samples):
        `[.1aEa] 8998    `[.1aE:a] 62051    `[.1a'E:'a] 9482    `[.1ta~t] 59609    `[.1t'a~'t] 9339
    the packs (counted from languages/*/sounds.map):
        145 files; accent line with f0=own: 145; f0= keys in sound lines: 196 in 145 packs
        packs with the line "ː -": 145; with "ʲ -": 145
    accent-layer strings (EVV_ACCENT_TRACE, {A v=1) in languages/*/openevv-*.dll:
        present in 15 of 34: enus x64, and x64 + x86 of dedx engx enux esex esux frfx itix
        absent in 19: enus x86, and x64 + x86 of dede engb eses esus frca frfr itit jajp plpl
    speech-recognition error by speaking module (from harness/results/status.json; median, lowest to highest, how many at or under 0.15):
        dedx n=61 0.46 0.18-1.63 0     esex n=12 0.20 0.06-1.22 4     itix n=11 0.17 0.08-0.56 5
        frfx n=3 0.40 0.25-0.40 0      engx n=6 0.06 0.03-0.66 5      enux n=1 0.05     esux n=1 0.06
        native: enus 0.01 engb 0.00 dede 0.03 eses 0.04 esus 0.03 itit 0.01 plpl 0.09 frfr 0.12 frca 0.14 jajp 0.15

    the defect (harness renders of text, shipped modules, preset 1; frames with voicing amplitude above zero, per phone):
        ru "кто."    k=s13[0/3]  t=s11[15/21]  o=s8[34/37]  #[12/92]        ro "pta."   p[0/3]  t[0/11]  a[41/41]  #[6/86]
        ru "псы."    p=s12[0/3]  s[25/27]  y=s46[32/33]  #[12/92]            ro "taxa."  t[0/3] a[19/20] k[4/17] s[0/18] a[25/25] #[6/86]
        ru "такса."  t=s11[0/4] a=s51[30/31] k=s13[5/18] s[11/17] a=s5[16/16] #[12/92]
        final pause, voiced frames and level against the loudest 20 ms:
        hi "आप." 92/92 -7.2 dB    ru "кот." 90/92 -6.6 dB    en-us-nyc "cat." 85/96 -7.5 dB
        hi "आपा." 12/92 -21.3 dB  ru "кота." 12/92 -18.7 dB  ro "pot." 0/90 -53.6 dB  id "tidak." 0/90 -38.2 dB
    the same with the product's evv_say.exe at default settings (last 300 ms against the loudest 20 ms):
        hi "आप." -7.1 dB   ru "кот." -6.4 dB   en-us-nyc "cat." -6.8 dB   hi "आपा.", ro "pot.", dede "Kot.": digital silence
        (with this machine's own settings, PauseMode=2, the final pause is cut from the file)
    the breathy-release key (hi; s70 has brth=90, s24 is plain d):
        "दूधसा."  d=s70[28/28]  s[voiced 17/20, friction 3/20]        "दूदसा."  d=s24[28/28]  s[voiced 0/20, friction 20/20]
        "दूध."    final pause voiced 17/83                            "दूद."    final pause voiced 0/83
        friction left in the s of ru "псы.": 4/27 frames (ro "taxa.": 18/18)
    sound definitions with a vot key: in 145 of 145 packs, 930 in all (dedx 542, esex 153, itix 130, esux 51, engx 21, enux 18, frfx 15)
    sound definitions with a brth key: 196, in 145 of 145 packs
    packs whose plain p, t and k all carry vot: dedx 61 of 87 (25 none, 1 two), enux 2 of 2, engx 1 of 9, esex 0 of 21, esux 0 of 7, itix 0 of 16, frfx 0 of 3
    tone lines with the unapplied key av: cmn 4, cmn-latn-pinyin 4

Not run in Phase 2: any build, the golden regression (nothing that it guards was touched), `openevv/test/matrix.sh`.

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
5. **No way in for IPA tone letters** yet (capability C2 of the design). The module phones named with `:` or `~` *can* be written, in single quotes (`'E:'`): Phase 2 measured it (D30); the harness does not do it yet.
6. The DLLs built from source in Phase 0 (`%LOCALAPPDATA%\OpenEvvBuild-ttsext`) have still not been compared with the shipped ones; the golden is of the **shipped** DLLs in `languages/`. Compare by pointing a copy of `languages/` at the built DLLs and running `golden.py`.
7. Another Claude session may share this working tree. Check `git log -3` and `git status -sb` before every commit, and commit by path.
8. This project's scratch build folder is `%LOCALAPPDATA%\OpenEvvBuild-ttsext`; `build_x64` and `build_x86` in the repository are git-ignored. `build_x64` now also holds `evv_render.exe` (`cmake --build build_x64 --config Release`).
9. **From Phase 2, for Phase 3.** Read `DESIGN.md` first: "A defect found on the way" and 4.4 (two defects to fix first), 4.3 (what to build, in order, each with its test), 11.1 (every change of behaviour is tied to a version line in the map; a listed defect's fix is the one exception and is shown and approved), 11.2 (the seven templates are first rebuilt from unchanged source and must give an identical golden; development happens in a staging data folder, never in `languages/`) and 13.2 (the proposed order). The key `f0` must stay inert in the present packs: a consonant's push on pitch gets a new key. Try `openevv/test/matrix.sh` under MSYS2 before the first change under `openevv/src`. `openevv/CLAUDE.md` binds every change there.
10. The harness venv has no TOML reader; the design's pack and table format needs `tomli` (MIT) on Python 3.10. Nothing was installed in Phase 2.

11. **From Phase 3A.** Until `b11f978` the golden silently skipped every phoneme named with `#` (D38a), so Phase 1's and Phase 2's counts of "every phoneme" were short by 2,321 map entries. The module's phone record has a voicing field (second field: 0 voiced, 1 voiceless or pause) in all seven templates (D40). The English module turns `t` before its `y` phone into `t S` (Shavian English `e@ i@ i@3`): one for Phases 4 and 6.

## Open questions

See `OPEN_QUESTIONS.md`. For the human: Q1 (the permissions file), Q5 (the Stop hook), Q7 (ASR for the 46 languages Whisper lacks), Q8 (the 32-bit US English module is older than the 64-bit one), Q9 (natural recordings to judge the recogniser by), Q10 and Q2 (pushing to GitHub), Q3 and Q4 from Phase 0. Answered in Phase 2: Q6 (module files may be rebuilt and replaced when proven) and Q11 (the defect is fixed first thing in Phase 3).
