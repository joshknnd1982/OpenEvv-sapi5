# Phase 5: independent audit of the master IPA table

**Audited:** branch `tts-ext/phase-4` at commit `1aa892a` (Phase 4 complete, D87), on the final stage `%USERPROFILE%\OpenEvvBuild-ttsext\stage-dev` (all seven templates `build4x`, front-end `p28`). **Auditor:** Claude Fable 5.1, 2026-10-10, a session that did not build any of it. **Scope:** the playbook's Phase 5 steps 1 to 8. This file is findings only; the fixes are a second pass (section 10, written after the findings).

Everything here was re-derived or re-run by the auditor: the chart was re-read from the IPA's own images, the sources were fetched again, the engine was made to say every entry again, and the harness was given wrong sounds on purpose. The scripts and their raw outputs are in `docs/tts-extension/audit5/`.

## 0. Summary

| Severity | Count | What |
|---|---|---|
| high | 3 | H1 to H3: the harness let a letter said with the wrong voicing, and a vowel made nearly silent, pass as itself (section 7); all three fixed with new checks. Nothing missing, silent or unlabelled (sections 6, 8) |
| medium | 4 | M1: z, ʝ, ɣ carried none of the noise shaping their voiceless partners got (fixed); M2: ɞ's estimated F3 broke the rounding rule (fixed); M3: a harness reading of the ejective on k and c before [a] (Q39); M4: a breath residue after a suppressed burst on k (labelled approximate, Q39) |
| low | 11 | L1 to L11: provenance and documentation points (three fixed), notes for the expert review, limits of marks on short or close bases, two small debts of the tools |

Counts at the end of the audit, before fixes: 175 of 175 checklist symbols mapped/composed/created with a passing, rendered, measured proof (1,617 rendered cases), 0 MISSING, 0 BLOCKED; the auditor's own reading of the 2026 chart gives 175 symbols, the same 175; 392 table entries re-rendered by the auditor (section 4); literature spot-check: 47 entries, 171 values, 0 mismatches (section 2).

## 1. Consistency (scripted: `audit5/audit_consistency.py`, output `audit5/consistency.txt`)

**Vowels (28).** Specification and the proofs' measured middles (median over four contexts) were checked against the chart's geometry.

