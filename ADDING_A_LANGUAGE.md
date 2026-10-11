# Adding a language, a dialect or an accent

A plain-English guide for the human and for any Claude model. It shows three worked examples that
really run (a language, a dialect that inherits from its parent, an accent), with the exact commands
and what they printed. The examples are tests: they live in `docs/tts-extension/examples/` and are
never shipped.

**Why everything is measured.** The person who looks after this project speaks only American
English, and Claude cannot hear at all. So nothing here is judged by ear. A language's quality is a
**level**, earned by measurements (see "The status ladder"), and only a native speaker who signs a
review can make it "authentic".

**What "data-only" means here.** The engine (IBM's rule machine and a formant synthesizer) and the
text reader (eSpeak NG) are not changed when a language is added. A language is one **pack**: a
TOML file, `pack.toml`, that says which eSpeak NG voice reads the text, which of the engine's seven
template modules speaks it, and how each of the language's sounds differs from the template's
nearest sound. A build step turns the pack into the four files the product reads
(`languages/<tag>/language.ini`, `sounds.map`, `phonemes.map`, `sample.txt`).

The same steps as slash commands (Claude Code, this repository): `/add-language`, `/add-dialect`,
`/add-accent`, `/improve-language`, `/diagnose-language`, `/create-missing-sound`
(`.claude/skills/`). Each ends with an independent review by the `tts-reviewer` agent.

## Contents

1. Setup (once) and the doctor
2. Where packs live
3. Worked example: a language (`sw-x-evvdemo`)
4. Worked example: a dialect that inherits (`ca-va-x-evvdemo`)
5. Worked example: an accent (`en-us-x-evvdemo-es`)
6. The commands, one line each
7. The status ladder
8. Shipping a pack
9. Improving, diagnosing, creating a missing sound
10. What cannot be done yet
11. Common mistakes

## 1. Setup (once) and the doctor

Windows, PowerShell, from the repository root. The tools need the project's Python environment (a
venv under your user folder with numpy, scipy, soundfile, jiwer, tomli and faster-whisper; the
harness README, `docs/tts-extension/harness/README.md`, says how to make it), the built tools and a
**stage**: a folder holding the rebuilt template modules and the newest front-end, which the
harness uses instead of the shipped ones (`EVV_STAGE`).

    cmake -G "Visual Studio 17 2022" -A x64 -S . -B build_x64
    cmake --build build_x64 --config Release
    $env:PYTHONUTF8='1'; $py="$env:USERPROFILE\OpenEvvBuild-ttsext\venv\Scripts\python.exe"
    $env:EVV_PACKS_EXTRA="$PWD\packs-proposed;$PWD\docs\tts-extension\examples\packs"

Every session begins with the **doctor**, which checks everything at once and must end with
`0 FAILED`:

    & $py engine\doctor.py --quick       # about a minute; the full form (no --quick) runs the whole golden regression, 25 to 40 minutes

What it printed on 2026-10-11, the session that wrote this guide:

    PASS  env        Python 3.10.11 at C:\Users\joshk\OpenEvvBuild-ttsext\venv\Scripts\python.exe; stage C:\Users\joshk\OpenEvvBuild-ttsext\stage-dev
    PASS  harness    == 76 checks, 76 passed, 0 failed  (docs\tts-extension\harness\selftest.py --quick, 2 s)
    PASS  packs      Ran 22 tests in 13.391s  (engine\packs\test_packs.py, 14 s)
    PASS  packs      check: every file identical to languages/  (engine\packs\build_packs.py check, 14 s)
    PASS  validate   validate: 21 packs, 21 accepted, 0 rejected  (engine\packs\validate_packs.py, 12 s)
    ...
    PASS  coverage   coverage: 175 of 175 checklist entries done (mapped 67, composed 53, created 55); MISSING 0, BLOCKED 0; ...
    PASS  estimated  437 estimated values in the table, 437 queued in Q15 (written 2026-10-10)
    PASS  golden     golden: 6 packs, 28 cases, 0 FAILED, 0 changed within tolerance, 2 s
    doctor: 16 checks, 16 passed, 0 warnings, 0 FAILED (none), 61 s

