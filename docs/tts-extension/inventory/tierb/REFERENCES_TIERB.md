# Tier B references (extIPA, VoQS)

Every source opened for `TIERB_CHECKLIST.json` / `.md`, all accessed **2026-10-06** by a research helper. Nothing was copied into the repository: chart definitions and article statements are restated in our own words, and the charts are cited, not reproduced (the CC BY-SA ones are ShareAlike, the others are "©" with no licence). PDFs were read through a text extractor in a temporary folder outside the repository and not kept. The ref key is what `acoustic_correlates[].refs` and the notes use.

## Charts

| Key | Title | URL | Licence | Used for |
|---|---|---|---|---|
| tierb:extipa_2015 | ExtIPA Symbols for Disordered Speech (revised to 2015), ICPLA; file `extIPA_2016.pdf`, PDF created 2017-03-05 | https://www.internationalphoneticassociation.org/sites/default/files/extIPA_2016.pdf | "© ICPLA 2015"; no licence stated | 2015 presence of each record; section names; row and column labels. Its text layer uses a custom font and private-use code points, so many grid glyphs could not be read (marked `unclear`). |
| tierb:extipa_2021 | ExtIPA Symbols for Disordered Speech, "ICPLA 2021" | https://www.internationalphoneticassociation.org/sites/default/files/extIPA_2021.pdf | CC BY-SA icons (U+1F16D, U+1F16F, U+1F10E in the text layer); version not printed | the main inventory: every grid symbol, diacritic, voicing row, rhythm/uncertainty item and "other sounds" line, with code points read from the text layer |
| tierb:extipa_2025 | ExtIPA Symbols for Disordered Speech, "ICPLA 2025" (`extIPAChart2025KM4.pdf`, PDF created 2025-08-01), downloaded from the Google Drive file linked on the ICPLA resources page | https://www.icpla.org.uk/resources (file: https://drive.google.com/file/d/1innt3AxeLuAj0p8_7_PpHV8aOY8LbpK3/view) | the page says CC BY-SA 3.0 Unported, "Copyright © 2021 International Clinical Phonetics and Linguistics Association"; CC icons on the chart | 2025 presence; the 2024 diacritic changes (U+033E, U+10790, partial denasal); encoded palatal/velar lateral fricatives |
| tierb:voqs_2016 | VoQS: Voice Quality Symbols (`VOQSchart_2016_X199.pdf`, "© 2016 Martin J. Ball, John H. Esling, B. Craig Dickson", PDF created 2016-08-13), Google Drive file linked on the ICPLA resources page | https://www.icpla.org.uk/resources (file: https://drive.google.com/file/d/1YQe1ijdy7v-k_fdgYviLj8lgS-frvTel/view) | © the authors; no licence stated; the page says the chart is maintained by ICPLA and copyright to Ball, Esling & Dickson | the VoQS inventory and headings (airstream, phonation, larynx height, supralaryngeal settings, braces and numerals). The text layer is a symbol font; labels were decoded by subtracting 0xF000, symbols cross-checked with Wikipedia. |
| tierb:voqs_2015v4 | VoQS: Voice Quality Symbols (`VOQSchart_2015v4.pdf`, "© 2015 Martin J. Ball, John Esling, Craig Dickson", PDF created 2015-03-05) | https://www.icpla.info/VOQSchart_2015v4.pdf | © the authors; no licence stated | the two items only on this issue (whispery creak, tight whisper) and the differences from 2016 |
| (index) | ICPLA, Resources page | https://www.icpla.org.uk/resources | page text; no licence for the page | which files are current (extIPA 2025, VoQS 2016) and their licence statements |
| (index) | ICPLA, Journal & Publications (older site) | https://www.icpla.info/journal-publications | none stated | links the 2015 extIPA chart ("updated 2015") and VoQS 2015v4 ("updated 2016"). Its own `extIPAChart2015.pdf` (PDF created 2015-06-12) is an earlier pre-approval layout and was not used for counting. |
| (index) | International Phonetic Association, IPA chart page | https://www.internationalphoneticassociation.org/content/ipa-chart | page: CC BY-SA 4.0 for the IPA chart | confirmed it does not link extIPA or VoQS; the two extIPA PDFs were found by their file paths (the 2015 one is also the IPA link given by Wikipedia) |

