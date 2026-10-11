---
name: improve-language
description: Improve an existing language of the OpenEVV engine at the layer its measurements say is failing, without regressing any other language. Use as /improve-language <tag>.
argument-hint: <tag> [what to improve]
disable-model-invocation: true
model: opus
effort: high
---

# Improve a language: $ARGUMENTS

Playbook Part 3, workflow D. Opus 5.5 at high (set above). If two rounds of fixes do not move the
measurements, stop with the playbook's MODEL SWITCH NEEDED pause (Fable 5.1 high).

Read first: `CLAUDE.md`, `docs/tts-extension/PROJECT_STATE.md`, the language's rows in
`docs/tts-extension/LANGUAGE_STATUS.md` and `docs/tts-extension/TRIAGE_PHASE6.md` (its failure layer
and evidence), `ADDING_A_LANGUAGE.md` ("Improving"). You cannot hear: measure (R2, R5, R16).

## Setup (PowerShell, repository root)

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Baseline**: re-measure before changing anything, and keep the output:

       & $py docs\tts-extension\harness\check_language.py <tag> --asr
       & $py docs\tts-extension\harness\diag.py <tag>        # what the front-end loses on the way
       & $py docs\tts-extension\harness\a3.py <tag>          # voiceless sounds stay voiceless (back up results/a3-staged.json first: it is overwritten)

2. **Fix at the identified layer only** (phoneme values, G2P, stress or tone, duration, voice
   scaling, engine): a shared cause is fixed once (the master table `ipa/table/`, the engine under
   `openevv/` with `openevv/CLAUDE.md`'s rules), not per language. A pack's change:
   - a sound's target with evidence: an `[[override]]` in `packs/<tag>/pack.toml` with its
     provenance (`state = "proposed"` until the human says to apply it: proposed overrides do not
     change the shipped files, and `build_packs.py check` stays identical);
   - better references for check B: cited ranges in `harness/reference/ranges.json` (with a
     spread, from a source registered and opened);
   - G2P: eSpeak NG's own rules are GPL and live upstream; record what is wrong and propose, do not
     edit `dist/espeak-ng-data` (rebuilding it needs the human's say-so).
3. **Re-measure** the language after each change (step 1's commands; for a proposed override,
   `build_packs.py build <scratch stage>\languages <tag> --proposed` in a copy of the stage, as in
   `/add-dialect`, and `engine\authenticity\show_effect.py <tag>`), then **the full regression**
   (`golden.py`, every language, 0 FAILED). Never trade one language's fix for another's
   regression (R8). An intended change to the golden: `golden.py --record <tags>` and a line in
   `docs/tts-extension/DECISIONS.md`.
4. **Record**: provenance on every new value; before and after numbers in `LANGUAGE_STATUS.md`
   (`harness/report.py` rewrites it for every language: run it when the change is real); the
   packet again (`engine\review\make_packet.py <tag>`).
5. **Report** in plain English: what moved, by how much, at which layer; the level now. Applying
   proposed overrides or rebuilding `languages/` waits for the human's say-so (R18, D34).
6. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths.

## Done when

- the baseline and the after measurements are both shown, raw
- the change is at the failing layer; provenance on every value
- the full golden: 0 FAILED (or each difference recorded in DECISIONS.md); `doctor --quick` passes
- LANGUAGE_STATUS (for a real change) and the report state the true level
