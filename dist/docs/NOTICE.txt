# Notice: whose is whose

Five different things are in this repository and its installer, under five different sets of terms.

## The SAPI 5 wrapper: MIT

Everything outside `openevv/`, `frontend/` and `languages/` is the wrapper: the SAPI 5 engine and voice enumerator, the engine host, OpenEVV Configuration, the tools, the build scripts and the installer script. It is under the MIT licence, in `LICENSE`. Its COM and SAPI scaffolding descends from the BestSpeech SAPI5 wrapper; see `CREDITS.md`.

## eSpeak NG and the front-end: GNU GPL version 3 or later

`frontend/` is `OpenEvvFrontend.exe`, which reads the 145 languages made from [eSpeak NG](https://github.com/espeak-ng/espeak-ng). It links eSpeak NG and is under the GNU General Public License version 3 or later, in `frontend/COPYING`, as eSpeak NG is. So is the eSpeak NG data installed with it in `espeak-ng-data\`, and so are the `sounds.map` and `phonemes.map` files in the eSpeak NG language packs, which are written from eSpeak NG's phoneme tables. The front-end is a program of its own: the wrapper starts it and talks to it over pipes, and does not link it. `src/common/frontend_proto.h`, the description of those pipes, is under the MIT licence so that both sides may include it.

The eSpeak NG it is built from is [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng) at the tag `frontend/CMakeLists.txt` names, which is eSpeak NG with the changes made for OpenEVV (number reading for more languages among them); its complete source is there. eSpeak NG is Copyright (C) 2005 to 2013 Jonathan Duddington, and from 2013 Reece H. Dunn and the eSpeak NG contributors.

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

The seven modules that speak the languages read by eSpeak NG (`dedx`, `itix`, `esex`, `esux`, `engx`, `enux` and `frfx` in `languages/`) are IBM's German, Italian, Spanish, English and French modules with a few rules of their phonology replaced by rules that do nothing. `openevv/accents/` holds what they differ by, and the rules written there are this project's own; the modules made from them are IBM's language data exactly as the modules they were made from are, and the same applies to them. They are not under the MIT licence or any other licence given here.

The profiles in `engine/profiles/` are summaries, written for this project, of what the published literature says of each language, with the sources named; they are part of the wrapper and under its licence. The measurements and descriptions they cite are their authors'.

## Names

IBM, ViaVoice and Embedded ViaVoice are trademarks of International Business Machines Corporation. Eloquence is a trademark of its respective owner. Microsoft, Windows and SAPI are trademarks of Microsoft Corporation. This project is not affiliated with, endorsed by or supported by IBM, Cerence, Nuance, Microsoft or Apple.
