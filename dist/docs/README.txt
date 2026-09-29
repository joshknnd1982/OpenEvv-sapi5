# OpenEVV SAPI5

The OpenEVV text-to-speech engine as SAPI 5 voices for Windows, in both 32-bit and 64-bit programs: NVDA, JAWS, Balabolka, e-book and document readers, and anything else that speaks through Microsoft SAPI 5.

[openevv](https://github.com/Mudb0y/openevv) is IBM's Embedded ViaVoice engine, the voice people know as Eloquence, rebuilt from IBM's 1999 objects as portable C whose audio matched IBM's own binary sample for sample. This project builds one engine module per language from that source and puts a SAPI 5 interface, a configuration utility and an installer around them. Nothing of IBM's binary code is used, SAPI 4 is not involved, and nothing is read from the registry.

## What you get

- **155 languages, eight voices each, 1,240 SAPI voices.** openevv's own ten: US English, British English, German, Castilian Spanish, Latin American Spanish, French, Canadian French, Italian, Japanese and Polish (experimental, because upstream is still turning Italian rules into Polish ones).
- **And 145 more, read by eSpeak NG:** every language and dialect [eSpeak NG](https://github.com/espeak-ng/espeak-ng) has that openevv does not, from Afrikaans to Yue Chinese, New York City English and Swiss French among them. eSpeak NG reads the text -- its spelling, dictionary, numbers, letter names, punctuation names, stress and tones -- and one of openevv's modules speaks it in the Eloquence voice, with the language's own sounds: Hindi's retroflex and breathy voiced stops, the palatalised consonants of Russian, the nasal vowels of Portuguese, the voicing lead of Hindi and Turkish b, d and g, the taps and trills, the uvulars, the h and the glottal stop the modules never had. Each language has the melody its literature describes, and a question asked with a question word ends differently from one that wants yes or no. Mandarin, Cantonese, Hakka, Vietnamese, Burmese and Shan are spoken with their tones, and so are the low tone of Punjabi and the tones of Cherokee where the text marks them, Mandarin's third tone and neutral tone changing as they do beside other tones. Spelling and moving through a line a character at a time say every letter by its name in the language, an accented letter with its accent. `docs/SOUNDS.md` says how, `docs/LANGUAGE-REPORT.md` what each language has and what is still missing.
- **The eight classic presets in every language:** Adult Male 1 (Reed), Adult Female 1 (Shelley), Child 1, Adult Male 2, Adult Male 3, Adult Female 2, Elderly Female 1 and Elderly Male 1. Voices are named "OpenEVV US English Adult Male 1" and so on.
- **Low latency.** The engine synthesises about 600 times faster than real time. From a program's `Speak()` call to the first audio handed to SAPI takes about 1.5 ms on a warm voice. A cancel returns in well under a millisecond, and the next utterance never waits for the one it replaced.
- **Everything adjustable, live.** OpenEVV Configuration adjusts all eight parameters of every voice in every language: gender, head size, pitch, inflection, roughness, breathiness, speed and volume. It also sets the sample rate (8 to 48 kHz), the resampler, the speed range for SAPI's rate, the pitch step, abbreviation expansion, how numbers are read, the spelling modes, backquote annotations, English heteronym fixes and user dictionaries. Each change is saved at once and heard on the next thing any program says, a screen reader already speaking included.
- **Languages you can add and remove** as folders, without reinstalling anything. See below.
- **Everything SAPI asks of an engine:** word, sentence and bookmark events on the exact sample, pauses, `<spell>` (NVDA's character navigation), rate, pitch and volume changes inside an utterance, and sentence skipping. A lone symbol the engine would render as silence is named instead (in Japanese that is most ASCII punctuation), but only when it is the whole utterance, so prose keeps its natural pauses.
- **Logs** of the voices, the engine hosts, the utility and the installer, in `%ProgramData%\OpenEVV\Logs`.

## Installing

Download `OpenEVV-SAPI5-Setup-<version>.exe` from the [Releases](../../releases) page and run it. It installs both SAPI interfaces, all 155 languages, OpenEVV Configuration (with a desktop shortcut, and in the Start menu) and the documentation. It then tests every voice in 32-bit and 64-bit programs and states the result on its last page. The wizard is Inno Setup's standard one and works with screen readers.

Windows may say "Windows protected your PC" first. That is SmartScreen noting a new, unsigned download, not a detection: choose More info, then Run anyway.

Installing over an older version keeps your settings and languages, and Windows never needs to restart. Files a running program still has open (a screen reader using an OpenEVV voice, say) are renamed out of the way and the new ones installed beside them: every program started afterwards uses the new version at once, and the programs that were already running keep the old one until you close them and start them again. The installer's last page names those programs.

## Native speakers: please help make your language right

Not every language is right yet. The 145 languages read by eSpeak NG were built from published descriptions, dictionaries, grammars and measurements, and checked by measuring the sound, but most of them have not yet been heard by a native speaker. If your language is read or spoken wrongly, please improve it with a pull request. If you would rather describe what you hear, open an issue: say which words or sentences are wrong and how a native speaker says them.

Where a fix goes depends on what is wrong:

- **How the text is read**: a word pronounced wrongly, a letter's name, how a number is read, the name of a punctuation mark. This is eSpeak NG's dictionary for the language, in the `openevv-languages` branch of [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages): `dictsource/<code>_list` holds words, letter names, numbers and punctuation names, and `dictsource/<code>_rules` the spelling rules. Send the pull request there. A fix that is right for eSpeak NG itself is welcome upstream at [espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng) too, and then every program that uses eSpeak NG benefits.
- **How the language sounds**: a vowel or consonant, the rhythm, the melody of a sentence or a question, the tones. This is in this repository: the pack's `languages/<tag>/sounds.map`, a text file that `docs/SOUNDS.md` explains entry by entry, and the language's profile `engine/profiles/<tag>.json`, which says what the literature says the language sounds like, with sources. `docs/LANGUAGE-REPORT.md` lists, language by language, what is known to be missing.

The easiest pull request to take says what was wrong, what is right, and where that is written down: a dictionary, a grammar, a published description, or simply "I am a native speaker of this language".

## Adding a new language to your installed copy

New OpenEVV languages are published as language packs: a `.zip` holding one folder with `language.ini` and two engine modules. To add one:

1. Download the pack's `.zip`, for example `OpenEVV-language-xxxx-1.0.0.zip`, from the [Releases](../../releases) page, or from wherever it was announced.
2. Open **OpenEVV Configuration** (on the desktop and in the Start menu) and go to the **Languages** page.
3. Press **Add a language pack...**, choose the `.zip` you downloaded, and press Open. You do not have to extract it first.

That is all. The utility says which language was added, and its eight voices are in every SAPI 5 program's voice list straight away. A program that lists voices only when it starts, such as NVDA, shows them after you choose its SAPI 5 synthesiser again or restart it. No administrator rights are needed and nothing else is reinstalled.

Without the utility, extract the zip and copy the language's folder into `%ProgramData%\OpenEVV\languages` (type that into File Explorer's address bar). It has the same effect. `OpenEvvConfig.exe --add-pack <file.zip>` does the same from a command line.

A pack you add replaces a shipped language with the same tag, which is also how an updated version of a language is installed. **Remove the selected language** on the same page takes a language away again (to the Recycle Bin); close programs that are using its voices first.

`docs/LANGUAGES.md` describes the pack format in full.

## Making and publishing a new language (for the maintainer)

A language in openevv is text: its rules, tables and dictionary in `openevv/lang/<tag>/`, which upstream's build compiles into the engine (`openevv/docs/language.md` explains each file). Turning one into a pack that users can install as above:

1. Put the language's folder in `openevv/lang/<tag>/`, bringing `openevv/` up to date from upstream first if the language came from there.
2. Add one line for it to the table at the top of `engine/make_language_packs.py`: its name, ECI language number, SAPI language ID, locale and code page.
3. Build the modules and the pack. This needs MSYS2, see "Building from source" below:

        engine\build_modules.cmd <tag>

   This writes `languages\<tag>\` with both modules and a `language.ini` whose voice list and parameters come from the module itself.
4. Try it: run `build_x64\bin\Release\OpenEvvConfig.exe`, pick the language on the Voices page and press Speak. Or run the Diagnostics self-test, which speaks all eight of its voices in both bitnesses.
5. Package it for download:

        python engine\zip_language_pack.py <tag>

   This writes `output\OpenEVV-language-<tag>-<version>.zip`.
6. Publish that zip on the Releases page, either with a new release of this project or in a release of its own, for example `gh release upload v1.0.0 output\OpenEVV-language-<tag>-1.0.0.zip`. Point users to "Adding a new language to your installed copy" above.

To ship the language in the installer as well, commit `languages/<tag>/` and build a new installer. `installer\openevv.iss` installs whatever is in `languages\`.

## OpenEVV Configuration

Four pages, all standard Windows controls, every one labelled. Each number is an edit box with a spin button; the arrow keys step it.

- **Voices:** pick a language and one of its eight voices, then adjust gender, head size, pitch, inflection, roughness, breathiness, speed and volume. **Restore this voice's defaults** undoes your changes to that voice. **Speak** plays test text with the settings as they are.
- **Speech:** settings for every voice:
  - the sample rate, and how rates above the engine's native 11,025 Hz are reached
  - the fastest and slowest speeds SAPI's rate +10 and -10 reach, and rate boost (+10 reaches 250)
  - the pitch change per SAPI pitch step
  - abbreviation expansion, and how numbers are read: 1999 as "nineteen ninety-nine", or as a whole number
  - the text mode: normal, spell letters and digits, spell everything, or the radio alphabet
  - backquote annotations, English heteronym fixes, naming lone symbols, and user dictionaries
- **Languages:** the installed languages; adding and removing packs; editing the main, root and abbreviation user dictionaries of the selected language.
- **Diagnostics:** the logging level, the log folder, and a self-test that speaks every voice of every language into memory, in both bitnesses, and one through SAPI itself.

Settings are per user, in `%APPDATA%\OpenEVV\settings.ini`.

### How SAPI's rate, pitch and volume map to the engine

- **Rate:** SAPI rate 0 is each voice's own speed, 50 for most voices. +10 reaches the fastest speed set on the Speech page: 156 by default, the same top as NVDA's own Eloquence driver, or 250 with rate boost. -10 reaches the slowest speed set there, 0 by default. The engine's speed scale is already exponential (each ten units is about 22% faster), so every SAPI step is an even change.
- **Pitch:** each SAPI pitch step moves the voice's pitch baseline by the pitch step set on the Speech page, 4 units by default. NVDA's capital-letter pitch change comes through this way.
- **Volume:** SAPI's volume, and a fragment's own volume, scale the voice's own volume.

## How it works

```
32-bit program -> x86\OpenEvvSAPI.dll --pipes--> x86\OpenEvvHost.exe -> languages\enus\openevv-enus-x86.dll
64-bit program -> x64\OpenEvvSAPI.dll --pipes--> x64\OpenEvvHost.exe -> languages\enus\openevv-enus-x64.dll
```

The engine runs in a small host process, one per language in use, started as soon as a program chooses a voice so that the first word never waits for it. There are two reasons for the separate process:

- **CET shadow stacks.** The engine backtracks through a landing place that restores the stack pointer itself. A 64-bit process that enforces hardware-enforced stack protection (CET shadow stacks) would kill itself at the first backtrack, and more programs enforce it every year, 64-bit PowerShell among them. The host is built without CET compatibility, and the tests run the whole SAPI suite inside a CET-enforcing process to prove the engine stays out of it.
- **Faults.** Nothing a transcribed 1999 engine does wrong should be able to take a screen reader down. A host that faults or hangs is replaced and the utterance retried. Hosts live in a job object, so none outlives its program, and Windows' crash dialog is suppressed so that nothing can steal a screen reader's focus.

The engine cannot abandon an utterance part way. Its rules build a shared structure that later rules assume is complete. So a cancel stops forwarding the audio, and the host finishes the rest, which takes a few milliseconds.

The SAPI voice list comes from a token enumerator that reads the language packs each time a program asks. There are no static voice tokens, so adding or removing a pack changes the list with nothing registered or unregistered.

A language read by eSpeak NG has one step more. The host starts `OpenEvvFrontend.exe`, which reads the text with eSpeak NG and writes every word as a pronunciation in the phones of one of seven modules made for these languages (IBM's German, Italian, Spanish, English and French modules with the habits of their own language taken out). Beside each word it writes what each phone was meant to be. The *accent layer* inside the engine changes the frames the module asks the synthesiser for, 200 a second, into the language's own sounds, melody and tones. Without that markup it does nothing, so openevv's own ten languages sound exactly as they did.

Upstream's `docs/quirks.md` and `docs/api.md` in `openevv/` document the engine's interface; `docs/LANGUAGES.md` here documents the pack format, and `docs/SOUNDS.md` the sounds.

## Building from source

Everything needed is in this repository. The ten language modules are prebuilt in `languages/`, so building the SAPI wrapper, the utility and the installer needs only:

- Visual Studio 2022 or its Build Tools, with the C++ workload and a Windows 10 or 11 SDK
- CMake 3.20 or later
- Inno Setup 6

Then run:

    build_all.bat

This builds x86 and x64, runs the test suites, stages `dist\` and writes `output\OpenEVV-SAPI5-Setup-<version>.exe`. `build_all.bat notest` skips the tests.

The eSpeak NG front-end is built too, with eSpeak NG fetched from [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng) (so the first build wants the internet and Git), or from a local checkout with `set ESPEAK_NG_SOURCE_DIR=C:\path\to\espeak-ng`. With a 64-bit Python on the PATH, every eSpeak NG pack is also checked against its template's module. `build_all.bat packs` writes the 145 eSpeak NG packs in `languages\` again from eSpeak NG's sources, choosing each template and translating each phoneme table.

Rebuilding the language modules from `openevv/` also needs [MSYS2](https://www.msys2.org/) with GNU make, Python and the two mingw-w64 GCCs:

    pacman -S --needed make python mingw-w64-x86_64-gcc mingw-w64-i686-gcc

Then run `engine\build_modules.cmd` for all ten languages or `engine\build_modules.cmd enus dede` for some, or `build_all.bat engine` for everything at once. The first build of a language decompiles its rules into C and takes a few minutes; later builds take about thirty seconds each. The build runs in `%LOCALAPPDATA%\OpenEvvBuild`, outside the repository.

### Layout

| Path | What it is |
|------|------------|
| `src/sapi/` | the SAPI 5 engine and voice enumerator (OpenEvvSAPI.dll) |
| `src/host/` | the engine host (OpenEvvHost.exe) |
| `src/common/` | shared by all of them: the host protocol and pool, settings, language packs, logging |
| `src/config/` | OpenEVV Configuration and its self-test |
| `src/tools/` | test tools: `sapi_test` (the SAPI engine through a mock site), `a11y_check` and `installer_a11y` (what a screen reader sees), `evv_probe` and `evv_chars` (measure a module directly) |
| `languages/` | the 155 language packs: openevv's ten, prebuilt, and the 145 read by eSpeak NG |
| `frontend/` | `OpenEvvFrontend.exe`, which reads those 145 with eSpeak NG (GPL v3; see its README) |
| `dist/` | the built SAPI wrapper, host, utility and eSpeak NG front-end, both bitnesses, and eSpeak NG's compiled data, in the installed layout |
| `openevv/` | the openevv engine source, a snapshot of [joshknnd1982/openevv](https://github.com/joshknnd1982/openevv) at 7148737 (= [Mudb0y/openevv](https://github.com/Mudb0y/openevv) main, 28 September 2026) |
| `engine/` | building the modules and packs from `openevv/`, and the eSpeak NG packs from eSpeak NG (`make_espeak_packs.py`, `espeak_phonemes.py`, `check_espeak_packs.py`, `espeak_templates.txt`) |
| `installer/` | the Inno Setup script |
| `samples/` | every voice of openevv's own ten languages, rendered straight from the engine modules; the 145 eSpeak NG languages' samples are a download on the Releases page (`engine/render_espeak_samples.py`) |

## Testing

`build_all.bat` runs all of these:

- **`sapi_test`, 64-bit, 32-bit, and 64-bit in a CET-enforcing process.** The SAPI engine through a mock SAPI site. It checks:
  - the voice list
  - every language
  - latency
  - bookmarks, word and sentence events, silences and spelling
  - rate, pitch and volume, measured in the audio
  - cancelling, and that the utterance after a cancel is whole
  - all seven sample rates
  - that a settings change is heard on the next utterance
  - recovery from a killed host
- **`sapi_test --all-voices`:** all 1,240 voices through SAPI.
- **`engine\check_espeak_packs.py`:** every eSpeak NG pack's sample, numbers and punctuation read and handed to its template's module, which must take every word as a pronunciation.
- **`a11y_check`:** walks every page of OpenEVV Configuration through MSAA on a private desktop. It fails on an unlabelled control or a duplicated access key, and checks that edits reach the settings file at once.
- **`installer_a11y`:** walks every page of the installer the same way, then installs and uninstalls a non-elevated probe build.
- **`OpenEvvConfig.exe --selftest`:** every voice of every language in both bitnesses, plus one through SAPI itself. The installer runs this too.

## Logs and troubleshooting

`%ProgramData%\OpenEVV\Logs` has one file per component and program: `sapi-x64-nvda.log`, `host-x64-nvda.log`, `config-openevvconfig.log`, `install.log`, and so on. At the standard level they record every utterance's timings and never the text. Set Logging to Full on the Diagnostics page to include the text too. Please attach the relevant logs to an [issue](../../issues).

## Licence and provenance

- **The wrapper** (everything outside `openevv/`, `frontend/` and `languages/`) is under the GNU General Public License version 2; see `LICENSE`. Its COM and SAPI scaffolding comes from the BestSpeech SAPI5 wrapper.
- **The eSpeak NG front-end** (`frontend/`, `OpenEvvFrontend.exe`), the eSpeak NG data installed with it and the eSpeak NG packs' phoneme maps are under the GNU General Public License version 3 or later, as eSpeak NG is; see `frontend/COPYING`. The front-end is a separate program the wrapper talks to over pipes.
- **The openevv engine** is under the MIT licence; see `openevv/LICENSE`.
- **The language data inside each language module** was transcribed from IBM's Embedded ViaVoice objects, and is IBM's work. Neither licence covers it, and nobody here can license it to anyone. `NOTICE.md` and `openevv/NOTICE` say whose it is and who the rights may belong to today.

`CREDITS.md` names everyone this is built on.
