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

Read first: `CLAUDE.md`, `ADDING_A_LANGUAGE.md` section 4 (the dialect example `ca-va-x-evvdemo`,
every command with its output), `docs/tts-extension/AUTHENTICITY.md` (the validator's rules M1-M6
and A1-A4, the anti-caricature rules), `DESIGN.md` 6.3 (inheritance). You cannot hear: measure (R2,
R5, R16).

## Setup (PowerShell, repository root)

The PowerShell tool keeps no state between calls: start **every** call with these lines (and
`$S`, `$G`, `$tag` once you have them).

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"
    $env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-<tag>"    # a work folder of your own: required beside another session, harmless alone
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Define the variety precisely** (R14): region, speaker group, era. Find descriptive sources and
   licensed recordings (R3, R4; a research subagent if you can launch one, else yourself); register
   each in `ipa/sources.toml` (`opened = true` only if read; say which tables or pages were used) and
   `REFERENCES.md`. No source and no recordings: say so; such a dialect cannot pass the validator
   (M2) and must not be invented. A table read from a PDF's text layer may have its symbol columns
   garbled: decode them from the paper's own vowel list, say so in the pack's note, and have the
   reviewer check the reading. A paper under a publisher's copyright is cited, never kept; only a
   file whose licence allows it goes in `third_party/` with the licence in `NOTICE.md`.
2. **List the differences** from the parent: mergers and shifts, consonant realizations, allophone
   rules, stress and rhythm, intonation, lexical sets; each with its source or measurement. No
   stage dialect, no eye-dialect, a variable feature only at the frequency a source gives.
3. **Turn vowel evidence into targets.**
   - *Recordings*: `& $py engine\authenticity\extract_targets.py <tag> <corpus> --write` (needs
     `measure.toml`; AUTHENTICITY.md steps 2-3).
   - *A published table* (group means in Hz): key each value by the reader's phoneme name and let
     the normalizer put it at the module voice's size and compare it with what the pack says now:

         & $py engine\authenticity\normalize.py <parent> <phoneme>=<F1>,<F2> ... --anchor <phonemes>

     `--anchor` lists the classes the size factor is taken over (the table's vowels the module also
     has as plain phones; leave out those the dialect moves). Give F3 only if the table has it.
   - *Phoneme names*: what the reader writes for a word: `& "$env:LOCALAPPDATA\OpenEvvBuild\frontend-x64\bin\espeak-ng.exe"
     --path=dist -v <voice> -q -x "<words>"`; the pack's `map` line of that name: search
     `packs/<parent>/pack.toml` for `kind = "map", name = "@<voice>:<phoneme>"` (the name carries the
     voice prefix, `@nl:A`; the reader's plain `a e i o u y` may have a line of their own, and
     `build_packs.py explain` does not find map lines). `normalize.py` and an `[[override]]` are keyed
     by that full name (`@nl:A`, not `A`). Every phoneme that says the sound needs the override: the
     map lines with the same `to = "<sound>"` (search for it; e.g. `@en-us-nyc:a` and `@en-us-nyc:aa`).
   - **Write an override only where F1 or F2 moves more than 6 per cent** from what the pack says now
     (`normalize.py` prints "override" or "within 6%"): measurement changes only what it shows to
     differ. Values from a table and a rule are `derived` with the source as `ref` and the rule in `norm`.
     Run the table's other variety (or the parent's own region) through `normalize.py` as well, and say
     in the note which overrides carry the dialect's difference and which only correct the parent
     toward the language's own values (Phase 9's Belgian Dutch trial: 4 of 11 were corrections).
