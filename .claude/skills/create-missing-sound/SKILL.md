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

Read first: `CLAUDE.md`; `DESIGN.md` 2 (the sound model, composition), 3 (the master table, its tiers
and the adapter), 4 (capability gaps) and 5 (the USP here); `docs/tts-extension/CREATED_SOUNDS.md`
(the register's rules); `PROJECT_STATE.md` "Phase 4 working notes" (the measures, their pitfalls, the
long runs); `openevv/CLAUDE.md` before touching anything under `openevv/`. The worked case is
CS-0076 ɓ̥ (`ipa/table/non_pulmonic.toml`, `DECISIONS.md` D92). You cannot hear: every value has a
provenance tag, every claim a measurement (R2, R5, R16).

## Setup (PowerShell, repository root)

The PowerShell tool keeps no state between calls: start **every** call with these lines. Pass IPA
as literal characters (PowerShell 5.1 has no `` `u{} `` escape).

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"
    # beside another session: $env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-<name>"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps (the USP)

1. **Normalize**: the exact code points and the intended phonetic meaning, cited (R3). Is it on the
   checklist (`docs/tts-extension/inventory/IPA_CHECKLIST.md`), in Tier B (extIPA, VoQS), or beyond
   both (Tier C)? Is it already an entry (`ipa/table/*.toml`)? How does the reader take it:
   `& $py engine\ipa\reader.py "<IPA>"`.
2. **Try composition**: base plus marks. Say it the sweep's way, alone and between [a i u] (a vowel:
   `--vowel`, between [p t k]), and read the sweep's own measures, against its neighbours:

       & $py engine\ipa\say_ipa.py "<X>" "<base>" "<neighbour>"

   (`engine.py <pack> ipa` reads IPA through a language's eSpeak NG table and fails on any letter the
   language lacks: do not use it here.) Judge with the measures the class needs: for voicing
   `voiced_frac`, `voiced_mid`, `voiced_tail`, `voice_gap_ms`, `voicing_slope`; for noise
   `centroid1k_hz`, `hf_db`; for vowels F1-F3; durations `duration_ms`. Check the front-end composes
   it as the adapter does: `& $py engine\ipa\compose_test.py --letters <X>` (minutes; the full run
   without `--letters` takes 3.5 to 4.5 hours, past a background job's 2-hour limit). If composition
   already gives the sound the sources describe, define nothing new: report the measurements.
3. **Feature substitution**: decompose (place, manner, phonation, airstream, secondary
   articulation); find the nearest realizable neighbour; note the lost feature.
4. **Capability check**: does the engine have the mechanism (source type, noise shaping, bursts,
   antiresonances, F0 control, timing, the layer's keys: `docs/tts-extension/SOUNDS_STAGED.md`)? If
   not, specify, implement and test a new capability, built in a copy outside the tree and staged
   (`PROJECT_STATE.md` "How to work in 3A"; R18: alongside the old, never replacing it silently).
5. **Design** an entry in the master table (`ipa/table/<section>.toml`, `DESIGN.md` 3.2; copy the
   shape of a near entry): a checklist symbol is Tier A; extIPA/VoQS Tier B; **anything beyond both
   is `tier = "C"`, keyed by its code points (`U+0253+U+0325`)**: coverage counts A and B only, so a
   Tier C entry never makes it fail. Every value tagged (`literature` with a registered `ref`,
   `derived` with its `rule`, `estimated` when no source gives it). The judge has requirements of its
   own: a voiceless letter must read `voiced_frac` at or under 0.5 (T-voicing); an implosive needs a
   `closure.voicing_slope_db10` target (T-airstream); a measure reads what the sound does, so set a
   target from what the measure would read of the sound the sources describe, and say so.
   `& $py engine\ipa\table.py` must report 0 problems.
6. **Render, measure, iterate** (at most 5 rounds): `& $py engine\ipa\sweep.py <id> --apply` (the
   five-round design loop is inside it; `prove.py <id>` is the same loop alone). After a change to
   the map its settle pass re-says **every** proof (about 45 minutes): run it as one foreground
   command with a long timeout, alone. Two symbols the chart treats as different must measurably
   differ: `distinct` contrasts with each neighbour (CS-0076 has eight). Still short after 5 rounds:
   tag `approximate` and state the deviation, but **check the trims the loop saves** (an approximate
   bound that accepts at last stores its trims as the design: a target you cannot meet honestly is
   better tagged `estimated` than chased by trims). Queue it for native review.
7. **Register**: `& $py engine\ipa\register.py` (CREATED_SOUNDS.md, a stable `CS-` number that never
   changes); every `estimated` value queued: `& $py engine\doctor.py --print-queue` lists Q15; add the
   new lines to `OPEN_QUESTIONS.md` Q15 (the doctor WARNs until then, and FAILs after 14 days);
   sources in `REFERENCES.md` and `ipa/sources.toml`.
8. **Regression**: `& $py engine\ipa\coverage.py` (MISSING 0, BLOCKED 0, "every proof of a done entry
   was made on the map as it stands": the sweep's settle pass of step 6 is the whole sweep, so do not
   run it twice); `compose_test.py --letters <X>`; the golden
   (`& $py docs\tts-extension\harness\golden.py`, 0 FAILED, 25 to 40 minutes); after an engine change
   also the engine gate (`matrix_each.sh`, PROJECT_STATE.md). Record any intended golden change in
   `DECISIONS.md` before committing.
9. **Report** in plain English: what the sound is, how it is made, which values are estimated or
   approximate, what a native listener should check (add it to a packet).
10. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths. If
    you cannot launch agents, say that the review is still owed.

## Done when

- the sound is `mapped`, `composed` or `created` with a passing proof shown (never silent or
  silently substituted); contrasts with its neighbours pass
- every value tagged; estimated ones queued in Q15 (`doctor` has no WARN for them); created ones
  registered with a stable id
- coverage: MISSING 0, BLOCKED 0; the golden 0 FAILED (or each change in DECISIONS.md); `doctor --quick` 0 FAILED
