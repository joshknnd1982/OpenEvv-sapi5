# Authenticity and native validation (Phase 7)

How a language, dialect or accent goes from `draft` towards `native-validated` (playbook 1.5), with
measured data from licensed recordings, a validator that refuses undocumented claims, and a packet a
native speaker can review. Decision D90 records why it is built this way; `PROJECT_STATE.md` has
the demonstration's outputs.

The pipeline, one command a step (Python: the harness venv, `PYTHONUTF8=1`, repository root):

| Step | Command | Writes |
|---|---|---|
| 1. Find licensed reference data | (research; `REFERENCES.md`, "Phase 7") | the source in `ipa/sources.toml` |
| 2. Measure targets from aligned recordings | `python engine/authenticity/extract_targets.py <tag> <corpus> [--write]` | `packs/<tag>/measured/<source>.json`; with `--write`, `[[override]]` blocks (`state = "proposed"`) in `pack.toml` |
| 3. Speaker normalization | inside step 2 (`engine/authenticity/normalize.py --selftest`) | the factor per speaker, in the JSON |
| 4. Check the pack's metadata and claims | `python engine/packs/validate_packs.py [tag]` (`--selftest`) | nothing; exit 1 on a rejected pack |
| 5. Hear the effect (measure it) | `python engine/packs/build_packs.py build <scratch> --proposed <tag>` and the harness | a scratch folder, never `languages/` |
| 6. Make the review packet | `python engine/review/make_packet.py <tag>` | `docs/tts-extension/review_packets/<tag>/` |
| 7. Record a reviewer's answers | `python engine/review/ingest_feedback.py <feedback.toml>` (`--selftest`) | `LANGUAGE_STATUS.md` (sign-offs), `review/signoffs.json`, the pack's status |
| 8. Apply the overrides (human's say-so, R18) | set `state = "applied"` in `pack.toml`, `build_packs.py check` shows the difference, then the shipped files are rebuilt | `languages/<tag>/sounds.map` |

## 1. Reference data

`REFERENCES.md`, "Phase 7: reference data discovery", lists every corpus and archive looked at
(Common Voice, FLEURS, PHOIBLE, Glottolog, the UCLA Phonetics Lab Archive, IDEA and others), with
licence, access, coverage and speaker metadata, usable or not, and why. A corpus is used only when
its licence is recorded and it gives each speaker's region or background. The recordings a pack's
measurements rest on are kept in the tree when their licence allows it (the human's rule: a clone
holds everything the project rests on): CMU ARCTIC awb is in `third_party/cmu_arctic/`, with its
licence in `NOTICE.md`; the measurements carry each token's recording id.

## 2. Target extraction

`extract_targets.py` reads `packs/<tag>/measure.toml`: the source, the speakers, the kind of
alignment, and the classes (an alignment label, its lexical set, the pack's IPA for it, and the
reader's phonemes it is said for). Alignments: Festvox label files (CMU ARCTIC ships them, made by
forced alignment with Festvox's EHMM) or TextGrids from the Montreal Forced Aligner (MIT; its
pretrained English models and dictionaries carry their own licences, see `REFERENCES.md`).

Measured with the harness's own analyser (`harness/analysis.py`, the one that measures the engine,
so both sides are read alike), on each recording resampled to 11025 Hz (the engine's band,
DESIGN.md 10.1):

- **vowels**: F1, F2, F3 at the middle (Burg LPC, 25 ms window), duration, F0 at the middle.
  Tokens shorter than 50 ms are left out (reduced), and so are tokens next to r, l, w or j (they pull
  the formants). Per class, tokens beyond 3 median absolute deviations in F1 or F2 are dropped as
  tracking errors and counted.
