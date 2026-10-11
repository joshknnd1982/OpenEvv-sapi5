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
`docs/tts-extension/LANGUAGE_STATUS.md` (the status table, and the Phase 6 triage table further down:
where their failure layers differ, the triage's compares with eSpeak NG's own voice and is the
better evidence), `DESIGN.md` 6 (packs), 8 (G2P), 9 (prosody) and 10 (the checks and the levels),
`OPEN_QUESTIONS.md` for findings about the language (a `/diagnose-language` run
records its diagnosis there), `ADDING_A_LANGUAGE.md` section 9. The numbers in `LANGUAGE_STATUS.md`
and `results/asr.json` may be older than the stage: measure again before comparing. You cannot hear:
measure (R2, R5, R16).

**R21 (playbook 1.3, the human's order of 2026-10-11): an improvement uses the IPA master table and
the master path.** Step 1 also records the pack's `realization`
(`Select-String -Path packs\<tag>\pack.toml -Pattern 'realization'`). A pack still at `"legacy"`
is first moved to `"master"` with `engine\packs\to_master.py <tag>` (its report shown, before and
after measured), unless the human says otherwise; a missing tool or a sound the master path cannot
say is not for you to work around: record it in `OPEN_QUESTIONS.md` and ask (R21g). A sound that the
table or the generator supplies is fixed there once (R21c), then every language is re-measured;
an `[[override]]` in the pack is only for a measured difference of the language's speakers, with
provenance. The ten native languages stay untouched unless the human orders otherwise (R21e).

## Setup (PowerShell, repository root)

The PowerShell tool keeps no state between calls: start **every** call with these lines.

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"
    # beside another session: $env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-improve-<tag>"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Baseline**: re-measure before changing anything, and keep the output:

       & $py docs\tts-extension\harness\check_language.py <tag> --asr
       & $py docs\tts-extension\harness\diag.py <tag>        # always name the tag: without one it rewrites results/diag.json

   For a voicing or silence question also `a3.py <tag>` (it overwrites `results/a3-staged.json` with
   only that tag: copy the file aside first and merge back). To try sentences of your own through
   the recogniser: `harness/asr_try.py <tag> "<sentence>" ...` (writes nothing).
2. **Change one thing, at the right place**: the failing layer (phoneme values, G2P, stress or tone,
   duration, voice scaling, engine) or the evidence itself. A shared cause is fixed once (the master
   table `ipa/table/`, the engine under `openevv/` with `openevv/CLAUDE.md`'s rules), not per
   language. Kinds of change:
   - *a sound's target with evidence*: an `[[override]]` in `packs/<tag>/pack.toml` with its
     provenance, `state = "proposed"` until the human says to apply it (proposed overrides do not
     change the shipped files: `build_packs.py check` stays identical). Normalize published values
     (`engine\authenticity\normalize.py`, as `/add-dialect` step 3) and write only what moves more
     than 6 per cent;
   - *better evidence for check B*: cited ranges in `harness/reference/ranges.json` (the store's own
     format: the source in its `sources` list as well as in `ipa/sources.toml`; mean and SD, the
     range is mean +- 2 SD; `variety`, `speaker_group`, `n`, `provenance`, `where_in_source`). **The
     lookup lends a variety's ranges to every variety of the same language** (`reference.lookup()`,
     `OPEN_QUESTIONS.md` Q46): say which other packs a new entry reaches. Check B compares raw Hz with
     the references' speaker group, unnormalized;
   - *G2P*: eSpeak NG's rules are GPL and live upstream; record what is wrong and propose, do not
     edit `dist/espeak-ng-data` (rebuilding it needs the human's say-so).
3. **Re-measure** the language after each change (step 1's commands; for a proposed override,
   `build_packs.py build <scratch stage>\languages <tag> --proposed` in a copy of the stage, as in
   `/add-dialect`, and `engine\authenticity\show_effect.py <tag>`). Then the regression that can see
   the change:
   - synthesis or pack data the product reads (a pack's sounds, the master table, the engine, the
     front-end): the full golden, `& $py docs\tts-extension\harness\golden.py` (every language,
     0 FAILED; 25 to 40 minutes), `doctor.py --quick`;
   - reference ranges: the golden cannot see them; run `check_language.py` on every pack the new
     entries reach (step 2) and report each before and after;
   never trade one language's fix for another's regression (R8). An intended change to the golden:
   `golden.py --record <tags>` and a line in `docs/tts-extension/DECISIONS.md`.
4. **Record**: provenance on every new value; for a real change, `asr.py <tag>` (refreshes that tag in
   `results/asr.json`) and then `report.py` (rewrites `LANGUAGE_STATUS.md` for every language: read
   its diff, and say every row that moved); a new packet (`make_packet.py <tag>`) only if what the
   language says changed.
5. **Report** in plain English: what moved, by how much, at which layer; the level now; the pack's
   realization and the R21f counts (from the table, composed, created, fallen back and why). Applying
   proposed overrides or rebuilding `languages/` waits for the human's say-so (R18, D34).
6. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths. If
   you cannot launch agents, say that the review is still owed.

## Done when

- the baseline and the after measurements are both shown, raw
- the change is at the failing layer (or is better evidence), with provenance on every value, made in the table or generator when the cause is shared and the pack is on the master path (R21)
- the regression that can see the change was run and shown (the full golden 0 FAILED for anything the
  product reads; every reached pack's check B for references); `doctor --quick` passes
- LANGUAGE_STATUS (for a real change) and the report state the true level