What each line means: `env` the tools and the stage are there; `harness` the measuring code
measures known test signals correctly; `packs` every pack builds to exactly the files the product
ships; `validate` every dialect and accent pack documents who it describes and cites its sources;
`table` and `coverage` the master table of IPA sounds is consistent and every one of the 175 IPA
chart symbols is made and proved; `estimated` every guessed value is queued to be checked;
`golden` nothing the engine says has changed by accident.

## 2. Where packs live

| Folder | What | Shipped? |
|---|---|---|
| `packs/<tag>/` | the 162 packs the product has; `build_packs.py check` proves each builds to `languages/<tag>/` | yes, through `languages/` |
| `packs-proposed/<tag>/` | a real new language, dialect or accent, measured and waiting for the human's say-so | not until moved (section 8) |
| `docs/tts-extension/examples/packs/<tag>/` | the worked examples of this guide; TEST, private-use tags (`-x-evvdemo`) | never |
| `languages/<tag>/` | what the product reads: built from `packs/`, never edited by hand | yes |
| a scratch stage, `%TEMP%\OpenEvvTests\stage-<tag>` | a copy of the stage where a new pack is built and measured | never |

The pack tools find `packs-proposed/` and the examples through `EVV_PACKS_EXTRA` (setup above).
A pack there may `extends` a pack of `packs/`; it can never replace one.

## 3. Worked example: a language (`sw-x-evvdemo`)

Every language eSpeak NG can read already has a pack, so the example makes **Swahili again, from
scratch, under a test tag**. This is the path a really new language takes when eSpeak NG gains a
voice for it.

