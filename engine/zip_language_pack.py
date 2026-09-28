"""Package language packs for download.

    python engine/zip_language_pack.py <tag> [<tag> ...] [--out DIR]
    python engine/zip_language_pack.py --espeak [--out DIR]

The second puts every pack read by eSpeak NG into one zip. Such a pack needs
the eSpeak NG front-end and data that the OpenEVV SAPI5 installer puts in, and
its template language installed.

Zips languages/<tag> into DIR (default output/) as
OpenEVV-language-<tag>-<version>.zip, with the pack's folder at the top of the
zip. A user installs it with OpenEVV Configuration's "Add a language pack"
button, or by extracting it into %ProgramData%\\OpenEVV\\languages.
"""
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def version():
    with open(os.path.join(ROOT, "src", "common", "version.h"), encoding="utf-8") as f:
        return re.search(r'EVV_VERSION_STRING "([^"]+)"', f.read()).group(1)


def is_espeak_pack(tag):
    with open(os.path.join(ROOT, "languages", tag, "language.ini"), encoding="utf-8-sig") as f:
        return "[Frontend]" in f.read()


def main():
    args = sys.argv[1:]
    out = os.path.join(ROOT, "output")
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    if args == ["--espeak"]:
        # every language read by eSpeak NG, in one zip: each is a folder of
        # its own inside it, and "Add a language pack" installs them all
        os.makedirs(out, exist_ok=True)
        tags = sorted(t for t in os.listdir(os.path.join(ROOT, "languages"))
                      if os.path.isfile(os.path.join(ROOT, "languages", t, "language.ini")) and is_espeak_pack(t))
        path = os.path.join(out, f"OpenEVV-eSpeak-NG-languages-{version()}.zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for tag in tags:
                src = os.path.join(ROOT, "languages", tag)
                for base, _dirs, files in os.walk(src):
                    for name in sorted(files):
                        full = os.path.join(base, name)
                        z.write(full, os.path.join(tag, os.path.relpath(full, src)))
        print(f"{len(tags)} eSpeak NG language packs: {path} ({os.path.getsize(path) // 1024} KB)")
        return 0
    if not args:
        print(__doc__)
        return 2
    os.makedirs(out, exist_ok=True)
    for tag in args:
        src = os.path.join(ROOT, "languages", tag)
        if not os.path.isfile(os.path.join(src, "language.ini")):
            print(f"{tag}: no language pack at {src}")
            return 1
        path = os.path.join(out, f"OpenEVV-language-{tag}-{version()}.zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for base, _dirs, files in os.walk(src):
                for name in sorted(files):
                    full = os.path.join(base, name)
                    z.write(full, os.path.join(tag, os.path.relpath(full, src)))
        print(f"{tag}: {path} ({os.path.getsize(path) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
