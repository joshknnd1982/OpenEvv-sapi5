#!/usr/bin/env python3
"""Builds the IPA checklist (Phase 0, step 6b; playbook R19a) from the research files.

    research/<section>.json   what each chart section prints, with sources (one helper a section)
    languages.json            what every shipped pack says for each sound (build_language_inventory.py)
    engine/espeak_phonemes.py which sounds each IBM module has as phones of its own (TEMPLATES)

and writes, beside this file,

    IPA_CHECKLIST.json   one record a symbol: the coverage script of later phases reads this
    IPA_CHECKLIST.md     the same for a person
    IPA_REFERENCES.md    every source the helpers opened, and the ones they name without having opened

It maps nothing and synthesizes nothing. "Engine today" is read from code and pack data only:
nothing in this file was rendered or measured. Run it from anywhere:

    python docs/tts-extension/inventory/build_ipa_checklist.py
"""

import collections
import json
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import espeak_phonemes as EP  # noqa: E402  (tables only; nothing runs on import)

SECTIONS = [("pulmonic", "Consonants (pulmonic)"), ("non_pulmonic", "Consonants (non-pulmonic)"),
            ("other_symbols", "Other symbols"), ("vowels", "Vowels"), ("diacritics", "Diacritics"),
            ("suprasegmentals", "Suprasegmentals"), ("tones", "Tones and word accents")]

# What the chart prints, section by section, as read by eye (Claude, 2026-10-05) from the rendered page
# of the human's copy of the official chart, IPA_Kiel.pdf ("(c) 2026 IPA", "IPA Chart revised to
# 2015/2005"; SHA-256 C8203013C676B243959072234526D60B874851D0509A00FD7528F4E56C706787). The helpers
# worked from the IPA's web site; this is the independent check that the two agree.
PDF = {
    "pulmonic": "p b t d ʈ ɖ c ɟ k ɡ q ɢ ʔ m ɱ n ɳ ɲ ŋ ɴ ʙ r ʀ ⱱ ɾ ɽ ɸ β f v θ ð s z ʃ ʒ ʂ ʐ ç ʝ x ɣ χ ʁ ħ ʕ h ɦ "
                "ɬ ɮ ʋ ɹ ɻ j ɰ l ɭ ʎ ʟ",
    "non_pulmonic": "ʘ ǀ ǃ ǂ ǁ ɓ ɗ ʄ ɠ ʛ ʼ",
    "other_symbols": "ʍ w ɥ ʜ ʢ ʡ ɕ ʑ ɺ ɧ \u035c \u0361",
    "vowels": "i y ɨ ʉ ɯ u ɪ ʏ ʊ e ø ɘ ɵ ɤ o ə ɛ œ ɜ ɞ ʌ ɔ æ ɐ a ɶ ɑ ɒ",
    # 31 rows of the table, and the ring above of the note under it
    "diacritics": "\u0325 \u030a \u032c ʰ \u0339 \u031c \u031f \u0320 \u0308 \u033d \u0329 \u032f ˞ \u0324 \u0330 "
                  "\u033c ʷ ʲ ˠ ˤ \u0334 \u031d \u031e \u0318 \u0319 \u032a \u033a \u033b \u0303 ⁿ ˡ \u031a",
    "suprasegmentals": "ˈ ˌ ː ˑ \u0306 | ‖ . ‿",
    # each level and contour tone in both printed forms; the last contour letter is hard to read in
    # the Kiel typeface (see OPEN_QUESTIONS.md)
    "tones": "\u030b ˥ \u0301 ˦ \u0304 ˧ \u0300 ˨ \u030f ˩ \u030c ˩˥ \u0302 ˥˩ \u1dc4 ˧˥ \u1dc5 ˩˧ \u1dc8 ˧˦˨ ꜜ ꜛ ↗ ↘",
}

# The seven modules whose phones engine/espeak_phonemes.py gives an IPA value for. Canadian French, Japanese
# and Polish have no such table, so a sound only they have as a phone of its own is not found here.
IBM = ["enus", "engb", "dede", "eses", "esus", "frfr", "itit"]