**Step 1: research.** For a real language: its sounds, stress or tone, spelling rules, recordings and
their licences, each source cited in `docs/tts-extension/REFERENCES.md` and registered in
`ipa/sources.toml`. (The example borrows Swahili's.)

**Step 2: start the pack from the eSpeak NG voice.** The generator picks the template module whose
sounds come closest to the language's, writes every sound, the melody and the tones, and the tool
proves the pack builds back to exactly what the generator wrote:

    & $py engine\packs\new_language.py bnt/sw sw-x-evvdemo --out docs\tts-extension\examples\packs --name "Swahili (worked example, TEST)"

    sw                     esex  Swahili                             87 sounds  0 tones late  register  tests
    1 packs written to C:\Users\joshk\AppData\Local\Temp\evv-newlang-ol23716l\languages
    sw-x-evvdemo: 67647 bytes of pack in docs/tts-extension/examples/packs\sw-x-evvdemo, identical to what the generator wrote (template esex)

(Its sounds came out line for line the same as the shipped Swahili pack's, `packs/sw`: only the tag,
the name and the list order differ.) A real language goes to `--out packs-proposed`.

**Step 3: look at the result.** Open `pack.toml`: `[engine]` names the reader (`espeak:bnt/sw`) and
the template (`esex`, the Castilian Spanish module); each `sound` line says how a sound differs from
the template's; each `map` line says which sound an eSpeak NG phoneme becomes. Add `review.toml`
(words and sentences for the native reviewer's packet).

**Step 4: build it into a scratch stage and listen with instruments.**

    $S="$env:TEMP\OpenEvvTests\demo-stage"; Copy-Item -Recurse "$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev" $S
    & $py engine\packs\build_packs.py build "$S\languages" sw-x-evvdemo
    $env:EVV_STAGE=$S
    & $py docs\tts-extension\harness\engine.py sw-x-evvdemo text "Habari ya asubuhi. Jina langu ni Amina." "$env:TEMP\OpenEvvTests\sw-demo.wav"

    sw-x-evvdemo           language.ini 7eb20285cb, sounds.map d74f8218d4, phonemes.map 604e4df8f9, sample.txt 4d172aaa99
    sw-x-evvdemo: 33253 samples at 11025 Hz, 3023 ms, 606 frames, 31 phones (trace): a b a R i y a a s u b u i # d i n a l a ng g u n i a m i n a #

The WAV can be played; the JSON beside it holds every frame and phone the engine made.

**Step 5: measure.** Record the new pack's own golden data (every phoneme it has, rendered and
measured) in a scratch folder, then judge it:

    & $py docs\tts-extension\harness\golden.py sw-x-evvdemo --record --golden "$env:TEMP\OpenEvvTests\demo-golden"
    & $py docs\tts-extension\harness\check_language.py sw-x-evvdemo --golden "$env:TEMP\OpenEvvTests\demo-golden" --asr --asr-like sw

    sw-x-evvdemo 134 cases  0 errors  0 not covered   16.8 s
    recorded 1 packs in 18 s; 0 not recorded
    sw-x-evvdemo CER 0.198  WER 0.750  (8 sentences, cuda/float16, 5 s)
    sw-x-evvdemo (Swahili (worked example, TEST)): 134 golden cases; module esex
    check A: pass; substituted 0; phones meant to sound 536, silent 0; formant and F0 checks 843 of 843
    check B: too few references (3/5 in range); references for 0 vowels; 3 needed
    ASR: CER 0.20 WER 0.75
    phonemes with no phone of their own: 2 f|h s|?
    level: 2 engine-verified; failure layer: unknown

How to read it: **check A** (the engine said what it was told: no sound swapped, none silent, every
vowel's formants and pitch where the frames asked) passes. **Check B** (the sounds within published
ranges for the language) cannot judge: there are no published Swahili vowel measurements in the
reference store. **ASR**: a speech recogniser (Whisper) understood the 8 test sentences with a
character error rate of 0.20; level 4 needs 0.15 or lower. So the level is **2, engine-verified**.
The same numbers as the shipped Swahili (`LANGUAGE_STATUS.md`): the copy measures like the original.
`--asr-like sw` borrows Swahili's test sentences because the test tag has none of its own; a real
new language adds its sentences (CC0 or CC BY, source recorded) to
`docs/tts-extension/harness/asr/sentences.json` and its Whisper code to `asr/whisper_codes.json`.
The two phonemes with "no phone of their own" (/h/ and the glottal stop) have no phone of the
Spanish module to stand for them: /h/ is heard only as breath on the vowel, the glottal stop as a
hush (`report.py`'s own description). A native reviewer should check both.

**Step 6: nothing else moved.** The other languages' golden regression, under the shared stage:

    $env:EVV_STAGE="$env:USERPROFILE\OpenEvvBuild-ttsext\stage-dev"
    & $py docs\tts-extension\harness\golden.py

For an example this is enough: the parent packs, which the example most nearly touches, and the
pack check:

    & $py docs\tts-extension\harness\golden.py sw ca ca-va en-us-nyc
    & $py engine\packs\build_packs.py check

    sw       134 cases  0 errors  0 not covered   27.5 s
    ca       158 cases  0 errors  0 not covered   32.9 s
    ca-va    158 cases  0 errors  0 not covered   34.2 s
    en-us-nyc 390 cases  0 errors  0 not covered   73.2 s
    golden: 4 packs, 840 cases, 0 FAILED, 0 changed within tolerance, 74 s
    packs checked: 162; files compared: 597 (5662611 bytes); by realization: legacy 145, module 17
    check: every file identical to languages/

A real new language runs the whole golden (every language, 25 to 40 minutes; `doctor.py` without
`--quick` does it too).

**Step 7: the review packet** for a native speaker (a web page with every word's audio, a
spectrogram described in words, and a form):

    & $py engine\review\make_packet.py sw-x-evvdemo --out docs\tts-extension\examples\packets\sw-x-evvdemo

    packet sw-x-evvdemo: 16 items (words 8, sentences 4, sounds 4); docs\tts-extension\examples\packets\sw-x-evvdemo; index.html 834332 bytes; folder 1482854 bytes
    items where the front-end or accent layer reported a loss: 1 (s-02)

Open `docs/tts-extension/examples/packets/sw-x-evvdemo/index.html` in a browser to see it. The words
and sentences come from the pack's `review.toml`. The flagged item is worth reading: in *mkuu* the
front-end put a short `e` before the syllabic m (`note schwa-inserted e before syllabic m`), because
the Spanish module has no syllabic m. A native reviewer should say whether that sounds acceptable.

**Step 8: status.** The pack's `[meta] status` and, for a real language,
`docs/tts-extension/LANGUAGE_STATUS.md`, get the true level (2 here). A test pack records nothing there.

## 4. Worked example: a dialect that inherits (`ca-va-x-evvdemo`)

A dialect pack `extends` its parent and holds **only what differs**. The example extends Valencian
(`ca-va`, itself a child of Catalan, `ca`) with the stressed open vowel /ɛ/ of one published group
of Valencian speakers.

**The evidence.** Jiménez and Marí (2019), Table 1 (after Escrivà 2014): 8 men of Albalat de la
Ribera, 24 tokens a vowel, mean F1 and F2 at the vowel's middle, Hz: i 360/2123, e 504/1847,
ɛ 652/1689, a 713/1308, ɔ 643/1038, o 494/963, u 393/874. The source is registered
(`ipa/sources.toml`, `jimenez2019`, opened, CC BY-NC-ND 4.0: the numbers are cited, nothing is copied).

**Size, not accent.** Men's and women's voices, and the engine's voice, differ in size; a pack holds
the *pattern* of a dialect's vowels, and the voice adds the size (`docs/tts-extension/AUTHENTICITY.md`
section 3). The normalizer puts the table at the size of the engine's Spanish module (Nearey's shared
log-mean over the vowels both have as plain phones, `--anchor`) and compares each vowel with what the
pack says now. Each value is keyed by the eSpeak NG phoneme the reader writes (`@ca-va:E` is
Valencian /ɛ/; `espeak-ng --path=dist -v roa/ca-va -q -x "terra"` shows the names):

    & $py engine\authenticity\normalize.py ca-va i=360,2123 e=504,1847 a=713,1308 o=494,963 u=393,874 @ca-va:E=652,1689 @ca-va:O=643,1038 --anchor i,e,a,o,u

    ca-va: module esex; factor x0.9089 over a e i o u (f1 f2)
      i            phone i   target 327.2 / 1929.6   now 280.0 / 1920.0   change F1 +16.9% F2 +0.5%   override
      e            phone e   target 458.1 / 1678.8   now 480.0 / 1800.0   change F1 -4.6% F2 -6.7%   override
      a            phone a   target 648.1 / 1188.9   now 660.0 / 1400.0   change F1 -1.8% F2 -15.1%   override
      o            phone o   target 449.0 / 875.3   now 480.0 / 900.0   change F1 -6.5% F2 -2.7%   override
      u            phone u   target 357.2 / 794.4   now 300.0 / 750.0   change F1 +19.1% F2 +5.9%   override
      @ca-va:E     phone e   target 592.6 / 1535.1   now 556.8 / 1800.0   change F1 +6.4% F2 -14.7%   override
      @ca-va:O     phone o   target 584.4 / 943.4   now 556.8 / 900.0   change F1 +5.0% F2 +4.8%   within 6%

