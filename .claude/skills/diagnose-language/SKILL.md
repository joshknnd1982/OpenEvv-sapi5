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

Read first: `CLAUDE.md`, the language's rows in `docs/tts-extension/LANGUAGE_STATUS.md` and
`docs/tts-extension/TRIAGE_PHASE6.md`, `docs/tts-extension/harness/README.md` (every measure and its
limits). You cannot hear: the listener's words are the symptom, your measurements the evidence.

## Setup (PowerShell, repository root)

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"

## Steps

1. **Hypotheses by layer**: turn the symptom into one or more of: phoneme values (a sound's
   formants, noise, timing), G2P (eSpeak NG's reading: wrong phonemes for the spelling), stress or
   tone, duration and coarticulation, voice or speaker scaling, an engine bug. For each, say what a
   measurement would show if it were the cause, and what it would show if not.
2. **Measure what tells them apart**, cheapest first, each with raw output:
   - the status: `& $py docs\tts-extension\harness\check_language.py <tag>` (checks A, B, the
     ASR result on file, the failure layer; `--asr` runs Whisper again, about a minute);
   - what the reader makes of the text: `& dist\x64\OpenEvvFrontend.exe --data dist\espeak-ng-data
     --voice <voice> --map languages\<tag>\sounds.map --text "<text>"` (the voice is `[ini.Frontend]
     Voice` of `packs/<tag>/pack.toml`) and eSpeak NG's own phonemes for the same text;
   - what the engine said: `& $py docs\tts-extension\harness\engine.py <tag> text "<text>" <out.wav>`
     (the JSON beside the WAV has every frame and phone);
   - per-phoneme measures against references: the golden's data (`harness/golden-staged/<tag>.json.gz`,
     read with `golden.read_golden`) and check B's rows (`check_language.py --json`);
   - what the front-end loses: `& $py docs\tts-extension\harness\diag.py <tag>`;
   - the ASR transcripts: `harness/results/asr.json`, `languages.<tag>.pairs` (reference against
     what Whisper heard), and eSpeak NG's own voice on the same sentences, `harness/results/asr_espeak.json`
     (if it fails the same way, G2P or the reader is first).
   Design a small test of your own when these do not separate the hypotheses (a minimal pair,
   a sound in three vowel contexts) and render it.
3. **Name the most likely cause** with its evidence and your confidence (high, medium, low), and the
   hypotheses ruled out and by what. Say what you could not measure.
4. **Propose a fix**, at that layer, with what it would touch (a pack, the master table, eSpeak NG's
   rules upstream, the engine) and how its success would be measured. Do not apply it.
5. **Report** in plain English: what is wrong, how sure, what fixing would touch. Record the
   diagnosis in `docs/tts-extension/OPEN_QUESTIONS.md` only if the human must decide something
   (as a question with choices, logged in `HUMAN_ANSWERS.md`).
6. **Review**: launch the `tts-reviewer` agent with the "Done when" list and your report's claims.

## Done when

- every hypothesis has a measurement for or against it, shown raw
- the cause is named with confidence and evidence; nothing in the tree was changed
- the proposed fix names its layer and its measure of success
