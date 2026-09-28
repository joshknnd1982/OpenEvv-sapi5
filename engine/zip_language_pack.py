"""Package language packs for download.

    python engine/zip_language_pack.py <tag> [<tag> ...] [--out DIR]

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


def main():
    args = sys.argv[1:]
    out = os.path.join(ROOT, "output")
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
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
