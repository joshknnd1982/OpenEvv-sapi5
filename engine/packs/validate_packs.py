"""The authenticity validator: a dialect or accent pack documents what it claims (playbook Phase 7,
steps 4 and 7; R14). docs/tts-extension/AUTHENTICITY.md explains each rule.

    python engine/packs/validate_packs.py [tag ...]   every dialect and accent pack, or those named
    python engine/packs/validate_packs.py --selftest  planted faults, each of which must be rejected

A pack of kind "dialect" or "accent" is REJECTED unless:

  M1  [meta] variety, region and speaker_group are given (who and where the pack is meant to sound like)
  M2  [meta] sources lists at least one registered source id (ipa/sources.toml) that was opened, and
      nothing else but those and the reader it was generated from ("eSpeak NG voice <voice>")
  M3  [meta] recordings is present: a list of the recording sets measured ("<source id>/<speaker>"),
      empty only when nothing was measured; every set it names belongs to a registered source
  M4  [meta] date is the date the metadata was last checked, YYYY-MM-DD
  M5  [meta] status = { level = 1..5, validated_by = "...", date = "..." }; level 5 (native-validated)
      only with a named reviewer and a date
  M6  [meta] licence is given

and, for any pack (anti-caricature, AUTHENTICITY.md):

  A1  every override value of a dialect or accent is `measured`, `literature`, `derived` or
      `approximate`: a dialect's feature is never `estimated` or `created` (it must rest on a
      descriptive source or on measured data)
  A2  its `ref` is a registered source id that was opened
  A3  a `measured` value is the value its evidence file holds for that sound and formant (or length),
      within 2 per cent: no measured feature is pushed further than the speakers went (the evidence is
      looked for in the folder of the pack that gave the override)
  A4  the pack still builds with every override realised (a ratio beyond 50 to 200 per cent of the
      module's phone is refused there)

Not checked, stated (AUTHENTICITY.md, section 5): the `[sounds]` lines of a legacy pack carry no
provenance of their own; they are the generator's, from the reader named in `sources`. A change made
by hand to a dialect's sound must be an `[[override]]`, which these rules do check.
"""
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import packlib as L  # noqa: E402
import tomlio  # noqa: E402

SOURCES = os.path.join(ROOT, "ipa", "sources.toml")
DIALECT_KINDS = ("dialect", "accent")
DIALECT_TAGS = ("measured", "literature", "derived", "approximate")
EXAGGERATION = 0.02


def registry(path=SOURCES):
    return tomlio.load(path).get("source", {})


def _source_id(s):
    return s.split("/")[0].split(":")[0]


