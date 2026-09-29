"""Make an OpenEVV language pack for every eSpeak NG language openevv lacks.

Each pack is languages/<tag>/ with language.ini, sounds.map and phonemes.map.
The pack has no engine module of its own: language.ini names a module as its
template, which speaks it, and names the eSpeak NG voice that reads the text.
OpenEvvFrontend reads the text with that voice and writes each word in the
template's phones, using sounds.map, which says besides how each sound of the
language differs from the phone that stands for it, what the language's
melody is and what its tones are (engine/accent/mapwriter.py, out of the
eSpeak NG phoneme tables and the language's profile in engine/profiles).

phonemes.map is the map of 1.1: the nearest phones and nothing more. It is
still written, and nothing of 1.2 reads it. A program of 1.1 that is still
running while 1.2 is installed over it goes on reading the file it knows.

A language openevv already has is left alone: the eSpeak NG voices for US and
British English, German, Castilian and Latin American Spanish, French,
Italian, Japanese and Polish are skipped, since openevv speaks those itself.
Their dialects are not: New York City English, Scottish English, Belgian
French and the rest are packs of their own, spoken with the openevv module of
their language.

The template for each language is the one whose phones come closest to the
sounds the language actually uses, weighted by how often it uses them: eSpeak
NG's own test sentences are read and every phoneme counted. Where eSpeak NG has
no test sentence for a language, the words of its dictionary are read instead.
engine/espeak_templates.txt can name a template by hand.

    python engine/make_espeak_packs.py --espeak-src ..\\espeak-ng ^
        --frontend <OpenEvvFrontend.exe> --data <espeak-ng-data> [tag ...]
"""
import argparse
import ctypes
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "accent"))
import espeak_phonemes as EP  # noqa: E402
import mapwriter  # noqa: E402
import prosody  # noqa: E402

# openevv's own languages: these eSpeak NG voices would be duplicates of them.
# Every other voice is a pack, the dialects of these languages included.
OPENEVV_HAS = {
    "gmw/en": "engb", "gmw/en-US": "enus", "gmw/de": "dede", "roa/es": "eses", "roa/es-419": "esus",
    "roa/fr": "frfr", "roa/it": "itit", "jpx/ja": "jajp", "zlw/pl": "plpl",
}

# Windows has no LCID for these; the nearest one it does have
LCID_FALLBACK = {
    "cmn": "zh-CN", "yue": "zh-HK", "hak": "zh-TW", "ltg": "lv-LV", "hyw": "hy-AM", "grc": "el-GR",
    "fa-latn": "fa-IR", "rup": "ro-RO", "pdc": "de-US", "sjn": None, "qya": None, "piqd": None,
    "jbo": None, "py": None, "qdb": None, "xex": None, "lfn": None, "io": None, "ia": None, "eo": None,
}
LOCALE_FALLBACK = {"cmn": "zh-CN", "yue": "zh-HK", "hak": "zh-TW"}


def read_voice(path, lang_root):
    v = {"file": path, "id": os.path.relpath(path, lang_root).replace("\\", "/"), "name": None,
         "languages": [], "status": None}
    for line in open(path, encoding="utf-8", errors="replace"):
        w = line.split("//")[0].split()
        if not w:
            continue
        if w[0] == "name":
            v["name"] = line.split(None, 1)[1].split("//")[0].strip()
        elif w[0] == "language" and len(w) > 1:
            v["languages"].append(w[1])
        elif w[0] == "status" and len(w) > 1:
            v["status"] = w[1]
        elif w[0] == "dictionary" and len(w) > 1:
            v["dictionary"] = w[1]
    v["code"] = (v["languages"][0] if v["languages"] else os.path.basename(path)).lower()
    v["dictionary"] = v.get("dictionary") or v["code"].split("-")[0]
    v["tag"] = os.path.basename(path).lower()
    return v


def all_voices(espeak_src):
    root = os.path.join(espeak_src, "espeak-ng-data", "lang")
    out = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            out.append(read_voice(os.path.join(dirpath, f), root))
    out.sort(key=lambda v: v["tag"])
    return out


def is_duplicate(v):
    return v["id"] in OPENEVV_HAS


# ---- sample text ---------------------------------------------------------------

