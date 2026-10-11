# Review packet: Dutch (Southern Standard, Flanders) (nl-be)

Made 2026-10-11 by `engine/review/make_packet.py`. Open `index.html` in a web browser: every item is there
with its audio, its spelling, its IPA (as eSpeak NG, the reader, reads it) and a spectrogram whose
description gives the numbers in words. When the packet is made, the same audio is also written to
`audio/` and the pictures to `spectrograms/` (the repository keeps only `index.html`, which embeds them;
make the packet again to have the loose files).

**Send the reviewer** this folder, or just `index.html`, `CHECKLIST.md` and `feedback.toml`. Which A/B
version is which, and what each pair tests, is kept outside it (`docs/tts-extension/review/keys/`).

- Speaking module: `dedx`, preset 1 (adult male). Reader: eSpeak NG voice `gmw/nl`.
- Variety: Southern Standard Dutch (Belgian Standard Dutch): the vowels of adult male Flemish teachers of Dutch from the central region (Flanders-Brabant: the provinces of Antwerpen and Vlaams-Brabant), read-aloud /sVs/ words, as one published table gives them. Region: Flanders, Belgium (central region: Antwerpen and Vlaams-Brabant provinces). Speaker group the pack aims at: Adank, van Hout and Smits (2004): Southern Standard Dutch talkers, teachers of Dutch recorded in Flanders-Brabant, stratified for age and gender, 20 talkers; the men's means are used (their table gives N per cell 20, which for two tokens a vowel is read here as 10 men).
- Status when made: level 2 (engine-verified). Only a named native reviewer's sign-off makes it level 5
  (native-validated); until then nothing here is called authentic.

**For the reviewer:** read `CHECKLIST.md`, listen, and fill in `feedback.toml`.

**For the project:** `python engine/review/ingest_feedback.py <filled feedback.toml>` records it in
`docs/tts-extension/LANGUAGE_STATUS.md` (only with a named reviewer, a date and consent to be named).
