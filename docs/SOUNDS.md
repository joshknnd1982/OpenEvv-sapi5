# The sounds, the melody and the tones of a language

Since 1.2.0 a language read by eSpeak NG is spoken with its own sounds, not with the nearest sounds of German, Spanish, Italian, French or English. This page says how, what the numbers are and where they come from, and how to change them with a text editor.

## What happens to a word

1. eSpeak NG reads the text: spelling rules, dictionary, numbers, letter names, stress, and in a language of tones the tone of every syllable with the changes tones make to each other.
2. `OpenEvvFrontend.exe` writes every word as a pronunciation in the phones of the module that is to speak it, using the pack's `sounds.map`. Before each word it writes what the phones were *meant* to be: which sound of the language each of them stands for, which tone the syllable has, where the stress is. Before the text it writes what those sounds and tones are.
3. The module makes of the pronunciation what it makes of any pronunciation: a stream of frames, 200 a second, each of which tells the formant synthesiser what to do for 5 ms.
4. The *accent layer* inside the engine (`openevv\src\accent\evv_accent.c`) knows which frames belong to which phone and what that phone was meant to be, and changes the frames accordingly before the synthesiser gets them: formants are moved, the voice begins earlier or later after a stop, breath or creak is added, a tap is cut into a sound, a syllable is given its tone. Where a language has a sound no module has a phone for at all, an h in Italian, a glottal stop nearly anywhere, the layer makes it out of the vowel beside it.

Nothing of this touches openevv's own ten languages. Their text has no markup in it, without markup the layer does nothing, and `test/matrix.sh` (979 recordings) holds them to the sample.

## The modules that speak

IBM wrote each module for one language, and each has that language's habits: the German one takes the voice out of a b, d or g at the end of a word, the Spanish ones turn b, d and g between vowels into fricatives, British English leaves out an r after a vowel and American English turns a t between vowels into a flap. A language that is not German must not have its final consonants devoiced.

So the languages read by eSpeak NG are spoken by seven modules made from IBM's seven with those habits taken out. They say the phones they are given. Each is its module with a handful of phonological rules replaced by rules that do nothing (`openevv\accents\<tag>\rules`), made by `openevv\tools\module\clone.py` when the modules are built:

| Module | Made from | What was taken out |
|---|---|---|
| `dedx` | German | devoicing at the end of a syllable, r said as a vowel after a vowel |
| `itix` | Italian | n said as ng before k and g, the choice between open and close e and o |
| `esex` | Castilian Spanish | b, d, g as fricatives, double consonants made single, vowels run together, n taking the place of the next consonant |
| `esux` | Latin American Spanish | the same |
| `engx` | British English | r left out and put in, a schwa before r |
| `enux` | US English | the flap |
| `frfx` | French | nothing yet: the French module changes little |

Their packs are in `languages\` like any other and say `Hidden=1` in `language.ini`: they lend their modules and are not languages, so they have no voices in the voice list. They keep the language number of the module they were made from.

## sounds.map

A text file in the pack's folder, in UTF-8. A line is a key and what belongs to it; `#` at the start of a word begins a comment. The file is read each time a voice starts, so a change is heard the next time the voice speaks.

    template dedx
    style standard
    vowels i I e E a A u U o O y Y oe OE @ aj aw oj a~ E~ o~ oe~ E: R
    glides r l j w
    schwa @
    secondary 2

These say which module speaks and how its pronunciations are written, and were in `phonemes.map` already (see `frontend\README.md`).

### A phoneme

    @hi:t.           t=s71                   # ʈ
    @hi:h            <h=s19                  # h
    @cmn:iE          j=s54 E=s50             # iɛ
    ɕ                S=s39

An eSpeak NG phoneme, by its table and name or by its IPA, and the phones that say it. `=s71` after a phone names the sound the phone is meant to be, a `sound` line of the same file. A phone with `<` before it is not in the module at all and is made by the engine out of the vowel beside it.

### A sound

    sound s71 f2=91 f3=79 f4=88 a4=52 a5=42 vot=9     # ʈ

