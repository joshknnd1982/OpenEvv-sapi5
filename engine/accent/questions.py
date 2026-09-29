#!/usr/bin/env python3
"""The words questions are asked with, language by language.

A question that can be answered yes or no and a question asked with a
question word -- who, what, where -- end differently in most languages: the
first rises, or rises and falls, and the second falls as a statement does
from a high question word. A text says neither; it has a question mark. So
the words are listed here, and a clause that ends in a question mark and has
one of them is said as the second kind.

`first' means the word counts among the first three words of its clause,
which is where the languages of Europe put it (after a preposition at most),
and keeps a word that is also a conjunction or a relative from being taken
for a question word further on. `any' means it counts wherever it stands, as
in the languages that leave the question word where the answer would be.

A word with `~' before it counts only when it is not the first word of its
clause: Hindi kya and its kin begin a question that wants yes or no, and ask
`what' inside one.

Only single words are listed; of `por que', `de ce', `ne zaman' the word
that is a question word by itself.
"""

ENGLISH = ('first', 'who what where when why how which whose whom')
FRENCH = ('first', 'qui que quoi où quand comment pourquoi combien quel quelle quels quelles lequel laquelle '
                   'lesquels lesquelles')
CATALAN = ('first', 'què qui quan on com quant quanta quants quantes quin quina quins quines')
PORTUGUESE = ('first', 'quê quem onde quando quanto quanta quantos quantas qual quais porquê aonde')
RUSSIAN = ('first', 'кто что где когда как почему зачем какой какая какое какие сколько куда откуда чей чья чьё '
                    'чьи кого чего кому чему кем чем')
SERBOCROATIAN = ('first', 'ko tko šta što gde gdje kada kad kako zašto koji koja koje koliko kuda kamo čiji '
                          'ко шта где када кад како зашто који која које колико куда чији')
PASHTO = ('any', 'څوک څه چیرته چېرته کله څنګه ولې څو کوم چا')
VIETNAMESE = None

