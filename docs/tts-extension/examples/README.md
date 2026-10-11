# Worked examples and skill tests: TEST ONLY, never shipped

Everything in this folder is a test. Nothing here is in `packs/` or `languages/`, the installer never
sees it, and no language's status in `LANGUAGE_STATUS.md` comes from it. Every tag carries a
private-use subtag (`-x-evvdemo...` for the worked examples of `ADDING_A_LANGUAGE.md`,
`-x-evvskill...` for the packs the Phase 8 skill exercises made), and every pack says "TEST" in its
name and notes.

The pack tools find these packs only when `EVV_PACKS_EXTRA` names `docs\tts-extension\examples\packs`
(`engine/packs/packlib.py`); `engine/doctor.py` validates them on every run.

| Folder | What | Made by |
|---|---|---|
| `packs/sw-x-evvdemo/` | a language: Swahili made again from its eSpeak NG voice | `ADDING_A_LANGUAGE.md` section 3 |
| `packs/ca-va-x-evvdemo/` | a dialect that inherits from Valencian, two vowel overrides from jimenez2019 | section 4 |
| `packs/en-us-x-evvdemo-es/` | an accent: one measured vowel of Mexican Spanish speakers of English (sidaras2009) | section 5 |
| `packs/*-x-evvskill*/` | the skill exercises of Phase 8 (`DECISIONS.md` D92) | the skills, run by test helpers |
| `packets/<tag>/` | their review packets (the loose audio and pictures are git-ignored; `index.html` embeds them) | `engine/review/make_packet.py --out` |

Their review keys (which A/B version carries an override) are in `docs/tts-extension/review/keys/<tag>.json`
like every packet's. The project's rule (playbook R20) is that nothing is deleted before Phase 10 is
complete; Phase 11 may remove these, item by item, with the human's yes.
