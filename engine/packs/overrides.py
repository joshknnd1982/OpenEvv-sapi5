# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""A pack's overrides: a sound's target moved, with provenance on every value (DESIGN.md 6.2, 6.3).

    [[override]]
    sound = "ʉː"                        # the sound, in IPA (engine-neutral)
    phonemes = ["@en-sc:u:"]            # the reader's phonemes it is said for (the legacy realization)
    state = "proposed"                  # proposed | applied: only `applied` reaches languages/
    recordings = ["awb/arctic_a0001", ...]   # the recordings its measured values come from (or on each value)
    note = "..."
    [override.formants.f2]              # f1 f2 f3, each a value with its provenance
    v = 1523.0                          # hertz, at the size of the template's own voice (normalize.py)
    tag = "measured"                    # measured | literature | derived | estimated | created | approximate
    ref = "cmu_arctic"                  # a source id of docs/tts-extension/REFERENCES.md
    recordings = [...]                  # measured: the recordings, when not given for the whole override
    n = 41                              # measured: tokens;  speakers = 1: speakers
    below_minimum = true                # measured: fewer than AUTHENTICITY.md's minimums
    norm = "nearey-uniform x0.958 to engx"   # measured: how the speaker was put at the voice's size
    evidence = "measured/cmu_arctic.json"    # measured: the targets file (in the pack's folder) it came from
    deviation = "..."                   # approximate: what differs from the source, in plain words
    [override.duration]                 # the vowel's audible length, ms, at the module's speaking rate
    v = 104.0                           # (the same keys of provenance as a formant)

Inheritance: overrides are keyed by `sound`; a child's override of a sound the parent also
overrides changes only what it names (formant by formant); `remove_overrides = ["<sound>"]` at the
top of a pack drops an inherited one whole.

