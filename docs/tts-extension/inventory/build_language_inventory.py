#!/usr/bin/env python3
"""First-pass inventory of every language pack and the phonemes it uses (Phase 0, step 6).

Reads languages/<tag>/language.ini, and for each pack:

  native    a module of its own (IBM's language data): the phonemes the module declares,
            asked of openevv/tools/module/phonemes.py, which reads lang/<tag>/<tag>.statements
            and <tag>.settings
  template  a hidden module that lends itself to the languages eSpeak NG reads: the phonemes
            of the module it was made from (openevv/accents/<tag>/recipe)
  espeak    a language read by eSpeak NG: every line of the pack's sounds.map

It records what is there and makes no judgment of quality. Nothing is written except
languages.json beside this file. Run it from anywhere:

    python docs/tts-extension/inventory/build_language_inventory.py
"""

import configparser
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
LANGS = os.path.join(ROOT, "languages")
OPENEVV = os.path.join(ROOT, "openevv")

# evv_map_load in frontend/src/evv_map.c: a line that begins with none of these is a phoneme.
KEYWORDS = {"template", "style", "vowels", "glides", "secondary", "schwa", "words", "cluster", "onset",
            "accent", "sound", "tone", "whwords", "weaktones", "tonename", "says", "may"}

NATIVE_LINE = re.compile(r"^\s*(\d+)\s+(\S+)\s+(numbers (\d+)|no numbers)\s+(no rule of its own|(\S+)(?:\s+at (\S+))?)")


def read_ini(path):
    ini = configparser.ConfigParser(comment_prefixes=(";",), interpolation=None, strict=False)
    ini.optionxform = str
    with open(path, encoding="utf-8-sig") as f:
        ini.read_file(f)
    return ini


def split_comment(line):
    """A `#' at the start of a word begins a comment (strip_comment in evv_map.c)."""
    m = re.search(r"(^|\s)#", line)
    if not m:
        return line.rstrip(), ""
    return line[:m.start()].rstrip(), line[m.end():].strip()


def read_sounds_map(path):
    out = {"header": {}, "accent": None, "says": [], "sounds": {}, "tones": [], "weaktones": [],
           "tonenames": [], "whwords": 0, "phonemes": []}
    table = None
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            raw = raw.rstrip("\r\n")
            m = re.match(r"#\s*eSpeak NG phoneme table (\S+)", raw)
            if m:
                table = m.group(1)
            body, comment = split_comment(raw)
            words = body.split()
            if not words:
                continue
            key, rest = words[0], words[1:]
            if key in ("template", "style", "schwa", "secondary", "words", "onset"):
                out["header"][key] = rest[0] if rest else ""
            elif key in ("vowels", "glides"):
                out["header"].setdefault(key, []).extend(rest)
            elif key == "cluster":
                out["header"].setdefault("clusters", []).append(rest)
            elif key == "accent":
                out["accent"] = " ".join(rest)
            elif key in ("says", "may"):
                out["says"].append({"kind": key, "phones": rest})
            elif key == "sound":
                out["sounds"][rest[0]] = {"def": " ".join(rest[1:]), "comment_ipa": comment}
            elif key == "tone":
                out["tones"].append({"id": rest[0], "def": " ".join(rest[1:])})
            elif key == "weaktones":
                out["weaktones"].extend(rest)
            elif key == "tonename":
                out["tonenames"].append(rest)
            elif key == "whwords":
                out["whwords"] += len([w for w in rest if w not in ("any", "first")])
            else:
                # phones as written: `t=s71' a phone and the sound it is meant to be, `<h=s19' a phone
                # the engine makes itself, `-' nothing said
                entry = {"key": key, "phones": [w for w in rest if w != "-"]}
                if key.startswith("@") and ":" in key:
                    entry["espeak_table"], entry["espeak_name"] = key[1:].split(":", 1)
                    entry["ipa"] = comment or None
                else:
                    entry["ipa"] = key      # a line that starts with IPA: any phoneme with that IPA
                    entry["by_ipa"] = True
                entry["section"] = table
                out["phonemes"].append(entry)
    return out


def linked_phonemes(tag):
    """A module with no tables as text (Japanese): the names of the phone statement's first field,
    read from the lifted C, lang/<tag>/delta_link_<tag>.c."""
    p = os.path.join(OPENEVV, "lang", tag, "delta_link_%s.c" % tag)
    if not os.path.exists(p):
        return None, "lang/%s has no tables as text and no delta_link_%s.c" % (tag, tag)
    text = open(p, encoding="utf-8", errors="replace").read()
    strings = dict(re.findall(r'static const char (s\d+)\[\] = "((?:[^"\\]|\\.)*)";', text))
    m = re.search(r"/\* phone \*/\s*static const char \*const v\d+_0\[\] = \{([^}]*)\}", text)
    if not m:
        return None, "no phone statement found in delta_link_%s.c" % tag
    names = [strings.get(s.strip(), "?") for s in m.group(1).split(",") if s.strip()]
    out = [{"index": i, "name": n, "settings_number": None, "rule": None, "locus_rule": None}
           for i, n in enumerate(names) if i > 0]      # the first name is the gap, as in the other modules
    return out, ("%s: %d phonemes declared in the phone statement of delta_link_%s.c (the module has no tables "
                 "as text); first name %r left out as the others' GAP is" % (tag, len(names), tag, names[0]))


