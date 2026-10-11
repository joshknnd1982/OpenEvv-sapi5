"""Build the files of the packs in packs/ and compare them with languages/ (DESIGN.md 11.3, M1).

    python engine/packs/build_packs.py check [tag ...]     build every pack into a scratch folder; every file
                                                            must equal the one in languages/ (exit 1 if not)
    python engine/packs/build_packs.py build <out> [tag ...]  write the folders languages/<tag>/ would hold
    python engine/packs/build_packs.py build <out> --proposed <tag>   the same with the pack's proposed
                                                            overrides realised too (to measure them; never into languages/)
    python engine/packs/build_packs.py explain <tag> <dotted key>   which pack of the chain gave a value,
                                                            e.g. ini.Language.Name, sounds.s12, phonemes.@af:a
    python engine/packs/build_packs.py list                 every pack: parent, kind, lines

`check` also says which language folders have no pack and which packs have no folder.
Nothing under languages/ is written; the engine's modules (the DLLs) are not pack files.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import packlib as L  # noqa: E402

LANGS = os.path.join(ROOT, "languages")
GENERATED = ("language.ini", "sounds.map", "phonemes.map", "sample.txt")


def check(tags):
    folders = sorted(t for t in os.listdir(LANGS) if os.path.isfile(os.path.join(LANGS, t, "language.ini")))
    have = L.list_tags()
    tags = tags or have
    bad, n_files, n_bytes, kinds = [], 0, 0, {}
    for tag in tags:
        try:
            flat, _ = L.resolve(tag)
            files = L.compile_pack(flat)
        except L.PackError as e:
            bad.append("%s: %s" % (tag, e))
            continue
        kinds[flat["engine"].get("realization", "?")] = kinds.get(flat["engine"].get("realization", "?"), 0) + 1
        for name in GENERATED:
            path = os.path.join(LANGS, tag, name)
            exists = os.path.isfile(path)
            if name in files and not exists:
                bad.append("%s/%s: the pack makes it, the folder has none" % (tag, name))
            elif name not in files and exists:
                bad.append("%s/%s: the folder has it, the pack does not make it" % (tag, name))
            elif exists:
                want = open(path, "rb").read()
                n_files += 1
                n_bytes += len(want)
                if want != files[name]:
                    # a checkout may hold the other line ending: the same text is the same file
                    if want.replace(b"\r\n", b"\n") == files[name].replace(b"\r\n", b"\n"):
                        continue
                    bad.append("%s/%s: differs (pack %d bytes, folder %d bytes)" % (tag, name, len(files[name]), len(want)))
    print("packs checked: %d; files compared: %d (%d bytes); by realization: %s" % (
        len(tags), n_files, n_bytes, ", ".join("%s %d" % kv for kv in sorted(kinds.items()))))
    nofile = [t for t in folders if t not in have]
    if nofile and tags == have:
        print("language folders with no pack: %d: %s" % (len(nofile), " ".join(nofile)))
    gone = [t for t in have if t not in folders]
    if gone:
        print("packs with no folder in languages/: %d: %s" % (len(gone), " ".join(gone)))
    for b in bad:
        print("FAIL", b)
    print("check: %s" % ("every file identical to languages/" if not bad else "%d FAILED" % len(bad)))
    return 1 if bad else 0


def build(out, tags):
    proposed = "--proposed" in tags
    tags = [t for t in tags if t != "--proposed"]
    if proposed and os.path.normcase(os.path.realpath(out)).startswith(os.path.normcase(os.path.realpath(LANGS))):
        raise L.PackError("--proposed builds a scratch folder, never languages/")
    for tag in tags or L.list_tags():
        files = L.build(tag, out, include_proposed=proposed)
        print("%-22s %s" % (tag, ", ".join("%s %s" % (n, hashlib.sha256(d).hexdigest()[:10]) for n, d in files.items())))
    return 0


def listing():
    for tag in L.list_tags():
        d = L.read_pack(tag)
        flat, _ = L.resolve(tag)
        print("%-24s %-9s extends %-14s %-8s %5d sound lines %5d phoneme lines" % (
            tag, d["pack"]["kind"], d["pack"].get("extends") or "-", flat["engine"].get("realization", "?"),
            len(flat.get("sounds", {}).get("line", [])), len(flat.get("phonemes", {}).get("line", []))))
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "check":
            return check(rest)
        if cmd == "build":
            return build(rest[0], rest[1:])
        if cmd == "list":
            return listing()
        if cmd == "explain":
            print(L.explain(rest[0], rest[1]) or "no such value in %s" % rest[0])
            return 0
    except L.PackError as e:
        print("STOP:", e)
        return 2
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
