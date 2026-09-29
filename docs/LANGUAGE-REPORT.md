# The languages, one by one

For each of the 145 languages read by eSpeak NG: what the literature says the language sounds like, what eSpeak NG reads otherwise, and what OpenEVV says. The first two are summaries of the language's profile in `engine\profiles`, which names its sources and marks every number with how sure it is; the third is read off the language's pack. `docs\SOUNDS.md` says what the numbers in a sound mean.

This page is written by `engine\accent\report.py`.

## Abkhaz (`ab`)

Northwest Caucasian (Abkhaz-Adyghean), Abkhaz-Abaza. Described: Literary Abkhaz, based on the Abzhywa dialect (58 consonants). The Bzyp dialect has 67 consonants and Sadz 60; the Cwyzhy variety described in the Journal of the IPA is spoken in Turkey.

**What the language has.** Three-way laryngeal contrast in stops and affricates: voiced, voiceless aspirated, ejective. Plain, palatalised and labialised series of velars and uvulars: kʰ kʲʰ kʷʰ, qʼ qʲʼ qʷʼ, χ χʲ χʷ, ʁ ʁʲ ʁʷ. Labialised dental stops and labialised alveolo-palatal affricates: dʷ tʷʰ tʷʼ, dʑʷ tɕʷʰ tɕʷʼ. Three places for sibilants: alveolar s z, palato-alveolar ʃ ʒ (with labialised ʃʷ ʒʷ), retroflex ʂ ʐ, and the matching affricates. Uvular against pharyngeal fricatives: χ against ħ, χʷ against ħʷ. Two vowels, open /a/ and close central /ə/ (a vertical system); long /aː/ is a third vowel or a sequence /aa/. Place of stress is contrastive.

Stress: free, mobile, contrastive. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The ejectives п т к ҵ ҷ ҿ are plain unaspirated consonants (p_, t_ and k_ use consonants/p-, consonants/t- and ustop/k_unasp2); the ejc flag is set on some of them but no glottalic release is synthesised.
- The uvular ejectives ҟ ҟь ҟә (q, qj, qw) are declared as voiced fricatives and built from the formants of the voiced uvular fricative (voc/Q_ulv), so they sound like a voiced fricative, not an ejective stop.
- Several voiceless consonants are flagged voiced and built on voiced formant data: қ (kʰ), қә (kʷʰ), кә (kʷʼ), ҭә (tʷʰ), тә (tʷʼ), ч (tʃʰ) and ҷ (tʃʼ).
- ҩ /ɥ/ is defined as a vowel (phoneme Uw), so it counts as a syllable and takes the stress: аҩны gives [aˈɥnə].
- у and и are always the vowels [u] and [i]; the glides /w/ and /j/ are never produced: уара gives [uˈara] and аԥсуа gives [apsˈua].
- аа, the long vowel /aː/, is two separate short vowels.
- е, и, о, у are independent vowel phonemes of fixed quality; the colouring of /a ə/ by palatalised and labialised consonants is not modelled.
- No stress rule is set for ab, so the default penultimate stress applies, which in words with the article a- is usually the article; Abkhaz stress is lexical and mobile. The deletion of unstressed schwa is absent.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 34 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: b (b=s1: voi=1 lead=75), ɡ (g=s1: voi=1 lead=75), gʲ (g=s2: f2=129 f3=127 voi=1 lead=75), gʷ (g=s3 w=s4: f2=80 f3=92 voi=1 lead=75; hold=55), ʁʷ (r=s6: f2=75), d (d=s1: voi=1 lead=75), ʐ (Z=s8: a4=51 f2=92 f3=87 f4=88), dz (d=s10 z=s11: voi=1 lead=75 hold=85; hold=70), dʑʷ (d=s12 w=s4 Z=s13: f2=103 f3=112 voi=1 lead=75 hold=85; hold=55; a3=34 a4=55 a5=22 f2=103 f3=112 hold=70), i (i=s14: dur=56), k (k=s15: vot=28), kʲ (k=s16: f2=129 f3=127 vot=36), kʲʰ (k=s19: f2=129 f3=127 vot=85 asp=50), q (k=s21: f2=68 f3=109 f1=118 burst=3 vot=30), qʲ (k=s22: f2=129 f3=127 f1=118 burst=3 vot=38), qʷ (k=s23 w=s4: f2=54 f1=118 burst=3 vot=30; hold=55), p_ (p=s24: vot=13), p (p=s24: vot=13), r (l=s25: tap=3 tapms=18 f2=109 f3=77), t_ (t=s26: vot=17), tʷ (t=s27 w=s4: f2=80 f3=92 vot=17; hold=55), t (t=s26: vot=17), tʷʰ (t=s28 w=s4: f2=80 f3=92 vot=70 asp=50; hold=55), u (u=s29: dur=57), χ (x=s30: f2=88), χʲ (x=s31: f2=191 f3=108), ħʷ (<h=s33: ms=85 whisper=48 f1=125 f2=88), tsʰ (T >h=s34: ms=45 whisper=46), tɕʷ (t=s35 w=s4 S=s36: f2=97 f3=107 hold=85; hold=55; a2=31 a3=34 a4=34 a5=22 f2=97 f3=107 hold=70), ʈʂʰ (t=s37 S=s38 >h=s34: f2=87 f3=83 f4=88 a4=52 a5=42 hold=85; a4=54 f2=87 f3=83 f4=88 hold=70; ms=45 whisper=46), ʂ (S=s39: a4=54 f2=87 f3=83 f4=88), ʃʷ (S=s9: f2=82 f3=93), ɥ (j=s40: f1=56 f2=111 f3=84), ɖʐ (d=s41 Z=s42: f2=92 f3=87 f4=88 a4=52 a5=42 voi=1 lead=75 hold=85; a4=51 f2=92 f3=87 f4=88 hold=70).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no is said higher as a whole, with little or no rise at the end.

Sources: Hewitt, B. George (1979). Abkhaz. Lingua Descriptive Studies 2. Amsterdam: North-Holland. Hewitt, George (2010). Abkhaz: A Comprehensive Self-Tutor. Munich: Lincom Europa. Chirikba, Viacheslav A. (2003). Abkhaz. Munich: Lincom Europa. Spruit, Arie (1986). Abkhaz Studies. PhD dissertation, University of Leiden. Catford, J. C. (1972). Labialization in Caucasian languages, with special reference to Abkhaz. Proceedings of the 7th International Congress of Phonetic Sciences. Catford, J. C. (1977). Mountain of tongues: the languages of the Caucasus. Annual Review of Anthropology 6. And 3 more in the profile.

## Afrikaans (`af`)

Indo-European, Germanic, West Germanic, Low Franconian (daughter of 17th-century Dutch). Described: Standard Afrikaans of South Africa, in the form described by Wissing (2020) and Donaldson (1993); regional and ethnolectal differences are noted.

**What the language has.** Short /a/ versus long /ɑː/ (man versus maan), which also differ in quality. Short mid vowels versus the long mid vowels, which are centring diphthongs: /ɛ/ versus /ɪə/ (bed, beet), /ɔ/ versus /ʊə/ (bom, boom), /œ/ versus /øə/ (put, neus). A stressable schwa /ə/ (written i: sit, kind) versus /i/ (written ie: siek) and /ɛ/. Front rounded /y øə œ œi/ versus unrounded /i ɪə ə əi/, a contrast that many speakers weaken or give up. Three closing diphthongs /əi œi œu/ (ys, huis, koud). Voiced versus voiceless plosives /b d/ versus /p t/ in onsets, neutralised at the end of a word; the contrast is cued more and more by pitch on the following vowel. /f/ versus /v/ (vier versus wier); native words have no /z/. Lexical stress.

Stress: lexical, mostly initial in native words. Rhythm: stress-timed. Tone: tonogenesis in progress.

**What eSpeak NG reads otherwise than the literature has it.**

- nasalised vowels keep the following [n] and are not lengthened: ons [õns], mens [mẽns], Afrikaans [ɐfrikˈɑ̃ns], where the language has [ɔ̃ːs], [mɛ̃ːs], [afriˈkɑ̃ːs].
- /ɦ/ is a voiceless [h].
- /b d/ are always fully voiced and there is no pitch lowering after them, so the cue that carries the contrast for most present-day speakers is missing.
- ê outside the lowering contexts is close [eː] (sê, hê, gesê) where the language has open [ɛː].
- /y/ is not lengthened before /r/ (vuur, muur, uur come out with the short vowel), although ie and oe are.
- dae and vrae lose their final schwa ([dɑː], [frɑː]).
- /l/ imports the English phoneme, clear before vowels, where Afrikaans has a velarised /l/ throughout.
- questions are given the same tune whether they are yes-no or wh-questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), ɐ (A=s8: f1=85), i (i=s5: dur=56), u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), h (<h=s16: ms=70 whisper=44), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɛ (E=s41: dur=84), ɔ (O=s42: dur=85), œ (OE=s41: dur=84), æ (E=s43: f1=124 f2=92 f3=92 dur=84), ɑː (a=s45: f1=89 f2=86 dur=72), iə (j=s46 @: hold=55), ʊə (w=s46 @: hold=55), ɛɪ (E:=s51: g1=83 g2=94 g3=97 glide=1), ẽ (e=s60: dur=53 nas=100).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (wie, wat, waar, wanneer ...) ends as a statement does, from a high question word.

Sources: Wissing, Daan (2020). Afrikaans. Journal of the International Phonetic Association 50(1), 127-140. Donaldson, Bruce C. (1993). A Grammar of Afrikaans. Berlin: Mouton de Gruyter. Donaldson, Bruce (1994). Afrikaans. In König and van der Auwera (eds.), The Germanic Languages. London: Routledge. Le Roux, T. H. and Pienaar, P. de Villiers (1927). Afrikaanse fonetiek. Cape Town: Juta. Combrink, J. G. H. and de Stadler, L. G. (1987). Afrikaanse fonologie. Johannesburg: Macmillan. Lass, Roger (1987). Intradiphthongal dependencies. In Anderson and Durand (eds.), Explorations in Dependency Phonology. Dordrecht: Foris. And 1 more in the profile.

## Amharic (`am`)

Afro-Asiatic, Semitic, South Semitic (Ethiosemitic), South Ethiopic. Described: Standard Amharic of Addis Ababa, as described by Hayward & Hayward (1992) from a speaker from Gondar.

**What the language has.** Three-way laryngeal contrast in stops and affricates: voiceless (moderately aspirated), voiced, ejective. Ejective fricative /sʼ/ against /s/ and /z/. Consonant gemination, lexical and grammatical (alə 'he said' against allə 'there is'), not shown in the script. Labialised against plain consonants, mainly before /a/. Two central vowels /ɨ/ and /ə/ against five peripheral vowels. /p pʼ pʷʼ/ occur in loanwords only; /ʔ/ is marginal.

Stress: weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Gemination is not written in the Ethiopic script and is never produced: አለ is [ʔalə] for both /alə/ 'he said' and /allə/ 'there is', አማርኛ has a single [ɲ].
- Every sixth-order letter inside a word is given the vowel ɨ; only a word-final one after a vowel is left bare. ትምህርት gives [tɨmɨhɨrɨt] for [tɨmhɨrt], ይሰብራል gives [jɨsəβɨral] for [jɨsəbral], ቋንቋ gives [kʼʷanɨkʼʷa] for [kʼʷankʼʷa].
- ጸ and ፀ are the plain affricate [ts], not the ejective /sʼ/ [tsʼ].
- Only k` uses an ejective recording (ustop/k_ejc). p`, t` and tS` use unaspirated plosive samples after a pause, although p_ejc, t_ejc and c_ejc samples exist in phsource/ustop.
- Stress is fixed on the first syllable, with the French stress lengths; the literature describes weak, variable stress.
- Labialised consonants are consonant plus w sequences.
- The IPA names of the ejectives are written with a grave accent (t`) instead of ʼ.
- No devoicing of voiced obstruents before pause, no palatalisation before /e/.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 18 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), r (l=s9: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), e (e=s6: dur=80), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s10: vot=17), k (k=s12: vot=28), h (<h=s17: ms=70 whisper=44), ɲ (n=s19: f2=136 f3=109), b (b=s21: voi=1 lead=75), d (d=s21: voi=1 lead=75), ɡ (g=s21: voi=1 lead=75), ɨ (Y=s42: f1=78 f2=106 f3=114 dur=137), t` (t=s10: vot=17), k` (k=s12: vot=28).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (ማን, ምን, የት, መቼ ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Hayward, Katrina & Hayward, Richard J. (1992). Amharic. Journal of the International Phonetic Association 22: 48-52. Reprinted in the Handbook of the International Phonetic Association, Cambridge University Press, 1999. Leslau, Wolf (1995). Reference Grammar of Amharic. Wiesbaden: Harrassowitz. Hudson, Grover (1997). Amharic and Argobba. In Robert Hetzron (ed.), The Semitic Languages. London: Routledge. Demolin, Didier (2004). Acoustic and aerodynamic characteristics of ejectives in Amharic. Journal of the Acoustical Society of America 115: 2610 (abstract). Seid, Hussien, Rajendran, S. & Yegnanarayana, B. (2009). Acoustic characteristics of ejectives in Amharic. Proceedings of Interspeech 2009, Brighton. Alemayehu Haile (1987). Lexical stress in Amharic. Journal of Ethiopian Studies 20.

## Aragonese (`an`)

Indo-European, Romance, Western Romance (Pyrenean, between Ibero-Romance and Occitano-Romance). Described: Common written Aragonese read with a central and western Pyrenean pronunciation; segmental detail from the Chistabino illustration (Mott 2007).

**What the language has.** Five vowels /i e a o u/ in stressed and unstressed syllables, without length or nasal contrasts (eastern Ribagorzan varieties add open-mid vowels). Tap /ɾ/ versus trill /r/ between vowels. Three voiceless fricatives at front places, /θ/, /s/ and /ʃ/ (written z or c, s, x), and the affricate /tʃ/ (ch). /l/ versus /ʎ/ and /n/ versus /ɲ/; /ʎ/ is frequent (muller, fillo, viello, güello). Voiced and voiceless stops; central Pyrenean varieties keep Latin voiceless stops between vowels (capeza, lupo) and voice stops after nasals and liquids. Lexical stress. /x/ occurs only in loans from Castilian.

Stress: lexical, on one of the last two syllables in traditional speech. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- written x is read [ks] between vowels unless an i precedes (caxa [kˈaksa], baxo [bˈakso]); in Aragonese spelling x stands for /ʃ/ (only initial x, x after i or after a consonant, and the digraphs aix, uix give [ʃ]).
- word-final r is always pronounced (muller [muʎˈeɾ], cantar [kantˈaɾ]), although it is silent in most varieties; only the plural -rs is reduced.
- open-mid [ɛ ɔ] are used in diphthongs and some other positions (pueyo [pwˈɛjɔ], fuella [fwˈɛʎa], ye [jˈɛ]); Aragonese has plain mid [e o].
- muito is stressed on the i ([muˈito]) instead of having the diphthong [ˈmujto].
- no tune set is selected, so the generic default tunes are used rather than the Spanish set.
- the rules and the exception list are small (290 and 528 lines), so many words fall back on Spanish-like defaults.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 5 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: tʰ (t=s4: vot=68 asp=50), u (u=s5: dur=114), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), eɪ (e=s35: g1=83 g2=109 g3=99 glide=1 dur=149).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (qué, quí, quién, quan ...) ends as a statement does, from a high question word.

Sources: Mott, Brian (2007). Chistabino (Pyrenean Aragonese). Journal of the International Phonetic Association 37(1), 103-114. Nagore Laín, Francho (1989). Gramática de la lengua aragonesa. 5th edition. Zaragoza: Mira Editores. Mott, Brian (1989). El habla de Gistaín. Huesca: Instituto de Estudios Altoaragoneses. Zamora Vicente, Alonso (1967). Dialectología española. 2nd edition. Madrid: Gredos.

## Arabic (`ar`)

Afro-Asiatic, Semitic, Central Semitic, Arabic. Described: Modern Standard Arabic read aloud in formal, fully vocalised style by an educated speaker of Levantine background, the norm of Thelwall & Sa'adeddin (1990). Stress in words without a heavy syllable, the value of jīm, voice onset time and intonation follow the colloquial background of the speaker; where figures come from a colloquial variety this is said.

**What the language has.** Emphatic (pharyngealised, retracted tongue root) against plain coronals: tˤ dˤ sˤ ðˤ against t d s ð. Vowel length: three short and three long vowels. Consonant gemination for every consonant, word-medially and word-finally. Uvular stop /q/ against velar /k/. Pharyngeal /ħ ʕ/ against glottal /h ʔ/ against post-velar /x ɣ/. Interdental fricatives /θ ð ðˤ/ against sibilants /s z sˤ/. Voicing in obstruents (there is no /p/ and no /v/ in native words).

Stress: weight-sensitive, not contrastive. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The emphatic consonants are not pharyngealised: ط is the plain dental phoneme t[ (IPA t̪), ص is s[ (IPA s̪), ظ (phoneme Z) uses the formant data of plain ð and has the IPA name ð, and ض (dH) has the transitions of plain d. The contrast is carried only by the following vowel.
- Emphasis colouring reaches only the vowel directly after ص ض ط ظ (rules with the letter group F choose the vowels a. i. u.). The vowel before an emphatic stays plain (first vowel of بَطَل and مَطَر) and no other syllable is affected, against the spread over the word described in the literature.
- No back [ɑ] next to q, x, ɣ or r, and no emphatic [ɫ] in الله.
- Text without vowel signs gets no short vowels and no gemination unless the word is in ar_listx (about 30,000 entries): يكتبون gives [jktbuːna].
- When the vowel sign comes before the shadda (the Unicode canonical order) the .replace rule in ar_rules corrupts the sequence to two shaddas and the vowel after the geminate is lost: كَتَّبَ gives kat:b'a and مَرَّة gives m'aRRt. The order shadda then vowel works.
- Stress does not follow syllable weight. The default is the antepenultimate vowel (stressRule 4 in the voice file), a final closed syllable with a short vowel forces penultimate stress (rules with =), and every word that begins with ب ف ك ل و has its first syllable marked unstressed as if it were a proclitic. So long vowels do not attract stress: جَمِيل gives ˈdʒamiːl, يَكْتُبُونَ gives jakˈtubuːna, الصَّبَاح is stressed on its second syllable; and كَتَبَ gives kaˈtaba, مَدْرَسَة gives madˈrasat.
- The diphthong /aj/ is two vowels with the stress on the second: بَيْت gives [baˈit] and سَيْف gives [saˈif].
- Case endings and tāʾ marbūṭa are always spoken as written (مَدْرَسَة ends in [at]); there are no pausal forms.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 32 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʔ (<q=s3: ms=50 hush=1), ɹ (r=s8: f2=92 f3=77), a (A=s4: f1=77 f2=117 f3=82), i (i=s6: dur=56), u (u=s7: f1=113 dur=57), t (t=s10: vot=39), k (k=s12: vot=42 asp=50), r (l=s9: tap=3 tapms=18 f2=109 f3=77), h (<h=s17: ms=70 whisper=44), b (b=s21: voi=1 lead=75), d (d=s22: voi=1 lead=70), t̪ (t=s24: f2=91 burst=-4 vot=39), ɡ (g=s21: voi=1 lead=75), ð (v=s33: f2=149 f3=110 a6=28 ab=48), θ (f=s34: f2=146 f3=110 a6=28 ab=48), ɣ (r=s40: f1=73 f3=116), χ (x=s2: f2=88), ħ (<h=s43: ms=85 whisper=48 f1=125 f2=88), ʕ (<h=s44: ms=80 whisper=30 voi=1 f1=125 f2=86), dˤ (d=s45: f2=75 f1=118 voi=1 lead=70), a. (A=s4: f1=77 f2=117 f3=82), i. (Y=s46: f1=78 f2=106 f3=114), u. (u=s7: f1=113 dur=57), ʐ (Z=s35: a4=51 f2=92 f3=87 f4=88), ei (e=s56: g1=81 g2=99 g3=105 glide=1), uo (w=s57 o=s5: hold=55; dur=53).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (ماذا, أين, متى, كيف ...) ends as a statement does, from a high question word.

Sources: Thelwall, Robin & Sa'adeddin, M. Akram (1990). Arabic. Journal of the International Phonetic Association 20(2): 37-39. Reprinted in the Handbook of the International Phonetic Association, Cambridge University Press, 1999. Al-Ani, Salman H. (1970). Arabic Phonology: An Acoustical and Physiological Investigation. The Hague: Mouton. Watson, Janet C. E. (2002). The Phonology and Morphology of Arabic. Oxford University Press. Jongman, Allard, Herd, Wendy, Al-Masri, Mohammad, Sereno, Joan & Combest, Sonja (2011). Acoustics and perception of emphasis in Urban Jordanian Arabic. Journal of Phonetics 39: 85-95. Davis, Stuart (1995). Emphasis spread in Arabic and Grounded Phonology. Linguistic Inquiry 26: 465-498. Card, Elizabeth (1983). A phonetic and phonological study of Arabic emphasis. PhD dissertation, Cornell University. And 8 more in the profile.

## Assamese (`as`)

Indo-European, Indo-Iranian, Indo-Aryan (Eastern zone, Bengali-Assamese). Described: Standard colloquial Assamese of eastern (Upper) Assam, Jorhat-Sibsagar, as in Mahanta 2012.

**What the language has.** Four-way laryngeal contrast in stops at three places (labial, alveolar, velar): voiceless unaspirated, voiceless aspirated, voiced, breathy voiced. No dental versus retroflex contrast: the two series of the script are one alveolar series. No affricates: the letters for the old palatal stops are /s/ and /z/. Voiceless velar fricative /x/, the reflex of the old sibilants (/ɔxɔm/ 'Assam'). Eight oral vowels with a three-way back contrast /u/ : /ʊ/ : /o/ : /ɔ/ (/bul/, /bʊl/ 'colour', /bol/ 'let us go', /bɔɹ/ 'big'). Oral versus nasal vowels only for /ɑ/ and /ʊ/ (/sɑ/ 'look' : /sɑ̃/ 'shadow'). No vowel length contrast. The rhotic is an alveolar approximant /ɹ/.

Stress: weight-sensitive within the first two syllables, weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Only the letter স gives a fricative of the /x/ type, and it is the uvular [χ] followed by a schwa (অসম [ɔχəm]); শ and ষ are [ʃ], a sound Assamese does not have (শেষ [ʃeʃ] for [xɛx]).
- চ and ছ are both the affricate [tʃ] (চাহ [tʃaho]); Assamese has /s/. জ is the palatal stop [ɟ] and য is [dʒ]; Assamese has /z/.
- Dental and retroflex stops are kept apart (ত [t̪] : ট [ʈ]) although Assamese has a single alveolar series.
- ৰ is the tap [ɾ] of the Hindi base table, not the approximant [ɹ].
- There is no /ʊ/: ও is [o], the apostrophe that marks /o/ in ক'লা is ignored, and harmony is applied only to the first inherent vowel.
- Word-final হ and ত receive an extra [o] (মানুহ [manuho], ভাত [bʰato], দাঁত [dãto]).
- ৱ before a vowel sign inserts [ɔ] (ৱাহ [wɔaho]).
- Nasalisation is lost on ওঁ (তেওঁ [teoː]).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 28 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), tʰ (t=s5: vot=70 asp=50), a (A=s6: dur=175), e (e=s7: dur=80), i (i=s8: dur=85), o (o=s7: dur=80), u (u=s9: dur=86), t (t=s11: vot=17), p (p=s12: vot=13), k (k=s13: vot=28), h (<h=s18: ms=70 whisper=44), b (b=s22: voi=1 lead=75), d (d=s22: voi=1 lead=75), ɟ (d=s29: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), ɡ (g=s22: voi=1 lead=75), χ (x=s3: f2=88), iː (i=s44: dur=117), ɔ (O=s50: dur=150), ɔ̃ (O=s58: dur=150 nas=100), bʰ (b=s64: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s64: voi=1 lead=75 brth=90 f0=-15), ɡʰ (g=s64: voi=1 lead=75 brth=90 f0=-15), æ (E=s72: f1=124 f2=92 f3=92 dur=126), tʃʰ (C >h=s73: ms=45 whisper=46).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (কি, কোন, ক’ত, কেতিয়া ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Mahanta, Shakuntala (2012). Assamese. Journal of the International Phonetic Association 42(2), 217-224. Mahanta, Shakuntala (2008). Directionality and Locality in Vowel Harmony: With Special Reference to Vowel Harmony in Assamese. LOT Dissertation Series 173, Utrecht. Goswami, Golok Chandra (1966). An Introduction to Assamese Phonology. Poona: Deccan College. Goswami, Golok Chandra & Tamuli, Jyotiprakash (2003). Asamiya. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Kakati, Banikanta (1962). Assamese, its Formation and Development, 3rd edn. Gauhati: Lawyer's Book Stall. Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. And 2 more in the profile.

## Azerbaijani (`az`)

Turkic, Oghuz. Described: Standard North Azerbaijani (Baku norm, Latin script). The JIPA illustration and the acoustic vowel study describe the Tabriz (Iranian) variety; statements taken from them are marked as such.

**What the language has.** Nine vowel qualities, including the open front /æ/ (ə) against mid /e/ and open back /ɑ/. Voiced versus voiceless aspirated stops and affricates. Palatal stops /c ɟ/ (spelt k, g) versus velar /ɡ/ (spelt q) and /k/ (mostly in Russian loans). Velar fricatives /x/ and /ɣ/ (spelt x, ğ) as full consonants, unlike Turkish soft g. No phonemic vowel length; long vowels only in careful pronunciation of Arabic and Persian loans.

Stress: fixed final by default, with morphological and lexical exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- ğ is handled with the Turkish soft-g rules: it is dropped with lengthening after a vowel and a following identical vowel is swallowed (dağ gives [daː], ağac gives [aːdʒ], oğul gives [oːul]); Azerbaijani ğ is a fricative [ɣ].
- every word-final ə of a polysyllabic word is marked unstressed, so nənə and küçə are stressed on the first syllable instead of the last.
- t between front vowels is turned into [ts] (iti gives [itsi], getir gives [ɟetsir]), which is not standard.
- p t k are the unaspirated base2 stops; Azerbaijani voiceless stops are aspirated.
- unstressable suffixes are not handled: gəlmədi and bilmirəm get final stress.
- ov and öv stay [ov] and [œv] instead of the diphthongs [ou̯] and [œy̯].
- k is always palatal [c], also next to back vowels and in Russian loans (Bakı gives [bacɯ]).
- /ɾ/ is a trill except between vowels, and a schwa is inserted before word-final r after a consonant.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 15 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɯ (Y=s1: f1=83 f2=89 f3=114 dur=137), ɾ (l=s3: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), a (A=s6: dur=175), i (i=s8: dur=85), o (o=s7: dur=80), u (u=s9: dur=86), t (t=s12: f2=91 burst=-4), r (l=s11: tap=3 tapms=18 f2=109 f3=77), ɫ (l=s16: f2=71 f3=91), h (<h=s17: ms=70 whisper=44), d (d=s12: f2=91 burst=-4), ɟ (d=s25: f2=135 f3=112 a3=56 a4=56), y (y=s8: dur=85), æ (E=s49: f1=124 f2=92 f3=92 dur=126), œ (OE=s38: dur=126).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (nə, kim, harada, haraya ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Ghaffarvand Mokari, Payam & Werner, Stefan (2017). Azerbaijani. Journal of the International Phonetic Association 47(2), 207-212. Ghaffarvand Mokari, Payam & Werner, Stefan (2016). An acoustic description of spectral and temporal characteristics of Azerbaijani vowels. Poznań Studies in Contemporary Linguistics 52(3), 503-518. Schönig, Claus (1998). Azerbaijanian. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge. Householder, Fred W. & Lotfi, Mansour (1965). Basic Course in Azerbaijani. Indiana University.

## Bashkir (`ba`)

Turkic, Kipchak (Volga Kipchak). Described: Literary Bashkir (based on the Kuvakan and Yurmaty dialects), Cyrillic script.

**What the language has.** Full vowels /i y u æ ɑ/ versus reduced (short, centralised) mid vowels /ĕ ø̆ ŏ ɯ̆/, spelt е/э, ө, о, ы. Interdental fricatives /θ ð/ (spelt ҫ, ҙ) versus alveolar /s z/. Velar /k ɡ/ versus uvular /q ʁ/, written with separate letters (к г versus ҡ ғ). /h/ (spelt һ) as a frequent native phoneme, corresponding to /s/ of other Turkic languages. Front versus back and rounded versus unrounded vowels.

Stress: fixed final by default, with morphological and lexical exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no stress rule is set for ba, so the default penultimate stress applies (бала, китап, башҡорт are stressed on the first syllable); Bashkir stress is final.
- the Cyrillic letter classes are not set up for ba, so rules with a vowel or consonant context never match: у and ү after a vowel stay full vowels (тау gives two syllables instead of [tɑw]).
- г next to front vowels becomes the velar fricative [ɣ] instead of the stop [ɡ].
- ь and ъ are always read as a glottal stop.
- Russian loanwords are read by the native rules (в is always [w], stress is not Russian).
- unstressable suffixes, imperatives and question words are not handled.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 10 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s9: tap=3 tapms=18 f2=109 f3=77), e (e=s6: dur=80), i (i=s7: dur=85), u (u=s8: dur=86), ɫ (l=s13: f2=71 f3=91), h (<h=s14: ms=70 whisper=44), ð (v=s26: f2=149 f3=110 a6=28 ab=48), ɣ (r=s33: f1=73 f3=116), ɯ (Y=s37: f1=83 f2=89 f3=114 dur=137), ɑ (A=s39: f1=91 f2=86 dur=175).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (нимә, ни, кем, ҡайҙа ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Poppe, Nicholas (1964). Bashkir Manual. Indiana University. Berta, Árpád (1998). Tatar and Bashkir. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge.

## Belarusian (`be`)

Indo-European, Balto-Slavic, Slavic, East Slavic. Described: Standard Belarusian (literary norm based on the central dialects around Minsk).

**What the language has.** Palatalised versus non-palatalised consonants for labials, dentals, velars, /n/ and /l/. The soft partners of /t d/ are the affricates /t͡sʲ d͡zʲ/ (tsekanne and dzekanne: дзень, цень). /r/, /t͡ʂ d͡ʐ/ and /ʂ ʐ/ are always hard (рака, рэчка, чысты). Fricative /ɣ/ is the regular reflex of г; the stop /ɡ/ occurs in few words (ганак, гузік). Long (geminate) consonants between vowels, mostly soft (калоссе [kaˈɫɔsʲːɛ], жыццё [ʐɨˈt͡sʲːɔ], ноччу). Position of stress is lexically contrastive.

Stress: free (lexical), mobile. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Stress: there is no stress dictionary. The letters о and ё are given primary stress by rule (correct for Belarusian spelling); every word without them is stressed on the first syllable, which is often wrong (вада, галава, зямля, вясна, сястра, рака all have final stress).
- Soft consonants other than sʲ, zʲ, t͡sʲ, d͡zʲ are coded as the hard consonant plus a phoneme [;] that has no sound data in the Belarusian table: there is no palatal transition into the following vowel (in нёс the vowel starts with the same formants as in нос) and almost no difference word-finally (конь, соль, быль).
- No fronted vowel allophones after soft consonants.
- Voicing assimilation and final devoicing are letter rules that look only inside the word; nothing is assimilated between a preposition and the next word.
- Long consonants are coded only for цц, чч, шш; other geminates are two separate consonants (калоссе [sʲsʲ]).
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s9: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), i (i=s7: dur=85), u (u=s8: dur=86), t (t=s10: vot=17), p (p=s11: vot=13), k (k=s12: vot=28), b (b=s21: voi=1 lead=75), d (d=s21: voi=1 lead=75), ɡ (g=s21: voi=1 lead=75), ʐ (Z=s34: a4=51 f2=92 f3=87 f4=88), ʂ (S=s35: a4=54 f2=87 f3=83 f4=88), zʲ (z=s36: f2=129 f3=108), sʲ (s=s36: f2=129 f3=108), ɣ (r=s40: f1=73 f3=116), ɛ (E=s43: dur=126), ɔ (O=s44: dur=150), ɨ (Y=s54: f1=78 f2=106 f3=114 dur=137), d͡z (d=s55 z=s56: voi=1 lead=75 hold=85; hold=70), ʈ͡ʂ (t=s60 S=s61: f2=87 f3=83 f4=88 a4=52 a5=42 hold=85; a4=54 f2=87 f3=83 f4=88 hold=70), ɖ͡ʐ (d=s62 Z=s63: f2=92 f3=87 f4=88 a4=52 a5=42 voi=1 lead=75 hold=85; a4=51 f2=92 f3=87 f4=88 hold=70).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (хто, што, дзе, калі ...) ends as a statement does, from a high question word.

Sources: Bird, Sonya & Litvin, Natallia (2021). Belarusian. Journal of the International Phonetic Association 51(3). Mayo, Peter (1993). Belorussian. In B. Comrie & G. G. Corbett (eds.), The Slavonic Languages. London: Routledge. Padlužny, A. I. (1989). Fanetyka belaruskaj litaraturnaj movy. Minsk: Navuka i tèchnika. Czekman, Walery & Smułkowa, Elżbieta (1988). Fonetyka i fonologia języka białoruskiego z elementami fonetyki i fonologii ogólnej. Warszawa: PWN. Vyhonnaja, L. C. (1991). Intanacyja. Nacisk. Arfaepija. Minsk: Navuka i tèchnika.

## Bulgarian (`bg`)

Indo-European, Balto-Slavic, Slavic, South Slavic (eastern group). Described: Standard Bulgarian (literary norm based on the north-eastern dialects, as spoken in Sofia).

**What the language has.** Six vowels, including the mid back unrounded (or central) /ɤ/ written ъ (сън [sɤn] 'dream' vs син [sin] 'son'). Palatalised versus plain consonants, only before the back vowels /a ɤ ɔ u/ (бял [bʲaɫ], лято, коня); there is no contrast before front vowels, before consonants or word-finally. The soft consonants are also analysed as consonant plus /j/. Voiced versus voiceless obstruents (neutralised word-finally and in clusters). Affricates /t͡s d͡z t͡ʃ d͡ʒ/. Position of stress is lexically and grammatically contrastive (вълна: [ˈvɤɫnɐ] 'wool' vs [vɐɫˈna] 'wave'; ходи: [ˈxɔdi] 'walks' vs [xoˈdi] 'walked').

Stress: free (lexical), mobile. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- Stress is lexical, but eSpeak has only suffix rules and a list of about 2,800 words (bg_listx); other words get penultimate stress, so common words with final stress are wrong (вода, жена, планина, добре, момче, голям) and some with initial stress too (ябълка).
- Vowel reduction depends on the stress, so every stress error also gives the wrong vowel qualities.
- Stressed endings written а, я but pronounced [ɤ] (чета, вървя, четат, благодаря, the short article in мъжа, града) are read with [a] and without final stress.
- Soft labials, к and р are coded as consonant plus a palatal glide phoneme; only soft д, т, н, з, с, г have their own phonemes.
- Word-final и is lengthened to [iː] (бели, големи, български); Bulgarian has no long vowels.
- Voicing assimilation is not applied across word boundaries except for the one-letter prepositions that are joined to the next word (от брата keeps [t]).
- България is stressed on the last but one vowel ([bɐɫɡaˈria]) instead of [bɐɫˈɡarijɐ].
- Only the default eSpeak tunes are used: wh-questions get the same fall-rise as yes-no questions, and ли-questions have no peak on the focused word.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), r (l=s9: tap=3 tapms=18 f2=109 f3=77), ɐ (A=s10: f1=85 dur=175), e (e=s6: dur=80), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s11: vot=17), p (p=s12: vot=13), k (k=s13: vot=28), ɫ (l=s17: f2=71 f3=91), b (b=s22: voi=1 lead=75), d (d=s22: voi=1 lead=75), ɡ (g=s22: voi=1 lead=75), tʲ (t=s48: f2=129 f3=108 vot=25), ɹ (r=s53: f2=92 f3=77), ʊ (U=s56: dur=185), ʌ (OE=s59: f1=112 f2=87 f3=114 dur=126).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (кой, коя, кое, кои ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Ternes, Elmar & Vladimirova-Buhtz, Tatjana (1999). Bulgarian. In Handbook of the International Phonetic Association, 55-57. Cambridge University Press. Scatton, Ernest A. (1984). A Reference Grammar of Modern Bulgarian. Columbus, OH: Slavica. Scatton, Ernest A. (1993). Bulgarian. In B. Comrie & G. G. Corbett (eds.), The Slavonic Languages. London: Routledge. Tilkov, Dimităr & Bojadžiev, Todor (1981). Bălgarska fonetika. Sofia: Nauka i izkustvo. Pettersson, Thore & Wood, Sidney (1987). Vowel reduction in Bulgarian and its implications for theories of vowel production: a review of the problem. Folia Linguistica 21. Wood, Sidney & Pettersson, Thore (1988). Vowel reduction in Bulgarian: the phonetic data and model experiments. Folia Linguistica 22. And 2 more in the profile.

## Bengali (`bn`)

Indo-European, Indo-Iranian, Indo-Aryan (Eastern zone, Bengali-Assamese). Described: Standard Colloquial Bengali; the inventory covers both the Kolkata and the Dhaka standard, the formant, duration, VOT and intonation figures come from Bangladeshi Standard (Dhaka) speakers.

**What the language has.** Four-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced. Dental versus postalveolar ('retroflex') stops. Seven vowel qualities with /e/ : /æ/ and /o/ : /ɔ/, contrastive mainly in the first syllable. Oral versus nasal vowels in the Kolkata standard (/kãʈa/ 'thorn' : /kaʈa/ 'to cut'); weak or absent in Bangladeshi Standard. Consonant gemination within morphemes (/d̪oʃi/ 'guilty' : /d̪oʃːi/ 'rogue'). No vowel length contrast. /ɾ/ versus /ɽ/ in the Kolkata standard; one rhotic in most Bangladeshi speech. /ʃ/ versus /s/, marginal in Kolkata, regular in Dhaka (/bas/ 'enough' : /baʃ/ 'bamboo').

Stress: fixed initial, weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Breathy voiced stops come from the Hindi base table: modal voiced closure plus a voiceless aspiration sample, no breathy vowel onset. /ɦ/ is voiceless [h].
- The final inherent vowel is often wrong in both directions: ভাত [bʰato], হয় [hɔjo] with an extra vowel, ছোট [tʃʰoʈ], বড় [bɔɽ] without the needed final [o].
- The letter এ is always [e]: এক [ek], দেখা [dekʰa] for [æk], [d̪ækʰa].
- Conjuncts are read letter by letter: বিশ্ব [biʃbɔ], পদ্ম [pɔdmɔ], আত্মা [atma], ক্ষতি [kʰkʰoti], লক্ষ্মী [lokʰkʰmi], জ্ঞান [ɡɡan].
- One phoneme /dʒ/ has two sounds: জ is the palatal stop phoneme [ɟ], য is [dʒ].
- ঢ় is produced as [h] followed by the retroflex flap (আষাঢ় [aʃahɽɔ]); the flap has no IPA name and prints as 'r.'.
- /ʃ/ stays [ʃ] before dentals and /r/ in স্নান [ʃnan], শ্রী [ʃɾi].
- Raising of the inherent vowel to [o] is applied only in the first syllable.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 16 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: tʰ (t=s4: vot=57 asp=50), a (a=s5: f1=84), e (e=s6: f1=110), i (i=s7: f1=133 dur=114), o (o=s8: f2=114), u (u=s9: f1=127 f2=128 f3=109 dur=114), k (k=s10: vot=34), h (<h=s14: ms=70 whisper=44), b (b=s17: voi=1 lead=75), d (d=s17: voi=1 lead=75), ɡ (g=s17: voi=1 lead=75), ɔ (c=s8: f2=114), bʰ (b=s59: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s59: voi=1 lead=75 brth=90 f0=-15), ʈ (t=s60: f3=77 f4=88 a4=52 a5=42), tʃʰ (C >h=s68: ms=45 whisper=46).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (কী, কে, কোথায়, কখন ...) ends as a statement does, from a high question word.

Sources: Khan, Sameer ud Dowla (2010). Bengali (Bangladeshi Standard). Journal of the International Phonetic Association 40(2), 221-225. Ferguson, Charles A. & Chowdhury, Munier (1960). The phonemes of Bengali. Language 36, 22-59. Dasgupta, Probal (2003). Bangla. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Chatterji, Suniti Kumar (1921). Bengali phonetics. Bulletin of the School of Oriental Studies 2, 1-25. Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. Hayes, Bruce & Lahiri, Aditi (1991). Bengali intonational phonology. Natural Language & Linguistic Theory 9, 47-96. And 6 more in the profile.

## Bishnupriya Manipuri (`bpy`)

Indo-European, Indo-Iranian, Indo-Aryan (Eastern zone, Bengali-Assamese), with a large Meitei (Tibeto-Burman) loan layer. Described: Bishnupriya Manipuri as spoken in the Barak Valley of Assam, Tripura and Sylhet; the two dialects Rajar Gang and Madai Gang are not distinguished here. Provisional description: no instrumental phonetic study is known to me.

**What the language has.** Aspirated versus unaspirated stops, voiced and voiceless (kʰ, tʰ, ɡʱ are attested in published transcriptions). The inherent vowel of the script is /ɔ/ as in Bengali and Assamese, not a schwa. The letters for the old palatal stops are fricatives: চ is [s], ছ is [ʃ] in published transcriptions (/sakɔɹ/ 'servant', /maʃ/ 'fish'); জ is the affricate [dʒ]. Back rounded vowels /ɔ/ : /ʊ/ : /u/ (ও is transcribed [ʊ]: /mʊɹ/ 'my'). No vowel length contrast is reported. Velar nasal /ŋ/ occurs word-finally and before consonants (/ɡaŋ/ 'village').

Stress: not described; presumably weak and non-contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The rule file is headed 'Pronunciation rule for Manipuri' and the translator source calls the language 'not indo-european': the rules appear to have been written with Meitei in mind, not the Indo-Aryan Bishnupriya language.
- The inherent vowel comes out as a schwa in many words (ঘর [ɡhəɾ], মণি [məni], জল [ɟəl]) where the published transcriptions have [ɔ] ([ɡʰɔɹ], [mɔni]); in other words it is [ɔ], and the choice differs from letter to letter.
- Aspirates are sequences of stop plus a separate [h] phoneme (gh, bh, dh, t.h, ch), not single aspirated or breathy stops.
- চ is the palatal stop [c] and ছ is [c] plus [h] (মাছ [machɔ]); the transcriptions have [s] and [ʃ].
- Extra final vowels: ধান [dhanɔ], মাছ [machɔ], এক [ekə], শেষ [ʃeʃə].
- A schwa is inserted in clusters at morpheme boundaries: করলু [kɔɾəlu] for [kɔɹlu].
- ঙ is [ŋɡ] (গাঙ [ɡaŋɡ]); ও is [o] where the transcriptions have [ʊ]; র is a tap.
- Intonation uses the generic eSpeak tunes.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 33 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), tʰ (t=s5: vot=70 asp=50), a (A=s6: dur=175), e (e=s7: dur=80), i (i=s8: dur=85), o (o=s7: dur=80), u (u=s9: dur=86), t (t=s11: vot=17), p (p=s12: vot=13), k (k=s13: vot=28), h (<h=s18: ms=70 whisper=44), ɳ (n=s19: f3=80), r. (l=s21: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s22: voi=1 lead=75), d (d=s22: voi=1 lead=75), ɟ (d=s29: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s22: voi=1 lead=75), iː (i=s44: dur=117), ɪ (I=s45: dur=137), aː (a=s48: dur=72), ɔ (O=s50: dur=150), ɔ̃ (O=s58: dur=150 nas=100), bʰ (b=s64: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s64: voi=1 lead=75 brth=90 f0=-15), ʈ (t=s65: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s66: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75), ɟʰ (d=s70: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75 brth=90 f0=-15), kʰ (k=s71: vot=85 asp=50), ɡʰ (g=s64: voi=1 lead=75 brth=90 f0=-15).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Sinha, Kali Prasad (1981). The Bishnupriya Manipuri Language. Calcutta: Firma KLM. Kalita, Nayan Jyoti; Saharia, Navanath & Sinha, Smriti Kumar (2013). Towards the development of a Bishnupriya Manipuri corpus. arXiv:1312.3251 (word forms with IPA transcription). Kalita, Nayan Jyoti; Saharia, Navanath & Sinha, Smriti Kumar (2014). Morphological analysis of the Bishnupriya Manipuri language using finite state transducers. In Computational Linguistics and Intelligent Text Processing, Lecture Notes in Computer Science 8403, 206-213 (word forms with IPA transcription). Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. Khan, Sameer ud Dowla (2016). The intonation of South Asian languages: towards a comparative analysis. Proceedings of Formal Approaches to South Asian Languages 6, 23-36 (areal intonation pattern only).

## Bosnian (`bs`)

Indo-European, Balto-Slavic, Slavic, South Slavic (western group, Serbo-Croatian). Described: Standard Bosnian (Neo-Štokavian Ijekavian norm as used in Sarajevo). Speakers in Bosnia and Herzegovina generally keep the four pitch accents and much of the post-accentual length.

**What the language has.** Four word accents: short falling (kȕća), long falling (mȃjka), short rising (vòda), long rising (rúka). Vowel length under the accent and in syllables after the accent. Postalveolar /t͡ʃ d͡ʒ/ (č, dž) versus alveolo-palatal /t͡ɕ d͡ʑ/ (ć, đ); the norm keeps them apart, many speakers in Bosnia merge them. Palatal /ʎ ɲ/ versus /l n/. /x/ is a stable phoneme and is kept in more words than in the Serbian and Croatian norms (lahko, mehko, kahva). Syllabic /r̩/, short or long, as a syllable nucleus that can carry the accent (krv, prst). Voiced versus voiceless obstruents, kept word-finally.

Stress: free (lexical) pitch accent, restricted by position. Rhythm: mixed. Tone: pitch accent, 4 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- There is no Bosnian pronunciation of its own: the voice uses the Croatian phoneme table (phonemes hr) and the shared rule file; the conditional entries ?3 and ?4 change only the names of some symbols and numbers.
- No pitch accent: the four accents are not distinguished and accent marks in the text are ignored, except that acute-marked vowels are read as long.
- No vowel length apart from a handful of words.
- Stress is always on the first syllable, which is wrong for words with a rising accent on a later syllable (ljepòta, telèvīzija).
- Syllabic r between consonants is a plain consonant and not a syllable nucleus: krv, prst, trg, smrt have no stressed syllable, and prvi, crkva, brzo are stressed on the last vowel.
- Unstressed /a i u/ are replaced by reduced qualities (& [æ]-like, [ɪ], [ʊ]); the standard has no vowel reduction.
- The long jat reflex ije is read as two syllables [i.je] (mlijeko, lijep).
- h is [x] at the start of a word and [h] elsewhere; Bosnian keeps a velar fricative in all positions.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 14 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=51), e (e=s5: dur=55), i (i=s6: dur=63), o (o=s7: dur=53), u (u=s8: dur=61), b (b=s16: voi=1 lead=75), d (d=s16: voi=1 lead=75), dʑ (d=s17 Z=s18: voi=1 lead=75 hold=85 f2=126 f3=122; a3=34 a4=55 a5=22 f2=126 f3=122 hold=70), tɕ (t=s19 S=s20: hold=85 f2=126 f3=122; a2=31 a3=34 a4=34 a5=22 f2=126 f3=122 hold=70), ɡ (g=s16: voi=1 lead=75), x (S=s32: f2=77 f3=107 a2=68 a3=0 a4=52 af=-4), ɛ (E=s5: dur=55), æ (a=s42: f1=85 f2=116 dur=51), ɪ (e=s55: f1=91 dur=55).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (ko, tko, šta, što ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

**Not yet.** The four accents are not in eSpeak NG's reading: stress is spoken, the rising and falling accents are not.

Sources: Jahić, Dževad; Halilović, Senahid & Palić, Ismail (2000). Gramatika bosanskoga jezika. Zenica: Dom štampe. Riđanović, Midhat (2012). Bosnian for Foreigners: With a Comprehensive Grammar. Sarajevo: Rabic. Lehiste, Ilse & Ivić, Pavle (1986). Word and Sentence Prosody in Serbocroatian. Cambridge, MA: MIT Press. Inkelas, Sharon & Zec, Draga (1988). Serbo-Croatian pitch accent: the interaction of tone, stress, and intonation. Language 64, 227-248. Godjevac, Svetlana (2005). Transcribing Serbo-Croatian intonation. In Sun-Ah Jun (ed.), Prosodic Typology: The Phonology of Intonation and Phrasing. Oxford University Press. Browne, Wayles (1993). Serbo-Croat. In B. Comrie & G. G. Corbett (eds.), The Slavonic Languages. London: Routledge. And 1 more in the profile.

## Catalan (`ca`)

Indo-European, Romance, Western Romance, Occitano-Romance. Described: Central Catalan (Eastern dialect group), educated speech of the Barcelona area, the basis of the standard of Catalonia.

**What the language has.** Seven vowels under stress /i e ɛ a ɔ o u/ against three in unstressed syllables [i ə u]. Close-mid versus open-mid vowels: déu [dew] 'god' versus deu [dɛw] 'ten', dóna [ˈdonə] 'gives' versus dona [ˈdɔnə] 'woman', ós [os] versus os [ɔs]. Tap /ɾ/ versus trill /r/ between vowels (cera versus serra). /s/ versus /z/ and /ʃ/ versus /ʒ/ between vowels; affricates /tʃ dʒ/ and marginal /ts dz/. /l/ versus /ʎ/ and /n/ versus /ɲ/, also word-finally (any, ull). No /v/: written v and b are one phoneme /b/. Obstruent voicing is neutralised at the end of a word. Geminates in a few words and clusters (il·lusió [ll], setmana [mm], espatlla [ʎʎ], poble [bbl]).

Stress: lexical, on one of the last three syllables. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- no tune set is selected in the voice file, so the generic default tunes are used; the low nuclear accent of statements and the two yes-no question patterns (rising, and falling after 'que') are not modelled.
- /l/ imports the English phoneme: clear before a vowel, dark only in the coda; Central Catalan /l/ is velarised in all positions.
- isolated rule errors in common words: rei is [rˈei] with two vowels and reina is [ɾəˈinə] with an initial tap and stress on the i, against [rej] and [ˈrejnə].
- a full trill is used in every coda (porta [pˈɔrtə], parlar [pərlˈa]) where the usual realisation is a tap or a short trill.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (a=s1: f1=76), u (u=s4: dur=114), b (b=s10: voi=1 lead=75), d (d=s10: voi=1 lead=75), c (t=s16: f2=148 f3=109 a3=56 a4=56 vot=32), ɡ (g=s10: voi=1 lead=75), ɛ (e=s26: f1=116), ɔ (o=s26: f1=116).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (què, qui, quan, on ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

Sources: Carbonell, Joan F. and Llisterri, Joaquim (1992). Catalan. Journal of the International Phonetic Association 22(1-2), 53-56. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Wheeler, Max W. (2005). The Phonology of Catalan. Oxford University Press. Hualde, José Ignacio (1992). Catalan. London: Routledge (Descriptive Grammars). Recasens, Daniel (1996). Fonètica descriptiva del català. 2nd edition. Barcelona: Institut d'Estudis Catalans. Recasens, Daniel and Espinosa, Aina (2006). Dispersion and variability of Catalan vowels. Speech Communication 48, 645-666. Veny, Joan (1982). Els parlars catalans: síntesi de dialectologia. Palma: Moll. And 5 more in the profile.

## Catalan (Balearic) (`ca-ba`)

Indo-European, Romance, Western Romance, Occitano-Romance. Described: Balearic Catalan (Eastern dialect group), described from Majorcan; Minorcan and Ibizan differ mainly in the treatment of unstressed o.

**What the language has.** Eight vowels under stress: /i e ɛ a ɔ o u/ plus stressed /ə/, which continues the close e of early Romance (set [sət] 'thirst' versus set [sɛt] 'seven'; pera [ˈpəɾə], ceba [ˈsəβə], cadena [kəˈðənə]). Four vowels in unstressed syllables in most of Majorca [i ə o u]; three [i ə u] in Minorca, Ibiza and the Sóller area. /v/ is kept distinct from /b/ (vi [vi] versus bé [be]). Tap /ɾ/ versus trill /r/ between vowels. /s/ versus /z/, /ʃ/ versus /ʒ/, affricates /tʃ dʒ ts dz/. /l/ versus /ʎ/ and /n/ versus /ɲ/. Obstruent voicing is neutralised at the end of a word. Lexical stress.

Stress: lexical, on one of the last three syllables. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the change of ʎ to [j] is applied to every ʎ after a vowel, also to the lateral from Latin LL, which Majorcan keeps: cavall is [kəvˈaj], aquell [əkˈəj], allà [əjˈa], bella [bˈejə], ella [ˈeə].
- no palatal stops [c ɟ]: qui, guerra, sac, amic have velar [k ɡ].
- stressed [ə] depends on a word list and spelling rules and misses common words (ceba, cera, negre keep [ɛ]), while every written 'è' becomes [ə], also in learned and borrowed words where Majorcan has [ɛ] (cafè [kəfˈə], ciència [siˈənsiə], València [vəlˈənsiə]).
- unstressed o is never raised before a stressed high vowel (conill [konˈij], cosí [kozˈi], comú [komˈu]), and there is no setting for the Minorcan and Ibizan reduction of every unstressed o to [u].
- final -ia keeps its vowel (història [istˈɔɾiə]).
- pes comes out as [pˈədz].
- /l/ imports the English phoneme, dark only in the coda, although Majorcan has the darkest l of all Catalan dialects in all positions.
- no tune set is selected, so the generic default tunes are used; the falling yes-no question is not modelled.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 9 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (a=s1: f1=76), u (u=s4: dur=114), b (b=s10: voi=1 lead=75), d (d=s10: voi=1 lead=75), c (t=s16: f2=148 f3=109 a3=56 a4=56 vot=32), ɡ (g=s10: voi=1 lead=75), ɛ (e=s26: f1=116), ɔ (o=s26: f1=116), ts (t=s38 s=s39: hold=85; hold=70).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (què, qui, quan, on ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

Sources: Carbonell, Joan F. and Llisterri, Joaquim (1992). Catalan. Journal of the International Phonetic Association 22(1-2), 53-56. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Wheeler, Max W. (2005). The Phonology of Catalan. Oxford University Press. Recasens, Daniel (1996). Fonètica descriptiva del català. 2nd edition. Barcelona: Institut d'Estudis Catalans. Veny, Joan (1982). Els parlars catalans: síntesi de dialectologia. Palma: Moll. Bibiloni, Gabriel (2016). El català de Mallorca: la fonètica. Palma: Lleonard Muntaner. Recasens, Daniel and Espinosa, Aina (2005). Articulatory, positional and coarticulatory characteristics for clear /l/ and dark /l/: evidence from two Catalan dialects. Journal of the International Phonetic Association 35(1), 1-25. And 4 more in the profile.

## Catalan (North-western) (`ca-nw`)

Indo-European, Romance, Western Romance, Occitano-Romance. Described: North-western Catalan (Western dialect group), described from the speech of Lleida and the surrounding plain.

**What the language has.** Seven vowels under stress /i e ɛ a ɔ o u/ and five in unstressed syllables [i e a o u]; there is no schwa and no reduction of a, e to [ə] or of o to [u]. Close-mid versus open-mid vowels under stress; many words with Central [ɛ] have Western [e] (cadena [kaˈðenɛ], francès [fɾanˈses], ceba [ˈseβɛ]). Tap /ɾ/ versus trill /r/ between vowels. /s/ versus /z/ between vowels; affricates /tʃ dʒ/ where Central Catalan has initial fricatives. /l/ versus /ʎ/ and /n/ versus /ɲ/. No /v/: written v and b are one phoneme /b/. Obstruent voicing is neutralised at the end of a word. Lexical stress; because unstressed vowels keep their quality, pairs such as the first and third person of verbs differ by their final vowel (canto [ˈkanto], canta [ˈkante]).

Stress: lexical, on one of the last three syllables. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no tune set is selected, so the generic default tunes are used.
- final unstressed a is [ɛ] in every word (the Lleida pattern), also in third person verb forms where [e] is general (dóna [dˈonɛ]).
- gemination is inconsistent with the dialect: regla is [rˈeɡɡlɛ] with a geminate while poble is [pˈɔβle] without.
- a full trill is used in every coda (porta [pˈɔrtɛ], parlar [parlˈa]) where the usual realisation is a tap.
- /l/ imports the English phoneme: clear before a vowel, dark only in the coda.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 7 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: u (u=s4: dur=114), b (b=s10: voi=1 lead=75), d (d=s10: voi=1 lead=75), c (t=s16: f2=148 f3=109 a3=56 a4=56 vot=32), ɡ (g=s10: voi=1 lead=75), ɛ (e=s26: f1=116), ɔ (o=s26: f1=116).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (què, qui, quan, on ...) ends as a statement does, from a high question word.

Sources: Carbonell, Joan F. and Llisterri, Joaquim (1992). Catalan. Journal of the International Phonetic Association 22(1-2), 53-56. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Wheeler, Max W. (2005). The Phonology of Catalan. Oxford University Press. Recasens, Daniel (1996). Fonètica descriptiva del català. 2nd edition. Barcelona: Institut d'Estudis Catalans. Veny, Joan (1982). Els parlars catalans: síntesi de dialectologia. Palma: Moll. Recasens, Daniel and Espinosa, Aina (2006). Dispersion and variability of Catalan vowels. Speech Communication 48, 645-666. Institut d'Estudis Catalans (2016). Gramàtica de la llengua catalana. Barcelona: IEC. And 1 more in the profile.

## Catalan (Valencian) (`ca-va`)

Indo-European, Romance, Western Romance, Occitano-Romance. Described: Valencian (Western dialect group): general Valencian as codified by the Acadèmia Valenciana de la Llengua, with notes on the central (apitxat) and southern areas.

**What the language has.** Seven vowels under stress /i e ɛ a ɔ o u/ and five in unstressed syllables [i e a o u]; there is no schwa and no reduction of a, e to [ə] or of o to [u]. Close-mid versus open-mid vowels under stress, with very open /ɛ ɔ/; many words with Central [ɛ] have [e] (cadena [kaˈðena], francés [fɾanˈses]). /v/ is distinct from /b/ in general Valencian (merged in the central apitxat area). Voiced affricate /dʒ/ for written j and g before e, i in all positions (roja [ˈrɔdʒa], gent [dʒent]); there is no phoneme /ʒ/. Tap /ɾ/ versus trill /r/ between vowels. /s/ versus /z/ between vowels (devoiced in the apitxat area). /l/ versus /ʎ/ and /n/ versus /ɲ/. Obstruent voicing is neutralised at the end of a word.

Stress: lexical, on one of the last three syllables. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no tune set is selected, so the generic default tunes are used.
- initial unstressed e before s, n, m is always lowered to [a] (escola [askˈɔla], estar [astˈaɾ], entendre [antˈendɾe]), which is the colloquial variant; careful speech has [e].
- /l/ is inherited from the Central table (English phoneme with dark coda l), although Valencian /l/ is the clearest of the Catalan dialects.
- què and perquè are given close [e] ([kˈe], [peɾkˈe]); Valencian keeps open [ɛ] in these words, which is why they are written with a grave accent also in Valencian spelling.
- no option for the regional features: vowel harmony of final -a, loss of d in -ada, or the devoicing and b/v merger of the apitxat area.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 7 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: u (u=s4: dur=114), b (b=s10: voi=1 lead=75), d (d=s10: voi=1 lead=75), c (t=s16: f2=148 f3=109 a3=56 a4=56 vot=32), ɡ (g=s10: voi=1 lead=75), ɛ (e=s26: f1=116), ɔ (o=s26: f1=116).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (què, qui, quan, on ...) ends as a statement does, from a high question word.

Sources: Carbonell, Joan F. and Llisterri, Joaquim (1992). Catalan. Journal of the International Phonetic Association 22(1-2), 53-56. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Wheeler, Max W. (2005). The Phonology of Catalan. Oxford University Press. Recasens, Daniel (1996). Fonètica descriptiva del català. 2nd edition. Barcelona: Institut d'Estudis Catalans. Veny, Joan (1982). Els parlars catalans: síntesi de dialectologia. Palma: Moll. Acadèmia Valenciana de la Llengua (2006). Gramàtica normativa valenciana. València: Acadèmia Valenciana de la Llengua. Saborit Vilar, Josep (2009). Millorem la pronúncia. València: Acadèmia Valenciana de la Llengua. And 4 more in the profile.

## Cherokee (`chr`)

Iroquoian, Southern Iroquoian. Described: Oklahoma (Western) Cherokee, as recorded in Feeling's Cherokee-English Dictionary (1975) and described by Montgomery-Anderson (2008) and Uchihara (2016); North Carolina Cherokee has a simpler tone system and keeps the glottal stop where Oklahoma has the lowfall tone.

**What the language has.** Six pitch patterns on the syllable: low, high, rising, falling, lowfall and superhigh. Short versus long vowels in six qualities; the sixth vowel, written v, is a nasalised central vowel. Unaspirated versus aspirated stops and affricates (written d, g, gw, j, dl versus t, k, kw, ch, tl in the usual romanisation). Glottal stop and h as consonants, also before and after other consonants. No labial stops or labial fricatives; m occurs in few native words. Lateral affricate tɬ.

Stress: none; tonal accent. Rhythm: mixed. Tone: lexical tone, 7 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- the Cherokee syllabary is not supported: the rules cover only romanised text in the style of the Cherokee-English Dictionary, and syllabary text is read as unknown letters.
- tone is spoken only if it is written with the superscript digits of the dictionary (¹ ² ³ ⁴ and their combinations); ordinary romanised text, which has no tone marks, gets no lexical tone at all, only the high fall on the last vowel.
- vowel length depends on the underdot of the dictionary for short vowels; in text without it every non-final vowel is long.
- long vowels are three times as long as short ones (300 against 100 units), against a ratio of about two in the literature.
- the vowel a uses the rounded back vowel of English 'lot' ([ɒ]) instead of a low central [a].
- g is voiced but has the burst of an aspirated k added to it, which blurs the contrast between plain g and aspirated k.
- tl, dl and hl are sequences with a voiced l; there is no lateral affricate or fricative.
- short vowels before h are not devoiced (noted as an open problem in the phoneme file).

**What OpenEVV says.** Spoken by the module made from US English (`enux`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʔ (<q=s3: ms=50 hush=1), e (I=s5: f1=106 f2=118 f3=112), i (i=s6: dur=74), o (U=s7: f2=71 f3=109), u (u=s8: dur=75), t (t=s11: vot=17), k (k=s13: vot=28), l (l=s10: f2=165 f3=92), h (<h=s16: ms=70 whisper=44), d (d=s20: voi=1 lead=75), ɡ (g=s20: voi=1 lead=75), ɒ (c=s51: f2=88 dur=58), ɒ̃ (c=s52: f2=88 dur=58 nas=100), ẽ (I=s53: f1=106 f2=118 f3=112 nas=100), ĩ (i=s54: dur=74 nas=100), õ (U=s55: f2=71 f3=109 nas=100), ũ (u=s56: dur=75 nas=100), ɐ̃ (H=s58: f1=116 f2=106 nas=100).

Tones: 2 (0:22,100:21), 3 (0:33,100:35), 23 (0:22,100:35), 32 (0:38,100:20), 1 (0:22,100:10), 4 (0:34,100:50), 43 (0:48,100:30). The pitch is made from them, syllable by syllable.
Timing: stressed 94 per cent, weak 106 per cent, last 88 per cent of the module's own.

**Not yet.** Tone is read only where the text marks it; the syllabary is read without tone.

Sources: Feeling, Durbin (1975). Cherokee-English Dictionary, edited by William Pulte. Tahlequah: Cherokee Nation of Oklahoma. Pulte, William & Feeling, Durbin (1975). Outline of Cherokee grammar. In Feeling (1975). Montgomery-Anderson, Brad (2008). A Reference Grammar of Oklahoma Cherokee. PhD dissertation, University of Kansas. Uchihara, Hiroto (2016). Tone and Accent in Oklahoma Cherokee. Oxford: Oxford University Press. Herrick, Dylan, Berardo, Marcellino, Feeling, Durbin, Hirata-Edds, Tracy & Peter, Lizette (2015). Collaborative documentation and revitalization of Cherokee tone. Language Documentation & Conservation 9, 12-31. Lindsey, Geoffrey (1985). Intonation and Interrogation: Tonal Structure and the Expression of a Pragmatic Function in English and Other Languages. PhD dissertation, University of California, Los Angeles. And 5 more in the profile.

## Chinese (Mandarin, latin as English) (`cmn`)

Sino-Tibetan, Sinitic, Mandarin. Described: Standard Chinese (Putonghua), Beijing-based pronunciation.

**What the language has.** Aspirated versus unaspirated in every stop and affricate (p pʰ, t tʰ, k kʰ, ts tsʰ, tʂ tʂʰ, tɕ tɕʰ); no voicing contrast in obstruents. Three sibilant places: dental (ts tsʰ s), retroflex (tʂ tʂʰ ʂ, with ɻ) and alveolo-palatal (tɕ tɕʰ ɕ). Four lexical tones plus a toneless (neutral) syllable type. Alveolar versus velar nasal coda (n, ŋ). Front rounded y against i and u. Plain versus rhotacised rhymes (erhua).

Stress: no contrastive word stress; full-toned (heavy) versus neutral-tone (light) syllables. Rhythm: syllable-timed. Tone: lexical tone, 5 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- no sentence intonation: tone languages are routed to CalcPitches_Tone() in src/libespeak-ng/intonation.c, which ignores the clause type; a statement and the same text ending in a question mark give byte-identical audio, and the declination variables are never set, so there is no declination, final lowering or focus.
- the tonal pitch range is very small: the tone table uses pitch values 9 to 55, which with the voice setting 'pitch 80 118' is about 75 to 99 Hz (under 5 semitones, measured on the output) where natural citation tones span most of an octave.
- third-tone sandhi is applied to every adjacent pair regardless of prosodic grouping, so a run of third tones is 35 35 ... 214 (小老虎 is 35 35 214 instead of 21 35 214; 我也很想买五把好雨伞 has nine rising tones in a row).
- the tone changes of 一 and 不 are not rules: they come from word-pair entries in the optional dictionary dictsource/extra/cmn_listx (about 1,800 entries beginning with 一 and 11,900 with 不); a pair that is not listed keeps the citation tone (一坨 and 一沓 come out with yi1), and without that file every 一 is yi1 and every 不 is bu4.
- erhua is not implemented and is broken for listed words: entries such as (花 儿) hua1r5 contain a syllable r5 that the rules cannot read, so 花儿, 这儿, 哪儿 and 一点儿 are spelled out in English.
- no tonal coarticulation: every syllable gets a fixed contour, and the voice attribute 'words 1' puts a short pause between words, so speech is staccato.
- inside a clause all full tones have the same length whatever the tone, so the half third is not shorter and tone 4 not shorter; only on the last syllable of a clause are tones 2 and 3 longer than tones 1 and 4 (about 290 against 235 ms measured).
- the neutral tone is shorter (150 against 230) and lower but keeps full vowel quality; many common neutral-tone words are said with full tones (东西, 朋友), and before a neutral tone from an underlying tone 3 the first syllable is always 21 (想想, 哪里).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 9 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: i (i=s6: f3=120), χ (x=s3: f2=88), ɑ (A=s48: f1=91 f2=86 dur=239), ɑu (a=s50: f1=89 f2=86 g1=53 g2=56 g3=112 glide=1 dur=72), ə (@=s1: dur=199), h (<h=s18: ms=70 whisper=44), ð (v=s33: f2=149 f3=110 a6=28 ab=48), əʊ (@=s75: g1=94 g2=65 g3=93 glide=1 dur=208), eə (j=s54 @=s1: hold=55; dur=199).

Tones: 55 (0:48,100:50), 35 (0:31,30:29,100:50), 214 (0:23,45:10,100:38), 21 (0:23,65:11,100:10), 51 (0:50,12:52,100:12), 53 (0:50,12:52,100:30), 11 (0:22,100:12), 22 (0:32,100:22), 33 (0:36,100:30), 44 (0:30,100:40). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Lee, Wai-Sum & Zee, Eric (2003). Standard Chinese (Beijing). Journal of the International Phonetic Association 33(1), 109-112. Duanmu, San (2007). The Phonology of Standard Chinese, 2nd edition. Oxford University Press. Chao, Yuen Ren (1968). A Grammar of Spoken Chinese. University of California Press. Chao, Yuen Ren (1930). A system of tone letters. Le Maître Phonétique. Lin, Yen-Hwei (2007). The Sounds of Chinese. Cambridge University Press. Xu, Yi (1997). Contextual tonal variations in Mandarin. Journal of Phonetics 25, 61-83. And 17 more in the profile.

## Chinese (Mandarin, latin as Pinyin) (`cmn-latn-pinyin`)

Sino-Tibetan, Sinitic, Mandarin. Described: Standard Chinese (Putonghua), Beijing-based pronunciation; the same spoken language and the same sounds as cmn, written in Hanyu Pinyin instead of Han characters.

**What the language has.** Aspirated versus unaspirated in every stop and affricate; Pinyin writes the unaspirated series b d g z zh j and the aspirated series p t k c ch q, and neither series is voiced. Three sibilant places: dental (z c s), retroflex (zh ch sh, with r) and alveolo-palatal (j q x). Four lexical tones plus a toneless (neutral) syllable type. Alveolar versus velar nasal coda (n, ng). Front rounded y (Pinyin ü, written u after j q x y) against i and u. Plain versus rhotacised rhymes (erhua, written with a final r).

Stress: no contrastive word stress; full-toned (heavy) versus neutral-tone (light) syllables. Rhythm: syllable-timed. Tone: lexical tone, 5 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- only Pinyin with tone digits is read reliably (ni3 hao3); standard Pinyin with tone marks is handled by replacing the accented vowel with vowel plus digit in place, which works only when the marked vowel is the last letter of the syllable (mā, nǐ) and fails otherwise (hǎo becomes ha3o, zhōngguó likewise) and the word is then spelled out in English.
- a syllable with no tone digit is read as an English word (ma is said as English), so the neutral tone must be written with the digit 5.
- ü with a tone digit is read as English (nü3, lü4); only the substitute spelling with v works (nv3, lv4).
- jiong, qiong and xiong are read as English because the final iong is missing from letter group L03 in cmn_rules.
- erhua spellings (hua1r5, huar1) are read as English.
- the tone changes of 一 and 不 are not applied to Pinyin input, because they exist only as Han-character word pairs in dictsource/extra/cmn_listx: yi1 ge4 and bu4 shi4 are spoken with their citation tones.
- third-tone sandhi is applied to every adjacent pair regardless of prosodic grouping (xiao3 lao3 hu3 is 35 35 214 instead of 21 35 214).
- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c ignores the clause type, and a question gives the same audio as a statement.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 4 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: i (i=s6: f3=120), χ (x=s3: f2=88), ɑ (A=s48: f1=91 f2=86 dur=239), ɑu (a=s50: f1=89 f2=86 g1=53 g2=56 g3=112 glide=1 dur=72).

Tones: 55 (0:48,100:50), 35 (0:31,30:29,100:50), 214 (0:23,45:10,100:38), 21 (0:23,65:11,100:10), 51 (0:50,12:52,100:12), 53 (0:50,12:52,100:30), 11 (0:22,100:12), 22 (0:32,100:22), 33 (0:36,100:30), 44 (0:30,100:40). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Lee, Wai-Sum & Zee, Eric (2003). Standard Chinese (Beijing). Journal of the International Phonetic Association 33(1), 109-112. Duanmu, San (2007). The Phonology of Standard Chinese, 2nd edition. Oxford University Press. Chao, Yuen Ren (1968). A Grammar of Spoken Chinese. University of California Press. Lin, Yen-Hwei (2007). The Sounds of Chinese. Cambridge University Press. Xu, Yi (1997). Contextual tonal variations in Mandarin. Journal of Phonetics 25, 61-83. Xu, Yi (1999). Effects of tone and focus on the formation and alignment of f0 contours. Journal of Phonetics 27, 55-105. And 14 more in the profile.

## Crimean Tatar (`crh`)

Turkic, Kipchak (West Kipchak, with strong Oghuz influence). Described: Standard Crimean Tatar, based on the Central (Orta yolaq) dialect; Latin script (Cyrillic also in use).

**What the language has.** Eight vowels: high versus non-high, front versus back, rounded versus unrounded. Voiced versus voiceless stops and affricates. Velar /k ɡ/ versus uvular /q/ and the fricatives /x ɣ/ (spelt h, ğ). High vowels are short and lax, non-high vowels are longer. No phonemic vowel length.

Stress: fixed final by default, with morphological exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- a palatal glide is put before every e and most i, which palatalises the preceding consonant in the Russian way (men gives [mʲen], ev gives [ʲef], kelmedi gives [cʲelmʲedɪ]); the descriptions of Crimean Tatar have no such palatalisation.
- word-final z, v and j are devoiced to [s f ʃ] by rule (qız gives [qɯs]); the standard language keeps final /z/ voiced.
- i after most consonants is a mid central vowel (F1 500, F2 1412 Hz) and ı is F1 448, F2 1280 Hz: both are mid rather than high, and the difference between them is small.
- ö is a mid central vowel with the same formant targets as schwa (525 and 1441 Hz).
- unstressable suffixes are covered only in part: the negative -ma/-me and the question particle are stressed (kelmedi gets final stress).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 24 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɯ (Y=s1: f1=83 f2=89 f3=114 dur=137), ɾ (l=s3: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), r (l=s10: tap=3 tapms=18 f2=109 f3=77), a (A=s6: dur=175), e (e=s7: dur=80), i (i=s8: dur=85), o (o=s7: dur=80), u (u=s9: dur=86), ɫ (l=s14: f2=71 f3=91), dʑ (d=s20 Z=s21: hold=85 f2=126 f3=121; a3=34 a4=55 a5=22 f2=126 f3=121 hold=70), tɕ (t=s22 S=s23: hold=85 f2=119 f3=116; a2=31 a3=34 a4=34 a5=22 f2=119 f3=116 hold=70), ɟ (d=s24: f2=135 f3=112 a3=56 a4=56), c (t=s24: f2=135 f3=112 a3=56 a4=56), ɣ (r=s34: f1=73 f3=116), q (k=s35: f2=68 f3=109 f1=118 burst=3), ɑ (A=s37: f1=91 f2=86 dur=175), ɛ (E=s38: dur=126), ɪ (I=s39: dur=137), iː (i=s40: dur=117), ø (oe=s7: dur=80), y (y=s8: dur=85), ɔ (O=s41: dur=150), dʲ (d=s42: f2=129 f3=108), tʲ (t=s42: f2=129 f3=108).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (ne, kim, qayda, qayerde ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Kavitskaya, Darya (2010). Crimean Tatar. Lincom Europa. McCollum, Adam G. & Kavitskaya, Darya (2018). Non-iterative vowel harmony in Crimean Tatar. Proceedings of the 35th West Coast Conference on Formal Linguistics, 259-268. Cascadilla Proceedings Project. Berta, Árpád (1998). West Kipchak languages. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge.

## Czech (`cs`)

Indo-European, Balto-Slavic, Slavic, West Slavic (Czech-Slovak). Described: Standard Czech as spoken in Bohemia (Prague); Moravian differences are noted where they matter.

**What the language has.** Phonemic vowel length in all five vowel qualities, independent of stress (dráha [ˈdraːɦa] 'track' vs drahá [ˈdraɦaː] 'dear', byt vs být). Plain trill /r/ versus raised fricative trill /r̝/ (ř), as in řeka, moře, tři. Palatal stops and nasal /c ɟ ɲ/ versus alveolar /t d n/. Voiced versus voiceless obstruents, including voiced glottal /ɦ/ paired with voiceless velar /x/. Syllabic /r̩ l̩/ as syllable nuclei (krk, vlk, prst, Plzeň), marginally syllabic m (sedm, osm).

Stress: fixed initial, weak. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- Words whose only syllable nucleus is a syllabic l are spelled out letter by letter (vlk, pln, plch); syllabic l works when the word also has a vowel (vlna, Plzeň, slza) and syllabic r always works (krk, prst).
- ř is voiceless only after p, t, k, f. It stays voiced word-finally (keř, lékař, tvář, věř), before a voiceless consonant (hořký, kuřte, mateřský) and after ch (chřipka), where Czech has [r̝̊].
- k is never voiced before a voiced obstruent (kdo, kde, kdy give [kd], leckdo [d͡zkd]) and h is not devoiced to [x] before a voiceless consonant (lehký [hk]).
- Final v is not devoiced (lev, krev end in [v]).
- Non-syllabic prepositions are not assimilated to the next word: v Praze keeps [v], s bratrem and s dětmi keep [s], k domu keeps [k], and z domu is devoiced to [s].
- Word-final obstruents stay voiced before a word beginning with a vowel or sonorant (dub roste with [b], nad oknem with [d]): this is the Moravian and Slovak pattern, not the Bohemian standard.
- No glottal stop before word-initial vowels.
- Stress is given the usual eSpeak marking (higher pitch and amplitude on the first syllable); the low stressed syllable with a post-stress rise is not modelled.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 20 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s16: ms=70 whisper=44), ɲ (n=s18: f2=136 f3=109), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɟ (d=s27: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s28: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s20: voi=1 lead=75), iː (i=s48: dur=117), aː (a=s50: dur=72), uː (u=s48: dur=117), oʊ (o=s53: g1=105 g2=129 g3=96 glide=1), r̝ (l=s57: tap=3 tapms=18 f2=109 f3=77 fric=46 a3=58 a4=54).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (kdo, co, kde, kdy ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Dankovičová, Jana (1999). Czech. In Handbook of the International Phonetic Association, 70-73. Cambridge University Press. Šimáčková, Šárka; Podlipský, Václav Jonáš & Chládková, Kateřina (2012). Czech spoken in Bohemia and Moravia. Journal of the International Phonetic Association 42(2), 225-232. Palková, Zdena (1994). Fonetika a fonologie češtiny. Praha: Karolinum. Skarnitzl, Radek; Šturm, Pavel & Volín, Jan (2016). Zvuková báze řečové komunikace: Fonetický a fonologický popis řeči. Praha: Karolinum. Skarnitzl, Radek & Volín, Jan (2012). Referenční hodnoty vokalických formantů pro mladé dospělé mluvčí standardní češtiny. Akustické listy 18. Podlipský, Václav Jonáš; Skarnitzl, Radek & Volín, Jan (2009). High front vowels in Czech: a contrast in quantity or quality? Proceedings of Interspeech 2009. And 3 more in the profile.

## Chuvash (`cv`)

Turkic, Oghur (Bulgar). Described: Literary Chuvash, based on the Anatri (lower) dialect, Cyrillic script.

**What the language has.** Full vowels /i y ɯ u e a/ versus the reduced vowels ӗ /ɘ̆/ (front) and ӑ /ə̆/ (back), which are very short and never attract stress when a full vowel is present. Single versus geminate obstruents between vowels: single ones are lenis and voiced, geminates are voiceless (the numerals have both forms: пилӗк and пиллӗк 'five', сакӑр and саккӑр 'eight'). No voicing contrast in native obstruents; /b d ɡ z ʐ f ts/ are phonemes only in Russian loans. Plain versus palatalised consonants, mostly predictable from the vowels but contrastive in some words and word-finally (spelt with ь). Front versus back vowels (vowel harmony).

Stress: weight-sensitive (full versus reduced vowels), unbounded. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- no stress rule is set for cv, so the default penultimate stress applies: ача and лаша are stressed on the first syllable and чӑваш on the reduced vowel; the Chuvash rule (last full vowel, else first syllable) is only hand-marked in the numerals of cv_list.
- single obstruents are never voiced between vowels or after sonorants (лаша gives [laʃa], кӗпе gives [kɵpɛ], сакӑр gives [sakɯr]).
- ӑ is the Turkish ɯ phoneme with full length (180) while the full vowel ы is a short schwa-like vowel (110): the durations of the reduced and the full vowel are the wrong way round.
- ӗ has a back rounded target (F2 about 1160 Hz), further back than ӑ (F2 about 1280 Hz), so the front-back contrast of the two reduced vowels is lost.
- the Turkish allophone rules are inherited: и, у, ӳ are lowered in final and closed syllables and э becomes [æ] before a final sonorant.
- consonants are not palatalised in front-vowel words; ь only adds a palatal glide; ҫ is the palatal fricative [ç] and ч is [tʃ].
- в is a fricative [v].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 13 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɯ (Y=s1: f1=83 f2=89 f3=114 dur=137), ʔ (<q=s5: ms=50 hush=1), a (A=s6: dur=175), e (e=s7: dur=80), o (o=s7: dur=80), u (u=s9: dur=86), r (l=s11: tap=3 tapms=18 f2=109 f3=77), ɛ (E=s38: dur=126), ɔ (O=s39: dur=150), ø (oe=s7: dur=80), ɪ (I=s48: dur=137), ɵ (Y=s50: f2=89 f3=107 dur=137).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (мӗн, кам, ӑҫта, хӑҫан ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Krueger, John R. (1961). Chuvash Manual. Indiana University. Clark, Larry (1998). Chuvash. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge. Dobrovolsky, Michael (1999). The phonetics of Chuvash stress: implications for phonology. Proceedings of the 14th International Congress of Phonetic Sciences, San Francisco, 539-542.

## Welsh (`cy`)

Indo-European, Celtic, Brittonic. Described: Northern Welsh (Gwynedd and Anglesey), the variety of the JIPA illustration (Bell et al. 2023); southern differences are noted.

**What the language has.** Voiceless lateral fricative /ɬ/ (written ll) against /l/. Voiceless trill /r̥/ (written rh) against voiced /r/. Voiceless nasals /m̥ n̥ ŋ̊/ (written mh, nh, ngh), which arise by nasal mutation of /p t k/. Fortis against lenis stops, kept apart more by aspiration than by voicing. Back fricative /χ/ and dental fricatives /θ ð/. Central /ɨ ɨː/ against front /ɪ iː/ in the north; merged as front vowels in the south. Vowel length, fully contrastive only in stressed final syllables and monosyllables before /n l r/ (tôn against ton); elsewhere it follows from the next consonant. Initial consonant mutations: soft, nasal and aspirate.

Stress: fixed, penultimate. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- ch is changed to palatal [ç] after e, i, u (chwech, eich, dechrau); Welsh /χ/ keeps its place after all vowels.
- rh is [h] followed by a voiced trill; it should be a voiceless trill or fricative, with any [h] phase after it.
- mh, nh, ngh are a voiced nasal followed by [h]; this is close to the phonetic descriptions, but there is no voiceless nasal phase.
- dialects are mixed: u and y are central [ɨ] as in the north, but stressed penultimate syllables get long vowels as in the south (tadau, afon, pethau with long vowels).
- the consonant after a stressed short vowel is not lengthened.
- the unstressed final syllable is treated as 'diminished' and given the shortest length value (170 against 250 for the stressed syllable), the opposite of the Welsh pattern.
- the low stressed syllable with rising pitch after it exists only in the tune for the last stressed word of a clause (intonation 4); earlier words get ordinary high stressed syllables.
- gwl-, gwr-, gwn- get an extra schwa (gwlad as [ɡwəlaːd]), and final clusters such as pobl, llyfr have no inserted vowel.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 27 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=86), r (l=s10: tap=3 tapms=18 f1=179), a (A=s5: f1=112 f2=90 dur=40), h (<h=s14: ms=70 whisper=44), x (S=s29: f2=78 a2=68 a3=0 a4=52 af=-4), ɬ (l=s32: fric=52 a3=54 a4=58 a5=44 whisper=30), ɛ (E=s33: dur=66), ɨ (X=s34: f1=88 f2=90 dur=86), ø (x=s35: f1=84 f3=94 dur=86), ɔ (c=s36: dur=41), ʊ (U=s37: dur=74), ʌ (H=s38: dur=60), ɨː (u=s39: f2=107 f3=110), eː (i=s40: f1=123 f3=107), oː (c=s41: f1=94 f3=93 dur=82), ɑː (a=s42: dur=78), ɑɨ (a=s43: g1=58 g2=131 g3=90 glide=1 dur=78), aɪ (A=s44: f1=112 f2=90 g1=67 g2=124 g3=108 glide=1 dur=81), aʊ (A=s46: f1=112 f2=90 g1=69 g2=70 g3=100 glide=1 dur=81), əɪ (x=s47: g1=87 g2=123 g3=111 glide=1 dur=164), əɨ (x=s48: g1=73 g2=104 g3=105 glide=1 dur=164), eʊ (i=s49: f1=123 f3=107 g1=129 g2=55 g3=95 glide=1), ɪu (I=s50: g1=80 g2=50 g3=96 glide=1 dur=156), ɨu (u=s51: f2=107 f3=110 g1=102 g2=61 g3=106 glide=1), ɔɨ (c=s53: g1=80 g2=197 g3=93 glide=1 dur=82), uɨ (u=s55: g1=105 g2=99 g3=109 glide=1).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (pwy, beth, ble, pryd ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent, last 118 per cent of the module's own.

Sources: Bell, Elise; Archangeli, Diana B.; Anderson, Skye J.; Hammond, Michael; Webb-Davies, Peredur; Brooks, Heddwen (2023). Northern Welsh. Journal of the International Phonetic Association 53(2): 487-510. Hannahs, S. J. (2013). The Phonology of Welsh. Oxford University Press. Ball, Martin J.; Williams, Briony (2001). Welsh Phonetics. Lewiston: Edwin Mellen Press. Jones, Glyn E. (1984). The distinctive vowels and consonants of Welsh. In Ball, Martin J. & Jones, Glyn E. (eds.), Welsh Phonology: Selected Readings. Cardiff: University of Wales Press. Mayr, Robert; Davies, Hannah (2011). A cross-dialectal acoustic study of the monophthongs and diphthongs of Welsh. Journal of the International Phonetic Association 41(1): 1-25. Williams, Briony (1983). Stress in Modern Welsh. PhD dissertation, University of Cambridge. And 4 more in the profile.

## Danish (`da`)

Indo-European, Germanic, North Germanic, East Scandinavian. Described: Standard Danish (rigsdansk) as spoken in Copenhagen, the variety of the IPA illustration (Grønnum 1998).

**What the language has.** Stød versus no stød on syllables with a long vowel or with a short vowel plus sonorant: hund [hunˀ] 'dog' versus hun [hun] 'she', vend [vɛnˀ] versus ven [vɛn], mord versus mor, læser [ˈlɛːˀsɐ] 'reads' versus læser [ˈlɛːsɐ] 'reader', anden [ˈanˀən] 'the duck' versus anden [ˈanən] 'other'. Four degrees of height among front unrounded vowels, /i e ɛ a/, three among front rounded and among back vowels, giving one of the largest vowel inventories known. Long versus short vowels with little difference of quality (hvile [ˈviːlə] versus vilde [ˈvilə]). Aspirated /p t k/ versus unaspirated /b d ɡ/ at the start of a syllable; both series are voiceless. Lexical stress (billigst versus bilist). Schwa versus full vowels in unstressed syllables.

Stress: lexical. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- stød is not modelled: hun and hund, ven and vend, and the noun and the verb læser come out the same; the phoneme names that begin with '?' mark short vowels, and the IPA trace prints them with a glottal stop [ʔ] before the vowel that is neither spoken nor correct.
- /b d ɡ/ come from the base table and are voiced stops; Danish has voiceless unaspirated stops; /t/ is a plain aspirated stop without affrication.
- soft d uses the English dental fricative phoneme [ð] where Danish has a velarised alveolar approximant without friction.
- vowel length is not part of the phoneme string: it is set by context procedures (LongVowelLength, ShortVowelLength) and by the spelling rules, and the IPA trace never shows length.
- schwa is always pronounced: there is no schwa assimilation and there are no syllabic consonants (gade, spille, manden keep [ə]).
- stressed syllables carry the pitch peaks as in the other eSpeak languages; the Copenhagen pattern of a low stressed syllable and a high post-tonic syllable is not modelled, although the voice has its own tunes (s2, c2, q2, e2).
- some vowel qualities are off: the long vowel of løbe and købe is the open [œ] instead of [øː].
- questions are given the same tune whether they are yes-no or wh-questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɐ̯ (A=s8: f1=85 dur=40), i (i=s5: f1=83 dur=56), h (<h=s14: ms=70 whisper=44), ʋ (v=s25: af=-14), ð (v=s26: f2=149 f3=110 a6=28 ab=48), ʌ (OE=s36: f1=112 f2=87 f3=114 dur=84), ʔʌ (<q=s3 OE=s36: ms=50 hush=1; f1=112 f2=87 f3=114 dur=84), ʔi (<q=s3 i=s5: ms=50 hush=1; f1=83 dur=56), ʔe (<q=s3 e=s4: ms=50 hush=1; f1=84 dur=53), ε (E=s38: f1=79 f2=111 dur=84), ʔu (<q=s3 u=s7: ms=50 hush=1; f3=86 dur=57), ʔo (<q=s3 o=s6: ms=50 hush=1; f1=84 f2=85 dur=53), ɒ (O=s40: f1=116 dur=85), ɔ (O=s41: f1=77 dur=85), ʔy (<q=s3 y=s42: ms=50 hush=1; f1=76 dur=56), œ (OE=s44: f1=77 dur=84), ʔœ (<q=s3 OE=s44: ms=50 hush=1; f1=77 dur=84).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (hvem, hvad, hvor, hvornår ...) ends as a statement does, from a high question word.
Timing: last 88 per cent of the module's own.

**Not yet.** Stød is not in eSpeak NG's reading.

Sources: Grønnum, Nina (1998). Danish. Journal of the International Phonetic Association 28(1-2), 99-105. Basbøll, Hans (2005). The Phonology of Danish. Oxford University Press. Grønnum, Nina (2005). Fonetik og fonologi: Almen og dansk. 3rd edition. Copenhagen: Akademisk Forlag. Fischer-Jørgensen, Eli (1989). Phonetic analysis of the stød in standard Danish. Phonetica 46, 1-59. Fischer-Jørgensen, Eli (1972). Formant frequencies of long and short Danish vowels. In Firchow et al. (eds.), Studies for Einar Haugen. The Hague: Mouton. Also in Annual Report of the Institute of Phonetics, University of Copenhagen 6. Grønnum, Nina and Basbøll, Hans (2001). Consonant length, stød and morae in Standard Danish. Phonetica 58, 230-253. And 3 more in the profile.

## Greek (`el`)

Indo-European, Hellenic. Described: Standard Modern Greek (Athens).

**What the language has.** Five vowels, with no contrast of length or nasality. Voiceless against voiced fricatives at four places: /f v/, /θ ð/, /s z/, /x ɣ/. Voiceless unaspirated stops against voiced stops. Position of stress (νόμος 'law' against νομός 'prefecture'). Affricates /t͡s d͡z/. No consonant length in the standard language: double letters stand for single consonants.

Stress: lexical, within the last three syllables. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- /s/ inside a word is not voiced before a voiced consonant: κόσμος, σβήνω, σμήνος, σεισμός keep [s]; only word-final ς is voiced before a voiced initial, and this is applied even across a full stop.
- the palatal stop [ɟ] is missing: γκ and γγ before front vowels stay velar (αγγίζω, άγγελος, εγγύηση).
- γ before front vowels and the glide from unstressed ι are the approximant [j], not the fricative [ʝ].
- unstressed ι before a stressed vowel is a full syllable after most consonants: παιδιά is given three syllables [peðiˈa] and ποιος two [ˈpios].
- double σσ is spoken long [ss] (θάλασσα), though the standard language has no geminates.
- prenasalisation is treated unevenly: μπ and ντ are always plain [b d], γκ and γγ after a vowel always [ŋɡ].
- /s z/ use the plain alveolar sounds of the base table, not the retracted Greek ones, and /r/ is a short trill rather than a tap.
- secondary stresses are added by rule (άνθρωπος as [ˈanθroˌpos]), but there is no rule for the second stress before an enclitic.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: f1=111), i (i=s5: f1=125), o (o=s6: f1=109 f2=111), u (u=s7: f1=129 f2=122 dur=114), b (b=s13: voi=1 lead=75), d (d=s13: voi=1 lead=75), c (t=s19: f2=148 f3=109 a3=56 a4=56 vot=32), ç (Y=s25: voi=0).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (ποιος, ποια, ποιο, ποιοι ...) ends as a statement does, from a high question word.

Sources: Arvaniti, Amalia (1999). Standard Modern Greek. Journal of the International Phonetic Association 29(2): 167-172. Arvaniti, Amalia (2007). Greek Phonetics: The State of the Art. Journal of Greek Linguistics 8: 97-208. Sfakianaki, Anna (2002). Acoustic characteristics of Greek vowels produced by adults and children. Selected Papers on Theoretical and Applied Linguistics 14: 383-394. Thessaloniki. Fourakis, Marios; Botinis, Antonis; Katsaiti, Maria (1999). Acoustic characteristics of Greek vowels. Phonetica 56: 28-43. Fourakis, Marios (1986). A timing model for word-initial CV syllables in Modern Greek. Journal of the Acoustical Society of America 79(6). Arvaniti, Amalia (2000). The phonetics of stress in Greek. Journal of Greek Linguistics 1: 9-39. And 5 more in the profile.

## English (Caribbean) (`en-029`)

Indo-European, Germanic, West Germanic, Anglo-Frisian. Described: Jamaican English, the standard English of Jamaica as spoken beside Jamaican Creole, taken here as the reference for the Caribbean because it is the best described and the closest to the eSpeak NG voice; other territories (Trinidad, Barbados, Guyana, the Bahamas) differ, above all in rhoticity.

**What the language has.** FACE and GOAT are long monophthongs /eː/ and /oː/; towards the Creole end of the range they are falling diphthongs [ie] and [uo]. TRAP and BATH have the same quality [a] and differ in length (no TRAP-BATH split of quality); PALM and START also have [aː]. LOT is unrounded and may merge with TRAP towards the Creole end ([a] in both rat and rot); in the standard the two are kept apart. STRUT is a back rounded vowel, separate from FOOT. NEAR and SQUARE are merged for many speakers (beer = bear). NORTH versus FORCE are kept apart ([aː] or [ɔː] against [oː]). Vowel length is contrastive and not tied to large differences of quality. Rhoticity is variable: Jamaican English keeps /r/ after a vowel mainly at the end of a stressed syllable (near, square, car) and less before a consonant; Barbados is fully rhotic, Trinidad and the Bahamas are non-rhotic, Guyana is variable.

Stress: lexical, free. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the voice is fully non-rhotic (car [kɑə], farmer [fɑəma], near [niə]); Jamaican English keeps /r/ in words such as near, square and car, and Barbadian English is fully rhotic.
- NEAR and SQUARE are kept apart as [ie]-like and [eə]-like diphthongs; many Jamaican speakers merge them.
- the IPA trace labels FACE and GOAT as [eɪ] and [oʊ], although their formant data are monophthongs (vowel/e, vowel/o).
- TH-stopping is applied to every /θ/ and /ð/ ('replace 00'), which fits informal speech and the Creole but not careful standard speech.
- there are no palatal stops before /a/ (cat, garden) and no reduction of final clusters.
- syllable timing is only approximated by equal length values for unstressed and secondary-stressed syllables (stressLength 175); primary-stressed syllables are still much longer, and the stress rules and reductions are those of British English apart from rule set 8.
- the tunes are the default English ones, and wh-questions get the rising question tune.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 25 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (A=s6: f1=112 f2=90 dur=40), i (i=s8: dur=50), h (<h=s15: ms=70 whisper=44), t̪ (t=s19: f2=91 burst=-4), ɪ (X=s1: dur=86), ʊ (U=s36: dur=74), aa (A=s37: f1=112 f2=90 dur=81), ɑː (a=s38: dur=78), ɛ (E=s39: dur=66), ɒ (@=s40: dur=68), ʌ (H=s42: dur=60), ɑə (a=s43: g1=81 g2=120 g3=91 glide=1 dur=78), ɔː (c=s45: dur=82), ɔə (c=s46: g1=114 g2=180 g3=95 glide=1 dur=82), oə (w=s47 x=s1: hold=55; dur=86), aʊ (A=s48: f1=112 f2=90 g1=69 g2=70 g3=100 glide=1 dur=81), oʊ (c=s49: f1=94 f3=93 g1=94 g2=128 g3=90 glide=1 dur=82), aɪ (A=s50: f1=112 f2=90 g1=67 g2=124 g3=108 glide=1 dur=81), eɪ (i=s51: f1=123 f3=107 g1=123 g2=94 g3=103 glide=1), ɔɪ (c=s52: g1=95 g2=236 g3=98 glide=1 dur=82), eə (y=s47 x=s1: hold=55; dur=86), iə (y=s47 x=s1: hold=55; dur=86).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (who, what, where, when ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Wells, J. C. (1982). Accents of English. Volume 3: Beyond the British Isles. Cambridge University Press. Devonish, Hubert and Harry, Otelemate G. (2004). Jamaican Creole and Jamaican English: phonology. In Schneider et al. (eds.), A Handbook of Varieties of English, volume 1. Berlin: Mouton de Gruyter. Harry, Otelemate G. (2006). Jamaican Creole. Journal of the International Phonetic Association 36(1), 125-131. Wassink, Alicia Beckford (2001). Theme and variation in Jamaican vowels. Language Variation and Change 13(2), 135-159. Cassidy, Frederic G. and Le Page, Robert B. (1967). Dictionary of Jamaican English. Cambridge University Press. Gooden, Shelome; Drayton, Kathy-Ann; Beckman, Mary (2009). Tone inventories and tune-text alignments: prosodic variation in 'hybrid' prosodic systems. Studies in Language 33(2), 396-436.

## English (Scotland) (`en-gb-scotland`)

Indo-European, Germanic, West Germanic, Anglo-Frisian. Described: Scottish Standard English, the English of educated speakers in the Central Belt (Edinburgh and Glasgow); not Scots.

**What the language has.** Rhotic: /r/ is pronounced in all positions, and there are no centring diphthongs and no separate long vowels of the RP kind (card [kard], beard [bird]). FOOT and GOOSE are one phoneme /ʉ/ (pull = pool, full = fool). TRAP, BATH and PALM are one phoneme /a/ (Sam = psalm, ant = aunt); there is no TRAP-BATH split. LOT, CLOTH and THOUGHT are one phoneme /ɔ/ (cot = caught). FOOT and STRUT are separate, as in the south of England (/ʉ/ versus /ʌ/). FACE and GOAT are monophthongs /e/ and /o/. More vowel contrasts before /r/ than in other accents: NORTH versus FORCE (horse [ɔr] versus hoarse [or]), and for many speakers three NURSE vowels (fir [ɪr], fern [ɛr], fur [ʌr]). /ʍ/ versus /w/ (which versus witch) and /x/ versus /k/ (loch versus lock).

Stress: lexical, free. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the Scottish Vowel Length Rule is modelled in part: /i/ and /ʉ/ are lengthened before voiced fricatives and before a pause, and PRICE takes its long form before vowels, voiced fricatives and at the end of a word; but morpheme boundaries inside a word are not seen, so brewed = brood, tied = tide, agreed has the vowel of greed.
- the short and the long PRICE diphthong share one formant file and differ only in duration; the language has [ʌi] against [ae].
- /l/ is clear before vowels as in RP; Scottish /l/ is dark in all positions.
- /r/ before a vowel is an approximant and /r/ after a vowel is only a colouring of the vowel (the phoneme r/ has no sound of its own); taps are not used.
- TRAP (length 200) and BATH or PALM (length 220) keep a small length difference, and LOT and THOUGHT use different formant data, although each pair is one phoneme in this accent.
- there is no glottal replacement of /t/.
- the tunes are the default English ones: the rising statements of Glasgow are not available, and wh-questions get the rising question tune.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 25 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=124), r (l=s11: tap=3 tapms=18 f1=179), a (A=s6: f1=112 f2=90 dur=59), e (I=s7: f2=106 f3=109), h (<h=s15: ms=70 whisper=44), ɪ (X=s1: dur=124), ʉ (u=s10: dur=79), a: (A=s38: f1=112 f2=90 dur=81), aː (A=s38: f1=112 f2=90 dur=81), ɔː (c=s41: dur=82), ɔ (c=s39: dur=61), o (c=s9: f1=94 f3=93 dur=61), ʌʉ (H=s42: g1=57 g2=116 g3=99 glide=1 dur=143), oː (c=s43: f1=94 f3=93 dur=82), aɪ (A=s45: f1=112 f2=90 g1=67 g2=124 g3=108 glide=1 dur=81), eː (i=s46: f1=123 f3=107), ɔɪ (c=s47: g1=95 g2=236 g3=98 glide=1 dur=82), iə (y=s48 x=s1: hold=55; dur=124), ʉɹ (u=s10 r: dur=79), əɹ (x=s1 r: dur=124).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (who, what, where, when ...) ends as a statement does, from a high question word.

Sources: Wells, J. C. (1982). Accents of English. Volume 2: The British Isles. Cambridge University Press. Abercrombie, David (1979). The accents of Standard English in Scotland. In Aitken and McArthur (eds.), Languages of Scotland. Edinburgh: Chambers. Aitken, A. J. (1981). The Scottish Vowel-length Rule. In Benskin and Samuels (eds.), So Meny People Longages and Tonges. Edinburgh. Scobbie, James M.; Hewlett, Nigel; Turk, Alice (1999). Standard English in Edinburgh and Glasgow: the Scottish Vowel Length Rule revealed. In Foulkes and Docherty (eds.), Urban Voices: Accent Studies in the British Isles. London: Arnold. Stuart-Smith, Jane (2004). Scottish English: phonology. In Schneider et al. (eds.), A Handbook of Varieties of English, volume 1. Berlin: Mouton de Gruyter. Scobbie, James M.; Gordeeva, Olga B.; Matthews, Benjamin (2007). Scottish English speech acquisition. In McLeod (ed.), The International Guide to Speech Acquisition. Clifton Park: Thomson Delmar Learning. And 2 more in the profile.

## English (Lancaster) (`en-gb-x-gbclan`)

Indo-European, Germanic, West Germanic, Anglo-Frisian. Described: Northern English of Lancashire as heard in and around Lancaster: a regional accent of the north-west of England, not the traditional rural dialect; features that belong to other parts of Lancashire are marked as such.

**What the language has.** No FOOT-STRUT split: STRUT words have the vowel of FOOT, /ʊ/ (put = putt, could = cud). No TRAP-BATH split: BATH words have the short front vowel of TRAP, /a/ (gas and grass rhyme; ant = aunt); PALM and START have a long vowel, so that Sam and psalm differ by length. FACE and GOAT are long monophthongs /eː/ and /oː/. Mainly non-rhotic, with long vowels and centring diphthongs where the spelling has r; rhoticity survives with some, mostly older, speakers in central and east Lancashire. LOT versus THOUGHT (cot versus caught). Long versus short vowels, more nearly a contrast of pure length than in RP because /a/ and /aː/ are close in quality. Lexical stress with reduction of unstressed vowels.

Stress: lexical, free. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- STRUT and FOOT are both labelled [ʊ] but use different formant files (vowel/o-_2 and vowel/uu), so a small difference of quality remains where the accent has one vowel.
- [ŋɡ] is produced only before a vowel (singing is [sɪŋɡɪn]); before a pause or a consonant the plain [ŋ] is used.
- /l/ is clear before vowels as in RP.
- there is no h-dropping, no glottal replacement of /t/ and no [ɹ] for /t/.
- the voice is fully non-rhotic; the remaining rhoticity of Lancashire cannot be chosen.
- the tunes are the default English ones, and wh-questions get the rising question tune.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 25 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=86), a (A=s6: f1=112 f2=90 dur=40), h (<h=s15: ms=70 whisper=44), ɪ (X=s1: dur=86), ʊ (U=s36: dur=74), ɑː (a=s38: dur=78), ɛ (E=s39: dur=66), ɒ (@=s40: dur=68), ɔː (c=s43: dur=82), æʊ (A=s44: g1=67 g2=74 g3=99 glide=1 dur=81), oː (c=s45: f1=94 f3=93 dur=82), aɪ (A=s47: f1=112 f2=90 g1=67 g2=124 g3=108 glide=1 dur=81), eː (i=s48: f1=123 f3=107), ɔɪ (c=s49: g1=95 g2=236 g3=98 glide=1 dur=82), eə (y=s50 x=s1: hold=55; dur=86), iə (y=s50 x=s1: hold=55; dur=86), ʊə (w=s50 x=s1: hold=55; dur=86).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (who, what, where, when ...) ends as a statement does, from a high question word.
Timing: last 118 per cent of the module's own.

Sources: Wells, J. C. (1982). Accents of English. Volume 2: The British Isles. Cambridge University Press. Beal, Joan (2004). English dialects in the North of England: phonology. In Schneider et al. (eds.), A Handbook of Varieties of English, volume 1. Berlin: Mouton de Gruyter. Hughes, Arthur; Trudgill, Peter; Watt, Dominic (2012). English Accents and Dialects. 5th edition. London: Hodder Education. Shorrocks, Graham (1998). A Grammar of the Dialect of the Bolton Area. Part I: Introduction, Phonology. Frankfurt: Peter Lang. Cruttenden, Alan (1997). Intonation. 2nd edition. Cambridge University Press.

## English (West Midlands) (`en-gb-x-gbcwmd`)

Indo-European, Germanic, West Germanic, Anglo-Frisian. Described: Urban English of the West Midlands conurbation: Birmingham ('Brummie') with the neighbouring Black Country.

**What the language has.** No FOOT-STRUT split: STRUT words have a vowel at or near that of FOOT, [ʊ] or an unrounded [ɤ] (put = putt). No TRAP-BATH split: BATH words have the short vowel of TRAP, [a]. Non-rhotic, with long vowels and centring diphthongs where the spelling has r. Wide diphthongs in FLEECE, GOOSE, FACE, GOAT, PRICE and MOUTH, shifted in the same direction as in London. PRICE [ɔi] is close to CHOICE [oi] and merges with it for some speakers. LOT versus THOUGHT (cot versus caught). Lexical stress with reduction of unstressed vowels.

Stress: lexical, free. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- [ŋɡ] is produced only before a vowel (singing is [sɪŋɡɪŋ]); at the end of a word the accent also has [ŋɡ].
- SQUARE is the central vowel [ɜː] (formant file vowel/3_en) and NURSE a front rounded vowel (vowel/y#); the descriptions have [ɛː] for SQUARE and [ɜː] for NURSE.
- FACE is labelled [eː] in the IPA trace although its formant data are those of a wide diphthong (vdiph/@i_3).
- STRUT and FOOT are both labelled [ʊ] but use different formant files.
- /h/ is removed everywhere ('replace 00 h NULL'); in speech h-dropping is variable and depends on style.
- KIT has the usual lax quality, not the very close vowel of Birmingham.
- the rising tune (intonation group 4) is applied to every statement and the same final movement to every clause; there is no rise plus plateau and no choice between rising and falling statements.
- there is no glottal replacement of /t/.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 25 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=86), a (A=s6: f1=112 f2=90 dur=40), i (i=s8: dur=50), ɪ (X=s1: dur=86), ʊ (U=s36: dur=74), ɑː (a=s38: dur=78), ɛ (E=s39: dur=66), ɒ (@=s40: dur=68), ei (i=s43: f1=123 f3=107 g1=92 g2=106 g3=115 glide=1), ɔː (c=s44: dur=82), əu (x=s45: g1=71 g2=59 g3=102 glide=1 dur=164), æʊ (A=s46: g1=67 g2=74 g3=99 glide=1 dur=81), ʌʊ (H=s47: g1=70 g2=85 g3=103 glide=1 dur=143), ɔɪ (c=s49: g1=95 g2=236 g3=98 glide=1 dur=82), eː (i=s50: f1=123 f3=107), oɪ (c=s51: f1=94 f3=93 g1=90 g2=234 g3=98 glide=1 dur=82), iə (y=s52 x=s1: hold=55; dur=86), ʊə (w=s52 x=s1: hold=55; dur=86).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (who, what, where, when ...) ends as a statement does, from a high question word.
Timing: last 118 per cent of the module's own.

Sources: Wells, J. C. (1982). Accents of English. Volume 2: The British Isles. Cambridge University Press. Clark, Urszula (2004). The English West Midlands: phonology. In Schneider et al. (eds.), A Handbook of Varieties of English, volume 1. Berlin: Mouton de Gruyter. Mathisen, Anne Grethe (1999). Sandwell, West Midlands: ambiguous perspectives on gender patterns and models of change. In Foulkes and Docherty (eds.), Urban Voices: Accent Studies in the British Isles. London: Arnold. Thorne, Steve (2003). Birmingham English: A Sociolinguistic Study. Doctoral dissertation, University of Birmingham. Hughes, Arthur; Trudgill, Peter; Watt, Dominic (2012). English Accents and Dialects. 5th edition. London: Hodder Education. Cruttenden, Alan (1997). Intonation. 2nd edition. Cambridge University Press.

## English (Received Pronunciation) (`en-gb-x-rp`)

Indo-European, Germanic, West Germanic, Anglo-Frisian. Described: Received Pronunciation in its mainstream form (also called General British or Standard Southern British English), with conservative and recent variants noted.

**What the language has.** FOOT versus STRUT: /ʊ/ and /ʌ/ are separate phonemes (put versus putt). TRAP versus BATH: BATH words have the long back vowel of PALM and START, /ɑː/ (ant versus aunt, gas versus grass). Non-rhotic: historical /r/ after a vowel is lost, which gives the long vowels /ɑː ɔː ɜː/ and the centring diphthongs /ɪə eə ʊə/ (card, cord, bird, near, square, cure). LOT versus THOUGHT (cot versus caught) and PALM versus LOT (balm versus bomb). Long versus short monophthongs, which differ in quality as well as length (beat versus bit, pool versus pull). Voiced versus voiceless obstruents in all positions, cued at the end of a word mainly by the length of the vowel before them. Dental fricatives /θ ð/ versus /f v/ and /t d/. Lexical stress (import as noun versus verb), with reduction of unstressed vowels.

Stress: lexical, free. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- final unstressed happY is lax [ɪ] (the voice replaces the final vowel by the phoneme i, which has KIT quality in this table): this is the conservative form, while most present-day speakers have [i].
- all CURE words have [ɔː] (cure [kjɔː], poor [pɔː]); many speakers keep [ʊə] after /j/.
- there is no glottal reinforcement or glottal replacement of /t/.
- wh-questions get the same rising tune as yes-no questions, because the tune is chosen from the question mark alone; statements, commas and exclamations use the default English tunes.
- NEAR and SQUARE are the older centring diphthongs; the monophthongal [ɛː] of present-day speech is not available.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 27 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: æ (A=s11: dur=40), ɪ (X=s1: dur=86), h (<h=s16: ms=70 whisper=44), ʊ (U=s37: f1=79 f3=110 dur=74), ɐ (A=s38: f2=90 dur=40), ɑː (a=s39: f3=91 dur=78), ɛ (E=s40: dur=66), ɒ (@=s41: dur=68), ʌ (H=s43: f3=111 dur=60), ɜː (R=s45: f1=91), iː (i=s46: f1=86 f3=109), ɔː (c=s47: f2=109 dur=82), uː (u=s48: f2=67), aʊ (A=s49: f1=112 f2=90 g1=64 g2=80 g3=103 glide=1 dur=81), əʊ (x=s50: g1=83 g2=80 g3=105 glide=1 dur=164), aɪ (A=s52: f1=112 f2=90 g1=62 g2=113 g3=107 glide=1 dur=81), eɪ (E=s53: f1=93 g1=73 g2=101 g3=105 glide=1 dur=136), ɔɪ (c=s54: g1=85 g2=213 g3=97 glide=1 dur=82), eə (y=s55 x=s1: hold=55; dur=86), iə (y=s55 x=s1: hold=55; dur=86).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (who, what, where, when ...) ends as a statement does, from a high question word.
Timing: last 118 per cent of the module's own.

Sources: Roach, Peter (2004). British English: Received Pronunciation. Journal of the International Phonetic Association 34(2), 239-245. Wells, J. C. (1982). Accents of English. 3 volumes. Cambridge University Press. Cruttenden, Alan (2014). Gimson's Pronunciation of English. 8th edition. London: Routledge. Deterding, David (1997). The formants of monophthong vowels in Standard Southern British English pronunciation. Journal of the International Phonetic Association 27, 47-55. Grabe, Esther and Low, Ee Ling (2002). Durational variability in speech and the Rhythm Class Hypothesis. In Gussenhoven and Warner (eds.), Laboratory Phonology 7. Berlin: Mouton de Gruyter. Docherty, Gerard J. (1992). The Timing of Voicing in British English Obstruents. Berlin: Foris. And 4 more in the profile.

## English (Shavian alphabet) (`en-shaw`)

Indo-European, Germanic, West Germanic, Anglo-Frisian. Described: British English of the Received Pronunciation type. The eSpeak NG voice uses its default English phoneme table ('en', the table of its British English voice en-GB), a non-rhotic accent close to RP with a short front [a] in TRAP. The Shavian alphabet is a script, not a dialect: its reference spellings follow RP, with every historical r written.

**What the language has.** The alphabet has one letter for each of 24 consonants and 16 vowels and diphthongs, plus 8 compound letters: six for a vowel followed by r (are, or, air, err, array, ear) and two for the sequences in ian and yew. FOOT versus STRUT (letters wool and up) and TRAP versus PALM or BATH (letters ash and ah): the spelling keeps the splits of southern British English. LOT versus THOUGHT (letters on and awe). Schwa has its own letter (ado), so reduced vowels are written as such. Historical r is always written, with the compound letters, so the spelling can be read with a rhotic or a non-rhotic accent; the voice reads it non-rhotically. Voiced and voiceless consonants are paired letters (tall and deep forms). Stress is not written.

Stress: lexical, free. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- word stress is guessed, because the spelling does not show it and the Shavian part of the dictionary has only letter names, 14 short forms and 8 words: begin and example are stressed on the first syllable, and information and understand have primary and secondary stress exchanged.
- the rules put a primary stress mark on the compound letters are, or, air, err and ear, so every syllable written with them is stressed.
- function words written in Shavian are not recognised, except the few in the list: it, was, he, can, from, we, at come out stressed and in their strong forms, where the same sentence in Latin letters has weak forms.
- TRAP is the front [a] of the default British table, and BATH depends on the script: Latin bath gives short [a], while the usual Shavian spelling with the letter ah gives [ɑː].
- the letter ian is read as a long [iː] plus schwa.
- wh-questions get the rising question tune.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 42 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=86), a (A=s6: f1=112 f2=90 dur=40), i (i=s8: f1=86 f3=109 dur=50), t (t=s11: vot=17), p (p=s12: vot=13), k (k=s13: vot=28), h (<h=s18: ms=70 whisper=44), b (b=s22: voi=1 lead=75), d (d=s22: voi=1 lead=75), ɡ (g=s22: voi=1 lead=75), ɪ (X=s1: dur=86), ʊ (U=s43: f1=79 f3=110 dur=74), əl (x=s1 l: dur=86), ɐ (A=s44: f2=90 dur=40), ɑː (a=s45: f3=91 dur=78), ɛ (E=s46: dur=66), ɒ (@=s47: dur=68), ʌ (H=s49: f3=111 dur=60), ɜː (R=s51: f1=91), iː (i=s52: f1=86 f3=109), ɔː (c=s53: f2=109 dur=82), uː (u=s54: f2=67), aʊ (A=s55: f1=112 f2=90 g1=64 g2=80 g3=103 glide=1 dur=81), əʊ (x=s56: g1=83 g2=80 g3=105 glide=1 dur=164), aɪ (A=s58: f1=112 f2=90 g1=62 g2=113 g3=107 glide=1 dur=81), eɪ (E=s59: f1=93 g1=73 g2=101 g3=105 glide=1 dur=136), ɔɪ (c=s60: g1=85 g2=213 g3=97 glide=1 dur=82), eə (y=s61 x=s1: hold=55; dur=86), iə (y=s61 x=s1: hold=55; dur=86), ʊə (w=s61 x=s1: hold=55; dur=86), aɪə (A=s6 y=s61 y=s61: f1=112 f2=90 dur=40; hold=55; hold=55), u (u=s10: f2=67 dur=52), ɭ (l=s17: f3=86), aː (A=s68: f1=112 f2=90 dur=81).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
Timing: last 118 per cent of the module's own.

Sources: Shaw, Bernard (1962). Androcles and the Lion. The Shaw Alphabet Edition, with a reading key, notes on the spelling by Peter MacCarthy and suggestions for writing by Kingsley Read. Harmondsworth: Penguin. MacCarthy, Peter A. D. (1969). The Bernard Shaw alphabet. In Haas (ed.), Alphabets for English. Manchester University Press. The Unicode Standard, Shavian block (U+10450 to U+1047F). Roach, Peter (2004). British English: Received Pronunciation. Journal of the International Phonetic Association 34(2), 239-245. Wells, J. C. (1982). Accents of English. 3 volumes. Cambridge University Press. Cruttenden, Alan (2014). Gimson's Pronunciation of English. 8th edition. London: Routledge. And 3 more in the profile.

## English (America, New York City) (`en-us-nyc`)

Indo-European, Germanic, West Germanic, Anglo-Frisian. Described: New York City English: the traditional accent of the city and its near suburbs as described by Labov (1966), with the changes now under way noted.

**What the language has.** Short-a split: tense /eə/ (bad, man, pass, cab) versus lax /æ/ (bat, back, pal), a phonemic split because some words are exceptions to the conditioning (tense avenue, lax auxiliary can against tense noun can). LOT versus THOUGHT: the two are kept far apart, THOUGHT being raised to [ɔə], [oə] or [ʊə] (cot versus caught, Don versus dawn). Traditionally non-rhotic, with centring diphthongs in NEAR, SQUARE, START, NORTH and CURE; /r/ after a vowel is variable and increasing. Mary, marry and merry are three different vowels, and hurry [ʌ] differs from furry [ɝ]. Orange, horrible, Florida have the vowel of LOT plus /r/, not that of NORTH. FOOT versus STRUT, as in all North American accents; no TRAP-BATH split of the British kind, BATH words follow the short-a split. In non-rhotic speech NORTH, FORCE and THOUGHT are one vowel (source = sauce). Older speakers keep PALM (father, balm) apart from LOT (bother, bomb).

Stress: lexical, free. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- NURSE is always the diphthong [əɪ], also at the end of a word and before a vowel (fur [fəɪ], hurry [həɪɹi], girl, work): this form is nearly extinct, it occurred only before a consonant, and hurry has [ʌ] in this accent.
- LOT uses the rounded British vowel (phoneme 0 with formant file vowel/0: lot, cot, bother come out as [ɒ]), where New York has an unrounded [ɑ]; dog and chocolate get the same vowel instead of the raised THOUGHT vowel.
- short-a tensing has no lexical or grammatical exceptions: the function words can, and, am, had are tense, stems before a suffix are lax (passing, manning), and badge is lax because /dʒ/ is not in the list of tensing consonants.
- the voice is fully non-rhotic and has no intrusive /r/ (law and order, the idea is); present-day speakers are variably rhotic.
- /θ ð/ are always fricatives, and there is no glottal stop in bottle or button.
- the tunes are the default English ones, and wh-questions get the rising question tune.

**What OpenEVV says.** Spoken by the module made from US English (`enux`). 44 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=132), æ (A=s8: dur=64), i (i=s6: dur=85), t (t=s10: vot=70 asp=50), p (p=s11: vot=58 asp=50), k (k=s12: vot=80 asp=50), l (l=s9: f2=165 f3=92), h (<h=s16: ms=70 whisper=44), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɡ (g=s20: voi=1 lead=75), ɪ (I=s40: dur=122), ʊ (U=s42: dur=121), əl (x=s1 l=s9: dur=132; f2=165 f3=92), ɐ (H=s43: f1=116 f2=106), ɑː (a=s6: dur=85), ᵻ (X=s1: dur=132), ɒ (c=s44: f2=88 dur=65), ɔ (c=s45: dur=65), əɪ (x=s47: g1=91 g2=128 g3=115 glide=1 dur=176), iː (i=s48: dur=117), ɔː (c=s49: dur=87), uː (u=s50: dur=116), aʊ (a=s51: f2=115 f3=106 g1=65 g2=90 g3=100 glide=1 dur=85), oʊ (u=s52: f1=159 f2=75 f3=107 g1=159 g2=91 g3=104 glide=1 dur=116), aɪ (a=s53: f2=115 f3=106 g1=62 g2=159 g3=109 glide=1 dur=85), eɪ (i=s54: f1=152 g1=152 g2=92 g3=96 glide=1 dur=117), ɔɪ (c=s55: g1=62 g2=175 g3=110 glide=1 dur=87), eə (y=s56 x=s1: hold=55; dur=132), iə (y=s56 x=s1: hold=55; dur=132), ʊə (w=s56 x=s1: hold=55; dur=132), aɪə (a=s4 y=s56 y=s56: f2=115 f3=106 dur=59; hold=55; hold=55), u (u=s6: dur=85), ɭ (l=s15: f2=178 f3=72), aː (a=s62: f2=115 f3=106 dur=85).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (who, what, where, when ...) ends as a statement does, from a high question word.
Timing: last 118 per cent of the module's own.

Sources: Labov, William (2006). The Social Stratification of English in New York City. 2nd edition. Cambridge University Press. (First edition 1966.). Labov, William; Ash, Sharon; Boberg, Charles (2006). The Atlas of North American English: Phonetics, Phonology and Sound Change. Berlin: Mouton de Gruyter. Wells, J. C. (1982). Accents of English. Volume 3: Beyond the British Isles. Cambridge University Press. Gordon, Matthew J. (2004). New York, Philadelphia, and other northern cities: phonology. In Schneider et al. (eds.), A Handbook of Varieties of English, volume 1. Berlin: Mouton de Gruyter. Newman, Michael (2014). New York City English. Berlin: De Gruyter Mouton. Becker, Kara (2014). (r) we there yet? The change to rhoticity in New York City English. Language Variation and Change 26(2), 141-168. And 2 more in the profile.

## Esperanto (`eo`)

constructed language. Described: the norm of the Fundamento and of the Academy of Esperanto.

**What the language has.** Five vowels with no length contrast. A voiceless velar fricative beside h. Affricates c, ĉ, ĝ beside the fricatives.

Stress: fixed, penultimate. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 9 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (a=s1: f1=76), u (u=s4: dur=114), h (<h=s8: ms=70 whisper=44), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), ɡ (g=s11: voi=1 lead=75), aʊ (a=s27: g1=71 g2=75 g3=97 glide=1 dur=135), oɪ (o=s31: g1=84 g2=197 g3=103 glide=1 dur=155), ts (t=s34 s=s35: hold=85; hold=70).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (kiu, kio, kie, kiam ...) ends as a statement does, from a high question word.

Sources: Zamenhof, L. L. (1905). Fundamento de Esperanto. Wennergren, Bertilo (2005). Plena Manlibro de Esperanta Gramatiko.

## Estonian (`et`)

Uralic, Finnic. Described: Standard Estonian (based on North Estonian).

**What the language has.** Three degrees of quantity: short (Q1), long (Q2) and overlong (Q3), a property of the stressed two-syllable foot carried by the vowel, the following consonant or both (sada, saada, saada; lina, linna, linna). Nine vowel qualities, including the back unrounded /ɤ/ (written õ) and the front rounded /y ø/. Plain versus palatalised alveolars: /t s n l/ against /tʲ sʲ nʲ lʲ/ (palk 'wages' against palk 'log'). Stops differ in length, not voicing: short (written b d g), long (p t k) and overlong (pp tt kk), all voiceless. A large set of diphthongs (36 in stressed syllables according to Asu & Teras 2009).

Stress: fixed, word-initial. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Q2 and Q3 are told apart only where the spelling or a few rules allow it (pp, tt, kk; a long vowel in a monosyllable; k, p, t after a long vowel or sonorant); since vowels and most consonants are written alike in Q2 and Q3 (linna, kooli, saada), most Q3 words are spoken as Q2.
- no pitch difference between Q2 and Q3: the early fall of Q3 is not produced.
- õ has a central rounded quality, printed [ɵ], instead of back unrounded [ɤ].
- palatalisation is guessed from the spelling and overapplied: l, n, s, t before i or j become full palatals such as [ʎ] (tuli is given as [tuʎɪ]), and nearly every word-final ll, nn, ss, tt after a vowel is palatalised.
- short b, d, g between vowels are fully voiced stops; Estonian has short voiceless stops with at most partial voicing.
- the half-long second-syllable vowel of Q1 words is produced only in words that begin with one consonant or none followed by vowel, single consonant, vowel, and it is given a laxer quality (phonemes A1, E1, I1, O1, U1; final i is printed [ɪ]).
- questions get a rising tune (intonation group 3), whereas Estonian questions usually fall.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 30 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s8: tap=3 tapms=18 f2=109 f3=77), e (e=s4: f1=118 f2=80 f3=90 dur=53), i (i=s5: f1=116 dur=56), o (o=s6: f1=119 f2=123 dur=53), u (u=s7: f1=148 f2=115 dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), ʎ (l=s13: f2=159), h (<h=s16: ms=70 whisper=44), ɲ (n=s18: f2=136 f3=109), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɡ (g=s20: voi=1 lead=75), aː (a=s41: dur=72), ɑ (O=s42: f2=120 dur=85), eː (e=s43: f1=118 f2=80 f3=90), ɛ (E=s44: dur=84), iː (i=s45: f1=116 dur=117), oː (o=s46: f1=119 f2=123), ɔ (O=s47: dur=85), uː (u=s48: f1=148 f2=115 dur=117), ʊ (U=s49: dur=114), ɵ (Y=s50: f2=89 f3=107), æ (OE=s52: f2=109 f3=107 dur=84), ø (oe=s54: f3=109 dur=53), y (y=s56: f2=89 dur=56), yː (y=s57: f2=89 dur=117), æi (OE=s58: f2=109 f3=107 g1=64 g2=144 g3=122 glide=1 dur=171).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (kes, mis, kus, millal ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Asu, Eva Liina; Teras, Pire (2009). Estonian. Journal of the International Phonetic Association 39(3): 367-372. Lehiste, Ilse (1960). Segmental and syllabic quantity in Estonian. American Studies in Uralic Linguistics 1: 21-82. Bloomington: Indiana University. Lehiste, Ilse (1997). Search for phonetic correlates in Estonian prosody. In Lehiste, Ilse & Ross, Jaan (eds.), Estonian Prosody: Papers from a Symposium. Tallinn: Institute of Estonian Language. Lippus, Pärtel; Asu, Eva Liina; Teras, Pire; Tuisk, Tuuli (2013). Quantity-related variation of duration, pitch and vowel quality in spontaneous Estonian. Journal of Phonetics 41(1): 17-28. Meister, Einar; Meister, Lya (2019). Production of Estonian vowels by Finnish speakers. Eesti ja soome-ugri keeleteaduse ajakiri / Journal of Estonian and Finno-Ugric Linguistics 10(1): 129-143. Leppik, Katrin; Lippus, Pärtel; Asu, Eva Liina (2019). The production of Estonian vowels in three quantity degrees by Spanish L1 speakers. Proceedings of the 19th International Congress of Phonetic Sciences, Melbourne. And 3 more in the profile.

## Basque (`eu`)

Language isolate. Described: Standard Basque (Euskara Batua) in a central, Gipuzkoan or High Navarrese type of pronunciation without /h/; the pitch-accent systems of Northern Bizkaian (Lekeitio, Gernika, Getxo) and of Goizueta are described in the tone section.

**What the language has.** Three sibilant places, each with a fricative and an affricate: laminal (tongue blade) alveolar /s̻ ts̻/ written z, tz; apical (tongue tip) alveolar /s̺ ts̺/ written s, ts; and prepalatal /ʃ tʃ/ written x, tx (zu 'you' versus su 'fire'; hotz 'cold' versus hots 'noise'; atzo 'yesterday' versus atso 'old woman'). Fricative versus affricate sibilant between vowels and at the end of a word (oso 'very' versus otso 'wolf'); apical versus laminal fricative also between vowels (hasi 'begin' versus hazi 'grow'). Tap /ɾ/ versus trill /r/ between vowels (ere 'also' versus erre 'burn'). Five vowels without length or nasality (the eastern dialect of Zuberoa adds /y/ and nasal vowels). Palatal consonants /ɲ ʎ c ɟ ʃ tʃ/, used also to form affectionate or diminutive variants of words (tt, dd, x in place of t, d, z). Voiced versus voiceless stops; northern dialects add aspirated stops and /h/. Accent: position of the accent in most dialects; accented versus unaccented words in the pitch-accent dialects.

Stress: weak accent fixed by position, with lexical exceptions; pitch accent in some dialects. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- written j is always a voiced palatal stop [ɟ] (jan [ɟˈan], jakin, jende); the recommended standard value is [j] and the most common southern value is [x], which the rules offer only through a word flag.
- palatalisation of n and l after i applies to every word unless it is listed as an exception, so loanwords and learned words are changed too (zinema [s̻iɲˈemˌa], injineru [inɟˈiɲeɾˌu]).
- no pitch-accent model: every word gets the same positional accent, so the accent contrasts of the western dialects (singular versus plural forms) and the marked words with initial accent cannot be rendered.
- sibilants are not voiced before voiced consonants, and there is no option for the western merger of the two alveolar series.
- no tune set is selected, so the generic default tunes are used; the accent is realised with the generic stress mechanism, not as a pitch rise on the second syllable.
- the rules contain long lists of case endings as suffix rules, and the comments in the rule file mark several choices as uncertain (the value of j, lenition of d and g).

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 6 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: u (u=s4: dur=114), d (d=s10: voi=1 lead=75), ɟ (d=s15: f2=148 f3=109 a3=56 a4=56 voi=1 lead=75), ɡ (g=s10: voi=1 lead=75), aɪ (a=s33: g1=69 g2=132 g3=105 glide=1 dur=135), ts̻ (t=s38 s=s39: hold=85; hold=70).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (nor, zer, non, noiz ...) ends as a statement does, from a high question word.

Sources: Hualde, José Ignacio (1991). Basque Phonology. London: Routledge. Hualde, José Ignacio and Ortiz de Urbina, Jon (eds.) (2003). A Grammar of Basque. Berlin: Mouton de Gruyter. Hualde, José Ignacio (1999). Basque accentuation. In van der Hulst (ed.), Word Prosodic Systems in the Languages of Europe. Berlin: Mouton de Gruyter. Hualde, José Ignacio; Elordieta, Gorka; Gaminde, Iñaki; Smiljanić, Rajka (2002). From pitch-accent to stress-accent in Basque. In Gussenhoven and Warner (eds.), Laboratory Phonology 7. Berlin: Mouton de Gruyter. Hualde, José Ignacio; Lujanbio, Oihana; Torreira, Francisco (2008). Lexical tone and stress in Goizueta Basque. Journal of the International Phonetic Association 38(1), 1-24. Hualde, José Ignacio; Lujanbio, Oihana; Zubiri, Juan Joxe (2010). Goizueta Basque. Journal of the International Phonetic Association 40(1), 113-127. And 3 more in the profile.

## Persian (`fa`)

Indo-European, Indo-Iranian, Iranian, Western Iranian (Southwestern). Described: Standard Iranian Persian (Tehran), careful educated speech, with notes on colloquial Tehran speech.

**What the language has.** Six vowel qualities in two sets: the historically long, stable vowels /iː ɒː uː/ and the historically short, unstable vowels /e æ o/; in Tehran speech the sets differ mainly in quality, length is secondary. Voiced versus voiceless obstruents; the voiceless stops and /tʃ/ are aspirated. One uvular phoneme /ɢ/ for both letters ق and غ: Tehran Persian has merged the older /q/ and /ɣ/; Dari, Tajik and some Iranian dialects keep them apart. Glottal stop /ʔ/ (letters ع and ء) as a consonant in careful speech. Single versus geminate consonants in careful speech, mainly in Arabic loans. /æ/ versus /ɒː/ (low front unrounded versus low back rounded).

Stress: fixed by word class, mostly word-final; realised as a pitch accent. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- word stress: no stress rule is set for fa, so the default penultimate rule applies wherever fa_rules or fa_list do not mark stress; nouns and adjectives mostly come out with penultimate or initial stress ([kˈetɑb], [mˈɑdar], [xˈɑneː], [ˈiːrɑn]) instead of final stress, and prefixed verbs are stressed on the stem instead of on mi-, be- or næ- ([mirˈavam], [narˈaftam]).
- ق and غ are both written q1 in fa_rules; the fa table defines no phoneme q1, so the result is the base q, a voiceless uvular stop, followed by an undefined '1', and --ipa prints 'q1'; the voiced stop [ɢ] and the fricative [ɣ] between vowels are missing.
- /k ɡ/ have no palatalised variants before front vowels or syllable-finally.
- ر is always the trill R; no tap between vowels.
- /n/ does not become [ŋ] before velars (رنگ gives [ranɡ]).
- word-final ه read as a vowel is long [eː] (خانه gives [xɑneː]); final /e/ is short.
- all eight vowel phonemes are declared 'starttype #i endtype #i' whatever their quality, which affects the choice of consonant transitions.
- the unwritten ezafe vowel is not supplied (کتاب من gives [ketɑb man]).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 15 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʔ (<q=s4: ms=50 hush=1), a (A=s5: dur=175), e (e=s6: dur=80), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), r (l=s10: tap=3 tapms=18 f2=109 f3=77), h (<h=s15: ms=70 whisper=44), q (k=s35: f2=68 f3=109 f1=118 burst=3), ɑ (A=s37: f1=91 f2=86 dur=175), ɹ (r=s9: f2=92 f3=77), ʊ (U=s44: dur=185), ʌ (OE=s50: f1=112 f2=87 f3=114 dur=126), iː (i=s52: dur=117), əʊ (@=s55: g1=94 g2=65 g3=93 glide=1 dur=208).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (چه, چی, کجا, چرا ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Majidi, Mohammad-Reza and Ternes, Elmar (1999). Persian (Farsi). In Handbook of the International Phonetic Association. Cambridge University Press (first published in Journal of the International Phonetic Association 21(2), 1991). Windfuhr, Gernot L. (1979). Persian Grammar: History and State of its Study. The Hague: Mouton. Windfuhr, Gernot and Perry, John R. (2009). Persian and Tajik. In Windfuhr (ed.), The Iranian Languages. London: Routledge. Lazard, Gilbert (1992). A Grammar of Contemporary Persian. Costa Mesa: Mazda Publishers. Samareh, Yadollah (1977). The Arrangement of Segmental Phonemes in Farsi. Tehran University Press. Mahootian, Shahrzad (1997). Persian. London: Routledge (Descriptive Grammars). And 9 more in the profile.

## Persian (Pinglish) (`fa-latn`)

Indo-European, Indo-Iranian, Iranian, Western Iranian (Southwestern). Described: Standard Iranian Persian (Tehran) written informally in Latin letters (Pinglish, Fingilish). The sounds are those of the fa profile; only the spelling differs, and because chat writing is colloquial, the colloquial Tehran forms noted below are frequent.

**What the language has.** Six vowel qualities in two sets: the historically long, stable vowels /iː ɒː uː/ and the historically short, unstable vowels /e æ o/; in Tehran speech the sets differ mainly in quality, length is secondary. Voiced versus voiceless obstruents; the voiceless stops and /tʃ/ are aspirated. One uvular phoneme /ɢ/ for the letters ق and غ, written gh or q in Latin letters. Glottal stop /ʔ/ as a consonant in careful speech, written with an apostrophe or left out in Latin letters. Single versus geminate consonants in careful speech, mainly in Arabic loans. /æ/ versus /ɒː/: the usual Latin spelling writes both as a, so this contrast is often not shown (some writers use aa or â for /ɒː/).

Stress: fixed by word class, mostly word-final; realised as a pitch accent. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Latin a is always /æ/ unless it is written aa or followed by an apostrophe, so /ɒː/ is lost in the usual spelling (khoda gives [xoda], madar [madar], iran [iran]).
- an apostrophe after a is read as the mark of /ɒː/, so the common use of the apostrophe for the glottal stop gives the wrong vowel and no [ʔ] (ba'd gives [bɑd]).
- word stress follows the default penultimate rule ([sˈalɑm], [kˈetab], [xˈahar], [mˈadar]) instead of final stress, and prefixed verbs are not stressed on the prefix.
- gh and q give q1 as in fa: the voiceless uvular stop of the base table followed by an undefined '1'; no [ɢ] or [ɣ].
- zh is read as [z] plus [h] (only jh gives [ʒ]), x is read as [ks] although it is a common spelling of /x/, and ei is read as two vowels [e.i] instead of the diphthong [ej] (kheili gives [xeˈili]).
- the word list fa_list is in Persian script, so Latin-letter words are read by letter rules only.
- /k ɡ/ have no palatalised variants, ر is always a trill, and /n/ does not become [ŋ] before velars, as in fa.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 10 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʔ (<q=s4: ms=50 hush=1), a (A=s5: dur=175), e (e=s6: dur=80), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), r (l=s10: tap=3 tapms=18 f2=109 f3=77), h (<h=s15: ms=70 whisper=44), q (k=s35: f2=68 f3=109 f1=118 burst=3), ɑ (A=s37: f1=91 f2=86 dur=175).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Majidi, Mohammad-Reza and Ternes, Elmar (1999). Persian (Farsi). In Handbook of the International Phonetic Association. Cambridge University Press (first published in Journal of the International Phonetic Association 21(2), 1991). Windfuhr, Gernot L. (1979). Persian Grammar: History and State of its Study. The Hague: Mouton. Windfuhr, Gernot and Perry, John R. (2009). Persian and Tajik. In Windfuhr (ed.), The Iranian Languages. London: Routledge. Lazard, Gilbert (1992). A Grammar of Contemporary Persian. Costa Mesa: Mazda Publishers. Samareh, Yadollah (1977). The Arrangement of Segmental Phonemes in Farsi. Tehran University Press. Mahootian, Shahrzad (1997). Persian. London: Routledge (Descriptive Grammars). And 9 more in the profile.

## Finnish (`fi`)

Uralic, Finnic. Described: Standard Finnish (yleiskieli); duration figures are from educated speakers from Jyväskylä (Lehtonen 1970).

**What the language has.** Vowel length (single versus double) for all eight vowels, in stressed and unstressed syllables alike. Consonant length (single versus geminate) for /p t k s m n l r/; /ŋ/ between vowels is always long [ŋː]. Three-way vowel series: front unrounded /i e æ/, front rounded /y ø/, back /u o ɑ/. Eighteen diphthongs contrasting with vowel sequences split by a syllable boundary. No voicing contrast in native stops apart from /t̪/ versus /d/; /b ɡ f ʃ/ occur only in loanwords.

Stress: fixed, word-initial. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- /h/ has a single realisation: no [x] or [ç] in syllable codas (kahvi, vihko, lahti) and no voiced [ɦ] between vowels.
- unstressed /i/ is replaced by a laxer vowel (phoneme I, printed [ɪ]) through ChangeIfUnstressed, although Finnish has no vowel reduction.
- boundary gemination is applied only after a short word list and four endings (fi_list $double; -lle, -nne, -sti, -tse); it is missing for most -e nouns, imperatives and infinitives and inside compounds (hernekeitto has single [k]).
- questions get a rising tune (intonation group 3 maps the question mark to the fall-rise 'comma' tune), whereas Finnish questions normally fall.
- the half-long second-syllable vowel after a light first syllable (tuli, kala) is not modelled; all single vowels have one length.
- length ratios are only approximated: a geminate stop adds a fixed 130 ms of closure (long_stop) and other geminates repeat the consonant, so the larger ratio for sonorants (about 1 : 2.5) and the position effects are not reproduced.
- single and double vowels share one formant target, so the more central quality of short vowels is absent.
- no utterance-final creaky or breathy voice.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 27 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s8: f2=91 burst=-4 vot=11), p (p=s9: vot=9), k (k=s10: vot=20), h (<h=s15: ms=70 whisper=44), b (b=s19: voi=1 lead=75), d (d=s20: f2=91 burst=-4 voi=1 lead=75), ɡ (g=s19: voi=1 lead=75), æ (E=s39: f1=124 f2=92 f3=92 dur=84), ø (oe=s4: dur=53), y (y=s5: dur=56), ai (a=s41: g1=43 g2=166 g3=113 glide=1 dur=72), æi (E=s42: f1=124 f2=92 f3=92 g1=61 g2=118 g3=108 glide=1 dur=171), oi (o=s43: g1=75 g2=250 g3=117 glide=1), ei (e=s44: g1=79 g2=101 g3=105 glide=1), ui (u=s46: g1=111 g2=250 g3=116 glide=1 dur=117), au (a=s48: g1=46 g2=69 g3=93 glide=1 dur=72), iu (i=s51: g1=113 g2=46 g3=82 glide=1 dur=117), æy (E=s52: f1=124 f2=92 f3=92 g1=62 g2=99 g3=86 glide=1 dur=171), uo (w=s56 o=s4: hold=55; dur=53), ie (j=s56 e=s4: hold=55; dur=53), yø (j=s57 oe=s4: f1=56 f2=111 f3=84 hold=55; dur=53).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (kuka, mikä, mitä, missä ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Suomi, Kari; Toivanen, Juhani; Ylitalo, Riikka (2008). Finnish Sound Structure: Phonetics, Phonology, Phonotactics and Prosody. Studia Humaniora Ouluensia 9. Oulu University Press. Lehtonen, Jaakko (1970). Aspects of Quantity in Standard Finnish. Studia Philologica Jyväskyläensia VI. University of Jyväskylä. Wiik, Kalevi (1965). Finnish and English Vowels. Annales Universitatis Turkuensis B 94. Turku. Iivonen, Antti; Harnud, Huhe (2005). Acoustical comparison of the monophthong systems in Finnish, Mongolian and Udmurt. Journal of the International Phonetic Association 35(1): 59-71. Suomi, Kari (1980). Voicing in English and Finnish Stops. Publications of the Department of Finnish and General Linguistics of the University of Turku. Suomi, Kari; Toivanen, Juhani; Ylitalo, Riikka (2003). Durational and tonal correlates of accent in Finnish. Journal of Phonetics 31: 113-138. And 5 more in the profile.

## Faroese (`fo`)

Indo-European, Germanic, North Germanic, West Scandinavian (Insular). Described: Faroese of the central area around Tórshavn, the variety most descriptions take as their base; dialect differences in the stops are noted.

**What the language has.** Aspirated versus unaspirated stops and affricates at the start of a word, all voiceless (t in tala against d in dalur, k in koma against g in góður); there are no voiced stops. Preaspirated versus plain stops after a vowel (koppur, hattur, takk with preaspiration against the unaspirated stops written bb, dd, gg). Every stressed vowel has a long and a short form, chosen by syllable structure, and the two often differ in quality: a is [ɛaː] long and [a] short, ó is [ɔuː] long and [œ] short, ú is [ʉuː] long and [ʏ] short, í is [ʊiː] long and [ʊi] short, ey is [ɛiː] long and [ɛ] short. Eight long diphthongs beside five long monophthongs. Palatal affricates /tʃʰ tʃ/ and /ʃ/ versus velar stops and /sk/, in part predictable from the following front vowel. Only three vowels [a ɪ ʊ] in unstressed syllables.

Stress: fixed initial in native words. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- stress is wrong in most words: the pronunciation list (about 228,000 entries) writes '%' before the first vowel of nearly every word, eSpeak NG reads '%' as 'unstressed', and no stress rule is set for fo, so the default rule puts the stress on a later syllable (eta is [eːdˈa], koppur [kɔhbːˈʊr], veður [veːvˈʊr]); Faroese has initial stress.
- the offglide of the diphthongs ei, ey, oy, í is written with the phoneme J, which in the base table is a voiced palatal stop, so eiga, oyra, seinni come out with a stop inside the vowel ([aɟːja]).
- long diphthongs are written as two vowel phonemes (E plus A:, O plus A:, O plus W:), which count as two syllables; the stress mark can then fall between the two halves (maður, dagur, bátur).
- several vowel phonemes of the table (2, 3, 8, 9) have no IPA name and print as digits in the IPA trace, and the phonemes 4 and 5 are declared as vowels but play consonant recordings.
- words that are not in the list are read by fo_rules, which has about one rule per letter: no vowel length rule, no preaspiration, no palatalisation apart from k and g before i, no skerping, ð always [v], and penultimate stress.
- the voiceless lateral before p, t, k is written with the dark l of the base table (mjólk, hjálpa), and the long vowels E: and W: have the length value of short vowels, as in the Icelandic table, whose definitions this table repeats.
- questions are given the generic question tune.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 35 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (r=s7: f2=92 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), ɫ (l=s12: f2=71 f3=91), h (<h=s13: ms=70 whisper=44), ɟ (d=s22: f2=135 f3=112 a3=56 a4=56), ʋ (v=s24: af=-14), ð (v=s25: f2=149 f3=110 a6=28 ab=48), θ (f=s26: f2=146 f3=110 a6=28 ab=48), χ (x=s2: f2=88), iː (i=s34: dur=117), ɪː (I=s35: dur=188), ɛ (E=s36: dur=84), ɑ (A=s37: f1=91 f2=86), aː (a=s38: dur=72), ɔ (O=s39: dur=85), ɔː (O=s40: dur=220), ɜ (OE=s41: f3=114 dur=84), 4 (A=s43: f1=85), 5 (l=s12: f2=71 f3=91), ɵ (Y=s46: f2=89 f3=107), ɵː (oe=s47: f1=110 f2=90 f3=111), 9 (OE=s36: dur=84), uː (u=s34: dur=117), ʊ (U=s49: dur=114), y (y=s5: dur=56), yː (y=s34: dur=117), œ (OE=s36: dur=84), œː (OE=s48: dur=171), oʊ (o=s56: g1=105 g2=129 g3=96 glide=1), oʊː (o=s57: g1=105 g2=129 g3=96 glide=1 dur=132), ø (oe=s4: dur=53).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (hvør, hvat, hvar, nær ...) ends as a statement does, from a high question word.

Sources: Árnason, Kristján (2011). The Phonology of Icelandic and Faroese. Oxford University Press. Thráinsson, Höskuldur; Petersen, Hjalmar P.; Jacobsen, Jógvan í Lon; Hansen, Zakaris Svabo (2004). Faroese: An Overview and Reference Grammar. Tórshavn: Føroya Fróðskaparfelag. Lockwood, W. B. (1955). An Introduction to Modern Faroese. Copenhagen: Munksgaard. Barnes, Michael P. and Weyhe, Eivind (1994). Faroese. In König and van der Auwera (eds.), The Germanic Languages. London: Routledge. Helgason, Pétur (2002). Preaspiration in the Nordic Languages: Synchronic and Diachronic Aspects. Doctoral dissertation, Stockholm University. Helgason, Pétur (2003). Faroese preaspiration. In Proceedings of the 15th International Congress of Phonetic Sciences, Barcelona.

## French (Belgium) (`fr-be`)

Indo-European, Romance, Western Romance, Gallo-Romance (langue d'oïl). Described: French as spoken in Wallonia and Brussels by speakers close to the local standard; stronger regional features (Liège, Hainaut) are noted as such.

**What the language has.** Four nasal vowels: /ɛ̃/ and /œ̃/ are kept apart (brin versus brun, empreinte versus emprunte), where most speakers in northern France have merged them. The contrast of patte and pâte (tache versus tâche, mal versus mâle) is kept, but as a length contrast [a] versus [aː] rather than by a back vowel quality. /ɛ/ versus long /ɛː/ (mettre versus maître, faite versus fête, bette versus bête, lettre versus l'être). Vowel length at the end of a word: a final vowel followed by written e is long (ami [ami] versus amie [amiː], bout versus boue, nu versus nue, armé versus armée), so many masculine and feminine forms differ. /e/ versus /ɛ/ in final open syllables (piqué versus piquais, né versus naît, future -ai versus conditional -ais). /o/ versus /ɔ/ and /ø/ versus /œ/ in closed syllables (côte versus cote, jeûne versus jeune). The usual French consonant contrasts, with /ɥ/ absent or marginal for many speakers.

Stress: phrase-final prominence, not lexical. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the voice is the voice of France with other number words: the only conditional entries for Belgium are septante and nonante in the word list; phonemes, rules and tunes are shared.
- brin and brun get different phoneme names (E~ and W~, printed [ɛ̃] and [œ̃]), but both phonemes play the same vowel data (vnasal/W_n) with the same length, so the contrast cannot be heard.
- no long /ɛː/: mettre and maître, faite and fête, bette and bête are identical.
- no length in final vowels: ami and amie, bout and boue, nu and nue, armé and armée are identical.
- /ɥ/ is a short [y] before i (huit [yˈit], lui [lyˈi]); the Belgian [w] is not available, nor the syllabic high vowels of lion, louer (lier [ljˈe], louer [lwˈe]).
- rose and chose have open [ɔ] ([ʁˈɔz], [ʃˈɔz]) where Belgian French has long close [oː].
- jeune is given the close vowel [ø], so jeune and jeûne differ only by length; the contrast is [œ] versus [øː].
- wagon is [vaɡˈɔ̃] with [v].

**What OpenEVV says.** Spoken by the module made from French (`frfx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (oe=s1: f3=114 dur=52), ə- (oe=s1: f3=114 dur=52), a (a=s5: f2=82 dur=49), e (e=s6: dur=59), i (i=s7: f1=111 dur=68), o (o=s8: f1=91 dur=44), u (u=s9: f1=113 f2=90 dur=68), b (b=s18: voi=1 lead=75), d (d=s18: voi=1 lead=75), ɡ (g=s18: voi=1 lead=75), y (y=s40: dur=68), ɛ (E=s41: dur=52), ɛ̃ (E=s43: dur=52 nas=100), œ̃ (oe=s43: dur=52 nas=100), ɔ̃ (c=s44: f2=87 dur=42 nas=100), œ (oe=s41: dur=52), a- (a=s5: f2=82 dur=49), ɔ (c=s47: f2=87 dur=42), ø (eu=s41: dur=52), ɪ (e=s46: f3=94 dur=59).

Melody: no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall. A question that wants yes or no rises at the end.
A question asked with a question word (qui, que, quoi, où ...) ends as a statement does, from a high question word.
Timing: last 118 per cent of the module's own.

Sources: Fougeron, Cécile and Smith, Caroline L. (1993). French. Journal of the International Phonetic Association 23(2), 73-76. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Hambye, Philippe and Simon, Anne Catherine (2012). The variation of pronunciation in Belgian French: from segmental phonology to prosody. In Gess, Lyche and Meisenburg (eds.), Phonological Variation in French: Illustrations from Three Continents. Amsterdam: John Benjamins. Pohl, Jacques (1983). Quelques caractéristiques de la phonologie du français parlé en Belgique. Langue française 60. Warnant, Léon (1997). Phonétique et phonologie. In Blampain, Goosse, Klinkenberg and Wilmet (eds.), Le français en Belgique. Louvain-la-Neuve: Duculot. Walter, Henriette (1982). Enquête phonologique et variétés régionales du français. Paris: Presses Universitaires de France. Simon, Anne Catherine (ed.) (2012). La variation prosodique régionale en français. Bruxelles: De Boeck-Duculot. And 4 more in the profile.

## French (Switzerland) (`fr-ch`)

Indo-European, Romance, Western Romance, Gallo-Romance (langue d'oïl). Described: French of western Switzerland (Suisse romande), centred on the cantons of Vaud and Neuchâtel where most of the described features are found; Geneva is closer to the French of France.

**What the language has.** Four nasal vowels: /ɛ̃/ and /œ̃/ are kept apart (brin versus brun). Front /a/ versus back /ɑ/, the second also long (patte [pat] versus pâte [pɑːt], tache versus tâche). /ɛ/ versus long /ɛː/ (mettre versus maître, faite versus fête). /e/ versus /ɛ/ in final open syllables (piqué versus piquais, né versus naît). /o/ versus /ɔ/ at the end of a word, which reference French lacks: peau [po] versus pot [pɔ], maux versus mot, saut versus sot (Vaud, Neuchâtel, Fribourg, Valais). Vowel length at the end of a word: a final vowel followed by written e is long or ends in a glide (ami [ami] versus amie [amiː] or [amij], nu versus nue, bout versus boue, armé versus armée). /o/ versus /ɔ/ and /ø/ versus /œ/ in closed syllables (côte versus cote, jeûne versus jeune).

Stress: phrase-final prominence, not lexical. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the voice is the voice of France with other number words: the only conditional entries for Switzerland are septante, huitante and nonante in the word list; phonemes, rules and tunes are shared.
- brin and brun get different phoneme names (E~ and W~, printed [ɛ̃] and [œ̃]), but both phonemes play the same vowel data (vnasal/W_n) with the same length, so the contrast cannot be heard.
- there is no back /ɑ/: pâte differs from patte only by a length mark on the same front [a] ([pˈaːt] against [pˈat]).
- no long /ɛː/: mettre and maître, faite and fête are identical.
- no final /ɔ/: peau and pot, maux and mot, saut and sot are all [o].
- no length or glide in final vowels: ami and amie, nu and nue, bout and boue, armé and armée are identical.
- rose and chose have open [ɔ] ([ʁˈɔz], [ʃˈɔz]) where Swiss French has long close [oː].
- jeune is given the close vowel [ø], so jeune and jeûne differ only by length; the contrast is [œ] versus [øː].

**What OpenEVV says.** Spoken by the module made from French (`frfx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (oe=s1: f3=114 dur=52), ə- (oe=s1: f3=114 dur=52), a (a=s5: f2=82 dur=49), e (e=s6: dur=59), i (i=s7: f1=111 dur=68), o (o=s8: f1=91 dur=44), u (u=s9: f1=113 f2=90 dur=68), b (b=s18: voi=1 lead=75), d (d=s18: voi=1 lead=75), ɡ (g=s18: voi=1 lead=75), y (y=s40: dur=68), ɛ (E=s41: dur=52), ɛ̃ (E=s43: dur=52 nas=100), œ̃ (oe=s43: dur=52 nas=100), ɔ̃ (c=s44: f2=87 dur=42 nas=100), œ (oe=s41: dur=52), a- (a=s5: f2=82 dur=49), ɔ (c=s47: f2=87 dur=42), ø (eu=s41: dur=52), ɪ (e=s46: f3=94 dur=59).

Melody: no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall. A question that wants yes or no rises at the end.
A question asked with a question word (qui, que, quoi, où ...) ends as a statement does, from a high question word.
Timing: last 118 per cent of the module's own.

Sources: Fougeron, Cécile and Smith, Caroline L. (1993). French. Journal of the International Phonetic Association 23(2), 73-76. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Métral, Jean-Pierre (1977). Le vocalisme du français en Suisse romande: considérations phonologiques. Cahiers Ferdinand de Saussure 31. Andreassen, Helene N.; Maître, Raphaël; Racine, Isabelle (2010). La Suisse. In Detey, Durand, Laks and Lyche (eds.), Les variétés du français parlé dans l'espace francophone: ressources pour l'enseignement. Paris: Ophrys. Racine, Isabelle and Andreassen, Helene N. (2012). A phonological study of a Swiss French variety: data from the canton of Neuchâtel. In Gess, Lyche and Meisenburg (eds.), Phonological Variation in French: Illustrations from Three Continents. Amsterdam: John Benjamins. Schwab, Sandra and Racine, Isabelle (2013). Le débit lent des Suisses romands: mythe ou réalité? Journal of French Language Studies 23(2). Walter, Henriette (1982). Enquête phonologique et variétés régionales du français. Paris: Presses Universitaires de France. And 5 more in the profile.

## Gaelic (Irish) (`ga`)

Indo-European, Celtic, Goidelic. Described: Traditional Gaeltacht Irish. There is no single spoken standard: the inventory follows Ní Chasaide (1999) and Ó Siadhail (1989), and Munster (West Kerry) values are given where dialects differ, because the rules of eSpeak NG are built on Munster pronunciation.

**What the language has.** Every consonant except /h/ comes in a broad (velarised) and a slender (palatalised) form; the contrast carries lexical and grammatical meaning (bó 'cow' against beo 'alive'; bád 'boat' against báid 'boats'). For velars the pair is velar against palatal: /k ɡ x ɣ ŋ/ against /c ɟ ç j ɲ/; for /sˠ/ the slender partner is postalveolar /ʃ/. Vowel length: five short vowels, five long vowels, and schwa in unstressed syllables. Tense against lax sonorants (written nn, ll, rr against n, l, r) in Connacht and Ulster, largely given up in Munster. Voicing in stops; voiceless stops are aspirated. Initial mutations (lenition and eclipsis) change the first consonant of a word by grammatical rule.

Stress: fixed initial in Connacht and Ulster; weight-sensitive in Munster. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- slender consonants are made by adding a separate [j] glide to a plain consonant, and only before certain vowel spellings; at the end of a word or before a consonant they often come out plain or broad (the final consonants of bliain, cailín, ainm and boird).
- broad consonants are not velarised; before front vowels the broad quality is imitated by an inserted [w] or schwa, which adds a syllable (naoi as [nəˈiː], gaoth as [ɡəˈeː], buí as [bwiː]).
- broad r is the English approximant [ɹ]; slender r is a trill, or [ʒ] between vowels (Éire); Irish has taps.
- slender d is the affricate [d͡ʒ] but slender t is a palatal stop [c] or [t͡ʃ], a mixture of dialect values.
- dialects are mixed: vowel rules are Munster-like (ceann with [au], ao as [eː], final -igh with [ɡ]) but stress stays on the first syllable, with at most a secondary stress on a later long vowel (bradán, amadán; none in cailín).
- broad and slender l and n differ only by the added glide; there are no dental or velarised laterals and nasals and no tense sonorants.
- words containing the letters j, k, q, w, x, y, z are handed to the English voice.
- IPA output prints the back vowel phoneme '0' as the letter A.

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 28 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=86), a (A=s5: f1=112 f2=90 dur=40), i̯ (i=s10: dur=40), u (u=s9: dur=52), t (t=s12: f2=91 burst=-4), r (l=s11: tap=3 tapms=18 f1=179), h (<h=s16: ms=70 whisper=44), d (d=s12: f2=91 burst=-4), d̪ (d=s12: f2=91 burst=-4), t̪ (t=s12: f2=91 burst=-4), x (S=s30: f2=78 a2=68 a3=0 a4=52 af=-4), ʁ (S=s31: f2=67 a2=68 a3=0 a4=52 af=-5 voi=1), χ (S=s3: f2=67 a2=68 a3=0 a4=52 af=-4), ɪ (X=s1: dur=86), eː (i=s34: f1=123 f3=107), ɐ (A=s35: f2=90 dur=40), ɛ (E=s36: dur=66), ɔ (c=s37: dur=41), ʊ (U=s38: dur=74), ŭ (u=s10: dur=40), A (a=s10: dur=40), oː (c=s40: f1=94 f3=93 dur=82), ɑː (a=s41: dur=78), uə (w=s43 x=s1: hold=55; dur=86), aɪ (A=s44: f1=112 f2=90 g1=67 g2=124 g3=108 glide=1 dur=81), aʊ (A=s45: f1=112 f2=90 g1=69 g2=70 g3=100 glide=1 dur=81).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (cé, cad, céard, cá ...) ends as a statement does, from a high question word.

Sources: Ní Chasaide, Ailbhe (1999). Irish. In Handbook of the International Phonetic Association. Cambridge University Press, 111-116. Ó Siadhail, Mícheál (1989). Modern Irish: Grammatical Structure and Dialectal Variation. Cambridge University Press. Ó Sé, Diarmuid (2000). Gaeilge Chorca Dhuibhne. Dublin: Institiúid Teangeolaíochta Éireann. Ó Cuív, Brian (1944). The Irish of West Muskerry, Co. Cork. Dublin Institute for Advanced Studies. de Bhaldraithe, Tomás (1945). The Irish of Cois Fhairrge, Co. Galway. Dublin Institute for Advanced Studies. Hickey, Raymond (2014). The Sound Structure of Modern Irish. De Gruyter Mouton. And 3 more in the profile.

## Gaelic (Scottish) (`gd`)

Indo-European, Celtic, Goidelic. Described: Lewis Gaelic (Outer Hebrides), the variety of the JIPA illustration (Nance & Ó Maolalaigh 2021); differences in other Hebridean and mainland dialects are noted.

**What the language has.** Two series of voiceless stops: unaspirated (written b d g) and aspirated (written p t c); there are no voiced stops. After a stressed vowel the aspirated stops are preaspirated, so the contrast there is preaspirated against plain. Broad against slender consonants: the slender partners of the dental stops are postalveolar affricates, of the velars palatal stops, of /s/ is /ʃ/, of /x/ is /ç/, of /ɣ/ is /j/. Three-way contrasts in laterals and in coronal nasals: velarised dental, plain alveolar, palatalised dental. Two rhotics: plain and palatalised. Vowel length, nine vowel qualities including back unrounded /ɯ ɤ/, and ten diphthongs. Nasal vowels, with a small functional load. In Lewis, a word accent that separates monosyllables from words of two or more syllables.

Stress: fixed, word-initial. Rhythm: stress-timed. Tone: pitch accent, 2 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- preaspiration is dropped after long vowels (bàta has none); the literature finds it shorter there, not absent.
- the kind of preaspiration is mixed: [h] before p and t but [x] or [ç] before c (mac as [maxk]), as in dialects such as Barra, while Lewis has [h] throughout and slender r as [ð] is a Lewis feature.
- there are no nasal vowels, also not after cn, gn (cnoc).
- no word accent and no mark of hiatus.
- the velarised dental nasal uses the plain [n] (phoneme n[ is marked temporary), so the three nasals are not fully kept apart.
- several vowel rules are marked uncertain in gd_rules (è, ò, oi, ia, ua); leat comes out with [ɛ] instead of [a].
- the voice is marked 'status testing'; the rule file is based on a description of the spelling, not on one dialect.
- IPA output prints the unaspirated stops as [b d ɡ] and most aspirated stops as plain [p t k].

**What OpenEVV says.** Spoken by the module made from British English (`engx`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (x=s1: dur=86), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=183), a (A=s5: f1=112 f2=90 dur=40), e (I=s6: f2=106 f3=109 dur=72), i (i=s7: dur=50), o (c=s8: f1=94 f3=93 dur=41), u (u=s9: dur=52), r (l=s10: tap=3 tapms=18 f1=179), ʎ (l=s13: f2=152 f3=115), h (<h=s15: ms=70 whisper=44), ɲ (n=s17: f2=155), d (d=s11: f2=91 burst=-4), ɕ (S=s25: a3=34 a4=32 a5=22 f2=128 f3=117), ɪ (X=s1: dur=86), ɛː (E=s34: dur=136), aː (A=s36: f1=112 f2=90 dur=81), ɔː (c=s37: dur=82), dʲ (d=s48: f2=129 f3=108 burst=-4), kʲ (k=s49: f2=129 f3=127).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (cò, dè, càite, cuin ...) ends as a statement does, from a high question word.

**Not yet.** The word accent of Lewis is not in eSpeak NG's reading.

Sources: Nance, Claire; Ó Maolalaigh, Roibeard (2021). Scottish Gaelic. Journal of the International Phonetic Association 51(2): 261-275. Ladefoged, Peter; Ladefoged, Jenny; Turk, Alice; Hind, Kevin; Skilton, St. John (1998). Phonetic structures of Scottish Gaelic. Journal of the International Phonetic Association 28: 1-41. Nance, Claire; Stuart-Smith, Jane (2013). Pre-aspiration and post-aspiration in Scottish Gaelic stop consonants. Journal of the International Phonetic Association 43(2): 129-152. Nance, Claire (2024). Scottish Gaelic. In Fox, Sue (ed.), Language in Britain and Ireland (3rd ed.). Cambridge University Press, 288-313. Borgstrøm, Carl Hj. (1940). The Dialects of the Outer Hebrides. Norsk Tidsskrift for Sprogvidenskap, supplementary volume 1. Oslo. Oftedal, Magne (1956). The Gaelic of Leurbost, Isle of Lewis. Norsk Tidsskrift for Sprogvidenskap, supplementary volume 4. Oslo. And 2 more in the profile.

## Guarani (`gn`)

Tupian, Tupí-Guaraní. Described: Paraguayan Guarani (avañeʼẽ) in the standard orthography of Paraguay (achegety).

**What the language has.** Six oral versus six nasal vowels in the stressed syllable: aka 'quarrel' versus akã 'head', pytu 'breath' versus pytũ 'dark', oke 'sleeps' versus okẽ 'door'. Central close /ɨ/ (written y) versus /i/ and /u/. Words are oral, nasal or nasal-oral as a whole; nasal and prenasalised consonants (m and mb, n and nd, ŋ and ng) alternate with the nasality of the word. Glottal stop (puso) between vowels. Stress on the last syllable versus marked earlier stress (tape versus áva). No voiced oral stops b d g and no trill in native words; l and the retroflex sibilant ʐ (written rr) come from Spanish loans.

Stress: lexical, final by default. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no nasal harmony: only the vowels written with a tilde are nasal, and nothing spreads to neighbouring vowels or voiced consonants (porã comes out with an oral o and r).
- the vowel /ɨ/ (y) uses the front rounded vowel of German ü (vowel file yy_4, IPA output y); its nasal partner ỹ uses a different, central and oral vowel file, so the pair neither matches nor is nasal.
- the puso is rendered as a short silence (phoneme _!) and not as a glottal stop.
- the modifier apostrophe U+02BC, which is often used for the puso, is not recognised and the word is spelled out letter by letter; only the ASCII apostrophe, U+2019 and U+02BB work.
- g̃ written with a combining tilde is read as plain g; the precomposed substitute ĝ is mapped to a retroflex nasal instead of the velar nasal or nasalised approximant.
- nd and nt are pronounced with a velar nasal ([ŋd], [ŋt]) instead of a dental one.
- v is pronounced as Spanish b ([b] or [β]) instead of the labiodental approximant [ʋ].
- rr is a trill, not the retroflex sibilant of Paraguayan speech.

**What OpenEVV says.** Spoken by the module made from Latin American Spanish (`esux`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: h (<h=s6: ms=70 whisper=44), d (d=s9: voi=1 lead=75), ɡ (g=s9: voi=1 lead=75), ʝ (Z=s22: f2=130 a4=0), ã (a=s27: nas=100), ẽ (e=s27: nas=100), ĩ (i=s27: nas=100), y (i=s28: f3=80).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (mbaʼe, mbaʼépa, máva, mávapa ...) ends as a statement does, from a high question word.

Sources: Estigarribia, Bruno (2020). A Grammar of Paraguayan Guarani. London: UCL Press. Gregores, Emma & Suárez, Jorge A. (1967). A Description of Colloquial Guaraní. The Hague: Mouton. Walker, Rachel (1999). Guaraní voiceless stops in oral versus nasal contexts: an acoustical study. Journal of the International Phonetic Association 29(1), 63-94. Clopper, Cynthia G. & Tonhauser, Judith (2013). The prosody of focus in Paraguayan Guaraní. International Journal of American Linguistics 79(2), 219-251. Kaiser, Eden (2008). Nasal spreading in Paraguayan Guaraní: introducing long-distance continuous spreading. Amerindia 32.

## Greek (Ancient) (`grc`)

Indo-European, Hellenic. Described: Classical Attic of the fifth and fourth centuries BC, in the reconstruction of Allen (1987). eSpeak NG does not follow this reconstruction: it speaks an Erasmian-type school pronunciation, with the classical vowel values but fricatives for φ θ χ, [z] for ζ and a stress accent in place of the pitch accent.

**What the language has.** Three series of stops: voiceless unaspirated /p t k/, voiceless aspirated /pʰ tʰ kʰ/ and voiced /b d ɡ/. Vowel length: short /i y e a o/ against long /iː yː eː ɛː aː ɔː uː/; the long mid vowels are close /eː/ (ει) and open /ɛː/ (η), and /ɔː/ (ω) beside /uː/ (ου, earlier [oː]). Consonant length: geminates such as λλ, μμ, νν, ππ, ττ, σσ, ρρ. Pitch accent: its place in the word, and on long vowels and diphthongs the choice between acute (rise) and circumflex (fall). /h/ at the beginning of a word (rough against smooth breathing). Front rounded /y yː/ (υ). Diphthongs with a short and with a long first element.

Stress: none: the word accent is one of pitch. Rhythm: mora-timed. Tone: pitch accent, 4 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- φ, θ, χ are fricatives [f θ x] (φ is defined as an 'affricate' played with the [f] sample), not the aspirated stops [pʰ tʰ kʰ] of Classical Attic.
- ζ is [z], not [zd].
- the pitch accent is replaced by stress: acute, grave and circumflex are all turned into one primary stress mark, so acute and circumflex sound alike and the grave is not lowered.
- stressed syllables are lengthened, which cuts across the quantity system.
- γ before κ, χ, ξ stays [ɡ]; only γγ gives [ŋɡ] (ἄγκυρα is given as [aɡkyra]).
- σ is not voiced before voiced consonants (κόσμος, Λέσβος).
- vowel length of α, ι, υ cannot be read from the spelling, and vowels written with a macron (ᾱ, ῑ) are not recognised: the word is broken up and spelled out.
- word-initial ῥ is [h] followed by a voiced trill.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 16 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=49), e (e=s5: dur=54), i (i=s6: dur=58), o (o=s4: dur=49), u (u=s7: dur=52), h (<h=s11: ms=70 whisper=44), b (b=s14: voi=1 lead=75), d (d=s14: voi=1 lead=75), ɡ (g=s14: voi=1 lead=75), ɛ (e=s30: f1=116 dur=54), ɔ (o=s31: f1=116 dur=49), y (i=s33: f3=80 dur=58), aɪ (a=s38: g1=69 g2=132 g3=105 glide=1 dur=135), ɛɪ (e=s40: f1=116 g1=88 g2=107 g3=98 glide=1 dur=149), oɪ (o=s41: g1=84 g2=197 g3=103 glide=1 dur=155), ɔɪ (o=s46: f1=116 g1=88 g2=199 g3=103 glide=1 dur=155).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no is said higher as a whole, with little or no rise at the end.

**Not yet.** eSpeak NG reads Ancient Greek with stress in place of its pitch accent.

Sources: Allen, W. Sidney (1987). Vox Graeca: A Guide to the Pronunciation of Classical Greek (3rd ed.). Cambridge University Press. Devine, A. M.; Stephens, Laurence D. (1994). The Prosody of Greek Speech. Oxford University Press. Probert, Philomen (2003). A New Short Guide to the Accentuation of Ancient Greek. London: Bristol Classical Press. Probert, Philomen (2006). Ancient Greek Accentuation: Synchronic Patterns, Frequency Effects, and Prehistory. Oxford University Press. Horrocks, Geoffrey (2010). Greek: A History of the Language and its Speakers (2nd ed.). Wiley-Blackwell. Sturtevant, Edgar H. (1940). The Pronunciation of Greek and Latin (2nd ed.). Philadelphia: Linguistic Society of America. And 1 more in the profile.

## Gujarati (`gu`)

Indo-European, Indo-Iranian, Indo-Aryan (Western zone). Described: Standard Gujarati (educated speech of central Gujarat: Ahmedabad, Vadodara).

**What the language has.** Four-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced. Modal versus murmured (breathy) vowels ([baɾ] 'twelve' : [ba̤ɾ] 'outside'), beside breathy voiced consonants: one of very few languages with both. Dental versus retroflex stops; /n/ : /ɳ/; /l/ : /ɭ/. Oral versus nasal vowels. Close-mid versus open-mid vowels /e/ : /ɛ/ and /o/ : /ɔ/, which the script does not distinguish. No vowel length contrast: the long and short i and u of the script are one phoneme each. Geminate consonants, best treated as clusters of two identical segments.

Stress: fixed penultimate, weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Murmured vowels do not exist: હ is always a separate voiceless [h] between two full vowels, so બહેન, બહાર, મહેનત are [bəheːn], [bʌhaːɾ], [məheːnʌt] for [bɛ̤n], [ba̤ɾ], [mɛ̤nət̪].
- Stress is assigned to the penultimate syllable before schwa deletion, so it often lands on a schwa and keeps it: સરકાર [səɾˈʌkaːɾ], છોકરી [cʰoːkˈʌɾi], બોલવું [boːlˈʌʋũ], ભારત [bʰaːɾˈʌt] for [səɾkaɾ], [tʃʰokɾi], [bolʋũ], [bʱaɾət̪].
- Nasalised /a/ is a nasalised schwa: આંખ [ʌ̃kʰ], પાંચ [pʌ̃c], માં [mʌ̃].
- ળ is the retroflex rhotic flap phoneme (ફળ prints [pʰʌr.]), not a lateral, and so merges with the flap allophone of /ɖ/.
- Only [eː] and [oː] exist: the open-mid vowels /ɛ ɔ/ cannot be produced from normal spelling.
- Vowel length follows the spelling of i and u although length is not contrastive.
- ફ is [pʰ] (ફૂલ [pʰuːl]); most speakers have [f].
- Breathy voiced stops and h come from the Hindi base table (voiced closure plus voiceless aspiration sample); intonation uses the generic tunes.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 28 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), tʰ (t=s5: f2=91 burst=-4 vot=68 asp=50), i (i=s8: dur=85), t (t=s11: f2=91 burst=-4 vot=16), p (p=s12: vot=13), k (k=s13: vot=28), ɳ (n=s19: f3=80), b (b=s22: voi=1 lead=75), d (d=s23: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s28: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s29: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s22: voi=1 lead=75), ʋ (v=s31: af=-14), ʂ (S=s35: a4=54 f2=87 f3=83 f4=88), h (<h=s18: ms=70 whisper=44), ʌ (OE=s42: f1=112 f2=87 f3=114 dur=126), ɪ (I=s44: dur=137), aː (a=s47: dur=72), ʊ (U=s50: dur=185), ʌ̃ (OE=s56: f1=112 f2=87 f3=114 dur=126 nas=100), ũ (u=s59: dur=86 nas=100), pʰ (p=s62: vot=65 asp=50), dʰ (d=s64: f2=91 burst=-4 voi=1 lead=75 brth=90 f0=-15), cʰ (t=s69: f2=135 f3=112 a3=56 a4=56 vot=75 asp=50), ɡʰ (g=s63: voi=1 lead=75 brth=90 f0=-15).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (શું, કોણ, ક્યાં, ક્યારે ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Cardona, George (1965). A Gujarati Reference Grammar. Philadelphia: University of Pennsylvania Press. Cardona, George & Suthar, Babu (2003). Gujarati. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Mistry, P. J. (1997). Gujarati phonology. In Kaye, Alan S. (ed.), Phonologies of Asia and Africa, vol. 2. Winona Lake: Eisenbrauns. Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. Pandit, Prabodh B. (1957). Nasalization, aspiration and murmur in Gujarati. Indian Linguistics 17, 165-172. Fischer-Jørgensen, Eli (1967). Phonetic analysis of breathy (murmured) vowels in Gujarati. Indian Linguistics 28, 71-139. And 7 more in the profile.

## Hakka Chinese (`hak`)

Sino-Tibetan, Sinitic, Hakka. Described: Sixian Hakka of Taiwan (Northern Sixian, Miaoli), which is the variety that eSpeak NG's tone values, its sandhi rule and its Pha̍k-fa-sṳ input correspond to; Meixian (Guangdong) values are given for comparison.

**What the language has.** Aspirated versus unaspirated in stops and affricates; no voiced stops. Voiced labiodental v against f. Three final nasals m n ŋ and three final stops p t k, all kept (unlike Mandarin). Four tones in open and nasal-final syllables and two in checked syllables. Apical (central) vowel ɨ against i after the sibilants. Syllabic nasals m̩, n̩, ŋ̍.

Stress: none (no lexical stress). Rhythm: syllable-timed. Tone: lexical tone, 6 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- only Pha̍k-fa-sṳ romanisation can be read: hak_list holds nothing but numerals, so Hakka written in Han characters is not spoken, although the language is flagged as using ideographs.
- the Sixian sandhi rule is applied only inside one written word (syllables joined by hyphens or written together): thiên-kông becomes 11 24 but thiên kông with a space keeps 24 24.
- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c ignores the clause type, and a question gives the same audio as a statement.
- the checked tones are not short in themselves: every vowel has length 250, and the checked syllable is shortened only by the time taken by the final stop (vowel about 210 ms against 280 ms measured).
- final p t k have a weak release burst after about 40 ms of closure, where Hakka has unreleased stops.
- rule gaps: the rhyme ie with the yangru mark is not covered (ngie̍t is misparsed), and chhṳ is given the alveolo-palatal affricate that belongs before i.
- the tone table uses a different pitch scale from the other tone languages (20 to 100 instead of 10 to 50), giving about 81 to 122 Hz at the default voice pitch (about 7 semitones, measured); this is wider than eSpeak's Mandarin and Cantonese but still narrower than natural speech.
- no tonal coarticulation.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 31 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=127), e (e=s5: dur=141), i (i=s6: dur=161), o (o=s7: dur=146), u (u=s8: dur=170), h (<h=s12: ms=70 whisper=44), th (t=s32: vot=70 asp=50), i. (i=s36: f1=114 f2=83 f3=87 dur=161), ai (a=s37: g1=53 g2=151 g3=117 glide=1 dur=135), au (a=s38: g1=57 g2=63 g3=97 glide=1 dur=135), eu (e=s39: g1=67 g2=55 g3=91 glide=1 dur=149), ia (y=s40 a=s4: hold=55; dur=127), iau (y=s40 a=s4 w=s40: hold=55; dur=127; hold=55), ie (y=s40 e=s5: hold=55; dur=141), io (y=s40 o=s7: hold=55; dur=146), iu (i=s41: g1=109 g2=53 g3=87 glide=1 dur=171), ua (w=s40 a=s4: hold=55; dur=127), ue (w=s40 e=s5: hold=55; dur=141), ui (u=s43: g1=95 g2=250 g3=110 glide=1 dur=181), o- (o=s7: dur=146), b (b=s15: voi=1 lead=75), d (d=s15: voi=1 lead=75), əl (a=s1 l: f1=76 dur=127), ɛ (e=s49: f1=116 dur=141), ɪ (i=s45: f1=142 f3=93 dur=161), ʌ (a=s52: f1=94 f2=85 dur=127), ɑː (a=s48: f1=110 f2=78 dur=183), iː (i=s55: dur=234), ɔː (o=s56: f1=116 dur=214), uː (u=s57: dur=253), eɪ (e=s62: g1=83 g2=109 g3=99 glide=1 dur=149).

Tones: 1 (0:20,30:20,100:40), 2 (0:12,100:10), 3 (0:32,100:11), 4 (0:49,100:50), 5 (0:22,100:20), 6 (0:50,100:48). The pitch is made from them, syllable by syllable.

Sources: Hashimoto, Mantaro J. (1973). The Hakka Dialect: A Linguistic Study of its Phonology, Syntax and Lexicon. Cambridge University Press. Lee, Wai-Sum & Zee, Eric (2009). Hakka Chinese. Journal of the International Phonetic Association 39(1), 107-111. Chung, Raung-fu (2004). Taiwan Kejia yuyin daolun [An introduction to the sounds of Taiwan Hakka]. Taipei: Wunan. Ministry of Education, Taiwan (2012). Kejiayu pinyin fang'an [Hakka romanisation scheme], with tone values for the Sixian, Hailu, Dapu, Raoping and Zhao'an varieties. Chen, Matthew Y. (2000). Tone Sandhi: Patterns across Chinese Dialects. Cambridge University Press.

## Hawaiian (`haw`)

Austronesian, Oceanic, Polynesian, Eastern Polynesian (Marquesic). Described: Standard Hawaiian as used across the islands and in the revitalisation movement (Parker Jones 2018, a speaker from Hawaiʻi island), with the older description of Elbert & Pukui (1979); Niʻihau speech differs (t for k, more taps for l).

**What the language has.** Short versus long vowels: Kona 'leeward' versus kōna 'his, hers', hui 'club' versus hūi 'halloo', pela 'mattress' versus pēla 'bail'. Glottal stop versus its absence, also word-initially: ʻaka 'laugh' versus aka 'shadow', kou 'your' versus koʻu 'my'. Eight consonants only; no voicing contrast, no sibilants, no contrast of t and k or of w and v. Diphthongs versus sequences of two syllables (loina with a diphthong, moena with two syllables).

Stress: weight-sensitive, counted in morae. Rhythm: mora-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the ʻokina is rendered as a short silence (phoneme _!) and not as a glottal stop or creak; at the start of a word it causes a long pause before the word and no consonant at all.
- w before a long vowel has no rule: wā and wō lose the w, and words such as uwē and ʻowā are spelled out letter by letter.
- the choice between [w] and [v] depends on the following vowel (v before i and e, w before a, o, u), whereas the literature conditions it on the preceding vowel: ʻewa, iwa, hewa come out with [w] where [v] is usual.
- a word with a long vowel gets its main stress on that vowel and no penultimate stress: mālama, kānaka, ʻōlelo are stressed on the first syllable instead of the penultimate; words with two long vowels get two equal main stresses.
- ae, ao, eu, oe, ou are two separate vowels; the long diphthongs are not defined.
- short a is never centralised.
- no devoicing or shortening at the end of a phrase.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 24 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (l=s8: f3=66), a (a=s4: dur=49), e (e=s5: dur=54), i (i=s6: dur=58), o (o=s4: dur=49), u (u=s7: dur=52), p (p=s9: vot=38), k (k=s10: vot=52 asp=50), h (<h=s13: ms=70 whisper=44), b (b=s16: voi=1 lead=75), d (d=s16: voi=1 lead=75), ɡ (g=s16: voi=1 lead=75), ʋ (v=s23: af=-14), aː (a=s32: dur=135), eː (e=s33: dur=149), iː (i=s34: dur=171), oː (o=s35: dur=155), uː (u=s36: dur=181), ai (a=s37: g1=53 g2=151 g3=117 glide=1 dur=135), au (a=s38: g1=57 g2=63 g3=97 glide=1 dur=135), ei (e=s39: g1=62 g2=123 g3=111 glide=1 dur=149), iu (i=s41: g1=109 g2=53 g3=87 glide=1 dur=171), ui (u=s42: g1=95 g2=250 g3=110 glide=1 dur=181), oi (o=s43: g1=63 g2=225 g3=115 glide=1 dur=155).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (aha, wai, hea, pehea ...) ends as a statement does, from a high question word.
Timing: last 88 per cent of the module's own.

Sources: Parker Jones, ʻŌiwi (2018). Hawaiian. Journal of the International Phonetic Association 48(1), 103-115. Elbert, Samuel H. & Pukui, Mary Kawena (1979). Hawaiian Grammar. Honolulu: University Press of Hawaii. Pukui, Mary Kawena & Elbert, Samuel H. (1986). Hawaiian Dictionary, revised and enlarged edition. Honolulu: University of Hawaii Press. Schütz, Albert J. (1981). A reanalysis of the Hawaiian vowel system. Oceanic Linguistics 20(1), 1-43. Schütz, Albert J. (1994). The Voices of Eden: A History of Hawaiian Language Studies. Honolulu: University of Hawaii Press. Parker Jones, ʻŌiwi (2010). A Computational Phonology and Morphology of Hawaiian. DPhil thesis, University of Oxford. And 2 more in the profile.

## Hebrew (`he`)

Afro-Asiatic, Semitic, Northwest Semitic, Canaanite. Described: General (non-Oriental) Modern Israeli Hebrew: no pharyngeals, uvular rhotic. The Oriental variety, with /ħ ʕ/ and an alveolar trill, is noted where it differs.

**What the language has.** Voicing in stops and fricatives. Place of stress: ˈboker 'morning' against boˈker 'cowboy', ˈberex 'knee' against beˈrex 'he blessed'. Stops against fricatives /p f/, /b v/, /k χ/; the pairs alternate within verb and noun paradigms but are separate phonemes. Five vowel qualities, no vowel length, no gemination in the general variety. /tʃ dʒ ʒ w/ occur in loanwords and names only.

Stress: lexical and contrastive, mostly final. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- The rules read pointed text. Ordinary unpointed words that are not in he_list or he_listx (about 300 entries) are spoken as consonant strings with no vowels, apart from a few endings: מלך gives [mlχ], דבר [dvr], בוקר [vvkr], כתבתי [χtvtˈi].
- Pointed words are recognised only when the marks come in the order listed in he_rules. With the Unicode canonical order (vowel point before dagesh or shin dot), or with a combination that is not listed (bet + dagesh + holam), the word is spelled out letter by letter with 'Invalid phoneme code' errors: שָׁלוֹם, דָּבָר, יַלְדָּה, בֹּקֶר.
- No stress rule is set, so the default penultimate stress applies, but Hebrew stress is mostly final: דָּבָר gives ˈdavar, גָּדוֹל ˈɡadol, חָבֵר ˈχaver, שָׁלוֹם ˈʃalom.
- Final vowel letters are pronounced as consonants in pointed words: יַלְדָּה ends in [h] and אֲנִי ends in [j].
- Furtive pataḥ is read after the consonant: רוּחַ gives [ˈruχa] for [ˈʁuaχ].
- /r/ is the alveolar trill R of the base table, not the uvular [ʁ] of the general variety.
- The he phoneme table is empty: all vowels and consonants are the generic base ones, without the lengthening of stressed and phrase-final vowels described by Laufer.
- No elision of /h/ and /ʔ/, no voicing assimilation, no language-specific intonation.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 20 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (a=s1: f1=76), ʔ (<q=s3: ms=50 hush=1), u (u=s4: dur=114), h (<h=s8: ms=70 whisper=44), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), ɡ (g=s11: voi=1 lead=75), χ (j=s2: f1=55 f2=88 f3=109), ɹ (l=s5: f3=66), əl (a=s1 l: f1=76), ɛ (e=s33: f1=116), ʌ (a=s35: f1=94 f2=85), ɑː (a=s32: f1=110 f2=78 dur=135), iː (i=s38: dur=171), uː (u=s40: dur=181), aɪ (a=s44: g1=69 g2=132 g3=105 glide=1 dur=135), eɪ (e=s45: g1=83 g2=109 g3=99 glide=1 dur=149).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (מי, מה, איפה, מתי ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent, last 118 per cent of the module's own.

Sources: Laufer, Asher (1990). Hebrew. Journal of the International Phonetic Association 20(2): 40-43. Reprinted in the Handbook of the International Phonetic Association, Cambridge University Press, 1999. Bolozky, Shmuel (1997). Israeli Hebrew phonology. In Alan S. Kaye (ed.), Phonologies of Asia and Africa, vol. 1. Winona Lake: Eisenbrauns. Most, Tova, Amir, Ofer & Tobin, Yishai (2000). The Hebrew vowel system: raw and normalized acoustic data. Language and Speech 43(3): 295-308. Silber-Varod, Vered, Sagi, Hagit & Amir, Noam (2016). The acoustic correlates of lexical stress in Israeli Hebrew. Journal of Phonetics 56: 1-14. Cohen, Evan-Gary, Silber-Varod, Vered & Amir, Noam (2018). The acoustics of primary and secondary stress in Modern Hebrew. Brill's Journal of Afroasiatic Languages and Linguistics 10: 1-19. Bat-El, Outi, Cohen, Evan-Gary & Silber-Varod, Vered (2019). Modern Hebrew stress: phonology and phonetics. Brill's Journal of Afroasiatic Languages and Linguistics 11(1): 96-118. And 6 more in the profile.

## Hindi (`hi`)

Indo-European, Indo-Iranian, Indo-Aryan (Central zone, Hindustani). Described: Modern Standard Hindi, educated speech of Delhi and western Uttar Pradesh (the variety of Ohala 1999).

**What the language has.** Four-way laryngeal contrast in stops and affricates at five places: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced (p pʰ b bʱ). Dental versus retroflex stops (t̪ : ʈ, d̪ : ɖ). Retroflex flaps /ɽ ɽʱ/ versus retroflex stops /ɖ ɖʱ/ (marginal: the flaps occur only after a vowel) and versus the alveolar tap /ɾ/. Phonemic vowel nasalisation on all ten vowels (/saːs/ 'mother-in-law' : /sãːs/ 'breath'). Three short lax vowels /ɪ ə ʊ/ against seven long peripheral vowels; length goes together with quality. Consonant gemination, word-medial only and only after /ɪ ə ʊ/ (/pət̪aː/ 'address' : /pət̪ːaː/ 'leaf'). /s/ versus /ʃ/; loan fricatives /f z/ are well established, /q x ɣ ʒ/ are kept only by some speakers.

Stress: weight-sensitive, weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Breathy voiced stops (b# d# d.# J# g#) are a modal voiced closure plus an added voiceless aspiration noise sample; the following vowel starts with modal voice and no F0 dip, so bʱ sounds like b followed by h. The IPA output writes them with ʰ (bʰ, dʰ, ɖʰ, ɡʰ, ɟʰ).
- /ɦ/ is the voiceless [h] of the base table (phoneme H imports base1/h), never breathy voiced.
- The [ɛ] and [ɔ] allophones of schwa next to /ɦ/ are missing for the inherent vowel: पहला, कहना, शहर, बहुत come out as [pʌhəlaː], [kʌhənaː], [ʃʌhəɾ], [bʌhʊt]; the schwa after /ɦ/ is not deleted either. The rule exists only for the independent letter अ.
- /ɽʱ/ (ढ़) is produced as the sequence flap + [h] + schwa: पढ़ना gives [pʌɽhənaː] with an extra syllable. The flap phoneme r. has no IPA name and prints as 'r.'.
- Schwa deletion is a context rule inside the phoneme definition and fails in words such as हरकत [hʌɾəkət] and उलझन [ʊləɟʰən] (expected [ɦərkət̪], [ʊldʒʱən]).
- Candrabindu inside a word gives a nasal vowel plus an alveolar [n] (दाँत [dãnt], चाँद [cãnd]); after an independent vowel or the inherent vowel no nasal vowel is made at all (आँख [aːnkʰ], हँसना [hʌnsənaː]).
- The palatal affricates are labelled as palatal stops (IPA c, ɟ); the aspirated c# simply calls the English [tʃ] of the base table, with no separate aspiration phase.
- The breathy velar g# carries dental place features in the phoneme table (vcd dnt stp); dentals print as plain t, d in IPA output.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 46 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f1=136 f2=81), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), tʰ (t=s5: f2=91 burst=-4 vot=67 asp=50), a (A=s6: f1=89 f2=89), e (e=s7: dur=53), i (i=s8: dur=56), o (o=s9: f2=113 dur=53), u (u=s10: f1=134 dur=57), t (t=s12: f2=91 burst=-4 vot=15), p (p=s13: vot=13), k (k=s14: vot=18), r (l=s11: tap=3 tapms=18 f2=109 f3=77), h (<h=s19: ms=70 whisper=44), ɳ (n=s20: f3=80), r. (l=s22: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s23: voi=1 lead=85), d (d=s24: f2=91 burst=-4 voi=1 lead=87), ɟ (d=s29: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s31: voi=1 lead=63), ʋ (v=s33: af=-14), ʂ (S=s37: a4=54 f2=87 f3=83 f4=88), ʌ (OE=s44: f1=112 f2=87 f3=114 dur=84), ɪ (I=s46: f3=90), ɛː (E:=s47: f1=116 f2=90), aː (a=s50: f1=87 f2=89 dur=72), oː (o=s51: f2=113), ʊ (U=s54: dur=114), uː (u=s55: f1=134 dur=117), ĩ (i=s56: dur=56 nas=100), ẽ (e=s58: dur=53 nas=100), ɛ̃ (E=s59: dur=84 nas=100), õ (o=s63: f2=113 dur=53 nas=100), ũ (u=s65: f1=134 dur=57 nas=100), aɪ (a=s66: g1=56 g2=144 g3=101 glide=1 dur=72), bʰ (b=s69: voi=1 lead=61 brth=90 f0=-15), dʰ (d=s70: f2=91 burst=-4 voi=1 lead=87 brth=90 f0=-15), ʈ (t=s71: f2=91 f3=79 f4=88 a4=52 a5=42 vot=9), ʈʰ (t=s73: f2=91 f3=79 f4=88 a4=52 a5=42 vot=60 asp=50), ɟʰ (d=s76: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75 brth=90 f0=-15), kʰ (k=s77: vot=92 asp=50).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (क्या, कौन, कहाँ, कहां ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Ohala, Manjari (1999). Hindi. In Handbook of the International Phonetic Association, Cambridge University Press, 100-103 (first published in Journal of the International Phonetic Association 24(1), 1994). Ohala, Manjari (1983). Aspects of Hindi Phonology. Delhi: Motilal Banarsidass. Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. Shapiro, Michael C. (2003). Hindi. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Lisker, Leigh & Abramson, Arthur S. (1964). A cross-language study of voicing in initial stops: acoustical measurements. Word 20(3), 384-422. Dixit, R. Prakash (1989). Glottal gestures in Hindi plosives. Journal of Phonetics 17, 213-237. And 15 more in the profile.

## Croatian (`hr`)

Indo-European, Balto-Slavic, Slavic, South Slavic (western group, Serbo-Croatian). Described: Standard Croatian (Neo-Štokavian Ijekavian norm). The codified norm has four pitch accents and post-accentual length; many educated speakers, especially in Zagreb, have stress without the tonal contrast and with reduced length contrasts.

**What the language has.** Four word accents in the norm: short falling (kȕća), long falling (mȃjka), short rising (vòda), long rising (rúka). Vowel length under the accent and in syllables after the accent (post-accentual length: jùnāk, genitive plural žénā). Postalveolar /t͡ʃ d͡ʒ/ (č, dž) versus alveolo-palatal /t͡ɕ d͡ʑ/ (ć, đ); many Croatian speakers merge the two series. Palatal /ʎ ɲ/ versus /l n/. Syllabic /r̩/, short or long, as a syllable nucleus that can carry the accent (krv, prst, trg, Hrvatska). Voiced versus voiceless obstruents, kept word-finally (grad [ɡraːd]).

Stress: free (lexical) pitch accent, restricted by position. Rhythm: mixed. Tone: pitch accent, 4 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- No pitch accent: the four accents are not distinguished and there are no tone phonemes. Accent marks in the text are ignored (kȕća, vòda, mâjka, grȃd read like the unmarked words), except that acute-marked vowels are read as long (rúka).
- No vowel length: the rules and word list give long vowels in a handful of words only (Hrvatska), so accented and post-accentual length are missing.
- Stress is always on the first syllable. That is right for falling accents but wrong for words with a rising accent on a later syllable (ljepòta, telèvīzija, interesàntan, Jugòslāvija).
- Syllabic r between consonants is a plain consonant (phoneme R2) and not a syllable nucleus: krv, prst, trg, vrt, smrt come out with no stressed syllable at all, and prvi, crkva, brzo, vrlo are stressed on the last vowel.
- Unstressed /a i u/ are replaced by reduced qualities (& [æ]-like, [ɪ], [ʊ]); the standard has no vowel reduction.
- The long jat reflex ije is read as two syllables [i.je] (mlijeko, lijep, dijete).
- The letter e is open-mid [ɛ] but close [e] after j, which has no basis in the language.
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 14 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=51), e (e=s5: dur=55), i (i=s6: dur=63), o (o=s7: dur=53), u (u=s8: dur=61), b (b=s16: voi=1 lead=75), d (d=s16: voi=1 lead=75), dʑ (d=s17 Z=s18: voi=1 lead=75 hold=85 f2=126 f3=122; a3=34 a4=55 a5=22 f2=126 f3=122 hold=70), tɕ (t=s19 S=s20: hold=85 f2=126 f3=122; a2=31 a3=34 a4=34 a5=22 f2=126 f3=122 hold=70), ɡ (g=s16: voi=1 lead=75), x (S=s32: f2=77 f3=107 a2=68 a3=0 a4=52 af=-4), ɛ (E=s5: dur=55), æ (a=s42: f1=85 f2=116 dur=51), ɪ (e=s55: f1=91 dur=55).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (ko, tko, šta, što ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

**Not yet.** The four accents are not in eSpeak NG's reading: stress is spoken, the rising and falling accents are not.

Sources: Landau, Ernestina; Lončarić, Mijo; Horga, Damir & Škarić, Ivo (1999). Croatian. In Handbook of the International Phonetic Association, 66-69. Cambridge University Press. Lehiste, Ilse & Ivić, Pavle (1986). Word and Sentence Prosody in Serbocroatian. Cambridge, MA: MIT Press. Inkelas, Sharon & Zec, Draga (1988). Serbo-Croatian pitch accent: the interaction of tone, stress, and intonation. Language 64, 227-248. Smiljanić, Rajka (2004). Lexical, Pragmatic, and Positional Effects on Prosody in Two Dialects of Croatian and Serbian: An Acoustic Study. New York: Routledge. Godjevac, Svetlana (2005). Transcribing Serbo-Croatian intonation. In Sun-Ah Jun (ed.), Prosodic Typology: The Phonology of Intonation and Phrasing. Oxford University Press. Browne, Wayles (1993). Serbo-Croat. In B. Comrie & G. G. Corbett (eds.), The Slavonic Languages. London: Routledge. And 3 more in the profile.

## Haitian Creole (`ht`)

French-based creole (Atlantic group). Described: Standard Haitian Creole based on the speech of Port-au-Prince and the west, in the official spelling of 1979-1980.

**What the language has.** Seven oral vowels /i e ɛ a ɔ o u/, with close-mid versus open-mid marked in the spelling (e versus è, o versus ò): pe 'be quiet' versus pè 'priest, fear'; bo 'kiss' versus bò 'side'. Three nasal vowels /ɛ̃ ã ɔ̃/ (written en, an, on) against the oral vowels and against oral vowel plus nasal consonant: pan [pã] 'peacock' versus pàn [pan] 'breakdown'; pen [pɛ̃] 'bread' versus pèn [pɛn] 'pain'; bon [bɔ̃] versus bòn [bɔn] 'maid'. Nasal vowel plus nasal consonant is a further possibility (written ann, enn, onn, anm): pann [pãn] 'to hang', venn [vɛ̃n] 'vein', chanm [ʃãm] 'room'. Voiced versus voiceless stops and fricatives, including /ʃ ʒ/ (ch, j). /ɣ/ (written r) versus /w/, only before unrounded vowels. No front rounded vowels in the basic variety: French u, eu correspond to /i/, /e/ or /ɛ/ (diri 'rice', ble 'blue'). High nasal vowels [ĩ ũ] are marginal (a few words of African origin and Vodou terms, as in oungan).

Stress: fixed, phrase-final; not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- there are no nasal vowels in the output: an, en, on are read as oral vowel plus [n] (pan [pˈan], pen [pˈen], pon [pˈon], mwen [mwˈen], manje [manjˈe]); the phoneme table defines three nasal vowels but no rule uses them.
- è and ò are read as close [e] and [o] (bèl [bˈel], fò [fˈo], tèt [tˈet]), so the contrasts e versus è and o versus ò are lost; the open-mid phonemes of the table are unused.
- ou is read as three segments [o u u] (bonjou [bonjouˈu], nou [nouˈu], moun [mouˈun]) instead of [u].
- j is read as the glide [j] instead of [ʒ] (jou, manje, bonjou).
- r is read as [h] instead of the velar fricative [ɣ] (rat [hˈat], kreyòl [khejˈol], frè [fhˈe]).
- ch is read as [ʃ] followed by [h] (chante [ʃhantˈe], chèz [ʃhˈez], machin [maʃhˈin]).
- ui is two vowels [u i] instead of [ɥi] (uit), and final ng is [ŋɡ] instead of [ŋ] (bilding).
- the number words in the word list are entered in ordinary spelling where phoneme codes are expected, so numbers are misread (1 is [yoˈun] with the French vowel [y], 5 is [sˈenk], 18 is [dizuˈit]), and 80 and 100 are given as French words with the French uvular r.

**What OpenEVV says.** Spoken by the module made from French (`frfx`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s5: dur=113), i (i=s6: dur=131), o (o=s7: dur=85), u (u=s6: dur=131), h (<h=s13: ms=70 whisper=44), b (b=s16: voi=1 lead=75), d (d=s16: voi=1 lead=75), ɡ (g=s16: voi=1 lead=75).

Melody: no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall. A question that wants yes or no rises at the end.
A question asked with a question word (kisa, kilès, kimoun, kote ...) ends as a statement does, from a high question word.

Sources: Valdman, Albert (2015). Haitian Creole: Structure, Variation, Status, Origin. Sheffield: Equinox. Valdman, Albert (1978). Le créole: structure, statut et origine. Paris: Klincksieck. Tinelli, Henri (1981). Creole Phonology. The Hague: Mouton. Dejean, Yves (1980). Comment écrire le créole d'Haïti. Outremont: Collectif Paroles. Cadely, Jean-Robert (2002). Le statut des voyelles nasales en créole haïtien. Lingua 112. Fattier, Dominique (2013). Haitian Creole. In Michaelis, Maurer, Haspelmath and Huber (eds.), The Survey of Pidgin and Creole Languages, volume II. Oxford University Press.

## Hungarian (`hu`)

Uralic, Ugric. Described: Educated Colloquial Hungarian (Budapest standard).

**What the language has.** Vowel length in seven pairs; in a/á and e/é the members also differ in quality: short rounded [ɒ] against long [aː], short open-mid [ɛ] against long close-mid [eː]. Consonant length (geminates) for nearly every consonant. Voicing in stops, fricatives and affricates. Palatal stops /c ɟ/ and palatal nasal /ɲ/ against dentals and velars. Four affricates /t͡s d͡z t͡ʃ d͡ʒ/. Front rounded vowels /y yː ø øː/.

Stress: fixed, word-initial. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- there is no general voicing assimilation: it happens only where a rule in hu_rules names the word or cluster (azt, fogkefe), so népdal, vízpart, hatból, rakd, lakásban and megszeretteti keep the voicing of the spelling.
- /n/ is not assimilated before velars, palatals or b: ing, hangya and különben are spoken with [n]; only n before p becomes [m].
- /h/ has one realisation: no [x] or [ç] in codas (doh, ihlet, technika), no [ɦ] between vowels, and the silent final h of méh is pronounced.
- /j/ after an obstruent at the end of a word stays a glide (lépj, kapj, dobj).
- yes/no questions get the general rising question tune; the Hungarian rise-fall with its peak on the penultimate syllable is not modelled.
- some coalesced clusters lose their length (egészség is given a single [ʃ]).
- IPA output prints short a as [ɑ]; the sound used is a rounded back vowel, so this is a labelling fault.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: i (i=s5: dur=56), o (o=s4: dur=53), t (t=s9: f2=91 burst=-4 vot=23), p (p=s10: vot=18), k (k=s11: vot=35), r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s16: ms=70 whisper=44), b (b=s20: voi=1 lead=75), d (d=s21: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s26: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), ɡ (g=s20: voi=1 lead=75), ɑ (A=s40: f1=91 f2=86), ɛ (E=s41: dur=84), ø (oe=s4: dur=53), y (y=s5: dur=56), iː (i=s42: dur=117), aː (a=s43: dur=72), uː (u=s42: dur=117), yː (y=s42: dur=117).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (ki, mi, hol, mikor ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent, last 88 per cent of the module's own.

Sources: Szende, Tamás (1994). Hungarian. Journal of the International Phonetic Association 24(2): 91-94. Siptár, Péter; Törkenczy, Miklós (2000). The Phonology of Hungarian. Oxford University Press. Gósy, Mária (2004). Fonetika, a beszéd tudománya. Budapest: Osiris. Gósy, Mária (2001). The VOT of the Hungarian voiceless plosives in words and in spontaneous speech. International Journal of Speech Technology 4: 75-85. Varga, László (2002). Intonation and Stress: Evidence from Hungarian. Palgrave Macmillan. Kenesei, István; Vago, Robert M.; Fenyvesi, Anna (1998). Hungarian. Routledge. And 5 more in the profile.

## Armenian (East Armenia) (`hy`)

Indo-European, Armenian. Described: Standard Eastern Armenian as spoken in Yerevan, in the reformed orthography of Armenia.

**What the language has.** Three-way laryngeal contrast in plosives and affricates: voiced, voiceless unaspirated, voiceless aspirated, kept in word-initial and word-final position. Trill /r/ against tap /ɾ/ (ser 'gender', seɾ 'love'). Dental against postalveolar affricates, three of each. Uvular fricatives /χ ʁ/ against glottal /h/. Six vowels, schwa among them; no vowel length. /f/ is rare and found mainly in loanwords.

Stress: fixed final, not contrastive. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- ղ /ʁ/ is sent to the phoneme r" (uvular trill, IPA ʀ); the uvular fricative that ph_armenian defines as Q is not used by the rules.
- ր /ɾ/ is the base phoneme r, an approximant of the English type [ɹ] before vowels; ռ is the trill R.
- Written voiced plosives and affricates that are pronounced aspirated are read as voiced: երգ gives [jerɡ], մարդ gives [mard], արջ gives [ardʒ].
- No devoicing in obstruent clusters: աղջիկ gives [aʀdʒik] for [ɑχtʃʰik].
- No schwa before a word-final ղ after a consonant: աստղ gives [astʀ] for [ɑstəʁ].
- A prothetic schwa is always put before initial sibilant plus stop (սպիտակ gives [əspitˈak]); in Yerevan speech it is variable and often absent.
- The voiced plosives are plain voiced and the unaspirated ones have no longer closure; the breathy and constricted voice qualities are not modelled.
- The default intonation tunes are used: no rise at the right edge of non-final words.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 17 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f2=88 dur=157), ɹ (r=s11: f2=92 f3=77), a (A=s6: dur=175), e (e=s7: f1=113 f2=81 dur=80), i (i=s8: dur=85), o (o=s9: f2=133 f3=91 dur=80), u (u=s10: f1=125 f2=124 dur=86), t (t=s13: vot=17), p (p=s14: vot=15), k (k=s15: vot=28), ʀ (r=s16: tap=3 tapms=18 f2=85 f3=112), h (<h=s20: ms=70 whisper=44), d (d=s25: voi=1 lead=75), ɡ (g=s25: voi=1 lead=75), aɪ (a=s47: g1=56 g2=146 g3=101 glide=1 dur=72), kʰ (k=s52: vot=85 asp=50), tʃʰ (C >h=s51: ms=45 whisper=46).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (ով, ինչ, որտեղ, երբ ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Seyfarth, Scott, Dolatian, Hossep, Guekguezian, Peter, Kelly, Niamh & Toparlak, Tabita (2024). Armenian (Yerevan Eastern Armenian and Beirut Western Armenian). Journal of the International Phonetic Association 54(1): 445-478. Seyfarth, Scott & Garellek, Marc (2018). Plosive voicing acoustics and voice quality in Yerevan Armenian. Journal of Phonetics 71: 425-450. Hacopian, Narineh (2003). A three-way VOT contrast in final position: data from Armenian. Journal of the International Phonetic Association 33(1): 51-79. Toparlak, Tabita (2019). Etudes phonétiques en arménien. Mémoire de master, Université Paris III Sorbonne Nouvelle. Formant values as published in Seyfarth et al. (2024). Dum-Tragut, Jasmine (2009). Armenian: Modern Eastern Armenian. Amsterdam: John Benjamins. Vaux, Bert (1998). The Phonology of Armenian. Oxford: Clarendon Press. And 2 more in the profile.

## Armenian (West Armenia) (`hyw`)

Indo-European, Armenian. Described: Standard Western Armenian of the diaspora, as spoken in Beirut, in the classical (Mashtotsian) orthography. There is no monolingual community; the realisation of the plosives depends on the majority language of the speaker's country.

**What the language has.** Two-way laryngeal contrast in plosives and affricates: voiced against voiceless (traditionally described as aspirated). The Western voiced series answers to the Eastern voiceless unaspirated series, and the Western voiceless series to both the Eastern voiced and the Eastern aspirated series: Eastern [pɑɾ] 'dance' is Western [bɑɾ], Eastern [bɑr] 'word' is Western [pʰɑɾ]. One rhotic, the tap /ɾ/: the trill of Eastern Armenian has merged with it. Dental against postalveolar affricates, two of each. Six vowels as in Eastern Armenian; a front rounded [ʏ] for written իւ varies with [ju], and [œ] for written էօ is found in a few loanwords and names. No vowel length and no gemination.

Stress: fixed final, with a few morphological exceptions. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- The conditional rules for Western Armenian in hy_rules (marked ?1) do not fire with this voice, although the voice file sets dictrules 1 (tested with the 1.53 build; apparently because tr_languages.c has no entry for hyw, so that Armenian script is handed to the hy translator). So the classical spelling is misread: word-initial յ stays [j] (Յակոբ gives [jaɡopʰ] for [hɑɡop]), ոյ stays [oj] (լոյս gives [lojs] for [lujs]) and final silent յ is pronounced (տղայ gives [dəʀaɪ] for [dəˈʁɑ]).
- ռ and ր remain two sounds (trill R and the approximant r); Western Armenian has a single tap.
- ր is the base phoneme r, an approximant of the English type before vowels, and ղ is the uvular trill r" instead of the fricative [ʁ].
- No devoicing in obstruent clusters and no loss of aspiration next to sibilants.
- The default intonation tunes are used: question-word questions do not end in a rise.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 17 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f1=87 f2=91 dur=157), tʰ (t=s5: vot=23), ɹ (r=s11: f2=92 f3=77), a (A=s6: dur=175), e (e=s7: f1=113 f2=79 f3=91 dur=80), i (i=s8: f1=114 f3=91 dur=85), o (o=s9: f2=133 dur=80), u (u=s10: f1=121 f2=130 dur=86), ʀ (r=s16: tap=3 tapms=18 f2=85 f3=112), h (<h=s20: ms=70 whisper=44), b (b=s24: voi=1 lead=75), d (d=s25: voi=1 lead=45), ɡ (g=s24: voi=1 lead=75), aɪ (a=s48: g1=56 g2=146 g3=101 glide=1 dur=72), kʰ (k=s53: vot=85 asp=50), dz (d=s54 z=s55: voi=1 lead=45 hold=85; hold=70), tʃʰ (C >h=s52: ms=45 whisper=46).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (ով, ինչ, ուր, երբ ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Seyfarth, Scott, Dolatian, Hossep, Guekguezian, Peter, Kelly, Niamh & Toparlak, Tabita (2024). Armenian (Yerevan Eastern Armenian and Beirut Western Armenian). Journal of the International Phonetic Association 54(1): 445-478. Kelly, Niamh E. & Keshishian, Lara (2021). Voicing patterns in stops among heritage speakers of Western Armenian in Lebanon and the US. Nordic Journal of Linguistics 44: 103-129. Kelly, Niamh E. & Keshishian, Lara (2019). The voicing contrast in stops and affricates in the Western Armenian of Lebanon. Proceedings of Interspeech 2019: 1721-1725. Toparlak, Tabita (2019). Etudes phonétiques en arménien. Mémoire de master, Université Paris III Sorbonne Nouvelle. Formant values as published in Seyfarth et al. (2024). Toparlak, Tabita & Dolatian, Hossep (2022). Intonation and focus marking in Western Armenian. Proceedings of the 4th Conference on Central Asian Languages and Linguistics (ConCALL-4): 81-94. Athanasopoulou, Angeliki, Vogel, Irene & Dolatian, Hossep (2017). Acoustic properties of canonical and non-canonical stress in French, Turkish, Armenian and Brazilian Portuguese. Proceedings of Interspeech 2017: 1398-1402. And 3 more in the profile.

## Interlingua (`ia`)

constructed language. Described: the Interlingua of the International Auxiliary Language Association (1951).

**What the language has.** Five vowels with no length contrast.

Stress: by rule, mostly penultimate. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 6 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: i (i=s4: dur=114), u (u=s4: dur=114), h (<h=s9: ms=70 whisper=44), b (b=s12: voi=1 lead=75), d (d=s12: voi=1 lead=75), ɡ (g=s12: voi=1 lead=75).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (qui, que, ubi, quando ...) ends as a statement does, from a high question word.

Sources: Gode, Alexander & Blair, Hugh (1951). Interlingua: a Grammar of the International Language.

## Indonesian (`id`)

Austronesian, Malayo-Polynesian, Malayic. Described: Standard Indonesian (Bahasa Indonesia) as spoken in Jakarta and Java; the regional first language of the speaker (Javanese, Sundanese, Batak and others) affects vowel quality and prosody.

**What the language has.** Six vowels including schwa; the spelling writes both /e/ and /ə/ as e. Voiced versus voiceless stops and affricates at four places. Four nasals m n ɲ ŋ. No vowel or consonant length, no tone. F, z, ʃ, x occur only in loanwords.

Stress: weak and non-contrastive; prominence belongs to the phrase rather than the word. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the letter e is guessed from stress: a stressed e becomes [ɛ] and an unstressed one [ə], so words with schwa in the penultimate syllable are wrong (besar, kecil, keras, emas come out with stressed [ɛ]); only a few words are corrected in the word list.
- final k is a released [k] (tidak, anak, bapak); the glottal stop appears only in a few listed words.
- ai and au are made diphthongs in closed syllables too, where the standard has two syllables (laut, baik, daun come out as one syllable).
- fixed penultimate stress with clearly longer and louder stressed vowels, where the literature finds weak or no word stress and a phrase-final pitch movement.
- no lowering of high and mid vowels in final closed syllables.
- final stops are released; sy is [ç] rather than [ʃ]; v is voiced [v].

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 11 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (E=s1: f1=93 f2=78), ʔ (<q=s3: ms=50 hush=1), ɹ (l=s5: f1=127 f3=68), i (i=s4: dur=114), u (u=s4: dur=114), h (<h=s9: ms=70 whisper=44), b (b=s12: voi=1 lead=75), d (d=s12: voi=1 lead=75), ɡ (g=s12: voi=1 lead=75), aʊ (a=s35: g1=57 g2=72 g3=97 glide=1 dur=131), aɪ (a=s38: g1=55 g2=127 g3=106 glide=1 dur=131).

Melody: no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall. A question that wants yes or no rises at the end.
A question asked with a question word (apa, siapa, mana, kapan ...) ends as a statement does, from a high question word.

Sources: Soderberg, Craig D. & Olson, Kenneth S. (2008). Indonesian. Journal of the International Phonetic Association 38(2), 209-213. Lapoliwa, Hans (1981). A Generative Approach to the Phonology of Bahasa Indonesia. Pacific Linguistics D-34. Canberra: Australian National University. van Zanten, Ellen (1989). The Indonesian Vowels: Acoustic and Perceptual Explorations. PhD dissertation, Leiden University. van Zanten, Ellen & van Heuven, Vincent J. (1984). The Indonesian vowels as pronounced and perceived by Toba Batak, Sundanese and Javanese speakers. Bijdragen tot de Taal-, Land- en Volkenkunde 140, 497-521. van Zanten, Ellen, Goedemans, Rob & Pacilly, Jos (2003). The status of word stress in Indonesian. In J. van de Weijer, V. J. van Heuven & H. van der Hulst (eds.), The Phonological Spectrum, vol. 2, 151-175. Amsterdam: John Benjamins. van Zanten, Ellen & Goedemans, Rob (2009). Prominence in Indonesian: stress, phrases, and boundaries. Wacana 11(2). And 5 more in the profile.

## Ido (`io`)

constructed language. Described: the norm of the Uniono por la Linguo Internaciona Ido.

**What the language has.** Five vowels with no length contrast.

Stress: by rule. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: u (u=s4: dur=114), h (<h=s8: ms=70 whisper=44), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), ɡ (g=s11: voi=1 lead=75), aʊ (a=s27: g1=71 g2=75 g3=97 glide=1 dur=135), eʊ (e=s28: g1=87 g2=64 g3=91 glide=1 dur=149), ts (t=s34 s=s35: hold=85; hold=70).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (qua, quo, ube, kande ...) ends as a statement does, from a high question word.

Sources: de Beaufront, Louis (1925). Kompleta Gramatiko detaloza di la linguo internaciona Ido.

## Icelandic (`is`)

Indo-European, Germanic, North Germanic, West Scandinavian (Insular). Described: Standard Icelandic in the majority (southern and Reykjavík) pronunciation, with unaspirated stops after vowels and voiceless sonorants before p, t, k; the northern 'hard' pronunciation is noted.

**What the language has.** Aspirated versus unaspirated stops at the start of a word, all voiceless (tala versus dala, panna versus banna, kala versus gala); there are no voiced stops. Preaspirated stops versus plain long stops after a short vowel (hattur [ˈhaʰtʏr] 'hat' versus haddur [ˈhatːʏr] 'hair'). Voiced versus voiceless sonorants at the start of a word (l versus hl, n versus hn, r versus hr: lið versus hlið). Palatal versus velar stops before back and front rounded vowels (kjör versus kör, gjóla versus góla). Long versus short consonants after a short vowel (vina versus vinna, which also differ in vowel length). Eight monophthongs and five diphthongs, all of which occur long and short by position. /θ/ and /ð/, in complementary distribution by position in the word.

Stress: fixed initial. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the long vowels E: and W: ([ɛː] and [œː]) have the same length value as the short vowels (130), while the other long vowels have 230, so gefa, vera and similar words have no long vowel.
- yes-no questions get the generic question tune with a final rise; Icelandic questions end in a fall after a late-rising nuclear accent.
- nn after a long vowel or diphthong at the end of a word gives a stop plus a voiced [n] (seinn, steinn), where the language has a voiceless [tn̥]; devoicing before a pause is written into the rules for l, ll and gn only.
- the rules for r insert extra segments: keyra comes out with a tap followed by a trill, ískra with a schwa before the r.
- the voiceless sonorants have IPA names that are not IPA (n#, l#, r#, m#), so the phoneme trace cannot be read by IPA tools; the voiceless nasals carry the attribute 'voiced' in the phoneme table.
- preaspiration is a plain [h] phoneme before an unaspirated stop; its length relative to the stop closure is not controlled.
- the pronunciation list has about 330 entries, so loans, names and irregular words are read by the letter rules (ll is always [tl], also in loans and pet names).
- only the majority pronunciation is available; there is no setting for the northern one.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 34 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɾ (l=s1: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), ɹ (r=s7: f2=92 f3=77), i (i=s5: dur=56), u (u=s6: dur=57), r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s13: ms=70 whisper=44), ɟ (d=s22: f2=135 f3=112 a3=56 a4=56), c (t=s22: f2=135 f3=112 a3=56 a4=56), ʋ (v=s24: af=-14), ð (v=s25: f2=149 f3=110 a6=28 ab=48), θ (f=s26: f2=146 f3=110 a6=28 ab=48), ɣ (r=s32: f1=73 f3=116), iː (i=s34: dur=117), ɪː (I=s35: dur=188), ɛ (E=s36: dur=84), aː (a=s37: dur=72), ɔ (O=s38: dur=85), ɔː (O=s39: dur=220), uː (u=s34: dur=117), y (y=s5: dur=56), yː (y=s34: dur=117), œ (OE=s36: dur=84), œː (OE=s40: dur=171), aɪ (a=s41: g1=56 g2=146 g3=101 glide=1 dur=72), aɪː (a=s42: g1=56 g2=146 g3=101 glide=1), eɪ (e=s43: g1=106 g2=89 g3=95 glide=1), eɪː (e=s44: g1=106 g2=89 g3=95 glide=1 dur=132), aʊ (a=s45: g1=58 g2=82 g3=93 glide=1 dur=72), aʊː (a=s46: g1=58 g2=82 g3=93 glide=1), oʊ (o=s47: g1=105 g2=129 g3=96 glide=1), oʊː (o=s48: g1=105 g2=129 g3=96 glide=1 dur=132), øyː (oe=s50: g1=79 g2=120 g3=108 glide=1 dur=132), r# (l=s8: tap=3 tapms=18 f2=109 f3=77).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (hver, hvað, hvar, hvenær ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Árnason, Kristján (2011). The Phonology of Icelandic and Faroese. Oxford University Press. Thráinsson, Höskuldur (1994). Icelandic. In König and van der Auwera (eds.), The Germanic Languages. London: Routledge. Thráinsson, Höskuldur (1978). On the phonology of Icelandic preaspiration. Nordic Journal of Linguistics 1, 3-54. Helgason, Pétur (2002). Preaspiration in the Nordic Languages: Synchronic and Diachronic Aspects. Doctoral dissertation, Stockholm University. Garnes, Sara (1976). Quantity in Icelandic: Production and Perception. Hamburg: Buske. Pétursson, Magnús (1974). Les articulations de l'islandais à la lumière de la radiocinématographie. Paris: Klincksieck. And 4 more in the profile.

## Lojban (`jbo`)

constructed language. Described: the baseline of the Logical Language Group.

**What the language has.** Six vowels, the sixth a schwa written y. A glottal stop, written with a full stop, and an h, written with an apostrophe, that only stands between vowels.

Stress: fixed, penultimate. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (a=s1: f1=76), u (u=s4: dur=114), h (<h=s8: ms=70 whisper=44), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), ɡ (g=s11: voi=1 lead=75), aɪ (a=s29: g1=69 g2=132 g3=105 glide=1 dur=135), eɪ (e=s30: g1=83 g2=109 g3=99 glide=1 dur=149).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.

Sources: Cowan, John Woldemar (1997). The Complete Lojban Language.

## Georgian (`ka`)

Kartvelian (South Caucasian). Described: Standard Georgian, based on the Kartlian dialect and spoken in Tbilisi.

**What the language has.** Three-way laryngeal contrast in stops and affricates: voiced, voiceless aspirated, ejective. One uvular, the ejective /qʼ/, with no plain or voiced partner. Back fricatives /x ɣ/ against glottal /h/. Five vowels, no length, no nasalisation, no diphthongs. No contrastive stress and no gemination within morphemes.

Stress: fixed initial, weak, not contrastive. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- There are no ejectives. პ ტ კ are the plain unaspirated stops p-, t-, k- of the consonants table, წ is an unaspirated [ts] and ყ is the plain uvular stop q; the ejective recordings in phsource/ustop are not used.
- ჭ /tʃʼ/ is the phoneme c (consonants/c2, a palatalised affricate with the IPA name c), so it differs from ჩ in place as well as in release.
- /qʼ/ has none of its fricative or glottal variants, and ღ and ხ are always velar.
- ვ is always [v]: no [f] or [ɸ] before voiceless consonants and no rounding after obstruents.
- Stress is strong: primary on the first syllable with secondary stresses on alternate later syllables (sˈakʰartʰvˌelo, mˈastsavlˌebeli) and the Tamil stress lengths and amplitudes. The literature describes weak initial stress cued by duration alone.
- A schwa is inserted inside the longest clusters, after r (მწვრთნელი gives [mtsvrətʰnˈeli]) and after the first consonant of გვფრცქვნი, where the inserted vowel even takes a primary stress ([ɡˈəvpʰrətsʰkʰvnˈi]).
- რ is the trill R; the literature describes a tap.
- The default intonation tunes are used: no rise at the end of each word and no low penult in questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 4 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (r=s10: f2=92 f3=77), t (t=s11: vot=17), ʊ (U=s47: dur=185), ʌ (OE=s53: f1=112 f2=87 f3=114 dur=126).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (ვინ, რა, სად, როდის ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Shosted, Ryan K. & Chikovani, Vakhtang (2006). Standard Georgian. Journal of the International Phonetic Association 36(2): 255-264. Vicenik, Chad (2010). An acoustic study of Georgian stop consonants. Journal of the International Phonetic Association 40(1): 59-92. The figures used here are from the preprint in UCLA Working Papers in Phonetics 107. Wysocki, Tamra (2004). Acoustic analysis of Georgian stop consonants and stop clusters. PhD dissertation, University of Washington. Cited from Vicenik (2010). Robins, R. H. & Waterson, Natalie (1952). Notes on the phonetics of the Georgian word. Bulletin of the School of Oriental and African Studies 14. Butskhrikidze, Marika (2002). The Consonant Phonotactics of Georgian. Utrecht: LOT. Chitoran, Ioana (1998). Georgian harmonic clusters: phonetic cues to phonological representation. Phonology 15: 121-141. And 5 more in the profile.

## Karakalpak (`kaa`)

Turkic, Kipchak (Kipchak-Nogai). Described: Literary Karakalpak of Karakalpakstan (Uzbekistan), based on the north-eastern dialect; Latin script (Cyrillic also in use).

**What the language has.** Nine vowels: front /i y e ø æ/ (i ú e ó á) and back /ɯ u o ɑ/ (ı u o a). Velar /k ɡ/ versus uvular /q ʁ/, tied to vowel backness in native words. Voiced versus voiceless obstruents. Sibilant shift typical of the Kipchak-Nogai group: /ʃ/ where most Turkic languages have /tʃ/ and /s/ where they have /ʃ/ (úsh 'three', bes 'five', tas 'stone').

Stress: fixed final by default, with morphological exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no stress rule is set for kaa, so the default penultimate stress applies (bala, kitaplar, úyler are stressed before the last syllable); Karakalpak stress is final.
- ı is the schwa phoneme @, which eSpeak cannot stress: words whose only vowel is ı get no stress at all (qız, mıń, jıldız).
- the phoneme table is a copy of the Kazakh one; the mid vowel ó (/ø/) has the short duration of the high vowels (100 against 200).
- every l that does not stand directly before a front vowel is dark [ɫ], also in front-vowel words (el, bel, kel-).
- the apostrophe-like letter ʼ that replaces Cyrillic ь and ъ has no rule.
- no labial on-glide for word-initial o and ó.
- unstressable suffixes and particles are not handled.
- t is the unaspirated base2 stop while p and k use aspirated samples.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 15 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), ʔ (<q=s4: ms=50 hush=1), e (e=s6: dur=80), o (o=s6: dur=80), ɫ (l=s13: f2=71 f3=91), h (<h=s14: ms=70 whisper=44), q (k=s34: f2=68 f3=109 f1=118 burst=3), ɪ (I=s36: dur=137), ɵ (Y=s37: f2=89 f3=107 dur=137), u (u=s8: dur=86), ʊ (U=s38: dur=185), ɑ (A=s39: f1=91 f2=86 dur=175), æ (E=s40: f1=124 f2=92 f3=92 dur=126), ʀ (r=s10: tap=3 tapms=18 f2=85 f3=112).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (ne, kim, qayda, qashan ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Menges, Karl H. (1947). Qaraqałpaq Grammar. Part One: Phonology. King's Crown Press. Kirchner, Mark (1998). Kazakh and Karakalpak. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge.

## Kazakh (`kk`)

Turkic, Kipchak (Kipchak-Nogai). Described: Standard Kazakh of Kazakhstan, Cyrillic script; acoustic values from one female speaker from the Zhambyl region (McCollum & Chen 2021).

**What the language has.** Front versus back vowel sets /e ɵ ɪ ʏ (æ)/ and /ɑ o ə ʊ/. Two vowel classes: the short, reducible high vowels /ə ɪ ʊ ʏ/ (ы і ұ ү) and the full vowels /ɑ æ e o ɵ/, the latter about twice as long. Velar /k ɡ/ versus uvular /q ʁ/, predictable from vowel backness in native words but free in loans. Voiced versus voiceless aspirated plosives. The vowel-glide units /ij/ (и) and /uw/ (у) behave as marginal phonemes.

Stress: disputed: traditionally fixed final; others describe initial intensity plus final pitch prominence, or phrase-level prominence only. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- у is always the glide [w], also after a consonant, so су 'water' comes out as [sw] with no vowel (expected [suw]).
- ы is the schwa phoneme @, which eSpeak cannot stress: words ending in a ы-syllable are stressed earlier (жұлдыз gets initial stress) and words whose only vowels are ы or и get no stress at all (қыз, ит).
- и is always [əj], also in front-vowel words (киім).
- ө has the short duration of the high vowels (100 against 200) although it is a full mid vowel; the short set should be ы і ұ ү.
- every л that does not stand directly before a front vowel is dark [ɫ], so codas of front-vowel words are velarised (ел, көл).
- ь and ъ are read as glottal stops.
- t is the unaspirated base2 stop while p and k use aspirated samples.
- no spirantisation of plosives between vowels and no labial harmony (both gradient in the language).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 24 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f1=136 f2=86 f3=122 dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), ʔ (<q=s4: ms=50 hush=1), r (l=s10: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), e (e=s6: f1=128 f2=110 f3=110 dur=80), o (o=s8: f1=131 f2=133 f3=125 dur=80), u (u=s9: dur=86), t (t=s11: f2=91 burst=-4 vot=28), p (p=s12: vot=49 asp=50), k (k=s13: vot=36), ɫ (l=s17: f2=71 f3=91), h (<h=s18: ms=70 whisper=44), b (b=s22: voi=1 lead=47), d (d=s23: f2=91 burst=-4 voi=1 lead=46), ɡ (g=s29: voi=1 lead=71), q (k=s40: f2=68 f3=109 f1=118 burst=3 vot=33), ɪ (I=s42: f1=128 dur=137), ɵ (@=s43: f1=115 f3=110 dur=157), ʊ (U=s44: f1=122 f2=114 f3=119 dur=185), ɑ (A=s45: f1=114 f2=107 f3=115 dur=175), æ (E=s46: f1=155 f2=112 f3=91 dur=126), ʀ (r=s14: tap=3 tapms=18 f2=85 f3=112).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (не, кім, қайда, қашан ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent, last 118 per cent of the module's own.

Sources: McCollum, Adam G. & Chen, Si (2021). Kazakh. Journal of the International Phonetic Association 51(2), 276-298. Vajda, Edward (1994). Kazakh phonology. In Edward H. Kaplan & Donald W. Whisenhunt (eds.), Opuscula Altaica: Essays Presented in Honor of Henry Schwarz. Western Washington University. Kirchner, Mark (1998). Kazakh and Karakalpak. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge. Muhamedowa, Raihan (2015). Kazakh: A Comprehensive Grammar. Routledge.

## Greenlandic (`kl`)

Eskaleut, Inuit. Described: West Greenlandic (Kalaallisut), central dialect, in the 1973 orthography.

**What the language has.** Three vowels /i u a/, each short or long. Consonant length: nearly every consonant occurs single and geminate. Velar against uvular: /k/ and /q/, /ɣ/ and /ʁ/. No voicing contrast in stops. No lexical stress and no lexical tone.

Stress: none. Rhythm: mora-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- ll is a short [ɬ]: the length of the geminate is lost (illu, Kalaallit).
- r before a consonant is spoken as a uvular trill or fricative followed by a short consonant (arfeq as [aʀfɛq], Qaqortoq as [qaqoʀtoq]); the literature has a long consonant after a uvularised vowel.
- /a/ is not retracted before q and r.
- prosody is stress-based: a primary stress is placed on the last long vowel or before a consonant cluster, otherwise on the final or the antepenultimate syllable; the HLH pattern on the last three morae is not modelled.
- questions get a rising tune, whereas Greenlandic yes/no questions end low and statements end high.
- word-final t after i is made an affricate [t͡ɕ] (Kalaallit, ippit); the literature has affrication of /t/ before /i/ only.
- final -ak, -ap, -at change the vowel to [æ], and final -ak ends in a voiced stop.
- all numbers are read in Danish, also 1 to 12, for which Greenlandic has its own words in the word list.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 10 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʀ (R=s9: f3=109), a (a=s4: dur=51), i (i=s6: dur=63), o (o=s7: dur=53), u (u=s8: dur=61), tɕ (t=s18 S=s19: hold=85 f2=126 f3=122; a2=31 a3=34 a4=34 a5=22 f2=126 f3=122 hold=70), ɣ (Z=s31: f2=77 f3=107 a2=68 a3=0 a4=52 af=-4), q (k=s33: f2=68 f3=109 f1=118 burst=3 vot=30), ɬ (l=s34: fric=52 a3=54 a4=58 a5=44 whisper=30), ɛ (E=s5: dur=55).

Melody: no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (kina, suna, sumi, qanga ...) ends as a statement does, from a high question word.

Sources: Fortescue, Michael (1984). West Greenlandic. London: Croom Helm. Rischel, Jørgen (1974). Topics in West Greenlandic Phonology: Regularities Underlying the Phonetic Appearance of Wordforms in a Polysynthetic Language. Copenhagen: Akademisk Forlag. Jacobsen, Birgitte (2000). The question of 'stress' in West Greenlandic: an acoustic investigation of rhythmicization, intonation, and syllable weight. Phonetica 57: 40-67. Arnhold, Anja (2014). Prosodic structure and focus realization in West Greenlandic. In Jun, Sun-Ah (ed.), Prosodic Typology II. Oxford University Press, 216-251. Nagano-Madsen, Yasuko (1992). Mora and Prosodic Coordination: A Phonetic Study of Japanese, Eskimo and Yoruba. Travaux de l'institut de linguistique de Lund 27. Lund University Press. Nagano-Madsen, Yasuko (1993). Phrase-final intonation in West Greenlandic Eskimo. Working Papers 40: 145-155. Lund University, Department of Linguistics. And 3 more in the profile.

## Kannada (`kn`)

Dravidian, South Dravidian. Described: Standard Kannada (educated speech of the Mysore and Bangalore area), formal style.

**What the language has.** Vowel length for five vowel qualities. Single versus geminate consonants. Voiced versus voiceless stops in all vocabulary; aspirated and breathy voiced stops in Sanskrit and other loans, kept in educated formal speech and mostly lost colloquially. Dental versus retroflex stops; alveolar versus retroflex nasal and lateral. /ɲ ŋ/ occur almost only before homorganic stops. /f z/ in Perso-Arabic and English loans; /ʃ/ and /ʂ/ are merged by most speakers.

Stress: no lexical stress; weak fixed prominence, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- ರ /r/ imports base1/r, the English approximant [ɹ] (IPA output [mˈɐɹɐ] for ಮರ), instead of a tap or trill.
- in the phoneme table short a carries the lng flag while the long vowels do not; the table is headed 'these are only guesses'.
- no on-glides for word-initial e and o.
- stress is fixed on the first syllable with stress-accent settings, and automatic secondary stress can fall on a short vowel next to an unstressed long one (ಕರ್ನಾಟಕ gives [kˈɐrnaːʈˌɐkɐ]).
- the obsolete letter ೞ (historical retroflex approximant, now /ɭ/) is read as [fa].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 27 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: tʰ (t=s4: f2=91 burst=-4 vot=68 asp=50), ɹ (r=s8: f2=92 f3=77), ɐ (A=s9: f1=85), e (e=s5: dur=53), i (i=s6: dur=56), o (o=s5: dur=53), u (u=s7: dur=57), t (t=s11: f2=91 burst=-4 vot=16), p (p=s12: vot=13), k (k=s13: vot=28), ɭ (l=s16: f2=111 f3=71), h (<h=s18: ms=70 whisper=44), d (d=s23: f2=91 burst=-4 voi=1 lead=75), ɡ (g=s22: voi=1 lead=75), ʂ (S=s35: a4=54 f2=87 f3=83 f4=88), iː (i=s43: dur=117), aː (a=s46: dur=72), uː (u=s43: dur=117), aɪ (a=s58: g1=56 g2=146 g3=101 glide=1 dur=72), bʰ (b=s61: voi=1 lead=75 brth=90 f0=-15), ʈ (t=s63: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s64: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75), b (b=s22: voi=1 lead=75), ʌ (OE=s42: f1=112 f2=87 f3=114 dur=84).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (ಏನು, ಯಾರು, ಎಲ್ಲಿ, ಯಾವಾಗ ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Sridhar, S. N. (1990). Kannada. London: Routledge (Descriptive Grammars). Schiffman, Harold F. (1983). A Reference Grammar of Spoken Kannada. Seattle: University of Washington Press. Steever, Sanford B. (1998). Kannada. In Steever (ed.), The Dravidian Languages. London: Routledge. Upadhyaya, U. P. (1972). Kannada Phonetic Reader. Mysore: Central Institute of Indian Languages. Krishnamurti, Bhadriraju (2003). The Dravidian Languages. Cambridge University Press.

## Korean (`ko`)

Koreanic. Described: Standard Seoul Korean.

**What the language has.** Three-way contrast in stops and affricates, all voiceless at the start of a word: lenis /p t k t͡ɕ/, fortis /p͈ t͈ k͈ t͈͡ɕ/, aspirated /pʰ tʰ kʰ t͡ɕʰ/. Two-way contrast in fricatives: lenis /s/ against fortis /s͈/. Back unrounded /ɯ ʌ/ against back rounded /u o/. Onglide diphthongs with /j/ and /w/, and /ɰi/. No lexical stress, tone or (for most speakers born after about 1970) vowel length.

Stress: none. Rhythm: syllable-timed. Tone: tonogenesis in progress, 2 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- lenis ㄱ is reversed: voiced [ɡ] at the start of a word and a voiceless uvular stop [q] between vowels and in codas (고기 is given as [ɡoqi], 한국어 as [hanquqʌ]); ㄷ is voiced [d] everywhere, also word-initially; only ㅂ and ㅈ are voiceless initially and voiced medially.
- no nasalisation of ㄱ and ㅂ codas before a nasal: 입니다, 감사합니다, 국물 and 먹는 keep a stop.
- no lateralisation and no change of ㄹ to [n]: 신라, 심리 and 독립 keep a tap after the consonant.
- ㅅ and ㅆ are the same sound (the fortis phoneme is a copy of the plain one, marked temporary), and neither becomes [ɕ] before i.
- fortis stops are plain unaspirated stops without long closure or tense voice; word-initial ㄲ uses the uvular stop sample.
- the consonant has no effect on the pitch of the next vowel, so the main present-day cue to lenis against aspirated stops is missing.
- prosody is stress-based (first syllable if heavy, otherwise the second) with generic tunes; the accentual phrase pattern and the boundary tones are not modelled.
- ㅎ plus a lenis stop gives a sequence of two stops (좋다 as [t͡ɕot tʰa]) instead of one aspirated stop, and ㅎ at the start of a syllable is a full [h] also between voiced sounds.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 23 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʌ (c=s1: f2=115 f3=112), ɹ (l=s10: f1=127 f3=68), ɐ (a=s11: f1=82 f2=92), e (e=s6: f1=112), i (i=s7: f1=130 f3=110 dur=114), o (o=s8: f3=110), u (u=s9: f1=135 f2=126 f3=110 dur=114), t (t=s12: vot=25), ɫ (l=s16: f2=67 f3=111), h (<h=s17: ms=70 whisper=44), d (d=s20: voi=1 lead=75), dʑ (d=s21 Z=s22: voi=1 lead=75 hold=85 f2=126 f3=122; a3=34 a4=55 a5=22 f2=126 f3=122 hold=70), tɕ (t=s23 S=s24: hold=85 f2=126 f3=122; a2=31 a3=34 a4=34 a5=22 f2=126 f3=122 hold=70), ɡ (g=s20: voi=1 lead=75), q (k=s38: f2=68 f3=109 f1=118 burst=3 vot=30), ɛ (E=s40: f1=110), ɯ (E=s41: f1=76 f2=80), kh (k=s42: vot=126 asp=50), t- (t=s12: vot=25), ph (p=s43: vot=91 asp=50), q- (k=s38: f2=68 f3=109 f1=118 burst=3 vot=30), tɕ- (t=s23 S=s24: hold=85 f2=126 f3=122; a2=31 a3=34 a4=34 a5=22 f2=126 f3=122 hold=70), d- (d=s20: voi=1 lead=75).

Melody: no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall. A question that wants yes or no rises at the end.
Timing: last 118 per cent of the module's own.

**Not yet.** The pitch that follows from the first consonant of a phrase is not spoken.

Sources: Lee, Hyun Bok (1999). Korean. In Handbook of the International Phonetic Association. Cambridge University Press, 120-123. Shin, Jiyoung; Kiaer, Jieun; Cha, Jaeeun (2013). The Sounds of Korean. Cambridge University Press. Sohn, Ho-Min (1999). The Korean Language. Cambridge University Press. Lisker, Leigh; Abramson, Arthur S. (1964). A cross-language study of voicing in initial stops: acoustical measurements. Word 20: 384-422. Cho, Taehong; Jun, Sun-Ah; Ladefoged, Peter (2002). Acoustic and aerodynamic correlates of Korean stops and fricatives. Journal of Phonetics 30(2): 193-228. Silva, David J. (2006). Acoustic evidence for the emergence of tonal contrast in contemporary Korean. Phonology 23: 287-308. And 5 more in the profile.

## Konkani (`kok`)

Indo-European, Indo-Iranian, Indo-Aryan (Southern zone, closest to Marathi). Described: Goan Konkani, the standard written in Devanagari (based on the Antruzi dialect); Mangalorean and Christian Goan varieties differ in vowels and vocabulary.

**What the language has.** Four-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced. Alveolar affricates /ts tsʰ dz dzʱ/ versus palatal affricates /tʃ tʃʰ dʒ dʒʱ/, written with the same letters. Plain versus breathy voiced (aspirated) sonorants: /m n ɳ l ɾ ʋ/ : /mʱ nʱ ɳʱ lʱ ɾʱ ʋʱ/. Dental versus retroflex stops; /n/ : /ɳ/; /l/ : /ɭ/. Nine oral vowels, with /e/ : /ɛ/ and /o/ : /ɔ/ and two central vowels, none of these contrasts shown in the script. Oral versus nasal vowels for all nine qualities; nasality carries grammatical meaning (/hɛ/ 'these' : /hɛ̃/ 'this, neuter'). No vowel length contrast in the Goan varieties. No contrastive stress or tone.

Stress: not contrastive, weak. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The translator source has no entry for Konkani, so the Devanagari letter classes (vowel sign, consonant) are never set up and every rule that tests them fails. After a consonant each vowel sign and the anusvara is spoken by its name: भारत comes out as [bʰəaːkaːrɾət], देव as [dəeːkaːrwə], कोंकणी as [kəoːkaːrŋkəɳikaːɾ], हांव as [həaːkaːrshɪɾʌwinduwə]. Only words without vowel signs (घर, जग, फळ) and listed words are read correctly, so the voice is unusable for ordinary text.
- For the same reason the default stress rule (penultimate) and default settings apply instead of the Indic ones.
- The phoneme table is a copy of the Hindi table with a few length changes: there is no central /ɨ/, and /ɛ ɔ/ exist only as the Hindi long vowels.
- The rules give च, ज, झ the palatal phonemes only; the alveolar affricates /ts dz dzʱ/ are missing.
- Breathy sonorants are sonorant plus [h]; breathy voiced stops are a voiced closure plus a voiceless aspiration sample.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 29 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f1=116 f2=73 dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), i (i=s8: f1=122 dur=85), u (u=s10: f1=141 f2=121 dur=86), t (t=s12: f2=91 burst=-4 vot=16), p (p=s13: vot=13), k (k=s14: vot=28), h (<h=s19: ms=70 whisper=44), b (b=s23: voi=1 lead=75), d (d=s24: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s29: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s23: voi=1 lead=75), ʂ (S=s36: a4=54 f2=87 f3=83 f4=88), ʌ (OE=s43: f1=112 f2=87 f3=114 dur=126), ɪ (I=s45: dur=137), eː (e=s46: f1=113 f2=88 f3=89), aː (a=s49: f1=84 dur=72), oː (o=s50: f1=113 f2=121), ɔː (O=s51: dur=220), ʊ (U=s53: dur=185), bʰ (b=s68: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s69: f2=91 burst=-4 voi=1 lead=75 brth=90 f0=-15), cʰ (t=s74: f2=135 f3=112 a3=56 a4=56 vot=75 asp=50).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (कितें, कोण, खंय, केन्ना ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Miranda, Rocky V. (2003). Konkani. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Almeida, Matthew (1989). A Description of Konkani. Panaji: Thomas Stephens Konknni Kendr. Katre, Sumitra Mangesh (1966). The Formation of Konkani. Poona: Deccan College. Sardesai, Madhavi (1986). Some Aspects of Konkani Grammar. Dissertation, Deccan College, Pune. Fadte, Swapnil; Vaz Fernandes, Edna; Karmali, Ramdas & Pawar, Jyoti D. (2022). Acoustic analysis of vowels in Konkani. ACM Transactions on Asian and Low-Resource Language Information Processing 21(5), 1-13. Fadte, Swapnil; Vaz, Edna; Ojha, Atul Kr.; Karmali, Ramdas & Pawar, Jyoti D. (2023). Empirical analysis of oral and nasal vowels of Konkani. arXiv:2305.10122. And 2 more in the profile.

## Kurdish (`ku`)

Indo-European, Indo-Iranian, Iranian, Western Iranian (Northwestern). Described: Kurmanji (Northern Kurdish) as written in the Hawar Latin alphabet; standard based on the Botan-type dialects of southeastern Turkey, with notes on dialect variation.

**What the language has.** Aspirated versus unaspirated voiceless stops and affricate: /pʰ p/, /tʰ t/, /kʰ k/, /tʃʰ tʃ/; together with the voiced series /b d ɡ dʒ/ a three-way laryngeal contrast; the Hawar alphabet does not write the difference. Pharyngeal fricatives /ħ ʕ/ in Arabic loans and, in many dialects, in some native words (heft 'seven' with [ħ]); written h, or not at all, in the standard spelling (optional letters ḧ and an apostrophe exist). Pharyngealised (emphatic) consonants such as [sˤ tˤ zˤ] in a limited set of words in many dialects (Kahn 1976); they lower and back the neighbouring vowels and are not written. Tap /ɾ/ versus trill /r/ (written r and rr); word-initial r is always the trill. Five long, peripheral vowels /iː eː ɑː oː uː/ (written î ê a o û) against three short, lax vowels /ɪ ɛ ʊ/ (written i e u). Uvular stop /q/ versus velar /k/; fricatives /x ɣ/ (ɣ written x, or ẍ in some spellings). /v/ versus /w/.

Stress: fixed on the end of the stem; morphologically conditioned, not contrastive in the lexicon. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- no aspiration contrast: every voiceless stop is the unaspirated base2 p, t, k; the table defines an aspirated p# but no rule uses it, and ku_list (letters and numbers only) has no entries that could supply the aspiration the spelling leaves out.
- no pharyngeals /ħ ʕ/ and no emphatics: h is always [h], and an apostrophe for /ʕ/ is ignored ('erd and erd both give [ɛrd]); the optional letters ḧ and ẍ are not in ku_rules.
- no /ɣ/: x is always the voiceless fricative.
- the oblique plural ending -an is stressed (malan gives [malˈan]) although the other inflectional endings -a, -ê, -ên are correctly left unstressed; personal endings of verbs are stressed too (dibêjim gives [dˌɪbeʒˈɪm]).
- r is a tap only between vowels and a trill everywhere else, so word-final r and rr are both trills.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 14 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɾ (l=s1: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s13: ms=70 whisper=44), ɟ (d=s22: f2=135 f3=112 a3=56 a4=56), q (k=s33: f2=68 f3=109 f1=118 burst=3), ɛ (E=s35: dur=84), ʊ (U=s37: dur=114), eʊ (e=s39: g1=110 g2=53 g3=87 glide=1), ɵ (Y=s45: f2=89 f3=107).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (kî, çi, kengî, çawa ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Thackston, W. M. (2006). Kurmanji Kurdish: A Reference Grammar with Selected Readings. Harvard University (manuscript). Bedir Khan, Djeladet and Lescot, Roger (1970). Grammaire kurde (dialecte kurmandji). Paris: Maisonneuve. Blau, Joyce and Barak, Veysi (1999). Manuel de kurde: kurmanji. Paris: L'Harmattan. Kahn, Margaret (1976). Borrowing and Variation in a Phonological Description of Kurdish. PhD dissertation, University of Michigan. Haig, Geoffrey and Matras, Yaron (2002). Kurdish linguistics: a brief overview. Sprachtypologie und Universalienforschung 55(1). Öpengin, Ergin and Haig, Geoffrey (2014). Regional variation in Kurmanji: a preliminary classification of dialects. Kurdish Studies 2(2). And 2 more in the profile.

## Kyrgyz (`ky`)

Turkic, Kipchak (Kyrgyz-Kipchak). Described: Standard Kyrgyz of Kyrgyzstan (northern dialect base), Cyrillic script.

**What the language has.** Eight short vowels in a symmetrical system: high versus non-high, front versus back, rounded versus unrounded. Phonemic vowel length, written with double letters (тоо 'mountain', суу 'water', жаан 'rain' versus жан 'soul'); long /iː ɯː/ are marginal. Voiced versus voiceless stops and affricates. Uvular [q ʁ] are variants of /k ɡ/ in back-vowel words, contrastive only in loans. Strong rounding harmony: low vowels also round after rounded vowels, and the spelling shows it (көлдөр, тоолор).

Stress: fixed final by default, with morphological exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the phoneme v (в) is defined as a vowel with vowel formants (a placeholder marked 'english v for now'), so в in loans such as вагон is not a fricative.
- ь and ъ are read as [j] (альбом gives [aljbom]).
- final stress is written into every vowel rule, so unstressable suffixes and particles are stressed (келдиби and келбейт get final stress).
- dark l is changed to clear l before every vowel, so the velarised onset of back-vowel words is never produced.
- no weakening of b, g, q between vowels.
- the ipa strings of the table are not IPA (oe, N, S, X, tS, dZ, l-, t[), so --ipa output is wrong although the sounds are right.
- the statement and question tunes are the ones written for French (s3 c3 q3 e3).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 12 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), ɑ (A=s8: f1=91 f2=86), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t[ (t=s9: f2=91 burst=-4), d[ (d=s9: f2=91 burst=-4), q (k=s33: f2=68 f3=109 f1=118 burst=3), ɯ (Y=s35: f1=83 f2=89 f3=114), oe (o=s36: g1=101 g2=247 g3=108 glide=1), u: (u=s38: dur=117).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (эмне, ким, кайда, качан ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Kara, Dávid Somfai (2003). Kyrgyz. Lincom Europa. Kirchner, Mark (1998). Kirghiz. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge. Hebert, Raymond J. & Poppe, Nicholas (1963). Kirghiz Manual. Indiana University.

## Latin (`la`)

Indo-European, Italic, Latino-Faliscan. Described: Classical Latin of the late Republic and early Empire in the reconstructed (restored) pronunciation; the ecclesiastical (Italianate) pronunciation is described in the notes. eSpeak NG follows the classical pronunciation.

**What the language has.** Vowel length for all five vowel qualities (malum 'evil' versus mālum 'apple'; rosa nominative versus rosā ablative; populus 'people' versus pōpulus 'poplar'). Single versus geminate consonants (anus 'old woman' versus annus 'year'; ager versus agger). Voiced versus voiceless stops; aspirated stops /pʰ tʰ kʰ/ only in Greek loanwords and a few native words (pulcher). Labialised velars /kʷ ɡʷ/ (written qu, and gu after n) versus velar plus vowel u. Syllable weight (light versus heavy) decides the place of the accent and is the basis of verse. /y yː/ and /z/ only in Greek loanwords.

Stress: weight-sensitive, fixed by rule. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- vowel length is known only when the text has macrons; plain text, which is the normal case, is read with all vowels short, and the accent rule then moves the stress to the antepenultimate in words with a long penultimate vowel (amicus [ˈamɪkʊs], regina [rˈɛɡɪna], habere [hˈabɛrɛ]).
- the word list is small (about 300 lines) and gives no vowel lengths for common words.
- final m is a full [m] (rosam [rˈɔsam]) and n before s, f a full [n] (cōnsul, īnfāns); the nasalised long vowels of the reconstruction are missing.
- consonantal i is found only at the start of a word and between vowels: coniunx is [kˈɔnɪʊŋks], adiuvō [adˈɪʊwoː], and iam is [ˈɪam].
- no devoicing of b before s, t (urbs [ˈʊrbs], obtineō [ɔbtˈɪnɛoː]).
- aspirated stops are a plain stop followed by a short separate [h] segment, and qu is the sequence [kw].
- there is no option for the ecclesiastical pronunciation.
- no tune set is selected, so the generic default tunes are used; elision in verse is not applied.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 18 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (E=s1: f1=93 f2=78 dur=55), a (a=s4: dur=51), h (<h=s13: ms=70 whisper=44), b (b=s16: voi=1 lead=75), d (d=s16: voi=1 lead=75), ɡ (g=s16: voi=1 lead=75), ɛ (E=s5: dur=55), ɪ (e=s36: f1=91 dur=55), ɔ (c=s7: dur=53), ʊ (o=s37: f1=92 f2=114 dur=53), aː (a=s38: dur=131), eː (e=s39: dur=148), iː (i=s40: dur=168), oː (o=s41: dur=150), y (i=s43: f1=110 f2=89 f3=81 dur=63), aʊ (a=s45: g1=57 g2=72 g3=97 glide=1 dur=131), aɪ (a=s46: g1=55 g2=127 g3=106 glide=1 dur=131), ɛʊ (E=s48: g1=82 g2=61 g3=94 glide=1 dur=148).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (quis, quid, ubi, quando ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

Sources: Allen, W. Sidney (1978). Vox Latina: A Guide to the Pronunciation of Classical Latin. 2nd edition. Cambridge University Press. Allen, W. Sidney (1973). Accent and Rhythm: Prosodic Features of Latin and Greek. Cambridge University Press. Sturtevant, Edgar H. (1940). The Pronunciation of Greek and Latin. 2nd edition. Philadelphia: Linguistic Society of America. Weiss, Michael (2009). Outline of the Historical and Comparative Grammar of Latin. Ann Arbor: Beech Stave Press. McCullagh, Matthew (2011). The sounds of Latin: phonology. In Clackson (ed.), A Companion to the Latin Language. Wiley-Blackwell. Cser, András (2020). The Phonology of Classical Latin. Transactions of the Philological Society 118, supplement.

## Luxembourgish (`lb`)

Indo-European, Germanic, West Germanic, Central Franconian (Moselle Franconian). Described: Central Luxembourgish (the Alzette valley and the city of Luxembourg), the emerging standard described by Gilles and Trouvain (2013).

**What the language has.** Short versus long vowels, mostly with a difference of quality as well: /ɑ/ versus /aː/ (Kapp, Kap), /i/ versus /iː/, /o/ versus /oː/, /u/ versus /uː/. Three short front vowels /i e æ/ (midd, Méck, Bett). Pairs of closing diphthongs with a short and a long first element: /ɑɪ/ versus /æːɪ/ (Leit, Zäit) and /ɑʊ/ versus /æːʊ/ (Auto, Raum). Centring diphthongs /iə uə/ (hien, Buedem) and mid-centralised closing diphthongs /əɪ əʊ/ (schéin, Schoul). Fortis versus lenis obstruents, neutralised at the end of a word. Alveolo-palatal [ɕ ʑ] versus postalveolar /ʃ ʒ/, a contrast that younger speakers are merging. Lexical stress, mainly in loans from French.

Stress: lexical, mostly initial in native words. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- there are no translator settings for lb, so stress follows the default penultimate rule, and neither lb_rules nor the 35,000 entries of lb_list mark stress: Lëtzebuerg and Lëtzebuerger are stressed on the second syllable, Gemeng on the prefix, Universitéit on the penultimate.
- unstressed -er and vocalised r are written with the consonant phoneme rR, a uvular fricative [ʁ], not with the vowel [ɐ]: Kanner is [kɑnʁ], Bäcker [bækʁ], Dier [diːʁ].
- /æ/ (phoneme E) uses the same formant data as /e/ and /eː/ (vowel/e), so Bett and hell sound like [e]; every short and long pair shares one formant file and differs only in duration.
- the front rounded vowels y, y: and œː are built from diphthong data (vdiph2/uu@, vdiph2/o@) and /ɛː/ from vdiph/ae_2, so they glide instead of holding one quality.
- final devoicing is written into single rules only (d after a consonant, g, and entries of the list): a final b, v or z in a word outside the list stays voiced, and final obstruents are not voiced before a vowel-initial word.
- /s/ is declared voiced and built on the formants of [z] (FMT(voc/z)); the consonants have no formant transitions (Vowelin, Vowelout) and no length modifiers.
- the IPA names of two phonemes are wrong: the velar nasal is labelled retroflex [ɳ] and /χ/ is labelled with a capital X.
- function words carry stress in running text (den Hond ass do comes out with four stressed words), although the list marks a few of them as unstressed.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 30 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʀ (r=s7: tap=3 tapms=18 f2=85 f3=112), ɑ (A=s8: f1=91 f2=86), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), h (<h=s13: ms=70 whisper=44), ɳ (n=s14: f3=80), ʑ (Z=s27: a3=34 a4=55 a5=22 f2=126 f3=121), X (x=s2: f2=88), ɕ (S=s30: a2=31 a3=34 a4=34 a5=22 f2=119 f3=116), aː (a=s35: dur=72), æ (E=s36: f1=124 f2=92 f3=92 dur=84), ɐ (A=s37: f1=85), iː (i=s38: dur=117), uː (u=s38: dur=117), y (y=s5: dur=56), yː (y=s38: dur=117), ɑ̃ː (a=s39: f1=89 f2=86 dur=72 nas=100), ɛ̃ː (E:=s40: nas=100), œː (OE=s41: dur=171), æːɪ (E=s42: f1=124 f2=92 f3=92 g1=79 g2=104 g3=97 glide=1 dur=209), ɑʊ (a=s43: f1=89 f2=86 g1=57 g2=79 g3=93 glide=1 dur=72), æːʊ (E=s44: f1=124 f2=92 f3=92 g1=82 g2=60 g3=89 glide=1 dur=209), ɑɪ (a=s45: f1=89 f2=86 g1=55 g2=143 g3=101 glide=1 dur=72), ɜɪ (OE=s46: f3=114 g1=77 g2=136 g3=118 glide=1 dur=171), oɪ (o=s47: g1=101 g2=236 g3=105 glide=1), iə (j=s48 @: hold=55), əʊ (@=s49: g1=94 g2=65 g3=93 glide=1 dur=208), uə (w=s48 @: hold=55).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (wien, wat, wou, wéini ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Gilles, Peter and Trouvain, Jürgen (2013). Luxembourgish. Journal of the International Phonetic Association 43(1), 67-74. Gilles, Peter (1999). Dialektausgleich im Lëtzebuergeschen: Zur phonetisch-phonologischen Fokussierung einer Nationalsprache. Tübingen: Niemeyer. Newton, Gerald (ed.) (1996). Luxembourg and Lëtzebuergesch: Language and Communication at the Crossroads of Europe. Oxford: Clarendon Press. Grabe, Esther and Low, Ee Ling (2002). Durational variability in speech and the Rhythm Class Hypothesis. In Gussenhoven and Warner (eds.), Laboratory Phonology 7. Berlin: Mouton de Gruyter.

## Lingua Franca Nova (`lfn`)

constructed language. Described: Elefen, as its grammar gives it.

**What the language has.** Five vowels with no length contrast.

Stress: by rule. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 4 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: u (u=s4: dur=114), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), ɡ (g=s11: voi=1 lead=75).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (ci, cual, do, cuando ...) ends as a statement does, from a high question word.

Sources: Boeree, C. George and others. Gramatica de Lingua Franca Nova (elefen.org).

## Ligurian (`lij`)

Indo-European, Romance, Western Romance, Gallo-Italic. Described: Genoese, the urban variety of Genoa that serves as the Ligurian koine, in the official spelling of the Académia Ligùstica do Brénno.

**What the language has.** Vowel length in stressed syllables for every vowel quality, shown in the official spelling (long vowels with a circumflex, ö for long [ɔː] and æ for long [ɛː]; short stressed vowels with an acute or grave): amîgo [aˈmiːɡu], mâ [maː], against tùtto [ˈtytu], neutte [ˈnøte]. Front rounded vowels /y ø/ next to /i e/ and /u/ (written u, eu; written o is [u]). Open-mid versus close-mid front vowels /ɛ e/. Velar nasal /ŋ/ versus alveolar /n/ between vowels: the velar nasal continues Latin single n and is written nn- or ñ (lùnn-a [ˈlyŋa] 'moon', campann-a 'bell'), while Latin double nn gives [n] (pénna [ˈpena] 'feather'). Voiced versus voiceless sibilants /s z/ and /ʃ ʒ/ (written s, ç, z, sc, x). Affricates /tʃ dʒ/; there are no /ts dz/ and no /ʎ/ (figgio, famiggia have /dʒ/). Lexical stress.

Stress: lexical, mostly penultimate. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the velar nasal between vowels is lost: nn- is read as plain [n] (lùnn-a [lˈyna], penn-a [pˈena], bonn-a [bˈuna]), so penn-a and pénna sound the same.
- the hyphen of nn-a also upsets the stress: campann-a is stressed on the first syllable ([kˈaŋpana]).
- the long vowel written êu is not recognised: fêugo is [fˈeːyːɡu] instead of [ˈføːɡu].
- lengoa is [leŋɡˈua] with stress on u; the expected form is [ˈleŋɡwa].
- double consonants get a half-length mark in the IPA output only; their duration in the synthesis is that of single consonants.
- /r/ is the base trill, where Genoese has a weak tap.
- intonation uses one of the generic tune sets (voice option 'intonation 2').

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (l=s9: f1=127 f3=68), a (a=s4: dur=51), e (e=s5: dur=55), i (i=s6: dur=63), o (o=s7: dur=53), u (u=s8: dur=61), b (b=s16: voi=1 lead=75), d (d=s16: voi=1 lead=75), ɡ (g=s16: voi=1 lead=75), ɛ (E=s5: dur=55), ɔ (c=s7: dur=53), y (i=s37: f1=110 f2=89 f3=81 dur=63), ø (e=s38: f1=91 f2=79 f3=84 dur=55), aː (a=s47: dur=131), ɛː (E=s48: dur=148), eː (e=s48: dur=148), iː (i=s49: dur=168), ɔː (c=s50: dur=150), uː (u=s51: dur=171), yː (i=s52: f1=110 f2=89 f3=81 dur=168), øː (e=s53: f1=91 f2=79 f3=84 dur=148).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.

Sources: Toso, Fiorenzo (1997). Grammatica del genovese: varietà urbana e di koinè. Recco: Le Mani. Forner, Werner (1988). Italienisch: Areallinguistik I. Ligurien. In Holtus, Metzeltin and Schmitt (eds.), Lexikon der Romanistischen Linguistik, volume IV. Tübingen: Niemeyer. Forner, Werner (1997). Liguria. In Maiden and Parry (eds.), The Dialects of Italy. London: Routledge. Ghini, Mirco (2001). Asymmetries in the Phonology of Miogliola. Berlin: Mouton de Gruyter.

## Lithuanian (`lt`)

Indo-European, Balto-Slavic, Baltic (East Baltic). Described: Standard Lithuanian (bendrinė kalba, based on the West Aukštaitian dialect of the Suvalkija region).

**What the language has.** Palatalised versus plain consonants throughout the system; the contrast is free before back vowels (spelled with i: kiaulė, liūtas) and automatic before front vowels. Phonemic vowel length in stressed and unstressed syllables (y, į, ū, ų, ė, o, ą, ę are long). Acute versus circumflex syllable accent on long stressed syllables (áukštas 'tall' vs aũkštas 'storey'; šáuk 'shoot' vs šaũk 'shout'). Position of stress is lexical and changes within paradigms (four accent classes of nouns). Mixed diphthongs: vowel plus l, m, n, r in one syllable behave like diphthongs and carry the accents. Voiced versus voiceless obstruents (neutralised word-finally and in clusters); /f x ɣ/ occur only in loanwords.

Stress: free (lexical), mobile, with pitch accent on long syllables. Rhythm: mixed. Tone: pitch accent, 3 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- No pitch accent: acute and circumflex are not distinguished, and accent marks in dictionary-style text are ignored (áukštas and aũkštas give the same output). A few suffix rules put the prominence on the first or second vowel of a diphthong (-áitis vs -aĩnis), which imitates the accents in those suffixes only.
- Stress is penultimate by default, with some suffix rules; Lithuanian stress is lexical and mobile, so many words are wrong (žmogus, gerai, namai, vanduo, Lietuva, mokykla have final stress; vasara, ežeras have initial stress).
- Hard l is defined as a vowel-type syllabic phoneme (IPA l̩, nominal length 300) and soft l carries the IPA label of a retroflex lateral (ɭ).
- The diphthong ei is not recognised and is read as two vowels (sveiki [sʲvʲe.ˈɪ.kʲi]); iau is read as [e] plus [u] (kiaulė).
- Soft labials, k, r and v are coded as consonant plus a palatal glide that is deleted before another consonant, so clusters lose palatalisation (kirsti); g, f, h, z, ž are never palatalised (geras, gėlė).
- Devoicing before a voiceless consonant is overridden by the palatalisation rule when a front vowel follows the cluster (dirbti keeps [b]); final devoicing rules exist only for d, g, ž (final b, z stay voiced).
- ę is a diphthong-like [ea] (phoneme eA) instead of [æː]; stressed a, e are not lengthened (namas, geras).
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 38 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s8: vot=17), p (p=s9: vot=13), k (k=s10: vot=28), b (b=s19: voi=1 lead=75), d (d=s19: voi=1 lead=75), tɕ (t=s24 S=s25: hold=85 f2=119 f3=116; a2=31 a3=34 a4=34 a5=22 f2=119 f3=116 hold=70), ɡ (g=s19: voi=1 lead=75), ʂ (S=s33: a4=54 f2=87 f3=83 f4=88), ɑ (A=s40: f1=91 f2=86), aː (a=s41: dur=72), ɛ (E=s42: dur=84), eɑ (j=s43 A=s40: hold=55; f1=91 f2=86), iː (i=s44: dur=117), ɔ (O=s45: dur=85), ʊ (U=s46: dur=114), uː (u=s44: dur=117), ai (a=s47: g1=43 g2=166 g3=113 glide=1 dur=72), ei (e=s48: g1=79 g2=101 g3=105 glide=1), au (a=s49: g1=46 g2=69 g3=93 glide=1 dur=72), ie (j=s43 e=s4: hold=55; dur=53), tʲ (t=s57: f2=129 f3=108 vot=25), nʲ (n=s59: f2=130), ɭ (l=s13: f2=111 f3=71), ɹ (r=s61: f2=92 f3=77), ɒ (O=s66: f1=116 dur=85), əʊ (@=s70: g1=94 g2=65 g3=93 glide=1 dur=208), aɪə (A j=s43 j=s43: hold=55; hold=55).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (kas, kur, kada, kaip ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

**Not yet.** The acute and the circumflex are not in eSpeak NG's reading.

Sources: Ambrazas, Vytautas (ed.) (1997). Lithuanian Grammar. Vilnius: Baltos lankos. Pakerys, Antanas (1982). Lietuvių bendrinės kalbos prozodija. Vilnius: Mokslas. Pakerys, Antanas (1995). Lietuvių bendrinės kalbos fonetika. Vilnius: Žara. Girdenis, Aleksas (2014). Theoretical Foundations of Lithuanian Phonology. Vilnius. (English translation of Teoriniai lietuvių fonologijos pagrindai, 2nd edition 2003). Dogil, Grzegorz (1999). Baltic languages. In H. van der Hulst (ed.), Word Prosodic Systems in the Languages of Europe. Berlin: Mouton de Gruyter. Dogil, Grzegorz & Möhler, Gregor (1998). Phonetic invariance and phonological stability: Lithuanian pitch accents. Proceedings of ICSLP 98, Sydney. And 4 more in the profile.

## Latgalian (`ltg`)

Indo-European, Balto-Slavic, Baltic (East Baltic). Described: Standard Latgalian: the written standard of 2007 and the High Latvian varieties of Latgale (eastern Latvia) on which it rests. Treated in Latvia as a historical variety of Latvian and by many linguists as a separate language.

**What the language has.** Palatalised versus plain consonants: consonants are soft before front vowels and the contrast is also found before back vowels and word-finally (soft final t of the infinitive, ļ, ņ, ķ, ģ). Central /ɨ/ (written y) after plain consonants versus /i/ after palatalised consonants; the two vowels are close to complementary distribution. Phonemic vowel length (ā, ē, ī, ū; long ō is rare, y has no long partner in the standard spelling). Short /o/ as a native vowel (lobs, Latgola), where Latvian has /a/. Narrow /e eː/ versus wide /æ æː/, both written e, ē. Two syllable tones on long syllables: falling and broken.

Stress: fixed initial. Rhythm: mixed. Tone: pitch accent, 2 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- There is little Latgalian of its own: the voice uses the Latvian phoneme table and the Latvian dictionary (phonemes lv, dictionary lv) with three conditional rules (dictrules 2): o is short [o], ō is [uo], and no break is inserted after y before a vowel.
- No palatalisation: consonants before front vowels and soft final consonants are read as plain Latvian consonants (dīna, sirds, saceit, byut); only ļ, ņ, ķ, ģ are palatal.
- No syllable tones and no glottalisation for the broken tone.
- The diphthong yu is two separate vowels (myusu has three syllables).
- Narrow or wide e is chosen by the rules written for Latvian words.
- No regressive voicing assimilation (lobs, vuords, golds keep [bs], [ds]).
- o in words that the Latvian rules treat as loanwords is still long [oː] (školā).
- y is shown as 'y' in IPA output although the sound is [ɨ].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 33 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r̝ (l=s7: tap=3 tapms=18 f2=109 f3=77 fric=46 a3=58 a4=54), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), r (l=s8: tap=3 tapms=18 f2=109 f3=77), ʎ (l=s13: f2=159), h (<h=s16: ms=70 whisper=44), ɲ (n=s18: f2=136 f3=109), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɟ (d=s27: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s28: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s20: voi=1 lead=75), ʋ (v=s30: af=-14), aː (a=s40: dur=72), æ (E=s41: f1=124 f2=92 f3=92 dur=84), æː (E=s42: f1=124 f2=92 f3=92 dur=171), iː (i=s43: dur=117), y (y=s5: dur=56), uː (u=s43: dur=117), ai (a=s44: g1=43 g2=166 g3=113 glide=1 dur=72), au (a=s45: g1=46 g2=69 g3=93 glide=1 dur=72), ei (e=s46: g1=79 g2=101 g3=105 glide=1), ie (j=s47 e=s4: hold=55; dur=53), iu (i=s48: g1=113 g2=46 g3=82 glide=1 dur=117), uo (w=s47 o=s4: hold=55; dur=53), ʐ (Z=s32: a4=51 f2=92 f3=87 f4=88).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (kas, kur, kod, kai ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

**Not yet.** The syllable tones are not in eSpeak NG's reading.

Sources: Nau, Nicole (2011). A Short Grammar of Latgalian. München: Lincom Europa. Leikuma, Lidija (2003). Latgalīšu volūda 1. Sanktpēterburga: Sanktpēterburgas Valsts universitāte. Cibuļs, Juris & Leikuma, Lidija (2003). Vasals! Latgaliešu valodas mācība. Rīga: n.i.m.s. Breidaks, Antons (2007). Darbu izlase. Rīga: LU Latviešu valodas institūts. Balode, Laimute & Holvoet, Axel (2001). The Latvian language and its dialects. In Ö. Dahl & M. Koptjevskaja-Tamm (eds.), The Circum-Baltic Languages, vol. 1. Amsterdam: John Benjamins. Laua, Alise (1997). Latviešu literārās valodas fonētika. Rīga: Zvaigzne ABC. (for the description of the syllable tones).

## Latvian (`lv`)

Indo-European, Balto-Slavic, Baltic (East Baltic). Described: Standard Latvian (based on the Central dialect). The codified norm has three syllable tones, as in the Vidzeme varieties around Valmiera and Cēsis; most speakers, including those in Rīga, distinguish two.

**What the language has.** Phonemic vowel length in stressed and unstressed syllables (kazas 'goats' vs kāzas 'wedding'; final -a vs -ā). Narrow /e eː/ versus wide /æ æː/, both written e, ē. Three syllable tones on long syllables in the codified norm: level, falling, broken (loks 'leek' level, loks 'arc' falling, logs 'window' broken; zāle 'hall' level vs zāle 'grass' broken). Palatal /c ɟ ɲ ʎ/ (ķ, ģ, ņ, ļ) versus /k ɡ n l/. Voiced versus voiceless obstruents, kept word-finally. The letter o stands for the diphthong /uo/ in native words and for /ɔ/ or /ɔː/ in loanwords.

Stress: fixed initial. Rhythm: mixed. Tone: pitch accent, 3 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- No syllable tones: level, falling and broken tone are not distinguished, there are no tone phonemes, and the glottalisation of the broken tone is missing (loks and logs differ only in k and g).
- No regressive voicing assimilation: labs, gads, mazs, logs, draugs, zirgs, augt, atbilde keep the written voicing ([bs], [ds], [zs], [ɡs], [ɡt], [tb]); the translator does not set the regressive voicing option.
- Voiceless obstruents after a short stressed vowel are not lengthened (lapa, aka, upe).
- v is never the glide [u̯] at the end of a syllable (tēvs is [tæːʋs]).
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 27 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), r (l=s8: tap=3 tapms=18 f2=109 f3=77), ʎ (l=s13: f2=159), h (<h=s16: ms=70 whisper=44), ɲ (n=s18: f2=136 f3=109), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɟ (d=s27: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s28: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s20: voi=1 lead=75), ʋ (v=s30: af=-14), aː (a=s40: dur=72), æ (E=s41: f1=124 f2=92 f3=92 dur=84), æː (E=s42: f1=124 f2=92 f3=92 dur=171), iː (i=s43: dur=117), uː (u=s43: dur=117), ei (e=s46: g1=79 g2=101 g3=105 glide=1), ie (j=s47 e=s4: hold=55; dur=53), uo (w=s47 o=s4: hold=55; dur=53).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (kas, kur, kad, kā ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

**Not yet.** The three syllable tones are not in eSpeak NG's reading.

Sources: Laua, Alise (1997). Latviešu literārās valodas fonētika. Rīga: Zvaigzne ABC. Nau, Nicole (1998). Latvian. München: Lincom Europa. Nītiņa, Daina & Grigorjevs, Juris (eds.) (2013). Latviešu valodas gramatika. Rīga: LU Latviešu valodas institūts. Grigorjevs, Juris (2008). Latviešu valodas patskaņu sistēmas akustisks un auditīvs raksturojums. Rīga: LU Latviešu valodas institūts. Grigorjevs, Juris & Jaroslavienė, Jurgita (2015). Comparative study of the qualitative features of the Lithuanian and Latvian monophthongs. Baltistica 50(1). Kariņš, A. Krišjānis (1996). The Prosodic Structure of Latvian. PhD dissertation, University of Pennsylvania. And 4 more in the profile.

## Māori (`mi`)

Austronesian, Oceanic, Polynesian, Eastern Polynesian (Tahitic). Described: Modern standard Māori of the North Island. The conservative reference is the speech of elders born between the 1880s and the 1930s (MAONZE corpus); changes in younger speakers are noted.

**What the language has.** Short versus long vowels: keke 'cake' versus kēkē 'armpit', matua 'parent' versus mātua 'parents', kaka 'garment' versus kākā 'parrot' versus kakā 'hot'. Diphthongs that differ only in the height of the second element (ai versus ae, au versus ao) or of the first (ou versus au). Velar nasal ŋ in all positions, including word-initially (ngā). F (written wh) versus h versus w. Ten consonants only; no voicing contrast, no sibilants. No glottal stop phoneme in the standard language, unlike Hawaiian; vowels that meet form a long vowel, a diphthong or a hiatus.

Stress: weight-sensitive, counted in morae. Rhythm: mora-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- stress is always put on the penultimate syllable (the engine default); the Māori rule of first long vowel, else first diphthong, else first syllable is not implemented, so Māori, whānau, tangata, wahine, aroha, mātua all get the wrong stress.
- ae and ai are both pronounced [aɪ], so the contrast that conservative speakers keep (tae versus tai) is lost; ao is given the quality of English [aʊ].
- oe is pronounced [we]: koe comes out as [kwe], hoe as [hwe].
- short a has the same quality as long ā.
- the voice file inserts a short pause after every word (words 1 2), which breaks up the phrase rhythm.
- numbers are disabled in the engine; the word list has only the digits 0 to 9.
- /t/ is not affricated before i and u.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=49), e (e=s5: dur=54), i (i=s6: dur=58), o (o=s4: dur=49), h (<h=s11: ms=70 whisper=44), ɔ (o=s31: f1=116 dur=49), aɪ (a=s38: g1=69 g2=132 g3=105 glide=1 dur=135), u" (u=s7: dur=52).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (aha, wai, hea, pēhea ...) ends as a statement does, from a high question word.

Sources: Bauer, Winifred (1993). Maori. London: Routledge. Harlow, Ray (2007). Māori: A Linguistic Introduction. Cambridge: Cambridge University Press. Biggs, Bruce (1961). The structure of New Zealand Maaori. Anthropological Linguistics 3(3). Watson, Catherine I., Maclagan, Margaret A., King, Jeanette, Harlow, Ray & Keegan, Peter J. (2016). Sound change in Māori and the influence of New Zealand English. Journal of the International Phonetic Association 46(2), 185-218. Maclagan, Margaret & King, Jeanette (2007). Aspiration of plosives in Māori: change over time. Australian Journal of Linguistics 27(1), 81-96. Maclagan, Margaret & King, Jeanette (2002). The pronunciation of wh in Māori: a case study from the late nineteenth century. Te Reo 45. And 2 more in the profile.

## Macedonian (`mk`)

Indo-European, Balto-Slavic, Slavic, South Slavic (eastern group). Described: Standard Macedonian (literary norm based on the west-central dialects of the Prilep, Bitola, Veles and Kičevo area, as spoken in Skopje).

**What the language has.** Five vowels without length or reduction; a marginal schwa in dialect words and some loans, written with an apostrophe. Palatal stops /c ɟ/ (ќ, ѓ) versus velar /k ɡ/ and versus the affricates /t͡ʃ d͡ʒ/. Affricate /d͡z/ (ѕ) versus fricative /z/. Clear /l/ (љ, and л before front vowels and ј) versus velarised /ɫ/ (л elsewhere); the two contrast only before back vowels (бела vs беља). Palatal /ɲ/ versus /n/. Syllabic /r̩/ between consonants and word-initially before a consonant (крв, прст, 'рж). Voiced versus voiceless obstruents (neutralised word-finally and in clusters).

Stress: fixed antepenultimate. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- No final devoicing except в to [f]: леб, град, заб, маж, нож, џеб keep voiced final consonants.
- No voicing assimilation in clusters or between words (татковци keeps [v] before ц, без тебе keeps [z]); the translator does not set the regressive voicing option for Macedonian.
- Unstressed /a/ is replaced by a reduced [æ]-like vowel (phoneme &), /i/ by [ɪ] and /u/ by [ʊ], inherited from the Croatian phoneme table; Macedonian has no vowel reduction.
- ч is mapped to the alveolo-palatal tS; ([t͡ɕ]) while џ is the postalveolar [d͡ʒ]; ќ is a palatal stop (k^, with no IPA name in the table) while ѓ is the affricate [d͡ʑ]: the voiced and voiceless partners do not match.
- A secondary stress is added on the last syllable of words of three or more syllables (планина [ˈplanɪˌnæ]).
- Exceptions to antepenultimate stress are not handled (литература and the verbal adverb одејќи are stressed on the third syllable from the end) and clitic groups are not treated as one stress unit (донеси го is read dónesi gó; each clitic gets its own stress).
- л before a back vowel is a clear [l]; a dark [ɫ] appears only after a vowel when no vowel follows (the rule of the English l phoneme that the table imports), so л and љ before back vowels contrast as [l] vs palatal [ʎ] (бела, беља) instead of [ɫ] vs [l].
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 11 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: i (i=s4: dur=114), u (u=s4: dur=114), h (<h=s9: ms=70 whisper=44), b (b=s12: voi=1 lead=75), d (d=s12: voi=1 lead=75), dʑ (d=s13 Z=s14: voi=1 lead=75 hold=85 f2=126 f3=122; a3=34 a4=55 a5=22 f2=126 f3=122 hold=70), tɕ (t=s15 S=s16: hold=85 f2=126 f3=122; a2=31 a3=34 a4=34 a5=22 f2=126 f3=122 hold=70), ɡ (g=s12: voi=1 lead=75), æ (a=s37: f1=85 f2=116), ɪ (e=s50: f1=91).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (кој, која, кое, кои ...) ends as a statement does, from a high question word.

Sources: Friedman, Victor A. (2001). Macedonian. SEELRC Reference Grammars. Durham, NC: Slavic and East European Language Research Center, Duke University. Friedman, Victor A. (1993). Macedonian. In B. Comrie & G. G. Corbett (eds.), The Slavonic Languages. London: Routledge. Lunt, Horace G. (1952). A Grammar of the Macedonian Literary Language. Skopje: Državno knigoizdatelstvo. Koneski, Blaže (1967). Gramatika na makedonskiot literaturen jazik. Skopje: Kultura. Sawicka, Irena & Spasov, Ljudmil (1997). Fonologija na sovremeniot makedonski standarden jazik. Skopje: Detska radost. Franks, Steven (1987). Regular and irregular stress in Macedonian. International Journal of Slavic Linguistics and Poetics 35-36. And 1 more in the profile.

## Malayalam (`ml`)

Dravidian, South Dravidian. Described: Standard Malayalam (educated speech of central Kerala), formal style.

**What the language has.** Six places of articulation in nasals: bilabial, dental, alveolar, retroflex, palatal, velar /m n̪ n ɳ ɲ ŋ/; all six contrast as geminates between vowels (Ladefoged and Maddieson 1996 give a six-word set, with dental pʌn̪n̪i 'pig' against alveolar kʌnni 'virgin'). Six places in stops and affricates: bilabial, dental, alveolar, retroflex, palato-alveolar, velar; the alveolar stop /t/ occurs only as the geminate [tː] (written റ്റ) and after /n/ (written ന്റ, pronounced [nd]); palatalised velars after front vowels are counted as a seventh place by Mohanan and Mohanan (1984). The dental and the alveolar nasal are both written ന in the ordinary script. Voiceless, voiceless aspirated, voiced and breathy voiced stops; the aspirated series belong to the Sanskrit vocabulary. Five liquids: tap /ɾ/ (ര), trill /r/ (റ), alveolar lateral /l/, retroflex lateral /ɭ/, retroflex approximant /ɻ/ (ഴ). Vowel length for five vowel qualities. Single versus geminate consonants, including all nasals and laterals. Three sibilants /s ʂ ɕ/.

Stress: weight-sensitive, weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- word-medial k, t and p are silent: in ph_malayalam these phonemes import a base phoneme and then add conditions for the start and end of the word, which leaves no sound for the middle of the word; the geminates ക്ക, ത്ത, പ്പ come out as a bare silent gap with no burst or formant transitions, and the words അക്ക, അത്ത, അപ്പ give byte-identical audio.
- ഴ /ɻ/ is phoneme r., the base retroflex flap (r3/@tap_rfx), not an approximant; it has no IPA name, so --ipa prints 'r.'.
- റ്റ is rendered as retroflex [ʈʈ], which merges the alveolar geminate [tː] with ട്ട, and the rule drops the inherent vowel after it (പാറ്റ gives [paːʈʈ], മാറ്റം [maːʈʈm]).
- there is no dental nasal: ന is always the alveolar base n, so the dental and alveolar nasals are not distinguished and ന്ത has an alveolar nasal.
- word-initial /p t̪ k/ call the English base phonemes p, t, k, which are aspirated, and the /t̪/ becomes alveolar.
- a word-final single stop letter with virama (ക് ട് ത് പ്) gets no epenthetic vowel: monosyllables keep a voiceless stop (അത് gives [ɐt], പന്ത് [pɐnt], വീട് [viːʈ]) and longer words end in a bare voiced stop.
- post-nasal voicing covers ക ട ത പ but not ച (ഇഞ്ചി gives [iɲci]).
- anusvara is always [m], also before stops.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 42 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: tʰ (t=s4: f2=91 burst=-4 vot=68 asp=50), ɾ (l=s1: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), ɐ (A=s8: f1=85), e (e=s5: dur=53), i (i=s6: dur=56), o (o=s5: dur=53), u (u=s7: dur=57), r̩ (l=s9: tap=3 tapms=18 f2=109 f3=77), t (t=s10: f2=91 burst=-4 vot=16), p (p=s11: vot=13), k (k=s12: vot=28), r (l=s9: tap=3 tapms=18 f2=109 f3=77), ɭ (l=s15: f2=111 f3=71), h (<h=s17: ms=70 whisper=44), ɳ (n=s18: f3=80), ɲ (n=s19: f2=136 f3=109), r. (l=s20: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s21: voi=1 lead=75), d (d=s22: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s27: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s28: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s21: voi=1 lead=75), ʂ (S=s34: a4=54 f2=87 f3=83 f4=88), ɕ (S=s36: a2=31 a3=34 a4=34 a5=22 f2=119 f3=116), iː (i=s42: dur=117), aː (a=s45: dur=72), uː (u=s42: dur=117), aɪ (a=s57: g1=56 g2=146 g3=101 glide=1 dur=72), aʊ (a=s58: g1=58 g2=82 g3=93 glide=1 dur=72), pʰ (p=s59: vot=65 asp=50), bʰ (b=s60: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s61: f2=91 burst=-4 voi=1 lead=75 brth=90 f0=-15), ʈ (t=s62: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s63: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75), ʈʰ (t=s64: f2=91 f3=79 f4=88 a4=52 a5=42 vot=60 asp=50), cʰ (t=s65: f2=135 f3=112 a3=56 a4=56 vot=75 asp=50), ɟʰ (d=s66: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75 brth=90 f0=-15), kʰ (k=s67: vot=85 asp=50), ɡʰ (g=s60: voi=1 lead=75 brth=90 f0=-15), ɨ (Y=s68: f1=78 f2=106 f3=114).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (എന്ത്, എന്താണ്, ആര്, ആരാണ് ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Namboodiripad, Savithry and Garellek, Marc (2017). Malayalam (Namboodiri Dialect). Journal of the International Phonetic Association 47(1) (Illustrations of the IPA). Asher, R. E. and Kumari, T. C. (1997). Malayalam. London: Routledge (Descriptive Grammars). Mohanan, K. P. and Mohanan, Tara (1984). Lexical phonology of the consonant system in Malayalam. Linguistic Inquiry 15(4). Mohanan, K. P. (1986). The Theory of Lexical Phonology. Dordrecht: Reidel. Ladefoged, Peter and Maddieson, Ian (1996). The Sounds of the World's Languages. Oxford: Blackwell. Punnoose, Reenu; Khattab, Ghada; Al-Tamimi, Jalal (2013). The contested fifth liquid in Malayalam: a window into the lateral-rhotic relationship in Dravidian languages. Phonetica 70(4). And 4 more in the profile.

## Mongolian (`mn`)

Mongolic. Described: Khalkha (Halh) Mongolian of Ulaanbaatar, Cyrillic script.

**What the language has.** Aspirated versus unaspirated obstruents, both voiceless: /pʰ tʰ tsʰ tʃʰ/ (п т ц ч) versus /p t ts tʃ/ (б д з ж); there is no voicing contrast and no native /k/. Pharyngeal (retracted tongue root) vowels /a ɔ ʊ/ versus non-pharyngeal /e o u/, with neutral /i/; ө and ү are the back or central rounded vowels /o u/, not front rounded vowels. Long versus short vowels, in word-initial syllables only. Full versus reduced (epenthetic, schwa-like) vowels in non-initial syllables. Plain versus palatalised consonants, in pharyngeal words (spelt with ь or a following и or iotated vowel). Velar /ɡ/ versus uvular /ɢ/ at the end of pharyngeal stems (баг 'team' versus бага 'small'). Alveolar /n/ versus velar /ŋ/ at the end of a syllable (хана 'wall' with /n/ versus хан with /ŋ/).

Stress: non-contrastive and disputed; no lexical stress according to Svantesson et al. (2005) and Karlsson (2005). Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the aspiration contrast is rendered as a voicing contrast: б д г ж are voiced [b d ɡ dʒ] and п т к ч are aspirated; Khalkha has voiceless unaspirated versus aspirated consonants, and there is no pre-aspiration after vowels.
- з is the voiced fricative [z]; Khalkha has the unaspirated affricate [ts] against aspirated ц [tsʰ].
- л uses the ordinary lateral approximant formants although the table calls it a lateral fricative; [ɮ] and its voiceless variant [ɬ] are not produced.
- short vowels of non-initial syllables keep their written quality and are only shortened (length 100 against 150); in Khalkha they are schwa-like and predictable, and the final vowel letters of words such as хана and бага are silent.
- non-initial long vowels get the full long length (250-270), although they are only slightly longer than an initial short vowel in Khalkha.
- palatalised consonants are missing: ь is dropped (тавь sounds like тав, хонь like хон) or becomes a full [i] in dictionary entries (морь gives [mɔri]).
- үй is mapped to the diphthong of уй [ʊi], which breaks the harmony (үйл, хүйтэн); е is always [je], also before ө (ерөнхий); юу is read as two short vowels.
- no velar versus uvular variants: г and х are always [ɡ] and [x].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), ɲ (n=s14: f2=136 f3=109), χ (x=s2: f2=88), O (O=s34: dur=85), 8 (Y=s35: f2=89 f3=107), U (U=s36: dur=114), u (u=s6: dur=57), a: (a=s37: dur=72), i: (i=s38: dur=117), O: (O=s39: dur=220), 8: (oe=s40: f1=110 f2=90 f3=111), U: (U=s41: dur=262), u: (u=s38: dur=117), ai (a=s42: g1=43 g2=166 g3=113 glide=1 dur=72), ei (e=s43: g1=79 g2=101 g3=105 glide=1), Oi (O=s44: g1=55 g2=222 g3=113 glide=1 dur=220), Ui (U=s45: g1=70 g2=216 g3=116 glide=1 dur=262).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (хэн, юу, хаана, хэзээ ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Svantesson, Jan-Olof; Tsendina, Anna; Karlsson, Anastasia & Franzén, Vivan (2005). The Phonology of Mongolian. Oxford University Press. Janhunen, Juha (2012). Mongolian. John Benjamins. Karlsson, Anastasia (2005). Rhythm and Intonation in Halh Mongolian. Lund University. Karlsson, Anastasia (2014). The intonational phonology of Mongolian. In Sun-Ah Jun (ed.), Prosodic Typology II. Oxford University Press. Walker, Rachel (1997). Mongolian stress, licensing, and factorial typology. Manuscript, Rutgers Optimality Archive. Nevins, Andrew (2009). Review of The Phonology of Mongolian. Phonology 26(3), 525-534.

## Ankhmaa (`mn-f`)

Mongolic. Described: Khalkha (Halh) Mongolian of Ulaanbaatar, Cyrillic script; the same language as mn, spoken with a female voice setting.

**What the language has.** Aspirated versus unaspirated obstruents, both voiceless: /pʰ tʰ tsʰ tʃʰ/ (п т ц ч) versus /p t ts tʃ/ (б д з ж); there is no voicing contrast and no native /k/. Pharyngeal (retracted tongue root) vowels /a ɔ ʊ/ versus non-pharyngeal /e o u/, with neutral /i/; ө and ү are the back or central rounded vowels /o u/, not front rounded vowels. Long versus short vowels, in word-initial syllables only. Full versus reduced (epenthetic, schwa-like) vowels in non-initial syllables. Plain versus palatalised consonants, in pharyngeal words (spelt with ь or a following и or iotated vowel). Velar /ɡ/ versus uvular /ɢ/ at the end of pharyngeal stems (баг 'team' versus бага 'small'). Alveolar /n/ versus velar /ŋ/ at the end of a syllable (хана 'wall' with /n/ versus хан with /ŋ/).

Stress: non-contrastive and disputed; no lexical stress according to Svantesson et al. (2005) and Karlsson (2005). Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the voice differs from mn only in global settings: pitch 140-210 Hz instead of 80-140 Hz, and all formants scaled (F1 112%, F2 117%, F3 111%, against F1 96% in mn); phonemes, rules, dictionary, speed, breath and intonation settings are the same, so every problem listed for mn applies.
- one scaling factor per formant is used for all vowels; there are no separate female vowel targets and no change of voice quality.
- the language line gives priority 4, which is more preferred than the default 5 of mn, so a request for the language mn by properties can select this voice before the plain Mongolian voice.
- the aspiration contrast is rendered as a voicing contrast (б д г ж voiced, п т к ч aspirated), without pre-aspiration; з is [z] instead of the unaspirated affricate [ts].
- л is a lateral approximant, not the lateral fricative [ɮ].
- short vowels of non-initial syllables keep their written quality and are only shortened; silent final vowel letters (хана, бага) are pronounced; non-initial long vowels get the full long length.
- palatalised consonants are missing (ь is dropped, or a full [i] in dictionary entries).
- үй is read as [ʊi]; е is always [je]; юу is two short vowels; г and х have no uvular variants.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), ɲ (n=s14: f2=136 f3=109), χ (x=s2: f2=88), O (O=s34: dur=85), 8 (Y=s35: f2=89 f3=107), U (U=s36: dur=114), u (u=s6: dur=57), a: (a=s37: dur=72), i: (i=s38: dur=117), O: (O=s39: dur=220), 8: (oe=s40: f1=110 f2=90 f3=111), U: (U=s41: dur=262), u: (u=s38: dur=117), ai (a=s42: g1=43 g2=166 g3=113 glide=1 dur=72), ei (e=s43: g1=79 g2=101 g3=105 glide=1), Oi (O=s44: g1=55 g2=222 g3=113 glide=1 dur=220), Ui (U=s45: g1=70 g2=216 g3=116 glide=1 dur=262).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (хэн, юу, хаана, хэзээ ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Svantesson, Jan-Olof; Tsendina, Anna; Karlsson, Anastasia & Franzén, Vivan (2005). The Phonology of Mongolian. Oxford University Press. Janhunen, Juha (2012). Mongolian. John Benjamins. Karlsson, Anastasia (2005). Rhythm and Intonation in Halh Mongolian. Lund University. Karlsson, Anastasia (2014). The intonational phonology of Mongolian. In Sun-Ah Jun (ed.), Prosodic Typology II. Oxford University Press. Walker, Rachel (1997). Mongolian stress, licensing, and factorial typology. Manuscript, Rutgers Optimality Archive. Nevins, Andrew (2009). Review of The Phonology of Mongolian. Phonology 26(3), 525-534.

## Marathi (`mr`)

Indo-European, Indo-Iranian, Indo-Aryan (Southern zone). Described: Standard Marathi (educated speech of Pune).

**What the language has.** Four-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced. Alveolar affricates /ts dz dzʱ/ versus palato-alveolar affricates /tʃ tʃʰ dʒ dʒʱ/, written with the same letters च ज झ (the spelling जग is both /dʒəɡ/ 'world' and /dzəɡ/ 'live!'). Plain versus breathy voiced (aspirated) sonorants /m n ɳ l ɾ ʋ/ : /mʱ nʱ ɳʱ lʱ ɾʱ ʋʱ/ (/maːɾ/ 'beat' : /mʱaːɾ/ 'a caste'). Dental versus retroflex stops; /n/ : /ɳ/; /l/ : /ɭ/. No phonemic nasal vowels in the standard language. Vowel length of i and u is written but hardly contrastive; six vowel qualities, plus /æ ɔ/ in English loans. Consonant gemination.

Stress: weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- च and झ are always palatal ([c], [ɟʰ]): चांगला, चोर, चूक, झाड, माझा come out with palatals where Marathi has the alveolar affricates /ts/ and /dzʱ/.
- ज is the fricative [z] by default (जा [zaː], राजा [ɾaːzaː]) and the palatal [ɟ] before front vowels, before य and in listed words (जग); there is no affricate [dz].
- Anusvara before a stop gives a nasal vowel and no nasal consonant: चांगला [cãɡlaː], आंबा [ãbaː] for [tsaːŋɡlaː], [aːmbaː]. Marathi has no phonemic nasal vowels.
- Breathy sonorants are a sonorant followed by a separate voiceless [h]: म्हणून [mhəɳuːn], न्हावी [nhaːvi], कोल्हा [koːlhaː].
- /ʋ/ is the fricative [v] of the base table (phoneme v imports base1/v).
- Vowel length follows the spelling of i and u.
- फ is [pʰ]; most speakers have [f].
- Breathy voiced stops and h come from the Hindi base table (voiced closure plus voiceless aspiration sample); intonation uses the generic tunes.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 36 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), i (i=s8: dur=85), t (t=s11: f2=91 burst=-4 vot=16), p (p=s12: vot=13), k (k=s13: vot=24), ɳ (n=s19: f3=80), b (b=s22: voi=1 lead=75), d (d=s23: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s28: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s29: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s30: voi=1 lead=110), ʂ (S=s36: a4=54 f2=87 f3=83 f4=88), h (<h=s18: ms=70 whisper=44), ʌ (OE=s43: f1=112 f2=87 f3=114 dur=126), iː (i=s44: dur=117), ɪ (I=s45: dur=137), ɛ (E=s46: dur=126), aː (a=s48: dur=72), ʊ (U=s51: dur=185), uː (u=s44: dur=117), ĩ (i=s52: dur=85 nas=100), ã (A=s56: dur=175 nas=100), ũ (u=s60: dur=86 nas=100), aɪ (a=s61: g1=56 g2=146 g3=101 glide=1 dur=72), bʰ (b=s64: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s65: f2=91 burst=-4 voi=1 lead=75 brth=90 f0=-15), ɖ (d=s67: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75), ʈʰ (t=s68: f2=91 f3=79 f4=88 a4=52 a5=42 vot=60 asp=50), ɟʰ (d=s71: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75 brth=90 f0=-15), ɡʰ (g=s73: voi=1 lead=89 brth=90 f0=-15), aɪ̃ (a=s74: g1=56 g2=146 g3=101 glide=1 dur=72 nas=100).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (काय, कोण, कुठे, केव्हा ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Dhongde, Ramesh Vaman & Wali, Kashi (2009). Marathi. London Oriental and African Language Library 13. Amsterdam: John Benjamins. Pandharipande, Rajeshwari V. (1997). Marathi. Descriptive Grammars. London: Routledge. Pandharipande, Rajeshwari V. (2003). Marathi. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. Lisker, Leigh & Abramson, Arthur S. (1964). A cross-language study of voicing in initial stops: acoustical measurements. Word 20(3), 384-422. Berkson, Kelly Harper (2012). Capturing breathy voice: durational measures of oral stops in Marathi. Kansas Working Papers in Linguistics 33, 27-46. And 4 more in the profile.

## Malay (`ms`)

Austronesian, Malayo-Polynesian, Malayic. Described: Standard Malay. The segmental description follows the Standard Malay of Brunei (Clynes & Deterding 2011) with the differences of the Peninsular Malaysian standard based on Johor-Riau speech (the 'schwa variety'), which is the variety eSpeak NG follows.

**What the language has.** Six vowels including schwa; the spelling writes both /e/ and /ə/ as e. Voiced versus voiceless stops and affricates at four places. Four nasals m n ɲ ŋ. High and mid vowels contrast fully only in the penultimate syllable (bila versus bela, dua versus doa). No vowel or consonant length, no tone, no lexical stress. F, v, z, ʃ, x occur only in loanwords; the glottal stop is marginal.

Stress: no lexical stress; phrase-level prominence. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the letter e is still ambiguous between /e/ and /ə/; rules and a long exception list catch many words, the rest are guessed.
- ai and au are made diphthongs in closed syllables too, where the standard has two syllables (baik, laut, daun come out as one syllable).
- final r is pronounced, although final a is made schwa as in the Johor-Riau based standard, where final r is silent; the result mixes two pronunciation norms.
- fixed penultimate stress marked by length and loudness, against the phrase-level prominence described in the literature.
- final stops other than k are released.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 11 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (E=s1: f1=93 f2=78), ʔ (<q=s3: ms=50 hush=1), ɹ (l=s5: f1=127 f3=68), i (i=s4: dur=114), u (u=s4: dur=114), h (<h=s9: ms=70 whisper=44), b (b=s12: voi=1 lead=75), d (d=s12: voi=1 lead=75), ɡ (g=s12: voi=1 lead=75), aʊ (a=s35: g1=57 g2=72 g3=97 glide=1 dur=131), aɪ (a=s38: g1=55 g2=127 g3=106 glide=1 dur=131).

Melody: no syllable is picked out by pitch inside the phrase; the phrase ends with a rise or a fall. A question that wants yes or no rises at the end.
A question asked with a question word (apa, siapa, mana, bila ...) ends as a statement does, from a high question word.

Sources: Clynes, Adrian & Deterding, David (2011). Standard Malay (Brunei). Journal of the International Phonetic Association 41(2), 259-268. Teoh, Boon Seong (1994). The Sound System of Malay Revisited. Kuala Lumpur: Dewan Bahasa dan Pustaka. Yunus Maris (1980). The Malay Sound System. Kuala Lumpur: Fajar Bakti. Zuraidah Mohd Don, Knowles, Gerry & Yong, Janet (2008). How words can be misleading: a study of syllable timing and 'stress' in Malay. The Linguistics Journal 3(2). Grabe, Esther & Low, Ee Ling (2002). Durational variability in speech and the Rhythm Class Hypothesis. In C. Gussenhoven & N. Warner (eds.), Laboratory Phonology 7, 515-546. Berlin: Mouton de Gruyter. Deterding, David (2011). Measurements of the rhythm of Malay. Proceedings of the 17th International Congress of Phonetic Sciences, Hong Kong, 576-579. And 1 more in the profile.

## Maltese (`mt`)

Afro-Asiatic, Semitic, Central Semitic, Arabic (descended from Siculo-Arabic), with heavy Italo-Romance and English contact. Described: Standard Maltese.

**What the language has.** Vowel length: five short vowels against six long ones, the long ones in stressed syllables only. Consonant gemination, word-medially and word-finally, for all consonants. Voicing in obstruents, neutralised word-finally and in clusters. Glottal stop /ʔ/ (written q) as a full consonant. One voiceless back fricative /ħ/ (written ħ, and h in some positions). No emphatic consonants: the Arabic emphatics merged with the plain ones and left only vowel quality differences. /ɪː/ (written ie) against /iː/ and /ɛː/. /ts/ against /dz/ (both written z) and marginal /ʒ/ in recent loanwords.

Stress: weight-sensitive, one primary stress per word. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- mt_rules is a stub. Several consonant letters are given a following vowel as if they were spelled: d gives [de], k [ke], x [ʃe], z [tse], ż [zə], ċ [tʃə]. So dar gives [dear], xemx gives [ʃeˈemʃe], ħobż gives [hobzˈə], ċavetta gives [tʃəavˈetːa].
- q, the glottal stop /ʔ/, is dropped before a vowel and turned into a stressed schwa elsewhere: qalb gives [alp], triq gives [trɪˈə].
- ħ is the glottal [h] of the base table, and there is no [ħ] for word-final h or għ.
- j is read as the vowels [iu] and w as [u]: żejt gives [zeiut], għajn gives [aiun].
- z is always [tse] with a vowel; /dz/ and /ʒ/ are missing.
- ie is [iː] or [iˈə] instead of [ɪː]; vowels after r, k and n are lengthened by rule whatever the word (mara gives [maraː]), so written length and spoken length do not agree.
- Stress is penultimate for every word, and the explicit stress marks inside some rules (be, bie, q) override it; final superheavy syllables are not stressed.
- The vowel table is copied from another language: it contains front rounded vowels and their diphthongs and lacks the Maltese qualities [ɐ] and [ɪː].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 15 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (r=s7: f2=92 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), h (<h=s16: ms=70 whisper=44), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), c (t=s28: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s20: voi=1 lead=75), iu (i=s51: g1=113 g2=46 g3=82 glide=1 dur=117), ie (j=s55 e=s4: hold=55; dur=53).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (min, xi, fejn, meta ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Borg, Albert & Azzopardi-Alexander, Marie (1997). Maltese. London: Routledge. Borg, Alexander (1997). Maltese phonology. In Alan S. Kaye (ed.), Phonologies of Asia and Africa, vol. 1, 245-285. Winona Lake: Eisenbrauns. Vella, Alexandra (1994). Prosodic structure and intonation in Maltese and its influence on Maltese English. PhD dissertation, University of Edinburgh. Vella, Alexandra (2003). Language contact and Maltese intonation: some parallels with other language varieties. In Kurt Braunmüller & Gisella Ferraresi (eds.), Aspects of Multilingualism in European Language History, 261-283. Amsterdam: John Benjamins. Vella, Alexandra (2009). On Maltese prosody. In Bernard Comrie et al. (eds.), Introducing Maltese Linguistics, 47-68. Amsterdam: John Benjamins. Grice, Martine, Vella, Alexandra & Bruggeman, Anna (2019). Stress, pitch accent, and beyond: intonation in Maltese questions. Journal of Phonetics 76: 100913. And 2 more in the profile.

## Totontepec Mixe (`mto`)

Mixe-Zoquean, Mixean, Oaxaca Mixean. Described: Mixe of Totontepec Villa de Morelos, Oaxaca (North Highland Mixe in the classification of Wichmann 1995; own name Ayöök).

**What the language has.** Nine vowel qualities, the largest inventory among the Mixe varieties: the six inherited vowels i e a ɨ o u and three innovations written ä, ë and ö. Eight kinds of syllable nucleus for each vowel (Crawford 1963): short V, long Vː, short checked Vʔ, long checked Vːʔ, rearticulated VʔV, aspirated Vh, long aspirated Vːh and rearticulated aspirated VʔVh. Modal versus glottalised (creaky or interrupted) versus aspirated (breathy) vowels. Plain versus palatalised consonants throughout the inventory; palatalisation also carries grammatical meaning (third person and other prefixes). No voicing contrast in obstruents; s, l, r only in loans and sound-symbolic words.

Stress: fixed on the root; morphologically conditioned. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the glottal stop is never produced in running text: the saltillo letter U+A78C, for which the rule is written, is read aloud as the word 'saltillo'; the ASCII apostrophe and U+2019 are dropped with a pause; U+02BC is spelled out as a symbol. All glottalised nuclei (Vʔ, VʔV) are therefore lost.
- m, n and ŋ are defined as the syllabic nasals of the base table, so every nasal forms a syllable of its own and can take the stress (mäjk comes out with a stressed syllabic m).
- long vowels written double are two vowel segments in two syllables (tuun has two syllables) instead of one long nucleus.
- the letter j, which spells /h/, triggers the palatalisation rules, so a consonant next to /h/ gets a palatal glide (töjtïk comes out with [tʲ]); the letter y, which spells the palatal element, is only [j].
- ä is a back vowel [ɑ], where the descriptions have a front low vowel /æ/; ï is close-mid [ɘ] rather than close /ɨ/; ö is the diphthong [əʊ].
- stress follows the engine default (penultimate syllable) instead of the root syllable.
- aspirated vowels are a vowel plus a full [h] segment, with no breathy voice on the vowel.
- Spanish is used for letter and symbol names.

**What OpenEVV says.** Spoken by the module made from Latin American Spanish (`esux`). 26 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (a=s1: f1=76 dur=51), tʰ (t=s4: vot=68 asp=50), a (a=s5: dur=51), e (e=s6: dur=54), i (i=s7: dur=57), o (o=s8: dur=49), u (u=s9: dur=52), h (<h=s12: ms=70 whisper=44), b (b=s15: voi=1 lead=75), d (d=s15: voi=1 lead=75), g (g=s15: voi=1 lead=75), θ (D=s23: voi=0), ʐ (Z=s24: a4=42 f2=93 f3=72 f4=88), ʂ (S=s25: a4=54 f2=93 f3=77 f4=88), ʝ (Z=s28: f2=130 a4=0), ɛ (e=s33: f1=116 dur=54), eʊ (e=s39: g1=87 g2=64 g3=91 glide=1 dur=150), aɪ (a=s41: g1=69 g2=132 g3=105 glide=1 dur=142), eɪ (e=s42: g1=83 g2=109 g3=99 glide=1 dur=150), oɪ (o=s44: g1=84 g2=197 g3=103 glide=1 dur=155), ts (t=s46 s=s47: hold=85; hold=70), ɑ (a=s48: f1=110 f2=78 dur=51), ɘ (e=s49: f1=89 f2=91 dur=54), əʊ (a=s50: f1=76 g1=65 g2=76 g3=97 glide=1 dur=142), kʰ (k=s51: vot=85 asp=50), pʰ (p=s52: vot=65 asp=50).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

Sources: Crawford, John Chapman (1963). Totontepec Mixe Phonotagmemics. Norman: Summer Institute of Linguistics of the University of Oklahoma. Schoenhals, Alvin & Schoenhals, Louise C. (1965). Vocabulario mixe de Totontepec. México: Instituto Lingüístico de Verano. Wichmann, Søren (1995). The Relationship among the Mixe-Zoquean Languages of Mexico. Salt Lake City: University of Utah Press. Suslak, Daniel F. (2003). The story of ö: orthography and cultural politics in the Mixe highlands. Pragmatics 13(4), 551-563. Martínez García, Nereida Crystabel (2010). La contribución del análisis lingüístico en el desarrollo de sistemas de escritura: el caso del mixe de Santa María Yacochi. MA thesis, Universidad de Sonora. (Summarises Crawford's analysis of Totontepec.). Jany, Carmen (2007). Phonemic versus phonetic correlates of vowel length in Chuxnabán Mixe. Proceedings of the 33rd Annual Meeting of the Berkeley Linguistics Society. And 4 more in the profile.

## Myanmar (Burmese) (`my`)

Sino-Tibetan, Tibeto-Burman, Lolo-Burmese. Described: Standard colloquial Burmese (Yangon and Mandalay).

**What the language has.** Four tones that combine pitch, voice quality, duration and vowel quality: low, high, creaky, checked. Three-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced. Voiced against voiceless sonorants: m m̥, n n̥, ɲ ɲ̊, ŋ ŋ̊, l l̥ (and rare w ʍ). Plain against aspirated fricative, s against sʰ (merging for some speakers). Oral open rhymes, nasalised rhymes and rhymes closed by a glottal stop. Full (major) syllables against reduced (minor) syllables with ə.

Stress: no contrastive stress; major versus minor syllables. Rhythm: mixed. Tone: lexical tone, 4 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- dictsource/my_rules maps letters one by one with no syllable parsing and supplies no inherent vowel after a bare consonant, so most words come out as strings of consonants (မြန်မာ gives [mrn mts], မင်္ဂလာပါ gives [mŋ ɡltspe]).
- the vowel sign aa is turned into the consonant cluster ts.
- tone is not assigned by rule: only a few vowel signs carry a fixed tone digit (ii and uu tone 1, u and e tone 3, visarga tone 2); the creaky dot below and the asat are turned into a short pause, and the tokenizer ends the word at them.
- Burmese is not flagged as a tone language in src/libespeak-ng/tr_languages.c (the my case only disables numbers), so CalcPitches_Tone() is not used; tone phonemes give a contour shape but pitch levels come from the default stress-based intonation.
- the tone definitions do not match the language: low (1) and checked (4) have the same rise-fall contour, high (2) is a wide rise and creaky (3) a dip followed by a rise; none has creaky or breathy voice or a glottal closure.
- the vowel phonemes of ph_myanmar (a01 to a50, one for each written rhyme) are not used by my_rules, which call generic vowels of the base table.
- no voiceless nasals or lateral (ha-hto is mapped to h plus a), no aspirated fricative, no palatal affricates; θ is mapped to the voiced fricative D.
- written final stops are not turned into a glottal stop, final nasals are not turned into nasalisation, and there is no voicing sandhi and no reduction to minor syllables.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 14 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=199), ɹ (r=s6: f2=92 f3=77), a (A=s5: dur=239), t (t=s8: vot=17), p (p=s9: vot=13), k (k=s10: vot=28), h (<h=s15: ms=70 whisper=44), b (b=s19: voi=1 lead=75), d (d=s19: voi=1 lead=75), ɡ (g=s19: voi=1 lead=75), ð (v=s30: f2=149 f3=110 a6=28 ab=48), kh (k=s40: vot=85 asp=50), ph (p=s41: vot=65 asp=50), th (t=s42: vot=70 asp=50).

Tones: 1 (0:12,80:12,100:16), 2 (0:47,70:50,100:34), 3 (0:52,100:30), 4 (0:50,100:47). The pitch is made from them, syllable by syllable.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

**Not yet.** eSpeak NG's Burmese voice is a beginning.

Sources: Watkins, Justin W. (2001). Burmese. Journal of the International Phonetic Association 31(2), 291-295. Wheatley, Julian K. (1987). Burmese. In Bernard Comrie (ed.), The World's Major Languages. Croom Helm. Okell, John (1969). A Reference Grammar of Colloquial Burmese. Oxford University Press. Green, Antony D. (2005). Word, foot, and syllable structure in Burmese. In Justin Watkins (ed.), Studies in Burmese Linguistics. Pacific Linguistics. Bradley, David (1982). Register in Burmese. In David Bradley (ed.), Papers in South-East Asian Linguistics 8: Tonation. Pacific Linguistics. Thein Tun (1982). Some acoustic properties of tones in Burmese. In David Bradley (ed.), Papers in South-East Asian Linguistics 8: Tonation. Pacific Linguistics. And 4 more in the profile.

## Norwegian Bokmål (`nb`)

Indo-European, Germanic, North Germanic. Described: Urban East Norwegian, the educated speech of Oslo and the surrounding region, the usual spoken form of Bokmål and the variety described by Kristoffersen (2000).

**What the language has.** Two word accents on stressed syllables of words with at least one following syllable: accent 1 bønder 'farmers' versus accent 2 bønner 'beans', accent 1 loven 'the law' versus accent 2 låven 'the barn', accent 1 tanken 'the tank' versus accent 2 tanken 'the thought'. Complementary quantity in stressed syllables: long vowel plus short consonant versus short vowel plus long consonant (tak [tɑːk] 'roof' versus takk [tɑkː] 'thanks', hat versus hatt). Three close rounded vowels /y ʉ u/ with different lip rounding and tongue position (by, bu, bo). Nine vowel qualities, each long and short. Dental or alveolar /t d n l s/ versus retroflex /ʈ ɖ ɳ ɭ ʂ/ (kart [kɑʈ] versus katt). /ç/ versus /ʂ/ (kjede versus skjede), a contrast that many younger speakers have merged. The retroflex flap /ɽ/ versus /ɾ/ and /l/.

Stress: lexical, mostly initial in native words. Rhythm: stress-timed. Tone: pitch accent, 2 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- the word accents are not marked anywhere: the phoneme table has no tone phonemes and the dictionary has no accent marks, so bønder and bønner, and the two words tanken, sound the same.
- retroflexes are missing: rt, rd, rn, rl are said as r plus a dental ([kʊrt], [bɑrn], [parla]); only rs is changed, to the postalveolar [ʃ]; nothing happens across word boundaries.
- kj and k before front vowels are the velar fricative [x], not the palatal [ç], while tj is an alveolo-palatal sibilant: one phoneme has two wrong renderings.
- stressed a before a single consonant is short and front (dag, mat, tak, sak, gate come out with the short phoneme a, which is the one the table uses for /æ/) where the language has long [ɑː]; tak and takk therefore differ in the wrong way.
- the letter o is [uː] by default, so words with [oː] or [ɔ] are wrong unless a rule catches them (loven comes out with [uː]).
- every word is stressed on its first syllable: stasjon, universitet, telefon, banan, student.
- silent letters are pronounced: god is [ɡuːd], og is [uːɡ]; the dictionary has about 240 entries and the rule file only a handful of rules for each letter.
- final unstressed -e is an open schwa [a]-like vowel (phoneme a#) where the language has [ə].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (r=s7: f2=92 f3=77), r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s13: ms=70 whisper=44), iː (i=s35: dur=117), y (y=s5: dur=56), ɛ (E=s36: dur=84), aː (a=s37: dur=72), ɑ (A=s38: f1=91 f2=86), ɔ (O=s40: dur=85), ʊ (U=s41: dur=114), uː (u=s35: dur=117), ʉ (Y=s42: f1=78), ʉː (oe=s43: f1=82 f3=109), øy (oe=s48: g1=79 g2=120 g3=108 glide=1), ɒ (O=s54: f1=116 dur=85), aɪə (A j=s47 j=s47: hold=55; hold=55).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (hvem, hva, hvor, når ...) ends as a statement does, from a high question word.

**Not yet.** The two word accents are not in eSpeak NG's reading, so words are told apart by stress alone.

Sources: Kristoffersen, Gjert (2000). The Phonology of Norwegian. Oxford University Press. Vanvik, Arne (1979). Norsk fonetikk. Oslo: Universitetet i Oslo. Haugen, Einar and Joos, Martin (1952). Tone and intonation in East Norwegian. Acta Philologica Scandinavica 22, 41-64. Fintoft, Knut (1970). Acoustical Analysis and Perception of Tonemes in Some Norwegian Dialects. Oslo: Universitetsforlaget. Fretheim, Thorstein and Nilsen, Randi Alice (1989). Terminal rise and rise-fall tunes in East Norwegian intonation. Nordic Journal of Linguistics 12, 155-181. Simonsen, Hanne Gram; Moen, Inger; Cowen, Steve (2008). Norwegian retroflex stops in a cross linguistic perspective. Journal of Phonetics 36, 385-405. And 1 more in the profile.

## Nahuatl (Classical) (`nci`)

Uto-Aztecan, Southern Uto-Aztecan, Nahuan (Aztecan). Described: Classical Nahuatl of the Valley of Mexico in the sixteenth and seventeenth centuries, as reconstructed from colonial grammars (above all Carochi 1645) and modern philology; there are no recordings, so all phonetic detail is reconstructed.

**What the language has.** Short versus long vowels in four qualities: toca 'to follow' versus tōca 'to bury', tlatia 'to burn' versus tlātia 'to hide'. Glottal stop (saltillo) after a vowel versus its absence; it also marks the plural of many nouns and verbs. Lateral affricate tɬ versus t and l. Labialised velar kʷ versus k, also at the end of a syllable (tēuctli with /kʷ/). Three affricates ts, tʃ, tɬ and two sibilants s, ʃ. No voiced stops, no r; four vowel qualities without a separate u.

Stress: fixed, penultimate. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- tl is the sequence t plus voiced l; there is no voiceless lateral affricate [tɬ].
- kʷ at the end of a syllable is wrong: uc is read as [wk] (tēuctli comes out as [teːwktli]) and cuh as [kw] plus a glottal stop.
- vowel length depends on macrons in the text; the usual unmarked spelling gives short vowels everywhere.
- w at the end of a syllable (uh) is a voiced [w]; l, n are not devoiced or weakened there.
- long vowels are not shortened before the glottal stop or at the end of a word.
- no separate handling of the glottal stop at the end of an utterance.

**What OpenEVV says.** Spoken by the module made from Latin American Spanish (`esux`). 4 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=51), e (e=s5: dur=54), i (i=s6: dur=57), o (o=s7: dur=49).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

Sources: Carochi, Horacio (1645). Arte de la lengua mexicana con la declaración de los adverbios della. México. Andrews, J. Richard (2003). Introduction to Classical Nahuatl, revised edition. Norman: University of Oklahoma Press. Launey, Michel (2011). An Introduction to Classical Nahuatl, translated and adapted by Christopher Mackay. Cambridge: Cambridge University Press. Karttunen, Frances (1983). An Analytical Dictionary of Nahuatl. Austin: University of Texas Press. Lockhart, James (2001). Nahuatl as Written. Stanford: Stanford University Press.

## Nepali (`ne`)

Indo-European, Indo-Iranian, Indo-Aryan (Northern zone, Eastern Pahari). Described: Standard Nepali, the eastern dialect used by educated speakers and in the national media (Khatiwada 2009).

**What the language has.** Four-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced (/tsar/ 'four', /tsʰar/ 'ash', /dzar/ 'lover', /dzʱar/ 'weed'). Dental versus retroflex stops; the retroflexes are only weakly retroflex (apical postalveolar). Affricates are laminal alveolar /ts tsʰ dz dzʱ/, not palatal. Six oral vowels; five of them have nasal counterparts (there is no /õ/). No vowel length contrast, although the script writes long and short i and u. Geminate consonants, word-medial only (/pʌka/ 'cook!' : /pʌkka/ 'sure'). Only two fricatives /s ɦ/: the letters श ष स are all [s] in ordinary speech.

Stress: weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The affricates are the Hindi palatals (च [c], छ [cʰ], ज [ɟ], झ [ɟʰ]); Nepali has laminal alveolar [ts tsʰ dz dzʱ].
- श and ष are [ʃ] and [ʂ] (देश [deːʃ], विषय [wɪʂəjə]); Nepali speakers have [s].
- Long Hindi vowels eː, oː, aː are used beside short i, u although Nepali has no length contrast; औ is the monophthong [ɔː] and final ौं is [ɔːn] (काठमाडौं [kaːʈʰəmaːɖɔːn]) instead of a diphthong [ʌu] and a nasal vowel.
- Word-final र keeps the inherent vowel: घर is [ɡʰʌɾə].
- The infinitive ending -नु comes out with two vowels: गर्नु [ɡʌrrnuʲu].
- ज्ञ is [ɟɲ] (ज्ञान [ɟɲaːn]); Nepali has [ɡj].
- Allophony is missing: /ɖ/ after a vowel stays a stop (पढ्नु [pʌɖʰnu...]), breathy stops are not weakened between vowels, aspirates are not spirantised.
- Breathy voiced stops come from the Hindi base table (voiced closure plus voiceless aspiration sample); no breathy vowel onset.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 53 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), tʰ (t=s5: f2=91 burst=-4 vot=68 asp=50), a (A=s6: dur=175), e (e=s7: dur=80), i (i=s8: dur=85), o (o=s7: dur=80), u (u=s9: dur=86), t (t=s11: f2=91 burst=-4 vot=16), p (p=s12: vot=13), k (k=s13: vot=28), ɭ (l=s16: f2=111 f3=71), h (<h=s18: ms=70 whisper=44), ɳ (n=s19: f3=80), ɲ (n=s20: f2=136 f3=109), r. (l=s21: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s22: voi=1 lead=75), d (d=s23: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s28: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s29: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s22: voi=1 lead=75), ʋ (v=s31: af=-14), ʂ (S=s35: a4=54 f2=87 f3=83 f4=88), ɣ (r=s39: f1=73 f3=116), q (k=s40: f2=68 f3=109 f1=118 burst=3 vot=30), ʌ (OE=s42: f1=112 f2=87 f3=114 dur=126), iː (i=s43: dur=117), ɪ (I=s44: dur=137), ɛ (E=s45: dur=126), aː (a=s47: dur=72), ɔ (O=s49: dur=150), ʊ (U=s50: dur=185), ẽ (e=s53: dur=80 nas=100), ʌ̃ (OE=s56: f1=112 f2=87 f3=114 dur=126 nas=100), õ (o=s53: dur=80 nas=100), pʰ (p=s62: vot=65 asp=50), bʰ (b=s63: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s64: f2=91 burst=-4 voi=1 lead=75 brth=90 f0=-15), ʈ (t=s65: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s66: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75), ʈʰ (t=s67: f2=91 f3=79 f4=88 a4=52 a5=42 vot=60 asp=50), ɖʰ (d=s68: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75 brth=90 f0=-15), cʰ (t=s69: f2=135 f3=112 a3=56 a4=56 vot=75 asp=50), ɟʰ (d=s70: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75 brth=90 f0=-15), kʰ (k=s71: vot=85 asp=50), ɡʰ (g=s63: voi=1 lead=75 brth=90 f0=-15), ʌɪ (a=s74: f1=76 f2=94 g1=53 g2=144 g3=101 glide=1 dur=72), ʌʊ (a=s75: f1=76 f2=94 g1=55 g2=81 g3=93 glide=1 dur=72).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (के, को, कहाँ, कहिले ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Khatiwada, Rajesh (2009). Nepali. Journal of the International Phonetic Association 39(3), 373-380. Pokharel, Madhav Prasad (1989). Experimental Analysis of Nepali Sound System. PhD dissertation, University of Pune. Bandhu, Chudamani; Dahal, Ballabh Mani; Holzhausen, Andreas & Hale, Austin (1971). Nepali Segmental Phonology. Kirtipur: Summer Institute of Linguistics, Tribhuvan University. Clements, George N. & Khatiwada, Rajesh (2007). Phonetic realization of contrastively aspirated affricates in Nepali. Proceedings of the 16th International Congress of Phonetic Sciences, Saarbrücken, 629-632. Acharya, Jayaraj (1991). A Descriptive Grammar of Nepali and an Analyzed Corpus. Washington: Georgetown University Press. Riccardi, Theodore (2003). Nepali. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. And 2 more in the profile.

## Dutch (`nl`)

Indo-European, Germanic, West Germanic, Low Franconian. Described: Northern Standard Dutch (the Netherlands); the main differences of Southern (Belgian) Standard Dutch are noted where they matter.

**What the language has.** Tense (long) versus lax (short) vowels, differing in quality and length: /aː/ versus /ɑ/ (maan versus man), /eː/ versus /ɪ/ and /ɛ/, /oː/ versus /ɔ/, /øː/ versus /ʏ/. Front rounded vowels /y ʏ øː œy/ versus front unrounded and back rounded vowels. Three true diphthongs /ɛi œy ɑu/ (ijs, huis, koud) versus the long mid vowels /eː øː oː/. Voiced versus voiceless obstruents /b d v z ɣ/ versus /p t f s x/, neutralised at the end of a word. /ʋ/ versus /v/ versus /f/ (wee, vee, fee); for many northern speakers /v/ and /f/ merge word-initially. /x/ versus /ɣ/, kept in the south and largely merged in the north. Schwa /ə/ as a separate unstressable vowel. Lexical stress (vóórkomen 'to occur' versus voorkómen 'to prevent').

Stress: lexical, weight-sensitive, within a three-syllable window. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- /r/ is always an alveolar trill (imported from base1/R2); neither the uvular variants nor the approximant used in the coda in the west of the Netherlands are available.
- /eː øː oː/ use closing-diphthong formant data also before /r/ (door, kleur), where the standard has monophthongal or centring vowels; only some words (meer, voor) get the special phonemes I: and O:.
- /i y u/ are not lengthened before /r/ (bier, vuur, boer use the short phonemes).
- the marginal long vowels /ɛː œː ɔː/ are missing: crème comes out as [krɛmə], militair with short [ɛ], freule with [øː], zone with [oː].
- progressive devoicing of fricatives is missing (afval [fv], opvallen [pv]) and regressive voicing is applied unevenly (zakdoek [ɡd] but opbellen [pb]).
- stress errors in compounds and particle verbs: huisdeur, ijsbeer, handdoek, zakdoek and opbellen are stressed on the second part; oranje is stressed on the first syllable.
- no schwa insertion in melk, film, arm, kalm.
- written g is a voiced velar [ɣ] and ch a strong [x] imported from Afrikaans: this matches neither the northern standard (both voiceless) nor the southern one (front-velar).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 17 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s8: tap=3 tapms=18 f2=109 f3=77), u (u=s7: f1=132 dur=57), t (t=s9: vot=15), p (p=s10: vot=10), k (k=s11: vot=25), h (<h=s16: ms=70 whisper=44), b (b=s20: voi=1 lead=85), d (d=s21: voi=1 lead=80), ʋ (v=s32: af=-14), ɣ (r=s40: f1=73 f3=116), ɪ (I=s43: f3=90), ɛ (E=s45: dur=84), ɔ (O=s46: f1=90 dur=85), aː (a=s48: dur=72), ɑ (O=s49: f1=116 f2=114 dur=85), oː (o=s53: f1=122 f2=121), ɛɪ (E:=s54: g1=81 g2=95 g3=96 glide=1).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (wie, wat, waar, wanneer ...) ends as a statement does, from a high question word.

Sources: Gussenhoven, Carlos (1992). Dutch. Journal of the International Phonetic Association 22(1-2), 45-47. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Verhoeven, Jo (2005). Belgian Standard Dutch. Journal of the International Phonetic Association 35(2), 243-247. Booij, Geert (1995). The Phonology of Dutch. Oxford University Press. Collins, Beverley and Mees, Inger M. (2003). The Phonetics of English and Dutch. 5th edition. Leiden: Brill. Pols, L. C. W.; Tromp, H. R. C.; Plomp, R. (1973). Frequency analysis of Dutch vowels from 50 male speakers. Journal of the Acoustical Society of America 53(4), 1093-1101. Adank, Patti; van Hout, Roeland; Smits, Roel (2004). An acoustic description of the vowels of Northern and Southern Standard Dutch. Journal of the Acoustical Society of America 116(3), 1729-1738. And 7 more in the profile.

## Nogai (`nog`)

Turkic, Kipchak (Kipchak-Nogai). Described: Literary Nogai of the North Caucasus (Dagestan, Karachay-Cherkessia, Stavropol), Cyrillic script.

**What the language has.** Nine vowels: front /i y e ø æ/ and back /ɯ u o ɑ/, the front rounded and open front vowels spelt with digraphs (уь, оь, аь). Velar /k ɡ/ versus uvular /q ʁ/, tied to vowel backness in native words. Voiced versus voiceless obstruents. Sibilant shift typical of the Kipchak-Nogai group: /ʃ/ where most Turkic languages have /tʃ/ and /s/ where they have /ʃ/ (уьш 'three', бес 'five', тас 'stone').

Stress: fixed final by default, with morphological exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the phoneme table is the Kazakh one without changes; the mid vowel оь (/ø/) has the short duration of the high vowels (100 against 200).
- outside the digraphs, ь and ъ are read as glottal stops (кельди, альбом, объект).
- the rule for the past copula еди stresses the penultimate syllable of every word ending in -еди (келеди, келмеди).
- the clear l chosen by the rules is turned into dark [ɫ] by the Kazakh phoneme table whenever no front vowel follows (эл, бел, кел-).
- Russian loanwords need the _^_RU mark in the word list, which has only three such entries.
- t is the unaspirated base2 stop while p and k use aspirated samples.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 23 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), e (e=s6: dur=80), o (o=s6: dur=80), u (u=s8: dur=86), r (l=s9: tap=3 tapms=18 f2=109 f3=77), ɫ (l=s13: f2=71 f3=91), ɕ (S=s31: a2=31 a3=34 a4=34 a5=22 f2=119 f3=116), q (k=s34: f2=68 f3=109 f1=118 burst=3), ɪ (I=s36: dur=137), ɵ (Y=s37: f2=89 f3=107 dur=137), ʊ (U=s38: dur=185), ɑ (A=s39: f1=91 f2=86 dur=175), æ (E=s40: f1=124 f2=92 f3=92 dur=126), ʀ (r=s10: tap=3 tapms=18 f2=85 f3=112), a (A=s5: dur=175), i (i=s7: dur=85), ja (j A=s5: dur=175), ʌ (OE=s46: f1=112 f2=87 f3=114 dur=126).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (не, ким, кайда, кашан ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Csató, Éva Á. & Karakoç, Birsel (1998). Noghay. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge. Baskakov, N. A. (1940). Nogajskij jazyk i ego dialekty: grammatika, teksty i slovar'. Izdatel'stvo Akademii Nauk SSSR.

## Oromo (`om`)

Afro-Asiatic, Cushitic, Lowland East Cushitic. Described: Western and central (Mecha-Tulama) Oromo as written in the Qubee orthography; the tone description follows Harar Oromo (Owens 1985), the best described variety.

**What the language has.** Vowel length in all five qualities: hara 'lake' against haaraa 'new'. Consonant gemination: badaa 'bad' against baddaa 'highland'. Plain voiceless, voiced and ejective stops and affricates: t d tʼ, k ɡ kʼ, tʃ dʒ tʃʼ. Implosive /ɗ/ (written dh) against /d/ and ejective /tʼ/ (written x). Glottal stop (written with an apostrophe, hudhaa) as a full consonant. Pitch accent with grammatical function. /p v z/ occur in loanwords only; the labial ejective /pʼ/ (written ph) is infrequent.

Stress: pitch accent; stress follows the high tone. Rhythm: mixed. Tone: pitch accent, 3 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- dh, the implosive /ɗ/, is the dental fricative [ð]: the phoneme D calls the base phoneme D (English th in this). dhugaa gives [ðuɡaː], haadha gives [haːða].
- y, the glide /j/, is sent to a vowel phoneme named y, which the table defines twice (as a front rounded vowel and as a central vowel with the IPA name ?). yaada begins with a vowel instead of [j].
- The glottal stop written with an apostrophe is dropped: har'a gives [hara], re'ee gives [reeː].
- ph, the ejective /pʼ/, is an unaspirated [p] whose IPA name is Φ; of the ejectives only q uses an ejective recording (ustop/k_ejc), x and c use unaspirated plosive samples after a pause.
- No pitch accent. Stress is penultimate, or final when the final vowel is long and the penult short, and it is realised with the default stress contour.
- Unstressed short i is changed to a lax [ɪ]; the vowel table contains unused vowels copied from other languages.
- z is [ts].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 15 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s8: vot=17), k (k=s10: vot=28), h (<h=s15: ms=70 whisper=44), b (b=s19: voi=1 lead=75), d (d=s19: voi=1 lead=75), ɡ (g=s19: voi=1 lead=75), ð (v=s30: f2=149 f3=110 a6=28 ab=48), ? (<q=s3: ms=50 hush=1), k` (k=s10: vot=28), t` (t=s8: vot=17).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (eenyu, maal, eessa, yoom ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent, last 88 per cent of the module's own.

**Not yet.** The pitch accent is not in eSpeak NG's reading.

Sources: Owens, Jonathan (1985). A Grammar of Harar Oromo (Northeastern Ethiopia). Hamburg: Buske. Lloret, Maria-Rosa (1997). Oromo phonology. In Alan S. Kaye (ed.), Phonologies of Asia and Africa. Winona Lake: Eisenbrauns. Banti, Giorgio (1988). Two Cushitic systems: Somali and Oromo nouns. In Harry van der Hulst & Norval Smith (eds.), Autosegmental Studies on Pitch Accent. Dordrecht: Foris. Stroomer, Harry (1995). A Grammar of Boraana Oromo (Kenya). Köln: Rüdiger Köppe. Gragg, Gene B. (1976). Oromo of Wellegga. In M. Lionel Bender (ed.), The Non-Semitic Languages of Ethiopia. East Lansing: Michigan State University. Mous, Maarten (2022). The grammatical primacy of tone in Cushitic. Stellenbosch Papers in Linguistics Plus 62. And 1 more in the profile.

## Oriya (`or`)

Indo-European, Indo-Iranian, Indo-Aryan (Eastern zone). Described: Standard Odia (educated speech of Cuttack, Puri and Bhubaneswar).

**What the language has.** Four-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced. Dental versus retroflex stops; /n/ : /ɳ/; /l/ : /ɭ/ (retroflex lateral, kept in Odia unlike Bengali and Hindi). Six vowel qualities /i e a ɔ o u/ with no length contrast: the long and short i and u of the script sound alike. Oral versus nasal vowels. A single sibilant /s/ for the three letters ଶ ଷ ସ; [ʃ] only in some clusters. Every consonant letter without a vowel sign is followed by /ɔ/, also at the end of a word: there is no schwa deletion (ଘର /ɡʱɔɾɔ/ 'house').

Stress: weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- ଘ is a plain [ɡ] at the start of a word and after a vowel (the first rule for the letter gives g, not g#): ଘର comes out as [ɡɔɾɔ].
- ଳ is the syllabic l phoneme of the base table followed by a long vowel: ଫଳ [pʰɔl̩ɔː], ଜଳ [ɟɔl̩ɔː], କମଳ [kɔmɔl̩ɔː] gain a syllable, and there is no retroflex lateral.
- ଣ is always [n] (ପାଣି [pani], ମଣିଷ [mɔnisɔ]); the retroflex nasal is lost.
- One phoneme /dʒ/ has two sounds: ଜ is the palatal stop phoneme [ɟ], ଯ is [dʒ].
- ଜ୍ଞ is [ɡɡ] (ଜ୍ଞାନ [ɡɡanɔ]) and କ୍ଷ is doubled [kʰkʰ] (ଲକ୍ଷ୍ମୀ [lɔkʰkʰmi]).
- The translator uses the Hindi settings (stress on the last heavy syllable) with the Bengali phoneme table.
- Breathy voiced stops come from the Hindi base table (voiced closure plus voiceless aspiration sample); /ɦ/ is voiceless [h]; intonation uses the generic tunes.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: tʰ (t=s4: vot=68 asp=50), i (i=s5: dur=114), u (u=s5: dur=114), h (<h=s9: ms=70 whisper=44), r. (r=s11: f3=87), b (b=s12: voi=1 lead=75), d (d=s12: voi=1 lead=75), ɟ (d=s17: f2=148 f3=109 a3=56 a4=56 voi=1 lead=75), ɡ (g=s12: voi=1 lead=75), ɔː (c=s38: dur=150), uː (u=s40: dur=171), pʰ (p=s48: vot=65 asp=50), bʰ (b=s49: voi=1 lead=75 brth=90 f0=-15), dʰ (d=s49: voi=1 lead=75 brth=90 f0=-15), ʈ (t=s50: f3=77 f4=88 a4=52 a5=42), ʈʰ (t=s52: f3=77 f4=88 a4=52 a5=42 vot=60 asp=50), ɟʰ (d=s55: f2=148 f3=109 a3=56 a4=56 voi=1 lead=75 brth=90 f0=-15), kʰ (k=s56: vot=85 asp=50), tʃʰ (C >h=s58: ms=45 whisper=46).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (କଣ, କିଏ, କେଉଁଠି, କେବେ ...) ends as a statement does, from a high question word.

Sources: Ray, Tapas S. (2003). Oriya. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Neukom, Lukas & Patnaik, Manideepa (2003). A Grammar of Oriya. Arbeiten des Seminars für Allgemeine Sprachwissenschaft 17. Zürich: Universität Zürich. Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. Khan, Sameer ud Dowla (2016). The intonation of South Asian languages: towards a comparative analysis. Proceedings of Formal Approaches to South Asian Languages 6, 23-36 (areal intonation pattern only).

## Punjabi (`pa`)

Indo-European, Indo-Iranian, Indo-Aryan (Northwestern zone). Described: Standard Punjabi based on the Majhi dialect, as written in Gurmukhi (Indian Punjab). Tone numerals and formants come from the Lyallpuri (Faisalabad) variety of Hussain et al. 2020, tone acoustics also from Indian Punjabi speakers (Evans et al. 2018).

**What the language has.** Three-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced. The breathy voiced series of the script (ਘ ਝ ਢ ਧ ਭ) no longer exists as such and is reflected in tone. Lexical tone on the stressed syllable: /kòːɽaː/ 'horse' (low), /koːɽaː/ 'whip' (mid), /kóːɽaː/ 'leper' (high). Dental versus retroflex stops; /n/ : /ɳ/; /l/ : /ɭ/; tap /ɾ/ versus retroflex flap /ɽ/. Three short central vowels /ɪ ə ʊ/ against seven long peripheral vowels. Oral versus nasal vowels for the seven peripheral vowels. Consonant gemination for 19 consonants, always after a short central vowel (/pət̪aː/ 'address' : /pət̪ːaː/ 'leaf'). Loan fricatives /f z x ɣ/ are used by educated and urban speakers only.

Stress: weight-sensitive, not contrastive. Rhythm: mixed. Tone: lexical tone, 3 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- There is one tone phoneme, written + and commented 'high tone', defined as Tone(5, 30, envelope/p_512): pitch raised above the intonation line, falling from the top of that range to the bottom by mid-vowel and rising slightly. The shape is that of the low tone [513]; the name is wrong, and it prints as a plain '+' in phoneme and IPA output.
- The tone is inserted only by the spelling rules for word-initial ਘ ਝ ਧ ਭ, which also turn the stop into k, c, t, p. For ਢ the rule before a vowel sign has no tone mark, so ਢੋਲ and ਢਿੱਡ come out as [ʈol], [ʈɪɖ] without tone.
- The high tone is never marked. Postvocalic ਹ and the subscript h are pronounced as [h]: ਚਾਹ [cah], ਬਾਹਰ [bahəɾ], ਪੜ੍ਹ [pʌɽh], ਕੋੜ੍ਹਾ [koɽha], ਮੂੰਹ [mũh].
- Non-initial ਘ ਝ ਢ ਧ ਭ are pronounced as Hindi breathy voiced stops with no tone: ਕੁਝ [kʊɟʰ], ਦੁੱਧ [dʊdʰ], ਮਾਘ [maɡʰ], ਸਿੰਘ [sɪ̃ɡʰ], ਸੁਧਾਰ [sʊdʰaɾ]. Punjabi has plain voiced stops there, with high tone before them or low tone after them.
- Gemination written with addak is lost before a word-final consonant (ਸੱਚ [sʌc], ਹੱਥ [hʌtʰ], ਅੱਖ [ʌkʰ]) and for the five tone letters, which have no addak rules (ਦੁੱਧ, ਬੁੱਢਾ).
- A vowel with tippi becomes a nasal vowel and the nasal consonant is dropped before a stop: ਅੰਬ [ʌ̃b], ਮੁੰਡਾ [mʊ̃ɖa] for [əmb], [mʊɳɖaː].
- /ʋ/ is the fricative [v] of the base table; the retroflex flap has no IPA name and prints as 'r.'.
- Intonation uses the generic eSpeak tunes and takes no account of the lexical tones.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 25 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f1=126 f2=78 dur=140), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), a (A=s6: f1=78 dur=150), e (e=s7: dur=70), i (i=s8: f1=114 f2=109 dur=75), o (o=s9: f2=114 dur=70), t (t=s12: f2=91 burst=-4 vot=16), p (p=s13: vot=13), k (k=s14: vot=28), r (l=s11: tap=3 tapms=18 f2=109 f3=77), ɳ (n=s20: f3=80), b (b=s23: voi=1 lead=75), d (d=s24: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s29: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), h (<h=s19: ms=70 whisper=44), ʌ (OE=s43: f1=112 f2=87 f3=114), ɪ (I=s45: f3=91 dur=120), ʊ (U=s53: f1=91 f2=85 dur=160), ĩ (i=s55: f1=114 f2=109 dur=75 nas=100), ã (A=s59: f1=78 dur=150 nas=100), dʰ (d=s69: f2=91 burst=-4 voi=1 lead=75 brth=90 f0=-15), ʈ (t=s70: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), kʰ (k=s76: vot=85 asp=50).

Tones: + (0:45,35:12,100:30). The pitch is made from them, syllable by syllable.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

**Not yet.** eSpeak NG marks one of the three tones, the low one after the letters that were breathy stops; the high tone is not read.

Sources: Hussain, Qandeel; Proctor, Michael; Harvey, Mark & Demuth, Katherine (2020). Punjabi (Lyallpuri variety). Journal of the International Phonetic Association 50(2), 282-297. Bhatia, Tej K. (1993). Punjabi: A Cognitive-Descriptive Grammar. London: Routledge. Gill, Harjeet Singh & Gleason, Henry A. (1962). A Reference Grammar of Panjabi. Hartford: Hartford Seminary Foundation. Shackle, Christopher (2003). Panjabi. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Bailey, Thomas Grahame (1914). A Panjabi Phonetic Reader. London: University of London Press. Bhatia, Tej K. (1975). The evolution of tones in Punjabi. Studies in the Linguistic Sciences 5(2), 12-24. And 8 more in the profile.

## Papiamento (`pap`)

Iberian-based (Portuguese and Spanish) creole of the ABC islands, with strong Dutch influence. Described: Papiamentu of Curaçao (the variety of the tone studies), in the phonemic spelling of Curaçao and Bonaire; Aruban Papiamento uses an etymological spelling.

**What the language has.** Close-mid versus open-mid vowels, marked in the Curaçao spelling (e versus è, o versus ò). Front rounded vowels /y ø/ (written ü, ù), mostly in words from Dutch (hür 'rent', bùs 'bus', minüt). Lexical stress: penultimate versus final (para [ˈpara] versus pará [paˈra] 'stopped'). Lexical tone, independent of stress: words of two syllables with penultimate stress have either a high-low or a low-high pitch pattern (para high-low 'bird' versus para low-high 'to stop'; biaha high-low 'trip' versus biaha low-high 'to travel'; sala high-low 'living room' versus sala low-high 'to salt'). Voiced versus voiceless obstruents, including /z v ʒ/ from Dutch and Iberian sources. /x/ (written g before e, i, and in Dutch words) versus /h/.

Stress: lexical, combined with lexical tone. Rhythm: syllable-timed. Tone: lexical tone, 3 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- no tone at all: the language is set up with the Spanish-type stress settings and the generic intonation, so para 'bird' and para 'to stop', biaha noun and verb, sound the same; only the place of stress is modelled.
- telling the two tone classes apart needs the part of speech or a word list, since the spelling does not mark tone; the word list has about 120 lines and no tone information.
- there is no language-specific phoneme table: the generic table base2 is used and schwa is missing, so final -er, -el, -en have a full vowel (hòmber [hˈɔmber]).
- i and u before a vowel are always glides, which shifts the stress in words such as dia ([djˈa] instead of [ˈdia]).
- /r/ is always a full trill.
- no tune set is selected, so the generic default tunes are used.

**What OpenEVV says.** Spoken by the module made from Latin American Spanish (`esux`). 9 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=135), e (e=s5: dur=141), i (i=s6: dur=149), o (o=s7: dur=146), u (u=s8: dur=154), h (<h=s12: ms=70 whisper=44), b (b=s15: voi=1 lead=75), d (d=s15: voi=1 lead=75), ɡ (g=s15: voi=1 lead=75).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (kiko, ken, unda, kuandu ...) ends as a statement does, from a high question word.

**Not yet.** The tone patterns of words are not in eSpeak NG's reading.

Sources: Kouwenberg, Silvia and Murray, Eric (1994). Papiamentu. München: Lincom Europa (Languages of the World/Materials 83). Römer, Raúl G. (1991). Studies in Papiamentu Tonology. Amsterdam and Kingston: Caribbean Culture Studies 5. Römer, Raúl G. (1977). Polarization phenomena in Papiamentu. Amsterdam Creole Studies 1. Remijsen, Bert and van Heuven, Vincent J. (2005). Stress, tone and discourse prominence in the Curaçao dialect of Papiamentu. Phonology 22, 205-235. Rivera-Castillo, Yolanda and Pickering, Lucy (2004). Phonetic correlates of stress and tone in a mixed system. Journal of Pidgin and Creole Languages 19(2), 261-284. Kouwenberg, Silvia (2004). The grammatical function of Papiamentu tone. Journal of Portuguese Linguistics 3(2). And 2 more in the profile.

## Pennsylvania Dutch (Lancaster) (`pdc`)

Indo-European, Germanic, West Germanic, High German, Rhine Franconian (Palatine base). Described: Pennsylvania Dutch (Pennsylvania German) as spoken by the Old Order Amish and Old Order Mennonites of Lancaster County, Pennsylvania; text in the Buffington-Barba spelling.

**What the language has.** Short versus long vowels, with a difference of quality: /ɪ/ versus /iː/, /ɛ/ versus /eː/, /ʊ/ versus /uː/, /ʌ/ versus /oː/, /ɑ/ versus /ɔː/. No front rounded vowels: the vowels of German schön, Tür, böse, Feuer are unrounded (schee, Dier, bees, Feier). Long /æː/ (written ae: Kaes, Baer) versus /eː/ (written ee: schee). Back rounded long /ɔː/ (written aa: Baam, Fraa, Daag) versus /oː/ (written oo: Schprooch). Palatal and velar fricatives [ç x] and the weak voiced fricative [ɣ] between back vowels (saage, Waage). /v/ (written w, ww) versus /f/ (written f, v). Lexical stress in prefixed words and loans.

Stress: lexical, mostly initial. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the stops b, d, g are inherited from the German table and are fully voiced; the descriptions have voiceless lenis stops.
- yes-no questions use tune q4, which ends in a rise; the documented pattern is a rise to the accented syllable followed by a final fall.
- ei stays [aɪ] before /r/ and /l/ (Eil, Meil, Scheier), where Keiser reports monophthongs for Pennsylvania speakers.
- stress is put on the first syllable of words that carry it later (Babbier is [ˈbɑbiːɐ]).
- English loans that keep their English spelling are read by the German-type letter rules (computer is [ˈkʌmpuːtɐ]); the pronunciation list has about 260 entries, mostly letters, symbols, numbers and function words.
- postvocalic /l/ uses the dark l of the English table and onset /l/ the clear one, which fits the voice notes, but there is no way to choose the older clear l and tapped r within this voice.
- the pronunciations have not been checked by native speakers (the voice is marked 'testing').

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 16 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (r=s7: f2=92 f3=77), ɑ (A=s8: f1=91 f2=86), i (i=s5: dur=56), ʋ (v=s11: af=-14), h (<h=s15: ms=70 whisper=44), ɣ (r=s33: f1=73 f3=116), ɐ (A=s36: f1=85), ɛ (E=s37: dur=84), ʊ (U=s40: dur=114), ɑː (a=s42: f1=89 f2=86 dur=72), uː (u=s43: dur=117), aː (a=s44: dur=72), aɪ (a=s45: g1=56 g2=146 g3=101 glide=1 dur=72), ɔː (O=s53: dur=220), ʌ (OE=s54: f1=112 f2=87 f3=114 dur=84), æːɐ̯ (E=s59: f1=124 f2=92 f3=92 g1=121 g2=76 g3=94 glide=1 dur=209).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (wer, was, wu, wann ...) ends as a statement does, from a high question word.

Sources: Buffington, Albert F. and Barba, Preston A. (1954). A Pennsylvania German Grammar. Allentown: Schlechter's. Frey, J. William (1942). A Simple Grammar of Pennsylvania Dutch. Clinton, South Carolina: Jacobs Press. Reed, Carroll E. and Seifert, Lester W. (1954). A Linguistic Atlas of Pennsylvania German. Marburg. Van Ness, Silke (1994). Pennsylvania German. In König and van der Auwera (eds.), The Germanic Languages. London: Routledge. Louden, Mark L. (2016). Pennsylvania Dutch: The Story of an American Language. Baltimore: Johns Hopkins University Press. Keiser, Steven Hartman (2012). Pennsylvania German in the American Midwest. Publication of the American Dialect Society 96. Durham: Duke University Press. And 4 more in the profile.

## Pennsylvania Dutch (Lehigh) (`pdc-x-lehigh`)

Indo-European, Germanic, West Germanic, High German, Rhine Franconian (Palatine base). Described: Eastern nonsectarian Pennsylvania Dutch (the speech of the Lutheran and Reformed 'church people') of Lehigh, Northampton and Berks counties, Pennsylvania, the variety on which the Buffington-Barba grammar and spelling are based.

**What the language has.** Short versus long vowels, with a difference of quality: /ɪ/ versus /iː/, /ɛ/ versus /eː/, /ʊ/ versus /uː/, /ʌ/ versus /oː/, /ɑ/ versus /ɔː/. No front rounded vowels: the vowels of German schön, Tür, böse, Feuer are unrounded (schee, Dier, bees, Feier). Three diphthongs /aɪ aʊ ɔɪ/ (Deitsch, Haus, Boi). Long /æː/ (written ae: Kaes) versus /eː/ (written ee: schee). Back rounded long /ɔː/ (written aa: Baam, Fraa) versus /oː/ (written oo: Schprooch). Palatal and velar fricatives [ç x] and the weak voiced fricative [ɣ] between back vowels. /v/ (written w, ww) versus /f/ (written f, v). Lexical stress in prefixed words and loans.

Stress: lexical, mostly initial. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the stops b, d, g are inherited from the German table and are fully voiced; the descriptions have voiceless lenis stops.
- yes-no questions use tune q4, which ends in a rise; the documented pattern is a rise to the accented syllable followed by a final fall.
- stress is put on the first syllable of words that carry it later (Babbier is [ˈbɑbiːɐ]).
- English loans that keep their English spelling are read by the German-type letter rules; the pronunciation list has about 260 entries.
- the voice differs from the Lancaster voice in four settings only (au, r, l, and the vowel before vocalised r); other eastern features documented by Reed and Seifert, above all differences of vocabulary and word form, are not represented.
- the pronunciations have not been checked by native speakers (the voice is marked 'testing').

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 12 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɾ (l=s1: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), ɑ (A=s7: f1=91 f2=86), i (i=s5: dur=56), ʋ (v=s10: af=-14), h (<h=s14: ms=70 whisper=44), ɐ (A=s35: f1=85), ɛ (E=s36: dur=84), aʊ (a=s43: g1=58 g2=82 g3=93 glide=1 dur=72), aɪ (a=s44: g1=56 g2=146 g3=101 glide=1 dur=72), ɔː (O=s52: dur=220), ʌ (OE=s53: f1=112 f2=87 f3=114 dur=84), eːɐ̯ (e=s58: g1=168 g2=66 g3=91 glide=1 dur=132).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (wer, was, wu, wann ...) ends as a statement does, from a high question word.

Sources: Buffington, Albert F. and Barba, Preston A. (1954). A Pennsylvania German Grammar. Allentown: Schlechter's. Frey, J. William (1942). A Simple Grammar of Pennsylvania Dutch. Clinton, South Carolina: Jacobs Press. Reed, Carroll E. and Seifert, Lester W. (1954). A Linguistic Atlas of Pennsylvania German. Marburg. Van Ness, Silke (1994). Pennsylvania German. In König and van der Auwera (eds.), The Germanic Languages. London: Routledge. Louden, Mark L. (2016). Pennsylvania Dutch: The Story of an American Language. Baltimore: Johns Hopkins University Press. Kopp, Achim (1999). The Phonology of Pennsylvania German English as Evidence of Language Maintenance and Shift. Selinsgrove: Susquehanna University Press. And 3 more in the profile.

## Pennsylvania Dutch (Midwest) (`pdc-x-midwest`)

Indo-European, Germanic, West Germanic, High German, Rhine Franconian (Palatine base). Described: Pennsylvania Dutch (Pennsylvania German) of the Amish settlements of the American Midwest: Holmes County (Ohio), Elkhart and LaGrange counties (Indiana), Kalona (Iowa), Arthur (Illinois); text in the Buffington-Barba spelling.

**What the language has.** Short versus long vowels, with a difference of quality: /ɪ/ versus /iː/, /ɛ/ versus /eː/, /ʊ/ versus /uː/, /ʌ/ versus /oː/, /ɑ/ versus /ɔː/. No front rounded vowels. The monophthong from ei, about [ɛː], is close to /eː/ and may be merging with it (Keiser 2012), so that pairs such as Deitsch and words with ee depend on a small difference of height. Long /æː/ (written ae) versus /eː/ (written ee). Back rounded long /ɔː/ (written aa) versus /oː/ (written oo). Palatal and velar fricatives [ç x] and the weak voiced fricative [ɣ] between back vowels. /v/ (written w, ww) versus /f/ (written f, v).

Stress: lexical, mostly initial. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the stops b, d, g are inherited from the German table and are fully voiced; the descriptions have voiceless lenis stops.
- the monophthong from ei is a fixed [ɛː] (formant file vowel/e_8); the gradient, speaker-dependent range between diphthong and monophthong and its closeness to /eː/ that Keiser measured cannot be shown.
- yes-no questions use tune q4, which ends in a rise; the pattern documented for Pennsylvania Dutch is a rise to the accented syllable followed by a final fall.
- stress is put on the first syllable of words that carry it later (Babbier is [ˈbɑbiːɐ]).
- English loans that keep their English spelling are read by the German-type letter rules; the pronunciation list has about 260 entries.
- the pronunciations have not been checked by native speakers (the voice is marked 'testing').

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 13 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɾ (l=s1: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), ɑ (A=s7: f1=91 f2=86), i (i=s5: dur=56), ʋ (v=s10: af=-14), h (<h=s14: ms=70 whisper=44), ɣ (r=s32: f1=73 f3=116), ɐ (A=s35: f1=85), ɛ (E=s36: dur=84), aː (a=s43: dur=72), ɔː (O=s51: dur=220), ʌ (OE=s52: f1=112 f2=87 f3=114 dur=84), eɐ̯ (e=s59: g1=168 g2=66 g3=91 glide=1), ɹ (r=s65: f2=92 f3=77).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (wer, was, wu, wann ...) ends as a statement does, from a high question word.

Sources: Keiser, Steven Hartman (2012). Pennsylvania German in the American Midwest. Publication of the American Dialect Society 96. Durham: Duke University Press. Keiser, Steven Hartman (2009). When 'speech islands' aren't islands: parallel independent development, drift, and minimal levels of contact for diffusion. Diachronica 26(1). Louden, Mark L. (2016). Pennsylvania Dutch: The Story of an American Language. Baltimore: Johns Hopkins University Press. Buffington, Albert F. and Barba, Preston A. (1954). A Pennsylvania German Grammar. Allentown: Schlechter's. Van Ness, Silke (1994). Pennsylvania German. In König and van der Auwera (eds.), The Germanic Languages. London: Routledge. Fasold, Ralph W. (1980). The conversational function of Pennsylvania Dutch intonation. Paper presented at NWAVE IX, Ann Arbor. And 1 more in the profile.

## Klingon (`piqd`)

constructed language. Described: the language of the published dictionary, in its romanisation.

**What the language has.** A retroflex stop and fricative. Uvular stop and affricate. A lateral affricate. A glottal stop that ends syllables as well as begins them.

Stress: by rule. Rhythm: stress-timed.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 22 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʔ (<q=s4: ms=50 hush=1), a (A=s5: dur=175), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), r̩ (l=s10: tap=3 tapms=18 f2=109 f3=77), t (t=s11: vot=17), p (p=s12: vot=13), r (l=s10: tap=3 tapms=18 f2=109 f3=77), b (b=s22: voi=1 lead=75), d (d=s22: voi=1 lead=75), ʋ (v=s32: af=-14), q (k=s40: f2=68 f3=109 f1=118 burst=3 vot=30), χ (x=s3: f2=88), ɛ (E=s42: dur=126), ai (a=s53: g1=43 g2=166 g3=113 glide=1 dur=72), au (a=s54: g1=46 g2=69 g3=93 glide=1 dur=72), ei (e=s55: g1=79 g2=101 g3=105 glide=1), iu (i=s56: g1=113 g2=46 g3=82 glide=1 dur=117), ui (u=s57: g1=111 g2=250 g3=116 glide=1 dur=117), oi (o=s58: g1=75 g2=250 g3=117 glide=1).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.

Sources: Okrand, Marc (1992). The Klingon Dictionary, second edition.

## Pashto (`ps`)

Indo-European, Indo-Iranian, Iranian, Eastern Iranian. Described: Southwestern (Kandahar) Pashto, the conservative variety on which the spelling is based and which the eSpeak NG base voice follows; the other dialect groups are summarised in the notes.

**What the language has.** Dental versus retroflex stops /t̪ d̪/ : /ʈ ɖ/, and retroflex nasal /ɳ/ and flap /ɽ/ beside /n/ and /r/. Three places for sibilants in the southwest: dental-alveolar /s z/, palato-alveolar /ʃ ʒ/ and retroflex /ʂ ʐ/ (letters ښ and ږ). Dental affricates /ts dz/ (څ ځ) versus palato-alveolar /tʃ dʒ/ (چ ج). /a/ versus /ə/ versus /ɑ/; /ə/ occurs stressed as well as unstressed. Free stress that distinguishes words and grammatical forms. Final vowels and diphthongs carry gender and number: /aj/ (ی), /əj/ (ۍ, ئ), /e/ (ې), /i/ (ي), /a/ and /ə/ (ه). No aspiration contrast in stops, unlike the neighbouring Indo-Aryan languages. /q f ʔ/ belong to the learned pronunciation of loanwords; everyday speech has [k], [p] and zero.

Stress: lexical, free and mobile; contrastive. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- ښ and ږ (phonemes S. and Z.) use the same friction recordings as ʃ and ʒ (ufric/sh, vocw/zh); only the formant transitions differ, so the retroflex and palato-alveolar sibilants sound almost the same; the base table's retroflex fricatives s. and z. with their own recordings (sh_rfx, zh_rfx) are not used.
- the retroflex stops ʈ ɖ use the alveolar burst recording (ustop/t_), and the retroflex flap and nasal use the plain r and n formant files (r3/r_, n/n_); retroflexion rests on transition settings only.
- the voiced retroflex stop ɖ is built from the voiceless recording ustop/t_ with no voiced formant frame, and in the output signal it has no voiced closure or burst, only a short dip between the vowels; the retroflex flap ɽ comes out as a long continuant, several times as long as the plain tap, not as a flap.
- /t d/ are defined as alveolar and /p t k/ use the aspirated English recordings; Pashto has dental, unaspirated stops.
- unwritten short vowels are often missing in the word list: about one entry in six of ps_list (about 122000 entries) has a run of four or more consonants, with و and ی taken as [w] and [j] (تلویزیونی as t@l'wjzjwni:, ننګرهار as n@n'grha:r, قلم as 'q@lm, مڼه as 'mn.a).
- the final letters of the ye series are not kept apart: the replace table of ps_rules turns ي into ی, final ی is read [iː] by rule, and list entries do the same, so the masculine ending /aj/ is not produced (سړی is [saɽaˈiː], لرګی ['lrgi:], خدای [χədaːˈiː]).
- schwa is declared 'unstressed' and given the shortest vowel length (130) in the phoneme table, although stressed /ə/ is common in Pashto; no stress rule is set for ps, so a word without a stress mark in the dictionary gets the general default (penultimate) placement.
- خ and غ are uvular [χ ʁ] (phonemes X and Q) rather than velar [x ɣ].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 26 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), r (l=s9: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s10: f2=91 burst=-4 vot=16), p (p=s11: vot=13), k (k=s12: vot=28), h (<h=s17: ms=70 whisper=44), ɳ (n=s18: f3=80), ɽ (l=s20: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s21: voi=1 lead=75), d (d=s22: f2=91 burst=-4 voi=1 lead=75), ɡ (g=s21: voi=1 lead=75), q (k=s39: f2=68 f3=109 f1=118 burst=3 vot=30), χ (x=s3: f2=88), aː (a=s41: dur=72), iː (i=s42: dur=117), uː (u=s42: dur=117), dz (d=s43 z=s44: f2=91 burst=-4 voi=1 lead=75 hold=85; hold=70), ʈ (t=s45: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s46: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75), ʂ (S=s34: a4=54 f2=87 f3=83 f4=88), ʐ (Z=s33: a4=51 f2=92 f3=87 f4=88).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (څوک, څه, چیرته, چېرته ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Penzl, Herbert (1955). A Grammar of Pashto: A Descriptive Study of the Dialect of Kandahar, Afghanistan. Washington: American Council of Learned Societies. MacKenzie, D. N. (1959). A standard Pashto. Bulletin of the School of Oriental and African Studies 22. MacKenzie, D. N. (1987). Pashto. In Comrie (ed.), The World's Major Languages. London: Croom Helm. Bečka, Jiří (1969). A Study in Pashto Stress. Prague: Academia. Henderson, Michael M. T. (1983). Four varieties of Pashto. Journal of the American Oriental Society 103(3). Skjærvø, Prods O. (1989). Pashto. In Schmitt (ed.), Compendium Linguarum Iranicarum. Wiesbaden: Reichert. And 4 more in the profile.

## Pashto (Northwestern) (`ps-x-northwest`)

Indo-European, Indo-Iranian, Iranian, Eastern Iranian. Described: Northwestern Pashto of the central Ghilzai area (MacKenzie's north-western group; Wardak speech is close to it). Apart from the consonants named below, the description is that of the ps profile.

**What the language has.** The letters ښ and ږ are palatal fricatives /ç ʝ/, distinct from palato-alveolar /ʃ ʒ/ and from velar /x ɣ/; the southwest has retroflex [ʂ ʐ] for them. ځ is the fricative [z] and so merges with ز; څ is [ts] in most descriptions, with [s] also reported. ژ is [ʒ], in places [z]. Dental versus retroflex stops /t̪ d̪/ : /ʈ ɖ/, and retroflex nasal /ɳ/ and flap /ɽ/ beside /n/ and /r/. /a/ versus /ə/ versus /ɑ/; /ə/ occurs stressed as well as unstressed. Free stress that distinguishes words and grammatical forms. No aspiration contrast in stops. /q f ʔ/ belong to the learned pronunciation of loanwords; everyday speech has [k], [p] and zero.

Stress: lexical, free and mobile; contrastive. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the dialect is made by four phoneme replacements on the base ps voice (S. to C, Z. to J^, ts to s, dz to z); vowels, stress, word list and rules are those of ps, so every problem listed in the ps profile applies (missing short vowels in ps_list, final ی read as [iː], alveolar and aspirated stops, retroflexion by transitions only).
- څ is turned into [s]; MacKenzie's table as usually reproduced keeps the affricate [ts] in the northwest and has the fricative only for ځ, so this replacement is doubtful.
- خ and غ stay uvular [χ ʁ].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 24 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), r (l=s9: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s10: f2=91 burst=-4 vot=16), p (p=s11: vot=13), k (k=s12: vot=28), h (<h=s17: ms=70 whisper=44), ɳ (n=s18: f3=80), ɽ (l=s20: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s21: voi=1 lead=75), d (d=s22: f2=91 burst=-4 voi=1 lead=75), ɡ (g=s21: voi=1 lead=75), ʝ (X=s37: voi=1 af=-5), q (k=s39: f2=68 f3=109 f1=118 burst=3 vot=30), χ (x=s3: f2=88), aː (a=s41: dur=72), iː (i=s42: dur=117), uː (u=s42: dur=117), ʈ (t=s45: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s46: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (څوک, څه, چیرته, چېرته ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: MacKenzie, D. N. (1959). A standard Pashto. Bulletin of the School of Oriental and African Studies 22. Henderson, Michael M. T. (1983). Four varieties of Pashto. Journal of the American Oriental Society 103(3). Skjærvø, Prods O. (1989). Pashto. In Schmitt (ed.), Compendium Linguarum Iranicarum. Wiesbaden: Reichert. Tegey, Habibullah and Robson, Barbara (1996). A Reference Grammar of Pashto. Washington: Center for Applied Linguistics. Elfenbein, Josef (1997). Pashto phonology. In Kaye (ed.), Phonologies of Asia and Africa, volume 2. Winona Lake: Eisenbrauns. Robson, Barbara and Tegey, Habibullah (2009). Pashto. In Windfuhr (ed.), The Iranian Languages. London: Routledge. And 1 more in the profile.

## Pashto (Southeastern) (`ps-x-southeast`)

Indo-European, Indo-Iranian, Iranian, Eastern Iranian. Described: Southeastern Pashto of the Quetta area (MacKenzie's south-eastern group, Kakar). Apart from the consonants named below, the description is that of the ps profile. The Karlani (central) varieties such as Waziri, which the voice file also names, have vowel shifts of their own and are not described here.

**What the language has.** The letters ښ and ږ are palato-alveolar [ʃ ʒ] and so merge with ش and ژ; the retroflex fricatives of the southwest are absent. The dental affricates /ts dz/ (څ ځ) are kept, distinct from /tʃ dʒ/. Dental versus retroflex stops /t̪ d̪/ : /ʈ ɖ/, and retroflex nasal /ɳ/ and flap /ɽ/ beside /n/ and /r/. /a/ versus /ə/ versus /ɑ/; /ə/ occurs stressed as well as unstressed. Free stress that distinguishes words and grammatical forms. No aspiration contrast in stops. /q f ʔ/ belong to the learned pronunciation of loanwords; everyday speech has [k], [p] and zero.

Stress: lexical, free and mobile; contrastive. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the dialect is made by two phoneme replacements on the base ps voice (S. to S, Z. to Z); vowels, stress, word list and rules are those of ps, so every problem listed in the ps profile applies (missing short vowels in ps_list, final ی read as [iː], alveolar and aspirated stops, retroflexion by transitions only).
- the voice file names the neighbouring Karlani areas, but the Karlani vowel shifts are not modelled; the voice is of the Quetta type only.
- خ and غ stay uvular [χ ʁ].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 24 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), r (l=s9: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s10: f2=91 burst=-4 vot=16), p (p=s11: vot=13), k (k=s12: vot=28), h (<h=s17: ms=70 whisper=44), ɳ (n=s18: f3=80), ɽ (l=s20: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s21: voi=1 lead=75), d (d=s22: f2=91 burst=-4 voi=1 lead=75), ɡ (g=s21: voi=1 lead=75), q (k=s39: f2=68 f3=109 f1=118 burst=3 vot=30), χ (x=s3: f2=88), aː (a=s41: dur=72), iː (i=s42: dur=117), uː (u=s42: dur=117), dz (d=s43 z=s44: f2=91 burst=-4 voi=1 lead=75 hold=85; hold=70), ʈ (t=s45: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s46: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (څوک, څه, چیرته, چېرته ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: MacKenzie, D. N. (1959). A standard Pashto. Bulletin of the School of Oriental and African Studies 22. Henderson, Michael M. T. (1983). Four varieties of Pashto. Journal of the American Oriental Society 103(3). Skjærvø, Prods O. (1989). Pashto. In Schmitt (ed.), Compendium Linguarum Iranicarum. Wiesbaden: Reichert. Tegey, Habibullah and Robson, Barbara (1996). A Reference Grammar of Pashto. Washington: Center for Applied Linguistics. Elfenbein, Josef (1997). Pashto phonology. In Kaye (ed.), Phonologies of Asia and Africa, volume 2. Winona Lake: Eisenbrauns. Robson, Barbara and Tegey, Habibullah (2009). Pashto. In Windfuhr (ed.), The Iranian Languages. London: Routledge. And 1 more in the profile.

## Pashto (Yusufzai) (`ps-x-yusufzai`)

Indo-European, Indo-Iranian, Iranian, Eastern Iranian. Described: Northeastern Pashto of the Yusufzai (Peshawar valley, Mardan, Swat), the basis of the usual pronunciation in Pakistan. Apart from the points named below, the description is that of the ps profile.

**What the language has.** The letter ښ is the velar fricative [x] and merges with خ; the letter ږ is the velar stop [ɡ] and merges with ګ; hence the names Pakhto and Pukhtun against southwestern Pashto and Pashtun. The dental affricates are lost: څ is [s] and ځ is [z], merging with س and ز. ژ is the affricate [dʒ] and merges with ج, so the dialect has no /ʒ/. The consonant inventory is therefore smaller than in the southwest: no /ʂ ʐ ʒ ts dz/. Dental versus retroflex stops /t̪ d̪/ : /ʈ ɖ/, and retroflex nasal /ɳ/ and flap /ɽ/ beside /n/ and /r/. /a/ versus /ə/ versus /ɑ/; /ə/ occurs stressed as well as unstressed. Free stress that distinguishes words and grammatical forms. No aspiration contrast in stops.

Stress: lexical, free and mobile; contrastive. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the dialect is made by five phoneme replacements on the base ps voice (S. to x, Z. to g, ts to s, dz to z, Z to dZ); vowels, stress, word list and rules are those of ps, so every problem listed in the ps profile applies (missing short vowels in ps_list, final ی read as [iː], alveolar and aspirated stops, retroflexion by transitions only).
- ښ becomes the velar x but خ keeps the uvular phoneme X, so the two letters, one phoneme /x/ in this dialect, sound different (ښه gives [xa], خدای [χədaːˈiː]).
- no dialect vowels: the reported [ɛ] for final /aj/ is not produced.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 23 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), r (l=s9: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s10: f2=91 burst=-4 vot=16), p (p=s11: vot=13), k (k=s12: vot=28), h (<h=s17: ms=70 whisper=44), ɳ (n=s18: f3=80), ɽ (l=s20: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s21: voi=1 lead=75), d (d=s22: f2=91 burst=-4 voi=1 lead=75), ɡ (g=s21: voi=1 lead=75), q (k=s39: f2=68 f3=109 f1=118 burst=3 vot=30), χ (x=s3: f2=88), aː (a=s41: dur=72), iː (i=s42: dur=117), uː (u=s42: dur=117), ʈ (t=s45: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s46: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
A question asked with a question word (څوک, څه, چیرته, چېرته ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: MacKenzie, D. N. (1959). A standard Pashto. Bulletin of the School of Oriental and African Studies 22. Henderson, Michael M. T. (1983). Four varieties of Pashto. Journal of the American Oriental Society 103(3). Skjærvø, Prods O. (1989). Pashto. In Schmitt (ed.), Compendium Linguarum Iranicarum. Wiesbaden: Reichert. Tegey, Habibullah and Robson, Barbara (1996). A Reference Grammar of Pashto. Washington: Center for Applied Linguistics. Elfenbein, Josef (1997). Pashto phonology. In Kaye (ed.), Phonologies of Asia and Africa, volume 2. Winona Lake: Eisenbrauns. Robson, Barbara and Tegey, Habibullah (2009). Pashto. In Windfuhr (ed.), The Iranian Languages. London: Routledge. And 1 more in the profile.

## Portuguese (Portugal) (`pt`)

Indo-European, Romance, Western Romance, Galician-Portuguese. Described: Standard European Portuguese as spoken in Lisbon (the variety of the IPA Handbook illustration).

**What the language has.** Four vowel heights under stress: /i e ɛ a/ and /u o ɔ a/ (avô [ɐˈvo] versus avó [ɐˈvɔ], pê versus pé). /a/ versus /ɐ/ under stress in a few contexts (falámos [fɐˈlamuʃ] past versus falamos [fɐˈlɐmuʃ] present). Oral versus nasal vowels (lá versus lã, mito versus minto) and oral versus nasal diphthongs (pau versus pão, mais versus mães). Tap /ɾ/ versus strong /ʁ/ between vowels (caro versus carro). Four sibilants /s z ʃ ʒ/ in onsets, neutralised to one coda sibilant. /l/ versus /ʎ/ and /n/ versus /ɲ/. Lexical stress (dúvida noun versus duvida verb), always accompanied by a change of vowel quality.

Stress: lexical, restricted to the last three syllables. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- pretonic e is often left unreduced in the first syllable of words of three or more syllables: that syllable is given secondary stress, which blocks the change to [ɨ] unless a spelling rule gives [ɨ] outright (a and o are reduced there). So pequeno is [pˌekˈenʊ], menino [mˌenˈinʊ], felicidade [fˌelisidˈadɨ], perceber [pˌeɾsɨbˈeɾ], where the literature has [pɨˈkenu], [mɨˈninu], [fɨlisiˈðaðɨ], [pɨɾsɨˈbeɾ].
- [ɨ] is never deleted (only word-initial 'es' loses its vowel), so the consonant clusters of connected European speech do not arise.
- final '-em', '-ens' is an oral diphthong plus a velar nasal [eɪŋ] (bem, tem, homem, também, ontem) instead of the nasal diphthong [ɐ̃j̃]; 'ãe' has an oral glide [ɐ̃j].
- every nasal vowel is followed by a nasal consonant segment, also before fricatives and at the end of a word (longe [lˈõnʒɨ], ênfase [ˈẽnfɐzɨ], fim [fˈĩŋ], bom [bˈõm]), where the language has a plain nasal vowel.
- the Lisbon centralisation before palatals is missing: leite, rei have [eɪ] and tenho, espelho, vermelho have [e], against [ɐj] and [ɐ].
- stressed 'a' before a nasal onset is nasalised as in Brazilian Portuguese (cama [kˈɐ̃mɐ], falamos [fˌɐlˈɐ̃mʊʃ]); European Portuguese has oral [ɐ].
- /b d ɡ/ are always stops; the fricative allophones [β ð ɣ] are missing.
- /l/ imports the English phoneme, clear before a vowel and dark only in the coda; European /l/ is velarised in all positions.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 17 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s5: f1=74 f2=110), i (i=s6: f2=112), o (o=s7: f1=75), u (u=s8: f3=90 dur=114), b (b=s15: voi=1 lead=75), d (d=s15: voi=1 lead=75), ɡ (g=s15: voi=1 lead=75), ʁ (G=s28: f1=55 f2=88 f3=89), ɛ (e=s30: f1=94), ʊ (o=s31: f1=87 f2=111 f3=94), ɨ (i=s32: f1=114 f2=83 f3=87), eɪ (e=s38: g1=82 g2=108 g3=99 glide=1 dur=149), ɐ̃ (a=s45: nas=100), õ (o=s48: f1=75 nas=100), ɔɪ (o=s51: g1=86 g2=199 g3=103 glide=1 dur=155), ɐ̃ʊ̃ (a=s53: g1=69 g2=75 g3=97 glide=1 dur=135 nas=100), õɪ̃ (o=s54: g1=82 g2=198 g3=103 glide=1 dur=155 nas=100).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (quê, quem, onde, quando ...) ends as a statement does, from a high question word.
Timing: stressed 112 per cent, weak 85 per cent of the module's own.

Sources: Cruz-Ferreira, Madalena (1995). European Portuguese. Journal of the International Phonetic Association 25(2), 90-94. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Mateus, Maria Helena and d'Andrade, Ernesto (2000). The Phonology of Portuguese. Oxford University Press. Escudero, Paola; Boersma, Paul; Rauber, Andréia Schurt; Bion, Ricardo A. H. (2009). A cross-dialect acoustic description of vowels: Brazilian and European Portuguese. Journal of the Acoustical Society of America 126(3), 1379-1393. Frota, Sónia and Vigário, Marina (2001). On the correlates of rhythmic distinctions: the European/Brazilian Portuguese case. Probus 13, 247-275. Frota, Sónia (2000). Prosody and Focus in European Portuguese: Phonological Phrasing and Intonation. New York: Garland. Frota, Sónia (2014). The intonational phonology of European Portuguese. In Jun (ed.), Prosodic Typology II. Oxford University Press. And 1 more in the profile.

## Portuguese (Brazil) (`pt-br`)

Indo-European, Romance, Western Romance, Galician-Portuguese. Described: Educated urban Brazilian Portuguese of the south-east (São Paulo, the variety of the JIPA illustration), with notes on Rio de Janeiro.

**What the language has.** Seven oral vowels under stress /i e ɛ a ɔ o u/, five before the stress /i e a o u/, three in final unstressed position [ɪ ɐ ʊ]. Oral versus nasal vowels (lá versus lã) and oral versus nasal diphthongs (pau versus pão). Tap /ɾ/ versus strong r /x/ between vowels (caro versus carro). Four sibilants /s z ʃ ʒ/ in onsets, one sibilant in the coda. /l/ versus /ʎ/ and /n/ versus /ɲ/. [tʃ dʒ] are mostly predictable variants of /t d/ before [i], but contrast marginally in loanwords and names (tchau, Djalma). Lexical stress (sábia, sabia, sabiá).

Stress: lexical, restricted to the last three syllables. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- final '-em', '-ens' is an oral diphthong plus a velar nasal [eɪŋ] (bem, tem, homem, também, viagem) instead of the nasal diphthong [ẽj̃]; 'ãe' has an oral glide [ɐ̃j].
- every nasal vowel is followed by a nasal consonant segment, also before fricatives and at the end of a word (longe [lˈõnʒɪ], ênfase [ˈẽnfɐzɪ], fim [fˈĩŋ], bom [bˈõm]), where the language has a plain nasal vowel or a nasal glide.
- no epenthetic [i] in consonant clusters: ritmo [xˈitmʊ], advogado [ˌadvoɡˈadʊ], pneu [pnˈeʊ], psicologia [psˌikoloʒˈiɐ] (the rule option for epenthesis is reserved for the MBROLA voices).
- coda r is always a tap and coda s always [s] or [z] (São Paulo pattern); there is no setting for the fricative coda r or the [ʃ] coda of Rio de Janeiro, and the strong r labelled [x] is synthesised with the glottal [h] sound.
- /ɲ/ is a full palatal nasal stop, not the nasal glide [j̃] usual in Brazil.
- the first syllable of longer words always gets secondary stress (pequeno [pˌekˈenʊ], cidade [sˌidˈadʒɪ]) whatever the distance to the main stress.
- intonation uses one of the generic tune sets (voice option 'intonation 2'): the rise-fall on the last stressed syllable of yes-no questions and the rising accent on each content word are not modelled.

**What OpenEVV says.** Spoken by the module made from Latin American Spanish (`esux`). 18 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s5: f1=74 f2=112), i (i=s6: f2=114), o (o=s7: f1=77 f2=89), u (u=s8: f3=90), b (b=s15: voi=1 lead=75), d (d=s15: voi=1 lead=75), ɡ (g=s15: voi=1 lead=75), ɛ (e=s32: f1=108), ɔ (o=s33: f1=110), ʊ (o=s34: f1=87 f2=111 f3=94), ɪ (i=s35: f1=142 f3=93), eɪ (e=s41: g1=82 g2=109 g3=99 glide=1 dur=150), ɐ̃ (a=s48: nas=100), õ (o=s51: f1=77 f2=89 nas=100), ɔɪ (o=s54: f1=110 g1=87 g2=199 g3=103 glide=1 dur=155), ɐ̃ʊ̃ (a=s56: g1=69 g2=75 g3=97 glide=1 dur=142 nas=100), õɪ̃ (o=s57: g1=82 g2=197 g3=103 glide=1 dur=155 nas=100).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (quê, quem, onde, quando ...) ends as a statement does, from a high question word.

Sources: Barbosa, Plínio A. and Albano, Eleonora C. (2004). Brazilian Portuguese. Journal of the International Phonetic Association 34(2), 227-232. Mateus, Maria Helena and d'Andrade, Ernesto (2000). The Phonology of Portuguese. Oxford University Press. Cristófaro Silva, Thaïs (1999). Fonética e fonologia do português: roteiro de estudos e guia de exercícios. São Paulo: Contexto. Bisol, Leda (ed.) (1996). Introdução a estudos de fonologia do português brasileiro. Porto Alegre: EDIPUCRS. Escudero, Paola; Boersma, Paul; Rauber, Andréia Schurt; Bion, Ricardo A. H. (2009). A cross-dialect acoustic description of vowels: Brazilian and European Portuguese. Journal of the Acoustical Society of America 126(3), 1379-1393. Frota, Sónia and Vigário, Marina (2001). On the correlates of rhythmic distinctions: the European/Brazilian Portuguese case. Probus 13, 247-275. And 2 more in the profile.

## Pyash (`py`)

constructed language. Described: as its maker describes it.

**What the language has.** A small inventory meant to be sayable by speakers of most languages.

Stress: not described. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (l=s5: f3=66), u (u=s4: dur=114), h (<h=s8: ms=70 whisper=44), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), c (t=s17: f2=148 f3=109 a3=56 a4=56 vot=32), ɡ (g=s11: voi=1 lead=75), ts (t=s34 s=s35: hold=85; hold=70).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.

Sources: The Pyash language documentation (its maker's own).

## Lang Belta (`qdb`)

constructed language. Described: the creole made for the television series The Expanse.

**What the language has.** A low back rounded vowel beside a.

Stress: by rule. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 20 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), ɽ (l=s10: tap=1 tapms=24 hold=60 f2=111 f3=66), æ (E=s11: f1=124 f2=92 f3=92 dur=126), e (e=s7: dur=80), i (i=s8: dur=85), u (u=s9: dur=86), t (t=s13: vot=17), p (p=s14: vot=13), k (k=s15: vot=28), ɲ (n=s23: f2=136 f3=109), b (b=s24: voi=1 lead=75), d (d=s24: voi=1 lead=75), ɡ (g=s24: voi=1 lead=75), θ (f=s36: f2=146 f3=110 a6=28 ab=48), χ (x=s3: f2=88), ɒ (O=s52: f1=116 dur=150), iː (i=s57: dur=117), uː (u=s57: dur=117).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Farmer, Nick. Published notes on Lang Belta.

## Quechua (`qu`)

Quechuan, Quechua II (Southern Quechua, IIC). Described: Cusco-Collao Quechua as spoken in and around Cusco, Peru. eSpeak NG accepts the letters for aspirated and ejective stops (ph th chh kh qh, p' t' ch' k' q'), which exist only in the Cusco-Collao and Bolivian varieties, not in Ayacucho-Chanka; its number words and pronouns (pichqa, ñuqa, qam, ñuqanchik) use the unified Southern Quechua spelling that Ayacucho shares. Acoustic figures come from the closely related Cochabamba (Bolivian) variety.

**What the language has.** Three-way laryngeal contrast in stops and affricates at five places: plain, aspirated, ejective (tanta 'gathering', thanta 'worn out', t'anta 'bread'). Velar versus uvular stops: k kʰ kʼ versus q qʰ qʼ. Three native vowel phonemes /i a u/; [e] and [o] are their allophones next to uvulars and are phonemes only in Spanish loans, which is why they are listed last among the vowels. Palatal ɲ and ʎ versus alveolar n and l. No voiced stops in native words.

Stress: fixed, penultimate. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no vowel lowering next to uvulars: qilla, sunqu, urqu keep [i] and [u]; [e o] appear only if the text is written with e and o.
- ch' fails at the start of a word: ch'aki is spelled out letter by letter, while sach'a inside a word works.
- every ejective is followed by a separate glottal stop; p' and ch' use the recordings of aspirated stops and q' uses a fricative noise, so only k' and t' have an ejective burst.
- aspirated stops are a plain stop followed by a separate [h], with no single aspirated phonemes.
- stops at the end of a syllable stay stops; the Cusco fricatives [ɸ s ʃ x χ] are missing.
- final stress written with an acute accent is ignored (arí is stressed on the first syllable).
- the number words are transcribed with velar k for uvular q (pusak, iskun, sukta, waranka), and numbers above nine are read digit by digit.

**What OpenEVV says.** Spoken by the module made from Latin American Spanish (`esux`). 6 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ʔ (<q=s3: ms=50 hush=1), h (<h=s7: ms=70 whisper=44), b (b=s10: voi=1 lead=75), d (d=s10: voi=1 lead=75), ɡ (g=s10: voi=1 lead=75), q (k=s26: f2=68 f3=109 f1=118 burst=3 vot=30).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (ima, pi, may, maypi ...) ends as a statement does, from a high question word.

Sources: Cusihuamán G., Antonio (1976). Gramática quechua: Cuzco-Collao. Lima: Ministerio de Educación and Instituto de Estudios Peruanos. Cerrón-Palomino, Rodolfo (1987). Lingüística quechua. Cusco: Centro de Estudios Rurales Andinos Bartolomé de las Casas. Mannheim, Bruce (1991). The Language of the Inka since the European Invasion. Austin: University of Texas Press. Adelaar, Willem F. H. with Muysken, Pieter C. (2004). The Languages of the Andes. Cambridge: Cambridge University Press. Parker, Steve & Weber, David (1996). Glottalized and aspirated stops in Cuzco Quechua. International Journal of American Linguistics 62. Gallagher, Gillian (2016). Vowel height allophony and dorsal place contrasts in Cochabamba Quechua. Phonetica 73(2), 101-119. And 4 more in the profile.

## K'iche' (`quc`)

Mayan, Eastern Mayan, K'ichean. Described: Western and central K'iche' of the Nahualá and Totonicapán type, which keeps five short and five long vowels; dialects such as Cantel and Chichicastenango have turned the length contrast into a tense and lax contrast. eSpeak NG reads the ALMG-based spelling.

**What the language has.** Plain versus glottalised stops and affricates at six places: p and ɓ, t and tʼ, ts and tsʼ, tʃ and tʃʼ, k and kʼ, q and qʼ. The glottalised labial is a voiced implosive, the others are ejectives. Velar versus uvular stops. Short versus long vowels in the conservative dialects (chaj 'pine' versus chaaj 'ash', written chäj and chaj in the spelling that marks lax vowels); tense versus lax vowels, or six vowels without length, in the innovating dialects. Glottal stop as a consonant, also after vowels (V'C). No voiced stops apart from the implosive.

Stress: fixed, final. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the phoneme table quc is declared without a phoneme file of its own, so the language uses the generic base vowels and consonants.
- glottalised consonants are rendered as a glottal stop followed by a plain stop ([ʔk], [ʔq], [ʔt], [ʔb], [ʔtʃ]); there are no ejective or implosive phonemes.
- tz' and ch' fail at the start of a word: tz'i' and ch'ich' are partly spelled out as English letter names; inside a word tz' comes out as a glottal stop plus t plus voiced [z].
- an apostrophe at the end of a word is dropped and replaced by a pause, so final b', k', q' and the final glottal stop (che') lose their glottalisation.
- o is pronounced as the two vowels o and u (job' has two syllables) and u is always long; the rules for these two letters do not match any description of the language.
- vowel length is not handled: double vowels become two syllables, and the diaeresis letters ä ë ï ö ü for lax vowels are replaced by the plain vowels.
- w is [v] and j is [h]; the literature has [w] with a devoiced or fricated final variant, and a uvular or velar fricative.
- no aspiration of final stops, no devoicing of final sonorants, no reduction of unstressed vowels in the phoneme table (the voice file only lowers their amplitude and length).

**What OpenEVV says.** Spoken by the module made from Latin American Spanish (`esux`). 12 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=51), e (e=s5: dur=54), i (i=s6: dur=57), o (o=s7: dur=49), u (u=s8: dur=52), h (<h=s12: ms=70 whisper=44), b (b=s15: voi=1 lead=75), q (k=s31: f2=68 f3=109 f1=118 burst=3 vot=30), d (d=s15: voi=1 lead=75), ɛ (e=s39: f1=116 dur=54), iː (i=s45: dur=157), eɪ (e=s52: g1=83 g2=109 g3=99 glide=1 dur=150).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

Sources: Larsen, Thomas W. (1988). Manifestations of Ergativity in Quiché Grammar. PhD dissertation, University of California, Berkeley. Mondloch, James L. (1978). Basic Quiché Grammar. Albany: Institute for Mesoamerican Studies, State University of New York. López Ixcoy, Candelaria Dominga (1997). Ri Ukemiik ri K'ichee' Chii': Gramática K'ichee'. Guatemala: Cholsamaj. Bennett, Ryan (2016). Mayan phonology. Language and Linguistics Compass 10(10), 469-514. England, Nora C. & Baird, Brandon O. (2017). Phonology and phonetics. In J. Aissen, N. C. England & R. Zavala Maldonado (eds.), The Mayan Languages. London: Routledge. Pinkerton, Sandra (1986). Quichean (Mayan) glottalized and nonglottalized stops: a phonetic study with implications for phonological universals. In J. J. Ohala & J. J. Jaeger (eds.), Experimental Phonology. Orlando: Academic Press. And 3 more in the profile.

## Quenya (`qya`)

constructed language. Described: the late Third Age form of the published writings.

**What the language has.** Long vowels beside short ones. Long consonants.

Stress: by rule. Rhythm: mora-timed.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 17 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s16: ms=70 whisper=44), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɡ (g=s20: voi=1 lead=75), ɛ (E=s41: dur=84), ɔ (O=s42: dur=85), aː (a=s44: dur=72), uː (u=s45: dur=117), aʊ (a=s46: g1=58 g2=82 g3=93 glide=1 dur=72), aɪ (a=s47: g1=56 g2=146 g3=101 glide=1 dur=72), ʍ (w=s51: whisper=46), uɪ (w=s52 I: hold=55).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Tolkien, J. R. R. (1955). The Lord of the Rings, Appendix E.

## Romanian (`ro`)

Indo-European, Romance, Eastern Romance (Daco-Romanian). Described: Standard Romanian (literary norm based on the speech of Bucharest and Muntenia).

**What the language has.** Seven vowels with three central ones: close /ɨ/ (written â, î), mid /ə/ (written ă) and open /a/ (râu [rɨw] 'river' versus rău [rəw] 'bad'; văr [vər] 'cousin' versus vâr [vɨr] 'I thrust' versus var [var] 'lime'). Plain versus palatalised consonant at the end of a word, which carries plural and second person marking (lup [lup] 'wolf' versus lupi [lupʲ] 'wolves'; pom versus pomi; rup 'I break' versus rupi 'you break'). The diphthongs /e̯a/ and /o̯a/ contrast with /ja/ and /wa/ and alternate with /e/ and /o/ (seară, seri; floare, flori). Affricates /ts tʃ dʒ/ versus fricatives /s ʃ ʒ/. Lexical stress (copii [koˈpij] 'children' versus copii [ˈkopij] 'copies'; cântă [ˈkɨntə] 'sings' versus cântă [kɨnˈtə] 'sang'). Three forms distinguished by final i alone: copil, copii [koˈpij], copiii [koˈpiji].

Stress: lexical, free and mobile in inflection. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- stress is set by a default rule (last syllable, or penultimate when the word ends in a vowel) with suffix rules and a word list, so lexical stress is often wrong: copii is [kˈopiɪ] for [koˈpij], iepure [jepˈuɾe] for [ˈjepure], înger [ɨŋdʒˈer] for [ˈɨndʒer]; homographs that differ in stress cannot be told apart.
- no voicing assimilation in obstruent clusters (absolvent [ˌabsolvˈent], subțire [subtsˈiɾe], obține [obtsˈine]).
- the velar nasal is used before the affricate in înger but not before velars (unchi [ˈunkʲ]).
- some vowel sequences are split or mis-grouped: leu is [lˈeu] with two vowels, leoaică is [leoˈaikˌə] for [leˈo̯ajkə].
- the diphthongs of â, î plus i or u have no IPA label and print as 'yɪ', 'yʊ' (câine [kˈyɪne], râu [rˈyʊ]), although the sound used is [ɨj], [ɨw].
- no tune set is selected, so the generic default tunes are used; the low accent plus rise-fall of yes-no questions is not modelled.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 33 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (E=s1: f1=93 f2=78), i (i=s4: dur=114), u (u=s4: dur=114), h (<h=s8: ms=70 whisper=44), b (b=s11: voi=1 lead=75), d (d=s11: voi=1 lead=75), c (t=s17: f2=148 f3=109 a3=56 a4=56 vot=32), ɡ (g=s11: voi=1 lead=75), zʲ (z=s24: f2=129 f3=108), ʒʲ (Z=s25: f2=120 f3=108), ʃʲ (S=s25: f2=120 f3=108), ɨ (i=s32: f1=122 f2=77 f3=88 dur=114), aʊ (a=s34: g1=57 g2=72 g3=97 glide=1 dur=131), aɪ (a=s37: g1=55 g2=127 g3=106 glide=1 dur=131), eɪ (e=s38: g1=91 g2=100 g3=99 glide=1 dur=148), oɪ (o=s40: g1=88 g2=203 g3=106 glide=1 dur=150), uɪ (w=s36 e=s41: hold=55; f1=91), lʲ (l=s42: f2=157 f3=113), mʲ (m=s43: f2=216 f3=123), nʲ (n=s44: f2=127 f3=109), əɪ (E=s45: f1=93 f2=78 g1=78 g2=101 g3=102 glide=1 dur=148), əʊ (E=s46: f1=93 f2=78 g1=81 g2=58 g3=94 glide=1 dur=148), iɪ (y=s36 e=s41: hold=55; f1=91), ea (y=s36 a: hold=55), ɔa (w=s36 a: hold=55), pʲ (p=s51: f2=220 f3=122 vot=21), tʲ (t=s52: f2=142 f3=106 vot=24), tsʲ (t=s53 s=s54: f2=142 f3=106 hold=85; f2=129 f3=108 hold=70), bʲ (b=s56: f2=220 f3=122 voi=1 lead=75), dʲ (d=s57: f2=142 f3=106 voi=1 lead=75), ɾʲ (r=s58: f2=153 f3=123), vʲ (v=s55: f2=200 f3=108).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (ce, cine, unde, când ...) ends as a statement does, from a high question word.

Sources: Chitoran, Ioana (2002). The Phonology of Romanian: A Constraint-Based Approach. Berlin: Mouton de Gruyter. Renwick, Margaret E. L. (2014). The Phonetics and Phonology of Contrast: The Case of the Romanian Vowel System. Berlin: De Gruyter Mouton. Vasiliu, Emanuel (1965). Fonologia limbii române. București: Editura Științifică. Pană Dindelegan, Gabriela (ed.) (2013). The Grammar of Romanian. Oxford University Press. Spinu, Laura; Vogel, Irene; Bunnell, H. Timothy (2012). Palatalization in Romanian: acoustic properties and perception. Journal of Phonetics 40(1), 54-66. Dascălu-Jinga, Laurenția (1998). Intonation in Romanian. In Hirst and Di Cristo (eds.), Intonation Systems: A Survey of Twenty Languages. Cambridge University Press. And 3 more in the profile.

## Russian (`ru`)

Indo-European, Balto-Slavic, Slavic, East Slavic. Described: Contemporary Standard Russian (Moscow-based norm).

**What the language has.** Palatalised ('soft') versus non-palatalised ('hard', slightly velarised) consonants at almost every place and manner, also word-finally and before consonants (брат [brat] vs брать [bratʲ], угол [ˈuɡəɫ] vs уголь [ˈuɡəlʲ]). Unpaired hard /ʂ ʐ t͡s/ and unpaired soft /t͡ɕ ɕː j/; soft velars /kʲ ɡʲ xʲ/ are marginal. Voiced versus voiceless obstruents (prevoiced versus voiceless unaspirated). Five stressed vowels /i e a o u/, with [ɨ] as a sixth phoneme or as the allophone of /i/ after hard consonants. Position of stress is lexically contrastive (мука: [ˈmukə] 'torment' vs [mʊˈka] 'flour'). Long /ɕː/ (and obsolescent /ʑː/) and geminates at morpheme boundaries.

Stress: free (lexical), mobile. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Soft labials, velars, /lʲ/ and /nʲ/ are coded as hard consonant plus a palatal glide phoneme [;] that is deleted when no vowel follows, so palatalisation is lost word-finally and before consonants: день, соль, уголь, степь, любовь, пальто, только come out hard (был and быль give identical audio). Only /tʲ dʲ sʲ zʲ mʲ/ and the sibilant series have their own soft phonemes; final рь is [r] plus a very short [ɪ].
- Ikanye is applied only to the letter е: unstressed а, я after soft consonants and after ч, щ stay [a] or [ʌ] (пятно [pʲatˈno], часы [t͡ɕaˈsɨ], язык [jaˈzɨk], часовой) where the language has [ɪ].
- Akanye is incomplete: unstressed о is [ʌ] (phoneme V) in every position including the first pretonic syllable, while pretonic а is [a], so pretonic /o/ and /a/ do not merge (вода [vʌˈda] vs сады [saˈdɨ]) and the two degrees [ɐ] and [ə] are not reproduced for о.
- Stress comes from a large word list (ru_listx) and otherwise from a guess based on the number of syllables; unlisted or ambiguous forms get wrong stress and so wrong reduction (города is read горо́да).
- No voicing assimilation between a preposition and its host: к дому, с братом, от брата keep voiceless [k s t], and из дома is devoiced to [ɪs].
- /ɕː/ (щ, сч) is a single short [ɕ].
- Hard /ɫ/ uses a retroflex lateral (shown as ɭ in IPA output) and ы is shown as 'y'; stressed [æ] between soft consonants is not distinguished from [a].
- Only the default eSpeak tunes are used: a question mark gives a fall-rise on the last stressed syllable for every question type, so the peak on the focused word of yes-no questions (IK-3) and the falling wh-question (IK-2) are missing.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 51 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), r (l=s10: tap=3 tapms=18 f2=109 f3=77), a (A=s5: f1=88 f2=84 dur=175), e (e=s6: f1=116 f2=82 dur=80), i (i=s7: f1=88 dur=85), o (o=s8: f1=131 dur=80), u (u=s9: f1=117 f2=83 dur=86), t (t=s11: f2=91 burst=-4 vot=20), p (p=s12: vot=18), k (k=s13: vot=38), ɭ (l=s15: f2=111 f3=71), b (b=s21: voi=1 lead=70), d (d=s22: f2=91 burst=-4 voi=1 lead=75), tʃʲ (t=s25 S=s24: f2=120 f3=108 burst=-4 hold=85; f2=120 f3=108 hold=70), ɡ (g=s28: voi=1 lead=78), ʑ (Z=s35: a3=34 a4=55 a5=22 f2=126 f3=121), sʲ (s=s36: f2=129 f3=108), ɕ (S=s37: a2=31 a3=34 a4=34 a5=22 f2=119 f3=116), tʲ (t=s42: f2=129 f3=108 burst=-4 vot=20), dʲ (d=s43: f2=129 f3=108 burst=-4 voi=1 lead=75), mʲ (m=s44: f2=220), y (y=s46: dur=85), ɪ (I=s45: dur=137), ja (j A=s5: f1=88 f2=84 dur=175), ɛ (E=s47: dur=126), ʌ (OE=s48: f1=112 f2=87 f3=114 dur=126), ɔ (O=s49: dur=150), ɵ (Y=s50: f2=89 f3=107 dur=137), ju (j u=s9: f1=117 f2=83 dur=86), ɑ (A=s51: f1=91 f2=86 dur=175), ɑː (a=s64: f1=89 f2=86 dur=72), iː (i=s67: f1=88 dur=117), aɪ (a=s73: g1=54 g2=143 g3=101 glide=1 dur=72), eɪ (e=s74: g1=107 g2=87 g3=94 glide=1).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (кто, что, где, когда ...) ends as a statement does, from a high question word.

Sources: Yanushevskaya, Irena & Bunčić, Daniel (2015). Russian. Journal of the International Phonetic Association 45(2), 221-228. Jones, Daniel & Ward, Dennis (1969). The Phonetics of Russian. Cambridge University Press. Avanesov, R. I. (1984). Russkoe literaturnoe proiznošenie. Moscow: Prosveščenie. Timberlake, Alan (2004). A Reference Grammar of Russian. Cambridge University Press. Halle, Morris (1959). The Sound Pattern of Russian. The Hague: Mouton. Fant, Gunnar (1960). Acoustic Theory of Speech Production. The Hague: Mouton. And 6 more in the profile.

## Russian (Classic) (`ru-cl`)

Indo-European, Balto-Slavic, Slavic, East Slavic. Described: Contemporary Standard Russian (Moscow-based norm). 'Classic' is an alternative eSpeak NG rule set for the same standard language, not a separate variety, so the linguistic description is that of Russian.

**What the language has.** Palatalised ('soft') versus non-palatalised ('hard', slightly velarised) consonants at almost every place and manner, also word-finally and before consonants (брат [brat] vs брать [bratʲ], угол [ˈuɡəɫ] vs уголь [ˈuɡəlʲ]). Unpaired hard /ʂ ʐ t͡s/ and unpaired soft /t͡ɕ ɕː j/; soft velars /kʲ ɡʲ xʲ/ are marginal. Voiced versus voiceless obstruents (prevoiced versus voiceless unaspirated). Five stressed vowels /i e a o u/, with [ɨ] as a sixth phoneme or as the allophone of /i/ after hard consonants. Position of stress is lexically contrastive. Long /ɕː/ (and obsolescent /ʑː/) and geminates at morpheme boundaries.

Stress: free (lexical), mobile. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- How it differs from ru: the voice file is the same as zle/ru (same 'replace 03 a a#' and dict_min) plus 'dictrules 3'. It has no phonemes line and no phoneme table of its own, so it uses the ru phoneme table and the ru dictionary; all differences come from the conditional ?3 entries in ru_rules and ru_list.
- Soft л is the single phoneme l^ (rule '?3 л (Y l^') instead of l plus palatal glide, so it survives word-finally and before consonants (соль, уголь, пальто, только), which ru loses. But l^ uses the same formant data as hard l (l^/l_rfx) and is only longer (length 80 vs 40), and there is no glide into the vowel, so the hard-soft contrast of the lateral rests on duration and on the following vowel allophone.
- Soft н is replaced by plain [n] everywhere (rule '?3 н (Y n'): нет [net], няня [ˈnanʌ], несу [nisˈu], день [dʲen], so the /n/ vs /nʲ/ contrast is lost completely, not only word-finally as in ru.
- ru_list ?3 entries change a few words and fixed phrases only: unstressed на and не, ноль and the letter name эль with l^, and не было, не были, ни был, вряд ли, что ли, наконец-то, аудиокнига.
- Other soft consonants behave as in ru: soft labials and velars are consonant plus palatal glide and lose palatalisation when no vowel follows (степь, любовь).
- As in ru, ikanye is applied only to the letter е (пятно, часы, язык keep [a]), and unstressed о is [ʌ] even in the first pretonic syllable while pretonic а is [a].
- As in ru, no voicing assimilation between preposition and host (к дому, с братом), /ɕː/ is short, hard /ɫ/ is a retroflex lateral, and only the default eSpeak tunes are used.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 52 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), r (l=s10: tap=3 tapms=18 f2=109 f3=77), a (A=s5: f1=88 f2=84 dur=175), e (e=s6: f1=116 f2=82 dur=80), i (i=s7: f1=88 dur=85), o (o=s8: f1=131 dur=80), u (u=s9: f1=117 f2=83 dur=86), t (t=s11: f2=91 burst=-4 vot=20), p (p=s12: vot=18), k (k=s13: vot=38), ɭ (l=s15: f2=111 f3=71), b (b=s21: voi=1 lead=70), d (d=s22: f2=91 burst=-4 voi=1 lead=75), tʃʲ (t=s25 S=s24: f2=120 f3=108 burst=-4 hold=85; f2=120 f3=108 hold=70), ɡ (g=s28: voi=1 lead=78), ʑ (Z=s35: a3=34 a4=55 a5=22 f2=126 f3=121), sʲ (s=s36: f2=129 f3=108), ɕ (S=s37: a2=31 a3=34 a4=34 a5=22 f2=119 f3=116), tʲ (t=s42: f2=129 f3=108 burst=-4 vot=20), dʲ (d=s43: f2=129 f3=108 burst=-4 voi=1 lead=75), mʲ (m=s44: f2=220), y (y=s46: dur=85), ɪ (I=s45: dur=137), ja (j A=s5: f1=88 f2=84 dur=175), ɛ (E=s47: dur=126), ʌ (OE=s48: f1=112 f2=87 f3=114 dur=126), ɔ (O=s49: dur=150), ɵ (Y=s50: f2=89 f3=107 dur=137), ju (j u=s9: f1=117 f2=83 dur=86), ɑ (A=s51: f1=91 f2=86 dur=175), ɑː (a=s64: f1=89 f2=86 dur=72), iː (i=s67: f1=88 dur=117), aɪ (a=s73: g1=54 g2=143 g3=101 glide=1 dur=72), eɪ (e=s74: g1=107 g2=87 g3=94 glide=1).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (кто, что, где, когда ...) ends as a statement does, from a high question word.

Sources: Yanushevskaya, Irena & Bunčić, Daniel (2015). Russian. Journal of the International Phonetic Association 45(2), 221-228. Jones, Daniel & Ward, Dennis (1969). The Phonetics of Russian. Cambridge University Press. Avanesov, R. I. (1984). Russkoe literaturnoe proiznošenie. Moscow: Prosveščenie. Timberlake, Alan (2004). A Reference Grammar of Russian. Cambridge University Press. Fant, Gunnar (1960). Acoustic Theory of Speech Production. The Hague: Mouton. Padgett, Jaye & Tabain, Marija (2005). Adaptive dispersion theory and phonological vowel reduction in Russian. Phonetica 62, 14-54. And 3 more in the profile.

## Russian (Latvia) (`ru-lv`)

Indo-European, Balto-Slavic, Slavic, East Slavic. Described: Russian as used in Latvia. Native speakers in Latvia use the sound system of Standard Russian; regional phonetic differences are slight and little documented. The description below is therefore that of Standard Russian. Russian spoken as a second language by Latvian speakers differs more, and that accent is what the eSpeak NG voice imitates.

**What the language has.** Palatalised ('soft') versus non-palatalised ('hard') consonants at almost every place and manner, also word-finally and before consonants. Voiced versus voiceless obstruents (prevoiced versus voiceless unaspirated). Five stressed vowels /i e a o u/, with [ɨ] after hard consonants. Position of stress is lexically contrastive. Long /ɕː/ and geminates at morpheme boundaries.

Stress: free (lexical), mobile. Rhythm: stress-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The voice models a Latvian accent rather than native Russian as spoken in Latvia: the phoneme table ru-lv (inherits ru) and the ?2 rules remove features that native speakers in Latvia share with the standard.
- Unstressed е stays [e] (река [rʲeˈka], сегодня [sʲeˈvodɲʌ]): no ikanye. а, я after soft consonants stay [a] as in ru.
- Unstressed о keeps the phoneme o (молоко is output as [moloˈko]) and is realised with an open vowel (formant file aa_7): one degree of akanye, without the [ə] of other unstressed syllables.
- Hard л is a clear alveolar [l] (the Latvian-style l), not velarised [ɫ].
- Final б and в are not devoiced (хлеб [xlʲeb], лев [lʲev]); final д, г, ж, з are.
- щ is a long hard [ʃʃ] and сч is [ʃ] instead of soft [ɕː].
- Soft н is the palatal nasal [ɲ] (kept word-finally: день [dʲeɲ]); soft л is l plus glide and is lost word-finally as in ru; м and з before soft vowels can stay hard (мил [mil], земля [zemlʲˈa]).
- ь and ъ before я, ю, е, ё give a short pause (семья [sʲem_ˈja]).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 49 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), r (l=s10: tap=3 tapms=18 f2=109 f3=77), a (A=s5: f1=88 f2=84 dur=175), e (e=s6: f1=116 f2=82 dur=80), i (i=s7: f1=88 dur=85), o (o=s8: f1=131 dur=80), u (u=s9: f1=117 f2=83 dur=86), t (t=s11: f2=91 burst=-4 vot=20), p (p=s12: vot=18), k (k=s13: vot=38), ɲ (n=s20: f2=136 f3=109), b (b=s22: voi=1 lead=70), d (d=s23: f2=91 burst=-4 voi=1 lead=75), tʃʲ (t=s26 S=s25: f2=120 f3=108 burst=-4 hold=85; f2=120 f3=108 hold=70), ɡ (g=s29: voi=1 lead=78), ʑ (Z=s36: a3=34 a4=55 a5=22 f2=126 f3=121), sʲ (s=s37: f2=129 f3=108), tʲ (t=s43: f2=129 f3=108 burst=-4 vot=20), dʲ (d=s44: f2=129 f3=108 burst=-4 voi=1 lead=75), mʲ (m=s45: f2=220), y (y=s47: dur=85), ɪ (I=s46: dur=137), ja (j A=s5: f1=88 f2=84 dur=175), ɛ (E=s48: dur=126), ʌ (OE=s49: f1=112 f2=87 f3=114 dur=126), ɔ (O=s50: dur=150), ɵ (Y=s51: f2=89 f3=107 dur=137), ju (j u=s9: f1=117 f2=83 dur=86), ɑ (A=s52: f1=91 f2=86 dur=175), ɑː (a=s64: f1=89 f2=86 dur=72), iː (i=s67: f1=88 dur=117), aɪ (a=s73: g1=54 g2=143 g3=101 glide=1 dur=72), eɪ (e=s74: g1=107 g2=87 g3=94 glide=1).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (кто, что, где, когда ...) ends as a statement does, from a high question word.

Sources: Yanushevskaya, Irena & Bunčić, Daniel (2015). Russian. Journal of the International Phonetic Association 45(2), 221-228. Jones, Daniel & Ward, Dennis (1969). The Phonetics of Russian. Cambridge University Press. Avanesov, R. I. (1984). Russkoe literaturnoe proiznošenie. Moscow: Prosveščenie. Timberlake, Alan (2004). A Reference Grammar of Russian. Cambridge University Press. Fant, Gunnar (1960). Acoustic Theory of Speech Production. The Hague: Mouton. Ringen, Catherine & Kulikov, Vladimir (2012). Voicing in Russian stops: cross-linguistic implications. Journal of Slavic Linguistics 20(2), 269-300. And 2 more in the profile.

## Aromanian (`rup`)

Indo-European, Romance, Eastern Romance. Described: Aromanian as written in the orthography with ã, dz, lj, nj, sh, ts; a general description drawn from the dialect studies, without one standard variety.

**What the language has.** Seven vowels with two central ones /ɨ/ and /ə/; several varieties have only one central vowel, and the orthography writes both with ã. Dental fricatives /θ ð/ and velar /ɣ/, mostly in words of Greek and Albanian origin (thimelj, dhascal). Affricates /ts dz/ and /tʃ dʒ/; /dz/ is kept where Romanian has /z/ (dzuã 'day', dzãc 'I say'). Palatal sonorants /ɲ ʎ/ (njic 'small', ljepuri 'hare') and palatal stops /c ɟ/ (written ch, gh before e, i), many of them from old labials before i (ghini 'well', cheptu 'chest'). Plain versus palatalised final consonant in plurals and verb forms, through final non-syllabic i. The diphthongs /e̯a/ and /o̯a/, alternating with /e/ and /o/. Lexical stress.

Stress: lexical, free. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- final short u and i are full vowels (lupu [lˈupu], lupi [lˈupi]); the non-syllabic or whispered final vowels of the language are missing, unlike in the Romanian voice.
- stress follows a fixed rule (penultimate when the word ends in a vowel, otherwise final), so forms with endings are wrong (casili [kasˈili], fratili [fratˈili], lupilj [lupˈiʎ], oaminj [o̯amˈiɲ] for stress on the first syllable).
- the letter o is always given primary stress, a heuristic that relies on the raising of unstressed o to u; it fails in newer loanwords that keep an unstressed o.
- ci, gi before a vowel keep a glide: ficior [fitʃjˈor], gioc [dʒjˈok], gione [dʒjˈone], where i only marks the affricate.
- the IPA labels of the palatal stops contain a stress mark in place of a palatal symbol (ghini prints as [gˈˈini], cheatrã as [kˈˈe̯atrə]).
- ã is always [ə] and â always [ɨ], as the spelling allows no better; varieties that distinguish the two central vowels cannot be served from this orthography.
- no tune set is selected, so the generic default tunes are used.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 22 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (E=s1: f1=93 f2=78), i (i=s4: dur=114), u (u=s4: dur=114), h (<h=s9: ms=70 whisper=44), b (b=s12: voi=1 lead=75), d (d=s12: voi=1 lead=75), gˈ (g=s12: voi=1 lead=75), ɡ (g=s12: voi=1 lead=75), ð (v=s19: f2=135 f3=116 a6=28 ab=48), θ (f=s20: f2=149 f3=116 a6=28 ab=48), ɣ (Z=s26: f2=77 f3=107 a2=68 a3=0 a4=52 af=-4), ɨ (i=s31: f1=122 f2=77 f3=88 dur=114), aʊ (a=s33: g1=57 g2=72 g3=97 glide=1 dur=131), eʊ (e=s34: g1=95 g2=59 g3=91 glide=1 dur=148), aɪ (a=s36: g1=55 g2=127 g3=106 glide=1 dur=131), eɪ (e=s37: g1=91 g2=100 g3=99 glide=1 dur=148), oɪ (o=s39: g1=88 g2=203 g3=106 glide=1 dur=150), e̯a (y=s35 a: hold=55), o̯a (w=s35 a: hold=55), ou̯ (o=s41: g1=71 g2=91 g3=97 glide=1 dur=150), ij (i=s4 y: dur=114).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (ți, cari, iu, cându ...) ends as a statement does, from a high question word.

Sources: Capidan, Theodor (1932). Aromânii: dialectul aromân. Studiu lingvistic. București: Academia Română. Caragiu Marioțeanu, Matilda (1968). Fono-morfologie aromână: studiu de dialectologie structurală. București: Editura Academiei. Caragiu Marioțeanu, Matilda (1975). Compendiu de dialectologie română (nord- și sud-dunăreană). București: Editura Științifică și Enciclopedică. Saramandu, Nicolae (1984). Aromâna. In Rusu (ed.), Tratat de dialectologie românească. Craiova: Scrisul Românesc. Gołąb, Zbigniew (1984). The Arumanian Dialect of Kruševo in SR Macedonia, SFR Yugoslavia. Skopje: Macedonian Academy of Sciences and Arts. Maiden, Martin (2016). Romanian, Istro-Romanian, Megleno-Romanian, and Aromanian. In Ledgeway and Maiden (eds.), The Oxford Guide to the Romance Languages. Oxford University Press.

## Sindhi (`sd`)

Indo-European, Indo-Iranian, Indo-Aryan (Northwestern zone). Described: Standard Sindhi based on the Vicholi (central, 'Middle') dialect of Sindh, written in the Perso-Arabic Sindhi script.

**What the language has.** Five-way contrast in voiced and voiceless stops at the labial, retroflex, palatal and velar places: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced and voiced implosive (/p pʰ b bʱ ɓ/); the dental place has no implosive. Four voiced implosives /ɓ ɗ ʄ ɠ/; the coronal one is retroflex or postalveolar [ᶑ]. Dental versus retroflex stops. Plain versus breathy voiced (aspirated) sonorants: /m n ɳ l ɽ/ : /mʱ nʱ ɳʱ lʱ ɽʱ/. Four nasal places /m n ɳ ɲ ŋ/, with /ɲ/ and /ŋ/ as independent phonemes. Ten vowels: short /ɪ ə ʊ/ against long peripheral /i e ɛ ɑ ɔ o u/. Oral versus nasal vowels. Consonant gemination is marginal: old geminate voiced stops became the implosives.

Stress: weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The four implosives are mapped to the plain voiced stops: ٻ gives [b], ڏ gives [ɖ], ڄ gives [ɟ], ڳ gives [ɡ], the same output as ب, ڊ, ج, گ. The implosive contrast, the most characteristic feature of Sindhi, is lost completely; the phoneme table has no implosive phonemes.
- ٿ (dental aspirated) becomes the retroflex unaspirated stop when the inherent vowel follows (ٿر [ʈʌr], هٿ [hʌʈ]); the rule has t. where t# is meant.
- ڱ (velar nasal) is mapped to the syllabic nasal phoneme N-, a vowel-type segment.
- Breathy sonorants are a sonorant plus separate [h] with inserted vowels (ماڻهو [maːɳhuː], ڳالهه [ɡaːləhʌh]).
- The word-final short vowels are never produced (ٻار [baːr], هٿ [hʌʈ]); unwritten short vowels inside words are guessed as schwa and then subjected to the Hindi schwa-deletion logic.
- The rules are an adaptation of the Urdu rules and still contain Urdu word entries; /r/ is the trill [R].
- Breathy voiced stops come from the Hindi base table (voiced closure plus voiceless aspiration sample); /ɦ/ is voiceless [h].
- Sindhi written in Devanagari is handed to the Nepali voice.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f1=129 f2=91), i (i=s7: dur=56), t (t=s10: f2=91 burst=-4 vot=16), p (p=s11: vot=13), r (l=s9: tap=3 tapms=18 f2=109 f3=77), h (<h=s17: ms=70 whisper=44), r. (l=s20: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s21: voi=1 lead=75), d (d=s22: f2=91 burst=-4 voi=1 lead=75), t̪ (t=s10: f2=91 burst=-4 vot=16), ɟ (d=s27: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), ʋ (v=s30: af=-14), q (k=s39: f2=68 f3=109 f1=118 burst=3 vot=30), ʌ (OE=s41: f1=112 f2=87 f3=114 dur=84), iː (i=s42: dur=117), ɪ (I=s43: f1=83), aː (a=s46: dur=72), ẽ (e=s53: dur=53 nas=100), ã (A=s55: nas=100), ɖ (d=s66: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75), kʰ (k=s71: vot=85 asp=50).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (ڇا, ڪير, ڪٿي, ڪڏهن ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Nihalani, Paroo (1995). Sindhi. Journal of the International Phonetic Association 25(2), 95-98; reprinted in Handbook of the International Phonetic Association (1999), Cambridge University Press, 131-134. Nihalani, Paroo (1974). An aerodynamic study of stops in Sindhi. Phonetica 29, 193-224. Nihalani, Paroo (1986). Phonetic implementation of implosives. Language and Speech 29(3), 253-262. Khubchandani, Lachman M. (2003). Sindhi. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Keerio, Ayaz (2010). Acoustic Analysis of Sindhi Speech: A Pre-curser for an ASR System. DPhil thesis, University of Sussex. Ladefoged, Peter & Maddieson, Ian (1996). The Sounds of the World's Languages. Oxford: Blackwell. And 3 more in the profile.

## Shan (Tai Yai) (`shn`)

Kra-Dai (Tai-Kadai), Tai, Southwestern Tai. Described: Shan of Shan State, Myanmar (Tai Long, also called Tai Yai), as written in the modern Shan script: five tones plus a sixth, emphatic tone.

**What the language has.** Aspirated against unaspirated stops (p pʰ, t tʰ, k kʰ); no voiced stops, unlike Thai and Lao. Five tones, with a sixth used for emphasis (a regular lexical tone in northern dialects). Vowel length only in the low vowel, a against aː, in closed syllables and diphthongs. Back unrounded ɯ ɤ against back rounded u o. Final stops p t k against final nasals m n ŋ. The diphthong aɯ, kept apart from ai.

Stress: none (no lexical stress). Rhythm: syllable-timed. Tone: lexical tone, 6 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- the tokenizer ends the word at the tone marks U+1087 to U+108A and at the asat U+103A, so the whole-syllable entries of shn_list and the context rules of shn_rules cannot match: ၵႃႇ, ၵႃႈ, ၵႃႉ and ၵႃႊ are all spoken with tone 1, and only the mark း (tone 4) is applied; in running text the marks for tones 2, 3, 5 and 6 have no effect.
- for the same reason closed syllables written with the inherent vowel lose it: ၶဝ်ႈ comes out as [kʰw], ၼမ်ႉ as [nm], ၽၵ်း as [pʰk].
- the rules give the short vowel signs i and u a fixed tone 5, so ၵိၼ် is spoken with the falling tone instead of the rising tone.
- when the mark း ends up as a separate token it is read out by name, as 'Myanmar letter' followed by the digits of its code point (1038).
- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c ignores the clause type, and a question gives the same audio as a statement.
- the tonal pitch range is very small: pitch values 10 to 50 give about 78 to 97 Hz at the default voice pitch (under 4 semitones).
- tone 5 has no creaky voice, no glottal closure and is not short.
- the aspirated t (t_h) uses the recording of plain t; ph_shan marks this as still to be done.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 25 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=140), ʔ (<q=s4: ms=50 hush=1), ɹ (r=s9: f2=92 f3=77), a (A=s5: dur=150), e (e=s6: dur=70), i (i=s7: dur=75), o (o=s6: dur=70), u (u=s8: dur=76), t (t=s11: vot=17), p (p=s12: vot=13), k (k=s13: vot=28), r (l=s10: tap=3 tapms=18 f2=109 f3=77), h (<h=s18: ms=70 whisper=44), d (d=s22: voi=1 lead=75), tɕ (t=s27 S=s28: hold=85 f2=119 f3=116; a2=31 a3=34 a4=34 a5=22 f2=119 f3=116 hold=70), ɟ (d=s29: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), p_h (p=s12 <h=s18: vot=13; ms=70 whisper=44), t_h (t=s11 <h=s18: vot=17; ms=70 whisper=44), k_h (k=s13 <h=s18: vot=28; ms=70 whisper=44), ɔ (O=s45: dur=127), əi (@=s54: g1=68 g2=130 g3=113 glide=1 dur=208), aːi (a=s56: g1=43 g2=166 g3=113 glide=1), ɔi (O=s57: g1=55 g2=222 g3=113 glide=1 dur=220), ɑː (a=s65: f1=89 f2=86).

Tones: 1 (0:20,30:20,100:40), 2 (0:12,100:10), 3 (0:32,70:31,100:22), 4 (0:49,100:50), 5 (0:42,100:20), 6 (0:30,50:42,100:30). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Edmondson, Jerold A. (2008). Shan and other Northern Tier Southeast Tai languages of Myanmar and China: themes and variations. In Anthony V. N. Diller, Jerold A. Edmondson & Yongxian Luo (eds.), The Tai-Kadai Languages. Routledge. Sao Tern Moeng (1995). Shan-English Dictionary. Dunwoody Press. Glick, Irving I. & Sao Tern Moeng (1991). Shan for English Speakers. Dunwoody Press. Cushing, Josiah Nelson (1887). Grammar of the Shan Language, 2nd edition. Rangoon: American Baptist Mission Press.

## Sinhala (`si`)

Indo-European, Indo-Iranian, Indo-Aryan (Insular Indo-Aryan, with Dhivehi). Described: Colloquial (spoken) Sinhala of the Colombo area; the literary language is read with the same sound system.

**What the language has.** Prenasalised voiced stops /ᵐb ⁿd̪ ᶯɖ ᵑɡ/ versus nasal plus stop clusters /mb nd̪ ɳɖ ŋɡ/ (/kaⁿd̪ə/ 'trunk' : /kand̪ə/ 'hill'): one of very few languages with this contrast. No aspiration contrast: only voiced and voiceless stops; the aspirate letters of the script occur in Sanskrit and Pali loans and are read as plain stops. Dental versus retroflex stops (the retroflexes are apical and only slightly retracted). Vowel length for all qualities, including the front open vowel /æ/ : /æː/. Consonant gemination (/malə/ 'flower' : /mallə/ 'bag'). /a/ versus /ə/, close to complementary distribution.

Stress: weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The prenasalised nasals (m#, n#, n.#, N#, n^#) are marked 'temporary' and simply call the full nasals m, n, ɳ, ŋ, ɲ: a prenasalised stop is produced as a full nasal plus stop, so කඳ /kaⁿd̪ə/ and කන්ද /kand̪ə/ sound the same. Only the IPA output shows a difference (ⁿd : nd).
- The anusvara sign is [m] unless a velar, palatal or retroflex stop follows: ගං gives [ɡam], මං [mam], සංවිධානය [samwi...]; Sinhala has [ŋ] everywhere.
- Word-final ව after a vowel loses its vowel: ලංකාව [laŋkaːw], භාෂාව [bʰaːʃaːw] for [laŋkaːʋə], [baːʃaːʋə]. This affects a very common noun ending.
- Aspirate letters are pronounced as aspirated or breathy stops (භ, ධ, ඛ, ඨ), which spoken Sinhala does not have.
- /r/ is the English approximant [ɹ] (phoneme r imports base1/r), not a tap.
- /a/ becomes [ə] in every unstressed syllable, also in closed ones: මහත්තයා gives [mahəttəjaː] for [mahattəjaː].
- ණ and ළ are retroflex [ɳ], [ɭ]; ශ is [s] while ෂ is [ʃ].
- The phoneme file notes that its definitions 'are only guesses'; intonation is the reduced generic tune (intonation 2).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 20 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: tʰ (t=s4: f2=91 burst=-4 vot=68 asp=50), ɹ (r=s8: f2=92 f3=77), ɐ (A=s9: f1=85), e (e=s5: dur=53), i (i=s6: dur=56), o (o=s5: dur=53), u (u=s7: dur=57), t (t=s11: f2=91 burst=-4 vot=16), p (p=s12: vot=13), k (k=s13: vot=28), ɭ (l=s16: f2=111 f3=71), h (<h=s18: ms=70 whisper=44), b (b=s22: voi=1 lead=75), d (d=s23: f2=91 burst=-4 voi=1 lead=75), ɡ (g=s22: voi=1 lead=75), iː (i=s43: dur=117), aː (a=s46: dur=72), uː (u=s43: dur=117), ʈ (t=s63: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), æ (E=s70: f1=124 f2=92 f3=92 dur=84).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (මොකක්ද, කවුද, කොහෙද, කවදාද ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Gair, James W. & Paolillo, John C. (1997). Sinhala. Languages of the World/Materials 34. München: Lincom Europa. Gair, James W. (2003). Sinhala. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Karunatillake, W. S. (1992). An Introduction to Spoken Sinhala. Colombo: M. D. Gunasena (3rd edn 2004). Disanayaka, J. B. (1991). The Structure of Spoken Sinhala. Maharagama: National Institute of Education. Chandralal, Dileep (2010). Sinhala. London Oriental and African Language Library 15. Amsterdam: John Benjamins. Coates, William A. & de Silva, M. W. S. (1960). The segmental phonemes of Sinhalese. University of Ceylon Review 18, 163-175. And 6 more in the profile.

## Sindarin (`sjn`)

constructed language. Described: the late Third Age form of the published writings.

**What the language has.** A front rounded vowel. Voiceless l and r. Dental fricatives. Long vowels beside short ones.

Stress: by rule. Rhythm: mixed.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 23 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s16: ms=70 whisper=44), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɡ (g=s20: voi=1 lead=75), ð (v=s31: f2=149 f3=110 a6=28 ab=48), θ (f=s32: f2=146 f3=110 a6=28 ab=48), ɬ (l=s40: fric=52 a3=54 a4=58 a5=44 whisper=30), χ (x=s2: f2=88), ɛ (E=s41: dur=84), ɔ (O=s42: dur=85), iː (i=s45: dur=117), uː (u=s45: dur=117), y (y=s5: dur=56), aɪ (a=s47: g1=56 g2=146 g3=101 glide=1 dur=72), ɔɪ (O=s50: g1=73 g2=194 g3=101 glide=1 dur=220), ʍ (w=s51: whisper=46), aɛ (a=s52: g1=72 g2=136 g3=99 glide=1 dur=72), ɛɪ (E:=s53: g1=83 g2=94 g3=97 glide=1), uɪ (w=s54 I: hold=55).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises at the end.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Tolkien, J. R. R. (1955). The Lord of the Rings, Appendix E.

## Slovak (`sk`)

Indo-European, Balto-Slavic, Slavic, West Slavic (Czech-Slovak). Described: Standard Slovak (codified norm based on the central dialects, as spoken in Bratislava and central Slovakia).

**What the language has.** Phonemic vowel length, independent of stress (sud 'barrel' vs súd 'court'). Short versus long syllabic liquids /r̩ l̩/ vs /r̩ː l̩ː/ (vrch vs vŕba, vlk vs kĺb). Four rising diphthongs /i̯a i̯ɛ i̯u u̯ɔ/ (written ia, ie, iu, ô) that count as long nuclei. Palatal /c ɟ ɲ ʎ/ versus alveolar /t d n l/ (ľ versus l is kept in the codified norm; many speakers merge it with /l/, especially before e and i). Voiced versus voiceless obstruents, including voiced glottal /ɦ/ paired with voiceless velar /x/. Affricates /t͡s d͡z t͡ʃ d͡ʒ/, all four native.

Stress: fixed initial, weak. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- The rising diphthongs are read as two full vowels: ia, ie, iu become unstressed [i] plus a stressed second vowel (piatok [pi.ˈa.tok], rieka [ri.ˈe.ka], chlieb [xli.ˈep]) and ô becomes [u] plus [o] (kôň [ˈku.oɲ]). This adds a syllable and moves the stress away from the first syllable.
- Some words whose only nucleus is a syllabic liquid are spelled out letter by letter (kĺb); others work (stĺp, vlk, krk, vŕba).
- k is never voiced before a voiced obstruent (kde gives [kɟ]).
- The prepositions s and k are not assimilated to the next word (s bratom, s otcom, k domu keep [s], [k]; the norm has [z], [ɡ]).
- ä is always [e]; there is no [æ] (acceptable for most speakers).
- Word-final voiceless obstruents are not voiced before a vowel or sonorant of the next word (vlak ide, chlap robí keep [k], [p]; the norm has [ɡ], [b]); only written voiced finals stay voiced there.
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.
- The nominal long to short vowel length in the phoneme table is about 2.4 to 1 (290 vs 120).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), r (l=s8: tap=3 tapms=18 f2=109 f3=77), ʎ (l=s13: f2=159), h (<h=s16: ms=70 whisper=44), ɲ (n=s18: f2=136 f3=109), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɣ (r=s38: f1=73 f3=116), tʲ (t=s46: f2=129 f3=108 vot=25), dʲ (d=s47: f2=129 f3=108 voi=1 lead=75), iː (i=s48: dur=117), aː (a=s50: dur=72), uː (u=s48: dur=117), r̩ː (l=s56: tap=3 tapms=18 f2=109 f3=77 hold=185), l̩ː (l=s58: hold=185).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (kto, čo, kde, kedy ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Hanulíková, Adriana & Hamann, Silke (2010). Slovak. Journal of the International Phonetic Association 40(3), 373-378. Kráľ, Ábel (1988). Pravidlá slovenskej výslovnosti. Bratislava: Slovenské pedagogické nakladateľstvo. Kráľ, Ábel & Sabol, Ján (1989). Fonetika a fonológia. Bratislava: Slovenské pedagogické nakladateľstvo. Pauliny, Eugen (1979). Slovenská fonológia. Bratislava: Slovenské pedagogické nakladateľstvo. Rubach, Jerzy (1993). The Lexical Phonology of Slovak. Oxford University Press. Short, David (1993). Slovak. In B. Comrie & G. G. Corbett (eds.), The Slavonic Languages. London: Routledge. And 1 more in the profile.

## Slovenian (`sl`)

Indo-European, Balto-Slavic, Slavic, South Slavic (western group). Described: Standard Slovenian as spoken in Ljubljana. The standard accepts two accent systems: a tonemic one (pitch accent, central dialects including Ljubljana) and a non-tonemic one (stress only, used by most speakers from other regions). Both are described.

**What the language has.** Close-mid versus open-mid vowels under stress, not shown in ordinary spelling (pot: [poːt] 'path' vs [pɔːt] 'sweat'; péti 'to sing' vs pêti 'fifth'). Schwa /ə/ as a separate vowel, also stressed (pes [pəs], dež [dəʃ]), spelled e. Tonemic varieties: acute versus circumflex pitch accent on long stressed syllables. Traditional norm: long versus short stressed vowels, the short ones almost only in final syllables (brat [brat] vs brata [ˈbraːta]). Position of stress is lexical. Voiced versus voiceless obstruents (neutralised word-finally and in clusters).

Stress: free (lexical), mobile. Rhythm: mixed. Tone: pitch accent, 3 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- Stress is put on the penultimate syllable by default (marked 'Temporary' in tr_languages.c) and the word list has only about 250 entries; Slovenian stress is lexical, so many words are wrong unless the text carries accent marks (slovenščina, otrok, rdeč, rjav).
- Every stressed vowel is made long and stressed e, o default to close-mid [eː oː]. Open-mid /ɛː ɔː/ and stressed schwa cannot be seen in the spelling and are mostly missed: voda, gora, noga get [oː] instead of [ɔː]; pes, dež get [eː] instead of [ə]; short final stressed vowels are lengthened (brat, kmet).
- No pitch accent: acute and circumflex are not distinguished (no tone phonemes in the phoneme table). This matches the non-tonemic standard only.
- Word-final nj is the palatal nasal [ɲ] (konj); the standard has [n].
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 14 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s9: vot=17), p (p=s10: vot=13), k (k=s11: vot=28), r (l=s8: tap=3 tapms=18 f2=109 f3=77), b (b=s20: voi=1 lead=75), d (d=s20: voi=1 lead=75), ɡ (g=s20: voi=1 lead=75), ʋ (v=s30: af=-14), ɛ (E=s41: dur=84), ɔ (O=s42: dur=85).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (kdo, kaj, kje, kdaj ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

**Not yet.** The tonemes are not in eSpeak NG's reading.

Sources: Šuštaršič, Rastislav; Komar, Smiljana & Petek, Bojan (1999). Slovene. In Handbook of the International Phonetic Association, 135-139. Cambridge University Press. Toporišič, Jože (2000). Slovenska slovnica. Maribor: Obzorja. Srebot-Rejec, Tatjana (1988). Word Accent and Vowel Duration in Standard Slovene: An Acoustic and Linguistic Investigation. München: Otto Sagner. Petek, Bojan; Šuštaršič, Rastislav & Komar, Smiljana (1996). An acoustic analysis of contemporary vowels of the standard Slovenian language. Proceedings of ICSLP 96, Philadelphia. Jurgec, Peter (2011). Slovenščina ima 9 samoglasnikov. Slavistična revija 59(3). Herrity, Peter (2000). Slovene: A Comprehensive Grammar. London: Routledge. And 2 more in the profile.

## Lule Saami (`smj`)

Uralic, Saami (Western Saami). Described: Lule Saami as written in the 1983 standard orthography and spoken around Jokkmokk (Sweden) and Tysfjord/Divtasvuodna (Norway).

**What the language has.** Three degrees of consonant quantity after a stressed vowel (Q1 short, Q2 long, Q3 overlong), alternating in consonant gradation. Vowel length (short against long) and four diphthongs. Preaspirated stops and affricates (hp, ht, hk, hts, htj) against plain ones. Pre-stopped nasals (bm, dn, dnj, gŋ) against plain nasals. Palatal /ɲ ʎ ɟ/ against alveolars and velars.

Stress: fixed, word-initial. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- the voice is marked 'status testing' and its phoneme table is a copy of the Finnish one with a few additions; it keeps the eighteen Finnish diphthong phonemes, of which only ie and uo belong to Lule Saami.
- quantity 3 is not told apart from quantity 2 in geminates (the spelling writes both double), so bállo and similar forms get one long consonant of fixed length.
- preaspiration is deleted in the quantity 3 spellings hkk, hpp, htt (áhkko is given as [ɑːkːuo]); descriptions have the first element lengthened there, not dropped.
- nj is rendered as [n], a short pause and [j] instead of the palatal nasal [ɲ], and lj has no rule, so [ʎ] is missing.
- the letter i is always long [iː] (idja, loddi), although long /iː/ is rare in the language.
- v in a syllable coda stays [v] (biejvve, jávrre) instead of the glide [w].
- the epenthetic vowel of quantity 3 clusters is produced only for a fixed list of vowel and cluster spellings.
- no aspiration of p, t, k in native words (only before á in loanword rules).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 33 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s7: tap=3 tapms=18 f2=109 f3=77), e (e=s4: dur=53), i (i=s5: dur=56), o (o=s4: dur=53), u (u=s6: dur=57), t (t=s8: vot=17), p (p=s9: vot=13), k (k=s10: vot=28), h (<h=s15: ms=70 whisper=44), b (b=s19: voi=1 lead=75), d (d=s19: voi=1 lead=75), ɟ (d=s26: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s27: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s19: voi=1 lead=75), ʂ (S=s33: a4=54 f2=87 f3=83 f4=88), ɛ (E=s40: dur=84), ɑ (A=s42: f1=91 f2=86), ɔ (O=s43: dur=85), ʊ (U=s44: dur=114), ʉ (Y=s45: f1=78), y (y=s5: dur=56), eu (e=s55: g1=85 g2=45 g3=87 glide=1), uo (w=s61 o=s4: hold=55; dur=53), ɹ (r=s64: f2=92 f3=77), ɒ (O=s69: f1=116 dur=85), iː (i=s72: dur=117), uː (u=s72: dur=117), aɪə (A j=s61 j=s61: hold=55; hold=55).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Spiik, Nils Eric (1989). Lulesamisk grammatik. Jokkmokk: Sameskolstyrelsen. Sammallahti, Pekka (1998). The Saami Languages: An Introduction. Kárášjohka: Davvi Girji. Ylikoski, Jussi (2022). Lule Saami. In Bakró-Nagy, Marianne; Laakso, Johanna; Skribnik, Elena (eds.), The Oxford Guide to the Uralic Languages. Oxford University Press. Fangel-Gustavson, Nora; Ridouane, Rachid; Morén-Duolljá, Bruce (2014). Quantity contrast in Lule Saami: a three-way system. Proceedings of the 10th International Seminar on Speech Production (ISSP), Cologne. Wiklund, K. B. (1891). Laut- und Formenlehre der Lule-lappischen Dialekte.

## Albanian (`sq`)

Indo-European, Albanian. Described: Standard Albanian, which is based on Tosk; phonetic detail from Northern Tosk speakers (Coretta et al. 2023).

**What the language has.** Two rhotics: a tap or flap (written r) against a trill (written rr). Two laterals: a plain, slightly palatalised alveolar /l/ against a velarised dental /ɫ/ (written ll). Dental fricatives /θ ð/ beside /s z/ and /ʃ ʒ/. Three pairs of affricates: alveolar /t͡s d͡z/, postalveolar /t͡ʃ d͡ʒ/, and the pair written q, gj, traditionally palatal stops /c ɟ/. Voicing in all stops, affricates and fricatives except /h/. Front rounded /y/ and a mid central vowel (written ë) that can be stressed. Lexical stress. No contrast of vowel length or nasality in the Tosk-based standard; both exist in Gheg.

Stress: lexical, largely predictable from word structure. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- a word-final vowel is never stressed unless a rule says so: shtëpi, liri, atdhe and kafe are stressed on the penultimate syllable, in shtëpi even on ë.
- rr at the beginning of a word gets a schwa in front (rrugë is given as [əˈruɡə]).
- single r is a trill and rr a double trill, so the contrast is one of length, not tap against trill.
- the vowel sequences ua and ie are made a glide plus vowel (grua as [ɡrwɑ], dielli as [djelli]), which moves the syllable peak.
- final unstressed ë after a consonant is made a very short schwa by rule in most words, a colloquial feature applied everywhere.
- IPA output is misleading: plain l is printed [ɫ], velarised ll is printed 'll', and stressed ë is printed [ʌ].
- no voicing of /h/ between vowels and no sandhi across words.
- intonation is generic.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 12 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (E=s1: f1=93 f2=78), i (i=s4: dur=114), u (u=s4: dur=114), k (k=s6: vot=55 asp=50), ɫ (l=s9: f2=67 f3=111), h (<h=s10: ms=70 whisper=44), d (d=s14: voi=1 lead=110), ð (v=s23: f2=135 f3=116 a6=28 ab=48), ɑ (c=s36: f1=125 f2=113), ɪ (e=s35: f1=91), aɪ (a=s38: g1=55 g2=127 g3=106 glide=1 dur=131), ɔɪ (c=s40: g1=73 g2=184 g3=108 glide=1 dur=150).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (kush, çfarë, ç, ku ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

Sources: Coretta, Stefano; Riverin-Coutlée, Josiane; Kapia, Enkeleida; Nichols, Stephen (2023). Northern Tosk Albanian. Journal of the International Phonetic Association 53(3): 1122-1144. Newmark, Leonard; Hubbard, Philip; Prifti, Peter (1982). Standard Albanian: A Reference Grammar for Students. Stanford University Press. Buchholz, Oda; Fiedler, Wilfried (1987). Albanische Grammatik. Leipzig: Verlag Enzyklopädie. Camaj, Martin (1984). Albanian Grammar. Wiesbaden: Harrassowitz. Moosmüller, Sylvia; Granser, Theodor (2006). The spread of Standard Albanian: an illustration based on an analysis of vowels. Language Variation and Change 18: 121-140. Kolgjini, Julie M. (2004). Palatalization in Albanian: an acoustic investigation of stops and affricates. PhD dissertation, University of Texas at Arlington.

## Serbian (`sr`)

Indo-European, Balto-Slavic, Slavic, South Slavic (western group, Serbo-Croatian). Described: Standard Serbian (Neo-Štokavian norm, Ekavian as used in Belgrade and Novi Sad; the Ijekavian standard is used in Bosnia and Herzegovina and Montenegro). Written in Cyrillic and Latin script.

**What the language has.** Four word accents: short falling (kȕća), long falling (mȃjka), short rising (vòda), long rising (rúka). Vowel length under the accent and in syllables after the accent (post-accentual length: jùnāk, genitive plural žénā). Postalveolar /t͡ʃ d͡ʒ/ (č, dž) versus alveolo-palatal /t͡ɕ d͡ʑ/ (ć, đ), kept apart by speakers in Serbia. Palatal /ʎ ɲ/ versus /l n/. Syllabic /r̩/, short or long, as a syllable nucleus that can carry the accent (krv, prst, srpski). Voiced versus voiceless obstruents, kept word-finally (grad [ɡraːd]).

Stress: free (lexical) pitch accent, restricted by position. Rhythm: mixed. Tone: pitch accent, 4 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- No pitch accent: the four accents are not distinguished and there are no tone phonemes. Accent marks in the text are ignored, except that acute-marked vowels are read as long.
- No vowel length apart from a handful of words, so accented and post-accentual length are missing.
- Stress is always on the first syllable. That is right for falling accents but wrong for words with a rising accent on a later syllable (lepòta, telèvīzija, interesàntan).
- Syllabic r between consonants is a plain consonant (phoneme R2) and not a syllable nucleus: krv, prst, trg, smrt come out with no stressed syllable, and prvi, srpski, crkva, brzo are stressed on the last vowel.
- Unstressed /a i u/ are replaced by reduced qualities ([ɐ], [ɪ], [ʊ]); the standard has no vowel reduction.
- The letter e is open-mid [ɛ] but close [e] after j, which has no basis in the language.
- Only the default eSpeak tunes are used; wh-questions get the same fall-rise as yes-no questions.

**What OpenEVV says.** Spoken by the module made from Italian (`itix`). 14 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=51), e (e=s5: dur=55), i (i=s6: dur=63), o (o=s7: dur=53), u (u=s8: dur=61), b (b=s16: voi=1 lead=75), d (d=s16: voi=1 lead=75), dʑ (d=s17 Z=s18: voi=1 lead=75 hold=85 f2=126 f3=122; a3=34 a4=55 a5=22 f2=126 f3=122 hold=70), tɕ (t=s19 S=s20: hold=85 f2=126 f3=122; a2=31 a3=34 a4=34 a5=22 f2=126 f3=122 hold=70), ɡ (g=s16: voi=1 lead=75), x (S=s32: f2=77 f3=107 a2=68 a3=0 a4=52 af=-4), ɛ (E=s5: dur=55), ɐ (a=s42: f1=82 f2=92 dur=51), ɪ (e=s55: f1=91 dur=55).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no ends as a statement does, in a higher register.
A question asked with a question word (ko, tko, šta, što ...) ends as a statement does, from a high question word.
Timing: stressed 106 per cent, weak 94 per cent of the module's own.

**Not yet.** The four accents are not in eSpeak NG's reading: stress is spoken, the rising and falling accents are not.

Sources: Lehiste, Ilse & Ivić, Pavle (1986). Word and Sentence Prosody in Serbocroatian. Cambridge, MA: MIT Press. Lehiste, Ilse & Ivić, Pavle (1963). Accent in Serbocroatian: An Experimental Study. Ann Arbor: University of Michigan. Inkelas, Sharon & Zec, Draga (1988). Serbo-Croatian pitch accent: the interaction of tone, stress, and intonation. Language 64, 227-248. Zsiga, Elizabeth & Zec, Draga (2013). Contextual evidence for the representation of pitch accents in Standard Serbian. Language and Speech 56. Smiljanić, Rajka (2004). Lexical, Pragmatic, and Positional Effects on Prosody in Two Dialects of Croatian and Serbian: An Acoustic Study. New York: Routledge. Godjevac, Svetlana (2005). Transcribing Serbo-Croatian intonation. In Sun-Ah Jun (ed.), Prosodic Typology: The Phonology of Intonation and Phrasing. Oxford University Press. And 2 more in the profile.

## Swedish (`sv`)

Indo-European, Germanic, North Germanic, East Scandinavian. Described: Central Standard Swedish, the educated speech of Stockholm and the Mälaren region, the variety of the IPA illustration (Engstrand 1990).

**What the language has.** Two word accents on stressed syllables of words with at least one following syllable: accent 1 anden 'the duck' versus accent 2 anden 'the spirit', tomten 'the plot' versus 'the gnome', buren 'the cage' versus 'carried', stegen 'the steps' versus 'the ladder'. Complementary quantity in stressed syllables: long vowel plus short consonant versus short vowel plus long consonant (glas [ɡlɑːs] versus glass [ɡlasː], vit versus vitt, ful versus full). Long and short vowels differ in quality as well as length, most of all /ɑː/ versus /a/ and /ʉː/ versus /ɵ/. Three close rounded vowels /yː ʉː uː/ with different kinds of lip rounding (ny, nu, bo). Three voiceless sibilant-like fricatives: /s/, the tj-sound /ɕ/ (tjugo, kör) and the sj-sound /ɧ/ (sju, sked, stjärna). Dental /t d n s l/ versus retroflex [ʈ ɖ ɳ ʂ ɭ] (kort, bord, barn, fors, karl). Lexical stress (formel versus formell, banan).

Stress: lexical. Rhythm: stress-timed. Tone: pitch accent, 2 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- the word accents are not marked anywhere: the phoneme table has no tone phonemes and the dictionary has no accent marks, so both words anden, tomten, buren and stegen sound the same; the Swedish tunes (sv_s, sv_c, sv_q, sv_e) only shape the intonation of the clause.
- complementary quantity is incomplete: the consonant after a short stressed vowel is mostly left short (matt [mat], tack [tak], full [fɵl], glass [ɡlas]); only some spelling rules add length (flickan).
- retroflexion is unreliable for rt: kort is [kɔrt], hjärta and skjorta lose the r and keep a dental [t], värld is [vɛːrd]; there is no retroflexion across word boundaries (för stor, har du, Anders sover).
- the lowering before r is missing: här, ära have [ɛː], kör and björn have [øː], dörr has [œ] of normal height; järn has a short vowel.
- rule errors: kö comes out with the tj-sound, giraff with [j] and initial stress, station with [sj] instead of the sj-sound, regn with schwa, lång with a close [o], universitet with initial stress.
- stops have no preaspiration, and long vowels have no diphthongal offglides.
- questions are given the same tune whether they are yes-no or wh-questions.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 35 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s8: tap=3 tapms=18 f2=109 f3=77), h (<h=s13: ms=70 whisper=44), ɳ (n=s14: f3=80), ɕ (S=s30: a2=31 a3=34 a4=34 a5=22 f2=119 f3=116), iː (i=s35: dur=117), ɛ (E=s36: dur=84), yː (y=s35: dur=117), y (y=s5: dur=56), ʉː (oe=s37: f1=82 f3=109), œ (OE=s36: dur=84), ɵ (Y=s38: f2=89 f3=107), ɑː (a=s40: f1=89 f2=86 dur=72), ɔ (O=s41: dur=85), ʊ (U=s42: dur=114), uː (u=s35: dur=117), ɧ (x=s43: f2=92 f3=88), ʈ (t=s44: f2=91 f3=79 f4=88 a4=52 a5=42), ɖ (d=s44: f2=91 f3=79 f4=88 a4=52 a5=42), ɹ (r=s7: f2=92 f3=77), i (i=s5: dur=56), ð (v=s25: f2=149 f3=110 a6=28 ab=48), ɐ (A=s48: f1=85), ɒ (O=s49: f1=116 dur=85), ʌ (OE=s50: f1=112 f2=87 f3=114 dur=84), ɜː (OE=s52: f3=114 dur=171), ɔː (O=s53: dur=220), əʊ (@=s55: g1=94 g2=65 g3=93 glide=1 dur=208), aɪ (a=s57: g1=56 g2=146 g3=101 glide=1 dur=72), eɪ (e=s58: g1=106 g2=89 g3=95 glide=1), aɪə (A j=s60 j=s60: hold=55; hold=55).

Melody: the stressed syllable is high and the pitch falls out of it. A question that wants yes or no rises at the end.
A question asked with a question word (vem, vad, var, när ...) ends as a statement does, from a high question word.

**Not yet.** The two word accents are not in eSpeak NG's reading, so words are told apart by stress alone.

Sources: Engstrand, Olle (1990). Swedish. Journal of the International Phonetic Association 20(1), 42-44. Reprinted in the Handbook of the International Phonetic Association (1999), Cambridge University Press. Riad, Tomas (2014). The Phonology of Swedish. Oxford University Press. Bruce, Gösta (1977). Swedish Word Accents in Sentence Perspective. Lund: Gleerup. Bruce, Gösta and Gårding, Eva (1978). A prosodic typology for Swedish dialects. In Gårding, Bruce and Bannert (eds.), Nordic Prosody. Lund University. Elert, Claes-Christian (1964). Phonologic Studies of Quantity in Swedish. Stockholm: Almqvist and Wiksell. Lindblad, Per (1980). Svenskans sje- och tje-ljud i ett allmänfonetiskt perspektiv. Lund: Gleerup. And 3 more in the profile.

## Swahili (`sw`)

Niger-Congo, Atlantic-Congo, Bantu (Sabaki group, Guthrie G.42). Described: Standard Swahili (Kiswahili Sanifu), based on the Unguja dialect of Zanzibar town; coastal (Mombasa) differences are noted where they matter.

**What the language has.** Five vowel qualities, with no phonemic length, nasalisation or reduction. Three stop series: voiceless, voiced implosive (ɓ ɗ ʄ ɠ) and prenasalised voiced (ᵐb ⁿd ⁿdʒ ᵑɡ). Velar nasal ŋ (written ng') versus prenasalised ᵑɡ (written ng). Syllabic nasals (mtu, nchi) versus non-syllabic prenasalisation (mbuzi, ndizi). Dental fricatives θ ð and velar fricatives x ɣ in words of Arabic origin. L versus r. Aspirated versus unaspirated voiceless stops in coastal varieties (pʰaa 'gazelle' versus paa 'roof'); not written and not kept by all standard speakers.

Stress: fixed, penultimate. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the velar nasal written ng' fails at the start of a word: ng'ombe and ng'ambo are read as the letter names of n and g followed by the rest of the word, whether the apostrophe is ASCII, U+2019 or U+02BC; inside a word (kung'aa) it is [ŋ], but the word is followed by an unwanted pause.
- b, d, j, g are plain pulmonic voiced stops everywhere; there are no implosive phonemes, so the implosive versus post-nasal plain alternation is missing.
- word-initial m or n before a consonant is syllabic only when it has to carry the penultimate stress (mtu, mbwa, nchi); in longer words (mtoto, mchezo, mkate) it is a plain non-syllabic nasal.
- kh is pronounced as k followed by h, not as the velar fricative [x]; the rule for [x] is shadowed by a rule for k.
- prenasalised stops are full nasal plus stop sequences, with no control of the short nasal portion.
- no aspirated stops for coastal varieties.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 5 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: u (u=s4: dur=114), h (<h=s8: ms=70 whisper=44), d (d=s11: voi=1 lead=75), ɟ (d=s16: f2=148 f3=109 a3=56 a4=56 voi=1 lead=75), ɡ (g=s11: voi=1 lead=75).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (nani, nini, wapi, lini ...) ends as a statement does, from a high question word.
Timing: last 88 per cent of the module's own.

Sources: Contini-Morava, Ellen (1997). Swahili phonology. In Alan S. Kaye (ed.), Phonologies of Asia and Africa. Winona Lake: Eisenbrauns. Polomé, Edgar C. (1967). Swahili Language Handbook. Washington, DC: Center for Applied Linguistics. Tucker, A. N. & Ashton, E. O. (1942). Swahili phonetics. African Studies 1. Ashton, E. O. (1944). Swahili Grammar (Including Intonation). London: Longmans, Green. Maw, Joan & Kelly, John (1975). Intonation in Swahili. London: School of Oriental and African Studies. Engstrand, Olle & Lodhi, Abdulaziz Y. (1985). On aspiration in Swahili: hypotheses, field observations, and an instrumental analysis. Phonetica 42. And 3 more in the profile.

## Tamil (`ta`)

Dravidian, South Dravidian. Described: Formal Tamil as read aloud by educated speakers from Tamil Nadu (the style described by Keane 2004), with notes on colloquial speech.

**What the language has.** Vowel length for all five vowel qualities. Single versus geminate consonants (stops, nasals, laterals, glides). Dental versus retroflex stops; dental or alveolar versus retroflex nasal and lateral. Five liquids: alveolar tap /ɾ/ (ர), alveolar trill /r/ (ற, merged with the tap by many speakers), alveolar lateral /l/, retroflex lateral /ɭ/, retroflex central approximant /ɻ/ (ழ). Stop voicing is not contrastive in the native vocabulary: [p t̪ ʈ tʃ k] and [b d̪ ɖ dʒ ɡ] are positional variants; voiced stops contrast only in loanwords, mostly word-initially. Dental /n̪/ (ந) and alveolar /n/ (ன) are separate letters but are in near-complementary distribution (dental word-initially and before /t̪/, alveolar elsewhere). /f z ʂ h/ belong to the loan vocabulary (Sanskrit, Perso-Arabic, English).

Stress: no lexical stress; weak fixed prominence, not contrastive. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- ழ /ɻ/ is phoneme z., which calls the base voiced retroflex sibilant fricative [ʐ] (recordings voc/zh with zh_rfx noise) and only relabels it ɻ for IPA output, so the retroflex approximant is produced with friction.
- ர /ɾ/ imports base1/r, the English approximant [ɹ] (IPA output [mˈʌɹʌm] for மரம்), instead of an alveolar tap; only ற is a trill.
- single stops between vowels are plain voiced stops [ɡ d b]; the lenited allophones [x ɣ h], [ð], [β] are missing, most audibly for /k/.
- ன்ற is [nr] without the stop of [ndr] (என்று comes out as [enrʉ]), and ற்ற is [ʈr] with a retroflex stop instead of alveolar [tːr].
- ந and ன are both the alveolar base n; there is no dental nasal, also not before dental stops.
- non-initial /ai/ is always the full diphthong aI with length 280, never shortened or monophthongised.
- stress is put on the first syllable with stress-accent settings (amplitude and length differences, unstressed a to V, u to U), although Tamil has no stress accent.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 31 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (r=s8: f2=92 f3=77), e (e=s5: dur=53), i (i=s6: dur=56), o (o=s5: dur=53), u (u=s7: dur=57), t (t=s10: f2=91 burst=-4 vot=8), p (p=s11: vot=12), k (k=s12: vot=24), r (l=s9: tap=3 tapms=18 f2=109 f3=77), ɭ (l=s15: f2=111 f3=71), ɳ (n=s18: f3=80), b (b=s21: voi=1 lead=74), d (d=s22: f2=91 burst=-4 voi=1 lead=78), ɡ (g=s29: voi=1 lead=62), θ (f=s33: f2=146 f3=110 a6=28 ab=48), ɻ (r=s34: f3=70), ʂ (S=s35: a4=54 f2=87 f3=83 f4=88), h (<h=s17: ms=70 whisper=44), ʌ (OE=s42: f1=112 f2=87 f3=114 dur=84), iː (i=s43: dur=117), ɛ (E=s44: dur=84), aː (a=s46: dur=72), ʉ (Y=s49: f1=78), uː (u=s43: dur=117), aɪ (a=s58: g1=56 g2=146 g3=101 glide=1 dur=72), aʊ (a=s59: g1=58 g2=82 g3=93 glide=1 dur=72), ʈ (t=s63: f2=91 f3=79 f4=88 a4=52 a5=42 vot=12), ɖ (d=s64: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=75).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (என்ன, யார், எங்கே, எப்போது ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Keane, Elinor (2004). Tamil. Journal of the International Phonetic Association 34(1) (Illustrations of the IPA). Schiffman, Harold F. (1999). A Reference Grammar of Spoken Tamil. Cambridge University Press. Asher, R. E. (1985). Tamil. London: Croom Helm (Croom Helm Descriptive Grammars). Annamalai, E. and Steever, Sanford B. (1998). Modern Tamil. In Steever (ed.), The Dravidian Languages. London: Routledge. Krishnamurti, Bhadriraju (2003). The Dravidian Languages. Cambridge University Press. McDonough, Joyce and Johnson, Keith (1997). Tamil liquids: an investigation into the basis of the contrast among five liquids in a dialect of Tamil. Journal of the International Phonetic Association 27. And 8 more in the profile.

## Telugu (`te`)

Dravidian, South-Central Dravidian. Described: Modern Standard Telugu (educated speech of coastal Andhra Pradesh), formal style.

**What the language has.** Vowel length for five vowel qualities. Single versus geminate consonants, for nearly every consonant. Voiced versus voiceless stops in all vocabulary; aspirated and breathy voiced stops in the learned (Sanskrit) and loan vocabulary, giving a four-way laryngeal contrast in educated speech that colloquial speech reduces to two. Dental versus retroflex stops; alveolar versus retroflex nasal and lateral. /æː/ is marginal: it contrasts with /aː/ and /eː/ in past-tense verb forms and in English loans and has no letter of its own. Three sibilants /s ʂ ɕ/ in educated speech, merged to /s/ by many speakers.

Stress: no lexical stress; weak, not contrastive. Rhythm: mora-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- anusvara ం is always [n]: word-final -ం comes out as [n] instead of [m] (పుస్తకం gives [pustakan]) and it does not assimilate to the next stop (సంపద [sanpada], అంగడి [anɡaɖi]).
- చ and జ are always palatal [c ɟ]; the alveolar affricates [ts dz] before back vowels are produced only for the rarely written letters ౘ and ౙ.
- no /æː/; it cannot be read off the spelling and te_list has no entries for it.
- in the phoneme table short a carries the lng flag while the long vowels do not; the table is headed 'these are only guesses' and the voice is marked 'status testing'.
- stress is fixed on the first syllable with stress-accent settings.
- ర and ఱ are always the trill R2; no tap between vowels.
- only word-initial short ఎ gets a [j] on-glide; initial ఏ, ఒ and ఓ get no on-glide.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 11 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s8: tap=3 tapms=18 f2=109 f3=77), i (i=s6: dur=56), u (u=s7: dur=57), t (t=s9: f2=91 burst=-4 vot=16), k (k=s11: vot=28), b (b=s20: voi=1 lead=75), d (d=s21: f2=91 burst=-4 voi=1 lead=75), ɟ (d=s26: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s27: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s20: voi=1 lead=75), aː (a=s44: dur=72).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (ఏమిటి, ఏమి, ఎవరు, ఎక్కడ ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Bhaskararao, Peri and Ray, Arpita (2017). Telugu. Journal of the International Phonetic Association 47(2) (Illustrations of the IPA). Krishnamurti, Bh. and Gwynn, J. P. L. (1985). A Grammar of Modern Telugu. Delhi: Oxford University Press. Krishnamurti, Bh. (1998). Telugu. In Steever (ed.), The Dravidian Languages. London: Routledge. Krishnamurti, Bhadriraju (2003). The Dravidian Languages. Cambridge University Press. Kostić, Djordje; Mitter, Alokananda; Krishnamurti, Bh. (1977). A Short Outline of Telugu Phonetics. Calcutta: Indian Statistical Institute. Abercrombie, David (1967). Elements of General Phonetics. Edinburgh University Press. And 1 more in the profile.

## Thai (`th`)

Kra-Dai (Tai-Kadai), Tai, Southwestern Tai. Described: Standard Thai (Central Thai of Bangkok).

**What the language has.** Three-way laryngeal contrast in labial and alveolar stops: voiced b d, voiceless unaspirated p t, voiceless aspirated pʰ tʰ; two-way in velars (k kʰ) and affricates (tɕ tɕʰ). Vowel length in all nine vowel qualities. Five tones in live syllables, three in dead syllables. Back unrounded ɯ ɤ against back rounded u o. Final nasals m n ŋ, final unreleased stops p t k and glottal stop, final glides j w.

Stress: fixed, final. Rhythm: stress-timed. Tone: lexical tone, 5 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- the Thai phoneme table is declared in phsource/phonemes as 'phonemetable th shn' with no file of its own, so Thai uses the Shan table unchanged: six Shan tones (24, 11, 32, 55, 42, 343) instead of the five Thai tones, and no long vowels except a.
- Thai is not flagged as a tone language in src/libespeak-ng/tr_languages.c (the th case only disables numbers), so CalcPitches_Tone() is not used and tone phonemes do not set pitch levels; pitch comes from the default stress-based intonation.
- dictsource/th_rules is a letter-by-letter placeholder: each consonant letter gives a consonant, a tone digit fixed by consonant class (3 for mid class, 55 for high class, 2 for low class) and an inherent a; there is no syllable parsing, no live or dead syllable tone rule, no vowel length and no neutralisation of final consonants.
- the four tone marks (mai ek, mai tho, mai tri, mai chattawa) have no rules, and the tokenizer ends the word at them.
- several vowel signs are mapped to consonants: sara aa, sara am and sara ii give s, mai han-akat and mai yamok give m; สวัสดี comes out as [sawmsads], มา as [mas], ดี as [ds].
- the rules write aspirates as kh, ph, th, ch, which are read as a stop plus h and not as the aspirated phonemes k_h, p_h, t_h of the inherited table.
- numbers are disabled in tr_languages.c although th_list has the digits, and there is no word segmentation for unspaced Thai text.
- the result is not intelligible as Thai.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 4 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɹ (l=s7: f3=66), a (a=s4: dur=76), h (<h=s10: ms=70 whisper=44), ɡ (g=s21: voi=1 lead=75).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
Timing: stressed 112 per cent, weak 85 per cent, last 118 per cent of the module's own.

**Not yet.** eSpeak NG reads Thai without tones, and its Thai voice is a beginning: the language is not yet intelligible.

Sources: Tingsabadh, M. R. Kalaya & Abramson, Arthur S. (1993). Thai. Journal of the International Phonetic Association 23(1), 24-28. Abramson, Arthur S. (1962). The Vowels and Tones of Standard Thai: Acoustical Measurements and Experiments. Indiana University Research Center in Anthropology, Folklore and Linguistics, Publication 20. Abramson, Arthur S. (1979). The coarticulation of tones: an acoustic study of Thai. In Studies in Tai and Mon-Khmer Phonetics and Phonology in Honour of Eugénie J. A. Henderson. Chulalongkorn University Press. Gandour, Jack, Potisuk, Siripong & Dechongkit, Sumalee (1994). Tonal coarticulation in Thai. Journal of Phonetics 22, 477-492. Potisuk, Siripong, Gandour, Jack & Harper, Mary P. (1996). Acoustic correlates of stress in Thai. Phonetica 53, 200-220. Morén, Bruce & Zsiga, Elizabeth (2006). The lexical and post-lexical phonology of Thai tones. Natural Language and Linguistic Theory 24, 113-178. And 7 more in the profile.

## Tigrinya (`ti`)

Afro-Asiatic, Semitic, South Semitic (Ethiosemitic), North Ethiopic. Described: Tigrinya of Eritrea and Tigray in its written standard form (central, Asmara-type pronunciation).

**What the language has.** Three-way laryngeal contrast in stops and affricates: voiceless, voiced, ejective. Ejective fricative /sʼ/ against /s/ and /z/. Pharyngeal /ħ ʕ/ against glottal /h ʔ/. Consonant gemination, lexical and grammatical, not shown in the script. Labialised against plain velars. Seven vowels; the first-order vowel, written ä and given here as /ɐ/, is also transcribed /ə/. /p/ and /v/ occur in loanwords only, /pʼ/ is rare.

Stress: weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- The pharyngeal /ħ/ (ሐ series) is sent to the phoneme X, the uvular fricative [χ]; the ti table has no pharyngeal ħ although the Arabic table has one. ሓደ gives [χadə].
- The spirantised ejective (ቐ series, [xʼ]~[χʼ]) is the plain uvular stop q: ቐይሕ gives [qəjɨx].
- ጸ and ፀ are the plain affricate [ts], not the ejective /sʼ/ [tsʼ].
- Gemination is never produced (the script does not write it): ትግርኛ has a single [ɲ].
- Every sixth-order letter inside a word is given the vowel ɨ: ትግርኛ gives [tɨɡɨrɨɲa] for [tɨɡrɨɲɲa], ክልተ gives [kɨlɨtə] for [kɨltə].
- No stress rule is set for ti, so the default penultimate stress applies and often lands on an inserted ɨ (kɨlˈɨtə).
- Only k` uses an ejective recording; p`, t` and tS` use unaspirated plosive samples after a pause.
- The rules were copied from Amharic (the headers of ti_rules and ti_list still say Amharic) and the first-order vowel is the Amharic schwa.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 26 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), ʔ (<q=s4: ms=50 hush=1), r (l=s9: tap=3 tapms=18 f2=109 f3=77), a (A=s5: dur=175), e (e=s6: dur=80), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s10: vot=17), p (p=s11: vot=13), k (k=s12: vot=28), h (<h=s17: ms=70 whisper=44), ɲ (n=s19: f2=136 f3=109), b (b=s21: voi=1 lead=75), d (d=s21: voi=1 lead=75), ɡ (g=s21: voi=1 lead=75), β (v=s30: af=-8), θ (f=s33: f2=146 f3=110 a6=28 ab=48), q (k=s40: f2=68 f3=109 f1=118 burst=3 vot=30), χ (x=s3: f2=88), ɨ (Y=s42: f1=78 f2=106 f3=114 dur=137), p` (p=s11: vot=13), t` (t=s10: vot=17), k` (k=s12: vot=28), ʕ (<h=s43: ms=80 whisper=30 voi=1 f1=125 f2=86).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (መን, እንታይ, ኣበይ, መዓስ ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Kogan, Leonid E. (1997). Tigrinya. In Robert Hetzron (ed.), The Semitic Languages. London: Routledge. Leslau, Wolf (1941). Documents tigrigna (éthiopien septentrional): grammaire et textes. Paris: Klincksieck. Shosted, Ryan K. & Rose, Sharon (2011). Affricating ejective fricatives: the case of Tigrinya. Journal of the International Phonetic Association 41(1): 41-65. Kingston, John (1985). The phonetics and phonology of the timing of oral and glottal events. PhD dissertation, University of California, Berkeley. Fre Woldu, Kiros (1985). The perception and production of Tigrinya stops. Uppsala University. Buckley, Eugene (1994). Tigrinya vowel features and vowel coalescence. University of Pennsylvania Working Papers in Linguistics 1. And 1 more in the profile.

## Turkmen (`tk`)

Turkic, Oghuz. Described: Standard Turkmen (based on the Teke dialect), Latin script.

**What the language has.** Phonemic vowel length, inherited from Proto-Turkic and not written: at [ɑt] 'horse' versus at [ɑːt] 'name', ot [ot] 'grass' versus ot [oːt] 'fire'. Dental fricatives /θ ð/ (spelt s, z) where other Turkic languages have /s z/. Front versus back and rounded versus unrounded vowels. Voiced versus voiceless stops and affricates. Short /e/ pairs with long /æː/ (spelt ä); long /eː/ and short /æ/ are marginal.

Stress: fixed final by default. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no stress rule is set for tk, so the default penultimate stress applies (kitap, sagat, dogan are stressed on the first syllable); Turkmen stress is final, and only a few suffix rules mark it.
- vowel length is not written, and eSpeak gets it only from a list of about 870 respelt word forms (tk_listx): forms not listed lose the long vowel (kitap has [ɑː], kitaplar does not) and homographs such as at 'horse' and at 'name' cannot be told apart.
- word-initial b is turned into [β] after any preceding word and into [m] after a word ending in a nasal, whatever the phrasing (sen biz gives [θen mið]).
- the ipa string of the long vowel ɯː has no length mark (affects --ipa output only).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 5 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: i (i=s6: dur=56), t (t=s10: f2=91 burst=-4), r (l=s9: tap=3 tapms=18 f2=109 f3=77), ø (oe=s5: dur=53), œ (OE=s36: dur=84).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (näme, kim, nirede, nirä ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Clark, Larry (1998). Turkmen Reference Grammar. Harrassowitz. Hoey, Elliott Michael (2013). Grammatical Sketch of Turkmen. MA thesis, University of California, Santa Barbara. Schönig, Claus (1998). Turkmen. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge.

## Setswana (`tn`)

Niger-Congo, Atlantic-Congo, Bantu (Sotho-Tswana group, Guthrie S.31). Described: Setswana as described for South African speakers from Taung and Kuruman (Bennett et al. 2016), with reference to the Botswana standard (Cole 1955; University of Botswana 2001).

**What the language has.** Seven vowel qualities in four heights; the letters e and o each spell two phonemes (ɪ and ɛ, ʊ and ɔ). Unaspirated (variably ejective) versus aspirated voiceless stops and affricates: p pʰ, t tʰ, k kʰ, ts tsʰ, tʃ tʃʰ, tɬ tɬʰ. Lateral affricates tɬ and tɬʰ (written tl, tlh). Uvular fricative χ (written g) and uvular affricate qχ (written kg); there is no voiced velar stop. Single versus doubled sonorants: mona 'jealousy' versus monna 'man'. High versus low tone, both lexical and grammatical.

Stress: fixed penultimate prominence, realised as lengthening. Rhythm: syllable-timed. Tone: lexical tone, 2 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- no tone at all: the phoneme table has no tone phonemes and the dictionary carries no tone marks, so lexical and grammatical high and low tones are lost.
- unstressed e is changed to the consonant l (ChangeIfUnstressed(l) in phoneme e, apparently a slip for a vowel): bogobe comes out as [βʊɡoβl], lefatshe as [llfatʃl].
- g, which spells the fricative /χ/, is pronounced as the voiced stop [ɡ]; kg, which spells /qχ/, is pronounced [kɡ].
- th and kh are read as the fricatives [θ] and [x], as in the Swahili rules the file was copied from, instead of aspirated /tʰ/ and /kʰ/.
- tsh is read as [tʃ] instead of /tsʰ/; š is read as [s].
- tl is read as the fricative [ɬ] instead of the affricate /tɬ/.
- ng is read as [ŋɡ], also word-finally (jang) and before w (ngwana), where Setswana has [ŋ].
- the seven-vowel system is not represented: e and o are given one quality each, with o becoming [ʊ] when unstressed, regardless of the lexical vowel.

**What OpenEVV says.** Spoken by the module made from Castilian Spanish (`esex`). 10 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: a (a=s4: dur=127), e (e=s5: dur=141), i (i=s6: dur=161), o (o=s7: dur=146), u (u=s8: dur=170), d (d=s15: voi=1 lead=75), ɡ (g=s15: voi=1 lead=75), ɬ (l=s30: fric=52 a3=54 a4=58 a5=44 whisper=30), ʊ (o=s36: f1=87 f2=111 f3=94 dur=146), K (l=s30: fric=52 a3=54 a4=58 a5=44 whisper=30).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (mang, eng, kae, leng ...) ends as a statement does, from a high question word.
Timing: last 118 per cent of the module's own.

**Not yet.** Tone is not in eSpeak NG's reading.

Sources: Bennett, Wm. G., Diemer, Maxine, Kerford, Justine, Probert, Tracy & Wesi, Tsholofelo (2016). Setswana (South African). Journal of the International Phonetic Association 46(2), 235-246. Cole, Desmond T. (1955). An Introduction to Tswana Grammar. London: Longmans, Green. Chebanne, Andy, Creissels, Denis & Nkhwa, H. W. (1997). Tonal Morphology of the Setswana Verb. München: LINCOM Europa. University of Botswana (2001). The Sound System of Setswana. Gaborone: Lightbooks. Le Roux, Mia & Le Roux, Jurie (2008). An acoustic assessment of Setswana vowels. South African Journal of African Languages 28, 156-171. Gouskova, Maria, Zsiga, Elizabeth & Tlale Boyer, One (2011). Grounded constraints and the consonants of Setswana. Lingua 121, 2120-2152. And 4 more in the profile.

## Turkish (`tr`)

Turkic, Oghuz. Described: Standard Turkish (Istanbul).

**What the language has.** Eight vowel qualities built on three binary oppositions: high versus non-high, front versus back, rounded versus unrounded (i y ɯ u, e ø a o). Voiced versus voiceless aspirated stops and affricates. Palatal versus velar stops (c ɟ versus k ɡ) and clear versus dark laterals (l versus ɫ), contrastive only next to back vowels in loanwords (kâr versus kar, hâlâ versus hala). Vowel length, marginal: long vowels in Arabic and Persian loanwords and from lost ğ (dağ). Consonant gemination (eli 'his hand' versus elli 'fifty').

Stress: fixed final by default with lexical and morphological exceptions; realised as a pitch accent. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- p t k come from the base2 table and use unaspirated samples; Turkish voiceless stops are aspirated (VOT about 40-70 ms).
- long vowels of loanwords are not produced: â î û are mapped to plain short a i u (hâlâ gives [hala]) and unmarked long vowels (memur, şair) have no dictionary entries.
- k is not palatalised before â (kâr gives [kar], expected [caɾ]) and has no palatal allophone rule before front vowels, although g becomes [ɟ] there; only the burst sample changes before i.
- non-final stress is only known for the roughly 150 entries of tr_listx (mostly place names): gazete, lokanta, şimdi, sonra, ancak get final stress.
- /ɾ/ is a trill except between vowels; the literature describes a tap everywhere, devoiced word-finally.
- lowering of i y u e ø to [ɪ ʏ ʊ ɛ œ] is applied in the last syllable of every word and before consonant clusters, wider than the phrase-final open syllable context described by Zimmer & Orgun.
- the ɯ target (F1 448, F2 1280 Hz) is lower and further back than measured values (about 400 and 1500 Hz).
- no weakening of /v/ to [ʋ] and no loss of intervocalic /h/.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 21 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɯ (Y=s1: f3=115), ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), a (A=s5: f1=80 f2=88), e (e=s6: f1=124 f2=85 dur=53), i (i=s7: f1=113 dur=56), o (o=s8: f1=121 f2=114 f3=111 dur=53), u (u=s9: f1=148 f2=128 dur=57), t (t=s12: f2=91 burst=-4 vot=50 asp=50), p (p=s13: vot=41 asp=50), r (l=s11: tap=3 tapms=18 f2=109 f3=77), ɫ (l=s17: f2=71 f3=91), h (<h=s18: ms=70 whisper=44), b (b=s22: voi=1 lead=66), d (d=s23: f2=91 burst=-4 voi=1 lead=53), ɟ (d=s28: f2=135 f3=112 a3=56 a4=56), ɛ (E=s42: dur=84), ɔ (O=s43: dur=85), y (y=s45: dur=56), ø (oe=s46: f1=120 f3=118 dur=53), æ (E=s54: f1=124 f2=92 f3=92 dur=84), œ (OE=s42: dur=84).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (ne, kim, nerede, nereye ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Zimmer, Karl & Orgun, Orhan (1999). Turkish. Handbook of the International Phonetic Association, Cambridge University Press. Göksel, Aslı & Kerslake, Celia (2005). Turkish: A Comprehensive Grammar. Routledge. Öğüt, Fatih; Kılıç, Mehmet Akif; Engin, Erkan Zeki & Midilli, Rasim (2006). Voice onset times for Turkish stop consonants. Speech Communication 48(9), 1094-1099. Malkoç, Ekrem (2009). Türkçe ünlü formant frekans değerleri ve bu değerlere dayalı ünlü dörtgeni. Dil Dergisi 146, 71-85. Kılıç, Mehmet Akif & Öğüt, Fatih (2004). A high unrounded vowel in Turkish: is it a central or back vowel? Speech Communication 43. Levi, Susannah V. (2005). Acoustic correlates of lexical accent in Turkish. Journal of the International Phonetic Association 35(1), 73-97. And 3 more in the profile.

## Tatar (`tt`)

Turkic, Kipchak (Volga Kipchak). Described: Literary Tatar, based on the Central (Kazan) dialect, Cyrillic script.

**What the language has.** Full vowels /i y u æ ɑ/ versus reduced (short, lax, centralised) mid vowels /ĕ ø̆ ŏ ɤ̆/, spelt е/э, ө, о, ы; the Volga vowel shift raised the old mid vowels and reduced the old high vowels. Front versus back and rounded versus unrounded vowels. Velar /k ɡ/ versus uvular /q ʁ/, predictable from vowel backness in native words but contrastive in Arabic and Persian loans. Alveolo-palatal fricatives /ɕ ʑ/ (spelt ч, җ) where most Turkic languages have affricates. Voiced versus voiceless obstruents.

Stress: fixed final by default, with morphological and lexical exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- г next to front vowels becomes the velar fricative [ɣ] (the phoneme g is changed to Q), so гөл gives [ɣøl]; Tatar has the stop [ɡ] there and a fricative only in back-vowel words.
- ь and ъ are always read as a glottal stop (сәгать gives [sæʁɑtʔ]); in Tatar they are silent markers, and [ʔ] occurs only in a few Arabic loans.
- the unwritten rounding harmony of the reduced vowels is not applied (борын gives [borɯn]).
- stress is always final: unstressable suffixes, imperatives and question words are not handled (барма gives final stress).
- Russian loanwords are read by the native rules: в is always [w], о and е are the reduced vowels, stress is final.
- t is the unaspirated base2 stop while p and k are the aspirated base1 stops.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 17 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: r (l=s9: tap=3 tapms=18 f2=109 f3=77), e (e=s6: dur=80), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), ɫ (l=s13: f2=71 f3=91), h (<h=s14: ms=70 whisper=44), ʑ (Z=s30: a3=34 a4=55 a5=22 f2=126 f3=121), ɕ (S=s31: a2=31 a3=34 a4=34 a5=22 f2=119 f3=116), ɣ (r=s33: f1=73 f3=116), q (k=s34: f2=68 f3=109 f1=118 burst=3), y (y=s7: dur=85), œ (OE=s36: dur=126), ɯ (Y=s37: f1=83 f2=89 f3=114 dur=137), æ (E=s38: f1=124 f2=92 f3=92 dur=126), ɑ (A=s39: f1=91 f2=86 dur=175), ɒ (O=s40: f1=116 dur=150).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (нәрсә, ни, кем, кайда ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Poppe, Nicholas (1963). Tatar Manual. Indiana University. Berta, Árpád (1998). Tatar and Bashkir. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge. Comrie, Bernard (1997). Tatar (Volga Tatar, Kazan Tatar) phonology. In Alan S. Kaye (ed.), Phonologies of Asia and Africa. Eisenbrauns.

## Uyghur (`ug`)

Turkic, Karluk. Described: Standard Uyghur of Xinjiang (Central dialect: Ürümchi, Ghulja), Arabic script; Latin script (ULY) also in use.

**What the language has.** Eight vowels: /i/ without a back partner (older /i/ and /ɯ/ have merged), /y u/, /e/, /ø o/, /æ ɑ/. Voiced versus voiceless aspirated stops and affricates. Velar /k ɡ/ versus uvular /q ʁ χ/. Stress can distinguish words (a stem plus an unstressable suffix against a plain stem). Vowel length is not written: long vowels come from loanwords and from the loss of coda /r/ and other consonants.

Stress: final by default, with morphological exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- no stress rule is set for ug, so the default penultimate stress applies (bala, kitab, uyghur are stressed on the first syllable); Uyghur stress is final by default.
- p t k are inherited from the Turkish table and are unaspirated; Uyghur voiceless stops are aspirated.
- i is always one short centralised vowel (length 100, F2 about 1660 Hz): no [i] versus [ɨ ~ ɯ] variants and no devoicing between voiceless consonants.
- no long vowels, and coda r is always a full trill.
- k and q stay stops before consonants, and voiced stops are not devoiced at the end of a syllable.
- unstressable suffixes and particles are not handled.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 11 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: e (e=s5: dur=53), o (o=s5: dur=53), u (u=s7: dur=57), r (l=s9: tap=3 tapms=18 f2=109 f3=77), h (<h=s14: ms=70 whisper=44), q (k=s34: f2=68 f3=109 f1=118 burst=3), χ (x=s3: f2=88), y (y=s6: dur=56), æ (E=s46: f1=124 f2=92 f3=92 dur=84), œ (OE=s36: dur=84), ɑ (A=s47: f1=91 f2=86).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
A question asked with a question word (نېمە, كىم, قەيەردە, قاچان ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Hahn, Reinhard F. (1991). Spoken Uyghur. University of Washington Press. Hahn, Reinhard F. (1998). Uyghur. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge. Engesæth, Tarjei; Yakup, Mahire & Dwyer, Arienne (2009). Teklimakandin Salam / Greetings from the Teklimakan: A Handbook of Modern Uyghur. University of Kansas. Yakup, Mahire & Sereno, Joan A. (2016). Acoustic correlates of lexical stress in Uyghur. Journal of the International Phonetic Association 46(1), 61-77.

## Ukrainian (`uk`)

Indo-European, Balto-Slavic, Slavic, East Slavic. Described: Standard Ukrainian (literary norm based on the central Dnieper dialects, as spoken in Kyiv).

**What the language has.** Palatalised versus plain consonants in the dental and alveolar series only (/t d s z t͡s d͡z n l r/); labials, velars and postalveolars have no soft phonemes, only slightly palatalised allophones before /i/. /i/ versus /ɪ/ (ліс [lʲis] 'forest' vs лис [lɪs] 'fox'). Voiced glottal fricative /ɦ/ versus velar stop /ɡ/ (rare) versus voiceless /x/. Long (geminate) consonants, mostly soft dentals between vowels (життя [ʒɪˈtʲːɑ], знання [znɑˈnʲːɑ]). Voiced versus voiceless obstruents, kept word-finally (дуб [dub]). Position of stress is lexically contrastive (замок: [ˈzɑmɔk] 'castle' vs [zɑˈmɔk] 'lock').

Stress: free (lexical), mobile. Rhythm: mixed.

**What eSpeak NG reads otherwise than the literature has it.**

- Stress: there is no stress dictionary (uk_list has about 225 lines, mostly symbols and numbers) and the position is guessed from the number of syllables by the routine written for Russian, so many common words are wrong: вода, село, весна get initial stress, молоко and голова get stress on the second syllable (all have final stress).
- в is always a bilabial fricative [β] (phoneme B) and is devoiced to [f] before voiceless consonants (вовк [βofk], вчора [ftʃora]); the glide [u̯] after vowels and initial [w] are missing.
- The Russian setting for regressive voicing is used, so voiced obstruents are devoiced before voiceless ones (казка [kaska]), which standard Ukrainian does not do; легко keeps [h] instead of [x]; voicing before a voiced obstruent fails across a soft sign (боротьба [borotba], просьба [prosba]).
- Palatalisation exists only for л and н (as palatal [ʎ ɲ]) and for сь, ць before vowels: д, т, з, с before і stay hard (діти, тінь, сіль), я ю є after д т з с ц р are read as [j] plus vowel (дякую [djakuju], рясно [rjasno], щастя [ʃtʃastja]) and final ть is hard (п'ять [pjat]).
- Long soft consonants are read as hard geminate plus [j] (життя [ʒɪttja]).
- і and ї are always long [iː]; Ukrainian has no vowel length.
- г is the voiceless [h], not voiced [ɦ].
- No raising of unstressed о before high vowels and no partial merger of unstressed е and и (minor).

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 23 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), a (A=s5: dur=175), e (e=s6: dur=80), i (i=s7: dur=85), o (o=s6: dur=80), u (u=s8: dur=86), t (t=s11: vot=17), p (p=s12: vot=13), k (k=s13: vot=28), r (l=s10: tap=3 tapms=18 f2=109 f3=77), ʎ (l=s15: f2=159), h (<h=s18: ms=70 whisper=44), ɲ (n=s20: f2=136 f3=109), b (b=s22: voi=1 lead=75), d (d=s22: voi=1 lead=75), d̪ (d=s23: f2=91 burst=-4 voi=1 lead=75), t̪ (t=s24: f2=91 burst=-4 vot=16), ɡ (g=s22: voi=1 lead=75), β (v=s31: af=-8), ɬ (l=s42: fric=52 a3=54 a4=58 a5=44 whisper=30), ɛ (E=s43: dur=126), ɪ (I=s44: dur=137).

Melody: the pitch rises through the stressed syllable to a peak at its end. A question that wants yes or no rises to the syllable before the last and falls on the last.
A question asked with a question word (хто, що, де, коли ...) ends as a statement does, from a high question word.
Timing: stressed 94 per cent, weak 106 per cent of the module's own.

Sources: Pompino-Marschall, Bernd; Steriopolo, Elena & Żygis, Marzena (2017). Ukrainian. Journal of the International Phonetic Association 47(3), 349-357. Shevelov, George Y. (1993). Ukrainian. In B. Comrie & G. G. Corbett (eds.), The Slavonic Languages. London: Routledge. Shevelov, George Y. (1979). A Historical Phonology of the Ukrainian Language. Heidelberg: Carl Winter. Zilynskyj, Ivan (1979). A Phonetic Description of the Ukrainian Language. Cambridge, MA: Harvard Ukrainian Research Institute. Danyenko, Andrii & Vakulenko, Serhii (1995). Ukrainian. München: Lincom Europa. Pugh, Stefan M. & Press, Ian (1999). Ukrainian: A Comprehensive Grammar. London: Routledge. And 1 more in the profile.

## Urdu (`ur`)

Indo-European, Indo-Iranian, Indo-Aryan (Central zone, Hindustani). Described: Standard Urdu, educated speech (Delhi-Lucknow norm as used in Pakistan and India); formant and duration figures come from Lahore speakers.

**What the language has.** Four-way laryngeal contrast in stops and affricates: voiceless unaspirated, voiceless aspirated, voiced, breathy voiced. Dental versus retroflex stops. Retroflex flaps /ɽ ɽʱ/ versus the tap /ɾ/ and versus retroflex stops. Phonemic vowel nasalisation. Three short lax vowels /ɪ ə ʊ/ against seven long peripheral vowels; length goes together with quality. Consonant gemination (written with tashdid, which is usually left out). Perso-Arabic consonants /q x ɣ z f ʒ/ are part of the educated norm: /q/ : /k/, /x/ : /kʰ/, /ɣ/ : /ɡ/, /z/ : /dʒ/.

Stress: weight-sensitive, weak, not contrastive. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- Breathy voiced stops are a modal voiced closure plus an added voiceless aspiration sample (inherited from the Hindi base table); no breathy voice on the vowel. IPA output writes ʰ for ʱ.
- /ɦ/ is voiceless [h].
- The script leaves short vowels out and eSpeak guesses them: عورت gives [aoːrət] for [ɔːrət̪], and the long vowel letters are always read as eː, oː, never ɛː, ɔː (بیٹھنا [beːʈʰnaː], چودہ [coːda]).
- Nasalised vowels inside a word are written with the letter nun and are read as vowel plus [n]: چاند [caːnd], آنکھ [aːnkʰ]; also word-final in نہیں [nahiːn].
- /ɽʱ/ is produced as flap + [h] + schwa: پڑھنا gives [pʌɽhənaː].
- /r/ is always the trill [R], where the Hindi voice uses a tap.
- Two different short central vowels are used for the same phoneme /ə/ ([a] from the zabar rules, [ʌ] or [ə] from the inherent-vowel rules): کرنا [karnaː] but پھل [pʰʌl].
- Final choti he is a short [a] (کمرہ [kamra]) where speakers have a long vowel.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 42 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: f1=136 f2=81), tʰ (t=s5: f2=91 burst=-4 vot=67 asp=50), a (A=s6: f1=89 f2=89), i (i=s8: dur=56), t (t=s12: f2=91 burst=-4 vot=15), p (p=s13: vot=13), k (k=s14: vot=18), r (l=s11: tap=3 tapms=18 f2=109 f3=77), r. (l=s22: tap=1 tapms=24 hold=60 f2=111 f3=66), b (b=s23: voi=1 lead=85), d (d=s24: f2=91 burst=-4 voi=1 lead=87), ɟ (d=s29: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), ɡ (g=s31: voi=1 lead=63), ʋ (v=s33: af=-14), ð (v=s34: f2=149 f3=110 a6=28 ab=48), ʐ (Z=s36: a4=51 f2=92 f3=87 f4=88), ʂ (S=s37: a4=54 f2=87 f3=83 f4=88), ɣ (r=s41: f1=73 f3=116), q (k=s42: f2=68 f3=109 f1=118 burst=3 vot=30), h (<h=s19: ms=70 whisper=44), ʌ (OE=s44: f1=112 f2=87 f3=114 dur=84), iː (i=s45: dur=117), ɪ (I=s46: f3=90), ɛː (E:=s47: f1=116 f2=90), ɛ (E=s48: dur=84), aː (a=s50: f1=87 f2=89 dur=72), oː (o=s51: f2=113), ɔ (O=s53: dur=85), ʊ (U=s54: dur=114), uː (u=s55: f1=134 dur=117), ĩ (i=s56: dur=56 nas=100), ẽ (e=s58: dur=53 nas=100), bʰ (b=s69: voi=1 lead=61 brth=90 f0=-15), dʰ (d=s70: f2=91 burst=-4 voi=1 lead=87 brth=90 f0=-15), ʈ (t=s71: f2=91 f3=79 f4=88 a4=52 a5=42 vot=9), ɖ (d=s72: f2=91 f3=79 f4=88 a4=52 a5=42 voi=1 lead=76), ʈʰ (t=s73: f2=91 f3=79 f4=88 a4=52 a5=42 vot=60 asp=50), cʰ (t=s75: f2=135 f3=112 a3=56 a4=56 vot=75 asp=50), ɟʰ (d=s76: f2=135 f3=112 a3=56 a4=56 voi=1 lead=75 brth=90 f0=-15), kʰ (k=s77: vot=92 asp=50), ɡʰ (g=s78: voi=1 lead=75 brth=90 f0=-15).

Melody: the stressed syllable is low and the rise comes after it. A question that wants yes or no rises at the end.
A question asked with a question word (کیا, کون, کہاں, کب ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Schmidt, Ruth Laila (1999). Urdu: An Essential Grammar. London: Routledge. Schmidt, Ruth Laila (2003). Urdu. In Cardona, George & Jain, Dhanesh (eds.), The Indo-Aryan Languages. London: Routledge. Kachru, Yamuna (1990). Hindi-Urdu. In Comrie, Bernard (ed.), The World's Major Languages. Oxford University Press. Ohala, Manjari (1999). Hindi. In Handbook of the International Phonetic Association, Cambridge University Press, 100-103 (same sound system). Masica, Colin P. (1991). The Indo-Aryan Languages. Cambridge University Press. Hussain, Sarmad (1997). Phonetic Correlates of Lexical Stress in Urdu. PhD dissertation, Northwestern University. And 7 more in the profile.

## Uzbek (`uz`)

Turkic, Karluk. Described: Standard Uzbek of Uzbekistan, based on the Tashkent dialect; Latin script (Cyrillic also in use).

**What the language has.** Six vowels, without front rounded vowels and without front-back pairs: /i e a/ and /u o ɔ/, spelt i e a and u oʻ o. Voiced versus voiceless aspirated plosives. Velar /k ɡ/ versus uvular /q ʁ χ/, not predictable from the vowels. /χ/ versus /h/ in careful standard speech (merged in traditional Tashkent speech). Vowel length only in loanwords (maʼno, maʼqul).

Stress: fixed final by default, with morphological and lexical exceptions. Rhythm: syllable-timed.

**What eSpeak NG reads otherwise than the literature has it.**

- the letter i is mapped to the phoneme y, imported from base2 as the front rounded vowel [y] (F2 about 1720 Hz), so every i sounds like ü (kitob gives [kytɑb], qiz gives [qyz]).
- no stress rule is set for uz, so the default penultimate stress applies (bola, kitob, vatan are stressed on the first syllable); Uzbek stress is final.
- numbers are switched off in the language options, so digits are read one by one.
- the tutuq belgisi ʼ (U+02BC, also produced from Cyrillic ь and ъ) has no rule: a word such as maʼno is spelt out letter by letter.
- the rule for f gives 'f,' and so puts a secondary stress mark on the following vowel (fasl).
- no centralised or devoiced variants of /i/ and /u/, no palatalisation of /k ɡ/, no lengthened vowels in loans.
- t is the unaspirated base2 stop while p and k use aspirated samples.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 12 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ɾ (l=s2: tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77), e (e=s6: dur=80), o (o=s8: f2=114 f3=116 dur=80), ɫ (l=s14: f2=71 f3=91), h (<h=s15: ms=70 whisper=44), ʋ (v=s26: af=-14), q (k=s35: f2=68 f3=109 f1=118 burst=3), χ (x=s3: f2=88), ʊ (U=s39: dur=185), ɑ (A=s40: f1=91 f2=86 dur=175), æ (E=s41: f1=124 f2=92 f3=92 dur=126), y (y=s7: dur=85).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no is said higher as a whole, with little or no rise at the end.
A question asked with a question word (nima, kim, qayerda, qayerga ...) ends as a statement does, from a high question word.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Ido, Shinji (2025). Uzbek. Journal of the International Phonetic Association 55(1-2), 152-168. Sjoberg, Andrée F. (1963). Uzbek Structural Grammar. Indiana University. Bodrogligeti, András J. E. (2003). An Academic Reference Grammar of Modern Literary Uzbek. Lincom Europa. Boeschoten, Hendrik (1998). Uzbek. In Lars Johanson & Éva Á. Csató (eds.), The Turkic Languages. Routledge.

## Vietnamese (Northern) (`vi`)

Austroasiatic, Vietic. Described: Northern Vietnamese, Hanoi.

**What the language has.** Six tones that differ in pitch contour and in voice quality. Implosive ɓ ɗ against voiceless unaspirated t, k and aspirated tʰ; there is no aspirated labial or velar stop (f and x fill those places). Long against short in two vowel pairs, a against ă and ɤ against ɤ̆, in closed syllables only. Back unrounded ɯ ɤ against back rounded u o. Final stops p t k against final nasals m n ŋ. Three centring diphthongs iə ɯə uə.

Stress: none (no lexical stress); phrase-level prominence. Rhythm: syllable-timed. Tone: lexical tone, 6 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c ignores the clause type, and a question gives the same audio as a statement; the only clause-level change is that an unmarked (ngang) last syllable is given tone 7, a slightly higher level.
- voice quality is not modelled: huyền is not breathy, and the glottalisation of ngã and nặng is imitated only by a dip in amplitude (envelopes vi_5amp and vi_6amp) while voicing continues.
- nặng is not short: its length reduction is commented out in ph_vietnam, and mạ lasts as long as mả and mã (about 340 ms measured).
- hỏi always has the full fall and rise, also inside a phrase, where the natural form is a low fall without the rise.
- ɓ is spoken with the plain voiced b of the base table, with a short pause before it at the start of a word, not as an implosive; ɗ has its own recording.
- no tonal coarticulation, and the voice attribute 'words 1 2' puts a pause between all words, so speech is staccato.
- sắc and nặng in stop-final syllables use the same pitch contours as in open syllables; only the vowel is shorter.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 19 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=140), a (A=s5: dur=150), e (e=s6: dur=70), i (i=s7: dur=75), o (o=s6: dur=70), k (k=s13: vot=28), h (<h=s18: ms=70 whisper=44), ɲ (n=s20: f2=136 f3=109), b (b=s22: voi=1 lead=75), t̪ (t=s24: f2=91 burst=-4 vot=16), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), e- (e=s6: dur=70), ɔ (O=s43: dur=127), y (y=s7: dur=75), əː (@=s45: dur=263), yə (j=s56 @=s1: f1=56 f2=111 f3=84 hold=55; dur=140), iɛ (j=s54 E: hold=55), ɗ (d=s66: voi=1 lead=75 impl=1 burst=-8).

Tones: 1 (0:33,100:32), 7 (0:33,100:26), 2 (0:22,100:11), 3 (0:32,35:32,100:50), 4 (0:30,50:11,100:30), 5 (0:32,40:26,60:30,100:52), 6 (0:30,100:12). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Kirby, James P. (2011). Vietnamese (Hanoi Vietnamese). Journal of the International Phonetic Association 41(3), 381-392. Thompson, Laurence C. (1965). A Vietnamese Grammar. University of Washington Press. Nguyễn, Văn Lợi & Edmondson, Jerold A. (1998). Tones and voice quality in modern northern Vietnamese: instrumental case studies. Mon-Khmer Studies 28, 1-18. Michaud, Alexis (2004). Final consonants and glottalization: new perspectives from Hanoi Vietnamese. Phonetica 61, 119-146. Pham, Andrea Hoa (2003). Vietnamese Tone: A New Analysis. Routledge. Brunelle, Marc (2009). Tone perception in Northern and Southern Vietnamese. Journal of Phonetics 37, 79-96. And 5 more in the profile.

## Vietnamese (Central) (`vi-vn-x-central`)

Austroasiatic, Vietic. Described: Central Vietnamese, Huế.

**What the language has.** Five tones: hỏi and ngã are one tone. Retroflex ʈ ʂ ʐ (written tr, s, r) against palatal c, alveolar s and the glide j (written ch, x, d or gi); Hanoi has lost these contrasts. Implosive ɓ ɗ against voiceless unaspirated t, k and aspirated tʰ. Long against short a and ɤ in closed syllables. Final alveolars and velars are merged: written n and t are said as ŋ and k after most vowels.

Stress: none (no lexical stress); phrase-level prominence. Rhythm: syllable-timed. Tone: lexical tone, 5 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c ignores the clause type, and a question gives the same audio as a statement.
- the tones are crowded into a very small range: with the voice setting 'pitch 82 118' everything lies between about 73 and 100 Hz, and huyền, sắc, hỏi, ngã and nặng all lie between about 73 and 85 Hz (under 3 semitones, measured on the output), so they are hard to tell apart.
- written s is the plain alveolar s, the same as x, so the retroflex ʂ is missing, although tr and r do get retroflex phonemes (cr, z.).
- several vowels (i, E, a:, @, @:, O) are reset to a fixed length of 150 in ph_vietnam_hue, which removes the coda-dependent durations of the Northern table.
- voice quality is not modelled; glottalisation is imitated only by a dip in amplitude (envelope vi_6amp, used on huyền, ngã and nặng).
- no tonal coarticulation, and a pause between all words ('words 1').

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 23 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=140), a (A=s5: dur=150), e (e=s6: dur=70), i (i=s7: dur=75), o (o=s6: dur=70), k (k=s13: vot=28), h (<h=s18: ms=70 whisper=44), ɲ (n=s20: f2=136 f3=109), b (b=s22: voi=1 lead=75), t̪ (t=s24: f2=91 burst=-4 vot=16), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), ʐ (Z=s35: a4=51 f2=92 f3=87 f4=88), ʝ (X=s39: voi=1 af=-5), e- (e=s6: dur=70), ɔ (O=s43: dur=127), kh (k=s44: vot=85 asp=50), y (y=s7: dur=75), əː (@=s45: dur=263), yə (j=s56 @=s1: f1=56 f2=111 f3=84 hold=55; dur=140), iɛ (j=s54 E: hold=55), cr (t=s30 l=s10: f2=135 f3=112 a3=56 a4=56 vot=32; tap=3 tapms=18 f2=109 f3=77), ɗ (d=s66: voi=1 lead=75 impl=1 burst=-8).

Tones: 1 (0:32,100:48), 7 (0:32,100:40), 2 (0:33,100:30), 3 (0:12,60:12,100:30), 4 (0:30,60:11,100:20), 5 (0:30,60:11,100:20), 6 (0:22,60:11,100:20). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Thompson, Laurence C. (1965). A Vietnamese Grammar. University of Washington Press. Hoàng, Thị Châu (2004). Phương ngữ học tiếng Việt [Vietnamese dialectology]. Hà Nội: Nhà xuất bản Đại học Quốc gia Hà Nội. Vũ, Thanh Phương (1982). Phonetic properties of Vietnamese tones across dialects. In David Bradley (ed.), Papers in South-East Asian Linguistics 8: Tonation. Pacific Linguistics. Phạm, Ben & McLeod, Sharynne (2016). Consonants, vowels and tones across Vietnamese dialects. International Journal of Speech-Language Pathology 18(2). Kirby, James P. (2011). Vietnamese (Hanoi Vietnamese). Journal of the International Phonetic Association 41(3), 381-392. Kirby, James (2010). Dialect experience in Vietnamese tone perception. Journal of the Acoustical Society of America 127(6).

## Vietnamese (Southern) (`vi-vn-x-south`)

Austroasiatic, Vietic. Described: Southern Vietnamese, Saigon (Ho Chi Minh City).

**What the language has.** Five tones: hỏi and ngã are one tone; tones differ in pitch only, not in voice quality. Retroflex ʈ ʂ (written tr, s) against palatal c and alveolar s (written ch, x) in careful speech; often merged in casual speech. Implosive ɓ ɗ against voiceless unaspirated t, k and aspirated tʰ. Long against short a and ɤ in closed syllables. Final alveolars and velars are merged after most vowels: written n and t are said as ŋ and k.

Stress: none (no lexical stress); phrase-level prominence. Rhythm: syllable-timed. Tone: lexical tone, 5 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- hỏi and ngã are kept as two tones with different contours (tone 4 a shallow dip high in the range, about 92 to 97 Hz; tone 5 a deep dip and high rise, about 93, 88, 104 Hz measured), where Saigon speech has one merged tone.
- hỏi lies in the upper part of the range and is nearly level, where the Southern tone is a low dipping rise.
- non-final ngang is a rise-fall (envelope i_risefall between pitch 20 and 35) instead of a level tone.
- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c ignores the clause type, and a question gives the same audio as a statement.
- the tonal range is small: about 78 to 111 Hz with the voice setting 'pitch 82 118' (about 6 semitones, measured), and only sắc and ngã leave the band from 78 to 97 Hz.
- written r is the voiced velar fricative (phoneme Q), a delta variant, not the usual approximant or retroflex fricative.
- written s is the plain alveolar s, the same as x, and written tr is the same as ch; the retroflexes of careful Saigon speech are missing.
- written qu stays [kw] (quả), where Saigon has [w].

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 23 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=140), ə- (@=s1: dur=140), a (A=s5: dur=150), e (e=s6: dur=70), i (i=s7: dur=75), k (k=s13: vot=28), h (<h=s18: ms=70 whisper=44), ɲ (n=s20: f2=136 f3=109), b (b=s22: voi=1 lead=75), t̪ (t=s24: f2=91 burst=-4 vot=16), c (t=s30: f2=135 f3=112 a3=56 a4=56 vot=32), ʝ (X=s39: voi=1 af=-5), ɣ (r=s40: f1=73 f3=116), e- (e=s6: dur=70), ɔ (O=s43: dur=127), kh (k=s44: vot=85 asp=50), y (y=s7: dur=75), aːʊ (a=s58: g1=58 g2=82 g3=93 glide=1), yə (j=s56 @=s1: f1=56 f2=111 f3=84 hold=55; dur=140), iɛ (j=s54 E: hold=55), ɔ- (O=s43: dur=127), ɗ (d=s66: voi=1 lead=75 impl=1 burst=-8).

Tones: 1 (0:34,100:33), 7 (0:34,100:27), 2 (0:22,100:11), 3 (0:32,30:32,100:50), 4 (0:22,50:10,100:40), 5 (0:22,50:10,100:40), 6 (0:22,60:11,100:20). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Thompson, Laurence C. (1965). A Vietnamese Grammar. University of Washington Press. Brunelle, Marc (2009). Tone perception in Northern and Southern Vietnamese. Journal of Phonetics 37, 79-96. Brunelle, Marc (2009). Northern and Southern Vietnamese tone coarticulation: a comparative case study. Journal of the Southeast Asian Linguistics Society 1. Vũ, Thanh Phương (1982). Phonetic properties of Vietnamese tones across dialects. In David Bradley (ed.), Papers in South-East Asian Linguistics 8: Tonation. Pacific Linguistics. Phạm, Ben & McLeod, Sharynne (2016). Consonants, vowels and tones across Vietnamese dialects. International Journal of Speech-Language Pathology 18(2). Hoàng, Thị Châu (2004). Phương ngữ học tiếng Việt [Vietnamese dialectology]. Hà Nội: Nhà xuất bản Đại học Quốc gia Hà Nội. And 2 more in the profile.

## xextan-test (`xex`)

constructed language. Described: as its maker describes it.

**What the language has.** A small inventory.

Stress: not described. Rhythm: syllable-timed.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 25 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: ə (@=s1: dur=157), a (A=s6: dur=175), i (i=s8: dur=85), o (o=s7: dur=80), u (u=s9: dur=86), t (t=s12: vot=17), p (p=s13: vot=13), k (k=s14: vot=28), r (l=s11: tap=3 tapms=18 f2=109 f3=77), h (<h=s19: ms=70 whisper=44), b (b=s23: voi=1 lead=75), d (d=s23: voi=1 lead=75), ɡ (g=s23: voi=1 lead=75), ɛ (E=s43: dur=126), aʊ (a=s47: g1=58 g2=82 g3=93 glide=1 dur=72), eʊ (e=s48: g1=110 g2=53 g3=87 glide=1), aɪ (a=s50: g1=56 g2=146 g3=101 glide=1 dur=72), eɪ (e=s51: g1=106 g2=89 g3=95 glide=1), oɪ (o=s53: g1=101 g2=236 g3=105 glide=1), ɐ̃ (A=s57: f1=85 dur=175 nas=100), ẽ (e=s58: dur=80 nas=100), ĩ (i=s59: dur=85 nas=100), õ (o=s58: dur=80 nas=100), ũ (u=s60: dur=86 nas=100), ɐ̃ʊ̃ (a=s64: f1=83 f2=106 g1=56 g2=82 g3=93 glide=1 dur=72 nas=100).

Melody: little movement on the stressed syllable, since none is described. A question that wants yes or no rises at the end.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: The Xextan language documentation (its maker's own).

## Chinese (Cantonese) (`yue`)

Sino-Tibetan, Sinitic, Yue. Described: Hong Kong Cantonese (close to the Guangzhou standard; differences noted).

**What the language has.** Aspirated versus unaspirated in stops and affricates (p pʰ, t tʰ, k kʰ, kʷ kʷʰ, ts tsʰ); no voiced obstruents. Labialised versus plain velar stops. Long aː versus short ɐ in closed syllables and diphthongs (saam1 'three' against sam1 'heart', gaai1 'street' against gai1 'chicken'). Six tones in open and nasal-final syllables, three in checked syllables. Three final nasals m n ŋ and three unreleased final stops p t k. Front rounded vowels yː and œː (with its short partner ɵ). Two syllabic nasals, m̩ and ŋ̍.

Stress: none (no lexical stress). Rhythm: syllable-timed. Tone: lexical tone, 10 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- the unaspirated stops p t k kʷ are spoken with the voiced stops b d g of the base table, so they are voiced instead of voiceless unaspirated.
- the affricates differ in place instead of aspiration: unaspirated ts (phoneme z) uses the alveolar affricate recording ustop/ts, which the Mandarin table uses for its aspirated affricate, and aspirated tsʰ (phoneme c) uses the palato-alveolar recording ustop/tsh.
- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c has no Cantonese branch and ignores the clause type; a question gives the same audio as a statement, so the rising boundary tone of particle-less questions is missing.
- the tonal pitch range is very small: the six tones lie between about 76 and 98 Hz at the default voice pitch (about 4.4 semitones, measured on the output); tone 3 (about 86 Hz) and tone 6 (about 81 Hz) are one semitone apart.
- changed tones exist only where the dictionary lists them (女人 has jan2), and the large list dictsource/extra/yue_listx overrides the small one: 話 is waa2 in yue_list but waa6 in yue_listx, so 廣東話 ends in waa6.
- syllabic m̩ is missing from the phoneme table; 唔 is listed as ng4 and spoken as a syllabic velar nasal.
- no shortening of long vowels in checked syllables beyond what the vowel phoneme itself has, and no glottal reinforcement of final stops.
- no creaky phonation on tone 4; rising tones are not longer than level tones.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 8 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: h (<h=s18: ms=70 whisper=44), ei (e=s47: g1=79 g2=101 g3=105 glide=1), ou (o=s51: g1=82 g2=106 g3=96 glide=1), ə (@=s1: dur=140), ð (v=s33: f2=149 f3=110 a6=28 ab=48), əʊ (@=s72: g1=94 g2=65 g3=93 glide=1 dur=208), eə (j=s55 @=s1: hold=55; dur=140).

Tones: 1 (0:50,100:50), 7 (0:50,100:32), 2 (0:22,35:22,100:50), 3 (0:30,100:30), 4 (0:22,100:10), 5 (0:20,35:20,100:32), 6 (0:22,100:21). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Zee, Eric (1999). Chinese (Hong Kong Cantonese). In Handbook of the International Phonetic Association, Cambridge University Press, 58-60. Bauer, Robert S. & Benedict, Paul K. (1997). Modern Cantonese Phonology. Mouton de Gruyter. Matthews, Stephen & Yip, Virginia (2011). Cantonese: A Comprehensive Grammar, 2nd edition. Routledge. Yue-Hashimoto, Anne O. (1972). Phonology of Cantonese. Cambridge University Press. Chen, Matthew Y. (2000). Tone Sandhi: Patterns across Chinese Dialects. Cambridge University Press. Yu, Alan C. L. (2007). Understanding near mergers: the case of morphological tone in Cantonese. Phonology 24, 187-214. And 7 more in the profile.

## Chinese (Cantonese, latin as Jyutping) (`yue-latn-jyutping`)

Sino-Tibetan, Sinitic, Yue. Described: Hong Kong Cantonese; the same spoken language and the same sounds as yue, written in the Jyutping romanisation of the Linguistic Society of Hong Kong instead of Han characters.

**What the language has.** Aspirated versus unaspirated in stops and affricates; Jyutping writes the unaspirated series b d g gw z and the aspirated series p t k kw c, and neither series is voiced. Labialised versus plain velar stops (gw, kw against g, k). Long aː (Jyutping aa) versus short ɐ (Jyutping a) in closed syllables and diphthongs (saam1 against sam1, gaai1 against gai1). Six tones, written with the digits 1 to 6 after the syllable. Three final nasals m n ng and three unreleased final stops p t k. Front rounded vowels yu, oe and eo. Two syllabic nasals, m and ng.

Stress: none (no lexical stress). Rhythm: syllable-timed. Tone: lexical tone, 6 in number.

**What eSpeak NG reads otherwise than the literature has it.**

- the syllabic nasals lose their syllable and their tone: m4 and ng5 come out as a bare consonant (m, N) with no tone, and hm4, hng6 likewise.
- a syllable typed without a tone digit is given tone 1 (nei hou is spoken with two high level tones).
- every Latin word is read as Jyutping, so English words inside the text are read letter by letter as Cantonese syllables.
- the unaspirated stops b d g gw are spoken with the voiced stops of the base table instead of voiceless unaspirated stops.
- the affricates differ in place instead of aspiration: z uses the alveolar affricate recording ustop/ts, c uses the palato-alveolar recording ustop/tsh.
- no sentence intonation and no declination: CalcPitches_Tone() in src/libespeak-ng/intonation.c ignores the clause type, and nei5 hou2 maa3? gives the same pitch as a statement.
- the tonal pitch range is very small: the six tones lie between about 76 and 98 Hz at the default voice pitch (about 4.4 semitones, measured on the output); tones 3 and 6 are one semitone apart.
- the finals ing, ung, eng, oeng, ang are built from a vowel plus the consonant N, while Han-character input uses the single rhyme phonemes ing, ung, eng, oeng, ang of the phoneme table, so the same word can sound different in the two scripts.

**What OpenEVV says.** Spoken by the module made from German (`dedx`). 3 of the language's phonemes are given a sound of their own.

The sounds, each with the phone it is made of and how it differs from it: h (<h=s18: ms=70 whisper=44), ei (e=s47: g1=79 g2=101 g3=105 glide=1), ou (o=s51: g1=82 g2=106 g3=96 glide=1).

Tones: 1 (0:50,100:50), 7 (0:50,100:32), 2 (0:22,35:22,100:50), 3 (0:30,100:30), 4 (0:22,100:10), 5 (0:20,35:20,100:32), 6 (0:22,100:21). The pitch is made from them, syllable by syllable.
Timing: stressed 88 per cent, weak 112 per cent of the module's own.

Sources: Zee, Eric (1999). Chinese (Hong Kong Cantonese). In Handbook of the International Phonetic Association, Cambridge University Press, 58-60. Bauer, Robert S. & Benedict, Paul K. (1997). Modern Cantonese Phonology. Mouton de Gruyter. Matthews, Stephen & Yip, Virginia (2011). Cantonese: A Comprehensive Grammar, 2nd edition. Routledge. Chen, Matthew Y. (2000). Tone Sandhi: Patterns across Chinese Dialects. Cambridge University Press. Yu, Alan C. L. (2007). Understanding near mergers: the case of morphological tone in Cantonese. Phonology 24, 187-214. Lisker, Leigh & Abramson, Arthur S. (1964). A cross-language study of voicing in initial stops: acoustical measurements. Word 20, 384-422. And 5 more in the profile.

