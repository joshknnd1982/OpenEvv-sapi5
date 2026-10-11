# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Target extraction: measured vowel targets (and consonant, duration and F0 facts) from licensed,
aligned recordings of known speakers, into a pack's overrides (playbook Phase 7, step 2;
docs/tts-extension/AUTHENTICITY.md, "Target extraction").

    python engine/authenticity/extract_targets.py <tag> <corpus folder> [--write]

<tag>'s pack folder holds `measure.toml`, which says what is measured and what it is for:

    [measure]
    source = "cmu_arctic"                 # a registered source id (ipa/sources.toml): its licence is recorded
    speakers = ["awb"]                    # sub-folders of the corpus folder: <speaker>/wav/*.wav + <speaker>/lab/*.lab
    folders = { awb = "cmu_us_awb_arctic" }   # a speaker's folder, where it is not named after the speaker
    alignment = "festvox-lab"             # festvox-lab | textgrid (Montreal Forced Aligner: <speaker>/textgrid/*.TextGrid)
    [[class]]
    label = "uw"                          # the alignment's label for the class
    set = "GOOSE"                         # Wells's lexical set, for people
    sound = "ʉː"                          # the pack's IPA for it
    phonemes = ["@en-sc:u:"]              # the reader's phonemes it is said for

What is measured, per speaker (the harness's own analyser, harness/analysis.py, on the recording
resampled to 11025 Hz: the engine's band, DESIGN.md 10.1):
  vowels      F1 F2 F3 at the middle (Burg LPC, 25 ms), duration, F0 at the middle; tokens of 50 ms or
              more, not next to r, l, w or j (they pull the formants); outliers beyond 3 median
              absolute deviations in F1 or F2 dropped (tracking errors), and counted
  stops       voice onset time (p t k b d g), from the stop's start to 80 ms into what follows: written
              as `vot_ms_unvalidated` and never used. harness/analysis.py's stop_timing was made for the
              engine's output; on CMU ARCTIC awb it reads p t k as prevoiced even after a pause (median
              -24 to -28 ms), which English stops are not (OPEN_QUESTIONS.md Q40)
  fricatives  noise centroid above 1 kHz over the middle half (s z sh f th)
  lengths    each vowel class's median duration over every token not before a pause (its own set:
              the formant filter drops short tokens and would make KIT and GOOSE about a third longer)
  every label median duration
Each class's targets are the medians; normalize.py puts the speaker at the size of the template
module's voice. A class with fewer than MIN_TOKENS tokens, or a variety measured on fewer than
MIN_SPEAKERS speakers, is flagged `below_minimum` (and said so in the pack).

Writes packs/<tag>/measured/<source>.json (every token with its recording id, the statistics, the
targets) and, with --write, replaces the pack's [[override]] blocks for the measured classes whose
target differs from what the pack says now by more than NEAR per cent in F1 or F2 (state
"proposed": the human's say-so applies them, R18).
"""
import argparse
import datetime
import json
import math
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [HERE, os.path.join(ROOT, "docs", "tts-extension", "harness"), os.path.join(ROOT, "engine", "packs")]
import normalize as N  # noqa: E402
import packlib as L  # noqa: E402
import overrides as O  # noqa: E402
import tomlio  # noqa: E402

RATE = 11025
MIN_TOKENS = 10       # per class and speaker (AUTHENTICITY.md: the median's standard error under about 3 %)
MIN_SPEAKERS = 5      # per variety, before a target is the variety's and not one speaker's
MIN_VOWEL_MS = 50.0
NEAR = 6              # per cent: a difference this small is not worth an override (engine/accent/sounds.py `near`)
DUR_NEAR = 12         # per cent, for a vowel's length (sounds.py `lasting` uses the same tolerance)
LIQUIDS = {"r", "l", "w", "y", "j", "er", "axr", "el"}
STOPS = {"p", "t", "k", "b", "d", "g"}
FRICATIVES = {"s", "z", "sh", "f", "th"}


# ---------------------------------------------------------------- alignments

def read_lab(path):
    """Festvox label file: a header ending at '#', then 'end_time colour label' lines -> [(start, end, label)]."""
    segs, t0, body = [], 0.0, False
    for line in open(path, encoding="utf-8", errors="replace"):
        if not body:
            body = line.strip() == "#"
            continue
        w = line.split()
        if len(w) >= 3:
            end = float(w[0])
            segs.append((t0, end, w[2].lower()))
            t0 = end
    return segs


def read_textgrid(path, tier="phones"):
    """A Praat TextGrid's interval tier (MFA writes 'phones') -> [(start, end, label)]."""
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r'name = "%s".*?intervals: size = \d+(.*?)(?:item \[|\Z)' % tier, text, re.S)
    if not m:
        raise ValueError("%s: no tier %r" % (path, tier))
    out = []
    for a, b, lab in re.findall(r"xmin = ([\d.]+)\s+xmax = ([\d.]+)\s+text = \"(.*?)\"", m.group(1), re.S):
        out.append((float(a), float(b), re.sub(r"\d", "", lab).lower()))
    return out


