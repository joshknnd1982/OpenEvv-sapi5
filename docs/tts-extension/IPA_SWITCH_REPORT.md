# The switch to the IPA sounds (Phase 12)

Every language, dialect and accent read by eSpeak NG (146 packs) was switched from the old sound generator to the IPA master table's sounds (`realization = "master"`, `engine/packs/to_master.py`; the human's order, D96, D97). The ten native languages and the seven templates were not touched. Before: release 1.3.0 as Phase 12 found it (`phase12/before/status.json`, the staged golden); after: the switched packs on the same modules (`golden-ipa/`, this phase's `asr.py`). Written by `docs/tts-extension/phase12/switch_report.py`; nothing here was judged by ear.

**Measured, not shipped.** Shown these numbers, the human chose to stop and investigate (Q59, 2026-10-11): `languages/`, `packs/`, `golden/` and `golden-staged/` stay as release 1.3.0 has them, and a new session finds and fixes the causes before the switch is measured again. The largest cause found so far is in the master path itself: a language's plain vowel said as the table's cardinal vowel (D97, Q59). The after-figures are `phase12/ipa_status.json` and `phase12/ipa_asr.json`.

## Plainly

**Recognition worse by more than 0.10 CER (75 languages; the human's guard answer was to ship them anyway; at Q59 they chose to stop and investigate):** id 0.101 -> 0.896, ru 0.182 -> 0.757, ru-cl 0.243 -> 0.748, ko 0.462 -> 0.951, en-029 0.039 -> 0.468, ca-ba 0.263 -> 0.664, en-us-nyc 0.013 -> 0.384, en-gb-x-gbcwmd 0.024 -> 0.390, fo 0.540 -> 0.905, nl-be 0.293 -> 0.651, ta 0.505 -> 0.854, af 0.174 -> 0.523, kk 0.354 -> 0.697, sd 1.068 -> 1.408, tk 0.503 -> 0.842, nl 0.199 -> 0.537, ca 0.263 -> 0.597, am 1.321 -> 1.647, nb 0.306 -> 0.630, tr 0.459 -> 0.782, ca-va 0.158 -> 0.479, ms 0.149 -> 0.463, ru-lv 0.179 -> 0.489, hu 0.207 -> 0.516, ca-nw 0.178 -> 0.479, da 0.346 -> 0.644, en-gb-x-rp 0.030 -> 0.328, cy 0.761 -> 1.034, pa 0.593 -> 0.863, sl 0.086 -> 0.350, ne 0.406 -> 0.660, bs 0.258 -> 0.510, hi 0.307 -> 0.557, yue 1.056 -> 1.306, mn 0.447 -> 0.696, lb 0.537 -> 0.784, mn-f 0.449 -> 0.686, is 0.590 -> 0.818, gu 0.437 -> 0.661, et 0.226 -> 0.449, sv 0.270 -> 0.491, sq 0.179 -> 0.398, hyw 0.323 -> 0.540, sw 0.198 -> 0.413, en-gb-x-gbclan 0.022 -> 0.235, hr 0.082 -> 0.294, az 0.486 -> 0.697, mt 0.452 -> 0.662, la 0.109 -> 0.318, te 0.447 -> 0.646, fa 0.447 -> 0.645, as 0.948 -> 1.145, cs 0.185 -> 0.375, hy 0.150 -> 0.338, en-gb-scotland 0.065 -> 0.252, bg 0.250 -> 0.436, lv 0.380 -> 0.556, be 0.244 -> 0.415, eu 0.154 -> 0.325, sk 0.283 -> 0.438, ps-x-southeast 0.613 -> 0.768, th 1.121 -> 1.273, ur 0.579 -> 0.728, ps-x-northwest 0.588 -> 0.728, bn 0.401 -> 0.537, uz 0.473 -> 0.606, ht 0.266 -> 0.391, ps 0.610 -> 0.734, ar 0.649 -> 0.768, ps-x-yusufzai 0.613 -> 0.731, kn 0.350 -> 0.466, he 0.653 -> 0.762, ro 0.133 -> 0.234, fr-be 0.171 -> 0.272, fr-ch 0.171 -> 0.272.

**Levels that dropped (7):** an 2 -> 1, en-us-nyc 4 -> 2, eu 2 -> 1, gn 2 -> 1, lfn 2 -> 1, pt 4 -> 2, pt-br 4 -> 2.

**Recognition better by more than 0.02 CER (5):** si 1.309 -> 0.981, vi-vn-x-south 1.669 -> 1.554, cmn 0.855 -> 0.786, tt 0.617 -> 0.561, ba 0.993 -> 0.973.

**CER over the 96 languages Whisper scores:** median change +0.210, mean +0.204; worse in 91, better in 5.

**Where the sounds came from (R21f, `to_master.py --all`):** composed 14324, created 12561, kept-apart 6, legacy-fallback 8, silent 980, table 17171.

## Every language

Fallbacks: phonemes on their old line because of a fault, each with its reason in the pack's map and in `to_master.py`'s report. Kept apart: phonemes kept on their old line so as not to merge with another (D96). Check A: pass or FAIL, the formant and F0 checks met / made. Check B: against reference ranges. Level: before / after (`report.py`; nothing above 4 without a native signature).

| Tag | Language | Template | Fallbacks | Kept apart | CER 1.3.0 | CER now | Change | Check A before | Check A after | Check B before / after | Level before / after | Failure layer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ab | Abkhaz | dedx | 0 | 0 | - | - | - | pass 643/650 | pass 622/625 | too few 2/4 / too few 1/4 | 2 / 2 | - |
| af | Afrikaans | dedx | 0 | 0 | 0.174 | 0.523 | +0.348 | pass 982/986 | pass 1008/1012 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| am | Amharic | dedx | 0 | 0 | 1.321 | 1.647 | +0.327 | pass 832/835 | pass 763/766 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| an | Aragonese | esex | 0 | 0 | - | - | - | pass 951/952 | FAIL 847/942 | too few 3/5 / too few 3/5 | 2 / 1 | phoneme values |
| ar | Arabic | dedx | 0 | 1 | 0.649 | 0.768 | +0.119 | pass 1828/1836 | pass 1836/1865 | too few 6/10 / too few 4/10 | 2 / 2 | unknown |
| as | Assamese | dedx | 0 | 0 | 0.948 | 1.145 | +0.197 | pass 1120/1128 | pass 1026/1038 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| az | Azerbaijani | dedx | 0 | 0 | 0.486 | 0.697 | +0.210 | pass 850/854 | pass 841/849 | too few 3/5 / too few 2/5 | 2 / 2 | unknown |
| ba | Bashkir | dedx | 0 | 0 | 0.993 | 0.973 | -0.020 | pass 799/801 | pass 780/782 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| be | Belarusian | dedx | 0 | 0 | 0.244 | 0.415 | +0.171 | pass 975/976 | pass 907/918 | too few 3/5 / too few 2/5 | 2 / 2 | unknown |
| bg | Bulgarian | dedx | 0 | 0 | 0.250 | 0.436 | +0.186 | pass 2124/2129 | pass 1910/1918 | too few 7/10 / too few 5/10 | 2 / 2 | unknown |
| bn | Bengali | itix | 0 | 0 | 0.401 | 0.537 | +0.137 | pass 1204/1210 | pass 1199/1206 | too few 2/4 / too few 4/5 | 2 / 2 | unknown |
| bpy | Bishnupriya Manipuri | dedx | 0 | 0 | - | - | - | pass 1120/1128 | pass 1026/1038 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| bs | Bosnian | itix | 0 | 0 | 0.258 | 0.510 | +0.252 | pass 801/808 | pass 1083/1086 | too few 2/4 / too few 5/5 | 2 / 2 | unknown |
| ca | Catalan | esex | 0 | 0 | 0.263 | 0.597 | +0.333 | pass 971/971 | pass 805/808 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| ca-ba | Catalan (Balearic) | esex | 0 | 0 | 0.263 | 0.664 | +0.401 | pass 969/969 | pass 770/773 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| ca-nw | Catalan (North-western) | esex | 0 | 0 | 0.178 | 0.479 | +0.301 | pass 974/974 | pass 903/964 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ca-va | Catalan (Valencian) | esex | 0 | 0 | 0.158 | 0.479 | +0.321 | pass 973/974 | pass 872/964 | FAIL 21/29 / FAIL 10/29 | 2 / 2 | phoneme values |
| chr | Cherokee | enux | 0 | 0 | - | - | - | pass 981/991 | pass 1017/1018 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| cmn | Chinese (Mandarin, latin as English) | dedx | 0 | 1 | 0.855 | 0.786 | -0.069 | FAIL 1983/2367 | pass 2088/2131 | too few 0/10 / too few 2/10 | 1 / 2 | stress-or-tone |
| cmn-latn-pinyin | Chinese (Mandarin, latin as Pinyin) | dedx | 0 | 1 | - | - | - | FAIL 947/1124 | pass 991/1005 | too few 0/5 / too few 1/5 | 1 / 2 | - |
| crh | Crimean Tatar | dedx | 0 | 0 | - | - | - | pass 807/811 | pass 786/795 | too few 3/5 / too few 2/5 | 2 / 2 | - |
| cs | Czech | dedx | 0 | 0 | 0.185 | 0.375 | +0.190 | pass 825/827 | pass 902/909 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| cv | Chuvash | dedx | 0 | 0 | - | - | - | pass 865/867 | pass 855/861 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| cy | Welsh | engx | 0 | 0 | 0.761 | 1.034 | +0.273 | pass 866/866 | pass 947/948 | too few 2/5 / too few 4/5 | 2 / 2 | unknown |
| da | Danish | dedx | 0 | 0 | 0.346 | 0.644 | +0.297 | pass 769/770 | pass 933/948 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| el | Greek | esex | 0 | 0 | 0.697 | 0.718 | +0.021 | pass 741/745 | pass 702/737 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| en-029 | English (Caribbean) | engx | 0 | 0 | 0.039 | 0.468 | +0.429 | pass 1010/1012 | pass 1129/1161 | too few 2/5 / too few 3/5 | 2 / 2 | unknown |
| en-gb-scotland | English (Scotland) | engx | 0 | 0 | 0.065 | 0.252 | +0.188 | pass 1083/1083 | pass 1165/1166 | too few 2/5 / too few 4/5 | 2 / 2 | unknown |
| en-gb-x-gbclan | English (Lancaster) | engx | 0 | 0 | 0.022 | 0.235 | +0.213 | pass 1008/1009 | pass 1161/1161 | too few 2/5 / too few 4/5 | 2 / 2 | unknown |
| en-gb-x-gbcwmd | English (West Midlands) | engx | 0 | 0 | 0.024 | 0.390 | +0.366 | pass 1009/1010 | pass 1162/1163 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| en-gb-x-rp | English (Received Pronunciation) | engx | 0 | 0 | 0.030 | 0.328 | +0.297 | pass 1007/1008 | pass 1161/1161 | too few 2/5 / too few 4/5 | 2 / 2 | unknown |
| en-shaw | English (Shavian alphabet) | engx | 0 | 0 | - | - | - | pass 2205/2213 | pass 2341/2342 | too few 4/10 / too few 7/10 | 2 / 2 | - |
| en-us-nyc | English (America, New York City) | enux | 0 | 0 | 0.013 | 0.384 | +0.371 | pass 2300/2306 | pass 2282/2287 | pass 82/94 / FAIL 63/94 | 4 / 2 | phoneme values |
| eo | Esperanto | esex | 0 | 0 | - | - | - | pass 889/890 | pass 796/880 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| et | Estonian | dedx | 0 | 0 | 0.226 | 0.449 | +0.223 | pass 773/774 | pass 888/894 | too few 3/5 / too few 2/5 | 2 / 2 | unknown |
| eu | Basque | esex | 0 | 0 | 0.154 | 0.325 | +0.171 | pass 979/980 | FAIL 862/970 | too few 4/7 / too few 4/7 | 2 / 1 | phoneme values |
| fa | Persian | dedx | 0 | 0 | 0.447 | 0.645 | +0.198 | pass 1788/1803 | pass 1811/1830 | too few 6/10 / too few 4/10 | 2 / 2 | unknown |
| fa-latn | Persian (Pinglish) | dedx | 0 | 0 | - | - | - | pass 764/769 | pass 736/744 | too few 3/5 / too few 2/5 | 2 / 2 | - |
| fi | Finnish | dedx | 0 | 0 | 0.490 | 0.529 | +0.039 | pass 816/816 | pass 879/885 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| fo | Faroese | dedx | 0 | 0 | 0.540 | 0.905 | +0.365 | pass 1015/1017 | pass 1088/1100 | too few 4/5 / too few 1/5 | 2 / 2 | unknown |
| fr-be | French (Belgium) | frfx | 2: `@fr:#cFR`, `ʰcFʀ` | 0 | 0.171 | 0.272 | +0.101 | pass 1208/1208 | pass 2237/2241 | too few 7/12 / too few 10/12 | 2 / 2 | unknown |
| fr-ch | French (Switzerland) | frfx | 2: `@fr:#cFR`, `ʰcFʀ` | 0 | 0.171 | 0.272 | +0.101 | pass 1208/1208 | pass 2237/2241 | too few 7/12 / too few 10/12 | 2 / 2 | unknown |
| ga | Gaelic (Irish) | engx | 0 | 0 | - | - | - | pass 1867/1869 | pass 2102/2104 | too few 4/10 / too few 8/10 | 2 / 2 | - |
| gd | Gaelic (Scottish) | engx | 0 | 0 | - | - | - | pass 949/952 | pass 1035/1035 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| gn | Guarani | esux | 0 | 0 | - | - | - | pass 881/884 | FAIL 783/877 | too few 3/5 / too few 4/5 | 2 / 1 | phoneme values |
| grc | Greek (Ancient) | esex | 0 | 0 | - | - | - | pass 156/156 | pass 872/947 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| gu | Gujarati | dedx | 0 | 0 | 0.437 | 0.661 | +0.224 | pass 1113/1123 | pass 1023/1035 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| hak | Hakka Chinese | esex | 0 | 0 | - | - | - | pass 2181/2183 | pass 2135/2186 | too few 6/10 / too few 6/10 | 2 / 2 | - |
| haw | Hawaiian | esex | 0 | 0 | 0.421 | 0.468 | +0.047 | pass 161/162 | pass 841/901 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| he | Hebrew | esex | 0 | 0 | 0.653 | 0.762 | +0.109 | pass 2020/2024 | pass 1839/2015 | too few 6/10 / too few 8/10 | 2 / 2 | unknown |
| hi | Hindi | dedx | 0 | 0 | 0.307 | 0.557 | +0.250 | pass 871/882 | pass 1011/1023 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| hr | Croatian | itix | 0 | 0 | 0.082 | 0.294 | +0.213 | pass 801/808 | pass 1083/1086 | too few 2/4 / too few 5/5 | 2 / 2 | unknown |
| ht | Haitian Creole | frfx | 2: `@ht:#cFR`, `ʰcFʀ` | 0 | 0.266 | 0.391 | +0.125 | pass 1058/1061 | pass 1048/1049 | too few 4/7 / too few 4/7 | 2 / 2 | unknown |
| hu | Hungarian | dedx | 0 | 0 | 0.207 | 0.516 | +0.309 | pass 690/691 | pass 792/798 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| hy | Armenian (East Armenia) | dedx | 0 | 0 | 0.150 | 0.338 | +0.188 | pass 898/902 | pass 815/823 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| hyw | Armenian (West Armenia) | dedx | 0 | 0 | 0.323 | 0.540 | +0.218 | pass 897/902 | pass 806/817 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| ia | Interlingua | itix | 0 | 0 | - | - | - | pass 908/908 | pass 904/905 | too few 2/4 / too few 4/5 | 2 / 2 | - |
| id | Indonesian | itix | 0 | 0 | 0.101 | 0.896 | +0.795 | pass 908/909 | pass 893/894 | too few 2/4 / too few 4/5 | 2 / 2 | unknown |
| io | Ido | esex | 0 | 0 | - | - | - | pass 889/890 | pass 796/880 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| is | Icelandic | dedx | 0 | 0 | 0.590 | 0.818 | +0.228 | pass 807/811 | pass 934/939 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| jbo | Lojban | esex | 0 | 0 | - | - | - | pass 889/890 | pass 841/880 | too few 3/5 / too few 4/5 | 2 / 2 | - |
| ka | Georgian | dedx | 0 | 0 | 0.312 | 0.391 | +0.079 | pass 1160/1163 | pass 1081/1086 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| kaa | Karakalpak | dedx | 0 | 0 | - | - | - | pass 787/792 | pass 779/787 | too few 3/5 / too few 2/5 | 2 / 2 | - |
| kk | Kazakh | dedx | 0 | 0 | 0.354 | 0.697 | +0.342 | pass 846/846 | pass 787/787 | too few 2/5 / too few 2/5 | 2 / 2 | unknown |
| kl | Greenlandic | itix | 0 | 0 | - | - | - | pass 666/668 | pass 930/930 | too few 2/4 / too few 4/5 | 2 / 2 | - |
| kn | Kannada | dedx | 0 | 0 | 0.350 | 0.466 | +0.116 | pass 2025/2035 | pass 2097/2115 | too few 7/10 / too few 6/10 | 2 / 2 | unknown |
| ko | Korean | itix | 0 | 0 | 0.462 | 0.951 | +0.489 | pass 990/990 | pass 988/988 | too few 2/4 / too few 4/5 | 2 / 2 | unknown |
| kok | Konkani | dedx | 0 | 0 | - | - | - | pass 1111/1120 | pass 1020/1032 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| ku | Kurdish | dedx | 0 | 0 | - | - | - | pass 712/716 | pass 851/857 | too few 4/5 / too few 2/5 | 2 / 2 | - |
| ky | Kyrgyz | dedx | 0 | 0 | - | - | - | pass 633/636 | pass 786/788 | too few 3/4 / too few 2/4 | 2 / 2 | - |
| la | Latin | itix | 0 | 0 | 0.109 | 0.318 | +0.209 | pass 720/722 | pass 949/950 | too few 2/4 / too few 5/5 | 2 / 2 | unknown |
| lb | Luxembourgish | dedx | 0 | 0 | 0.537 | 0.784 | +0.247 | pass 760/763 | pass 844/873 | too few 3/4 / too few 2/4 | 2 / 2 | unknown |
| lfn | Lingua Franca Nova | esex | 0 | 0 | - | - | - | pass 935/936 | FAIL 833/926 | too few 3/5 / too few 3/5 | 2 / 1 | phoneme values |
| lij | Ligurian | itix | 0 | 0 | - | - | - | pass 731/738 | pass 1002/1003 | too few 2/4 / too few 4/5 | 2 / 2 | - |
| lt | Lithuanian | dedx | 0 | 0 | 0.348 | 0.434 | +0.086 | pass 1850/1852 | pass 1993/2011 | too few 8/10 / too few 6/10 | 2 / 2 | unknown |
| ltg | Latgalian | dedx | 0 | 0 | - | - | - | pass 820/820 | pass 878/887 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| lv | Latvian | dedx | 0 | 0 | 0.380 | 0.556 | +0.177 | pass 820/820 | pass 878/887 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| mi | Māori | esex | 0 | 0 | 0.325 | 0.360 | +0.035 | pass 160/161 | pass 908/957 | too few 3/5 / too few 4/5 | 2 / 2 | unknown |
| mk | Macedonian | itix | 0 | 0 | 0.164 | 0.256 | +0.092 | pass 1095/1098 | pass 1092/1097 | too few 2/4 / too few 5/5 | 2 / 2 | unknown |
| ml | Malayalam | dedx | 0 | 0 | 0.935 | 1.000 | +0.065 | pass 1088/1094 | pass 1036/1046 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| mn | Mongolian | dedx | 0 | 0 | 0.447 | 0.696 | +0.249 | pass 714/718 | pass 862/867 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| mn-f | Ankhmaa | dedx | 0 | 0 | 0.449 | 0.686 | +0.237 | pass 714/718 | pass 862/867 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| mr | Marathi | dedx | 0 | 0 | 0.549 | 0.599 | +0.049 | pass 1113/1123 | pass 1027/1039 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| ms | Malay | itix | 0 | 0 | 0.149 | 0.463 | +0.314 | pass 908/909 | pass 893/894 | too few 2/4 / too few 4/5 | 2 / 2 | unknown |
| mt | Maltese | dedx | 0 | 0 | 0.452 | 0.662 | +0.210 | pass 780/780 | pass 838/846 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| mto | Totontepec Mixe | esux | 0 | 0 | - | - | - | pass 284/284 | pass 852/887 | none / none | 2 / 2 | - |
| my | Myanmar (Burmese) | dedx | 0 | 1 | 0.986 | 1.085 | +0.100 | pass 1360/1361 | pass 1210/1214 | too few 2/5 / too few 3/5 | 2 / 2 | stress-or-tone |
| nb | Norwegian Bokmål | dedx | 0 | 0 | 0.306 | 0.630 | +0.324 | pass 1839/1843 | pass 2060/2063 | too few 8/10 / too few 2/10 | 2 / 2 | unknown |
| nci | Nahuatl (Classical) | esux | 0 | 0 | - | - | - | pass 281/281 | pass 836/871 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| ne | Nepali | dedx | 0 | 0 | 0.406 | 0.660 | +0.255 | pass 1145/1153 | pass 1053/1065 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| nl | Dutch | dedx | 0 | 0 | 0.199 | 0.537 | +0.337 | pass 889/890 | pass 877/889 | too few 4/5 / too few 1/5 | 2 / 2 | unknown |
| nl-be | Dutch (Southern Standard, Flanders) | dedx | 0 | 0 | 0.293 | 0.651 | +0.358 | pass 889/890 | pass 877/889 | too few 4/5 / too few 1/5 | 2 / 2 | unknown |
| nog | Nogai | dedx | 0 | 0 | - | - | - | pass 1698/1707 | pass 1686/1699 | too few 9/12 / too few 5/12 | 2 / 2 | - |
| om | Oromo | dedx | 0 | 0 | - | - | - | pass 694/697 | pass 797/801 | too few 3/5 / too few 2/5 | 2 / 2 | - |
| or | Oriya | itix | 0 | 0 | - | - | - | pass 1200/1208 | pass 1199/1206 | too few 2/4 / too few 4/5 | 2 / 2 | - |
| pa | Punjabi | dedx | 0 | 0 | 0.593 | 0.863 | +0.270 | pass 1076/1090 | pass 1019/1033 | too few 3/5 / too few 2/5 | 2 / 2 | stress-or-tone |
| pap | Papiamento | esux | 0 | 0 | - | - | - | pass 941/942 | pass 881/930 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| pdc | Pennsylvania Dutch (Lancaster) | dedx | 0 | 0 | - | - | - | pass 977/980 | pass 1008/1059 | too few 4/5 / too few 2/5 | 2 / 2 | - |
| pdc-x-lehigh | Pennsylvania Dutch (Lehigh) | dedx | 0 | 0 | - | - | - | pass 977/980 | pass 1008/1059 | too few 4/5 / too few 2/5 | 2 / 2 | - |
| pdc-x-midwest | Pennsylvania Dutch (Midwest) | dedx | 0 | 0 | - | - | - | pass 988/991 | pass 1018/1070 | too few 4/5 / too few 2/5 | 2 / 2 | - |
| piqd | Klingon | dedx | 0 | 0 | - | - | - | pass 999/1000 | pass 929/942 | too few 3/5 / too few 1/5 | 2 / 2 | - |
| ps | Pashto | dedx | 0 | 0 | 0.610 | 0.734 | +0.124 | pass 907/909 | pass 829/836 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| ps-x-northwest | Pashto (Northwestern) | dedx | 0 | 0 | 0.588 | 0.728 | +0.139 | pass 913/915 | pass 830/836 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| ps-x-southeast | Pashto (Southeastern) | dedx | 0 | 0 | 0.613 | 0.768 | +0.155 | pass 907/909 | pass 829/836 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| ps-x-yusufzai | Pashto (Yusufzai) | dedx | 0 | 0 | 0.613 | 0.731 | +0.118 | pass 909/911 | pass 822/828 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| pt | Portuguese (Portugal) | esex | 0 | 0 | 0.064 | 0.150 | +0.086 | pass 967/970 | pass 903/970 | pass 20/24 / FAIL 13/24 | 4 / 2 | phoneme values |
| pt-br | Portuguese (Brazil) | esux | 1: `@pt:I` | 0 | 0.059 | 0.109 | +0.050 | pass 981/985 | pass 881/975 | pass 22/27 / FAIL 16/27 | 4 / 2 | phoneme values |
| py | Pyash | esex | 0 | 0 | - | - | - | pass 889/890 | pass 859/880 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| qdb | Lang Belta | dedx | 0 | 0 | - | - | - | pass 1235/1237 | pass 1194/1200 | too few 3/5 / too few 2/5 | 2 / 2 | - |
| qu | Quechua | esux | 0 | 0 | - | - | - | FAIL 897/899, 3 silent | FAIL 799/892 | too few 3/5 / too few 4/5 | 1 / 1 | phoneme values |
| quc | K'iche' | esux | 0 | 0 | - | - | - | pass 594/596 | pass 1654/1837 | too few 6/10 / too few 6/10 | 2 / 2 | - |
| qya | Quenya | dedx | 0 | 0 | - | - | - | pass 726/728 | pass 833/843 | too few 3/5 / too few 2/5 | 2 / 2 | - |
| ro | Romanian | itix | 0 | 0 | 0.133 | 0.234 | +0.101 | pass 1163/1163 | pass 1157/1159 | too few 2/4 / too few 4/5 | 2 / 2 | unknown |
| ru | Russian | dedx | 0 | 0 | 0.182 | 0.757 | +0.575 | pass 2227/2231 | pass 2075/2105 | too few 10/12 / too few 5/12 | 2 / 2 | unknown |
| ru-cl | Russian (Classic) | dedx | 0 | 0 | 0.243 | 0.748 | +0.505 | pass 2227/2231 | pass 2075/2105 | too few 10/12 / too few 5/12 | 2 / 2 | unknown |
| ru-lv | Russian (Latvia) | dedx | 0 | 0 | 0.179 | 0.489 | +0.310 | pass 2227/2231 | pass 2077/2105 | too few 10/12 / too few 5/12 | 2 / 2 | unknown |
| rup | Aromanian | itix | 0 | 0 | - | - | - | pass 997/997 | pass 991/993 | too few 2/4 / too few 4/5 | 2 / 2 | - |
| sd | Sindhi | dedx | 0 | 0 | 1.068 | 1.408 | +0.340 | pass 875/885 | pass 1011/1023 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| shn | Shan (Tai Yai) | dedx | 0 | 0 | - | - | - | pass 1923/2003 | pass 1857/2014 | too few 4/10 / too few 2/10 | 2 / 2 | - |
| si | Sinhala | dedx | 0 | 0 | 1.309 | 0.981 | -0.329 | pass 1096/1105 | pass 1080/1092 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| sjn | Sindarin | dedx | 0 | 0 | - | - | - | pass 776/780 | pass 844/849 | too few 4/5 / too few 2/5 | 2 / 2 | - |
| sk | Slovak | dedx | 0 | 0 | 0.283 | 0.438 | +0.155 | pass 825/827 | pass 905/909 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| sl | Slovenian | dedx | 0 | 0 | 0.086 | 0.350 | +0.265 | pass 765/765 | pass 831/839 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| smj | Lule Saami | dedx | 0 | 0 | - | - | - | pass 1865/1871 | pass 2009/2014 | too few 6/10 / too few 6/10 | 2 / 2 | - |
| sq | Albanian | itix | 0 | 0 | 0.179 | 0.398 | +0.219 | pass 966/968 | pass 966/968 | too few 1/4 / too few 5/5 | 2 / 2 | unknown |
| sr | Serbian | itix | 0 | 0 | 0.166 | 0.225 | +0.059 | pass 824/831 | pass 1122/1125 | too few 2/4 / too few 5/5 | 2 / 2 | unknown |
| sv | Swedish | dedx | 0 | 0 | 0.270 | 0.491 | +0.221 | pass 1833/1839 | pass 2021/2060 | too few 6/10 / too few 2/10 | 2 / 2 | unknown |
| sw | Swahili | esex | 0 | 0 | 0.198 | 0.413 | +0.215 | pass 843/843 | pass 757/837 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ta | Tamil | dedx | 0 | 0 | 0.505 | 0.854 | +0.349 | pass 1944/1955 | pass 2110/2131 | too few 8/10 / too few 6/10 | 2 / 2 | unknown |
| te | Telugu | dedx | 0 | 0 | 0.447 | 0.646 | +0.199 | pass 875/885 | pass 1015/1027 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| th | Thai | esex | 0 | 0 | 1.121 | 1.273 | +0.152 | pass 506/506 | pass 933/968 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| ti | Tigrinya | dedx | 0 | 0 | - | - | - | pass 844/848 | pass 774/779 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| tk | Turkmen | dedx | 0 | 0 | 0.503 | 0.842 | +0.339 | pass 698/701 | pass 885/894 | too few 3/5 / too few 2/5 | 2 / 2 | unknown |
| tn | Setswana | esex | 0 | 0 | - | - | - | pass 957/957 | pass 940/946 | too few 3/5 / too few 3/5 | 2 / 2 | - |
| tr | Turkish | dedx | 0 | 0 | 0.459 | 0.782 | +0.324 | pass 720/725 | pass 841/849 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| tt | Tatar | dedx | 0 | 0 | 0.617 | 0.561 | -0.056 | pass 799/801 | pass 780/782 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| ug | Uyghur | dedx | 0 | 0 | - | - | - | pass 664/665 | pass 853/855 | too few 4/5 / too few 3/5 | 2 / 2 | - |
| uk | Ukrainian | dedx | 0 | 0 | 0.254 | 0.286 | +0.032 | pass 811/813 | pass 740/744 | too few 4/5 / too few 2/5 | 2 / 2 | unknown |
| ur | Urdu | dedx | 0 | 0 | 0.579 | 0.728 | +0.149 | pass 871/882 | pass 1011/1023 | too few 4/5 / too few 3/5 | 2 / 2 | unknown |
| uz | Uzbek | dedx | 0 | 0 | 0.473 | 0.606 | +0.133 | pass 781/785 | pass 784/786 | too few 3/5 / too few 3/5 | 2 / 2 | unknown |
| vi | Vietnamese (Northern) | dedx | 0 | 0 | 1.361 | 1.420 | +0.059 | pass 982/986 | pass 989/991 | too few 3/5 / too few 2/5 | 2 / 2 | stress-or-tone |
| vi-vn-x-central | Vietnamese (Central) | dedx | 0 | 0 | 1.405 | 1.461 | +0.056 | pass 980/986 | pass 960/991 | too few 2/5 / too few 2/5 | 2 / 2 | stress-or-tone |
| vi-vn-x-south | Vietnamese (Southern) | dedx | 0 | 0 | 1.669 | 1.554 | -0.115 | pass 982/986 | pass 987/991 | too few 3/5 / too few 2/5 | 2 / 2 | stress-or-tone |
| xex | xextan-test | dedx | 1: `@pt:I` | 0 | - | - | - | pass 943/948 | pass 884/887 | too few 4/6 / too few 3/6 | 2 / 2 | - |
| yue | Chinese (Cantonese) | dedx | 0 | 1 | 1.056 | 1.306 | +0.250 | pass 2001/2003 | pass 1999/2029 | too few 2/10 / too few 2/10 | 2 / 2 | stress-or-tone |
| yue-latn-jyutping | Chinese (Cantonese, latin as Jyutping) | dedx | 0 | 1 | - | - | - | pass 886/886 | pass 887/903 | too few 1/5 / too few 1/5 | 2 / 2 | - |

## Each fallback and each phoneme kept apart, with its reason

- ar `@cmn:i[` (kept-apart): kept apart from @cmn:i. (ɨ): eSpeak NG writes i̪ and ɨ, which come out alike on dedx
- cmn `@cmn:i[` (kept-apart): kept apart from @cmn:i. (ɨ): eSpeak NG writes i̪ and ɨ, which come out alike on dedx
- cmn-latn-pinyin `@cmn:i[` (kept-apart): kept apart from @cmn:i. (ɨ): eSpeak NG writes i̪ and ɨ, which come out alike on dedx
- fr-be `@fr:#cFR` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- fr-be `ʰcFʀ` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- fr-ch `@fr:#cFR` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- fr-ch `ʰcFʀ` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- ht `@ht:#cFR` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- ht `ʰcFʀ` (legacy-fallback): IPA 'ʰcFʀ': U+0046 F is not in the table (LATIN CAPITAL LETTER F)
- my `@my:ng` (kept-apart): kept apart from @my:N (ŋ): eSpeak NG writes nɡ and ŋ, which come out alike on dedx
- pt-br `@pt:I` (legacy-fallback): IPA '' holds no sound to realise
- xex `@pt:I` (legacy-fallback): IPA '' holds no sound to realise
- yue `@yue:ng` (kept-apart): kept apart from @yue:N- (ŋ̩): eSpeak NG writes nɡ̩ and ŋ̩, which come out alike on dedx
- yue-latn-jyutping `@yue:ng` (kept-apart): kept apart from @yue:N- (ŋ̩): eSpeak NG writes nɡ̩ and ŋ̩, which come out alike on dedx