An override is written only where F1 or F2 moves more than 6 per cent (the rule `extract_targets.py`
uses too: measurement changes only what it shows to differ), so /ɔ/ stays as it is. The example
writes /ɛ/ alone to stay small; a real Valencian pack from this table would also override
/i e a o u/, which differ as much. A rule turned the published value into the target, so the tag is
`derived`, with the source as its `ref` and the rule in `norm`.

**The pack** (`docs/tts-extension/examples/packs/ca-va-x-evvdemo/pack.toml`, in full in the tree):

    [pack]
    tag = "ca-va-x-evvdemo"
    kind = "dialect"
    extends = "ca-va"
    [meta]
    variety = "TEST ONLY (...): Valencian Catalan with the stressed open vowel /ɛ/ of the men of Albalat de la Ribera ..."
    region = "Albalat de la Ribera (Ribera Baixa), Valencian Community, Spain"
    speaker_group = "8 men of Albalat de la Ribera recorded by Escrivà (2014), as tabulated by jimenez2019 (Table 1); ..."
    sources = ["eSpeak NG voice roa/ca-va", "jimenez2019"]
    recordings = []
    date = "2026-10-11"
    status = { level = 2, validated_by = "", date = "" }
    [ini.Language]
    Tag = "ca-va-x-evvdemo"
    Name = "Catalan (Valencian, worked example, TEST)"
    Order = "990"                     # its place in the voice list: any number no other pack uses
    [[override]]
    sound = "ɛ"
    phonemes = ["@ca-va:E"]
    state = "proposed"
    [override.formants.f1]
    v = 592.6
    tag = "derived"
    ref = "jimenez2019"
    n = 24
    speakers = 8
    norm = "652 Hz x0.9089: Nearey shared log-mean over i e a o u (F1, F2) of Table 1 against module esex's phones (normalize.py)"
    [override.formants.f2]
    ...                               # 1535.1, the same way

