# TTS Engine Extension Playbook (condensed)

**Purpose:** Map every IPA symbol (plus tones and sounds) to a phoneme and acoustic specification in the TTS engine being extended (parametric/formant, concatenative, neural, or hybrid), creating new phonemes, sounds and engine capabilities wherever the engine has none, so that adding any language, dialect or accent becomes a small, data-only, automatically verifiable change.

**Two binding core requirements (R19):**
1. **Research the entire current official IPA chart** (consonants, non-pulmonic, other symbols, vowels, diacritics, suprasegmentals, tones/word accents; roughly 155 symbols, but count exactly) and record each symbol's definition and acoustic correlates with sources.
2. **Map every symbol to the engine**: phoneme, acoustic realization, tone, stress, duration, transitions. Where the engine can't produce a symbol, extend it until it can. Never skip, silently substitute, or leave a symbol silent.

**Done =** a coverage script lists every checklist symbol with its state and proof of render + measurement; nothing MISSING or BLOCKED.

**Environment:** Claude Code in the Claude desktop app (Code tab), Local environment, full tools. Applies to any engine type (original, decompiled or cloned source). Verified 2026-10-01; revised 2026-10-02.

---

## PART 0: HUMAN SETUP

**Every session:** + New session (Cmd/Ctrl+N); set before sending anything: Environment **Local**; project folder = repo containing this file; model (Cmd/Ctrl+Shift+I); effort (Cmd/Ctrl+Shift+E); permission mode (Cmd/Ctrl+Shift+M; **never Bypass**); worktree **off** for phases 0–9 (on only for parallel steady-state sessions). Then send:

> Read Part 1 of TTS_EXTENSION_PLAYBOOK.md and the Phase N section only (not the other phases), plus docs/tts-extension/PROJECT_STATE.md if it exists, then run Phase N.

Claude can't switch its own model/effort. At each phase end it stops, summarizes, and names what to switch; the human starts a new session with the new settings. If a slash command like `/model` isn't available in Desktop, use the menus (terminal: `claude --model <alias> --effort <level>`). Project memory lives in repo files (`docs/tts-extension/`), not chat. **Do not delete or archive old sessions (or enable auto-archive) until Phase 9 is done.**

| Phase | Work | Model | Effort | Permission |
|---|---|---|---|---|
| 0 | Orientation, safety net, CLAUDE.md | Fable 5.1 (`fable`) | high | Accept edits |
| 1 | Render + measurement harness | Opus 5.5 (`opus`) | high | Auto |
| 2 | Architecture design (human approves) | Fable 5.1 | xhigh | Accept edits |
| 3 | Engine capability extensions | Opus 5.5 | high | Auto |
| 4 | Master IPA → acoustic table | Opus 5.5 | high | Auto |
| 5 | Independent audit | Fable 5.1 | high | Auto |
| 6 | Packs, migration, triage | Sonnet 5.5 (`sonnet`) | medium | Auto |
| 7 | Authenticity/native validation | Opus 5.5 | high | Auto |
| 8 | Skills and automation | Opus 5.5 | high | Auto |
| 9 | Completion review | Fable 5.1 | high | Auto |

Notes: Opus 5.5 at `high` is an acceptable cheaper Phase 0. `max` effort only for single hard decisions, never a whole phase. Fable 5.1 is priciest ($10/$50 per M tokens vs $4/$20 Opus, $2/$10 Sonnet) and needs Claude Code v2.1.257+ (`claude update`). Switch model/effort only at phase boundaries (cache). If Auto isn't offered, use Accept edits; Manual defeats `/goal`.

**Rewrites are expected.** Mapping every symbol may require changing or replacing engine parts (fixed phoneme lists, fixed frame/parameter or unit/vocabulary sizes, timing models, per-language tables, G2P, language loading, voice scaling, even the synthesis core/model). Claude must say so early (Phase 0 lists candidates; Phase 2 decides keep/extend/replace, human approves); replacements are built alongside the old code behind the same interface, proven by the baseline tag, phase branches and golden regression; the public integration interface never changes (R18).

**`/goal` (optional).** After preflight Claude prints the line for the phase; paste it to run unattended. The checker only reads visible conversation, so Claude prints raw output (R16). `/goal` shows status; `/goal clear` stops it.

| Phase | Condition after `/goal ` |
|---|---|
| 0 | ARCHITECTURE_MAP.md, short CLAUDE.md, IPA_CHECKLIST.md/.json (exact count shown) exist; build command run this session with successful output shown; baseline tag exists; PROJECT_STATE.md says Phase 0 complete; Phase 0 PAUSE block printed. Or stop after 40 turns. |
| 1 | render, analysis and full-regression commands each ran with output shown; LANGUAGE_STATUS.md has a baseline for all existing languages; harness self-tests pass (output shown); Phase 1 PAUSE printed. Or stop after 60 turns. |
| 2 | DESIGN.md has all 13 numbered decisions and questions for the human were asked. Or stop after 40 turns. (Approval gate applies.) |
| 3 | every sound class in DESIGN.md's priority list is implemented with harness measurements and passing golden regression shown, or escalated with reasons; work committed; Phase 3 PAUSE printed. Or stop after 80 turns. |
| 4 | coverage output shows every IPA_CHECKLIST symbol mapped/composed/created with a rendered-and-measured test (MISSING: 0, BLOCKED: 0, Tier A unsupported: 0, counts shown); golden regression PASS; every created sound in CREATED_SOUNDS.md; Phase 4 PAUSE printed. Or stop after 80 turns. |
| 5 | AUDIT_PHASE5.md (with independent checklist re-derivation and diff) exists; every high-severity finding fixed with before/after measurements; regression PASS; Phase 5 PAUSE printed. Or stop after 60 turns. |
| 6 | all existing languages load from packs; golden regression PASS or every difference in DECISIONS.md; LANGUAGE_STATUS.md has failure-layer label + evidence for every non-passing language; Phase 6 PAUSE printed. Or stop after 100 turns. |
| 7 | target-extraction, pack-validation and review-packet commands each ran on one real example with output shown; Phase 7 PAUSE printed. Or stop after 60 turns. |
| 8 | each skill exercised on a small real task with output shown; doctor output shows all checks passing; ADDING_A_LANGUAGE.md exists; Phase 8 PAUSE printed. Or stop after 60 turns. |
| 9 | doctor, regression, coverage and harness outputs shown (coverage covering every symbol of a freshly re-researched checklist, MISSING: 0, BLOCKED: 0); both fresh-trial additions done with step counts; final report printed. Or stop after 60 turns. |

