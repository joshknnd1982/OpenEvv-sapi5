# OpenEvvFrontend: eSpeak NG's reading, in openevv's voice

openevv speaks ten languages, each a module of rules transcribed from IBM's Embedded ViaVoice. OpenEVV SAPI5 adds 145 more from [eSpeak NG](https://github.com/espeak-ng/espeak-ng): eSpeak NG reads the text, and an openevv module says what it read.

`OpenEvvFrontend.exe` is the reader. Given a language pack's eSpeak NG voice and its `phonemes.map`, it takes a text through eSpeak NG's own translation, clause by clause, exactly as eSpeak NG would before speaking it: the language's spelling rules and dictionary, its numbers, abbreviations and letter names, its word stress and its switches into other languages. It then writes every word as a pronunciation annotation in the phones of the pack's *template*, the openevv module that speaks it:

    Watu wote wamezaliwa huru. Nina miaka 25.
    `[.1wa.0tu] `[.1wo.0te] `[.0wa.0me.0za.1li.0wa] `[.1ju.0Ru]. `[.1ni.0na] `[.0mi.1a.0ka] `[.0i.0Si.1Ri.0ni.0na] `[.1ta.0no].

That is Swahili as eSpeak NG reads it, in the phones of openevv's Castilian Spanish: the h of *huru* is the Spanish jota, and 25 is *ishirini na tano*. The engine host (`OpenEvvHost.exe`) sends it the text of each utterance and hands the annotated result to the template's engine, which speaks it with its own voices, rhythm and melody. The punctuation that ends each clause is kept, so the engine's intonation follows the sentence. Each word comes back with the characters it was read from, so SAPI's word events and bookmarks land on the right words.

## The phoneme map

`phonemes.map`, in every eSpeak NG pack, is the translation between eSpeak NG's phonemes and the template's. `engine/espeak_phonemes.py` writes it from eSpeak NG's phoneme tables. Every phoneme a language uses is given the template phones nearest to it, by place, manner and voicing for a consonant and by height, backness and rounding for a vowel, unless the template has a substitution its own speakers would use. A diphthong is its most open vowel with the rest as glides, unless the template has the diphthong itself. The file is text and can be edited: a line is an eSpeak NG phoneme and the phones to say it with.

    template eses
    style standard          # french: the stress digit before the vowel, as frfr writes it
    vowels i e a o u        # the template's vowels: each is the nucleus of a syllable
    glides r R l L y w      # may follow an obstruent at the start of a syllable
    schwa e                 # put before a syllabic consonant
    secondary 0             # the digit for secondary stress; Italian and Spanish have none
    @sw:h   j               # eSpeak NG's h in table sw: said as Spanish jota
    θ       T               # any phoneme whose IPA is θ

What each template's phones are was measured, not assumed: every phone was put through the module as an annotation and read back with `eciGeneratePhonemes`, and real words were read to see which phone the module uses for which sound. Two things the modules refuse were found the same way and are handled here. The Italian and Spanish modules have no secondary stress, and read an annotation containing a `2` aloud as text. The Italian module loops forever on a word with two primary stresses whose first syllable has no consonant (`[.1a.1a]`), so every second primary stress in a word starts a word of its own.

## The sound map

Since 1.2 a pack also has `sounds.map`, which `language.ini` names as `Sounds=`. It is the same kind of file with more kinds of line in it: beside the phones for each phoneme it names the sound each phone is meant to be (`t=s71`), says how each such sound differs from the module's phone (`sound s71 f2=91 f3=79 f4=88 vot=9`), gives the language's melody (`accent ...`), its tones (`tone 35 p=0:31,30:29,100:50`) and the words its questions are asked with (`whwords ...`). With such a map the front-end writes, before each word's annotation, what each phone was meant to be, in braces, and before the text the sounds and tones the text uses:

    {A v=1 f0=own shape=1 accent=24 ...}{D s71 f2=91 f3=79 f4=88 vot=9}{W .1 t=s71 a=s48^- l}`[.1tal]{P s}.

The engine takes the markup out of the text before its rules see it, so the module reads the annotations it always read, and its accent layer makes the frames the module asks for into the sounds that were meant. `docs/SOUNDS.md` in the repository says what every line and every key means.

In a language of tones the front-end asks eSpeak NG for the tones as they are after sandhi (for Mandarin, the third tone before another third tone, and the neutral tone after each of the four), which eSpeak NG works out only when it computes pitch, a step the front-end otherwise never takes.

## Commands

    OpenEvvFrontend --data <espeak-ng-data> --voice bnt/sw --map phonemes.map --text "Habari"
    OpenEvvFrontend --data <espeak-ng-data> --voice bnt/sw --stats sample.txt    # phoneme counts, JSON
    OpenEvvFrontend --data <espeak-ng-data> --dump-phonemes                      # every phoneme table, JSON
    OpenEvvFrontend --data <espeak-ng-data> --serve                              # the host's pipe protocol

`--anchors` with `--text` prints where each word came from, `--punctuation` has punctuation marks named, as spelling wants, `--spell` has the whole text spelled, every character by its name, and `--phonemes` lets the text name eSpeak NG's phonemes in `[[double brackets]]`, which is how a single sound is asked for to be measured. `src/common/frontend_proto.h` describes the pipe protocol.

Spelling is asked of eSpeak NG with the command it keeps for saying characters, the character with the number one, `18Y` before the text and `Y` after it. The engine host writes it around what SAPI asks to be spelled and around a text that is a single letter, so that a letter is always read by its name and never as a word or a sound.

## Building

`frontend\build_frontend.cmd` builds both bitnesses with MSVC and Ninja and stages them, and eSpeak NG's compiled data, in `dist\`. eSpeak NG is fetched from [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng) at the tag named in `CMakeLists.txt`, or taken from a local checkout named by `ESPEAK_NG_SOURCE_DIR`. `build_all.bat` runs it.

## Licence

This program links eSpeak NG, so it is under the GNU General Public License version 3 or later (`COPYING`), like eSpeak NG itself, and so is the eSpeak NG data installed with it. It is a separate program from the SAPI wrapper, which starts it and talks to it over pipes. The source of the eSpeak NG it is built from is the tag named in `CMakeLists.txt` of [joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng); the source of this program is this directory.
