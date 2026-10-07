# Open questions

Things only the human or a native speaker can answer. Each has a recommended default so work is never blocked on it.

## For the human

**Q1. The permissions file `.claude/settings.json` was not created (Phase 0, step 4b).** Claude's write to it was refused by the app's own safety check ("self-modification": Claude may not change its own permission settings in Auto mode). This is the right behaviour and Claude did not work around it. If you want it, create the file yourself with the content below, or tell Claude in chat to create it and approve the prompt. *Recommended default: create it; without it you are asked more often, and nothing else changes.*

What it does, in plain English: lets the build, test, speak-to-WAV and inventory commands, and `git add` / `git commit`, run without asking each time; refuses force-pushes, `git reset --hard` and recursive deletes always (a refusal beats an allowance). It does not allow `git push`, so pushing still asks you.

```json
{
  "permissions": {
    "allow": [
      "PowerShell(cmake *)",
      "PowerShell(git add *)",
      "PowerShell(git commit *)",
      "PowerShell(git status *)",
      "PowerShell(git diff *)",
      "PowerShell(git log *)",
      "PowerShell(python docs\\tts-extension\\*)",
      "PowerShell(python engine\\accent\\*)",
      "PowerShell(python engine\\check_espeak_packs.py *)",
      "PowerShell(python openevv\\tools\\module\\phonemes.py *)",
      "PowerShell(.\\build_x64\\bin\\Release\\evv_say.exe *)",
      "PowerShell(.\\build_x86\\bin\\Release\\evv_say.exe *)",
      "PowerShell(.\\build_x64\\bin\\Release\\sapi_test.exe *)",
      "PowerShell(.\\build_x86\\bin\\Release\\sapi_test.exe *)",
      "PowerShell(.\\dist\\x64\\OpenEvvFrontend.exe *)"
    ],
    "deny": [
      "PowerShell(git push --force*)",
      "PowerShell(git push -f*)",
      "PowerShell(git push * --force*)",
      "PowerShell(git push * -f*)",
      "PowerShell(git reset --hard*)",
      "PowerShell(Remove-Item * -Recurse*)",
      "PowerShell(Remove-Item -Recurse*)",
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(git reset --hard*)",
      "Bash(rm -r*)",
      "Bash(rm -fr*)",
      "Bash(rm * -r*)"
    ]
  }
}
```

**Q2. Should the playbook and these handoff files be pushed to GitHub?** They are committed on the local branch `tts-ext/phase-0` only. The repository is public. *Recommended default: keep the branch local until Phase 2's design is approved.*

**Q3. Licence of the language data (flag, not a blocker).** The modules' language data is IBM's and is not licensed to this project (`NOTICE.md`). Extending the engine does not change that, but it shapes where new work should go. *Recommended default: put all new sound definitions in files of our own under MIT (the accent layer and new tables), and do not add to IBM's rule files more than is unavoidable. Phase 2 will propose this formally.*

**Q4. Is a second machine or CI wanted?** Everything was built and run on one Windows 11 PC. *Recommended default: no; one machine is enough until Phase 8.*

## For Phase 1 (Claude can answer these by measuring)

- The modules built from source today are not byte-identical to the DLLs in `languages/` (different hashes; the 64-bit English one has the same size). Is their audio identical? Nothing may be concluded until both are rendered and compared.
- openevv's own gate, `test/matrix.sh` (979 cases), has not been run on this machine. Can it run under MSYS2 as its script suggests?
- `engine/accent/probe.py` needs `probe-<tag>.exe` and names a build script that is not in the repository (`engine\build_probes.cmd`). How were the probes built?
- The engine's second utterance on one instance differs from its first (documented, deterministic). The golden regression must render each case on a fresh instance or with the same history.

## About the chart itself

- **The rising-falling contour tone letter.** The IPA's symbol list gives levels 3-4-2 (`U+02E7 U+02E6 U+02E8`) and the checklist records that; in the Kiel typeface of the chart PDF the glyph looks as if it could end at level 3. Other sources give 2-4-2 and 4-5-4 for the same IPA number (533). *Default: accept any rise-then-fall sequence of tone letters as this tone; the exact levels are the transcriber's.*
- **ʡ (epiglottal plosive):** the chart gives no voicing; Unicode calls it voiced, descriptive sources voiceless. *Default: voiceless.*
- **ʢ:** the chart says fricative; the IPA's symbol list says fricative/approximant. *Default: design it as the chart says and note the variant.*
- **ɧ:** the chart says "simultaneous ʃ and x"; descriptions of Swedish vary and doubt true double friction. *Default: follow the chart's definition, mark `approximate`, queue for a Swedish speaker.*
- **The tie bar below and the linking mark** share IPA number 509 in the sources read. They are different characters (`U+035C`, `U+203F`) and separate entries here.

## For native speakers and experts (none needed yet)

Nothing can be validated by ear until Phase 7 produces review packets. Languages will be queued here as their sounds are marked `approximate`.

## Added in Phase 1 (2026-10-05)

**Q5. A Stop hook, so that a Claude turn cannot end while the harness's smoke check fails (playbook Phase 1, step 8).** The script is `harness/stop_hook.py`. In plain English: when Claude is about to finish a turn, it looks at whether anything under `openevv/`, `languages/`, `engine/`, `frontend/` or `dist/espeak-ng-data/` has uncommitted changes. If nothing there changed (almost always), it does nothing. If something did, it runs the one-minute smoke check, and if that fails, Claude is told why and keeps working instead of stopping. It never blocks twice in a row, so it cannot loop. Claude may not change its own settings, so if you want it, add this to `.claude/settings.json` (create the file if Q1's content is not there yet; merge the `hooks` key into it if it is). *Recommended default: add it before Phase 3, the first phase that changes the engine; it costs nothing until then.*

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/docs/tts-extension/harness/stop_hook.py\"",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

(Checked against https://code.claude.com/docs/en/hooks.md on 2026-10-05: a Stop hook blocks with exit code 2 and its stderr; `stop_hook_active` is true on a forced continuation; commands run in bash on Windows.)

**Q6. Should the shipped native modules be rebuilt with the accent layer's text filter?** Nine of the ten native modules (all but US English) speak the accent markup aloud instead of reading it (`DECISIONS.md` D13). It does not affect users today: the product never sends markup to a native module. It matters for Phase 2/3 if native languages are to get accents or new sounds the way the eSpeak NG packs do. Rebuilding overwrites the DLLs in `languages/`, which needs your say-so. *Recommended default: decide in Phase 2's design; nothing is rebuilt now.*

**Q7. ASR for the 46 languages Whisper does not know.** Meta's Omnilingual ASR (Apache 2.0, 1,600+ languages) would cover about 30 of them but needs WSL2 (Linux on Windows) and a model download of a few GB. Meta MMS is non-commercial (CC BY-NC) and is not proposed. *Recommended default: leave them "ASR unavailable" until Phase 7 (the native-validation pipeline), then decide.*

## Added in Phase 2 (2026-10-05)

**The five questions of the design** are in `DESIGN.md` section 14, with the answers given (`DECISIONS.md` D34). Q6 above (rebuilding the native modules) is question 4 there and is **answered: yes, when proven**. Q11 below is question 5 and is **answered: fixed first thing in Phase 3**.

**Q8. The 32-bit US English module is older than the 64-bit one.** `languages/enus/openevv-enus-x86.dll` is still the 1.0.0 file; the 64-bit one was rebuilt for 1.2.3 and contains the accent layer, the 32-bit one does not (`DECISIONS.md` D30). No user is affected today: the product never sends the accent layer's markup to a native module, and in Phase 0 the two gave the same sound for the same sentence. It matters only if US English is ever to be given accents through the layer, and then 32-bit programs would hear the markup read aloud. *Recommended default: nothing now; rebuild both together with the other nine native modules if and when question 4 is answered yes, with the proof `DESIGN.md` 11.3 (M5) asks for.*

**Q9. Natural recordings to judge the recogniser by (for Phase 7).** `DESIGN.md` 10.3 proposes that a language may also pass the speech-recognition check if its error is close to the same recogniser's error on *natural* recordings of the same sentences. Common Voice's recordings are CC0, but they are a download of some size, behind Mozilla's terms. *Recommended default: decide in Phase 7; until then the one pass mark of 0.15 stands.*

**Q11 (answered 2026-10-05: option (b), first thing in Phase 3). A defect in the released product: voiceless sounds and pauses are voiced after certain stops.** Found by the reviewer of the design and measured (`DESIGN.md`, "A defect found on the way"; `DECISIONS.md` D33). In the 145 languages read by eSpeak NG, a stop whose sound carries a voice-onset or a breathy-release setting switches the voice on afterwards even when a voiceless consonant or a pause follows: Russian "кто" comes out with its t voiced, and a sentence ending in such a stop is followed by a voiced sound through the whole pause (about half a second at default settings; shortened-pause settings hide most of that part). It is most frequent where the plain p, t and k carry the setting: 61 of the 87 languages spoken through the German-based module, and the two spoken through the American English one. The ten native languages are not affected. Claude cannot hear it; the frames and the signal level say so. You speak American English: one voice you could check by ear is "OpenEVV English (America, New York City)", with a short sentence ending in t, p or k, pause shortening off.

The fix is a few lines in the accent layer, but it ships only in rebuilt template modules (fourteen files in `languages/`), and it changes what those languages say, for the better. Two ways: **(a)** fix it at once on `main` as a release of its own (1.2.5), in a separate session; **(b)** fix it as the first act of Phase 3 and release it whenever the next release is made. *Recommended default: (b), unless users are already complaining, because (b) costs nothing extra and the proof (the module baseline, the new check, the golden recorded again) is the first work of Phase 3 anyway. Either way nothing is rebuilt without your say-so.*

**Q10. Should the handoff files and the design be pushed to GitHub?** Still local (Q2). *Recommended default, unchanged: after the design is approved, push the `tts-ext/*` branches if you want them backed up; they change nothing in the released product.* **Answered 2026-10-06: yes.** The five branches `tts-ext/phase-0` to `tts-ext/phase-4` were pushed to `origin` as new branches (no force, no tags; `main` untouched). Q2 is answered with it.

### For Phase 3 (found by reading and measuring in Phase 2; Claude can act on these)

- The golden lists 15 module phones as `not_covered` because their names hold `:` or `~`. They can be written in single quotes (D30). Cover them and re-record those packs.
- The tone key `av` is parsed by the accent layer and never applied; eight tone lines of the two Mandarin packs carry it. Apply it or remove it (defect X-2 of `DESIGN.md` 4.4).
- The map keyword `may` is parsed and not documented; `tonename` is documented and used by no pack; `docs/SOUNDS.md` documents no limit (64 vowels, 32 glides, 8 phones an entry, 1,023-byte lines, 7-letter phone names, 11-letter ids).
- `openevv/test/matrix.sh` has still not been run on this machine. Its scripts say they support MSYS2 (`make win-probe`, then `EVV_MATRIX_NATIVE=build/probe-<langs>.exe`). Try it before the first change under `openevv/src`.
- The chassis files (`engine/accent/chassis/*.json`) do not record the voice they were measured with, and the script that built the measuring programs (`engine\build_probes.cmd`) is not in the repository. The adapter needs them re-measured with the voice written down.

### Carried forward, not design questions

The three findings below (Quechua's silent vowel, Western Armenian's /p t/, the English diphthong cases) are faults or doubts in single packs. The design does not settle them; they belong to Phase 4 (the sounds) and Phase 6 (triage).

## Added in Phase 3 (2026-10-05)

**Q12 (fixed 2026-10-06, `DECISIONS.md` D51: in `engine/build_modules.sh`, as recommended). A template module cannot be built in a fresh folder without its parent** (`DECISIONS.md` D36). `itix` and `esex` fail because `tools/module/clone.py` copies a file (`lang/<parent>/rules/constants.letters`) that only a build of the parent writes. Release builds are not affected: `engine/build_modules.cmd` builds every language, parents first. A one-line fix, in `engine/build_modules.sh` (run `python3 tools/rules/letters.py write <parent>` before `clone.py` when `lang/<parent>/letters` exists) or in `clone.py` itself, would make each template buildable alone. *Recommended default: make the fix in `engine/build_modules.sh` (ours, MIT) in Phase 3, prove it by building one template in a fresh folder, and leave `openevv/tools` as it is.*

**Q13. A stop's `vot` can lengthen the voice onset but not shorten it** (found 2026-10-06 by the C3 loop, `DECISIONS.md` D47). On the German-based module (staged, fixed), /t/ between two a's, with the sound key `vot` set to nothing, 0, 15, 40, 60 and 90 ms, the harness measured a voice onset of 34, 34, 34, 48 and 66 ms (and none found at 90). The accent layer's own comment says an onset earlier than the module's "is begun sooner" (`evv_accent.c`, the release of the stop), but nothing moves below the module's own 34 ms. 256 sound definitions in 70 packs ask for a `vot` under 30 ms (Hindi's plain t has `vot=15`), so those packs ask for a short-lag stop and, where the module's own onset is longer, do not get one. It may be a defect (the branch that begins the voice sooner never acts), or the branch may act on frames the measurement does not see; which one is not yet known. Fixing it would change what those packs say, so it is a third listed defect only once it is understood, and then shown to you and approved like X-1. *Recommended default: Claude diagnoses it at the start of Phase 4 (frames against the trace, one case), reports which it is, and proposes a fix to approve; meanwhile the master table's stops are not proved through `vot` below the module's own onset.* **Diagnosed 2026-10-06 (D60): not reproduced; no fix needed.** /t/ between a's, the German-based module, the harness's own measure: with no `vot` 40 ms (38 on the Phase 3A stage), `vot=5` 14 ms, `vot=15` 18 ms, `vot=40` 40 ms, on the development stage and on the 3A stage alike; the frames show the module's burst in the stop's own span (145 to 160 ms) and the voice begun where `vot` says. The table's t (`vot=15`) measures 18, 16 and 12 ms between a, i and u. The shortest onset this layer gives is about 14 ms (the burst and the voice's 15 ms rise), under every literature value of a plain voiceless stop in the table. Why the C3 loop read 34 ms for every value below 34 was not found; its runs are not reproducible from what was kept.

**Q14. The accent layer does not report phones the markup asked for that are never placed** (the R15 review of 3A, `DECISIONS.md` D52). `phone-unsounded` covers a phone passed over before a later one is matched; one still in the queue when the text ends or is stopped is dropped with the queue and not reported. *Recommended default: Claude adds the report (at the queue's end, saying whether the text ended or was stopped) at the next rebuild of the template modules, which Phase 4 needs anyway for the first mechanism of 3B, and counts it over the golden then.*

## Added in Phase 4 (2026-10-06)

**Q15. The verification queue: every `estimated` value in the master table** (playbook Phase 4: "estimated values in OPEN_QUESTIONS.md"; `DESIGN.md` 3.2). Each is a value no opened source gave; its note in `ipa/table/*.toml` says what it rests on. A measured or published value for any of them replaces it (`DESIGN.md` 5: the tag becomes `literature`, the revision goes up, the proof is run again). Written by `python engine/ipa/table.py`'s validator; 157 values on 2026-10-06 (regenerated after D64):

- `U+0071` q: `spec.locus.F1`
- `U+0071` q: `spec.vot_ms`
- `U+0078` x: `spec.noise.peak_hz`
- `U+00E7` ç: `spec.noise.peak_hz`
- `U+00E7` ç: `keys.a5`
- `U+01C0` ǀ: `spec.vot_ms`
- `U+01C0` ǀ: `keys.burstms`
- `U+01C0` ǀ: `keys.ej`
- `U+01C0` ǀ: `keys.bgain`
- `U+01C0` ǀ: `keys.hold`
- `U+01C0` ǀ: `keys.a2`
- `U+01C0` ǀ: `keys.a3`
- `U+01C0` ǀ: `keys.a4`
- `U+01C0` ǀ: `keys.a5`
- `U+01C0` ǀ: `keys.a6`
- `U+01C1` ǁ: `keys.ej`
- `U+01C1` ǁ: `keys.burst`
- `U+01C1` ǁ: `keys.bgain`
- `U+01C1` ǁ: `keys.a2`
- `U+01C1` ǁ: `keys.a3`
- `U+01C1` ǁ: `keys.a4`
- `U+01C1` ǁ: `keys.a5`
- `U+01C1` ǁ: `keys.a6`
- `U+01C2` ǂ: `spec.vot_ms`
- `U+01C2` ǂ: `keys.burstms`
- `U+01C2` ǂ: `keys.ej`
- `U+01C2` ǂ: `keys.burst`
- `U+01C2` ǂ: `keys.bgain`
- `U+01C2` ǂ: `keys.a2`
- `U+01C2` ǂ: `keys.a3`
- `U+01C2` ǂ: `keys.a4`
- `U+01C2` ǂ: `keys.a5`
- `U+01C2` ǂ: `keys.a6`
- `U+01C3` ǃ: `keys.burstms`
- `U+01C3` ǃ: `keys.ej`
- `U+01C3` ǃ: `keys.burst`
- `U+01C3` ǃ: `keys.bgain`
- `U+01C3` ǃ: `keys.a2`
- `U+01C3` ǃ: `keys.a3`
- `U+01C3` ǃ: `keys.a4`
- `U+01C3` ǃ: `keys.a5`
- `U+01C3` ǃ: `keys.a6`
- `U+01C3` ǃ: `keys.f2`
- `U+0253` ɓ: `spec.locus.F2`
- `U+0253` ɓ: `keys.impl`
- `U+0253` ɓ: `keys.hold`
- `U+0256` ɖ: `spec.locus.F3`
- `U+0257` ɗ: `spec.locus.F2`
- `U+0257` ɗ: `keys.impl`
- `U+0257` ɗ: `keys.hold`
- `U+0258` ɘ: `spec.formants.F1`
- `U+0258` ɘ: `spec.formants.F2`
- `U+0258` ɘ: `spec.formants.F3`
- `U+025E` ɞ: `spec.formants.F1`
- `U+025E` ɞ: `spec.formants.F2`
- `U+025E` ɞ: `spec.formants.F3`
- `U+0260` ɠ: `spec.locus.F2`
- `U+0260` ɠ: `keys.impl`
- `U+0260` ɠ: `keys.hold`
- `U+0261` ɡ: `spec.locus.F2`
- `U+0262` ɢ: `spec.locus.F1`
- `U+0262` ɢ: `spec.locus.F2`
- `U+0265` ɥ: `spec.formants.F1`
- `U+0265` ɥ: `spec.formants.F2`
- `U+0265` ɥ: `spec.formants.F3`
- `U+0266` ɦ: `spec.duration.inherent_ms`
- `U+0267` ɧ: `spec.noise.peak_hz`
- `U+026E` ɮ: `spec.noise.peak_hz`
- `U+0270` ɰ: `spec.formants.F1`
- `U+0270` ɰ: `spec.formants.F2`
- `U+0270` ɰ: `spec.formants.F3`
- `U+0274` ɴ: `spec.formants.F1`
- `U+0274` ɴ: `spec.formants.F2`
- `U+0274` ɴ: `spec.formants.F3`
- `U+0278` ɸ: `spec.locus.F2`
- `U+027A` ɺ: `spec.tap.closed_ms`
- `U+0281` ʁ: `spec.noise.peak_hz`
- `U+0284` ʄ: `spec.locus.F2`
- `U+0284` ʄ: `keys.impl`
- `U+0284` ʄ: `keys.hold`
- `U+0288` ʈ: `spec.locus.F3`
- `U+028D` ʍ: `spec.locus.F2`
- `U+0290` ʐ: `spec.noise.peak_hz`
- `U+0291` ʑ: `spec.noise.peak_hz`
- `U+0298` ʘ: `spec.vot_ms`
- `U+0298` ʘ: `spec.burst.length_ms`
- `U+0298` ʘ: `spec.burst.level_db`
- `U+0298` ʘ: `keys.vot`
- `U+0298` ʘ: `keys.ej`
- `U+0298` ʘ: `keys.bgain`
- `U+0298` ʘ: `keys.a2`
- `U+0298` ʘ: `keys.a3`
- `U+0298` ʘ: `keys.a4`
- `U+0298` ʘ: `keys.a5`
- `U+0298` ʘ: `keys.a6`
- `U+0298` ʘ: `keys.ab`
- `U+029B` ʛ: `spec.locus.F2`
- `U+029B` ʛ: `keys.impl`
- `U+029B` ʛ: `keys.hold`
- `U+029C` ʜ: `spec.trill.closed_ms`
- `U+029F` ʟ: `spec.formants.F1`
- `U+029F` ʟ: `spec.formants.F2`
- `U+029F` ʟ: `spec.formants.F3`
- `U+02A2` ʢ: `spec.trill.closed_ms`
- `U+02B2` ʲ: `transform.consonant.locus.F2`
- `U+02B7` ʷ: `transform.consonant.formants.F2`
- `U+02BC` ʼ: `transform.consonant.release.burst_gain_db`
- `U+02BC` ʼ: `transform.consonant.release.ejective_silence_ms`
- `U+02D1` ˑ: `transform.vowel.duration.inherent_ms`
- `U+02D1` ˑ: `transform.consonant.duration.inherent_ms`
- `U+02E4` ˤ: `transform.consonant.locus.F1`
- `U+0303` ̃: `transform.vowel.nasal.open_pct`
- `U+0303` ̃: `transform.consonant.nasal.open_pct`
- `U+0306` ̆: `transform.vowel.duration.inherent_ms`
- `U+0306` ̆: `transform.consonant.duration.inherent_ms`
- `U+0308` ̈: `transform.vowel.formants.F2`
- `U+030A` ̊: `transform.consonant.breath.whisper_db`
- `U+030A` ̊: `transform.vowel.breath.whisper_db`
- `U+0318` ̘: `transform.vowel.formants.F1`
- `U+0318` ̘: `transform.consonant.formants.F1`
- `U+0319` ̙: `transform.vowel.formants.F1`
- `U+0319` ̙: `transform.vowel.formants.F2`
- `U+0319` ̙: `transform.consonant.formants.F1`
- `U+031C` ̜: `transform.vowel.formants.F2`
- `U+031C` ̜: `transform.vowel.formants.F3`
- `U+031D` ̝: `transform.vowel.formants.F1`
- `U+031D` ̝: `transform.consonant.formants.F1`
- `U+031E` ̞: `transform.vowel.formants.F1`
- `U+031E` ̞: `transform.consonant.formants.F1`
- `U+031F` ̟: `transform.vowel.formants.F2`
- `U+031F` ̟: `transform.consonant.locus.F2`
- `U+0320` ̠: `transform.vowel.formants.F2`
- `U+0320` ̠: `transform.consonant.locus.F2`
- `U+0324` ̤: `transform.vowel.phonation.breathy_pct`
- `U+0324` ̤: `transform.consonant.phonation.breathy_pct`
- `U+0325` ̥: `transform.consonant.breath.whisper_db`
- `U+0325` ̥: `transform.vowel.breath.whisper_db`
- `U+0329` ̩: `transform.consonant.duration.inherent_ms`
- `U+032A` ̪: `transform.consonant.locus.F2`
- `U+032F` ̯: `transform.vowel.duration.inherent_ms`
- `U+0330` ̰: `transform.vowel.phonation.creaky_pct`
- `U+0330` ̰: `transform.consonant.phonation.creaky_pct`
- `U+0339` ̹: `transform.vowel.formants.F2`
- `U+0339` ̹: `transform.vowel.formants.F3`
- `U+033A` ̺: `transform.consonant.locus.F3`
- `U+033B` ̻: `transform.consonant.locus.F2`
- `U+033C` ̼: `transform.consonant.locus.F2`
- `U+033D` ̽: `transform.vowel.formants.F1`
- `U+033D` ̽: `transform.vowel.formants.F2`
- `U+035C` ͜: `spec.duration.inherent_ms`
- `U+0361` ͡: `spec.duration.inherent_ms`
- `U+03B2` β: `spec.locus.F2`
- `U+03C7` χ: `spec.noise.peak_hz`
- `U+2197` ↗: `spec.st_per_syllable`
- `U+2198` ↘: `spec.st_per_syllable`
- `U+2C71` ⱱ: `spec.tap.closed_ms`
- `U+A71B` ꜛ: `spec.step_st`

**Q16. May Claude download Unicode's two data files?** The secondary coverage metric (`DESIGN.md` 1, the "Unicode net") classifies every code point of ten Unicode blocks; Python 3.10 here knows only Unicode 13, so the script reads Unicode's own `UnicodeData.txt` (about 2 MB) and `Blocks.txt` (about 10 kB) from https://www.unicode.org/Public/UCD/latest/ucd/ (Unicode License v3, which permits copying with its notice). Downloading a file needs your say-so. *Recommended default: yes, into `docs/tts-extension/inventory/unicode/` with the licence notice beside them.* **Answered 2026-10-06: yes.** Downloaded (Unicode 18.0.0, with `LICENSE.txt`); the net is in `coverage.py`.

**Q17. May Claude download two research data files the vowel helper found?** Kuronen (2000), a thesis with Swedish vowel formants (for ʉ and ɵ, which have no measured male values yet), and Deterding's per-speaker spreadsheets of Standard Southern British English vowels (for ɜ ɒ ʌ), both linked from their authors' pages. *Recommended default: yes, read only for the facts, nothing copied into the repository but the cited numbers.* **Answered 2026-10-06: yes.** Read: ɵ now has literature values (Kuronen 2000, Sweden-Swedish, 4 M: 411, 1223, 2493 Hz, replacing three estimates) and is proved with them; the other four vowels keep their values and list these as candidates.

**Q18. Two Tier A aliases mean something else in Tier B** (found by the Tier B inventory, 2026-10-06, `inventory/tierb/TIERB_CHECKLIST.md`). U+2193 (↓) is read as downstep in `ipa/aliases.toml`, but extIPA and VoQS use it for ingressive airflow; U+A71E (ꜞ) is the checklist's other spelling of upstep, but extIPA uses it for a percussive release. And VoQS names phonation as Catford did: its "whispery" voice is the IPA's breathy voice (̤). *Recommended default: in strict IPA input keep the Tier A readings; a pack or a text that declares extIPA or VoQS gets theirs (`DESIGN.md` 1, Tier B), decided when Tier B is mapped.*

**Q19. Syllable division and linking have no measured cue yet.** The marks `.` and `‿` are proved by structure (the syllable begins where they say) and by the sound changing by 8 ms or more, not against a measured value: no source on onset against coda cues (Lehiste 1960, Nakatani and Dukes 1977, Turk and Shattuck-Hufnagel 2000) or on liaison consonants' length (Spinelli, McQueen and Cutler 2003, abstract only) could be opened. *Recommended default: look again in Phase 5's audit; until then they stay `derived` from the chart's definitions.*

## For Phase 2 (found by measuring in Phase 1)

- Quechua (`qu`): in the golden case `s|t\``, the engine meant a final vowel `a` and gave it 11 frames with neither voicing nor noise (silent). Check whether the map or the template devoices it deliberately.
- Western Armenian (`hyw`): its eSpeak NG phonemes `p` and `t` are mapped to the module's `b` and `d` (sound `s24`), so they are said prevoiced (VOT -80 and -95 ms). Western Armenian does voice the historical /p t/, so this may be right, but the phonemes are labelled /p t/: Phase 4 should check the eSpeak NG table and the map together.
- English-based packs read by eSpeak NG (en-029, en-gb-x-rp and others): the diphthong cases `e@`, `i@`, `i@3` begin with a `t` whose whole span is closure; harmless, but a sign that the module merges the burst into the vowel.
