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

**Q15. The verification queue: every `estimated` value in the master table** (playbook Phase 4: "estimated values in OPEN_QUESTIONS.md"; `DESIGN.md` 3.2). Each is a value no opened source gave; its note in `ipa/table/*.toml` says what it rests on. A measured or published value for any of them replaces it (`DESIGN.md` 5: the tag becomes `literature`, the revision goes up, the proof is run again). Written by `python engine/ipa/table.py`'s validator; 436 values on 2026-10-09 (regenerated after D83 and D84):

- `B:U+0021#label` !: `transform.consonant.phonation.diplophonia_pct`
- `B:U+0021#label` !: `transform.consonant.phonation.open_quotient_pct`
- `B:U+0021#label` !: `transform.vowel.phonation.diplophonia_pct`
- `B:U+0021#label` !: `transform.vowel.phonation.open_quotient_pct`
- `B:U+0021+U+0021#label` !!: `transform.consonant.phonation.diplophonia_pct`
- `B:U+0021+U+0021#label` !!: `transform.consonant.phonation.open_quotient_pct`
- `B:U+0021+U+0021#label` !!: `transform.vowel.phonation.diplophonia_pct`
- `B:U+0021+U+0021#label` !!: `transform.vowel.phonation.open_quotient_pct`
- `B:U+0031/U+0032/U+0033` 1 2 3: `spec.degree_scale`
- `B:U+0046` F: `spec.pitch.offset_st`
- `B:U+0046` F: `transform.consonant.pitch.offset_st`
- `B:U+0046` F: `transform.vowel.phonation.tilt_db`
- `B:U+0046` F: `transform.vowel.pitch.offset_st`
- `B:U+004A+U+0354` J͔: `transform.consonant.formants.F1`
- `B:U+004A+U+0354` J͔: `transform.consonant.formants.F3`
- `B:U+004A+U+0354` J͔: `transform.vowel.formants.F1`
- `B:U+004A+U+0354` J͔: `transform.vowel.formants.F3`
- `B:U+004A+U+0355` J͕: `transform.consonant.formants.F1`
- `B:U+004A+U+0355` J͕: `transform.consonant.formants.F3`
- `B:U+004A+U+0355` J͕: `transform.vowel.formants.F1`
- `B:U+004A+U+0355` J͕: `transform.vowel.formants.F3`
- `B:U+004C+U+031D` L̝: `transform.consonant.formants.F1`
- `B:U+004C+U+031D` L̝: `transform.consonant.formants.F2`
- `B:U+004C+U+031D` L̝: `transform.consonant.formants.F3`
- `B:U+004C+U+031D` L̝: `transform.consonant.formants.F4`
- `B:U+004C+U+031D` L̝: `transform.consonant.pitch.offset_st`
- `B:U+004C+U+031D` L̝: `transform.vowel.formants.F1`
- `B:U+004C+U+031D` L̝: `transform.vowel.formants.F2`
- `B:U+004C+U+031D` L̝: `transform.vowel.formants.F3`
- `B:U+004C+U+031D` L̝: `transform.vowel.formants.F4`
- `B:U+004C+U+031D` L̝: `transform.vowel.pitch.offset_st`
- `B:U+004C+U+031E` L̞: `transform.consonant.formants.F1`
- `B:U+004C+U+031E` L̞: `transform.consonant.formants.F2`
- `B:U+004C+U+031E` L̞: `transform.consonant.formants.F3`
- `B:U+004C+U+031E` L̞: `transform.consonant.formants.F4`
- `B:U+004C+U+031E` L̞: `transform.consonant.pitch.offset_st`
- `B:U+004C+U+031E` L̞: `transform.vowel.formants.F1`
- `B:U+004C+U+031E` L̞: `transform.vowel.formants.F2`
- `B:U+004C+U+031E` L̞: `transform.vowel.formants.F3`
- `B:U+004C+U+031E` L̞: `transform.vowel.formants.F4`
- `B:U+004C+U+031E` L̞: `transform.vowel.pitch.offset_st`
- `B:U+0056+U+0319+U+02E4` V̙ˤ: `transform.consonant.formants.F1`
- `B:U+0056+U+0319+U+02E4` V̙ˤ: `transform.consonant.formants.F2`
- `B:U+0056+U+0319+U+02E4` V̙ˤ: `transform.consonant.phonation.open_quotient_pct`
- `B:U+0056+U+0319+U+02E4` V̙ˤ: `transform.vowel.formants.F1`
- `B:U+0056+U+0319+U+02E4` V̙ˤ: `transform.vowel.formants.F2`
- `B:U+0056+U+0319+U+02E4` V̙ˤ: `transform.vowel.phonation.open_quotient_pct`
- `B:U+0056+U+032C+U+0021+U+0021` V̬!!: `transform.consonant.phonation.diplophonia_pct`
- `B:U+0056+U+032C+U+0021+U+0021` V̬!!: `transform.vowel.phonation.diplophonia_pct`
- `B:U+0057+U+0348` W͈: `transform.consonant.breath.whisper_db`
- `B:U+0057+U+0348` W͈: `transform.vowel.breath.whisper_db`
- `B:U+0066#dyn` f: `spec.level_db`
- `B:U+0066#dyn` f: `transform.consonant.breath.gain_db`
- `B:U+0066#dyn` f: `transform.consonant.noise.gain_db`
- `B:U+0066#dyn` f: `transform.consonant.pitch.offset_st`
- `B:U+0066#dyn` f: `transform.consonant.voice.level_db`
- `B:U+0066#dyn` f: `transform.vowel.breath.gain_db`
- `B:U+0066#dyn` f: `transform.vowel.formants.F1`
- `B:U+0066#dyn` f: `transform.vowel.pitch.offset_st`
- `B:U+0066#dyn` f: `transform.vowel.voice.level_db`
- `B:U+0066+U+0066#dyn` ff: `spec.level_db`
- `B:U+0066+U+0066#dyn` ff: `transform.consonant.breath.gain_db`
- `B:U+0066+U+0066#dyn` ff: `transform.consonant.noise.gain_db`
- `B:U+0066+U+0066#dyn` ff: `transform.consonant.pitch.offset_st`
- `B:U+0066+U+0066#dyn` ff: `transform.consonant.voice.level_db`
- `B:U+0066+U+0066#dyn` ff: `transform.vowel.breath.gain_db`
- `B:U+0066+U+0066#dyn` ff: `transform.vowel.formants.F1`
- `B:U+0066+U+0066#dyn` ff: `transform.vowel.pitch.offset_st`
- `B:U+0066+U+0066#dyn` ff: `transform.vowel.voice.level_db`
- `B:U+0068+U+032A+U+0346` h̪͆: `keys.a2`
- `B:U+0068+U+032A+U+0346` h̪͆: `keys.a3`
- `B:U+0068+U+032A+U+0346` h̪͆: `keys.a4`
- `B:U+0068+U+032A+U+0346` h̪͆: `keys.a5`
- `B:U+0068+U+032A+U+0346` h̪͆: `keys.a6`
- `B:U+0068+U+032A+U+0346` h̪͆: `keys.ab`
- `B:U+0068+U+032A+U+0346` h̪͆: `keys.fric`
- `B:U+0068+U+032A+U+0346` h̪͆: `spec.noise.centroid_hz`
- `B:U+0070#dyn` p: `spec.level_db`
- `B:U+0070#dyn` p: `transform.consonant.breath.gain_db`
- `B:U+0070#dyn` p: `transform.consonant.noise.gain_db`
- `B:U+0070#dyn` p: `transform.consonant.pitch.offset_st`
- `B:U+0070#dyn` p: `transform.consonant.voice.level_db`
- `B:U+0070#dyn` p: `transform.vowel.breath.gain_db`
- `B:U+0070#dyn` p: `transform.vowel.formants.F1`
- `B:U+0070#dyn` p: `transform.vowel.pitch.offset_st`
- `B:U+0070#dyn` p: `transform.vowel.voice.level_db`
- `B:U+0070+U+0070#dyn` pp: `spec.level_db`
- `B:U+0070+U+0070#dyn` pp: `transform.consonant.breath.gain_db`
- `B:U+0070+U+0070#dyn` pp: `transform.consonant.noise.gain_db`
- `B:U+0070+U+0070#dyn` pp: `transform.consonant.pitch.offset_st`
- `B:U+0070+U+0070#dyn` pp: `transform.consonant.voice.level_db`
- `B:U+0070+U+0070#dyn` pp: `transform.vowel.breath.gain_db`
- `B:U+0070+U+0070#dyn` pp: `transform.vowel.formants.F1`
- `B:U+0070+U+0070#dyn` pp: `transform.vowel.pitch.offset_st`
- `B:U+0070+U+0070#dyn` pp: `transform.vowel.voice.level_db`
- `B:U+00A1` ¡: `keys.a2`
- `B:U+00A1` ¡: `keys.a3`
- `B:U+00A1` ¡: `keys.a4`
- `B:U+00A1` ¡: `keys.a5`
- `B:U+00A1` ¡: `keys.a6`
- `B:U+00A1` ¡: `keys.ab`
- `B:U+00A1` ¡: `keys.hitaf`
- `B:U+00A1` ¡: `keys.hitg`
- `B:U+00A1` ¡: `spec.strike.centroid_hz`
- `B:U+00A1` ¡: `spec.strike.delay_ms`
- `B:U+00A1` ¡: `spec.strike.length_ms`
- `B:U+0152` Œ: `transform.consonant.phonation.breathy_pct`
- `B:U+0152` Œ: `transform.consonant.phonation.diplophonia_pct`
- `B:U+0152` Œ: `transform.consonant.pitch.offset_st`
- `B:U+0152` Œ: `transform.vowel.phonation.breathy_pct`
- `B:U+0152` Œ: `transform.vowel.phonation.diplophonia_pct`
- `B:U+0152` Œ: `transform.vowel.pitch.offset_st`
- `B:U+01C3+U+00A1` ǃ¡: `keys.ej`
- `B:U+01C3+U+00A1` ǃ¡: `keys.rel2af`
- `B:U+01C3+U+00A1` ǃ¡: `keys.rel2g`
- `B:U+01C3+U+00A1` ǃ¡: `keys.rel2ms`
- `B:U+01C3+U+00A1` ǃ¡: `spec.slap.length_ms`
- `B:U+0266+U+032A+U+0346` ɦ̪͆: `keys.a2`
- `B:U+0266+U+032A+U+0346` ɦ̪͆: `keys.a3`
- `B:U+0266+U+032A+U+0346` ɦ̪͆: `keys.a4`
- `B:U+0266+U+032A+U+0346` ɦ̪͆: `keys.a5`
- `B:U+0266+U+032A+U+0346` ɦ̪͆: `keys.a6`
- `B:U+0266+U+032A+U+0346` ɦ̪͆: `spec.noise.centroid_hz`
- `B:U+02AC` ʬ: `keys.a2`
- `B:U+02AC` ʬ: `keys.a3`
- `B:U+02AC` ʬ: `keys.a4`
- `B:U+02AC` ʬ: `keys.a5`
- `B:U+02AC` ʬ: `keys.a6`
- `B:U+02AC` ʬ: `keys.ab`
- `B:U+02AC` ʬ: `keys.hitaf`
- `B:U+02AC` ʬ: `keys.hitg`
- `B:U+02AC` ʬ: `spec.strike.centroid_hz`
- `B:U+02AC` ʬ: `spec.strike.length_ms`
- `B:U+02AC` ʬ: `spec.strike.level_db`
- `B:U+02AD` ʭ: `keys.a2`
- `B:U+02AD` ʭ: `keys.a3`
- `B:U+02AD` ʭ: `keys.a4`
- `B:U+02AD` ʭ: `keys.a5`
- `B:U+02AD` ʭ: `keys.a6`
- `B:U+02AD` ʭ: `keys.ab`
- `B:U+02AD` ʭ: `keys.hitaf`
- `B:U+02AD` ʭ: `keys.hitg`
- `B:U+02AD` ʭ: `spec.strike.centroid_hz`
- `B:U+02AD` ʭ: `spec.strike.length_ms`
- `B:U+02AD` ʭ: `spec.strike.level_db`
- `B:U+02B2#label` ʲ: `transform.vowel.formants.F2`
- `B:U+02B6#label` ʶ: `transform.consonant.formants.F1`
- `B:U+02B6#label` ʶ: `transform.consonant.formants.F2`
- `B:U+02B6#label` ʶ: `transform.vowel.formants.F1`
- `B:U+02B6#label` ʶ: `transform.vowel.formants.F2`
- `B:U+02B7#label` ʷ: `transform.vowel.formants.F3`
- `B:U+02DE#label` ˞: `transform.consonant.formants.F3`
- `B:U+02E0#label` ˠ: `transform.vowel.formants.F2`
- `B:U+02E4#label` ˤ: `transform.vowel.formants.F1`
- `B:U+02E4#label` ˤ: `transform.vowel.formants.F2`
- `B:U+02EC#post` ˬ: `transform.consonant.voicing.part_from_pct`
- `B:U+02EC#pre` ˬ: `transform.consonant.voicing.part_to_pct`
- `B:U+02F7` ˷: `transform.consonant.voicing.part_from_pct`
- `B:U+02F7` ˷: `transform.vowel.voicing.part_from_pct`
- `B:U+0324#label` ̤: `transform.consonant.phonation.breathy_pct`
- `B:U+0324#label` ̤: `transform.vowel.phonation.breathy_pct`
- `B:U+0325+U+1ABD` ̥᪽: `transform.consonant.voicing.part_from_pct`
- `B:U+0325+U+1ABD` ̥᪽: `transform.consonant.voicing.part_to_pct`
- `B:U+0325+U+1ABD` ̥᪽: `transform.vowel.voicing.part_from_pct`
- `B:U+0325+U+1ABD` ̥᪽: `transform.vowel.voicing.part_to_pct`
- `B:U+0325+U+1AC3` ̥᫃: `transform.consonant.voicing.part_to_pct`
- `B:U+0325+U+1AC3` ̥᫃: `transform.vowel.voicing.part_to_pct`
- `B:U+0325+U+1AC4` ̥᫄: `transform.consonant.voicing.part_from_pct`
- `B:U+0325+U+1AC4` ̥᫄: `transform.vowel.voicing.part_from_pct`
- `B:U+032C+U+1ABD` ̬᪽: `transform.consonant.voicing.part_from_pct`
- `B:U+032C+U+1ABD` ̬᪽: `transform.consonant.voicing.part_to_pct`
- `B:U+032C+U+1AC3` ̬᫃: `transform.consonant.voicing.part_to_pct`
- `B:U+032C+U+1AC4` ̬᫄: `transform.consonant.voicing.part_from_pct`
- `B:U+0346` ͆: `transform.consonant.locus.F2`
- `B:U+0347` ͇: `transform.consonant.locus.F2`
- `B:U+0347#label` ͇: `transform.vowel.formants.F2`
- `B:U+0348` ͈: `transform.consonant.duration.inherent_ms`
- `B:U+0348` ͈: `transform.consonant.noise.gain_db`
- `B:U+0348#label` ͈: `transform.consonant.phonation.open_quotient_pct`
- `B:U+0348#label` ͈: `transform.consonant.phonation.tilt_db`
- `B:U+0348#label` ͈: `transform.vowel.phonation.open_quotient_pct`
- `B:U+0348#label` ͈: `transform.vowel.phonation.tilt_db`
- `B:U+0349` ͉: `transform.consonant.duration.inherent_ms`
- `B:U+0349` ͉: `transform.consonant.noise.gain_db`
- `B:U+0349#label` ͉: `transform.consonant.phonation.open_quotient_pct`
- `B:U+0349#label` ͉: `transform.vowel.phonation.open_quotient_pct`
- `B:U+034A` ͊: `transform.consonant.phonation.tilt_db`
- `B:U+034A` ͊: `transform.consonant.voice.level_db`
- `B:U+034A+U+1ABB` ͊᪻: `transform.consonant.phonation.tilt_db`
- `B:U+034A+U+1ABB` ͊᪻: `transform.consonant.voice.level_db`
- `B:U+034B` ͋: `transform.consonant.noise.F5_db`
- `B:U+034B` ͋: `transform.consonant.noise.flat_db`
- `B:U+034B` ͋: `transform.consonant.noise.level_db`
- `B:U+034C` ͌: `transform.consonant.nasal.open_pct`
- `B:U+034C` ͌: `transform.consonant.noise.F2_db`
- `B:U+034C` ͌: `transform.consonant.noise.level_db`
- `B:U+034C` ͌: `transform.consonant.noise.over_voice_db`
- `B:U+034D` ͍: `transform.consonant.locus.F2`
- `B:U+034E` ͎: `transform.consonant.noise.F3_db`
- `B:U+034E` ͎: `transform.consonant.noise.F4_db`
- `B:U+034E` ͎: `transform.consonant.noise.F5_db`
- `B:U+034E` ͎: `transform.consonant.noise.F6_db`
- `B:U+034E` ͎: `transform.consonant.noise.flat_db`
- `B:U+0354` ͔: `transform.consonant.noise.F5_db`
- `B:U+0355` ͕: `transform.consonant.formants.F4`
- `B:U+0355` ͕: `transform.consonant.noise.F5_db`
- `B:U+0362` ͢: `transform.consonant.duration.inherent_ms`
- `B:U+0398` Θ: `transform.consonant.formants.F2`
- `B:U+0398` Θ: `transform.consonant.formants.F3`
- `B:U+0398` Θ: `transform.vowel.formants.F2`
- `B:U+0398` Θ: `transform.vowel.formants.F3`
- `B:U+0418` И: `transform.vowel.phonation.tilt_db`
- `B:U+042E` Ю: `transform.consonant.phonation.breathy_pct`
- `B:U+042E` Ю: `transform.consonant.phonation.diplophonia_pct`
- `B:U+042E` Ю: `transform.consonant.pitch.offset_st`
- `B:U+042E` Ю: `transform.vowel.phonation.breathy_pct`
- `B:U+042E` Ю: `transform.vowel.phonation.diplophonia_pct`
- `B:U+042E` Ю: `transform.vowel.pitch.offset_st`
- `B:U+10780#label` 𐞀: `transform.consonant.phonation.diplophonia_pct`
- `B:U+10780#label` 𐞀: `transform.consonant.phonation.open_quotient_pct`
- `B:U+10780#label` 𐞀: `transform.consonant.pitch.offset_st`
- `B:U+10780#label` 𐞀: `transform.vowel.phonation.diplophonia_pct`
- `B:U+10780#label` 𐞀: `transform.vowel.phonation.open_quotient_pct`
- `B:U+10780#label` 𐞀: `transform.vowel.pitch.offset_st`
- `B:U+1DB9#label` ᶹ: `transform.consonant.formants.F2`
- `B:U+1DB9#label` ᶹ: `transform.consonant.formants.F3`
- `B:U+1DB9#label` ᶹ: `transform.vowel.formants.F2`
- `B:U+1DB9#label` ᶹ: `transform.vowel.formants.F3`
- `B:U+1DF01` 𝼁: `spec.locus_slope.F2`
- `B:U+1DF01` 𝼁: `spec.locus_slope.F3`
- `B:U+1DF03` 𝼃: `spec.locus_slope.F2`
- `B:U+1DF03` 𝼃: `spec.locus_slope.F3`
- `B:U+1DF06` 𝼆: `spec.locus.F2`
- `B:U+1DF06` 𝼆: `spec.locus.F3`
- `B:U+1DF06` 𝼆: `spec.locus_slope.F2`
- `B:U+1DF06` 𝼆: `spec.noise.peak_hz`
- `B:U+1DF07` 𝼇: `spec.locus_slope.F2`
- `B:U+1DF07` 𝼇: `spec.locus_slope.F3`
- `B:U+2180` ↀ: `transform.consonant.noise.level_db`
- `B:U+2180` ↀ: `transform.vowel.noise.level_db`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.a2`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.a3`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.a4`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.a5`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.a6`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.ab`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.fric`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `keys.trate`
- `B:U+2180+U+0361+U+0072` ↀ͡r: `spec.trill.rate_hz`
- `B:U+2E28+U+2E29` ⸨⸩: `transform.consonant.noise.flat_db`
- `B:U+2E28+U+2E29` ⸨⸩: `transform.consonant.noise.level_db`
- `B:U+2E28+U+2E29` ⸨⸩: `transform.vowel.noise.flat_db`
- `B:U+2E28+U+2E29` ⸨⸩: `transform.vowel.noise.level_db`
- `B:U+A78E` ꞎ: `spec.noise.peak_hz`
- `B:U+A7F8#label` ꟸ: `transform.consonant.formants.F1`
- `B:U+A7F8#label` ꟸ: `transform.vowel.bandwidths.B1`
- `B:U+A7F8#label` ꟸ: `transform.vowel.formants.F1`
- `B:U+A7F8#label` ꟸ: `transform.vowel.formants.F3`
- `B:U+A7FF` ꟿ: `transform.consonant.phonation.open_quotient_pct`
- `B:U+A7FF` ꟿ: `transform.vowel.phonation.open_quotient_pct`
- `B:U+A7FF` ꟿ: `transform.vowel.trill.depth_db`
- `B:U+A7FF` ꟿ: `transform.vowel.trill.rate_hz`
- `B:term:crescendo` crescendo: `spec.level_rise_db`
- `B:term:crescendo` crescendo: `transform.consonant.breath.gain_db`
- `B:term:crescendo` crescendo: `transform.consonant.noise.gain_db`
- `B:term:crescendo` crescendo: `transform.consonant.voice.level_db`
- `B:term:crescendo` crescendo: `transform.vowel.breath.gain_db`
- `B:term:crescendo` crescendo: `transform.vowel.voice.level_db`
- `U+0071` q: `spec.locus.F1`
- `U+0071` q: `spec.vot_ms`
- `U+0078` x: `spec.noise.peak_hz`
- `U+00E7` ç: `keys.a5`
- `U+00E7` ç: `spec.noise.peak_hz`
- `U+01C0` ǀ: `keys.a2`
- `U+01C0` ǀ: `keys.a3`
- `U+01C0` ǀ: `keys.a4`
- `U+01C0` ǀ: `keys.a5`
- `U+01C0` ǀ: `keys.a6`
- `U+01C0` ǀ: `keys.bgain`
- `U+01C0` ǀ: `keys.burstms`
- `U+01C0` ǀ: `keys.ej`
- `U+01C0` ǀ: `keys.hold`
- `U+01C0` ǀ: `spec.vot_ms`
- `U+01C1` ǁ: `keys.a2`
- `U+01C1` ǁ: `keys.a3`
- `U+01C1` ǁ: `keys.a4`
- `U+01C1` ǁ: `keys.a5`
- `U+01C1` ǁ: `keys.a6`
- `U+01C1` ǁ: `keys.bgain`
- `U+01C1` ǁ: `keys.burst`
- `U+01C1` ǁ: `keys.ej`
- `U+01C2` ǂ: `keys.a2`
- `U+01C2` ǂ: `keys.a3`
- `U+01C2` ǂ: `keys.a4`
- `U+01C2` ǂ: `keys.a5`
- `U+01C2` ǂ: `keys.a6`
- `U+01C2` ǂ: `keys.bgain`
- `U+01C2` ǂ: `keys.burst`
- `U+01C2` ǂ: `keys.burstms`
- `U+01C2` ǂ: `keys.ej`
- `U+01C2` ǂ: `spec.vot_ms`
- `U+01C3` ǃ: `keys.a2`
- `U+01C3` ǃ: `keys.a3`
- `U+01C3` ǃ: `keys.a4`
- `U+01C3` ǃ: `keys.a5`
- `U+01C3` ǃ: `keys.a6`
- `U+01C3` ǃ: `keys.bgain`
- `U+01C3` ǃ: `keys.burst`
- `U+01C3` ǃ: `keys.burstms`
- `U+01C3` ǃ: `keys.ej`
- `U+01C3` ǃ: `keys.f2`
- `U+0253` ɓ: `keys.hold`
- `U+0253` ɓ: `keys.impl`
- `U+0253` ɓ: `spec.locus.F2`
- `U+0253` ɓ: `spec.locus_slope.F2`
- `U+0256` ɖ: `spec.locus.F3`
- `U+0257` ɗ: `keys.hold`
- `U+0257` ɗ: `keys.impl`
- `U+0257` ɗ: `spec.locus.F2`
- `U+0257` ɗ: `spec.locus_slope.F2`
- `U+0258` ɘ: `spec.formants.F1`
- `U+0258` ɘ: `spec.formants.F2`
- `U+0258` ɘ: `spec.formants.F3`
- `U+025E` ɞ: `spec.formants.F1`
- `U+025E` ɞ: `spec.formants.F2`
- `U+025E` ɞ: `spec.formants.F3`
- `U+0260` ɠ: `keys.hold`
- `U+0260` ɠ: `keys.impl`
- `U+0260` ɠ: `spec.locus.F2`
- `U+0260` ɠ: `spec.locus_slope.F2`
- `U+0262` ɢ: `spec.locus.F1`
- `U+0262` ɢ: `spec.locus.F2`
- `U+0262` ɢ: `spec.locus_slope.F2`
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
- `U+0278` ɸ: `spec.locus_slope.F2`
- `U+027A` ɺ: `spec.tap.closed_ms`
- `U+027D` ɽ: `spec.locus.F3`
- `U+0281` ʁ: `spec.noise.peak_hz`
- `U+0284` ʄ: `keys.hold`
- `U+0284` ʄ: `keys.impl`
- `U+0284` ʄ: `spec.locus.F2`
- `U+0284` ʄ: `spec.locus_slope.F2`
- `U+0288` ʈ: `spec.locus.F3`
- `U+028D` ʍ: `spec.locus.F2`
- `U+0290` ʐ: `spec.noise.peak_hz`
- `U+0291` ʑ: `spec.noise.peak_hz`
- `U+0298` ʘ: `keys.a2`
- `U+0298` ʘ: `keys.a3`
- `U+0298` ʘ: `keys.a4`
- `U+0298` ʘ: `keys.a5`
- `U+0298` ʘ: `keys.a6`
- `U+0298` ʘ: `keys.ab`
- `U+0298` ʘ: `keys.bgain`
- `U+0298` ʘ: `keys.ej`
- `U+0298` ʘ: `keys.vot`
- `U+0298` ʘ: `spec.burst.length_ms`
- `U+0298` ʘ: `spec.burst.level_db`
- `U+0298` ʘ: `spec.vot_ms`
- `U+029B` ʛ: `keys.hold`
- `U+029B` ʛ: `keys.impl`
- `U+029B` ʛ: `spec.locus.F2`
- `U+029B` ʛ: `spec.locus_slope.F2`
- `U+029C` ʜ: `spec.trill.closed_ms`
- `U+029F` ʟ: `spec.formants.F1`
- `U+029F` ʟ: `spec.formants.F2`
- `U+029F` ʟ: `spec.formants.F3`
- `U+02A2` ʢ: `spec.trill.closed_ms`
- `U+02B2` ʲ: `transform.consonant.locus.F2`
- `U+02B7` ʷ: `transform.consonant.formants.F2`
- `U+02BC` ʼ: `transform.consonant.release.burst_gain_db`
- `U+02BC` ʼ: `transform.consonant.release.ejective_silence_ms`
- `U+02D1` ˑ: `transform.consonant.duration.inherent_ms`
- `U+02D1` ˑ: `transform.vowel.duration.inherent_ms`
- `U+02E4` ˤ: `transform.consonant.locus.F1`
- `U+0303` ̃: `transform.consonant.nasal.open_pct`
- `U+0303` ̃: `transform.vowel.nasal.open_pct`
- `U+0306` ̆: `transform.consonant.duration.inherent_ms`
- `U+0306` ̆: `transform.vowel.duration.inherent_ms`
- `U+0308` ̈: `transform.vowel.formants.F2`
- `U+030A` ̊: `transform.consonant.breath.whisper_db`
- `U+030A` ̊: `transform.vowel.breath.whisper_db`
- `U+0318` ̘: `transform.consonant.formants.F1`
- `U+0318` ̘: `transform.vowel.formants.F1`
- `U+0319` ̙: `transform.consonant.formants.F1`
- `U+0319` ̙: `transform.vowel.formants.F1`
- `U+0319` ̙: `transform.vowel.formants.F2`
- `U+031C` ̜: `transform.vowel.formants.F2`
- `U+031C` ̜: `transform.vowel.formants.F3`
- `U+031D` ̝: `transform.consonant.formants.F1`
- `U+031D` ̝: `transform.vowel.formants.F1`
- `U+031E` ̞: `transform.consonant.formants.F1`
- `U+031E` ̞: `transform.vowel.formants.F1`
- `U+031F` ̟: `transform.consonant.locus.F2`
- `U+031F` ̟: `transform.vowel.formants.F2`
- `U+0320` ̠: `transform.consonant.locus.F2`
- `U+0320` ̠: `transform.vowel.formants.F2`
- `U+0324` ̤: `transform.consonant.phonation.breathy_pct`
- `U+0324` ̤: `transform.vowel.phonation.breathy_pct`
- `U+0325` ̥: `transform.consonant.breath.whisper_db`
- `U+0325` ̥: `transform.vowel.breath.whisper_db`
- `U+0329` ̩: `transform.consonant.duration.inherent_ms`
- `U+032A` ̪: `transform.consonant.locus.F2`
- `U+032F` ̯: `transform.vowel.duration.inherent_ms`
- `U+0330` ̰: `transform.consonant.phonation.creaky_pct`
- `U+0330` ̰: `transform.vowel.phonation.creaky_pct`
- `U+0339` ̹: `transform.vowel.formants.F2`
- `U+0339` ̹: `transform.vowel.formants.F3`
- `U+033A` ̺: `transform.consonant.locus.F3`
- `U+033B` ̻: `transform.consonant.locus.F2`
- `U+033C` ̼: `transform.consonant.locus.F2`
- `U+033D` ̽: `transform.vowel.formants.F1`
- `U+033D` ̽: `transform.vowel.formants.F2`
- `U+035C` ͜: `spec.duration.inherent_ms`
- `U+0361` ͡: `double.dedx.ɡ͡b.1.hold`
- `U+0361` ͡: `double.dedx.ɡ͡b.2.hold`
- `U+0361` ͡: `released.dedx.d͡ð.frelaf`
- `U+0361` ͡: `spec.duration.inherent_ms`
- `U+03B2` β: `spec.locus.F2`
- `U+03B2` β: `spec.locus_slope.F2`
- `U+03C7` χ: `spec.noise.peak_hz`
- `U+2197` ↗: `spec.st_per_syllable`
- `U+2198` ↘: `spec.st_per_syllable`
- `U+2C71` ⱱ: `spec.tap.closed_ms`
- `U+A71B` ꜛ: `spec.step_st`

**Q16. May Claude download Unicode's two data files?** The secondary coverage metric (`DESIGN.md` 1, the "Unicode net") classifies every code point of ten Unicode blocks; Python 3.10 here knows only Unicode 13, so the script reads Unicode's own `UnicodeData.txt` (about 2 MB) and `Blocks.txt` (about 10 kB) from https://www.unicode.org/Public/UCD/latest/ucd/ (Unicode License v3, which permits copying with its notice). Downloading a file needs your say-so. *Recommended default: yes, into `docs/tts-extension/inventory/unicode/` with the licence notice beside them.* **Answered 2026-10-06: yes.** Downloaded (Unicode 18.0.0, with `LICENSE.txt`); the net is in `coverage.py`.

**Q17. May Claude download two research data files the vowel helper found?** Kuronen (2000), a thesis with Swedish vowel formants (for ʉ and ɵ, which have no measured male values yet), and Deterding's per-speaker spreadsheets of Standard Southern British English vowels (for ɜ ɒ ʌ), both linked from their authors' pages. *Recommended default: yes, read only for the facts, nothing copied into the repository but the cited numbers.* **Answered 2026-10-06: yes.** Read: ɵ now has literature values (Kuronen 2000, Sweden-Swedish, 4 M: 411, 1223, 2493 Hz, replacing three estimates) and is proved with them; the other four vowels keep their values and list these as candidates.

**Q18. Two Tier A aliases mean something else in Tier B** (found by the Tier B inventory, 2026-10-06, `inventory/tierb/TIERB_CHECKLIST.md`). U+2193 (↓) is read as downstep in `ipa/aliases.toml`, but extIPA and VoQS use it for ingressive airflow; U+A71E (ꜞ) is the checklist's other spelling of upstep, but extIPA uses it for a percussive release. And VoQS names phonation as Catford did: its "whispery" voice is the IPA's breathy voice (̤). *Recommended default: in strict IPA input keep the Tier A readings; a pack or a text that declares extIPA or VoQS gets theirs (`DESIGN.md` 1, Tier B), decided when Tier B is mapped.* **Decided (2026-10-07, seventh session, D67), by the default under the human's standing answer (D60):** in strict IPA input the Tier A readings stay (↓ downstep, ꜞ upstep, ̤ breathy); a pack or a text that declares extIPA or VoQS gets theirs, which is built when those records are mapped (4f). Nothing reads extIPA or VoQS yet, so nothing changes now.

**Q19. Syllable division and linking have no measured cue yet.** The marks `.` and `‿` are proved by structure (the syllable begins where they say) and by the sound changing by 8 ms or more, not against a measured value: no source on onset against coda cues (Lehiste 1960, Nakatani and Dukes 1977, Turk and Shattuck-Hufnagel 2000) or on liaison consonants' length (Spinelli, McQueen and Cutler 2003, abstract only) could be opened. *Recommended default: look again in Phase 5's audit; until then they stay `derived` from the chart's definitions.*

**Q20. ɢ is not yet proved: the bend into a consonant works by ratios** (2026-10-07, D65; Claude acts on this first in the next session: the Unmappable Sound Protocol asks for the capability to be built before an entry is marked approximate). The accent layer's `ant` (D64) bends a vowel's end by multiplying the vowel's own frames by the consonant's formant ratios. Where the module's own transition has not reached the consonant (a 45 ms stressed [a] before a voiced stop), a ratio meant for the consonant lands on the vowel: ɢ's F1 raise (1.22) takes [a]'s F1 to about 975 Hz, the formant-order clamp lifts F2 above it, and the vowel's F2 does not fall towards the uvular (edge F2 32 Hz under ɡ's, not 49; [i] holds by 116 Hz). q shows the same before [a] and passes on the vowel after it. *Default: in the next engine change, give `ant` a target in the consonant's own frames (or cap a raising ratio by the vowel's own formant), rebuild, and prove ɢ again without the bound; if it still misses after five rounds, mark it `approximate` with its deviation stated (D65 has the text and the bound, 18.3 Hz, that the sweep can now hold a contrast to).* **Acted on (2026-10-07, sixth session, D66):** the layer now lets F1 give way when a bend brings F2 down onto it (the wrong-way lift is gone: ɢ's F2 at the end of [a] is asked for under ɡ's, 1053 against 1097 Hz, where it was 1174); a longer bend (half the vowel) was tried and not kept (Q21). The edge still misses (31.6 Hz under ɡ's, 48.8 needed). A first version of this session then marked ɢ `approximate`; the review (R15) held that against the default here, which names the fix itself (a target towards the consonant's own place) and five rounds, and two rounds had been run. ɢ is therefore still not yet (`MISSING`): the fix named here is Q21, and ɢ is tried again after it (rounds 3 to 5), approximate only if those miss. **Closed (2026-10-07, seventh session, D67):** with Q21 built, ɢ passed on round 3 of the protocol without its bound: edge F2 1425.6 against ɡ's 1494.8 Hz (69.2 under, 59.8 needed). It is `created`, not approximate.

**Q21. `ant` bends a vowel by the carrier's ratios, not towards the consonant's own place** (2026-10-07, D66; for Phase 5's audit or the final engine change of Phase 4). The bend multiplies the vowel's frames by the ratio the consonant applies to its carrier. Where the carrier's place is far from the vowel's, that ratio lands on the wrong base: θ (F2 x 1.84) and f (x 1.63) take an [i]'s F2 (about 2300 Hz) past its F3, so the tracker reads 3270 Hz for f's [i] edge now, and with a bend over half the vowel θ's [i] read 1472 (it failed its contrast with f, which is why that longer bend was not kept). The proofs pass on the median context, and in [i] the value is not the dental or labiodental locus the specification gives. *Default: give the layer the consonant's target as a ratio of the voice's own neutral formants (the voice's scale, not hertz), bend towards that, rebuild, re-run the whole sweep, the golden and the engine gate; then prove ɢ again (rounds 3 to 5 of the protocol; approximate only if they miss, with the deviation D66 records). Until then ɢ is not yet and the [i] edges of the raising consonants are reported as they are.* **Acted on (2026-10-07, seventh session, D67):** the layer has the keys `l1` to `l4` (a place's formant, per mille of the voice's own F5, read from each frame) and `lk` (the locus equation's slope); the vowel before a place ends at locus + slope x (its own formant - locus), and the vowel after one starts there, from its own middle (not the module's way out of the carrier). 27 consonants whose sources give a slope (or are set equal to one that does) are realised so; the rest keep their ratios. θ's [i] edges are now 2357 and 2309 Hz (f's 2485, 2435), where the ratio took them past F3. Only the reference template's F5 is measured (3900 Hz): the other templates keep the ratios until theirs is, at the rebuild of all seven.

**Q22. A tied pair the template has no phone for loses the marks on its letters** (2026-10-07, eighth session, D68; found by the Tier B entries t̼͡θ̼ and d̼͡ð̼). The front-end says such a pair as its letters in a row (D66) by its old longest-match lookup, which skips every mark on either letter (`ipa-char-skipped U+033C ̼ in /t̼͡θ̼/`) as well as the tie: the marked and the plain affricate measured the same edge F2, 1593.7 Hz. This is a Tier A loss too: any marked affricate the template lacks (t̪͡s̪, t̠͡ɹ̠̊˔) is said without its marks, and reported. *Default: in the next front-end change, a tied pair with no line of its own is split at the tie and each letter composed with its own marks (C4); the tie stays reported as said in a row; and the affricate itself (closure, then the stop released into the fricative, as one segment) is built as a mechanism through the USP, after which t̼͡θ̼ and d̼͡ð̼ are proved. Until then those two Tier B records are `MISSING`.* **First half done (2026-10-07, eleventh session, D71):** the front-end (`evv_map.c`, `evv_map_lookup_ex`) splits a tied pair with no line of its own at the tie and looks up, or composes, each side with its own marks (/t̼͡θ̼/ is now `t` with f2=75 and `θ` with f2=75, where both marks were skipped), and reports the pair as `tie-as-sequence` (a loss: it is not yet one segment). extIPA's sliding mark (U+0362) joins two letters the same way. The affricate as one segment is still to do, so t̼͡θ̼ and d̼͡ð̼ stay `MISSING`. **Second half done (2026-10-09, seventeenth session, D84):** an affricate the template has no phone for is made as the stop released into the fricative's friction (D72's `frel`), one sound with a line and a `letter` line of its own (t͡θ, d͡ð), and the front-end composes the marks of both sides on it (t̼͡θ̼ is t͡θ with ̼, no loss); t̼͡θ̼ and d̼͡ð̼ are proved.

**Q23. The raised mark makes no friction on a consonant** (2026-10-07, eighth session, D68). The IPA's own example of ̝ is an approximant raised to a fricative (ɹ̝, a voiced alveolar fricative), and extIPA's lateral fricatives ꞎ 𝼅 𝼆 𝼄 are defined by the equivalents ɭ̝̊ ɭ̝ ʎ̝̊ ʟ̝̊. In this engine ̝'s consonant transform only lowers F1 by a tenth (an `estimated` value; its proof is on vowels only), so ɭ̝ is an ɭ with a lower F1 and no noise: a mark cannot change the carrier, and the accent layer has no key that turns on a frication source over a voiced approximant's frames. *Default: the four extIPA letters are made letters of their own (created, on a fricative carrier, like ɬ and ɮ), and Tier A's ̝ on an approximant base is given a fricative realisation at the next engine change (a key for a frication source, or a composition rule that moves an approximant + ̝ onto its fricative letter), proved on ɹ and l; until then ̝ on a consonant is the F1 change only, and the proof says so.*

*Q23, corrected (2026-10-07, ninth session, D69):* the accent layer does have a key that turns on a frication source over a voiced sound: `fric` (with the band levels `a2` to `a6` and `ab`) raises AF while the voice goes on; D69 uses it for extIPA's nasal friction, and the frames of m͋ show AF 60 with AV 49. It cannot serve ̝ as a mark's line, though: a `mod` line applies to every consonant, and `fric` raises AF in a stop's closure too, and sets the band levels there with it (`evv_accent.c` 2576 to 2586: no test for a stop; only the later blend of the band levels, from 2588, skips stops). *Default unchanged: ̝ on an approximant becomes a fricative by a composition rule (or a mark line restricted by stricture) at the next front-end or engine change.*

**Q24. A mark's test compares the medians of the plain and the marked cases, not their differences context by context** (2026-10-07, ninth session, D69). `check_shift` takes the median over the three contexts of the plain sound and, separately, of the marked one, and compares the two; its own comment says the comparison is "a mark against its own base in the same context: the context's variation cancels", which is true only of paired differences. m͇ shows the cost: the engine raised the vowel's requested F2 onset in all three contexts (1640 to 1770, 2132 to 2301, 1148 to 1239 Hz), but the tracker read [i] after m as 3092 Hz plain and 1325 marked, and the medians came from different contexts (plain 1670, marked 1651: -18.7 Hz, "the wrong way"). *Default: at the next change of the sweep, judge a mark by the median of its per-context differences; then run the whole sweep, since every mark's proof and some Tier A ones may move. Until then m͇ is MISSING.* **Done 2026-10-07 (tenth session, D70):** `check_shift` judges each measure by the median of its per-context differences (marked minus plain, wherever both were found; the medians as before where fewer than two contexts have both), against the plain median's size; each target in a proof lists the differences (`paired`). m͇ then moved +78 Hz (differences -1193, +78, +79: the tracker's [i] outvoted), n̪͆ -25 Hz (-82, -25, -19), ɬ̪͆ -36 Hz (-42, -36, -19); tʰ̪͆ -13 Hz (-59, -13, -5), still short of the 1.5 per cent (Q25).

**Q25. Four extIPA spellings on the new marks are not yet** (2026-10-07, ninth session, D69). n̪͆ and ɬ̪͆ moved their edge F2 by -18.8 and -18.6 Hz against a minimum of about 19.7 (1.5 per cent): the engine realises about 1.4 per cent of the 6 per cent asked of n and ɬ (the mark's own bases p, f, m move by 2.0 to 3.6 per cent); tʰ̪͆ by -5.2 Hz (the aspiration lies between the release and the vowel, which begins after the place's transition is mostly over); m͇ by Q24. The bidental fricatives h̪͆ and ɦ̪͆ are not composites: h is made by the layer from the vowel after it, so the marks have nothing to move, and a bidental fricative needs a letter of its own through the USP (no measurement of one has been looked for yet). *Default: n̪͆ and ɬ̪͆ wait for Q24's paired test, not for a larger value (0.94 comes from its source); tʰ̪͆ is judged at the release's noise instead of the vowel's onset once a measure of where a release's noise lies exists; h̪͆ and ɦ̪͆ go through the USP with the other needs-new letters.* **The bidental fricatives done 2026-10-09 (fifteenth session, D79)**: letters of their own, spelt with three characters, on h's and ɦ's layer-made breath with friction through the teeth. **tʰ̪͆ done 2026-10-09 (sixteenth session, D80)**: judged at the release's noise, as the default said, it is no longer a composite but a letter of its own spelt with four characters, t released into h̪͆'s friction for the length of tʰ's aspiration; its release noise is 19.0 dB above 3 kHz against below 1 kHz where tʰ's is 0.3 (the new `rel_hf_db`), its centre 3570 Hz (h̪͆'s target 3514).

**Q26. The nareal fricative's current spelling, U+033E, is not read** (2026-10-07, ninth session, D69; found by the R15 review). The Tier B inventory and `ipa/unicode_net.toml` record that extIPA changed the mark from U+034B to U+033E (vertical tilde) in 2024, and the 2025 chart uses U+033E. The table has U+034B only, so text written to the current chart is not read as nasal friction (the reader refuses U+033E in strict IPA; the front-end leaves it off with a `mark-left-off` loss). *Default: make U+033E an alias of U+034B (`ipa/aliases.toml`, and its own `mod` line from the adapter so the front-end composes it), with a test that both spellings say the same, at the next change of the reader or the adapter.* **Done 2026-10-07 (tenth session, D70):** U+033E is an `always` alias of U+034B in `ipa/aliases.toml` (the reader reads it as U+034B), and the adapter writes every mark's line again under a one-character alias of it (`mod ̾ c fric=60 a5=60 ab=60`), since the front-end composes by the character it is given; the reader's test now checks that each such alias reads alike on a letter.

## For Phase 2 (found by measuring in Phase 1)

- Quechua (`qu`): in the golden case `s|t\``, the engine meant a final vowel `a` and gave it 11 frames with neither voicing nor noise (silent). Check whether the map or the template devoices it deliberately.
- Western Armenian (`hyw`): its eSpeak NG phonemes `p` and `t` are mapped to the module's `b` and `d` (sound `s24`), so they are said prevoiced (VOT -80 and -95 ms). Western Armenian does voice the historical /p t/, so this may be right, but the phonemes are labelled /p t/: Phase 4 should check the eSpeak NG table and the map together.
- English-based packs read by eSpeak NG (en-029, en-gb-x-rp and others): the diphthong cases `e@`, `i@`, `i@3` begin with a `t` whose whole span is closure; harmless, but a sign that the module merges the burst into the vowel.

**Q27. Pre-aspiration is made shorter than asked** (2026-10-07, tenth session, D70). extIPA's ʰ◌ asks the layer's `pre` for 98 ms of breath before a stop's closure (rogers1995, fast speech); between vowels the frames carry 30 ms before p, 40 before t and 20 before k. The layer takes the voice out of a stop's own frames before its closure, and the module gives a stop only that much of the vowel's tail; the vowel before is already spoken by then. The entry is `approximate` with this stated. Making the whole length would mean the layer reaching back into the vowel before (as `lead` reaches before a voiced stop's release), an engine change under R18. *Default: leave it approximate until a pack needs pre-aspiration (Icelandic, Scottish Gaelic, Faroese, Sámi); then extend `pre` and prove it against rogers1995.*

**Q28. A whispered vowel before a stop ends with 10 to 15 ms of voice** (2026-10-07, eleventh session, D71; found while making extIPA's reiteration). In `pə̥pa` the frames of the whispered [ə] carry breath and no voice, but its last two or three (at 115 to 125 ms) carry the module's voice (AV 52) where it moves into the next closure: the layer's `whisper` acts on a sound's own frames, and those belong to the stop's way in. The same happens wherever ̥ marks a vowel before a stop, and in extIPA's reiteration (`p\p\pa`, said with a whispered schwa between the repetitions). Tier A's ̥ on a vowel passes its tests (its proof judges the vowel's own frames), so nothing has been marked as failing. *Default: at the next engine change, carry a whispered sound's voice-off into the next sound's way-in frames while they are still its vowel's, rebuild, run the golden and the whole sweep; until then reiteration states it as a deviation.*

**Q29. Nothing measured tells a fricated release from an affricate, and the lateral ones are not told from the median** (2026-10-08, twelfth session, D72). extIPA's fricated releases (tᶿ kˣ d𐞞 k𐞜 t𐞙 d𐞚) are made as a stop released into friction of the place the superscript names (the accent layer's new `frel`). Their lengths come from Liverpool English's fricated /t/ and /k/ (sangster2002: 55 to 98 ms between vowels, 75 the median; /d/ 45.5 ms word-initially), which is about as long as an affricate's release friction elsewhere (kye2025: ts 64.5 ms, the lateral tɬʼ 48.2 ms); the only statement that a fricated release has "less frication" than an affricate is Wikipedia's, unsourced. Within the engine, k𐞜 is said as kˣ (𝼄's noise bands are x's in this table; its laterality is in formants a release over the vowel's onset does not move), and the lateral-and-median releases are one noise with both fricatives' bands. *Default: keep the Liverpool lengths and the stated deviations; a phonetician, or recordings of a fricated release in a language or a clinical sample that uses one, should judge whether the release is too long (an affricate) and whether k𐞜 and kˣ must differ. All six marks and their six spellings are `approximate` until then.*

**Q30. A t voiced by ̬ loses its voice for 5 to 10 ms just after its release** (2026-10-08, twelfth session, D72; found while checking the R15 review's finding on t̬ᶿ). In `ˈat̬a` on the development stage the frames carry the layer's voice through the closure (AV 34) and the burst (38), then, 15 ms after the release, one frame with no voice and breath 41 and one with AV 28 and breath 10, before the vowel's voice. The module's own t asks for a breath there, and the layer's `voi=1` does not fill a frame whose friction has just stopped. Tier A's ̬ passed its test (the share of voiced frames), which a two-frame gap does not move. *Default: trace it at the next engine change (the `voi` branch of the sound's own frames against the release's frames); until then ̬ on a voiceless stop keeps this gap, and t̬ᶿ with it.*

**Q31. A voiced lateral release on ɡ: ɮ's own F3 under the friction hides it from the periodicity test** (2026-10-08, thirteenth session, D73). D73 gives a release's friction the named fricative's own F3 (and F2 where its noise lies on F2). For 𐞞 (ɮ, F3 2652 Hz) the release's periodicity on ɡ then moved by 1.97 to 1.998 dB, against the 2 its test needs, in three designs (ɮ's F2 and F3; F3 alone; F3 and ɮ's own voice level, -13 dB): the marked ɡ is steadily aperiodic (-4.7, -4.4, -4.6 dB in [a], [i], [u]) but the plain ɡ is already aperiodic in two contexts (-3.1, -2.6: the module's velar release carries its own noise), so the paired median cannot reach 2 dB. 𐞞 keeps the vowel onset's F3 (as in D72), a stated deviation; 𐞚 keeps ɮ's F3. *Default: when a measure of a voiced release's friction that does not depend on the base's own release noise exists (the friction's spectrum against the voiced fricative's own, say), give 𐞞 ɮ's F3 again and judge it by that; nothing for the human to decide.*

**Q32. extIPA's ͌ (velopharyngeal friction, D71) silences the voice of a voiced letter** (2026-10-09, thirteenth session; found while designing ʩ̬). ͌'s transform sets the friction's level (`fric`), and the accent layer says a sound with `fric` as a sound it makes itself, with no voice unless `voi=1` (`made()`). D71 tested ͌ on s, f, ʃ only, which are voiceless. On ŋ, ŋ͌ measured a voiced share of 0.097 (`%USERPROFILE%\OpenEvvBuild-ttsext\d77_attempt\sweep_d77a.log`), the same as ŋ̊͌: voiced and voiceless velopharyngeal friction would be said alike. *Default: at the next engine change, keep a voiced letter's voice under a mark's added friction (or have the mark's line carry `voi` from its letter), add a voiced base to ͌'s tests (ŋ, or a voiced fricative), and re-run the whole sweep; nothing for the human to decide.* **Answered 2026-10-09 (fourteenth session, D77): a misdiagnosis.** ŋ͌ keeps its voice (23 of 23 frames voiced); the attempt's ʩ̬ was spelt `ŋ̬̊͌`, and ̊ set the voice off. What was real: at 60 dB ͌'s friction did not show over a voice (the synthesiser holds AF plus a parallel gain at 120 dB). The layer's new key `fgain` makes it 15 dB louder over a voice; ŋ is now one of ͌'s test bases, its voice kept and its periodicity lowered by 5.1 dB; the whole sweep was re-run.

**Q33. ̬ cannot voice a letter whose own line is whispered** (2026-10-09, fourteenth session, D77). The accent layer takes the voice out of any sound that carries `whisper` (it makes ŋ̊, ʩ and 𝼀 voiceless that way), and ̬ only sets `voi=1`, so 𝼀 with extIPA's partial voicing ◌̬᪽, or ʩ written with ◌̬᪽, is composed with `voi=1` and `whisper` together and is said voiceless: the front-end and the adapter agree on the keys (`compose_test.py`), but the sound loses the voicing the marks ask for. It cannot simply be let go: ɦ and ʕ are `voi=1` with `whisper` on purpose (breathy voice). ʩ̬ and 𝼀̬ are not affected (letters of their own, no `whisper`). *Default: at the next engine change, give a mark's voicing a key of its own that overrides a letter's whisper (or have the front-end drop a letter's `whisper` when a mark sets `voi=1` on a letter whose `voi` is 0), test ̬ and ◌̬᪽ on ʩ and 𝼀 by their voiced share, and re-run the whole sweep; nothing for the human to decide.*

**Q34. Two latent gaps found with the percussives** (2026-10-09, fifteenth session, D78; neither changes what any entry says today). (1) The map's `letter` lines carry no `release` (nor `place_mark`), so ǃ¡ and ǃ have the same letter line and the front-end's nearest-letter fallback finds them 0 apart; ǃ¡ comes first, so a letter with no line of its own whose nearest is ǃ would be said with a slap. Every letter of the dedx map has a line, so it cannot happen now. (2) A strike's noise bands and a fricated release's (`frel`, D72) are the same keys, `a2` to `ab`: ¡ with ˣ is composed with ˣ's bands in place of ¡'s, so its strike takes the velar friction's spectrum (the front-end and the adapter agree, `compose_test.py`). *Default: at the next front-end or adapter change, write `release` and `place_mark` into the letter lines and count them in the fallback's distance; give the strike bands of its own if a mark on a percussive ever matters (none is attested); nothing for the human to decide.* **(1) done 2026-10-09 (sixteenth session, D80)**, at the front-end change of D80: the letter lines carry `release`, `place_mark`, `aspiration`, `fricated_release` and `tongue_part`, and the fallback counts them (weights 2, 1, 2, 2 and 1, `estimated` as every weight is); tʰ̪͆ and t, ǃ¡ and ǃ are no longer 0 apart. (2) stands.

