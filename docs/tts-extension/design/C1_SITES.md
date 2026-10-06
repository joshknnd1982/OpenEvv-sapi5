# C1 "Never silent": where things are lost today

Written 2026-10-05 in Phase 3A as the starting point for capability C1 (`DESIGN.md` 4.3). **Established by a research helper reading the code; not re-run.** Four claims were checked by hand at the lines given and hold: the dropped phoneme (`frontend_main.c:482-483`), unknown keys ignored (`evv_accent.c:543-553`), spare bytes inside the result tolerated (`frontend_client.cpp:192-199`), the front-end's stderr discarded (`frontend_client.cpp:84`). Line numbers are of commit `2b2943d`, before any C1 change.

## Limits

| Where | Constant | Value |
|---|---|---|
| `frontend/src/evv_map.h:21-24, 41, 133` | `EVV_MAX_PHONES`, `EVV_PHONE_LEN`, `EVV_ID_LEN`, `EVV_ASK_LEN`, key, `EVV_WORD_MAX` | 8, 8, 12, 40, 48, 256 |
| `frontend/src/frontend_main.c:122` | `MAX_CLAUSE_WORDS` | 400 |
| `frontend/src/evv_map.c:241` | map line buffer | 1,024 bytes |
| `openevv/src/accent/evv_accent.c:105-111, 267-268, 362` | `NAME_LEN`, `ID_LEN`, `MAX_DEFS`, `MAX_TONES`, `MAX_RULES`, `MAX_PARTS`, `MAX_POINTS`, `TABLE`, `LINE_UP`, `MACHINES` | 8, 12, 384, 64, 96, 4, 8, 64, 16, 16 |

The front-end's sound and tone tables grow with `realloc`: 384 is the accent layer's limit only.

## Front-end (`frontend/src`): lost without a word

Nothing on the phoneme or map path writes to stderr; only `main()`'s command-line errors do (`frontend_main.c:835-898`).

**While translating** (`frontend_main.c`)
- 480-483: a phoneme with no map line is dropped (`if (n == 0) continue;`). 475-481: `ipa+ː` not in the map falls back to `ipa` without the length.
- 486-493: a tone the map does not name is written as no tone (`^-`); a tone when the map has no tone ids, or when `TonePhoneme()` gives nothing, is ignored.
- 229-232: past 400 words in a clause, later words merge into the last.
- 258-261, 354, 362: a vowelless word that would overflow 256 phones is dropped whole; 363, 372 with 385-386: a vowelless word with no neighbour and no `schwa` in the map is dropped.
- 374: the annotation buffer cuts silently (`put()`, `evv_map.c:666-667`). 136, 162, 175: more than 64 stretches to spell are ignored. 544: past 100,000 clauses the text is cut. 87-89, 102-104: a failed `realloc` drops output.
- 743-745: a decoder failure (539) is reported as "no voice has been set" (misleading).
- 460-462: pauses, stress marks, virtual, deleted and invalid phonemes are skipped **by design** (not a loss).

**Map lookups** (`evv_map.c`)
- 551-555: an entry is cut to 8 phones. 582-599: in left-to-right decomposition a character no key starts with is skipped (598) while the lookup still succeeds: **the main partial loss** (an IPA mark vanishes).
- 572-573: `@table:mnemonic` key cut at 64 bytes. 612-613: phones beyond 256 a word dropped; 646: a syllabic consonant with no `schwa` gets no nucleus.
- 151-158: a phone's `=sN` or a tone that no `sound` or `tone` line defines is written into `{W}` with no definition (unknown sound or tone id).
- 506-516: a question word of 40 bytes or more never matches.

