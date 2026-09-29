"""Assemble languages/<tag>/ from freshly built engine modules.

For each language this copies openevv-<tag>-x86.dll and openevv-<tag>-x64.dll
into languages/<tag>/ and writes language.ini, asking the 64-bit module itself
for its eight presets' names and parameters (through ctypes, the way any
program would call it), so the pack describes the engine it carries.

    python engine/make_language_packs.py <built-modules-dir> [tag ...]

<built-modules-dir> holds one folder per tag, as engine/build_modules.sh
leaves them. Needs a 64-bit Python.
"""
import ctypes
import os
import shutil
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# tag: (name, ECI id, SAPI Language attribute, locale, code page, order, experimental)
# A name that begins "Module:" is a module that is no language: it says the
# phones it is given, for the languages eSpeak NG reads, and its pack is
# hidden.
LANGS = {
    "dedx": ("Module: international, from German", 0x00040000, "407", "de-DE", 65001, 910, False),
    "itix": ("Module: international, from Italian", 0x00050000, "410", "it-IT", 65001, 911, False),
    "esex": ("Module: international, from Castilian Spanish", 0x00020000, "C0A;40A", "es-ES", 65001, 912, False),
    "esux": ("Module: international, from Latin American Spanish", 0x00020001, "80A;540A", "es-MX", 65001, 913,
             False),
    "engx": ("Module: international, from British English", 0x00010001, "809", "en-GB", 65001, 914, False),
    "enux": ("Module: international, from US English", 0x00010000, "409", "en-US", 65001, 915, False),
    "frfx": ("Module: international, from French", 0x00030000, "40C", "fr-FR", 65001, 916, False),
    "enus": ("US English", 0x00010000, "409", "en-US", 1252, 10, False),
    "engb": ("British English", 0x00010001, "809", "en-GB", 1252, 20, False),
    "dede": ("German", 0x00040000, "407", "de-DE", 1252, 30, False),
    "eses": ("Castilian Spanish", 0x00020000, "C0A;40A", "es-ES", 1252, 40, False),
    "esus": ("Latin American Spanish", 0x00020001, "80A;540A", "es-MX", 1252, 50, False),
    "frfr": ("French", 0x00030000, "40C", "fr-FR", 1252, 60, False),
    "frca": ("Canadian French", 0x00030001, "C0C", "fr-CA", 1252, 70, False),
    "itit": ("Italian", 0x00050000, "410", "it-IT", 1252, 80, False),
    "plpl": ("Polish", 0x00110000, "415", "pl-PL", 65001, 90, True),
    "jajp": ("Japanese", 0x00080000, "411", "ja-JP", 932, 100, False),
}

AGES = {3: "Child", 7: "Senior", 8: "Senior"}


def presets(dll_path, lang_id):
    lib = ctypes.WinDLL(dll_path)
    lib.eciNewEx.restype = ctypes.c_void_p
    lib.eciNewEx.argtypes = [ctypes.c_int]
    lib.eciGetVoiceName.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
    lib.eciGetVoiceParam.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.eciDelete.argtypes = [ctypes.c_void_p]
    h = lib.eciNewEx(lang_id)
    if not h:
        raise RuntimeError(f"{dll_path}: eciNewEx(0x{lang_id:x}) failed")
    out = []
    for n in range(1, 9):
        buf = ctypes.create_string_buffer(64)
        lib.eciGetVoiceName(h, n, buf)
        params = [lib.eciGetVoiceParam(h, n, p) for p in range(8)]
        out.append((buf.value.decode("latin-1"), params))
    lib.eciDelete(h)
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    if struct.calcsize("P") != 8:
        print("make_language_packs.py needs a 64-bit Python")
        return 2
    built = sys.argv[1]
    tags = sys.argv[2:] or [t for t in LANGS if os.path.isdir(os.path.join(built, t))]
    for tag in tags:
        name, lid, lcid, locale, cp, order, experimental = LANGS[tag]
        src = os.path.join(built, tag)
        dst = os.path.join(ROOT, "languages", tag)
        os.makedirs(dst, exist_ok=True)
        for arch in ("x86", "x64"):
            f = f"openevv-{tag}-{arch}.dll"
            shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
        voices = presets(os.path.join(dst, f"openevv-{tag}-x64.dll"), lid)
        lines = [
            f"; OpenEVV language pack: {name}.",
            "; Drop a folder like this one into %ProgramData%\\OpenEVV\\languages (or the",
            "; languages folder of the installation) and its voices appear in every SAPI5",
            "; program; delete the folder and they are gone. docs/LANGUAGES.md has the format.",
            "",
            "[Language]",
            f"Tag={tag}",
            f"Name={name}" + (" (experimental)" if experimental else ""),
            f"Id=0x{lid:08x}",
            f"LCID={lcid}",
            f"Locale={locale}",
            f"Codepage={cp}",
            f"Module32=openevv-{tag}-x86.dll",
            f"Module64=openevv-{tag}-x64.dll",
            f"Order={order}",
            f"Experimental={1 if experimental else 0}",
        ]
        if name.startswith("Module:"):
            lines += ["; lends its modules to the languages eSpeak NG reads, and is not a language itself",
                      "Hidden=1"]
        lines.append("")
        for n, (vname, params) in enumerate(voices, 1):
            lines += [
                f"[Voice{n}]",
                f"Name={vname}",
                f"Gender={'Female' if params[0] == 1 else 'Male'}",
                f"Age={AGES.get(n, 'Adult')}",
                "; gender, head size, pitch, inflection, roughness, breathiness, speed, volume",
                "Params=" + ",".join(str(p) for p in params),
                "",
            ]
        with open(os.path.join(dst, "language.ini"), "w", encoding="utf-8", newline="\r\n") as f:
            f.write("\n".join(lines))
        print(f"{tag}: {name}, voices: " + ", ".join(v[0] for v in voices))
    return 0


if __name__ == "__main__":
    sys.exit(main())
