# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Start a new language pack from an eSpeak NG voice (ADDING_A_LANGUAGE.md, step 2).

    python engine/packs/new_language.py <voice> <tag> --out <pack folder> [--name "..."]
        e.g. new_language.py bnt/sw sw-x-evvdemo --out docs/tts-extension/examples/packs --name "Swahili (worked example)"

Runs the generator (engine/make_espeak_packs.py: the template whose phones come closest, the sounds,
melody and tones from eSpeak NG's phoneme tables and engine/profiles) in a scratch folder, gives the
result the tag and name asked for, and writes <pack folder>/<tag>/pack.toml with `kind = "language"`,
proved to build back to the generated files byte for byte (else nothing is written). It never writes
languages/ or packs/ unless --out says so, and refuses a tag that packs/ or languages/ already has.

Where the generator looks (the defaults are this machine's, PROJECT_STATE.md "Environment"):
    --espeak-src   ESPEAK_NG_SOURCE_DIR or %LOCALAPPDATA%/OpenEvvBuild/dev/espeak-ng (its test sentences)
    --frontend     EVV_STAGE's x64/OpenEvvFrontend.exe if there is one, else dist/x64/OpenEvvFrontend.exe
    --data         dist/espeak-ng-data
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import import_packs as I  # noqa: E402
import packlib as L  # noqa: E402
import tomlio  # noqa: E402

HEADER = """\
# OpenEVV pack: {tag}. Started by engine/packs/new_language.py from eSpeak NG's voice {voice}
# (ADDING_A_LANGUAGE.md); engine/packs/packlib.py says what each part means. realization = "legacy":
# the sound lines below are the ones the generator wrote; edit freely, then build it into a stage
# (`python engine/packs/build_packs.py build <stage>/languages {tag}`) and measure it.
"""


def defaults():
    stage = os.environ.get("EVV_STAGE", "")
    fe = os.path.join(stage, "x64", "OpenEvvFrontend.exe") if stage else ""
    return dict(
        espeak_src=os.environ.get("ESPEAK_NG_SOURCE_DIR") or os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "OpenEvvBuild", "dev", "espeak-ng"),
        frontend=fe if fe and os.path.isfile(fe) else os.path.join(ROOT, "dist", "x64", "OpenEvvFrontend.exe"),
        data=os.path.join(ROOT, "dist", "espeak-ng-data"))


def rename(folder, old, new, name):
    """The generated folder <old> becomes <new>: the folder, language.ini's Tag and, if asked, its Name."""
    src, dst = os.path.join(folder, old), os.path.join(folder, new)
    os.rename(src, dst)
    path = os.path.join(dst, "language.ini")
    text = open(path, encoding="utf-8", newline="").read()
    text, n = re.subn(r"^Tag=%s(\r?)$" % re.escape(old), lambda m: "Tag=%s%s" % (new, m.group(1)), text, 1, re.M)
    if n != 1:
        raise SystemExit("STOP: language.ini of %s has no line Tag=%s" % (old, old))
    if name:
        lang = text.index("[Language]")
        m = re.compile(r"^Name=.*?(\r?)$", re.M).search(text, lang)
        text = text[:m.start()] + "Name=%s%s" % (name, m.group(1)) + text[m.end():]
    open(path, "w", encoding="utf-8", newline="").write(text)


def crlf(folder):
    """The generator writes the maps with LF and language.ini with CRLF; the files in languages/ have CRLF
    throughout (git's checkout, .gitattributes `* text=auto`), and a pack keeps one line ending."""
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        text = open(path, encoding="utf-8", newline="").read()
        open(path, "w", encoding="utf-8", newline="").write(text.replace("\r\n", "\n").replace("\n", "\r\n"))


def main():
    d = defaults()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("voice", help="eSpeak NG voice id, e.g. bnt/sw (dist/espeak-ng-data/lang/<voice>)")
    ap.add_argument("tag", help="the new pack's tag (lower case; a private-use tag for a test: xx-x-name)")
    ap.add_argument("--out", required=True, help="the folder the pack goes in (packs, or an examples folder)")
    ap.add_argument("--name", default="")
    ap.add_argument("--espeak-src", default=d["espeak_src"])
    ap.add_argument("--frontend", default=d["frontend"])
    ap.add_argument("--data", default=d["data"])
    a = ap.parse_args()
    tag = a.tag
    if tag != tag.lower() or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", tag):
        raise SystemExit("STOP: a tag is lower-case letters, digits and hyphens: %r" % tag)
    for taken in (os.path.join(L.packs_dir(), tag), os.path.join(ROOT, "languages", tag), os.path.join(a.out, tag)):
        if os.path.exists(taken):
            raise SystemExit("STOP: %s exists already" % taken)
    if not os.path.isfile(os.path.join(a.data, "lang", *a.voice.split("/"))):
        raise SystemExit("STOP: no eSpeak NG voice %s in %s" % (a.voice, os.path.join(a.data, "lang")))
    vtag = os.path.basename(a.voice).lower()
    work = tempfile.mkdtemp(prefix="evv-newlang-")
    try:
        langs = os.path.join(work, "languages")
        p = subprocess.run([sys.executable, os.path.join(ROOT, "engine", "make_espeak_packs.py"),
                            "--espeak-src", a.espeak_src, "--frontend", a.frontend, "--data", a.data,
                            "--out", langs, vtag], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        print(p.stdout.strip())
        if p.returncode != 0 or not os.path.isfile(os.path.join(langs, vtag, "language.ini")):
            print(p.stderr.strip())
            raise SystemExit("STOP: the generator made no pack for %s (is it one openevv speaks natively? "
                             "make_espeak_packs.py OPENEVV_HAS)" % a.voice)
        rename(langs, vtag, tag, a.name)
        crlf(os.path.join(langs, tag))
        pack = I.pack_of(tag, langs)
        pack["pack"]["kind"] = "language"
        pack["meta"]["note"] = "started by engine/packs/new_language.py from eSpeak NG voice %s" % a.voice
        path = L.pack_path(tag, a.out)
        os.makedirs(os.path.dirname(path))
        text = tomlio.dumps(pack, HEADER.format(tag=tag, voice=a.voice))
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        bad = I.check_equal(tag, langs, a.out)
        if bad:
            shutil.rmtree(os.path.dirname(path))
            raise SystemExit("STOP: the pack does not build back to the generated files (%s); nothing written"
                             % ", ".join(bad))
        print("%s: %d bytes of pack in %s, identical to what the generator wrote (template %s)" % (
            tag, len(text.encode("utf-8")), os.path.dirname(path), pack["engine"]["template"]))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