---

## PART 1: INSTRUCTIONS FOR CLAUDE (read every session)

### 1.1 Mission
Extend a TTS engine (any type) to meet the two core requirements above, then make future growth data-only. Specifically: (a) every IPA symbol, diacritic, tone and suprasegmental maps to an engine-neutral acoustic specification and a working realization; (b) any sound the engine can't produce gets a newly designed phoneme and, if needed, a new synthesis capability; (c) adding a language, authentic dialect or accent is a data-only change verifiable automatically. The human speaks only American English and can't judge other languages by ear, so correctness must be **measurable**. You cannot hear audio; never imply you can.

### 1.1b Engine-neutral terms
In Phase 0 classify the engine and record the term mapping in `ARCHITECTURE_MAP.md`.
- **Parametric** (formant, rule-based, articulatory, HMM): sound = frame parameters (formants, bandwidths, source amplitudes, noise, antiresonances, F0).
- **Concatenative** (diphone, unit selection): sound = units + selection/join/prosody rules.
- **Neural/statistical**: sound = phoneme inventory + model inputs; a new sound needs training/fine-tuning data (licensed recordings or synthetic data) and retraining.
- **Hybrid**: treat each component by its own type.

Terms: **engine-neutral acoustic specification** (target sound written once in the master table: features, formant targets, sources, noise bands, closure/burst timing, durations, transitions, F0/tone); **native realization** (engine-specific form: parameters, units, or inventory entry + data/model changes); **engine adapter** maps the first to the second; **create/extend** = new parameters/mechanisms (parametric), new units + selection/join rules (concatenative), new inventory + data + retrain (neural); the exit proof is always render + measure (R19f). Where an engine lacks a named parameter, map it to the native equivalent instead of dropping it. **Public integration interface** = whatever other software uses to call the engine (OS speech API, library API, plugin ABI, server, CLI).

### 1.2 Session preflight (before anything else)
1. Read Part 1 and only your phase section (Grep the heading, Read with offset/limit), then `docs/tts-extension/PROJECT_STATE.md` and `CLAUDE.md` if present.
2. State in one line which model you believe you are and the effort if visible; if unsure, ask the human to confirm via `/status` or the session header.
3. Compare with the phase's required model/effort. On mismatch: Phases 2, 5, 9 and any "escalate to Fable" step: **STOP** and tell the human to switch. Other phases: warn, continue only on confirmation.
4. Confirm the prior phase's exit criteria in `PROJECT_STATE.md`; if unmet, offer to finish them first.
5. TaskCreate a task list; the last task is "verify exit criteria."
6. Work on branch `tts-ext/phase-N`; commit small and often.

### 1.3 Standing rules
- **R1** Never delete or overwrite original engine code or existing language data. Add alongside; keep the legacy path until migration is proven equal. No force-push or history rewrites. (Replacement only via R18.)
- **R2** No unverified claims about sound. Every acoustic value has a provenance tag (1.5). Never invent a measured value or cite an unread source.
- **R3** Look up, don't recall: for phonetic reference data, standards, corpora, licenses and tool availability use web search/fetch and cite in `REFERENCES.md` (title, URL, access date, license, what was used).
- **R4** Record the license before importing any data or code; don't copy GPL/ShareAlike into an incompatible project; prefer measuring other engines' output over copying their data. Record the origin/license status of the engine codebase itself (esp. decompiled/reverse-engineered) in `PROJECT_STATE.md` and flag (not block on) concerns.
- **R5** Measure, then claim: "verified" only when the harness shows the engine realizes the requested parameters AND realized values fall within reference ranges.
- **R6** Compose, don't enumerate: base symbol + feature/diacritic transforms; hard-code only what composition can't express. This governs combinations beyond the chart and never excuses skipping a checklist symbol: each gets its own table entry and rendered test.
- **R7** Never silently approximate: use the USP (1.6), tag `approximate` with a plain statement of the deviation, list for native review.
- **R8** Never regress: the golden regression must pass before every commit touching synthesis or data; intentional changes are recorded in `DECISIONS.md`.
- **R9** Plain English to the human: short sentences, no unexplained jargon, a recommendation, and what you need. At most 5 questions at a time, each with a recommended default.
- **R10** Be agentic: run builds, tests, renders and measurements yourself; ask only for things only the human can do (approve a design, switch models, obtain a native speaker).
- **R11** Honest status: never mark done what failed or was skipped.
- **R12** Don't assume the OS. Determine in Phase 0 the OS, compiler, runtime and integration interface; make all scripts/tests work there.
- **R13** Context hygiene: work in chunks; when context is heavy write state to files and use the pause protocol; never rely on chat memory across sessions.
- **R14** Authenticity is documented, not asserted: variety, region, speaker group and sources recorded and status per 1.5; avoid caricature; use descriptive sources and recordings.
- **R15** Before declaring a phase done, a fresh-context subagent (sees only the diff and exit criteria) reviews and reports only correctness/requirement gaps, not style. Fix real gaps, re-review at most once. Don't chase every finding; needless abstraction/defensive code is a defect. `/code-review` suits code changes.
- **R16** Show evidence: print raw output of every check relied on (tests, regression summary, coverage table, measurements). Never write "tests pass" without the output visible.
- **R17** You're in the Desktop Code tab; the human reads chat, diffs and the Browser pane. Refer to Desktop menus/shortcuts (no terminal-only keys). Use AskUserQuestion for decisions. For visuals write an HTML/PNG file and tell them to click its path. Delegate broad exploration/research to subagents.
- **R18** Rewrites allowed under control: (a) keep/extend/replace per component recorded in DESIGN.md with coupling analysis; replacing a core synthesis component needs the human's explicit approval; (b) build the replacement alongside the old behind the same interface/adapter from a tagged baseline; (c) golden regression must show equality, or every difference shown to the human and approved in DECISIONS.md; (d) keep the public integration interface compatible; (e) retire legacy only after Phase 9 and with the human's agreement. If extension is a dead end, say so plainly with evidence and effort estimates and propose an alternative. Never rewrite silently.
- **R19** Research the whole IPA chart, then map every symbol (core requirement; overrides convenience).
  - **(a) Research:** in Phase 0 build `inventory/IPA_CHECKLIST.md` and `.json` from the *current* official chart (fetch it; record version/date, URL, license in `REFERENCES.md`), cross-checked against Unicode and one descriptive phonetics reference. Cover all sections. Count exactly and explain any difference from ~155. Per symbol: symbol, exact codepoints, official name, chart section, articulatory definition, expected acoustic correlates (cited), engine's current ability.
  - **(b) Map:** every symbol gets an explicit master-table entry resolving to something the engine synthesizes: phoneme ID or composition recipe plus, as applicable to class/engine type: formants and bandwidths (F1 upward), source types/amplitudes (voicing, aspiration, frication, burst…), noise shaping, nasal/other antiresonances, durations, onset/offset transitions, F0/tone behavior, stress correlates. Diacritics, suprasegmentals, stress marks, tone letters and breaks each map to a defined transform or prosodic control with a demonstrated effect.
  - **(c) Extend** the engine where it can't (USP 1.6, R18). Not optional, not a reason to drop a symbol.
  - **(d) As accurate as possible, honestly labelled:** if imperfect, tag `approximate`, state the deviation, queue for native review. Missing, silent, or unlabelled substitution is not acceptable.
  - **(e) No holes:** checklist symbols may end only as `mapped`, `composed` or `created`; `unsupported-with-justification` is not available (Tier B/C only). If truly impossible, escalate to Fable 5.1 `xhigh`, propose an extension/replacement under R18, and report as **BLOCKED** at the top of the next pause. The project isn't complete while any symbol is MISSING or BLOCKED.
  - **(f) Proof by rendering:** mapped only when the real engine rendered it (isolated and, where applicable, in ≥3 vowel contexts; diacritics, suprasegmentals, stress, tones applied to base sounds) and harness measurements are shown (R16).

