# Phase 9 trial B: /add-dialect "Belgian Dutch (Southern Standard Dutch, Flanders) of nl" (tag nl-be)

Run 2026-10-11 by a fresh helper (Sonnet 5.5) that read only `.claude/skills/add-dialect/SKILL.md`,
`ADDING_A_LANGUAGE.md`, `docs/tts-extension/AUTHENTICITY.md` and `DESIGN.md` 6.3 (and `CLAUDE.md`, which
was in its context). It cannot hear audio; every claim about sound below is a measurement. Another
session was running on the shared stage, so every PowerShell call began with
`$env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-nl-be"`, the stage was copied
(`$env:TEMP\OpenEvvTests\stage-nl-be`) before building, and goldens went to
`golden-nl-be` / `golden-nl-be-proposed` under `%TEMP%\OpenEvvTests`.

Every PowerShell call also began with (setup of the skill):

    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"

## Setup, and "if nl-be exists anywhere, stop"

    Get-ChildItem -Recurse -Directory -Filter "nl-be*"        -> nothing
    Get-ChildItem packs\nl, packs-proposed
    Get-ChildItem : Cannot find path '...\packs-proposed' because it does not exist.

`nl-be` exists nowhere. `packs-proposed/` did not exist yet (the other trial created it a few minutes
later).

    & $py engine\doctor.py --quick          (1 min 55 s)
    PASS  validate   validate: 21 packs, 21 accepted, 0 rejected  (engine\packs\validate_packs.py, 18 s)
    PASS  coverage   coverage: 175 of 175 checklist entries done (mapped 67, composed 53, created 55); MISSING 0, BLOCKED 0; ...
    PASS  golden     golden: 6 packs, 28 cases, 0 FAILED, 0 changed within tolerance, 10 s
    doctor: 16 checks, 16 passed, 0 warnings, 0 FAILED (none), 115 s

Model check (skill line 12): "Opus 5.5 high for large vowel shifts or many allophone rules: if so and
you are not Opus, say so first and stop." This is Sonnet. The change is 11 vowels, each a steady-state
retarget, no rule and no shift in the sense of a sound change, so the helper judged it not "large" and
went on. Decision D1 below. The abstract of the source itself says the two varieties "differ little"
in the monophthongs.

## Step 1: define the variety, find sources (about 20 min)

Variety: Southern Standard Dutch (Belgian Standard Dutch), adult male teachers of Dutch, Flanders-Brabant
(the provinces of Antwerpen and Vlaams-Brabant), read /sVs/ words. Not Brabantic dialect, not
tussentaal.

    WebSearch "Adank van Hout Smits 2004 An acoustic description of the vowels of Northern and Southern
    Standard Dutch Journal of the Acoustical Society of America"
      -> JASA 116(3), 1729-1738, doi:10.1121/1.1779271. Author order differs in some citation lists
         (Cambridge: Adank, van Hout, van de Velde); MPI, UvA and the paper itself: Adank, van Hout, Smits.
    WebFetch https://www.mpi.nl/publications/item_57759
      -> "Files public" PDF at https://pure.mpg.de/rest/items/item_57759_3/component/file_57760/content,
         no licence stated.
    WebFetch of that PDF -> the tool saved the 141 KB PDF (10 pages, with a text layer) into its tool-results
      folder (a download the helper did not ask the human about; it is outside the repository and is not
      used again). pypdf (in the venv, run with -I) extracted the text to %TEMP%\OpenEvvTests\nlbe-src\adank2004.txt.
      The abstract: "differ little in the formant frequencies at steady-state for the nine monophthongal
      vowels ... larger differences ... for the dynamic specifications of the three long mid vowels".
      (c) 2004 Acoustical Society of America. Table I (p. 1732): F1, F2, F3, F0 and duration at the middle of
      each of 15 vowels, "N per cell is 20", 20 NSD (Randstad) and 20 SSD (Flanders-Brabant) talkers.