# The marks: what in the shipped product does this, read from openevv/src/accent/evv_accent.c (the
# keys of a `sound' line), frontend/src and docs/SOUNDS.md. `own' = a module does it itself; `some' =
# there is a mechanism that covers some cases; `none' = no mechanism was found. This table is Claude's
# reading of the code, not a measurement.
MARKS = {
    "U+0325": ("some", "keys `voi=0` and `whisper` on a sound line; no rule that puts the mark on any base"),
    "U+030A": ("some", "as U+0325"),
    "U+032C": ("some", "keys `voi=1`, `lead`, `bar`; no rule that puts the mark on any base"),
    "U+02B0": ("some", "keys `vot`, `asp` (and `pre` for preaspiration) after a stop"),
    "U+0339": ("none", "only by hand as formant ratios on one sound"),
    "U+031C": ("none", "only by hand as formant ratios on one sound"),
    "U+031F": ("none", "only by hand as formant ratios on one sound"),
    "U+0320": ("none", "only by hand as formant ratios on one sound"),
    "U+0308": ("none", "only by hand as formant ratios on one sound"),
    "U+033D": ("none", "only by hand as formant ratios on one sound"),
    "U+0329": ("some", "the front-end puts the map's `schwa` phone before a syllabic consonant: a vowel plus "
                       "the consonant, not a syllabic consonant"),
    "U+032F": ("some", "a diphthong is its most open vowel with the rest as glides (frontend/README.md)"),
    "U+02DE": ("some", "the English modules have r-coloured vowels of their own; elsewhere F3 ratios by hand"),
    "U+0324": ("some", "keys `brth` (after a release, or on a tone), `oq`, `tl`, `ah`"),
    "U+0330": ("some", "key `creak` (lowers the open quotient, sets diplophonia); also on a tone"),
    "U+033C": ("none", "no key"),
    "U+02B7": ("none", "only by hand as formant ratios on one sound; no composing transform"),
    "U+02B2": ("none", "only by hand as formant ratios on one sound; no composing transform"),
    "U+02E0": ("none", "only by hand as formant ratios on one sound; no composing transform"),
    "U+02E4": ("none", "only by hand as formant ratios on one sound; no composing transform"),
    "U+0334": ("none", "only by hand as formant ratios on one sound; no composing transform"),
    "U+031D": ("none", "only by hand as formant ratios on one sound"),
    "U+031E": ("none", "only by hand as formant ratios on one sound"),
    "U+0318": ("none", "no key"),
    "U+0319": ("none", "no key"),
    "U+032A": ("some", "t and d of the Italian, Spanish and French modules are dental already "
                       "(DENTAL_MODULES, engine/accent/sounds.py:95); elsewhere an F2 ratio by hand"),
    "U+033A": ("none", "no key"),
    "U+033B": ("none", "no key"),
    "U+0303": ("some", "key `nas` (moves the nasal zero, widens B1); the French and German modules have "
                       "nasal vowels of their own"),
    "U+207F": ("none", "no key"),
    "U+02E1": ("none", "no key"),
    "U+031A": ("some", "key `noburst`"),
    "U+02BC": ("some", "key `ej`: silence after the burst; nothing else of an ejective"),
    "U+035C": ("some", "the modules have some affricates as phones and take them apart (`says C t S`); "
                       "nothing for a double articulation such as k\u0361p"),
    "U+0361": ("some", "as U+035C"),
    "U+02C8": ("own", "the stress digit 1 of every module's annotations"),
    "U+02CC": ("own", "the stress digit 2; the Italian and Spanish modules have no secondary stress"),
    "U+02D0": ("some", "the map is tried with the phoneme's IPA plus the length mark; key `dur`; "
                       "the German module has long vowels of its own"),
    "U+02D1": ("none", "no handling found"),
    "U+0306": ("none", "no handling found"),
    "U+007C": ("some", "phrases end where the punctuation says (`{P c}` after a comma); the mark itself is not read"),
    "U+2016": ("some", "phrases end where the punctuation says (`{P s}`, `{P q}`); the mark itself is not read"),
    "U+002E": ("own", "every annotation marks its syllables with `.`; the front-end divides the syllables"),
    "U+203F": ("unknown", "not determined in Phase 0"),
    "U+A71C": ("none", "no key; declination (`decl`) is per phrase, not a step at a mark"),
    "U+A71B": ("none", "no key"),
    "U+2197": ("some", "the end of a question rises (`fq`, `qreg`) by the punctuation; the mark itself is not read"),
    "U+2198": ("some", "the end of a statement falls (`fs`) by the punctuation; the mark itself is not read"),
}
TONE = ("some", "`tone` lines: up to 8 points on Chao's five levels, with the layer's own pitch (`f0=own`); "
                "tones are named as eSpeak NG names them, in %d of 145 packs; the IPA mark itself is not read")

