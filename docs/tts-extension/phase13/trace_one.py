# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 13 (D99): the trace engine/check_espeak_packs.py reads, kept for one pack and one map, to see
which phones the accent layer could not place (column 6 "-") and where its sounds landed.

    EVV_ACCENT_TRACE=<out>.tsv python docs/tts-extension/phase13/trace_one.py <tag> <sounds.map> <out>

prints (phones, not placed, the first few); <out>.ann is the annotation the module was given.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import check_espeak_packs as C  # noqa: E402

tag, mapf = sys.argv[1], sys.argv[2]
langs = os.path.join(ROOT, "languages")
ini = C.read_ini(os.path.join(langs, tag, "language.ini"))
tpl = ini[("Language", "Template")]
tini = C.read_ini(os.path.join(langs, tpl, "language.ini"))
m = C.Module(os.path.join(langs, tpl, tini[("Language", "Module64")]), int(tini[("Language", "Id")], 0))
sample = open(os.path.join(langs, tag, "sample.txt"), encoding="utf-8-sig").read().strip()
rc, ann, err = C.translate(os.path.join(ROOT, "dist", "x64", "OpenEvvFrontend.exe"),
                           os.path.join(ROOT, "dist", "espeak-ng-data"),
                           ini[("Frontend", "Voice")], mapf, sample + C.EXTRA)
open(sys.argv[3] + ".ann", "w", encoding="utf-8").write(ann)
C.traced()
m.speak(ann)
print(tag, C.traced())