def native_phonemes(tag):
    """What tools/module/phonemes.py says the module declares."""
    if not os.path.exists(os.path.join(OPENEVV, "lang", tag, "%s.statements" % tag)):
        return linked_phonemes(tag)
    env = dict(os.environ, PYTHONUTF8="1")
    r = subprocess.run([sys.executable, os.path.join(OPENEVV, "tools", "module", "phonemes.py"), tag],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    lines = r.stdout.splitlines()
    out = []
    notes = [l.strip() for l in lines[1:] if not NATIVE_LINE.match(l) and l.strip()]
    for line in lines[1:]:
        m = NATIVE_LINE.match(line)
        if m:
            out.append({"index": int(m.group(1)), "name": m.group(2),
                        "settings_number": int(m.group(4)) if m.group(4) else None,
                        "rule": m.group(6), "locus_rule": m.group(7)})
    return out, " ".join([lines[0].strip()] + notes) if lines else r.stderr.strip()


def recipe_template(tag):
    p = os.path.join(OPENEVV, "accents", tag, "recipe")
    if not os.path.exists(p):
        return None
    for line in open(p, encoding="utf-8"):
        w = line.split()
        if len(w) >= 2 and w[0] == "template":
            return w[1]
    return None


def main():
    packs = []
    for tag in sorted(os.listdir(LANGS)):
        ini_path = os.path.join(LANGS, tag, "language.ini")
        if not os.path.exists(ini_path):
            continue
        ini = read_ini(ini_path)
        lang = ini["Language"]
        pack = {"tag": tag, "name": lang.get("Name"), "locale": lang.get("Locale"), "lcid": lang.get("LCID"),
                "eci_language_id": lang.get("Id"), "experimental": lang.get("Experimental") == "1",
                "voices": [{"name": ini[s].get("Name"), "params": ini[s].get("Params")}
                           for s in ini.sections() if s.startswith("Voice")]}
        if "Frontend" in ini:
            pack["kind"] = "espeak"
            pack["template"] = lang.get("Template")
            pack["espeak_voice"] = ini["Frontend"].get("Voice")
            sm = read_sounds_map(os.path.join(LANGS, tag, ini["Frontend"].get("Sounds", "sounds.map")))
            pack["sounds_map"] = sm
            own = [p for p in sm["phonemes"] if not p.get("by_ipa")]
            pack["counts"] = {"phoneme_lines": len(sm["phonemes"]), "by_espeak_name": len(own),
                              "by_ipa": len(sm["phonemes"]) - len(own), "sounds": len(sm["sounds"]),
                              "tones": len(sm["tones"]),
                              "espeak_tables": sorted({p["espeak_table"] for p in own})}
        else:
            pack["kind"] = "template" if lang.get("Hidden") == "1" else "native"
            pack["modules"] = [lang.get("Module32"), lang.get("Module64")]
            source = tag
            if pack["kind"] == "template":
                source = recipe_template(tag)
                pack["made_from"] = source
            phonemes, note = native_phonemes(source)
            pack["phonemes_source"] = "openevv/lang/%s" % source
            pack["phonemes_note"] = note
            pack["phonemes"] = phonemes
            pack["counts"] = {"declared": len(phonemes) if phonemes is not None else None}
        packs.append(pack)

    kinds = {}
    for p in packs:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    templates = {}
    for p in packs:
        if p["kind"] == "espeak":
            templates[p["template"]] = templates.get(p["template"], 0) + 1
    out = {"what": "First-pass inventory of the language packs in languages/ and the phonemes each uses. "
                   "No quality judgments. Written by build_language_inventory.py.",
           "counts": {"pack_folders": len(packs), **kinds,
                      "languages": kinds.get("native", 0) + kinds.get("espeak", 0),
                      "espeak_packs_by_template": dict(sorted(templates.items(), key=lambda kv: -kv[1]))},
           "packs": packs}
    # one pack to a line, so that a change to one language is one line of a diff
    with open(os.path.join(HERE, "languages.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write('{"what": %s,\n "counts": %s,\n "packs": [\n' % (json.dumps(out["what"]), json.dumps(out["counts"])))
        f.write(",\n".join("  " + json.dumps(p, ensure_ascii=False, separators=(",", ":")) for p in packs))
        f.write("\n ]}\n")

    print(json.dumps(out["counts"], ensure_ascii=False, indent=1))
    print("%-6s %-9s %s" % ("tag", "kind", "phonemes"))
    for p in packs:
        if p["kind"] != "espeak":
            print("%-6s %-9s %s  (%s)" % (p["tag"], p["kind"], p["counts"]["declared"], p["phonemes_note"]))
    lines = [p["counts"]["by_espeak_name"] for p in packs if p["kind"] == "espeak"]
    sounds = [p["counts"]["sounds"] for p in packs if p["kind"] == "espeak"]
    print("espeak packs: %d; phoneme lines by eSpeak NG name per pack: min %d, max %d; sounds per pack: min %d, max %d; "
          "packs with tones: %d" % (len(lines), min(lines), max(lines), min(sounds), max(sounds),
                                    sum(1 for p in packs if p["kind"] == "espeak" and p["counts"]["tones"])))


if __name__ == "__main__":
    main()
