---
name: add-accent
description: Add an authentic accent (a target language spoken with features of a speaker group, often a first language) as a pack extending the target, every feature sourced or measured, nothing stereotyped. Use as /add-accent <accent> of <target tag>.
argument-hint: <accent, e.g. Spanish-speakers'> of <target tag>
disable-model-invocation: true
model: sonnet
effort: medium
---

# Add an accent: $ARGUMENTS

Playbook Part 3, workflow C. Sonnet 5.5 at medium (set above); Opus 5.5 high for an accent that
carries a whole phonological system across: if so and you are not Opus, say so first and stop.

Read first: `CLAUDE.md`, `ADDING_A_LANGUAGE.md` (its accent example `en-us-x-evvdemo-es`),
`docs/tts-extension/AUTHENTICITY.md` (rules M1-M6, A1-A4 and section 5, anti-caricature). An accent
describes real speakers; it is never a performance. You cannot hear: measure (R2, R5, R16).

## Setup (PowerShell, repository root)

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Define the accent**: the speaker group (first language and its variety, region, proficiency or
   experience where relevant) and the target variety. Find descriptive or experimental sources with
   measured values and licensed recordings (R3, R4; delegate to a research subagent); register them
   in `ipa/sources.toml` (`opened = true` only if read) and `REFERENCES.md`.
2. **Build the substitution list**: each feature (a vowel quality or length moved, a sound replaced,
   devoicing, epenthesis, stress or rhythm, intonation) with who does it and how often, from the
   sources. Prefer features measured in groups of speakers. A sound outside the target language:
   look it up in the master table (`ipa/table/*.toml`); a gap is `/create-missing-sound`.
3. **What the engine can carry today**: the target must be a legacy pack (`[engine] realization =
   "legacy"`: the native modules enus, engb, dede and the rest cannot take overrides). A vowel's
   quality and length are `[[override]]` blocks (formants F1-F3 in Hz, duration in ms; values
   `measured`, `literature`, `derived` or `approximate` with `ref`, never `estimated`). Substituting
   one phoneme for another, devoicing, epenthesis and rhythm have no sourced pack mechanism yet
   (accent packs over a reader's rules, DESIGN.md L4, are not built): list each such feature in the
   pack's note as **not made** and in the report. Never fake one by hand-editing `[sounds]` lines.
4. **Write the pack** `packs-proposed/<tag>/pack.toml`: `kind = "accent"`, `extends = "<target>"`,
   `[meta]` (variety: the accent and target; region; speaker_group: the group as the sources describe
   it; sources; recordings; date; status; licence), `[ini.Language]` Tag, Name, Order, and the
   overrides (`state = "proposed"`); `review.toml` with words for each overridden sound. Copy the
   shape of `docs/tts-extension/examples/packs/en-us-x-evvdemo-es/`.
5. **Validate and measure** in a scratch stage:

       & $py engine\packs\validate_packs.py <tag>          # "accepted"
       $S="$env:TEMP\OpenEvvTests\stage-<tag>"; Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S
       & $py engine\packs\build_packs.py build "$S\languages" <tag>
       $env:EVV_STAGE=$S
       & $py engine\authenticity\show_effect.py <tag>       # each override: before, after, target
       & $py docs\tts-extension\harness\golden.py <tag> --record --golden "$env:TEMP\OpenEvvTests\golden-<tag>"
       & $py docs\tts-extension\harness\check_language.py <tag> --golden "$env:TEMP\OpenEvvTests\golden-<tag>" --asr --asr-like <target>

   An accent is meant to move the sounds: check A must still pass (the engine says what it is told);
   check B against the target's references is expected to move and is reported, not chased.
6. **The target is unaffected**: under the shared stage
   (`$env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"`), `golden.py <target>` 0 FAILED.
7. **Packet**: `& $py engine\review\make_packet.py <tag>` under the scratch stage (a test pack:
   `--out docs\tts-extension\examples\packets\<tag>`). A native reviewer of the speaker group judges
   it; a reviewer's "this sounds like a parody" takes the feature back to its evidence.
8. **Report** in plain English; flag anything weakly sourced or that could read as a stereotype, for
   removal. Status: the true level; shipping waits for the human's say-so.
9. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths.

## Done when

- `validate_packs.py <tag>` accepts it; every feature sourced; features not made listed as such
- each override's effect measured (`show_effect.py`) and shown; check A passes
- the target's golden: 0 FAILED; packet made; level stated; nothing called authentic