How the sound differs from the module's phone. Every number is a difference or a time, never a formant in hertz, because a module speaks with a voice, a head size and a sex, that has already scaled every formant by the time the layer sees it: only a ratio means the same in every voice.

| Key | What it says | Unit |
|---|---|---|
| `f1` `f2` `f3` `f4` | the formants, against the phone's own | per cent |
| `g1` `g2` `g3` `g4` | where the formants have got to by the end of the sound; with `glide=1` they move there through the sound, as a diphthong's do | per cent |
| `b1` `b2` `b3` `b4` | the formants' bandwidths | per cent |
| `dur` | how long a vowel's stretch lasts | per cent |
| `hold` | how long a consonant's stretch lasts | per cent |
| `reach` | how long the formants take to get where they are going | ms |
| `vot` | after a stop: the time from the release to the voice | ms |
| `asp` | the breath in that time | dB |
| `lead` | a voiced stop after a silence: how long before the release the voice begins | ms |
| `bar` | how loud the voice is behind a closure | dB |
| `voi` | 1: voiced throughout; 0: voiceless throughout | |
| `brth` | breathy voice after the release, for so long | ms |
| `f0` | the pitch where the vowel begins after the sound | tenths of a semitone |
| `ej` | an ejective: silence after the burst | ms |
| `impl` | an implosive: the voice swells towards the release | |
| `burst` | the burst, louder or softer | dB |
| `noburst` | the stop is not released | |
| `pre` | breath before the closure (preaspiration) | ms |
| `nas` | the nose open | per cent |
| `fric` | friction of the sound's own | dB |
| `a2` `a3` `a4` `a5` `a6` `ab` | the noise: how loud at each formant, and unfiltered | dB |
| `av` `ah` `af` | voice, breath and friction, louder or softer | dB |
| `tap` | the tongue shuts the mouth so many times: 1 a tap, 2 or 3 a trill | |
| `tapms` | for how long each time | ms |
| `oq` `tl` | the open quotient and the tilt of the voice | as the synthesiser has them |
| `creak` | creaky voice | per cent |
| `whisper` | said without voice, with breath at this level | dB |
| `ms` `hush` | for a sound the engine makes: how long it lasts, and that it is silence (a glottal stop) | ms |

Since 1.3.0, `vot` and `brth` switch the voice on after a stop only where the module itself voices what follows: before a pause or a voiceless sound the burst and the breath stay voiceless, and the next consonant's noise is not faded out (defect X-1 of the TTS extension, `docs/tts-extension/DESIGN.md` 4.4). Every key is nought, or the value given, unless a line names it, so a pack that names none of the keys below is spoken as before.

The keys added in 1.3.0 for the sounds of the IPA chart (the Q and D numbers are those of `docs/tts-extension/OPEN_QUESTIONS.md` and `DECISIONS.md`):

