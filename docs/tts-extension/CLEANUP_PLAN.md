# Cleanup plan (Phase 14)

Written 2026-10-12 by the twenty-ninth session (Opus 5.5, effort high), on branch `tts-ext/phase-13`. Step 1 of playbook Phase 14: an inventory, read only. **Nothing here is deleted without the human's yes to its category** (answers logged in `HUMAN_ANSWERS.md`). Only paths listed in this file may be deleted.

## The guard

| Check | Result |
|---|---|
| `PROJECT_STATE.md` says Phase 13 is complete and the installer tested | yes: "Phase 13 ... COMPLETE (2026-10-12)", installer 1.4.0 built, tested, published |
| another session with `isRunning: true` (`list_sessions`, archived included) | none (40 other sessions, every one `isRunning: false`) |
| `git status -sb` | `## tts-ext/phase-13...origin/tts-ext/phase-13`, two untracked files, `diag-compare.json` and `diag-golden.json`: Phase 13's own tool output, named as untracked in `PROJECT_STATE.md` ("For Phase 14"); not anyone's pending work |
| processes from `OpenEvvBuild*`, `msys64`, a `venv` | 0 |
| files under the work folders changed in the last 30 minutes | at 13:07, 11,783 in `%USERPROFILE%\OpenEvvBuild-ttsext` (newest 12:53:04): the Phase 13 session's last fresh-clone check after D100 (`clone-check-everything`, `p13\fe-intree-x64`); that session is not running. At 13:23, 84 (the tail of the same writes). Checked again before each deletion; nothing is deleted while a folder is still being written |

## Disk before

`Get-PSDrive C` (2026-10-12 13:07): **Used 268.92 GB, Free 683.43 GB.** The human says the drive was at about 170 GB before the project began: about 99 GB of growth.

## Where the 99 GB went (measured)

| Whose | GB | What |
|---|---|---|
| this project | about 67.0 | the rows of categories A to F below |
| the Claude app's own storage (protected) | 9.74 + 1.61 | `%APPDATA%\Claude` (`vm_bundles` 8.34 GB, caches); `%TEMP%\claude` (session scratchpads). The app owns them: Settings, storage page |
| not this project | the rest | Windows' page file (7.8 GB, sized by Windows), browser and driver updates since 2026-09-28 (Chrome, Brave, Edge, Copilot, NVIDIA App's driver cache 0.8 GB), `OneDrive\dev\pocket-tts-sapi5` (another project), other SAPI projects' folders. Not counted to the GB: no baseline from before the project exists |

