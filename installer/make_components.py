#!/usr/bin/env python3
"""Writes installer/generated/*.inc: the language choice of the installer.

installer/openevv.iss lets the person installing choose which languages to install. Each
language pack in languages/ is one Inno Setup component; the packs that only lend their engine
modules to other packs (Hidden=1 in language.ini) are installed when a language that speaks
with them is chosen, and only then. This script reads languages/*/language.ini and writes what
the installer script includes:

  types.inc       [Types]: the ready-made choices, and the list of tags the script checks
  components.inc  [Components]: one check box per language, in two groups
  files.inc       [Files]: each pack's files, tied to its component
  code.inc        the tables the [Code] section works from

Run it whenever a language pack is added, removed or renamed (build_all.bat packs does that):

  python installer/make_components.py          write the files
  python installer/make_components.py --check  say whether they are up to date (exit code 1 if not)

The installer script refuses to compile when languages/ holds a pack these files do not list,
so a forgotten run is found when the installer is built, not when somebody installs it.
"""
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LANGUAGES = os.path.join(ROOT, "languages")
OUT = os.path.join(HERE, "generated")

# The languages of the "English only" choice.
ENGLISH = ("enus", "engb")
VOICES_FALLBACK = 8
# The types of installation, in the order the wizard lists them (the combo box's item numbers).
TYPES = ("openevv", "english", "full", "custom")
# Setup removes the languages that are unchecked when it upgrades, so its standard warning, that
# "deselecting these components will not uninstall them", would be untrue.
NOWARN = "disablenouninstallwarning"


def read_ini(path):
    """{section: {key: value}} of a language.ini (UTF-8), keys lower-case."""
    data, section = {}, None
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in ";#":
                continue
            m = re.match(r"\[(.+)\]$", line)
            if m:
                section = m.group(1).strip().lower()
                data.setdefault(section, {})
            elif "=" in line and section is not None:
                k, v = line.split("=", 1)
                data[section][k.strip().lower()] = v.strip()
    return data


def read_packs():
    packs = []
    for tag in sorted(os.listdir(LANGUAGES)):
        ini = os.path.join(LANGUAGES, tag, "language.ini")
        if not os.path.isfile(ini):
            continue
        d = read_ini(ini)
        lang = d.get("language", {})
        voices = sum(1 for s in d if re.fullmatch(r"voice\d+", s)) or VOICES_FALLBACK
        packs.append({
            "dir": tag,                       # the folder, which is what the installer copies
            "tag": lang.get("tag", tag),
            "name": lang.get("name", tag),
            "template": lang.get("template", ""),
            "hidden": lang.get("hidden", "0") not in ("", "0"),
            "order": int(lang.get("order", "1000")),
            "voices": voices,
        })
    return packs


def sort_key_name(p):
    # "Maori" sorts with the Ms, not after the Zs
    plain = unicodedata.normalize("NFKD", p["name"]).encode("ascii", "ignore").decode()
    return (plain.casefold(), p["tag"])