**Q35. Left against right, told apart by a convention** (2026-10-09, seventeenth session, D83). extIPA's offset marks ◌͔ ◌͕ (the main gesture offset to the listener's right or left) and VoQS's offset jaw J͔ J͕ name a side, which nothing measured tells apart and one channel of sound cannot carry. Under the human's rule (two symbols the chart tells apart must not be said alike) each pair is now set apart by a stated convention: ◌͕'s lateral sibilant has its peak a little higher than ◌͔'s (F4 at 0.76 of [s]'s against 0.70), and J͕'s F3 is a little higher than J͔'s (1.03 against 0.97). *Default: keep the conventions until a phonetician or a recording says how a side shows in sound (an asymmetric lip or jaw opening may move the formants' bandwidths more than their frequencies); replace them then, the tag becoming `literature` or `measured`.*

**Q36. Flutter is not used** (2026-10-09, seventeenth session, D83). The synthesiser's flutter (FL, a slow wobble of the pitch at three fixed rates) was offered to the labels as a key `fl` and taken out again: at its most it moved the pulses' spacing by under a point, so harsh voice and the voices like it are made with the diplophonia (DI) alone, on a constricted voice. A random cycle-to-cycle jitter, which harsh, oesophageal and tracheo-oesophageal voices have and diplophonia's regular alternation is not, is not made. *Default: at the next engine change, consider a jitter key of the accent layer (each period's length moved at random by a set share), tested against `pulse_jitter_pct`; until then those labels stay `approximate` with this deviation stated.*
