---
name: diagnose-language
description: Diagnose why a language of the OpenEVV engine sounds wrong, by turning a listener's symptom into hypotheses per layer and measurements that tell them apart; proposes a fix but does not apply it. Use as /diagnose-language <tag> <symptom>.
argument-hint: <tag> <the listener's words>
disable-model-invocation: true
model: opus
effort: high
---

# Diagnose a language: $ARGUMENTS

Playbook Part 3, workflow F. Opus 5.5 at high (set above). This skill measures and reports; it
changes no pack, table or engine file. A fix the evidence supports is then `/improve-language`.

Read first: `CLAUDE.md`; the language's rows in `docs/tts-extension/LANGUAGE_STATUS.md` (the status
table at the top, written by `report.py`, and the Phase 6 triage table further down, which compares
with eSpeak NG's own voice: where their failure layers differ, the triage's is the later and better
evidenced, but measure rather than trust either); `docs/tts-extension/TRIAGE_PHASE6.md` (how the
triage decided); `DESIGN.md` 8 (G2P), 9 (prosody and timing) and 10 (what each check measures);
`docs/tts-extension/harness/README.md` (every measure and its limits). You cannot
hear: the listener's words are the symptom, your measurements the evidence.

## Setup (PowerShell, repository root)

The PowerShell tool keeps no state between calls: start **every** call with these lines.

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"
    $env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-diagnose-<tag>"     # your own scratch renders

## Steps

1. **Hypotheses by layer**: turn the symptom into one or more of: phoneme values (a sound's
   formants, noise, timing), G2P (eSpeak NG's reading: wrong phonemes for the spelling), stress or
   tone, duration and coarticulation (between sounds, across word boundaries), voice or speaker
   scaling, an engine bug, **the recogniser** (Whisper's spelling habits, its language model filling
   in common words) and **the metric** (a word error rate inflates on long words: one wrong letter
   is a wrong word). For each, say what a measurement would show if it were the cause, and if not.
2. **Measure what tells them apart**, cheapest first, each with raw output:
   - the status: `& $py docs\tts-extension\harness\check_language.py <tag>` (checks A, B, the ASR
     result on file, the failure layer; `--asr` runs Whisper on the standard sentences again);
   - **your own sentences through the recogniser**:
     `& $py docs\tts-extension\harness\asr_try.py <tag> "<sentence>" "<variant>" ...` (writes
     nothing): the same sentence with a comma at a word boundary, a word alone, a respelling;
   - what the reader makes of the text: eSpeak NG's phonemes,
     `& "$env:LOCALAPPDATA\OpenEvvBuild\frontend-x64\bin\espeak-ng.exe" --path=dist -v <voice> -q -x "<text>"`
     (the voice is `[ini.Frontend] Voice` in `packs/<tag>/pack.toml`; `_|` and `_!` are its short
     pauses), and what the front-end tells the engine,
     `& dist\x64\OpenEvvFrontend.exe --data dist\espeak-ng-data --voice <voice> --map languages\<tag>\sounds.map --text "<text>"`
     (`--map` takes `sounds.map`, the file with the language's own sounds `sN`);
   - what the engine said: `& $py docs\tts-extension\harness\engine.py <tag> text "<text>" <out.wav>`
     (the JSON beside the WAV has every frame and phone with its times; `harness/analysis.py`
     measures formants, F0, intensity, noise and stop timing from Python);
   - per-phoneme measures against references: check B's rows (`check_language.py <tag> --json <file>`);
   - what the front-end loses: `& $py docs\tts-extension\harness\diag.py <tag>` (always name the tag:
     without one it rewrites the tracked `results/diag.json`);
   - the ASR transcripts on file: `harness/results/asr.json`, `languages.<tag>.pairs`, and eSpeak
     NG's own voice on the same sentences, `harness/results/asr_espeak.json` (if it fails the same
     way, G2P or the reader comes first; if it fails differently, compare where).
   Design a small test of your own when these do not separate the hypotheses (a minimal pair, a
   sound in three vowel contexts, a word boundary with and without a pause) and render it.
3. **Name the most likely cause** with its evidence and your confidence (high, medium, low), the
   share of the symptom each cause explains where you can measure it, the hypotheses ruled out and
   by what, and what you could not measure.
4. **Propose a fix**, at that layer, with what it would touch (a pack, the master table, eSpeak NG's
   rules upstream, the front-end, the engine) and how its success would be measured (numbers to
   reach). Do not apply it.
5. **Report** in plain English: what is wrong, how sure, what fixing would touch. Record the
   diagnosis in `docs/tts-extension/OPEN_QUESTIONS.md` as a finding for an `/improve-language`
   session (and, if the human must choose something, as a question with choices, logged in
   `HUMAN_ANSWERS.md`). Do not run `asr.py` or `report.py` (they rewrite tracked results).
6. **Review**: launch the `tts-reviewer` agent with the "Done when" list and your report's claims. If
   you cannot launch agents, say that the review is still owed.

## Done when

- every hypothesis has a measurement for or against it, shown raw
- the cause is named with confidence and evidence; nothing in the tree was changed but the finding
- the proposed fix names its layer and its measure of success
