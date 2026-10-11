"""Say any IPA the way the sweep says it, and measure it the way the sweep does: nothing is written.

    python engine/ipa/say_ipa.py "<IPA>" ["<IPA>" ...] [--vowel] [--template dedx] [--pack hi]   (needs EVV_STAGE)

For /create-missing-sound step 2: is a sound (a letter with marks, a combination beyond the chart)
already made by composition? Each symbol is said alone and between [a], [i] and [u] (a vowel with
--vowel: between [p], [t] and [k]) by the staged front-end's IPA reading (`--ipa`) on the realised
master table (ipa/realized/<template>.map, with the pack's header lines: compose_test.test_map), and
spoken by the pack's module; the same per-symbol measures as the sweep's proofs (sweep.measure and
its summary, the median over the contexts) are printed, with what the front-end made of the input.
`engine.py <pack> ipa` reads IPA through the pack's eSpeak NG table and so cannot say a letter the
language lacks; this can.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose_test as CT  # noqa: E402
import sweep as S  # noqa: E402

E = S.E


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ipa", nargs="+")
    ap.add_argument("--vowel", action="store_true", help="say each between consonants, not vowels")
    ap.add_argument("--template", default="dedx")
    ap.add_argument("--pack", default="hi", help="a pack whose template is --template (its module speaks)")
    a = ap.parse_args()
    if not E.STAGE:
        sys.exit("STOP: set EVV_STAGE (the sweep's stage)")
    work = os.path.join(E.WORK, "say_ipa")
    p, map_path = S.test_map(a.pack, a.template, work)
    man = "vowel" if a.vowel else None
    around = S.CONSONANTS_AROUND if a.vowel else S.VOWELS_AROUND
    for x in a.ipa:
        ctx = [("alone", x)] + [("%s_%s" % (c, c), "ˈ%s%s%s" % (c, x, c)) for c in around]
        inputs = []
        for cid, text in ctx:
            rc, out, d = CT.say_ipa(p, map_path, text)
            if rc != 0:
                sys.exit("STOP: the front-end failed on %r" % text)
            inputs.append((cid, text, out))
        rend = E.render(a.pack, [(cid, "annotated", out) for cid, _, out in inputs], work=os.path.join(work, "r"))
        cases = {}
        print("%s (%s):" % (x, " ".join("U+%04X" % ord(ch) for ch in x)))
        for (cid, text, out), r in zip(inputs, rend):
            cases[cid] = S.measure(r, p, cid, man)
            print("  %-6s %-8s said %s" % (cid, text, out[out.rfind("}{") + 1:][-160:]))
        summ = S.summary(cases, man)
        for k in sorted(summ):
            v = summ[k]
            if isinstance(v, (int, float)) and v is not None:
                print("    %-28s %s" % (k, round(v, 3)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
