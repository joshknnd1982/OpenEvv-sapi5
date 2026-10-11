---
name: create-missing-sound
description: Create a sound the OpenEVV engine cannot yet make (an IPA symbol, a combination, or a described sound) by the Unmappable Sound Protocol, measured, registered with a stable id, and regression-tested. Use as /create-missing-sound <IPA symbol or description>.
argument-hint: <IPA symbol, combination or description>
disable-model-invocation: true
model: fable
effort: high
---

# Create a missing sound: $ARGUMENTS

Playbook Part 3, workflow E, and the USP (playbook 1.6). Fable 5.1 at high (set above); `xhigh` if
step 4 needs a new synthesis mechanism: then stop with the MODEL SWITCH NEEDED pause first. Master
table or engine changes run one session at a time (no parallel session on them).

Read first: `CLAUDE.md`; `DESIGN.md` 2 (the sound model, composition), 3 (the master table, the
adapter), 4 (capability gaps) and 5 (the USP here); `docs/tts-extension/CREATED_SOUNDS.md` (the
register's rules); `PROJECT_STATE.md` "Phase 4 working notes" (the measures, their pitfalls, and
the long runs); `openevv/CLAUDE.md` before touching anything under `openevv/`. You cannot hear:
every value has a provenance tag, every claim a measurement (R2, R5, R16).

## Setup (PowerShell, repository root)

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps (the USP)

1. **Normalize**: the exact code points and the intended phonetic meaning, cited (R3). Is it on the
   checklist (`docs/tts-extension/inventory/IPA_CHECKLIST.md`) or Tier B? Is it already an entry
   (`& $py engine\ipa\reader.py "<IPA>"` says how the reader takes it; `ipa/table/*.toml`)?
2. **Try composition**: base plus marks (voicing, aspiration, nasalization, secondary articulation,
   length, phonation, tone). Render it in three vowel contexts on the reference template dedx,
   through a pack it speaks (`& $py docs\tts-extension\harness\engine.py hi ipa "a<X>a" <out.wav>`,
   also i and u; hi's template is dedx, the sweep's default) and
   check the front-end composes it as the adapter does (`& $py engine\ipa\compose_test.py --letters <X>`).
   If composition gives the sound, define the transform (no new phoneme) and go to step 6.
3. **Feature substitution**: decompose (place, manner, phonation, airstream, secondary
   articulation); find the nearest realizable neighbour; note the lost feature.
4. **Capability check**: does the engine have the mechanism (source type, noise shaping, bursts,
   antiresonances, F0 control, timing)? If not, specify, implement and test a new capability in
   the engine or the accent layer, built in a copy outside the tree and staged (`PROJECT_STATE.md`
   "How to work in 3A"; R18: alongside the old, never replacing it silently).
5. **Design**: an entry in the master table (`ipa/table/<section>.toml`, `DESIGN.md` 3.2): formants
   and bandwidths, sources and levels, noise bands, antiresonances, closure and burst, VOT,
   durations, transitions, F0; every value tagged (`literature` with a registered `ref`, `derived`
   with its `rule`, `estimated` queued for verification); `& $py engine\ipa\table.py` must report 0
   problems.
6. **Implement, render, measure, iterate** (at most 5 rounds):
   `& $py engine\ipa\prove.py <id>` (realise, render, measure, correct), then
   `& $py engine\ipa\sweep.py <id> --apply` (alone and in three contexts, judged). Two symbols the
   chart treats as different must measurably differ: add a `distinct` contrast test with each
   neighbour it could be confused with. Still short after 5 rounds: tag `approximate`, state the
   deviation, queue it for native review.
7. **Register**: `& $py engine\ipa\register.py` (CREATED_SOUNDS.md, a stable `CS-` number that never
   changes); every `estimated` value queued (`& $py engine\doctor.py --print-queue` gives Q15's list
   for `OPEN_QUESTIONS.md`); sources in `REFERENCES.md`.
8. **Regression**: after any map change the whole sweep (`& $py engine\ipa\sweep.py --apply`, about
   20 minutes), `& $py engine\ipa\coverage.py` (MISSING 0, BLOCKED 0), `compose_test.py`, and the
   golden (`& $py docs\tts-extension\harness\golden.py`, 0 FAILED); after an engine change also the
   engine gate (`matrix_each.sh`, PROJECT_STATE.md). Long runs: one per background job (2-hour limit).
   Record any intended golden change in `DECISIONS.md` before committing.
9. **Report** in plain English: what the sound is, how it is made, which values are estimated or
   approximate, what a native listener should check (add it to a packet).
10. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths.

## Done when

- the sound is `mapped`, `composed` or `created` with a passing proof shown (never silent or
  silently substituted); contrasts with its neighbours pass
- every value tagged; estimated ones queued; created ones registered with a stable id
- coverage: MISSING 0, BLOCKED 0; the golden 0 FAILED (or each change in DECISIONS.md); `doctor --quick` passes
