# OpenEVV SAPI5: TTS extension project

**Mission.** Map every symbol of the official IPA chart (consonants, vowels, diacritics, suprasegmentals, tones) to an engine-neutral acoustic specification and a working, measured realization in this engine, extending the engine where it cannot produce a sound, so that adding a language, dialect or accent becomes a data-only change that is verified automatically. The human speaks only American English and cannot judge other languages by ear, so correctness must be measured.

Full rules, pause protocol and phase prompts: `TTS_EXTENSION_PLAYBOOK.md` Part 1. Read it, your phase section, and `docs/tts-extension/PROJECT_STATE.md` at the start of every session.

## Rules that cause mistakes if forgotten

- Never delete or overwrite original engine code or existing language data. Add alongside. No force-push, no history rewrites.
- You cannot hear audio. Never claim or imply that you can.
- Every acoustic value carries a provenance tag: `measured`, `literature`, `derived`, `estimated`, `created` or `approximate`.
- Show the raw output of every command you rely on. Never write "tests pass" without it.
- Before each pause, a fresh-context subagent reviews the diff against the phase's exit criteria.
- End every phase with the pause protocol (playbook 1.4), then stop.
- Research the whole IPA chart and map every checklist symbol, extending the engine where needed (R19). No symbol may be skipped, silent, or silently substituted.
- Look things up (web) and cite them in `docs/tts-extension/REFERENCES.md`; record the licence before importing anything. The IPA chart is CC BY-SA and eSpeak NG is GPL: cite, do not paste into MIT files.
- The language data under `openevv/lang/` and every module DLL in `languages/` is IBM's and is not licensed here (`NOTICE.md`). Do not put a licence header on it.
- Several Claude sessions may share this working tree. Check `git log -3` and `git status -sb` before committing; commit by naming paths, never `git add -A`; never amend, reset or revert work you did not make.

## Commands (Windows, PowerShell, from the repository root)

Build the wrapper and tools (git-ignored output, touches nothing tracked):

    cmake -G "Visual Studio 17 2022" -A x64 -S . -B build_x64
    cmake --build build_x64 --config Release

Speak to a WAV file without SAPI or a sound device:

    .\build_x64\bin\Release\evv_say.exe <tag> <preset 1-8> <text | @utf8file> <out.wav> 64
    .\build_x64\bin\Release\evv_say.exe --list

Build engine modules from `openevv/` in a copy outside the repository (MSYS2 at `C:\msys64`; about 4 minutes a module):

    $env:MSYSTEM='MSYS'; $env:CHERE_INVOKING='1'; $env:OPENEVV_WORK="$env:LOCALAPPDATA\OpenEvvBuild-ttsext"; $env:TAGS='enus dedx'
    & C:\msys64\usr\bin\bash.exe -l "$PWD\engine\build_modules.sh"

Tests:

    .\build_x64\bin\Release\sapi_test.exe --out $env:TEMP\OpenEvvTests\x64
    $env:PYTHONUTF8='1'; python engine\check_espeak_packs.py dist\x64\OpenEvvFrontend.exe dist\espeak-ng-data

Inventories:

    $env:PYTHONUTF8='1'; python docs\tts-extension\inventory\build_language_inventory.py
    $env:PYTHONUTF8='1'; python docs\tts-extension\inventory\build_ipa_checklist.py

**These overwrite tracked files; do not run them without the human's say-so:** `build_all.bat` (restages `dist\`), `engine\build_modules.cmd` (overwrites the DLLs in `languages\`), `build_all.bat packs` (rewrites all 145 eSpeak NG packs). In this environment run a batch file by absolute path.

## Handoff files (`docs/tts-extension/`)

`PROJECT_STATE.md` (phase, done, next step, environment) · `ARCHITECTURE_MAP.md` · `DECISIONS.md` · `DESIGN.md` (Phase 2) · `CREATED_SOUNDS.md` · `LANGUAGE_STATUS.md` · `REFERENCES.md` · `OPEN_QUESTIONS.md` · `inventory/IPA_CHECKLIST.md` + `.json` · `inventory/languages.json`

`openevv/CLAUDE.md` holds the upstream engine's own working rules; it applies when changing anything under `openevv/`.