def utterances(folder, speaker, alignment, sub=None):
    sub = os.path.join(folder, sub or speaker)
    wavs = os.path.join(sub, "wav")
    for name in sorted(os.listdir(wavs)):
        if not name.lower().endswith(".wav"):
            continue
        base = name[:-4]
        if alignment == "festvox-lab":
            ap = os.path.join(sub, "lab", base + ".lab")
            if os.path.isfile(ap):
                yield base, os.path.join(wavs, name), read_lab(ap)
        else:
            ap = os.path.join(sub, "textgrid", base + ".TextGrid")
            if os.path.isfile(ap):
                yield base, os.path.join(wavs, name), read_textgrid(ap)


def load_wav(path):
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
    x, rate = sf.read(path, dtype="float64", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if rate != RATE:
        g = math.gcd(int(rate), RATE)
        x = resample_poly(x, RATE // g, int(rate) // g)
    return np.round(x * 32767 * 0.9 / max(1e-9, float(abs(x).max()))).astype("int16"), RATE


# ---------------------------------------------------------------- measuring

def mad_keep(toks, keys=("f1", "f2"), k=3.0):
    keep = list(toks)
    for key in keys:
        vals = [t[key] for t in keep if t.get(key)]
        if len(vals) < 4:
            continue
        med = statistics.median(vals)
        mad = statistics.median(abs(v - med) for v in vals) * 1.4826 or 1.0
        keep = [t for t in keep if t.get(key) and abs(t[key] - med) <= k * mad]
    return keep


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    q = statistics.quantiles(vals, n=4) if len(vals) > 1 else [vals[0]] * 3
    sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
    med = statistics.median(vals)
    return dict(n=len(vals), median=round(med, 1), q1=round(q[0], 1), q3=round(q[2], 1), mean=round(statistics.mean(vals), 1),
                sd=round(sd, 1), se_median_pct=round(100 * 1.2533 * sd / math.sqrt(len(vals)) / med, 2) if med else None)


def measure(folder, spec):
    import analysis as A
    vowel_labels = {c["label"]: c for c in spec["class"]}
    tokens = {s: {lab: [] for lab in vowel_labels} for s in spec["measure"]["speakers"]}
    cons = {s: {} for s in spec["measure"]["speakers"]}
    durs = {s: {} for s in spec["measure"]["speakers"]}
    lengths = {s: {lab: [] for lab in vowel_labels} for s in spec["measure"]["speakers"]}
    n_utt, mismatched = {}, {}
    for spk in spec["measure"]["speakers"]:
        n = 0
        for uid, wav, segs in utterances(folder, spk, spec["measure"].get("alignment", "festvox-lab"),
                                         spec["measure"].get("folders", {}).get(spk)):
            x, rate = load_wav(wav)
            # an alignment made on another cut of the recording (seen: CMU ARCTIC's packed awb audio is
            # trimmed, its labels are not) is refused, not measured
            if not segs or abs(segs[-1][1] - len(x) / float(rate)) > 0.05:
                mismatched.setdefault(spk, []).append(uid)
                continue
            n += 1
            for i, (a, b, lab) in enumerate(segs):
                ms = (b - a) * 1000.0
                durs[spk].setdefault(lab, []).append(ms)
                prev = segs[i - 1][2] if i else "pau"
                nxt = segs[i + 1][2] if i + 1 < len(segs) else "pau"
                if lab in vowel_labels:
                    # a vowel's length is measured on its own set: every token but those before a pause
                    # (lengthened at a phrase's end); the formant filter below would drop the short ones
                    if nxt != "pau":
                        lengths[spk][lab].append((ms, "%s/%s/%s" % (spec["measure"]["source"], spk, uid)))
                    if ms < MIN_VOWEL_MS or prev in LIQUIDS or nxt in LIQUIDS:
                        continue
                    mid = (a + b) * 500.0
                    f = A.formants(x, rate, mid)
                    f0 = A.f0_at(x, rate, mid)
                    tok = dict(rec="%s/%s/%s" % (spec["measure"]["source"], spk, uid), t=round(a, 3), ms=round(ms, 1),
                               prev=prev, next=nxt, f0=round(f0, 1) if f0 else None)
                    for k in range(3):
                        tok["f%d" % (k + 1)] = round(f[k][0], 1) if len(f) > k else None
                    tokens[spk][lab].append(tok)
                elif lab in STOPS and nxt not in ("pau",):
                    st = A.stop_timing(x, rate, a * 1000.0, b * 1000.0)
                    vot = st.get("vot_ms") if isinstance(st, dict) else None
                    if vot is not None:
                        cons[spk].setdefault(lab, {}).setdefault("vot_ms_unvalidated", []).append(vot)
                elif lab in FRICATIVES and ms >= 40:
                    q = (b - a) * 250.0
                    m = A.spectrum_moments(x, rate, a * 1000.0 + q, b * 1000.0 - q, fmin=1000.0)
                    c = m.get("centroid_hz") if isinstance(m, dict) else None
                    if c:
                        cons[spk].setdefault(lab, {}).setdefault("centroid_hz", []).append(c)
        n_utt[spk] = n
        if mismatched.get(spk):
            print("speaker %s: %d recordings refused, their alignment does not end where the audio does (first: %s)"
                  % (spk, len(mismatched[spk]), " ".join(mismatched[spk][:5])))
    if not any(n_utt.values()):
        raise SystemExit("no recording could be measured")
    return tokens, cons, durs, n_utt, lengths


# ---------------------------------------------------------------- what the pack says now

def pack_now(flat, phonemes):
    """(module phone, {f1: Hz, f2: Hz, f3: Hz, ms: the vowel's audible length}) the pack says a phoneme with today."""
    phones = O.chassis(flat["ini"]["Language"]["Template"])
    lines = flat["sounds"]["line"]
    m = [x for x in lines if x["kind"] == "map" and x["name"] == phonemes[0]]
    if not m:
        raise SystemExit("the pack's sound map has no phoneme %r" % phonemes[0])
    phone, _, sid = m[0]["to"].partition("=")
    keys = {}
    if sid:
        keys = [x for x in lines if x["kind"] == "sound" and x["id"] == sid][0]["keys"]
    own = phones[phone]["f"]
    now = {"f%d" % k: round(own[k - 1] * int(keys.get("f%d" % k, 100)) / 100.0, 1) for k in (1, 2, 3)}
    m = phones[phone]
    now["ms"] = round(m["ms_sound"] + m["ms"] * (int(keys.get("dur", 100)) / 100.0 - 1), 1)
    return phone, now


def run(tag, folder, write=False):
    pack_dir = os.path.dirname(L.pack_path(tag))
    spec = tomlio.load(os.path.join(pack_dir, "measure.toml"))
    flat, _ = L.resolve(tag)
    src = spec["measure"]["source"]
    tokens, cons, durs, n_utt, lengths = measure(folder, spec)
    template = flat["ini"]["Language"]["Template"]
    phones = O.chassis(template)
    out = dict(source=src, pack=tag, template=template, made=datetime.date.today().isoformat(),
               method="harness/analysis.py at 11025 Hz; vowel middles; Burg LPC 25 ms; MAD 3; tokens >= %d ms, "
                      "not next to r l w j" % MIN_VOWEL_MS,
               minimums=dict(tokens_per_class=MIN_TOKENS, speakers=MIN_SPEAKERS), utterances=n_utt,
               speakers={}, sounds={})
    n_spk = len(spec["measure"]["speakers"])
    per_speaker_means = {}
    for spk in spec["measure"]["speakers"]:
        sp = out["speakers"][spk] = dict(classes={}, consonants={}, durations_ms={})
        means = {}
        for c in spec["class"]:
            raw = tokens[spk][c["label"]]
            keep = mad_keep(raw)
            st = {k: stats([t[k] for t in keep]) for k in ("f1", "f2", "f3", "f0")}
            st["ms_formant_tokens"] = stats([t["ms"] for t in keep])
            st["ms"] = stats([m for m, _ in lengths[spk][c["label"]]])
            sp["classes"][c["label"]] = dict(set=c["set"], sound=c["sound"], tokens=len(raw), kept=len(keep),
                                             dropped=len(raw) - len(keep), stats=st, token_list=keep,
                                             length_recordings=sorted({r for _, r in lengths[spk][c["label"]]}))
            if st["f1"] and st["f2"] and st["f3"]:
                means[c["label"]] = {k: st[k]["median"] for k in ("f1", "f2", "f3")}
        per_speaker_means[spk] = means
        for lab, d in sorted(cons[spk].items()):
            sp["consonants"][lab] = {k: stats(v) for k, v in d.items()}
        for lab, v in sorted(durs[spk].items()):
            sp["durations_ms"][lab] = stats(v)
    # the reference: the module phones the pack says each class with
    ref = {}
    for c in spec["class"]:
        phone, _ = pack_now(flat, c["phonemes"])
        ref[c["label"]] = {"f%d" % k: phones[phone]["f"][k - 1] for k in (1, 2, 3)}
    # speaking rate, like size, is the voice's: one factor per speaker puts its vowel lengths at the
    # module's rate (the log-mean of the classes' medians against the module phones' audible lengths)
    rate = {}
    for spk in per_speaker_means:
        cls = [c for c in spec["class"] if out["speakers"][spk]["classes"][c["label"]]["stats"]["ms"]]
        mod = [math.log(phones[pack_now(flat, c["phonemes"])[0]]["ms_sound"]) for c in cls]
        own = [math.log(out["speakers"][spk]["classes"][c["label"]]["stats"]["ms"]["median"]) for c in cls]
        rate[spk] = math.exp(sum(mod) / len(mod) - sum(own) / len(own))
        out["speakers"][spk]["rate_normalization"] = dict(method="log-mean of class median lengths", factor=round(rate[spk], 4),
                                                          reference="module %s's phones, audible length (ms_sound)" % template)
    norm = {}
    for spk, means in per_speaker_means.items():
        fac, shared = N.scale(means, ref)
        norm[spk] = (fac, N.apply(means, fac))
        out["speakers"][spk]["normalization"] = dict(method="nearey-uniform", factor=round(fac, 4), classes=shared,
                                                     reference="module %s's own phones (engine/accent/chassis)" % template)
    for c in spec["class"]:
        lab = c["label"]
        phone, now = pack_now(flat, c["phonemes"])
        vals = [norm[s][1][lab] for s in norm if lab in norm[s][1]]
        kept = [out["speakers"][s]["classes"][lab]["kept"] for s in norm]
        recs = sorted({t["rec"] for s in norm for t in out["speakers"][s]["classes"][lab]["token_list"]}
                      | {r for s in norm for r in out["speakers"][s]["classes"][lab]["length_recordings"]})
        snd = out["sounds"][c["sound"]] = dict(label=lab, set=c["set"], phonemes=c["phonemes"], module_phone=phone,
                                               pack_now_hz=now, speakers=len(vals), tokens=sum(kept), recordings=recs)
        below = len(vals) < MIN_SPEAKERS or any(k < MIN_TOKENS for k in kept)
        snd["below_minimum"] = below
        for k in ("f1", "f2", "f3"):
            if vals:
                tgt = round(statistics.mean(v[k] for v in vals), 1)
                snd[k] = dict(target_hz=tgt, raw_median_hz=[out["speakers"][s]["classes"][lab]["stats"][k]["median"]
                                                             for s in norm],
                              change_pct=round(100.0 * (tgt / now[k] - 1), 1))
        ms = [out["speakers"][s]["classes"][lab]["stats"]["ms"]["median"] * rate[s] for s in norm
              if out["speakers"][s]["classes"][lab]["stats"]["ms"]]
        if ms:
            tgt = round(statistics.mean(ms), 1)
            snd["duration"] = dict(target_ms=tgt, raw_median_ms=[out["speakers"][s]["classes"][lab]["stats"]["ms"]["median"]
                                                                 for s in norm],
                                   change_pct=round(100.0 * (tgt / now["ms"] - 1), 1),
                                   n=sum(out["speakers"][s]["classes"][lab]["stats"]["ms"]["n"] for s in norm
                                         if out["speakers"][s]["classes"][lab]["stats"]["ms"]))
    out["n_speakers"] = n_spk
    os.makedirs(os.path.join(pack_dir, "measured"), exist_ok=True)
    path = os.path.join(pack_dir, "measured", "%s.json" % src)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report(out)
    print("written: %s" % os.path.relpath(path, ROOT))
    if write:
        n = write_overrides(tag, pack_dir, out, src)
        print("pack.toml: %d proposed overrides written (classes whose F1 or F2 differs by more than %d%%, or length by more than %d%%)"
              % (n, NEAR, DUR_NEAR))
    return out


def report(out):
    for spk, sp in out["speakers"].items():
        nm = sp["normalization"]
        print("speaker %s: %d utterances; normalization factor x%.4f to module %s over %d classes; rate factor x%.4f" % (
            spk, out["utterances"][spk], nm["factor"], out["template"], len(nm["classes"]), sp["rate_normalization"]["factor"]))
        print("  %-6s %-8s %-4s %5s %5s  %-22s %-22s %-22s %-14s" % (
            "label", "set", "IPA", "kept", "drop", "F1 median (q1-q3) Hz", "F2 median (q1-q3) Hz",
            "F3 median (q1-q3) Hz", "ms / F0 Hz"))
        for lab, c in sp["classes"].items():
            s = c["stats"]
            f = lambda k: ("%6.0f (%4.0f-%4.0f)" % (s[k]["median"], s[k]["q1"], s[k]["q3"])) if s[k] else "   -"
            print("  %-6s %-8s %-4s %5d %5d  %-22s %-22s %-22s %4.0f / %3.0f%s" % (
                lab, c["set"], c["sound"], c["kept"], c["dropped"], f("f1"), f("f2"), f("f3"),
                s["ms"]["median"] if s["ms"] else 0, s["f0"]["median"] if s["f0"] else 0,
                "  BELOW MINIMUM (%d tokens)" % c["kept"] if c["kept"] < MIN_TOKENS else ""))
        for lab, d in sp["consonants"].items():
            print("  %-6s %s" % (lab, "; ".join("%s median %.1f (n %d)%s" % (
                k, v["median"], v["n"], " NOT VALID on natural speech (Q40), not used" if "unvalidated" in k else "")
                for k, v in d.items() if v)))
    print("targets at the size of module %s (normalized), against what the pack says now:" % out["template"])
    for snd, d in out["sounds"].items():
        if "f1" not in d:
            continue
        print("  %-4s %-8s phone %-2s  F1 %6.0f (now %6.0f, %+5.1f%%)  F2 %6.0f (now %6.0f, %+5.1f%%)  F3 %6.0f (now %6.0f)  "
              "speakers %d, tokens %d%s" % (snd, d["set"], d["module_phone"], d["f1"]["target_hz"], d["pack_now_hz"]["f1"],
                                           d["f1"]["change_pct"], d["f2"]["target_hz"], d["pack_now_hz"]["f2"],
                                           d["f2"]["change_pct"], d["f3"]["target_hz"], d["pack_now_hz"]["f3"],
                                           d["speakers"], d["tokens"], "  below minimum" if d["below_minimum"] else ""))
        if "duration" in d:
            print("  %-4s %-8s          length %4.0f ms (now %4.0f, %+5.1f%%)" % (
                snd, d["set"], d["duration"]["target_ms"], d["pack_now_hz"]["ms"], d["duration"]["change_pct"]))


def write_overrides(tag, pack_dir, out, src):
    """Replaces the [[override]] blocks of the measured sounds in pack.toml (the rest of the file is kept)."""
    path = os.path.join(pack_dir, "pack.toml")
    text = open(path, encoding="utf-8").read()
    eol = "\r\n" if "\r\n" in text else "\n"
    text = text.replace("\r\n", "\n")
    blocks = re.split(r"(?m)^(?=\[\[override\]\]$)", text)
    head, old = blocks[0], blocks[1:]
    measured = set(out["sounds"])
    keep = [b for b in old if re.search(r'^sound = "(.*)"$', b, re.M).group(1) not in measured]
    sp = list(out["speakers"])
    new = []
    for snd, d in out["sounds"].items():
        moved = "f1" in d and (abs(d["f1"]["change_pct"]) > NEAR or abs(d["f2"]["change_pct"]) > NEAR)
        longer = "duration" in d and abs(d["duration"]["change_pct"]) > DUR_NEAR
        if not (moved or longer):
            continue
        fac = "; ".join("%s x%.4f" % (s, out["speakers"][s]["normalization"]["factor"]) for s in sp)
        b = ["[[override]]",
             "sound = %s" % json.dumps(snd, ensure_ascii=False),
             "phonemes = %s" % json.dumps(d["phonemes"], ensure_ascii=False),
             'state = "proposed"',
             "note = %s" % json.dumps("%s (%s): measured on %d speaker(s), %d tokens; extract_targets.py %s%s" % (
                 d["set"], d["label"], d["speakers"], d["tokens"], out["made"],
                 "; below the minimums of AUTHENTICITY.md" if d["below_minimum"] else ""), ensure_ascii=False)]
        # the recordings once for the override (both formants come from the same tokens), eight a line,
        # without the source id the values' `ref` already gives
        ids = sorted({r.split("/", 1)[1] for r in d["recordings"]})
        b += ["recordings = ["] + ["  %s," % ", ".join(json.dumps(i) for i in ids[j:j + 8]) for j in range(0, len(ids), 8)] + ["]"]
        rfac = "; ".join("%s x%.4f" % (s, out["speakers"][s]["rate_normalization"]["factor"]) for s in sp)
        parts = ([("[override.formants.%s]" % k, d[k]["target_hz"], d["tokens"],
                   "nearey-uniform to %s (%s)" % (out["template"], fac)) for k in ("f1", "f2")] if moved else [])
        if longer:
            parts.append(("[override.duration]", d["duration"]["target_ms"], d["duration"]["n"],
                          "rate log-mean to %s (%s); every token not before a pause" % (out["template"], rfac)))
        for head_, v, n, how in parts:
            b += ["", head_, "v = %.1f" % v, 'tag = "measured"', "ref = %s" % json.dumps(src),
                  "n = %d" % n, "speakers = %d" % d["speakers"],
                  "below_minimum = %s" % ("true" if d["below_minimum"] else "false"),
                  "norm = %s" % json.dumps(how), "evidence = %s" % json.dumps("measured/%s.json" % src)]
        new.append("\n".join(b) + "\n")
    body = head.rstrip("\n") + "\n" + "".join("\n" + b.rstrip("\n") + "\n" for b in keep + new)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(body.replace("\n", eol))
    L.resolve(tag)  # the pack must still load
    return len(new)


def main():
    ap = argparse.ArgumentParser(description="Measure targets from aligned recordings into a pack.")
    ap.add_argument("tag")
    ap.add_argument("corpus")
    ap.add_argument("--write", action="store_true", help="write the proposed overrides into pack.toml")
    a = ap.parse_args()
    run(a.tag, a.corpus, a.write)


if __name__ == "__main__":
    main()