### 1.4 Pause protocol (end of every phase)
When exit criteria are met, update `PROJECT_STATE.md` and `LANGUAGE_STATUS.md` (if relevant), commit, then output **exactly**:

> ⏸ **PHASE {N} COMPLETE. PAUSE.**
> **What got done (plain English):** {3–6 short sentences}
> **What I need from you:** {decisions, approvals, or "nothing"}
> **Next phase:** Phase {N+1}: {name}
> **Switch model to:** {Model name} (alias `{alias}`): model dropdown next to the send button (Cmd/Ctrl+Shift+I)
> **Set thinking effort to:** `{level}`: effort menu (Cmd/Ctrl+Shift+E)
> **Permission mode:** {Accept edits | Auto}: mode selector (Cmd/Ctrl+Shift+M)
> **Then:** time to start a new session for the next phase of the project, but do not delete any old sessions until the whole project is complete.
> **In the new session, paste:** `Read Part 1 of TTS_EXTENSION_PLAYBOOK.md and the Phase {N+1} section only (not the other phases), plus docs/tts-extension/PROJECT_STATE.md, then run Phase {N+1}.`

Then **stop**; don't begin the next phase. (Report any BLOCKED symbols at the top.)

**Mid-phase escalation:** same structure titled `⏸ MODEL SWITCH NEEDED`, naming the step, required model/effort, and whether to continue in this session or start a new one. Record the pending step in `PROJECT_STATE.md` first.

### 1.5 Provenance tags and status levels
**Tag on every acoustic value:** `measured` (harness on real recordings; cite IDs) · `literature` (cited source you read) · `derived` (documented rule) · `estimated` (your theory-based estimate; **must** be queued for verification) · `created` (new value/sound under USP) · `approximate` (documented deliberate deviation).

**Status levels:** 1 `draft` · 2 `engine-verified` (harness check A) · 3 `reference-verified` (check B) · 4 `intelligibility-verified` (ASR round trip passes threshold, where an ASR model supports the language) · 5 `native-validated` (named native/expert signed off the review packet, recorded in `LANGUAGE_STATUS.md`). Only level 5 may be called "authentic"; always state each language's level.

### 1.6 Unmappable Sound Protocol (USP)
1. **Normalize:** exact codepoints and intended phonetic meaning (cited).
2. **Try composition:** base + feature/diacritic transforms (voicing, aspiration, nasalization, secondary articulation, length, phonation, tone). If it works, define the transform; no new phoneme.
3. **Try feature substitution:** decompose (place, manner, phonation, airstream, secondary articulation); find the nearest realizable neighbor; note the lost feature.
4. **Capability check:** does the engine have the needed mechanism (source type, noise shaping, bursts, antiresonances, F0 control, timing; or units/inventory/model capacity)? If not, specify, implement and test a new capability (Phase 3 style), following R18.
5. **Design:** write the engine-neutral specification then its native realization from articulatory-acoustic phonetics and literature/recordings: F1–F6 and bandwidths, sources and amplitudes, noise bands, antiresonances, closure/burst timing, VOT, durations, transitions (locus/onset targets), F0. Tag each value.
6. **Implement, render, measure, iterate:** isolation and several vowel contexts; up to **5 rounds**; if still unconvincing mark `approximate`, state deviation, add to native-review queue; trigger an escalation pause if a stronger model would likely do better.
7. **Register** in `CREATED_SOUNDS.md`: symbol, codepoints, why existing sounds were insufficient, full spec, provenance, test files, status, open questions, with a never-changing **stable ID**.
8. **No holes:** every symbol ends `mapped`, `composed` or `created` (checklist symbols: only these; otherwise BLOCKED and escalated). Only Tier B/C extras may end `unsupported-with-justification` (rare; needs human acknowledgement).

### 1.7 Handoff files (`docs/tts-extension/`)
`PROJECT_STATE.md` (phase, done, decisions, open questions, next step, environment; update every phase end) · `DECISIONS.md` (dated design decisions) · `ARCHITECTURE_MAP.md` (Phase 0) · `DESIGN.md` (Phase 2) · `CREATED_SOUNDS.md` · `LANGUAGE_STATUS.md` (status level + failure-layer triage per language/dialect/accent) · `REFERENCES.md` · `OPEN_QUESTIONS.md` (things only the human or a native speaker can answer) · `inventory/IPA_CHECKLIST.md` + `.json` (drives the coverage script).

