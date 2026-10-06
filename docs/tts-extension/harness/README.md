# The measurement harness (Phase 1; extended in Phase 3)

Replaces listening with measurement. Nothing here changes the engine: it drives the shipped modules (or, under `EVV_STAGE`, rebuilt ones) through the product's own host and reads the logs the modules already write.

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
| Add cases the golden lacks, only if every case it has is unchanged | `python docs/tts-extension/harness/golden.py --record-new [tags]` | as the golden |
| Render and compare (or, with `--record-new`, add) only the cases a golden folder lacks | `golden.py ... --only-missing-from <folder>` (also `a3.py`, which then writes `results/a3[-staged]-new.json`) | minutes |
| Check A3: voiceless sounds and pauses stay unvoiced (with the pack's definitions against without) | `python docs/tts-extension/harness/a3.py [tags]` | ~ 30 min for all |
| Stage rebuilt template modules in a data folder (never `languages/`) | `python docs/tts-extension/harness/stage.py <built modules> <stage folder> [tags]` | seconds |
| What the front-end loses on the way (C1): count it over every golden input and sentence; `--compare OLD.exe` also proves the output byte-identical to an older front-end's; `--plant` plants each kind of fault and checks it is reported | `python docs/tts-extension/harness/diag.py [--compare OLD.exe \| --plant] [tags]` | ~ 5 s |
| The same for the accent layer, through the staged modules (planted markup faults, each must be reported) | `python docs/tts-extension/harness/diag.py --plant-accent` (needs `EVV_STAGE`) | ~ 5 s |
| The template comparison: five languages built for all seven templates in a scratch stage, checks A, B and ASR (DESIGN.md 13.2) | `python docs/tts-extension/harness/template_compare.py [--langs ...] [--no-asr]` (needs `EVV_STAGE`) | ~ 15 min |
| The master table: validate it, its self-test, coverage of the chart | `python engine/ipa/table.py [--selftest]`, `python engine/ipa/coverage.py` | seconds |
| Read IPA (C2), and its tests | `python engine/ipa/reader.py "<IPA>"`, `python engine/ipa/reader.py --test` | seconds |
| Realise an entry for a template; write ipa/realized/<template>.map | `python engine/ipa/adapter.py <id> [template]`, `adapter.py --write <template>` | seconds |
| Realise, render, measure, correct (up to five rounds): ipa/proofs/<id>.json | `python engine/ipa/prove.py <id> [--template dedx] [--pack hi]` | ~ 1 min |
| Composition when speaking (C4): the front-end against the adapter, and the fallbacks | `python engine/ipa/compose_test.py` | seconds |
| ASR round trip | `python docs/tts-extension/harness/asr.py [tags]` | ~ 20 min on the GPU |
| Status of every language: LANGUAGE_STATUS.md, reports/index.html | `python docs/tts-extension/harness/report.py` | ~ 1 min |
| Second opinion from Praat (GPL file) | `python docs/tts-extension/harness/praat_crosscheck.py` | ~ 20 s |

Examples:

    python docs/tts-extension/harness/engine.py hi ipa "ʈəˈmaːʈər" %TEMP%\t.wav
    python docs/tts-extension/harness/engine.py enus module "`[.1hEl.0o]" %TEMP%\h.wav --preset 2
    python docs/tts-extension/harness/engine.py hi text "नमस्ते" %TEMP%\n.wav --override "s5 f2=91 vot=80"

## Staged modules (Phase 3, DESIGN.md 11.2)

Changes to the engine reach the product only in rebuilt template modules. They are built outside the repository (`engine/build_modules.sh`), staged with `stage.py` in a data folder, and measured by setting `EVV_STAGE` to that folder: the product reads its `languages\<tag>\` before the shipped one, so the staged module speaks and `languages/` is never touched. A front-end staged as `<stage>d\OpenEvvFrontend.exe` is used before `dist`'s (`EVV_FRONTEND` names another). Under `EVV_STAGE` the golden reads and writes `golden-staged/` (the staged modules' own golden) and A3 writes `results/a3-staged.json`; `golden.py --golden <folder>` compares with another golden (the baseline proof compares staged modules with `golden/`). `golden/` always describes the modules in `languages/`; at a replacement point the staged modules and their golden replace the shipped ones together.

## Files

| File | What |
|---|---|
| `engine.py` | Rendering: inputs, the fresh host per case, the logs, cutting the case out of them, retries |
| `ipa.py` | IPA to eSpeak NG phoneme names or to a module's own phones; fails loudly, never substitutes |
| `analysis.py` | Measures: formants (Burg LPC), F0, intensity, spectral moments and band edges, stop timing and VOT, nasal antiformant, tone contour; what the frames requested |
| `synth.py` | Synthetic signals with known answers, for the self-tests |
| `selftest.py` | The harness's own proof |
| `reference.py`, `reference/ranges.json` | The reference-range store (cited values only) and check B |
| `golden.py`, `golden/<tag>.json.gz` | The golden regression: metrics and hashes, not audio; every phoneme a pack maps, borrowed ones through eSpeak NG's table switch, and from Phase 3 every consonant again before a voiceless consonant and at the end before the pause (`x|` cases); what cannot be rendered is listed per pack as `not_covered`. `golden-staged/`: the same for staged modules |
| `a3.py`, `results/a3.json` | Check A3 on the `x|` cases: what is meant voiceless or silent stays so |
| `stage.py` | Stages rebuilt template modules in a data folder |
| `diag.py`, `results/diag.json` | C1: what the front-end loses on the way, per pack; the planted faults |
| `asr.py`, `asr/` | The ASR round trip; `asr/sentences.json` (CC0 / CC BY sentences), `asr/whisper_codes.json` |
| `report.py`, `results/` | Status levels, failure layers, LANGUAGE_STATUS.md, `../reports/index.html` |
| `template_compare.py`, `results/template_compare.json` | The template comparison of Phase 3A |
| `results/diag-golden[-staged].json` | What the front-end and the accent layer reported over a full golden run (C1), per pack |
| `smoke.py` | The one-minute check |
| `praat_crosscheck.py` | **GPL v3 or later** (imports Parselmouth); everything else here is MIT |

`src/tools/evv_render.cpp` is the renderer these drive: `evv_say` for a list of cases, ending its host cleanly so the engine's frame log is complete.

## What a rendering's JSON holds

`input` (kind, text, what was said, the front-end's annotated output), `rate`, `n_samples`, `case_ms`, `wav_sha256`, `segmentation` (`trace` or `runs`), `attempts`, `frames` (the 62 parameters of every frame, names in `frames.names`), and `phones`: name, the phone it was meant to be, its sound (`sN` in the pack's sounds.map), tone, stress, the module's phone record, `start_ms`, `end_ms`. `diag`: what the front-end and the accent layer reported losing on the way (C1: source, level `loss` or `note`, kind, detail, count); with `EVV_STRICT=1` a loss fails the render.

## Known limits (written down, not hidden)

- IPA tone letters (˥˦˧˨˩) are not converted yet; a pack's tones come from its text. IPA input for frca, jajp and plpl needs a phone-to-IPA table those modules lack; their annotation input works.
- Module phones whose names hold `:` or `~` (German `E: a~ E~ o~ oe~`, French nasals): unquoted, the module speaks the annotation as text. From Phase 3 the golden writes them in single quotes (`` `[.1t'E:'t] ``, `DECISIONS.md` D30), so none is `not_covered`; the words that reached them before stay as cases too.
- Check B cannot use the store's VOT or fricative values (means without a published spread) or its tone values (no tone cases until Phase 4); of the consonants, only the general nasal ranges are checked.
- Nine native modules (all but enus) do not know the accent layer's markup, so their phones are segmented by the array log's runs, labelled only when the input named the phones.
- IPA, eSpeak-phoneme and override renders of a pack read by eSpeak NG go through `--annotated`: the product's frames (selftest.py proves it), but a different warm-up, so the noise generator's samples differ from the product's.
