# Phase 9 trial A: /add-language Finnish fiu/fi fi-x-evvtrial

Date 2026-10-11. Run by a helper that read only `.claude/skills/add-language/SKILL.md`, `ADDING_A_LANGUAGE.md`,
CLAUDE.md and the first 60 lines of PROJECT_STATE.md (the skill says to read it). Every PowerShell call began with
`$env:EVV_HARNESS_WORK="$env:TEMP\OpenEvvTests\harness-fi-x-evvtrial"` plus the skill's Setup lines. Scratch stage:
`%TEMP%\OpenEvvTests\stage-fi-x-evvtrial`; golden: `%TEMP%\OpenEvvTests\golden-fi-x-evvtrial`.

## Step 0: precondition and Setup

Tag check (nothing found anywhere): no directory `fi-x-evvtrial*` in the tree, no mention in `harness/asr/*.json`.

Reader check as given in the arguments (`fiu/fi`):

    Test-Path dist\espeak-ng-data\lang\fiu\fi      ->  False
    Get-ChildItem dist\espeak-ng-data\lang         ->  aav art ... urj ... (no "fiu" family folder; eu ko qu are loose files)
    Test-Path dist\espeak-ng-data\lang\urj\fi      ->  True

DECISION 1 (human's): `fiu/fi` does not exist; Finnish is `urj/fi` (the family folder `urj`). Took the voice that exists and
reads Finnish. (Mistake of mine: I also opened `packs/fi/pack.toml` to see the name of the voice; the skill does not tell
you to look there, and a user without that file would have used `Get-ChildItem dist\espeak-ng-data\lang` as the skill says.)

Doctor (`& $py engine\doctor.py --quick`, 118 s):

    doctor: 16 checks, 16 passed, 0 warnings, 0 FAILED (none), 117 s

## Step 1: research (about 4 min)

Done myself (no research subagent). One web search and one fetch:
- Search "Finnish phonology vowel inventory formants quantity initial stress orthography phonemic": results listed in
  REFERENCES.md, none opened except through the search summary.
- Opened: <https://en.wikipedia.org/wiki/Finnish_phonology> (CC BY-SA 4.0, stated on the page).
  Facts: 8 vowels /i y u e o æ ɑ ø/ short and long; vowel harmony; fixed initial stress; length by doubled letters; spelling near
  phonemic; consonant gradation; native consonants m n ŋ p t k s h ʋ l j r.
- Recorded in `docs/tts-extension/REFERENCES.md` (new section at the end) and `ipa/sources.toml`
  (`[source.wikipedia_finnish_phonology]`, `opened = true`). Could not find: published Finnish vowel formant tables that are
  open (so check B has no references), open Finnish recordings (ASR sentences are borrowed through `--asr-like fi`).

## Step 2: reader and start

    & $py engine\packs\new_language.py urj/fi fi-x-evvtrial --out packs-proposed --name "Finnish (trial, TEST)"
    fi                     dedx  Finnish                            114 sounds  0 tones peak  fall      tests+dictionary  (automatic: itit)
    1 packs written to C:\Users\joshk\AppData\Local\Temp\evv-newlang-3bq71hqg\languages
    fi-x-evvtrial: 75639 bytes of pack in packs-proposed\fi-x-evvtrial, identical to what the generator wrote (template dedx)

2.9 s. Unclear: the generated `[ini.Language]` has `Order = "200"`, `Id = "0x00040000"`, `LCID = "40B"` - the same as the real `fi`
(the dialect example says "any number no other pack uses" only in the pack text, not in the language steps). I set
`Order = "991"` (DECISION 2, mine; Id and LCID left because the guide never mentions them).

## Step 3: write the pack

Edited `packs-proposed/fi-x-evvtrial/pack.toml` `[meta]`: `sources` (voice + the Wikipedia article), `note` (TEST copy, nothing
hand-changed, what is not made), `Order`. No `[[override]]` (no value was changed by hand, so no provenance tags needed).
Wrote `review.toml` (8 words including the quantity trio tuli/tuuli/tulli; 4 sentences from the Finnish ASR set, Common Voice CC0).

    & $py engine\packs\validate_packs.py fi-x-evvtrial
    fi-x-evvtrial          accepted
    validate: 1 packs, 1 accepted, 0 rejected

(Not asked for by the skill for a kind="language" pack, but cheap.)

## Step 4: measure

    Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S          (0.14 s, 92,863,012 bytes, a real copy)
    & $py engine\packs\build_packs.py build "$S\languages" $tag
    fi-x-evvtrial          language.ini a7222af3ed, sounds.map af6033713b, phonemes.map af9d805f49, sample.txt b4f9ceb032
    & $py docs\tts-extension\harness\engine.py $tag text "Hei, tuuli puhaltaa tulli kiitos." ...\fi-x-evvtrial.wav
    fi-x-evvtrial: 31691 samples at 11025 Hz, 2881 ms, 577 frames, 23 phones (trace): e # t u l I p u a l t a t u l l I k i t o s #

(Observation, not judged by ear: "Hei" came out as the single phone `e`, the `i` of the diphthong is not in the trace. Not
investigated further; it is the reader/template behaviour, the same for the shipped `fi`.)

    & $py docs\tts-extension\harness\golden.py $tag --record --golden $G
    fi-x-evvtrial 161 cases  0 errors  0 not covered   77.4 s
    recorded 1 packs in 80 s; 0 not recorded

    & $py docs\tts-extension\harness\check_language.py $tag --golden $G --asr --asr-like fi        (17 s)
    fi-x-evvtrial CER 0.490  WER 0.872  (8 sentences, cuda/float16, 9 s)
    fi-x-evvtrial (Finnish (trial, TEST)): 161 golden cases; module dedx
    check A: pass; substituted 0; phones meant to sound 601, silent 0; formant and F0 checks 816 of 816
    check B: too few references (4/5 in range); references for 0 vowels; 3 needed
    ASR: CER 0.49 WER 0.87
    phonemes with no phone of their own: 2 f|h s|?
    level: 2 engine-verified; failure layer: unknown

Comparison on the same stage (`check_language.py fi --asr`): identical, `ASR: CER 0.49 WER 0.87`, same check A line, same level.
So the copy measures like the shipped Finnish. CER 0.49 is far above the 0.15 needed for level 4; the skill says "level 2 is the
usual result" but gives no instruction for a high CER (no failure layer is named: "failure layer: unknown"). I did not chase it.

Quantity (Finnish's main contrast), measured from the engine's own trace, not by ear:

    tuli   775 ms, 5 phones: t u l I #
    tuuli  825 ms, 5 phones: t u l I #
    tulli  852 ms, 6 phones: t u l l I #

The long vowel in `tuuli` is the same phone sequence as `tuli` and only 50 ms (6 %) longer overall; the long consonant adds a
phone and 77 ms. The packet reports `said-as-nothing ː` for /aː tː kː yː æː ɪː/ ("the map gives it as -"). So the length mark is
carried by duration, not a phone, and the contrast is weak. This is a finding for a native reviewer and for a real Finnish
improvement; nothing was changed (this is a copy of the shipped data).

Time for step 4: about 3.5 min.

## Step 5: map every phoneme

`check_language.py` lists two: `f|h` and `s|?`. Looked up in the master table:

    & $py engine\ipa\coverage.py          (rows, trimmed)
    13  ʔ    U+0294  pulmonic  mapped   pass  2  derived 2   <q{hush=1 ms=45}
    47  h    U+0068  pulmonic  mapped   pass  2  derived 2   <h{ms=102 whisper=44}

So /h/ is made as breath (a `<h` whisper phone of 102 ms) and the glottal stop as a 45 ms hush; neither has a phone of the dedx
module. Both are in the table, so no `/create-missing-sound`. Not substituted, not silent (check A: "silent 0"). The guide's
Swahili paragraph explains the same two. Unclear: the label `f|h` (and `s|?`) is not explained anywhere I read; I took it as
"phoneme h (after f) / ? (after s)". The skill also gives no way to see which Finnish words use them.

## Step 6: regression

DECISION 3 (deviation, mine): did NOT run the full `golden.py` the skill asks for. Reason: reading `golden.py` (line 380-385), a run
with no tags writes `docs/tts-extension/harness/results/diag-golden-staged.json` (the file's time stamp, 13:09, shows the other
session's regression had just written it), and the trial rules forbid writing into `results/`. Also it would take 25-40 min beside
the other session. Instead, on my scratch stage (a copy of stage-dev plus my pack), the dedx-template neighbours, which a tag
list does not write results for:

    & $py docs\tts-extension\harness\golden.py fi et hu dede
    dede      86 cases  0 errors  0 not covered   26.0 s
    hu       153 cases  0 errors  0 not covered  105.8 s
    fi       161 cases  0 errors  0 not covered  113.6 s
    et       164 cases  0 errors  0 not covered  115.7 s
    golden: 4 packs, 564 cases, 0 FAILED, 0 changed within tolerance, 118 s
    & $py engine\packs\build_packs.py check
    packs checked: 162; files compared: 597 (5662611 bytes); by realization: legacy 145, module 17
    check: every file identical to languages/
    & $py engine\doctor.py --quick
    doctor: 17 checks, 17 passed, 0 warnings, 0 FAILED (none), 93 s

(17 checks now: the validate step picked up my pack.) The full 155-pack golden is therefore NOT shown; the "Done when" line
"the golden regression of every existing language" is not met. A new pack built only into a scratch stage cannot change another
language's output, which is why this is low risk.

## Step 7: packet

    & $py engine\review\make_packet.py fi-x-evvtrial --out docs\tts-extension\examples\packets\fi-x-evvtrial
    packet fi-x-evvtrial: 32 items (words 8, sentences 4, sounds 20); docs\tts-extension\examples\packets\fi-x-evvtrial; index.html 1484660 bytes; folder 2625848 bytes
    items where the front-end or accent layer reported a loss: 5 (w-hyv s-01 s-02 s-03 s-04)
    IPA: eSpeak NG C:\Users\joshk\AppData\Local\OpenEvvBuild\frontend-x64\bin\espeak-ng.exe

The matplotlib `RuntimeWarning: divide by zero encountered in log10` appeared (the skill said it is harmless); PowerShell shows it
as a NativeCommandError because stderr was captured: the command did succeed. Key written: `docs/tts-extension/review/keys/fi-x-evvtrial.json`.
The flagged losses are all "said-as-nothing ː" (length mark). Note: the packet script prints a path to an eSpeak NG outside the
repository (`%LOCALAPPDATA%\OpenEvvBuild\frontend-x64`), not in the instructions.

## Step 8: status

Added `status = { level = 2, validated_by = "", date = "" }` to `[meta]` of `pack.toml`; re-validated (accepted) and rebuilt
(same hashes as before). Test pack: nothing written to `LANGUAGE_STATUS.md`.

## Step 9: report (plain English)

Finnish was made again as the TEST tag `fi-x-evvtrial` from eSpeak NG's `urj/fi`, template `dedx` (the German module). 114
sounds, nothing changed by hand, so nothing is created, approximate or estimated by this pack (it inherits the generator's
values; the provenance of those is the template's). Level 2: the engine says what it is told (816 of 816 readings, nothing
silent or substituted). Check B cannot judge (no Finnish vowel references). ASR 0.49 CER, too high for level 4, same as the shipped
Finnish. For a native reviewer first: vowel and consonant length (tuli/tuuli/tulli: 775/825/852 ms, the long vowel adds the same
phones), the diphthong in "hei", /h/ and the glottal stop (breath and hush). Not shipped; shipping waits for the human.

## Step 10: review

Launched the `tts-reviewer` agent with the Done-when list. Its result: see the end of this file.

REVIEW RESULT: pending when this log was written; see the final report and the appended section below if present.

## (1) Commands and decisions

- Commands run (PowerShell/tool calls that ran the project's tools): doctor 2, new_language 1, validate 2, build 2, engine.py 5,
  golden --record 1, check_language 2, coverage 2, golden tags 1, build_packs check 1, make_packet 1 = about 20; plus about 10 file
  reads and edits, 2 web calls.
- Decisions a human would have had to make: (1) which voice, since `fiu/fi` does not exist; (2) the pack's `Order` number (and
  whether to change Id/LCID); (3) whether to run a full 155-pack regression beside another session (skipped); (4) whether CER 0.49
  at level 2 is acceptable or to investigate; (5) which words/sentences go in `review.toml`. Five. None were asked by the skill as
  questions; each was taken by the default above.

## (2) Level reached

    level: 2 engine-verified; failure layer: unknown

(in `check_language.py fi-x-evvtrial --golden ... --asr --asr-like fi`; check A pass, 816 of 816; check B too few references
(4/5 in range); ASR CER 0.49.)

## (3) Documentation gaps

1. Skill/task arguments: the invocation named the voice `fiu/fi`, which does not exist. The skill's step 2 says "the voices are the
   files under `dist/espeak-ng-data/lang/`" but gives no command to find a voice by language name. Add after that sentence:
   "To find the voice for a language: `Get-ChildItem dist\espeak-ng-data\lang -Recurse -File | Where Name -eq <code>`; the voice is
   `<family folder>/<code>`, for example `urj/fi`."
2. ADDING_A_LANGUAGE.md section 3, Step 2 / skill step 2: the generated `[ini.Language]` has the real language's `Order`, `Id` and
   `LCID`. Add: "Change `Order` to a number no pack uses (the dialect example uses 990) and leave Id/LCID alone; the build does not
   check them." (I could not find where Id/LCID matter, and I did not verify that the duplicate Order is harmless.)
3. Skill step 6 says to run `golden.py` for every language with `EVV_STAGE` on the shared stage. Without tags, `golden.py` writes
   `docs/tts-extension/harness/results/diag-golden-staged.json` (golden.py line 380-385), and that file is hit by another session
   running the same thing. Add to step 6: "A run without tags overwrites `results/diag-golden-staged.json`; do not run it while
   another session does, and use the scratch stage `$S` (it is a copy), not `stage-dev`, so you also test your own pack." Also: the
   skill does not say whether the regression should include the new pack's tag; with the scratch stage it does.
4. Skill step 4: "Check A passes with a few misses" - here it passed with none, and ASR CER 0.49 gives "failure layer: unknown".
   Add: "A CER above 0.15 with check A passing and no references means the level stays 2; say so and name the likely layer
   (`/diagnose-language`) instead of leaving 'unknown'."
5. Skill step 5: "`check_language.py` lists the phonemes with 'no phone of their own'" - the label `f|h`, `s|?` is never explained.
   Add to ADDING_A_LANGUAGE.md section 3 step 5, after "The two phonemes ...": "(`f|h` means the phoneme h as the front-end gives it
   after f; the sound is looked up under `h` in `coverage.py`.)" - if that is what it means; I am not certain.
6. Skill step 2 says "stop and report" when there is no voice; but the task argument can simply be wrong. Say: "If the voice
   given does not exist but another voice reads the language, use it and say so."
7. Skill step 7: the matplotlib warning is "harmless" but PowerShell turns captured stderr into a red NativeCommandError; add
   "(PowerShell prints it as an error record; judge by the line `packet <tag>: ...`)".
8. Quantity: ADDING_A_LANGUAGE.md section 10 (what cannot be done yet) does not list length-contrast languages. Finnish (and
   Estonian) rely on duration and the packet says `said-as-nothing ː`. Add a bullet: "Length (Finnish, Estonian, Japanese
   moras): the length mark ː is made by duration alone; measure it (tuli/tuuli/tulli) before claiming it."
9. Skill step 1 says a research subagent "if you can launch one"; no instruction on how to decide that a Wikipedia article is
   enough. Add: "A language with no open acoustic study stays at level 2; say so; do not search for more than an hour."
10. Skill steps 3 and 8: `status = {...}` is written in `[meta]`, but the generator does not write that key, and
   `packlib.py` is named for the format. Add the line to the generated pack in the guide's step 3 example.

## (4) What I did not finish

- The full golden regression of every existing language (step 6), for the reason given.
- Investigating why ASR is 0.49 and why the long vowel adds only 50 ms (a pointer to /improve-language, not done: a copy).
- The `i` of "hei" being missing from the phone trace (not checked in the engine's trace of each word).
- Reading `packs/fi` (I did once, in error); not used for any value.
- The reviewer's result, if absent below.
