# Phase 9, step 2: Claude's own transcription of the seven official sub-chart PNGs
# (IPA_Kiel_*_0600.png, fetched 2026-10-11 from the IPA's site, "(c) 2026 IPA, revised to 2015/2005"),
# read as images in this session, compared with the committed checklist.
import json, unicodedata, sys
MINE = {
 "pulmonic": "p b t d ʈ ɖ c ɟ k ɡ q ɢ ʔ m ɱ n ɳ ɲ ŋ ɴ ʙ r ʀ ⱱ ɾ ɽ ɸ β f v θ ð s z ʃ ʒ ʂ ʐ ç ʝ x ɣ χ ʁ ħ ʕ h ɦ ɬ ɮ ʋ ɹ ɻ j ɰ l ɭ ʎ ʟ".split(),
 "non_pulmonic": "ʘ ǀ ǃ ǂ ǁ ɓ ɗ ʄ ɠ ʛ ʼ".split(),
 "other_symbols": "ʍ w ɥ ʜ ʢ ʡ ɕ ʑ ɺ ɧ".split() + ["\u035c", "\u0361"],   # t͜s (tie below), k͡p (tie above)
 "vowels": "i y ɨ ʉ ɯ u ɪ ʏ ʊ e ø ɘ ɵ ɤ o ə ɛ œ ɜ ɞ ʌ ɔ æ ɐ a ɶ ɑ ɒ".split(),
 # left column 12, middle column 12, right column 7, and the ring above from the note (ŋ̊)
 "diacritics": ["\u0325","\u032c","ʰ","\u0339","\u031c","\u031f","\u0320","\u0308","\u033d","\u0329","\u032f","˞",
                "\u0324","\u0330","\u033c","ʷ","ʲ","ˠ","ˤ","\u0334","\u031d","\u031e","\u0318","\u0319",
                "\u032a","\u033a","\u033b","\u0303","ⁿ","ˡ","\u031a", "\u030a"],
 "suprasegmentals": ["ˈ","ˌ","ː","ˑ","\u0306","|","‖",".","‿"],
 "tones": ["\u030b","˥","\u0301","˦","\u0304","˧","\u0300","˨","\u030f","˩",
           "\u030c","˩˥","\u0302","˥˩","\u1dc4","˧˥","\u1dc5","˩˧","\u1dc8","˧˦˨","ꜜ","ꜛ","↗","↘"],
}
cp = lambda s: " ".join("U+%04X" % ord(c) for c in s)
d = json.load(open("docs/tts-extension/inventory/IPA_CHECKLIST.json", encoding="utf8"))
theirs = {}
for x in d["symbols"]:
    theirs.setdefault(x["section"], []).append(" ".join(x["codepoints"]))
total = 0
for sec, syms in MINE.items():
    mine = [cp(s) for s in syms]; total += len(mine)
    t = theirs.get(sec, [])
    print(f"{sec:16} mine {len(mine):3}  checklist {len(t):3}  "
          f"only-in-mine {[m for m in mine if m not in t]}  only-in-checklist {[x for x in t if x not in mine]}")
print("total mine", total, "checklist", len(d["symbols"]))
