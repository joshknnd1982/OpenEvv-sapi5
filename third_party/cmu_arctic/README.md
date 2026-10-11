# CMU ARCTIC, speaker awb (Scottish English, male)

From the CMU ARCTIC speech databases, J. Kominek and A. W. Black, Language Technologies Institute,
Carnegie Mellon University (http://festvox.org/cmu_arctic/). **Not this project's work and not under
its MIT licence**: the licence is CMU's notice in `cmu_us_awb_arctic/COPYING` ("free for use for any
purpose (commercial or otherwise)", keep the notice, mark modifications, keep the authors' names).

Kept in the tree at the human's request (2026-10-11, `docs/tts-extension/HUMAN_ANSWERS.md`) so that a
`git clone` holds what the Scottish pack's measured targets rest on. Fetched 2026-10-11 from the
unpacked tree http://festvox.org/cmu_arctic/cmu_arctic/cmu_us_awb_arctic/ :

| Path | What |
|---|---|
| `cmu_us_awb_arctic/wav/` | 1,138 recordings, 16 kHz, 16-bit mono, untrimmed (the packed tarball's audio is trimmed and does not fit the labels; it is not included) |
| `cmu_us_awb_arctic/lab/` | 1,138 phone label files (Festvox format: `end_time 125 phone`), made automatically, never hand-corrected, US phone set |
| `cmu_us_awb_arctic/etc/txt.done.data` | the prompts (from the packed tarball `cmu_us_awb_arctic.tar.bz2`) |
| `cmu_us_awb_arctic/COPYING`, `AREADME` | the voice's licence and readme |

**Modifications: none.** Files are byte for byte as downloaded. Used by
`engine/authenticity/extract_targets.py en-gb-scotland third_party/cmu_arctic` (docs/tts-extension/AUTHENTICITY.md).