def shell_tokens(src):
    """Enough of the shell to read eSpeak NG's test scripts."""
    bs = chr(92)
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in " \t":
            i += 1
        elif c == bs and i + 1 < n and src[i + 1] == "\n":
            i += 2
        elif c == "\n":
            out.append("\n"); i += 1
        elif c == "#" and (not out or out[-1] == "\n"):
            j = src.find("\n", i); i = n if j < 0 else j
        elif c == '"':
            j, buf = i + 1, ""
            while j < n and src[j] != '"':
                if src[j] == bs and j + 1 < n and src[j + 1] in '"$`' + bs:
                    buf += src[j + 1]; j += 2; continue
                buf += src[j]; j += 1
            out.append(buf); i = j + 1
        elif c == "'":
            j = src.find("'", i + 1); out.append(src[i + 1:j]); i = j + 1
        else:
            j = i
            while j < n and src[j] not in " \t\n":
                j += 1
            out.append(src[i:j]); i = j
    return out


def test_sentences(espeak_src):
    samples = {}
    for fn in ("language-pronunciation.test", "translate.test"):
        p = os.path.join(espeak_src, "tests", fn)
        if not os.path.exists(p):
            continue
        line = []
        for tok in shell_tokens(open(p, encoding="utf-8").read()) + ["\n"]:
            if tok == "\n":
                if len(line) >= 4 and line[0] in ("test_phon", "test_phon_ssml") and len(line[3]) > 3 \
                        and "<" not in line[3]:
                    samples.setdefault(line[1].lower(), []).append(line[3])
                line = []
            else:
                line.append(tok)
    return samples


def dictionary_words(espeak_src, dictionary, limit=4000):
    p = os.path.join(espeak_src, "dictsource", dictionary + "_list")
    words = []
    if not os.path.exists(p):
        return words
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.split("//")[0].strip()
        if not line or line[0] in "_?$.":
            continue
        w = line.split()[0]
        if w.startswith("(") or any(ch.isdigit() for ch in w):
            continue
        words.append(w)
        if len(words) >= limit:
            break
    return words


def rule_strings(espeak_src, dictionary):
    """The letters each of a language's spelling rules matches, run together
    four at a time into pseudo-words: text in the language's own script for
    one that has too few dictionary words to read."""
    p = os.path.join(espeak_src, "dictsource", dictionary + "_rules")
    out = []
    if not os.path.exists(p):
        return out
    in_group = False
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.split("//")[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("."):
            in_group = line.startswith(".group")
            continue
        if not in_group:
            continue
        rest = line.split(")", 1)[1] if ")" in line else line
        rest = rest.split("(", 1)[0]
        w = rest.split()
        if not w:
            continue
        m = "".join(ch for ch in w[0] if ch.isalpha())
        if m and not m.isascii() or (m and m.isalpha() and len(m) <= 4):
            out.append(m.lower())
    words = []
    for i in range(0, len(out), 4):
        words.append("".join(out[i:i + 4]))
    return words


def read_curated_samples():
    p = os.path.join(HERE, "espeak_samples.txt")
    out = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.startswith("#") or "\t" not in line:
                continue
            tag, text = line.rstrip("\n").split("\t", 1)
            out[tag.strip().lower()] = text.strip()
    return out


def letterish(ch):
    """A letter, or a mark that belongs to one: Devanagari's vowel signs and
    Arabic's harakat are marks, and a sentence is made of them too."""
    import unicodedata
    return ch.isalpha() or unicodedata.category(ch).startswith("M")


def script_of(ch):
    import unicodedata
    try:
        return unicodedata.name(ch).split()[0]
    except ValueError:
        return "?"


def pack_sample(v, samples, espeak_src, curated):
    """The sentence a pack speaks first: a curated one, else the longest of
    eSpeak NG's test sentences written in the language's own script -- some
    test lines are phoneme drills or English words -- trimmed to a sentence
    or two, else real words from its dictionary."""
    if v["tag"] in curated:
        return curated[v["tag"]]
    for key in (v["tag"], v["code"], v["code"].split("-")[0]):
        # sentences, not test vectors: mostly letters and spaces
        texts = [t for t in samples.get(key, []) if not any(ch in t for ch in "<>%")
                 and sum(1 for ch in t if letterish(ch) or ch.isspace()) >= 0.8 * len(t)]
        if not texts:
            continue
        import collections
        letters = collections.Counter(script_of(ch) for t in texts for ch in t if ch.isalpha())
        main = letters.most_common(1)[0][0] if letters else "LATIN"
        best = max(texts, key=lambda t: sum(1 for ch in t if ch.isalpha() and script_of(ch) == main))
        if sum(1 for ch in best if ch.isalpha()) < 12:
            continue
        best = " ".join(best.split())
        # a sentence or two
        cut, out = 0, ""
        for i, ch in enumerate(best):
            if ch in ".!?。！？।॥።؟" and i - cut > 0:
                out = best[:i + 1]
                if len(out) >= 100:
                    break
        return (out or best)[:400].strip()
    words = dictionary_words(espeak_src, v["dictionary"], limit=2000)
    words = [w for w in words if len(w) > 2 and all(ch.isalpha() or ch in "'-" for ch in w)][:10]
    if len(words) >= 5:
        return ", ".join(words) + "."
    # nothing to read but the numbers, which eSpeak NG reads in the language
    return "1, 2, 3, 4, 5, 6, 7, 8, 9, 10."


def sample_text(v, samples, espeak_src):
    for key in (v["tag"], v["code"], v["code"].split("-")[0]):
        if key in samples:
            text = "\n".join(samples[key])
            if sum(1 for ch in text if ch.isalpha()) >= 80:
                return text, "tests"
            # a phoneme drill or two: some of the dictionary's own words say more
            # about the language -- not too many, since a dictionary is mostly
            # the words the rules get wrong, loanwords among them
            words = [w for w in dictionary_words(espeak_src, v["dictionary"], limit=1500) if len(w) > 2][:300]
            return text + "\n" + ". ".join(words), "tests+dictionary"
    words = dictionary_words(espeak_src, v["dictionary"])
    if len(words) >= 300:
        return ". ".join(words), "dictionary"
    return ". ".join(words + rule_strings(espeak_src, v["dictionary"])), "rules"


# ---- Windows locale -------------------------------------------------------------

def lcid_for(code):
    code = code.lower()
    names = [code]
    parts = code.split("-")
    if len(parts) > 1:
        names.append("-".join(parts[:2]))
    names.append(parts[0])
    if code in LCID_FALLBACK:
        names = [LCID_FALLBACK[code]] if LCID_FALLBACK[code] else []
    elif parts[0] in LCID_FALLBACK:
        names = [LCID_FALLBACK[parts[0]]] if LCID_FALLBACK[parts[0]] else []
    try:
        f = ctypes.windll.kernel32.LocaleNameToLCID
        f.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32]
        f.restype = ctypes.c_uint32
    except Exception:
        return None
    for n in names:
        lcid = f(n, 0)
        if lcid and lcid not in (0x1000, 0x0c00, 0x0400, 0x0800):
            return lcid
    return None


