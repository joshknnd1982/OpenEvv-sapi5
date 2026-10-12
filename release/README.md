# release/: the published installers, in the repository

So that a `git clone` holds the installer as well as everything it is built from (the human's choice,
2026-10-12, `docs/tts-extension/HUMAN_ANSWERS.md` Q68), each published release's installer is kept here, the
same file as on the [Releases](https://github.com/joshknnd1982/OpenEvv-sapi5/releases) page.

| Release | File | Bytes | SHA-256 |
|---|---|---|---|
| 1.4.0 (12 October 2026) | `1.4.0/OpenEVV-SAPI5-Setup-1.4.0.exe` | 34,222,020 | `821329171a28de7ff657131217c54068462344e8e804d67374abe7c8df0c663c` |

Run it to install OpenEVV SAPI5 (README.md, "Installing"). It is built from this repository by `build_all.bat`
(README.md, "Building from source"); this file is the one published, its hash checked after downloading it back
from GitHub.

Not kept here, and on the release page instead: the language-pack zip of the 146 languages read by eSpeak NG
(its contents are `languages/` in this repository) and the samples zip (146 recordings; remade from the tree in
about 90 seconds by `engine/render_espeak_samples.py`).

**Licence**: the installer bundles files under several licences: this project's own work (MIT), openevv (MIT),
IBM's language data in the language modules (not licensed here), eSpeak NG and the front-end (GPL-3.0-or-later),
the files adapted from the BestSpeech wrapper (their author's terms) and the community dictionary (CC0).
`NOTICE.md` and `docs/tts-extension/LICENCE_AUDIT.md` say which is which.
