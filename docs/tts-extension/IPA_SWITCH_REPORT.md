# The switch to the IPA sounds (Phase 12)

Every language, dialect and accent read by eSpeak NG (146 packs) was switched from the old sound generator to the IPA master table's sounds (`realization = "master"`, `engine/packs/to_master.py`; the human's order, D96, D97). The ten native languages and the seven templates were not touched. Before: release 1.3.0 as Phase 12 found it (`phase12/before/status.json`, the staged golden); after: the switched packs on the same modules (`golden-ipa/`, this phase's `asr.py`). Written by `docs/tts-extension/phase12/switch_report.py`; nothing here was judged by ear.

**Shipped (2026-10-12, the human's answer to Q62: ship all now).** This report replaces D97's. The first switch (D97, column "CER D97") said every language's phonemes as the table's single value per IPA letter and was much worse (median CER +0.210); the human chose to stop and investigate (Q59). The causes were found by measurement and fixed in the generator, not in the languages (D98): the master path now reads a language's phonemes phonemically (a letter the template has is its own phone; what the template lacks comes from the table, a vowel towards the typical value the table cites; the language's own stop onsets, aspiration and vowel formants from its profile and `engine/packs/phonemic.toml`; eSpeak NG's own vowel lengths), and a fault of the shared map line (a phoneme's variant's IPA taken for the phoneme's) was mended. Measured on these packs: `golden-ipa/` (now also `golden/` and `golden-staged/`), check A and B, `asr.py` and `diag.py`; the after-figures are `phase12/p12c_status.json` and `phase12/p12c_asr.json`. Still worse by more than 0.10, shipped as the human chose: Cantonese, Burmese and Sindhi (above 0.98 CER in 1.3.0 already), Malay, Greek and Welsh (whole vowel-initial sentences heard as Whisper's filler phrases). Quechua fails check A as it did in 1.3.0 (Q61). Any language goes back to its old sounds with one line (`realization = "legacy"`).

## Plainly

**Recognition worse by more than 0.10 CER (6 languages; shipped, the human's answer to Q62):** yue 1.056 -> 1.574, ms 0.149 -> 0.298, el 0.697 -> 0.825, cy 0.761 -> 0.888, my 0.986 -> 1.103, sd 1.068 -> 1.185.

**Levels that dropped (1):** pt-br 4 -> 2.

**Recognition better by more than 0.02 CER (28):** vi-vn-x-south 1.669 -> 1.468, fi 0.490 -> 0.294, uk 0.254 -> 0.101, tt 0.617 -> 0.484, is 0.590 -> 0.472, ru-cl 0.243 -> 0.134, ar 0.649 -> 0.548, bs 0.258 -> 0.159, lt 0.348 -> 0.250, haw 0.421 -> 0.328, sk 0.283 -> 0.193, sv 0.270 -> 0.180, si 1.309 -> 1.224, cmn 0.855 -> 0.771, nl-be 0.293 -> 0.223, ur 0.579 -> 0.510, lb 0.537 -> 0.468, bg 0.250 -> 0.182, mi 0.325 -> 0.265, ko 0.462 -> 0.402, lv 0.380 -> 0.327, vi 1.361 -> 1.323, mr 0.549 -> 0.514, ka 0.312 -> 0.279, ru 0.182 -> 0.150, ru-lv 0.179 -> 0.147, ps-x-southeast 0.613 -> 0.585, nb 0.306 -> 0.279.

**CER over the 96 languages Whisper scores:** median change -0.006, mean -0.002; worse in 44, better in 52.

**Where the sounds came from (R21f, `to_master.py --all`):** composed 14322, created 12567, kept-apart 9, legacy-fallback 6, silent 980, table 17166.

## Every language

Fallbacks: phonemes on their old line because of a fault, each with its reason in the pack's map and in `to_master.py`'s report. Kept apart: phonemes kept on their old line so as not to merge with another (D96). Check A: pass or FAIL, the formant and F0 checks met / made. Check B: against reference ranges. Level: before / after (`report.py`; nothing above 4 without a native signature).

| Tag | Language | Template | Fallbacks | Kept apart | CER 1.3.0 | CER D97 | CER now | Change | Check A before | Check A after | Check B before / after | Level before / after | Failure layer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ab | Abkhaz | dedx | 0 | 0 | - | - | - | - | pass 643/650 | pass 753/753 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| af | Afrikaans | dedx | 0 | 0 | 0.174 | 0.523 | 0.158 | -0.017 | pass 982/986 | pass 949/950 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| am | Amharic | dedx | 0 | 0 | 1.321 | 1.647 | 1.312 | -0.009 | pass 832/835 | pass 915/915 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| an | Aragonese | esex | 0 | 0 | - | - | - | - | pass 951/952 | pass 941/943 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| ar | Arabic | dedx | 0 | 1 | 0.649 | 0.768 | 0.548 | -0.101 | pass 1828/1836 | pass 2081/2083 | too few 6/10 / too few 6/10 | 2 / 2 | unknown |
| as | Assamese | dedx | 0 | 0 | 0.948 | 1.145 | 1.020 | +0.073 | pass 1120/1128 | pass 1214/1216 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| az | Azerbaijani | dedx | 0 | 0 | 0.486 | 0.697 | 0.475 | -0.011 | pass 850/854 | pass 925/927 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| ba | Bashkir | dedx | 0 | 0 | 0.993 | 0.973 | 0.997 | +0.003 | pass 799/801 | pass 750/752 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| be | Belarusian | dedx | 0 | 0 | 0.244 | 0.415 | 0.256 | +0.013 | pass 975/976 | pass 1032/1032 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| bg | Bulgarian | dedx | 0 | 0 | 0.250 | 0.436 | 0.182 | -0.068 | pass 2124/2129 | pass 2066/2070 | too few 7/10 / too few 8/10 | 2 / 2 | unknown |
| bn | Bengali | itix | 0 | 0 | 0.401 | 0.537 | 0.447 | +0.047 | pass 1204/1210 | pass 1199/1206 | too few 2/4 / too few 2/4 | 2 / 2 | unknown |
| bpy | Bishnupriya Manipuri | dedx | 0 | 0 | - | - | - | - | pass 1120/1128 | pass 1214/1216 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| bs | Bosnian | itix | 0 | 0 | 0.258 | 0.510 | 0.159 | -0.099 | pass 801/808 | pass 1081/1086 | too few 2/4 / too few 1/4 | 2 / 2 | unknown |
| ca | Catalan | esex | 0 | 0 | 0.263 | 0.597 | 0.336 | +0.073 | pass 971/971 | pass 809/809 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ca-ba | Catalan (Balearic) | esex | 0 | 0 | 0.263 | 0.664 | 0.316 | +0.053 | pass 969/969 | pass 774/774 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ca-nw | Catalan (North-western) | esex | 0 | 0 | 0.178 | 0.479 | 0.170 | -0.008 | pass 974/974 | pass 965/965 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ca-va | Catalan (Valencian) | esex | 0 | 0 | 0.158 | 0.479 | 0.165 | +0.007 | pass 973/974 | pass 964/965 | FAIL 21/29 / FAIL 21/29 | 2 / 2 | phoneme values |
| chr | Cherokee | enux | 0 | 0 | - | - | - | - | pass 981/991 | pass 1004/1010 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| cmn | Chinese (Mandarin, latin as English) | dedx | 0 | 1 | 0.855 | 0.786 | 0.771 | -0.084 | FAIL 1983/2367 | pass 2298/2397 | too few 0/10 / too few 4/10 | 1 / 2 | stress-or-tone |
| cmn-latn-pinyin | Chinese (Mandarin, latin as Pinyin) | dedx | 0 | 1 | - | - | - | - | FAIL 947/1124 | pass 1098/1145 | too few 0/5 / too few 2/5 | 1 / 2 | - |
| crh | Crimean Tatar | dedx | 0 | 0 | - | - | - | - | pass 807/811 | pass 896/896 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| cs | Czech | dedx | 0 | 0 | 0.185 | 0.375 | 0.188 | +0.003 | pass 825/827 | pass 1069/1070 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| cv | Chuvash | dedx | 0 | 0 | - | - | - | - | pass 865/867 | pass 942/942 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| cy | Welsh | engx | 0 | 0 | 0.761 | 1.034 | 0.888 | +0.127 | pass 866/866 | pass 914/914 | too few 2/5 / too few 2/5 | 2 / 2 | unknown |
| da | Danish | dedx | 0 | 0 | 0.346 | 0.644 | 0.376 | +0.029 | pass 769/770 | pass 947/948 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| el | Greek | esex | 0 | 0 | 0.697 | 0.718 | 0.825 | +0.128 | pass 741/745 | pass 736/738 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| en-029 | English (Caribbean) | engx | 0 | 0 | 0.039 | 0.468 | 0.062 | +0.024 | pass 1010/1012 | pass 1095/1097 | too few 2/5 / too few 2/5 | 2 / 2 | - |
| en-gb-scotland | English (Scotland) | engx | 0 | 0 | 0.065 | 0.252 | 0.052 | -0.013 | pass 1083/1083 | pass 1100/1100 | too few 2/5 / too few 2/5 | 2 / 2 | - |
| en-gb-x-gbclan | English (Lancaster) | engx | 0 | 0 | 0.022 | 0.235 | 0.039 | +0.017 | pass 1008/1009 | pass 1107/1107 | too few 2/5 / too few 2/5 | 2 / 2 | - |
| en-gb-x-gbcwmd | English (West Midlands) | engx | 0 | 0 | 0.024 | 0.390 | 0.054 | +0.030 | pass 1009/1010 | pass 1107/1107 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| en-gb-x-rp | English (Received Pronunciation) | engx | 0 | 0 | 0.030 | 0.328 | 0.065 | +0.034 | pass 1007/1008 | pass 1103/1103 | too few 2/5 / too few 2/5 | 2 / 2 | - |
| en-shaw | English (Shavian alphabet) | engx | 0 | 0 | - | - | - | - | pass 2205/2213 | pass 2223/2224 | too few 4/10 / too few 4/10 | 2 / 2 | - |
| en-us-nyc | English (America, New York City) | enux | 0 | 0 | 0.013 | 0.384 | 0.039 | +0.026 | pass 2300/2306 | pass 2319/2328 | pass 82/94 / pass 78/94 | 4 / 4 | - |
| eo | Esperanto | esex | 0 | 0 | - | - | - | - | pass 889/890 | pass 879/880 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| et | Estonian | dedx | 0 | 0 | 0.226 | 0.449 | 0.246 | +0.021 | pass 773/774 | pass 1041/1041 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| eu | Basque | esex | 0 | 0 | 0.154 | 0.325 | 0.146 | -0.008 | pass 979/980 | pass 970/971 | too few 4/7 / too few 4/7 | 2 / 2 | - |
| fa | Persian | dedx | 0 | 0 | 0.447 | 0.645 | 0.429 | -0.018 | pass 1788/1803 | pass 1945/1946 | too few 6/10 / too few 8/10 | 2 / 2 | unknown |
| fa-latn | Persian (Pinglish) | dedx | 0 | 0 | - | - | - | - | pass 764/769 | pass 842/842 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| fi | Finnish | dedx | 0 | 0 | 0.490 | 0.529 | 0.294 | -0.197 | pass 816/816 | pass 1020/1020 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| fo | Faroese | dedx | 0 | 0 | 0.540 | 0.905 | 0.565 | +0.025 | pass 1015/1017 | pass 1134/1134 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| fr-be | French (Belgium) | frfx | 2: `@fr:#cFR`, `ʰcFʀ` | 0 | 0.171 | 0.272 | 0.152 | -0.019 | pass 1208/1208 | pass 2247/2247 | too few 7/12 / too few 7/12 | 2 / 2 | unknown |
| fr-ch | French (Switzerland) | frfx | 2: `@fr:#cFR`, `ʰcFʀ` | 0 | 0.171 | 0.272 | 0.152 | -0.019 | pass 1208/1208 | pass 2247/2247 | too few 7/12 / too few 7/12 | 2 / 2 | unknown |
| ga | Gaelic (Irish) | engx | 0 | 0 | - | - | - | - | pass 1867/1869 | pass 2018/2018 | too few 4/10 / too few 4/10 | 2 / 2 | - |
| gd | Gaelic (Scottish) | engx | 0 | 0 | - | - | - | - | pass 949/952 | pass 1011/1011 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| gn | Guarani | esux | 0 | 0 | - | - | - | - | pass 881/884 | pass 873/876 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| grc | Greek (Ancient) | esex | 0 | 0 | - | - | - | - | pass 156/156 | pass 946/948 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| gu | Gujarati | dedx | 0 | 1 | 0.437 | 0.661 | 0.486 | +0.049 | pass 1113/1123 | pass 1207/1209 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| hak | Hakka Chinese | esex | 0 | 0 | - | - | - | - | pass 2181/2183 | pass 2179/2185 | too few 6/10 / too few 6/10 | 2 / 2 | - |
| haw | Hawaiian | esex | 0 | 0 | 0.421 | 0.468 | 0.328 | -0.094 | pass 161/162 | pass 900/901 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| he | Hebrew | esex | 0 | 0 | 0.653 | 0.762 | 0.637 | -0.016 | pass 2020/2024 | pass 2015/2015 | too few 6/10 / too few 6/10 | 2 / 2 | unknown |
| hi | Hindi | dedx | 0 | 0 | 0.307 | 0.557 | 0.386 | +0.079 | pass 871/882 | pass 1195/1197 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| hr | Croatian | itix | 0 | 0 | 0.082 | 0.294 | 0.093 | +0.011 | pass 801/808 | pass 1081/1086 | too few 2/4 / too few 1/4 | 2 / 2 | - |
| ht | Haitian Creole | frfx | 2: `@ht:#cFR`, `ʰcFʀ` | 0 | 0.266 | 0.391 | 0.307 | +0.042 | pass 1058/1061 | pass 1049/1049 | too few 4/7 / too few 4/7 | 2 / 2 | unknown |
| hu | Hungarian | dedx | 0 | 0 | 0.207 | 0.516 | 0.197 | -0.010 | pass 690/691 | pass 975/975 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| hy | Armenian (East Armenia) | dedx | 0 | 0 | 0.150 | 0.338 | 0.145 | -0.005 | pass 898/902 | pass 978/978 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| hyw | Armenian (West Armenia) | dedx | 0 | 0 | 0.323 | 0.540 | 0.320 | -0.003 | pass 897/902 | pass 978/978 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| ia | Interlingua | itix | 0 | 0 | - | - | - | - | pass 908/908 | pass 905/905 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| id | Indonesian | itix | 0 | 0 | 0.101 | 0.896 | 0.108 | +0.007 | pass 908/909 | pass 895/896 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| io | Ido | esex | 0 | 0 | - | - | - | - | pass 889/890 | pass 879/880 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| is | Icelandic | dedx | 0 | 0 | 0.590 | 0.818 | 0.472 | -0.117 | pass 807/811 | pass 1041/1045 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| jbo | Lojban | esex | 0 | 0 | - | - | - | - | pass 889/890 | pass 879/880 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| ka | Georgian | dedx | 0 | 0 | 0.312 | 0.391 | 0.279 | -0.033 | pass 1160/1163 | pass 1239/1239 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| kaa | Karakalpak | dedx | 0 | 0 | - | - | - | - | pass 787/792 | pass 873/873 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| kk | Kazakh | dedx | 0 | 0 | 0.354 | 0.697 | 0.420 | +0.066 | pass 846/846 | pass 918/918 | too few 2/5 / too few 2/5 | 2 / 2 | unknown |
| kl | Greenlandic | itix | 0 | 0 | - | - | - | - | pass 666/668 | pass 929/929 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| kn | Kannada | dedx | 0 | 0 | 0.350 | 0.466 | 0.346 | -0.004 | pass 2025/2035 | pass 2265/2270 | too few 7/10 / too few 7/10 | 2 / 2 | unknown |
| ko | Korean | itix | 0 | 0 | 0.462 | 0.951 | 0.402 | -0.060 | pass 990/990 | pass 988/988 | too few 2/4 / too few 2/4 | 2 / 2 | unknown |
| kok | Konkani | dedx | 0 | 0 | - | - | - | - | pass 1111/1120 | pass 1206/1208 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| ku | Kurdish | dedx | 0 | 0 | - | - | - | - | pass 712/716 | pass 996/996 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| ky | Kyrgyz | dedx | 0 | 0 | - | - | - | - | pass 633/636 | pass 757/759 | too few 3/4 / too few 3/4 | 2 / 2 | - |
| la | Latin | itix | 0 | 0 | 0.109 | 0.318 | 0.130 | +0.021 | pass 720/722 | pass 949/950 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| lb | Luxembourgish | dedx | 0 | 0 | 0.537 | 0.784 | 0.468 | -0.068 | pass 760/763 | pass 845/849 | too few 3/4 / too few 3/4 | 2 / 2 | unknown |
| lfn | Lingua Franca Nova | esex | 0 | 0 | - | - | - | - | pass 935/936 | pass 926/927 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| lij | Ligurian | itix | 0 | 0 | - | - | - | - | pass 731/738 | pass 1001/1001 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| lt | Lithuanian | dedx | 0 | 0 | 0.348 | 0.434 | 0.250 | -0.098 | pass 1850/1852 | pass 2309/2309 | too few 8/10 / too few 6/10 | 2 / 2 | unknown |
| ltg | Latgalian | dedx | 0 | 0 | - | - | - | - | pass 820/820 | pass 1038/1038 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| lv | Latvian | dedx | 0 | 0 | 0.380 | 0.556 | 0.327 | -0.053 | pass 820/820 | pass 1038/1038 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| mi | Māori | esex | 0 | 0 | 0.325 | 0.360 | 0.265 | -0.060 | pass 160/161 | pass 957/958 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| mk | Macedonian | itix | 0 | 0 | 0.164 | 0.256 | 0.156 | -0.008 | pass 1095/1098 | pass 1095/1097 | too few 2/4 / too few 2/4 | 2 / 2 | unknown |
| ml | Malayalam | dedx | 0 | 0 | 0.935 | 1.000 | 0.990 | +0.056 | pass 1088/1094 | pass 1037/1042 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| mn | Mongolian | dedx | 0 | 0 | 0.447 | 0.696 | 0.466 | +0.019 | pass 714/718 | pass 945/948 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| mn-f | Ankhmaa | dedx | 0 | 0 | 0.449 | 0.686 | 0.498 | +0.048 | pass 714/718 | pass 945/948 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| mr | Marathi | dedx | 0 | 1 | 0.549 | 0.599 | 0.514 | -0.035 | pass 1113/1123 | pass 1209/1211 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| ms | Malay | itix | 0 | 0 | 0.149 | 0.463 | 0.298 | +0.149 | pass 908/909 | pass 895/896 | too few 2/4 / too few 2/4 | 2 / 2 | unknown |
| mt | Maltese | dedx | 0 | 0 | 0.452 | 0.662 | 0.461 | +0.009 | pass 780/780 | pass 977/977 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| mto | Totontepec Mixe | esux | 0 | 0 | - | - | - | - | pass 284/284 | pass 887/888 | none / none | 2 / 2 | - |
| my | Myanmar (Burmese) | dedx | 0 | 1 | 0.986 | 1.085 | 1.103 | +0.117 | pass 1360/1361 | pass 1361/1361 | too few 2/5 / too few 2/5 | 2 / 2 | stress-or-tone |
| nb | Norwegian Bokmål | dedx | 0 | 0 | 0.306 | 0.630 | 0.279 | -0.027 | pass 1839/1843 | pass 2082/2082 | too few 8/10 / too few 6/10 | 2 / 2 | unknown |
| nci | Nahuatl (Classical) | esux | 0 | 0 | - | - | - | - | pass 281/281 | pass 871/872 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| ne | Nepali | dedx | 0 | 0 | 0.406 | 0.660 | 0.487 | +0.082 | pass 1145/1153 | pass 1237/1239 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| nl | Dutch | dedx | 0 | 0 | 0.199 | 0.537 | 0.197 | -0.003 | pass 889/890 | pass 979/979 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| nl-be | Dutch (Southern Standard, Flanders) | dedx | 0 | 0 | 0.293 | 0.651 | 0.223 | -0.070 | pass 889/890 | pass 979/979 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| nog | Nogai | dedx | 0 | 0 | - | - | - | - | pass 1698/1707 | pass 1734/1735 | too few 9/12 / too few 10/12 | 2 / 2 | - |
| om | Oromo | dedx | 0 | 0 | - | - | - | - | pass 694/697 | pass 951/951 | too few 3/5 / too few 2/5 | 2 / 2 | - |
| or | Oriya | itix | 0 | 0 | - | - | - | - | pass 1200/1208 | pass 1197/1206 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| pa | Punjabi | dedx | 0 | 0 | 0.593 | 0.863 | 0.600 | +0.007 | pass 1076/1090 | pass 1203/1205 | too few 3/5 / too few 4/5 | 2 / 2 | stress-or-tone |
| pap | Papiamento | esux | 0 | 0 | - | - | - | - | pass 941/942 | pass 930/931 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| pdc | Pennsylvania Dutch (Lancaster) | dedx | 0 | 0 | - | - | - | - | pass 977/980 | pass 956/957 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| pdc-x-lehigh | Pennsylvania Dutch (Lehigh) | dedx | 0 | 0 | - | - | - | - | pass 977/980 | pass 951/952 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| pdc-x-midwest | Pennsylvania Dutch (Midwest) | dedx | 0 | 0 | - | - | - | - | pass 988/991 | pass 968/969 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| piqd | Klingon | dedx | 0 | 0 | - | - | - | - | pass 999/1000 | pass 1046/1046 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| ps | Pashto | dedx | 0 | 0 | 0.610 | 0.734 | 0.591 | -0.019 | pass 907/909 | pass 983/983 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| ps-x-northwest | Pashto (Northwestern) | dedx | 0 | 0 | 0.588 | 0.728 | 0.591 | +0.003 | pass 913/915 | pass 983/983 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| ps-x-southeast | Pashto (Southeastern) | dedx | 0 | 0 | 0.613 | 0.768 | 0.585 | -0.028 | pass 907/909 | pass 983/983 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| ps-x-yusufzai | Pashto (Yusufzai) | dedx | 0 | 0 | 0.613 | 0.731 | 0.604 | -0.009 | pass 909/911 | pass 983/983 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| pt | Portuguese (Portugal) | esex | 0 | 0 | 0.064 | 0.150 | 0.105 | +0.041 | pass 967/970 | pass 962/963 | pass 20/24 / pass 20/24 | 4 / 4 | - |
| pt-br | Portuguese (Brazil) | esux | 0 | 0 | 0.059 | 0.109 | 0.041 | -0.018 | pass 981/985 | pass 972/974 | pass 22/27 / FAIL 21/27 | 4 / 2 | phoneme values |
| py | Pyash | esex | 0 | 0 | - | - | - | - | pass 889/890 | pass 879/880 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| qdb | Lang Belta | dedx | 0 | 0 | - | - | - | - | pass 1235/1237 | pass 1197/1200 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| qu | Quechua | esux | 0 | 0 | - | - | - | - | FAIL 897/899, 3 silent | FAIL 892/892, 2 silent | too few 3/5 / too few 3/5 | 1 / 1 | phoneme values |
| quc | K'iche' | esux | 0 | 0 | - | - | - | - | pass 594/596 | pass 1828/1834 | too few 6/10 / too few 6/10 | 2 / 2 | - |
| qya | Quenya | dedx | 0 | 0 | - | - | - | - | pass 726/728 | pass 976/976 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| ro | Romanian | itix | 0 | 0 | 0.133 | 0.234 | 0.157 | +0.024 | pass 1163/1163 | pass 1158/1158 | too few 2/4 / too few 2/4 | 2 / 2 | unknown |
| ru | Russian | dedx | 0 | 0 | 0.182 | 0.757 | 0.150 | -0.032 | pass 2227/2231 | pass 2233/2233 | too few 10/12 / too few 9/12 | 2 / 2 | unknown |
| ru-cl | Russian (Classic) | dedx | 0 | 0 | 0.243 | 0.748 | 0.134 | -0.109 | pass 2227/2231 | pass 2233/2233 | too few 10/12 / too few 9/12 | 2 / 2 | - |
| ru-lv | Russian (Latvia) | dedx | 0 | 0 | 0.179 | 0.489 | 0.147 | -0.032 | pass 2227/2231 | pass 2233/2233 | too few 10/12 / too few 9/12 | 2 / 2 | - |
| rup | Aromanian | itix | 0 | 0 | - | - | - | - | pass 997/997 | pass 992/992 | too few 2/4 / too few 2/4 | 2 / 2 | - |
| sd | Sindhi | dedx | 0 | 0 | 1.068 | 1.408 | 1.185 | +0.117 | pass 875/885 | pass 1195/1197 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| shn | Shan (Tai Yai) | dedx | 0 | 0 | - | - | - | - | pass 1923/2003 | pass 2260/2260 | too few 4/10 / too few 4/10 | 2 / 2 | - |
| si | Sinhala | dedx | 0 | 0 | 1.309 | 0.981 | 1.224 | -0.086 | pass 1096/1105 | pass 1080/1086 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| sjn | Sindarin | dedx | 0 | 0 | - | - | - | - | pass 776/780 | pass 982/982 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| sk | Slovak | dedx | 0 | 0 | 0.283 | 0.438 | 0.193 | -0.090 | pass 825/827 | pass 1069/1070 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| sl | Slovenian | dedx | 0 | 0 | 0.086 | 0.350 | 0.066 | -0.019 | pass 765/765 | pass 1001/1002 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| smj | Lule Saami | dedx | 0 | 0 | - | - | - | - | pass 1865/1871 | pass 2302/2302 | too few 6/10 / too few 8/10 | 2 / 2 | - |
| sq | Albanian | itix | 0 | 0 | 0.179 | 0.398 | 0.171 | -0.008 | pass 966/968 | pass 966/968 | too few 1/4 / too few 1/4 | 2 / 2 | unknown |
| sr | Serbian | itix | 0 | 0 | 0.166 | 0.225 | 0.172 | +0.006 | pass 824/831 | pass 1119/1124 | too few 2/4 / too few 1/4 | 2 / 2 | unknown |
| sv | Swedish | dedx | 0 | 0 | 0.270 | 0.491 | 0.180 | -0.090 | pass 1833/1839 | pass 2088/2088 | too few 6/10 / too few 6/10 | 2 / 2 | unknown |
| sw | Swahili | esex | 0 | 0 | 0.198 | 0.413 | 0.190 | -0.008 | pass 843/843 | pass 837/837 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ta | Tamil | dedx | 0 | 0 | 0.505 | 0.854 | 0.488 | -0.017 | pass 1944/1955 | pass 2454/2456 | too few 8/10 / too few 6/10 | 2 / 2 | unknown |
| te | Telugu | dedx | 0 | 0 | 0.447 | 0.646 | 0.453 | +0.007 | pass 875/885 | pass 1197/1199 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| th | Thai | esex | 0 | 0 | 1.121 | 1.273 | 1.211 | +0.090 | pass 506/506 | pass 961/964 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ti | Tigrinya | dedx | 0 | 0 | - | - | - | - | pass 844/848 | pass 928/928 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| tk | Turkmen | dedx | 0 | 0 | 0.503 | 0.842 | 0.490 | -0.013 | pass 698/701 | pass 954/956 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| tn | Setswana | esex | 0 | 0 | - | - | - | - | pass 957/957 | pass 942/943 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| tr | Turkish | dedx | 0 | 0 | 0.459 | 0.782 | 0.472 | +0.013 | pass 720/725 | pass 988/990 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| tt | Tatar | dedx | 0 | 0 | 0.617 | 0.561 | 0.484 | -0.132 | pass 799/801 | pass 750/752 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| ug | Uyghur | dedx | 0 | 0 | - | - | - | - | pass 664/665 | pass 927/930 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| uk | Ukrainian | dedx | 0 | 0 | 0.254 | 0.286 | 0.101 | -0.153 | pass 811/813 | pass 877/877 | too few 4/5 / too few 4/5 | 2 / 2 | - |
| ur | Urdu | dedx | 0 | 0 | 0.579 | 0.728 | 0.510 | -0.069 | pass 871/882 | pass 1195/1197 | too few 4/5 / too few 4/5 | 2 / 2 | unknown |
| uz | Uzbek | dedx | 0 | 0 | 0.473 | 0.606 | 0.527 | +0.054 | pass 781/785 | pass 863/866 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| vi | Vietnamese (Northern) | dedx | 0 | 1 | 1.361 | 1.420 | 1.323 | -0.037 | pass 982/986 | pass 970/977 | too few 3/5 / too few 3/5 | 2 / 2 | stress-or-tone |
| vi-vn-x-central | Vietnamese (Central) | dedx | 0 | 0 | 1.405 | 1.461 | 1.472 | +0.067 | pass 980/986 | pass 1110/1110 | too few 2/5 / too few 2/5 | 2 / 2 | stress-or-tone |
| vi-vn-x-south | Vietnamese (Southern) | dedx | 0 | 0 | 1.669 | 1.554 | 1.468 | -0.201 | pass 982/986 | pass 1110/1110 | too few 3/5 / too few 3/5 | 2 / 2 | stress-or-tone |
| xex | xextan-test | dedx | 0 | 0 | - | - | - | - | pass 943/948 | pass 1013/1014 | too few 4/6 / too few 4/6 | 2 / 2 | - |
| yue | Chinese (Cantonese) | dedx | 0 | 1 | 1.056 | 1.306 | 1.574 | +0.518 | pass 2001/2003 | pass 2266/2266 | too few 2/10 / too few 2/10 | 2 / 2 | stress-or-tone |
| yue-latn-jyutping | Chinese (Cantonese, latin as Jyutping) | dedx | 0 | 1 | - | - | - | - | pass 886/886 | pass 1014/1014 | too few 1/5 / too few 1/5 | 2 / 2 | - |

## Each fallback and each phoneme kept apart, with its reason

- ar `@cmn:i[` (kept-apart): kept apart from @cmn:i. (ɨ): eSpeak NG writes i̪ and ɨ, which come out alike on dedx
- cmn `@cmn:i[` (kept-apart): kept apart from @cmn:i. (ɨ): eSpeak NG writes i̪ and ɨ, which come out alike on dedx
- cmn-latn-pinyin `@cmn:i[` (kept-apart): kept apart from @cmn:i. (ɨ): eSpeak NG writes i̪ and ɨ, which come out alike on dedx
- fr-be `@fr:#cFR` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- fr-be `ʰcFʀ` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- fr-ch `@fr:#cFR` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- fr-ch `ʰcFʀ` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- gu `@gu:i:` (kept-apart): kept apart from @gu:i (i): eSpeak NG writes iː and i, which come out alike on dedx
- ht `@ht:#cFR` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- ht `ʰcFʀ` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- mr `@mr:i:` (kept-apart): kept apart from @mr:i (i): eSpeak NG writes iː and i, which come out alike on dedx
- my `@my:ng` (kept-apart): kept apart from @my:N (ŋ): eSpeak NG writes nɡ and ŋ, which come out alike on dedx
- vi `@vi:a` (kept-apart): kept apart from @vi:a: (aː): eSpeak NG writes a and aː, which come out alike on dedx
- yue `@yue:ng` (kept-apart): kept apart from @yue:N- (ŋ̩): eSpeak NG writes nɡ̩ and ŋ̩, which come out alike on dedx
- yue-latn-jyutping `@yue:ng` (kept-apart): kept apart from @yue:N- (ŋ̩): eSpeak NG writes nɡ̩ and ŋ̩, which come out alike on dedx
