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

Read first: `CLAUDE.md`, `ADDING_A_LANGUAGE.md` (the worked example `sw-x-evvdemo` is this skill run
end to end), `docs/tts-extension/PROJECT_STATE.md`; `DESIGN.md` 6 (packs) and 9 (G2P) as needed.
You cannot hear: every claim about sound is a measurement shown with its raw output (R2, R5, R16).

## Setup (PowerShell, repository root)

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"
    & $py engine\doctor.py --quick          # must end "0 FAILED" before you start

## Steps

1. **Research** (R3, R4; delegate to a research subagent). Inventory, phonotactics, stress or tone,
   spelling-to-sound, reference recordings and their licences. Cite each source in
   `docs/tts-extension/REFERENCES.md` and register it in `ipa/sources.toml` (`opened = true` only
   if read). Say plainly what you could not find.
2. **Reader.** A pack is read by an eSpeak NG voice (`dist/espeak-ng-data/lang/<voice>`); find the
   language's voice. No voice means no reader: stop and report (a reader written in a pack is
   DESIGN.md L5, not built). Start the pack (the tag: BCP 47, lower case; a test copy gets `-x-`):

       & $py engine\packs\new_language.py <voice> <tag> --out packs-proposed --name "<Name>"

3. **Map every phoneme.** The generator maps each of the voice's phonemes onto the template's
   phones; list what has no phone of its own (step 5's `phonemes with no phone of their own`) and
   look each one up in the master table (`python engine\ipa\coverage.py`, `ipa/table/*.toml`).
   A sound the table lacks: run `/create-missing-sound` (Fable 5.1). Never leave a phoneme silent or
   silently substituted (R7, R19).
4. **Write the pack** (`packs-proposed/<tag>/pack.toml`; `engine/packs/packlib.py` has the format):
   `[meta]` sources and licence, a `note`; every hand-changed value as an `[[override]]` with its
   provenance tag and `ref` (`engine/packs/overrides.py`); words for the packet in `review.toml`.
5. **Measure** in a scratch copy of the stage (never `languages/`):

       $S="$env:TEMP\OpenEvvTests\stage-<tag>"; Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S
       & $py engine\packs\build_packs.py build "$S\languages" <tag>
       $env:EVV_STAGE=$S
       & $py docs\tts-extension\harness\engine.py <tag> text "<a sentence>" "$env:TEMP\OpenEvvTests\<tag>.wav"
       & $py docs\tts-extension\harness\golden.py <tag> --record --golden "$env:TEMP\OpenEvvTests\golden-<tag>"
       & $py docs\tts-extension\harness\check_language.py <tag> --golden "$env:TEMP\OpenEvvTests\golden-<tag>" --asr

   ASR needs the tag in `harness/asr/sentences.json` (CC0 or CC BY sentences, source recorded) and
   `asr/whisper_codes.json`; if Whisper lacks the language, say "ASR unavailable" and why.
6. **Regression**: `$env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"`, then
   `& $py docs\tts-extension\harness\golden.py` (every existing language, 0 FAILED) and
   `& $py engine\doctor.py --quick`.
7. **Packet**: `& $py engine\review\make_packet.py <tag>` under the scratch stage (a test pack:
   `--out docs\tts-extension\examples\packets\<tag>`).
8. **Status**: the TRUE level from step 5 (1 draft, 2 check A, 3 check B, 4 ASR at or under 0.15;
   never 5 without a named reviewer) in the pack's `[meta] status` and, for a real language,
   `docs/tts-extension/LANGUAGE_STATUS.md` with its failure layer. A test pack records nothing there.
9. **Report** in plain English: what was done, the level, which sounds are created, approximate or
   estimated, what a native reviewer should check first. Shipping it (moving the pack into `packs/`
   and building `languages/<tag>/`) waits for the human's say-so (R18, D34).
10. **Review**: launch the `tts-reviewer` agent with the "Done when" list below and the changed paths;
    fix real gaps (one re-review at most, R15).

## Done when

- the pack validates (`validate_packs.py <tag>`) and builds; every phoneme has a sound, none silent
- check A, check B and ASR (or "unavailable" with the reason) shown with raw output
- the golden regression of every existing language: 0 FAILED, output shown
- the packet made; the level stated and justified; sources cited with licences
