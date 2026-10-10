# Project state

Read this at the start of every session, after Part 1 of `TTS_EXTENSION_PLAYBOOK.md` and your phase section.

## Phase

**Phase 4 (Master IPA → acoustic table): COMPLETE (2026-10-10, eighteenth session)** on branch `tts-ext/phase-4`. Sessions of 2026-10-06 to 2026-10-10: Opus 5.5. The eighteenth session's work is D87 (the engine change before the rebuild, the two research steps, the review's fixes). **Next: Phase 5 (Independent audit)**, in a new session; read "For Phase 5" below first.

### Phase 4 at its end (coverage.py on the final stage, 2026-10-10)

    section             mapped  composed   created   MISSING   BLOCKED  no entry    all
    pulmonic                30         0        29         0         0         0     59
    non_pulmonic             0         6         5         0         0         0     11
    other_symbols            2         2         8         0         0         0     12
    vowels                  19         0         9         0         0         0     28
    diacritics               0        32         0         0         0         0     32
    suprasegmentals          6         3         0         0         0         0      9
    tones                   10        10         4         0         0         0     24
    all                     67        53        55         0         0         0    175
    coverage: 175 of 175 checklist entries done (mapped 67, composed 53, created 55); MISSING 0, BLOCKED 0;
    rendered and measured 175 (proof passed 175); approximate 3
    provenance of every value in the table: derived 186, estimated 170, literature 210, measured 37
    state against proof: every entry that is not MISSING has a passing proof
    proof against map: every proof of a done entry was made on the map as it stands
    Unicode net: 891 of 891 classified; A 123, B 48, C 575, alias 73, not-phonetic 72
    Tier B (extIPA, VoQS): 203 records; 186 done and proved, 0 MISSING, 17 notation only