- **vowel length**: each class's median duration over its own tokens (every token not before a pause:
  the formant filter above drops short tokens and made KIT and GOOSE up to 38 per cent too long, as the
  R15 re-review found), put at the module's speaking rate by one factor per
  speaker (the log-mean of the class medians against the module phones' audible lengths, as section
  3 does for size), written as an `[override.duration]` where it differs from the pack by more than
  12 per cent (`sounds.py lasting`'s tolerance) and realised as the `dur` key. `dur` is a per cent of
  the phone's stretch, so in a word where the module's own vowel is longer (before a voiced consonant)
  the same override moves it further in milliseconds (`show_effect.py`: KIT asked -27 ms, kit -30, bid -55).
- **fricatives**: noise centroid above 1 kHz over the middle half (s z sh f th); **every label**:
  median duration; **F0** per vowel class. Reported in the JSON, not written: a pack's pitch is never
  in hertz (DESIGN.md 7, rule 4) and a fricative's noise is set by band levels, not a centroid, so
  neither has an adapter yet.
- **stops**: voice onset time is measured but written as `vot_ms_unvalidated` and never used. The
  harness's `stop_timing` was made for the engine's clean output; on awb it reads every p, t and k as
  prevoiced, even after a pause (median -24 to -28 ms over 30 to 137 tokens; English voiceless stops
  are not prevoiced), so it is wrong on natural speech. A measure validated on natural recordings is
  `OPEN_QUESTIONS.md` Q40.

Each class's target is the median of the kept tokens, normalized (section 3). An override is
written only where the target differs from what the pack says now by more than 6 per cent in F1 or
F2 (`engine/accent/sounds.py`'s own "near" threshold): measurement changes what it shows to differ,
nothing else.

### Sample-size minimums (`derived`)

| Minimum | Value | Why |
|---|---|---|
| tokens per class and speaker | 10 | a vowel's F1 or F2 varies within one speaker by 4 to 14 per cent (standard deviation; measured on CMU ARCTIC awb, ten classes, 71 to 836 tokens each); the standard error of a median is about 1.25 SD / sqrt(n), so 10 tokens put it at 1.6 to 5.5 per cent, under the 6 per cent an override needs to be written |
| speakers per variety | 5 | speakers of one variety differ in their normalized vowels by several per cent; below five, a target describes the speakers recorded, not the variety |

Below either minimum the result is still written, flagged: `below_minimum = true` on the override,
"BELOW MINIMUM" in the report, and the note says so. A flagged override can be applied, but the
pack cannot claim the variety's values from it.

## 3. Speaker normalization

**The voice, not the pack, carries speaker scaling.** This engine's voice scales the vocal tract
with one multiplier on F1 to F5 (head size; gender adds range-dependent factors; DESIGN.md 7), and a
pack's sound is a ratio against the module's own phone, so it scales with any voice. A measured
target must therefore be the variety's vowel *pattern*, at the size of the module's voice, with the
recorded speaker's size taken out.

The method is Nearey's log-mean in its shared form (one mean over F1, F2 and F3: "Nearey2",
`normSharedLogmean` in phonR): G = the mean of ln F over the speaker's class medians; the target is
F x exp(G(module) - G(speaker)), where G(module) is taken over the module phones that say the same
classes (`engine/accent/chassis/<template>.json`). It removes exactly one multiplier, which is what
the engine's voice adds back. Adank, Smits and van Hout (2004) found per-formant procedures better at
removing anatomical differences between human speakers; here the shared form is chosen because the
engine's own scaling is shared, so a per-formant one would bake one speaker's formant ratios into
the pack. Classes weigh alike (medians, not tokens). Bias, stated: a dialect shifts some classes, and
G moves with them by a few per cent at most over ten classes; the factor is in the JSON to be looked at.

Speaking rate is the voice's too, so durations get the same treatment: one factor per speaker (awb
x1.5576; see the JSON) puts the class medians at the module's rate, and only the *pattern* of lengths
(FLEECE long, KIT short) reaches the pack.

`normalize.py --selftest`: a uniformly larger speaker comes back exactly; a fronted vowel survives;
the spread between two speakers of different size falls to nothing. And the check DESIGN.md 7 asked
for: the same override rendered on presets 1 and 2 must give the same ratio to the module's phone in
the frames (shown in `PROJECT_STATE.md`).

