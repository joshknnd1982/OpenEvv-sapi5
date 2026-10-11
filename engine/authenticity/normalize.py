"""Speaker normalization: measured vowel targets made comparable across speakers (playbook Phase 7, step 3).

The rule (docs/tts-extension/AUTHENTICITY.md, "Speaker normalization"): **the voice, not the pack,
carries speaker scaling.** This engine's voice scales a vocal tract with one multiplier on F1 to F5
(head size, DESIGN.md 7), so a pack must hold the *pattern* of a variety's vowels, free of the size
of the speaker who was recorded. The method that removes exactly one multiplier is Nearey's uniform
log-mean normalization (Nearey 1978; Adank, Smits and van Hout 2004 compare it with the others):

    G(speaker) = the mean, over the vowel classes measured and over F1, F2, F3, of ln F
    a speaker's vowel, normalized:   ln F - G(speaker)
    put at the size of a reference:  F x exp(G(reference) - G(speaker))

Each class weighs the same in G (class means, not tokens), so a vowel spoken more often does not
pull it. The reference is the template module the pack speaks with (its own phones, as
engine/accent/chassis/<template>.json measured them), over the phones that say the same classes:
the target then comes out at the size of the module's voice, and the voice's settings scale it
from there like any other sound.

Known bias, stated: G is taken over the classes both sides have, and a dialect moves some of them
(a fronted GOOSE raises its F2); over ten or more classes this moves G by a few per cent at most,
and `scale()` reports the factor so it can be looked at.

    python engine/authenticity/normalize.py --selftest
"""
import math
import sys

FORMANTS = ("f1", "f2", "f3")


def log_mean(class_means, classes=None, formants=FORMANTS):
    """G: the mean of ln F over the classes and formants given ({class: {f1: Hz, ...}})."""
    classes = sorted(classes if classes is not None else class_means)
    logs = [math.log(class_means[c][k]) for c in classes for k in formants
            if class_means.get(c, {}).get(k)]
    if not logs:
        raise ValueError("log_mean: no formant values over the classes %s" % classes)
    return sum(logs) / len(logs)


def scale(speaker_means, reference_means, classes=None, formants=FORMANTS):
    """The one factor that puts the speaker at the reference's size: exp(G(ref) - G(speaker)).

    Only classes both sides have (and, inside them, formants both have) are used."""
    shared = sorted(c for c in (classes if classes is not None else speaker_means)
                    if c in speaker_means and c in reference_means)
    if not shared:
        raise ValueError("scale: the speaker and the reference share no vowel class")
    pairs = [(c, k) for c in shared for k in formants
             if speaker_means[c].get(k) and reference_means[c].get(k)]
    gs = sum(math.log(speaker_means[c][k]) for c, k in pairs) / len(pairs)
    gr = sum(math.log(reference_means[c][k]) for c, k in pairs) / len(pairs)
    return math.exp(gr - gs), shared


def apply(class_means, factor, formants=FORMANTS):
    """Every class's formants multiplied by the factor (rounded to 0.1 Hz)."""
    return {c: {k: round(v[k] * factor, 1) for k in formants if v.get(k)} for c, v in class_means.items()}


def spread(speakers, classes, formant):
    """Mean over classes of the between-speaker standard deviation of ln F: how far apart the
    speakers are, as a share (0.10 is about 10 per cent). Used to show that normalization brings
    speakers of one variety together."""
    out = []
    for c in classes:
        xs = [math.log(s[c][formant]) for s in speakers if s.get(c, {}).get(formant)]
        if len(xs) > 1:
            m = sum(xs) / len(xs)
            out.append(math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1)))
    return sum(out) / len(out) if out else float("nan")


def selftest():
    ref = {"i": {"f1": 300, "f2": 2200, "f3": 2900}, "a": {"f1": 700, "f2": 1200, "f3": 2500},
           "u": {"f1": 320, "f2": 900, "f3": 2300}, "e": {"f1": 450, "f2": 1900, "f3": 2600}}
    ok = True
    # 1. a speaker 18 per cent larger in every formant comes back to the reference exactly
    big = {c: {k: v * 1.18 for k, v in f.items()} for c, f in ref.items()}
    fac, shared = scale(big, ref)
    back = apply(big, fac)
    err = max(abs(back[c][k] - ref[c][k]) / ref[c][k] for c in ref for k in FORMANTS)
    r = abs(fac - 1 / 1.18) < 1e-9 and err < 0.001
    print("normalize selftest 1 (uniform scale undone): factor %.6f (expected %.6f), worst error %.4f%%: %s"
          % (fac, 1 / 1.18, 100 * err, "pass" if r else "FAIL"))
    ok &= r
    # 2. a dialect difference in one class survives normalization (it is pattern, not size)
    dia = {c: dict(f) for c, f in ref.items()}
    dia["u"]["f2"] = 1500                    # a fronted u
    dia = {c: {k: v * 0.85 for k, v in f.items()} for c, f in dia.items()}
    fac, _ = scale(dia, ref)
    out = apply(dia, fac)
    ratio_u = out["u"]["f2"] / ref["u"]["f2"]
    ratio_i = out["i"]["f2"] / ref["i"]["f2"]
    r = ratio_u > 1.5 and abs(ratio_i - 1) < 0.06
    print("normalize selftest 2 (a fronted u kept, the rest at the reference's size): u F2 x%.3f, i F2 x%.3f: %s"
          % (ratio_u, ratio_i, "pass" if r else "FAIL"))
    ok &= r
    # 3. two speakers of different size: the spread between them falls to (near) nothing
    s1 = {c: {k: v * 1.20 for k, v in f.items()} for c, f in ref.items()}
    s2 = {c: {k: v * 0.90 for k, v in f.items()} for c, f in ref.items()}
    before = spread([s1, s2], ref, "f2")
    after = spread([apply(s1, scale(s1, ref)[0]), apply(s2, scale(s2, ref)[0])], ref, "f2")
    r = before > 0.15 and after < 0.001
    print("normalize selftest 3 (between-speaker spread of ln F2): before %.3f, after %.4f: %s"
          % (before, after, "pass" if r else "FAIL"))
    ok &= r
    print("normalize selftest: %s" % ("3 of 3 pass" if ok else "FAILED"))
    return ok


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    print(__doc__)