Everything else (every other sound, the melody, the reader, the licence) comes from `ca-va` and `ca`;
`build_packs.py explain ca-va-x-evvdemo <key>` says which pack a value came from. `state = "proposed"`
means the override is measured and shown, but not yet in what ships. Beside it, `review.toml` names
the words for the packet and, per overridden sound, the words `show_effect.py` measures (`[[check]]`).

**Validate** (the authenticity rules: who the dialect describes, a registered and opened source, no
`estimated` value, nothing pushed past its evidence):

    & $py engine\packs\validate_packs.py ca-va-x-evvdemo

    ca-va-x-evvdemo        accepted
    validate: 1 packs, 1 accepted, 0 rejected

**Measure the override's effect** (the pack built into the scratch stage without it, as it would ship
today; `show_effect.py` makes the version with it, and reads each word's vowel, F1 and F2 as asked by
the frames and as measured in the sound):

    $env:EVV_STAGE="$env:TEMP\OpenEvvTests\demo-stage"
    & $py engine\packs\build_packs.py build "$env:EVV_STAGE\languages" ca-va-x-evvdemo
    & $py engine\authenticity\show_effect.py ca-va-x-evvdemo

    ca-va-x-evvdemo: each word's vowel at its middle, preset 1 (adult male); asked = the frames, meas = the sound
      IPA  word     target F1/F2    before: asked (meas)            after: asked (meas)             after vs target (asked)
      ɛ    terra      593 /  1535     581 ( 581) /  1800 (1789)       611 ( 613) /  1562 (1560)     F1  +3.1%  F2  +1.8%
      ɛ    cel        593 /  1535     557 ( 554) /  1800 (1792)       590 ( 589) /  1530 (1535)     F1  -0.4%  F2  -0.3%
    largest distance from the target (F1 or F2, asked): before median 17.3%, after median 1.8% (2 words)
    preset 2 against preset 1 (F1, F2 asked): the voice's own scaling, the same with and without the override
      ɛ    terra    before x1.177 / x1.210   after x1.178 / x1.210
      ɛ    cel      before x1.099 / x1.210   after x1.100 / x1.210
    largest difference between the two versions' preset-2 ratios: 0.001

The proposed override brings the vowel from 17.3 to 1.8 per cent of the published target, and the
female voice (preset 2) scales it exactly as it scales the parent's: the pack moved the pattern, the
voice kept the size.

**Its own checks, and the parent untouched:**

    & $py docs\tts-extension\harness\golden.py ca-va-x-evvdemo --record --golden "$env:TEMP\OpenEvvTests\demo-golden"
    & $py docs\tts-extension\harness\check_language.py ca-va-x-evvdemo --golden "$env:TEMP\OpenEvvTests\demo-golden" --asr --asr-like ca-va

    ca-va-x-evvdemo 158 cases  0 errors  0 not covered   20.9 s
    ca-va-x-evvdemo CER 0.158  WER 0.329  (8 sentences, cuda/float16, 6 s)
    check A: pass; substituted 0; phones meant to sound 601, silent 0; formant and F0 checks 973 of 974
        s|?: a F0 measured None, frames 127.15
    check B: too few references (3/5 in range); references for 0 vowels; 3 needed
    ASR: CER 0.16 WER 0.33
    level: 2 engine-verified; failure layer: unknown

Built again with `--proposed` (the override in) and recorded into another folder, the same checks
print the same lines: check A 973 of 974, CER 0.158. The one reading missed: in the glottal-stop case
`s|?`, the pitch tracker found no pitch on the vowel `a` where the frames asked for 127 Hz; the parent
`ca-va` has the same case. Without the override the example is Valencian itself, and measures so:
`check_language.py ca-va --asr` on the same stage printed the same CER 0.158 and WER 0.329. And
Valencian itself is untouched: `golden.py ca ca-va` in section 3, 0 FAILED.