---

## PART 2: THE PHASES

Each phase prompt below is addressed to Claude. Start every phase with preflight (1.2) on branch `tts-ext/phase-N`; end with the pause protocol (1.4) naming the next phase's model/effort/permission from the Part 0 table.

### PHASE 0: Orientation and safety net
Fable 5.1 · high (Opus 5.5 high acceptable). First session; never delete it. **Change no engine behavior.** Use subagents for broad exploration.

1. Write `ARCHITECTURE_MAP.md`: language/build system; OS/compiler/runtime and the public integration interface (verify); text-to-audio flow; **engine type** and term mapping (1.1b) and synthesis model (parametric: every parameter, frame rate/update model; unit-based: unit type, inventory, selection/join rules; neural: architecture, phoneme vocabulary, inputs, training pipeline); how phonemes and languages are defined; where G2P, stress, intonation and duration live; how existing languages were added (count exactly: N) and what they share; how voices differ; existing tests.
2. Determine and actually run a command-line build; record exact commands. If it fails, diagnose and report; fix only build-environment issues, never engine logic.
3. Create branch `tts-ext/phase-0`; tag the start commit `tts-ext-baseline`; delete nothing.
4. Create a SHORT root `CLAUDE.md` (under 60 lines; only what would cause mistakes if missing): one-paragraph mission; one line each for critical rules (never delete/overwrite original code or language data; never claim to hear audio; provenance tag on every acoustic value; show raw command output; independent subagent review before each pause; run the pause protocol each phase; research the whole IPA chart and map every checklist symbol, extending the engine, per R19); build/run/test commands; handoff file list; pointer "Full rules, pause protocol and phase prompts: TTS_EXTENSION_PLAYBOOK.md Part 1."
4b. Create `.claude/settings.json` permission rules (check current permissions docs for syntax; explain in plain English first): allow the build/test/render/analysis and git add/commit commands found; deny `git push --force*`, `git reset --hard*`, recursive deletes.
5. Create skeletons for PROJECT_STATE, DECISIONS, REFERENCES, OPEN_QUESTIONS, LANGUAGE_STATUS. In PROJECT_STATE record environment, engine licensing/origin note (R4), and Phase 0 complete.
6. First-pass machine-readable inventory (under `inventory/`) of the N languages and the phonemes each uses (no quality judgments).
6b. Research the entire IPA chart (R19a) with parallel subagents, one per chart section (pulmonic; non-pulmonic; other symbols; vowels; diacritics; suprasegmentals; tones/word accents). Produce `IPA_CHECKLIST.md` and `.json`, including the engine's CURRENT ability per symbol (already synthesized / partly / absent / unknown), determined from the code and by trying the engine where possible. State the exact count, reconcile with ~155, record chart version/date/URL/license in `REFERENCES.md`. Don't map or synthesize yet.
7. In `ARCHITECTURE_MAP.md` add "gaps I already notice" (clicks, ejectives, implosives, trills, breathy/creaky phonation, tone contours, pharyngealization, etc., each marked suspected vs confirmed-by-code) and "rewrite candidates" (e.g. fixed phoneme enumeration, fixed-size frame, hard-coded per-language tables, language-bound G2P, timing model unable to express bursts/contours), each with why it blocks, coupling, dependents. Rewrite nothing.

**Exit:** engine builds/runs from CLI; ARCHITECTURE_MAP answers every item in step 1; CLAUDE.md written; baseline tag exists; inventory covers all N languages; IPA_CHECKLIST.md/.json cover every chart section with exact count; all handoff files exist. **Next:** Phase 1.

### PHASE 1: Headless rendering and measurement harness
Opus 5.5 · high. Replace the human's ears with automated, repeatable measurement. Two checks: **A (engine fidelity)**: engine realizes what was asked; **B (target correctness)**: realized sounds fall within reference ranges. For parametric/unit engines requested parameters/units are ground truth (trackers on synthetic speech are a secondary, error-prone signal). For neural/opaque engines, A verifies phoneme sequence, durations and F0 targets by forced alignment and signal measurements. State which kind of evidence each check uses.

1. CLI render tool: IPA/phoneme string (optionally text + language + voice + overrides) → WAV + JSON of what the engine actually used (frames, units, or predicted durations/F0). Add only a minimal non-invasive logging hook. Must work in this machine's real environment without the OS/service integration layer (R12).
2. Analysis tooling (Python fine; verify availability/license first, R3/R4; e.g. Parselmouth): vowels (F1–F3 midpoint + trajectories, duration), stops (closure, burst spectrum, VOT), fricatives (centroid, band edges), nasals (murmur, antiresonance), laterals/rhotics (e.g. F3), tones (F0 contours). Extensible metric set.
3. Reference-range store: JSON keyed by phoneme and variety, each value with provenance; seed from cited web research; leave unfound values empty, not guessed.
4. ASR round trip: synthesize test sentences per language, transcribe with a current multilingual ASR model (record coverage gaps), compute CER/WER; use a permissively licensed (verified) sentence set; record "ASR unavailable" rather than inventing scores.
5. Golden regression suite: store metrics (not just audio) for every phoneme used by existing languages; one command re-renders and compares within tolerance; fails loudly on drift.
6. Report generator updating `LANGUAGE_STATUS.md` with each language's status level and, for failures, a first-pass failure-layer label: phoneme values / G2P / stress-or-tone / duration-or-coarticulation / unknown.
7. Visual `reports/index.html` (tables plus spectrogram and formant-track PNGs: realized vs requested vs reference).
8. Smoke check (under ~1 minute); offer a Stop hook so a turn can't end while it fails (check hooks docs, scope to engine/data folders, explain first).
9. Run the harness over all existing languages; record results; fix nothing.

**Exit:** documented render, analysis and full-regression commands; ASR coverage gap list; LANGUAGE_STATUS.md baseline for all languages; harness self-tests (known synthetic signals with known formants prove the analyzer). **Next:** Phase 2.

