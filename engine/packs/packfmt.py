"""Read and write the files of a pack as data: language.ini, sounds.map, phonemes.map, sample.txt.

A pack's files are text in formats the product already reads (docs/LANGUAGES.md). This module takes
each file apart into records (the same record for a line in either map) and puts it together again,
byte for byte as the generators (engine/make_espeak_packs.py, engine/accent/mapwriter.py,
engine/espeak_phonemes.py) write it. A line that does not survive that round trip is kept as a
`raw` record, so nothing is ever lost or changed; the importer counts them.

Record kinds of a map (the keys of a record are the fields it is written with):

    blank       an empty line                                          key b<n>
    comment     text="# ..."                                           key c<n>
    directive   name, value: template, style, vowels, glides, schwa,
                secondary, words, onset, cluster, tone, weaktones      key name (cluster: name:value; tone: name:first word)
    accent      set={k="v", ...}: the melody's keys, in order          key "accent"
    whwords     where, words=[...]                                     key w<n>
    says        from, to=[...]                                         key says:<from>
    sound       id, keys={k="v", ...}, note                            key id
    map         name, to, note: a phoneme or a letter and what says it  key name
    raw         text: a line this module could not take apart          key r<n>

The key is what an inheriting pack names to replace or remove a line (DESIGN.md 6.3).
"""
import re

SCALAR_DIRECTIVES = ("template", "style", "vowels", "glides", "schwa", "secondary", "words", "onset", "weaktones")
REPEAT_DIRECTIVES = ("cluster", "tone")


# ---------------------------------------------------------------- keys

def line_key(rec):
    """The key an inheriting pack uses for this line, when the record carries none of its own."""
    if "key" in rec:
        return rec["key"]
    k = rec["kind"]
    if k == "sound":
        return rec["id"]
    if k == "map":
        return rec["name"]
    if k == "accent":
        return "accent"
    if k == "says":
        return "says:" + rec["from"]
    if k == "directive":
        n = rec["name"]
        if n == "cluster":
            return "cluster:" + rec["value"]
        if n == "tone":
            return "tone:" + rec["value"].split()[0]
        return n
    raise ValueError("a %s line needs a key of its own" % k)


# ---------------------------------------------------------------- the maps

def _render_line(r, fmt):
    k = r["kind"]
    if k == "blank":
        return ""
    if k == "comment":
        return r["text"]
    if k == "raw":
        return r["text"]
    if k == "directive":
        return "%s %s" % (r["name"], r["value"])
    if k == "accent":
        return "accent " + " ".join("%s=%s" % kv for kv in r["set"].items())
    if k == "whwords":
        return "whwords %s %s" % (r["where"], " ".join(r["words"]))
    if k == "says":
        return "says %s %s" % (r["from"], " ".join(r["to"]))
    if k == "sound":
        keys = " ".join("%s=%s" % kv for kv in r["keys"].items())
        return "%-40s # %s" % ("sound %s %s" % (r["id"], keys), r.get("note", ""))
    if k == "map":
        note = r.get("note", "")
        if fmt == "phonemes":  # engine/espeak_phonemes.py: a phoneme of a table has its IPA after it, a letter has nothing
            if r["name"].startswith("@"):
                return "%-16s %-14s  # %s" % (r["name"], r["to"], note)
            return "%-16s %s" % (r["name"], r["to"])
        return ("%-16s %-22s%s" % (r["name"], r["to"], ("  # " + note) if note else "")).rstrip()
    raise ValueError("unknown line kind %r" % k)


def render_map(records, eol="\r\n", fmt="sounds"):
    """fmt: "sounds" (engine/accent/mapwriter.py) or "phonemes" (engine/espeak_phonemes.py)."""
    return eol.join(_render_line(r, fmt) for r in records) + eol


