# Language packs

Every language OpenEVV speaks is a folder. The SAPI 5 voice list is built from the folders present each time a program asks for it, so adding a language is copying a folder in and removing one is deleting it: nothing is registered, and no program has to be reinstalled.

## Where they live

- `C:\Program Files\OpenEVV SAPI5\languages\` holds the 155 languages the installer puts there: openevv's own ten and 145 read by eSpeak NG.
- `%ProgramData%\OpenEVV\languages\` (usually `C:\ProgramData\OpenEVV\languages\`) is yours. Anyone can write there without being an administrator, and a pack there wins over a shipped pack with the same tag, so it is also how to replace one.

OpenEVV Configuration's Languages page does all of this with buttons: **Add a language pack** takes a downloaded `.zip` as it is (or `language.ini` inside an extracted pack) and installs every language in it into your folder, **Remove the selected language** sends a pack to the Recycle Bin (asking for administrator rights only for a shipped pack), and **Open the languages folder** opens yours. `OpenEvvConfig.exe --add-pack <zip or folder>` does the same from a command line.

A program already speaking with a voice from a pack has that pack's engine module open, so remove a language after closing programs that are using its voices.

## What is in a pack

    languages\enus\
        language.ini
        openevv-enus-x86.dll     the engine and the language, for 32-bit
        openevv-enus-x64.dll     the same, for 64-bit
        dict\main.dic            optional: dictionaries shipped with the pack
        dict\root.dic
        dict\abbr.dic

Only one of the two modules is required. A 32-bit program can use a pack that has only a 64-bit module, and the other way round, on 64-bit Windows.

## language.ini

UTF-8, so Notepad can edit it. Only `[Language]` with `Id` and one module is required; everything else has a sensible default.

    [Language]
    Tag=enus                     ; short name; the folder name if missing
    Name=US English              ; shown in voice names: "OpenEVV US English Adult Male 1"
    Id=0x00010000                ; the ECI language number the module answers to
    LCID=409                     ; SAPI "Language" attribute, hex; several allowed: C0A;40A
    Locale=en-US
    Codepage=1252                ; how text is handed over: 1252, 932 (Shift-JIS), 65001 (UTF-8)
    Module32=openevv-enus-x86.dll
    Module64=openevv-enus-x64.dll
    Order=10                     ; where the language sorts in the voice list
    Experimental=0

    [Voice1]                     ; one section per preset, 1 to 8
    Name=Adult Male 1
    Gender=Male                  ; Male or Female
    Age=Adult                    ; Adult, Child or Senior
    Params=0,50,65,30,0,0,50,92  ; gender, head size, pitch, inflection,
                                 ; roughness, breathiness, speed, volume

`engine\make_language_packs.py` writes these files by asking each module for its own presets, so the parameters in a shipped pack are the engine's.

The ECI language numbers IBM assigned: 0x10000 US English, 0x10001 British English, 0x20000 Castilian Spanish, 0x20001 Mexican Spanish, 0x30000 French, 0x30001 Canadian French, 0x40000 German, 0x50000 Italian, 0x60000 Mandarin, 0x70000 Brazilian Portuguese, 0x80000 Japanese, 0x90000 Finnish, 0xa0000 Korean, 0xb0000 Cantonese, 0xc0000 Dutch, 0xd0000 Norwegian, 0xe0000 Swedish, 0xf0000 Danish. openevv uses 0x110000 for Polish.

## A language read by eSpeak NG

145 of the languages have no engine module of their own. eSpeak NG reads their text -- its spelling rules, its dictionary, its numbers and letter names, its word stress -- and one of openevv's own modules, the pack's *template*, speaks what it read. Such a pack is a folder too:

    languages\sw        language.ini
        phonemes.map             eSpeak NG's phonemes, as the template's
        sample.txt               a sentence in the language, for Speak and the self-test

and its `language.ini` names a template and an eSpeak NG voice instead of modules:

    [Language]
    Tag=sw
    Name=Swahili
    Id=0x00020000                ; the template's ECI language
    LCID=441
    Locale=sw
    Codepage=65001
    Template=eses                ; the pack whose modules speak it
    Order=289

    [Frontend]
    Engine=espeak
    Voice=bnt/sw                 ; the eSpeak NG voice, as a path under espeak-ng-data\lang
    Map=phonemes.map

The template's modules speak it with the template's own eight presets, which the `[Voice]` sections repeat. The engine host starts `OpenEvvFrontend.exe` beside it, which reads the text with eSpeak NG's data in `espeak-ng-data\` of the installation, and hands the template's engine a pronunciation for every word. `frontend\README.md` says how, and what `phonemes.map` holds; it is text, and a line of it is an eSpeak NG phoneme and the template phones that say it, so a sound can be changed with Notepad. A pack whose template is not installed is not offered.

The template is an accent: every word is said with that module's sounds, rhythm and melody. `engine\espeak_templates.txt` chooses it where a relative or a neighbour of the language decides -- the Celtic languages with British English, the Germanic ones with German, Brazilian Portuguese with Latin American Spanish, the dialects of English and French with their own language -- and otherwise `engine\make_espeak_packs.py` takes the template whose phones come closest to the sounds the language uses most, weighing most heavily two sounds of the language that the template could only say alike. `engine\check_espeak_packs.py` holds every pack to its template's module: a sample of the language, its numbers and its punctuation are read and handed to the module, and any word the module would not take as a pronunciation is a failure.

eSpeak NG's own dialects of openevv's languages are packs of their own -- New York City, Scottish and Caribbean English, Received Pronunciation, Lancaster and the West Midlands, English in the Shavian alphabet, Belgian and Swiss French -- spoken with openevv's module for the language. Only the eSpeak NG voices that openevv's own ten already are, are left out.

What eSpeak NG cannot bring across. A template can only say the sounds its module has, so a sound none of openevv's modules has is said as the nearest one it does. Tone is lost: the tonal languages are read with their tones by eSpeak NG, but the modules have no way to take a pitch for a syllable -- every change of pitch or speed inside an utterance makes the engine pause, which was measured -- so they are spoken with the template's own intonation.

## Any ECI library is a module

The engine host drives a module through the functions IBM published for its ECI interface (`eciNewEx`, `eciAddText`, `eciSynthesize` and the rest), looked up by name. A module is therefore any DLL exporting that interface, of the right bitness:

- The modules here are upstream openevv's `eci.dll` and `eci32.dll`, built with one language each.
- Upstream's release builds, which carry several languages in one DLL, work too: give each language its own folder whose `language.ini` names the same DLL with that language's `Id`.

IBM's own ViaVoice and Eloquence runtimes keep their languages in `.syn` files loaded by IBM's `eci.dll`, and read their configuration from the registry. Those files are not openevv modules and cannot be dropped in; an OpenEVV language pack is the equivalent of one.

## Building a module for a language

A language in openevv is text: its rules, tables and dictionary under `openevv\lang\<tag>\`, which upstream's build compiles into the engine. `openevv\docs\language.md` says what each file is and what it takes to add a language.

With MSYS2 installed (see the README), one command builds the modules for a language and installs its pack:

    engine\build_modules.cmd enus

For a language of your own, put its `lang\<tag>` folder in `openevv\lang\`, add a line for it to the table at the top of `engine\make_language_packs.py` (name, ECI number, LCID, locale, code page), and run the same command with its tag. Copy the resulting `languages\<tag>` folder to any machine's `%ProgramData%\OpenEVV\languages\`.

## User dictionaries

Every language can have three dictionaries of your own, read by the engine before its built-in rules:

- `main.dic`: whole words, spoken exactly as written in the pronunciation column.
- `root.dic`: word roots, which also apply to the forms built on them.
- `abbr.dic`: abbreviations, expanded where the engine finds them.

One entry per line: the word, a tab, and what to say instead. For example:

    NVDA	N V D A
    Eloquence	Elo quence

They live in `%ProgramData%\OpenEVV\dictionaries\<tag>\`, and OpenEVV Configuration's Languages page opens them in Notepad. Save as UTF-8 or ANSI, either works. A change is picked up by every OpenEVV voice before the next thing it says. A pack's own `dict\` folder is used for any volume you have not made your own. The Speech page's **Use the user dictionaries** turns all of them off and on.

With **Honour backquote annotations** on, a pronunciation can also be given in the engine's own phoneme alphabet: `` `[.1hE.0lo] ``.

In a language read by eSpeak NG the same three files work, applied before eSpeak NG reads the text: a word in `main.dic` or `abbr.dic` is replaced by what follows it, a word beginning with an entry of `root.dic` has that beginning replaced, and eSpeak NG then reads the replacement in the language. Annotations are not taken from the text in those languages, since the text is eSpeak NG's to read.