**A finding about `%LOCALAPPDATA%`**: `%LOCALAPPDATA%\OpenEvvBuild` and `%LOCALAPPDATA%\OpenEvvBuild-ttsext` are stored, by Windows' redirection for the Claude app, inside `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\`. It is one copy, not two (`fsutil file queryfileid` gives the same file id `0x...070000000c895f` by both paths). They are this project's build folders (the playbook names them in category B), so they are deleted by their `%LOCALAPPDATA%` path only, and nothing else in the Claude package folder is touched (it also holds other projects' folders: LucentSAPI, BestSpeech, AcuVoice SAPI5 and others).

## Installers to keep (Step 2, before anything is deleted)

| File | Bytes | Where now |
|---|---|---|
| `OpenEVV-SAPI5-Setup-1.4.0.exe` | 34,222,020 | `output\` (also `release\1.4.0\` in git, `p13\download-check\`, `clone-check-everything\release\1.4.0\`) |
| `OpenEVV-eSpeak-NG-languages-1.4.0.zip` | 27,240,394 | `output\` |
| `OpenEVV-eSpeak-NG-samples-1.4.0.zip` | 107,846,796 | `output\` |
| `OpenEVV-SAPI5-Setup-1.3.0.exe` | 34,177,557 | `output\` (built, never published) |
| `OpenEVV-SAPI5-Setup-1.2.0.exe` | 33,184,697 | `%LOCALAPPDATA%\OpenEvvBuild\dev\OpenEvv-sapi5\output\` |
| `OpenEVV-SAPI5-Setup-1.1.1.exe` | 33,111,568 | same |
| `OpenEVV-eSpeak-NG-languages-1.2.0.zip` | 26,851,311 | same |
| `OpenEVV-eSpeak-NG-samples-1.2.0.zip` | 97,880,307 | same |

Copied to the folder the human chooses, `Get-FileHash` of source and copy compared, a `README.txt` beside them.

## The candidates

Sizes from `Get-ChildItem -Recurse -File -Force | Measure-Object Length -Sum` (GB = 2^30 bytes). No candidate is, or holds at its top level, a junction or symbolic link (checked: `Attributes -band ReparsePoint`, 0 found); each is checked again, recursively, before its deletion.

### A. Test and render output

| Path | GB | Files | Created | Changed | Wrote it | Rebuildable |
|---|---|---|---|---|---|---|
| `%TEMP%\OpenEvvTests` | 26.74 | 739,636 | 2026-09-28 | 2026-10-12 | the harness (`harness` 19.36 GB: renders, per-case `.tsv` dumps), `harness-create-b` 4.67, `sapi_test` outputs, stages of the worked examples | yes: every run writes it again |
| 66 items in `%TEMP%` (list below) | 0.19 | | 2026-10-05 to 10-12 | | scratch of Phases 3 to 13: `p11`, `p12dry`, `p12_dbl_proofs`, `effect_*` (14), `packs_*` (2), `packet_eo-x-evvskill_*`, `compose*.log` (3), research papers fetched for reading (`lt08`, `zas154`, `insp16`, `ek08`, `chg`, `swg`, `yosh`, `jang25`, `cassia`, `cho02`, `kor`, `ic91`, `smile15`, `clopper` .pdf/.txt; the sources are cited with their URLs in `REFERENCES.md`), `ucd` (Unicode data), JSON and text dumps, `OpenEVV_installer_a11y_setup.log` | yes |
| `docs\tts-extension\harness\results\diag-compare.json`, `diag-golden.json` (untracked) | 0.0001 | 2 | 2026-10-12 | | `diag.py --compare`, `golden.py` | yes |

The 66 `%TEMP%` items, by name: asr_head.json, asr_p12.json, cassia.pdf, cassia.txt, chg.pdf, chg.txt, cho02.pdf, cho02.txt, clopper.pdf, clopper.txt, clopper_wb.html, cmu_arctic_before.json, compose_run.log, compose_run2.log, compose3.log, dump.txt, effect_ca-va-x-evvdemo_7035z4ze, effect_ca-va-x-evvdemo_ctfpq4vj, effect_ca-va-x-evvdemo_irpmmqsu, effect_ca-va-x-evvdemo_usjegxj3, effect_ca-va-x-evvskill_3d91pj0i, effect_en-gb-scotland_aa6smoqd, effect_en-gb-scotland_gklrstt1, effect_en-gb-scotland_j12pthsb, effect_en-us-x-evvdemo-es_2ico5lh3, effect_en-us-x-evvdemo-es_gtpfigk_, effect_en-us-x-evvdemo-es_jafja4n2, effect_en-us-x-evvskill-es_5i3hb1s7, effect_nl-be_bwbi6vt0, effect_nl-be_v9bovyo4, ek08.pdf, evvdump.json, fleurs.md, g14.txt, ic91.pdf, ic91.txt, icpla.html, insp16.pdf, insp16.txt, jang25.pdf, jang25.txt, kor.pdf, kor.txt, lt08.pdf, lt08.txt, old_up.json, OpenEVV_installer_a11y_setup.log, oq_head.md, p11, p12_dbl_proofs, p12dry, packet_eo-x-evvskill_pdzft2s6, packs_12ty8au0, packs_bm1syj_a, smile15.pdf, smile15.txt, status_head.json, swg.pdf, swg.txt, tagblobs.txt, tum.txt, ucd, yosh.pdf, yosh.txt, zas154.pdf, zas154.txt.

**Not in the plan, left alone**: the other 3,002 new items of `%TEMP%` (0.10 GB: `*.tmp.js`, `*.tmp.png`, 1,632 `tmp*`, `is-*-uninstall.tmp`, `mdc_*.html`, `a`, `b`, `a.json`...), because their names do not prove they are this project's; Windows' own "Temporary files" clean-up (Settings, System, Storage) removes them safely.

### B. Build files

| Path | GB | Files | Created | Changed | Wrote it | Rebuildable |
|---|---|---|---|---|---|---|
| `%USERPROFILE%\OpenEvvBuild-ttsext`, all but `models` and `venv` | 23.04 | 416,642 | 2026-10-05 | 2026-10-12 | every phase: `p13` 7.30 (scratch packs, stages, maps, the 146 rendered samples, `download-check`), `p12-measure-work` 4.50, `build3a` 1.22 (the engine work copy), four fresh-clone checks 4.28 (`clone-check-everything`, `-p13`, `-p13-main`, `-p10`), `p12c` 0.68, `p12-sweep-work` 0.63, `corpora` 0.32 (CMU ARCTIC awb, licence in `REFERENCES.md`), `pre-release-1.2.4` 0.24 (also in git, tag `tts-ext-pre-release`), the stages (`stage-dev` and others), 33 module builds, the front-end builds `fe`, 388 loose logs and scripts 0.45 | modules: MSYS2, about 4 minutes a module; the staged golden recordings and the stages are gone for good (the goldens in git stay) |
| `%LOCALAPPDATA%\OpenEvvBuild` | 7.25 | 108,518 | 2026-09-28 | 2026-09-29 | the 1.1 to 1.2 work before the TTS extension: `dev` 5.24 (an old copy of the repository with the 1.1.1 and 1.2.0 installers, and the eSpeak NG checkout at `openevv-1.2.0`, now in the tree as `third_party/espeak-ng`, D100), `openevv` 1.41, `modules` 0.32, front-end builds | yes (D100: the front-end builds from `third_party/espeak-ng`) |
| `%LOCALAPPDATA%\OpenEvvBuild-ttsext` | 0.88 | 15,348 | 2026-10-05 | 2026-10-05 | Phase 0: `venv` 0.53 (the first venv, never used), `openevv` 0.30, `modules` 0.05 | yes |
| repository `build_x64`, `build_x86`, `build_frontend_x64`, `build_frontend_x86` (git-ignored) | 0.13 | | 2026-10-05 | 2026-10-12 | `cmake`, `build_all.bat` | yes: `cmake --build` |
| repository `__pycache__` (13 folders, git-ignored) | 0.001 | | | | Python | yes |
| repository `output\` (git-ignored) | 0.19 | 4 | 2026-10-11 | 2026-10-12 | `build_all.bat`, the zips | only after Step 2's copies are hash-verified; 1.4.0's installer also stays in git (`release\1.4.0\`) |

### C. AI models, weights, Python environments

| Path | GB | Created | What | Rebuildable |
|---|---|---|---|---|
| `%USERPROFILE%\OpenEvvBuild-ttsext\models\faster-whisper-large-v3` | 2.88 (3.09 decimal) | 2026-10-05 | the Whisper model of the ASR round trip | a 3 GB download (`docs/tts-extension/harness/README.md`) |
| `%USERPROFILE%\OpenEvvBuild-ttsext\venv` | 1.27 | 2026-10-05 | the harness Python (numpy, scipy, faster-whisper, CUDA libraries) | `pip install` again |
| pip cache `%LOCALAPPDATA%\pip\cache` | 3.77 | 2026-07-08 | **0.63 GB written since 2026-09-28 (this project's venv), 3.14 GB older (other projects)**; `pip cache purge` clears all of it | wheels download again |
| `%USERPROFILE%\.cache\huggingface` | 0.21 | **2026-09-01** | before this project; not its | left alone |

### D. Tools the project installed

| Item | Size | Dated | Note |
|---|---|---|---|
| MSYS2, `C:\msys64` | 1.62 GB, 34,695 files | 2026-09-28 | builds the engine modules; without it modules cannot be rebuilt |
| `pypdf 6.19.0` in Python 3.10 (system) | under 0.01 GB | 2026-10-07 | read the IPA chart and papers |
| `pillow 12.3.0` in Python 3.10 (system) | about 0.01 GB | 2026-09-28 | origin not certain (that day other projects were worked on too) |
| **Not this project's, left alone**: the installed `OpenEVV SAPI5 1.4.0` program (the product; the human installed it 2026-10-12), `eSpeak-NG SAPI`, `SSI-263 SAPI`, `Votrax SC-01`, `Pocket TTS SAPI5`, Git 2.56 (an update of the Git installed before), browsers, LibreOffice, Python, CMake, Inno Setup, Visual Studio Build Tools | | | |

### E. The repository working copy

`C:\Users\joshk\OneDrive\dev\espeakproject\OpenEvv-sapi5`: 1.52 GB, 13,642 files (`.git` 0.39 GB). Everything is on GitHub (`origin`): `tts-ext/phase-13` and `main` both at `8c9e0329`, in step with `origin`. Branches `tts-ext/phase-0` to `phase-4` have no upstream set (their commits are ancestors of the pushed branches; checked before any deletion). Git-ignored review-packet audio and spectrograms (about 25 MB, rebuildable) live here too. **Default: keep.** It is in OneDrive: deleting it deletes OneDrive's cloud copy too.

### F. Sessions

40 other sessions (none archived), all with this repository as their folder: 34 "TTS extension Phase N" or "Phase N ..." sessions, and the helpers "Whisper installation location", "Unicode data and vowel research downloads", "OpenEVV TTS extension playbook", "Phase 10 rules and openEVV documentation", "Phase 11 TTS playbook and project cleanup", "IPA sounds for new languages". They use about 0.85 GB (`~\.claude`); deleting them tidies the sidebar more than the disk. This session goes last. The auto-memory folder `~\.claude\projects\...\memory`: default keep.

## Protected, not touched

The human's own files (`OneDrive\Music`, `Documents`, `Videos`, `Pictures`, `Desktop`, `Downloads`), other projects (`OneDrive\dev\pocket-tts-sapi5`, `~\.pockettts`), Claude's own storage (`%LOCALAPPDATA%\Packages\Claude_*` except the two `OpenEvvBuild*` folders reached by their `%LOCALAPPDATA%` path, `%APPDATA%\Claude`, `%TEMP%\claude`), software installed before 2026-09-28. The Recycle Bin and OneDrive's online recycle bin are the human's to empty.

## How each deletion is done

Full path resolved and compared with this list; a recursive search for a junction or symbolic link inside it (refused if one is found); `cmd /c rmdir /s /q <path>` (a file: `cmd /c del /f /q`); `Test-Path` after; `Get-PSDrive C` after each category. No wildcard over a parent folder, no `git clean`.

## What was done (2026-10-12)

| Step | Answer | Done | Free space after (`Get-PSDrive C`) |
|---|---|---|---|
| before | | | 683.43 GB free, 268.92 used (13:07) |
| 2 installers | Documents\OpenEVV-Installers (OneDrive is uninstalled: a plain folder) | 8 files copied, 8 SHA-256 equal, `README.txt` written | 682.30 (other activity and the copies) |
| A | yes, all three | `%TEMP%\OpenEvvTests`, the 66 items, the two untracked results: 69 paths, 0 refused, 0 left | 709.90 (+27.60) |
| B | yes, all of B | 490 items of `OpenEvvBuild-ttsext` (all but `models`, `venv`), both `%LOCALAPPDATA%\OpenEvvBuild*`, `build_x64`, `build_x86`, `build_frontend_x64`, `build_frontend_x86`, `output`, 13 `__pycache__`: 510 paths, 0 refused, 0 left. Guard checked first: 0 files changed in 30 minutes, 0 processes | 740.86 (+30.96) |
| C | yes, both; purge the pip cache | `models`, `venv`, then the empty `OpenEvvBuild-ttsext`; `pip cache purge` (pip 23.0.1 removed 65 files and left `http-v2`, 3.65 GB, which it does not know), then `pip\cache\http-v2` deleted under the same yes; pip cache left 0.0000 GB | 748.82 (+7.96) |
| D | remove MSYS2; uninstall both packages | `C:\msys64` deleted; `pip uninstall -y pypdf pillow` | 750.20 (+1.38) |
| tags | push | `tts-ext-baseline`, `tts-ext-pre-release` pushed (`git ls-remote` shows both) | |
| E | delete it, last | after this file's last commit: branches proved on `origin` (every local branch at the same commit on GitHub), the tree clean, a fresh clone checked, then deleted | in `CLEANUP_REPORT.txt` |
| F | delete all 40; delete the memory notes | after E | in `CLEANUP_REPORT.txt` |

Every deletion went through one script (`safe_delete.py`, session scratchpad): a path not on the list refused; a folder that is or holds a junction or symbolic link refused (0 found); `cmd /c rmdir /s /q` or `del /f /q`; gone checked after.

**Step 4, the stray search again** (whole of C:, outside Windows and the Claude app's folders; files over 100 MB new since 2026-09-28; `*.wav *.mp4 *.tsv *.png` and model files; `venv`, `__pycache__`, `build*`, `stage*` folders): files over 100 MB 36 → 27 (left: Program Files, ProgramData, the page file, `pocket-tts-sapi5`, this repository's git pack, the installers folder's samples zip); pattern files 1,103,700 → 4,157 (this project's left only in this repository and in `~\.claude\projects\...OpenEvv-sapi5`); new venv, build or stage folders 1,840 → 24 (none this project's). Left, explained: this repository (E) and the project's session folder (F), both deleted last; the installers folder (kept); the installed program `OpenEVV SAPI5 1.4.0` (the product, the human's).
