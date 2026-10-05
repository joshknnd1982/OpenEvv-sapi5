# Created sounds

The register of every sound designed under the Unmappable Sound Protocol (playbook 1.6, step 7). **Empty: no sound has been created yet.** Phases 0 to 2 map and synthesize nothing.

## How the register works (decided in Phase 2: `DESIGN.md` section 5)

- A created sound's specification is not kept here. It is an entry of the master table (`ipa/table/*.toml`) like any other sound, with `state = "created"`. This file is the register that points at it.
- **Two ids, neither ever changes.** The *key* is the symbol's code points, as in the checklist (`U+01C3`); a sound with no code point of its own is keyed `X-<name>`. The *register number* is `CS-0001` onward: given once, never reused, never renumbered, and kept even when the sound is later superseded.
- **Revision** counts changes to the specification. Every change moves the golden regression for the packs that use the sound, so it is listed in `DECISIONS.md` before it is committed.
- **Status** is the playbook's level (1 draft to 5 native-validated), plus `approximate` with the deviation stated where the five design rounds did not get there.
- A sound that a later mechanism lets the engine compose instead stays in the register, marked superseded.

**Which sounds are "created" is a rule, not a judgement** (`DESIGN.md` 4.1): a letter that none of the seven IBM modules the checklist read has as a phone of its own is created (Canadian French, Japanese and Polish were not consulted, so the list can only become shorter), because its sound is designed here from the literature, whether it needs a new mechanism (the clicks) or only the engine's present keys (ʈ, which is t with its formants moved). So are the four controls the engine lacks today. A letter some module has is `mapped`; a base plus a general rule is `composed`; neither is registered here.

Planned by `design/TRACEABILITY.md`, none started: 55 entries. 51 letters (29 pulmonic consonants, the five clicks, eight of the "other symbols", nine vowels) and 4 controls (downstep, upstep, global rise, global fall).

## Register

| Register no. | Key | Symbol | Code points | Why existing sounds were not enough | Specification (master-table entry) | Provenance | Test and proof files | Status | Revision | Open questions |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |
