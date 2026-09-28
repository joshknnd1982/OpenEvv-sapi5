# Changes

## 1.1.0 - 28 September 2026

145 more languages, read by eSpeak NG and spoken with the OpenEVV voices.

- Every language and dialect eSpeak NG has that openevv does not: 145 language packs, 1,160 more SAPI voices, 1,240 in all. They include the dialects of openevv's own languages that eSpeak NG has -- New York City, Scottish and Caribbean English, Received Pronunciation, Lancaster and West Midlands English, English in the Shavian alphabet, Belgian and Swiss French -- and leave out only the nine eSpeak NG voices openevv's ten already are.
- eSpeak NG reads the text: its spelling rules, dictionary, numbers, letter names and word stress for the language. `OpenEvvFrontend.exe` writes what it read as pronunciations in the phones of one of openevv's own modules, the pack's template, which speaks it. Numbers are read in the language itself.
- The template is chosen for the accent: a relative or a neighbour where openevv has one (the Celtic languages with British English, the Germanic ones with German, Brazilian Portuguese with Latin American Spanish, each dialect with its own language), and otherwise the module whose phones come closest to the language's sounds, weighted by how often the language uses them.
- Each pack's `phonemes.map` is the translation of eSpeak NG's phoneme tables into the template's phones, as a text file that can be edited.
- Word events, sentence events and bookmarks land on the right words in these languages too, and a lone symbol is named in the language's own words. The user dictionaries apply as word replacements before eSpeak NG reads the text.
- About 1.5 ms from `Speak()` to the first audio on a warm voice, as in openevv's own languages.
- eSpeak NG itself was improved first where it could not read numbers in a language (see the eSpeak NG branch `openevv-languages`).
- OpenEVV Configuration: a language read by eSpeak NG says which voice reads it and which module speaks it, its Speak button uses a sentence in the language, and removing a language that others are spoken with warns first.
- The self-test speaks two presets of each eSpeak NG language in each bitness, and `sapi_test` checks every pack, its word events and its latency. `engine\check_espeak_packs.py` holds every pack to its template's module.
- What cannot be brought across: a sound none of openevv's modules has is said as the nearest one, and tone is not spoken, since the modules pause at every change of pitch inside an utterance.

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