# Sounds whose stand-in in the packs is known from the code to lack the mechanism the sound is made by.
STAND_IN = {
    "ʘ": "click", "ǀ": "click", "ǃ": "click", "ǂ": "click", "ǁ": "click",
    "ɓ": "implosive", "ɗ": "implosive", "ʄ": "implosive", "ɠ": "implosive", "ʛ": "implosive",
    "r": "trill", "ʀ": "trill", "ʙ": "trill", "ɾ": "tap", "ɽ": "tap", "ɺ": "tap", "ⱱ": "tap",
}
STAND_IN_NOTE = {
    "click": "stand-in: a stop with a louder burst and a silence after it (`burst`, `ej`); the synthesiser has no "
             "source for a click (ARCHITECTURE_MAP.md section 10)",
    "implosive": "stand-in: a voiced stop whose voicing swells towards the release (`impl`)",
    "trill": "where the module has no trill of its own: dips in voicing and F1 (`tap=2..3`), not closures",
    "tap": "where the module has no tap of its own: one dip in voicing and F1 (`tap=1`), not a closure",
}


def cps(text):
    return ["U+%04X" % ord(c) for c in text]


def show(sym):
    """A combining mark is shown on a dotted circle."""
    return ("\u25cc" + sym) if unicodedata.category(sym[0]).startswith("M") else sym


def pack_evidence(packs):
    """IPA string -> {template: Counter of how the packs of that template say it}, and for the marks,
    every IPA string in any map with the packs it is in."""
    by_ipa = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    tags_of = collections.defaultdict(lambda: collections.defaultdict(set))
    packs_of = collections.defaultdict(set)
    strings = collections.defaultdict(set)
    for p in packs:
        if p["kind"] != "espeak":
            continue
        sounds = p["sounds_map"]["sounds"]
        for e in p["sounds_map"]["phonemes"]:
            ipa = (e.get("ipa") or "").split("  ")[0].strip()
            if not ipa:
                continue
            ipa = unicodedata.normalize("NFD", ipa)
            strings[ipa].add(p["tag"])
            said = []
            kind = "not said"
            for ph in e["phones"]:
                name, _, sid = ph.partition("=")
                sid = sid.split("^")[0]
                d = sounds.get(sid, {}).get("def") if sid else None
                if name.startswith(("<", ">")):
                    kind = "made by the accent layer"
                elif d and kind != "made by the accent layer":
                    kind = "module phone reshaped"
                elif kind == "not said":
                    kind = "module phone as it is"
                said.append("%s{%s}" % (name, d) if d else name)
            by_ipa[ipa][p["template"]][(kind, " ".join(said))] += 1
            tags_of[ipa][p["template"]].add(p["tag"])
            packs_of[ipa].add(p["tag"])
    return by_ipa, packs_of, strings, tags_of


