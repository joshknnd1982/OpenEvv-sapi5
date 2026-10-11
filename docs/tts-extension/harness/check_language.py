"""One language's status, the way report.py judges it, printed and written nowhere in the tree.

    python docs/tts-extension/harness/check_language.py <tag> [--golden DIR] [--asr] [--asr-like TAG] [--json FILE]

For a pack being added or changed (ADDING_A_LANGUAGE.md): checks A (engine fidelity) and B (reference
ranges) on the tag's golden data, the ASR round trip, the status level and the failure layer, by
report.py's own functions. report.py writes LANGUAGE_STATUS.md for every language; this writes nothing
but --json.

  --golden DIR     the golden folder holding <tag>.json.gz (a new pack's: record it there first with
                   `golden.py <tag> --record --golden DIR`); default golden.py's (golden-staged/ under EVV_STAGE)
  --asr            run the ASR round trip now (Whisper, about a minute) instead of reading results/asr.json
  --asr-like TAG   with --asr: the sentences and Whisper language of TAG (a test copy of a language)
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E  # noqa: E402
import golden  # noqa: E402
import report as R  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tag")
    ap.add_argument("--golden")
    ap.add_argument("--asr", action="store_true")
    ap.add_argument("--asr-like")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.tag not in E.packs():
        sys.exit("STOP: no pack %s in languages/ or in EVV_STAGE's languages/ (build it there first)" % a.tag)
    if a.golden:
        golden.GOLDEN = os.path.abspath(a.golden)
    if not os.path.exists(golden.golden_path(a.tag)):
        sys.exit("STOP: no golden data %s: run golden.py %s --record --golden <folder> first"
                 % (golden.golden_path(a.tag), a.tag))
    if a.asr:
        import asr
        res = asr.run([a.tag], like={a.tag: a.asr_like} if a.asr_like else None)
    else:
        res = (R.load(os.path.join(R.RESULTS, "asr.json"), {}) or {}).get("languages", {})
    s = R.status(a.tag, res)
    ca, cb = s["a"], s["b"]
    print("%s (%s): %d golden cases; module %s" % (s["tag"], s["name"], s["cases"], s["module"]))
    print("check A: %s; substituted %d; phones meant to sound %d, silent %d; formant and F0 checks %d of %d"
          % ("pass" if ca["passed"] else "FAIL", ca["substituted"], ca["a1_phones"], ca["a1_silent"],
             ca["a2_ok"], ca["a2_checks"]))
    for p in ca["problems"][:10]:
        print("    " + p)
    print("check B: %s%s" % (R.fmt_b(cb), "; " + cb["why"] if cb.get("why") else ""))
    print("ASR: %s" % R.fmt_asr(s["asr"]))
    print("phonemes with no phone of their own: %d %s" % (len(s["no_own_phone"]), " ".join(s["no_own_phone"][:12])))
    print("level: %s; failure layer: %s" % (R.LEVEL_NAME[s["level"]], s["failure_layer"] or "none"))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
