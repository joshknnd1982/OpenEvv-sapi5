# sounds.map: what the staged engine adds (draft for docs/SOUNDS.md)

`docs/SOUNDS.md` describes the shipped product. The rebuilt template modules and the front-end of the TTS extension (Phases 3 and 4) are staged only (`%USERPROFILE%\OpenEvvBuild-ttsext\stage-dev`); nothing in `languages\` or `dist\` reads what is below yet. When the rebuilt modules replace the shipped ones (with the human's say-so, `DECISIONS.md` D34), this page is merged into `docs/SOUNDS.md`: the key table goes under "A sound", the lines after it under "sounds.map". Every key is nought, or the value given, unless a line names it, so a pack that names none of them is spoken as before.

## Keys of a sound

How the keys already documented behave now:

- `vot` and `brth` switch the voice on after a stop only where the module itself voices what follows: before a pause or a voiceless sound the burst and the breath stay voiceless, and the next consonant's noise is not faded out (defect X-1, `DESIGN.md` 4.4, fixed in Phase 3).
- In a `tone` line, `av` raises or lowers the voice's level over the tone, in dB; it was read and never applied before (defect X-2).

The keys that are new:

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

What the layer now does by itself:
- A whispered sound's voice ends where the sound ends: a sound after it with no voice of its own does not begin with the module's voice (Q28).
- A stop the layer voices is found released under its voice bar, so that the voice it asks for after the release is given (Q30).
- A phone the markup asked for that is never said is reported in the trace, as `phone-unplaced`, when its phrase is over or the text is stopped (Q14).

## Lines of the map

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
