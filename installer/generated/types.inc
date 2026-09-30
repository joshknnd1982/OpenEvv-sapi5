; Written by installer\make_components.py from languages\*\language.ini. Do not edit it by hand:
; run  python installer\make_components.py  when a language pack is added, removed or renamed.
; The tags of every pack in languages\. openevv.iss stops the build when languages\ holds one
; that is not in this list.
#define LangTags "|ab|af|am|an|ar|as|az|ba|be|bg|bn|bpy|bs|ca|ca-ba|ca-nw|ca-va|chr|cmn|cmn-latn-pinyin|crh|cs|cv|cy|da|dede|dedx|el|en-029|en-gb-scotland|en-gb-x-gbclan|en-gb-x-gbcwmd|en-gb-x-rp|en-shaw|en-us-nyc|engb|engx|enus|enux|eo|eses|esex|esus|esux|et|eu|fa|fa-latn|fi|fo|fr-be|fr-ch|frca|frfr|frfx|ga|gd|gn|grc|gu|hak|haw|he|hi|hr|ht|hu|hy|hyw|ia|id|io|is|itit|itix|jajp|jbo|ka|kaa|kk|kl|kn|ko|kok|ku|ky|la|lb|lfn|lij|lt|ltg|lv|mi|mk|ml|mn|mn-f|mr|ms|mt|mto|my|nb|nci|ne|nl|nog|om|or|pa|pap|pdc|pdc-x-lehigh|pdc-x-midwest|piqd|plpl|ps|ps-x-northwest|ps-x-southeast|ps-x-yusufzai|pt|pt-br|py|qdb|qu|quc|qya|ro|ru|ru-cl|ru-lv|rup|sd|shn|si|sjn|sk|sl|smj|sq|sr|sv|sw|ta|te|th|ti|tk|tn|tr|tt|ug|uk|ur|uz|vi|vi-vn-x-central|vi-vn-x-south|xex|yue|yue-latn-jyutping|"
#define LangCount 155
#define LangNativeCount 10
#define LangEspeakCount 145
#define LangVoices 1240

Name: "openevv"; Description: "The ten OpenEVV languages (80 voices)"
Name: "english"; Description: "English only: US and British English (16 voices)"
Name: "full"; Description: "All 155 languages (1,240 voices)"
Name: "custom"; Description: "Custom: choose the languages one by one"; Flags: iscustom