## Unicode

| Key | Title | URL | Licence | Used for |
|---|---|---|---|---|
| tierb:unicode_l2_20_039 | K. Miller & M. Ball, "Unicode request for extIPA support", L2/20-039, 2020-01-08 | https://www.unicode.org/L2/L2020/20039-ext-ipa-req.pdf | Unicode Consortium document register (unicode.org terms of use); facts cited | the revision history (2010 Oslo panel, 2016 Halifax approval); which extIPA letters and modifiers were unencoded; that the 2018 JIPA article is described as publicly available |
| tierb:unicode_l2_20_038 | K. Miller & M. Ball, "Unicode request for VoQS support", L2/20-038, 2020-01-08 | https://www.unicode.org/L2/L2020/20038-voqs-req.pdf | as above | faucalized voice is a small-capital H with stroke (U+A7F8 re-described); aryepiglottic modifier small capital AA; И (U+0418) for electrolarynx and ꟿ (U+A7FF) for spasmodic dysphonia; the U+02C1 / U+02E4 question |
| tierb:unicode_l2_20_116 | K. Miller & M. Ball, "Expansion of the extIPA and VoQS", L2/20-116, 2020-04-14 | https://www.unicode.org/L2/L2020/20116-ext-ipa-voqs-expansion.pdf | as above | the combining parentheses (encoding order; paired U+1ABB/U+1ABD); proposed letters and modifiers (the final code points differ: taken from UnicodeData) |
| tierb:unicodedata_18 | Unicode 18.0.0 `UnicodeData.txt` (the repository copy) | `docs/tts-extension/inventory/unicode/UnicodeData.txt` | Unicode License v3 | every `unicode_names` entry; every code point checked to be assigned |

## Articles and encyclopedia pages

| Key | Title | URL | Licence | Used for |
|---|---|---|---|---|
| tierb:wp_extipa | Wikipedia, "Extensions to the International Phonetic Alphabet" (wikitext, revision 1365477471 of 2026-07-22) | https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet | CC BY-SA 4.0 | code points of the letters and superscripts; the 2024 changes; IPA equivalents of the lateral fricatives and upper-pharyngeal plosives; the snort; partial-application and displaced-timing conventions; descriptions of nasal escape and velopharyngeal friction |
| tierb:wp_voqs | Wikipedia, "Voice Quality Symbols" (wikitext, revision 1367572045 of 2026-08-03) | https://en.wikipedia.org/wiki/Voice_Quality_Symbols | CC BY-SA 4.0 | VoQS symbols and their code points; degree numerals 1-3; the Catford terminology (VoQS whispery voice = IPA breathy voice) |
| tierb:wp_velopharyngeal | Wikipedia, "Velopharyngeal consonant" | https://en.wikipedia.org/wiki/Velopharyngeal_consonant | CC BY-SA 4.0 | velopharyngeal friction: incomplete port closure, usually loud, nasal airflow; snort |
| tierb:wp_nasal_fricative | Wikipedia, "Nasal fricative" (served from the "Nasalization" article) | https://en.wikipedia.org/wiki/Nasal_fricative | CC BY-SA 4.0 | turbulence at the anterior nasal port; velopharyngeal port open |
| tierb:wp_percussive | Wikipedia, "Percussive consonant" | https://en.wikipedia.org/wiki/Percussive_consonant | CC BY-SA 4.0 | percussives have no airstream mechanism; the three extIPA percussives |
| tierb:wp_falsetto | Wikipedia, "Falsetto" | https://en.wikipedia.org/wiki/Falsetto | CC BY-SA 4.0 | vibration of the ligamentous edges; few overtones; range relative to modal |
| tierb:wp_harsh | Wikipedia, "Harsh voice" | https://en.wikipedia.org/wiki/Harsh_voice | CC BY-SA 4.0 (the article carries a "needs more citations" tag) | constricted laryngeal cavity, ventricular damping |
| tierb:wp_faucalized | Wikipedia, "Faucalized voice" | https://en.wikipedia.org/wiki/Faucalized_voice | CC BY-SA 4.0 | lowered, forward-tilted larynx; widened pharynx; higher pitch |
| tierb:wp_whisper | Wikipedia, "Whispering" | https://en.wikipedia.org/wiki/Whispering | CC BY-SA 4.0 | abducted, non-vibrating folds; turbulence between the arytenoids |
| tierb:wp_creaky | Wikipedia, "Creaky voice" | https://en.wikipedia.org/wiki/Creaky_voice | CC BY-SA 4.0 | 20-50 pulses a second, about two octaves below modal; slow airflow |
| tierb:wp_breathy | Wikipedia, "Breathy voice" | https://en.wikipedia.org/wiki/Breathy_voice | CC BY-SA 4.0 | more airflow, slower vibration; the Ladefoged versus Catford/Laver terminology |
| tierb:wp_esophageal | Wikipedia, "Esophageal speech" | https://en.wikipedia.org/wiki/Esophageal_speech | CC BY-SA 4.0 (the article carries a "needs more citations" tag) | pharyngo-oesophageal source; 50-100 Hz; quieter |
| tierb:wp_electrolarynx | Wikipedia, "Electrolarynx" | https://en.wikipedia.org/wiki/Electrolarynx | CC BY-SA 4.0 | monotone buzz from an external vibrator |
| tierb:wp_buccal | Wikipedia, "Buccal speech" | https://en.wikipedia.org/wiki/Buccal_speech | CC BY-SA 4.0 | cheek air source; high rough sound; 69-571 Hz sung range; 2 s maximum |
| tierb:wp_diplophonia | Wikipedia, "Diplophonia" | https://en.wikipedia.org/wiki/Diplophonia | CC BY-SA 4.0 | two concurrent pitches; quasi-periodic vibration |
| tierb:wp_denasalization | Wikipedia, "Denasalization" | https://en.wikipedia.org/wiki/Denasalization | CC BY-SA 4.0 | reduced nasal resonance; the 2025 "partial" meaning of U+034A |

