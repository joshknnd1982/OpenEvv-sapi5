# Language packs

Every language OpenEVV speaks is a folder. The SAPI 5 voice list is built from the folders present each time a program asks for it, so adding a language is copying a folder in and removing one is deleting it: nothing is registered, and no program has to be reinstalled.

## Where they live

- `C:\Program Files\OpenEVV SAPI5\languages\` holds the ten languages the installer puts there.
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
