# Questions from the human, with the answers given

Questions the human asked out of curiosity during the TTS extension project, and the answers Claude gave from the code and the data, each dated. (`HUMAN_ANSWERS.md` is the other direction: questions Claude asked and the human's decisions.) The human asked for this file on 2026-10-11 and for it to be committed in Phase 10.

## 2026-10-11 (Phase 9). What files is the speech recogniser recognising speech from: eSpeak NG, native speakers, both, or something else?

**This engine's own output, and nothing else, for the scores in `LANGUAGE_STATUS.md`.** The round trip (`docs/tts-extension/harness/asr.py`) takes up to eight test sentences per language as plain text, has **this engine** (OpenEVV: the IBM-derived module, through the staged front-end, exactly as the product speaks text, preset 1, the adult male voice) render each sentence to a WAV file in a scratch folder (`%TEMP%\OpenEvvTests\harness\asr\<tag>\`), and gives those WAV files to Whisper large-v3 with the language told, not guessed. Whisper's transcript is compared with the sentence text, and the character and word error rates are the score. So a language's CER says how well a recogniser understands *this engine* saying that language.

The sentence texts are not recordings: they are text from Mozilla Common Voice (CC0) and, for languages it lacks, Tatoeba (CC BY 2.0 FR), listed in `docs/tts-extension/harness/asr/sentences.json` with their sources (`REFERENCES.md`). No human voice is transcribed.

Two other things exist beside it, so that the names are not confused:

- **eSpeak NG's own voice** was scored once, in Phase 6 (`harness/asr_espeak.py`, results in `results/asr_espeak.json`): the same sentences and the same recogniser, but spoken by eSpeak NG itself. That is a comparison, not the status score: where eSpeak NG's own voice fails the same sentences, the fault is in the reading of the text (the spelling-to-sound rules both share), not in this engine's sounds.
- **Native speakers' recordings** are never transcribed. The only native-speaker audio in the project is CMU ARCTIC speaker awb (one Scottish man, `third_party/cmu_arctic/`), and it is used in Phase 7 to *measure* vowel formants and lengths for the Scottish English overrides, not for recognition. Native speakers come into the project as reviewers of the A/B packets after Phase 9, by listening, not through the recogniser.

Why it is done this way: the human cannot judge other languages by ear, so intelligibility is measured by a machine that was trained on real speech of each language; a low score is a baseline and a pointer (Whisper is weaker on some languages, and a synthetic voice is far from its training data), not a verdict on its own.