Pages fetched through a summarising fetch tool (all Wikipedia pages above except the two read as wikitext) were checked only against what that tool returned; the short facts used are restated, not quoted.

## Opened but not readable beyond the metadata

| Title | URL | Licence | What was learned |
|---|---|---|---|
| M. J. Ball, S. J. Howard & K. Miller (2018). Revisions to the extIPA chart. JIPA 48(2), 155-164, doi:10.1017/S0025100317000147 (online 2017-04-11) | https://www.cambridge.org/core/journals/journal-of-the-international-phonetic-association/article/revisions-to-the-extipa-chart/06C01EA81DA2AECA2AC52AAF21556B33 | "© International Phonetic Association 2017" | abstract and metadata only: the PDF link returned the paywalled HTML page, not the article. It was described as publicly available in L2/20-039; that could not be confirmed from here. |
| M. J. Ball, J. H. Esling & B. C. Dickson (2018). Revisions to the VoQS system for the transcription of voice quality. JIPA 48(2), 165-171, doi:10.1017/S0025100317000159 | https://www.cambridge.org/core/journals/journal-of-the-international-phonetic-association/article/revisions-to-the-voqs-system-for-the-transcription-of-voice-quality/67662EA00A0B1D77136AF8514B6F230B | "© International Phonetic Association 2017" | abstract only (first major revision; additions to phonation types; supralaryngeal layout changed) |
| M. J. Ball (2024). Changes to certain extIPA diacritics. Clinical Linguistics & Phonetics 38(7), 692-695, doi:10.1080/02699206.2024.2365205 | https://www.tandfonline.com/doi/full/10.1080/02699206.2024.2365205 (HTTP 403 here); metadata via https://api.crossref.org/works/10.1080/02699206.2024.2365205 and Europe PMC (PMID 38950200) | CC BY-NC-ND 4.0 per Crossref | three extIPA diacritics changed and an updated chart given (abstract); the three were identified from the 2025 chart, not from the paper |

## Named but not opened

Duckworth, Allen, Hardcastle & Ball (1990); Ball, Esling & Dickson (1995, 2000); Bernhardt & Ball (1993); Catford (1977); Laver (1994); Ball & Lowry (2001); Titze (2008); Ward et al. (1969); Kiritani et al. (1993); the Speech STAR interactive extIPA chart (https://www.seeingspeech.ac.uk/speechstar/extipa-charts/). Facts that rest on them come only through the Wikipedia pages above and carry those pages' keys.
