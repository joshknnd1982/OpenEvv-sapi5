---
name: add-dialect
description: Add an authentic dialect of an existing language as a pack that extends its parent and holds only the differences, each sourced or measured. Use as /add-dialect <dialect> of <parent tag>.
argument-hint: <dialect name> of <parent tag>
disable-model-invocation: true
model: sonnet
effort: medium
---

# Add a dialect: $ARGUMENTS

Playbook Part 3, workflow B. Sonnet 5.5 at medium (set above); Opus 5.5 high for large vowel shifts
or many allophone rules: if so and you are not Opus, say so first and stop.

Read first: `CLAUDE.md`, `ADDING_A_LANGUAGE.md` (its dialect example `ca-va-x-evvdemo`),
`docs/tts-extension/AUTHENTICITY.md` (the pipeline, the validator's rules M1-M6 and A1-A4, the
anti-caricature rules), `DESIGN.md` 6.3 (inheritance). You cannot hear: measure (R2, R5, R16).

## Setup (PowerShell, repository root)

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Define the variety precisely** (R14): region, speaker group, era. Find descriptive sources and
   licensed recordings (R3, R4; delegate to a research subagent); register each in `ipa/sources.toml`
   (`opened = true` only if read) and `REFERENCES.md`. No source and no recordings: say so; such a
   dialect cannot pass the validator (M2) and must not be invented.
2. **List the differences** from the parent: mergers and shifts, consonant realizations, allophone
   rules, stress and rhythm, intonation, lexical sets; each with its source or measurement. No
   stage dialect, no eye-dialect, a variable feature only at the frequency a source gives.
3. **Measure** if recordings exist (`AUTHENTICITY.md` steps 2-3):
   `& $py engine\authenticity\extract_targets.py <tag> <corpus> --write` (needs `measure.toml`).
4. **Write the pack** `packs-proposed/<tag>/pack.toml` with `kind = "dialect"`, `extends = "<parent>"`
   and only what differs: `[meta]` (variety, region, speaker_group, sources, recordings, date, status,
   licence), `[ini.Language]` Tag, Name, Order, the reader's `[ini.Frontend] Voice` if the dialect
   has its own eSpeak NG voice, and each vowel change as an `[[override]]` (`state = "proposed"`,
   values `measured`, `literature`, `derived` or `approximate` with `ref`: never `estimated`).
   Copy the shape of `docs/tts-extension/examples/packs/ca-va-x-evvdemo/pack.toml`. A difference no
   override can express (a merger, an allophone rule) is listed in the note as not yet made, and
   reported; never hand-edit `[sounds]` lines in a dialect.
5. **Validate and measure** in a scratch stage:

       & $py engine\packs\validate_packs.py <tag>          # "accepted"
       $S="$env:TEMP\OpenEvvTests\stage-<tag>"; Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S
       & $py engine\packs\build_packs.py build "$S\languages" <tag>     # without the proposed overrides
       $env:EVV_STAGE=$S
       & $py engine\authenticity\show_effect.py <tag>       # each override: F1/F2 before, after, target
       & $py docs\tts-extension\harness\golden.py <tag> --record --golden "$env:TEMP\OpenEvvTests\golden-<tag>"
       & $py docs\tts-extension\harness\check_language.py <tag> --golden "$env:TEMP\OpenEvvTests\golden-<tag>" --asr --asr-like <parent>

   `show_effect.py` reads the words of `review.toml`'s `[[check]]` entries (`sound`, `words`,
   `question`) for each overridden sound and needs both F1 and F2 in a formant override.
6. **The parent is unaffected**: `$env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"`;
   `& $py docs\tts-extension\harness\golden.py <parent>` (0 FAILED); `build_packs.py check`.
7. **Packet**: `& $py engine\review\make_packet.py <tag>` under the scratch stage (the override's
   A/B items are blind; a test pack: `--out docs\tts-extension\examples\packets\<tag>`).
8. **Status and report**: the true level (never 5 without a named reviewer); for a real dialect,
   `LANGUAGE_STATUS.md`. Report in plain English which claims are measured, which from literature,
   which differences are not made. Shipping waits for the human's say-so.
9. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths.

## Done when

- `validate_packs.py <tag>` accepts the pack; it holds only differences from its parent
- every difference has a source or measurement; each override's effect measured and shown
- the parent's golden: 0 FAILED; `build_packs.py check` unchanged
- packet made; level stated; nothing called authentic
