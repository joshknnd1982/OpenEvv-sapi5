# Phase 9: completion review

Playbook Phase 9, run on 2026-10-11 (twenty-third session) on Fable 5.1 (the phase's model), branch `tts-ext/phase-9`. This session did not build the project; everything below was verified by running it, not by reading the earlier phases' summaries. Raw output of every command relied on is shown (R16).

## 1. Doctor, golden regression, coverage, harness

The full doctor (`engine\doctor.py` without `--quick`: the harness self-test, the pack tests and the byte-identical check against `languages/`, the validators, the master table and its validator, coverage, the estimated-value queue, and the whole golden regression of the staged modules):

    doctor: C:\Users\joshk\OneDrive\dev\espeakproject\OpenEvv-sapi5, full, stage C:\Users\joshk\OpenEvvBuild-ttsext\stage-dev
    PASS  env        Python 3.10.11 at C:\Users\joshk\OpenEvvBuild-ttsext\venv\Scripts\python.exe; stage C:\Users\joshk\OpenEvvBuild-ttsext\stage-dev
    PASS  harness    == 76 checks, 76 passed, 0 failed  (docs\tts-extension\harness\selftest.py --quick, 3 s)
    PASS  packs      Ran 22 tests in 10.928s  (engine\packs\test_packs.py, 11 s)
    PASS  packs      check: every file identical to languages/  (engine\packs\build_packs.py check, 11 s)
    PASS  validate   validate: 21 packs, 21 accepted, 0 rejected  (engine\packs\validate_packs.py, 13 s)
    PASS  validate   validate: 6 packs, 6 accepted, 0 rejected  (engine\packs\validate_packs.py ca-va-x-evvdemo, 1 s)
    PASS  validate   validate selftest: 16 of 16 pass  (engine\packs\validate_packs.py --selftest, 0 s)
    PASS  validate   normalize selftest: 3 of 3 pass  (engine\authenticity\normalize.py --selftest, 0 s)
    PASS  validate   ingest selftest: pass  (engine\review\ingest_feedback.py --selftest, 0 s)
    PASS  table      table: 393 entries (composed 245, created 76, mapped 72); 0 problems; 439 estimated values queued for verification  (engine\ipa\table.py, 0 s)
    PASS  table      validator: the table accepted; 30 planted faults, 30 refused  (engine\ipa\table.py --selftest, 1 s)
    PASS  coverage   coverage: 175 of 175 checklist entries done (mapped 67, composed 53, created 55); MISSING 0, BLOCKED 0; rendered and measured 175 (proof passed 175); approximate 6  (engine\ipa\coverage.py --quiet, 15 s)
    PASS  coverage   state against proof: every entry that is not MISSING has a passing proof
    PASS  coverage   proof against map: every proof of a done entry was made on the map as it stands
    PASS  estimated  439 estimated values in the table, 439 queued in Q15 (written 2026-10-11)
    PASS  golden     golden: 155 packs, 29237 cases, 0 FAILED, 0 changed within tolerance, 2118 s  (docs\tts-extension\harness\golden.py, 2119 s)
    doctor: 16 checks, 16 passed, 0 warnings, 0 FAILED (none), 2175 s

Run at 13:15 on 2026-10-11 with the symbol sweep, the two trial helpers and the speech-recognition run sharing the machine (the golden took 2118 s instead of Phase 8's 1728 s; nothing it measures depends on time). The golden is of the staged modules (`golden-staged/`, D43): 155 packs, 29,237 cases, 0 FAILED. `git status` after it: no tracked file under `harness/results/` or `ipa/` changed.

After every change of this phase (the reference lookup, the regenerated results, the trial packs under `packs-proposed/`), `engine\doctor.py --quick` once more:

    PASS  validate   validate: 2 packs, 2 accepted, 0 rejected  (engine\packs\validate_packs.py fi-x-evvtrial, 0 s)
    PASS  golden     golden: 6 packs, 28 cases, 0 FAILED, 0 changed within tolerance, 4 s  (docs	ts-extension\harness\golden.py --smoke, 5 s)
    doctor: 17 checks, 17 passed, 0 warnings, 0 FAILED (none), 67 s

(17 checks, not 16: the doctor now finds `packs-proposed/` and validates the two trial packs too.)

## 2. IPA coverage, re-researched

**The chart, re-fetched.** The IPA's chart page (<https://www.internationalphoneticassociation.org/content/ipa-chart>, opened 2026-10-11) says the chart has been re-issued every year since 2025 with the year and the copyright symbols updated, that the latest revision is "IPA chart revised to 2015/2005" (2005 added the labiodental flap, 2015 changed wording and layout), that the 2018 and 2020 issues were the same revision, and that the chart is CC BY-SA 4.0. The copy in the tree, `IPA_Kiel.pdf`, has SHA-256 `c8203013…706787`, the hash `REFERENCES.md` records; no PDF renderer is available here, so the seven official 600 ppi sub-chart PNGs of the same issue ("© 2026 IPA, revised to 2015/2005" in each footer) were fetched from the IPA's site (`IPAcharts/IPA_charts_E/images/IPA_Kiel_{CP,CnP,OS,V,D,S,T}_0600.png`) and read as images in this session.

**My own transcription against the checklist** (`phase9/phase9_chart_diff.py`, written and run this session, kept in the tree with the logs of the doctor, the sweep and the ASR run; it holds my reading of the seven images and compares codepoints with `inventory/IPA_CHECKLIST.json`):

    pulmonic         mine  59  checklist  59  only-in-mine []  only-in-checklist []
    non_pulmonic     mine  11  checklist  11  only-in-mine []  only-in-checklist []
    other_symbols    mine  12  checklist  12  only-in-mine []  only-in-checklist []
    vowels           mine  28  checklist  28  only-in-mine []  only-in-checklist []
    diacritics       mine  32  checklist  32  only-in-mine []  only-in-checklist []
    suprasegmentals  mine   9  checklist   9  only-in-mine []  only-in-checklist []
    tones            mine  24  checklist  24  only-in-mine []  only-in-checklist []
    total mine 175 checklist 175

How 175 relates to the "about 155" the playbook expects: 107 letters and 68 marks, where the chart prints each level and contour tone twice (a diacritic and a tone letter: 10 pairs), each of the two tie bars, and the ring above as well as the ring below (12 equivalent pairs in all, 163 distinct symbols); every printed form has its own entry so that each way of writing a sound is read and proved.

**The checklist rebuilt**: `python docs\tts-extension\inventory\build_ipa_checklist.py` ran to its last line, `agrees with the PDF and with Unicode: yes`, and `git status --short docs/tts-extension/inventory` printed nothing: the rebuilt `IPA_CHECKLIST.json` and `.md` are byte-identical to the committed ones.

**Coverage** (the doctor's lines, run this session, on the checklist as rebuilt):

    PASS  table      table: 393 entries (composed 245, created 76, mapped 72); 0 problems; 439 estimated values queued for verification  (engine\ipa\table.py, 0 s)
    PASS  table      validator: the table accepted; 30 planted faults, 30 refused  (engine\ipa\table.py --selftest, 1 s)
    PASS  coverage   coverage: 175 of 175 checklist entries done (mapped 67, composed 53, created 55); MISSING 0, BLOCKED 0; rendered and measured 175 (proof passed 175); approximate 6  (engine\ipa\coverage.py --quiet, 15 s)
    PASS  coverage   state against proof: every entry that is not MISSING has a passing proof
    PASS  coverage   proof against map: every proof of a done entry was made on the map as it stands

Every checklist symbol is mapped, composed or created; MISSING 0, BLOCKED 0; no Tier A symbol is unsupported.

**A fresh render-and-measure sweep** of the 175 (every entry said again by the real engine from IPA through the staged front-end and the staged reference module, alone and in context, and judged by the sweep's checks A0 to B2; `engine\ipa\sweep.py` over the seven chart sections, `--rounds 1` so nothing is redesigned, in a work folder of its own):

    sweep: 176 entries, 176 rendered, 173 passed every check, 3 not yet; proofs in ipa/proofs/
    sweep exit: 0 after 1854 s

(the three "not yet", from the same log:)

    U+01C0   ǀ   fail A0:ok A1:ok A2:ok B3:FAIL B2:ok  edge_F2=1548 edge_F3=2634 vot_ms=34 duration_ms=145  [vot_ms 34.0≠26]
    U+01C2   ǂ   fail A0:ok A1:ok A2:ok B3:FAIL B2:ok  edge_F2=1548 edge_F3=2635 vot_ms=20 duration_ms=110  [vot_ms 20.0≠13]
    U+01C3   ǃ   fail A0:ok A1:ok A2:ok B3:FAIL B2:ok  edge_F2=1257 edge_F3=2635 vot_ms=20 duration_ms=110  [vot_ms 20.0≠13.1]

The 176th entry is CS-0076 ɓ̥ (`U+0253+U+0325`, Tier C, which sits in the non-pulmonic section); every one of the 175 checklist ids was swept and none was missing. The three that did not pass with `--rounds 1` are the three clicks whose voice onset is the engine's own floor (the deviation `CREATED_SOUNDS.md` and the proofs state as `approximate`, D60 and D64); `--rounds 1` forbids the design loop in which that deviation is accepted within its bound. Run again with the normal rounds they pass as the committed proofs say:

    U+01C0   ǀ   PASS A0:ok A1:ok A2:ok B3:ok B2:ok  edge_F2=1548 edge_F3=2634 vot_ms=34 duration_ms=145
    U+01C2   ǂ   PASS A0:ok A1:ok A2:ok B3:ok B2:ok  edge_F2=1548 edge_F3=2635 vot_ms=20 duration_ms=110
    U+01C3   ǃ   PASS A0:ok A1:ok A2:ok B3:ok B2:ok  edge_F2=1257 edge_F3=2635 vot_ms=20 duration_ms=110
    sweep: 3 entries, 3 rendered, 3 passed every check, 0 not yet; proofs in ipa/proofs/

(ǀ's proof: `vot_ms target 26, measured 34.0, within True, approximate bound max 40`, with the deviation written out.) The 176 proofs the fresh sweep wrote were compared field by field with the committed ones: all 176 identical but for the path of the work folder the map was written in (`proofs rewritten 176, identical but for the work-folder path 176, different []`). The engine renders and measures every symbol today exactly as the proofs on record say; the committed proofs were then restored (`git checkout -- ipa/proofs`), since the sweep without `--apply` is a check and the record already holds the same content.

**Tier B (extIPA and VoQS), unsupported-with-justification**: 19 records, acknowledged by the human on 2026-10-09 (D81). They are extIPA's symbols that name no sound: `*` (a sound with no available symbol), `○` and the circled letters Ⓒ ₵⃝ Ⓕ Ⓛ Ⓖ Ⓝ Ⓟ Ⓡ Ⓢ Ⓣ Ⓥ Ṽ⃝ Ʞ⃝ σ⃝ (an indeterminate segment, consonant, obstruent, fricative, liquid, glide, nasal, plosive, rhotic, sibilant, tone or stress, vowel, nasal vowel, click, syllable), the oval round letters ("probably these sounds"), `( )` (silent articulation, mouthing) and `⸨ ⸩` (speech obscured by noise). The front-end and the reader read them, report them and invent no sound for them; `( )` and `⸨ ⸩` get a behaviour (D81). `coverage.py` counts 17 as notation only, the two with a behaviour being the difference. The rest of Tier B: 186 records done and proved (mapped 5, composed 162, created 19), 0 MISSING, 117 approximate (the doctor's coverage line, this session).

**Tier C** (beyond the chart and the extIPA/VoQS inventory): one entry, CS-0076 ɓ̥, `created`, proved in the sweep above; no Tier C item is unsupported.

**Created sounds**: 76 registered in `CREATED_SOUNDS.md` (CS-0001 to CS-0076), every one at level 2 (engine-verified on the reference template dedx); 21 of them carry `approximate` with the deviation stated (the three clicks' voice onset, which the carrier's floor in this module sets, D60 and D64; the velodorsal and the lateral-and-median fricative sounds, for which nothing measured was found; the bidental aspiration; and the rest as the register says). None is at level 3 or above: no reference recordings of these sounds were measured, and no native or expert reviewer has heard them.

**Approximate and estimated on the checklist**: 6 of the 175 entries are approximate: the three clicks ǀ ǃ ǂ (voice onset after the burst 20 to 34 ms where their specification asks 13 to 26, the carrier's own floor) and the three release diacritics ⁿ ˡ ̚ (each is the stop with its burst withheld, `noburst=1`, and nothing of the nasal, lateral or unreleased release itself beyond that). 439 values in the table are tagged `estimated` and all 439 are queued for verification (`OPEN_QUESTIONS.md` Q15; the doctor's `estimated` line). Nothing on the chart is MISSING, BLOCKED, silent or silently substituted.

## 3. Ease of extension: two fresh trials

Two fresh helpers (Sonnet 5.5, effort medium: the model each skill names) were given only the skill text, `ADDING_A_LANGUAGE.md` and what those two name, a work folder of their own, and the order to take every human decision by its recommended default and log it. Their logs, with every command, its raw output and the gaps they found, are `trials/PHASE9_TRIAL_A_fi-x-evvtrial.md` and `trials/PHASE9_TRIAL_B_nl-be.md`.

**Why trial A is a test copy and not a brand-new language.** With the eSpeak NG data the product ships (154 voices, `dist/espeak-ng-data`, the same 154 as the source clone at tag `openevv-1.2.0`), every readable language already has a pack; the only voices without one (de, en, en-US, es, es-419, fr, it, ja, pl) are the languages the ten native modules cover. A language outside the repository needs a newer eSpeak NG build, which rewrites `dist/espeak-ng-data` and waits for the human (Q44, HUMAN_ANSWERS.md; Phase 10). So trial A took the path the guide gives for exactly that case: a language generated from scratch under a private tag, Finnish as `fi-x-evvtrial`, chosen because no example or skill test had used it. That is not the letter of the criterion ("a brand-new language not in the repo"), and Q44 was answered for Phase 8's worked example, not for this trial; so the human is asked at this pause (Q51) whether the test copy stands as trial (a), or trial (a) is run again on a real new language once Phase 10 has rebuilt the eSpeak NG data.

| | Trial A: `/add-language Finnish` | Trial B: `/add-dialect Belgian Dutch of nl` |
|---|---|---|
| Result | `packs-proposed/fi-x-evvtrial/`, 114 sounds, template dedx, no hand-changed value; validator accepted; packet of 32 items; level 2 | `packs-proposed/nl-be/` extending `nl`: 11 vowel overrides, each `derived` from Adank, van Hout and Smits (2004) Table I (Southern Standard Dutch men) at the module's size (factor x0.9704); validator accepted; packet in `review_packets/nl-be/`; level 2 |
| The raw level line | `check A: pass; substituted 0; phones meant to sound 601, silent 0; formant and F0 checks 816 of 816` / `check B: too few references (4/5 in range); references for 0 vowels; 3 needed` / `ASR: CER 0.49 WER 0.87` / `level: 2 engine-verified; failure layer: unknown` | `check A: pass; substituted 0; phones meant to sound 580, silent 0; formant and F0 checks 889 of 890` / `check B: too few references (4/5 in range)` / `ASR: CER 0.199` (its parent `nl` prints the same lines on the same stage) / `level: 2 engine-verified` |
| Measured effect | none to measure (no override) | median distance from the targets over 22 words 18.1 % before, 1.7 % after; preset-2 ratio difference 0.003; 5 of 22 words still more than 6 % off (hoed F2 -21 %: its vowel is not the phoneme the override names; bal, bed, bos, maan on F1 or F2) |
| Commands run | about 20 tool commands plus about 10 file reads and 2 web calls (its count) | about 40 (its estimate) |
| Decisions a human would have made | 5 (its count: the voice `urj/fi` where the invocation said `fiu/fi`; the pack's `Order`; whether to run the whole golden beside another session; whether CER 0.49 at level 2 is acceptable; which words go in `review.toml`) | 9 (which paper and which group; the anchor; which vowels get overrides under the 6 % rule; `Order`; where the packet goes; what to do with a word the override misses; whether a worse recogniser score blocks; the level; no recordings) |
| Time | about 13 minutes | about 23 minutes |
| What the helper did not do | the whole-tree golden (it saw that a tagless run rewrites `results/diag-golden-staged.json` while this session's doctor ran, and ran `golden.py fi et hu dede` instead: `4 packs, 564 cases, 0 FAILED`); it opened `packs/fi/pack.toml` once to find the voice | fix hoed; look for recordings; use the women's values |
| Review (`tts-reviewer`) | ran: five findings, all about the trial's own log and packet (the log was not yet written when it ran; the packet was made before the status and says "level ?"; `f|h` and `s|?` unexplained; the partial golden; the ASR figure 0.49 against the 0.31 on record for `fi`) | ran: reproduced the numbers; a wrong vowel in the note (fixed); the hoed A/B pair asks a question whose two sides are the same |

**Findings about the engine, checked by this session, not by the helpers' word.** (1) Finnish quantity: `engine.py fi text tuli|tuuli|tulli` on the stage gives 775, 825 and 852 ms, 5, 5 and 6 phones (`t u l I #` for both *tuli* and *tuuli*); the long vowel is the short one's phone at `dur=117` (`languages/fi/sounds.map`), so the contrast is made but adds only about 50 ms: `OPEN_QUESTIONS.md` Q47, an `/improve-language fi` item. (2) The helper's proposed sentence "the size factor changes by under one per cent whichever anchor vowel is left out" is false: `normalize.py nl ... --anchor` over the six Dutch anchors gives 0.9704, and 0.9705, 0.9609, 0.9673, 0.9747, 0.9967, 0.9530 with one vowel left out in turn; the guide now says so and asks for the anchor to be named in each override's `norm`. (3) `fi` at CER 0.49 on the stage against 0.31 in `results/asr.json` (2026-10-05, shipped modules): see the fresh ASR run of section 4.

**Documentation fixed from the trials** (22 gaps, in `ADDING_A_LANGUAGE.md` and the two skills; the diff is in this phase's commit): how to find a voice by language code, and to use the voice that reads the language when the one given does not exist; a test copy's `Order`, `Id` and `LCID`, and how to list the taken Orders; the `[meta] status` key the generator does not write; the packet after the status (its README copies it); PowerShell showing the harmless matplotlib warning as an error; the case-id labels `f|h`, `s|?`; what "check A passes, no references, CER above 0.15, layer unknown" means and that `/diagnose-language` is the next step; the tagless golden rewriting a tracked results file and running it under the scratch stage; a stopping rule for research; `EVV_HARNESS_WORK` as a setup line; map names carry the voice prefix (`@nl:A`) and `normalize.py` and overrides are keyed by it; how to find every phoneme that says a sound; the 6 % rule also against the table's other variety, with corrections of the parent told apart from dialect differences; garbled PDF tables; copyright papers cited not kept; the CER with and without the overrides, a rise above 0.05 reported; a word an override does not reach; where a real pack's packet goes; `packs-proposed/` must be created for a hand-written pack; the anchor's effect on the size factor (measured); length as a phoneme in section 10.

**Verdict on ease of extension.** Both additions were data-only: no engine code, no module rebuilt, `languages/`, `dist/` and the shared stage untouched (each helper's final `git status` is in its log; `build_packs.py check` still prints `every file identical to languages/`). Each was measured and honestly levelled by the tools alone. What a human still decides is listed above; none of it needed knowledge outside the guide once the gaps above were filled. What the process cannot yet do is in the guide's section 10: a language eSpeak NG cannot read, dialect rules beyond vowel targets, overrides on the native modules, and level 3 for a language the reference store has no ranges for (both trials stopped at 2 for that reason).

## 4. Honest status table

**Q46 ruled first (D93)**: check B judges a pack against its own variety, then its parents, then the cross-language entries, never a sibling; a bare language takes its standard region (`pt` -> `pt-PT`). `reference.py --selftest`:

    reference selftest: 15 of 15 pass

**The ASR round trip re-run on the stage** (`asr.py`, 2026-10-11, Whisper large-v3, every language, 1291 s):

    asr: 155 languages, 105 scored, 50 unavailable -> docs\tts-extension\harness\results\asr.json

Against the record of 2026-10-05 (shipped modules): 105 pairs, median CER 0.325 -> 0.307; better by more than 0.02: 37, worse: 20, within 0.02: 48; at or under 0.15: 25 -> 24. Crossed downward (now pass): sl 0.346 -> 0.086, hy 0.175 -> 0.150. Crossed upward (now fail): ca 0.119 -> 0.263, ca-nw 0.127 -> 0.178, ca-va 0.117 -> 0.158. Most improved: sl -0.26, fr-be and fr-ch -0.23, yue -0.23, vi-vn-x-central -0.22, mr -0.18, my -0.15, af -0.15. Most worsened: si +0.28, el +0.23, cmn +0.20, vi-vn-x-south +0.18, fi +0.18, tr +0.18, ca +0.14, cy +0.10. Native modules unchanged (enus 0.006 -> 0.009; pt and pt-br identical). This resolves the trial's question about `fi`: 0.49 is what the stage gives (0.31 was the shipped module).

**`report.py` on the staged golden** (29,237 cases) with the new lookup:

    levels: 1 draft: 3, 2 engine-verified: 148, 4 intelligibility-verified: 4
    check A pass: 152 of 155
    check B: pass 4, fail 3, too few references 144, no reference 4
    failure layers: {'unknown': 72, 'phoneme values': 6, 'stress-or-tone': 7}

**The honest table** (every language, dialect and accent: `LANGUAGE_STATUS.md`, the generated table, 155 rows; the kinds: 10 native modules, 145 read by eSpeak NG, of which 21 dialect packs and 1 accent pack, en-us-nyc counted among the dialects):

| Level | Count | Which | What it means, plainly |
|---|---|---|---|
| 1 draft | 3 | cmn, cmn-latn-pinyin, qu | check A fails: the engine did not realize what its frames asked (Mandarin: 83.6 % of the formant and pitch checks on the shipped golden and 83.8 % on the staged, Q48; Quechua: three phones meant to sound were silent) |
| 2 engine-verified | 148 | everything else | the engine realized what it asked for; 144 of them have too few cited reference values to go further, 3 (dede, eses, ca-va) fail check B against their own references, 1 (ca) passes neither B nor ASR |
| 3 reference-verified | 0 | | the four that pass check B also pass ASR |
| 4 intelligibility-verified | 4 | enus, en-us-nyc, pt, pt-br | check A, check B and ASR (CER at or under 0.15) all pass |
| 5 native-validated | 0 | | no named native speaker or expert has signed off anything |

**Nothing below level 5 is confirmed authentic, and nothing is at level 5: no language, dialect or accent in this product has been heard by a native speaker or an expert.** "Authentic" is a word this project does not yet use for any of its 155. Level 4 says a recogniser understood eight sentences; level 2 says the synthesiser did what the data asked. The checks are shown in the table's columns, and the 21 dialect packs carry the variety, region and speaker group they claim, with a descriptive source each (D91).

Changes from the committed status, every one explained: cmn and cmn-latn-pinyin 2 -> 1 (Q48: not a change in the engine, a status report that had not been re-run since the golden gained its `#` cases); check B rows under D93 (ca-va FAIL 21/29 on its own ranges; eight packs FAIL -> too few references; en-us-nyc 72/82 -> 82/94; pt 21/24 -> 20/24); failure layers sl and hy "unknown" -> none (ASR now passes), ca and ca-nw none -> "unknown" (ASR now fails), cmn "stress-or-tone" -> "phoneme values".

**The ten items for native review, in order** (D82: review starts after this phase; `FINDING_NATIVE_REVIEWERS.md` says how; packets exist for the first three):

1. **Scottish English, `en-gb-scotland`**: the packet is made (86 items, A/B blind) and 10 overrides from one speaker wait on it; a reviewer's A/B answers decide whether they apply (Q42).
2. **Belgian Dutch, `nl-be`** (proposed): 11 overrides from a published table, packet made; the recogniser's error rises with them (0.199 -> 0.293), which only a Flemish ear can weigh.
3. **US English, `enus`**: the product's main voice, level 4, the richest reference set (416 entries); a native sign-off would be the project's first level 5, and the Spanish-accented example packets (`en-us-x-evvdemo-es`) rest on it.
4. **Mandarin, `cmn`**: level 1 (Q48), tones, the largest speaker population in the list; a native listener can say whether the neutral tone and the measured failures are audible.
5. **Hindi, `hi`**: CER 0.37, the Indic allophony list (Phase 6 escalation), retroflexes and aspirates created on the German template.
6. **Arabic, `ar`**: CER 0.65, pharyngeals and emphatics (created sounds ħ ʕ and the pharyngealized diacritic are in it).
7. **German, `dede`**: the native module fails check B on its own references (16/25), CER 0.03: the reviewer hears whether the vowels the ranges reject sound wrong.
8. **Castilian and Latin American Spanish, `eses`, `esus`**: `eses` fails check B 6/14 on its own references; `esus` has none of its own now; both native modules.
9. **Valencian and Central Catalan, `ca-va`, `ca`**: ca-va fails its own Valencian ranges (21/29) and the Catalan packs' CER rose on the stage above 0.15; a Catalan reviewer hears the stage against the shipped modules.
10. **The 76 created sounds** (clicks, implosives, ejectives, the epiglottals, the velodorsal and lateral-median fricatives, the tone and register controls): an expert phonetician, not a native speaker of one language, reviews `CREATED_SOUNDS.md` with the proofs' renders; the 21 approximate ones first.

## 5. Rewrite and legacy report (R18)

**No component was replaced or rewritten.** The design (DESIGN.md 12.1, approved D35) keeps the synthesis core, the sources and noise, the frame, the timing model and frame generation, the modules' phoneme tables, G2P, language loading, voice scaling and the public integration layer unchanged, and extends the accent layer, the front-end and the harness. The only "replace" in the design, the sound knowledge (the generator in `engine/accent/` with its profiles), was to be replaced *beside the old* by the master table, the adapter and pack sources, with the old path kept until migration stage M6. Where that stands:

| What | Done | Legacy remains? | Evidence |
|---|---|---|---|
| The master table, adapter and composition (`engine/ipa/`, `ipa/table/*.toml`) | built; every chart symbol is said through it on the reference template | the legacy generator (`engine/accent/sounds.py`, `prosody.py`, `questions.py`, `engine/make_espeak_packs.py`, the profiles) is still what every shipped pack's sound lines come from | 145 packs `realization = "legacy"`, 17 `"module"`, 0 `"master"` (grep of `packs/*/pack.toml` this session); DECISIONS.md D89 "Not done, by design: the `master` realization (M3, M4)" |
| Packs (`packs/`, the compiler `engine/packs/`) | every one of the 162 folders of `languages/` is a pack that builds byte-identically | nothing was removed; `languages/` is still what the product reads and is unchanged since release 1.2.4 | the doctor: `check: every file identical to languages/` |
| The two defect fixes X-1 (voicing switched on after a stop before a voiceless sound or a pause) and X-2 (the tone key `av` parsed and never applied), in `openevv/src/accent/evv_accent.c` | fixed in the staged template modules only | the shipped modules in `languages/` still have the defects; the staged modules wait for Phase 10 | D40, D41: 941 of 29,237 golden cases moved, every one explained and shown to the human, approved D43; the staged golden (`golden-staged/`) is recorded on the fixed modules and passes (this session's doctor) |
| The burst source (C12) in `openevv/src/klatt/klatt_synth.c` | 16 lines added: a frication gain from the dead frame word ATV, inert at zero | nothing replaced: "at nought, as for every sound before, nothing changes" | `git diff tts-ext-baseline..HEAD -- openevv/src/klatt/klatt_synth.c` (the only change to the synthesis core) |
| The accent layer and the front-end | extended (`evv_accent.c` +929 lines, `evv_map.c` +1133, `frontend_main.c` +1080; six files modified under `openevv/src` and `frontend/`, the rest added) | every new key and mechanism is inert without markup; existing packs' sound is held by the golden | `git diff --stat tts-ext-baseline..HEAD` (this session); golden 0 FAILED |

**Whether to retire any legacy code**: nothing can be retired yet. The legacy generator is the production path for all 145 eSpeak-read packs (the `master` realization was never built, M3 and M4 are not done), the shipped modules are the pre-fix ones, and the native modules were never rebuilt. Retiring anything before Phase 10 ships the staged modules would leave the product without its only path. Recommendation: **retire nothing** in Phase 10; revisit the legacy generator only after a `master` realization exists and has proved byte-identical or approved-different for every pack (R18c). This is put to the human at the pause; nothing is retired without a yes (R18e).

## 5b. Residual risks and recommended next improvements

**Risks that stand**

- **No authenticity has been confirmed.** 0 of 155 are native-validated; 148 are at level 2, 144 of them because the reference store has ranges for few languages (English, German, Spanish, Portuguese, Dutch, Catalan-Valencian, Mandarin, Cantonese, Armenian, Korean, Hungarian, Tamil: 970 entries). Level 3 is out of reach for most languages until ranges are added, which the `/improve-language` skill does one language at a time.
- **The staged modules change intelligibility both ways** (section 4): 37 languages better, 20 worse; the Catalan packs cross the 0.15 line upward. Phase 10 ships the stage; the human decides whether Catalan is diagnosed first.
- **Mandarin is level 1 on shipped and staged alike** (Q48); whether the harness's measurement or the sound is at fault is not known.
- **Check B measures raw Hz** against the references' speaker group with no size normalization (D93, stated); the engine's adult male voice and a source's men may differ in size, so some "out of range" rows are size, not quality.
- **Estimated and approximate values**: 439 `estimated` values queued (Q15), 6 approximate chart entries, 21 approximate created sounds, 117 approximate Tier B records: each honestly labelled, none verified against recordings.
- **Thin evidence behind the two measured dialects**: Scottish on one speaker (five is the minimum the validator wants), Belgian Dutch on a table alone, no recordings.
- **The harness on natural speech**: VOT is not measured on recordings (Q40); 50 languages have no recogniser (Q7's Omnilingual plan not done).
- **The legacy generator is the only production path**: the `master` realization (M3, M4) was never built, so sounds in packs still come from the old generator with no provenance per value; the native modules do not know the accent layer (D13, Q6). Nothing is retired (Q49).
- **The reference lookup's locale keys**: `zh-*` packs do not reach the `cmn`/`yue` entries (D93, stated).
- **Shared-tree hazards found by the trials and this review**: a tagless `golden.py` rewrites a tracked results file; `asr.py` rewrites `results/asr.json`; `a3.py <tags>` truncates its results file; `sweep.py` without `--apply` still rewrites the tracked `ipa/proofs/` (this session restored them with `git checkout` after comparing). Documented, not changed.
- **Licensing** (R4, flagged since Phase 0): the language data in every module is IBM's, in litigation; the eSpeak NG side is GPL; nothing of either was copied into MIT files.

**Recommended next improvements, in order of return**

1. Phase 10 as planned, with the Catalan rise and Mandarin's level 1 in the release notes.
2. Native review packets for the ten items above, starting with the three that have packets.
3. `/diagnose-language cmn` on Fable 5.1 (Q48), then `/diagnose-language ca` (the stage's rise).
4. Reference ranges for the ten largest languages the store lacks (Hindi, Arabic, Russian, Japanese, French, Italian, Polish, Turkish, Vietnamese, Indonesian): the single biggest lever on the status table, each a cited table through `/improve-language`.
5. Size normalization in check B (D93, stated) so that "out of range" means quality.
6. More speakers for Scottish (OpenSLR 83 or VCTK, with an aligner; Q42) and recordings for Belgian Dutch.
7. Finnish and Swahili (Q47, Q45) by `/improve-language`; the `master` realization (M3, M4) only after the human wants provenance per pack value.

## 6. Verdict

Every exit criterion of Phases 0 to 8 was checked by this session, by running it where it can be run and by opening the artefact where it is a document:

| Phase | Its exit criteria (as `PROJECT_STATE.md` records them) | Verified in Phase 9 by |
|---|---|---|
| 0 | architecture map, the checklist from the current chart, baseline tag | `ARCHITECTURE_MAP.md` present; the chart re-fetched and re-transcribed, 0 differences, checklist rebuilt byte-identical (section 2); `git rev-parse tts-ext-baseline` = `10542ae` |
| 1 | harness measures, reference ranges, ASR, golden, status baseline | the doctor: `selftest.py --quick` 76 of 76; `asr.py` every language; `golden.py` 0 FAILED; `report.py` run (section 4) |
| 2 | design approved | `DESIGN.md` and D35 ("APPROVED", 2026-10-05) |
| 3 | the two defects fixed, the capabilities, the IPA reader, the master table | the staged golden passes (0 FAILED) and every chart symbol is said through the table (the sweep, section 2); D40, D41, D43 |
| 4 | every checklist symbol mapped, composed or created, MISSING 0, BLOCKED 0, proof by rendering | `coverage.py` 175 of 175, the fresh sweep 176 of 176 rendered and judged, proofs identical to the record |
| 5 | independent audit, 0 differences | `AUDIT_PHASE5.md`; this session's own independent transcription of the chart, 0 differences (section 2) |
| 6 | all languages load from packs, regression passes, every non-passing language has a layer and evidence | `build_packs.py check` every file identical; golden 0 FAILED; `LANGUAGE_STATUS.md` regenerated with a layer per failing language (section 4) |
| 7 | the pipeline end to end on one real example, validator rejects incomplete packs, packet generator works | `validate_packs.py --selftest` 16 of 16, `normalize.py --selftest` 3 of 3, `ingest_feedback.py --selftest` pass (the doctor); the Scottish packet in the tree (4.27 MB, 86 items); the pipeline run again end to end by trial B on Belgian Dutch |
| 8 | six skills exercised, the reviewer agent, the guide with examples that run, the doctor passes | two skills run again by fresh helpers (section 3) and the `tts-reviewer` agent launched by both; the doctor 16 of 16 |

**Phases 0 to 9 are complete, with one Phase 9 item put to the human: whether the Finnish test copy stands as trial (a), the only form the trial could take with the shipped eSpeak NG data (Q51).** No IPA chart symbol is MISSING or BLOCKED; every one renders and is measured; adding a language, a dialect or an accent is a data-only change that the tools measure and level without the engine being touched. What is *not* complete is authenticity: no language is native-validated, and the status table says so for each. The project is complete once Phases 10 (release) and 11 (cleanup) are done. **Next: Phase 10.**

## R15 review

The `tts-reviewer` agent (fresh context: the exit criteria above and the uncommitted tree) re-ran `reference.py --selftest` (15 of 15), called `lookup()` for ca-BA, ca, en-GB, es-MX, es-419 and nl-BE (None each: no sibling ever returned) and for es, en, pt, ca-VA (es-ES, en-US, pt-PT, ca-VA), re-derived the status counts, the ASR comparison and the Mandarin check from the files, re-ran the chart diff (175 of 175, 0 differences), and confirmed nothing changed under `languages/`, `dist/`, `openevv/` or `packs/`. Seven findings, each answered:

1. *Trial (a) is a test copy, not "a brand-new language not in the repo", and the Phase 9 table said "done" without asking the human.* True. Section 3 and PROJECT_STATE now say so plainly, and the human is asked at the pause (Q51).
2. *The nl-be packet still held the hoed A/B pair whose two sides are the same.* Fixed: `review.toml` asks about *doek* instead; the packet was made again on the trial's scratch stage (`packet nl-be: 79 items (words 14, sentences 4, compare 44, sounds 17)`), and the new pair differs as a pair should (`c-u-doek-A` u asked 245 / 1040 Hz, measured 250 / 1040; `c-u-doek-B` asked 305 / 844, measured 303 / 841).
3. *The R15 result was pointed at but not shown.* This section, and D94.
4. *The evidence lived only in the session's scratch folder.* `docs/tts-extension/phase9/` now holds `phase9_chart_diff.py`, `doctor_full.log`, `sweep_phase9.log` and `asr_phase9.log`; the seven official sub-chart images are in `docs/tts-extension/inventory/ipa_chart_images/` with their CC BY-SA 4.0 licence recorded in `NOTICE.md` (the rule: a clone holds everything the project rests on).
5. *Mandarin's percentage: 1979 of 2367 is 83.6 %, not 83.8 %.* Corrected in this report, `LANGUAGE_STATUS.md`, D94 and Q48 (83.6 % shipped, 83.8 % staged).
6. *The Finnish trial packet said "level ?".* Made again on the trial's scratch stage after the status was set: `packet fi-x-evvtrial: 32 items`, README "Status when made: level 2 (engine-verified)".
7. *`sweep.py` rewriting tracked proofs was missing from the hazards.* Added to 5b.

Not re-reviewed (R15 allows one re-review; each fix above is shown with its output). The quick doctor after the fixes is in section 1.
