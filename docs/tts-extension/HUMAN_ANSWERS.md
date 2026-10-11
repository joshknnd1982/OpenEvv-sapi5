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

## 2026-10-11, Phase 8 (skills and automation)

| Question | Choices offered | Answer |
|---|---|---|
| **Q43. The doctor must check that every pack validates; 25 dialect packs fail the authenticity validator (Q41).** How should Phase 8 handle them? | Fix them now: reclassify the 5 that are not dialects (4 spellings, and mn-f, a voice) as languages, cite a real descriptive source for each of the other 20 and fill their metadata, nothing about their sound changed; the doctor then requires every pack to pass (recommended) · The doctor tolerates the 25 as recorded debt and fails only on a new rejection | **Fix them now.** |
| **Q44. The worked "add a language" example of `ADDING_A_LANGUAGE.md`**: every language eSpeak NG reads already has a pack. Which example? | A test copy of Swahili generated from scratch under a private tag (`sw-x-evvdemo`), marked TEST, in a separate examples folder, never shipped; real sentences, so ASR and the packet run end to end (recommended) · A tiny invented language with hand-written words (stops at check A) · A real new language from a newer eSpeak NG release (needs the shipped eSpeak NG data rebuilt; documented, not run) | **A test copy of Swahili.** |
| **Q46. Valencian reference ranges and sibling dialects.** The `/improve-language` skill test added jimenez2019 Table 1 (14 entries, ca-VA, adult men) to the reference store: ca-va's check B went from "too few references" to FAIL 21/29 (F1 of /ɛ ɔ/ 40-55 Hz below the range, /i u/ just below). `reference.lookup()` lends a variety's ranges to every variety of the language, so ca, ca-ba and ca-nw are now judged against them too (FAIL 21/29 each; levels unchanged at 2). A parent-chain rule (a pack's own variety, then its parent, never a sibling) would change check B for 12 packs (ca ca-ba ca-nw en-029 en-gb-scotland en-gb-x-gbclan en-gb-x-gbcwmd en-gb-x-rp en-shaw engb esus pt; pt loses its "pass 21/24" and may drop from level 4). | Keep the ranges and today's lookup; record the question with the 12-pack table for Phase 9 to rule on (recommended) · Set the ranges aside as a proposal; nothing changes · The parent-chain lookup now | **Keep, Phase 9 rules.** The ranges are kept; OPEN_QUESTIONS.md Q46 holds the table. |

## 2026-10-11, twenty-third session (Phase 9): asked at the phase's pause

| Question | Choices offered | Answer |
|---|---|---|
| **Q49. Retire any legacy code?** (R18e; `COMPLETION_REVIEW_PHASE9.md` section 5.) No component was replaced: the legacy generator (`engine/accent/`, `engine/make_espeak_packs.py`) is the production path for all 145 eSpeak-read packs, the `master` realization was never built, the shipped modules are the pre-fix ones. | Retire nothing now; revisit after a `master` realization exists and has proved every pack byte-identical or approved-different (recommended) · Retire the legacy generator in Phase 10 (not possible without breaking every eSpeak-read pack's build) | **Retire nothing now** (asked again at Phase 10's start, 2026-10-11, twenty-fourth session). |
| **Q50. The two trial packs in `packs-proposed/`.** `nl-be` is a real proposed dialect (11 sourced overrides; the recogniser's error rises with them, 0.199 to 0.293); `fi-x-evvtrial` is a test copy of Finnish. | Leave both in `packs-proposed/` for Phase 10's say-so, `nl-be` named in the release notes as proposed and unshipped, `fi-x-evvtrial` moved to `docs/tts-extension/examples/packs/` in Phase 10 (recommended) · Ship `nl-be` in Phase 10 · Delete both (not before Phase 11, R20) | **Ship `nl-be` in Phase 10** (asked again at Phase 10's start, 2026-10-11). Not the recommended choice; the pack is moved to `packs/`, its overrides applied, `languages/nl-be/` built and shipped in 1.3.0 at level 2, its recogniser figures stated in the release notes. `fi-x-evvtrial` (a TEST copy) stays in `packs-proposed/`, unshipped, for Phase 11 (R20: nothing moved or deleted in its name before then). |
| **Q51. Does the Finnish test copy stand as trial (a) of Phase 9?** The playbook asks for "a brand-new language not in the repo"; with the shipped eSpeak NG data every readable language already has a pack (the only unpacked voices are the nine the native modules cover), so the trial generated Finnish from scratch under a private tag, `fi-x-evvtrial`, by the guide's own path for a new language, and reached level 2. The R15 reviewer noted that Q44 was answered for Phase 8's example, not for this trial. | Accept the test copy as trial (a): the steps, tools and decisions are the same as for a real new language, and a real one needs the eSpeak NG data rebuilt, which is Phase 10's say-so (recommended) · Run trial (a) again in Phase 10, after the eSpeak NG data is rebuilt with a language not yet in the tree · Run it now with a newer eSpeak NG built to a scratch data folder (a day's work; does not change what the product ships) | **Accept the test copy as trial (a)** (asked again at Phase 10's start, 2026-10-11). |

## 2026-10-11, twenty-fourth session (Phase 10, release)

| Question | Choices offered | Answer |
|---|---|---|
| **The release's version, and the D34 say-so.** The new installer replaces the 7 shipped template modules and the front-end with the staged ones. Shown first: 1,136 of the 29,237 golden cases differ between `golden/` (shipped) and `golden-staged/`, in 143 packs, all but 3 of them `x|` cases (a consonant at a word's end or before another consonant) and the 3 others Shavian English's `e@ i@ i@3` (D40); they come from the approved defect fixes (D40, D41, D43) and the whispered-sound rule (D87, Q28); the other 28,101 cases are identical. | 1.3.0 and ship them (recommended) · 1.2.5 and ship them · Do not replace the modules | **1.3.0 and ship them.** |
| **Merge `tts-ext/phase-10` into `main` and push `main`?** (step 3.5; the README becomes GitHub's front page; a normal merge or fast-forward, never forced; no GitHub Release, no installer upload) | Yes, merge and push (recommended) · Not yet; after I test · No | **Yes, merge and push.** Asked before the human had tested the installer; done at once. |

## 2026-10-11, after Phase 10: the human's order for Phases 11 to 13

The human wrote (in chat, after the Phase 10 pause), in short: move cleanup after the new work; build the tool that switches **all** languages, dialects and accents read by eSpeak NG to the new IPA sound system, "even if it is just hypothesis at this point", "as automatic as possible"; "a mass switch is fine"; "let the ten originals alone"; native speakers approve later, through pull requests on GitHub; then build a new installer to test, and commit, push and release on GitHub the language packs with their new sounds, all source, a new README and the installer. And: "If the generator was never built, then you must add a phase that builds it." Carried into the playbook as Phases 11 (the generator and a pilot), 12 (switch all, measure), 13 (release 1.4.0 on GitHub), with cleanup moved to Phase 14 and R20 moved to Phase 13.

| Question | Choices offered | Answer |
|---|---|---|
| **A language whose recognition error rises a lot (by more than 0.10) after the switch?** | Ship anyway, report it; any language can go back with one line; only a sound that comes out silent or swapped keeps its old line, as a fault (recommended) · Keep the old sounds for those · Ask me per language | **Ship anyway, report it.** |

## 2026-10-11, during Phase 11: the human's order that all future work uses the new sounds

The human wrote (in chat): the playbook must say that "all subsequent and future openEVV languages, accents, dialects and language improvements, etcetera, must use the new sounds, IPA and sound generator(s)". Carried into `TTS_EXTENSION_PLAYBOOK.md` as standing rule R21 (1.3) and a pointer in Part 3 and in workflows A to F. Not a question; no choices were offered. Carve-outs written into R21: the legacy realization stays as a per-pack switch and as the fault fallback (R1, R18e); the ten native languages stay untouched unless the human orders otherwise.