**Packet**: `make_packet.py ca-va-x-evvdemo --out docs\tts-extension\examples\packets\ca-va-x-evvdemo`.
Its A/B items are blind: each word said with and without the override, the listener not told which.

    packet ca-va-x-evvdemo: 14 items (words 6, compare 4, sounds 4); docs\tts-extension\examples\packets\ca-va-x-evvdemo; index.html 486177 bytes; folder 862389 bytes

The 4 "compare" items are the A/B pairs (two words, each said twice); the key that says which is
which is kept outside the packet, in `docs/tts-extension/review/keys/ca-va-x-evvdemo.json`.

## 5. Worked example: an accent (`en-us-x-evvdemo-es`)

An accent is a target language spoken with features of a group of speakers, usually from their first
language. It is described from measurements of real speakers, never performed. The example carries
**one** measured feature of adult native speakers of Mexican Spanish speaking American English: the
KIT vowel (as in *bit*) nearer to FLEECE (*beat*) in quality.

**The evidence.** Sidaras, Alexander and Nygaard (2009), Table 3: 12 native speakers of Mexican
Spanish (6 men, 6 women, in the Atlanta area) and 6 native English speakers, measured alike. KIT:
English 526.87 / 2079.26 Hz, Spanish speakers 392.07 / 2395.58 Hz (lower F1, higher F2: closer to
FLEECE). FLEECE and the vowel lengths differ by less than 6 per cent (the paper: these speakers keep
the length difference), so no override is written for them. The two groups are of similar make-up,
so the accent is carried by the **ratio** (F1 x0.7442, F2 x1.1521), applied to the pack's own KIT
(386 / 1785 Hz): 287.2 / 2056.6 Hz, tagged `derived`.

**The target.** Overrides need a pack whose sounds are written out (`realization = "legacy"`); the
native US English module (`enus`) cannot take them. The only American English pack that can is New
York City's (`en-us-nyc`), so the example extends it and says so in its notes: the rest of the
accent's target is NYC English, which the source's speakers did not speak.

**The pack**: `kind = "accent"`, `extends = "en-us-nyc"`, `[meta]` naming the speaker group as the
source describes it, and in its note **what it does not make**: every other feature of a Spanish
speaker's English. One override, `sound = "ɪ"`, `phonemes = ["@en-us-nyc:I"]`, F1 287.2 and F2 2056.6
(`docs/tts-extension/examples/packs/en-us-x-evvdemo-es/pack.toml`).

    & $py engine\packs\validate_packs.py en-us-x-evvdemo-es
    en-us-x-evvdemo-es     accepted
    validate: 1 packs, 1 accepted, 0 rejected

    & $py engine\packs\build_packs.py build "$env:EVV_STAGE\languages" en-us-x-evvdemo-es
    & $py engine\authenticity\show_effect.py en-us-x-evvdemo-es
      IPA  word     target F1/F2    before: asked (meas)            after: asked (meas)             after vs target (asked)
      ɪ    bit        287 /  2056     398 ( 401) /  1754 (1751)       295 ( 281) /  2017 (2004)     F1  +2.7%  F2  -1.9%
      ɪ    sit        287 /  2056     402 ( 404) /  1744 (1742)       297 ( 287) /  2006 (1997)     F1  +3.4%  F2  -2.5%
    largest distance from the target (F1 or F2, asked): before median 39.2%, after median 3.0% (2 words)
    largest difference between the two versions' preset-2 ratios: 0.002

Its checks, without and then with the override:

    check A: pass; substituted 0; phones meant to sound 1452, silent 0; formant and F0 checks 2300 of 2306
    check B: pass 82/94                    (with the override: pass 81/94)
    ASR: CER 0.01 WER 0.04                 (with the override: CER 0.00 WER 0.02)
    level: 4 intelligibility-verified; failure layer: none

Check B compares with **native** American English ranges, so an accent is expected to move one value
out of them (KIT): 82 became 81 of 94, and that is the accent working, not a fault. The recogniser
still understands every sentence. (The six check-A readings that miss are New York City's nasalized
vowels, the same in the parent `en-us-nyc`.) Packet: 36 items, 4 of them the blind A/B pairs of
*bit* and *sit*. The level of a real accent pack would still need a native reviewer from the speaker
group to go further, and its notes list everything it does not make.

## 6. The commands, one line each

