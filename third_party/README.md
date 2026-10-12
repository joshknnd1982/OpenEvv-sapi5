# third_party/: other people's work kept in this repository

Each folder here is someone else's work, kept unchanged under its own licence, so that a `git clone` of this
repository holds everything the project rests on. None of it is under this project's MIT licence;
`docs/tts-extension/LICENCE_AUDIT.md` puts every file in a class and `engine/check_licences.py` checks it.

## espeak-ng/

The eSpeak NG source that the 146 languages read by eSpeak NG are built from: the library, and for every
language its dictionary (`dictsource/<code>_list`, `<code>_rules`), its phoneme table (`phsource/`) and its
voice file (`espeak-ng-data/lang/`). It is the `openevv-languages` branch of
[joshknnd1982/espeak-ng](https://github.com/joshknnd1982/espeak-ng/tree/openevv-languages) at the tag
`openevv-1.2.0` (commit `1eadf123ffea44585eb81ed1f96d96add95536bf`), the tag `frontend/CMakeLists.txt` names and
release 1.4.0 was built from: 2,690 files, each byte-identical to the tag's (checked file by file when it was
copied, 2026-10-12), except that `src/include/espeak/speak_lib.h`, a symbolic link in the tag, is a copy of the
file it points to (`src/include/espeak-ng/speak_lib.h`), so that a clone on Windows builds.

- **Licence**: GPL-3.0-or-later (`espeak-ng/COPYING`); `src/compat/getopt.c` BSD-2-Clause (`COPYING.BSD2`); parts
  of the Android app Apache-2.0 (`COPYING.APACHE`); Unicode data under `COPYING.UCD`, as its `README.md` says.
  It cannot be put under the MIT licence: GPL code can only be passed on under the GPL.
- **How it is used**: `frontend/` builds `OpenEvvFrontend.exe` (a separate program, also GPL) from this copy by
  default, so building needs no download; `ESPEAK_NG_SOURCE_DIR` still names another checkout. The compiled
  data the product installs is `dist/espeak-ng-data/`.
- **Changing how a language is read**: a correction to a dictionary or a rule is made in the fork
  (README.md, "Fix how words, letters, numbers or punctuation are read"), tagged there, and this copy is
  replaced by the new tag's tree at the next release.

## cmu_arctic/

CMU ARCTIC speaker awb, the recordings the Scottish English measurements rest on; `cmu_arctic/README.md` says
what it is and under which notice.
