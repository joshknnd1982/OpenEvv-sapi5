# The human's answers

Every question put to the human, the choices offered and the one picked, newest at the bottom. Claude asks each open question as a set of choices (the recommended one first), records the answer here at once, and then carries it into `OPEN_QUESTIONS.md` and `DECISIONS.md`. The questions' full text is in `OPEN_QUESTIONS.md` under the same number.

Answers given before this file existed are in `DECISIONS.md` (D34, the design's five questions; D60, "assume yes" for any question missed; D81, the notation-only records; D82, native speakers after Phase 9).

## 2026-10-10, seventeenth session: the open questions, Q1 to Q36

### Batch 1: setup

| Question | Choices offered | Answer |
|---|---|---|
| **Q1.** A permissions file (`.claude/settings.json`) so build, test and speak-to-WAV commands run without asking each time (Claude may not write it) | I'll create it (recommended) · Leave it as is | **I'll create it.** The human creates the file from the content in OPEN_QUESTIONS.md Q1; Claude does not write it. |
| **Q5.** A Stop hook that keeps a turn going while the smoke test fails | Leave it out (recommended) · I'll add it | **Leave it out.** |
| **Q4.** A second machine or CI | No, one PC (recommended) · Yes, plan CI for Phase 8 · Yes, start it now | **No, one PC.** Revisit in Phase 8. |
| **Q8.** The 32-bit US English module is the old 1.0.0 file | Rebuild with the rest (recommended) · Rebuild it soon · Leave it | **Rebuild with the rest:** both US English files when the native modules are rebuilt and replaced, with proof and the human's say-so then. |

### Batch 2: data for later phases, and two judgement calls

| Question | Choices offered | Answer |
|---|---|---|
| **Q7.** Speech recognition for the 46 languages Whisper lacks (Meta's Omnilingual ASR, Apache 2.0, needs WSL2 and a few GB of model) | Decide in Phase 7 (recommended) · Yes, plan Omnilingual · No | **Yes, plan Omnilingual.** Phase 7 sets up WSL2 and Omnilingual ASR, asking the human before each download, to cover about 30 more languages. |
| **Q9.** Judge the recogniser against natural recordings of the same sentences (Common Voice, CC0) | Decide in Phase 7 (recommended) · Yes, use recordings · No | **Yes, use recordings.** Phase 7 downloads Common Voice clips per language (asking first) and compares against them, beside the 0.15 pass mark. |
| **Q35.** Left and right offsets (extIPA ◌͔ ◌͕, VoQS J͔ J͕) told apart by a small stated convention | Keep the convention (recommended) · Make the difference larger · Say them alike | **Make the difference larger**, still labelled approximate and listed for an expert after Phase 9. |
| **Q29.** Fricated releases (tᶿ kˣ ...) with Liverpool English lengths, about an affricate's; nothing measured tells them apart | Keep, expert review later (recommended) · Make them shorter · Search more first | **Search more first:** a research step for clinical recordings or papers before deciding. |

### Batch 3: engine fixes before the final rebuild of the seven templates

| Question | Choices offered | Answer |
|---|---|---|
| **Q28, Q30, Q33.** Three voicing faults: a whispered vowel's 10 to 15 ms of voice before a stop; a ̬-voiced t's 5 to 10 ms gap after its release; ̬ unable to voice a whispered letter | Before the final rebuild (recommended) · Later (Phase 5 audit) · Leave them | **Before the final rebuild:** fix all three in the accent layer, with a test that catches each, then rebuild the seven templates once. |
| **Q36.** A random cycle-to-cycle jitter setting (harsh, oesophageal, tracheo-oesophageal voices) | Yes, before the rebuild (recommended) · Later · No | **Yes, before the rebuild:** a jitter key in the accent layer, tested against `pulse_jitter_pct`, used for the harsh family and Œ, Ю. |
| **Q23.** The raised mark ̝ on an approximant (ɹ̝, l̝) makes no friction | Yes, before the rebuild (recommended) · Later (Phase 5) · Leave it | **Yes, before the rebuild:** friction over the voice for ̝ on an approximant, proved on ɹ and l. |
| **Q27.** Pre-aspiration ʰp gets 20 to 40 ms of the 98 asked | When a language needs it (recommended) · Before the rebuild · Leave it | **When a language needs it** (Icelandic, Scottish Gaelic, Faroese, Sámi); approximate until then. |

### Batch 4: the remaining technical items

| Question | Choices offered | Answer |
|---|---|---|
| **Q14.** No report when a sound the markup asked for is never placed | Yes, at the rebuild (recommended) · Later | **Yes, at the rebuild:** the report goes into the accent layer with the final template rebuild, counted over the golden. |
| **Q19.** The syllable mark `.` and the link `‿` have no measured cue | Look again in Phase 5 (recommended) · Search now · Leave as is | **Search now:** a research step before Phase 4 ends. |
| **Q31.** A voiced lateral release on ɡ needs a measure of the release's own friction | With the final sweep (recommended) · Phase 5 · Leave it | **With the final sweep:** build the measure in the remaining Phase 4 work, then give 𐞞 ɮ's F3 again. |
| **Q34 (2).** A strike and a fricated release share their noise settings (¡ˣ) | Only if ever needed (recommended) · Fix before the rebuild | **Only if ever needed.** |

### Questions not asked (already closed)

Q2, Q6, Q10, Q11, Q13, Q16, Q17, Q18, Q20, Q21, Q22, Q24, Q25, Q26, Q32 are answered or done (their text in OPEN_QUESTIONS.md says how); Q3 is a standing rule (new sound definitions in files of our own); Q15 is the queue of `estimated` values, not a question.