## 4. Authenticity metadata (validator)

Every pack of kind `dialect` or `accent` records in `[meta]`: `variety`, `region`, `speaker_group`,
`sources` (at least one registered, opened source of `ipa/sources.toml`, and nothing else but the
reader the pack was generated from, "eSpeak NG voice <voice>"), `recordings` (the recording
sets measured, `[]` if none), `date` (last checked), `status = { level, validated_by, date }` and
`licence`. `validate_packs.py` rejects a pack that lacks any of them (rules M1 to M6 in its header),
and level 5 without a named reviewer and a date. Its self-test plants each fault in a copy of a
complete pack and must see it rejected.

## 5. Anti-caricature

A dialect or accent is described, never performed. Rules (A1 to A4 in `validate_packs.py`; the rest
are the reviewer's and the author's duty):

- **Every dialect-specific value cites a descriptive source or measured data.** An override of a
  dialect or accent pack is `measured`, `literature`, `derived` or `approximate`, each with `ref`;
  never `estimated` or `created`.
- **No feature is pushed past its evidence.** A `measured` value must equal its evidence file's target
  within 2 per cent; a ratio beyond 50 to 200 per cent of the module's phone is refused outright.
- **Not checked by the validator, stated:** the `[sounds]` lines of a legacy pack carry no provenance
  of their own; they are the generator's (`engine/make_espeak_packs.py`), made from the reader named
  in `sources`. A dialect feature added or changed by hand must be an `[[override]]`, which the rules
  check; a hand edit of a `[sounds]` line in a dialect pack is against this rule even though the
  validator cannot see it.
- **Describe the speakers, not a stereotype.** Sources are descriptive studies and recordings of real
  speakers with known background; no stage dialect, no "as heard in films", no eye-dialect spelling.
- **Optional, variable or stigmatised features** (a glottal stop for t, a dropped h, a vocalised l) go
  in only with a source that says who uses them and how often, and as the frequency the source gives,
  never as a constant.
- **Native review is the last word.** A reviewer's "this sounds like a parody" is recorded and the
  feature is taken back to its evidence.

## 6. Review packets

`make_packet.py <tag>`: a self-contained folder: `index.html` (audio players and spectrograms
embedded, spelling, IPA and question beside each item; works offline, and every picture has a
description giving its numbers), `audio/`, `spectrograms/`, `items.json`, `CHECKLIST.md` (plain
language), `feedback.toml` (the form), `README.md`. Items: words, sentences and minimal pairs (from
`packs/<tag>/review.toml`, else the language's ASR sentences), the A/B comparison of each override
(the pack as it is and with the measured override, blind), and
every sound the language has that the module lacks, with the master table's flags (created,
approximate, estimated values). **The A/B items are blind**: which of A and B carries the override is
fixed by a hash of the item, so it changes from word to word; neither the page nor `items.json` says
which (an A/B item's vowels are listed there without their sound ids), and pairs are shown without
what they are meant to test. The answer key is kept outside the packet,
`docs/tts-extension/review/keys/<tag>.json`, so sending the whole folder cannot unblind it; the ingest
reads it.

## 7. Ingesting feedback

`ingest_feedback.py <form>` records a review only with the reviewer's name (or a stable pseudonym),
a date, the native variety, `consent_to_name = "yes"` and an overall answer; otherwise it refuses and
writes nothing. It keeps the form, adds a record to `review/signoffs.json`, rewrites the sign-off
section of `LANGUAGE_STATUS.md`, and sets the pack's status: level 5 only if the answer is "yes" and
the language already stands at level 4 (a level needs every level below it). Only level 5 is called
authentic. `validated_by` in a pack's status names the reviewer who said "yes" (signed off); the level
says whether that made it native-validated.

## 8. Finding reviewers

`FINDING_NATIVE_REVIEWERS.md`. Claude contacts no one.