- Height against F1: in every column of one backness and rounding, F1 rises with openness, in the specification and as measured. No violation.
- Backness against F2: in every row of one height and rounding, F2 falls from front to back, specified and measured. No violation.
- Rounding lowers F2: in all 12 rounded/unrounded pairs, specified and measured (from 64 Hz, ɑ/ɒ, to 932 Hz, ɨ/ʉ).
- Rounding lowers F3: in 9 of 12 pairs. The three exceptions: o/ɤ (+86 Hz), ɒ/ɑ (+25 Hz), ɞ/ɜ (+79 Hz). The first two are Jassem's own cardinal measurements (one speaker, `literature`, re-read by the auditor, section 2): the table reports its source faithfully, and a 25 to 86 Hz F3 difference is inside Jassem's standard deviations (48 to 174 Hz). The third is `estimated` (ɞ's F3 is the midpoint of œ and ɔ, 2563 Hz) and lands above the unrounded ɜ's literature F3 (2484): **finding M2**.
- Spacing: F1 < F2 < F3 everywhere; the smallest F2-F1 gap is 251 Hz (ɒ), the smallest F3-F2 gap is 578 Hz (æ). The measured middles are within 8 per cent of the specification for all 84 vowel formants (the largest: ɶ F1 629 against 676, 7.0 per cent).

**Consonants (71 Tier A letters).**

- Voiced/voiceless pairs (18 pairs): the place values (loci, formants, noise peak) agree within 10 per cent wherever both members have them. Three voiceless members carry a locus their partner lacks: s and ʃ an F3 locus and ɬ an F2 and F3 locus, all from `chong2022`, which measured only the voiceless sounds; z, ʒ and ɮ have no F3 locus target, so the template's `l3` place cue at the vowel's edge is given for s, ʃ, ɬ and not for their partners (**L10**, section 9: not changed in this phase, since giving the voiced members the same loci by the voicing rule would re-make the map and the whole sweep again; Q39 (3) carries it); the voiced member is shorter wherever both have a duration (z 118 against s 178; v 80 against f 166; ʒ 123 against ʃ 178; ɣ 85 against x 125; ʝ 88 against ç 121), except h/ɦ (102.5 each) and ħ/ʕ (105 each), where the one source pooled them (`djeradi1991`, `chowbabel2024`): stated in the notes, not a defect. **But** three voiceless fricatives carry a `noise.peak_hz` target that moved their realisation (s: `a4=50 a5=30 f3=111 f4=135` for 4591 Hz; ç: four noise keys for 4000 Hz; x: four noise keys for 2200 Hz) while their voiced partners z, ʝ, ɣ have no noise target and are the module's own phones with their locus keys only. ʒ, ʐ, ʑ and ɮ were given their partners' peaks ("voicing does not move the place resonance", the table's own rule, `jongman2000`), so the table is inconsistent with itself: measured, s's noise centre above 1 kHz is 4528 Hz and z's 3505; ç's 3790 and ʝ's 2875; x's 2595 and ɣ's 3135 (ɣ's above x's). **Finding M1.**
- Place ordering (specified F2 loci): stops p 843 < t 1628 < c 1828, ʈ 1482 (lower than t, the retroflex's retracted locus), k 1026, q 586 (uvular below velar); voiced b 837 < d 1671 < ɟ 1898, ɖ 1434, ɡ 984, ɢ 586. Fricative noise peaks: s 4591 > ʃ 3820 > ɕ 3392 > ʂ 2812 > ɬ 2655 > x 2200 > ɧ 2000 > χ 1300 = ʁ 1300; ç 4000. All in the articulatory order one expects (the palatal ç above the postalveolar, the uvulars lowest). Measured peaks follow the specified ones within 2 to 7 per cent.
- Duplicates: no two letters are realised with the same carrier and keys; no two marks share a transform except ̥ and ̊, which the chart prints as one thing (`equivalent_to`). No letter is an unmoved module phone at a feature distance (the sweep's A0, re-checked).
- Nasals: the murmur's energy between 0.8 and 2.5 kHz lies 6.6 to 17.5 dB under the band below 0.8 kHz in all seven (`band_db`): a nasal signature. Rhotics and retroflexes: measured F3 1751 (ɹ), 1858 (ɻ), 1772 (ɽ), 2070 (ʀ, a trill), against 2300 to 2500 for the plain alveolars: lowered, as the feature asks. Laterals: l, ɭ, ʎ, ʟ have formant targets only; nothing in their specification or tests names a lateral-specific cue (an antiresonance, the F3/F4 gap); whether that lets a non-lateral pass as l is tested in section 7.
- Marks (37 Tier A transforms): every operation's direction agrees with the mark's meaning (more rounded lowers F2 and F3; advanced raises F2; raised lowers F1 and adds friction on an approximant; ATR lowers F1, RTR raises it; labialised, velarised, pharyngealised lower the F2 locus; palatalised raises it; long scales duration by 2.3 (vowel) or 2.0 (consonant), half-long 1.5/1.4, extra-short 0.55/0.6; aspirated adds 63.5 ms of VOT; voiceless sets the voice off and adds breath; voiced sets it on and the VOT to 0). Tones: the ten level and contour letters and their ten diacritic twins carry the same Chao levels ([5], [4], [3], [2], [1], [1,5], [5,1], [3,5], [1,3], [3,4,2]).

## 2. Literature spot-check (sources fetched by the auditor)

Method: for each source, the PDF or page was fetched again (the fetch tool, `curl`), its text extracted with `pdftotext` (MSYS2 poppler) or its scanned pages viewed as images (`pypdf` image extraction, the pages read), and the table's value compared with the printed one. 47 entries across all seven sections, 171 values. Every value below was found as the table states it; "n" is the number of table values confirmed from that source.

| Section | Entries | Source re-read | What was compared | n | Result |
|---|---|---|---|---|---|
| vowels | i y ɨ ʉ ɯ u e ø ɤ o ɛ œ ʌ ɔ a ɶ ɑ ɒ | Jassem & Krzyśko 1992, Table 3 pp. 349-351 (scanned; read from the page images) | F1 F2 F3 of each cardinal vowel, the SDs quoted in the notes (28.8, 115.3, 108.7 for [i]), speaker WJ, f0 97-105 Hz, 10 tokens, 200-300 ms | 54 | all 54 as printed |
| vowels | ɪ ʏ ʊ | Pätzold & Simpson 1997, Table 2b (male medians) | 343/1803/2483 n 1009; 374/1431/2284 n 102; 382/1058/2363 n 435 (the row labels are shifted in the extraction, as the notes say; the n columns fix them) | 9 | as printed |
| vowels | ɜ | Williams 2013, Table 4.3 (SSBE men) | NURSE 564/1386/2484, duration 154 ms | 4 | as printed |
| vowels | æ | Fischer-Jørgensen 1972, p. 52 table (page image) | long isolated /a:/ 630/1710/2490, 7 male speakers | 3 | as printed |
| vowels | ɐ | Alispahic et al. 2017, Table 1 | AusE /ɐ/ 743/1386/2581, reproduced from Elvin et al. 2016 (the note says "secondary": correct) | 3 | as printed |
| pulmonic | m ɱ n ɳ ɲ ŋ | Maselli et al. 2026, Appendix 2 "Average values (consonants)" | F1 to F4 and durations of all six nasals (e.g. ɳ 394/1213/2314/3356, 0.05 s), four male speakers | 30 | as printed |
| pulmonic | r ɾ l ɭ | Punnoose 2010, Tables 21, 22, 23 | tap 31.21 ms (SD 10.26); l 50.39 (10.19); ɭ 40.83 (12.29); midpoints r 493/1235/2294, ɾ 380/1750/2492, l 369/1698/2556, ɭ 436/1309/2356 | 15 | as printed |
| pulmonic | w ɹ j | Espy-Wilson 1992, Table VI (prevocalic) | w 381/848/2320/3525; r 419/1285/1779/3350; j 317/2142/2827/3661, averaged over all speakers | 12 | as printed |
| pulmonic | p ʈ c k ɡ | Stoakes 2013, Tables 6.13 and 6.15 | fortis VOT 20/17/34/23 ms (and t 15); loci p HK 806.5 OK 880.2 (slopes 0.74/0.76); c OK 1828, 0.34 (HK's 727 not significant); k HK 1026, 0.86 (OK's -1668 invalid); ɡ HK 984.4, 0.88; b HK 656.1, OK 1018 | 10 | as printed |
| pulmonic | f v θ ð s z ʃ ʒ | Jongman et al. 2000 | the KU ScholarWorks copy now answers 403 and the publisher's is paywalled: **not re-opened**; the values stand on Phase 4's reading | 0 | not checked |
| pulmonic | s ɬ (ʃ) | Chong & Kasstan 2022 (JIPA, open access) | /s/ peak 4591 Hz; /ɬ/ 2655 Hz; four speakers (one woman, three men); Table 6 (loci) is an image on the publisher's page: F2/F3 loci not checked | 2 | as printed |
| pulmonic | ç ʝ x ɣ | Nirgianaki et al., Greek fricatives | palatal 121.02 / 87.92 ms, velar 125.21 / 85.48 ms, two women and two men | 4 | as printed |
| pulmonic | ɻ | Narayanan et al. 1999, Table III | observed 450/1500/1850/3025 | 4 | as printed |
| pulmonic | ɕ ʂ | Chiu 2009, Table 1 (Polish, max-amplitude frequency) | 3391.62, 2811.74 Hz; one male speaker, 15 tokens (the IPA glyphs are garbled in the text, as the note says; the rows are in the paper's own order s, retroflex, alveolo-palatal) | 2 | as printed |
| pulmonic | ʙ | Olson 2023, Table 4 | /bʙ/ 12 tokens, first period 52.4 ms (SD 4.4), 19.2 Hz (SD 1.6) | 1 | as printed |
| pulmonic | ʀ | Kochetov & Howson 2015, Table 1 | uvular trill, initial 23.2 Hz, final 23.5, 17 cycles | 1 | as printed |
| pulmonic | r | Żygis 2004, p. 146 | closed phase of the 2nd and 3rd cycles about 20 ms | 1 | as printed |
| pulmonic | r | Cámara & Alcalá-Durand 2026 (arXiv) | median 2 closures (mean 2.03, SD 0.83), 356 speakers, median token 80 ms, word-initial 91 ms | 2 | as printed |
| pulmonic | ħ ʕ | Karaoui et al. 2021 (text, Table 3 is an image) | /a/ plain 519.60/1573.437/2485.809; next to ħ: F1 +223.76, F2 +24.62 (1598.06), F3 -11.65 (2474.16); next to ʕ: F2 +132.78 (1706.2), F3 +53.87 (2539.7); one male speaker | 4 | as reconstructed in the notes |
| pulmonic | ʜ | Heap 1997 | "trilling is about 40 Hz" in the phonetician's voiceless trill | 1 | as printed |
| pulmonic | ʜ | Moisik & Esling 2010, Fig. 2 | "An epiglottal trill (234 ms) in Somali", one token | 1 | as printed |
| pulmonic | ʋ | Colombo 2015, Tables 5 and 8 | onset <w> F2 1381 Hz, CI 1244-1514; onset duration 0.049-0.061 s | 2 | as printed |
| pulmonic | ʎ | Rost Bagudanch 2009 | the UAB repository answers with a bot wall (Anubis): **not re-opened** | 0 | not checked |
| pulmonic | ɬ ꞎ | Gordon et al. 2002 | the archive copy is blocked for this tool and the publisher's is paywalled: **not re-opened** | 0 | not checked |
| other | ʡ | Sylak 2013, table (16) | low vowels after ʡ: F1 810.327, F2 1144.648; five male speakers | 1 | as printed |
| non-pulmonic | ǀ ǃ ǂ ǁ | Miller & Shah 2009, section 3.2 | dental COG about 3000 Hz (men), palatal 1500-2000 (men), lateral about 2000, alveolar about 1000 | 4 | as printed |
| non-pulmonic | ǀ ǁ ǃ¡ | Wright et al. 1995, pp. 16-17 (scanned; read from the page images) | "about a 20 ms delay between post-alveolar release and tongue slap"; Table 4 burst-plus-fricative 21.5 ms (dental), 15.7 (lateral), five male speakers | 3 | as printed (the click burst lengths are `derived` from this table) |
| non-pulmonic | ɓ ɗ ʄ ɠ ʛ | Mori 2023 (JIPA, open access) | 28 speakers (7 men, 21 women); "amplitude continuously increases during oral closure" for the implosives: the direction of the table's slope is the paper's; the 1.2 dB per 10 ms value is a reading of Figure 8, not a printed number (**L2**) | 5 | direction confirmed, value is a figure reading |
| diacritics (Tier B) | W W͈ | Zhao & Lin 2016, Table 1 | men: RF1 1.56, RF2 1.06, RF3 0.98 | 6 | as printed |
| other sounds (Tier B) | 𝼄 𐞜 | Steed & Hardie 2004 | lateral F2 1349.3, F3 2537.3 (Table 1); fricative 17.04 cs; energy at about 2 kHz with a possible second peak at 2.4 kHz | 6 | as printed |
| phonation (Tier B) | Œ Ю | Allegra et al. 2019, Table 2 (Europe PMC XML) | jitter ES 3.91 ± 2.36 (n 32), TEP 2.92 ± 1.95 (n 35) | 4 | as printed |
| phonation (Tier B) | C | Chen et al. 1997 (ASA abstract) | men's vocal fry 49.1 Hz, modal 117.5 Hz, 10 men and 10 women | 3 | as printed |
| airstream (Tier B) | ↓ | Orlikoff et al. 1997 (Europe PMC abstract) | inspiratory voice 5.1 semitones above comfortable expiratory, 16 subjects | 4 | as printed |
| connected speech (Tier B) | (.) (..) (…) | Campione & Véronis 2002 | brief pauses around 150 ms, medium around 500, spontaneous 78 and 426, long centred on 1585 ms | 3 | as printed |
| connected speech (Tier B) | \ | Tumanova et al. 2011, Table 3 (PMC) | repetitions 0.28 to 1.69 s (mean 0.87), 19 children | 2 | as printed |
| suprasegmentals | ˌ | Torresquintero 2016, pp. 16-17 | primary 8 ms longer than secondary, F0 3.8 Hz higher (not significant) | 1 | as printed |
| suprasegmentals | ‿ | Shoemaker 2012 | HAL answers with a bot wall (Anubis): **not re-opened** | 0 | not checked |
| diacritics | ˞ | Hagiwara 1995 | the eScholarship PDF is a scan with no text layer and 199 pages: Table 7.1 **not located** by the auditor | 0 | not checked |

Totals: 47 entries checked (of which 42 fully confirmed, 1 confirmed in direction with a figure-read value, 4 not re-openable); 171 values compared, 0 mismatches. The four sources that could not be re-opened (Jongman 2000, Rost 2009, Gordon 2002, Shoemaker 2012) and the one not located (Hagiwara 1995) are listed in `OPEN_QUESTIONS.md` for the human (section 9, L5); nothing suggests their values are wrong, but the auditor could not see them.

## 3. Provenance honesty (scripted: `audit5/provenance.txt`)

- The validator (`engine/ipa/table.py`): 392 entries, 0 problems, 436 estimated values queued. Re-run by the auditor.
- `literature`: 240 values, 41 distinct source ids, every one in `ipa/sources.toml` with `opened = true` (210 sources, all opened). **L1:** `REFERENCES.md` holds the Phase 4 sources by delegation ("every source an entry of the master table cites is in `ipa/sources.toml`") rather than by entry: 25 of the 41 ids the table cites (jassem1992, maselli_etal2026, punnoose_2010, espy_wilson_1992, chong2022, ... ) were not named in `REFERENCES.md` itself (`audit5/provenance.txt`). The playbook (R3) asks for the citation in `REFERENCES.md`; the information exists, in the store the file points to. Low: a documentation gap, no value is unsourced.
- `measured`: 44 values, every one names a proof file that exists and holds the key it corrects (`trims` or `said_as.keys`).
- `estimated`: 436 values, every entry id queued in `OPEN_QUESTIONS.md` Q15. The notes say where each estimate comes from; 313 of them do not contain the word "estimate" or an explicit "no measurement found", most because they point to a sibling value ("as for consonants", "see a2"). None presents the number as a measurement: the tag is the statement. Not a defect.
- `derived`: 487 values, each with a rule; every source id a rule names is in `sources.toml`, except three named as "in the read-ahead" or as a summary: `kye2021` (ʼ's burst gain, also in the Phase 0 checklist sources), `schindler2005` (the fry labels' F0), `abudalbuh2011` (a VoQS jaw setting): **L3**, the three should be entries of `sources.toml` or the notes should say they were not opened (they are tagged `estimated`, so nothing rests on them as fact).
- Weak literature, honestly labelled: Moisik & Esling's 234 ms is one token (the note says so); Żygis's 20 ms is one token (said); Chiu's glyphs are garbled (said, and the auditor's reading agrees); Karaoui's loci are reconstructed from differences in the text (said; the arithmetic checks). **L2:** Mori 2023's closure-voicing slope (1.2 dB per 10 ms, five implosives) is a reading of a figure, tagged `literature`; `derived` (with the reading as the rule) would state what it is.
- No `literature` or `measured` value lacks a real source or proof. No `estimated` value is presented as fact in `CREATED_SOUNDS.md`, `PROJECT_STATE.md` or `LANGUAGE_STATUS.md` (every table entry is at level 2, "engine-verified", never higher).

## 4. Composition: a sample said and measured (scripted: `audit5/audit_compose.py`; logs `audit5/compose_marks.log`, `audit5/compose_prosody.log`, results `audit5/audit_compose_32.json`)

**Every entry re-rendered.** Before sampling, the auditor made the engine say all 392 table entries again (`sweep.py --rounds 1`, no design rounds, `audit5/sweep_rerender_tail.log`): 392 rendered, 389 passed every check and their proof files came out byte for byte as Phase 4 left them (the renders are deterministic); the three that did not are the approximate clicks ǀ ǂ ǃ, whose stated deviation (the voice 20 to 34 ms after the burst, the module's floor) is accepted only after the design loop's five rounds, which `--rounds 1` skipped: an artefact of the auditor's flag, not a change in the sounds. Their proof files were restored.

**Marks on bases their proofs never used.** Each of the 36 Tier A marks with a measurable shift was composed on three bases drawn at random from the pool its meaning allows (vowels for the vowel marks, voiceless stops for the aspiration and release marks, sonorants for the syllabic mark, and so on), leaving out the bases its own proof used; each pair was said plain and marked in three contexts (ˈpVp ˈtVt ˈkVk, or ˈaCa ˈiCi ˈuCu) and judged by the sweep's own paired-difference rule. 107 mark-on-base pairs, 96 in the intended direction (90 per cent); every one composed by the front-end (no fallback, no loss). The 11 that were not:

| Pair | What was measured | Reading |
|---|---|---|
| ʼ on c | the long VOT 38 → 8 ms (wanted +, 82 to 136) | a harness reading, not the sound: the frames and the signal hold the ejective (closure, burst, 100 ms of silence, the voice late); `vot_long` reads 0 on k and c before [a]; ʼ's own proof on k passed because the median over three vowels hid the [a] reading. **M3** |
| ˡ on k | burst found 1 → 1 (wanted gone) | the engine's `noburst` takes the burst out but leaves k's 15 ms of breath (AH 39 in the frames), which the burst finder reads as a release; t and d, unaspirated, release cleanly. **M4** |
| ̆ on l | 45 → 40 ms (wanted at least -8) | the mark asked for 0.6 of l's 50; the module floors a consonant near 40 ms. A limit on consonants shorter than about 50 ms; the proof's bases (a, e, n) are longer. **L6** |
| ̘ on b, d; ̙ on f, k | no measure applies | the tongue-root marks' consonant transform (F1 x0.95 / x1.05) has nothing to show on a stop or fricative, which have no F1 to read. Nominal. **L7** |
| ̙ on m; ̞ on m | F1 +7.9 and +14.9 Hz (15 needed) | on a nasal's 240 Hz murmur F1 the marks' 5 and 10 per cent are at or under the harness's 15 Hz floor. **L7** |
| ̝ on i | F1 -8.3 Hz (23 needed) | a close vowel's F1 (217 Hz) sits on the voice's second harmonic, where the tracker cannot follow a further drop (D15). **L7** |
| ̝ on w | F1 +22.7 Hz (wanted -), periodicity above 1 kHz -8.8 dB (wanted -, met) | the friction the raised mark adds over w's voice is right; the F1 reading moves the wrong way under that noise. **L8** |

(The first run of the sampling script went on from the marks to the prosody entries and stopped on a fault of the script itself, which had left the prosody cases without the front-end's text that the syllable-break and tie tests read; in that run the break's "the syllable begins where the mark is" failed on every vowel for that reason. The script was corrected and the 32 prosody entries run again; `audit5/compose_marks.log` keeps the marks' lines and `compose_prosody.log` the corrected run.)

**Suprasegmentals and tones on other vowels.** The 32 prosody entries (24 tones, 2 stresses, 4 boundaries, 2 ties) were said on i, o and ɛ instead of their proofs' a, e and u and judged by `prosody.judge`: 32 entries, 335 targets, 329 met. Not met: the falling tone's start on [i] (both the diacritic ̂ and the letters ˥˩, the same sound), the rising-falling tone's first leg on [ɛ] (both ᷈ and ˧˦˨), and one of the ties' 76 targets (ɡ͡b's closure against the plain b's) for both ͜ and ͡. Each twin pair fails the same target, so the two spellings say the same thing; each failure is one vowel of three on one target of six to nine (**L9**). Stress, length (through the marks above), the breaks, the link and the register steps held on every new vowel.

So 36 + 32 = 68 diacritic, stress, length, break and tone entries were measure-checked for their intended effect on material their proofs did not use (the playbook asks for 30).

## 5. Created sounds

75 registered (55 Tier A, 20 Tier B), each pointing at a table entry with a passing proof. The auditor:

- re-read the literature behind the Tier A created sounds whose values are `literature` (section 2): c, ħ, ɐ, ɕ, ɤ, ɨ, ɬ, ɭ, ɯ, ɱ, ɳ, ɵ (Kuronen: not re-downloaded; the thesis was taken from JYX with the human's say-so in Phase 4 and nothing of it is in the tree), ɶ, ɻ, ʀ, ʂ, ʈ, ʉ, ʋ, ʕ, ʙ, ʜ, ʡ, ǀ ǁ ǂ ǃ (Miller & Shah), 𝼄, Œ Ю, and found every value as printed;
- read the notes of every `estimated` value of a created sound (ɘ ɞ ɰ ɴ ʟ ɥ χ ɧ ʐ ʑ ɮ ɸ β ʍ ɢ q ɦ ʘ, the clicks' realisation keys): each states what it rests on and that nothing measured was found; the estimates are plausible by place (uvular below velar, voiced equal to voiceless, midpoints between cardinal neighbours), with two remarks: **M2** (ɞ's F3) and **L4**: ɰ's F2 (1300 Hz, "w raised for the lack of rounding") sits well above the F2 of its vowel ɯ (808 Hz, Jassem), whose semivowel ɰ is; 900 to 1100 Hz would be nearer that reading. Both are queued for an expert (Q15); L4 is a note for that review, not a change the auditor can ground in a measurement;
- re-rendered and re-measured all 75 with the sweep (section 4's run): 72 passed exactly as in Phase 4, the three approximate clicks as explained there;
- the three Tier A created sounds marked `approximate` (ǀ, ǂ, ǃ: the voice onset after the click's burst, 20 to 34 ms against the 13 to 26 specified, the module's own floor, Q13/D60) state their deviation and bounds; the 117 Tier B approximate entries likewise. Kept.

## 6. Coverage, re-run by the auditor (`engine/ipa/coverage.py --quiet`, 2026-10-10)

    section             mapped  composed   created   MISSING   BLOCKED  no entry    all
    pulmonic                30         0        29         0         0         0     59
    non_pulmonic             0         6         5         0         0         0     11
    other_symbols            2         2         8         0         0         0     12
    vowels                  19         0         9         0         0         0     28
    diacritics               0        32         0         0         0         0     32
    suprasegmentals          6         3         0         0         0         0      9
    tones                   10        10         4         0         0         0     24
    all                     67        53        55         0         0         0    175
    coverage: 175 of 175 checklist entries done (mapped 67, composed 53, created 55); MISSING 0, BLOCKED 0; rendered and measured 175 (proof passed 175); approximate 3
    provenance of every value in the table: derived 186, estimated 170, literature 210, measured 37
    0 without an entry; 0 entries not on the checklist
    state against proof: every entry that is not MISSING has a passing proof
    proof against map: every proof of a done entry was made on the map as it stands
    Unicode net: 891 of 891 classified; A 123, B 48, C 575, alias 73, not-phonetic 72
    tier B: 186 done and proved (mapped 5, composed 162, created 19), 0 MISSING, 17 notation only (acknowledged by the human as unsupported-with-justification, D81: nothing to say); approximate 117

And, independently of coverage.py: every one of the 175 checklist proof files exists, says `passed`, was made on `stage-dev`, and holds rendered cases (1,617 in all) with a WAV hash and per-phone measures (`audit5/proofs_check.txt`).

## 7. Harness sanity: wrong sounds planted (scripted: `audit5/audit_sanity.py`; logs `audit5/sanity_before.log`, `sanity_after_voicing.log`, `sanity_after_level.log`)

Twelve faults were planted in the realised map the sweep says an entry with (a key changed on its sound line, or its carrier swapped), and the sweep's own `say_entry` and B2 contrasts run on each:

| Planted fault | Before | After the fixes (section 10) |
|---|---|---|
| s said with voice (`voi=1`) | **passed every check** (H1) | caught: T-voicing, voiced share 1.0 against at most 0.5 |
| a whispered (`voi=0 whisper=44`) | **passed every check** (H2) | caught: T-voicing, voiced share 0.0 against at least 0.6 |
| a 30 dB down (`av=-30 ah=-30`) | **passed every check** (H3) | caught: T-level, 16.1 dB under its neighbours against at most 10 |
| z without voice (`voi=0`) | caught (B2: voiced share against s) | caught (B2 and T-voicing) |
| l said on j with l's keys | caught (B3: F1 266 against 369, F2 2157 against 1698) | caught |
| m said on b with m's keys | caught (B3: F1 F2 F3; B2 against n) | caught |
| n said on d with n's keys | caught (B3: F1, F3, duration) | caught |
| p aspirated (`vot=80`) | caught (B3: VOT) | caught |
| r with no trill (`trate tapms tdepth` dropped) | caught (B3: trill rate and closure; B2 against ɾ) | caught |
| ʃ with s's noise keys | caught (B3: peak 5062 against 3820, F3 locus; B2 against s) | caught |
| i said with u's keys | caught (B3: F1 F2 F3; B2 against y and ɨ) | caught |
| t with no burst (said on n) | caught (A1 and B3) | caught (and T-voicing) |

Three holes, all of one kind: nothing in the checks looked at whether a letter was voiced as its features say, nor at how loud it was; the formants, the noise, the timing and the partner contrasts were all in place. A voiceless fricative said with voice, a voiced vowel said whispered and a vowel made nearly silent all passed as themselves. Two new checks (T-voicing, T-level, section 10) close them; the twelve cases are the regression test (`audit5/audit_sanity.py`).

## 8. Checklist completeness: the chart re-derived

The auditor fetched the IPA's current chart page (revision note "IPA Chart revised to 2015/2005", re-issued annually, copyright 2026 IPA, CC BY-SA 4.0) and the seven official 600 ppi sub-chart images (`IPA_Kiel_CP/CnP/OS/V/D/S/T_0600.png`), read each image, and wrote down every symbol with its code points without looking at the Phase 0 file (`audit5/checklist_rederived.py`):

| Section | Auditor's count | How counted |
|---|---|---|
| Consonants (pulmonic) | 59 | plosives 13 (ʔ counted), nasals 7, trills 3, taps/flaps 3 (ⱱ), fricatives 22, lateral fricatives 2, approximants 5, lateral approximants 4 |
| Consonants (non-pulmonic) | 11 | 5 clicks, 5 voiced implosives, the ejective mark (the four examples pʼ tʼ kʼ sʼ are examples, not symbols) |
| Other symbols | 12 | ʍ w ɥ ʜ ʢ ʡ ɕ ʑ ɺ ɧ, and the tie bar in both positions (t͜s, k͡p as printed) |
| Vowels | 28 | the chart's 28 letters (ə and ɐ between the pairs) |
| Diacritics | 32 | the 31 cells of the box plus the ring above (ŋ̊) named in the footnote |
| Suprasegmentals | 9 | primary, secondary, long, half-long, extra-short, minor group, major group, syllable break, linking |
| Tones and word accents | 24 | 5 level diacritics + 5 level letters, 5 contour diacritics + 5 letter sequences, downstep, upstep, global rise, global fall |
| **All** | **175** | |

Diff against `inventory/IPA_CHECKLIST.json` (175 entries): 0 symbols in the auditor's list missing from the checklist, 0 in the checklist missing from the auditor's, 0 section differences, every code-point id identical (the contour letter sequences as ˩˥ ˥˩ ˧˥ ˩˧ ˧˦˨, downstep and upstep as U+A71C and U+A71B). The checklist's own twelve `equivalent_to` pairs (ring above/below, the two tie bars, the ten tone diacritic/letter twins) are the chart's own doublings, each with an entry and a proof of its own.

Every symbol has a rendered, measured entry (section 6). The measure-check of 30 or more diacritic, stress, length, break and tone entries for their intended effect, on bases and vowels their own proofs did not use: section 4.

## 9. Findings, ranked

| # | Severity | Finding | State |
|---|---|---|---|
| H1 | high | the harness let a voiceless letter said with voice pass (s with `voi=1`): nothing checked a letter's voicing against its features | fixed: T-voicing |
| H2 | high | the harness let a voiced vowel said whispered pass | fixed: T-voicing |
| H3 | high | the harness let a vowel 30 dB down (16 dB under its neighbours) pass: a sound hardly made | fixed: T-level |
| M1 | medium | z, ʝ, ɣ carried none of the noise shaping s, ç, x got, so three voiced/voiceless pairs differed in more than voicing, against the table's own rule (ʒ ʐ ʑ ɮ follow it) | fixed: noise targets added, re-proved |
| M2 | medium | ɞ's estimated F3 (2563) above the unrounded ɜ's (2484), against the rounding rule its neighbours obey | fixed: derived below ɜ's (2300), re-proved |
| M3 | medium | `vot_long` reads 0 for the ejective on k and c before [a] though the sound is right; the proof's median over vowels hid it | not fixed: Q39 (2), for Phase 6's harness work; ʼ on c recorded here |
| M4 | medium | the engine's `noburst` leaves an aspirated stop's breath (15 ms on k) after a suppressed burst, so ̚ ˡ ⁿ on k are not wholly unreleased, lateral or nasal | not fixed (an engine change needing the seven templates rebuilt): the three marks now `approximate` with the deviation stated; Q39 (1) for Phase 6's rebuild |
| L1 | low | REFERENCES.md named only 16 of the 41 sources the table cites, delegating to `ipa/sources.toml` | fixed: a generated list of the 40 cited sources appended |
| L2 | low | the implosives' closure-voicing slope, read off a figure, was tagged `literature` | fixed: `derived`, the reading as its rule |
| L3 | low | three sources named in notes (kye2021, schindler2005, abudalbuh2011) were not in `ipa/sources.toml` | fixed: added, as recorded in REFERENCES.md |
| L4 | low | ɰ's estimated F2 (1300) sits well above its vowel ɯ's (808) | Q38 for the expert review |
| L5 | low | five sources could not be re-opened by the auditor (bot walls, a 403, a paywall, a text-less scan) | Q37 |
| L6 | low | the extra-short mark on a consonant of about 50 ms is floored by the module near 40 ms | noted here |
| L7 | low | the tongue-root, raised and lowered marks' consonant transforms are nominal on obstruents and at the harness's floor on a nasal's F1; ̝ on i cannot lower an F1 that sits on a harmonic | noted here |
| L8 | low | ̝ on w: the F1 reading moves the wrong way under the friction the mark adds (the friction itself is right) | noted here |
| L9 | low | on the new vowels, the falling tone's start on [i], the rising-falling tone's first leg on [ɛ] and ɡ͡b's closure ratio miss one target each | noted here |
| L10 | low | s, ʃ, ɬ carry an F3 (ɬ also F2) locus from `chong2022` that z, ʒ, ɮ lack: a place cue at the vowel's edge the voiced partners do not get | Q39 (3) |
| L11 | low | `register.py` counts a created sound's revision as 1 plus its trims, so ɞ (CS-0006) stays at revision 1 though its F3 specification changed (DESIGN.md 5 asks for revision plus one) | noted here and in PROJECT_STATE for Phase 6; the change is recorded in D88 |

Nothing missing, silent or unlabelled was found: every checklist symbol has an entry, a passing proof on the final stage, 1,617 rendered cases, and the chart re-derived by the auditor is the same 175 symbols.

## 10. Fixes (second pass), with the measurements before and after

- **H1, H2, H3: two checks added to the sweep's judge** (`engine/ipa/sweep.py`, part of B3 for every letter): *T-voicing*, the share of the target's frames the engine voiced must be at most 0.5 for a voiceless letter and at least 0.6 for a voiced, breathy or creaky one (the proofs read 0 to 0.36 and 0.84 to 1.0; a click's or ʡ's unspecified voicing is not judged); *T-level*, the target's loudest phone against the louder of its neighbours, median over the contexts, at least -10 dB for a vowel and -25 for a consonant (the proofs read -2.4 to +6.7 and down to -12.6). Before: the three planted faults passed every check. After (`audit5/sanity_after_voicing.log`, `sanity_after_level.log`): s with voice, voiced share 1.0, caught; a whispered, 0.0, caught; a 30 dB down, -16.1 dB against its neighbours, caught; the nine controls still caught. The whole sweep below shows the two checks pass every real entry. The floors are set from the proofs' own range with a margin, not from the smallest attenuation they catch: a vowel about 15 dB down, or a consonant about 12 dB down, would still pass T-level; the planted 30 dB case read -16.1 dB. A sound that quiet is the hole the audit found; a finer floor would need a study of the module's own level variation across contexts, left to Phase 6.
- **M1: z, ʝ, ɣ given their voiceless partners' noise targets** (`noise.peak_hz`: z 4591 Hz `derived` from s's literature peak; ʝ 4000 and ɣ 2200 `estimated`, equal to the ç and x estimates), and re-proved by the whole sweep: z peak 4660.6 Hz (s 4660.6), noise centre above 1 kHz 4387.4 (s 4527.8); ʝ peak 3608.2 (ç 4259.7), centre 3595.2 (ç 3789.9); ɣ peak 2405.5 (x 2205.0), centre 2614.7 (x 2594.6); keys z a2=0 a3=0 a4=50 a5=30 a6=0 f4=124 hold=98 l2=453 lk=53, ʝ a2=36 a3=36 a4=56 a5=0 a6=0 f4=121 hold=73 voi=1, ɣ a2=50 a3=70 a4=50 a5=0 a6=0 f3=99 hold=68 voi=1. Before: z's noise centre above 1 kHz 3505 Hz against s's 4528; ʝ 2875 against ç 3790; ɣ 3135 against x 2595.
- **M2: ɞ's F3 derived below ɜ's** (2300 Hz: ɜ's literature F3 times the mean F3 ratio of the rounded/unrounded pairs œ/ɛ and ɔ/ʌ, 0.926) and re-proved: ɞ F3 measured 2302.8 Hz against the target 2300 (ɜ 2478.3), F1 505.5, F2 1272.3; passed True, 1 design round(s). Before: 2563 specified, 2570 measured, above ɜ's 2484.
- **M3's evidence** that the ejective's sound is right on k before [a] is the frame dump in `audit5/ejective_frames.txt` (closure silent 85 to 150 ms, the burst at 155 to 165, the ejective's silence to 260, the voice from 270).
- **M4 labelled** (not fixed): ̚ ˡ ⁿ are `approximate` with the breath residue on an aspirated stop stated; Q39 (1) carries the engine fix to Phase 6's rebuild. **M3 recorded**: Q39 (2).
- **L1, L2, L3 fixed** in `REFERENCES.md` (the generated list of the 40 cited sources), `ipa/table/non_pulmonic.toml` (the five slopes `derived`, the figure reading as the rule) and `ipa/sources.toml` (three entries). **L4, L5**: Q38, Q37. **L6 to L9**: recorded in sections 4 and 9.
- **The whole sweep with `--apply` on the fixed table and the new checks** (`sweep_p5b.log`): `sweep: 392 entries, 392 rendered, 392 passed every check, 0 not yet; proofs in ipa/proofs/`. Then `register: 75 created sounds, 75 lines`; the validator: `table: 392 entries (composed 245, created 75, mapped 72); 0 problems; 437 estimated values queued for verification`; coverage:

    section             mapped  composed   created   MISSING   BLOCKED  no entry    all
    pulmonic                30         0        29         0         0         0     59
    non_pulmonic             0         6         5         0         0         0     11
    other_symbols            2         2         8         0         0         0     12
    vowels                  19         0         9         0         0         0     28
    diacritics               0        32         0         0         0         0     32
    suprasegmentals          6         3         0         0         0         0      9
    tones                   10        10         4         0         0         0     24
    all                     67        53        55         0         0         0    175
    coverage: 175 of 175 checklist entries done (mapped 67, composed 53, created 55); MISSING 0, BLOCKED 0; rendered and measured 175 (proof passed 175); approximate 6
    provenance of every value in the table: derived 193, estimated 171, literature 205, measured 39
    0 without an entry; 0 entries not on the checklist
    state against proof: every entry that is not MISSING has a passing proof
    proof against map: every proof of a done entry was made on the map as it stands
    Unicode net: 891 of 891 classified; A 123, B 48, C 575, alias 73, not-phonetic 72
    all                                                                5       162        19         0        17   203
    tier B: 186 done and proved (mapped 5, composed 162, created 19), 0 MISSING, 17 notation only (acknowledged by the human as unsupported-with-justification, D81: nothing to say); approximate 117

- The staged golden regression, run again after everything above: `golden: 155 packs, 29237 cases, 0 FAILED, 0 changed within tolerance, 2196 s` (`golden_p5.log`); nothing of this phase reaches it, and the run shows it.
- Every proof file now carries the T-voicing and T-level targets; the proofs of z, ʝ, ɣ and ɞ are new; every other entry's proof was re-made on the new map (the settle passes) and passed as before.