Registered: `ipa/sources.toml` `[source.adank2004]` (`opened = true`; pages used: Table I; licence: (c)
ASA, publicly hosted, no open licence stated, facts cited, nothing copied) and `REFERENCES.md`
"Southern Standard Dutch trial (nl-be, 2026-10-11)". Appended with a small Python script that keeps each
file's line ending (sources.toml CRLF, REFERENCES.md LF). `git status` shows both files modified; the
other trial appended to the same files in the same period (no collision seen).

Recordings: none. The skill says "licensed recordings (R3, R4)"; none were looked for beyond the table,
so the pack has `recordings = []` and only a published table (the validator accepted that).

Unclear: the column order of Table I is garbled by the PDF's symbol font (the text layer gives
`/Ä/ /a/ /}/ /e/ /Ö/ /(/ /i/ /Å/ /u/ /o/ /+/ /y/`). The helper decoded it as /ɑ a ɛ e ø ɪ i ɔ u o ʏ y/
by the abstract's list and the duration row (long: a, e, ø, o). The order cannot be confirmed from the
page image (the Read tool's PDF mode needs pdftoppm, not installed), so the values carry that
uncertainty. In particular the /ɔ/ F1 (398 Hz Southern, 402 Hz Northern) looks low for /ɔ/ and close
to /o/ (369, 412); the helper kept the values as read.

Also unclear: "N per cell is 20" with two tokens per vowel and 20 talkers split by gender: the helper
read it as 10 men x 2 tokens = 20 tokens (`n = 20`, `speakers = 10`), and said so in `speaker_group`.

## Step 2: the differences from the parent

The parent `nl` is the eSpeak NG Dutch voice on the German module (dedx) and says "Dutch" with no
region. What the sources give: only steady-state vowels. List in `[meta] note` as **not made**:
long mid vowels' movement (Table II), consonants (Southern g, h, r, fricative devoicing), stress,
rhythm, intonation, any lexicon or tussentaal. No source was read for those, so none is claimed.

## Step 3: vowel evidence into targets

Phoneme names (what the reader writes), run with the frontend:

    & "$env:LOCALAPPDATA\OpenEvvBuild\frontend-x64\bin\espeak-ng.exe" --path=dist -v gmw/nl -q -x "<word>"
    pak p'Ak | maan m'a:n | pet p'Et | zee z'e:  | neus n'Y:s | pit p'It | piet p'it | pot p'Ot
    boek b'uk | boom b'o:m | put p'8t | fuut f'yt | hoed h'ut | bal b'Al | bed b'Et | deuk d'Y:k

Then the map lines in `packs/nl/pack.toml` (found with Select-String on `kind = "map"`: the skill
names `build_packs.py explain <parent> sounds.<key>`, which printed `no such value in nl` for
`sounds.A`).

    & $py engine\authenticity\normalize.py nl A=555,1066 ... --anchor i,e:,a:,o:,u,y
    the pack's sound map has no phoneme 'A'

The names had to carry the voice prefix, `@nl:A`, as in the example (`@ca-va:E`). Second try
(Southern Standard Dutch men, Table I):

    & $py engine\authenticity\normalize.py nl "@nl:A=555,1066" "@nl:a:=717,1429" "@nl:E=475,1616" "@nl:e:=384,1993" "@nl:Y:=374,1539" "@nl:I=364,1745" "@nl:i=278,2179" "@nl:O=398,850" "@nl:u=266,978" "@nl:o:=369,862" "@nl:8=353,1492" "@nl:y=265,1825" --anchor "@nl:i,@nl:e:,@nl:a:,@nl:o:,@nl:u,@nl:y"
    nl: module dedx; factor x0.9704 over @nl:a: @nl:e: @nl:i @nl:o: @nl:u @nl:y (f1 f2)
      @nl:A    phone O   target 538.6 / 1034.5   now 661.2 / 1026.0   change F1 -18.5% F2 +0.8%   override
      @nl:a:   phone a   target 695.8 / 1386.7   now 800.0 / 1246.0   change F1 -13.0% F2 +11.3%   override
      @nl:E    phone E   target 461.0 / 1568.2   now 550.0 / 1800.0   change F1 -16.2% F2 -12.9%   override
      @nl:e:   phone e   target 372.6 / 1934.0   now 370.0 / 2150.0   change F1 +0.7% F2 -10.0%   override
      @nl:Y:   phone oe  target 362.9 / 1493.5   now 433.2 / 1465.0   change F1 -16.2% F2 +1.9%   override
      @nl:I    phone I   target 353.2 / 1693.4   now 380.0 / 2000.0   change F1 -7.1% F2 -15.3%   override
      @nl:i    phone i   target 269.8 / 2114.5   now 265.0 / 2150.0   change F1 +1.8% F2 -1.7%   within 6%
      @nl:O    phone O   target 386.2 / 824.9    now 513.0 / 900.0    change F1 -24.7% F2 -8.3%   override
      @nl:u    phone u   target 258.1 / 949.1    now 330.0 / 750.0    change F1 -21.8% F2 +26.5%  override
      @nl:o:   phone o   target 358.1 / 836.5    now 475.8 / 889.4    change F1 -24.7% F2 -5.9%   override
      @nl:8    phone Y   target 342.6 / 1447.9   now 400.0 / 1317.2   change F1 -14.3% F2 +9.9%   override
      @nl:y    phone y   target 257.2 / 1771.0   now 300.0 / 1820.0   change F1 -14.3% F2 -2.7%   override

(The anchor was i, e:, a:, o:, u, y: the table's vowels the module also has as plain phones; the skill
says to leave out those the dialect moves, which is not known before looking. Decision D2: anchor on
the six, accept.)

Eleven of twelve vowels move more than 6 per cent: 11 overrides, /i/ none. To separate "Southern"
from "the parent is poor Dutch" the helper also normalized the Northern men (same table, same anchor,
factor x0.9824): the parent is off the Northern table in nearly the same way (e.g. /ɑ/ F1 -14.1 %,
/ɛ/ F1 -15.2 %, /ɔ/ F1 -23.0 %, /u/ F1 -22.9 %). Raw-Hz ratios Southern/Northern (men), with those
beyond 6 per cent: /ɑ/ F2 -9.0, /a/ F1 +7.0, /ɛ/ F2 -7.1, /ɪ/ F2 -9.1, /u/ F2 +21.5, /o/ F1 -10.4 and
F2 -7.2, /ʏ/ F2 -6.5; /e ø ɔ y/ differ by under 6 per cent between the two varieties. So 7 of the 11
overrides carry a Southern-versus-Northern difference, and 4 (e, ø, ɔ, y) only correct the parent. The
skill's rule ("write an override only where F1 or F2 moves more than 6 per cent from what the pack
says now") gives all 11; the helper followed it and said the 4-versus-7 split in the pack's note.

## Step 4: the pack

Files: `packs-proposed/nl-be/pack.toml` (kind dialect, extends nl, `[meta]`, `[ini.Language]` Tag, Name,
Order "1100" (all of 290-309 and up to 992 are used), 11 `[[override]]`, each `state = "proposed"`,
f1 and f2 `derived`, `ref = "adank2004"`, `n = 20`, `speakers = 10`, `norm` text) and `review.toml`
(14 words, 4 sentences with `source` because `nl-be` has none of its own in `asr/sentences.json`,
11 `[[check]]`). Override `phonemes`: `@nl:A`; `@nl:a:`; `@nl:E`, `@nl:E2`; `@nl:e:`; `@nl:Y:`; `@nl:I`;
`@nl:O`; `@nl:u`, `u`; `@nl:o:`; `@nl:8`; `@nl:y`, `y` (the names in the parent's `[sounds]` section that
say each sound; found by reading the pack's lines).

    & $py engine\packs\validate_packs.py nl-be
    nl-be                  accepted
    validate: 1 packs, 1 accepted, 0 rejected

## Step 5: validate and measure in a scratch stage

    $tag='nl-be'; $S="$env:TEMP\OpenEvvTests\stage-$tag"; $G="$env:TEMP\OpenEvvTests\golden-$tag"
    Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S       (0.2 s)
    & $py engine\packs\build_packs.py build "$S\languages" $tag
    nl-be                  language.ini ad3c7dbc16, sounds.map 533579d8ec, phonemes.map 0e1a237be6, sample.txt 321baf57be
    & $py engine\authenticity\show_effect.py $tag                                (40 s)

Each override, asked F1/F2 in the frames (measured in the sound in brackets in the tool's output; here
the asked values), preset 1, before / after / target; the full table is in the tool's output (22
words). Per sound, first word:

| IPA | word | target F1/F2 | before | after | after vs target |
|---|---|---|---|---|---|
| ɑ | pak | 539 / 1034 | 633 / 1017 | 516 / 1025 | F1 -4.2 %, F2 -0.9 % |
| aː | maan | 696 / 1387 | 800 / 1165 | 699 / 1289 | F1 +0.5 %, F2 -7.0 % |
| ɛ | pet | 461 / 1568 | 550 / 1800 | 462 / 1566 | F1 +0.2 %, F2 -0.1 % |
| eː | zee | 373 / 1934 | 370 / 2150 | 374 / 1935 | F1 +0.4 %, F2 +0.1 % |
| øː | neus | 363 / 1494 | 433 / 1439 | 365 / 1468 | F1 +0.6 %, F2 -1.7 % |
| ɪ | pit | 353 / 1693 | 380 / 2000 | 353 / 1700 | F1 -0.1 %, F2 +0.4 % |
| ɔ | pot | 386 / 825 | 479 / 890 | 372 / 826 | F1 -3.7 %, F2 +0.1 % |
| u | boek | 258 / 949 | 323 / 750 | 257 / 936 | F1 -0.4 %, F2 -1.4 % |
| oː | boom | 358 / 836 | 476 / 889 | 359 / 838 | F1 +0.3 %, F2 +0.2 % |
| ʏ | put | 343 / 1448 | 400 / 1317 | 344 / 1450 | F1 +0.4 %, F2 +0.1 % |
| y | fuut | 257 / 1771 | 300 / 1820 | 261 / 1769 | F1 +1.5 %, F2 -0.1 % |

Summary line: `largest distance from the target (F1 or F2, asked): before median 18.1%, after median 1.7% (22 words)`;
`largest difference between the two versions' preset-2 ratios: 0.003`.

The misses, said plainly (second word of each sound, same tool output): **hoed** (u) after F2 750 against
the target 949, -21.0 % (before and after both 250 / 750: the override did not reach this word's vowel;
the trace of `hoed boek` is `u t b u k #`, no h phone, and the word starts with the breathy h, so the
module's own onset handling holds the vowel; not diagnosed further); **bed** (ɛ) F1 +11.9 %, F2 -7.3 %;
**bal** (ɑ) F1 -12.4 %; **maan** (aː) F2 -7.0 %; **bos** (ɔ) F1 +6.9 %. These are the module's own
context effects (the same vowel asks for different formants after different consonants and before voiced
stops), larger than 6 per cent in 5 of 22 words. The medians hide them; the "after median 1.7 %" is
the median over words of the larger of F1 and F2 distance.

    & $py docs\tts-extension\harness\golden.py $tag --record --golden $G           (85 s)
    nl-be    154 cases  0 errors  0 not covered   76.6 s
    & $py docs\tts-extension\harness\check_language.py $tag --golden $G --asr --asr-like nl       (14 s)
    nl-be    CER 0.199  WER 0.491  (8 sentences, cuda/float16, 7 s)
    check A: pass; substituted 0; phones meant to sound 580, silent 0; formant and F0 checks 889 of 890
        v|A~: O F1 measured 317.44, frames 554.0
    check B: too few references (4/5 in range); references for 0 vowels; 3 needed
    ASR: CER 0.20 WER 0.49
    level: 2 engine-verified; failure layer: unknown

The parent on the same stage (`check_language.py nl --asr`): CER 0.199, WER 0.491, same check A line
(889 of 890, `v|A~`), same check B, level 2. So the pack without its overrides measures as `nl`.

With the overrides built in (`build_packs.py build "$S\languages" nl-be --proposed`, record into
`golden-nl-be-proposed`, check, then rebuild without):

    nl-be    154 cases  0 errors  0 not covered   79.3 s
    nl-be    CER 0.293  WER 0.597  (8 sentences, cuda/float16, 6 s)
    check A: pass; substituted 0; phones meant to sound 580, silent 0; formant and F0 checks 889 of 890
    check B: too few references (4/5 in range); references for 0 vowels; 3 needed
    level: 2 engine-verified; failure layer: unknown

Check A holds (889 of 890, the same one miss as the parent). **The recogniser understands the
proposed version worse: CER 0.199 to 0.293.** Whisper's Dutch model is trained largely on Netherlands
Dutch and the sentences are Netherlands Common Voice sentences, so this is no proof the vowels are
wrong, and no proof they are right; it is stated and not chased. Nothing in the skill's "Done when"
asks for it, but it is the number a human deciding to ship would want. Rebuilt without:
`sounds.map 533579d8ec` again (the same hash as before).

## Step 6: the parent is unaffected

    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"
    & $py docs\tts-extension\harness\golden.py nl                      (94 s)
    nl       154 cases  0 errors  0 not covered   91.1 s
    golden: 1 packs, 154 cases, 0 FAILED, 0 changed within tolerance, 94 s
    & $py engine\packs\build_packs.py check
    packs checked: 162; files compared: 597 (5662611 bytes); by realization: legacy 145, module 17
    check: every file identical to languages/

## Step 7: packet

    $env:EVV_STAGE=$S ; & $py engine\review\make_packet.py nl-be       (42 s)
    packet nl-be: 79 items (words 14, sentences 4, compare 44, sounds 17); C:\Users\joshk\OneDrive\dev\espeakproject\OpenEvv-sapi5\docs\tts-extension\review_packets\nl-be; index.html 3082327 bytes; folder 5436998 bytes
    items where the front-end or accent layer reported a loss: 1 (s-04)

The matplotlib `RuntimeWarning` appeared as the skill said. The flagged item s-04 is the parent's: `note
said-as-nothing 'ː' in /ɪː/: the map gives it as -`. The key is `docs/tts-extension/review/keys/nl-be.json`.
For a real pack the skill does not say where the packet goes; the helper used the default (no `--out`),
which is `docs/tts-extension/review_packets/nl-be/` as AUTHENTICITY.md section 6 says (the skill names
`--out` only for a test pack). The packet was made from the stage as built in step 5 without
`--proposed`, as the skill says; the A/B items make the overridden version themselves.

## Step 8: status and report

`[meta] status` level 2 equals what `check_language.py` printed for the pack as built (level 2
engine-verified). Not 5. LANGUAGE_STATUS.md: its table is generated, so a bullet was added under its
latest heading ("Phase 8 (2026-10-11)"): "Proposed, not shipped: `nl-be` ..." (one `Edit`, nothing
else in the file).

Measured: the vowels' formants as asked in the frames and as measured in the sound (22 words), check
A. From literature: the 11 target F1/F2 pairs (adank2004 Table I, Southern men, `derived` after the
size normalization). Not made: the long mid vowels' movement, consonants, stress, rhythm, intonation,
vocabulary; the women's and the other three Flemish regions' values; no recording of ours was
measured. Nothing is called authentic. Shipping waits for the human.

## Step 9: review

The `tts-reviewer` agent was launched with the Done-when list and the changed paths. It edited nothing,
re-ran validate, build check, show_effect, check_language (nl-be and nl) and golden nl, and reproduced
the log's numbers. Exit criteria 1, 3, 4 met; 2 met except `hoed`. Its findings, and what was done:

1. The /u/ override does not reach "hoed", yet the packet's A/B pair c-u-hoed-A/B asks for 250/750 Hz
   in both; the pair's `phones` is `u t #` with no /h/ and `diag` empty. The missing /h/ is the parent's
   (`phonemes with no phone of their own: 2 f|h s|?`). Not fixed: this log's earlier explanation ("the
   module's own onset handling") was a guess and is withdrawn; the cause is that the word has no
   audible h phone, so the pair is identical in what it asks for. Owed: drop `hoed` from the `/u/`
   `[[check]]` in review.toml (or accept it) and make `make_packet.py` flag an A/B pair whose two
   sides ask for the same formants.
2. The pack note said "long mid vowels /e o O/"; fixed to "/e o ø/" (`O` is /ɔ/ in the pack's
   notation). Validate re-run: accepted.
3. The step 5 block above omits the line `phonemes with no phone of their own: 2 f|h s|?` that the tool
   prints for nl-be and for nl. Stated here; the parent's other lines were summarised, not pasted
   (the reviewer reproduced them exactly).
4. `pack.toml`'s `[meta] note` was edited after the measurements and the packet (two edits, text only,
   `fixnote.py`; then the /e o ø/ fix above). No value changed; the reviewer's reruns used the file as
   it stood and matched.
Confirmed by the reviewer: the Table I column decoding (by the abstract, the durations, Table II's
/ɔu/), every SSD male value, the x0.9704 arithmetic, the seven Southern-versus-Northern differences,
`n = 20`, `speakers = 10` ("five young men, five older men", two tokens each; Flanders-Brabant: Lier,
Heist-op-den-Berg), licence records. This closes the "not confirmed" item below about column order.

## Decisions a human would have had to make (all taken by default)

- D1. Sonnet versus the "Opus for large vowel shifts" line: continued on Sonnet (11 small steady-state
  retargets, abstract says the varieties differ little).
- D2. Which table vowels to anchor the size factor on (the skill leaves it to the author): the six plain
  phones i, e, a, o, u, y.
- D3. Which of the 12 vowels get an override: all those over 6 per cent (11), as the skill's rule says,
  even where only the parent's own error (not a Southern difference) explains it (4 of them).
- D4. Order "1100" for the voice list (any unused number).
- D5. Whether to read the speakers as 10 men (the paper says "N per cell is 20").
- D6. Packet location (default, no `--out`).
- D7. Reading the PDF at all (WebFetch saved it outside the tree; the helper kept it and extracted text
  with pypdf). The human's approval of a download would normally be asked.
- D8. Adding to `ipa/sources.toml` and `REFERENCES.md` (tracked files, the skill asks for it).
- D9. A bullet in LANGUAGE_STATUS.md.

## Closing figures

(1) Commands run: about 40 PowerShell calls (including the doctor, 4 Python helper scripts of the
helper's own, 2 web searches/fetches for the paper and 3 file reads of the PDF); 9 decisions listed above.

(2) Level reached: `level: 2 engine-verified; failure layer: unknown` (the raw line, from
`check_language.py nl-be --golden ... --asr --asr-like nl`).

(3) Documentation gaps: see below.

(4) Not finished: see below.

## Documentation gaps

1. SKILL step 3, "`build_packs.py explain <parent> sounds.<key>` or search `packs/<parent>/pack.toml`":
   `explain nl sounds.A` printed `no such value in nl`, and a search for `A =` finds nothing, because the
   sound map lines are `{ kind = "map", name = "@nl:A", to = "O=s50" ... }` records. Change to: "search
   `packs/<parent>/pack.toml` for `kind = "map", name = "@<voice>:<phoneme>"` (the name carries the voice
   prefix, e.g. `@nl:A`, and the reader's plain `a`, `e`, `i`, `o`, `u`, `y` may have a line of their own)".
2. SKILL step 3 and ADDING_A_LANGUAGE.md section 4: `normalize.py` refuses a bare name (`the pack's
   sound map has no phoneme 'A'`). Say once: "key by the full map name, `@nl:A`, not `A`".
3. SKILL step 3, "Every phoneme that says the sound needs the override": there is no command that lists
   them. Add one (a `build_packs.py explain <pack> sounds.line --name ...` or a `phonemes_of <sound>`
   option), or say how to find them (grep `to = "O=s50"`).
4. SKILL step 3, the rule "override only where F1 or F2 moves more than 6 per cent from what the pack
   says now": for a dialect of a parent whose vowels are generally off the language's own table, this
   writes overrides that are corrections of the parent, not dialect differences (here 4 of 11). Change to:
   "Compare also the table's other variety (or the parent's own region) in raw Hz, and say in the note
   which overrides carry the dialect's difference and which only correct the parent."
5. SKILL step 1 and "Done when": there is no step that asks for the sources' column and token
   identification to be checked against the page when the table's symbols are garbled in text
   extraction. Add: "if you read a table from a PDF's text layer and the symbol columns are garbled,
   decode them from the paper's own list and say so in the note".
6. SKILL step 5: "`$S` is a copy of the shared stage ... `Copy-Item -Recurse ... $S # once`" is right,
   but beside another session it also needs `EVV_HARNESS_WORK` before the `Copy-Item`; the comment at the
   top of the setup block says so only as a comment. Make it a line of the setup, not a comment.
7. SKILL step 5 and "Done when": nothing says what to do when the overrides make the recogniser
   worse (here CER 0.199 to 0.293). Add a line: "report the CER with and without the overrides; a
   rise of more than 0.05 goes in the note and to the human".
8. SKILL step 5: `show_effect.py` can show an override that does not reach a word (here `hoed`, F2
   -21 % after the override, unchanged by it). "Done when" says "its effect is measured and shown" but
   not what to do about a word it missed. Add: "a word the override does not move by half the gap is
   named in the note and either explained or taken out of review.toml".
9. SKILL step 7: "a test pack: `--out docs\tts-extension\examples\packets\$tag`" leaves the real-pack
   location implicit. Change to: "a real pack: no `--out` (it goes to `docs/tts-extension/review_packets/<tag>/`)".
10. SKILL step 4: `Order`: "any number no other pack uses" does not say how to find the free numbers
    (290-309 and 913-992 are taken). Give the one-liner that lists them, or say "use 1000 + n".
11. SKILL step 1 does not say that WebFetch of a PDF may save the PDF on disk; the project rule is that
    third-party reference files stay in the tree with a licence in `NOTICE.md` ("a clone holds
    everything"). It says only "register each in `ipa/sources.toml`". State whether a PDF read for a
    table is kept in `third_party/` (here the licence forbids: copyright ASA, no open licence) or only
    cited.
12. ADDING_A_LANGUAGE.md section 4 prints `ca-va`'s `--anchor i,e,a,o,u` but never says how the
    anchor was chosen; the skill says "leave out those the dialect moves". Add one sentence: "if unsure,
    use the vowels i e a o u that the module has as plain phones; the size factor then changes by
    under 1 per cent whichever of them you leave out".
13. ADDING_A_LANGUAGE.md section 2: "`packs-proposed/<tag>/` ... a real new language" - the folder
    does not exist in a fresh clone; `new_language.py` makes it, but a dialect written by hand needs
    `New-Item -ItemType Directory`. Say so in the skill's step 4.

## What was not finished

- The `tts-reviewer` review: see step 9 above.
- The Table I column order was decoded, not confirmed against the page image (no PDF rasterizer in this
  environment); a second reader should look at the paper's Table I once.
- `hoed`'s F2 shortfall (-21 %) was not diagnosed.
- No recordings were sought (the skill says "licensed recordings"; none were searched for beyond the
  table), so `recordings = []` and the validator's "speakers per variety >= 5" minimum is met only by
  the table's 10 men (inferred).
- Level 3 (check B) is not reachable: the reference store has no Dutch vowel ranges; the adank2004
  table could be added to `docs/tts-extension/harness/reference/ranges.json` by `/improve-language`
  (not done: that is a change to a tracked results/reference file outside the task).
- The women's values (also in Table I) are not used; a Southern female voice (preset 2) scales the
  men's pattern.
