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
