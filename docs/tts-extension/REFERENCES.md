# References

Every outside source this project has used: title, URL, access date, licence, what was used (R3). Record the licence before importing anything (R4). Nothing here has been copied into the repository; charts and tables are cited, and facts are written in our own words.

## The IPA chart (the standard the checklist follows)

| | |
|---|---|
| Title | The International Phonetic Alphabet (the IPA chart) |
| Publisher | International Phonetic Association |
| Version | The issue marked "© 2026 IPA", footer "IPA Chart revised to 2015/2005". The IPA's chart page says the 2018 and 2020 issues were this same revision and that the chart has been re-issued every year since 2025 with the year updated. The last change of a symbol was in 2005 (the labiodental flap ⱱ added). |
| URL | <https://www.internationalphoneticassociation.org/content/ipa-chart> (PDF: `.../IPAcharts/common_files/pdfs/pdfs_IPA_charts_E/IPA_Kiel.pdf`) |
| Accessed | 2026-10-05 |
| Licence | Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0), © International Phonetic Association |
| Local copy | `IPA_Kiel.pdf` in the human's Downloads folder, 603,341 bytes, SHA-256 `C8203013C676B243959072234526D60B874851D0509A00FD7528F4E56C706787`. Not in the repository (ShareAlike). Its text layer is in a legacy 8-bit font and cannot be read as text; the rendered page was read by eye. |
| Used for | Which symbols exist, in which section, with which label: the contents and the count of `inventory/IPA_CHECKLIST.md`. |

Cross-checks: the IPA's own number chart, symbol list and interactive-chart data (same site); the Unicode Character Database 18.0.0 (`UnicodeData.txt`, `NamesList.txt`, <https://www.unicode.org/>, Unicode licence) for every codepoint and character name, and Python 3.10's `unicodedata` (Unicode 13) again when the checklist is built; Wikipedia, "International Phonetic Alphabet" and "IPA number" (CC BY-SA 4.0), for IPA numbers and for the sentence "107 letters ... 31 diacritics ... 17 additional signs" used to reconcile the count.

## Descriptive phonetics sources for the acoustic correlates

116 sources, listed one by one with URL, licence, whether the source was actually opened, and what it was used for, in **`inventory/IPA_REFERENCES.md`** (generated from `inventory/research/*.json`). 112 were opened and read in this phase; 4 were not opened and are named only because an opened source quotes them. Two of those matter: the vowel formant values of Catford (2001) and of Peterson & Barney (1952) are in 25 vowel correlates **as quoted on an opened page** (Wikipedia's "Formant" article and a Princeton course page), and the checklist marks each one "as quoted there, not opened". Read the originals before any of those numbers becomes a target. Each correlate in the checklist names the sources it came from; a correlate with no opened source is tagged `recalled-unverified` and must be verified before any value is taken from it.

## Tool documentation

| Title | URL | Accessed | Licence | Used for |
|---|---|---|---|---|
| Claude Code documentation, "Configure permissions" | <https://code.claude.com/docs/en/permissions> | 2026-10-05 | Anthropic documentation | The syntax of permission rules for `.claude/settings.json` (see OPEN_QUESTIONS.md, Q1) |

## Sources already cited inside the repository (not re-read in Phase 0)

These are named by the existing code and documents as the origin of numbers already in the product. They were **not opened in Phase 0** and are listed so that later phases know what to read before relying on them.

| Where it is cited | What it names |
|---|---|
| `engine/accent/sounds.py:48-64` (`VOWEL`) | Peterson & Barney 1952; Hillenbrand et al. 1995; Catford 1988 |
| `engine/accent/sounds.py:118-123` (`LOCUS`) | Delattre, Liberman & Cooper 1955; Stevens 1998; Ladefoged & Maddieson 1996 |
| `engine/accent/sounds.py:128-133` (VOT) | Cho & Ladefoged 1999; Lisker & Abramson 1964 |
| `engine/accent/sounds.py:91` (`LENGTH`) | Lehtonen 1970; Fatima & Aden 2003 |
| `engine/profiles/<tag>.json` (`sources`) | per-language literature, 145 profiles |

## Software and data in the repository, with licences (see `NOTICE.md`, which is authoritative)

| What | Licence |
|---|---|
| openevv engine code (`openevv/src`, tools, tests) | MIT, © 2026 Stanislaw Przedzinkowski; additions here MIT |
| Language data (`openevv/lang/`, module DLLs in `languages/`, `klatt_tables.c`, `eci_xmltok_tables.c`) | IBM's; **not licensed here** |
| eSpeak NG, `frontend/`, `dist/espeak-ng-data`, the packs' `sounds.map`/`phonemes.map` | GPL v3 or later |
| The wrapper (`src/`, `engine/`, `installer/`) | MIT, except the BestSpeech-derived SAPI files listed in `NOTICE.md` |
| Community dictionary (`dictionaries/community/`) | CC0 1.0 |
