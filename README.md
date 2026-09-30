# OpenEVV SAPI5

The OpenEVV text-to-speech engine as SAPI 5 voices for Windows, in both 32-bit and 64-bit programs: NVDA, JAWS, Balabolka, e-book and document readers, and anything else that speaks through Microsoft SAPI 5.

[openevv](https://github.com/Mudb0y/openevv) is IBM's Embedded ViaVoice engine, the voice people know as Eloquence, rebuilt from IBM's 1999 objects as portable C whose audio matched IBM's own binary sample for sample. This project builds one engine module per language from that source and puts a SAPI 5 interface, a configuration utility and an installer around them. Nothing of IBM's binary code is used, SAPI 4 is not involved, and nothing is read from the registry.

## What you get

- **155 languages, eight voices each, 1,240 SAPI voices.** openevv's own ten: US English, British English, German, Castilian Spanish, Latin American Spanish, French, Canadian French, Italian, Japanese and Polish (experimental, because upstream is still turning Italian rules into Polish ones).
- **And 145 more, read by eSpeak NG:** every language and dialect [eSpeak NG](https://github.com/espeak-ng/espeak-ng) has that openevv does not, from Afrikaans to Yue Chinese, New York City English and Swiss French among them. eSpeak NG reads the text -- its spelling, dictionary, numbers, letter names, punctuation names, stress and tones -- and one of openevv's modules speaks it in the Eloquence voice, with the language's own sounds: Hindi's retroflex and breathy voiced stops, the palatalised consonants of Russian, the nasal vowels of Portuguese, the voicing lead of Hindi and Turkish b, d and g, the taps and trills, the uvulars, the h and the glottal stop the modules never had. Each language has the melody its literature describes, and a question asked with a question word ends differently from one that wants yes or no. Mandarin, Cantonese, Hakka, Vietnamese, Burmese and Shan are spoken with their tones, and so are the low tone of Punjabi and the tones of Cherokee where the text marks them, Mandarin's third tone and neutral tone changing as they do beside other tones. Spelling and moving through a line a character at a time say every letter by its name in the language, an accented letter with its accent. `docs/SOUNDS.md` says how, `docs/LANGUAGE-REPORT.md` what each language has and what is still missing.
- **The eight classic presets in every language:** Adult Male 1 (Reed), Adult Female 1 (Shelley), Child 1, Adult Male 2, Adult Male 3, Adult Female 2, Elderly Female 1 and Elderly Male 1. Voices are named "OpenEVV US English Adult Male 1" and so on.
- **Low latency.** The engine synthesises about 600 times faster than real time. From a program's `Speak()` call to the first audio handed to SAPI takes about 1.5 ms on a warm voice. A cancel returns in well under a millisecond, and the next utterance never waits for the one it replaced.
- **Everything adjustable, live.** OpenEVV Configuration adjusts all eight parameters of every voice in every language: gender, head size, pitch, inflection, roughness, breathiness, speed and volume. It also sets the sample rate (8 to 48 kHz), the resampler, the speed range for SAPI's rate, the pitch step, abbreviation expansion, how numbers are read, the spelling modes, the pauses at punctuation, backquote annotations, English heteronym fixes and user dictionaries. Each change is saved at once and heard on the next thing any program says, a screen reader already speaking included.
- **Languages you can add and remove** as folders, without reinstalling anything. See below.
- **The community pronunciation dictionary** for English, the IBMTTS community's [IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries) (public domain): a main, a root and an abbreviation dictionary of pronunciation fixes, installed with OpenEVV and read before your own dictionaries. OpenEVV Configuration switches it on and off, and one button looks on GitHub for a newer version and installs it. See below.
- **Everything SAPI asks of an engine:** word, sentence and bookmark events on the exact sample, pauses, `<spell>` (NVDA's character navigation), rate, pitch and volume changes inside an utterance, and sentence skipping. A lone symbol the engine would render as silence is named instead (in Japanese that is most ASCII punctuation), but only when it is the whole utterance, so prose keeps its natural pauses.
- **Logs** of the voices, the engine hosts, the utility and the installer, in `%ProgramData%\OpenEVV\Logs`.

## Installing

Download `OpenEVV-SAPI5-Setup-<version>.exe` from the [Releases](../../releases) page and run it. It installs both SAPI interfaces, OpenEVV Configuration (with a desktop shortcut, and in the Start menu), the documentation and the languages you choose. It checks that the voices are registered with Windows and states the result on its last page. The wizard is Inno Setup's standard one and works with screen readers.

**Choosing the languages.** Every language adds eight voices to every SAPI 5 program, and 155 languages are 1,240 voices, a long list for a screen reader or any other program to go through, and more than some programs take well. So the wizard's **Select languages** page lets you install only the ones you will use. It has a check box for each of the 155 languages, and a list of ready-made choices above them:

- *The ten OpenEVV languages* (80 voices), the languages the engine speaks itself: US and British English, German, Castilian and Latin American Spanish, French, Canadian French, Italian, Japanese and Polish. This is what the wizard offers first on a computer with no OpenEVV on it.
- *English only*: US and British English (16 voices).
- *All 155 languages* (1,240 voices): the ten above and the 145 read by eSpeak NG.
- *Custom*: check the languages one by one. **Select all languages** and **Select no languages** under the list check or clear every one; at least one language has to be selected, and the wizard says so if none is.

Each language that eSpeak NG reads is spoken by one of the engine's modules; the wizard installs that module when you choose a language that needs it, and only then, so a single such language adds about 9 to 17 MB.

**Changing the languages later.** Run the installer again. Its language page offers exactly the languages that are installed now; it installs the ones you add and removes the ones you clear, and never asks Windows to restart. Installing over a version that put every language in (1.2.3 and earlier) offers all of them, so nothing is removed unless you clear it. A language you removed yourself with OpenEVV Configuration is not put back. OpenEVV Configuration's Languages page also removes languages one at a time, and adds language packs.

**Unattended installs.** With nothing on the command line, an install over an existing one keeps exactly the languages that are installed, and one on a computer with no OpenEVV installs the ten OpenEVV languages. `/TYPE=full` installs all 155, `/TYPE=english` US and British English, `/TYPE=openevv` the ten. `/COMPONENTS="openevv\enus,espeak\nb"` names languages: `openevv\` or `espeak\` and the language's folder name in `languages\`, with `-` written as `_` (`espeak\en_gb_scotland`); `installer\generated\components.inc` lists them all.

Windows may say "Windows protected your PC" first. That is SmartScreen noting a new, unsigned download, not a detection: choose More info, then Run anyway.

Installing over an older version keeps your settings and the languages you have installed, and Windows never needs to restart. Files a running program still has open (a screen reader using an OpenEVV voice, say) are renamed out of the way and the new ones installed beside them: every program started afterwards uses the new version at once, and the programs that were already running keep the old one until you close them and start them again. The installer's last page names those programs.

## Native speakers: help make your language right

OpenEVV speaks 145 languages through eSpeak NG. Most of them were built from dictionaries, grammars and published research, not by people who speak them, so not every language is right yet. If you speak one of them, you can make it better. You do not need to be a programmer to start.

Each language has two parts, and they are kept in two places:

- **Reading** is how the text becomes sounds: how each word is pronounced, the names of the letters, how numbers are said, and the names of punctuation marks. This is eSpeak NG's dictionary for the language, kept in the `openevv-languages` branch of [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages).
- **Sound** is what those sounds sound like in the OpenEVV voice: the vowels and consonants, the accent, the rhythm, the melody of sentences and questions, and the tones. This is kept here, in this repository.

Everything below happens on GitHub. If you do not have an account, make one at github.com; it is free. Every language has a short tag. Find your language in [docs/LANGUAGE-REPORT.md](docs/LANGUAGE-REPORT.md): the tag is in brackets after its name, for example Welsh (`cy`). That page also lists what is already known to be missing in each language.

### Tell us what is wrong (no programming needed)

1. Go to this repository's [Issues](../../issues) page and press **New issue**.
2. For the title, write the language and the problem, for example "Welsh: ll sounds like l".
3. In the description, write the words or the sentence that are wrong, how a native speaker says them, and which voice you heard. Write the words in the language's own spelling. If you know the International Phonetic Alphabet, add that too.
4. If you can, attach a short recording of yourself saying it. Put the recording in a .zip file first, because GitHub does not accept sound files on their own.
5. Press **Submit new issue**.

That is enough. Someone who knows the files can make the change from what you wrote.

### Fix how words, letters, numbers or punctuation are read

These changes go to eSpeak NG's dictionary, and you can make them in your web browser.

1. Open the dictionary folder: [dictsource on the openevv-languages branch](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages/dictsource).
2. Open your language's word list. It is named with the language's code and `_list`, for example `cy_list` for Welsh. An accent or dialect shares its language's list: Scottish English uses `en_list`. The file ending in `_rules` beside it, for example `cy_rules`, has the spelling rules used for every word that is not in the list.
3. Press **Edit this file**. GitHub says you need your own copy to propose changes. Press **Fork this repository**.
4. Make your change. Each line is a word, one or more spaces, and how the word is said, written in eSpeak NG's phoneme letters for the language. For example, English has `hello  h@l'oU`. The `'` goes before the stressed syllable. Lines that begin with `_` are special:
   - `_a` is the name of the letter a.
   - `_1` to `_9`, `_1X` (ten), `_0C` (hundred) and `_0M1` (thousand) are how numbers are built.
   - `_.` and `_,` are the names of punctuation marks.

   Copy the pattern of the lines near yours. eSpeak NG's [dictionary guide](https://github.com/espeak-ng/espeak-ng/blob/master/docs/dictionary.md) and [numbers guide](https://github.com/espeak-ng/espeak-ng/blob/master/docs/numbers.md) explain every kind of line.
5. Press **Commit changes**, write one line saying what you changed, and press **Propose changes**.
6. Press **Create pull request**. In the description, say what was wrong, what is right, and how you know: a dictionary, a grammar, or simply "I am a native speaker".

You do not have to test the change yourself; it is checked before it goes in. If you have eSpeak NG installed, `espeak-ng -v cy -x "word"` shows the phonemes it reads for a word, which helps you check. A fix that is right for eSpeak NG itself is welcome at [espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng) as well, so that every program that uses eSpeak NG gets it.

### Fix how the language sounds: its accent, melody and tones

These changes go to this repository. Each language's sounds are in one text file, `languages/<tag>/sounds.map`, for example `languages/cy/sounds.map`. It says which OpenEVV sound each of the language's sounds is made from, and how it is changed: where a vowel sits, where a consonant is made, how long the voice waits after a stop, the melody of statements and questions, and the tones. [docs/SOUNDS.md](docs/SOUNDS.md) explains every line.

To try a change on your own computer first:

1. Copy the folder `C:\Program Files\OpenEVV SAPI5\languages\<tag>` into `%ProgramData%\OpenEVV\languages`. To open that second folder, type `%ProgramData%\OpenEVV\languages` into File Explorer's address bar. A language in that folder takes the place of the installed one with the same tag.
2. Open `sounds.map` in your copy with Notepad and change one thing, as docs/SOUNDS.md describes.
3. Save the file and listen. The file is read each time a voice starts, so press **Speak** in OpenEVV Configuration, or restart your screen reader.
4. When you are done, delete your copied folder to go back to the installed language.

To send the change:

1. Open the [languages](languages) folder in this repository, then your language's folder, then `sounds.map`.
2. Press **Edit this file**, then **Fork this repository**.
3. Make the same change you tried.
4. Press **Commit changes**, then **Propose changes**, then **Create pull request**. Say what the sound should be and where that is written down.

Each language also has a profile, `engine/profiles/<tag>.json`, which says what books and research say about how the language sounds, with their sources. Its `sounds.map` was first written from the profile. If you know a better source, a change to the profile is welcome too.

### Add an accent or a dialect

An accent is a new voice for a language that is already here, the way Scottish English sits beside British English.

1. Open an issue with a title like "New accent: Welsh English". Say where the accent is spoken and how it differs from the language.
2. eSpeak NG needs a voice for the accent. A voice is a small text file in the `espeak-ng-data/lang` folder of the [openevv-languages branch](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages/espeak-ng-data/lang). Copy the voice of the same language, give the copy the accent's name, and change what differs. Words the accent says differently go in the language's `_list` with a `?` and a number in front of them, and only the voice that asks for that number reads them. eSpeak NG's [voices guide](https://github.com/espeak-ng/espeak-ng/blob/master/docs/voices.md) and the Accent part of its [guide to adding a language](https://github.com/espeak-ng/espeak-ng/blob/master/docs/add_language.md) explain how. Send this as a pull request to the fork, as in the steps above.
3. OpenEVV then needs a language folder for the new voice, in `languages`. The simplest way to make one is to copy the folder of the language, then change `Tag`, `Name` and `Voice` in its `language.ini`, and in `sounds.map` the sounds the accent says differently. Send that as a pull request here. The new voice works once OpenEVV is built with the new eSpeak NG voice. If this step is more than you want to do, stop after step 2; the maintainer can make the folder.

### Add a new language

1. Look in [docs/LANGUAGE-REPORT.md](docs/LANGUAGE-REPORT.md) first: the language may already be there under another name.
2. Open an issue with a title like "New language:" and its name. Say where it is spoken, how it is written, and whether you can listen to it and check it.
3. Teach eSpeak NG to read it. eSpeak NG's [guide to adding a language](https://github.com/espeak-ng/espeak-ng/blob/master/docs/add_language.md) says, step by step, which files a language needs: a voice file, a word list (`_list`), spelling rules (`_rules`), and, if the language has sounds no other language has, a phoneme table. Send the pull request to the `openevv-languages` branch of [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages), and, if you like, to [espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng) too.
4. Describe how it sounds. Copy the profile of a related language in `engine/profiles`, name the copy with your language's tag, and change what is different: its vowels, its consonants, where the stress falls, the melody, and its tones if it has any. Say where each fact comes from.
5. Make the language's folder. This needs the build tools described in "Building from source" below, with `ESPEAK_NG_SOURCE_DIR` set to your eSpeak NG folder. Then `python engine\make_espeak_packs.py --espeak-src <your eSpeak NG folder> --frontend dist\x64\OpenEvvFrontend.exe --data dist\espeak-ng-data <tag>` writes `languages\<tag>`, and `python engine\check_espeak_packs.py dist\x64\OpenEvvFrontend.exe dist\espeak-ng-data <tag>` checks it. If you do not have the tools, stop after step 4 and send the pull request; the maintainer will make the folder.
6. Send a pull request here with the profile and, if you made it, the folder.

### Add a new sound (a phoneme)

Sometimes a language has a sound that neither eSpeak NG nor OpenEVV has yet.

1. In eSpeak NG, the sound goes in the language's phoneme table, in the `phsource` folder. eSpeak NG's [phoneme guide](https://github.com/espeak-ng/espeak-ng/blob/master/docs/phonemes.md) and the Phoneme Definition File part of its [guide to adding a language](https://github.com/espeak-ng/espeak-ng/blob/master/docs/add_language.md) explain how to write one. Then the language's `_list` and `_rules` can use it.
2. In OpenEVV, the new phoneme needs a line in the language's `sounds.map` saying which OpenEVV sound it is made from, and a `sound` line saying how it differs: how far its formants move, how long its voice waits, how much noise it has. [docs/SOUNDS.md](docs/SOUNDS.md) lists every key a `sound` line can have. This is how OpenEVV already makes retroflex, palatal, uvular and pharyngeal consonants, breathy and nasal sounds, h and the glottal stop, and ejectives and implosives as nearly as its kind of synthesiser can.
3. If the sound is something OpenEVV cannot make yet, open an issue and describe it; a recording helps.

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

To ship the language in the installer as well, commit `languages/<tag>/`, run `python installer\make_components.py` (it writes the list of languages the installer offers, in `installer\generated\`, which is committed too) and build a new installer. The installer's build stops, naming the folder, if `languages\` holds one that list does not.

## OpenEVV Configuration

Five pages, all standard Windows controls, every one labelled. Each number is an edit box with a spin button; the arrow keys step it.

- **Voices:** pick a language and one of its eight voices, then adjust gender, head size, pitch, inflection, roughness, breathiness, speed and volume. **Restore this voice's defaults** undoes your changes to that voice. **Speak** plays test text with the settings as they are.
- **Speech:** settings for every voice:
  - the sample rate, and how rates above the engine's native 11,025 Hz are reached
  - the fastest and slowest speeds SAPI's rate +10 and -10 reach, and rate boost (+10 reaches 250)
  - the pitch change per SAPI pitch step
  - abbreviation expansion, and how numbers are read: 1999 as "nineteen ninety-nine", or as a whole number
  - the text mode: normal, spell letters and digits, spell everything, or the radio alphabet
  - punctuation pauses: do not shorten, shorten at end of text only, or shorten all pauses (see below)
  - backquote annotations, English heteronym fixes, naming lone symbols, and user dictionaries
- **Languages:** the installed languages; adding and removing packs; editing the main, root and abbreviation user dictionaries of the selected language.
- **Community dictionary:** the switch for the community pronunciation dictionary, which version of it is in use, and **Check for a newer version and install it** (see below).
- **Diagnostics:** the logging level, the log folder, and a self-test that speaks every voice of every language into memory, in both bitnesses, and one through SAPI itself.

Settings are per user, in `%APPDATA%\OpenEVV\settings.ini`.

### How SAPI's rate, pitch and volume map to the engine

- **Rate:** SAPI rate 0 is each voice's own speed, 50 for most voices. +10 reaches the fastest speed set on the Speech page: 156 by default, the same top as NVDA's own Eloquence driver, or 250 with rate boost. -10 reaches the slowest speed set there, 0 by default. The engine's speed scale is already exponential (each ten units is about 22% faster), so every SAPI step is an even change.
- **Pitch:** each SAPI pitch step moves the voice's pitch baseline by the pitch step set on the Speech page, 4 units by default. NVDA's capital-letter pitch change comes through this way.
- **Volume:** SAPI's volume, and a fragment's own volume, scale the voice's own volume.

### Shorter pauses at punctuation

The engine pauses at a comma, a full stop, a question mark and an exclamation mark for as long as a person reading aloud would, about 155 ms for a comma and 400 ms for the others, and it goes on being silent for about 400 ms after the last word of every text it is given. That is slow for a screen reader. The **Punctuation pauses** setting on the Speech page shortens them, with the three choices of the [IBMTTS driver for NVDA](https://github.com/davidacm/NVDA-IBMTTS-Driver), whose method it uses:

- **Do not shorten:** the engine's own pauses. This is the default, so nothing sounds different until you choose otherwise.
- **Shorten at end of text only:** the silence after the last word of what is said goes, whether the text ends in a mark or not, and the pauses between phrases stay. Every announcement and every character you move over comes out with no silence after it.
- **Shorten all pauses:** every pause at , . : ; ? ! and a dash, in every language, to about 40 ms. The mark still gives the phrase its melody: a question still rises.

It works by putting the engine's one-unit pause annotation, `` `p1 ``, in front of each mark, which the engine reads in place of the pause the mark would make. It applies to all 155 languages: the ten the engine speaks itself take it in the text, and for a language read by eSpeak NG the host puts it into the text eSpeak NG's front-end makes. Three details:

- A full stop that ends an abbreviation ("Mr.", "Dr.", "St.", an initial, an ordinal such as the "3." of "am 3. Mai") is left alone, because the annotation between a word and its dot stops the engine's dictionary from reading it as the abbreviation. Put in front of every dot, as the driver's method does, it changes how such words are read in this engine; this does not.
- While pauses are shortened a backquote in the text is read as a space, as the driver does, because the engine treats a backquote as the start of a command once it accepts the annotation. The "Honour backquote annotations" setting keeps them.
- Nothing is added while the text mode spells, or to `<spell>`: the engine would spell the annotation.

The setting is `PauseMode` (0, 1 or 2) in `settings.ini`. Every running voice takes it on its next utterance.

### The community dictionary

[IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries) is the pronunciation dictionary the IBMTTS community keeps for the Eloquence engine, in the format the engine's own dictionaries have: one entry a line, the word, a tab, and what to say instead (spelt out, or as an annotation with the phonemes, `` `[.1post.2fIks] ``). It has a main, a root and an abbreviation dictionary for US English (`ENU*.dic`); the repository also holds German ones (`DEU*.dic`), which OpenEVV does not use. It is in the public domain (CC0) and is maintained by amirsol81, x0 (ultrasound1372), thunderdrop and many contributors.

- **Where it applies:** the US English voices, and English only. The repository also holds German files, which OpenEVV neither installs nor reads, and no other language is touched, the 145 read by eSpeak NG included. If the project ever publishes British English files (`ENG*.dic`), they are used for the British English voices without a new OpenEVV.
- **Under your own dictionaries:** the engine host loads it first and your own main, root and abbreviation dictionaries (Languages page) after it, so where you and the community disagree about a word, yours wins. Take your entry away and the community's is back.
- **On or off:** the checkbox on the Community dictionary page, saved at once and heard on the next thing any program says. It is on by default, and `CommunityDictionary` (0 or 1) in `settings.ini` is the setting. The Speech page's *Expand abbreviations* switch is the engine's whole dictionary and turns this off with the rest.
- **Two copies, the newer wins:** the version installed with OpenEVV is in `dictionaries\community` beside the program. **Check for a newer version and install it** asks GitHub for the newest commit of the project's `master` branch (the newest, not the monthly release: a fix made yesterday is worth having today). If it is not the one already in use, the branch's zip is downloaded, every file in it is checked against its checksum, and only then are the files put in `%ProgramData%\OpenEVV\community-dictionary`. Every voice already speaking uses them on its next utterance, and nothing restarts. A failed check or download changes nothing and says why; if GitHub's API refuses (it allows sixty requests an hour without a token) the zip alone is enough. Whichever copy has the later commit date is the one in use.
- **Without a window:** `OpenEvvConfig.exe --update-community-dictionary --report FILE` does the same, and its exit code is 1 when it failed.
- **Speed:** the root dictionary has 69,000 entries. The engine reads it in about a tenth of a second, in 32-bit and, since 1.2.3, in 64-bit modules; see the changelog for the fault that had made it 63 seconds in the 64-bit ones.

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
| `src/common/` | shared by all of them: the host protocol and pool, settings, language packs, logging, the community dictionary (`community_dict.*`), and, for OpenEvvConfig alone, its update (`community_update.*`, `http.*`, `zip_reader.*`) |
| `src/config/` | OpenEVV Configuration and its self-test |
| `src/tools/` | test tools: `sapi_test` (the SAPI engine through a mock site), `a11y_check` and `installer_a11y` (what a screen reader sees), `evv_probe` and `evv_chars` (measure a module directly) |
| `languages/` | the 155 language packs: openevv's ten, prebuilt, and the 145 read by eSpeak NG |
| `frontend/` | `OpenEvvFrontend.exe`, which reads those 145 with eSpeak NG (GPL v3; see its README) |
| `dist/` | the built SAPI wrapper, host, utility and eSpeak NG front-end, both bitnesses, and eSpeak NG's compiled data, in the installed layout |
| `openevv/` | the openevv engine source, a snapshot of [joshknnd1982/openevv](https://github.com/joshknnd1982/openevv) at 7148737 (= [Mudb0y/openevv](https://github.com/Mudb0y/openevv) main, 28 September 2026) |
| `engine/` | building the modules and packs from `openevv/`, and the eSpeak NG packs from eSpeak NG (`make_espeak_packs.py`, `espeak_phonemes.py`, `check_espeak_packs.py`, `espeak_templates.txt`) |
| `dictionaries/community/` | the community pronunciation dictionary installed with OpenEVV: the English files of IBMTTSDictionaries at the commit `community-dictionary.ini` names, byte for byte |
| `installer/` | the Inno Setup script, the list of languages it offers (`generated/`, written by `make_components.py` from `languages/`) and `test_language_choice.ps1`, which tests the choice of languages |
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
  - the community dictionary against the engine, with the switch on and off, under the user's own entry, for a language it has no files for, and an update installed from a zip while a voice is speaking: a damaged zip, a file that is not a zip and a zip holding something that is not a dictionary are each refused and leave what was installed alone
- **`sapi_test --all-voices`:** all 1,240 voices through SAPI.
- **`engine\check_espeak_packs.py`:** every eSpeak NG pack's sample, numbers and punctuation read and handed to its template's module, which must take every word as a pronunciation.
- **`a11y_check`:** walks every page of OpenEVV Configuration through MSAA on a private desktop. It fails on an unlabelled control or a duplicated access key, and checks that edits reach the settings file at once.
- **`installer_a11y`:** walks every page of the installer the same way, then installs and uninstalls a non-elevated probe build. On the language page it checks that both lists have names, that there are at least 155 languages, what is checked when upgrading, that **Select all languages** checks everything and **Select no languages** clears it, and that going on with no language is refused with a message.
- **`installer\test_language_choice.ps1`:** installs the probe with every type and with single languages, upgrades it (adding languages, removing them, with nothing on the command line, from an installation that has no record of a choice, after a language was deleted by hand) and uninstalls it, and checks which language packs, and which module packs, are left each time against what `languages\*\language.ini` says they should be. `build_all.bat` runs it.
- **`OpenEvvConfig.exe --selftest`:** every voice of every language in both bitnesses, plus one through SAPI itself. It is the "Run the self-test" button on the Diagnostics page; the installer does not run it, so installing stays quick.

## Logs and troubleshooting

`%ProgramData%\OpenEVV\Logs` has one file per component and program: `sapi-x64-nvda.log`, `host-x64-nvda.log`, `config-openevvconfig.log`, `install.log`, and so on. At the standard level they record every utterance's timings and never the text. Set Logging to Full on the Diagnostics page to include the text too. Please attach the relevant logs to an [issue](../../issues).

## Licence and provenance

- **The wrapper** (everything outside `openevv/`, `frontend/` and `languages/`) is under the GNU General Public License version 2; see `LICENSE`. Its COM and SAPI scaffolding comes from the BestSpeech SAPI5 wrapper.
- **The eSpeak NG front-end** (`frontend/`, `OpenEvvFrontend.exe`), the eSpeak NG data installed with it and the eSpeak NG packs' phoneme maps are under the GNU General Public License version 3 or later, as eSpeak NG is; see `frontend/COPYING`. The front-end is a separate program the wrapper talks to over pipes.
- **The openevv engine** is under the MIT licence; see `openevv/LICENSE`.
- **The community pronunciation dictionary** (`dictionaries/community/`) is [eigencrow/IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries), released to the public domain under CC0 1.0 (its `LICENSE.md` is installed beside it).
- **The language data inside each language module** was transcribed from IBM's Embedded ViaVoice objects, and is IBM's work. Neither licence covers it, and nobody here can license it to anyone. `NOTICE.md` and `openevv/NOTICE` say whose it is and who the rights may belong to today.

`CREDITS.md` names everyone this is built on.