def letter_ability(symbol, by_ipa, packs_of, tags_of):
    sym = unicodedata.normalize("NFD", symbol)    # the form the pack strings are kept in (c with cedilla decomposes)
    native = [t for t in IBM if symbol in EP.TEMPLATES[t].vowels.values() or symbol in EP.TEMPLATES[t].consonants.values()]
    per_template = {}
    kinds = collections.Counter()
    for tmpl, c in sorted(by_ipa.get(sym, {}).items()):
        (kind, said), n = c.most_common(1)[0]
        per_template[tmpl] = {"how": kind, "as": said, "packs": len(tags_of[sym][tmpl]), "map_lines": sum(c.values()),
                              "variants": len(c)}
        kinds[kind] += 1
    says = [k for k in kinds if k != "not said"]
    if native:
        status = "already"
    elif says:
        status = "partly"
    else:
        status = "absent"
    detail = []
    if native:
        detail.append("a phone of its own in the IBM modules: " + ", ".join(native))
    if per_template:
        detail.append("in the maps of %d of 145 packs; by template: " % len(packs_of.get(sym, ())) + "; ".join(
            "%s %s `%s`" % (t, v["how"], v["as"] or "-") for t, v in per_template.items()))
    else:
        detail.append("in no pack's map")
    if symbol in STAND_IN:
        detail.append(STAND_IN_NOTE[STAND_IN[symbol]])
    return {"status": status, "native_in_modules": native, "packs_with_a_line": len(packs_of.get(sym, ())),
            "by_template": per_template, "detail": ". ".join(detail)}


def mark_ability(rec, strings, n_tone_packs):
    sym = rec["symbol"]
    key = "+".join(rec["codepoints"])
    if rec["section"] == "tones" and key not in MARKS:
        mech, text = TONE[0], TONE[1] % n_tone_packs
    else:
        mech, text = MARKS[key]
    # letters that have the mark built in and do not decompose: dark l, the r-coloured vowels
    built_in = {"U+0334": "ɫ", "U+02DE": "ɚɝ"}.get(key, "")
    hits = {s: tags for s, tags in strings.items() if sym in s or any(c in s for c in built_in)}
    tags = set().union(*hits.values()) if hits else set()
    examples = [s for s, _ in sorted(hits.items(), key=lambda kv: -len(kv[1]))[:6]]
    if mech == "own":
        status = "already"
    elif mech == "unknown":
        status = "unknown"
    elif mech == "some" or tags:
        status = "partly"
    else:
        status = "absent"
    detail = text
    if rec["section"] not in ("tones",) and sym not in ".|":
        detail += ". Sounds written with this mark are in the maps of %d of 145 packs" % len(tags)
        if examples:
            detail += " (most often: %s)" % " ".join(examples)
    return {"status": status, "mechanism": mech, "packs_with_a_sound_so_marked": len(tags),
            "examples": examples, "detail": detail}


