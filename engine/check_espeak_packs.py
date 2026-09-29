"""Hold every eSpeak NG language pack to what its template's engine accepts.

For each pack this reads a text in the language -- its sample sentence, some
numbers and punctuation -- with OpenEvvFrontend, exactly as the engine host
would, and hands the result to the template's own module (the 64-bit one,
through its ECI exports). The module is then asked which phonemes it made of
it. An annotation the module could not read is spoken instead of obeyed --
backquote, bracket, full stop and all -- so any word the module did not take
as a pronunciation is a failure, and so is a text that came out as nothing.

A pack whose map gives the language sounds of its own (sounds.map) is held to
one thing more. The engine writes down which phone every stretch of speech
was and which sound the map meant it to be (EVV_ACCENT_TRACE), and a phone
the engine could not find in what the map said is one the module said
otherwise than it was given: more than a few of those and the sounds of the
language are being laid over the wrong phones.

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

# Where the engine writes what it made of each phone. The name is in the
# environment a checking process starts with: a module asks its C library,
# which looked at the environment when the process began and not since.
TRACE = os.environ.get("EVV_ACCENT_TRACE") or os.path.join(tempfile.gettempdir(),
                                                           "openevv-check-%d.tsv" % os.getpid())

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
            if (os.path.exists(os.path.join(langs, t, "sounds.map")) or
                os.path.exists(os.path.join(langs, t, "phonemes.map"))) and (not only or t in only)]
    failures = 0
    # each pack in a process of its own: a module that loops for ever on
    # something it was handed is a failure to report, not a check that hangs
    env = dict(os.environ)
    for tag in tags:
        env["EVV_ACCENT_TRACE"] = "%s-%s" % (TRACE, tag)
        try:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--one", fe, data, tag],
                               capture_output=True, timeout=120, env=env)
            out = r.stdout.decode("utf-8", "replace").strip()
            print(out.splitlines()[0] if out else "%-20s FAIL  no report: %s" % (tag, r.stderr.decode()[-300:]))
            if r.returncode != 0:
                failures += 1
        except subprocess.TimeoutExpired:
            print("%-20s FAIL  the module did not finish within two minutes: it hangs on this language" % tag)
            failures += 1
        try:
            os.remove(env["EVV_ACCENT_TRACE"])
        except OSError:
            pass
    print("%d packs checked, %d failed" % (len(tags), failures))
    return 1 if failures else 0


READ = [0]


def traced():
    """What the engine wrote down since this was last asked: (phones, those
    of them it could not place, the first few of those). The module holds
    the file open, so it is read on from where the last reading stopped."""
    if not os.path.exists(TRACE):
        return 0, 0, []
    phones, lost, which = 0, 0, []
    with open(TRACE, encoding="latin-1") as f:
        f.seek(READ[0])
        text = f.read()
        READ[0] = f.tell()
        for line in text.splitlines():
            c = line.rstrip("\n").split("\t")
            if len(c) < 10 or c[0] in ("#", "-"):
                continue
            phones += 1
            if c[5] == "-":
                lost += 1
                if len(which) < 4:
                    which.append(c[0])
    return phones, lost, which


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
        rc, ann, err = translate(fe, data, ini[("Frontend", "Voice")],
                                 os.path.join(langs, tag, ini.get(("Frontend", "Sounds"),
                                                                  ini.get(("Frontend", "Map"), "phonemes.map"))),
                                 text)
        checked += 1
        problems = []
        if rc != 0:
            problems.append("front-end failed: " + err.strip())
        words_in = ann.count("`[")
        if words_in == 0:
            problems.append("nothing came out")
        try:
            ann.encode("cp1252")
        except UnicodeEncodeError:
            problems.append("the front-end wrote what is not in the engine's character set")
            ann = ann.encode("cp1252", "replace").decode("cp1252")
        out = m.phonemes(ann) if ann else ""
        # every word the module read as a pronunciation comes back as one;
        # anything it read as text comes back as more
        words_out = out.count("`[")
        if words_out != words_in:
            # find the first word it would not take
            bad = None
            head = ann[:ann.find("{W")] if "{W" in ann else ""
            for w in re.findall(r"(?:\{W[^}]*\})?`\[[^\]]*\]", ann):
                if m.phonemes(head + w).count("`[") != 1:
                    bad = w
                    break
            problems.append("the module read %d words as %d%s" % (words_in, words_out,
                                                                  (", first refused: " + bad) if bad else ""))
        traced()
        samples = m.speak(ann) if ann else 0
        if ann and samples == 0:
            problems.append("no audio")
        phones, lost, which = traced()
        placed = ""
        if "{A " in ann:
            if phones == 0:
                problems.append("the engine wrote down no phones: the accent layer is not in this module")
            elif lost * 20 > phones:
                problems.append("%d of %d phones were not the ones the map gave (%s)" % (lost, phones,
                                                                                         " ".join(which)))
            placed = "%d phones, %d not placed" % (phones, lost)
        status = "FAIL" if problems else "ok"
        print("%-20s %-5s %-4s %6.2f s  %s  %s" % (tag, tpl, status, samples / 11025.0, placed,
                                                   "; ".join(problems)))
        if problems:
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