### PHASE 2: Architecture design (human approves)
Fable 5.1 · xhigh (`max` only for a genuinely contested decision). STOP if not on Fable at xhigh. **No implementation.** First investigate the repo, ARCHITECTURE_MAP, IPA_CHECKLIST.json, Phase 1 results and LANGUAGE_STATUS. Write `DESIGN.md` deciding and justifying:

1. **Scope tiers:** A = every symbol in IPA_CHECKLIST.json (all must reach mapped/composed/created; no `unsupported`); B = extIPA and VoQS; C = user-defined. Define a Unicode coverage metric (e.g. U+0250–02AF, U+1D00–1DBF, U+02B0–02FF, U+0300–036F, U+02E5–02E9). The coverage script is driven primarily by IPA_CHECKLIST.json with Unicode ranges as a secondary net for B/C.
2. **Sound model:** articulatory + phonatory + airstream feature system; compositional scheme (base + transforms); affricates, double articulations, ligatures; unknown combinations use nearest-feature fallback WITH a loud warning, never a silent crash or wrong sound.
3. **Master table format:** IPA, codepoints, features, engine-neutral spec (all parameters incl. bandwidths), native realization, source types, default durations, transition rules, provenance per value, status level, test refs.
4. **Capability gaps:** for EVERY checklist symbol decide as-is / composition / new mechanism; produce a symbol-to-capability traceability table (no orphans). List classes the engine can't make (clicks, ejectives, implosives, trills, breathy/creaky/whispery, voiceless nasals, pharyngealization, nasalized vowels, tone contours/registers, ATR, etc.) and the minimum new mechanisms in priority order, each with a test strategy.
5. **USP integration:** where created sounds live, stable IDs, registry, override/promotion when better data arrives.
6. **Pack format:** human-readable, diffable (choose YAML/TOML/JSON, justify). Contents: inventory (references into master table), overrides with provenance, G2P rules, allophony/context rules, stress/tone rules, duration tendencies, intonation, metadata (variety, region, speaker group, sources, status). Inheritance: dialect/accent packs `extends` a parent and hold only differences (mergers, shifted targets, replaced rhotics, flapping/glottalization); define override semantics precisely.
7. **Voice vs language:** vocal-tract scaling, pitch range, voice quality belong to the voice; define the boundary.
8. **G2P strategy:** authoring, testing, license-checked imports (R4), irregular orthographies.
9. **Prosody/timing:** language-level vs phoneme-level.
10. **Verification pipeline:** how checks A/B, ASR, regression and native packets map to status levels; thresholds; what blocks promotion.
11. **Migration plan** for existing languages with zero regression (legacy retained until equality proven).
12. **Rewrite scope and compatibility (R18):** for EVERY component (phoneme tables, frames/unit inventory, timing model, source/noise generators or unit selection, G2P, language loading, voice scaling, synthesis core/model, public integration layer) decide keep/extend/replace with reasons, coupling map, effort, risk, safest migration order. State what must NOT change (public interface). Honestly evaluate whether a clean re-implementation of the synthesizer beats incremental extension. Any core "replace" needs explicit human approval.
13. **Risk register** and recommended phase-plan adjustments (phases 3–9 may be reordered/split with justification).

Then ask the human via AskUserQuestion at most 5 plain-English questions, each with a recommended default (file format, threshold strictness, which English varieties first); write answers to DECISIONS.md.

**Exit:** DESIGN.md complete and consistent, all 13 items, questions asked. **STOP GATE:** no normal pause until the human replies "APPROVED" (or requests changes, which you make). Record approval in DECISIONS.md and PROJECT_STATE.md, then pause. **Next:** Phase 3.

### PHASE 3: Engine capability extensions
Opus 5.5 · high. Escalate to Fable 5.1 high for any class unconvincing after 5 rounds. Read DESIGN, DECISIONS, CREATED_SOUNDS. Implement DESIGN.md's priority classes ONE at a time; every checklist symbol the engine can't yet realize must be covered by some class (R19c); none dropped for being hard. Typical order (follow DESIGN.md if different): (a) full pulmonic coverage (affricates, trills, taps, laterals, uvular/pharyngeal/epiglottal, retroflex, labiodental/other); (b) secondary articulations; (c) phonation types (breathy, creaky, whispery, voiceless nasals/vowels); (d) airstream mechanisms (ejectives, implosives, clicks); (e) tone/F0 control (levels, contours, registers, Chao numerals/tone letters); (f) nasalized vowels, ATR, rhoticity, length/overlength; (g) anything else in DESIGN.md.