PowerShell, repository root, after the setup lines of section 1. `<S>` is a scratch stage, `<G>` a
scratch golden folder.

| What | Command |
|---|---|
| Health of everything | `& $py engine\doctor.py [--quick]` |
| Start a language pack | `& $py engine\packs\new_language.py <voice> <tag> --out packs-proposed --name "<Name>"` |
| Validate a pack (authenticity rules) | `& $py engine\packs\validate_packs.py <tag>` |
| Build a pack into a stage | `& $py engine\packs\build_packs.py build <S>\languages <tag> [--proposed]` |
| Which pack gave a value | `& $py engine\packs\build_packs.py explain <tag> <dotted key>` |
| **Render** text or IPA to a WAV (+ JSON) | `& $py docs\tts-extension\harness\engine.py <tag> text\|ipa "<input>" <out.wav> [--preset N]` |
| **Measure**: record a new pack's golden data | `& $py docs\tts-extension\harness\golden.py <tag> --record --golden <G>` |
| **Measure**: checks A, B, ASR, level | `& $py docs\tts-extension\harness\check_language.py <tag> [--golden <G>] [--asr] [--asr-like <tag>]` |
| **Measure**: an override's effect | `& $py engine\authenticity\show_effect.py <tag>` |
| Measure targets from aligned recordings | `& $py engine\authenticity\extract_targets.py <tag> <corpus> [--write]` |
| **Regress**: every language unchanged | `& $py docs\tts-extension\harness\golden.py` (under the shared stage; 0 FAILED) |
| **Regress**: one language | `& $py docs\tts-extension\harness\golden.py <tag>` |
| **Review packet** | `& $py engine\review\make_packet.py <tag> [--out <folder>]` |
| Record a reviewer's answers | `& $py engine\review\ingest_feedback.py <feedback.toml>` |
| Every language's status page | `& $py docs\tts-extension\harness\report.py` (rewrites `LANGUAGE_STATUS.md`) |

## 7. The status ladder

| Level | Name | Earned by |
|---|---|---|
| 1 | draft | the pack builds |
| 2 | engine-verified | check A: the engine says what it is told, nothing swapped or silent |
| 3 | reference-verified | check B: the sounds fall in published ranges for the language |
| 4 | intelligibility-verified | a speech recogniser understands the test sentences (character error 0.15 or lower) |
| 5 | native-validated | a named native speaker signed the review packet (`ingest_feedback.py`) |

Only level 5 may be called **authentic**. A level is never raised without its evidence shown.

## 8. Shipping a pack