4. **Write the pack** `packs-proposed/<tag>/pack.toml` (create the folder with `New-Item -ItemType
   Directory`; a fresh clone has no `packs-proposed/`): `kind = "dialect"`, `extends = "<parent>"`,
   only what differs: `[meta]` (variety, region, speaker_group, sources, recordings, date, status;
   `licence` is inherited from the parent unless the dialect's differ), `[ini.Language]` Tag, Name
   and Order (its place in the voice list: any number no other pack uses; `Select-String -Path
   packs\*\pack.toml,packs-proposed\*\pack.toml -Pattern 'Order = "\d+"'` lists the taken ones, 290 to
   309 and 913 to 992 today, so 1000 and up are free), the reader's
   `[ini.Frontend] Voice` if the dialect has its own eSpeak NG voice, and each vowel change as an
   `[[override]]` (`state = "proposed"`; never `estimated`). Copy the shape of
   `docs/tts-extension/examples/packs/ca-va-x-evvdemo/`. Write `review.toml` beside it: `[words]
   list`, `[sentences] list` and `source` if the tag has no ASR sentences, and one `[[check]]` (`sound`,
   `words`, `question`) per overridden sound. A difference no override can express (a merger, an
   allophone rule) goes in the note as **not made**; never hand-edit `[sounds]` lines in a dialect.
5. **Validate and measure** in a scratch stage (`$S` is a copy of the shared stage):

       $tag='<tag>'; $S="$env:TEMP\OpenEvvTests\stage-$tag"; $G="$env:TEMP\OpenEvvTests\golden-$tag"
       & $py engine\packs\validate_packs.py $tag          # "accepted"
       Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S     # once
       & $py engine\packs\build_packs.py build "$S\languages" $tag
       $env:EVV_STAGE=$S
       & $py engine\authenticity\show_effect.py $tag       # each override: F1/F2 before, after, target
       & $py docs\tts-extension\harness\golden.py $tag --record --golden $G
       & $py docs\tts-extension\harness\check_language.py $tag --golden $G --asr --asr-like <parent>

   The stage holds the pack **without** its proposed overrides (what would ship today);
   `show_effect.py` makes the "after" version itself. To check that the overrides keep check A,
   build again with `--proposed` into `$S`, record into another golden folder, check, then build
   without it again. Check A passes with a few misses (it needs most of its formant and pitch
   readings within tolerance); read the misses it prints. Report the CER with and without the
   overrides: a rise of more than 0.05 goes in the note and to the human (the recogniser is tuned to
   the standard variety, so a rise does not show the vowels wrong, but it is never hidden; Phase 9's
   trial: 0.199 to 0.293). A word that `show_effect.py` shows the override does not reach (moved by
   less than half its gap: its phoneme is not the one the override names) is named in the note and
   either given its own override or taken out of `review.toml`, so the packet does not ask an A/B
   question whose two sides are the same.
6. **The parent is unaffected**: `$env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"`;
   `& $py docs\tts-extension\harness\golden.py <parent>` (0 FAILED, a minute or two);
   `& $py engine\packs\build_packs.py check` (every file identical).
7. **Packet**, under the scratch stage, after step 8's status is written (the packet's README copies
   it): `& $py engine\review\make_packet.py $tag` (a real pack: no `--out`, it goes to
   `docs/tts-extension/review_packets/<tag>/`; a test pack:
   `--out docs\tts-extension\examples\packets\$tag`). It also writes the blind A/B key to
   `docs/tts-extension/review/keys/<tag>.json`. A matplotlib `RuntimeWarning` on stderr is harmless
   (PowerShell shows it as an error; the packet line printed is what counts).
8. **Status and report**: the pack's `[meta] status` level is what `check_language.py` printed for
   the pack as built in step 5 (without proposed overrides); level 2 is the usual result while check
   B has no references for the language; never 5 without a named reviewer. For a real dialect,
   `LANGUAGE_STATUS.md` too. Report in plain English which claims are measured, which from
   literature, which differences are not made. Shipping waits for the human's say-so.
9. **Review**: launch the `tts-reviewer` agent with the "Done when" list and the changed paths. If
   you cannot launch agents, say that the review is still owed.

## Done when

- `validate_packs.py <tag>` accepts the pack; it holds only differences from its parent
- every override moves its vowel by more than 6 per cent, has a source, and its effect is measured and shown
- the parent's golden: 0 FAILED; `build_packs.py check` unchanged
- packet made; level stated and equal to the measurement; nothing called authentic