def problems(tag, root=None, sources=None):
    """-> a list of what is wrong with the pack (empty: accepted)."""
    sources = registry() if sources is None else sources
    out = []
    try:
        flat, _ = L.resolve(tag, root)
    except L.PackError as e:
        return ["the pack does not load: %s" % e]
    kind = flat["pack"]["kind"]
    meta = flat.get("meta", {})
    if kind in DIALECT_KINDS:
        for k in ("variety", "region", "speaker_group"):
            if not (isinstance(meta.get(k), str) and meta[k].strip()):
                out.append("M1 [meta] %s is missing" % k)
        reg = [s for s in meta.get("sources", []) if s in sources and sources[s].get("opened")]
        if not reg:
            out.append("M2 [meta] sources names no registered, opened source (ipa/sources.toml): %s"
                       % (meta.get("sources") or "none"))
        reader = "eSpeak NG voice %s" % flat.get("ini", {}).get("Frontend", {}).get("Voice", "")
        other = [s for s in meta.get("sources", []) if s not in reg and s != reader]
        if other:
            out.append("M2 [meta] sources names what is neither a registered, opened source nor the pack's reader: %s"
                       % other)
        if not isinstance(meta.get("recordings"), list):
            out.append("M3 [meta] recordings is missing (a list; [] when nothing was measured)")
        else:
            for r in meta["recordings"]:
                if not isinstance(r, str) or _source_id(r) not in sources:
                    out.append("M3 [meta] recordings: %r is not of a registered source" % (r,))
        if not (isinstance(meta.get("date"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["date"])):
            out.append("M4 [meta] date is missing or not YYYY-MM-DD")
        st = meta.get("status")
        if not isinstance(st, dict) or not isinstance(st.get("level"), int) or not 1 <= st["level"] <= 5 \
                or not isinstance(st.get("validated_by"), str) or not isinstance(st.get("date"), str):
            out.append('M5 [meta] status is missing or not { level = 1..5, validated_by = "...", date = "..." }')
        elif st["level"] == 5 and not (st["validated_by"].strip() and st["date"].strip()):
            out.append("M5 [meta] status level 5 (native-validated) needs a named reviewer and a date")
        if not (isinstance(meta.get("licence"), str) and meta["licence"].strip()):
            out.append("M6 [meta] licence is missing")
    _, origin = L.resolve(tag, root)
    for o in flat.get("override", {}).values():
        values = sorted(o.get("formants", {}).items()) + ([("duration", o["duration"])] if "duration" in o else [])
        for k, v in values:
            field = "override.%s.%s" % (o["sound"], "duration" if k == "duration" else "formants." + k)
            folder = os.path.dirname(L.pack_path(origin.get(field, origin.get("override.%s" % o["sound"], tag)), root))
            where = "override %s %s" % (o["sound"], k)
            if kind in DIALECT_KINDS and v["tag"] not in DIALECT_TAGS:
                out.append("A1 %s is %s: a dialect's feature rests on a source or a measurement" % (where, v["tag"]))
            if v.get("ref") and not (v["ref"] in sources and sources[v["ref"]].get("opened")):
                out.append("A2 %s cites %r, not a registered, opened source" % (where, v["ref"]))
            if kind in DIALECT_KINDS and v["tag"] in ("literature", "derived", "approximate") and not v.get("ref"):
                out.append("A2 %s (%s) cites no source" % (where, v["tag"]))
            if v["tag"] == "measured":
                path = os.path.join(folder, v["evidence"])
                try:
                    with open(path, encoding="utf-8") as f:
                        e = json.load(f)["sounds"][o["sound"]][k]
                    ev = e["target_ms"] if k == "duration" else e["target_hz"]
                except (OSError, KeyError, ValueError):
                    out.append("A3 %s: its evidence %s holds no target for it" % (where, v["evidence"]))
                    continue
                if abs(v["v"] - ev) > EXAGGERATION * ev:
                    out.append("A3 %s is %.0f, its measurement %.0f (more than %d%% apart)" % (
                        where, v["v"], ev, 100 * EXAGGERATION))
    if flat.get("override"):
        try:
            L.compile_pack(flat, include_proposed=True)
        except L.PackError as e:
            out.append("A4 the overrides cannot be realised: %s" % e)
    return out


def validate(tags, root=None):
    sources = registry()
    tags = tags or [t for t in L.list_tags(root)
                    if L.read_pack(t, root)["pack"]["kind"] in DIALECT_KINDS or L.read_pack(t, root).get("override")]
    rejected = 0
    for tag in tags:
        p = problems(tag, root, sources)
        print("%-22s %s" % (tag, "accepted" if not p else "REJECTED (%d)" % len(p)))
        for x in p:
            print("    " + x)
        rejected += bool(p)
    print("validate: %d packs, %d accepted, %d rejected" % (len(tags), len(tags) - rejected, rejected))
    return 1 if rejected else 0


GOOD = '''
[pack]
tag = "zz-x-test"
name = "Test dialect"
kind = "dialect"
format = 1
[meta]
variety = "a test variety"
region = "nowhere"
speaker_group = "one adult man"
sources = ["hillenbrand1995"]
recordings = ["hillenbrand1995/m01"]
date = "2026-10-11"
licence = "MIT"
status = { level = 2, validated_by = "", date = "" }
[engine]
reader = "espeak:xx/zz"
template = "engx"
realization = "legacy"
[files]
eol = "lf"
[ini.Language]
Tag = "zz-x-test"
Name = "Test dialect"
Template = "engx"
[ini.Frontend]
Voice = "xx/zz"
Sounds = "sounds.map"
[sounds]
line = [
  { kind = "directive", name = "template", value = "engx" },
  { kind = "sound", id = "s1", keys = { dur = "80" }, note = "u" },
  { kind = "map", name = "@zz:u:", to = "u=s1" },
]
[[override]]
sound = "ʉː"
phonemes = ["@zz:u:"]
state = "proposed"
[override.formants.f2]
v = 1600.0
tag = "measured"
ref = "hillenbrand1995"
recordings = ["hillenbrand1995/m01/uw"]
n = 12
speakers = 1
evidence = "measured/test.json"
[override.duration]
v = 100.0
tag = "measured"
ref = "hillenbrand1995"
recordings = ["hillenbrand1995/m01/uw"]
n = 12
speakers = 1
evidence = "measured/test.json"
'''


def selftest():
    sources = registry()
    work = tempfile.mkdtemp(prefix="validate_packs_")
    try:
        def case(name, text, expect):
            d = os.path.join(work, name, "zz-x-test")
            os.makedirs(os.path.join(d, "measured"))
            with open(os.path.join(d, "pack.toml"), "w", encoding="utf-8") as f:
                f.write(text)
            with open(os.path.join(d, "measured", "test.json"), "w", encoding="utf-8") as f:
                json.dump({"sounds": {"ʉː": {"f2": {"target_hz": 1600.0}, "duration": {"target_ms": 100.0}}}}, f)
            p = problems("zz-x-test", os.path.join(work, name), sources)
            ok = (not p) if expect is None else any(x.startswith(expect) for x in p)
            print("  %-34s %-9s %s" % (name, "accepted" if not p else "rejected", "pass" if ok else "FAIL %s" % p))
            return ok
        cases = [
            ("complete pack", GOOD, None),
            ("no variety", GOOD.replace('variety = "a test variety"\n', ""), "M1"),
            ("no region", GOOD.replace('region = "nowhere"\n', ""), "M1"),
            ("no speaker group", GOOD.replace('speaker_group = "one adult man"\n', ""), "M1"),
            ("an unregistered source", GOOD.replace('sources = ["hillenbrand1995"]', 'sources = ["my memory"]'), "M2"),
            ("an unregistered source beside one", GOOD.replace('sources = ["hillenbrand1995"]',
                                                             'sources = ["hillenbrand1995", "a film"]'), "M2"),
            ("no recordings", GOOD.replace('recordings = ["hillenbrand1995/m01"]\n', ""), "M3"),
            ("no date", GOOD.replace('date = "2026-10-11"\n', ""), "M4"),
            ("no status", GOOD.replace('status = { level = 2, validated_by = "", date = "" }\n', ""), "M5"),
            ("level 5 with no reviewer", GOOD.replace("level = 2", "level = 5"), "M5"),
            ("no licence", GOOD.replace('licence = "MIT"\n', ""), "M6"),
            ("an estimated dialect feature", GOOD.replace('tag = "measured"', 'tag = "estimated"'), "A1"),
            ("a measured value, source unknown", GOOD.replace('ref = "hillenbrand1995"', 'ref = "nobody"'), "A2"),
            ("a measured value exaggerated 10%", GOOD.replace("v = 1600.0", "v = 1760.0"), "A3"),
            ("a measured length exaggerated 20%", GOOD.replace("v = 100.0", "v = 120.0"), "A3"),
            ("a value no module could say", GOOD.replace("v = 1600.0", "v = 3500.0"), "A4"),
        ]
        ok = all([case(*c) for c in cases])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("validate selftest: %s" % ("%d of %d pass" % (len(cases), len(cases)) if ok else "FAILED"))
    return ok


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if a and a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    sys.exit(validate(a))