The exit criteria, each with its evidence (logs in `%USERPROFILE%\OpenEvvBuild-ttsext\`):

| Exit criterion (playbook Phase 4) | State |
|---|---|
| zero MISSING / BLOCKED | **met**: coverage above (`coverage_d87.log`) |
| mapped + composed + created = the Phase 0 count (175) | **met**: 67 + 53 + 55 = 175 |
| every symbol has a rendered, measured test | **met**: the final 4i, the whole sweep with `--apply` on the final stage (all seven templates rebuilt from the final source, `build4x`; front-end `p28`): `sweep: 392 entries, 392 rendered, 392 passed every check, 0 not yet`, `settle 1: 0 proofs made on another map` (`sweep_d87.log`) |
| every created sound in CREATED_SOUNDS.md with a stable ID | **met**: `register: 75 created sounds, 75 lines` (`register_d87.log`) |
| legacy golden regression passes | **met, with intended changes recorded**: the staged golden moved in 117 cases (83 packs, dedx) and then 78 cases (56 packs, the other six templates), every one Q28's rule (a voiceless l, w or ɬ before s: the s no longer begins with its voice), recorded again (D87); the engine's own gate `matrix_each`: 10 languages, 979 cases, every one as it was (`matrix_d87.log`); the front-end `p28` against `p27` on every golden input and sentence of 145 packs: 0 differ (`diag_d87.log`) |
| estimated values in OPEN_QUESTIONS.md | **met**: Q15 regenerated, 436 values (the validator: 0 problems) |
| PROJECT_STATE updated | this |
| R15 review | done (D87's last bullet): seven findings, five fixed and re-proved, one already planned (the golden after the rebuild), one not changed with its reason (V‼) |

**The final stage** is `%USERPROFILE%\OpenEvvBuild-ttsext\stage-dev`: all seven templates rebuilt from the tree's `openevv/src` (`build4x\modules`), the front-end `fe\p28-x64`. Kept: `stage-dev-langs-4v` (the stage's languages before, dedx `build4v` and six 3A templates), `stage-dev-dedx-4t`, `stage-dev-fe-p27` and older. Nothing in `languages\` or `dist\` has changed: replacing the shipped modules and front-end is a separate step, shown to the human and done only with their say-so (D34); `docs/tts-extension/SOUNDS_STAGED.md` is the text to merge into `docs/SOUNDS.md` then.

### For Phase 5 (read first)

- **What D87 changed** (read it): the accent layer's new keys `vmark`, `jit`, `rfric`; a whispered sound's voice carried off into the next (Q28); a stop the layer voices found released under its bar (Q30); `phone-unplaced` (Q14: 0 over the golden; `phone-unsounded` 65, as before); the link ‿ a mark of the consonant before it (front-end `p28`); shorter fricated releases and made affricates told from them (Q29); `rel_mid_db` (Q31); the left/right conventions widened (Q35); every template's F5 (3900 Hz).
- **Known and stated, not fixed**: on the six templates other than dedx, a voiceless l, w or ɬ before s leaves the s 2 or 3 faint voiced frames (voice under 30, the carry stopping where the module's voice falls under that); dedx has none. The harsh label's slight degree (`jit` 19) adds almost no jitter (the calibration is not a straight line under 40). Œ and Ю measure above their literature means but within one standard deviation (tested). Q27 (pre-aspiration) and Q34 part 2 stand as the human answered.
- **The audit's material**: `DECISIONS.md` D1 to D87; `HUMAN_ANSWERS.md`; `OPEN_QUESTIONS.md` (Q15 the 436 estimated values); the proofs `ipa/proofs/*.json`; the logs named above. The composition tests of the final map: `compose_d87_labels.log`, `compose_d87_g0.log` to `g2.log`.

### Phase 4 working notes, sessions one to seventeen (kept for the record)

- **Done in the seventeenth session** (D83, D84; read them before a new entry). The braces: a label (`kind = "label"`, in `ipa/table/tierb_braces.toml`) is a transform of every letter of its class in its stretch; the adapter gives each degree and each ramp step a private-use mark with `mod` lines and writes `label` lines (`d` a base, `m` a mark on the base before it, `r` a ramp, `-` none, `g=` a group) and `pause` lines; the front-end (`p27`) composes each letter in a stretch with them, a degree on one symbol, the same labels written again passed over before `}`, an inner label of a group replacing the outer; a map with no `label` or `pause` lines (every pack's) reads braces and parentheses as before. New engine keys: `di`, `mono`, `mute` (and `pst` held between two sounds at the same pitch of their own). New measures: `pulses` (`pulse_hz`, `pulse_jitter_pct`: a voice no tracker follows), `ah_mid`, `f0_span_st`, `f0_low_hz`, `gap_ms`, `vowel_voiced`, `vowel_db`; new checks T-pause, T-brace, T-degree, T-ramp, T-same; a semitone measure needs 0.5 and a per-cent one 2 points. **What the design rounds taught**: test voice quality on [a e ɛ] long vowels (this module's [i u o] read F1, pulses and breath badly, and its high vowels already carry breath); compare two entries only on the same words (long against long); a level offset does not silence a sound's transitions (`mute` does); the synthesiser's flutter is too small to measure (Q36). D84: the tie entry's `released` pairs (t͡θ, d͡ð) get a line and a `letter` line, the module's own affricates a `letter` line too, and the front-end composes both sides' marks on a pair that is a letter. Logs (`%USERPROFILE%\OpenEvvBuild-ttsext\`): `sweep_d83a.log` to `sweep_d83e.log` (design rounds), `matrix_d83.log`, `chain_d83.log`, `diag_d83.log`, `compose_d83a.log` (labels), `compose_d83b.log`, `golden_d83.log`, `sweep_d83.log`, `register_d83.log`, `coverage_d83.log`, `selftest_d83.log`, `reader_d83.log`, `table_d83.log`; builds `build4s`, `build4t`, front-ends `fe\p24` to `fe\p27`.
- **Native speakers come after Phase 9** (the human, 2026-10-09, D82): no phase waits for or asks for one; Phase 7 builds the review packets and stops at level 4; "authentic" (level 5) only after a named native reviewer signs off, later.
- **Done in the sixteenth session** (D80; read it before a new entry). tʰ̪͆ is a letter of four characters (t with ʰ ̪ ͆, the marks read on the ʰ): t released into h̪͆'s friction (`frel`) for tʰ's aspiration, over tʰ's breath; a letter's own `release` targets (`fricated_ms`, `centroid_hz`), and every stop's release noise read over one window (`rel_centroid1k_hz`, `rel_hf_db`: the 30 ms after the burst's first 10). The raspberry ↀ͡r̪͆ is a composite of a **tied letter** ↀ͡r (a character, a tie bar and a letter the map lists as a letter) with ̪ and ͆; ↀ͡r is r's trill with no voice and no breath, friction alone (`airstream = "buccal"`, proved by a `source` target: the shares of the middle third's frames with voice, breath and friction, the measures `voiced_*`, `breath_*`, `noise_*`). ↀ alone (VoQS's airstream, or the ICPLA's abbreviation of the raspberry) waits for the braces. The front-end (`p23`) takes a letter with one to three of its own marks in one search and a tied letter (also after marks written before it), and its letter lines carry `release`, `place_mark`, `aspiration`, `fricated_release` and `tongue_part` for the fallback (Q34's first part). The validator refuses a letter over 7 bytes and a tied letter with marks of its own. **Long runs go in a detached chain** (`%USERPROFILE%\OpenEvvBuild-ttsext\chain_d80.sh`, started with PowerShell `Start-Process` on Git's `bash.exe -c`): two composition tests, the golden, the whole sweep, register, coverage and the self-test took 1 h 26 min one after another, past the 2-hour limit a background job would have been stopped at if run as one. Logs: `sweep_d80a.log`, `sweep_d80b.log`, `sweep_d80.log`, `golden_d80.log`, `compose_d80a.log` to `compose_d80f.log` (`d80d` and the first `d80e` stopped part way), `chain_d80.log`, `coverage_d80.log`, `register_d80.log`, `selftest_d80.log`.
- **Read ahead for VoQS and the braces** (REFERENCES.md, "read ahead for VoQS and the braces"): what every VoQS symbol means (Θ is a protruded tongue), the degree numerals, extIPA's loudness glyphs and tempo words, and the measured correlates found (oesophageal and tracheo-oesophageal F0, jitter, shimmer, phonation time; the kinds of creak; falsetto against chest; whisper's formant ratios; vocal effort's tilt; tempo ratios). No source gives a level for forte or piano or a rate for allegro or lento: those will be `derived` from the vocal-effort and tempo studies or `estimated`.
- **Run everything under** `EVV_STAGE=C:\Users\joshk\OpenEvvBuild-ttsext\stage-dev`. The sweep: `python engine/ipa/sweep.py <sections or ids> [--apply]` (with `--apply` its settle pass re-says every passing proof made on another map; it does not see an engine or front-end change, so after one of those run the whole sweep); then `engine/ipa/register.py` and `engine/ipa/coverage.py` (`--tierb` lists every Tier B record). A whole sweep takes about 20 minutes and prints only at the end; `compose_test.py` about 45; the golden about 22. **A sweep with `--apply` now sets a failing entry back to MISSING** (seen this session: 8 went back and came back once fixed).
- **Two ways a whole sweep died this session**, both outside the engine: the harness's flake (D14, "frame log cut short") while an engine build ran beside it; and `OSError: [Errno 22]` writing a proof (OneDrive holding the file). Nothing is applied when it dies: run the sweep alone, and re-run the ids from the one it died on with `--apply`.
- **Done in the fifteenth session** (D78; read it before a new entry). The percussives ʬ ʭ ¡ and the cluck ǃ¡ are letters of their own (`airstream = "percussive"`; ǃ¡ `release = "percussive"`), made with the accent layer's new **strike** (`hit` ms after a stop's closure begins, or into any other sound; `hitms` long; `hitaf` its level on the bands `a2` to `ab`; `hitg` its gain over the parallel gains' ceiling: without the gain a strike does not show over a vowel's ringing) and **`rel2g`** (the existing second release `rel2`, louder). A percussive's closure parts with no burst (`noburst`, `vot=0`). The front-end reads a **letter of two letters** (ǃ¡) whole, after a tie bar too, and composes marks on its line. The sweep's new measures: `strike_found`/`strike_db`/`strike_centroid_hz`/`strike_ms`/`strike_len_ms` and `slap_found`/`slap_ms`/`slap_db`/`slap_len_ms`; **levels are peak against peak** (the strike's loudest 2 ms against the loudest 2 ms of the middle of the vowel after, or before at a word's end); a `_found` contrast needs one against nought; a percussive's airstream needs a `strike` target (T-percussive). Every value of the strikes of ʬ ʭ ¡ is `estimated` (nothing measured for them as speech); the slap's time (20 ms) is `literature` (wright_etal_1995). Q34 is new (latent: letter lines carry no `release`; a strike shares its bands with a fricated release). The run logs: `%USERPROFILE%\OpenEvvBuild-ttsext\sweep_d78a.log` to `sweep_d78k.log` (design rounds), `sweep_d78.log` (the whole sweep), `golden_d78.log`, `matrix_d78.log`, `matrix_d78b.log`, `compose_d78a.log`, `compose_d78b.log`, `chain_d78s.sh`.
- **Done after D78 in the fifteenth session: D79** (read it before a new fricative): h̪͆ ɦ̪͆ on `<h` with `fric` and noise bands; a letter of three characters in the front-end (`p19`) and the reader; **compare two fricatives' noise only by `centroid1k_hz` or `hf_db`** (their `centroid_hz`/`peak_hz` are read from 60 per cent of each one's own target); in the common window this engine's fricatives crowd between 3.0 and 3.8 kHz, where `hf_db` separates them by 7 dB or more. Logs: `sweep_d79a.log` to `sweep_d79e.log`, `sweep_d79.log`, `golden_d79.log`, `compose_d79a.log`, `compose_d79b.log`, `chain_d79a.sh`, `chain_d79s.sh`.
- **What was read ahead for D79** (kept for the record): the bidental fricatives h̪͆ ɦ̪͆ (Q25): Wikipedia's "Bidental consonant" (citing Ladefoged and Maddieson 1996, pp. 144-145) has the lips fully open, the teeth clenched, the tongue flat, and the sound "intermediate between [ʃ] and [f]"; "Voiceless bidental fricative" (citing the same, Trask 2004, and Ball 2024, doi:10.1080/02699206.2024.2365205, not opened) gives the Shapsug Adyghe variant of /x/ ([daːh̪͆a]). No spectrum was found. A design to try: h's layer-made breath (`<h`, the vowel's own formants: the tongue does not move) with friction whose centre is midway between this engine's ʃ (3894 Hz) and f (2920 Hz), about 3400 Hz (`derived` from "intermediate"); required contrasts with h, ʃ, f, θ, s. **h̪͆ is three characters**: the front-end and the reader know a letter of two (a letter and a mark, D74; two letters, D78) but not of three, so with a further mark (h̪͆ː) they would compose on h; extend both (the front-end's `compose()` search for a letter's own mark, the reader's `makes_letter`) before its proof, and test h̪͆ with marks in `compose_test.py`.
- **Done in the fourteenth session** (D77; read it before a new entry). The composition test (`compose_test.py`) now reads each string with the reader and compares the front-end with the adapter on that reading; `--letters` tests only the letters named, and its summary counts the letters of two it skips. **Its whole run on D77's map: 181,556 compositions compared, 0 failed** (three groups run one after another, `compose_d77_g0.log` to `g2.log`, about 70, 55 and 65 minutes; run side by side every composition failed, cause not found: run them one at a time, each under the two-hour limit on a background job). New engine key, nought by default: `fgain` (friction louder than the synthesiser's 120 dB ceiling on AF plus a parallel gain, over a voice, for a voiced definition only). New sweep measures for a nasal (or a mark on one): `band_db` (0.8 to 2.5 kHz against below 0.8 kHz) and `hnr_hi_db` (periodicity above 1 kHz). New map line: `after ᪽ ̥ ̬` (the second half of a mark of two; written by the adapter). A stand-in letter (`said_as`) may now be spelt with two characters (ʩ̬). A contrast with a composite reads its marked sound on its one base. **The human's rule stands** (memory: two symbols that should sound different must be made to differ, with a test): ʩ̬ against ʩ, 𝼀 against ʩ, 𝼀̬ against 𝼀 and ʩ̬, all `distinct`. Q33 (̬ cannot voice a whispered letter) is new; Q32 is answered. The run logs: `%USERPROFILE%\OpenEvvBuild-ttsext\sweep_d77b.log` to `sweep_d77f.log` (f: the whole sweep), `golden_d77.log`, `golden_d77b.log`, `matrix_d77.log`, `compose_d77a.log` to `compose_d77*.log`.
- **The human answered every open question on 2026-10-10** (D86, `HUMAN_ANSWERS.md`; from now on every question is asked as choices and logged there). **What is left, in this order**: (1) **the engine change before the rebuild**: Q28, Q30, Q33 (the voicing faults, each with a test), Q36 (a random jitter key; the harsh family and Œ Ю use it), Q23 (̝ on an approximant makes friction, proved on ɹ and l), Q14 (the report of a phone never placed); then the whole sweep, the golden and the engine gate. (1b) **research**: Q29 (fricated releases against affricates), Q19 (a cue of syllable division and linking). (1c) Q35 (the left/right conventions larger) and Q31 (a measure of a voiced release's friction, then 𐞞 with ɮ's F3); D85's diff in the next R15. Q27 and Q34 (2) stay as they are. (2) **The rebuild of all seven templates** from the final source (Q14's report of unplaced phones goes in), **measure each template's F5** at preset 1 and add it to `adapter.VOICE_F5` (until then only dedx speaks places; the others keep the ratios), stage them, the golden and `matrix_each`, then the **final 4i** (the whole sweep there with `--apply`, `register.py`, `coverage.py`), R15, and the pause. `docs/SOUNDS.md` must then also document `vfrom`, `vto`, `premod`, `pst`, `frel`, `frelaf`, `frelav`, `frelf2`, `frelf3`, `lmur`, `fgain`, `hit`, `hitms`, `hitaf`, `hitg`, `rel2g`, `notation extipa`/`extipa`, `after`, `reiterate`, `di`, `mono`, `mute`, the `label` and `pause` lines and the braces (D83), the `released` pairs and the affricates' `letter` lines (D84), that a mark line holds 12 keys, and that a letter may be spelt with two characters (a letter and a mark, or two letters), three or four (a letter and its own marks), or as a tied letter (ↀ͡r), and that letter lines carry `release`, `place_mark`, `aspiration`, `fricated_release` and `tongue_part`.
- **What D72 added** (read before a new mark): a mark the inventory spells only on its examples (the superscript of a fricated release) is a Tier B modifier of its own id, accepted by coverage because a record's composite names it; the layer's `frel`/`frelaf`/`frelav` (a stop released into friction on the noise bands `a2` to `ab`; a voiceless stop's voice waits for it, `release_vot`; voicing is the definition's `voi` where a mark set it, `stop_voiceless`); a mark line holds 12 keys (front-end `EVV_MAX_OPS`, and the validator refuses more: a ninth key was silently dropped before); the sweep's release measures `rel_af_ms` (frames: friction at AF 50 or more from the closure's end), `rel_hnr_db` (periodicity above 1.5 kHz in the 30 ms after it: for friction on a voice) and `rel_noise_db` (the friction's level against the vowel; a test's floor of -40 dB tells it from silence). **A lesson of D72**: on a voiced sound a noise-level measure follows the voice, not the noise (lowering the voice lowered it): judge noise on a voice by its periodicity. **Run the engine's gate under MSYS2** (`bash -l`, as the builds are): under Git Bash every probe fails to build. The runs of D72 are logged in `%USERPROFILE%\OpenEvvBuild-ttsext\golden_d72.log`, `matrix_d72.log`, `sweep_d72.log` (and `sweep_d72a` to `h` for the design rounds), `compose_d72b.log` (164,539 compositions, about four and a half hours: run detached; `compose_test.py` now reads a composed definition from the front-end's output, since its notes are cut at 200 bytes).
- **What D71 added** (read before a new mark): a level a mark changes (`voice.level_db`, `noise.gain_db`, `breath.gain_db`) is `add`, added to the letter's own offset, from 0 dB where it has none (a `set` replaced a vowel's own av and ah: the R15 review's finding); a joining mark (`kind = "tie"` with an `edit` and a transform) is judged as a mark, the joined pair against the same letters in the same syllable position (`plain_form = ".{}"`); an extIPA-only reading is `notation = "extipa"` on the entry and in its tests (the sweep declares it in that entry's map; the proof keeps the table's map's hash); the new measures `mid_db`, `noise_db`, `noise_sd_hz`, `noise_bw_hz` work on a mark's base manner, while the older per-manner measures (peak, centroid) still do not (D69's rule: for a voiced fricative base a mark's peak is the voice's harmonic, so test sibilant marks on s and ʃ). The tie split in the front-end happens only when the bare pair has no line (t͡sʰ keeps its affricate). Where two marks set one key, the one met last in canonical order is said (front-end and, in `compose_test.py`, the adapter: D71). `compose_test.py` now takes about three and a half hours (135,757 compositions): run it detached, past the two-hour limit on background jobs. The runs of D71 are logged in `%USERPROFILE%\OpenEvvBuild-ttsext\golden_d71.log`, `matrix_d71.log`, `sweep_d71.log`, `compose_d71.log`.
- **What D70 added** (read before a new mark): a mark of two characters (`after_mark`: its own line goes under its second character, shared, refused if two records want different lines there; the validator requires a last character that is a Tier A mark to carry that mark's transform); a mark written before its letter (`placement = "before"`, a `premod` line; the front-end and the reader give it to the letter after it when the letter before has no line for it); `vfrom`/`vto`; the sweep's `steady` tests and `plain_form`/`marked_form`; the voice-run measures (`voice_in_ms`, `voice_out_ms`: a consonant's span begins in the vowel before it, so its thirds cannot say where voicing was added); a mark is judged by the median of its paired differences (Q24). The runs of D70 are logged in `%USERPROFILE%\OpenEvvBuild-ttsext\golden_d70.log`, `matrix_d70.log`, `sweep_d70.log`, `compose_d70.log`. **Never run `git stash` in this tree**: this session ran it by mistake and popped it at once; nothing was lost, but another session sharing the tree would have lost its work.
- **A mark of Tier B** (D69): written like a Tier A mark (`DESIGN.md` 3.5); give a ratio in whole per cent (the map's `mod` line holds integers: 1.075 was said as 108 and `compose_test.py` failed); a mark has no manner, so a per-manner measure for it must take the base's (`base_man` in `sweep.measure`); a mark whose meaning depends on the letter is `approximate` with every reading it does not make stated. After a map change run the whole sweep and `compose_test.py` (about 45 minutes); D69's runs are logged in `%USERPROFILE%\OpenEvvBuild-ttsext\sweep_d69.log` and `compose_d69*.log`.
- **Tier B in practice** (D68): `python engine/ipa/sweep.py tierb` sweeps the section; proof files are `ipa/proofs/B_<points>.json` (`T.file_id`). In this engine a fricative's noise rides on one formant, so a noise peak and a target for that formant move together: give a new fricative values that agree, or the design rounds swing. A fricative whose noise moves a formant gets no `ant` from the adapter; ꞎ and 𝼆 carry it as an engine key of their own. Any change to the realised map makes every proof "on another map": run the whole sweep after the last map change of a session.
- **What D67 changed that a later change may disturb**: places (`l2`, `lk`) on 27 consonants; the vowel after a place starts at the place's equation applied to its own middle; ʈ against t's F2 is now reported only (by their equations they differ by less than the harness can tell); a retroflex against a non-retroflex must show a lower edge F3, required by the feature (ʈ ɖ ɽ); ɽ has an F3 target now (estimated, 1800 Hz). The place check compares the vowel after's first frame with the equation at the table's own vowel: s is at 7.8 per cent of its 8 on [u]. ꜛ's [a] syllable 2 is read from the frames (its signal has no pitch track in either version).
- **The front-end** is built from a copy (`fe\pN\frontend` + `fe\pN\src\common`) with `fe\build_fe.cmd <copy>\frontend <build dir>` and staged by copying `bin\OpenEvvFrontend.exe` to `stage-dev\x64\`. Do not restage it while a golden or a sweep runs.
- **A stopped background job can leave its children running**: after stopping a chain, list the python and bash processes (PowerShell `Get-CimInstance Win32_Process`) and stop the strays, or two sweeps write the table at once.
- **Windows tools here**: Git Bash worked. Heredocs in the Bash tool collapse `\\`, and a `"""` inside a Python heredoc ends the string: write edit scripts with the file tool. Windows Python wants Windows paths (`C:\...`), not `/tmp`. `git commit -F <file>`.
- **The level hold (D64)**, **`ant`** (D64, D66, D67), the work copy for engine builds (`build3a\openevv`, its `src/` equal to the tree's: `diff -rq --strip-trailing-cr`), one template's build (`build_in_place.sh`, about 3 minutes), the gates (`golden.py --golden docs/tts-extension/harness/golden-staged`, `matrix_each.sh <copy> c enus engb dede eses esus frfr frca itit jajp plpl`), the engine keys of D63 and D64, 32-bit renders, the `tts-ext/*` branches on GitHub: as the fifth session's notes said (D64, D65); they still hold. The chains of this session are `%USERPROFILE%\OpenEvvBuild-ttsext\chain_q21*.sh`.
- Research: 4b in REFERENCES.md "Phase 4b"; the fourth session's under "Phase 4 (fourth session)"; the sixth's (labial-velars) and this session's (the locus-equation tables re-read) under their dates.

### Phase 3, for the record

**Phase 3 (Engine capability extensions), part 3A: COMPLETE (2026-10-06)**, on branch `tts-ext/phase-3`; last commit of 3A `dd310b8` and this file's. Part 3B (the mechanisms C5, C6, C7, C10, C11) is done **inside Phase 4**, each mechanism followed at once by the symbols that need it, as the approved plan says (`DESIGN.md` 13.2, `DECISIONS.md` D35). **Next: Phase 4.** Session of 2026-10-05/06: Opus 5.5.

The defect fixes X-1 and X-2 are approved (D43) and live, with C1 in the accent layer, in the **staged** template modules only; nothing in `languages/` or `dist/` has changed. Replacing the 14 template module files and the front-end there is a separate step, shown to the human and done only with their say-so (D34 answer 4).

### Part 3A: where it stands

| Step (`DESIGN.md` 13.2, D35) | State |
|---|---|
| (a) rebuild the seven templates from unchanged source, prove the golden identical | **done** (D39): 29,237 of 29,237 cases identical in frames and sound |
| (b) try `openevv/test/matrix.sh` under MSYS2 | **done** (D37, D42): runs with `probe.exe`, `RULES=c`, one language a probe; 979 of 979 as they were on the fixed source. Not tried: `RULES=bytecode`, `probe`, `probe32` |
| (c) fix X-1, then X-2, with check A3 and the word-final and cluster golden cases; show the human what moved | **done and approved** (D38, D38a, D40, D41, D43) |
| (d) C1 to C4 and the new harness measures | **done (2026-10-06).** C1: front-end and host `0b809c0` (D44), accent layer `9e2272a` (D46). C2 reader `3b65642` (D45). C3 table, validator, adapter, the loop `3b65642` `3592b4e` `f415d0e` (D45, D47; Q13). C4 composition when speaking and IPA in `69c6dee` (D48). New measures `afd2609` (D49). The stage (`%USERPROFILE%\OpenEvvBuild-ttsext\stage`) now holds the C1 modules and the C4 front-end; the previous stage is `stage-pre-c1`. |
| (e) template comparison, with the defect fixed; choose the reference template | **done**, `7a2a01d` (D50): no template stands out, so by the design's rule the German-based **dedx** carries the proofs; the language moves the ASR error more than the template, except Indonesian (dedx 0.35, itix 0.10). Q12 fixed (D51). |
| the R15 review of the whole of 3A | **done** (D52): nine findings; eight fixed and shown by tests, one deferred (Q14). `dd310b8`. |

Small items queued for 3A: Q12 (make a template buildable without its parent, in `engine/build_modules.sh`); `docs/SOUNDS.md` must say how `vot` and `brth` now behave and document the tone key `av`, at the point the fixed modules replace the shipped ones (not before: it describes the shipped product).

### For Phase 4 (read first)

- **The tools of 3A**: `engine/ipa/` (table, reader, adapter, prove, compose_test, coverage; seed_table only once), `ipa/` (features, table, sources, aliases, realized, proofs), harness `diag.py`, `template_compare.py`, the new measures in `analysis.py` (D49; not in the golden's per-phone measures). README of the harness lists every command.
- **Measure on the stage**: `EVV_STAGE=%USERPROFILE%\OpenEvvBuild-ttsext\stage` (the C1 modules, the C4 front-end in `x64\`). Its golden is `golden-staged/` (29,237 cases, identical on these modules); `languages/`'s is `golden/`.
- **Decisions waiting**: Q13 (`vot` cannot shorten a stop's voice onset below the module's own: diagnose first; the /t/ of the C3 loop is not proved because of it), Q14 (phones never placed: report them at the next module rebuild). The 5 packs that lose IPA marks on their sentences (Georgian aspiration, Pashto) and the 65 `phone-unsounded` events in 17 packs are Phase 4/6 triage (D44, D46).
- **The reference template is dedx** (D50). Proofs: alone and in three vowel contexts on dedx; the same tests on the other six recorded, not blocking.
- `docs/SOUNDS.md` must say how `vot` and `brth` now behave, document the tone key `av` and the C4 lines (`version`, `letter`, `mod`, `weights`) at the point the fixed modules and front-end replace the shipped ones (not before).

### How to work in 3A (learned in this session)

- Build: `%USERPROFILE%\OpenEvvBuild-ttsext\build_in_place.sh <work copy> <out folder> <tags>` (run with MSYS2 `bash -l`): the loop of `engine/build_modules.sh` without its refresh of the copy. Work copy: `%USERPROFILE%\OpenEvvBuild-ttsext\build3a\openevv`, whose `src/` equals the repository's (fixed) `openevv/src`; copy a changed source file in by hand and check with `diff -rq --strip-trailing-cr openevv/src <work>/src`. Seven templates: 20 to 25 minutes. Latest fixed build: `...\build3z\modules`.
- Stage: `python docs/tts-extension/harness/stage.py <out folder> %USERPROFILE%\OpenEvvBuild-ttsext\stage` (the fixed modules; `stage-base` holds the unchanged rebuild). Measure with `EVV_STAGE=C:\Users\joshk\OpenEvvBuild-ttsext\stage`.
- Golden: `golden/` = the shipped modules (29,237 cases); `golden-staged/` = the staged fixed modules (recorded at the end of this session; check that it is committed). A full run takes 50 to 75 minutes; `--only-missing-from <folder>` renders only cases that folder lacks. A3: `a3.py`, about 45 minutes for all packs.
- **Background jobs are stopped at 2 hours**, and a stop mid-run makes the last packs fail with "front-end failed" and no message: one long run per job. The engine gate: `%USERPROFILE%\OpenEvvBuild-ttsext\matrix_each.sh <work copy> c <langs>` (about 15 minutes for ten).
- Front-end: built from the tree into a scratch copy with `%USERPROFILE%\OpenEvvBuild-ttsext\fe\build_fe.cmd <copy>\frontend <build dir>` (a copy holding `frontend\` and `src\common\`, against eSpeak NG at `%LOCALAPPDATA%\OpenEvvBuild\dev\espeak-ng`, tag `openevv-1.2.0`; the release cache's own path to a checkout is stale). `fe\base-x64` = the unchanged front-end, `fe\new-x64` = with C1. The new one is staged as `stage\x64\OpenEvvFrontend.exe`, which `engine.py` uses under `EVV_STAGE`. `dist\` is untouched.
- Heredocs in the Bash tool collapse `\\` to `\`: write edit scripts with the file tool (this broke one edit, caught by the compiler).
- The harness's known flake (D14) happened once (`ru-cl`, "frame log cut short" in 5 attempts); a re-run of that pack passed.

**The human's answers in Phase 2** (D34): TOML; the standard pass marks; Southern American English first; module files in `languages/` may be rebuilt and replaced when proven, at stated points, the differences shown first; the defect fixed first thing in Phase 3.

Phase 2 complete and the design APPROVED, 2026-10-05 (commit `7713bfc`). Phase 1 complete, 2026-10-05 (`cdcd70f`). Phase 0 complete, 2026-10-05 (`53a830d`).

BLOCKED symbols: none. (At the start of Phase 4 all 175 were `MISSING`; at its end none is, on the final stage; see the Phase 4 table above.)

## What Phase 2 did

- Read the engine again for the design, with six research helpers (accent layer, synthesiser, front-end and pack generator, native modules, wrapper, and the web), and checked by hand the findings the design leans on. The findings are in `DESIGN.md` ("The facts this design rests on"); those that correct earlier documents are in `DECISIONS.md` D30 and `ARCHITECTURE_MAP.md` 13.
- **`DESIGN.md`**: scope tiers and the coverage metric; the sound model (features, composition, fallback with a warning); the master table's format; capability gaps; the USP in this design; the pack format (TOML) and inheritance; voice against language; G2P; prosody and timing; verification; migration; keep, extend or replace for every component, and what must not change; risks and changes proposed to the phase plan.
- **`design/TRACEABILITY.md`** (written by `design/build_traceability.py`): a decision for every one of the 175 checklist entries. 109 as-is, 50 composition, 16 new mechanism; meant to end 67 mapped, 53 composed, 55 created (by rule, a letter is `created` when none of the seven IBM modules the checklist read has it as a phone of its own). Plans, not results.
- The direction, in one line: **extend, do not rewrite.** The synthesiser and the modules stay; one engine-neutral table of sounds with provenance replaces the scattered tables; an adapter turns it into what this engine reads; two defects are fixed first; twelve capabilities are to be built (four foundations, five mechanisms, three only if a measurement fails without them); the module files in `languages/` are rebuilt only at stated points, after proof, with the human's say-so.
- An independent review of the diff (R15) found the defect above, a gap in the migration plan (no place for rebuilding the template modules) and smaller things; the one re-review R15 allows found the defect described too narrowly (the breathy-release key does it too; 61 of the 87 German-template packs, not all) and a few loose ends. All fixed in the design (D33).
- Decisions D22 to D35 in `DECISIONS.md`; the Phase 2 sources and licences in `REFERENCES.md`; Q8 to Q11 and a list for Phase 3 in `OPEN_QUESTIONS.md`; the register's rules in `CREATED_SOUNDS.md`.

### Phase 2 commands and what they printed (2026-10-05)

    python docs\tts-extension\design\build_traceability.py
        entries 175 = 59 pulmonic + 11 non_pulmonic + 12 other_symbols + 28 vowels + 32 diacritics + 9 suprasegmentals + 24 tones
        decision: {'as-is': 109, 'new mechanism': 16, 'composition': 50}
        meant to end as: {'mapped': 67, 'created': 55, 'composed': 53}
        needed by (to build): {'C5': 4, 'C6': 1, 'C7': 2, 'C8': 0, 'C9': 0, 'C10': 6, 'C11': 3, 'C12': 0}
        needed only if a measurement fails: {'C5': 6, 'C6': 9, 'C7': 0, 'C8': 6, 'C9': 5, 'C10': 2, 'C11': 2, 'C12': 2}
        orphans: 0; capabilities serving no symbol: 0; equivalent pairs decided alike: yes
    head size, harness render of enus `[.1tat] (mid voiced frame, F1-F5; B1; nasal pole):
        default (50): 750 1232 2440 3600 3900; 120; 200
        `vh0:         937 1540 3050 4500 4875; 120; 200      (x 1.25)
        `vh100:       562  924 1830 2700 2925; 120; 200      (x 0.75)
    quoted phone names, evv_render dede preset 1, Annotations=1 (samples):
        `[.1aEa] 8998    `[.1aE:a] 62051    `[.1a'E:'a] 9482    `[.1ta~t] 59609    `[.1t'a~'t] 9339
    the packs (counted from languages/*/sounds.map):
        145 files; accent line with f0=own: 145; f0= keys in sound lines: 196 in 145 packs
        packs with the line "ː -": 145; with "ʲ -": 145
    accent-layer strings (EVV_ACCENT_TRACE, {A v=1) in languages/*/openevv-*.dll:
        present in 15 of 34: enus x64, and x64 + x86 of dedx engx enux esex esux frfx itix
        absent in 19: enus x86, and x64 + x86 of dede engb eses esus frca frfr itit jajp plpl
    speech-recognition error by speaking module (from harness/results/status.json; median, lowest to highest, how many at or under 0.15):
        dedx n=61 0.46 0.18-1.63 0     esex n=12 0.20 0.06-1.22 4     itix n=11 0.17 0.08-0.56 5
        frfx n=3 0.40 0.25-0.40 0      engx n=6 0.06 0.03-0.66 5      enux n=1 0.05     esux n=1 0.06
        native: enus 0.01 engb 0.00 dede 0.03 eses 0.04 esus 0.03 itit 0.01 plpl 0.09 frfr 0.12 frca 0.14 jajp 0.15

    the defect (harness renders of text, shipped modules, preset 1; frames with voicing amplitude above zero, per phone):
        ru "кто."    k=s13[0/3]  t=s11[15/21]  o=s8[34/37]  #[12/92]        ro "pta."   p[0/3]  t[0/11]  a[41/41]  #[6/86]
        ru "псы."    p=s12[0/3]  s[25/27]  y=s46[32/33]  #[12/92]            ro "taxa."  t[0/3] a[19/20] k[4/17] s[0/18] a[25/25] #[6/86]
        ru "такса."  t=s11[0/4] a=s51[30/31] k=s13[5/18] s[11/17] a=s5[16/16] #[12/92]
        final pause, voiced frames and level against the loudest 20 ms:
        hi "आप." 92/92 -7.2 dB    ru "кот." 90/92 -6.6 dB    en-us-nyc "cat." 85/96 -7.5 dB
        hi "आपा." 12/92 -21.3 dB  ru "кота." 12/92 -18.7 dB  ro "pot." 0/90 -53.6 dB  id "tidak." 0/90 -38.2 dB
    the same with the product's evv_say.exe at default settings (last 300 ms against the loudest 20 ms):
        hi "आप." -7.1 dB   ru "кот." -6.4 dB   en-us-nyc "cat." -6.8 dB   hi "आपा.", ro "pot.", dede "Kot.": digital silence
        (with this machine's own settings, PauseMode=2, the final pause is cut from the file)
    the breathy-release key (hi; s70 has brth=90, s24 is plain d):
        "दूधसा."  d=s70[28/28]  s[voiced 17/20, friction 3/20]        "दूदसा."  d=s24[28/28]  s[voiced 0/20, friction 20/20]
        "दूध."    final pause voiced 17/83                            "दूद."    final pause voiced 0/83
        friction left in the s of ru "псы.": 4/27 frames (ro "taxa.": 18/18)
    sound definitions with a vot key: in 145 of 145 packs, 930 in all (dedx 542, esex 153, itix 130, esux 51, engx 21, enux 18, frfx 15)
    sound definitions with a brth key: 196, in 145 of 145 packs
    packs whose plain p, t and k all carry vot: dedx 61 of 87 (25 none, 1 two), enux 2 of 2, engx 1 of 9, esex 0 of 21, esux 0 of 7, itix 0 of 16, frfx 0 of 3
    tone lines with the unapplied key av: cmn 4, cmn-latn-pinyin 4

Not run in Phase 2: any build, the golden regression (nothing that it guards was touched), `openevv/test/matrix.sh`.

## What Phase 1 did

A harness that replaces listening with measurement, in `docs/tts-extension/harness/` (its `README.md` has every command). Nothing in the engine, the product or the language data changed; nothing was deleted or pushed.

- **Render** (`engine.py` + `src/tools/evv_render.cpp`, a new tool): text, IPA, eSpeak NG phoneme names, a module's own annotation or the front-end's output in; a WAV plus JSON of every frame the synthesiser received and every phone the engine meant out. Optional `sounds.map` overrides. Each case in a host of its own; the engine's existing logs, no new hook. `evv_render`'s audio is byte-identical to `evv_say`'s (enus, hi).
- **Analyse** (`analysis.py`, numpy/scipy, MIT): formants (Burg LPC) and trajectories, F0 and tone contours, intensity, fricative moments and band edges, stop closure/burst/VOT, nasal antiformant and murmur, F3 minimum; and what the frames requested per phone.
- **Self-tests** (`selftest.py`): 72 of 72 pass: the analyser on synthetic signals with known answers, and every engine fact the harness relies on. Praat agrees on 24 of 24 comparisons (`praat_crosscheck.py`, the only GPL file).
- **Reference store** (`reference/ranges.json`, `reference.py`): 956 cited values from 14 opened sources (US English, German, Spanish, Portuguese, French, Dutch, Australian English vowels; VOT; English fricatives; nasals; /ɹ/; Mandarin tones). Values not found are absent. Check B uses the vowel formants (and /ɹ/'s) and the general nasal ranges; it cannot use the VOT or fricative values (means without a spread, so no range) or the tone values (no tone cases until Phase 4).
- **ASR round trip** (`asr.py`): Whisper large-v3 on the GPU; sentences from Common Voice (CC0) and Tatoeba (CC BY 2.0 FR), 142 languages. 105 scored, 50 unavailable (reasons recorded).
- **Golden regression** (`golden.py`, `golden/*.json.gz`): every phoneme every pack maps (borrowed ones too) and every native phone, 16,472 cases, metrics and hashes, not audio; fails loudly on drift, in the frames or in the sound (proven by a planted change); 15 entries it cannot render are listed, not dropped.
- **Report** (`report.py`): `LANGUAGE_STATUS.md` baseline for all 155 languages and `reports/index.html` (tables, spectrograms with requested vs measured formants, vowel charts against references).
- **Smoke check** (`smoke.py`, 6 s with facts cached) and a Stop hook script (`stop_hook.py`), not installed: `OPEN_QUESTIONS.md` Q5.
- An independent review of the diff (R15) found nine problems; the real ones were fixed (D20), among them a VOT measurement bug and a golden that could not see synthesiser changes. The one re-review R15 allows found the VOT fix incomplete and two doc claims still wrong; fixed (D21).
- Decisions D9 to D21 in `DECISIONS.md`; Phase 1 sources and licences in `REFERENCES.md`; Q5 to Q7 and two measured findings in `OPEN_QUESTIONS.md`.

## Phase 1 results in numbers (preset 1, 64-bit, 11025 Hz)

| | |
|---|---|
| Level 1 draft | 1 (qu: a vowel the engine meant, made silent) |
| Level 2 engine-verified | 150 |
| Level 4 intelligibility-verified | 4 (enus, en-us-nyc, pt, pt-br) |
| Check A (engine fidelity) | 154 of 155 pass; no substitution anywhere (A0) |
| Check B (reference ranges) | 14 languages have enough references: 4 pass, 10 fail; 137 too few (nasals only), 4 none |
| ASR | 105 scored (median CER 0.33; 25 at or under 0.15), 50 unavailable |
| Golden | 155 packs, 16,472 cases, recorded and re-run: 0 failed, every frame and every sound identical |

Findings (measured, not fixed): nine native modules speak the accent markup instead of reading it (D13); the host's 1.5 s grace sometimes kills a host before it flushes its logs (D14); IPA tone letters and phones named with `:`/`~` cannot be given to the engine directly yet (harness README, "Known limits").

## What Phase 0 did

- Tagged the start: `tts-ext-baseline` = `10542ae` (main, release 1.2.4). Branch `tts-ext/phase-0`. No engine file was changed; nothing was deleted; nothing was pushed.
- `ARCHITECTURE_MAP.md`: what the engine is (a hybrid whose every sounding part is parametric: IBM's rule machine and a Klatt formant synthesiser, an accent layer on its frames, eSpeak NG for reading text), the 62-word frame, how phonemes and languages are defined, how the 155 languages were added, the tests, 21 gaps (each confirmed by code or suspected), 10 rewrite candidates.
- Built and ran from the command line (outputs below).
- Root `CLAUDE.md` (53 lines).
- `inventory/languages.json`: all 162 pack folders = 155 languages (10 native, 145 read by eSpeak NG) + 7 hidden template modules, with every phoneme each declares or maps.
- `inventory/IPA_CHECKLIST.md` and `.json`: the whole official chart, researched by seven helpers with web sources, **175 entries (163 distinct)**, checked symbol by symbol against the human's own PDF of the chart and against Unicode. For each: codepoints, names, definition, expected acoustic correlates with sources, and what the engine does today (read from code and pack data, not measured).
- Skeletons: `DECISIONS.md` (8 decisions), `REFERENCES.md`, `OPEN_QUESTIONS.md`, `LANGUAGE_STATUS.md`, `CREATED_SOUNDS.md`. `DESIGN.md` belongs to Phase 2 and does not exist yet.

**Not done:** `.claude/settings.json` (step 4b). The app refused to let Claude write its own permission settings. The proposed content is in `OPEN_QUESTIONS.md` Q1 for the human to create or approve.

## The checklist in numbers

| Section | Entries | already | partly | absent | unknown |
|---|---|---|---|---|---|
| Consonants (pulmonic) | 59 | 30 | 29 | 0 | 0 |
| Consonants (non-pulmonic) | 11 | 0 | 11 | 0 | 0 |
| Other symbols | 12 | 2 | 7 | 3 | 0 |
| Vowels | 28 | 19 | 9 | 0 | 0 |
| Diacritics | 32 | 0 | 21 | 11 | 0 |
| Suprasegmentals | 9 | 3 | 4 | 1 | 1 |
| Tones and word accents | 24 | 0 | 22 | 2 | 0 |
| **All** | **175** | **54** | **103** | **17** | **1** |

"already" = an IBM module has the sound as a phone of its own; "partly" = said as another phone, reshaped or not, or a mechanism that covers some cases; see `DECISIONS.md` D5. Of the 477 acoustic correlates recorded, 348 come from a source a helper opened and 129 are from memory and tagged `recalled-unverified`.

## Environment

- Harness Python: venv at `%USERPROFILE%\OpenEvvBuild-ttsext\venv` (Python 3.10.11; numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.9, jiwer 4.0.0, soundfile 0.14.0, praat-parselmouth 0.4.7, faster-whisper 1.2.1, ctranslate2 4.8.2, nvidia-cublas-cu12 12.8.4.1). Not under `%LOCALAPPDATA%`: a folder the Claude app creates there is redirected into `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\` (a first venv landed there; it is unused).
- Whisper model: `%USERPROFILE%\OpenEvvBuild-ttsext\models\faster-whisper-large-v3` (3.09 GB).
- Hardware: AMD Ryzen 7 260 (8 cores, 16 threads), 31.3 GB RAM, NVIDIA GeForce RTX 5060 Laptop GPU (8 GB, compute capability 12.0, driver 572.97). Whisper runs on it in float16.
- Harness scratch: `%TEMP%\OpenEvvTests\harness` (outside OneDrive).

- Windows 11 Home 10.0.26300, 64-bit. Repository at `C:\Users\joshk\OneDrive\dev\espeakproject\OpenEvv-sapi5` (inside a OneDrive folder: tests write outside the tree for that reason).
- Visual Studio 2022 Build Tools 17.14 (MSVC x86 + x64), CMake, Python 3.10 64-bit, MSYS2 at `C:\msys64` (make, python3, both mingw-w64 GCCs), Inno Setup 6. Ninja and bash are not on PATH.
- Public integration interface: SAPI 5 (COM). Lower interface: IBM's ECI API on each module DLL.
- Engine output: 16-bit mono PCM, 11025 Hz by default; 200 frames a second.
- eSpeak NG data in `dist/espeak-ng-data` is from `joshknnd1982/espeak-ng` at tag `openevv-1.2.0`.

## Commands that were run, and what they printed (2026-10-05)

Wrapper, 64-bit and 32-bit:

    cmake -G "Visual Studio 17 2022" -A x64 -S . -B build_x64      -> configure exit: 0
    cmake --build build_x64 --config Release                         -> build exit: 0
        OpenEvvSAPI.dll 445952  OpenEvvHost.exe 337408  OpenEvvConfig.exe 535040  evv_say.exe 385024  sapi_test.exe 448512 ...
    cmake -G "Visual Studio 17 2022" -A Win32 -S . -B build_x86 ; cmake --build build_x86 --config Release
        -> configure exit: 0, build exit: 0

Engine modules from source (MSYS2 GCC, outside the repository):

    engine/build_modules.sh with TAGS='enus dedx', OPENEVV_WORK=%LOCALAPPDATA%\OpenEvvBuild-ttsext
        === enus built in 250 s
        clone: lang/dedx made from lang/dede, 1 rule files of ours, 0 edits
        === dedx built in 174 s
        exit: 0   (openevv-enus-x64.dll 9867960, openevv-enus-x86.dll 7869098, openevv-dedx-x64.dll 7970515, openevv-dedx-x86.dll 6305728)

Speaking from the command line, with the modules shipped in `languages/`:

    evv_say.exe enus 1 "The quick brown fox jumps over the lazy dog." enus.wav 64
        enus: 34045 samples at 11025 Hz, first audio 165.5 ms, 183.6 ms in all
    evv_say.exe hi 1 "नमस्ते दुनिया" hi.wav 64
        hi: 11451 samples at 11025 Hz, first audio 69.4 ms, 70.8 ms in all
    evv_say.exe (32-bit) enus 1 <same sentence> enus32.wav 32
        enus: 34045 samples at 11025 Hz      (the 32-bit and 64-bit WAV files have the same SHA-256, EEE4CA40D578ADD1...)

The existing SAPI test suite on the unchanged engine (the baseline before any change):

    build_x64\bin\Release\sapi_test.exe --out %TEMP%\OpenEvvTests\ttsext_phase0_x64
        72 passed, 0 failed      exit: 0

The front-end, asked what it tells the engine for two Hindi words with retroflex stops:

    dist\x64\OpenEvvFrontend.exe --data dist\espeak-ng-data --voice inc/hi --map languages\hi\sounds.map --text "टमाटर ठंडा"
        {A v=1 f0=own range=90 shape=1 ...}{D s71 f2=91 f3=79 f4=88 a4=52 a5=42 vot=9} ... {W .0 t=s71 @=s1^- .1 m a=s50^- .0 t=s71 @=s1^- l=s2}`[.0t@.1ma.0t@l] ...

Inventories:

    python docs\tts-extension\inventory\build_language_inventory.py
        "pack_folders": 162, "espeak": 145, "native": 10, "template": 7, "languages": 155
        "espeak_packs_by_template": dedx 87, esex 21, itix 16, engx 9, esux 7, frfx 3, enux 2
    python docs\tts-extension\inventory\build_ipa_checklist.py
        entries 175 = 59 pulmonic + 11 non_pulmonic + 12 other_symbols + 28 vowels + 32 diacritics + 9 suprasegmentals + 24 tones
        equivalent pairs 12, distinct 163; letters 107, marks 68
        engine today: {'already': 54, 'partly': 103, 'absent': 17, 'unknown': 1}
        acoustic correlates by provenance: {'literature': 348, 'recalled-unverified': 129}
        references: 112 opened, 4 named but not opened
        agrees with the PDF and with Unicode: yes

Not run: `build_all.bat`, `engine\build_modules.cmd`, the front-end build, the installer, openevv's `test/matrix.sh` (see `DECISIONS.md` D2 and `OPEN_QUESTIONS.md`).

### Phase 1 (2026-10-05), venv python, `PYTHONUTF8=1`, from the repository root

    cmake --build build_x64 --config Release --target evv_render
        evv_render.vcxproj -> ...\build_x64\bin\Release\evv_render.exe
    evv_render vs evv_say, first case, SHA-256 of the WAV:
        say_en.wav 241135d6327dad97  en/a.wav 241135d6327dad97   say_hi.wav 9f2b8cdce8bcaee5  hi/a.wav 9f2b8cdce8bcaee5
    python docs/tts-extension/harness/selftest.py
        == 72 checks, 72 passed, 0 failed          exit 0   (after the review's fixes)
    python docs/tts-extension/harness/praat_crosscheck.py
        == 24 compared, 24 agree within 5 % (F1 60 Hz), 0 differ
    python docs/tts-extension/harness/golden.py --record
        recorded 155 packs in 562 s; 0 not recorded   (then enus engb dede eses esus frfr frca itit jajp plpl again
        with the vowel frame of D17: recorded 10 packs, 0 not recorded; frca plpl jajp once more for their classes)
    python docs/tts-extension/harness/golden.py
        golden: 155 packs, 13766 cases, 0 FAILED, 0 changed within tolerance, 632 s     exit 0   (before the review)
    after the review's fixes (D20), golden.py --record, then golden.py:
        recorded 155 packs in 795 s; 0 not recorded
        golden: 155 packs, 16472 cases, 0 FAILED, 0 changed within tolerance, 882 s     exit 0
    after the re-review's fixes (D21), the final baseline, golden.py --record, then golden.py:
        recorded 155 packs in 1123 s; 0 not recorded
        golden: 155 packs, 16472 cases, 0 FAILED, 0 changed within tolerance, 1216 s    exit 0
    voiceless stops /p t k c q/ in the golden: 909 cases, 2 with a negative VOT (hyw /p t/, which its map
    sends to the module's b and d: OPEN_QUESTIONS.md), 13 with no burst found (no VOT reported)
    python docs/tts-extension/harness/golden.py enus engb dede eses esus frfr frca itit jajp plpl   (after the last re-record)
        golden: 10 packs, 416 cases, 0 FAILED, 0 changed within tolerance, 18 s
    python docs/tts-extension/harness/smoke.py
        selftest --quick: exit 0 (60 checks, 60 passed); golden --smoke: 6 packs, 28 cases, 0 FAILED; smoke: passed in 7 s
    python docs/tts-extension/harness/asr.py     (then asr.py sr, after the Serbian transliteration)
        asr: 155 languages, 105 scored, 50 unavailable
    python docs/tts-extension/harness/report.py
        levels: 1 draft: 1, 2 engine-verified: 150, 4 intelligibility-verified: 4
        check A pass: 154 of 155
        check B: pass 4, fail 10, too few references 137, no reference 4
        failure layers: {'unknown': 72, 'stress-or-tone': 8, 'phoneme values': 11}

## Licence and origin of the engine (R4: flagged, not blocking)

The engine is IBM's Embedded ViaVoice (Eloquence) rebuilt as C from its 1999 Windows objects, that is, reverse-engineered. Its authors' code is MIT. **The language data in every module is IBM's and is licensed to no one here**; who holds those rights today is in litigation (Cerence v. Microsoft and Nuance, D. Del. 1:25-cv-00553). eSpeak NG and everything derived from its phoneme tables (the front-end, its data, the packs' maps) are GPL v3 or later. The wrapper is MIT. `NOTICE.md` is the authoritative statement. For this project: new sound definitions should live in files of our own; nothing GPL or ShareAlike may be pasted into MIT files.

## Things the next phase must know

1. **Measure with the harness, not by ear.** One render: `python docs/tts-extension/harness/engine.py <tag> ipa "<IPA>" out.wav` (venv python, `PYTHONUTF8=1`, from the repository root). Before committing anything that touches synthesis or data: `golden.py` (about 10 minutes, must say `0 FAILED`); after any such edit: `smoke.py`. An intended change: `golden.py --record <tags>` and a line in DECISIONS.md.
2. **Renders depend on history**: every case is spoken in a host of its own on purpose (D11). IPA and phoneme input give the product's frames but not its noise samples (D12).
3. **The native modules other than enus do not know the accent layer's markup** (D13, `OPEN_QUESTIONS.md` Q6). Giving native languages new sounds through the accent layer would mean rebuilding them, which overwrites `languages/`.
4. **Check B is thin**: vowel references exist for a handful of languages. Most of the "level 2" languages are there for lack of references, not because they failed anything.
5. **No way in for IPA tone letters** yet (capability C2 of the design). The module phones named with `:` or `~` *can* be written, in single quotes (`'E:'`): Phase 2 measured it (D30); the harness does not do it yet.
6. The DLLs built from source in Phase 0 (`%LOCALAPPDATA%\OpenEvvBuild-ttsext`) have still not been compared with the shipped ones; the golden is of the **shipped** DLLs in `languages/`. Compare by pointing a copy of `languages/` at the built DLLs and running `golden.py`.
7. Another Claude session may share this working tree. Check `git log -3` and `git status -sb` before every commit, and commit by path.
8. This project's scratch build folder is `%LOCALAPPDATA%\OpenEvvBuild-ttsext`; `build_x64` and `build_x86` in the repository are git-ignored. `build_x64` now also holds `evv_render.exe` (`cmake --build build_x64 --config Release`).
9. **From Phase 2, for Phase 3.** Read `DESIGN.md` first: "A defect found on the way" and 4.4 (two defects to fix first), 4.3 (what to build, in order, each with its test), 11.1 (every change of behaviour is tied to a version line in the map; a listed defect's fix is the one exception and is shown and approved), 11.2 (the seven templates are first rebuilt from unchanged source and must give an identical golden; development happens in a staging data folder, never in `languages/`) and 13.2 (the proposed order). The key `f0` must stay inert in the present packs: a consonant's push on pitch gets a new key. Try `openevv/test/matrix.sh` under MSYS2 before the first change under `openevv/src`. `openevv/CLAUDE.md` binds every change there.
10. The harness venv has no TOML reader; the design's pack and table format needs `tomli` (MIT) on Python 3.10. Nothing was installed in Phase 2.

11. **From Phase 3A.** Until `b11f978` the golden silently skipped every phoneme named with `#` (D38a), so Phase 1's and Phase 2's counts of "every phoneme" were short by 2,321 map entries. The module's phone record has a voicing field (second field: 0 voiced, 1 voiceless or pause) in all seven templates (D40). The English module turns `t` before its `y` phone into `t S` (Shavian English `e@ i@ i@3`): one for Phases 4 and 6.

## Open questions

See `OPEN_QUESTIONS.md`. For the human: Q1 (the permissions file), Q5 (the Stop hook), Q7 (ASR for the 46 languages Whisper lacks), Q8 (the 32-bit US English module is older than the 64-bit one), Q9 (natural recordings to judge the recogniser by), Q10 and Q2 (pushing to GitHub), Q3 and Q4 from Phase 0. Answered in Phase 2: Q6 (module files may be rebuilt and replaced when proven) and Q11 (the defect is fixed first thing in Phase 3).
