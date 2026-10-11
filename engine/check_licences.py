# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""The licence audit: every tracked file in exactly one licence class, by a rule (playbook Phase 10, step 2).

    python engine/check_licences.py                 the classes, their counts, and every check below
    python engine/check_licences.py --list <class>  the files of one class
    python engine/check_licences.py --rules         every rule, in order, with how many files it took

The rules are tried in order and the first that matches a file decides its class, so a file is in
exactly one class; a file no rule matches is "unclassified" and fails the check, as does a rule that
matches nothing (a stale path). A rule is a path pattern (`*` within a folder, `**` across folders)
and, for packs only, a pattern of the file's content: a pack whose `pack.toml` holds `[sounds]` or
`[phonemes]` carries lines written from eSpeak NG's phoneme tables, which are GPL (NOTICE.md).

Two more checks, so the headers cannot claim what the audit does not:
  - a file outside the class "mit-here" or "mit-openevv" that says `SPDX-License-Identifier: MIT`
    fails (MIT claimed over somebody else's work);
  - a code file of this project's own (`.py .cpp .h .sh .cmd .bat .iss .ps1`, class "mit-here",
    outside openevv/, whose own rules govern it) with no `SPDX-License-Identifier` line in its first
    five lines is listed, and fails with --headers.

docs/tts-extension/LICENCE_AUDIT.md explains each class. Exit 0 when every check passes.
"""
import argparse
import re
import subprocess
import sys
from collections import Counter, OrderedDict

CLASSES = OrderedDict([
    ("mit-here", "MIT, written by this project (LICENSE)"),
    ("mit-openevv", "MIT, upstream openevv's own work (openevv/LICENSE)"),
    ("ibm", "IBM's language data and the modules built from it: not licensed here (NOTICE.md, openevv/NOTICE)"),
    ("gpl", "GPL-3.0-or-later: eSpeak NG, the front-end, its data and what is written from its phoneme tables; Praat through Parselmouth"),
    ("bestspeech", "adapted from the BestSpeech SAPI 5 wrapper: its author's terms (NOTICE.md)"),
    ("mixed-binary", "a binary built from MIT files and BestSpeech-derived files: both sets of terms"),
    ("rendered", "speech rendered by the engine (IBM's language data at work), with test text: not MIT-licensed here"),
    ("sentences", "test sentences: Common Voice (CC0 1.0) and Tatoeba (CC BY 2.0 FR), each sentence's source recorded"),
    ("cc0", "the community pronunciation dictionary: CC0 1.0"),
    ("cc-by-sa", "the IPA chart: CC BY-SA 4.0, International Phonetic Association"),
    ("unicode", "Unicode Character Database files: Unicode License v3"),
    ("cmu", "CMU ARCTIC speaker awb: CMU's own notice (free for any purpose, notice kept)"),
])

PACK_DATA = re.compile(r"^\[(sounds|phonemes)\]", re.M)

# (class, path patterns, content pattern or None, why). First match wins.
RULES = [
    ("mit-here", ["third_party/cmu_arctic/README.md"], None, "this project's description of the corpus"),
    ("cmu", ["third_party/cmu_arctic/**"], None, "the corpus, unchanged"),
    ("cc-by-sa", ["IPA_Kiel.pdf", "docs/tts-extension/inventory/ipa_chart_images/*"], None, "the IPA's chart and its official images"),
    ("unicode", ["docs/tts-extension/inventory/unicode/*"], None, "UnicodeData.txt, Blocks.txt and their licence"),
    ("cc0", ["dictionaries/community/*", "dist/docs/community-dictionary-*.txt"], None, "IBMTTSDictionaries, byte for byte"),
    ("gpl", ["frontend/**", "dist/x64/OpenEvvFrontend.exe", "dist/x86/OpenEvvFrontend.exe", "dist/espeak-ng-data/**",
             "dist/docs/eSpeak-NG-*.txt"], None, "the eSpeak NG front-end and data"),
    ("gpl", ["docs/tts-extension/harness/praat_crosscheck.py"], None, "imports Parselmouth (Praat, GPL v3); its own header says so"),
    ("gpl", ["languages/*/sounds.map", "languages/*/phonemes.map", "languages/*/sample.txt"], None,
     "written from eSpeak NG's phoneme tables; sample sentences partly from eSpeak NG's tests"),
    ("gpl", ["packs/*/pack.toml", "packs-proposed/*/pack.toml", "docs/tts-extension/examples/packs/*/pack.toml"], PACK_DATA,
     "a pack holding [sounds] or [phonemes] lines: the data of its sounds.map and phonemes.map"),
    ("ibm", ["languages/*/*.dll"], None, "the language modules: IBM's data compiled with openevv"),
    ("mit-openevv", ["openevv/lang/plpl/rules/is_val.up", "openevv/lang/plpl/rules/it_phone.up"], None,
     "rules written by upstream for Polish (openevv/NOTICE)"),
    ("ibm", ["openevv/lang/**", "openevv/src/klatt/klatt_tables.c", "openevv/src/eci/ssml/eci_xmltok_tables.c"], None,
     "transcribed out of IBM's objects (openevv/NOTICE)"),
    ("bestspeech", ["src/sapi/com.hpp", "src/sapi/com.cpp", "src/sapi/registry.hpp", "src/sapi/registry.cpp",
                    "src/sapi/utils.hpp", "src/sapi/ISpDataKeyImpl.hpp", "src/sapi/ISpDataKeyImpl.cpp",
                    "src/sapi/IEnumSpObjectTokensImpl.hpp", "src/sapi/IEnumSpObjectTokensImpl.cpp",
                    "src/sapi/voice_token.hpp", "src/sapi/voice_token.cpp", "src/sapi/sapi_main.cpp",
                    "src/sapi/ISpTTSEngineImpl.hpp"], None, "the list in NOTICE.md"),
    ("mixed-binary", ["dist/x64/OpenEvvSAPI.dll", "dist/x86/OpenEvvSAPI.dll"], None, "built from src/sapi, BestSpeech files included"),
    ("rendered", ["samples/*.wav", "samples/*/*.wav", "docs/tts-extension/review_packets/*/index.html",
                  "docs/tts-extension/review_packets/*/items.json", "docs/tts-extension/examples/packets/*/index.html",
                  "docs/tts-extension/examples/packets/*/items.json"], None, "audio the engine spoke, and the text it spoke"),
    ("sentences", ["docs/tts-extension/harness/asr/sentences.json", "docs/tts-extension/harness/results/asr.json",
                   "docs/tts-extension/harness/results/asr_espeak.json"], None,
     "the sentence set, and the results that quote it beside the recogniser's transcripts"),
    ("mit-here", ["openevv/src/accent/*", "openevv/accents/**", "openevv/tools/module/clone.py"], None,
     "this project's additions to the engine, under openevv/LICENSE's terms (NOTICE.md)"),
    ("mit-openevv", ["openevv/**", "dist/docs/openevv-*.txt"], None, "upstream openevv"),
    ("mit-here", ["src/**", "engine/**", "installer/**", "docs/**", "ipa/**", "packs/**", "packs-proposed/**", ".claude/**",
                  "samples/README.md", "samples/render-report.txt", "languages/*/language.ini",
                  "dist/x64/OpenEvvHost.exe", "dist/x86/OpenEvvHost.exe", "dist/x64/OpenEvvConfig.exe",
                  "dist/x86/OpenEvvConfig.exe", "dist/docs/*.txt",
                  "*.md", "LICENSE", "CMakeLists.txt", "build_all.bat", ".gitignore", ".gitattributes"], None,
     "the wrapper, the tools, the harness, the tables, proofs, packs' own data and every document"),
]

CODE_EXT = (".py", ".cpp", ".h", ".sh", ".cmd", ".bat", ".iss", ".ps1")
SPDX = re.compile(r"SPDX-License-Identifier:\s*(\S+)")


def glob_re(pat):
    out, i = "", 0
    while i < len(pat):
        if pat.startswith("**", i):
            out += ".*"
            i += 2
        elif pat[i] == "*":
            out += "[^/]*"
            i += 1
        elif pat[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pat[i])
            i += 1
    return re.compile(out + r"\Z")


COMPILED = [(c, [glob_re(p) for p in pats], content, why) for c, pats, content, why in RULES]


def tracked(root):
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def head(root, path, n=5):
    try:
        with open("%s/%s" % (root, path), "rb") as f:
            return f.read(4096).decode("utf-8", "replace").splitlines()[:n]
    except OSError:
        return []


def classify(root, files):
    cls, hits = {}, Counter()
    for path in files:
        for i, (c, pats, content, _) in enumerate(COMPILED):
            if not any(p.match(path) for p in pats):
                continue
            if content is not None:
                try:
                    with open("%s/%s" % (root, path), encoding="utf-8") as f:
                        if not content.search(f.read()):
                            continue
                except OSError:
                    continue
            cls[path] = c
            hits[i] += 1
            break
    return cls, hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", metavar="CLASS")
    ap.add_argument("--rules", action="store_true")
    ap.add_argument("--headers", action="store_true", help="fail on a first-party code file with no SPDX line")
    a = ap.parse_args()
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
    files = tracked(root)
    cls, hits = classify(root, files)
    if a.list:
        for p in sorted(p for p, c in cls.items() if c == a.list):
            print(p)
        return 0
    if a.rules:
        for i, (c, pats, content, why) in enumerate(RULES):
            print("%3d  %-12s %5d  %s%s  (%s)" % (i + 1, c, hits[i], ", ".join(pats),
                                                 " if the content holds [sounds] or [phonemes]" if content else "", why))
    unclassified = sorted(set(files) - set(cls))
    stale = [i for i in range(len(RULES)) if hits[i] == 0]
    false_mit, no_header = [], []
    for path, c in sorted(cls.items()):
        lines = head(root, path)
        ids = [m.group(1) for m in (SPDX.search(l) for l in lines) if m]
        if c not in ("mit-here", "mit-openevv") and "MIT" in ids:
            false_mit.append(path)
        if c == "mit-here" and path.endswith(CODE_EXT) and not path.startswith("openevv/") and not ids:
            no_header.append(path)
    counts = Counter(cls.values())
    print("licences: %d tracked files" % len(files))
    for c, title in CLASSES.items():
        print("  %-12s %5d  %s" % (c, counts[c], title))
    print("  %-12s %5d" % ("unclassified", len(unclassified)))
    for p in unclassified:
        print("    UNCLASSIFIED " + p)
    for i in stale:
        print("    STALE RULE %d (%s): matches no tracked file" % (i + 1, ", ".join(RULES[i][1])))
    for p in false_mit:
        print("    MIT CLAIMED over a file of class %s: %s" % (cls[p], p))
    print("first-party code files without an SPDX line: %d" % len(no_header))
    for p in no_header[:20]:
        print("    no header: " + p)
    if len(no_header) > 20:
        print("    ... and %d more" % (len(no_header) - 20))
    failed = bool(unclassified or stale or false_mit or (a.headers and no_header))
    print("check: %s (unclassified %d, stale rules %d, MIT claimed over another's file %d%s)" % (
        "FAILED" if failed else "pass", len(unclassified), len(stale), len(false_mit),
        ", missing headers %d" % len(no_header) if a.headers else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
