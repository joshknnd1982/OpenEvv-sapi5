# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Mechanical checks of README.md (playbook Phase 10, step 2b.6); a few seconds, so the doctor runs it.

    python engine/check_readme.py              links, paths, version, the MIT wording, line endings
    python engine/check_readme.py --commands   and every Python script the README names answers --help

  - every relative link `[..](path)` and every repository path written in backquotes exists in the
    tree (a placeholder such as `<tag>`, an installed path such as `%ProgramData%\\...`, a GitHub page
    such as `../../releases`, and build output such as `build_x64\\...` or `output\\` are not tree paths
    and are skipped, the last named in the output);
  - the version the README names ("version x.y.z", "in x.y.z") equals src/common/version.h's;
  - no line says that all files, or everything in the repository, is under the MIT licence;
  - the file keeps CRLF line endings throughout, as it had.
With --commands, each `.py` the README names (in a path or inside a command line) is run with --help
when its text handles --help or uses argparse (a script without it could act instead of answering, so
it is listed as not run).
Exit 0 when every check passes.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILT = ("build_x64", "build_x86", "build_frontend_", "output")
NOT_PATHS = ("tts-ext/", "espeak/", "openevv/enus")   # a branch; the installer's component names
RUNTIME = {"settings.ini"}                            # written on the user's computer, not in the tree
LINK = re.compile(r"\]\(([^)\s]+)\)")
TICK = re.compile(r"`([^`\s]+)`")
FALSE_MIT = re.compile(r"\b(all|every)\s+(the\s+)?(files?|of the files|of this repository|code in this repository)\b[^.]{0,40}\bMIT\b"
                       r"|\bMIT\b[^.]{0,30}\b(all|every)\s+files?\b"
                       r"|\beverything\b[^.]{0,80}\bMIT\b", re.I)
# a line that states the limit itself ("not every file ... is") is the honest form, not the claim
MIT_LIMIT = re.compile(r"not every file|not all files|except|LICENCE_AUDIT|own work", re.I)


def tree_path(p):
    p = p.replace("\\", "/").split("#")[0].rstrip("/.,:;")
    if not p or p.startswith(("http:", "https:", "mailto:", "../", "%", "/", "-")) or re.match(r"^[A-Za-z]:", p):
        return None
    if any(c in p for c in "<>*?{}$|=\"'(") or p.startswith(".") or p.startswith(NOT_PATHS) or p in RUNTIME:
        return None
    if "/" not in p and not re.search(r"\.(md|py|bat|cmd|txt|json|toml|pdf|ini|map|iss|ps1|exe|dll|h|cpp)$", p):
        return None
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--commands", action="store_true")
    a = ap.parse_args()
    raw = open(os.path.join(ROOT, "README.md"), "rb").read()
    text = raw.decode("utf-8")
    problems, built, checked = [], set(), set()
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
    names = {f.rsplit("/", 1)[-1] for f in files}
    dirs = {f.rsplit("/", 1)[0] for f in files if "/" in f}
    for d in list(dirs):
        while "/" in d:
            d = d.rsplit("/", 1)[0]
            dirs.add(d)

    def exists(p):
        # a whole path; or a bare name, which the README uses beside the folder it lives in (`DECISIONS.md`
        # after docs/tts-extension/), found anywhere in the tree; or the tail of a real path (`harness/README.md`)
        if os.path.exists(os.path.join(ROOT, p)):
            return True
        if "/" not in p:
            return p in names
        return any(f.endswith("/" + p) for f in files) or any(d.endswith("/" + p) for d in dirs)

    for m in list(LINK.finditer(text)) + list(TICK.finditer(text)):
        p = tree_path(m.group(1))
        if p is None or p in checked:
            continue
        checked.add(p)
        if p.startswith(BUILT):
            built.add(p)
        elif not exists(p):
            problems.append("missing path: " + p)
    ver = re.search(r'EVV_VERSION_STRING "([^"]+)"', open(os.path.join(ROOT, "src", "common", "version.h")).read()).group(1)
    named = set(re.findall(r"\b(?:version|in|In)\s+(\d+\.\d+\.\d+)\b", text))
    old = sorted(v for v in named if v != ver and tuple(map(int, v.split("."))) > tuple(map(int, ver.split("."))))
    if ver not in named:
        problems.append("the README never names version %s (version.h)" % ver)
    for v in old:
        problems.append("the README names version %s, later than version.h's %s" % (v, ver))
    for n, line in enumerate(text.splitlines(), 1):
        if FALSE_MIT.search(line) and not MIT_LIMIT.search(line):
            problems.append("line %d may claim every file is MIT: %s" % (n, line.strip()[:120]))
    lf = raw.count(b"\n") - raw.count(b"\r\n")
    if lf:
        problems.append("%d lines end in LF only (the file is CRLF)" % lf)
    ran = []
    if a.commands:
        py = sys.executable
        scripts = set()
        blocks = [l for l in text.splitlines() if l.startswith("    ") and not l.lstrip().startswith(("-", "|"))]
        for span in re.findall(r"`([^`]+)`", text) + blocks:  # whole command lines too, not only paths
            for tok in span.split():
                tok = tok.replace("\\", "/").strip("\"'")
                if not tok.endswith(".py"):
                    continue
                hits = [tok] if tok in files else [f for f in files if f.endswith("/" + tok)]
                if len(hits) == 1:
                    scripts.add(hits[0])
                else:
                    problems.append("script %s: %s" % (tok, "not in the tree" if not hits else "ambiguous: " + ", ".join(hits)))
        for p in sorted(scripts):
            src = open(os.path.join(ROOT, p), encoding="utf-8", errors="replace").read()
            if "argparse" not in src and "--help" not in src:
                ran.append("not run (no --help): " + p)
                continue
            r = subprocess.run([py, os.path.join(ROOT, p), "--help"], cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120)
            first = (r.stdout.strip().splitlines() or [""])[0][:70]
            ran.append("exit %d  %s  %s" % (r.returncode, p, first))
            if r.returncode != 0:
                problems.append("--help failed: %s (exit %d)" % (p, r.returncode))
    print("readme: %d tree paths checked, %d build outputs named (%s), version %s, CRLF %s" % (
        len(checked) - len(built), len(built), ", ".join(sorted(built)) or "none", ver, "kept" if not lf else "BROKEN"))
    for line in ran:
        print("  " + line)
    for p in problems:
        print("  PROBLEM " + p)
    print("check: %s (%d problems)" % ("FAILED" if problems else "pass", len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
