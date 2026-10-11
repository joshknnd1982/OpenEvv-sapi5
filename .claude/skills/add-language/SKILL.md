---
name: add-language
description: Add a new language to the OpenEVV TTS engine as a data-only pack, measured and honestly levelled. Use as /add-language <name> [eSpeak NG voice] [tag].
argument-hint: <language name> [espeak voice, e.g. bnt/sw] [tag]
disable-model-invocation: true
model: sonnet
effort: medium
---

# Add a language: $ARGUMENTS

Playbook Part 3, workflow A. Recommended model: Sonnet 5.5 at medium (set above); Opus 5.5 high for
hard phonology; Fable 5.1 high for tonal, click or heavy-sandhi languages. If the language is one of
those and you are not that model, say so first and stop (the playbook's MODEL SWITCH NEEDED pause).

Read first: `CLAUDE.md`, `ADDING_A_LANGUAGE.md` section 3 (the worked example `sw-x-evvdemo` is this
skill run end to end, every command with its output), `docs/tts-extension/PROJECT_STATE.md`;
`DESIGN.md` 6 (packs) and 8 (G2P) as needed. You cannot hear: every claim about sound is a
measurement shown with its raw output (R2, R5, R16).

## Setup (PowerShell, repository root)

The PowerShell tool keeps no state between calls: start **every** call with these lines (and
`$S`, `$G`, `$tag` once you have them).

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"
    # beside another session: $env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-<tag>"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Research** (R3, R4; a research subagent if you can launch one, else yourself). Inventory,
   phonotactics, stress or tone, spelling-to-sound, reference recordings and their licences. Cite
   each source in `docs/tts-extension/REFERENCES.md` and register it in `ipa/sources.toml`
   (`opened = true` only if read). Say plainly what you could not find. Stop researching once you
   have the inventory, the stress or tone system, the spelling rules and one descriptive source
   (about an hour at most): a language with no open acoustic study stays at level 2, and saying so
   is the right outcome.
2. **Reader.** A pack is read by an eSpeak NG voice: `Test-Path dist\espeak-ng-data\lang\<voice>`
   (the voices are the files under `dist/espeak-ng-data/lang/`; to find one by language code:
   `Get-ChildItem dist\espeak-ng-data\lang -Recurse -File -Filter <code>`, the voice is
   `<folder>/<code>`, e.g. `urj/fi`). If the voice you were given does not exist but one reads the
   language, use it and say so. No voice at all means no reader: stop and report (a reader written
   in a pack is DESIGN.md L5, not built). Start the pack (the tag: BCP 47, lower case; a test copy
   gets `-x-`):

       & $py engine\packs\new_language.py <voice> <tag> --out packs-proposed --name "<Name>"

3. **Write the pack** (`packs-proposed/<tag>/pack.toml`; `engine/packs/packlib.py` has the format):
   `[meta]` sources, licence, a `note` and `status = { level = 1, validated_by = "", date = "" }`
   (the generator writes no status; 1 is draft until step 8); a test copy keeps its original's
   `Order` in `[ini.Language]`, a pack that will ship takes a number no other pack uses; every
   hand-changed value as an `[[override]]` with its
   provenance tag and `ref` (`engine/packs/overrides.py`). Beside it, `review.toml` (the shape of
   `docs/tts-extension/examples/packs/sw-x-evvdemo/review.toml`): `[words] list` and, if the tag has
   no ASR sentences, `[sentences] list` and `source`.
4. **Measure** in a scratch copy of the stage (never `languages/`):

       $tag='<tag>'; $S="$env:TEMP\OpenEvvTests\stage-$tag"; $G="$env:TEMP\OpenEvvTests\golden-$tag"
       Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S     # once
       & $py engine\packs\build_packs.py build "$S\languages" $tag
       $env:EVV_STAGE=$S
       & $py docs\tts-extension\harness\engine.py $tag text "<a sentence>" "$env:TEMP\OpenEvvTests\$tag.wav"
       & $py docs\tts-extension\harness\golden.py $tag --record --golden $G
       & $py docs\tts-extension\harness\check_language.py $tag --golden $G --asr

   ASR needs the tag in `harness/asr/sentences.json` (CC0 or CC BY sentences, source recorded) and
   `asr/whisper_codes.json`; a test copy borrows its original's with `--asr-like <tag>`. If Whisper
   lacks the language, the result is "ASR unavailable" with its reason: say so. Check A passes with
   a few misses (most formant and pitch readings within tolerance); read the misses it prints. Check
   A passing, no references and a CER above 0.15 is level 2 with failure layer "unknown"; that is
   not a dead end but the entry point of `/diagnose-language`, say so in the report. The labels
   `f|h`, `s|?` are golden case ids (kind letter, bar, eSpeak NG phoneme name; `ADDING_A_LANGUAGE.md`
   step 5).
5. **Map every phoneme.** `check_language.py` lists the phonemes with "no phone of their own" (said
   only as breath, a hush or a mark on a neighbour). Look each one up in the master table
   (`& $py engine\ipa\coverage.py`, `ipa/table/*.toml`) and say how it is made. A sound the table
   lacks: run `/create-missing-sound` (Fable 5.1). Never leave a phoneme silent or silently
   substituted (R7, R19).
6. **Regression**: `& $py docs\tts-extension\harness\golden.py` under your scratch stage `$S`
   (every existing language and your pack, 0 FAILED; 25 to 40 minutes), then
   `$env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"` and `& $py engine\doctor.py --quick`.
   A tagless run rewrites the tracked `results/diag-golden-staged.json`: never run it while another
   session runs the golden or the doctor; if you must wait, say so and run the parent packs by tag
   (`golden.py <tags>`) meanwhile.
7. **Packet**, under the scratch stage, after step 8's status is written (the packet's README copies
   `[meta] status`): `& $py engine\review\make_packet.py $tag` (a test pack:
   `--out docs\tts-extension\examples\packets\$tag`). It also writes its key to
   `docs/tts-extension/review/keys/<tag>.json`; a matplotlib `RuntimeWarning` on stderr is harmless
   (PowerShell shows it as a red error record; the `packet <tag>:` line is what counts).
8. **Status**: the TRUE level `check_language.py` printed (1 draft, 2 check A, 3 check B, 4 ASR at
   or under 0.15; level 2 is the usual result while check B has no references for the language;
   never 5 without a named reviewer) in the pack's `[meta] status = { level = N, validated_by = "", date = "" }` and, for a real language,
   `docs/tts-extension/LANGUAGE_STATUS.md` with its failure layer. A test pack records nothing there.
9. **Report** in plain English: what was done, the level, which sounds are created, approximate or
   estimated, what a native reviewer should check first (the packet's flagged items). Shipping it
   (moving the pack into `packs/` and building `languages/<tag>/`, `ADDING_A_LANGUAGE.md` section 8)
   waits for the human's say-so (R18, D34).
10. **Review**: launch the `tts-reviewer` agent with the "Done when" list below and the changed
    paths; fix real gaps (one re-review at most, R15). If you cannot launch agents, say that the
    review is still owed.

## Done when

- the pack builds; every phoneme has a sound, none silent; the ones with no phone of their own explained
- check A, check B and ASR (or "unavailable" with the reason) shown with raw output
- the golden regression of every existing language: 0 FAILED, output shown
- the packet made; the level stated and justified; sources cited with licences
