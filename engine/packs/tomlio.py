"""Read TOML (tomllib, or tomli on Python 3.10) and write the small part of it a pack uses.

The writer writes what packlib builds: nested tables of strings, integers, booleans and lists, and
`line` arrays, one inline table to a line, so a diff of two packs is a diff of lines.
"""
import json
import re

try:
    import tomllib as _toml
except ImportError:  # Python 3.10
    import tomli as _toml

_BARE = re.compile(r"[A-Za-z0-9_-]+")


def loads(text):
    return _toml.loads(text)


def load(path):
    with open(path, "rb") as f:
        return _toml.load(f)


def _str(s):
    out = json.dumps(s, ensure_ascii=False)
    # JSON leaves DEL and the C1 controls as they are; TOML does not allow them bare
    return re.sub(r"[\x7f-\x9f]", lambda m: "\\u%04x" % ord(m.group(0)), out)


def _key(k):
    return k if _BARE.fullmatch(k) else _str(k)


def _val(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return _str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_val(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join("%s = %s" % (_key(k), _val(x)) for k, x in v.items()) + " }" if v else "{}"
    raise TypeError("cannot write %r" % (v,))


def _is_lines(v):
    return isinstance(v, list) and v and all(isinstance(x, dict) for x in v)


def _table(out, path, d):
    scalars = [(k, v) for k, v in d.items() if not isinstance(v, dict) and not _is_lines(v)]
    arrays = [(k, v) for k, v in d.items() if _is_lines(v)]
    tables = [(k, v) for k, v in d.items() if isinstance(v, dict)]
    if path and (scalars or arrays or not tables):
        out.append("")
        out.append("[%s]" % ".".join(_key(p) for p in path))
    for k, v in scalars:
        out.append("%s = %s" % (_key(k), _val(v)))
    for k, v in arrays:
        out.append("%s = [" % _key(k))
        for x in v:
            out.append("  %s," % _val(x))
        out.append("]")
    for k, v in tables:
        _table(out, path + [k], v)


def dumps(d, header=""):
    out = [header.rstrip("\n")] if header else []
    _table(out, [], d)
    return "\n".join(out).lstrip("\n") + "\n"
