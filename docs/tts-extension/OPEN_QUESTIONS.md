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

## For Phase 2 (found by measuring in Phase 1)

- Quechua (`qu`): in the golden case `s|t\``, the engine meant a final vowel `a` and gave it 11 frames with neither voicing nor noise (silent). Check whether the map or the template devoices it deliberately.
- Western Armenian (`hyw`): its eSpeak NG phonemes `p` and `t` are mapped to the module's `b` and `d` (sound `s24`), so they are said prevoiced (VOT -80 and -95 ms). Western Armenian does voice the historical /p t/, so this may be right, but the phonemes are labelled /p t/: Phase 4 should check the eSpeak NG table and the map together.
- English-based packs read by eSpeak NG (en-029, en-gb-x-rp and others): the diphthong cases `e@`, `i@`, `i@3` begin with a `t` whose whole span is closure; harmless, but a sign that the module merges the burst into the vowel.
