# Notice: whose is whose

Several different things are in this repository and its installer, under different sets of terms. `docs/tts-extension/LICENCE_AUDIT.md` puts every file git tracks in exactly one licence class, by a rule, and `engine/check_licences.py` checks that no file is left out; this page says why each class is what it is.

## The SAPI 5 wrapper: MIT

Everything outside `openevv/`, `frontend/` and `languages/` is the wrapper and this project's own work, except the files the sections below name: the SAPI 5 engine and voice enumerator, the engine host, OpenEVV Configuration, the tools, the build scripts and the installer script, and the TTS extension's tools, harness, IPA tables, proofs, measurements and documents. It is under the MIT licence, in `LICENSE`. All of this project's own work is MIT; not every file in the repository is, and the sections below say which are not. Its COM and SAPI scaffolding descends from the BestSpeech SAPI5 wrapper; see `CREDITS.md`. The files listed in the next section are not covered by the MIT licence.

## Not covered: files adapted from the BestSpeech SAPI 5 wrapper

The files below were adapted from the BestSpeech SAPI 5 wrapper by Gozaltech (<https://github.com/gozaltech/BstSpeech-sapi>) and still contain much of that project's code: its SAPI 5 COM server and token enumerator skeleton. They are an exception to the section above: the MIT licence does not cover them, and they stay under their original author's terms.

- `src/sapi/com.hpp` and `src/sapi/com.cpp`
- `src/sapi/registry.hpp` and `src/sapi/registry.cpp`
- `src/sapi/utils.hpp`
- `src/sapi/ISpDataKeyImpl.hpp` and `src/sapi/ISpDataKeyImpl.cpp`
- `src/sapi/IEnumSpObjectTokensImpl.hpp` and `src/sapi/IEnumSpObjectTokensImpl.cpp`
- `src/sapi/voice_token.hpp` and `src/sapi/voice_token.cpp`
- `src/sapi/sapi_main.cpp`
- `src/sapi/ISpTTSEngineImpl.hpp`

## eSpeak NG and the front-end: GNU GPL version 3 or later

`frontend/` is `OpenEvvFrontend.exe`, which reads the 146 languages made from [eSpeak NG](https://github.com/espeak-ng/espeak-ng). It links eSpeak NG and is under the GNU General Public License version 3 or later, in `frontend/COPYING`, as eSpeak NG is. So is the eSpeak NG data installed with it in `espeak-ng-data\`, and so are the `sounds.map` and `phonemes.map` files in the eSpeak NG language packs, which are written from eSpeak NG's phoneme tables. The front-end is a program of its own: the wrapper starts it and talks to it over pipes, and does not link it. `src/common/frontend_proto.h`, the description of those pipes, is under the MIT licence so that both sides may include it.

The eSpeak NG it is built from is [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng) at the tag `frontend/CMakeLists.txt` names, which is eSpeak NG with the changes made for OpenEVV (number reading for more languages among them); its complete source is there. eSpeak NG is Copyright (C) 2005 to 2013 Jonathan Duddington, and from 2013 Reece H. Dunn and the eSpeak NG contributors.

`packs/` holds the same language packs as data (one `pack.toml` each; `packs/README.md`), from which the files of `languages/<tag>/` are built identically. The loader that reads them (`engine/packs/`) is this project's own work, under the MIT licence. The `[sounds]` and `[phonemes]` lines in the packs of the 146 eSpeak NG languages (and of the dialects that hold such lines) are the data of their `sounds.map` and `phonemes.map` files and carry the licence of those files given above (GPL-3.0-or-later); the `[ini]` of a pack is its `language.ini`. A pack's own overrides, measured targets and review lists are this project's, under the MIT licence; a pack holding no `[sounds]` or `[phonemes]` lines (the module packs, `nl-be`) is wholly this project's.

`docs/tts-extension/harness/praat_crosscheck.py` is under the GPL version 3 or later too, as its own header says: it imports Parselmouth, which contains Praat. Nothing else in the harness imports it.

## The openevv engine: MIT

`openevv/` is a snapshot of the openevv engine, and every language module in `languages/` is compiled from it. Its authors' own work (the engine in `openevv/src`, its front ends, tools, tests and documents) is under the MIT licence in `openevv/LICENSE`. Copyright (c) 2026 Stanislaw Przedzinkowski.

What this project added to the engine is under the same licence: the accent layer in `openevv/src/accent`, which gives a language read by eSpeak NG its own sounds, melody and tones, the few lines in `openevv/src/eci` and `openevv/src/klatt` that call it, and `openevv/tools/module/clone.py`. Copyright (c) 2026 the OpenEVV SAPI5 contributors.

## The community pronunciation dictionary: CC0

`dictionaries/community/` is [eigencrow/IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries), byte for byte, at the commit `community-dictionary.ini` names. It was released under the Creative Commons CC0 1.0 Universal dedication; the text is in `dictionaries/community/LICENSE.md` and is installed with it. OpenEvvConfig.exe can download a newer copy of the same files from GitHub, which stay under the same dedication.

## The language data: IBM's, and not licensed here

The language data under `openevv/lang/`, and therefore the language inside every module in `languages/`, is **not** covered by either licence. It was transcribed out of IBM's Embedded ViaVoice 4.3 objects, byte for byte where the engine's arithmetic depends on it, and it is IBM's work. `openevv/src/klatt_tables.c` and `openevv/src/eci_xmltok_tables.c` are the same: data lifted from IBM's objects. The SDK they came from says:

    Licensed Materials - Property of IBM
    (C) Copyright IBM Corp. 1999, 2004  All Rights Reserved.

Neither this project nor openevv is in a position to license that data to anyone. It is here because the engine cannot speak without it. Who holds the rights in it today is not simple:

- IBM published the objects.
- The engine underneath was Eloquence, by Eloquent Technology, which passed to SpeechWorks, then ScanSoft, then Nuance.
- Nuance's text-to-speech rights went to Cerence in the 2019 spinoff, and are now the subject of Cerence Inc. v. Microsoft Corporation and Nuance Communications, Inc., D. Del. 1:25-cv-00553, filed 6 May 2025.

`openevv/NOTICE` is upstream's own statement of this and is the authoritative one. None of this is legal advice. If you mean to do more with the language data than use it, the rights are yours to sort out with whoever holds them.

Polish (`openevv/lang/plpl`) began as a copy of IBM's Italian and is still largely Italian data, so the same applies to it.

The seven modules that speak the languages read by eSpeak NG (`dedx`, `itix`, `esex`, `esux`, `engx`, `enux` and `frfx` in `languages/`) are IBM's German, Italian, Spanish, English and French modules with a few rules of their phonology replaced by rules that do nothing. `openevv/accents/` holds what they differ by, and the rules written there are this project's own; the modules made from them are IBM's language data exactly as the modules they were made from are, and the same applies to them. They are not under the MIT licence or any other licence given here. Since 1.3.0 these seven are built with this project's accent layer (`openevv/src/accent`, MIT, above) compiled in; the language data inside them is IBM's exactly as before.

Speech the engine has rendered, kept in the tree as examples and for review (`samples/*.wav`, and the review packets' `index.html` and `items.json` under `docs/tts-extension/review_packets/` and `docs/tts-extension/examples/packets/`), is IBM's language data at work and is not offered under the MIT licence; the text the packets speak is Common Voice's (CC0) or this project's word lists.

The profiles in `engine/profiles/` are summaries, written for this project, of what the published literature says of each language, with the sources named; they are part of the wrapper and under its licence. The measurements and descriptions they cite are their authors'.

## The IPA chart: CC BY-SA 4.0

`IPA_Kiel.pdf` is the International Phonetic Association's chart, 2026 issue ("IPA Chart revised to 2015/2005"), copyright 2026 International Phonetic Association, https://www.internationalphoneticassociation.org/content/ipa-chart, licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). It is kept in the tree unchanged, at the human's request (2026-10-10, HUMAN_ANSWERS.md), so that a `git clone` holds everything the TTS extension project rests on; it is the Association's work, not this project's, and nothing of it is copied into the MIT-licensed files, which cite it (docs/tts-extension/inventory/IPA_CHECKLIST.md, REFERENCES.md).

The seven sub-chart images in `docs/tts-extension/inventory/ipa_chart_images/` (`IPA_Kiel_CP_0600.png`, `_CnP_`, `_OS_`, `_V_`, `_D_`, `_S_`, `_T_`: the pulmonic and non-pulmonic consonants, other symbols, vowels, diacritics, suprasegmentals, tones and word accents) are the Association's official 600 ppi renderings of the same 2026 issue, fetched on 2026-10-11 from https://www.internationalphoneticassociation.org/IPAcharts/IPA_charts_E/images/ under the same CC BY-SA 4.0 licence, kept unchanged for the same reason (the Phase 9 completion review read them to re-check the checklist); nothing of them is copied into the MIT-licensed files.

`third_party/cmu_arctic/` holds speaker awb (Scottish English) of the CMU ARCTIC speech databases, J. Kominek and A. W. Black, Carnegie Mellon University (http://festvox.org/cmu_arctic/): 1,138 recordings, their phone labels, prompts, readme and licence, unchanged. It is CMU's work under CMU's own notice, `third_party/cmu_arctic/cmu_us_awb_arctic/COPYING` (free for any purpose, commercial or otherwise; keep the notice, mark modifications, keep the authors' names), not under the MIT licence. It is kept in the tree at the human's request (2026-10-11) because the Scottish pack's measured vowel targets rest on it. Those measurements (`packs/en-gb-scotland/measured/cmu_arctic.json`) and the tools that made them (`engine/authenticity/`, `engine/review/`) are this project's own work, under the MIT licence; the review packets made from a pack (`docs/tts-extension/review_packets/`) hold the engine's speech of that pack's text, whose sentences carry the licence `harness/asr/sentences.json` records (Common Voice, CC0).

## Test sentences and Unicode data

`docs/tts-extension/harness/asr/sentences.json` holds the test sentences the speech-recognition check speaks: from Mozilla Common Voice (CC0 1.0) and, for the languages it lacks, from Tatoeba (CC BY 2.0 FR), each Tatoeba sentence with its id and author. `results/asr.json` and `results/asr_espeak.json` beside it quote them. They stay under those terms, not the MIT licence (`REFERENCES.md` records the sources).

`docs/tts-extension/inventory/unicode/` holds `UnicodeData.txt` and `Blocks.txt` of the Unicode Character Database, unchanged, under the Unicode License v3, whose text is beside them (`LICENSE.txt`).

## Names

IBM, ViaVoice and Embedded ViaVoice are trademarks of International Business Machines Corporation. Eloquence is a trademark of its respective owner. Microsoft, Windows and SAPI are trademarks of Microsoft Corporation. This project is not affiliated with, endorsed by or supported by IBM, Cerence, Nuance, Microsoft or Apple.