Realization ("legacy" packs, and "master" packs on top of the master path's lines): the override's hertz become a sound line of ratios against the module
phone each listed phoneme is said with (engine/accent/chassis/<template>.json, the module's own
phones as measured), on top of the keys of the sound line that phoneme had, under a new sound id;
a duration becomes `dur`, the per cent of the phone's stretch that makes the vowel sound that long
(engine/accent/sounds.py `lasting`: what lies outside the stretch stays as it was), 40 to 300;
the listed phonemes are pointed at it. Nothing else moves. `proposed` overrides are realised only
when asked for (a scratch build to measure them, `build_packs.py build <out> --proposed`): putting
them into languages/ is the human's say-so (R18), recorded by setting `state = "applied"`.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CHASSIS = os.path.join(os.path.dirname(HERE), "accent", "chassis")

TAGS = ("measured", "literature", "derived", "estimated", "created", "approximate")
STATES = ("proposed", "applied")
FORMANT_KEYS = ("f1", "f2", "f3")
OVERRIDE_KEYS = {"sound", "phonemes", "state", "note", "formants", "duration", "recordings"}
VALUE_KEYS = {"v", "tag", "ref", "recordings", "n", "speakers", "below_minimum", "norm", "deviation", "evidence"}
# a ratio outside this is refused: no measured or cited vowel of a man's voice lies so far from the
# module's nearest phone, and a value out there is a typing slip or a caricature (AUTHENTICITY.md)
RATIO_MIN, RATIO_MAX = 50, 200


class OverrideError(Exception):
    pass


def check_value(v, where, recordings=None):
    if not isinstance(v, dict) or set(v) - VALUE_KEYS:
        raise OverrideError("%s: a value holds only %s" % (where, sorted(VALUE_KEYS)))
    if not isinstance(v.get("v"), (int, float)) or v["v"] <= 0:
        raise OverrideError("%s: v must be a positive number of hertz" % where)
    if v.get("tag") not in TAGS:
        raise OverrideError("%s: tag %r is not one of %s (every value carries its provenance)" % (where, v.get("tag"), TAGS))
    if v["tag"] in ("measured", "literature") and not v.get("ref"):
        raise OverrideError("%s: a %s value names its source (ref)" % (where, v["tag"]))
    if v["tag"] == "measured":
        recs = v.get("recordings") or recordings
        if not recs or not all(isinstance(r, str) and r for r in recs):
            raise OverrideError("%s: a measured value lists the recordings it was measured on" % where)
        if not isinstance(v.get("n"), int) or v["n"] < 1 or not isinstance(v.get("speakers"), int):
            raise OverrideError("%s: a measured value says how many tokens (n) and speakers" % where)
        if not v.get("evidence"):
            raise OverrideError("%s: a measured value names the targets file it came from (evidence)" % where)
    if v["tag"] == "approximate" and not v.get("deviation"):
        raise OverrideError("%s: an approximate value states its deviation" % where)


def check_override(o, where):
    if not isinstance(o, dict) or set(o) - OVERRIDE_KEYS:
        raise OverrideError("%s: an override holds only %s" % (where, sorted(OVERRIDE_KEYS)))
    if not isinstance(o.get("sound"), str) or not o["sound"]:
        raise OverrideError("%s: an override names its sound" % where)
    where = "%s override %r" % (where, o["sound"])
    if o.get("state", "proposed") not in STATES:
        raise OverrideError("%s: state %r is not one of %s" % (where, o.get("state"), STATES))
    if "phonemes" in o and not (isinstance(o["phonemes"], list) and all(isinstance(p, str) for p in o["phonemes"])):
        raise OverrideError("%s: phonemes is a list of the reader's phoneme names" % where)
    f = o.get("formants", {})
    if set(f) - set(FORMANT_KEYS):
        raise OverrideError("%s: formants are %s" % (where, FORMANT_KEYS))
    for k, v in f.items():
        check_value(v, "%s %s" % (where, k), o.get("recordings"))
    if "duration" in o:
        check_value(o["duration"], "%s duration" % where, o.get("recordings"))


def merge(base, child_list, removes, where):
    """base: {sound: override}; returns the merged dict (a child's override changes only what it names)."""
    out = {s: json.loads(json.dumps(o)) for s, o in base.items()}
    for s in removes:
        if s not in out:
            raise OverrideError("%s: remove_overrides %r, but no override of that sound is inherited" % (where, s))
        del out[s]
    for o in child_list:
        cur = out.setdefault(o["sound"], {"sound": o["sound"]})
        for k, v in o.items():
            if k == "formants":
                cur.setdefault("formants", {}).update(json.loads(json.dumps(v)))
            elif k == "duration":
                cur["duration"] = json.loads(json.dumps(v))
            else:
                cur[k] = json.loads(json.dumps(v))
    return out


def chassis(template):
    path = os.path.join(CHASSIS, "%s.json" % template)
    if not os.path.isfile(path):
        raise OverrideError("no measurement of the module %s's own phones (%s)" % (template, path))
    with open(path, encoding="utf-8") as f:
        return json.load(f)["phones"]


def realize(flat, include_proposed=False):
    """Writes the overrides that are to be realised into flat['sounds'] (in place). Returns a list of
    (sound, phoneme, module phone, new sound id, keys) for what was done."""
    ovs = flat.get("override", {})
    todo = [o for o in ovs.values() if o.get("state", "proposed") == "applied" or include_proposed]
    if not todo:
        return []
    tag = flat["pack"]["tag"]
    if flat.get("engine", {}).get("realization") not in ("legacy", "master"):
        raise OverrideError("pack %r: overrides are realised only for realization = \"legacy\" or \"master\"" % tag)
    lines = flat.get("sounds", {}).get("line", [])
    template = flat["ini"]["Language"]["Template"]
    phones = chassis(template)
    sounds = {x["id"]: x for x in lines if x["kind"] == "sound"}
    used = [int(i[1:]) for i in sounds if i[1:].isdigit()]
    nxt = max(used or [0]) + 1
    last_sound = max((j for j, x in enumerate(lines) if x["kind"] == "sound"), default=len(lines) - 1)
    done = []
    for o in sorted(todo, key=lambda o: o["sound"]):
        names = o.get("phonemes") or []
        if not names:
            raise OverrideError("pack %r override %r: no phonemes to say it for" % (tag, o["sound"]))
        for name in names:
            at = [j for j, x in enumerate(lines) if x["kind"] == "map" and x["name"] == name]
            if not at:
                raise OverrideError("pack %r override %r: the sound map has no phoneme %r" % (tag, o["sound"], name))
            line = lines[at[0]]
            to = line["to"]
            if " " in to.strip() or to.strip() in ("", "-"):
                raise OverrideError("pack %r override %r: %r is said as %r, not one phone" % (tag, o["sound"], name, to))
            phone, _, sid = to.partition("=")
            if phone not in phones or phones[phone].get("kind") != "vowel":
                raise OverrideError("pack %r override %r: module phone %r of %s is not a measured vowel" % (
                    tag, o["sound"], phone, template))
            keys = dict(sounds[sid]["keys"]) if sid else {}
            for k, v in sorted(o.get("formants", {}).items()):
                own = phones[phone]["f"][int(k[1]) - 1]
                pc = int(round(100.0 * v["v"] / own))
                if not RATIO_MIN <= pc <= RATIO_MAX:
                    raise OverrideError("pack %r override %r: %s %.0f Hz is %d%% of %s's %d Hz, outside %d to %d%%" % (
                        tag, o["sound"], k, v["v"], pc, phone, own, RATIO_MIN, RATIO_MAX))
                keys[k] = str(pc)
            if "duration" in o:
                m = phones[phone]
                r = int(round(100.0 * (m["ms"] + o["duration"]["v"] - m["ms_sound"]) / m["ms"]))
                if not 40 <= r <= 300:
                    raise OverrideError("pack %r override %r: duration %.0f ms is a stretch of %d%% of %s's, outside 40 to 300%%"
                                        % (tag, o["sound"], o["duration"]["v"], r, phone))
                keys["dur"] = str(r)
            new = "s%d" % nxt
            nxt += 1
            rec = {"kind": "sound", "id": new, "keys": keys, "note": "%s (override, %s)" % (
                o["sound"], o.get("state", "proposed"))}
            last_sound += 1
            lines.insert(last_sound, rec)
            at = [j for j, x in enumerate(lines) if x["kind"] == "map" and x["name"] == name]
            lines[at[0]] = dict(line, to="%s=%s" % (phone, new))
            sounds[new] = rec
            done.append((o["sound"], name, phone, new, keys))
    return done
