"""Rewrite a pack so that it holds only what differs from its parent (`extends`), and prove it.

    python engine/packs/make_child.py <child tag> <parent tag> [--keep-over 0.6] [--dry-run]

The child's finished files (parent chain resolved, then the child) must equal what the flat child
built before; if they do not, or if the delta is not smaller than --keep-over of the flat file, the
pack is left as it was. Lines are matched by key (engine/packs/packfmt.py), in order, so a line the
parent has and the child has too, unchanged, is not written again.
"""
import argparse
import copy
import difflib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import packfmt as F  # noqa: E402
import packlib as L  # noqa: E402
import tomlio  # noqa: E402

HEADER = """\
# OpenEVV pack: {tag}, extends {parent}: only what differs from {parent} is written here
# (docs/tts-extension/DESIGN.md 6.3). `python engine/packs/build_packs.py explain {tag} <key>` says
# which pack of the chain a value of the finished pack comes from.
"""


def lines_delta(parent, child):
    pk, ck = [F.line_key(x) for x in parent], [F.line_key(x) for x in child]
    sm = difflib.SequenceMatcher(None, pk, ck, autojunk=False)
    remove, line = [], []
    ops = sm.get_opcodes()
    for n, (tag, i1, i2, j1, j2) in enumerate(ops):
        if tag == "equal":
            for a, b in zip(parent[i1:i2], child[j1:j2]):
                if a != b:
                    line.append(dict(b))
        else:
            remove += pk[i1:i2]
            for j in range(j1, j2):
                e = dict(child[j])
                if n != len(ops) - 1:  # the last block of the child goes at the end of what is left: no anchor needed
                    e["after"] = ck[j - 1] if j > 0 else "^"
                line.append(e)
    # a key removed and written again elsewhere is a move: the remove list may name it once
    out = {}
    if remove:
        out["remove"] = remove
    if line:
        out["line"] = line
    return out


def table_delta(parent, child, path, removes):
    out = {}
    for k, v in child.items():
        if isinstance(v, dict) and isinstance(parent.get(k), dict):
            d = table_delta(parent[k], v, path + [k], removes)
            if d:
                out[k] = d
        elif parent.get(k) != v or k not in parent:
            out[k] = copy.deepcopy(v)
    for k in parent:
        if k not in child:
            removes.append(".".join(path + [k]))
    return out


def child_of(child_flat, parent_flat, tag, parent):
    removes = []
    d = {"pack": {"tag": tag, "name": child_flat["pack"]["name"], "kind": child_flat["pack"]["kind"],
                  "extends": parent, "format": L.FORMAT}}
    for sec in ("meta", "engine", "files", "ini", "sample"):
        if sec in child_flat:
            t = table_delta(parent_flat.get(sec, {}), child_flat[sec], [sec], removes)
            if t:
                d[sec] = t
    for sec in ("sounds", "phonemes"):
        if sec in child_flat:
            t = lines_delta(parent_flat.get(sec, {"line": []})["line"], child_flat[sec]["line"])
            if t:
                d[sec] = t
    if removes:
        d["remove"] = removes
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("child")
    ap.add_argument("parent")
    ap.add_argument("--keep-over", type=float, default=0.6)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cpath = L.pack_path(a.child)
    cflat, _ = L.resolve(a.child)
    if cflat["pack"].get("extends"):
        print("%s already extends %s" % (a.child, cflat["pack"]["extends"]))
        return 0
    pflat, _ = L.resolve(a.parent)
    want = L.compile_pack(cflat)
    d = child_of(cflat, pflat, a.child, a.parent)
    text = tomlio.dumps(d, HEADER.format(tag=a.child, parent=a.parent))
    old = open(cpath, "rb").read()
    ratio = len(text.encode("utf-8")) / len(old)
    # prove it in a scratch folder: the parent's chain, the new child
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp()
    try:
        for t in [x["pack"]["tag"] for x in L.chain_of(a.parent)] + [a.child]:
            os.makedirs(os.path.join(tmp, t), exist_ok=True)
            src = cpath if t == a.child else L.pack_path(t)
            shutil.copy(src, os.path.join(tmp, t, "pack.toml"))
        with open(os.path.join(tmp, a.child, "pack.toml"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        try:
            got = L.compile_pack(L.resolve(a.child, tmp)[0])
        except L.PackError as e:
            print("%-22s STOP %s" % (a.child, e))
            return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if got != want:
        print("%-22s extends %-6s NOT IDENTICAL, left as it was (%s)" % (
            a.child, a.parent, ", ".join(k for k in want if got.get(k) != want[k])))
        return 1
    if ratio > a.keep_over:
        print("%-22s extends %-6s identical but %.0f%% of the flat file: left flat" % (a.child, a.parent, ratio * 100))
        return 0
    if not a.dry_run:
        with open(cpath, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print("%-22s extends %-6s identical, %6d -> %6d bytes (%.0f%%)%s" % (
        a.child, a.parent, len(old), len(text.encode("utf-8")), ratio * 100, "  (dry run)" if a.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
