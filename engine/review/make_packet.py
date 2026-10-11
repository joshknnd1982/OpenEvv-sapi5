"""The native review packet: everything a speaker of a language, dialect or accent needs to judge it,
in one folder (playbook Phase 7, step 5; docs/tts-extension/AUTHENTICITY.md, "Review packets").

    python engine/review/make_packet.py <tag> [--out <folder>] [--no-flagged]

Writes <out> (default docs/tts-extension/review_packets/<tag>/):

    index.html       the whole packet in one file: audio players and spectrograms embedded, with the
                     orthography, the IPA and the questions beside each item (no network needed)
    audio/*.wav      every item, as spoken by the engine (preset 1, adult male)
    spectrograms/*.png   every item: the sound's spectrogram, the formants the engine asked for (lines)
                     and measured (dots); each picture's description gives the numbers in words
    items.json       what every item is, for tools (nothing in it says which A/B version is which: an
                     A/B item's vowels are listed without the sound ids that would tell)

and, outside the packet so that sending the whole folder cannot unblind it,
docs/tts-extension/review/keys/<tag>.json: which A/B version carries the override and what each pair
tests, for the project and the ingest command.
    CHECKLIST.md     the reviewer's questions, in plain language
    feedback.toml    the form the reviewer fills in and sends back (engine/review/ingest_feedback.py)
    README.md        what this is and how to send it back

What goes in:
  * words, sentences and minimal pairs from packs/<tag>/review.toml when the pack has one; otherwise
    the language's ASR sentences (harness/asr/sentences.json, CC0 / CC BY) and words taken from them;
  * the pack's overrides (proposed or applied): each word said with and without them, blind (A or B
    by a hash of the item; neither the page nor items.json says which), so the reviewer can say
    which is nearer;
  * every sound the language has that the speaking module has not (the pack's reshaped sounds), said in
    a frame ("t_t" for a vowel, "a_a" for a consonant), with what the master table says about that
    symbol: created, approximate, values estimated.
The IPA is what eSpeak NG, the pack's reader, reads (espeak-ng.exe --ipa; EVV_ESPEAK_EXE names it).
"""
import argparse
import base64
import datetime
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HARNESS = os.path.join(ROOT, "docs", "tts-extension", "harness")
sys.path[:0] = [HARNESS, os.path.join(ROOT, "engine", "packs"), os.path.join(ROOT, "engine", "ipa")]
import analysis as A  # noqa: E402
import engine as E  # noqa: E402
import packlib as L  # noqa: E402
import overrides as O  # noqa: E402
import tomlio  # noqa: E402

OUT = os.path.join(ROOT, "docs", "tts-extension", "review_packets")
KEYS = os.path.join(ROOT, "docs", "tts-extension", "review", "keys")
ESPEAK = os.environ.get("EVV_ESPEAK_EXE") or os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "OpenEvvBuild", "frontend-x64", "bin", "espeak-ng.exe")
ESPEAK_DATA = os.path.join(ROOT, "dist")
LEVELS = {1: "draft", 2: "engine-verified", 3: "reference-verified", 4: "intelligibility-verified",
          5: "native-validated"}