**Loading the map** (`evv_map_load`, 231-455)
- 241: a line over 1,024 bytes is split and its rest read as a new entry. 384-416: an unknown keyword (a typo such as `vowel`) becomes a phoneme entry. 545, 154: duplicate keys and duplicate sound ids are shadowed.
- `copy_name` (21-25) cuts phone names to 7 bytes, ids to 11, question words to 39; `tmpl[16]` (260). `cluster` past 16 (298), `weaktones` past 16 (365) overflow silently.
- Ignored without notice: bad `secondary` (280), bad `onset` (307), a `style` other than `french` (265), `tonename` with one argument (372), `cluster` with one phone (298), `sound`/`tone` without an id (140), words holding `{` or `}` (103-104), repeated `accent` lines (315, last wins), `copy[1024]`/`all[1024]` (99, 136, 313, 328).
- Already reported through `err`: keys of 48 bytes or more, more than 8 phones, more than 64 vowels or 32 glides, no vowels.

## How a diagnostic can reach the host

- Two anonymous pipes, the front-end run with `--serve`; framing in `src/common/frontend_proto.h:26-57` (`EVV_FE_RESULT` = head, anchors, text; 8 MB at most). Writer: `serve()`, `frontend_main.c:700-769` (result at 747-762, `hh.size = sizeof(r) + alen + r.text_len`).
- Host: `frontend_client.cpp:54-110` spawns it with stderr discarded (84); `request()` 112-124 reads the header and exactly `size` bytes; `translate()` 159-204 parses. **Spare bytes inside the result body are ignored** (192, 199). A *separate* message after the result is **not** tolerated: the next request would read it as its reply and restart the front-end. So diagnostics go inside the result body, counted in `hh.size`, after the text.
- Hook: `FrontendClient::translate` after line 199 reads what lies past `sizeof head + anchor_bytes + text_len`.

## Accent layer (`openevv/src/accent/evv_accent.c`): lost without a word

- 543-553 `keys_set`: an unknown `key=value` is dropped (used by `{A}` 607, `{D}` 663, `{T}` 719); `atoi` turns a non-number into 0. 603-605: any `f0=` other than `own` turns the layer's pitch off.
- 482-495, 507-516: words cut to their buffers (64; 128 in `{T}`; 16 in `{P}`), names to 8, ids to 12.
- 651-652: past 384 definitions, dropped. 685-686: past 64 tones, dropped. 699, 704-709: past 8 tone points, or a malformed point, the rest ignored. 728-743: past 96 rules, past 4 parts, a rule with no parts: dropped.
- 827: unknown tone id in `{W}`: no tone. 833: unknown sound id: the module's own sound. 805-806: a failed `realloc` drops the rest of the word.
- 848-855: the `{P}` ending letter is not checked. 594-597: a second `{A}` resets what was read.
- 962-975: an unknown group letter, a missing `}`, or a group before `{A v=1` is spoken as text. 377-391, 945: past 16 machines the markup is spoken.
- At synthesis: 1145-1184 a phone not matched within the look-ahead (`misses++`, `known=0`); 1576 index out of range; 1275 pitch points dropped past `MAX_POINTS + 2`; 2565-2569 `LINE_UP` full.
- The trace: opened at 344-358 from `EVV_ACCENT_TRACE`; 1036-1038 `sentence:` lines; 2383-2400 one 13-column line per phone. A diagnostic line such as `diag\t<kind>\t<detail>` fits; the harness's reader skips lines with fewer than 13 columns (`engine.py`, `read_trace`), so it must be taught to read them.

## Product log and harness

- `src/common/log.h`: levels `kOff` 0, `kStandard` 1, `kFull` 2 (Standard never records what was spoken); `log::write(int lvl, const char* fmt, ...)`; files `%ProgramData%\OpenEVV\Logs\host-x64-<client>.log`, rotated at 2 MB (`log.cpp:97-109`). The host sets the level from `LogLevel` (`host_main.cpp:888-895`); existing front-end lines at `frontend_client.cpp:108, 173`; translation errors at `host_main.cpp:645, 656`.
- Harness: `engine.frontend()` captures the CLI front-end's stderr but uses it only on failure; `_run()` sets `EVV_ACCENT_TRACE` per case; `SETTINGS` has `LogLevel=0`, so host-log diagnostics would not reach the harness unless it raises the level and reads the log, or the render path forwards them.