def main():
    inv = json.load(open(os.path.join(HERE, "languages.json"), encoding="utf-8"))
    by_ipa, packs_of, strings, tags_of = pack_evidence(inv["packs"])
    n_tone_packs = sum(1 for p in inv["packs"] if p["kind"] == "espeak" and p["counts"]["tones"])

    records, refs, problems, charts, ok = [], [], [], [], True
    for sec, title in SECTIONS:
        d = json.load(open(os.path.join(HERE, "research", sec + ".json"), encoding="utf-8"))
        charts.append({"section": sec, **d["chart"]})
        got = [s["symbol"] for s in d["symbols"]]
        want = PDF[sec].split()
        if sorted(got) != sorted(want):
            ok = False
            print("MISMATCH with the PDF in %s: only in research %s; only in PDF %s" % (
                sec, sorted(set(got) - set(want)), sorted(set(want) - set(got))))
        opened = {r["id"]: bool(r.get("read")) for r in d.get("references", [])}
        for r in d.get("references", []):
            refs.append({"section": sec, **r})
        for p in d.get("problems", []):
            problems.append({"section": sec, "problem": p})
        for n, s in enumerate(d["symbols"], 1):
            if cps(s["symbol"]) != s["codepoints"]:
                ok = False
                print("CODEPOINTS do not match the symbol: %s %s" % (sec, s["codepoints"]))
            names = [unicodedata.name(c, "?") for c in s["symbol"]]
            if len(names) == 1 and names[0] != "?" and names[0] != s["unicode_name"]:
                ok = False
                print("UNICODE NAME differs from Python's: %s %s / %s" % (s["codepoints"], s["unicode_name"], names[0]))
            rec = {"id": "+".join(s["codepoints"]), "section": sec, "section_title": title, "n": n,
                   "symbol": s["symbol"], "codepoints": s["codepoints"], "unicode_name": s["unicode_name"],
                   "ipa_name": s.get("ipa_name"), "ipa_number": s.get("ipa_number"),
                   "chart_example": s.get("chart_example"), "alt_codepoints": s.get("alt_codepoints") or [],
                   "equivalent_to": s.get("equivalent_to"), "articulatory": s["articulatory"],
                   "features": s.get("features") or {},
                   # refs: sources a helper opened. quoted_unopened: a source the opened one quotes, not opened itself
                   "acoustic_correlates": [{"text": c["text"], "provenance": c["provenance"],
                                            "refs": ["%s:%s" % (sec, x) for x in c.get("refs", []) if opened.get(x)],
                                            "quoted_unopened": ["%s:%s" % (sec, x) for x in c.get("refs", [])
                                                                if not opened.get(x)]}
                                           for c in s["acoustic_correlates"]],
                   "notes": s.get("notes") or ""}
            # in those two boxes everything is a letter but the ejective mark and the tie bars
            is_letter = sec in ("pulmonic", "vowels") or (
                sec in ("non_pulmonic", "other_symbols") and rec["id"] not in MARKS)
            rec["kind"] = "letter" if is_letter else "mark"
            rec["engine_today"] = letter_ability(s["symbol"], by_ipa, packs_of, tags_of) if is_letter \
                else mark_ability(rec, strings, n_tone_packs)
            # later phases fill these in; a symbol may only end as mapped, composed or created (R19e)
            rec["state"] = "MISSING"
            rec["proof"] = None
            records.append(rec)

    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        ok = False
        print("DUPLICATE ids: %s" % [i for i, n in collections.Counter(ids).items() if n > 1])

    # an equivalent pair is one thing printed twice: count the things as well as the printed forms
    by_symbol = {r["symbol"]: r for r in records}
    by_id = {r["id"]: r for r in records}
    pairs = set()
    for r in records:
        e = r["equivalent_to"]
        if e:
            other = by_id.get(e) or by_symbol.get(e)
            if other is None:
                ok = False
                print("equivalent_to names nothing: %s -> %s" % (r["id"], e))
                continue
            r["equivalent_to"] = other["id"]
            pairs.add(frozenset((r["id"], other["id"])))
    counts = {"entries": len(records), "equivalent_pairs": len(pairs), "distinct": len(records) - len(pairs),
              "letters": sum(1 for r in records if r["kind"] == "letter"),
              "marks": sum(1 for r in records if r["kind"] == "mark"),
              "by_section": {sec: sum(1 for r in records if r["section"] == sec) for sec, _ in SECTIONS},
              "engine_today": dict(collections.Counter(r["engine_today"]["status"] for r in records)),
              "engine_today_by_section": {sec: dict(collections.Counter(
                  r["engine_today"]["status"] for r in records if r["section"] == sec)) for sec, _ in SECTIONS},
              "acoustic_correlates": dict(collections.Counter(
                  c["provenance"] for r in records for c in r["acoustic_correlates"]))}

    out = {"what": "The IPA checklist: every symbol the official chart prints, with its definition, expected "
                   "acoustic correlates and what the engine does for it today. Written by build_ipa_checklist.py "
                   "from research/*.json; do not edit by hand.",
           "chart": {"title": "The International Phonetic Alphabet", "issue": "(c) 2026 IPA",
                     "revision": "IPA Chart revised to 2015/2005",
                     "url": "https://www.internationalphoneticassociation.org/content/ipa-chart",
                     "licence": "CC BY-SA 4.0 (the chart is cited here, not reproduced)",
                     "local_copy": "IPA_Kiel.pdf in the human's Downloads folder, SHA-256 "
                                   "C8203013C676B243959072234526D60B874851D0509A00FD7528F4E56C706787 (not in the repository)",
                     "as_read_by_each_helper": charts},
           "engine_today_means": {
               "already": "letters: at least one of seven IBM modules (enus, engb, dede, eses, esus, frfr, itit: the ones whose phones "
                          "engine/espeak_phonemes.py gives an IPA value for) has the sound as a phone of its own; frca, jajp and "
                          "plpl were not consulted, so a sound only they have is under-reported. marks: the modules do it themselves.",
               "partly": "letters: no module has it; the shipped packs say it as another module phone, reshaped by the "
                         "accent layer, made by the accent layer, or as it is (a plain substitution). marks: a mechanism "
                         "covers some cases, or some sounds so marked are defined one by one.",
               "absent": "nothing in the shipped product says it.",
               "unknown": "not determined in Phase 0.",
               "note": "Read from code and pack data. Nothing was rendered or measured: this says what the engine "
                       "attempts, not whether the result is right."},
           "counts": counts, "symbols": records, "problems": problems}
    with open(os.path.join(HERE, "IPA_CHECKLIST.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")

    write_md(out, records, counts, problems)
    write_refs(refs)

    print("entries %d = %s" % (counts["entries"], " + ".join("%d %s" % (counts["by_section"][s], s) for s, _ in SECTIONS)))
    print("equivalent pairs %d, distinct %d; letters %d, marks %d" % (
        counts["equivalent_pairs"], counts["distinct"], counts["letters"], counts["marks"]))
    print("engine today: %s" % counts["engine_today"])
    for sec, _ in SECTIONS:
        print("  %-16s %s" % (sec, counts["engine_today_by_section"][sec]))
    print("acoustic correlates by provenance: %s" % counts["acoustic_correlates"])
    print("references: %d opened, %d named but not opened" % (
        sum(1 for r in refs if r.get("read")), sum(1 for r in refs if not r.get("read"))))
    print("agrees with the PDF and with Unicode: %s" % ("yes" if ok else "NO"))
    return 0 if ok else 1


def cell(text):
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def write_md(out, records, counts, problems):
    L = []
    w = L.append
    w("# IPA checklist")
    w("")
    w("Written by `build_ipa_checklist.py` from `research/*.json`. Do not edit by hand; `IPA_CHECKLIST.json` is the same thing for programs.")
    w("")
    w("**Chart:** The International Phonetic Alphabet, the issue marked \"© 2026 IPA\", \"IPA Chart revised to 2015/2005\" "
      "(<https://www.internationalphoneticassociation.org/content/ipa-chart>), CC BY-SA 4.0. The chart is cited, not reproduced. "
      "The IPA says the 2018 and 2020 issues were this same revision, and that it has re-issued the chart every year since 2025. "
      "Every section was also checked symbol by symbol against the human's copy, `IPA_Kiel.pdf`.")
    w("")
    w("## The count")
    w("")
    w("| Section | Entries |")
    w("|---|---|")
    for sec, title in SECTIONS:
        w("| %s | %d |" % (title, counts["by_section"][sec]))
    w("| **All** | **%d** |" % counts["entries"])
    w("")
    w("**%d entries**: one for every representation the chart prints. %d of them are a second printed form of the same thing "
      "(each level and contour tone is printed as a diacritic and as a tone letter: 10; the ring above for voiceless beside the "
      "ring below: 1; the tie bar above beside the tie bar below: 1), which leaves **%d distinct things**: %d letters and %d marks."
      % (counts["entries"], counts["equivalent_pairs"], counts["distinct"], counts["letters"],
         counts["distinct"] - counts["letters"]))
    w("")
    w("Against the rough figure of 155: Wikipedia's article on the IPA (read 2026-10-05) counts 107 letters, 31 diacritics and "
      "17 suprasegmental signs. The 107 letters are the same 107 here (59 pulmonic, 10 clicks and implosives, 10 other symbols, "
      "28 vowels) and the 31 diacritics are the 31 rows of the diacritics table. The difference is in the rest: this checklist "
      "also has the ejective mark and the tie bar, which the chart prints outside the diacritics table, and counts 9 "
      "suprasegmentals and 14 tones and word accents (23) where that article counts 17; which of them it leaves out it does not say. "
      "Then 12 more for the second printed forms. 107 + 31 + 1 + 1 + 23 = 163 distinct; 163 + 12 = 175 entries.")
    w("")
    w("## What the engine does today")
    w("")
    w("Read from code and from the maps of the 145 packs. **Nothing was rendered or measured**: this says what the engine attempts, not whether it is right.")
    w("")
    for k in ("already", "partly", "absent", "unknown"):
        w("- **%s**: %s" % (k, out["engine_today_means"][k]))
    w("")
    w("| Section | already | partly | absent | unknown |")
    w("|---|---|---|---|---|")
    for sec, title in SECTIONS:
        c = counts["engine_today_by_section"][sec]
        w("| %s | %d | %d | %d | %d |" % (title, c.get("already", 0), c.get("partly", 0), c.get("absent", 0), c.get("unknown", 0)))
    c = counts["engine_today"]
    w("| **All** | **%d** | **%d** | **%d** | **%d** |" % (c.get("already", 0), c.get("partly", 0), c.get("absent", 0), c.get("unknown", 0)))
    w("")
    w("Every symbol's state for the coverage script is `MISSING` until a later phase maps it, composes it or creates it and proves it by rendering and measuring (R19).")
    w("")
    for sec, title in SECTIONS:
        rs = [r for r in records if r["section"] == sec]
        w("## %s (%d)" % (title, len(rs)))
        w("")
        w("| # | Symbol | Codepoints | IPA no. | Name (IPA; Unicode) | Definition | Engine today | How |")
        w("|---|---|---|---|---|---|---|---|")
        for r in rs:
            name = "; ".join(x for x in (r["ipa_name"], r["unicode_name"]) if x)
            w("| %d | %s | %s | %s | %s | %s | **%s** | %s |" % (
                r["n"], cell(show(r["symbol"])), " ".join(r["codepoints"]), cell(r["ipa_number"]), cell(name),
                cell(r["articulatory"]) + (" (same thing as %s)" % r["equivalent_to"] if r["equivalent_to"] else ""),
                r["engine_today"]["status"], cell(r["engine_today"]["detail"])))
        w("")
        w("### Expected acoustic correlates: %s" % title.lower())
        w("")
        w("`literature` = found in a source the helper opened (named in brackets; `IPA_REFERENCES.md`). `recalled-unverified` = "
          "stated from memory with no opened source: to be verified before any value is used (it counts as `estimated`, playbook 1.5).")
        w("")
        for r in rs:
            w("- **%s** (%s):" % (show(r["symbol"]), r["articulatory"]))
            for c in r["acoustic_correlates"]:
                src = (" [" + ", ".join(x.split(":", 1)[1] for x in c["refs"]) + "]") if c["refs"] else ""
                if c["quoted_unopened"]:
                    src += " (as quoted there from %s, not opened)" % ", ".join(x.split(":", 1)[1] for x in c["quoted_unopened"])
                w("  - %s (`%s`)%s" % (c["text"].replace("\n", " "), c["provenance"], src))
        w("")
    w("## What the helpers could not verify")
    w("")
    for sec, title in SECTIONS:
        w("### %s" % title)
        w("")
        for p in problems:
            if p["section"] == sec:
                w("- %s" % p["problem"].replace("\n", " "))
        w("")
    with open(os.path.join(HERE, "IPA_CHECKLIST.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


def write_refs(refs):
    L = ["# Sources of the IPA checklist", "",
         "Written by `build_ipa_checklist.py` from `research/*.json`. Accessed 2026-10-05 unless a row says otherwise. "
         "\"Opened\" says whether the helper fetched and read the source in its session; a source that was not opened is "
         "named only because another source quotes it, and nothing in the checklist rests on it directly.", "",
         "| Section | Id | Title | Author, year | URL | Licence | Opened | Used for |", "|---|---|---|---|---|---|---|---|"]
    for r in refs:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["section"], cell(r.get("id")), cell(r.get("title")),
            cell(", ".join(str(x) for x in (r.get("author"), r.get("year")) if x)),
            cell(r.get("url")), cell(r.get("licence")), "yes" if r.get("read") else "no", cell(r.get("used_for"))))
    with open(os.path.join(HERE, "IPA_REFERENCES.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