def bcp47(code):
    parts = code.split("-")
    out = [parts[0]]
    for p in parts[1:]:
        if len(p) == 2 and p.isalpha():
            out.append(p.upper())
        elif len(p) == 4 and p.isalpha():
            out.append(p.title())
        else:
            out.append(p)
    return "-".join(out)


# ---- the packs -----------------------------------------------------------------------

def run_stats(frontend, data, voice, text):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write(text)
        tmp = f.name
    try:
        r = subprocess.run([frontend, "--data", data, "--voice", voice, "--stats", tmp],
                           capture_output=True, timeout=600)
        if r.returncode != 0:
            raise RuntimeError("%s: %s" % (voice, r.stderr.decode("utf-8", "replace").strip()))
        return json.loads(r.stdout.decode("utf-8"))
    finally:
        os.unlink(tmp)


def read_overrides():
    p = os.path.join(HERE, "espeak_templates.txt")
    out = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            w = line.split("#")[0].split()
            if len(w) >= 2:
                out[w[0].lower()] = w[1]
    return out


PRESETS = [
    ("Adult Male 1", "Male", "Adult"), ("Adult Female 1", "Female", "Adult"), ("Child 1", "Female", "Child"),
    ("Adult Male 2", "Male", "Adult"), ("Adult Male 3", "Male", "Adult"), ("Adult Female 2", "Female", "Adult"),
    ("Elderly Female 1", "Female", "Senior"), ("Elderly Male 1", "Male", "Senior"),
]


def template_voices(template_tag):
    """The eight presets as the template's own pack lists them."""
    ini = os.path.join(ROOT, "languages", template_tag, "language.ini")
    voices = {}
    if os.path.exists(ini):
        sec = None
        for line in open(ini, encoding="utf-8-sig"):
            line = line.strip()
            m = re.match(r"\[(Voice\d)\]", line)
            if m:
                sec = m.group(1)
                voices[sec] = {}
            elif sec and "=" in line and not line.startswith(";"):
                k, val = line.split("=", 1)
                voices[sec][k.strip()] = val.strip()
    return voices


