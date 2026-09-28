# Changes

## 1.0.0 - 28 September 2026

First release.

- The openevv engine (IBM Embedded ViaVoice, the Eloquence voice) as SAPI 5 voices for 32-bit and 64-bit programs. It is built from openevv 7148737 (Mudb0y/openevv main as of 28 September 2026).
- Ten languages with eight voices each, 80 SAPI voices: US and British English, German, Castilian and Latin American Spanish, French and Canadian French, Italian, Japanese, and Polish (experimental).
- Language packs: a language is a folder with `language.ini` and two engine modules. Add one from a downloaded `.zip` with OpenEVV Configuration, or by copying the folder into `%ProgramData%\OpenEVV\languages`; its voices appear in every SAPI 5 program at once.
- OpenEVV Configuration:
  - every parameter of every voice
  - sample rate and resampler, speed range, rate boost and pitch step
  - abbreviations, number reading and text modes
  - annotations, heteronym fixes and user dictionaries
  - language pack management, logging and a self-test
  - every change heard at once in every program
- About 1.5 ms from `Speak()` to the first audio on a warm voice; cancels return at once.
- The installer installs everything, tests every voice in both bitnesses, logs to `%ProgramData%\OpenEVV\Logs`, and works with screen readers.