Moving a pack into the product changes what users hear, so it waits for the human's say-so
(playbook R18). Then: move `packs-proposed/<tag>` to `packs/<tag>`; for an override, set
`state = "applied"`; build `languages/<tag>/` (`build_packs.py build languages <tag>`); `build_packs.py
check` must then say every file is identical; record the new pack's golden (`golden.py <tag>
--record-new`, and under the stage); run the doctor; record the decision in
`docs/tts-extension/DECISIONS.md`. The installer picks up `languages/` at the next release.

## 9. Improving, diagnosing, creating a missing sound

- **Improve** a language (`/improve-language <tag>`): start from its failure layer in
  `LANGUAGE_STATUS.md`, re-measure first, change only that layer, re-measure, and run the whole
  golden regression: one language's fix must never break another.
- **Diagnose** (`/diagnose-language <tag> <symptom>`): turn a listener's words into hypotheses (wrong
  sound values, wrong reading of the spelling, stress or tone, timing, voice, an engine fault) and
  measurements that tell them apart; it proposes a fix and changes nothing.
- **Create a missing sound** (`/create-missing-sound <symbol>`): the Unmappable Sound Protocol of the
  playbook (1.6): try composing it from a base and marks, then a near neighbour, then a new
  engine capability; design it with sourced values, render and measure it in several vowel
  contexts, register it in `docs/tts-extension/CREATED_SOUNDS.md` with a number that never changes.

**Each skill was tested in Phase 8** on a small real task by a helper that knew only the skill's own
text (`docs/tts-extension/DECISIONS.md` D92 has the details, the skills were corrected from what the
helpers found):

| Skill | Task | What it showed |
|---|---|---|
| `/add-language` | Esperanto made again from its voice, `eo-x-evvskill` (TEST) | check A pass (558 sounds, 0 silent), check B and ASR cannot judge (Whisper has no Esperanto), level 2, as the shipped `eo`; found a crash in `make_packet.py` (fixed) |
| `/add-dialect` | Catarroja women's /ɛ ɔ/ over Valencian, `ca-va-x-evvskill` (TEST), from jimenez2019 Table 5 | both vowels moved past 6 per cent; median distance from the target 15.6 % before, 1.7 % after; parent golden 0 FAILED |
| `/add-accent` | Mexican Spanish speakers' TRAP over NYC English, `en-us-x-evvskill-es` (TEST), from sidaras2009 | 8.7 % before, 4.4 % after; check A pass; target golden 0 FAILED |
| `/improve-language` | Valencian (`ca-va`, real): published vowel ranges for check B | check B from "too few references" to FAIL 21/29 (the open vowels' F1 low); level 2 unchanged; found that the ranges reach the other Catalan varieties too (`OPEN_QUESTIONS.md` Q46) |
| `/diagnose-language` | Swahili (`sw`, real): word error 0.75 against character error 0.20 | mostly the metric on long words; the main boundary fault an inserted "ya" at vowel-to-vowel junctions between words (`OPEN_QUESTIONS.md` Q45, a fix proposed, nothing changed) |
| `/create-missing-sound` | ɓ̥, the voiceless bilabial implosive (beyond the chart) | composition (ɓ with the voiceless ring) gave only a devoiced b, so the sound was **created**: CS-0076, a Tier C entry, b with its voice off over the first 70 per cent of the closure and then the implosive's swell (after the one acoustic study, a 20 to 50 ms silence then prevoicing); measured 47 % voiced with a 40 ms gap, distinct from ɓ (100 %, no gap) and from p (23 %, 95 ms); every proof re-said, coverage MISSING 0, golden 155 packs 0 FAILED; two values `estimated`, queued in Q15. `engine/ipa/say_ipa.py` came from this test |

## 10. What cannot be done yet

- **A language eSpeak NG cannot read.** Every pack is read by an eSpeak NG voice; a reader written in
  the pack itself is designed (`DESIGN.md` 8.2, L5) but not built.
- **Accent and dialect rules beyond vowel targets.** An override moves a vowel's formants and length.
  Swapping one phoneme for another, devoicing, inserting a vowel, mergers, rhythm: no sourced pack
  mechanism yet (`DESIGN.md` 8.3, L2 and L4). List such features in the pack's note as not made.
- **Overrides on the native modules** (US and British English, German, Spanish, French, Italian,
  Japanese, Polish and the rest): they have no written-out sound lines, so no override; use a legacy
  pack of the language as the parent.
- **A test of a language without recogniser support**: Whisper lacks some languages; their packs stop
  at level 3 until a native reviewer listens.

## 11. Common mistakes

- **Putting a new pack in `packs/`** before it ships: `build_packs.py check` then fails (no
  `languages/<tag>/`). Use `packs-proposed/`.
- **Building into the shared stage** (`stage-dev`): every later golden run then fails on the new
  pack. Copy the stage and build there.
- **A Hz value straight from a paper** into an override without normalizing for speaker size, or a
  women's table against the male module: normalize (section 4) or use a ratio between groups
  measured alike (section 5).
- **Tagging a dialect's value `estimated`**: refused by the validator. Find a source or measure.
- **Hand-editing `[sounds]` lines in a dialect**: the validator cannot see it, and it hides a claim
  without provenance. Use an `[[override]]`, or list the feature as not made.
- **Calling a language "authentic"** below level 5, or raising a level without its measurement.
- **`asr.py <tag>` for a test pack**: it writes the tracked `results/asr.json`. Use
  `check_language.py --asr`, which writes nothing.
- **Comparing with an old number**: `check_language.py` without `--asr` reads `results/asr.json`, measured
  on 2026-10-05 with the shipped modules (ca-va's CER there is 0.12; on today's stage it is 0.158). Run
  `--asr` on both sides of any comparison.
- **`a3.py <tags>`** overwrites `results/a3-staged.json` with only those tags: back it up first.
- **Deleting anything** (build folders, renders, models) before the project's Phase 10 is complete:
  not allowed (playbook R20).
