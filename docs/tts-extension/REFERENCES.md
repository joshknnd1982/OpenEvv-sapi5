# References

Every outside source this project has used: title, URL, access date, licence, what was used (R3). Record the licence before importing anything (R4). Nothing here has been copied into the repository; charts and tables are cited, and facts are written in our own words.

## The IPA chart (the standard the checklist follows)

| | |
|---|---|
| Title | The International Phonetic Alphabet (the IPA chart) |
| Publisher | International Phonetic Association |
| Version | The issue marked "© 2026 IPA", footer "IPA Chart revised to 2015/2005". The IPA's chart page says the 2018 and 2020 issues were this same revision and that the chart has been re-issued every year since 2025 with the year updated. The last change of a symbol was in 2005 (the labiodental flap ⱱ added). |
| URL | <https://www.internationalphoneticassociation.org/content/ipa-chart> (PDF: `.../IPAcharts/common_files/pdfs/pdfs_IPA_charts_E/IPA_Kiel.pdf`) |
| Accessed | 2026-10-05 |
| Licence | Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0), © International Phonetic Association |
| Local copy | `IPA_Kiel.pdf` in the human's Downloads folder, 603,341 bytes, SHA-256 `C8203013C676B243959072234526D60B874851D0509A00FD7528F4E56C706787`. Not in the repository (ShareAlike). Its text layer is in a legacy 8-bit font and cannot be read as text; the rendered page was read by eye. |
| Used for | Which symbols exist, in which section, with which label: the contents and the count of `inventory/IPA_CHECKLIST.md`. |

Cross-checks: the IPA's own number chart, symbol list and interactive-chart data (same site); the Unicode Character Database 18.0.0 (`UnicodeData.txt`, `NamesList.txt`, <https://www.unicode.org/>, Unicode licence) for every codepoint and character name, and Python 3.10's `unicodedata` (Unicode 13) again when the checklist is built; Wikipedia, "International Phonetic Alphabet" and "IPA number" (CC BY-SA 4.0), for IPA numbers and for the sentence "107 letters ... 31 diacritics ... 17 additional signs" used to reconcile the count.

## Descriptive phonetics sources for the acoustic correlates