Per class: (1) write the acoustic spec (USP step 5) with provenance; research via web, cite in REFERENCES.md. (2) Implement per DESIGN.md; prefer additive, parameter-driven changes; keep legacy behavior bit-for-bit unless DECISIONS.md says otherwise (R8). For "replace" components follow R18 (alongside, switch only when regression equals or differences are approved, keep old in tree). If an unplanned replacement turns out to be necessary, stop, record it, tell the human in plain English, and get approval first if it touches the synthesis core. (3) Extend harness metrics if missing (extend, don't replace). (4) Render in isolation and ≥3 vowel contexts, measure, compare to references, iterate ≤5 rounds. (5) Run full golden regression; must pass. (6) Record results, deviations, status; register created sounds. (7) Commit.

If a class stays unconvincing after 5 rounds: mark approximate, record what's wrong in OPEN_QUESTIONS.md, write the pending step to PROJECT_STATE.md, and issue MODEL SWITCH NEEDED recommending Fable 5.1 high for that class.

**Exit:** every priority class implemented and measured, or approximate/escalated with reasons (escalated classes must be resolved before Phase 4 ends, never dropped); every checklist symbol's capability need traceable to an implemented/escalated class; regression passes; harness extended; PROJECT_STATE lists exactly which classes are done. **Next:** Phase 4 (schedule any escalations first).

### PHASE 4: Master IPA → acoustic table
Opus 5.5 · high. Read DESIGN, CREATED_SOUNDS, REFERENCES and IPA_CHECKLIST.json (the worklist: every record mapped). Build the master table in DESIGN.md's format, in chunks (commit and run the harness after each): 4a pulmonic consonants; 4b non-pulmonic; 4c vowels (cardinal and non-cardinal, rounding, ATR); 4d diacritics as composable transforms; 4e suprasegmentals, stress, tone letters, Chao numerals, tone diacritics; 4f Tier B extIPA and VoQS; 4g affricates, double articulations, ligatures; 4h resolve every remaining hole via USP (extending the engine again if needed, R18); 4i symbol-by-symbol sweep: render EVERY checklist symbol with the real engine (isolated and ≥3 vowel contexts; diacritics/stress/length/breaks/tones applied to base sounds), measure, and record the test file and result against its checklist record.

Per entry: IPA, codepoints, features, engine-neutral spec and native realization, sources, durations, transitions, provenance per value, status, test ref. Prefer `literature`/`measured`; `estimated` only if nothing better, and queue every one in OPEN_QUESTIONS.md. Never invent a citation.

Write a coverage script driven by IPA_CHECKLIST.json printing per symbol: state (mapped/composed/created/MISSING/BLOCKED), engine phoneme ID or recipe, whether a rendered test and measurement exist, provenance, status; plus the Unicode metric as a secondary net. At exit MISSING = 0, BLOCKED = 0 (or each listed at the top of the pause), Tier A unsupported = 0; list any Tier B/C unsupported for human acknowledgement. Print summary counts (total, mapped, composed, created, rendered-and-measured) to compare with the Phase 0 exact count. Check A must pass for all new entries; Check B where references exist.

**Exit:** zero MISSING/BLOCKED; mapped+composed+created equals the Phase 0 checklist count; every symbol has a rendered, measured test; every created sound in CREATED_SOUNDS.md with stable ID; legacy golden regression passes; estimated values in OPEN_QUESTIONS.md; PROJECT_STATE updated. **Next:** Phase 5.

### PHASE 5: Independent audit
Fable 5.1 · high (STOP if not on Fable). You didn't build this; be skeptical. Produce `AUDIT_PHASE5.md` (findings only) first, then fix in a second pass. Script what can be scripted:

1. **Consistency:** formant ordering/spacing follows articulatory logic (height~F1, backness~F2, rounding lowers F2/F3); symmetry across places; voiced/voiceless pairs differ only where they should; duplicates/near-duplicates under different symbols; plausible nasal/lateral/rhotic signatures.
2. **Literature:** spot-check ≥40 entries across all sections against sources you fetch yourself; report numbers.
3. **Provenance honesty:** `literature`/`measured` without a real REFERENCES entry is a defect; `estimated` presented as fact is a defect.
4. **Composition:** sample 100 composed sounds, render, measure; confirm the change from base is in the intended direction.
5. **Created sounds:** check each CREATED_SOUNDS entry against the literature; re-render/re-measure; keep/revise/mark approximate.
6. Rerun coverage: still zero MISSING.
7. **Harness sanity:** try to find a case where a wrong sound still passes; add a test that catches it.
8. **Checklist completeness:** independently re-derive the checklist from the current official chart (don't treat the Phase 0 file as ground truth), diff against IPA_CHECKLIST.json, confirm every symbol has a rendered, measured entry; measure-check ≥30 diacritic/stress/length/break/tone entries for intended effect. Any missing, silent, or unlabelled-substituted symbol is high severity.

Rank by severity; fix all high-severity; track the rest in OPEN_QUESTIONS.md; rerun regression and harness; update statuses honestly. **Exit:** audit complete; highs fixed and verified; regression passes; PROJECT_STATE updated. **Next:** Phase 6.

### PHASE 6: Packs, migration, triage
Sonnet 5.5 · medium; escalate hard languages to Opus 5.5 high (Fable 5.1 high for tonal/click/heavy-allophony). Read DESIGN (pack format, inheritance, migration) and LANGUAGE_STATUS.

**Part 1, migrate:** implement the pack loader (with `extends` and override semantics) and migrate existing languages. Legacy path stays until the golden regression proves equality (R1, R8, R18); intentional differences go to DECISIONS.md and are shown to the human; delete no legacy code. Migrate in batches of ~10, harness and commit after each. After the loader and ONE pilot language are proven, you may parallelize independent languages with subagents (or tell the human to use `/batch`), each in its own worktree, each running the regression and reporting numbers; merge one batch at a time and rerun the full regression after each. Master table and engine stay single-threaded.

**Part 2, triage:** for every language, using the harness (A/B, ASR where supported), assign a failure layer (phoneme values / G2P / stress-or-tone / duration-or-coarticulation / unknown) with evidence; update LANGUAGE_STATUS; write a prioritized fix list grouped by shared root cause. Never claim a language "sounds right," only status levels. Languages needing deeper phonetic reasoning (tonal, clicks, heavy allophony/sandhi) go under "Needs escalation" in PROJECT_STATE with reasons rather than guesses.

**Exit:** all languages load from packs; regression passes or differences documented; failure-layer + evidence for every non-passing language; prioritized fix list and "Needs escalation" list written. **Next:** Phase 7.

### PHASE 7: Authenticity and native-validation pipeline
Opus 5.5 · high. Read DESIGN (verification), REFERENCES, LANGUAGE_STATUS. Take a language/dialect/accent from `draft` toward `native-validated`:

1. **Reference data discovery:** check (verify existence, coverage, license; assume nothing) Common Voice, FLEURS, PHOIBLE, Glottolog, UCLA Phonetics Lab Archive, IDEA, plus descriptive grammars/archives; record all findings in REFERENCES.md, including unusable ones.
2. **Target extraction:** script + doc: from licensed recordings with known speaker region/background, use forced alignment (check current tools/licenses/language coverage, e.g. Montreal Forced Aligner) and the harness analyzer to measure vowel targets, consonant properties, durations and F0 per class; write into pack overrides tagged `measured` with recording IDs; state sample-size minimums and flag results below them.
3. **Speaker normalization:** implement/document so measured targets are comparable; the voice, not the pack, carries speaker scaling.
4. **Authenticity metadata:** every dialect/accent pack records target variety, region, speaker group, sources, recordings, date, status; a validator rejects packs missing fields.
5. **Native review packet generator:** self-contained folder per language/dialect/accent: audio (words, sentences, minimal pairs, plus sounds flagged created/approximate/estimated), IPA and orthography, a plain-language reviewer checklist (understandable? vowel like X or Y? too buzzy/breathy/harsh? least natural sentences?) and a feedback template. A command ingests completed feedback into LANGUAGE_STATUS.md, updating status only when a named reviewer and date are recorded. Also build each packet as a single `index.html` with embedded audio players and spectrogram images (audio playback in the Browser pane isn't guaranteed; images are what the human can use).
6. Write a short practical doc on finding native reviewers (communities, university linguistics programs, forums); contact no one on the human's behalf.
7. **Anti-caricature:** forbid exaggerated stereotyped features; every dialect-specific rule must cite a descriptive source or measured data.

**Exit:** pipeline demonstrated end-to-end on ONE real example (an English variety if possible; otherwise whatever is licensable, said plainly); validator rejects incomplete packs; packet generator works; PROJECT_STATE updated. **Next:** Phase 8.

### PHASE 8: Skills and automation
Opus 5.5 · high.
1. Check the CURRENT Claude Code docs for skills and subagents (fetch; don't rely on memory). Create `.claude/skills/<name>/SKILL.md` for add-language, add-dialect, add-accent, improve-language, diagnose-language, create-missing-sound. Frontmatter: `name`, `description`, `disable-model-invocation: true`, and recommended `model`/`effort` from Part 3 if the docs confirm those fields (else put them in the body). Use `$ARGUMENTS` for the name (e.g. `/add-language Swahili`). Keep each short and self-contained, pointing to CLAUDE.md, DESIGN.md and harness commands.
1b. Create `.claude/agents/tts-reviewer.md` (tools Read, Grep, Glob, Bash; model opus) implementing the R15 review (check against exit criteria and status-ladder honesty; report only correctness/requirement gaps). Every skill's last step calls it.
2. Write root `ADDING_A_LANGUAGE.md`: plain-English guide for the human and any Claude model, with one complete worked language, one dialect (inheritance) and one accent example that actually run; exact commands for render, measure, regress, review-packet; status ladder; common mistakes.
3. Add a `doctor` command: environment ok, harness runs, golden regression passes, coverage reports zero MISSING/BLOCKED across the whole checklist, every pack validates, no stale `estimated` values past a threshold without queued verification.
4. Exercise each skill on a small real task (e.g. a tiny test dialect extending an existing language; a test language with a few words); remove or clearly mark test artifacts without deleting anything the human created.
5. Update CLAUDE.md so future sessions know the skills and doctor exist.

**Exit:** skills exist and were exercised; guide's examples run; doctor passes; PROJECT_STATE updated. **Next:** Phase 9.

### PHASE 9: Completion review
Fable 5.1 · high (STOP if not on Fable). You didn't build this; verify by running things, not by reading summaries.
1. Run doctor, golden regression, coverage and the full harness; report raw results.
2. **IPA coverage:** re-research the current chart yourself, rebuild the checklist, diff against IPA_CHECKLIST.json; run coverage and a fresh render-and-measure sweep: every symbol mapped/composed/created and renders; zero MISSING, BLOCKED, Tier A unsupported. List Tier B/C unsupported items, created sounds with status levels, and approximate/estimated items.
3. **Ease of extension:** two fresh trials following ONLY ADDING_A_LANGUAGE.md and the skills: (a) add a brand-new language not in the repo (accessible reference material); (b) add a new dialect pack extending an existing language. Record steps and human decisions needed; fix unclear docs.
4. **Honest status table** of all languages/dialects/accents by level (1.5); state plainly that anything below `native-validated` is NOT confirmed authentic; list the top 10 items for native review.
5. **Rewrite/legacy report (R18):** every replaced/rewritten component, why, regression evidence of preserved sounds (or approved differences), whether legacy remains. Ask the human whether to retire any legacy code; retire nothing without a yes.
5b. Residual risks and recommended next improvements.
6. Final PROJECT_STATE update: "Project complete" only if every exit criterion of Phases 0–8 is verified true; otherwise list exactly what remains and which phase prompt to re-run, with model and effort.

If complete, tell the human in plain English: the project is complete; they may now delete old sessions if they wish; how to start each Part 3 workflow (one-line starters); the best next investment is native-speaker review packets for highest-impact languages. If not, pause for the phase to redo.

---

## PART 3: STEADY-STATE WORKFLOWS (after Phase 9)

One language/dialect/accent per session; each starts with preflight (1.2). If the running model/effort differs from the one required, say so before starting. Each is also a slash command after Phase 8 (`/add-language Swahili`). Parallel work: one session per language with worktree on; pack-only changes merge cleanly; master table/engine changes (workflow E) one session at a time.

**Short model-switch pause:**
> ⏸ **MODEL SWITCH NEEDED.** Step: {name}. **Switch model to:** {model} (`/model {alias}`). **Set thinking effort to:** `{level}` (`/effort {level}`). Pending step recorded in `PROJECT_STATE.md`. Start a new session and paste: `Read CLAUDE.md and docs/tts-extension/PROJECT_STATE.md, then continue the pending step.`

**A. Add a language** (Sonnet 5.5 medium; Opus high for hard phonology; Fable high for tonal/click/heavy-sandhi). Starter: `Add the language <NAME> (<ISO>). Follow ADDING_A_LANGUAGE.md and the add-language skill.`
1. Research: inventory, phonotactics, stress/tone, orthography-to-sound rules, reference recordings and licenses; cite; say what you couldn't find.
2. Map every phoneme to the master table; for gaps run USP; if a new capability is needed or 5 rounds fail, MODEL SWITCH NEEDED to Fable high.
3. Write the pack (inventory, G2P, stress/tone, durations, intonation, authenticity metadata); tag provenance on every value.
4. Run harness: A, B, ASR (or note unavailable), regression for all existing languages.
5. Generate the review packet; update LANGUAGE_STATUS with the TRUE level and failure-layer notes.
6. Plain-English report: what was done, level, which sounds are created/approximate/estimated, what a native reviewer should check first.

**B. Add an authentic dialect** (Sonnet medium; Opus high for large vowel shifts/many allophone rules). Starter: `Add the dialect <NAME> of <PARENT LANGUAGE>. Follow the add-dialect skill.` The pack `extends` the parent and contains ONLY differences.
1. Define the variety precisely (region, speaker group, era); find descriptive sources and licensed recordings (R3, R4, R14); if none, say so and mark everything `estimated`.
2. List differences (mergers/shifts, consonant realizations, allophone rules, stress/rhythm, intonation, lexical sets), each with a source or measurement; no caricature.
3. If recordings exist, run the Phase 7 extraction for `measured` overrides.
4. Write, validate, run harness plus the parent's regression (parent unaffected).
5. Generate review packet; update LANGUAGE_STATUS.
6. Report in plain English which claims are measured vs estimated.

**C. Add an authentic accent** (Sonnet medium; Opus high for accents transferring a whole phonological system). Starter: `Add the <ACCENT> accent of <TARGET LANGUAGE>. Follow the add-accent skill.` An `extends` pack on the target with substitutions and rule changes (substituted phonemes, devoicing, epenthesis, stress/rhythm, intonation).
1. Define the accent (speaker group, first language, proficiency if relevant); find descriptive sources and licensed recordings; cite.
2. Build the substitution map and rules, each sourced or measured; map sounds outside the target language via the master table (USP if a gap).
3. Write, validate, run harness and parent regression; generate packet; update LANGUAGE_STATUS.
4. Plain-English report; flag anything stereotyped or weakly sourced for removal.

**D. Improve an existing language** (Opus 5.5 high). Starter: `Improve the language <NAME>. Follow the improve-language skill.`
1. Start from LANGUAGE_STATUS failure layer and evidence; rerun the harness to confirm the baseline.
2. Fix at the identified layer only; if the cause is shared, fix once in the master table/engine, not per language.
3. After each change re-measure the language, then run the full regression; never trade one language's fix for another's regression (R8).
4. Update provenance and status; regenerate the packet; record before/after numbers in LANGUAGE_STATUS.
5. If two fix rounds don't move measurements, MODEL SWITCH NEEDED to Fable high.

**E. Create a missing sound** (Fable 5.1 high; xhigh for a new synthesis mechanism). Starter: `Create the missing sound <IPA symbol or description>. Follow the create-missing-sound skill.` Run the USP (1.6) in full: normalize → composition → feature substitution → capability check → design → implement/render/measure/iterate (≤5 rounds) → register in CREATED_SOUNDS.md with stable ID → full regression. Cite sources, tag provenance, state plainly if `approximate` and how, add a packet entry for native listeners, report in plain English.

**F. Diagnose a language that sounds wrong** (Opus 5.5 high). Starter: `Diagnose why <NAME> sounds wrong. Follow the diagnose-language skill. Symptom: <reviewer's words>.`
1. Turn the symptom into hypotheses by layer: phoneme values, G2P, stress/tone, duration/coarticulation, voice/speaker scaling, engine bug.
2. Design and run measurements that distinguish them; report numbers.
3. Name the most likely cause with evidence and confidence; propose a fix but don't apply it until data supports the diagnosis (then follow D).
4. Plain-English report: what's wrong, confidence, what fixing would touch.

---

## APPENDICES

**A. Launch (terminal alternative):** `claude --model fable --effort xhigh` (Phase 2, workflow E new mechanisms) · `--model fable --effort high` (Phases 0, 5, 9, E) · `--model opus --effort high` (1, 3, 4, 7, 8, D, F) · `--model sonnet --effort medium` (6, A, B, C). Terminal: `/model fable|opus|sonnet`, `/effort low|medium|high|xhigh|max`. Pin exact versions with `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5`. Haiku 4.5 is deliberately unused (no effort control, too weak for acoustic reasoning).

**B. Honesty limits:** (1) Claude cannot hear; it can measure. (2) Matching references proves *plausible*, not *authentic*; only `native-validated` means authentic. (3) `estimated`, `created` and `approximate` values are hypotheses awaiting verification.

**C. Directory layout:** `CLAUDE.md`, `TTS_EXTENSION_PLAYBOOK.md`, `ADDING_A_LANGUAGE.md` (Phase 8), `.claude/skills/` and `.claude/agents/` (Phase 8), `docs/tts-extension/` (PROJECT_STATE, DECISIONS, ARCHITECTURE_MAP, DESIGN, CREATED_SOUNDS, LANGUAGE_STATUS, REFERENCES, OPEN_QUESTIONS, AUDIT_PHASE5, `inventory/IPA_CHECKLIST.md|json`).

**D. Troubleshooting (Claude-relevant):**
- Named model unavailable or request fails: `claude update` (Fable 5.1 needs v2.1.257+, Opus 5.5 v2.1.280+, Sonnet 5.5 v2.1.284+). If still unavailable, say so and recommend the nearest model (Fable → Opus 5.5 xhigh; Opus → Sonnet 5.5 high; Sonnet → Opus medium) and log the substitution in DECISIONS.md.
- Model swapped automatically: safety classifiers can re-run flagged requests (occasionally on decompiled/reverse-engineered code) on a fallback model with a transcript notice; if early, try `claude --safe-mode`, or turn off auto-switching in `/config`. Preflight (1.2) should catch a wrong model.
- Context filling mid-phase: write state to PROJECT_STATE.md and issue a pause.
- Engine builds only on one OS: run the Local session on such a machine; scripts must work there (R12). Windows: Desktop reads user/system env vars, not PowerShell profiles; install tools system-wide and restart; Git needed for worktrees; use WSL if the engine builds under Linux (no @mentions/plugins in WSL).
- Exit criteria fail: don't pause for the next phase; report and fix or escalate.
- Plan change: edit DESIGN.md in a Fable xhigh session; log in DECISIONS.md first.
- `/goal` stuck: `/goal` shows the checker's reason; `/goal clear` stops it.
- Check CLAUDE.md loaded: ask Claude to quote the critical rules.

**E. Desktop tips:** side chat (Cmd/Ctrl+; or `/btw`) for questions; Esc stops, Enter queues a correction (after two repeated corrections, write state to handoff files and start a fresh session); Esc twice or `/rewind` undoes only file-edit-tool changes, so small git commits (R1) are the real safety net; Ctrl+O cycles Normal/Thinking/Verbose; the usage ring shows context and plan usage; Fable 5.1 may bill to usage credits (consent asked first); HTML reports open in the Browser pane by clicking their path; parallel sessions only in steady state with worktrees (use `.worktreeinclude` for needed gitignored files); old sessions are a safety net until Phase 9 completes.