def build():
    packs = read_packs()
    by_tag = {p["tag"].lower(): p for p in packs}
    for p in packs:
        if p["dir"].lower() != p["tag"].lower():
            sys.exit("languages\\%s: language.ini says Tag=%s; the installer needs the folder to be named by the tag" %
                     (p["dir"], p["tag"]))
        if not re.fullmatch(r"[a-z0-9_-]+", p["tag"]):
            sys.exit("languages\\%s: a tag is lower-case letters, digits, - and _ only" % p["dir"])
    hidden = [p for p in packs if p["hidden"]]
    visible = [p for p in packs if not p["hidden"]]
    for p in visible:
        if p["template"]:
            t = by_tag.get(p["template"].lower())
            if t is None or not t["hidden"]:
                sys.exit("languages\\%s: its template %s is %s; a template must be a pack that says Hidden=1, "
                         "or choosing this language would have to install another language as well" %
                         (p["dir"], p["template"], "not there" if t is None else "a language of its own"))
    native = sorted((p for p in visible if not p["template"]), key=lambda p: (p["order"], p["name"].casefold()))
    espeak = sorted((p for p in visible if p["template"]), key=sort_key_name)
    # Inno Setup names a component with letters, digits and underscores only
    for p in native:
        p["comp"] = "openevv\\" + p["tag"].replace("-", "_")
    for p in espeak:
        p["comp"] = "espeak\\" + p["tag"].replace("-", "_")
    for n in ENGLISH:
        if n not in by_tag or by_tag[n]["hidden"] or by_tag[n]["template"]:
            sys.exit("the English-only choice names %s, which is not one of the languages the engine speaks itself" % n)

    def voices(ps):
        return sum(p["voices"] for p in ps)

    def plural(n, one, many):
        return "%d %s" % (n, one if n == 1 else many)

    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
             10: "ten", 11: "eleven", 12: "twelve"}
    n_native = words.get(len(native), str(len(native)))
    english = [by_tag[t] for t in ENGLISH]
    every = native + espeak
    header = ("; Written by installer\\make_components.py from languages\\*\\language.ini. Do not edit it by hand:\n"
              "; run  python installer\\make_components.py  when a language pack is added, removed or renamed.\n")
    out = {}

    # ---- [Types] -------------------------------------------------------------------------------
    t = [header,
         "; The tags of every pack in languages\\. openevv.iss stops the build when languages\\ holds one\n"
         "; that is not in this list.\n",
         '#define LangTags "|' + "|".join(p["tag"] for p in packs) + '|"\n',
         "#define LangCount %d\n" % len(every),
         "#define LangNativeCount %d\n" % len(native),
         "#define LangEspeakCount %d\n" % len(espeak),
         "#define LangVoices %d\n" % voices(every),
         "\n",
         'Name: "openevv"; Description: "The %s OpenEVV languages (%s)"\n' % (n_native, plural(voices(native), "voice", "voices")),
         'Name: "english"; Description: "English only: US and British English (%s)"\n' % plural(voices(english), "voice", "voices"),
         'Name: "full"; Description: "All %d languages (%s)"\n' % (len(every), "{:,} voices".format(voices(every))),
         'Name: "custom"; Description: "Custom: choose the languages one by one"; Flags: iscustom\n']
    out["types.inc"] = "".join(t)

    # ---- [Components] --------------------------------------------------------------------------
    def types_of(p):
        if p["tag"] in ENGLISH:
            return "openevv english full"
        return "openevv full" if not p["template"] else "full"

    c = [header,
         'Name: "openevv"; Description: "The %s languages the OpenEVV engine speaks itself"; Types: openevv english full; Flags: %s\n' % (n_native, NOWARN)]
    for p in native:
        c.append('Name: "%s"; Description: "%s"; Types: %s; Flags: %s\n' % (p["comp"], p["name"], types_of(p), NOWARN))
    c.append('Name: "espeak"; Description: "The %d languages read by eSpeak NG and spoken by the engine"; Types: full; Flags: %s\n' % (len(espeak), NOWARN))
    for p in espeak:
        c.append('Name: "%s"; Description: "%s"; Types: full; Flags: %s\n' % (p["comp"], p["name"], NOWARN))
    out["components.inc"] = "".join(c)

    # ---- [Files] -------------------------------------------------------------------------------
    flags = "ignoreversion recursesubdirs createallsubdirs restartreplace uninsrestartdelete"
    f = [header,
         "; {#PackMask} is * in the real installer and language.ini in the accessibility probe, which\n"
         "; installs only each pack's ini file, so that the choice can be tested without the 216 MB.\n"]
    # In the order of the folders, as the installer has always copied them, so that a module pack comes
    # right after the language whose module it is made from (dedx after dede, engx after engb): the
    # modules are alike, and compressed together they take 3 MB less than compressed apart.
    for p in sorted(packs, key=lambda q: q["dir"].lower()):
        if p["hidden"]:
            users = [q["comp"] for q in espeak if q["template"].lower() == p["tag"].lower()]
            if not users:
                sys.exit("languages\\%s is a module pack that no language uses" % p["dir"])
            comps = " ".join(users)
        else:
            comps = p["comp"]
        f.append('Source: "..\\languages\\%s\\{#PackMask}"; DestDir: "{app}\\languages\\%s"; Components: %s; Flags: %s\n'
                 % (p["dir"], p["dir"], comps, flags))
    out["files.inc"] = "".join(f)

    # ---- [Code] --------------------------------------------------------------------------------
    def pas(s):
        return s.replace("'", "''")

    k = ["{ Written by installer\\make_components.py from languages\\*\\language.ini. Do not edit it by hand:\n"
         "  run  python installer\\make_components.py  when a language pack is added, removed or renamed. }\n",
         "const\n",
         "  { the numbers of the types of installation in the wizard's list }\n"] + \
        ["  Type%s = %d;\n" % (t.capitalize(), i) for i, t in enumerate(TYPES)] + [
         "\n",
         "{ the languages of the type that is English only }\n",
         "function IsEnglishTag(const Tag: String): Boolean;\n",
         "begin\n",
         "  Result := " + " or ".join("(Tag = '%s')" % t for t in ENGLISH) + ";\n",
         "end;\n",
         "\n",
         "procedure RegisterPacks;\n",
         "begin\n",
         "  { tag, component, template, name; a pack that only lends its modules has no component }\n"]
    for p in native + espeak:
        k.append("  AddPack('%s', '%s', '%s', '%s');\n" % (p["tag"], pas(p["comp"]), p["template"], pas(p["name"])))
    for h in sorted(hidden, key=lambda p: p["tag"]):
        k.append("  AddPack('%s', '', '', '%s');\n" % (h["tag"], pas(h["name"])))
    k.append("end;\n")
    out["code.inc"] = "".join(k)
    return out


def main():
    check = "--check" in sys.argv[1:]
    out = build()
    stale = []
    for name, text in sorted(out.items()):
        path = os.path.join(OUT, name)
        data = ("﻿" + text).replace("\n", "\r\n").encode("utf-8")
        old = open(path, "rb").read() if os.path.exists(path) else None
        if old != data:
            stale.append(name)
            if not check:
                os.makedirs(OUT, exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(data)
    if check:
        if stale:
            print("out of date: " + ", ".join("installer/generated/" + s for s in stale) +
                  "\nrun: python installer/make_components.py")
            return 1
        print("installer/generated is up to date")
        return 0
    print("wrote %s" % (", ".join(stale) if stale else "nothing: already up to date"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
