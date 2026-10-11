"""Write packs/<tag>/pack.toml for each folder of languages/ (DESIGN.md 11.3, stage M1).

The pack holds, as data, exactly what the folder holds: `realization = "legacy"` (the sound
definitions are the ones the generator wrote; the master table does not speak them yet). Nothing in
languages/ is read for anything but its text and nothing there is changed. The importer refuses to
write a pack whose build is not byte-identical to the folder it came from.

    python engine/packs/import_packs.py [--src languages] [--out packs] [--force] <tag> [<tag> ...]
    python engine/packs/import_packs.py --all
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import packfmt as F  # noqa: E402
import packlib as L  # noqa: E402
import tomlio  # noqa: E402

HEADER = """\
# OpenEVV pack: {tag}. Written by engine/packs/import_packs.py from languages/{tag}/ (stage M1,
# docs/tts-extension/DESIGN.md 11.3); engine/packs/packlib.py says what each part means.
# realization = "legacy": the sound lines below are the ones the generator wrote; edit freely, then
# `python engine/packs/build_packs.py check` says whether the folder in languages/ still agrees.
"""


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def pack_of(tag, src):
    d = os.path.join(src, tag)
    ini_text = read(os.path.join(d, "language.ini"))
    ini, eol = F.parse_ini(ini_text)
    lang, fe = ini["Language"], ini.get("Frontend", {})
    has_maps = os.path.isfile(os.path.join(d, "sounds.map"))
    out = {
        "pack": {"tag": tag, "name": lang["Name"], "kind": "dialect" if "-" in tag else "language", "format": L.FORMAT},
        "meta": {},
        "engine": {},
        "files": {"eol": "crlf" if eol == "\r\n" else "lf"},
        "ini": ini,
    }
    if has_maps:
        out["meta"]["sources"] = ["eSpeak NG voice %s" % fe["Voice"]]
        out["meta"]["licence"] = "per NOTICE.md"
        out["engine"] = {"reader": "espeak:" + fe["Voice"], "template": lang["Template"], "realization": "legacy"}
        sm, e1 = F.parse_map(read(os.path.join(d, "sounds.map")), "sounds")
        pm, e2 = F.parse_map(read(os.path.join(d, "phonemes.map")), "phonemes")
        assert e1 == e2 == eol, "%s: the files do not share a line ending" % tag
        out["sounds"] = {"line": sm}
        out["phonemes"] = {"line": pm}
        sample = read(os.path.join(d, "sample.txt"))
        assert sample.endswith(eol) and eol not in sample[:-len(eol)], "%s: sample.txt is not one line" % tag
        out["sample"] = {"text": sample[:-len(eol)]}
    else:
        out["meta"]["licence"] = "per NOTICE.md"
        out["engine"] = {"reader": "module", "realization": "module"}
        if lang.get("Hidden") == "1":
            out["meta"]["note"] = "a template module: lends its sounds to the languages eSpeak NG reads; not a language itself"
    if not out["meta"].get("note"):
        out["meta"]["note"] = "imported from languages/%s" % tag
    return out


def check_equal(tag, src, out_root):
    flat, _ = L.resolve(tag, out_root)
    files = L.compile_pack(flat)
    bad = []
    for name, data in files.items():
        want = open(os.path.join(src, tag, name), "rb").read()
        if want != data:
            bad.append(name)
    missing = [n for n in ("language.ini", "sounds.map", "phonemes.map", "sample.txt")
               if os.path.isfile(os.path.join(src, tag, n)) and n not in files]
    return bad + missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.join(ROOT, "languages"))
    ap.add_argument("--out", default=os.path.join(ROOT, "packs"))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true", help="write over a pack that is already there")
    ap.add_argument("tags", nargs="*")
    a = ap.parse_args()
    tags = a.tags or ([t for t in sorted(os.listdir(a.src)) if os.path.isfile(os.path.join(a.src, t, "language.ini"))]
                      if a.all else [])
    if not tags:
        ap.error("name the tags, or --all")
    failed = 0
    for tag in tags:
        path = L.pack_path(tag, a.out)
        if os.path.exists(path) and not a.force:
            print("%-22s already a pack (--force to write it again)" % tag)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = tomlio.dumps(pack_of(tag, a.src), HEADER.format(tag=tag))
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        bad = check_equal(tag, a.src, a.out)
        if bad:
            failed += 1
            os.remove(path)
            print("%-22s NOT IDENTICAL: %s (pack removed)" % (tag, ", ".join(bad)))
        else:
            print("%-22s %6d bytes of pack, identical to languages/%s" % (tag, len(text.encode("utf-8")), tag))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