def write_ini(path, v, t, lcid, order, sample_source):
    tv = template_voices(t.tag)
    lines = [
        "; OpenEVV language pack: %s, read by eSpeak NG and spoken by openevv's %s module" % (v["name"], t.name),
        "; with the language's own sounds, melody and tones.",
        "; Drop a folder like this one into %ProgramData%\\OpenEVV\\languages (or the",
        "; languages folder of the installation) and its voices appear in every SAPI5",
        "; program; delete the folder and they are gone. docs/LANGUAGES.md has the format.",
        "; Written by engine/make_espeak_packs.py.",
        "",
        "[Language]",
        "Tag=%s" % v["tag"],
        "Name=%s" % v["name"],
        "Id=0x%08X" % t.lang_id,
        "LCID=%X" % lcid if lcid else "LCID=1000",
        "Locale=%s" % bcp47(LOCALE_FALLBACK.get(v["code"], v["code"])),
        "Codepage=65001",
        "Template=%s" % mapwriter.CLONE.get(t.tag, t.tag),
        "Order=%d" % order,
        "Experimental=%d" % (1 if v.get("status") in ("testing", "immature") else 0),
        "",
        "[Frontend]",
        "; eSpeak NG reads the text; its phonemes are said with the template's phones,",
        "; each as the language's own sound (Sounds=). Map= is the map of 1.1, the",
        "; nearest phones only, for a program of 1.1 still running through an upgrade.",
        "Engine=espeak",
        "Voice=%s" % v["id"],
        "Map=phonemes.map",
        "Sounds=sounds.map",
        "",
    ]
    for n, (name, gender, age) in enumerate(PRESETS, 1):
        sec = "Voice%d" % n
        lines += ["[%s]" % sec, "Name=%s" % tv.get(sec, {}).get("Name", name),
                  "Gender=%s" % tv.get(sec, {}).get("Gender", gender), "Age=%s" % tv.get(sec, {}).get("Age", age)]
        if "Params" in tv.get(sec, {}):
            lines += ["; gender, head size, pitch, inflection, roughness, breathiness, speed, volume",
                      "Params=%s" % tv[sec]["Params"]]
        lines.append("")
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--espeak-src", required=True)
    ap.add_argument("--frontend", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "languages"))
    ap.add_argument("--report", default=None, help="write a JSON report of every choice here")
    ap.add_argument("tags", nargs="*")
    a = ap.parse_args()

    dump = subprocess.run([a.frontend, "--data", a.data, "--dump-phonemes"], capture_output=True, check=True)
    tables = dict((t["table"], t) for t in json.loads(dump.stdout.decode("utf-8")))
    samples = test_sentences(a.espeak_src)
    curated = read_curated_samples()
    overrides = read_overrides()
    voices = [v for v in all_voices(a.espeak_src) if not is_duplicate(v)]
    if a.tags:
        voices = [v for v in voices if v["tag"] in a.tags]
    report = []
    for order, v in enumerate(voices):
        text, source = sample_text(v, samples, a.espeak_src)
        stats = run_stats(a.frontend, a.data, v["id"], text)
        best, scored = EP.choose_template(stats)
        chosen = overrides.get(v["tag"], best)
        t = EP.TEMPLATES[chosen]
        counts = {}
        for s in stats:
            counts[s["table"]] = counts.get(s["table"], 0) + s["count"]
        table_names = sorted(counts, key=lambda k: -counts[k])
        dst = os.path.join(a.out, v["tag"])
        os.makedirs(dst, exist_ok=True)
        EP.write_map(os.path.join(dst, "phonemes.map"), t, table_names, tables, stats, v["id"], v["name"])
        made = mapwriter.write_map(os.path.join(dst, "sounds.map"), v["tag"], chosen, table_names, tables, stats,
                                   v["id"], v["name"], prosody.load_profile(v["tag"]))
        lcid = lcid_for(v["code"])
        write_ini(os.path.join(dst, "language.ini"), v, t, lcid, 200 + order, source)
        with open(os.path.join(dst, "sample.txt"), "w", encoding="utf-8", newline="\r\n") as f:
            f.write(pack_sample(v, samples, a.espeak_src, curated) + "\n")
        report.append({"tag": v["tag"], "name": v["name"], "voice": v["id"], "template": chosen,
                       "module": made["clone"], "sounds": made["sounds"], "melody": made["kind"],
                       "question": made["question"], "tones": made["tones"], "unsaid": made["unsaid"],
                       "automatic": best, "sample": source, "lcid": lcid, "tables": table_names,
                       "scores": [(c, round(s, 3)) for s, c in scored]})
        print("%-22s %-5s %-34s %3d sounds %2d tones %-5s %-9s %s%s" % (
            v["tag"], made["clone"], v["name"][:34], made["sounds"], made["tones"], made["kind"],
            made["question"], source, "" if chosen == best else "  (automatic: %s)" % best))
    if a.report:
        json.dump(report, open(a.report, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%d packs written to %s" % (len(report), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
