"""What a pack's overrides do, measured (AUTHENTICITY.md, step 5): each override's words rendered with the
pack as it is and with its proposed overrides realised (a scratch build, never languages/), the vowel's
F1 and F2 read at its middle, both as the engine asked for them (the frames) and as measured in the sound,
against the override's target; then the same on preset 2 (the adult female voice), to show the voice
and not the pack carries the speaker's size (DESIGN.md 7, rule 5: the ratio to preset 1 is the same for
both versions).

    python engine/authenticity/show_effect.py <tag>      (needs EVV_STAGE like the harness)
"""
import os
import statistics
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(ROOT, "docs", "tts-extension", "harness"), os.path.join(ROOT, "engine", "packs"),
                os.path.join(ROOT, "engine", "review")]
import engine as E  # noqa: E402
import packlib as L  # noqa: E402
import make_packet as M  # noqa: E402


def vowel_of(r):
    """(F1, F2 asked; F1, F2 measured; the phone's ms) of a one-syllable word's vowel (its first)."""
    rd = M.vowel_readings(r)
    return rd[0][2:] if rd else None


def main(tag):
    flat, _ = L.resolve(tag)
    spec = M.review_spec(tag)
    ovs = flat.get("override", {})
    work = tempfile.mkdtemp(prefix="effect_%s_" % tag)
    files = L.compile_pack(flat, include_proposed=True)
    after = os.path.join(work, "sounds-after.map")
    with open(after, "wb") as f:
        f.write(files["sounds.map"])
    cases = []
    for c in spec.get("check", []):
        if c["sound"] in ovs:
            for w in c["words"]:
                cases.append((c["sound"], w))
    res = {}
    for preset in (1, 2):
        for name, mp in (("before", None), ("after", after)):
            rs = E.render(tag, [("%s_%d" % (M.slug(w), i), "text", w) for i, (s, w) in enumerate(cases)],
                          preset=preset, work=os.path.join(work, "%s%d" % (name, preset)), map_path=mp)
            for (s, w), r in zip(cases, rs):
                res[(s, w, name, preset)] = vowel_of(r)
    print("%s: each word's vowel at its middle, preset 1 (adult male); asked = the frames, meas = the sound" % tag)
    print("  %-4s %-8s %-15s %-31s %-31s %s" % ("IPA", "word", "target F1/F2", "before: asked (meas)",
                                               "after: asked (meas)", "after vs target (asked)"))
    errs_b, errs_a = [], []
    for s, w in cases:
        if "f1" not in ovs[s].get("formants", {}):
            continue  # a length alone: below
        o = ovs[s]["formants"]
        t1, t2 = o["f1"]["v"], o["f2"]["v"]
        b, a = res[(s, w, "before", 1)], res[(s, w, "after", 1)]
        if not (a and b):
            print("  %-4s %-8s no vowel found" % (s, w))
            continue
        eb = max(abs(b[0] / t1 - 1), abs(b[1] / t2 - 1))
        ea = max(abs(a[0] / t1 - 1), abs(a[1] / t2 - 1))
        errs_b.append(eb)
        errs_a.append(ea)
        print("  %-4s %-8s %5.0f / %5.0f   %5d (%4s) / %5d (%4s)     %5d (%4s) / %5d (%4s)     F1 %+5.1f%%  F2 %+5.1f%%" % (
            s, w, t1, t2, b[0], b[2] or "-", b[1], b[3] or "-", a[0], a[2] or "-", a[1], a[3] or "-",
            100 * (a[0] / t1 - 1), 100 * (a[1] / t2 - 1)))
    print("largest distance from the target (F1 or F2, asked): before median %.1f%%, after median %.1f%% (%d words)" % (
        100 * statistics.median(errs_b), 100 * statistics.median(errs_a), len(errs_a)))
    durs = [(s, w) for s, w in cases if "duration" in ovs[s]]
    if durs:
        print("vowel length (the phone's span in the frames, ms), preset 1: target is the vowel's audible length,")
        print("the span also holds the movement into the next consonant, so compare the change, not the value")
        for s, w in durs:
            b, a = res[(s, w, "before", 1)], res[(s, w, "after", 1)]
            if a and b:
                print("  %-4s %-8s target %5.0f ms   before %4d   after %4d   (%+.0f ms)" % (
                    s, w, ovs[s]["duration"]["v"], b[4], a[4], a[4] - b[4]))
    print("preset 2 against preset 1 (F1, F2 asked): the voice's own scaling, the same with and without the override")
    worst = 0.0
    for s, w in cases:
        b1, a1, b2, a2 = (res[(s, w, n, p)] for n, p in (("before", 1), ("after", 1), ("before", 2), ("after", 2)))
        if not all((b1, a1, b2, a2)):
            continue
        rb = (b2[0] / b1[0], b2[1] / b1[1])
        ra = (a2[0] / a1[0], a2[1] / a1[1])
        worst = max(worst, abs(ra[0] - rb[0]), abs(ra[1] - rb[1]))
        print("  %-4s %-8s before x%.3f / x%.3f   after x%.3f / x%.3f" % (s, w, rb[0], rb[1], ra[0], ra[1]))
    print("largest difference between the two versions' preset-2 ratios: %.3f" % worst)


if __name__ == "__main__":
    main(sys.argv[1])