def espeak_ipa(voice, text):
    """eSpeak NG's IPA for the text, as the pack's reader reads it; None if espeak-ng.exe is absent."""
    if not os.path.isfile(ESPEAK):
        return None
    r = subprocess.run([ESPEAK, "--path=%s" % ESPEAK_DATA, "--ipa", "-q", "-v", voice, text],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    return " ".join(r.stdout.decode("utf-8", "replace").split()) or None


def table_flags():
    """{ipa letter: (state, approximate, number of estimated values)} from the master table."""
    try:
        import table as T
        t = T.load()
    except Exception as e:  # the packet still works; it says why the flags are missing
        return {}, "the master table could not be read: %s" % e
    out = {}
    for sid, e in t.sounds.items():
        if e.get("kind") != "base" or "ipa" not in e:
            continue
        est = 0
        for part in ("spec",):
            for v in _values(e.get(part, {})):
                est += v.get("tag") == "estimated"
        out[e["ipa"]] = (e.get("state", "?"), bool(e.get("approximate")), est)
    return out, None


def _values(d):
    if isinstance(d, dict):
        if "tag" in d and "v" in d:
            yield d
        else:
            for v in d.values():
                yield from _values(v)


def base_letter(ipa, flags):
    """The master-table letter a pack's sound note is: the longest leading run that is a letter."""
    s = ipa.split()[0] if ipa.split() else ""
    for n in range(len(s), 0, -1):
        if s[:n] in flags:
            return s[:n]
    return None


def review_spec(tag):
    path = os.path.join(os.path.dirname(L.pack_path(tag)), "review.toml")
    return tomlio.load(path) if os.path.isfile(path) else {}


def asr_sentences(tag, n=8):
    with open(os.path.join(HARNESS, "asr", "sentences.json"), encoding="utf-8") as f:
        d = json.load(f)["languages"].get(tag)
    if not d:
        return [], None
    return [s["text"] for s in d["sentences"][:n]], "%s (%s)" % (d["source"], d.get("locale"))


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:40] or "x"


# ---------------------------------------------------------------- measuring and drawing one item

def vowel_readings(r):
    """[(phone name, sound id, F1 asked, F2 asked, F1 measured, F2 measured, phone ms)] at each vowel's middle."""
    x, rate = E.read_wav(r["wav"])
    t = E.frame_times(r["frames"])
    out = []
    for ph in r["phones"]:
        if ph.get("name") in ("#", "_") or ph["end_ms"] - ph["start_ms"] < 30:
            continue
        cls = A.phone_class(ph.get("record"), ph["name"], None)
        if cls != "vowel":
            continue
        mid = (ph["start_ms"] + ph["end_ms"]) / 2.0
        i = int(min(range(len(t)), key=lambda j: abs(t[j] - mid)))
        f = A.formants(x, rate, mid)
        out.append((ph["name"], ph.get("sound") or "", int(r["frames"][i, E.P["f1"]]), int(r["frames"][i, E.P["f2"]]),
                    round(f[0][0]) if len(f) > 0 else None, round(f[1][0]) if len(f) > 1 else None,
                    round(ph["end_ms"] - ph["start_ms"])))
    return out


