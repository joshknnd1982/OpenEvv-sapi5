# The measurement harness (Phase 1)

Replaces listening with measurement. Nothing here changes the engine: it drives the shipped modules through the product's own host and reads the logs the modules already write.

## Setup (once)

1. Build the wrapper and tools, including `evv_render.exe` (git-ignored output):

       cmake -G "Visual Studio 17 2022" -A x64 -S . -B build_x64
       cmake --build build_x64 --config Release

2. A Python 3.10 venv **outside the repository**, with numpy, scipy, matplotlib, jiwer, soundfile, faster-whisper and (for `praat_crosscheck.py` only) praat-parselmouth. On this machine it is `%USERPROFILE%\OpenEvvBuild-ttsext\venv`. Make it under your user folder, not `%LOCALAPPDATA%`: from inside the Claude app, Windows redirects new `%LOCALAPPDATA%` folders into the app's private storage.

       python -m venv %USERPROFILE%\OpenEvvBuild-ttsext\venv
       %USERPROFILE%\OpenEvvBuild-ttsext\venv\Scripts\python -m pip install numpy scipy matplotlib jiwer soundfile faster-whisper praat-parselmouth nvidia-cublas-cu12==12.8.4.1

3. For ASR, Whisper large-v3 for CTranslate2 (`Systran/faster-whisper-large-v3`, revision `edaa852e`, MIT, 3.09 GB) in `%USERPROFILE%\OpenEvvBuild-ttsext\models\faster-whisper-large-v3`, or wherever `EVV_WHISPER_MODEL` says.

Every command below runs from the repository root with that venv's `python` and `PYTHONUTF8=1`. Scratch audio goes to `%TEMP%\OpenEvvTests\harness` (or `EVV_HARNESS_WORK`), never into OneDrive.

## Commands

| What | Command | Time |
|---|---|---|
| Render one case: WAV + JSON of every frame and phone | `python docs/tts-extension/harness/engine.py <tag> <text\|ipa\|espeak\|module\|annotated> "<input>" out.wav [--preset N] [--override "sN key=value ..."]` | < 1 s |
| Self-tests (analyser on synthetic signals, engine facts) | `python docs/tts-extension/harness/selftest.py` | ~ 1 min |
| Smoke check | `python docs/tts-extension/harness/smoke.py` | < 1 min |
| Full golden regression (every phoneme of every language) | `python docs/tts-extension/harness/golden.py` (exit 1 on drift) | ~ 7 min |
| Record the golden again after an intended change (and write it in DECISIONS.md) | `python docs/tts-extension/harness/golden.py --record [tags]` | ~ 7 min |
| ASR round trip | `python docs/tts-extension/harness/asr.py [tags]` | ~ 20 min on the GPU |
| Status of every language: LANGUAGE_STATUS.md, reports/index.html | `python docs/tts-extension/harness/report.py` | ~ 1 min |
| Second opinion from Praat (GPL file) | `python docs/tts-extension/harness/praat_crosscheck.py` | ~ 20 s |

Examples:

    python docs/tts-extension/harness/engine.py hi ipa "ʈəˈmaːʈər" %TEMP%\t.wav
    python docs/tts-extension/harness/engine.py enus module "`[.1hEl.0o]" %TEMP%\h.wav --preset 2
    python docs/tts-extension/harness/engine.py hi text "नमस्ते" %TEMP%\n.wav --override "s5 f2=91 vot=80"

## Files

| File | What |
|---|---|
| `engine.py` | Rendering: inputs, the fresh host per case, the logs, cutting the case out of them, retries |
| `ipa.py` | IPA to eSpeak NG phoneme names or to a module's own phones; fails loudly, never substitutes |
| `analysis.py` | Measures: formants (Burg LPC), F0, intensity, spectral moments and band edges, stop timing and VOT, nasal antiformant, tone contour; what the frames requested |
| `synth.py` | Synthetic signals with known answers, for the self-tests |
| `selftest.py` | The harness's own proof |
| `reference.py`, `reference/ranges.json` | The reference-range store (cited values only) and check B |
| `golden.py`, `golden/<tag>.json.gz` | The golden regression: metrics and hashes, not audio; every phoneme a pack maps, borrowed ones through eSpeak NG's table switch; what cannot be rendered is listed per pack as `not_covered` |
| `asr.py`, `asr/` | The ASR round trip; `asr/sentences.json` (CC0 / CC BY sentences), `asr/whisper_codes.json` |
| `report.py`, `results/` | Status levels, failure layers, LANGUAGE_STATUS.md, `../reports/index.html` |
| `smoke.py` | The one-minute check |
| `praat_crosscheck.py` | **GPL v3 or later** (imports Parselmouth); everything else here is MIT |

`src/tools/evv_render.cpp` is the renderer these drive: `evv_say` for a list of cases, ending its host cleanly so the engine's frame log is complete.

## What a rendering's JSON holds

`input` (kind, text, what was said, the front-end's annotated output), `rate`, `n_samples`, `case_ms`, `wav_sha256`, `segmentation` (`trace` or `runs`), `attempts`, `frames` (the 62 parameters of every frame, names in `frames.names`), and `phones`: name, the phone it was meant to be, its sound (`sN` in the pack's sounds.map), tone, stress, the module's phone record, `start_ms`, `end_ms`.

## Known limits (written down, not hidden)

- IPA tone letters (˥˦˧˨˩) are not converted yet; a pack's tones come from its text. IPA input for frca, jajp and plpl needs a phone-to-IPA table those modules lack; their annotation input works.
- Module phones whose names hold `:` or `~` (German `E: a~ E~ o~ oe~`, French nasals) cannot be written in an annotation: the module speaks the annotation as text. The golden reaches them through words, and lists them as `not_covered`.
- Check B cannot use the store's VOT values (means without a published spread) or its tone values (no tone cases until Phase 4).
- Nine native modules (all but enus) do not know the accent layer's markup, so their phones are segmented by the array log's runs, labelled only when the input named the phones.
- IPA, eSpeak-phoneme and override renders of a pack read by eSpeak NG go through `--annotated`: the product's frames (selftest.py proves it), but a different warm-up, so the noise generator's samples differ from the product's.