def _parse_line(line):
    if line == "":
        return {"kind": "blank"}
    if line.startswith("#"):
        return {"kind": "comment", "text": line}
    w = line.split()
    head = w[0]
    if head == "accent" and len(w) > 1 and all("=" in t for t in w[1:]):
        return {"kind": "accent", "set": dict(t.split("=", 1) for t in w[1:])}
    if head == "whwords" and len(w) > 2:
        return {"kind": "whwords", "where": w[1], "words": w[2:]}
    if head == "says" and len(w) > 2:
        return {"kind": "says", "from": w[1], "to": w[2:]}
    if head == "sound" and len(w) > 2 and re.fullmatch(r"s\d+", w[1]):
        left, _, note = line.partition(" # ")
        parts = left.split()
        if all("=" in t for t in parts[2:]):
            return {"kind": "sound", "id": parts[1], "keys": dict(t.split("=", 1) for t in parts[2:]),
                    "note": note}
    if head in SCALAR_DIRECTIVES + REPEAT_DIRECTIVES and len(w) > 1:
        return {"kind": "directive", "name": head, "value": line[len(head):].strip()}
    m = re.fullmatch(r"(\S+)\s+(\S(?:.*?\S)??)(?:\s{2,}# (.*))?", line)
    if m and not m.group(2).startswith("#"):
        return {"kind": "map", "name": m.group(1), "to": m.group(2), "note": m.group(3) or ""}
    m = re.fullmatch(r"(\S+)", line)
    if m:
        return {"kind": "map", "name": m.group(1), "to": "", "note": ""}
    return {"kind": "raw", "text": line}


def parse_map(text, fmt="sounds"):
    """-> (records, eol). Every record renders back to its own line; a line that does not is `raw`."""
    eol = "\r\n" if "\r\n" in text else "\n"
    body = text.replace("\r\n", "\n")
    assert body.endswith("\n"), "a map ends with a newline"
    lines = body[:-1].split("\n")
    out = []
    counts = {"blank": 0, "comment": 0, "whwords": 0, "raw": 0}
    for line in lines:
        r = _parse_line(line)
        if r["kind"] != "raw" and _render_line(r, fmt) != line:
            r = {"kind": "raw", "text": line}
        k = r["kind"]
        if k in counts:
            counts[k] += 1
            r = dict(r)
            r["key"] = {"blank": "b", "comment": "c", "whwords": "w", "raw": "r"}[k] + str(counts[k])
        out.append(r)
    keys = [line_key(r) for r in out]
    if len(set(keys)) != len(keys):  # two lines of one key: the later ones are kept as they are
        seen = {}
        for r in out:
            kk = line_key(r)
            seen[kk] = seen.get(kk, 0) + 1
            if seen[kk] > 1:
                r["key"] = "%s#%d" % (kk, seen[kk])
    return out, eol


# ---------------------------------------------------------------- language.ini

def parse_ini(text):
    """-> ({section: {key: value}}, eol), sections in file order; a comment line is the key _c<n>,
    a blank line the key _b<n>, both in place; lines before the first section are the section _top."""
    eol = "\r\n" if "\r\n" in text else "\n"
    body = text.replace("\r\n", "\n")
    lines = body.split("\n")
    sec = "_top"
    out = {"_top": {}}
    n = 0
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            sec = line[1:-1]
            out[sec] = {}
            n = 0
            continue
        n += 1
        if line == "":
            out[sec]["_b%d" % n] = ""
        elif line.startswith(";"):
            out[sec]["_c%d" % n] = line
        else:
            k, _, v = line.partition("=")
            out[sec][k] = v
    return out, eol


def render_ini(ini, eol="\r\n"):
    lines = []
    for sec, items in ini.items():
        if sec != "_top":
            lines.append("[%s]" % sec)
        for k, v in items.items():
            if k.startswith("_b"):
                lines.append("")
            elif k.startswith("_c"):
                lines.append(v)
            else:
                lines.append("%s=%s" % (k, v))
    return eol.join(lines)
