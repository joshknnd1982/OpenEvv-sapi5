"""The pack loader: packs/<tag>/pack.toml -> the files languages/<tag>/ holds today.

DESIGN.md 6: a pack is TOML; `extends` names one parent; the product only ever sees the complete,
flat result, written in today's formats (language.ini, sounds.map, phonemes.map, sample.txt).

What a pack file holds (format 1, realization "legacy": the sound definitions are the ones the
generator wrote, kept as data; M4 of DESIGN.md 11.3 turns them into master-table references):

    [pack]      tag, name, kind (language | dialect | accent), extends, format
    [meta]      variety, region, speaker_group, sources, recordings, date, licence, status, note
                (R14: documented, not asserted; engine/packs/validate_packs.py says what a dialect or accent must hold)
    [engine]    reader ("espeak:<voice>" | "module"), template, realization ("legacy" | "master" | "module")
    [files]     eol ("crlf" | "lf")
    [ini.<Section>]   the keys of language.ini; a key _cN is a comment line, _bN a blank line
    [sounds] / [phonemes]   line = [...] the records of sounds.map / phonemes.map (engine/packs/packfmt.py)
    [sample]    text
    [[override]]  a sound's target moved, every value with its provenance (engine/packs/overrides.py)
    remove      a list of dotted keys to delete from what the parent gave
    remove_overrides  a list of sounds whose inherited override is dropped

Inheritance (DESIGN.md 6.3), as built here:
  * a pack has at most one parent; a chain is allowed; a cycle or a missing parent stops the build;
  * tables merge key by key at every depth; a plain value replaces the parent's; a plain list replaces;
  * `line` is the one keyed list: an entry of a key the parent also has replaces it in place, a new
    entry goes at the end or where its `after = "<key>"` says ("^" is the very start); `remove = ["<key>"]`
    inside [sounds] or [phonemes] deletes lines; `reset = true` there drops everything inherited;
  * `remove = ["ini.Voice3.Params"]` at the top deletes any other inherited key;
  * anything unknown (a key, a section, a missing line to remove, a missing `after`) stops the build.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import overrides as O  # noqa: E402
import packfmt as F  # noqa: E402
import tomlio  # noqa: E402

FORMAT = 1
KINDS = ("language", "dialect", "accent")
REALIZATIONS = ("legacy", "master", "module")
TOP = {"pack", "meta", "engine", "files", "ini", "sounds", "phonemes", "sample", "remove", "override",
       "remove_overrides"}
PACK_KEYS = {"tag", "name", "kind", "extends", "format"}
META_KEYS = {"variety", "region", "speaker_group", "sources", "recordings", "date", "licence", "status", "note"}
ENGINE_KEYS = {"reader", "template", "realization"}
LINE_TABLE_KEYS = {"line", "remove", "reset"}
KIND_FIELDS = {
    "blank": {"kind", "key", "after"},
    "comment": {"kind", "key", "after", "text"},
    "raw": {"kind", "key", "after", "text"},
    "directive": {"kind", "key", "after", "name", "value"},
    "accent": {"kind", "key", "after", "set"},
    "whwords": {"kind", "key", "after", "where", "words"},
    "says": {"kind", "key", "after", "from", "to"},
    "sound": {"kind", "key", "after", "id", "keys", "note"},
    "map": {"kind", "key", "after", "name", "to", "note"},
}


class PackError(Exception):
    pass


def packs_dir():
    return os.path.join(os.path.dirname(os.path.dirname(HERE)), "packs")


def extra_dirs():
    """EVV_PACKS_EXTRA: folders (separated by os.pathsep) searched after packs/ for a tag packs/ lacks.
    For worked examples and test packs (docs/tts-extension/examples/packs/): they may extend a pack of
    packs/, never replace one, and `list_tags` (so `build_packs.py check`) never sees them."""
    return [d for d in os.environ.get("EVV_PACKS_EXTRA", "").split(os.pathsep) if d]


def pack_path(tag, root=None):
    if root:
        return os.path.join(root, tag, "pack.toml")
    path = os.path.join(packs_dir(), tag, "pack.toml")
    if not os.path.isfile(path):
        for d in extra_dirs():
            if os.path.isfile(os.path.join(d, tag, "pack.toml")):
                return os.path.join(d, tag, "pack.toml")
    return path


def list_tags(root=None):
    root = root or packs_dir()
    return sorted(t for t in os.listdir(root) if os.path.isfile(os.path.join(root, t, "pack.toml")))


# ---------------------------------------------------------------- reading and checking one file

def _strs(d):
    """Every scalar of a sound's or an accent's keys is a string in memory: '90', 'own'."""
    return {k: (str(v) if not isinstance(v, str) else v) for k, v in d.items()}


def _entry(e, where):
    if not isinstance(e, dict) or e.get("kind") not in KIND_FIELDS:
        raise PackError("%s: a line has no known kind: %r" % (where, e))
    extra = set(e) - KIND_FIELDS[e["kind"]]
    if extra:
        raise PackError("%s: a %s line has unknown fields %s" % (where, e["kind"], sorted(extra)))
    e = dict(e)
    for f in ("keys", "set"):
        if f in e:
            e[f] = _strs(e[f])
    try:
        F.line_key(e)
    except (KeyError, ValueError) as x:
        raise PackError("%s: %s" % (where, x))
    return e


def read_pack(tag, root=None):
    """The raw pack file, checked for shape (unknown keys stop the build)."""
    path = pack_path(tag, root)
    if not os.path.isfile(path):
        raise PackError("pack %r: no file %s" % (tag, path))
    d = tomlio.load(path)
    where = "pack %r" % tag
    extra = set(d) - TOP
    if extra:
        raise PackError("%s: unknown sections %s" % (where, sorted(extra)))
    p = d.get("pack", {})
    if set(p) - PACK_KEYS:
        raise PackError("%s: unknown [pack] keys %s" % (where, sorted(set(p) - PACK_KEYS)))
    if p.get("tag") != tag:
        raise PackError("%s: [pack] tag is %r, the folder says %r" % (where, p.get("tag"), tag))
    if p.get("format") != FORMAT:
        raise PackError("%s: format %r is not %d" % (where, p.get("format"), FORMAT))
    if p.get("kind") not in KINDS:
        raise PackError("%s: kind %r is not one of %s" % (where, p.get("kind"), KINDS))
    if set(d.get("meta", {})) - META_KEYS:
        raise PackError("%s: unknown [meta] keys %s" % (where, sorted(set(d["meta"]) - META_KEYS)))
    e = d.get("engine", {})
    if set(e) - ENGINE_KEYS:
        raise PackError("%s: unknown [engine] keys %s" % (where, sorted(set(e) - ENGINE_KEYS)))
    if e.get("realization") not in (None,) + REALIZATIONS:
        raise PackError("%s: realization %r is not one of %s" % (where, e.get("realization"), REALIZATIONS))
    if set(d.get("files", {})) - {"eol"} or d.get("files", {}).get("eol", "lf") not in ("crlf", "lf"):
        raise PackError("%s: [files] holds only eol = crlf | lf" % where)
    for sec in ("sounds", "phonemes"):
        t = d.get(sec)
        if t is None:
            continue
        if set(t) - LINE_TABLE_KEYS:
            raise PackError("%s: unknown [%s] keys %s" % (where, sec, sorted(set(t) - LINE_TABLE_KEYS)))
        t["line"] = [_entry(x, "%s [%s]" % (where, sec)) for x in t.get("line", [])]
        keys = [F.line_key(x) for x in t["line"]]
        dup = sorted(k for k in set(keys) if keys.count(k) > 1)
        if dup:
            raise PackError("%s [%s]: two lines with the key %s" % (where, sec, dup[:3]))
    ovs = d.get("override", [])
    if not isinstance(ovs, list):
        raise PackError("%s: override is a list ([[override]])" % where)
    try:
        for o in ovs:
            O.check_override(o, where)
    except O.OverrideError as x:
        raise PackError(str(x))
    sounds = [o["sound"] for o in ovs]
    if len(set(sounds)) != len(sounds):
        raise PackError("%s: two overrides of one sound" % where)
    if set(d.get("sample", {})) - {"text"}:
        raise PackError("%s: [sample] holds only text" % where)
    for sec, t in d.get("ini", {}).items():
        for k, v in t.items():
            if not isinstance(v, str):
                raise PackError("%s: [ini.%s] %s must be a string" % (where, sec, k))
    return d


# ---------------------------------------------------------------- resolving a chain

def chain_of(tag, root=None):
    """[root, ..., tag]; a cycle or a missing parent is an error."""
    seen, order, t = [], [], tag
    while t:
        if t in seen:
            raise PackError("pack %r: extends is a cycle: %s" % (tag, " -> ".join(seen + [t])))
        seen.append(t)
        d = read_pack(t, root)
        order.append(d)
        t = d["pack"].get("extends", "")
        if t and not os.path.isfile(pack_path(t, root)):
            raise PackError("pack %r extends %r, which has no pack.toml" % (seen[-1], t))
    return list(reversed(order))


def _merge_lines(base, child, where, origin, tag, sec):
    lines = [] if child.get("reset") else list(base)
    for k in child.get("remove", []):
        i = [j for j, x in enumerate(lines) if F.line_key(x) == k]
        if not i:
            raise PackError("%s: remove %r, but there is no such line to remove" % (where, k))
        del lines[i[0]]
        origin.pop("%s.%s" % (sec, k), None)
    for e in child.get("line", []):
        e = dict(e)
        after = e.pop("after", None)
        k = F.line_key(e)
        have = [j for j, x in enumerate(lines) if F.line_key(x) == k]
        if have and after is None:
            lines[have[0]] = e
        else:
            if have:
                del lines[have[0]]
            if after is None:
                lines.append(e)
            elif after == "^":
                lines.insert(0, e)
            else:
                at = [j for j, x in enumerate(lines) if F.line_key(x) == after]
                if not at:
                    raise PackError("%s: %r is to go after %r, which is not there" % (where, k, after))
                lines.insert(at[0] + 1, e)
        origin["%s.%s" % (sec, k)] = tag
    return lines


def _leaves(v, path, origin, tag):
    if isinstance(v, dict):
        for k, x in v.items():
            _leaves(x, path + [k], origin, tag)
    else:
        origin[".".join(path)] = tag


def _merge_table(base, child, path, origin, tag):
    for k, v in child.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge_table(base[k], v, path + [k], origin, tag)
        else:
            base[k] = copy.deepcopy(v)
            _leaves(v, path + [k], origin, tag)
    return base


def _remove_dotted(flat, dotted, where, origin):
    parts = dotted.split(".")
    t = flat
    for p in parts[:-1]:
        if not isinstance(t, dict) or p not in t:
            raise PackError("%s: remove %r, but there is no such key" % (where, dotted))
        t = t[p]
    if not isinstance(t, dict) or parts[-1] not in t:
        raise PackError("%s: remove %r, but there is no such key" % (where, dotted))
    del t[parts[-1]]
    origin.pop(dotted, None)


def resolve(tag, root=None):
    """-> (flat pack dict, origin {dotted key: the pack of the chain that gave it})."""
    flat, origin = {}, {}
    for d in chain_of(tag, root):
        t = d["pack"]["tag"]
        where = "pack %r" % t
        for sec in ("pack", "meta", "engine", "files", "ini", "sample"):
            if sec in d:
                _merge_table(flat.setdefault(sec, {}), d[sec], [sec], origin, t)
        for sec in ("sounds", "phonemes"):
            if sec in d:
                cur = flat.setdefault(sec, {"line": []})
                cur["line"] = _merge_lines(cur["line"], d[sec], where, origin, t, sec)
        if "override" in d or "remove_overrides" in d:
            try:
                flat["override"] = O.merge(flat.get("override", {}), d.get("override", []),
                                           d.get("remove_overrides", []), where)
            except O.OverrideError as x:
                raise PackError(str(x))
            for s in d.get("remove_overrides", []):
                origin.pop("override.%s" % s, None)
            for o in d.get("override", []):
                origin["override.%s" % o["sound"]] = t
                # each value too: a child that changes one formant leaves the others (and their
                # evidence files) its parent's
                for k in o.get("formants", {}):
                    origin["override.%s.formants.%s" % (o["sound"], k)] = t
                if "duration" in o:
                    origin["override.%s.duration" % o["sound"]] = t
        for dotted in d.get("remove", []):
            _remove_dotted(flat, dotted, where, origin)
    flat["pack"]["tag"] = tag
    return flat, origin


# ---------------------------------------------------------------- compiling

def check_flat(flat):
    tag = flat["pack"]["tag"]
    ini = flat.get("ini")
    if not ini:
        raise PackError("pack %r: no [ini] (every pack writes a language.ini)" % tag)
    lang = ini.get("Language", {})
    if lang.get("Tag") != tag:
        raise PackError("pack %r: [ini.Language] Tag is %r" % (tag, lang.get("Tag")))
    eng = flat.get("engine", {})
    if eng.get("template") not in (None, lang.get("Template")):
        raise PackError("pack %r: [engine] template %r is not [ini.Language] Template %r" % (
            tag, eng.get("template"), lang.get("Template")))
    voice = ini.get("Frontend", {}).get("Voice")
    if eng.get("reader", "").startswith("espeak:") and eng["reader"] != "espeak:" + (voice or ""):
        raise PackError("pack %r: [engine] reader %r is not the Voice= of [ini.Frontend] (%r)" % (
            tag, eng["reader"], voice))
    sm = [x for x in flat.get("sounds", {}).get("line", []) if x["kind"] == "directive" and x["name"] == "template"]
    if sm and sm[0]["value"] != lang.get("Template"):
        raise PackError("pack %r: sounds.map says template %r, language.ini %r" % (tag, sm[0]["value"], lang.get("Template")))
    for name, key in (("Map", "phonemes"), ("Sounds", "sounds")):
        if ini.get("Frontend", {}).get(name) and key not in flat:
            raise PackError("pack %r: language.ini names %s but the pack has no [%s]" % (tag, name, key))


def compile_pack(flat, include_proposed=False):
    """-> {file name: bytes}. Overrides with state "applied" are realised into sounds.map; with
    include_proposed, the "proposed" ones too (a scratch build to measure them, never languages/)."""
    check_flat(flat)
    if flat.get("override"):
        flat = copy.deepcopy(flat)
        try:
            O.realize(flat, include_proposed)
        except O.OverrideError as x:
            raise PackError(str(x))
    eol = "\r\n" if flat.get("files", {}).get("eol", "crlf") == "crlf" else "\n"
    out = {"language.ini": F.render_ini(flat["ini"], eol)}
    if "sounds" in flat:
        out["sounds.map"] = F.render_map(flat["sounds"]["line"], eol, "sounds")
    if "phonemes" in flat:
        out["phonemes.map"] = F.render_map(flat["phonemes"]["line"], eol, "phonemes")
    if "sample" in flat:
        out["sample.txt"] = flat["sample"]["text"] + eol
    return {k: v.encode("utf-8") for k, v in out.items()}


def build(tag, out_root, root=None, include_proposed=False):
    flat, origin = resolve(tag, root)
    files = compile_pack(flat, include_proposed)
    dst = os.path.join(out_root, tag)
    os.makedirs(dst, exist_ok=True)
    for name, data in files.items():
        with open(os.path.join(dst, name), "wb") as f:
            f.write(data)
    return files


def explain(tag, dotted, root=None):
    """Which pack of the chain a value of the finished pack came from."""
    flat, origin = resolve(tag, root)
    return origin.get(dotted)