116 sources, listed one by one with URL, licence, whether the source was actually opened, and what it was used for, in **`inventory/IPA_REFERENCES.md`** (generated from `inventory/research/*.json`). 112 were opened and read in this phase; 4 were not opened and are named only because an opened source quotes them. Two of those matter: the vowel formant values of Catford (2001) and of Peterson & Barney (1952) are in 25 vowel correlates **as quoted on an opened page** (Wikipedia's "Formant" article and a Princeton course page), and the checklist marks each one "as quoted there, not opened". Read the originals before any of those numbers becomes a target. Each correlate in the checklist names the sources it came from; a correlate with no opened source is tagged `recalled-unverified` and must be verified before any value is taken from it.

## Tool documentation

| Title | URL | Accessed | Licence | Used for |
|---|---|---|---|---|
| Claude Code documentation, "Configure permissions" | <https://code.claude.com/docs/en/permissions> | 2026-10-05 | Anthropic documentation | The syntax of permission rules for `.claude/settings.json` (see OPEN_QUESTIONS.md, Q1) |

## Sources already cited inside the repository (not re-read in Phase 0)

These are named by the existing code and documents as the origin of numbers already in the product. They were **not opened in Phase 0** and are listed so that later phases know what to read before relying on them.

| Where it is cited | What it names |
|---|---|
| `engine/accent/sounds.py:48-64` (`VOWEL`) | Peterson & Barney 1952; Hillenbrand et al. 1995; Catford 1988 |
| `engine/accent/sounds.py:118-123` (`LOCUS`) | Delattre, Liberman & Cooper 1955; Stevens 1998; Ladefoged & Maddieson 1996 |
| `engine/accent/sounds.py:128-133` (VOT) | Cho & Ladefoged 1999; Lisker & Abramson 1964 |
| `engine/accent/sounds.py:91` (`LENGTH`) | Lehtonen 1970; Fatima & Aden 2003 |
| `engine/profiles/<tag>.json` (`sources`) | per-language literature, 145 profiles |

## Software and data in the repository, with licences (see `NOTICE.md`, which is authoritative)

| What | Licence |
|---|---|
| openevv engine code (`openevv/src`, tools, tests) | MIT, © 2026 Stanislaw Przedzinkowski; additions here MIT |
| Language data (`openevv/lang/`, module DLLs in `languages/`, `klatt_tables.c`, `eci_xmltok_tables.c`) | IBM's; **not licensed here** |
| eSpeak NG, `frontend/`, `dist/espeak-ng-data`, the packs' `sounds.map`/`phonemes.map` | GPL v3 or later |
| The wrapper (`src/`, `engine/`, `installer/`) | MIT, except the BestSpeech-derived SAPI files listed in `NOTICE.md` |
| Community dictionary (`dictionaries/community/`) | CC0 1.0 |

## Phase 1 (2026-10-05): software, models and data the harness uses

All accessed 2026-10-05. Installed into the venv outside the repository; nothing of theirs is copied into it.

| What | Version | Licence (where stated) | Used for |
|---|---|---|---|
| numpy | 2.2.6 | BSD-3-Clause | everything |
| scipy | 1.15.3 | BSD-3-Clause | LPC, filters, spectra |
| matplotlib | 3.10.9 | PSF-style (matplotlib licence) | report pictures |
| jiwer | 4.0.0 | Apache-2.0 | CER / WER |
| soundfile | 0.14.0 | BSD-3-Clause | (available; the harness reads WAV with the standard library) |
| praat-parselmouth | 0.4.7 | GPL-3.0 (Praat: GPL) | `praat_crosscheck.py` only, which is GPL-3.0-or-later for that reason |
| faster-whisper | 1.2.1 | MIT | ASR |
| ctranslate2 | 4.8.2 | MIT | ASR runtime |
| nvidia-cublas-cu12 | 12.8.4.1 | NVIDIA proprietary (redistributable runtime) | ASR on the GPU; installed with the human's approval |
| Whisper large-v3 for CTranslate2, `Systran/faster-whisper-large-v3` rev `edaa852ec7e145841d8ffdb056a99866b5f0a478` (https://huggingface.co/Systran/faster-whisper-large-v3) | 3,087,284,237-byte model.bin | MIT (model card) | ASR; downloaded with the human's approval |
| OpenAI Whisper's language list, `whisper/tokenizer.py` `LANGUAGES` (https://github.com/openai/whisper) | | MIT | `harness/asr/whisper_codes.json`, our tags to Whisper codes (109 of 155) |

ASR sentence sets (licence pages opened by a research helper; its notes: scratch `asr_research.md`, summarised here):

| Set | Licence | Statement opened | Use |
|---|---|---|---|
| Common Voice sentence text (`server/data/<locale>/sentence-collector.txt` and Wikipedia-extract files; not `europarl-*`) | CC0 1.0 | README of https://github.com/common-voice/common-voice; https://wiki.mozilla.org/CommonVoice | primary set, committed in `harness/asr/sentences.json` |
| Tatoeba (`*_sentences_detailed.tsv.bz2`, https://tatoeba.org/en/downloads) | CC BY 2.0 FR (some CC0) | https://tatoeba.org/en/terms_of_use (6.2, 6.5) | fallback; each sentence's id and author kept |
| FLORES+ | CC BY-SA 4.0, gated | openlanguagedata | not used (ShareAlike) |
| UDHR translations | no licence stated | OHCHR pages refused automated reading | not used |
| Meta MMS ASR | CC BY-NC 4.0 | | noted, not used (non-commercial) |
| Meta Omnilingual ASR | Apache-2.0 | | noted for the 46 tags Whisper lacks; needs WSL2 (fairseq2) |

## Phase 1: acoustic reference values (`harness/reference/ranges.json`)

Read by a research helper who opened each source; numbers are facts cited from their authors, no text copied. Where a value came second-hand or a table had to be re-aligned by hand, the entry's `notes` say so.

| Id | Source | URL | Terms seen | Used |
|---|---|---|---|---|
| hillenbrand1995 | J. Hillenbrand, L. A. Getty, M. J. Clark, K. Wheeler (1995). Acoustic characteristics of American English vowels | https://github.com/santiagobarreda/hillenbrand_et_al_1995 | Data files headed '(c) 1995 James Hillenbrand'; repository README says hosted with permission from Jim Hillenbrand; repository LICENSE file is MIT. Paper: J. Acoust. Soc. Am. 97(5), 3099-3111, doi:10.1121/1.411872 (journal article, facts cited). | Read vowdata.ds (descriptive statistics: mean, SD, N, min, max of duration, f0, F1-F4 per vowel and group m/w/c) from h95-alldata.zip by HTTP range requests (audio not downloaded). Verified that vowda |
| petersonbarney1952_data | G. E. Peterson, H. L. Barney; data file as documented by Watrous (1991) (1952). Control methods used in a study of the vowels (data file verified_pb.data) | https://www.cs.cmu.edu/Groups/AI/util/areas/speech/database/pb/ | CMU AI Repository package; 'Copying:' field empty, no licence stated. Paper: J. Acoust. Soc. Am. 24, 175-184 (facts cited). | Downloaded pb.tgz (small text data) and computed means/SDs per vowel and group over both repetitions of all speakers (33 men, 28 women, 15 children). These are DERIVED values; the paper's Table II was |
| cho_ladefoged1997_wpp95 | T. Cho, P. Ladefoged (1997). Variations and universals in VOT: evidence from 17 endangered languages | https://escholarship.org/uc/item/66f052kd | UCLA Working Papers in Phonetics 95, pp. 18-40, open on eScholarship; no licence statement seen; facts cited. Earlier version of Cho & Ladefoged (1999) J. Phonetics 27, which was not opened. | Scanned PDF; read Tables 1 and 2 (p. 19 = PDF p. 24) as images: summaries of Lisker & Abramson (1964) VOT means for unaspirated and aspirated /p t k/. Lisker & Abramson (1964) Word 20 itself was not o |
| jongman2000 | A. Jongman, R. Wayland, S. Wong (2000). Acoustic characteristics of English fricatives | https://hdl.handle.net/1808/13393 | Publisher's version deposited in KU ScholarWorks (accessrights 'openAccess'); J. Acoust. Soc. Am. 108(3), 1252-1263, doi:10.1121/1.1288413; journal article, facts cited. | Text of p. 1256 (spectral peak by place and by sex), Table I (spectral moments by place), Table VI (frication duration per fricative). Per-fricative spectral peaks exist only in Fig. 1 (not read). |
| xu1997 | Y. Xu (1997). Contextual tonal variations in Mandarin | https://www.homepages.ucl.ac.uk/~uclyyix/yispapers/Xu_JP97.pdf | Author-hosted copy of J. Phonetics 25, 61-83 (Elsevier); journal article, facts cited. | Section 3.1: approximate f0 landmarks and durations of the four tones on isolated /ma/, 8 male speakers. Exact contour values are only in Fig. 2. |
| moore_jongman1997 | C. B. Moore, A. Jongman (1997). Speaker normalization in the perception of Mandarin Chinese tones | https://kuscholarworks.ku.edu/entities/publication/edc91d32-6a91-4327-a7bc-d1a80025a76c | Publisher's version in KU ScholarWorks; PDF footer: redistribution subject to ASA license or copyright. J. Acoust. Soc. Am. 102, 1864-1877, doi:10.1121/1.420092; facts cited. | Onset, turning point and offset F0 of tone 2 (speaker S2) and tone 3 (speaker S1), two female speakers. |
| linge2011 | O. Linge (2011). Teaching the third tone in Standard Chinese: tone representation in textbooks and its consequences for students | https://www.hackingchinese.com/media/teaching_the_third_tone_in_standard_chinese.pdf | Lund University student paper (also listed at https://www.lunduniversity.lu.se/lup/publication/1979823); no licence statement seen; facts cited. | Secondary source for Chao (1968) tone numbers 55, 35, 214, 51 (Table 1) and the 21 low realisation of T3. Chao (1968) not opened. |
| escudero2009 | P. Escudero, P. Boersma, A. S. Rauber, R. A. H. Bion (2009). A cross-dialect acoustic description of vowels: Brazilian and European Portuguese | https://www.fon.hum.uva.nl/paul/papers/BPEP_vowels64_pic.pdf | Author-hosted manuscript of J. Acoust. Soc. Am. 126, 1379-1393, doi:10.1121/1.3180321; facts cited. | Table I: geometric means (SD as ratio) of duration, F0, F1, F2, F3 for 7 oral vowels, 10 F + 10 M speakers per dialect (Sao Paulo, Lisbon). Formant ceilings not recorded. The manuscript may differ fro |
| chladkova2011 | K. Chládková, P. Escudero, P. Boersma (2011). Context-specific acoustic differences between Peruvian and Iberian Spanish vowels | https://www.fon.hum.uva.nl/paul/papers/Spanish2011.pdf | 'Author's complimentary copy' of J. Acoust. Soc. Am. 130(1) (table on p. 421); facts cited. | Table I: geometric means (between-speaker SD as factor) of duration, F0, F1, F2 for /a e i o u/, Madrid and Lima, 10 speakers per cell (9 Lima women). |
| alispahic2017 | S. Alispahic, K. E. Mulak, P. Escudero (2017). Acoustic Properties Predict Perception of Unfamiliar Dutch Vowels by Adult Australian English and Peruvian Spanish Listeners | https://doi.org/10.3389/fpsyg.2017.00052 | CC BY 4.0 (Frontiers in Psychology 8:52; PMC5269591). Read via NCBI E-utilities efetch (PMC web pages blocked automated access). | Table 1 male F1-F3 for Australian English (from Elvin et al. 2016) and Dutch (from Adank et al. 2004a). Its Peruvian Spanish rows equal chladkova2011 and were not duplicated. |
| paetzold_simpson1997 | M. Pätzold, A. P. Simpson (1997). Acoustic analysis of German vowels in the Kiel Corpus of Read Speech | https://www.ipds.uni-kiel.de/kjk/pub_exx/aipuk32/mpas.pdf | Arbeitsberichte des Instituts fuer Phonetik Kiel (AIPUK) 32; open PDF on the Kiel institute site; no licence statement seen; facts cited. | Table 2a/2b (p. 225): medians and quartiles of F1-F3 for 16 monophthongs and 3 diphthongs (onset/offset), 12 female and 12 male speaker-corpora. Text extraction misplaces the row labels; rows were re- |
| gendrot_addadecker2005 | C. Gendrot, M. Adda-Decker (2005). Impact of duration on F1/F2 formant values of oral vowels: an automatic analysis of large broadcast news corpora in French and German | https://www.isca-archive.org/interspeech_2005/gendrot05_interspeech.pdf | ISCA Archive, Proc. Interspeech 2005, 2453-2456, doi:10.21437/Interspeech.2005-753; facts cited. | Table 5: mean F1-F3 of 10 French oral vowels by sex, automatically measured broadcast news. Three vowel-symbol glyphs missing in the PDF text; assigned by column order and the paper's Table 3. |
| hagiwara1995 | R. Hagiwara (1995). Acoustic Realizations of American /r/ as Produced by Women and Men (UCLA Working Papers in Phonetics 90) | https://escholarship.org/uc/item/8779b7gq | (c) 1995 Robert Elliott Hagiwara (title page); open on eScholarship; facts cited. | Scanned; read Tables 7.1-7.3 (pp. 107-108) as images: F1-F3 means and SDs of syllabic, final and initial /r/, 9 women and 6 men, southern Californian English; plus the F3 cut-off values in the text. |
| becker2007 | M. R. Becker (2007). Acoustic Analysis of the Production of [m] and [n] in Codas by Brazilian Students | https://nupffale.ufsc.br/newsounds/Papers/4.Becker_Marcia.pdf | New Sounds 2007: Proceedings of the Fifth International Symposium on the Acquisition of Second Language Speech; no licence statement seen; facts cited. | Secondary citation only: antiformant ranges for [m] and [n] and the 200-300 Hz nasal formant attributed to Fujimura (1962, p. 1871). Fujimura (1962) itself not opened (no open copy found). |

Named in the sources above but **not opened**: Lisker & Abramson 1964 and Cho & Ladefoged 1999 (VOT values come through Cho & Ladefoged 1997's tables), Fujimura 1962 (nasal ranges through Becker 2007), Espy-Wilson et al. 2000, Peterson & Barney's own Table II (means were computed from the data file: provenance `derived`), Hillenbrand et al.'s Table V (means from the author's statistics file).

## Phase 2 (2026-10-05): sources for the design

Opened by a research helper on 2026-10-05 (the main session did not open them again). Nothing was copied into the repository; facts are restated. "Used for" names the part of `DESIGN.md` that rests on it.

### Standards and charts

| Title | URL | Licence | Used for |
|---|---|---|---|
| extIPA Symbols for Disordered Speech (revised to 2015), ICPLA | https://www.internationalphoneticassociation.org/sites/default/files/extIPA_2016.pdf | "© ICPLA 2015"; no licence stated | Tier B: which chart (section 1) |
| ExtIPA Symbols for Disordered Speech, ICPLA 2021 | https://www.internationalphoneticassociation.org/sites/default/files/extIPA_2021.pdf | CC BY-SA icons on the chart; version not printed | Tier B: the newer issue exists; ShareAlike, so cited only |
| ICPLA, Journal & Publications (links the 2015 extIPA chart and the VoQS chart "updated 2016") | https://www.icpla.info/journal-publications | none stated | Tier B: where the charts are published |
| Ball, Howard & Miller (2018). Revisions to the extIPA chart. JIPA 48(2), 155-164, doi:10.1017/S0025100317000147 | Cambridge Core abstract page | journal article | the revision was approved in 2016 |
| VoQS: Voice Quality Symbols (chart) | https://www.icpla.info/VOQSchart_2015v4.pdf | "© 2015 Ball, Esling, Dickson"; no licence stated | Tier B: what VoQS contains (airstream, phonation, settings, degrees) |
| Ball, Esling & Dickson (2018). Revisions to the VoQS system. JIPA 48(2), 165-171, doi:10.1017/S0025100317000159 | Cambridge Core | journal article | Tier B |
| Unicode 18.0.0 (released 2026-09-16); `Blocks.txt`, `UnicodeData.txt`, `DerivedAge.txt`, `NamesList.txt` | https://www.unicode.org/Public/UCD/latest/ucd/ | Unicode License v3 (https://www.unicode.org/license.txt): permissive, notice kept | the ten blocks and their 891 assigned characters (section 1); the tone letters' block |
| TOML v1.1.0 (2025-12-24) and v1.0.0 (2021-01-12) | https://toml.io/en/ | MIT (specification repository) | the pack format (section 6.1) |
| YAML 1.2.2 (2021-10-01) | https://yaml.org/spec/1.2.2/ | | the comparison in section 6.1 |
| RFC 8259, The JSON Data Interchange Format | https://www.rfc-editor.org/rfc/rfc8259 | | JSON has no comments |

### Software looked at (none installed in this phase)

| What | URL | Licence | Fact used |
|---|---|---|---|
| Python `tomllib` | https://docs.python.org/3/library/tomllib.html | PSF | in the standard library from 3.11, reads only; this machine has 3.10 |
| `tomli` 2.4.1, `tomli-w` 1.2.0 | https://pypi.org/project/tomli/ , https://pypi.org/project/tomli-w/ | MIT | the reader and writer for Python 3.10 |
| `tomlc17` (a C parser; not needed, the product never reads TOML) | https://github.com/cktan/tomlc17 | MIT | noted |
| PyYAML 6.0.3 and its `resolver.py` | https://pypi.org/project/PyYAML/ , https://github.com/yaml/pyyaml/blob/main/lib/yaml/resolver.py | MIT | it implements YAML 1.1: an unquoted `no` loads as false (read in the source, not run) |
| PanPhon | https://github.com/dmort27/panphon ; paper https://aclanthology.org/C16-1328/ | MIT (code and tables); paper CC BY 4.0 | a feature table that may be used as a cross-check; 24 feature columns today, 21 in the paper |
| PHOIBLE | https://phoible.org/ ; https://github.com/phoible/dev | site CC BY-SA 3.0; repository data CC BY 4.0, code MIT | reference only; not copied |
| B. Hayes, Introductory Phonology, feature spreadsheets | https://brucehayes.org/IP/ | none stated | reference only; not copied |
| Meta Omnilingual ASR | https://github.com/facebookresearch/omnilingual-asr | Apache 2.0; needs fairseq2, which has no native Windows support | noted for Phase 7 (OPEN_QUESTIONS Q7) |
| Allosaurus; `facebook/wav2vec2-lv-60-espeak-cv-ft` and `-xlsr-53-`; Montreal Forced Aligner | github.com/xinjli/allosaurus ; huggingface.co/facebook ; montreal-forced-aligner.readthedocs.io | GPL v3; Apache 2.0; MIT | phone recognisers and aligners: noted, not adopted (trained on natural speech; the wav2vec2 labels are eSpeak's own) |

### Literature

| Id | Source | URL | Used for |
|---|---|---|---|
| klatt1980 | D. H. Klatt (1980). Software for a cascade/parallel formant synthesizer. JASA 67(3), 971-995, doi:10.1121/1.383940 | https://www.fon.hum.uva.nl/david/ma_ssp/doc/Klatt-1980-JAS000971.pdf (scanned copy; © ASA) | 39 control parameters; the text only "evaluates" a step excitation at a plosive release, the listing has one (`PLSTEP`); this engine has none (F6) |
| klatt_klatt1990 | D. H. Klatt, L. C. Klatt (1990). Analysis, synthesis, and perception of voice quality variations among female and male talkers. JASA 87(2), 820-857, doi:10.1121/1.398894 | https://www.fon.hum.uva.nl/david/ma_ssp/doc/Klatt-1990-JAS000820.pdf | the frame's words are KLSYN88's (open quotient, tilt, flutter, diplophonia, aspiration, tracheal pair, DF1/DB1); breathy voice raises open quotient, tilt and aspiration (C6) |
| exter2011 | M. Exter (2011). The acoustic modeling of click types. ICPhS XVII | https://www.internationalphoneticassociation.org/icphs-proceedings/ICPhS2011/OnlineProceedings/RegularSession/Exter/Exter.pdf | abrupt clicks are single transients without turbulence, the response of the cavity in front of the back closure: the reason for C12's trigger |
| wp_click | Wikipedia, "Click consonant" | https://en.wikipedia.org/wiki/Click_consonant (CC BY-SA 4.0; cited, not copied) | which clicks are noisy and long, which abrupt; which are low and which high: the order the click test checks |
| vicenik_georgian | C. Vicenik. An Acoustic Study of Georgian Stop Consonants. UCLA Working Papers in Phonetics 107, 1-30 | eScholarship, item 63t1324h | ejectives: a voicing lag between voiced and aspirated, creaky onset, flat or rising pitch |
| mori2023 | Mori (2023). The acoustic characteristics of implosive and plosive bilabials in Shimaore. JIPA 53(3), 950-976, doi:10.1017/S0025100322000184 | Cambridge Core (CC BY 4.0) | implosives: amplitude rises through the closure, shorter prevoicing, higher pitch |
| trills2026 | Counting Closures in Spanish Trills: A Multi-Corpus Acoustic Study. arXiv:2609.17424v1 (2026-09-15) | https://arxiv.org/html/2609.17424 (CC BY-SA 4.0; cited) | it calls 18 to 40 Hz the canonical trill range and searches within it; its own results are a median of two closures and medians of 23 to 28 Hz: C11's test, to be confirmed against a second source |
| keating_esposito | P. Keating, C. Esposito. Linguistic Voice Quality. UCLA Working Papers in Phonetics 105, 85-91 | eScholarship, item 04r5q6qn | H1 minus H2 and cepstral measures separate breathy, modal and creaky: C6's test |
| styler2017 | W. Styler (2017). On the acoustical features of vowel nasality in English and French. JASA 142(4), doi:10.1121/1.5008854 | eScholarship, item 5j61c2w4 | A1 minus P0, F1 bandwidth and tilt mark nasality; nasal peaks near 250 and 950 Hz: C9's trigger |
| omnilingual2025 | Omnilingual ASR (paper), arXiv:2511.09690, Table 5 | https://arxiv.org/pdf/2511.09690 | Whisper large-v3 averages about 2 % character error on eight well-resourced languages and about 22 % over 81: why one pass mark cannot be fair (section 10.3) |
| whisper2022 | Radford et al., Robust Speech Recognition via Large-Scale Weak Supervision, arXiv:2212.04356 | https://arxiv.org/pdf/2212.04356 | error falls with training hours; its Table 13 is for large-v2 and word error, so no number is taken from it |

### Licences of pronunciation data (R4: recorded before anything is imported; nothing has been imported)

| Source | Licence text opened | Result (`DESIGN.md` 8.4) |
|---|---|---|
| eSpeak NG | `COPYING`, https://github.com/espeak-ng/espeak-ng : GPL v3 or later | stays in the front-end's data; never in MIT files |
| Epitran | `LICENSE.txt`, https://github.com/dmort27/epitran : MIT | its own maps may be used with the notice |
| WikiPron | README, https://github.com/CUNY-CL/wikipron : code Apache 2.0; data under Wiktionary's terms | data only as a separate ShareAlike pack |
| CMUdict | `LICENSE`, https://github.com/cmusphinx/cmudict : BSD-style, 2 clauses | may be used with the notice |
| ipa-dict | https://github.com/open-dict-data/ipa-dict : MIT unless a language's source says otherwise (some ShareAlike, GPL 2, non-commercial) | per language only |
| Unicode CLDR | `LICENSE`, https://github.com/unicode-org/cldr : Unicode License v3 | may be used with the notice (number spell-out rules) |
| Wiktionary | https://en.wiktionary.org/wiki/Wiktionary:Copyrights : CC BY-SA 4.0 and GFDL | only as a separate ShareAlike pack |

These readings of licences are ours and are not legal advice.

### Looked for and not opened, so nothing rests on them

The full text of Ball (2024), "Changes to certain extIPA diacritics" (doi:10.1080/02699206.2024.2365205; only its metadata was opened); the licence version of the 2021 extIPA chart and any licence for the VoQS chart; Ladefoged & Traill on clicks; Ladefoged & Maddieson (1996); Solé on trills; House & Stevens (1956); Gordon & Ladefoged (2001); Chen (1997) (its figures are as quoted by Styler 2017); Hayes (2009), the book; per-language error rates for Whisper large-v3; the constant in Klatt 1980's `PLSTEP` line (unreadable in the scan).

## Phase 4 (2026-10-06): the master table

Every source an entry of the master table cites is in `ipa/sources.toml` (id, title, authors, year, URL, licence as stated, whether it was opened, access date); an entry's value names its source by id. That file is the list for Phase 4; this section adds only what is not a source of a value.

- **Unicode Character Database 18.0.0** (`UnicodeData.txt`, `Blocks.txt`; `Blocks-18.0.0.txt` dated 2026-07-08), https://www.unicode.org/Public/UCD/latest/ucd/, accessed 2026-10-06. Unicode License v3, which permits copying and redistribution with its notice: the notice is beside the files as `docs/tts-extension/inventory/unicode/LICENSE.txt` (from https://www.unicode.org/license.txt). Downloaded with the human's say-so (`OPEN_QUESTIONS.md` Q16). Used by `engine/ipa/coverage.py` for the Unicode net (the secondary coverage metric, `DESIGN.md` 1): 891 assigned code points in the ten blocks, as the design counted.
- **Kuronen (2000)** and **Deterding's per-speaker spreadsheets (1997)**: downloaded with the human's say-so (`OPEN_QUESTIONS.md` Q17) into the session's scratch folder only, read for facts; nothing of them is in the repository but the cited numbers. Entries `kuronen2000` and `deterding_data` in `ipa/sources.toml`.
- **The Unicode net's classes** (`ipa/unicode_net.toml`, written by `docs/tts-extension/inventory/build_unicode_net.py`): the Tier B and other-tradition classes were checked against Wikipedia's "Extensions to the International Phonetic Alphabet", "Voice Quality Symbols", "Combining Diacritical Marks Extended" and "Combining Diacritical Marks Supplement" (CC BY-SA 4.0; facts only, nothing copied) and Unicode's `NamesList.txt` 18.0.0 (Unicode License v3), accessed 2026-10-06; the URLs are in the file's header.
- **Tier B (extIPA, VoQS) inventory**: every chart and source opened, with its licence, is in `docs/tts-extension/inventory/tierb/REFERENCES_TIERB.md` (2026-10-06). The extIPA charts of 2015 (no licence stated), 2021 and 2025 (CC BY-SA) and the VoQS charts of 2015 and 2016 (no licence stated) are cited, not reproduced.

### Phase 4b (2026-10-06, third session): clicks, implosives, the ejective mark

Opened again by a research helper on 2026-10-06 for their numbers (the earlier session cited them without keeping the numbers). Facts cited, nothing pasted; the figure readings are marked as such in the table's rules.

- **Miller and Shah (2009)**, "The acoustics of Mangetti Dune !Xung clicks", Interspeech 2009, 2283-2286, https://www.isca-archive.org/interspeech_2009/miller09b_interspeech.pdf (c) ISCA, free access. Used: burst duration (figure 2), burst RMS over the vowel's (figure 3), centre of gravity (section 3.2 text and figure 6), for the two male speakers JF and MA. The paper's abstract and section 3.1.1 disagree on which clicks have the longer bursts; the figures agree with 3.1.1, which is what the table follows. The "about 6 dB" claim in the checklist is the paper's paraphrase of Ladefoged and Traill (1994), not a measurement of its own, and is not used.
- **Miller-Ockhuizen and Sands (2000)**, ICSLP 2000, https://www.isca-archive.org/icslp_2000/millerockhuizen00_icslp.pdf (c) ISCA. Used: the peak burst frequencies of SR (ǃ 1033 Hz, ǁ 2255 Hz) as support for the centroids; the burst durations were already used for vot_ms (table 4, its columns garbled in the scan).
- **Miller, Brugman and Sands (2007)**, ICPhS XVI, http://www.icphs2007.de/conference/Papers/1664/1664.pdf, free access. Used: only the remark that the bilabial click's first spectral peak is the lowest of the five (figure 2), in a note; no number taken.
- **Mori (2023)**, JIPA 53(3), CC BY 4.0 (row above). Used: the RMS curve of figure 8 (implosive amplitude rising about 8.9 dB over the last 75 ms of the closure; the plain b nearly flat), read from the figure, and the voiced closures 57.9 against 105.6 ms (section 3.1.1).
- **Nihalani (1991)**, "Low level phonetic implementation rules: evidence from Sindhi", ICPhS 12 vol. 2, 134-137, https://www.coli.uni-saarland.de/Phonetics/icphs/ICPhS1991/12_ICPhS_1991_Vol_2/p12.2_134.pdf, free-access scan. Used: implosive voicing 70 to 72 per cent of the plosive's (table 2), in a rule.
- **Kye (2021)** (checklist reference `non_pulmonic:kye2021`, Phase 0): its summary of Lindau (1984) and Kingston, that "stiff" ejectives have an intense burst, backs the `estimated` burst gain of the ejective mark; no level was found.
- Not found open: Lindau (1984) itself; Sands (1991)'s UCLA working paper with the Xhosa burst durations.

### Phase 4 (2026-10-06, fourth session): the level hold, the uvulars

- **Gallagher (2014)**, "Dorsal consonant place and vowel height in Cochabamba Quechua", author's manuscript in the NYU archive, https://archive.nyu.edu/jspui/bitstream/2451/33774/4/gallagher_2014_quechua_uvulars.pdf (`ipa/sources.toml` `gallagher2014`; no licence stated; facts cited). Opened again on 2026-10-06 for its Table 5: F1 at the onset of a vowel after a uvular against after a velar stop, isolation words, 507 / 410 Hz (front) and 536 / 432 Hz (back), 9 F + 2 M speakers; the ratio (1.24) is used for q's and ɢ's onset F1 (D64). The paper gives no voice onset time. Opened again on 2026-10-07 (its text streams decompressed locally) for ɢ (D65): it measures the high vowels only, no /a/, and finds an F2 difference after uvulars for front vowels only (onset: velar F2 2600 against uvular 2134 Hz; back vowels -116.88 Hz, SE 160.96, not significant).
- **Klatt (1980)**'s digital resonator, as `docs/tts-extension/harness/synth.py` already implements it, is what `level_rise` computes the vowels' gain with (D64); nothing new was opened for it.

### Phase 4 (2026-10-07, sixth session): double articulations (4g)

Opened by a research helper on 2026-10-07; every number below was read from the document (two are scans, read against the page image). No document states a licence: facts cited, nothing copied. Keys are those of `ipa/sources.toml`.

- **Connell (1991)**, "Accounting for the reflexes of labial-velar stops", Proc. ICPhS 12 vol. 3 pp. 110-113, https://www.coli.uni-saarland.de/Phonetics/icphs/ICPhS1991/12_ICPhS_1991_Vol_3/p12.3_110-113.pdf (`connell_1991`). Used: Table 1 p. 112 (Ibibio, 8 speakers: closure k͡p 162 ms, p 147, k 113; VOT k͡p -26, p 6, k 21); 2.4 (the velar released before the labial in all tokens, mean 38 ms); p. 111 (the vowel before most often velar-like, the vowel after labial-like with a lower locus); p. 113 (the labial release the more salient).
- **Maddieson (1995)**, "Gestural economy", Proc. ICPhS 13 vol. 4 pp. 574-577, https://www.coli.uni-saarland.de/Phonetics/icphs/ICPhS1995/13_ICPhS_1995_Vol_4/p13.4_574.pdf (`maddieson_1995`). Used: Fig. 3 and p. 575-576 (Ewe: the velar gesture leads the labial by a few ms; each like the plain stop's).
- **Grawunder, Winter and Atoyebi (2011)**, "Voicing of labiovelar stops in Yoruba", Proc. ICPhS 17 pp. 767-770, https://www.internationalphoneticassociation.org/icphs-proceedings/ICPhS2011/OnlineProceedings/RegularSession/Grawunder/Grawunder.pdf (`grawunder_2011`). Used: 3.1 (k͡p prevoiced in 95 per cent of tokens, mean 19 ms; ɡ͡b in 99), 3.2, 3.3. Not modelled: prevoicing of k͡p (language-specific; D66).
- **Burns and Shaw (2023)**, "Effect of vowel context on stop place identification in Yoruba", Proc. ICPhS 20 pp. 2946-2950, https://www.internationalphoneticassociation.org/icphs-proceedings/ICPhS2023/full_papers/645.pdf (`burns_shaw_2023`). Used: Table 1b (Nupe, 1 speaker: F2 at the vowel onset after ɡ͡b 1283 Hz on /a/ against labial 1353 and velar 1456), p. 2949 (labial-velars heard mostly as labials).
- **Cahill (1999)**, "Aspects of the phonology of labial-velar stops", Studies in African Linguistics 28(2) 155-184, https://journals.flvc.org/sal/article/download/107374/102695/146604 (`cahill_1999`; open-access journal). Used: 3.1 (ingressive airflow in most languages surveyed; k͡p usually unaspirated).
- **Maselli and Delvaux (2024)**, "Aerodynamics of Sakata labial-velar oral stops", Interspeech 2024 pp. 3140-3144, https://orbi.umons.ac.be/bitstream/20.500.12907/51165/1/maselli24_interspeech.pdf (`maselli_2024`). Used: qualitative only (suction during the closure).
- Named but not opened (paywalled or blocked), so nothing rests on them: Connell (1994) "The structure of labial-velar stops", J. Phonetics 22; Maddieson (1993), UCLA WPP.

### Phase 4 (2026-10-07, seventh session): locus equations (Q21)

Read again by a research helper on 2026-10-07 for their locus-equation tables; each PDF was downloaded to the session's scratch folder and the table pages read as rendered page images, not from memory. Both were already in `ipa/sources.toml` (opened); no new source, no new licence. Facts cited, nothing copied.

- **Stoakes (2013)**, PhD thesis, Melbourne (`stoakes2013`; URL in `ipa/sources.toml`). Used: Table 6.15 p. 214 (CV locus equations, F2, males HK and OK: locus, intercept, slope, adjusted r² for pː b tː d ʈː ɖ cː ɟ kː ɡ); the definition L = c / (1 - k) and the measuring points (F2 at 5 per cent into the vowel against its midpoint) on pp. 131-132; the author's remarks on reliability on pp. 208, 213 and 216 (velar and retroflex loci inconsistent; palatal fits weak). Read and not used: Table 6.14 (VC, males), Table 6.17 (CV, females). Printed page = PDF page - 24. The table's printed loci were computed from unrounded slopes and are used as printed. Found in passing: the table prints a lenis ɡ locus (HK 984.4 Hz, slope 0.88), which the master table had said it did not; corrected (D67).
- **Jongman, Wayland and Wong (2000)** (`jongman2000`). Used: Table III p. 1259 (locus-equation slope and intercept by place and sex, voicing and vowels pooled; males f,v 0.770 / 299 Hz, θ,ð 0.529 / 819, s,z 0.533 / 825, ʃ,ʒ 0.557 / 887); Table IV p. 1259 (mean F2 at vowel onset, which the master table had used as the locus); the method on p. 1256 (onset at the first glottal pulse, 23.3 ms window). No locus frequency and no R² is printed: the locus is derived as c / (1 - k), Stoakes's definition.

### Phase 4 (2026-10-07, eighth session): Tier B, the extIPA lateral fricatives (4f, D68)

Found and opened by a research helper on 2026-10-07 (web search and fetch); numbers read in the opened text, nothing copied but the cited facts.

- **Gordon, Barthmaier and Sands (2002)**, "A cross-linguistic acoustic study of voiceless fricatives", *JIPA* 32(2): 141-174, doi:10.1017/S0025100302001020 (`gordon2002`). Read in the author's own manuscript through the Wayback Machine (https://web.archive.org/web/2010/http://www.linguistics.ucsb.edu/faculty/gordon/fricativeacoustics.pdf); the printed paper (Cambridge University Press, copyright; only its abstract open) may differ in wording. Licence: none stated; facts cited. Used: Toda's voiceless retroflex lateral fricative, 6 speakers (3 F, 3 M), word-final after a: duration (Table 14, mean 195.4 ms; ɬ 189.5), centre of gravity (Table 15, mean 4222 Hz; ɬ 4164, not significantly different), the male spectra's main peak between 2 and 4 kHz (ɬ about 3 to 4.5 kHz), F3 lowered against ɬ (p = .001; Figure 17, values not read as numbers).
- **Steed and Hardie (2004)** (`steed_hardie_2004`, already in `ipa/sources.toml`), read again in full: Kuman's voiceless velar lateral fricative, 1 M: the noise strong between about 1.5 and 3 kHz, its spectral peak about 2 kHz, "possibly 2.4" (text; the table takes 2.4 and marks 𝼄 approximate, D68), Table 1's lateral F2 (mean 1349.3 Hz) and F3 (mean 2537.3 Hz), the fricative portion's mean 17.04 cs. Two row labels of Table 1 did not extract; the values used are the means, which do not depend on them.
- **Shalev, Ladefoged and Bhaskararao (1993)**, "Phonetics of Toda", *UCLA Working Papers in Phonetics* 84: 89-123 (https://escholarship.org/uc/item/8k45g432; licence none stated). Opened: its acoustic section measures only central fricatives; nothing used.
- **The IPA chart (2015, Doulos version)**, https://www.internationalphoneticassociation.org/sites/default/files/IPA_Doulos_2015.pdf, CC BY-SA 3.0 (cited, not copied): the raised diacritic's example is glossed "voiced alveolar fricative" (Q23).
- **Wikipedia, "Voiceless palatal lateral fricative"** (CC BY-SA 4.0; cited, not copied): the languages said to have it; its sources are descriptive and give no measurement. No acoustic measurement of a palatal lateral fricative was found, so 𝼆's values are `estimated` (Q15).
- Looked for and not opened: Maddieson and Emmorey (1984), *Phonetica* 41: 181-190 (abstract only, no numbers); Ladefoged and Maddieson (1996) (copyright, not opened); any Archi or Mid-Wahgi measurement (none found).

### Phase 4 (2026-10-07, ninth session): extIPA's place marks and nasal friction (4f, D69)

Found and opened by a research helper on 2026-10-07 (web search and fetch); numbers read in the opened text, nothing copied but the cited facts.

- **Massone (1988)** (`massone1988`, already in `ipa/sources.toml`), read again: Table 1, the start of the F2 transition, two male speakers of Buenos Aires Spanish: [m] 1982 / 1900, [ɱ] 1817 / 1817, [n] 2246 / 1941, [n̪] 1776 / 1569 Hz (the scan's OCR is poor). Used: the ratio of the labiodental to the bilabial, 1817 / 1941 = 0.936, as the basis of the `estimated` F2 lowering of extIPA's bridge above (U+0346).
- **Figueroa, Painequeo, Márquez, Salamanca and Bertín (2019)**, "Evidencia del contraste interdental/alveolar en el mapudungun hablado en la costa", *Onomázein* 44: 191-216, doi:10.7764/onomazein.44.09 (`figueroa2019`; https://dialnet.unirioja.es/descarga/articulo/6996559.pdf; no licence shown). 19 speakers, 3437 CV tokens; F2 at the vowel's onset, from interdental to alveolar: laterals +28.14 Hz, voiceless stops -46.58 Hz, nasals not significant; no effect at the vowel's middle. Used: the deviation stated on the interdental spellings (t̪͆ and the rest), which this engine says further from the alveolar than measured.
- **Zajac, Powell and McQuillan (2021)**, "Development and Resolution of Nasal Fricatives in a Child With Repaired Bilateral Cleft Lip and Palate: A Case Report" (title from Crossref's record, https://api.crossref.org/works/10.1044/2021_persp-21-00028), *Perspectives of the ASHA Special Interest Groups* 6(4): 743-754, doi:10.1044/2021_persp-21-00028 (`zajac2021`; PMC8664246, author manuscript). One child with a repaired cleft: anterior nasal fricatives aperiodic, energy above 3 kHz, most intense above 5 kHz, first moment 8.7 to 9.7 kHz. Used: where the noise of extIPA's nasal friction (U+034B) is put (the highest resonance and the flat path) and the measure that judges it (energy above 3 kHz against the murmur's below 1 kHz). No level against the murmur was found: the level is `estimated` (Q15).
- **Tabain, Butcher, Breen and Beare (2014)**, "Lateral formants in three Central Australian languages", *Proc. Interspeech 2014*: 920-924, doi:10.21437/Interspeech.2014-240 (© ISCA). Arrernte's lamino-dental lateral against the alveolar, F2 +67 Hz at the lateral's middle (21 speakers, mostly female). Read; not used (laminal dentals, not said to be interdental).
- **Suzuki and Lee (2019)**, *Proc. ICPhS 2019* (Tshivenda dental against alveolar; the dental nasal said with the tongue between the teeth): the values only in a figure; not used.
- Looked for and not found or not opened: any measurement of a dentolabial or a labioalveolar consonant; of interdental against dental [θ]; Ball, Howard and Miller (2018), *JIPA* 48(2) (paywalled); Laver (1994); Dart (1991) (the page returned empty); a level of nasal turbulence against the murmur.

### Phase 4 (2026-10-07, tenth session): extIPA's voicing marks (4f, D70)

Found and opened in this session (web search and fetch, 2026-10-07); numbers read in the opened text, nothing copied but the cited facts.

- **Rogers (1995)**, "Aspirated stops in Scots Gaelic", *Proceedings of the XIIIth International Congress of Phonetic Sciences*, Stockholm, vol. 3: 448-451 (`rogers1995`; https://www.coli.uni-saarland.de/Phonetics/icphs/ICPhS1995/13_ICPhS_1995_Vol_3/p13.3_448.pdf; no licence statement seen). Two women (Harris, Lewis), 120 words in a frame, four times at a normal rate and twice fast; Table 1, preaspiration of the medial fortis stops: 171 and 148 ms read slowly, 94 and 102 ms fast (the table's text is OCR, its columns read by their sums: preaspiration + closure + VOT = the voiceless duration, 171 + 66 + 31 = 268 against 267). Used: the `literature` length of extIPA's pre-aspiration (ʰ◌), 98 ms, the mean of the two fast means.
- **Wikipedia, "Extensions to the International Phonetic Alphabet"** (https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet, CC BY-SA 4.0, read 2026-10-07; facts cited, nothing pasted). Its table of partial diacritics: ◌᪽ partial or central voicing (s̬᪽) and devoicing (z̥᪽), ◌᫃ initial, ◌᫄ final; on displaced diacritics, the phonation "begins before the consonant or vowel does or continues beyond it" (ˬz pre-voiced, zˬ post-voiced, a˷ creaky offglide). Used: what the twelve voicing marks mean, and the deviation stated on ˬ◌ and ◌ˬ. It gives no durations.
- Looked for and not found: any measurement of how much of a partly voiced or devoiced sound is voiced, of extIPA's long aspiration (◌ʰʰ) or of a creaky offglide's length; the shares used are `estimated` (Q15).

### Phase 4 (2026-10-07, eleventh session): extIPA's other diacritics (4f, D71)

Found and opened by a research helper on 2026-10-07 (web search and fetch); numbers read in the opened text, nothing copied but the cited facts. Each is in `ipa/sources.toml` under the id given.

- **ICPLA, extIPA chart 2025** (`icpla_extipa2025`, https://www.icpla.org.uk/resources; CC BY-SA 3.0, cited, not copied): the diacritics' labels (labial spreading, strong and weak articulation, partially denasal, velopharyngeal friction, main gesture offset right and left, whistled articulation, ingressive airflow, sliding articulation, reiteration).
- **Wikipedia, "Extensions to the International Phonetic Alphabet"** (`wp_extipa`, raw wikitext; CC BY-SA 4.0, facts cited): the denasal mark means partly denasal since 2025 and with the parentheses mark (U+1ABB) a lesser degree; velopharyngeal friction is written with superscript feng (U+10790) since 2024; the offsets are the listener's left and right; sliding articulation is "within the time of a single segment".
- **Ball, Howard and Miller (2018)**, "Revisions to the extIPA chart", *JIPA* 48(2): 155-164: the abstract only (subscription); no per-mark detail used.
- **Barthel and Quené (2015)**, ICPhS 2015 paper 0337 (`barthel_quene2015`): smiled speech raises F2 of a rounded /o:/ by 0.50 Bark, about 93 Hz; spread and neutral vowels under 0.1 Bark (not significant). Used for ◌͍.
- **Lasarcyk and Trouvain (2008)**, ISSP 2008 (`lasarcyk_trouvain2008`): spreading raises mainly F2, on rounded vowels (a figure; no numbers taken).
- **Kraehenmann and Lahiri (2008)**, *JASA* 123(6): 4446-4455 (`kraehenmann_lahiri2008`; © ASA): closure durations of Swiss German fortis and lenis (Table VI), contact 249 against 164 ms utterance-initially. **Cho, Jun and Ladefoged (2002)**, *J. Phonetics* 30 (`cho_jun_ladefoged2002`; © Elsevier): fortis and lenis bursts of equal energy. **Fougeron and Keating (1997)**, *JASA* 101 (`fougeron_keating1997`; abstract only). Used for ◌͈ ◌͉, whose values stay `estimated`: no measurement of force as such exists in anything found.
- **Yoshida**, IULC Working Papers (`yoshida_korean_denasal`; licence not checked): denasalized nasals' nasal-channel level -18.42 and -11.46 dB by region. Used for ◌͊. Lee, Yang, Wang and Kuo (2005, *J. Voice* 19), Pegoraro-Krook et al. (2006), Dalston, Warren and Dalston (1991): abstracts only, no values used.
- **Zajac (2015)**, *Perspectives SSOD* 25: 17-28 (`zajac2015`; NIH manuscript, © ASHA): the posterior nasal fricative's flutter (80 to 100 Hz) and its prominent part below 1 kHz. Used for ◌͌. Zajac (2019), Zajac and Eshghi (2018), Zajac and Preisser (2016): read for context, no values used.
- **Orlikoff, Baken and Kraus (1997)**, *JASA* 102: 1838-1845 (`orlikoff1997`; abstract only): inspiratory phonation +5.1 semitones, jitter higher. **Vanhecke et al. (2016)**, *J. Voice* 30(6) (`vanhecke2016`; © The Voice Foundation): one soprano, ANNE -27.80 against -30.10 dB. Used for ◌↓. Eklund (2007), Fonetik 2007: function only; Eklund (2008, *JIPA*) not opened.
- **Akagi, Suzuki, Hayashi, Saito and Michi (2001)**, *Folia Phoniatr. Logop.* 53 (`akagi2001`; abstract and the ASA 1996 abstract 3aSC45): a lateral misarticulation's peak near 3.2 kHz, flat or falling above 4 kHz. Used for ◌͔ ◌͕. Valentini-Botinhao et al. (2012), WOCCI: read, not used.
- **Shosted (2006)**, ISSP 2006: 565-572 (`shosted2006`): whistled [s] peak 1.55 kHz, bandwidth 130 Hz (Tables 3 and 4). **Shosted (2011)**, ACAL 40: 119-129 (`shosted2011`; © Cascadilla): the noise above the whistle weaker, the centre of gravity lower. Used for ◌͎. Lee, Pangilinan, Lee-Kim and Kawahara (NINJAL abstract): read, not used.
- **Tumanova, Zebrowski, Throneburg and Kulak Kayikci (2011)**, "Articulation rate and its relationship to disfluency type, duration, and temperament in preschool children who stutter", *J. Commun. Disord.* 44(1): 116-129 (title and Table 3 checked again in the PMC text, 2026-10-07) (`tumanova2011`; NIH manuscript, © Elsevier): sound-syllable repetitions 0.28 to 1.69 s (Table 3). Used for \. Zebrowski (1994), Throneburg and Yairi (1994), Yairi and Hall (1993): abstracts only, no values.
- Looked for and not found or not opened: a measurement of labial spreading on a consonant; of force of articulation as such; nasalance of hyponasal speech; any value for sliding articulation; per-unit and silent-interval durations of stuttered repetitions; Lee-Kim, Kawahara and Lee (2014, *Phonetica* 71; the publisher returned 405); Bladon et al. (1987); Eklund (2008).

### Phase 4 (2026-10-08, twelfth session): extIPA's fricated releases (4f, D72)

Read by a research helper (web search and fetch, 2026-10-08); facts cited, nothing pasted. Licences as recorded in `ipa/sources.toml`.

- **Sangster (2002)**, *Inter- and intra-speaker variation in Liverpool English: a sociophonetic study*, DPhil thesis, University of Oxford (`sangster2002`; ORA download, no licence statement checked): friction timed from the closure's end, aspiration included (pp. 124-128); Table 4.iii, 16 subjects, /t/ 93.6 / 105.1 ms, /d/ 45.5 / 65.8 (word-initial / final); Tables 6.iii and 6.v, intervocalic, two speakers, two interviews: /t/ 82, 69, 93, 71, /k/ 71, 55, 98, 79 ms. Used: the median of the eight intervocalic means, 75 ms, for the voiceless superscripts (`derived`); /d/'s 45.5 ms for the voiced ones (`literature`).
- **McDonough and Wood (2008)**, "The stop contrasts of the Athabaskan languages", *J. Phonetics* 36: 427-449 (`mcdonough_wood2008`; author's copy, © Elsevier): the aspirated stops are [tx] [kx], a velar fricated release; releases of the plain unaspirated stops 19.4 to 37.3 ms (Table 2), of the others mostly above 100 ms; centre of gravity 3821 Hz 10 ms into Dogrib [tx]. Read, recorded; not used for a value (a contrastive aspirated stop, not a fricated release of a plain one).
- **Kye (2025)**, "Phonetic structures of Lushootseed obstruents", *JIPA* 55: 173-213 (`kye2025`; CC BY 4.0): release friction of the affricates (Table 10), tɬʼ 48.24 ms, ts 64.49, dz 44.28; the friction's main peak (Table 11) tɬʼ 1644 Hz, ts 3765. Used: to compare the lengths, and for the band of the sweep's new release measure (noise above 1.5 kHz: a lateral friction's peak lies below 2.5 kHz).
- **Miller and Ball (2020)**, Unicode L2/20-039 (`unicode_l2_20_039`): quotes Ball, Howard and Miller (2018, *JIPA* 48(2): 162, paywalled, not opened): the chart's lines show how extIPA symbols transcribe unusual plosive releases; any superscript lateral fricative writes a lateral fricated release. Used for the reading of the marks as an open set.
- The extIPA chart of 2025 (`icpla_extipa2025`, already cited) prints "[d, k] with lateral fricated release" and "[t, d] with lateral and median release"; "median fricated release" (tᶿ kˣ) is on the 2021 chart only, as the inventory records.
- Looked for and not found or not opened: any measurement of a lateral fricated release as distinct from a lateral affricate; Watson (2007, no durations in what was seen); Cardoso and Honeybone (2022, abstract only); Jones and Llamas (2008) and McDougall and Jones (2009, paywalled); Jessen (1998); Sotho and Tswana [kx]; Navajo, Tlingit, Zulu and Xhosa lateral affricate durations. Lee and Shinagawa (2025, *Gengo Kenkyu* 168), plain [ɬ] in five Southern Bantu languages (about 121 ms, centre of gravity 4283 Hz median): read, not used (a fricative, not a release).

### Phase 4 (2026-10-08, twelfth session): read ahead for the next Tier B groups (not used yet)

Read by a research helper (web search and fetch, 2026-10-08) for the velodorsals, percussives, velopharyngeal fricatives and grooved laterals; nothing below is in the table yet. Facts only; the licences are as the helper found them, to be entered in `ipa/sources.toml` when a value is used.

- **Oren, Rollins, Padakanti, Kummer, Gutmark and Boyce (2020)**, "Using high-speed nasopharyngoscopy to quantify the bubbling above the velopharyngeal valve in cases of nasal rustle", *Cleft Palate Craniofac. J.* 57(5): 637-645, doi:10.1177/1055665619894183 (PMC9175873, NIH manuscript, © the publisher): 10 children; secretion bubbling periodic, 18 to 100 Hz, most between 20 and 40 Hz (Fig. 5A), random from token to token; energy mainly 20 to 100 Hz.
- **Oren, Kummer and Boyce (2022)**, "Secretion bubbling as the sound mechanism for nasal rustle: a perceptual study", *JSLHR* 65(3): 869-877, doi:10.1044/2021_JSLHR-21-00137 (PMC9150726): bubbling 20 to 100 Hz; removing the one dominant rate lowered every rating and removed the rustle in 40 per cent of cases. The mechanism is disputed (Zajac and Eshghi 2018, doi:10.1177/1055665617730366: tissue flutter, linked to loudness, no rate given).
- **Zajac (2019)**, *Cleft Palate Craniofac. J.* 56(5): 690-696, doi:10.1177/1055665618805889 (PMC7161417): posterior nasal fricatives, quasi-periodic nasal energy (Fig. 2), a port under 5 mm2 in about 90 per cent of children who use them; no rate. **Zajac, Powell and McQuillan (2021)**, *Perspectives ASHA SIGs* 6(4): 743-754 (PMC8664246): anterior nasal fricatives, first spectral moment 8.7 to 9.7 kHz (the contrast case, already near zajac2021).
- **Sands, Maddieson and Ladefoged (1996)**, "The phonetic structures of Hadza", *Studies in African Linguistics* 25(2), p. 183: a variant of [ǃ] whose quiet release is followed by the underside of the tongue tip striking the floor of the mouth (the "cluck" ǃ¡), also frequent in Sandawe; no duration or spectrum given.
- Not found or not opened: any acoustic description of a velodorsal stop or nasal (Ball, Manuel and Müller 2004, "Deapicalization and velodorsal articulation as learned behaviors", not located); any measured percussive transient (Ball 1998, *JIPA* 28, paywalled; Wright, Maddieson, Sands and Ladefoged 1995, blocked); a second source for the velopharyngeal flutter rate (zajac2015, read in D71, gives about 80 to 100 Hz; the bubbling of nasal rustle above is a different, slower periodicity, 20 to 40 Hz mostly); any acoustic study of the grooved lateral fricatives ʪ ʫ.

### Phase 4 (2026-10-08, thirteenth session): the r's, the velodorsals (D74, D75), and read ahead

- **Zhou, Espy-Wilson, Boyce, Tiede, Holland and Choe (2008)**, JASA 123(6): 4466-4481, doi:10.1121/1.2902168 (`zhou_etal_2008`, the authors' lab copy, (c) ASA; facts cited). Read again for D74: F1 to F3 similar for "retroflex" (tip-up) and bunched /r/; F5 - F4 1531 and 1406 Hz for S1's retroflex, 796 and 735 for S2's bunched (sustained, supine and upright, Tables III and IV; the text says 1469 and 651 for upright), about 1900, 2000 (S3, S4) against 500, 600 (S5, S6), and about 2100, 1500, 1600 against 700, 900, 600 in "warav" at the F3 minimum.
- **Ball, Manuel and Mueller (2004)**, "An atypical articulatory setting as learned behaviour: a videofluorographic study", *Child Language Teaching and Therapy* 20(2): 153-162, doi:10.1191/0265659004ct268oa (`ball_manuel_muller_2004`; abstract only at research.ucc.ie, the publisher refused the text): one child, velodorsal articulation with deapicalization and hypernasality. This is the paper the twelfth session could not locate under another title.
- **Wikipedia, "Velar consonant"**, section Velodorsals (`wikipedia_velar_consonant`, CC BY-SA 4.0, facts only): the velum lowers onto a static tongue; disordered speech; no source cited there.
- **ICPLA extIPA chart 2025** (`icpla_extipa2025`, already registered): ɹ̈ is the bunched (molar) r, ɹ̺ the apical r.
- Read ahead, not used yet (a research helper, 2026-10-08): **Wright, Maddieson, Ladefoged and Sands (1995)**, "A phonetic study of Sandawe clicks", *UCLA Working Papers in Phonetics* 91: 1-24 (escholarship.org/content/qt3h25w3h3/qt3h25w3h3.pdf; no licence seen): the tongue slap after a post-alveolar click about 20 ms after the release, of varying level, sometimes louder than the release; ǃ's release peak near 1200 Hz (secondary 4000, 6000), ǀ near 6000 (1800), ǁ near 2000 (6500); no spectrum of the slap. **Sands, Maddieson and Ladefoged (1996)**, "The phonetic structures of Hadza", *Studies in African Linguistics* 25(2) (journals.flvc.org, open access, licence not confirmed): the flapped ǃ, the tongue tip's underside striking the floor of the mouth in one movement. **Ball (1998)**, "On percussives", JIPA 28: 95-98: paywalled, abstract only. Nothing measured was found for ʬ or ʭ.
- Read for the velopharyngeals (a research helper, 2026-10-09; used in the attempt of PROJECT_STATE, not in the table): **Zajac (2019)**, *Cleft Palate Craniofac. J.* 56(5): 690-696, doi:10.1177/1055665618805889 (`zajac2019`, PMC7161417, author manuscript): a posterior nasal fricative is an oral stop (lingual-velar the most common, after Peterson 1975 and Trost 1981) with the air through a partly closed port; quasi-periodic nasal energy well below 1 kHz. **Oren, Kummer and Boyce (2020)**, *CPCJ* 57(1): 123-126 (PMC9153061): nasal emission, turbulence, rustle and snort as terms. **Oren et al. (2020)**, *CPCJ* 57(5): 637-645 (PMC9175873): bubbling 18 to 100 Hz, mostly 20 to 40. **Eshghi, Vallino, Baylis, Preisser and Zajac (2017)**, *JSLHR* 60(6) (PMC5544409): flutter striations below 1 kHz and above 6 kHz. **Zajac and Preisser (2016)**, *CPCJ* 53(6): 649-656 (abstract only): flutter in 4 to 100 per cent of syllables. **Zajac (2015)**, *Perspect. Speech Sci. Orofac. Disord.* 25(1): 17-28, doi:10.1044/ssod25.1.17: paywalled this time; its flutter rate of about 80 to 100 Hz (read in D71) could not be confirmed again. **Wikipedia**, "Velopharyngeal consonant" and "Extensions to the IPA" (`wikipedia_velopharyngeal`, CC BY-SA 4.0): ʩ the velopharyngeal fricative; 𝼀 the snort, read as a velopharyngeal fricative with a uvular trill, no source cited. Not opened: Ball, Howard and Miller 2018 (the download returned a page, not the paper); Rollins and Kummer 2025; Mason, Pua and Perry 2018.

### Phase 4 (2026-10-09, fourteenth session): the velopharyngeals (D77), and the percussives read ahead

- **Unicode Character Database 18.0.0** (`UnicodeData.txt`, already in `inventory/unicode/`, Q16): the canonical combining class of U+1AC1 to U+1ACE (220 for U+1AC3, U+1AC4 and U+1ACA, 230 for the rest), which Python 3.10 (Unicode 13.0) and Windows' `NormalizeString` do not know; the reader's `LATE_CCC` and the front-end's `ipa_normalize` carry them (D77). Also U+0591 (class 220) and U+0592 (class 230), the stand-ins the front-end uses.
- **Zajac (2019)** and **Wikipedia, "Velopharyngeal consonant"** (`zajac2019`, `wikipedia_velopharyngeal`, registered in the thirteenth session): used for ʩ ʩ̬ 𝼀 𝼀̬ (D77).
- Read ahead for the percussives, not used yet (a research helper, 2026-10-09): **Wright, Maddieson, Ladefoged and Sands (1995)**, "A phonetic study of Sandawe clicks", *UCLA WPP* 91: 1-24 (escholarship.org/content/qt3h25w3h3/qt3h25w3h3.pdf, free, no licence line; an image-only scan, pages 5 to 8 not decoded): p. 16, two of five male speakers slap consistently in post-alveolar clicks and most do sometimes; about 20 ms from release to slap "when both are detectable"; the release may be "virtually inaudible" while the slap has the same or greater amplitude than the vowel after; Fig. 17 (speaker 4, k!ʔ) read off the plot by the helper, not stated: the slap at about 19 to 22 ms, about 3 ms long, its peak about a tenth of the release's, about four cycles in 2.5 ms (near 1.5 kHz, very rough); Fig. 18 (speaker 3, ŋ!ama): the slap's spike larger than the release and the vowel's peaks; p. 17, the post-alveolar click has no frication. No spectrum of the slap. **Xie, Li, Wu and Wang (2024)**, *IEEE TDSC* 21(4) (arXiv 2504.00435, IEEE licensed copy): teeth clenching heard by in-ear microphones (bone-conducted), one contact 10 to 20 ms, energy mainly 100 Hz to 2.5 kHz; the air-conducted sound "much lower" (no figure). **Xia and Wang (2022)**, *BMC Oral Health* 22:74, doi:10.1186/s12903-021-02018-9 (PMC8925045, CC BY 4.0): 56 adults, tooth contact by bone conduction, Praat "pitch" 2906 ± 755 Hz (of doubtful meaning on a transient), 54.8 ± 5.2 dB. **Yeh, Cengarle and De Burgh (Dolby), US 2023/0267945 A1** (an engineering patent, not a measurement): lip smacks "typically of 100 ms", detected by the largest spectral peak above 1.5 kHz against that between 100 Hz and 1.5 kHz; speech clicks about 2 to 5 ms. Not opened: Ball (1998) "On percussives", *JIPA* 28 (paywalled, abstract: percussives often made on an oral airstream, "resonating percussives"); Demolin, Ghio and Harvey (2023), ICPhS (a bot wall; the abstract gives ǃ an FFT peak near 2 kHz). **Nothing measured as speech was found for ʬ, ʭ, or ¡ alone.**

### Phase 4 (2026-10-09, fifteenth session): the percussives (D78)

- **Wikipedia, "Percussive consonant"** (https://en.wikipedia.org/wiki/Percussive_consonant, accessed 2026-10-09, CC BY-SA 4.0: facts cited, nothing copied; `wikipedia_percussive`), opened this session: one part of the mouth striking another with no airstream mechanism (after Pike 1943); ʬ the lips smacked, ʭ the teeth clashed, ¡ a sublaminal lower-alveolar tongue slap; none a phoneme of any known language; a tongue slap in the release of Sandawe's alveolar clicks (after Wright et al. 1995); no duration, level or spectrum. Used for the design of ʬ ʭ ¡ (no burst at their parting: nothing is held behind the closure) (D78).
- **Wright, Maddieson, Ladefoged and Sands (1995)** (`wright_etal_1995`, read by the research helper of the fourteenth session, above): the slap's time after the click's release (20 ms, `literature`) and its level (as loud as the vowel or louder: 0 dB, `derived`), for ǃ¡ and ¡; its length (about 3 ms) and its frequency (near 1.5 kHz) were read off Fig. 17 by the helper and enter only as `estimated` (D78).
- Named in notes of `estimated` values only, not cited as `literature`: the Dolby patent (Yeh, Cengarle and De Burgh, US 2023/0267945 A1, a detector of lip smacks), Xie, Li, Wu and Wang (2024) and Xia and Wang (2022, CC BY 4.0) on tooth contact heard by bone conduction (all read by the fourteenth session's helper, above). Nothing measured as speech was found for ʬ, ʭ or ¡ alone; each of their strike values is `estimated` and in Q15.
