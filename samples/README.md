# Samples

Every preset voice of every language, rendered straight from the engine modules by `engine/render_samples.py` (each language's own `evv.exe`, built beside its modules): no SAPI, no registry, no installer. 11,025 Hz, the engine's own rate.

- `<tag>-all-voices.wav`: all eight voices of a language in a row, voice 1 to voice 8, each saying its number.
- `<tag>/<tag>-voice<n>.wav`: one voice.
- `render-report.txt`: the length of each render.

The voices, in order: Adult Male 1, Adult Female 1, Child 1, Adult Male 2, Adult Male 3, Adult Female 2, Elderly Female 1, Elderly Male 1.

The tags: `enus` US English, `engb` British English, `dede` German, `eses` Castilian Spanish, `esus` Latin American Spanish, `frfr` French, `frca` Canadian French, `itit` Italian, `plpl` Polish (experimental), `jajp` Japanese.
