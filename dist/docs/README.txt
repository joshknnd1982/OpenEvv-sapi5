# OpenEVV SAPI5

The OpenEVV text-to-speech engine as SAPI 5 voices for Windows, in both 32-bit and 64-bit programs: NVDA, JAWS, Balabolka, e-book and document readers, and anything else that speaks through Microsoft SAPI 5.

[openevv](https://github.com/Mudb0y/openevv) is IBM's Embedded ViaVoice engine, the voice people know as Eloquence, rebuilt from IBM's 1999 objects as portable C whose audio matched IBM's own binary sample for sample. This project builds one engine module per language from that source and puts a SAPI 5 interface, a configuration utility and an installer around them. Nothing of IBM's binary code is used, SAPI 4 is not involved, and nothing is read from the registry.

## What you get

- **156 languages, eight voices each, 1,248 SAPI voices** (in version 1.4.0). openevv's own ten: US English, British English, German, Castilian Spanish, Latin American Spanish, French, Canadian French, Italian, Japanese and Polish (experimental, because upstream is still turning Italian rules into Polish ones).
- **And 146 more, read by eSpeak NG:** every language and dialect [eSpeak NG](https://github.com/espeak-ng/espeak-ng) has that openevv does not, from Afrikaans to Yue Chinese, New York City English and Swiss French among them, and Belgian Dutch (Southern Standard Dutch as spoken in Flanders), added in 1.3.0. eSpeak NG reads the text -- its spelling, dictionary, numbers, letter names, punctuation names, stress and tones -- and one of openevv's modules speaks it in the Eloquence voice, with the language's own sounds: Hindi's retroflex and breathy voiced stops, the palatalised consonants of Russian, the nasal vowels of Portuguese, the voicing lead of Hindi and Turkish b, d and g, the taps and trills, the uvulars, the h and the glottal stop the modules never had. Since 1.4.0 these sounds come from the IPA master table (below). Each language has the melody its literature describes, and a question asked with a question word ends differently from one that wants yes or no. Mandarin, Cantonese, Hakka, Vietnamese, Burmese and Shan are spoken with their tones, and so are the low tone of Punjabi and the tones of Cherokee where the text marks them, Mandarin's third tone and neutral tone changing as they do beside other tones. Spelling and moving through a line a character at a time say every letter by its name in the language, an accented letter with its accent. `docs/SOUNDS.md` says how; `docs/LANGUAGE-REPORT.md` says what each language has and what is still missing (written for the sounds of 1.2; `docs/tts-extension/LANGUAGE_STATUS.md` has each language's level now).
- **The eight classic presets in every language:** Adult Male 1 (Reed), Adult Female 1 (Shelley), Child 1, Adult Male 2, Adult Male 3, Adult Female 2, Elderly Female 1 and Elderly Male 1. Voices are named "OpenEVV US English Adult Male 1" and so on.
- **Low latency.** The engine synthesises about 600 times faster than real time. From a program's `Speak()` call to the first audio handed to SAPI takes about 1.5 ms on a warm voice. A cancel returns in well under a millisecond, and the next utterance never waits for the one it replaced.
- **Everything adjustable, live.** OpenEVV Configuration adjusts all eight parameters of every voice in every language: gender, head size, pitch, inflection, roughness, breathiness, speed and volume. It also sets the sample rate (8 to 48 kHz), the resampler, the speed range for SAPI's rate, the pitch step, abbreviation expansion, how numbers are read, the spelling modes, the pauses at punctuation, backquote annotations, English heteronym fixes and user dictionaries. Each change is saved at once and heard on the next thing any program says, a screen reader already speaking included.
- **Languages you can add and remove** as folders, without reinstalling anything. See below.
- **The community pronunciation dictionary** for English, the IBMTTS community's [IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries) (CC0 1.0): a main, a root and an abbreviation dictionary of pronunciation fixes, installed with OpenEVV and read before your own dictionaries. OpenEVV Configuration switches it on and off, and one button looks on GitHub for a newer version and installs it. See below.
- **Everything SAPI asks of an engine:** word, sentence and bookmark events on the exact sample, pauses, `<spell>` (NVDA's character navigation), rate, pitch and volume changes inside an utterance, and sentence skipping. A lone symbol the engine would render as silence is named instead (in Japanese that is most ASCII punctuation), but only when it is the whole utterance, so prose keeps its natural pauses.
- **Logs** of the voices, the engine hosts, the utility and the installer, in `%ProgramData%\OpenEVV\Logs`.

## What is new in 1.4.0: every language read by eSpeak NG speaks with the IPA sounds

*1.4.0 is the first release published with this work: 1.3.0 (the section after this one) was built but never published on its own. If the [Releases](../../releases) page does not show 1.4.0 yet, the release there (1.2.4) has none of it.*

In 1.3.0 every symbol of the IPA chart got a measured sound in the engine, but no language used them: each language read by eSpeak NG still spoke with the sounds an older generator had written for it. **In 1.4.0 all 146 of them, languages, dialects and accents, speak with the IPA master table's sounds**, the same table the chart's proofs use, so a sound fixed once in the table is fixed for every language that has it. The ten languages the engine speaks itself are unchanged, and so are the engine's modules, the eSpeak NG front-end and its data.

**How a language's sounds are made now.** Each language's pack names each of its sounds as IPA (`[master.ipa]` in `packs/<tag>/pack.toml`), and the pack compiler (`realization = "master"`, `engine/packs/master.py`) makes the sound from the table when the pack is built: a sound the module speaking the language already has is said as that module's own sound; one it lacks comes from the table, composed from a base sound and its marks where it can be; and a language's own published measurements (stop timing, vowel formants) are used where a study gives them, each sound line naming its source. Counted by the tool over the 146 packs (`engine\packs\to_master.py --all --dry-run`): 17,166 sounds taken from the table, 14,319 composed, 12,567 created; 6 left on their 1.3.0 sound because the table cannot read eSpeak NG's IPA for them (French `#cFR`), 12 kept on their 1.3.0 sound so that two different phonemes do not come out alike (in Mandarin, Cantonese, Burmese, Marathi, Gujarati and Vietnamese), and 980 said as nothing because they are marks or boundaries, not sounds.

**Said plainly: some languages may sound odd, and many of these sounds are hypotheses.** Nobody who made this can hear most of these languages, and Claude, which did the work, cannot hear at all. The sounds were checked by measurement (every phoneme of every language rendered and measured: the engine check passes in 155 of the 156 languages) and by a speech recogniser (Whisper large-v3) on eight test sentences per language. Against 1.3.0, over the 96 languages the recogniser can score, the median change in character error is -0.007: 52 are understood better, 44 worse. **Harder to understand than in 1.3.0 by more than 0.10:** Cantonese, Welsh, Malay, Sindhi, Greek, Burmese and Faroese. These are measurements of a recogniser, not of listeners, and they vary: Cantonese, Sindhi, Welsh, Mandarin, Sinhala, Malayalam, Punjabi and Tamil gave a different figure in two runs of the same build (Cantonese 1.52 and 2.10), so Sindhi is on this list in one run and not in the other. Brazilian Portuguese dropped from level 4 to level 2 (one vowel 33 Hz outside a published range), though it is understood better than before. Quechua stays at level 1 (its ejectives, as in 1.3.0). Every language's figures are in [`docs/tts-extension/IPA_SWITCH_REPORT.md`](docs/tts-extension/IPA_SWITCH_REPORT.md).

**One language back to its 1.3.0 sounds.** In its pack, `packs/<tag>/pack.toml`, set `realization = "legacy"` under `[engine]`, then `python engine\packs\build_packs.py build languages <tag>` rebuilds `languages\<tag>\` with the old sound lines, which the pack still holds. If you would rather hear a language as 1.3.0 said it, say so in an issue.

**A fault found and fixed before release.** The installer build's own check of every language pack found that in 65 languages a diphthong said with the module's own two-part phone (as in English *eye*, German *ei*) made the engine lose its place and put later words' sounds on the wrong vowels (in Vietnamese, 43 of the 199 sounds of the check's text). Those diphthongs are now a vowel gliding to the next, as the table writes them; the check passes for all 146 again, and the figures above were measured after the fix (`docs/tts-extension/DECISIONS.md` D99).

**Levels now** ([`docs/tts-extension/LANGUAGE_STATUS.md`](docs/tts-extension/LANGUAGE_STATUS.md)): **1 at level 1** (Quechua), **152 at level 2**, **3 at level 4** (US English, New York English, Portuguese), none at level 3 or 5. **No language is confirmed authentic**: only a named native speaker's signed review can raise a language to level 5.

**Native speakers, please tell us.** See "Native speakers: help make your language right" below: a [language review issue](../../issues/new?template=language-review.yml), a pull request to the language's `pack.toml`, or a review packet's `feedback.toml`.

## What came in 1.3.0: the whole IPA chart, language packs and a new dialect

*1.3.0 was built but never published on its own: everything in this section reaches users with 1.4.0.*

The aim of this work (the "TTS extension", recorded in `docs/tts-extension/`): every symbol of the International Phonetic Alphabet has a defined sound in this engine, so that adding a language, a dialect or an accent is a change to a text file, and its sounds are checked by measurement rather than by anyone's ear. The person who maintains this project speaks only American English, and Claude, the AI that did the work, cannot hear at all. So nothing here was judged to "sound right": every check is a measurement of the engine's own output. Every language has a **level** (below), and only a native speaker's signed review can make one authentic. Many sound values are tagged `estimated`, `created` or `approximate`: they are reasoned hypotheses, waiting for a phonetician or a native speaker to check them.

### The sounds: the whole IPA chart

The official IPA chart (`IPA_Kiel.pdf`, the 2026 issue, CC BY-SA 4.0) was read symbol by symbol and checked against Unicode and a phonetics reference: **175 symbols**, consonants, clicks, implosives and ejectives, vowels, diacritics, suprasegmentals, and tones and word accents. Every one now has a sound in the engine: **67** were sounds the engine already had (mapped), **53** are a base sound with a mark (composed), and **55** are new (created). **None is missing and none is blocked**; none is silent or silently replaced by another. Each was spoken by the real engine, alone and between vowels, and measured (formants, bursts, voice onset, noise, length, pitch): all 175 proofs pass, and each is kept in `ipa/proofs/`. Six are marked `approximate`, with what is missing said in words. Beyond the chart, **186 of the 203** symbols of extIPA and VoQS (the notation for disordered speech and voice quality) are done the same way; the other 17 are notation only, with nothing to say (the human accepted this, `docs/tts-extension/DECISIONS.md` D81). Every new sound, 76 in all, is listed in [`docs/tts-extension/CREATED_SOUNDS.md`](docs/tts-extension/CREATED_SOUNDS.md) with why the old sounds were not enough and what its values rest on.

What the engine could not make before and can make now, as nearly as a formant synthesiser can:

- clicks, ejectives and implosives; trills at their own rate, taps and flaps; uvular, pharyngeal and epiglottal consonants; retroflex and palatal consonants; lateral fricatives and affricates;
- breathy, creaky, whispered and harsh voice; voiceless nasals and vowels; partial voicing; labialised, palatalised, velarised and pharyngealised consonants; nasalised vowels; long and extra-short sounds;
- tones: the tone letters (˥ ˦ ˧ ˨ ˩ and their contours), the tone diacritics, registers, downstep and upstep, and global rise and fall.

A mark or a tone letter is a change applied to whatever sound it is written on, so it works on any base, not on a list. Two examples from the proofs: the ejective mark ʼ on t moves the start of the voice from 18 ms after the release to 110 ms (the target is 82 to 136 ms), with no breath in the gap; and the falling tone ˥˩ on [a] starts 6.19 semitones above 100 Hz (the target is 6.03) and falls at 78.5 semitones a second (the target is at least 22).

**Who can use these sounds today.** They are tools for whoever writes or improves a language: `docs/SOUNDS.md` lists every key, and `engine\ipa\say_ipa.py` says and measures any IPA. In 1.3.0 no language used them yet. Since 1.4.0 every one of the 146 languages read by eSpeak NG speaks with the table's sounds, and every one of their sound maps uses some of these keys (trill rate and depth, ejective bursts, places of articulation among them; counted in the shipped `sounds.map` files). Text is read as it was, and speaking IPA typed into a SAPI program is a later addition.

### Changes to the language packs

- **Every language is a pack**: one readable text file, `packs/<tag>/pack.toml`, which says which eSpeak NG voice reads the text, which of the engine's seven template modules speaks it, and how each of its sounds differs from the template's nearest one. The files the product reads in `languages/` are built from the packs, and `engine\packs\build_packs.py check` proves them identical (163 packs: the 156 languages and the 7 templates). [`packs/README.md`](packs/README.md) explains the format.
- **A new dialect or accent `extends` its parent** and holds only what differs, each change with a published source or a measurement (18 packs extend a parent today; eight older English and French dialects are whole packs). A dialect's pack names the variety, the region, the speakers described, its sources and recordings, and a validator refuses a dialect pack without them: all 22 dialect packs pass.
- **Measured overrides.** A pack can move a vowel to values measured from licensed recordings or taken from a published table, each value tagged with where it came from. Belgian Dutch, new in 1.3.0, is the first to ship with them: eleven vowels from Adank, van Hout and Smits (2004), Flemish men. Said plainly: on the same eight test sentences a speech recogniser understands it less well than Dutch (character error 0.293 against 0.199), so it waits for a Flemish speaker's review. Scottish English's ten vowels measured from one Scottish speaker's recordings (CMU ARCTIC, `third_party/cmu_arctic/`) are proposed only, not shipped.
- **Every language has a level**, earned only by evidence: 1 draft; 2 engine-verified (the engine says what it is told, nothing swapped or silent); 3 reference-verified (its sounds fall in published ranges); 4 intelligibility-verified (a speech recogniser understands its test sentences); 5 native-validated (a named native speaker signed its review packet). Of the 156 languages in 1.3.0: **3 at level 1** (Mandarin, Mandarin in pinyin, Quechua), **149 at level 2**, **4 at level 4** (US English, New York English, Portuguese, Brazilian Portuguese), none at level 3 or 5 (1.4.0's levels are in the section above). **No language is confirmed authentic.** [`docs/tts-extension/LANGUAGE_STATUS.md`](docs/tts-extension/LANGUAGE_STATUS.md) gives each language's level and the layer where it fails first (sound values, reading of the spelling, stress or tone, or not yet known).
- **Review packets**: one web page per language for a native speaker to listen to and answer (see "Native speakers" below).

### Changes to the engine

- The synthesiser and IBM's rule engine are kept, not replaced. The **accent layer** inside the engine, which gives a language read by eSpeak NG its own sounds, gained the keys the chart needed: trill rate and depth, a click's second release, ejective bursts, the place of a consonant shown on its neighbours, partial voicing, fricated releases, strikes, diplophonia, jitter, monotone, silent articulation and more. The seven template modules are rebuilt with it.
- The eSpeak NG **front-end** now reads IPA marks, tone letters and extIPA's braces and composes them on their base sounds.
- **Two defects fixed**: a stop's voice onset no longer leaks onto a voiceless sound or a pause after it (at the end of Russian "кот.", Hindi "आप." or New York English "cat." the hum is gone), and a tone's level setting, read and never used before, now works (Mandarin's neutral tone is 3 dB softer, as its table says). And a voiceless l or w no longer lends its voice to the s after it.
- **What that changes in the languages already here**, measured: of the 29,237 cases of the golden regression (every sound of every language, measured and recorded), 1,136 in 143 languages changed: 1,133 of them a consonant at a word's end or before another consonant, and 3 Shavian English vowels where the English module itself turns t before them into t and sh; the maintainer saw them and said to ship them (`DECISIONS.md` D40 to D43, D87, D95); the other 28,101 are identical.

### What did not change

The SAPI interface, OpenEVV Configuration and its settings, the installer's choice of languages (Belgian Dutch is one more box in it), and the ten languages the engine speaks itself: their modules are the same files as in 1.2.4.

**One command checks it all:** `python engine\doctor.py` (with the harness's Python, `ADDING_A_LANGUAGE.md` section 1) runs the harness self-test, the pack tests, the pack validator, the IPA coverage count and, without `--quick`, the golden regression of all 156 languages.

## Installing

Download `OpenEVV-SAPI5-Setup-<version>.exe` from the [Releases](../../releases) page and run it. It installs both SAPI interfaces, OpenEVV Configuration (with a desktop shortcut, and in the Start menu), the documentation and the languages you choose. It checks that the voices are registered with Windows and states the result on its last page. The wizard is Inno Setup's standard one and works with screen readers.

**Choosing the languages.** Every language adds eight voices to every SAPI 5 program, and 156 languages are 1,248 voices, a long list for a screen reader or any other program to go through, and more than some programs take well. So the wizard's **Select languages** page lets you install only the ones you will use. It has a check box for each of the 156 languages, and a list of ready-made choices above them:

- *The ten OpenEVV languages* (80 voices), the languages the engine speaks itself: US and British English, German, Castilian and Latin American Spanish, French, Canadian French, Italian, Japanese and Polish. This is what the wizard offers first on a computer with no OpenEVV on it.
- *English only*: US and British English (16 voices).
- *All 156 languages* (1,248 voices): the ten above and the 146 read by eSpeak NG.
- *Custom*: check the languages one by one. **Select all languages** and **Select no languages** under the list check or clear every one; at least one language has to be selected, and the wizard says so if none is.

Each language that eSpeak NG reads is spoken by one of the engine's modules; the wizard installs that module when you choose a language that needs it, and only then, so a single such language adds about 9 to 17 MB.

**Changing the languages later.** Run the installer again. Its language page offers exactly the languages that are installed now; it installs the ones you add and removes the ones you clear, and never asks Windows to restart. Installing over a version that put every language in (1.2.3 and earlier) offers all of them, so nothing is removed unless you clear it. A language you removed yourself with OpenEVV Configuration is not put back. OpenEVV Configuration's Languages page also removes languages one at a time, and adds language packs.

**Unattended installs.** With nothing on the command line, an install over an existing one keeps exactly the languages that are installed, and one on a computer with no OpenEVV installs the ten OpenEVV languages. `/TYPE=full` installs all 156, `/TYPE=english` US and British English, `/TYPE=openevv` the ten. `/COMPONENTS="openevv\enus,espeak\nb"` names languages: `openevv\` or `espeak\` and the language's folder name in `languages\`, with `-` written as `_` (`espeak\en_gb_scotland`); `installer\generated\components.inc` lists them all.

Windows may say "Windows protected your PC" first. That is SmartScreen noting a new, unsigned download, not a detection: choose More info, then Run anyway.

Installing over an older version keeps your settings and the languages you have installed, and Windows never needs to restart. Files a running program still has open (a screen reader using an OpenEVV voice, say) are renamed out of the way and the new ones installed beside them: every program started afterwards uses the new version at once, and the programs that were already running keep the old one until you close them and start them again. The installer's last page names those programs.

## Native speakers: help make your language right

OpenEVV speaks 146 languages through eSpeak NG. Most of them were built from dictionaries, grammars and published research, not by people who speak them, so not every language is right yet, and **none is marked authentic until a native speaker has said so**. If you speak one of them, you can make it better. You do not need to be a programmer to start.

### How to send a correction

Three ways, from the simplest:

1. **Open a [language review issue](../../issues/new?template=language-review.yml)** (the form asks which language, the variety you speak, whether you understand it, what sounds wrong, and whether your name may be recorded). No programming needed. A recording helps: put it in a .zip first.
2. **Send a pull request to the language's pack**, `packs/<tag>/pack.toml` (see "Fix how the language sounds" below).
3. **Fill in a review packet's `feedback.toml`** and attach it (zipped) to a language review issue (see the next part).

A signed review from a named native speaker changes one thing by itself: the language's **level**, to 5 (native-validated). What you report becomes a change to the pack, which is measured like any other before it ships, and the maintainer decides what ships.

### The quickest help: review a language with its review packet

A review packet is one web page, `index.html`, for one language, dialect or accent, with a short `README.md`, a `CHECKLIST.md` and a form, `feedback.toml`. The page holds recordings of words, sentences and minimal pairs, the sounds the project is least sure of, a picture of each sound described in words, and questions: is it understandable, does a vowel sound like X or like Y, is anything buzzy, breathy or harsh, which sentences are least natural. Where the project changed a vowel it plays two versions without saying which is which (a blind A/B), so that your answer is not led. You answer in `feedback.toml` with your name, the date and your variety of the language; the maintainer records it with `engine\review\ingest_feedback.py`. **A signed form from a named native reviewer changes one thing: the language's level, to 5 (native-validated).** It changes no sound by itself; what you report becomes a change in the pack, measured like any other. Packets exist for Scottish English, Belgian Dutch, Welsh, Icelandic, southern Vietnamese, Cantonese, Finnish, Ukrainian, Malay, Tatar, Greek and Burmese (`docs/tts-extension/review_packets/`); one for any other language is made with `engine\review\make_packet.py <tag>`, and if you cannot make one, open an issue naming the language and ask for it. `docs/tts-extension/FINDING_NATIVE_REVIEWERS.md` is for the maintainer: where native reviewers can be found.

### Adding or improving a language, a dialect or an accent as a pack

[`ADDING_A_LANGUAGE.md`](ADDING_A_LANGUAGE.md) is the guide: three worked examples (a language, a dialect that inherits, an accent), each with the commands that were run and what they printed. Start every session with the doctor, `engine\doctor.py --quick`; it must end with `0 FAILED`. The same steps are slash commands for Claude Code in this repository: `/add-language`, `/add-dialect`, `/add-accent`, `/improve-language`, `/diagnose-language` and `/create-missing-sound`, each ending with an independent review. In short:

- **a new language** starts with `engine\packs\new_language.py <eSpeak NG voice> <tag> --out packs-proposed`, which makes a pack from the voice; you then correct its sounds, measure it (`docs\tts-extension\harness\check_language.py`) and make its packet. eSpeak NG must already read the language (see "Add a new language" below);
- **a dialect or an accent** is a pack that `extends` its parent and lists only differences, each with a source or a measurement; a guess is refused for a dialect, and nothing may be a caricature;
- **improving a language** begins at its failure layer in `LANGUAGE_STATUS.md` (sound values, reading of the spelling, stress or tone, timing); `/diagnose-language` turns a listener's description into measurements, `/improve-language` changes only that layer and runs the whole regression, so that one language's fix cannot break another;
- **a missing sound** is asked for in an issue, or made with `/create-missing-sound`: composed from a base and marks, or from a near neighbour, or with a new engine capability, then registered in `CREATED_SOUNDS.md` with a number that never changes.

New packs wait in `packs-proposed/`. **The maintainer decides what ships**: a pack moves to `packs/` and into an installer only with the maintainer's say-so. What cannot be done yet is listed in the guide's section 10 (a language eSpeak NG cannot read; accent rules beyond vowel targets; overrides on the ten native languages).

The sections below are the routes that need no tools: an issue, or a change to a file on GitHub.

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

These changes go to this repository. Each language's sounds are in its pack, `packs/<tag>/pack.toml`, for example `packs/cy/pack.toml`, from which the installed `languages/<tag>/sounds.map` is built. It says which OpenEVV sound each of the language's sounds is made from, and how it is changed: where a vowel sits, where a consonant is made, how long the voice waits after a stop, the melody of statements and questions, and the tones. [docs/SOUNDS.md](docs/SOUNDS.md) explains every line of `sounds.map`, and [packs/README.md](packs/README.md) how the pack holds them.

To try a change on your own computer first:

1. Copy the folder `C:\Program Files\OpenEVV SAPI5\languages\<tag>` into `%ProgramData%\OpenEVV\languages`. To open that second folder, type `%ProgramData%\OpenEVV\languages` into File Explorer's address bar. A language in that folder takes the place of the installed one with the same tag.
2. Open `sounds.map` in your copy with Notepad and change one thing, as docs/SOUNDS.md describes.
3. Save the file and listen. The file is read each time a voice starts, so press **Speak** in OpenEVV Configuration, or restart your screen reader.
4. When you are done, delete your copied folder to go back to the installed language.

To send the change:

1. Open the [packs](packs) folder in this repository, then your language's folder, then `pack.toml`. Since 1.4.0 the sound lines of `sounds.map` are made from the IPA master table when the pack is built, so the change goes in one of two places: if a sound is simply the wrong sound, change which IPA sound the phoneme is under `[master.ipa]` (Welsh *ll* is the line `"@cy:l#" = "ɬ"`); if it is the right sound but should be made differently in your language (a vowel higher, a stop with a longer delay), describe it in the pull request and name your source, and the maintainer writes it as an `[[override]]` with that source. A dialect's pack holds only its own differences; the rest is in its parent's.
2. Press **Edit this file**, then **Fork this repository**.
3. Make the change.
4. Press **Commit changes**, then **Propose changes**, then **Create pull request**. Say what the sound should be and where that is written down. The maintainer rebuilds `languages/<tag>/` from the pack and measures it before it ships. A sound the master table does not have yet goes into the table, not into one pack, so every language can use it.

Each language read by eSpeak NG also has a profile, `engine/profiles/<tag>.json`, which says what books and research say about how the language sounds, with their sources; its first `sounds.map` was written from it. The pack is what is built from now on, so a correction goes into the pack, with its source; a better source for the profile is welcome too.

### Add an accent or a dialect

An accent is a new voice for a language that is already here, the way Scottish English sits beside British English and Belgian Dutch beside Dutch.

1. Open an issue with a title like "New accent: Welsh English". Say where the accent is spoken and how it differs from the language.
2. eSpeak NG needs a voice for the accent. A voice is a small text file in the `espeak-ng-data/lang` folder of the [openevv-languages branch](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages/espeak-ng-data/lang). Copy the voice of the same language, give the copy the accent's name, and change what differs. Words the accent says differently go in the language's `_list` with a `?` and a number in front of them, and only the voice that asks for that number reads them. eSpeak NG's [voices guide](https://github.com/espeak-ng/espeak-ng/blob/master/docs/voices.md) and the Accent part of its [guide to adding a language](https://github.com/espeak-ng/espeak-ng/blob/master/docs/add_language.md) explain how. Send this as a pull request to the fork, as in the steps above.
3. OpenEVV then needs a pack for it: a short `packs-proposed/<tag>/pack.toml` that `extends` the language and holds only what the accent or dialect says differently, each with its source, and who it describes. `ADDING_A_LANGUAGE.md` section 4 shows one, step by step, and `/add-dialect` or `/add-accent` does it with Claude Code. Send that as a pull request here. If this step is more than you want to do, stop after step 2; the maintainer can make the pack.

### Add a new language

1. Look in [docs/LANGUAGE-REPORT.md](docs/LANGUAGE-REPORT.md) first: the language may already be there under another name.
2. Open an issue with a title like "New language:" and its name. Say where it is spoken, how it is written, and whether you can listen to it and check it.
3. Teach eSpeak NG to read it. eSpeak NG's [guide to adding a language](https://github.com/espeak-ng/espeak-ng/blob/master/docs/add_language.md) says, step by step, which files a language needs: a voice file, a word list (`_list`), spelling rules (`_rules`), and, if the language has sounds no other language has, a phoneme table. Send the pull request to the `openevv-languages` branch of [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages), and, if you like, to [espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng) too.
4. Describe how it sounds: its vowels, its consonants, where the stress falls, the melody, and its tones if it has any, and where each fact comes from. Writing that in the issue is enough.
5. Make the language's pack. Once the eSpeak NG data in `dist\espeak-ng-data` has the new voice (the maintainer rebuilds it), `engine\packs\new_language.py <voice> <tag> --out packs-proposed` writes the pack, and `ADDING_A_LANGUAGE.md` section 3 shows the rest: correcting its sounds, measuring it and making its review packet. Not yet run for a language this repository does not already read: every language the shipped eSpeak NG data reads has a pack, so the guide's worked example is a test copy of Swahili. If you do not have the tools, stop after step 4 and send the pull request; the maintainer will make the pack.
6. Send a pull request here with the pack in `packs-proposed/`.

### Add a new sound (a phoneme)

Sometimes a language has a sound that neither eSpeak NG nor OpenEVV has yet.

1. In eSpeak NG, the sound goes in the language's phoneme table, in the `phsource` folder. eSpeak NG's [phoneme guide](https://github.com/espeak-ng/espeak-ng/blob/master/docs/phonemes.md) and the Phoneme Definition File part of its [guide to adding a language](https://github.com/espeak-ng/espeak-ng/blob/master/docs/add_language.md) explain how to write one. Then the language's `_list` and `_rules` can use it.
2. In OpenEVV, the new phoneme needs a line in the language's pack saying which OpenEVV sound it is made from, and a `sound` line saying how it differs: how far its formants move, how long its voice waits, how much noise it has. [docs/SOUNDS.md](docs/SOUNDS.md) lists every key a `sound` line can have. Every symbol of the IPA chart already has a sound in the master table (`ipa/table/`), so look there first: [`docs/tts-extension/CREATED_SOUNDS.md`](docs/tts-extension/CREATED_SOUNDS.md) lists the sounds made for it.
3. If the sound is something OpenEVV cannot make yet, open an issue and describe it; a recording helps. `/create-missing-sound` in Claude Code designs, measures and registers a new one.

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

A language in openevv is text: its rules, tables and dictionary in `openevv/lang/<tag>/`, which upstream's build compiles into the engine (`openevv/docs/language.md` explains each file). Turning one into a pack that users can install as above (not run for 1.3.0 or 1.4.0, which made no new native module; `zip_language_pack.py --espeak` made 1.4.0's download of the 146 languages read by eSpeak NG):

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

It works by putting the engine's one-unit pause annotation, `` `p1 ``, in front of each mark, which the engine reads in place of the pause the mark would make. It applies to all 156 languages: the ten the engine speaks itself take it in the text, and for a language read by eSpeak NG the host puts it into the text eSpeak NG's front-end makes. Three details:

- A full stop that ends an abbreviation ("Mr.", "Dr.", "St.", an initial, an ordinal such as the "3." of "am 3. Mai") is left alone, because the annotation between a word and its dot stops the engine's dictionary from reading it as the abbreviation. Put in front of every dot, as the driver's method does, it changes how such words are read in this engine; this does not.
- While pauses are shortened a backquote in the text is read as a space, as the driver does, because the engine treats a backquote as the start of a command once it accepts the annotation. The "Honour backquote annotations" setting keeps them.
- Nothing is added while the text mode spells, or to `<spell>`: the engine would spell the annotation.

The setting is `PauseMode` (0, 1 or 2) in `settings.ini`. Every running voice takes it on its next utterance.

### The community dictionary

[IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries) is the pronunciation dictionary the IBMTTS community keeps for the Eloquence engine, in the format the engine's own dictionaries have: one entry a line, the word, a tab, and what to say instead (spelt out, or as an annotation with the phonemes, `` `[.1post.2fIks] ``). It has a main, a root and an abbreviation dictionary for US English (`ENU*.dic`); the repository also holds German ones (`DEU*.dic`), which OpenEVV does not use. It is released under CC0 1.0 and is maintained by amirsol81, x0 (ultrasound1372), thunderdrop and many contributors.

- **Where it applies:** the US English voices, and English only. The repository also holds German files, which OpenEVV neither installs nor reads, and no other language is touched, the 146 read by eSpeak NG included. If the project ever publishes British English files (`ENG*.dic`), they are used for the British English voices without a new OpenEVV.
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

The eSpeak NG front-end is built too, with eSpeak NG fetched from [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng) (so the first build wants the internet and Git), or from a local checkout with `set ESPEAK_NG_SOURCE_DIR=C:\path\to\espeak-ng`. With a 64-bit Python on the PATH, every eSpeak NG pack is also checked against its template's module. `build_all.bat packs` writes the 145 eSpeak NG packs of 1.2 in `languages\` again from eSpeak NG's sources, choosing each template and translating each phoneme table (it predates `packs/`; `engine\packs\build_packs.py build languages <tag>` builds a language's folder from its pack).

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
| `languages/` | the 156 languages as the product reads them: openevv's ten, prebuilt, and the 146 read by eSpeak NG, built from `packs/` |
| `frontend/` | `OpenEvvFrontend.exe`, which reads those 146 with eSpeak NG (GPL v3; see its README) |
| `dist/` | the built SAPI wrapper, host, utility and eSpeak NG front-end, both bitnesses, and eSpeak NG's compiled data, in the installed layout |
| `openevv/` | the openevv engine source, a snapshot of [joshknnd1982/openevv](https://github.com/joshknnd1982/openevv) at 7148737 (= [Mudb0y/openevv](https://github.com/Mudb0y/openevv) main, 28 September 2026) |
| `packs/` | every language as a pack (`pack.toml`); a dialect or accent `extends` its parent. `packs-proposed/` holds new ones not yet shipped |
| `ipa/` | the IPA master table (`table/`), its aliases and sources, and a rendered, measured proof for every symbol (`proofs/`) |
| `ADDING_A_LANGUAGE.md` | how to add or improve a language, dialect or accent, with worked examples |
| `docs/tts-extension/` | the extension's records: decisions, design, created sounds, language status, the licence audit, references, the IPA checklist, the measurement harness (`harness/README.md`), review packets |
| `third_party/` | CMU ARCTIC speaker awb, the recordings the Scottish English measurements rest on (CMU's notice) |
| `IPA_Kiel.pdf` | the IPA chart, 2026 issue (CC BY-SA 4.0) |
| `engine/` | building the modules and packs from `openevv/`, and the eSpeak NG packs from eSpeak NG (`make_espeak_packs.py`, `espeak_phonemes.py`, `check_espeak_packs.py`, `espeak_templates.txt`) |
| `dictionaries/community/` | the community pronunciation dictionary installed with OpenEVV: the English files of IBMTTSDictionaries at the commit `community-dictionary.ini` names, byte for byte |
| `installer/` | the Inno Setup script, the list of languages it offers (`generated/`, written by `make_components.py` from `languages/`) and `test_language_choice.ps1`, which tests the choice of languages |
| `samples/` | every voice of openevv's own ten languages, rendered straight from the engine modules; the samples of the 146 eSpeak NG languages, as 1.4.0 says them, are a download on the Releases page (`engine/render_espeak_samples.py`) |

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
- **`sapi_test --all-voices`:** all 1,248 voices through SAPI.
- **`engine\check_espeak_packs.py`:** every eSpeak NG pack's sample, numbers and punctuation read and handed to its template's module, which must take every word as a pronunciation and say each phone where the pack's map put it (this check found the fault fixed before 1.4.0).
- **`a11y_check`:** walks every page of OpenEVV Configuration through MSAA on a private desktop. It fails on an unlabelled control or a duplicated access key, and checks that edits reach the settings file at once.
- **`installer_a11y`:** walks every page of the installer the same way, then installs and uninstalls a non-elevated probe build. On the language page it checks that both lists have names, that there are at least 155 languages, what is checked when upgrading, that **Select all languages** checks everything and **Select no languages** clears it, and that going on with no language is refused with a message.
- **`installer\test_language_choice.ps1`:** installs the probe with every type and with single languages, upgrades it (adding languages, removing them, with nothing on the command line, from an installation that has no record of a choice, after a language was deleted by hand) and uninstalls it, and checks which language packs, and which module packs, are left each time against what `languages\*\language.ini` says they should be. `build_all.bat` runs it.
- **`engine\doctor.py`:** the extension's health check: the harness's own self-test, the pack loader's tests, every pack validated, the IPA coverage count (zero MISSING or BLOCKED), the pack check above (on three languages with `--quick`) and, without `--quick`, the golden regression of all 156 languages against the recorded measurements.
- **`engine\check_licences.py`:** puts every tracked file in one licence class by a rule and fails on a file no rule takes (`docs/tts-extension/LICENCE_AUDIT.md`).
- **`engine\check_readme.py`:** every relative link and path in this README exists, the version it names is `version.h`'s, and no line stretches the MIT licence over files the licence audit puts in another class.
- **`OpenEvvConfig.exe --selftest`:** every voice of every language in both bitnesses, plus one through SAPI itself. It is the "Run the self-test" button on the Diagnostics page; the installer does not run it, so installing stays quick.

## Logs and troubleshooting

`%ProgramData%\OpenEVV\Logs` has one file per component and program: `sapi-x64-nvda.log`, `host-x64-nvda.log`, `config-openevvconfig.log`, `install.log`, and so on. At the standard level they record every utterance's timings and never the text. Set Logging to Full on the Diagnostics page to include the text too. Please attach the relevant logs to an [issue](../../issues).

## Licence and provenance

All of this project's own work is under the MIT licence (`LICENSE`); not every file in this repository is. [`docs/tts-extension/LICENCE_AUDIT.md`](docs/tts-extension/LICENCE_AUDIT.md) puts every file in one licence class by a rule, and `engine\check_licences.py` checks it.

- **This project's own work**: the wrapper, the tools, the build and installer scripts, the TTS extension's harness, IPA tables, proofs, packs' own data and documents, is under the MIT licence; see `LICENSE`. The wrapper's COM and SAPI scaffolding comes from the BestSpeech SAPI5 wrapper; the files adapted from it, and the SAPI DLL built from them, are not covered by that licence, and `NOTICE.md` lists them.
- **The eSpeak NG front-end** (`frontend/`, `OpenEvvFrontend.exe`), the eSpeak NG data installed with it and the eSpeak NG packs' phoneme maps are under the GNU General Public License version 3 or later, as eSpeak NG is; see `frontend/COPYING`. The front-end is a separate program the wrapper talks to over pipes.
- **The openevv engine** is under the MIT licence; see `openevv/LICENSE`.
- **The community pronunciation dictionary** (`dictionaries/community/`) is [eigencrow/IBMTTSDictionaries](https://github.com/eigencrow/IBMTTSDictionaries), released under CC0 1.0 (its `LICENSE.md` is installed beside it).
- **Other people's data kept in the tree**, each under its own terms and named in `NOTICE.md`: the IPA chart and its images (CC BY-SA 4.0), CMU ARCTIC speaker awb (`third_party/cmu_arctic/`, CMU's notice), the Unicode data files (Unicode License v3), the test sentences (Common Voice CC0, Tatoeba CC BY 2.0 FR), and `praat_crosscheck.py` (GPL, it imports Praat). The engine's rendered speech in `samples/` and the review packets is IBM's language data at work and is not offered under the MIT licence.
- **The language data inside each language module** was transcribed from IBM's Embedded ViaVoice objects, and is IBM's work. Neither licence covers it, and nobody here can license it to anyone. `NOTICE.md` and `openevv/NOTICE` say whose it is and who the rights may belong to today.

`CREDITS.md` names everyone this is built on.
