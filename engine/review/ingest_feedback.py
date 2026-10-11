"""Record a reviewer's completed feedback (playbook Phase 7, step 5; AUTHENTICITY.md, "Ingesting feedback").

    python engine/review/ingest_feedback.py <filled feedback.toml> [--dry-run]
    python engine/review/ingest_feedback.py --selftest

A review is recorded only when the form names its reviewer, gives the date (YYYY-MM-DD), the native
variety, consent to be named ("yes"), and an overall answer (yes | with changes | no). Anything less is
refused and nothing is written. When it is recorded:

  * the form is copied to docs/tts-extension/review/feedback/<tag>/<date>-<name>.toml;
  * docs/tts-extension/review/signoffs.json gains a record (who, when, variety, accept, the items
    answered "no", the least natural sentences, the A/B answers counted);
  * the section between the NATIVE markers of LANGUAGE_STATUS.md is written again from signoffs.json;
  * if the answer was "yes", the pack's [meta] status gets the reviewer and the date, and level 5
    (native-validated) only if the language already stands at level 4 (a level needs every level
    below it: report.py); any other answer leaves the pack's status as it was. The sign-off table
    shows each review's level before and after, the A/B answers mapped through the packet's key (review/keys/<tag>.json)
    (which version was new), and the pairs' answers.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "engine", "packs"))
import packlib as L  # noqa: E402
import tomlio  # noqa: E402

DOCS = os.path.join(ROOT, "docs", "tts-extension")
BEGIN, END = "<!-- NATIVE BEGIN (written by engine/review/ingest_feedback.py) -->", "<!-- NATIVE END -->"
ACCEPT = ("yes", "with changes", "no")


class Refused(Exception):
    pass


def read_form(path):
    try:
        d = tomlio.load(path)
    except Exception as e:
        raise Refused("the form is not readable TOML: %s" % e)
    r, o, p = d.get("reviewer", {}), d.get("overall", {}), d.get("packet", {})
    for k in ("name", "date", "native_variety", "consent_to_name"):
        if k in r and not isinstance(r[k], str):
            raise Refused("reviewer %s must be written in quotes (a string), as the form shows" % k)
    missing = [k for k in ("name", "date", "native_variety") if not str(r.get(k, "")).strip()]
    if missing:
        raise Refused("the form has no %s: a review is recorded only with a named reviewer and a date"
                      % ", ".join(missing))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["date"].strip()):
        raise Refused("the date %r is not YYYY-MM-DD" % r["date"])
    try:
        datetime.date.fromisoformat(r["date"].strip())
    except ValueError:
        raise Refused("the date %r is not a day of the calendar" % r["date"])
    if str(r.get("consent_to_name", "")).strip().lower() != "yes":
        raise Refused("consent_to_name is not \"yes\": the reviewer has not agreed to be named, so nothing is recorded")
    if str(o.get("accept", "")).strip().lower() not in ACCEPT:
        raise Refused("overall accept must be one of %s" % (ACCEPT,))
    if not p.get("tag"):
        raise Refused("the form names no packet tag")
    return d


def packet_key(tag, docs=DOCS):
    path = os.path.join(docs, "review", "keys", "%s.json" % tag)
    return json.load(open(path, encoding="utf-8"))["items"] if os.path.isfile(path) else {}


def summarize(d, key=None):
    key = key or {}
    items = d.get("item", {})
    no = sorted(k for k, v in items.items() if str(v.get("understood", "")).lower() == "no"
                or str(v.get("like_my_variety", "")).lower() == "no")
    ab = {}
    for k, v in items.items():
        n = str(v.get("nearer", "")).strip().lower()
        if n in ("a", "b"):
            # one answer a word (the form's item is the word, "<id>"; the versions are "<id>-A", "<id>-B");
            # the packet's key (review/keys/<tag>.json) says which version carried the override
            chosen = key.get("%s-%s" % (k, n.upper()), {}).get("version", "unknown (no key)")
            n = {"override": "the measured override", "pack": "the pack as it is"}.get(chosen, chosen)
        if n:
            ab[n] = ab.get(n, 0) + 1
    pairs = {}
    for k, v in items.items():
        if str(v.get("should_be", "")).strip() or str(v.get("sounds", "")).strip():
            pid = key.get(k, {}).get("pair") or k.rsplit("-", 1)[0]
            pairs.setdefault(pid, "should be %s, voice says %s" % (str(v.get("should_be", "")).strip() or "?",
                                                                     str(v.get("sounds", "")).strip() or "?"))
    answered = sum(1 for v in items.values() if any(str(x).strip() for k, x in v.items() if k != "notes"))
    r, o = d["reviewer"], d["overall"]
    return dict(tag=d["packet"]["tag"], packet_made=d["packet"].get("made", ""), reviewer=r["name"].strip(),
                date=r["date"].strip(), native_variety=r["native_variety"].strip(), grew_up=r.get("grew_up", ""),
                expertise=r.get("expertise", ""), accept=o["accept"].strip().lower(),
                least_natural=o.get("least_natural", []), voice_quality=o.get("voice_quality", ""),
                items_answered=answered, items_total=len(items), items_no=no, ab=ab, pairs=pairs,
                recorded=datetime.date.today().isoformat())


def status_section(records):
    lines = [BEGIN, ""]
    if not records:
        lines.append("None yet.")
    else:
        lines += ["| Tag | Reviewer | Date | Native variety | Accepts | Level | Items answered | Answered \"no\" | A/B: nearer | Pairs | Least natural |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in sorted(records, key=lambda x: (x["tag"], x["date"])):
            lines.append("| %s | %s | %s | %s | %s | %s | %d of %d | %s | %s | %s | %s |" % (
                x["tag"], x["reviewer"], x["date"], x["native_variety"], x["accept"],
                "%s to %s" % (x.get("level_before"), x.get("level_after")), x["items_answered"],
                x["items_total"], " ".join(x["items_no"]) or "none",
                ", ".join("%s %d" % kv for kv in sorted(x["ab"].items())) or "-",
                "; ".join("%s: %s" % kv for kv in sorted(x.get("pairs", {}).items())) or "-",
                " ".join(x["least_natural"]) or "-"))
    lines += ["", END]
    return "\n".join(lines)


def splice(text, section):
    if BEGIN in text and END in text:
        a = text.index(BEGIN)
        b = text.index(END) + len(END)
        return text[:a] + section + text[b:]
    head = "## Native-speaker sign-offs"
    if head not in text:
        raise Refused("LANGUAGE_STATUS.md has neither the NATIVE markers nor a '%s' heading" % head)
    a = text.index(head) + len(head)
    rest = text[a:]
    # the heading's old placeholder ("None yet.") is replaced by the section
    rest = re.sub(r"^\s*None yet\.\s*", "\n\n", rest, count=1)
    return text[:a] + "\n\n" + section + rest


def language_level(tag, status_md):
    m = re.search(r"^\| %s \| [^|]* \| [^|]* \| (\d) " % re.escape(tag), status_md, re.M)
    return int(m.group(1)) if m else None


def set_pack_status(tag, rec, level, packs_root=None):
    path = L.pack_path(tag, packs_root)
    text = open(path, encoding="utf-8").read()
    new = 'status = { level = %d, validated_by = %s, date = %s }' % (
        level, json.dumps(rec["reviewer"], ensure_ascii=False), json.dumps(rec["date"]))
    if re.search(r"^status = \{.*\}$", text, re.M):
        text = re.sub(r"^status = \{.*\}$", new.replace("\\", "\\\\"), text, count=1, flags=re.M)
    else:
        text = re.sub(r"^\[meta\]\n", "[meta]\n" + new + "\n", text, count=1, flags=re.M)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def ingest(form, docs=DOCS, packs_root=None, dry=False):
    d = read_form(form)
    rec = summarize(d, packet_key(d["packet"]["tag"], docs))
    tag = rec["tag"]
    flat, _ = L.resolve(tag, packs_root)  # the pack must exist
    status_path = os.path.join(docs, "LANGUAGE_STATUS.md")
    signoffs = os.path.join(docs, "review", "signoffs.json")
    records = json.load(open(signoffs, encoding="utf-8")) if os.path.isfile(signoffs) else []
    if any(x["tag"] == tag and x["reviewer"] == rec["reviewer"] and x["date"] == rec["date"] for x in records):
        raise Refused("this review (%s, %s, %s) is already recorded" % (tag, rec["reviewer"], rec["date"]))
    text = open(status_path, encoding="utf-8").read()
    level_now = language_level(tag, text) or flat.get("meta", {}).get("status", {}).get("level", 1)
    level = 5 if rec["accept"] == "yes" and level_now >= 4 else level_now
    rec["level_before"], rec["level_after"] = level_now, level
    if dry:
        return rec
    records.append(rec)
    os.makedirs(os.path.dirname(signoffs), exist_ok=True)
    with open(signoffs, "w", encoding="utf-8", newline="\n") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    keep = os.path.join(docs, "review", "feedback", tag, "%s-%s.toml" % (rec["date"], re.sub(r"\W+", "_", rec["reviewer"])))
    os.makedirs(os.path.dirname(keep), exist_ok=True)
    shutil.copy(form, keep)
    with open(status_path, "w", encoding="utf-8", newline="") as f:
        f.write(splice(text, status_section(records)))
    if rec["accept"] == "yes":
        # only a reviewer who accepts is named as the pack's validator; any other answer is recorded
        # in the sign-offs and leaves the pack's status as it was
        set_pack_status(tag, rec, level, packs_root)
    return rec


def selftest():
    """Everything on copies: the real LANGUAGE_STATUS.md, signoffs and packs are not touched."""
    work = tempfile.mkdtemp(prefix="ingest_")
    ok = True
    try:
        docs = os.path.join(work, "docs")
        os.makedirs(docs)
        shutil.copy(os.path.join(DOCS, "LANGUAGE_STATUS.md"), docs)
        os.makedirs(os.path.join(docs, "review", "keys"))
        with open(os.path.join(docs, "review", "keys", "en-gb-scotland.json"), "w", encoding="utf-8") as f:
            json.dump({"items": {"c-goose-A": {"version": "pack"}, "c-goose-B": {"version": "override"}}}, f)
        packs = os.path.join(work, "packs")
        tag = "en-gb-scotland"
        shutil.copytree(os.path.join(L.packs_dir(), tag), os.path.join(packs, tag))
        form = '''[packet]
tag = "en-gb-scotland"
made = "2026-10-11"
[reviewer]
name = "%s"
date = "%s"
native_variety = "%s"
consent_to_name = "%s"
[overall]
accept = "%s"
least_natural = ["s-02"]
[item."w-fleece"]
understood = "yes"
like_my_variety = "no"
notes = ""
[item."c-goose"]
nearer = "B"
'''
        cases = [
            ("blank form (as made)", ("", "", "", "", ""), "refused"),
            ("no date", ("TEST REVIEWER (selftest, not a real review)", "", "Scottish English", "yes", "yes"), "refused"),
            ("no consent to be named", ("TEST REVIEWER (selftest, not a real review)", "2026-10-11", "Scottish English", "", "yes"), "refused"),
            ("a bad answer", ("TEST REVIEWER (selftest, not a real review)", "2026-10-11", "Scottish English", "yes", "maybe"), "refused"),
            ("a date not in the calendar", ("TEST REVIEWER (selftest, not a real review)", "2026-13-40", "Scottish English", "yes", "yes"), "refused"),
            ("a reviewer who says no", ("TEST NAYSAYER (selftest, not a real review)", "2026-10-10", "Scottish English", "yes", "no"), "recorded"),
            ("complete", ("TEST REVIEWER (selftest, not a real review)", "2026-10-11", "Scottish English", "yes", "yes"), "recorded"),
            ("the same review again", ("TEST REVIEWER (selftest, not a real review)", "2026-10-11", "Scottish English", "yes", "yes"), "refused"),
        ]
        for name, vals, want in cases:
            path = os.path.join(work, "form.toml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(form % vals)
            before = open(os.path.join(docs, "LANGUAGE_STATUS.md"), encoding="utf-8").read()
            try:
                rec = ingest(path, docs, packs)
                got = "recorded"
                why = "level %s -> %s" % (rec["level_before"], rec["level_after"])
            except Refused as e:
                got, why = "refused", str(e)
            after = open(os.path.join(docs, "LANGUAGE_STATUS.md"), encoding="utf-8").read()
            changed = before != after
            good = got == want and changed == (want == "recorded")
            print("  %-26s %-8s (%s)%s: %s" % (name, got, why[:90], "; status file changed" if changed else "",
                                               "pass" if good else "FAIL"))
            ok &= good
        text = open(os.path.join(docs, "LANGUAGE_STATUS.md"), encoding="utf-8").read()
        sec = text[text.index(BEGIN):text.index(END)]
        good = "TEST REVIEWER" in sec and "w-fleece" in sec and "the measured override 1" in sec
        lvl = re.search(r"^status = .*$", open(L.pack_path(tag, packs), encoding="utf-8").read(), re.M)
        good &= lvl is not None and "TEST REVIEWER" in lvl.group(0) and "level = 5" not in lvl.group(0)
        good &= "NAYSAYER" in sec and "NAYSAYER" not in lvl.group(0)   # recorded, never named as validator
        print("  %-26s %s; pack: %s: %s" % ("what was written", " | ".join(sec.splitlines()[4].split("|")[1:6]),
                                             lvl.group(0) if lvl else "no status line", "pass" if good else "FAIL"))
        ok &= good
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("ingest selftest: %s" % ("pass" if ok else "FAILED"))
    return ok


def main():
    ap = argparse.ArgumentParser(description="Record a reviewer's completed feedback.toml.")
    ap.add_argument("form", nargs="?")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
    if not a.form:
        ap.print_help()
        return 2
    try:
        rec = ingest(a.form, dry=a.dry_run)
    except Refused as e:
        print("REFUSED, nothing written: %s" % e)
        return 1
    print("%s: %s review by %s (%s), %s; answered %d of %d items; level %s -> %s" % (
        "would record" if a.dry_run else "recorded", rec["tag"], rec["reviewer"], rec["native_variety"], rec["date"],
        rec["items_answered"], rec["items_total"], rec["level_before"], rec["level_after"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