WH = {
    'an': ('first', 'qué quí quién quan cuan cómo aón cuánto cuánta cuántos cuántas cuál'),
    'ca': CATALAN, 'ca-ba': CATALAN, 'ca-nw': CATALAN, 'ca-va': CATALAN,
    'fr-be': FRENCH, 'fr-ch': FRENCH,
    'pt': PORTUGUESE, 'pt-br': PORTUGUESE,
    'ro': ('first', 'ce cine unde când cum cât câtă câți câte care'),
    'rup': ('first', 'ți cari iu cându cum cãt cãtu'),
    'pap': ('first', 'kiko ken unda kuandu kon pakiko kuantu kua'),
    'ht': ('first', 'kisa kilès kimoun kote kikote kilè kijan kouman poukisa konbyen'),
    'la': ('first', 'quis quid ubi quando quomodo cur quare quot qualis quantus quo unde uter'),
    'eu': ('any', 'nor zer non noiz nola zergatik zein zenbat nork nori noren nora nondik'),
    'mt': ('first', 'min xi fejn meta kif għaliex għalfejn liema kemm'),
    'nl': ('first', 'wie wat waar wanneer hoe waarom welke welk hoeveel'),
    'af': ('first', 'wie wat waar wanneer hoe hoekom waarom watter hoeveel'),
    'lb': ('first', 'wien wat wou wéini wéi firwat wéivill wéieen wouhin'),
    'pdc': ('first', 'wer was wu wann wie ferwas weller wieviel'),
    'pdc-x-lehigh': ('first', 'wer was wu wann wie ferwas weller wieviel'),
    'pdc-x-midwest': ('first', 'wer was wu wann wie ferwas weller wieviel'),
    'da': ('first', 'hvem hvad hvor hvornår hvordan hvorfor hvilken hvilket hvilke hvis'),
    'nb': ('first', 'hvem hva hvor når hvordan hvorfor hvilken hvilket hvilke'),
    'sv': ('first', 'vem vad var när hur varför vilken vilket vilka vart vems'),
    'is': ('first', 'hver hvað hvar hvenær hvernig hvers hvaða hvert hví'),
    'fo': ('first', 'hvør hvat hvar nær hvussu hví hvørjum'),
    'en-029': ENGLISH, 'en-gb-scotland': ENGLISH, 'en-gb-x-gbclan': ENGLISH, 'en-gb-x-gbcwmd': ENGLISH,
    'en-gb-x-rp': ENGLISH, 'en-us-nyc': ENGLISH,
    'cy': ('first', 'pwy beth ble pryd sut pam pa faint ble lle'),
    'ga': ('first', 'cé cad céard cá cathain conas cén'),
    'gd': ('first', 'cò dè càite cuin ciamar carson'),
    'ru': RUSSIAN, 'ru-cl': RUSSIAN, 'ru-lv': RUSSIAN,
    'uk': ('first', 'хто що де коли як чому навіщо який яка яке які скільки куди звідки чий кого чого'),
    'be': ('first', 'хто што дзе калі як чаму навошта які якая якое якія колькі куды адкуль чый'),
    'bg': ('first', 'кой коя кое кои какво къде кога как защо колко какъв каква какви чий'),
    'mk': ('first', 'кој која кое кои што каде кога како зошто колку каков чиј'),
    'sr': SERBOCROATIAN, 'hr': SERBOCROATIAN, 'bs': SERBOCROATIAN,
    'sl': ('first', 'kdo kaj kje kdaj kako zakaj kateri katera katero koliko kam čigav'),
    'cs': ('first', 'kdo co kde kdy jak proč který která které jaký jaká kolik kam čí'),
    'sk': ('first', 'kto čo kde kedy ako prečo ktorý ktorá ktoré aký aká koľko kam čí'),
    'lt': ('first', 'kas kur kada kaip kodėl kuris kuri kiek koks kokia ką'),
    'lv': ('first', 'kas kur kad kā kāpēc kurš kura cik kāds kāda ko'),
    'ltg': ('first', 'kas kur kod kai kuodeļ kurs kura cik kaids'),
    'fi': ('first', 'kuka mikä mitä missä milloin miten miksi kuinka kumpi kenen mistä mihin ketä'),
    'et': ('first', 'kes mis kus millal kuidas miks milline mitu kuhu kust kelle mida'),
    'hu': ('first', 'ki mi hol mikor hogyan miért melyik mennyi hány hová hova honnan milyen mit kit kinek'),
    'el': ('first', 'ποιος ποια ποιο ποιοι ποιες τι πού πότε πώς γιατί πόσο πόσος πόση πόσα πόσοι'),
    'sq': ('first', 'kush çfarë ç ku kur si pse cili cila sa'),
    'hy': ('any', 'ով ինչ որտեղ երբ ինչպես ինչու քանի ինչքան ում ուր'),
    'hyw': ('any', 'ով ինչ ուր երբ ինչպէս ինչու քանի որքան'),
    'ka': ('any', 'ვინ რა სად როდის როგორ რატომ რამდენი რომელი ვის რას'),
    'tr': ('any', 'ne kim nerede nereye nereden nasıl neden niçin niye hangi kaç kimin neyi kimi'),
    'az': ('any', 'nə kim harada haraya haradan necə niyə hansı neçə kimin'),
    'tk': ('any', 'näme kim nirede nirä haçan nähili haýsy näçe'),
    'uz': ('any', 'nima kim qayerda qayerga qachon qanday nega qancha qaysi nechta'),
    'crh': ('any', 'ne kim qayda qayerde ne zaman nasıl neden qaysı qaç'),
    'kaa': ('any', 'ne kim qayda qashan qalay nege qansha qaysı neshe'),
    'kk': ('any', 'не кім қайда қашан қалай неге қандай қанша қай неше'),
    'ky': ('any', 'эмне ким кайда качан кандай эмнеге канча кайсы нече'),
    'tt': ('any', 'нәрсә ни кем кайда кайчан ничек нигә нинди ничә кайсы'),
    'ba': ('any', 'нимә ни кем ҡайҙа ҡасан нисек ниңә ниндәй нисә ҡайһы'),
    'nog': ('any', 'не ким кайда кашан калай неге кандай неше'),
    'cv': ('any', 'мӗн кам ӑҫта хӑҫан мӗнле мӗншӗн миҫе хӑш'),
    'ug': ('any', 'نېمە كىم قەيەردە قاچان قانداق نېمىشقا قانچە قايسى'),
    'mn': ('any', 'хэн юу хаана хэзээ яаж яагаад ямар хэд хэдэн аль'),
    'mn-f': ('any', 'хэн юу хаана хэзээ яаж яагаад ямар хэд хэдэн аль'),
    'ar': ('first', 'ماذا أين متى كيف لماذا كم أي أيّ مَن لمن بماذا'),
    'fa': ('any', 'چه چی کجا چرا چطور چگونه چند کدام'),
    'ku': ('any', 'kî çi kengî çawa çima kîjan çend kê'),
    'ps': PASHTO, 'ps-x-northwest': PASHTO, 'ps-x-southeast': PASHTO, 'ps-x-yusufzai': PASHTO,
    'he': ('first', 'מי מה איפה מתי איך למה מדוע כמה איזה איזו לאן מאין היכן'),
    'am': ('any', 'ማን ምን የት መቼ እንዴት ለምን ስንት የትኛው'),
    'ti': ('any', 'መን እንታይ ኣበይ መዓስ ከመይ ንምንታይ ክንደይ'),
    'om': ('any', 'eenyu maal eessa yoom akkam maaliif meeqa kam'),
    'hi': ('any', '~क्या कौन कहाँ कहां कब कैसे कैसा कैसी क्यों कितना कितने कितनी किस किसका किसने किधर कौनसा'),
    'ur': ('any', '~کیا کون کہاں کب کیسے کیسا کیوں کتنا کتنے کتنی کس کدھر'),
    'bn': ('any', 'কী কে কোথায় কখন কেন কীভাবে কেমন কত কোন কার কাকে'),
    'as': ('any', 'কি কোন ক’ত কেতিয়া কিয় কেনেকৈ কিমান কাৰ'),
    'mr': ('any', 'काय कोण कुठे केव्हा कधी कसे कसा कशी का किती कोणता कोणती'),
    'ne': ('any', 'के को कहाँ कहिले कसरी किन कति कुन कसको'),
    'gu': ('any', 'શું કોણ ક્યાં ક્યારે કેમ કેવી કેટલા કેટલી કયો કઈ'),
    'pa': ('any', '~ਕੀ ਕੌਣ ਕਿੱਥੇ ਕਦੋਂ ਕਿਵੇਂ ਕਿਉਂ ਕਿੰਨਾ ਕਿੰਨੇ ਕਿਹੜਾ ਕਿਹੜੀ'),
    'or': ('any', 'କଣ କିଏ କେଉଁଠି କେବେ କିପରି କାହିଁକି କେତେ କେଉଁ'),
    'sd': ('any', 'ڇا ڪير ڪٿي ڪڏهن ڪيئن ڇو ڪيترا ڪهڙو'),
    'si': ('any', 'මොකක්ද කවුද කොහෙද කවදාද කොහොමද ඇයි කීයද මොන'),
    'kok': ('any', 'कितें कोण खंय केन्ना कशें कित्याक कितले खंयचें'),
    'ta': ('any', 'என்ன யார் எங்கே எப்போது எப்படி ஏன் எத்தனை எது எந்த எவ்வளவு'),
    'te': ('any', 'ఏమిటి ఏమి ఎవరు ఎక్కడ ఎప్పుడు ఎలా ఎందుకు ఎంత ఏది ఏ ఎన్ని'),
    'kn': ('any', 'ಏನು ಯಾರು ಎಲ್ಲಿ ಯಾವಾಗ ಹೇಗೆ ಏಕೆ ಯಾಕೆ ಎಷ್ಟು ಯಾವ ಯಾವುದು'),
    'ml': ('any', 'എന്ത് എന്താണ് ആര് ആരാണ് എവിടെ എപ്പോൾ എങ്ങനെ എന്തുകൊണ്ട് എത്ര ഏത്'),
    'id': ('any', 'apa siapa mana kapan bagaimana mengapa kenapa berapa'),
    'ms': ('any', 'apa siapa mana bila bagaimana mengapa kenapa berapa'),
    'sw': ('any', 'nani nini wapi lini vipi gani ngapi'),
    'tn': ('any', 'mang eng kae leng jang goreng bokae'),
    'haw': ('any', 'aha wai hea pehea ʻehia ahea ināhea'),
    'mi': ('any', 'aha wai hea pēhea āhea hia'),
    'gn': ('any', 'mbaʼe mbaʼépa máva mávapa moõ moõpa arakaʼe mbaʼéicha mbaʼére mboy'),
    'qu': ('any', 'ima pi may maypi maymanta haykʼaq imayna imarayku imanaqtin haykʼa mayqin'),
    'kl': ('any', 'kina suna sumi qanga qanoq sooq qassit'),
    'eo': ('first', 'kiu kio kie kiam kiel kial kiom kia kies kien'),
    'ia': ('first', 'qui que ubi quando como proque qual quante'),
    'io': ('first', 'qua quo ube kande quale pro quanta'),
    'lfn': ('first', 'ci cual do cuando como perce cuanto'),
}


def of(tag):
    """(where, [words]) for a language, or None."""
    got = WH.get(tag)
    if not got:
        return None
    where, words = got
    return where, words.split()