def draw(r, png, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x, rate = E.read_wav(r["wav"])
    t = E.frame_times(r["frames"])
    fig, ax = plt.subplots(figsize=(6.4, 2.6), dpi=72)
    ax.specgram(x.astype(float) + 1e-3, NFFT=256, Fs=rate, noverlap=200, cmap="Greys", scale="dB", vmin=-20)
    tr = A.formant_track(x, rate, 0, r["case_ms"])
    loud = [(tt, f) for tt, f in tr if A.intensity_db(x, rate, tt - 10, tt + 10) > -45]
    for k, col in ((1, "#d62728"), (2, "#1f77b4"), (3, "#2ca02c")):
        ax.plot(t / 1000.0, r["frames"][:, E.P["f%d" % k]], color=col, lw=1.0, label="F%d asked" % k)
        ax.plot([tt / 1000.0 for tt, f in loud if len(f) >= k], [f[k - 1][0] for tt, f in loud if len(f) >= k],
                ".", color=col, ms=2, label="F%d measured" % k)
    for ph in r["phones"]:
        ax.axvline(ph["start_ms"] / 1000.0, color="#999", lw=0.5)
        ax.text((ph["start_ms"] + ph["end_ms"]) / 2000.0, rate / 2 - 400, ph["name"], ha="center", fontsize=7)
    ax.set_ylim(0, rate / 2)
    ax.set_xlabel("seconds", fontsize=7)
    ax.set_ylabel("Hz", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.set_title(title, fontsize=8)
    ax.legend(fontsize=5, ncol=3, loc="upper right")
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)
    from PIL import Image  # matplotlib's own dependency: a 32-colour palette keeps the packet small
    Image.open(png).convert("RGB").quantize(colors=32).save(png, optimize=True)


def describe(item, readings):
    parts = ["Spectrogram of %s, %.1f seconds" % (item["label"], item["ms"] / 1000.0)]
    if readings:
        parts.append("; vowels at their middle (asked for by the engine, then measured in the sound): " + "; ".join(
            "%s F1 %d Hz (measured %s), F2 %d Hz (measured %s)" % (n, a1, m1 if m1 else "none", a2, m2 if m2 else "none")
            for n, s, a1, a2, m1, m2, ms in readings))
    return "".join(parts) + "."


# ---------------------------------------------------------------- the packet

def make(tag, out, flagged=True):
    flat, _ = L.resolve(tag)
    p = E.pack(tag)
    spec = review_spec(tag)
    voice = flat["ini"].get("Frontend", {}).get("Voice")
    name = flat["pack"]["name"]
    meta = flat.get("meta", {})
    if os.path.isdir(out):
        # only a packet made before is replaced; any other folder is left alone
        if os.listdir(out) and not os.path.isfile(os.path.join(out, "items.json")):
            raise SystemExit("%s is not empty and holds no packet (items.json): choose another --out" % out)
        shutil.rmtree(out)
    for d in ("audio", "spectrograms"):
        os.makedirs(os.path.join(out, d))
    work = tempfile.mkdtemp(prefix="packet_%s_" % tag)

    # a sounds.map with the proposed overrides realised, for the before/after items
    after_map = None
    ovs = list(flat.get("override", {}).values())
    if ovs:
        files = L.compile_pack(flat, include_proposed=True)
        after_map = os.path.join(work, "sounds-after.map")
        with open(after_map, "wb") as f:
            f.write(files["sounds.map"])

    items = []
    key = {}   # what the reviewer is not shown: which A/B version is which, what each pair is meant to test

    def add(group, iid, label, kind, text, ortho, question, map_path=None, extra=None):
        items.append(dict(group=group, id=iid, label=label, kind=kind, text=text, orthography=ortho,
                          question=question, map=map_path, **(extra or {})))

    words = spec.get("words", {}).get("list")
    sents = spec.get("sentences", {}).get("list")
    sent_src = spec.get("sentences", {}).get("source")
    if not sents:
        sents, sent_src = asr_sentences(tag)
    if not words:
        seen = []
        for s in sents:
            for w in re.findall(r"\w{3,}", s):
                if w.lower() not in seen:
                    seen.append(w.lower())
        words = seen[:12]
    for w in words:
        add("words", "w-" + slug(w), "the word '%s'" % w, "text", w, w,
            "Can you understand the word? Does it sound like your variety?")
    for i, s in enumerate(sents):
        add("sentences", "s-%02d" % (i + 1), "sentence %d" % (i + 1), "text", s, s,
            "Can you understand the whole sentence? Which word sounds least natural?")
    for pr in spec.get("pair", []):
        for side in ("a", "b"):
            add("pairs", "p-%s-%s" % (slug(pr["id"]), side), "the word '%s' (pair %s)" % (pr[side], pr["id"]),
                "text", pr[side], pr[side], pr["question"], extra={"pair": pr["id"]})
            key["p-%s-%s" % (slug(pr["id"]), side)] = dict(pair=pr["id"], contrast=pr.get("contrast", ""),
                                                          ref=pr.get("ref", ""))
    for o in sorted(ovs, key=lambda o: o["sound"]):
        ow = [c for c in spec.get("check", []) if c.get("sound") == o["sound"]]
        for w in (ow[0]["words"] if ow else []):
            q = ow[0].get("question", "Which of the two sounds more like your variety, A or B, or neither?")
            note = "; ".join("%s %.0f Hz (%s, %s)" % (k.upper(), v["v"], v["tag"], v.get("ref", ""))
                             for k, v in sorted(o.get("formants", {}).items()))
            base = "c-%s-%s" % (slug(o["sound"].encode("unicode_escape").decode()), slug(w))
            # blind: which of A and B carries the override is fixed by a hash of the item, so it differs
            # from word to word and from packet to packet alike; only the key (docs/tts-extension/review/keys/<tag>.json) says which is which
            new_side = "B" if int(hashlib.sha256(base.encode()).hexdigest(), 16) % 2 else "A"
            for side in ("A", "B"):
                mp = after_map if side == new_side else None
                add("compare", "%s-%s" % (base, side), "'%s', version %s" % (w, side), "text", w, w, q, map_path=mp,
                    extra={"version": side})
                key[base + "-" + side] = dict(sound=o["sound"], word=w,
                                              version="override" if side == new_side else "pack",
                                              override_state=o.get("state", "proposed"), override_values=note)
    flags, flag_err = table_flags()
    if flagged:
        phones = O.chassis(flat["ini"]["Language"]["Template"])
        sounds = {x["id"]: x for x in flat.get("sounds", {}).get("line", []) if x["kind"] == "sound"}
        done = set()
        for x in flat.get("sounds", {}).get("line", []):
            if x["kind"] != "map" or not x["name"].startswith("@") or "not met" in x.get("note", ""):
                continue
            phone, _, sid = x["to"].partition("=")
            if not sid or sid not in sounds or sid in done or " " in x["to"]:
                continue
            done.add(sid)
            ph = x["name"].split(":", 1)[1]
            ipa = x.get("note", "").split("(")[0].strip()
            vowel = phones.get(phone, {}).get("kind") == "vowel"
            frame = ("t'%st" % ph) if vowel else ("'a%sa" % ph)
            letter = base_letter(ipa, flags)
            st = flags.get(letter)
            flag = ("master table: %s%s%s" % (st[0], ", approximate" if st[1] else "",
                                              ", %d values estimated" % st[2] if st[2] else "")) if st else \
                "not a letter of the master table on its own"
            add("sounds", "u-%s" % sid, "the sound %s (%s)" % (ipa, sid), "espeak", frame, "",
                "Is this a sound of your variety? Does it sound like the sound it should be (%s)?" % ipa,
                extra={"ipa_sound": ipa, "said_as": "the module's phone %s, reshaped by %s" % (phone, " ".join(
                    "%s=%s" % kv for kv in sounds[sid]["keys"].items())), "flag": flag})

    # render, group by group (one map per call)
    by_map = {}
    for it in items:
        by_map.setdefault(it["map"], []).append(it)
    for mp, group in by_map.items():
        rs = E.render(tag, [(it["id"], it["kind"], it["text"]) for it in group], work=os.path.join(work, "r"),
                      map_path=mp)
        for it, r in zip(group, rs):
            wav = os.path.join("audio", it["id"] + ".wav")
            shutil.copy(r["wav"], os.path.join(out, wav))
            it["audio"] = wav.replace(os.sep, "/")
            it["ms"] = r["case_ms"]
            it["phones"] = " ".join(ph["name"] for ph in r["phones"])
            it["diag"] = ["%s %s %s" % (d.get("level"), d.get("kind"), d.get("detail")) for d in r.get("diag", [])]
            rd = vowel_readings(r)
            it["vowels"] = [dict(phone=a, f1_asked=c, f2_asked=d, f1_measured=e, f2_measured=f, ms=g)
                            if it["group"] == "compare" else
                            dict(phone=a, sound=b, f1_asked=c, f2_asked=d, f1_measured=e, f2_measured=f, ms=g)
                            for a, b, c, d, e, f, g in rd]
            png = os.path.join("spectrograms", it["id"] + ".png")
            draw(r, os.path.join(out, png), "%s: %s" % (tag, it["label"]))
            it["spectrogram"] = png.replace(os.sep, "/")
            it["alt"] = describe(it, rd)
    for it in items:
        if it["kind"] == "text":
            it["ipa"] = espeak_ipa(voice, it["text"]) if voice else None
        else:
            it["ipa"] = "[%s] (eSpeak NG phonemes, in a frame)" % it["text"]
        it.pop("map")
    shutil.rmtree(work, ignore_errors=True)

    info = dict(tag=tag, name=name, kind=flat["pack"]["kind"], made=datetime.date.today().isoformat(),
                template=flat["ini"]["Language"]["Template"], reader=voice, preset=1,
                variety=meta.get("variety", ""), region=meta.get("region", ""),
                speaker_group=meta.get("speaker_group", ""), status=meta.get("status", {}),
                sentences_source=sent_src, ipa_from=("eSpeak NG %s" % ESPEAK) if os.path.isfile(ESPEAK) else None,
                flags_note=flag_err)
    with open(os.path.join(out, "items.json"), "w", encoding="utf-8") as f:
        json.dump(dict(packet=info, items=items), f, ensure_ascii=False, indent=1)
    os.makedirs(KEYS, exist_ok=True)
    with open(os.path.join(KEYS, "%s.json" % tag), "w", encoding="utf-8") as f:
        json.dump(dict(packet=info["tag"], made=info["made"], items=key), f, ensure_ascii=False, indent=1)
    write_checklist(out, info, items)
    write_feedback(out, info, items)
    write_readme(out, info)
    write_html(out, info, items)
    return info, items


# ---------------------------------------------------------------- the texts

def write_checklist(out, info, items):
    v = info["variety"] or info["name"]
    lines = [
        "# Reviewer's checklist: %s (%s)" % (info["name"], info["tag"]), "",
        "Thank you for listening. You do not need to know anything about phonetics. Answer what you can;",
        "\"I don't know\" is a good answer. Write your answers in `feedback.toml` (any text editor will do).", "",
        "The voice is a synthetic adult man's voice. It will never sound exactly like a person: we want to",
        "know whether it sounds like **%s** and where it does not." % v, "",
        "## About you (needed: a review is only recorded with a name and a date)", "",
        "1. Your name, as you want it recorded (or a stable pseudonym), and today's date.",
        "2. Which variety you speak natively, where you grew up, and for how long.",
        "3. Whether you are also a linguist or a language teacher (optional).", "",
        "## For every word and sentence", "",
        "4. **Understandable?** yes, mostly, or no.",
        "5. **Does it sound like your variety?** yes, partly, or no. If not, which word or sound is wrong?",
        "6. **Voice quality:** is it too buzzy, too breathy, too harsh, or fine?", "",
        "## For the pairs of words", "",
        "7. Say whether the two words should sound **the same** or **different** in your variety, and",
        "   whether the voice makes them the same or different.", "",
        "## For the A/B comparisons", "",
        "8. The same word twice. **Which is nearer to your variety: A, B, both the same, or neither?**",
        "   (Do not try to guess which one we changed.)", "",
        "## For the single sounds", "",
        "9. A sound of the language on its own, in a short frame. **Is it a sound of your variety?**",
        "   Does it sound like the symbol it is given? If it sounds like another sound, which one?", "",
        "## At the end", "",
        "10. Which **three sentences sound least natural**?",
        "11. Overall, would you accept this voice as **recognisably %s**? yes, with changes, or no." % v,
        "12. Anything else, in your own words.", "",
        "Items in this packet: %d (%s)." % (len(items), ", ".join(
            "%s %d" % (g, sum(1 for i in items if i["group"] == g)) for g in
            ("words", "sentences", "pairs", "compare", "sounds") if any(i["group"] == g for i in items))), "",
    ]
    with open(os.path.join(out, "CHECKLIST.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def _q(s):
    return json.dumps(s, ensure_ascii=False)


def write_feedback(out, info, items):
    lines = [
        "# Feedback on the review packet %s (%s), made %s." % (info["tag"], info["name"], info["made"]),
        "# Fill in what you can; leave \"\" where you have no answer. Answers: see CHECKLIST.md.",
        "# Send the filled file back to whoever gave you the packet. It is read by engine/review/ingest_feedback.py.",
        "",
        "[packet]",
        "tag = %s" % _q(info["tag"]),
        "made = %s" % _q(info["made"]),
        "",
        "[reviewer]",
        "name = \"\"                 # required: as it is to be recorded (or a stable pseudonym)",
        "date = \"\"                 # required: the date you reviewed, YYYY-MM-DD",
        "native_variety = \"\"       # required: the variety you speak natively",
        "grew_up = \"\"              # where, and for how long",
        "expertise = \"\"            # optional: linguist, teacher, ...",
        "consent_to_name = \"\"      # required: \"yes\" if your name may be written in the project's files",
        "",
        "[overall]",
        "accept = \"\"               # required: yes | with changes | no  (recognisably %s?)" % (info["variety"] or info["name"]),
        "least_natural = []        # up to three sentence ids, e.g. [\"s-03\", \"s-07\"]",
        "voice_quality = \"\"        # fine | buzzy | breathy | harsh",
        "comments = \"\"",
        "",
    ]
    for it in items:
        if it["group"] == "compare":
            if it["version"] == "B":
                continue  # one answer for the word: its two versions share it
            lines.append("[item.%s]" % _q(it["id"][:-2]))
            lines.append("# the word '%s', versions A and B" % it["orthography"])
            lines.append("nearer = \"\"            # A | B | same | neither")
            lines.append("notes = \"\"")
            lines.append("")
            continue
        lines.append("[item.%s]" % _q(it["id"]))
        lines.append("# %s%s" % (it["label"], (": " + it["orthography"]) if it["orthography"] else ""))
        if it["group"] == "pairs":
            lines.append("should_be = \"\"         # same | different (in your variety)")
            lines.append("sounds = \"\"            # same | different (as the voice says them)")
        else:
            lines.append("understood = \"\"        # yes | mostly | no")
            lines.append("like_my_variety = \"\"   # yes | partly | no")
        lines.append("notes = \"\"")
        lines.append("")
    with open(os.path.join(out, "feedback.toml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def write_readme(out, info):
    st = info["status"] or {}
    lines = [
        "# Review packet: %s (%s)" % (info["name"], info["tag"]), "",
        "Made %s by `engine/review/make_packet.py`. Open `index.html` in a web browser: every item is there" % info["made"],
        "with its audio, its spelling, its IPA (as eSpeak NG, the reader, reads it) and a spectrogram whose",
        "description gives the numbers in words. When the packet is made, the same audio is also written to",
        "`audio/` and the pictures to `spectrograms/` (the repository keeps only `index.html`, which embeds them;",
        "make the packet again to have the loose files).", "",
        "**Send the reviewer** this folder, or just `index.html`, `CHECKLIST.md` and `feedback.toml`. Which A/B",
        "version is which, and what each pair tests, is kept outside it (`docs/tts-extension/review/keys/`).", "",
        "- Speaking module: `%s`, preset 1 (adult male). Reader: eSpeak NG voice `%s`." % (info["template"], info["reader"]),
        "- Variety: %s. Region: %s. Speaker group the pack aims at: %s." % (
            info["variety"] or "(not recorded)", info["region"] or "(not recorded)", info["speaker_group"] or "(not recorded)"),
        "- Status when made: level %s (%s). Only a named native reviewer's sign-off makes it level 5" % (
            st.get("level", "?"), LEVELS.get(st.get("level"), "?")),
        "  (native-validated); until then nothing here is called authentic.", "",
        "**For the reviewer:** read `CHECKLIST.md`, listen, and fill in `feedback.toml`.", "",
        "**For the project:** `python engine/review/ingest_feedback.py <filled feedback.toml>` records it in",
        "`docs/tts-extension/LANGUAGE_STATUS.md` (only with a named reviewer, a date and consent to be named).", "",
    ]
    with open(os.path.join(out, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


GROUPS = (("words", "Words"), ("sentences", "Sentences"), ("pairs", "Pairs of words"),
          ("compare", "A/B comparisons: the same word, two versions"), ("sounds", "Single sounds"))


def _data(path, mime):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode("ascii"))


def write_html(out, info, items):
    e = html.escape
    st = info["status"] or {}
    body = [
        "<h1>Review packet: %s (%s)</h1>" % (e(info["name"]), e(info["tag"])),
        "<p>Made %s. Speaking module <code>%s</code>, preset 1 (adult male); reader eSpeak NG <code>%s</code>. "
        "Variety: %s. Region: %s. Status: level %s (%s); nothing here is called authentic until a named native "
        "reviewer signs off.</p>" % (e(info["made"]), e(info["template"]), e(info["reader"] or ""),
                                     e(info["variety"] or "not recorded"), e(info["region"] or "not recorded"),
                                     e(str(st.get("level", "?"))), e(LEVELS.get(st.get("level"), "?"))),
        "<p>Each item: the audio, what was said, the IPA, the question, and a spectrogram (lines: the formants the "
        "engine asked for; dots: measured in the sound). The picture's description gives the numbers. "
        "Questions are in CHECKLIST.md; answers go in feedback.toml.</p>",
    ]
    for g, title in GROUPS:
        its = [i for i in items if i["group"] == g]
        if not its:
            continue
        body.append('<section><h2 id="%s">%s (%d)</h2>' % (g, e(title), len(its)))
        for it in its:
            body.append('<article id="%s"><h3>%s <small>(%s)</small></h3>' % (e(it["id"]), e(it["label"]), e(it["id"])))
            body.append('<audio controls preload="none" src="%s" aria-label="%s"></audio>'
                        % (_data(os.path.join(out, it["audio"]), "audio/wav"), e(it["label"])))
            rows = []
            if it["orthography"]:
                rows.append(("Text", it["orthography"]))
            rows.append(("IPA", it.get("ipa") or "not available"))
            for k, lab in (("said_as", "How the engine makes it"), ("flag", "Flag")):
                if it.get(k):
                    rows.append((lab, it[k]))
            rows.append(("Question", it["question"]))
            rows.append(("Engine phones", it["phones"]))
            if it["diag"]:
                rows.append(("Lost on the way", "; ".join(it["diag"])))
            body.append("<table>%s</table>" % "".join("<tr><th scope=\"row\">%s</th><td>%s</td></tr>" % (e(a), e(b))
                                                      for a, b in rows))
            body.append('<img src="%s" alt="%s">' % (_data(os.path.join(out, it["spectrogram"]), "image/png"),
                                                     e(it["alt"])))
            body.append("</article>")
        body.append("</section>")
    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review packet %s</title>
<style>
:root{--bg:#fff;--fg:#111;--mut:#555;--line:#ddd}
@media (prefers-color-scheme: dark){:root{--bg:#121212;--fg:#eee;--mut:#aaa;--line:#333}}
body{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:60rem;margin:0 auto;padding:0 16px}
article{border-top:1px solid var(--line);padding:.5rem 0}
th{text-align:left;color:var(--mut);padding-right:1rem;vertical-align:top;font-weight:normal}
img{max-width:100%%;height:auto;background:#fff} audio{width:100%%;max-width:28rem}
small{color:var(--mut)}
</style></head><body><main>
%s
</main></body></html>
""" % (e(info["tag"]), "\n".join(body))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(page)


def main():
    ap = argparse.ArgumentParser(description="Make the native review packet of a language, dialect or accent.")
    ap.add_argument("tag")
    ap.add_argument("--out")
    ap.add_argument("--no-flagged", action="store_true", help="leave out the single sounds")
    a = ap.parse_args()
    out = a.out or os.path.join(OUT, a.tag)
    info, items = make(a.tag, out, not a.no_flagged)
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)
    print("packet %s: %d items (%s); %s; index.html %d bytes; folder %d bytes" % (
        a.tag, len(items), ", ".join("%s %d" % (g, sum(1 for i in items if i["group"] == g)) for g, _ in GROUPS
                                      if any(i["group"] == g for i in items)),
        out, os.path.getsize(os.path.join(out, "index.html")), size))
    lost = [i["id"] for i in items if i["diag"]]
    if lost:
        print("items where the front-end or accent layer reported a loss: %d (%s)" % (len(lost), " ".join(lost[:10])))
    print("IPA: %s" % (info["ipa_from"] or "NOT AVAILABLE (espeak-ng.exe not found; set EVV_ESPEAK_EXE)"))


if __name__ == "__main__":
    main()
