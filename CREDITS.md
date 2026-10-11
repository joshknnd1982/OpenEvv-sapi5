# Credits

OpenEVV SAPI5 stands on other people's work. This file says whose, and on what terms each part is redistributed.

## The engine: openevv

[openevv](https://github.com/Mudb0y/openevv), by Stanislaw Przedzinkowski (Mudb0y) and contributors, is the heart of this: IBM's Embedded ViaVoice text-to-speech engine rebuilt from IBM's 1999 Windows objects as C, proved sample for sample against IBM's own binary in every language the SDK shipped, and now maintained against 979 recorded cases. Its language lifters, rules decompiler, Windows port, sample-rate converter, SSML reader, crash fixes and the `eci.dll` that exports IBM's published interface are all upstream's. The modules in `languages/` are upstream's `eci.dll` and `eci32.dll`, built from `openevv/` (a snapshot of [joshknnd1982/openevv](https://github.com/joshknnd1982/openevv), which tracks upstream), one language each: the ten native ones unchanged, and since 1.3.0 the seven template modules with this project's accent layer (`openevv/src/accent`) compiled in.

Upstream's documentation also shaped the wrapper directly. `docs/quirks.md` explained why an utterance cannot be interrupted, and why a discarding callback must answer "processed". `docs/api.md` documented the index marks, the queued synthesis mode and the user dictionaries. The NVDA driver in `nvda/` provided the speed range that NVDA users know: 40 to 156, with a 1.6 times boost.

The engine code is MIT-licensed; the language data is IBM's. See `NOTICE.md`.

## 146 more languages: eSpeak NG

[eSpeak NG](https://github.com/espeak-ng/espeak-ng), by Jonathan Duddington, Reece H. Dunn and hundreds of contributors, reads the 146 languages openevv has no module for: their spelling rules, dictionaries, numbers, letter names and stress are eSpeak NG's, and so are the phoneme tables `phonemes.map` is translated from. The language maintainers named in eSpeak NG's `espeak-ng-data/lang` files and dictionary sources did the work of each language. eSpeak NG is under the GNU GPL version 3 or later; see `NOTICE.md`.

The names of letters, numbers and punctuation marks added to eSpeak NG for 1.2 come from each language's own references: its language boards and academies (among them the Kunsill Nazzjonali tal-Ilsien Malti, Te Taura Whiri i te Reo Māori, the Akademi Kreyòl Ayisyen, PanSALB and An Caighdeán Oifigiúil), its school books, dictionaries and Wikipedia, and from the Unicode Common Locale Data Repository and the translations of NVDA's symbol names, where the language has them.

## The community pronunciation dictionary: IBMTTSDictionaries

[IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries) is the pronunciation dictionary the IBMTTS driver community keeps for the ECI engine: main, root and abbreviation dictionaries for US English (it holds German ones too, which OpenEVV does not use), maintained by [amirsol81](https://github.com/amirsol81), [x0](https://github.com/ultrasound1372) and [thunderdrop](https://github.com/thunderdrop), with contributions from many people. It is released under CC0 1.0. OpenEVV installs it, reads it beneath the user's own dictionaries, and can download its newest version. No ownership of the IBMTTS driver or its dependencies is implied.

## The speech engine underneath: Eloquence and IBM

Eloquence was created by Eloquent Technology, Inc., and IBM licensed it as the formant engine of ViaVoice and Embedded ViaVoice. The language data in every module is IBM's work, transcribed from the Embedded ViaVoice 4.3 SDK that IBM still serves from its public download site. No licence here covers it. See `NOTICE.md`.

## The SAPI 5 scaffolding: the BestSpeech SAPI5 wrapper

The COM and SAPI plumbing in `src/sapi/` descends from the BestSpeech SAPI5 wrapper by Gozaltech: the class factory and registrar (`com.*`), the registry helpers (`registry.*`), the `ISpDataKey` implementation, the voice tokens and the `TokenEnums` token enumerator. It was adapted with the fixes learned on earlier wrappers in this series: registry deletion with `RegDeleteTreeW`, bookmark strings allocated the way SAPI frees them, and every fragment action handled.

## Earlier wrappers in this series

The engine host and pool, the logging, the settings watcher, the configuration utility's structure, the self-test, the accessibility checks (`a11y_check`, `installer_a11y`) and the installer script follow the Monologue 1.0, Outloud and Orpheus SAPI5 wrappers (github.com/joshknnd1982), and what each of them taught about screen readers and SAPI.

## The IPA work (1.3.0): what it rests on

The sounds made for the IPA chart in 1.3.0 rest on other people's work, each source named where it is used and listed in `docs/tts-extension/REFERENCES.md`: the International Phonetic Association's chart (2026 issue, CC BY-SA 4.0) and the Unicode Character Database (Unicode License v3); the published phonetics literature on every sound's acoustics; the CMU ARCTIC recordings of speaker awb by John Kominek and Alan W. Black, Carnegie Mellon University, from which the Scottish English vowels were measured; the vowel measurements of Southern Standard Dutch by Patti Adank, Roeland van Hout and Roel Smits (2004), which Belgian Dutch's vowels come from; Mozilla Common Voice (CC0) and Tatoeba (CC BY 2.0 FR) for the test sentences; OpenAI's Whisper large-v3 (MIT), run through faster-whisper, to measure how well each language is understood; and Praat by Paul Boersma and David Weenink, through Parselmouth, to cross-check the formant measurements. None of the recognisers or measuring tools is installed with OpenEVV.

## Tools

Built with Microsoft Visual C++ (Visual Studio 2022 Build Tools), CMake and [Inno Setup](https://jrsoftware.org/isinfo.php) by Jordan Russell and Martijn Laan; the language modules with GCC from [MSYS2](https://www.msys2.org/)'s mingw-w64 toolchains.