| Key | What it says | Unit |
|---|---|---|
| `trate` `tdepth` | a trill at its own rate, whatever the sound's length; how far the level drops at each closure | closures a second; dB |
| `breathy` | breathy voice through the whole sound, added to the voice's own setting | per cent |
| `burstms` | how long the burst lasts before an ejective's silence | ms |
| `rel2` `rel2ms` `rel2af` `rel2g` | a second, weaker release so long after the first, for so long (a click's back closure); its noise; louder by so much than the synthesiser's parallel gains reach | ms; ms; dB; dB |
| `bgain` | the burst louder by so many dB than the parallel gains reach | dB |
| `ant` | the sound before this one ends at this one's formants over so many ms: its place shows on the way in | ms |
| `l1` to `l4`, `lk` | a place's formant (its locus) in per mille of the voice's own fifth formant, and how much of the vowel's own formant the place keeps (a locus equation's slope) | per mille; per cent |
| `vfrom` `vto` | the part of the sound, in per cent of it, that `voi`, `whisper` and `creak` are said over (extIPA's partial voicing) | per cent |
| `vmark` | the voice `voi` gives is a mark's: it is heard over the whisper of a letter that has one, and the whisper keeps the rest of the sound outside `vfrom`, `vto` (Q33). Without it a whisper takes out any voice, as ɦ's breathy voice (`voi` and `whisper` together) needs | 1 |
| `pst` | the sound at a pitch of its own, so far from the voice's line (extIPA's ingressive airflow) | tenths of a semitone |
| `frel` `frelaf` `frelav` | a stop released into friction for so long (extIPA's fricated releases), on the noise keys `a2` to `ab`; its level; the voice under it, louder or softer | ms; dB; dB |
| `frelf2` `frelf3` | the friction's own second and third formants, the fricative it names | per mille of the voice's fifth formant |
| `lmur` | the sound's formant ratios are its nasal murmur, said over its own stretch only | 1 |
| `fgain` | friction louder by so many dB than the parallel gains reach, over a voice (velopharyngeal friction; with `rfric`, a raised approximant's) | dB |
| `rfric` | friction at this level over the voice of a sound with none of its own (an approximant raised to a fricative, ̝ on ɹ or l, Q23), on the sound's own third to fifth formants; never on a stop | dB |
| `hit` `hitms` `hitaf` `hitg` | a strike (extIPA's percussives): so many ms after a stop's closure begins, or after any other sound's start, a noise this long on the noise keys, at this level, louder by so much than the parallel gains reach | ms; ms; dB; dB |
| `di` | every second period of the voice later and weaker (the synthesiser's diplophonia): ventricular voice, harshness | per cent, 0 to 95 |
| `jit` | each frame's pitch moved at random by up to so much, so that each period differs from the last (a harsh, oesophageal or tracheo-oesophageal voice's jitter, Q36); the same every time the same is said. About 2.5 times the jitter measured is asked for (calibrated on dedx, D87) | tenths of a per cent |
| `mono` | the pitch drawn so far towards the voice's middle: 100 a monotone (an electrolarynx) | per cent |
| `mute` | the sound not heard: 1 no voice, breath or friction (extIPA's silent articulation); 2 its friction kept (extraneous noise) | |

What the layer does by itself since 1.3.0:
- A whispered sound's voice ends where the sound ends: a sound after it with no voice of its own does not begin with the module's voice (Q28).
- A stop the layer voices is found released under its voice bar, so that the voice it asks for after the release is given (Q30).
- A phone the markup asked for that is never said is reported in the trace, as `phone-unplaced`, when its phrase is over or the text is stopped (Q14).

### The melody and the rhythm

    accent f0=own shape=1 accent=24 accent2=10 unstressed=-2 decl=8 declmax=30 fs=-18 fw=-12 fc=14 fe=-12 fq=38 qreg=8 span=2 stressed=88 weak=112

With `f0=own` the pitch is not the module's: the layer makes it, from the stress of each syllable or from its tone.

| Key | What it says | Unit |
|---|---|---|
| `shape` | 0: the stressed syllable is high and the pitch falls out of it. 1: it is low and the rise comes after it. 2: the pitch rises through it to a late peak | |
| `accent` `accent2` `unstressed` | how far from the middle of the voice a syllable with main stress, with secondary stress and with none is | tenths of a semitone |
| `range` | how far the bottom of the voice is from the top (Chao's 1 to 5), at the voice's usual pitch fluctuation | tenths of a semitone |
| `level` | where a syllable with no tone sits | tenths of a Chao level |
| `decl` `declmax` | how fast the pitch sinks through a phrase, and how far | tenths of a semitone a second; tenths of a semitone |
| `fs` `fq` `fw` `fc` `fe` | the end of a statement, of a question that wants yes or no, of a question asked with a question word, of a phrase before a comma, of an exclamation | tenths of a semitone |
| `span` | over how many syllables the end is come to | |
| `qreg` | the whole of a question raised | tenths of a semitone |
| `qfall` | a question that rises and falls: how far its last syllable comes down again | tenths of a semitone |
| `lag` `lead` | how fast the voice follows where it is told to go, and how far ahead it is told | radians a second; ms |
| `coda` | how long what follows the vowel in its syllable is taken to last, when a tone is laid over both | ms |
| `stressed` `weak` `last` `vowel` `stretch` | how long stressed vowels, unstressed vowels, the last syllable of a phrase, all vowels and everything last | per cent |
| `stop` | the number the module's own table gives the manner of a stop: 1 in the module made from German, 0 in the others | |
| `frange` `fshift` | with the module's own pitch (`f0` left out): its movement made wider or narrower, and the whole of it moved | per cent; tenths of a semitone |

The voice's own pitch and pitch fluctuation, which a screen reader sets, are the middle and the scale of all of it.

### Questions

    whwords first qui que quoi où quand comment pourquoi combien

The words a question is asked with. A clause that ends in a question mark and has one of them ends as `fw` says, and any other question as `fq` says. `first` counts the word among the first three of its clause, `any` wherever it stands. A word with `~` before it counts only when it does not begin the clause.

### Tones

    words apart
    onset 2
    tone 35 p=0:31,30:29,100:50 dur=106
    tone 214 p=0:23,45:10,100:38 dur=125 creak=40 cfrom=30 cto=65
    weaktones 11 22 33 44
    tonename 2 35

A tone is named as eSpeak NG names it (`tonename` gives another name where that is wanted) and is a line of points: at so many per cent of the syllable's rhyme the voice is to be at such a level, in tenths of Chao's five levels, 10 the bottom of the voice and 50 the top. The voice does not jump from point to point; it follows them as a larynx does, a little late and without corners. `dur` lengthens the syllable, `creak`, `cfrom` and `cto` make part of it creaky, `brth` breathy, `stop` ends it in a glottal closure of so many milliseconds, `weak` lets a tone give way towards the middle of the voice. `av` raises or lowers the voice's level over the tone, in dB (since 1.3.0: before, it was read and never applied, defect X-2).

`words apart` makes every syllable a word of its own, which a language of one-syllable words wants; `onset` says how many phones may begin a syllable there, and `cluster` names pairs that may where `onset` is 1. A syllable whose tone is listed under `weaktones` is light, and every other syllable has the weight of a stressed one.

Tone sandhi is eSpeak NG's: the third tone of Mandarin arrives as a second tone before another third tone and as a low falling tone before any other, and the neutral tone arrives already as one of four, by the tone before it.

### What the module says instead

    says C t S

The module says the phone `C` as `t` and then `S`: every module takes an affricate apart. The layer has to be told, or it would look for a `C` that never comes.

### The lines for IPA (a map of version 2)

Since 1.3.0 the front-end reads IPA marks, tone letters and extIPA's braces and composes them on the sounds they belong to; the IPA master table (`ipa/table/`) is realised into these lines by `engine/ipa` (`ipa/realized/dedx.map`). No language shipped in 1.3.0 uses them yet: text is still read by eSpeak NG into each language's own sounds, and the realised map is read by the tools, `engine/ipa/say_ipa.py` (any IPA, said and measured) and the proofs of `ipa/proofs/`. Speaking IPA through SAPI is a later addition.

| Line | What it says |
|---|---|
| `version 2` | the map is written for the front-end that composes marks (C4) |
| `letter <ipa> <c or v> <features>` | a letter of the chart and its features: what a letter with no line of its own is said as, by the nearest one (the fallback). A letter may be spelt with two characters (a letter and a mark, or two letters: ǃ¡), three or four (a letter and its own marks: h̪͆, tʰ̪͆), or as a tied letter (ↀ͡r). Its features include `release`, `place_mark`, `aspiration`, `fricated_release` and `tongue_part` |
| `weights <feature>=<n> ...` | how far apart two letters are, feature by feature, for that fallback |
| `mod <mark> <c or v> <keys>` | a mark on a consonant or a vowel: keys set (`voi=1`), added (`vot+64`) or multiplied (`hold*131`, per cent), composed on the letter's own line; a line holds 12 keys at most |
| `premod <mark> <c or v> <keys>` | a mark written before its letter (extIPA's ʰp, ˬz) |
| `after <mark> <first marks>` | the second character of a mark of two characters (◌̥᪽'s ᪽), said only after the first ones |
| `reiterate <c or v> <ipa>` | what is said at extIPA's `\` (reiteration) after a consonant or a vowel |
| `notation extipa`, `extipa <line>` | the map reads extIPA's own meaning of a character the IPA reads otherwise; an `extipa` line counts only under it |
| `label <label> <d, m, r or -> <marks...>` | a VoQS or extIPA label in braces (`{V! ... V!}`): each degree or step is a mark of its own (a private-use character) with its own `mod` lines, composed on every letter of its class in the stretch (D83) |
| `pause <spelling> <ms>` | extIPA's pauses: `(.)`, `(..)`, `(...)` and timed ones |
| `tonemark` `register` `slope` | tone letters and diacritics, downstep and upstep, global rise and fall typed in IPA |
| `syllabic <sound>` | the schwa that carries a consonant marked syllabic |

Two more things the front-end does with these lines:
- A tied pair the template has no phone for (t͡θ, d͡ð) is a sound of its own: the stop released into the fricative, its friction as long as the template's own affricates' (D84, D87).
- The link `‿`, given a `mod` line, is a mark of the consonant before it: a linking consonant is said shorter (Q19).

## Where the numbers come from

`engine\accent\sounds.py` writes the sounds, `engine\accent\prosody.py` the melody and the tones, `engine\accent\questions.py` the question words, and `engine\accent\mapwriter.py` puts them into a pack's `sounds.map`; `engine\make_espeak_packs.py` runs them for every language.

- **Each module was measured** (`engine\accent\chassis.py`, results in `engine\accent\chassis\<module>.json`): every phone was put through the module and its formants, its length, its voice onset time and its noise were read off the frames the module asked the synthesiser for.
- **Vowels.** The formants of each vowel of the IPA chart for a man's voice (`VOWEL` in `sounds.py`: the middle of what is reported across languages), or the language's own where its profile has a published table, are scaled to the size of the module's voice and held against the module's nearest vowel. The ratio is the definition. A vowel the module has is left as the module says it unless the language's own measurements are more than 8 per cent away.
- **Consonants.** The place of a consonant shows in the formants of the vowels beside it, which start from the consonant's *locus*. The ratio between the locus of the sound wanted and the locus of the module's phone is the definition: a retroflex is a t with the third formant at 79 per cent. Voice onset times are the language's own where its profile has them (Lisker and Abramson 1964 for many), and otherwise those of the kind of stop (Cho and Ladefoged 1999).
- **Length.** A language that tells long vowels from short has them as 1.8 to 1; one that does not has all its vowels the same length, whatever the module's phone would have been in its own language.
- **Melody.** Each language's profile (`engine\profiles\<tag>.json`) says what the literature says of its stress, rhythm, intonation and tone, with sources. `prosody.py` reads the kind of pitch accent and the kind of question out of it, and a table by hand puts right what the words of a profile mislead.
- **Tones.** The shapes in `prosody.py` are the citation shapes of the literature with their timing.

## Measuring

Nothing here was tuned by ear. What is heard is measured, in the sound itself and the same way whoever made it:

    python engine\accent\proof_hindi.py languages\hi
    python engine\accent\proof_mandarin.py languages\cmn
    python engine\accent\verify_pack.py languages\hi report.md

`verify_pack.py` says every phoneme of a language that has a sound of its own twice, through the pack and through eSpeak NG's own synthesiser, and sets the formants, the voice onset time and the noise of both beside what the sound was meant to be. `engine\check_espeak_packs.py` holds every pack to its module: every word taken as a pronunciation, and every phone the module says found in what the map meant.

The engine writes down what it did if it is asked: with `EVV_ACCENT_TRACE=file` in the environment, every stretch of speech is a line of `file`: the phone, when it was asked for and when it sounded, what it was meant to be, its sound, its tone and its stress. With `EVV_KLATT_TAP=file` every frame is a line.

## What is not there yet

- The languages with a word accent of pitch, Swedish, Norwegian, Serbian, Croatian, Bosnian, Slovenian, Lithuanian and Latvian, are read by eSpeak NG without it, so they are spoken with stress and the melody of the sentence only.
- Thai is read by eSpeak NG without tones, and its Burmese and Thai voices are beginnings.
- British English's t before r is still said as ch by the module made from it.
- A language's profile is a summary of what was published, and its numbers are marked with how sure they are. Where nothing was published the chart's values stand.
