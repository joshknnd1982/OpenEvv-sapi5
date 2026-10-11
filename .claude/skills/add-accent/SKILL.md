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

Read first: `CLAUDE.md`, `ADDING_A_LANGUAGE.md` section 5 (the accent example `en-us-x-evvdemo-es`,
every command with its output), `docs/tts-extension/AUTHENTICITY.md` (rules M1-M6, A1-A4 and section
5, anti-caricature). An accent describes real speakers; it is never a performance. You cannot hear:
measure (R2, R5, R16).

**R21 (playbook 1.3, the human's order of 2026-10-11): an accent is built on the IPA master table
and the master path.** The pack `extends` a target whose sounds come from the table (`realization =
"master"`; after Phase 12 every eSpeak NG pack is). The accent's sounds are other IPA sounds of the
table named for the phoneme, or an `[[override]]` for a measured group difference with provenance; a
sound the table lacks (a sound of the speakers' first language) goes into the table
(`/create-missing-sound`), never into this pack alone. A missing `engine\packs\to_master.py`, or a
target still at `legacy`, is not for you to work around: say so, record it in `OPEN_QUESTIONS.md` and
ask the human (R21g). The ten native languages stay untouched (R21e).

## Setup (PowerShell, repository root)

The PowerShell tool keeps no state between calls: start **every** call with these lines (and
`$S`, `$G`, `$tag` once you have them).

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"
    # beside another session: $env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-<tag>"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Define the accent**: the speaker group (first language and its variety, region, proficiency or
   experience where relevant) and the target variety. Find descriptive or experimental sources with
   measured values and licensed recordings (R3, R4; a research subagent if you can launch one, else
   yourself); register them in `ipa/sources.toml` (`opened = true` only if read) and `REFERENCES.md`.
2. **Build the feature list**: each feature (a vowel quality or length moved, a sound replaced,
   devoicing, epenthesis, stress or rhythm, intonation) with who does it and how often, from the
   sources. Prefer features measured in groups of speakers. A sound outside the target language:
   look it up in the master table (`ipa/table/*.toml`); a gap is `/create-missing-sound`.
3. **What the engine can carry today**: the target must be a pack whose sounds are written out and
   come from the master path (`[engine] realization = "master"`, R21; a pack still at `"legacy"`
   also carries overrides, but is not a target for new work: see above); the native modules enus,
   engb, dede and the rest cannot take overrides. A vowel's
   quality and length are `[[override]]` blocks (formants in Hz, duration in ms; `measured`,
   `literature`, `derived` or `approximate` with `ref`, never `estimated`). Substituting one phoneme
   for another, devoicing, epenthesis and rhythm have no sourced pack mechanism yet (DESIGN.md L4):
   list each in the pack's note as **not made**. Never fake one by hand-editing `[sounds]` lines.
4. **Turn the evidence into targets.**
   - *Phoneme names*: what the reader writes: `& "$env:LOCALAPPDATA\OpenEvvBuild\frontend-x64\bin\espeak-ng.exe"
     --path=dist -v <voice> -q -x "<words>"`; then the pack's `map` lines of those names in
     `packs/<target>/pack.toml`. Override **every** phoneme that says the sound (TRAP in en-us-nyc is
     `@en-us-nyc:a` and `@en-us-nyc:aa`).
   - *What the pack says now*: `& $py engine\authenticity\normalize.py <target> <phoneme>=<F1>,<F2>`
     prints the module phone and its "now" F1/F2 (the map line's sound keys applied to the module's
     phone, `engine/accent/chassis/<template>.json`). Base every computation on that value, not on a
     render's "before" (which moves with the neighbouring sounds).
   - *Ratio method* (a study that measured the speaker group and native speakers alike): target =
     now x (group's value / natives' value), per formant; tag `derived`, the arithmetic in `norm`.
     *Absolute values* (the group alone): normalize them as `/add-dialect` step 3 does.
   - **Write an override only where F1 or F2 moves more than 6 per cent** from now.
5. **Write the pack** `packs-proposed/<tag>/pack.toml`: `kind = "accent"`, `extends = "<target>"`,
   `[meta]` (variety: the accent and target; region; speaker_group: the group as the sources describe
   it; sources; recordings; date; status; `licence` inherited unless different), `[ini.Language]` Tag,
   Name, Order (any number no other pack uses), the overrides (`state = "proposed"`), and in the note
   every feature not made. `review.toml` beside it: `[words] list` and one `[[check]]` (`sound`,
   `words`, `question`) per overridden sound. Copy the shape of `docs/tts-extension/examples/packs/en-us-x-evvdemo-es/`.
6. **Validate and measure** in a scratch stage:

       $tag='<tag>'; $S="$env:TEMP\OpenEvvTests\stage-$tag"; $G="$env:TEMP\OpenEvvTests\golden-$tag"
       & $py engine\packs\validate_packs.py $tag          # "accepted"
       Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S     # once
       & $py engine\packs\build_packs.py build "$S\languages" $tag      # without the proposed overrides
       $env:EVV_STAGE=$S
       & $py engine\authenticity\show_effect.py $tag       # each override: before, after, target
       & $py docs\tts-extension\harness\golden.py $tag --record --golden $G
       & $py docs\tts-extension\harness\check_language.py $tag --golden $G --asr --asr-like <target>

   An accent is meant to move sounds: check A must still pass with the overrides (build with
   `--proposed` into `$S`, record into another golden folder, check, then build without again); check
   B against the target's native references is expected to lose the moved values and is reported,
   not chased.
7. **The target is unaffected**: `$env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"`;
   `& $py docs\tts-extension\harness\golden.py <target>` (0 FAILED, about a minute);
   `& $py engine\packs\build_packs.py check`.
8. **Packet**, under the scratch stage: `& $py engine\review\make_packet.py $tag` (a test pack:
   `--out docs\tts-extension\examples\packets\$tag`); it also writes the blind A/B key to
   `docs/tts-extension/review/keys/<tag>.json`; a matplotlib `RuntimeWarning` on stderr is harmless.
   A native reviewer of the speaker group judges it; "this sounds like a parody" takes the feature
   back to its evidence.
9. **Report** in plain English, with the R21f counts (sounds from the table, composed, created,
   fallen back and why; the target's realization); flag anything weakly sourced or that could read
   as a stereotype, for removal. Status: the pack's `[meta] status` level is what `check_language.py` printed for the pack
   as built in step 6 (without proposed overrides); never 5 without a named reviewer. Shipping waits
   for the human's say-so.
10. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths. If
    you cannot launch agents, say that the review is still owed.

## Done when

- `validate_packs.py <tag>` accepts it; every feature sourced; features not made listed as such; the target is on the master path (R21)
- every override moves its vowel by more than 6 per cent; its effect measured (`show_effect.py`) and shown; check A passes with the overrides
- the target's golden: 0 FAILED; packet made; level stated and equal to the measurement; nothing called authentic
