"""Hold every eSpeak NG language pack to what its template's engine accepts.

For each pack this reads a text in the language -- its sample sentence, some
numbers and punctuation -- with OpenEvvFrontend, exactly as the engine host
would, and hands the result to the template's own module (the 64-bit one,
through its ECI exports). The module is then asked which phonemes it made of
it. An annotation the module could not read is spoken instead of obeyed --
backquote, bracket, full stop and all -- so any word the module did not take
as a pronunciation is a failure, and so is a text that came out as nothing.

    python engine/check_espeak_packs.py <OpenEvvFrontend.exe> <espeak-ng-data> [tag ...]
"""
import ctypes
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CB = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p)


class Module(object):
    def __init__(self, dll, lang_id):
        L = self.lib = ctypes.WinDLL(dll)
        L.eciNewEx.restype = ctypes.c_void_p
        L.eciNewEx.argtypes = [ctypes.c_int]
        L.eciAddText.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        for n in ("eciSynthesize", "eciSynchronize", "eciClearInput", "eciDelete"):
            getattr(L, n).argtypes = [ctypes.c_void_p]
        L.eciSetParam.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        L.eciRegisterCallback.argtypes = [ctypes.c_void_p, CB, ctypes.c_void_p]
        L.eciSetOutputBuffer.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        L.eciGeneratePhonemes.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        self.h = L.eciNewEx(lang_id)
        self.buf = (ctypes.c_short * 4096)()
        self.pbuf = ctypes.create_string_buffer(1 << 20)
        self.samples = 0
        self.phon = []
        self.cb = CB(self._cb)
        L.eciRegisterCallback(self.h, self.cb, None)
        L.eciSetOutputBuffer(self.h, 4096, self.buf)
        L.eciSetParam(self.h, 1, 1)  # annotations

    def _cb(self, h, msg, param, data):
        if msg == 0:
            self.samples += param
        elif msg == 1:
            self.phon.append(self.pbuf.raw[:param])
        return 1

    def phonemes(self, text):
        L = self.lib
        self.phon = []
        L.eciSetParam(self.h, 0, 1)
        L.eciAddText(self.h, text.encode("cp1252"))
        L.eciGeneratePhonemes(self.h, len(self.pbuf), self.pbuf)
        L.eciClearInput(self.h)
        L.eciSetParam(self.h, 0, 0)
        return b"".join(self.phon).replace(b"\x08", b"").decode("cp1252", "replace")

    def speak(self, text):
        L = self.lib
        self.samples = 0
        L.eciSetParam(self.h, 0, 0)
        L.eciAddText(self.h, text.encode("cp1252"))
        L.eciSynthesize(self.h)
        L.eciSynchronize(self.h)
        return self.samples


def read_ini(path):
    out, sec = {}, None
    for line in open(path, encoding="utf-8-sig"):
        line = line.strip()
        if line.startswith("["):
            sec = line.strip("[]")
        elif "=" in line and not line.startswith(";"):
            k, v = line.split("=", 1)
            out[(sec, k.strip())] = v.strip()
    return out


def translate(fe, data, voice, mapf, text):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write(text)
        tmp = f.name
    try:
        r = subprocess.run([fe, "--data", data, "--voice", voice, "--map", mapf, "--file", tmp],
                           capture_output=True, timeout=120)
        return r.returncode, r.stdout.decode("utf-8", "replace").strip(), r.stderr.decode("utf-8", "replace")
    finally:
        os.unlink(tmp)


EXTRA = " 0 1 2 3 7 10 25 100 1999 2026. ( ) , ; : ! ?"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[0] == "--one":
        return check(argv[1], argv[2], set(argv[3:]))
    fe, data = argv[0], argv[1]
    only = set(argv[2:])
    langs = os.path.join(ROOT, "languages")
    tags = [t for t in sorted(os.listdir(langs))
            if os.path.exists(os.path.join(langs, t, "phonemes.map")) and (not only or t in only)]
    failures = 0
    # each pack in a process of its own: a module that loops for ever on
    # something it was handed is a failure to report, not a check that hangs
    for tag in tags:
        try:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--one", fe, data, tag],
                               capture_output=True, timeout=120)
            out = r.stdout.decode("utf-8", "replace").strip()
            print(out.splitlines()[0] if out else "%-20s FAIL  no report: %s" % (tag, r.stderr.decode()[-300:]))
            if r.returncode != 0:
                failures += 1
        except subprocess.TimeoutExpired:
            print("%-20s FAIL  the module did not finish within two minutes: it hangs on this language" % tag)
            failures += 1
    print("%d packs checked, %d failed" % (len(tags), failures))
    return 1 if failures else 0


def check(fe, data, only):
    langs = os.path.join(ROOT, "languages")
    modules = {}
    failures = 0
    checked = 0
    for tag in sorted(os.listdir(langs)):
        ini_path = os.path.join(langs, tag, "language.ini")
        if not os.path.exists(ini_path) or (only and tag not in only):
            continue
        ini = read_ini(ini_path)
        if ("Frontend", "Voice") not in ini:
            continue
        tpl = ini[("Language", "Template")]
        if tpl not in modules:
            tini = read_ini(os.path.join(langs, tpl, "language.ini"))
            modules[tpl] = Module(os.path.join(langs, tpl, tini[("Language", "Module64")]),
                                  int(tini[("Language", "Id")], 0))
        m = modules[tpl]
        sample = ""
        sp = os.path.join(langs, tag, "sample.txt")
        if os.path.exists(sp):
            sample = open(sp, encoding="utf-8-sig").read().strip()
        text = (sample or ini[("Language", "Name")]) + EXTRA
        rc, ann, err = translate(fe, data, ini[("Frontend", "Voice")], os.path.join(langs, tag, "phonemes.map"),
                                 text)
        checked += 1
        problems = []
        if rc != 0:
            problems.append("front-end failed: " + err.strip())
        words_in = ann.count("`[")
        if words_in == 0:
            problems.append("nothing came out")
        out = m.phonemes(ann) if ann else ""
        # every word the module read as a pronunciation comes back as one;
        # anything it read as text comes back as more
        words_out = out.count("`[")
        if words_out != words_in:
            # find the first word it would not take
            bad = None
            for w in re.findall(r"`\[[^\]]*\]", ann):
                if m.phonemes(w).count("`[") != 1:
                    bad = w
                    break
            problems.append("the module read %d words as %d%s" % (words_in, words_out,
                                                                  (", first refused: " + bad) if bad else ""))
        samples = m.speak(ann) if ann else 0
        if ann and samples == 0:
            problems.append("no audio")
        status = "FAIL" if problems else "ok"
        print("%-20s %-5s %-4s %6.2f s  %s" % (tag, tpl, status, samples / 11025.0, "; ".join(problems)))
        if problems:
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
