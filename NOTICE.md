# Notice: whose is whose

Three different things are in this repository and its installer, under three different sets of terms.

## The SAPI 5 wrapper: GNU GPL version 2

Everything outside `openevv/` and `languages/` is the wrapper: the SAPI 5 engine and voice enumerator, the engine host, OpenEVV Configuration, the tools, the build scripts and the installer script. It is under the GNU General Public License version 2, in `LICENSE`. Its COM and SAPI scaffolding descends from the BestSpeech SAPI5 wrapper; see `CREDITS.md`.

## The openevv engine: MIT

`openevv/` is a snapshot of the openevv engine, and every language module in `languages/` is compiled from it. Its authors' own work (the engine in `openevv/src`, its front ends, tools, tests and documents) is under the MIT licence in `openevv/LICENSE`. Copyright (c) 2026 Stanislaw Przedzinkowski.

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

## Names

IBM, ViaVoice and Embedded ViaVoice are trademarks of International Business Machines Corporation. Eloquence is a trademark of its respective owner. Microsoft, Windows and SAPI are trademarks of Microsoft Corporation. This project is not affiliated with, endorsed by or supported by IBM, Cerence, Nuance, Microsoft or Apple.
