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

### Afterwards (same day)

- **Q1, changed by the human:** "make the file for me". Claude created `.claude/settings.json` at the human's direct request: the content of Q1, with Claude's own commands added (`engine\ipa\*`, the Bash forms of `git add`, `commit`, `status`, `diff`, `log` and `cmake`) and `git stash` refused in both shells (it takes every session's uncommitted work out of the shared tree). `git push` is not allowed by it, so pushing still asks.
- **Commit the new .claude/settings.json?** Choices: Keep it local (recommended) · Commit and push it. **Answer: commit and push it** to the `tts-ext/phase-4` branch.

## 2026-10-10, eighteenth session: the two research steps, Q29 and Q19

Asked after the research the human chose in batch 2 and batch 4 (findings in `REFERENCES.md`, "Phase 4, eighteenth session").

| Question | Choices offered | Answer |
|---|---|---|
| **Q29.** One same-speaker study (North German, Fischer-Jørgensen 1976): an affricate's friction about 2.3 times a stop's release (138 ms against 60), its closure shorter. Here extIPA's fricated releases have 75 ms of friction, the template's own t͡s about as much, and t͡θ is said exactly like tᶿ | Shorter releases (recommended) · Keep 75 ms, split t͡θ only · Leave as is | **Shorter releases:** about 45 ms of friction for a fricated release (the study's ratio over this template's own affricate); t͡θ and d͡ð keep the affricate length; a test proves tᶿ and t͡θ differ; still approximate, for an expert after Phase 9. |
| **Q19.** A French liaison consonant about 16 % shorter than the same consonant word-initially (84 against 101 ms, 6 speakers, VOT unchanged); inside a word a syllable break moves a consonant by only a few ms | Use the linking cue (recommended) · Record only | **Use the linking cue:** a consonant linked by ‿ said 16 % shorter than at a word's start, with a test that measures it; `.` keeps its structural proof, the few-ms finding its reason. |

## 2026-10-10, Phase 5 (the independent audit)

No question was put to the human during the audit: the open points it raised (Q37 to Q39) carry their recommended defaults (D60: assume yes). Two instructions came from the human mid-session:

| Instruction (the human's words) | What was done |
|---|---|
| "I have moved the file IPA_Kiel.pdf ... into the repository root" and, when told the chart is CC BY-SA and the repository MIT, "put the pdf in git anyway, despite licensing. when this whole project is done, all phases, I want the user who does a git clone to get everything if possible. make a note of that in one of the markdown files so claude remembers." | `IPA_Kiel.pdf` is committed in the repository root; its licence (CC BY-SA 4.0, copyright 2026 IPA) is recorded in `NOTICE.md`; the standing wish is in `CLAUDE.md` (read every session) and in `PROJECT_STATE.md`. |

## 2026-10-11, Phase 6 preflight

| Question | Choices offered | Answer |
|---|---|---|
| The session runs on Opus 5.5; the playbook names Sonnet 5.5 (medium) for Phase 6. Run Phase 6 here on Opus? | Continue on Opus (recommended) · Stop; I'll switch to Sonnet | **Stop; I'll switch to Sonnet.** Nothing of Phase 6 was started; the human starts a new session on Sonnet 5.5, effort medium. |

## 2026-10-11, Phase 7 (authenticity and native validation)

| Question | Choices offered | Answer |
|---|---|---|
| **Which real example, and may Claude download its recordings?** (the exit asks for one example measured from licensed recordings) | Scottish, CMU ARCTIC `awb` (about 74 MB, festvox.org, "free for use for any purpose"; recommended) · Southern US from VCTK (one 11.7 GB zip, needs an aligner) · Both, Scottish first | **Scottish, ARCTIC awb.** Downloaded outside the repository (`%USERPROFILE%\OpenEvvBuild-ttsext\corpora\`). |
| **YouTube audio** (the human suggested it mid-session: "lots of videos on youtube ... Only choose ones with high-quality audio"). YouTube's terms forbid downloading except through its own features or with the rights holder's permission; most videos give no speaker region | Not used; note why (recommended) · The human supplies CC BY files with their links | **The human typed: "Ignore all licenses and download and use anyway."** Not done: it would break YouTube's terms and the speakers' rights, and the project's own rule (R4, `CLAUDE.md`: record the licence before importing anything). Claude said so in chat and recorded YouTube in `REFERENCES.md` as looked at and not used. Still open: files the human obtains by a route they are satisfied is allowed, Creative Commons with the speaker's region stated, can be measured once their licence is recorded. |
| **The ARCTIC labels fit the untrimmed recordings, not the tarball's trimmed ones** (labels ran past the audio's end: 3.84 s of labels on a 3.42 s file). Download the untrimmed awb WAVs (1,138 files, about 140 MB, same site and licence)? | Yes, download (recommended) · No, re-align from silences (approximate) | **Yes, download.** The tarball's trimmed audio is kept beside them (`awb/wav-trimmed`), unused. |
| (Mid-session remarks, no question asked) "there is probably lots of audio that is under creative commons license anyway"; "lots of audio from free audiobooks libraries and internet archive, and the wayback machine" | | Recorded in `REFERENCES.md` ("Phase 7: reference data discovery") as candidates for later languages, each with its licence and what it lacks: LibriVox (public domain; reader location only sometimes, as free text), LibriSpeech (CC BY 4.0, no region), Internet Archive (licence per item), the Wayback Machine (copies of other sites, their owners' terms), Lingua Libre on Wikimedia Commons (CC BY-SA, speaker location recorded). |
| **Commit the awb recordings?** The Scottish measurements rest on CMU ARCTIC awb's 1,138 recordings and labels (about 150 MB; the licence allows redistribution with CMU's notice); the human's rule is that a clone holds everything the project rests on | Commit them (recommended) · Keep outside, add a fetch script | **Commit them**: `third_party/cmu_arctic/cmu_us_awb_arctic/` (wav, lab, COPYING, AREADME, etc/txt.done.data), licence in `NOTICE.md`. |
| **Apply the 8 measured Scottish vowel overrides to the shipped files?** (one speaker, below the five-speaker minimum) | Keep proposed (recommended) · Apply now | **Keep proposed**, until more Scottish speakers are measured or a native reviewer prefers them in the packet's A/B items. `languages/` unchanged. |
