# Phase 6 triage: fix list and needs-escalation list

Written by `harness/triage.py` from the measurements named in its header; the rules that give a layer are there too. Levels are those of the Phase 1 baseline: this phase measured no language afresh against references, so none changed. A3 on the final stage (`stage-dev`): 145 packs, 0 failures (20 packs failed it on the Phase 3 stage).

| Failure layer | Languages |
|---|---|
| phoneme values | 21 |
| G2P | 68 |
| stress-or-tone | 0 |
| unknown | 11 |
| not measured | 41 |
| passes ASR | 14 |
| all | 155 |

### Fixes, in the order to do them (grouped by shared root cause)

1. **Check A fails (the engine made a meant vowel silent)**
   qu. Read the case in `status.json`; the sound definition or the map line for that vowel.

2. **Phones the engine meant that the map gave no sound (phone-unsounded)**
   65 events in 17 languages (en-us-nyc 9, ga 8, en-shaw 8, gd 4, en-gb-x-rp 4, en-gb-x-gbcwmd 4, en-gb-x-gbclan 4, en-gb-scotland 4, en-029 4, cy 4, quc 2, pt-br 2, pap 2, nci 2, mto 2, qu 1, gn 1). The map line says `-` or names a sound the module lacks; add the sound to the pack or map the phoneme.

3. **Check B fails (vowel or nasal values outside cited ranges)**
   dede en-029 en-gb-scotland en-gb-x-gbclan en-gb-x-gbcwmd en-gb-x-rp en-shaw engb eses esus. Native modules and English or Spanish dialects, where cited ranges exist; the measured values are in `status.json`. Fix is a sound value (formant targets of the template or the pack), judged against the reference, not by ear.

4. **The text is read wrongly, or the recogniser cannot judge it (own voice of eSpeak NG fails too)**
   68 languages, worst first: vi-vn-x-south (eSpeak 1.42, here 1.49), am (eSpeak 1.34, here 1.43), th (eSpeak 1.31, here 1.22), vi-vn-x-central (eSpeak 1.28, here 1.63), si (eSpeak 1.15, here 1.03), sd (eSpeak 1.12, here 1.05), as (eSpeak 0.99, here 0.98), my (eSpeak 0.99, here 1.13), vi (eSpeak 0.98, here 1.27), ml (eSpeak 0.96, here 0.94), ba (eSpeak 0.95, here 0.92), yue (eSpeak 0.85, here 1.29), ps-x-northwest (eSpeak 0.68, here 0.59), ps-x-yusufzai (eSpeak 0.68, here 0.62), ps (eSpeak 0.67, here 0.61), ps-x-southeast (eSpeak 0.67, here 0.62), he (eSpeak 0.63, here 0.65), ur (eSpeak 0.57, here 0.65), ar (eSpeak 0.57, here 0.65), pa (eSpeak 0.55, here 0.66), lb (eSpeak 0.55, here 0.57), uz (eSpeak 0.54, here 0.46), fo (eSpeak 0.53, here 0.54), gu (eSpeak 0.48, here 0.44), mn (eSpeak 0.46, here 0.42) .... Nothing in the sounds of this engine explains these; the fix is the rules of eSpeak NG for the language, the own reader of a pack (DESIGN.md 8.2), or a better reference sentence set. A native reader is needed to tell which.

5. **The voice of this engine is understood worse than that of eSpeak NG on the same phonemes**
   34 languages. By template: dedx: 28 languages, mean gap 0.19; esex: 3 languages, mean gap 0.10; frfx: 2 languages, mean gap 0.18; itix: 1 languages, mean gap 0.14. The widest gaps: yue +0.43, vi-vn-x-central +0.34, mr +0.34, vi +0.29, az +0.27, cmn +0.27, sl +0.27, tt +0.22, fa +0.21, tr +0.21, lt +0.20, nl +0.18, fr-be +0.18, fr-ch +0.18, el +0.16. The cause is in what this engine does with the phonemes: stress, duration, coarticulation or sound values; the harness cannot yet separate them (the next measure to build: the same sentences with the own phoneme durations of eSpeak NG and stress, to see which of the two the engine gets wrong).

6. **Languages no recogniser can judge**
   41 languages: ab an bpy chr cmn-latn-pinyin crh cv eo fa-latn grc hak ia io jbo kaa kl kok ku ky lfn lij ltg nog om or pdc pdc-x-lehigh pdc-x-midwest piqd py qdb qya rup shn sjn smj ti tn ug xex yue-latn-jyutping. Level 2 at most until a native reader or another recogniser reads them (Phase 7 builds the review packets).

### Needs escalation (reasoned, not guessed)

- **Tonal languages, for Fable 5.1 at `high` (playbook Phase 6 rule): chr cmn cmn-latn-pinyin hak jajp my pa shn vi vi-vn-x-central vi-vn-x-south yue yue-latn-jyutping.** Reason: tone contours, tone sandhi and tone-bearing syllable length are set by the tone lines of the pack and the F0 control of the template; the harness measures a contour against the points asked, not whether the points are the language. Their layers above say where the ASR evidence points.
- **Click languages: none**: no phoneme of the eSpeak NG tables of the 145 maps has a click letter (ǃ ǀ ǁ ǂ ʘ) in its IPA (checked over every `phonemes.map`); the clicks are in the master table (Phase 4) and no pack uses them.
- **Heavy allophony or sandhi, for Opus 5.5 at `high`:** languages whose written form leaves out what is said (Arabic and Hebrew vowels, Persian short vowels: `ar`, `he`, `fa`) and Indic schwa deletion and conjunct pronunciation (`hi`, `ur`, `bn`, `as`, `gu`, `kn`, `ml`, `mr`, `ne`, `or`, `pa`, `si`, `ta`, `te`, `sd`, `kok`, `bpy`). Reason: the fault, where there is one, is in how eSpeak NG reads the text (G2P layer), which needs the language own phonology to judge; an ASR score cannot say.
