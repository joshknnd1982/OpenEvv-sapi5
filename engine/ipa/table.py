"""The master table of sounds (DESIGN.md 3), read, and checked. MIT licence.

    python engine/ipa/table.py             validate ipa/: exit 1 on any refusal
    python engine/ipa/table.py --selftest  plant each kind of fault in a copy; each must be refused

The validator refuses (DESIGN.md 3.2): an unknown field; a number without a provenance tag; a
`literature` value without a source in ipa/sources.toml that was opened; a `measured` value without
its proof, a `derived` one without its rule, an `approximate` one (or entry) without a sentence
saying what deviates; two letters with one feature bundle (unless the chart prints them as one,
`equivalent_to`); a feature or value ipa/features.toml does not define; a modifier with no class
of base; an entry without tests; an entry whose state is not MISSING without a proof that exists;
an id that is not its code points, or code points that are not its IPA; a Tier B composite
(D68) whose parts are not Tier A entries, Tier B letters or Tier B marks (D69) spelling it. It lists every `estimated` value: they are
the queue for verification.
"""

import copy
import json
import os
import re
import sys

import tomli

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IPA = os.path.join(ROOT, 'ipa')

KINDS = {'base', 'modifier', 'syllable-mark', 'tone', 'boundary', 'tie', 'composite'}
STATES = {'MISSING', 'mapped', 'composed', 'created', 'BLOCKED'}
TAGS = {'measured', 'literature', 'derived', 'estimated', 'created', 'approximate'}
FIELDS = {'ipa', 'codepoints', 'name', 'section', 'tier', 'kind', 'features', 'edit', 'levels', 'register',
          'slope', 'stress', 'boundary', 'placement', 'equivalent_to', 'state', 'level', 'approximate',
          'deviation', 'plan', 'spec', 'transform', 'realization', 'tests', 'history', 'registry',
          'chart', 'parts', 'said_as'}
VALUE_FIELDS = {'v', 'tag', 'ref', 'note', 'proof', 'rule', 'deviation', 'key', 'part'}
# a modifier's transform of a value (DESIGN.md 2.2): scale it, or add to it
TRANSFORM_OPS = {'scale', 'add', 'set', 'toward'}
PLACEMENTS = {'before', 'after', 'over', 'between'}


def file_id(sid):
    """An id as a file name: a Tier B id's `:' and `/' cannot be in one on Windows (D68)."""
    return re.sub(r'[:/]', '_', sid)


class Table(object):
    def __init__(self, features, sounds, sources, where):
        self.features = features   # ipa/features.toml
        self.sounds = sounds       # id -> entry
        self.sources = sources     # id -> source
        self.where = where         # id -> file it came from

    def letters(self):
        return {i: e for i, e in self.sounds.items() if e.get('kind') == 'base'}

    def by_ipa(self):
        return {e['ipa']: i for i, e in self.sounds.items()}


def load(folder=IPA):
    with open(os.path.join(folder, 'features.toml'), 'rb') as f:
        features = tomli.load(f)
    sources = {}
    path = os.path.join(folder, 'sources.toml')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            sources = tomli.load(f).get('source', {})
    sounds, where = {}, {}
    tdir = os.path.join(folder, 'table')
    for name in sorted(os.listdir(tdir)):
        if not name.endswith('.toml'):
            continue
        with open(os.path.join(tdir, name), 'rb') as f:
            data = tomli.load(f)
        for sid, e in data.get('sound', {}).items():
            if sid in sounds:
                raise ValueError('%s: %s is also in %s' % (name, sid, where[sid]))
            sounds[sid] = e
            where[sid] = name
    return Table(features, sounds, sources, where)


def _vocab(features, cls):
    """{feature: allowed values} for a class, `both` included."""
    out = {}
    for group in (cls, 'both'):
        for k, spec in features.get(group, {}).items():
            vals = list(spec.get('scale', [])) + list(spec.get('set', [])) + list(spec.get('extra', []))
            out[k] = ('list', spec['list']) if 'list' in spec else ('one', vals)
    return out


def _check_value(sid, path, val, t, problems, estimated):
    """A number of the specification: { v, tag, ref?, note?, proof?, rule?, deviation? }."""
    if isinstance(val, dict) and 'tag' not in val and not (set(val) & ({'v'} | TRANSFORM_OPS)):
        for k, x in val.items():
            _check_value(sid, path + '.' + k, x, t, problems, estimated)
        return
    if isinstance(val, list):
        for i, x in enumerate(val):
            _check_value(sid, '%s[%d]' % (path, i), x, t, problems, estimated)
        return
    if not isinstance(val, dict):
        problems.append('%s %s: a value without a provenance tag' % (sid, path))
        return
    ops = set(val) & TRANSFORM_OPS
    if path.startswith('transform') and len(ops) != 1:
        problems.append('%s %s: a transform needs one of scale, add, set or toward' % (sid, path))
    for k in val:
        if k not in VALUE_FIELDS and k not in TRANSFORM_OPS:
            problems.append('%s %s: unknown field %s' % (sid, path, k))
    tag = val.get('tag')
    if tag not in TAGS:
        problems.append('%s %s: tag %r is not one of %s' % (sid, path, tag, sorted(TAGS)))
    elif tag == 'literature':
        src = t.sources.get(val.get('ref', ''))
        if src is None:
            problems.append('%s %s: literature with no source %r in ipa/sources.toml' % (sid, path, val.get('ref')))
        elif not src.get('opened'):
            problems.append('%s %s: literature from %s, which was not opened' % (sid, path, val.get('ref')))
    elif tag == 'measured' and not val.get('proof'):
        problems.append('%s %s: measured with no proof' % (sid, path))
    elif tag == 'derived' and not val.get('rule'):
        problems.append('%s %s: derived with no rule' % (sid, path))
    elif tag == 'approximate' and not val.get('deviation'):
        problems.append('%s %s: approximate with no deviation stated' % (sid, path))
    elif tag == 'estimated':
        estimated.append('%s %s' % (sid, path))


def validate(t):
    """(problems, the verification queue of `estimated` values)."""
    problems, estimated = [], []
    bundles = {}
    for sid, e in sorted(t.sounds.items()):
        for k in e:
            if k not in FIELDS:
                problems.append('%s: unknown field %s' % (sid, k))
        cps = e.get('codepoints') or []
        # a Tier B id is `B:' and its code points (inventory/tierb, D68)
        # (a Tier B id may carry the inventory's `#pre', `#post', `#voqs' after its points)
        if (sid.split('#')[0] if e.get('tier') == 'B' else sid) != ('B:' if e.get('tier') == 'B' else '') + '+'.join(cps):
            problems.append('%s: the id is not its code points %s' % (sid, '+'.join(cps)))
        if ''.join(chr(int(c[2:], 16)) for c in cps) != e.get('ipa'):
            problems.append('%s: the code points are not its ipa %r' % (sid, e.get('ipa')))
        kind = e.get('kind')
        if kind not in KINDS:
            problems.append('%s: kind %r' % (sid, kind))
        if e.get('state') not in STATES:
            problems.append('%s: state %r' % (sid, e.get('state')))
        if e.get('approximate') and not e.get('deviation'):
            problems.append('%s: approximate with no deviation stated' % sid)
        if e.get('equivalent_to') and e['equivalent_to'] not in t.sounds:
            problems.append('%s: equivalent to %s, which the table lacks' % (sid, e['equivalent_to']))
        if kind not in ('base', 'composite') and e.get('placement') not in PLACEMENTS:
            problems.append('%s: placement %r' % (sid, e.get('placement')))
        if kind == 'base':
            f = dict(e.get('features') or {})
            cls = f.pop('class', None)
            if cls not in ('consonant', 'vowel'):
                problems.append('%s: class %r' % (sid, cls))
            else:
                vocab = _vocab(t.features, cls)
                for k, v in f.items():
                    if k not in vocab:
                        problems.append('%s: feature %s is not a %s feature' % (sid, k, cls))
                    elif vocab[k][0] == 'one' and v not in vocab[k][1]:
                        problems.append('%s: %s = %r is not in the scale' % (sid, k, v))
                key = json.dumps(full_bundle(t, e['features']), sort_keys=True)
                other = bundles.get(key)
                if other and t.sounds[other].get('equivalent_to') != sid and e.get('equivalent_to') != other:
                    problems.append('%s and %s have one feature bundle' % (other, sid))
                bundles.setdefault(key, sid)
        if kind == 'composite':
            # a Tier B spelling made of Tier A entries (D68): its parts must be Tier A entries, and
            # spell it, or spell the IPA it is said as (a new letter standing for a Tier A spelling)
            parts = e.get('parts') or []
            if e.get('tier') != 'B' or not parts:
                problems.append('%s: a composite is a Tier B entry with parts' % sid)
            for x in parts:
                px = t.sounds.get(x) or {}
                if px.get('tier') != 'A' and not (px.get('tier') == 'B' and px.get('kind') in ('base', 'modifier')):
                    problems.append('%s: part %s is not a Tier A entry or a Tier B letter or mark' % (sid, x))
            spelt = ''.join((t.sounds.get(x) or {}).get('ipa', '?') for x in parts)
            if spelt != (e.get('said_as') or e.get('ipa')):
                problems.append('%s: its parts spell %r, not %r' % (sid, spelt, e.get('said_as') or e.get('ipa')))
            tests = e.get('tests') or {}
            if not tests.get('bases') or tests['bases'][0] != (parts or [None])[0]:
                problems.append('%s: a composite is judged against its first part, its base' % sid)
            # judged by one of its own marks, with that mark's own test (a subset of its shifts)
            mark = t.sounds.get(tests.get('judged_by')) or {}
            if tests.get('judged_by') not in parts[1:] or any(
                    s not in (mark.get('tests') or {}).get('shift', []) for s in tests.get('shift') or [None]):
                problems.append('%s: not judged by one of its marks with that mark\'s own test' % sid)
            for k in ('spec', 'features', 'transform', 'realization', 'edit'):
                if e.get(k):
                    problems.append('%s: a composite has no %s of its own (its parts\' are its values)' % (sid, k))
        if kind == 'modifier':
            edit = e.get('edit') or {}
            if not edit:
                problems.append('%s: a modifier with no class of base' % sid)
            for cls, ed in edit.items():
                if cls not in ('consonant', 'vowel'):
                    problems.append('%s: edit for class %r' % (sid, cls))
                    continue
                vocab = _vocab(t.features, cls)
                for k, v in ed.items():
                    if k not in vocab:
                        problems.append('%s: edits %s, not a %s feature' % (sid, k, cls))
                    elif vocab[k][0] == 'list':
                        if not (isinstance(v, str) and v[:1] in '+-' and v[1:] in vocab[k][1]):
                            problems.append('%s: %s edit %r is not +value or -value' % (sid, k, v))
                    elif v not in vocab[k][1]:
                        problems.append('%s: %s = %r is not in the scale' % (sid, k, v))
        if kind == 'tone':
            lv = e.get('levels')
            if lv is not None and not (isinstance(lv, list) and lv and all(isinstance(x, int) and 1 <= x <= 5
                                                                            for x in lv)):
                problems.append('%s: levels %r are not Chao levels 1 to 5' % (sid, lv))
            if lv is None and not (e.get('register') or e.get('slope')):
                problems.append('%s: a tone with no levels, register or slope' % sid)
        tests = e.get('tests') or {}
        if not tests.get('checks'):
            problems.append('%s: no tests' % sid)
        if e.get('state') not in ('MISSING', None):
            proof = tests.get('proof')
            if not proof or not os.path.exists(os.path.join(ROOT, proof)):
                problems.append('%s: state %s with no proof file' % (sid, e.get('state')))
        for k, v in (e.get('spec') or {}).items():
            _check_value(sid, 'spec.' + k, v, t, problems, estimated)
        for cls, tr in (e.get('transform') or {}).items():
            if kind != 'modifier' or cls not in (e.get('edit') or {}):
                problems.append('%s: a transform for %s, which is not a class this modifier edits' % (sid, cls))
            for k, v in tr.items():
                _check_value(sid, 'transform.%s.%s' % (cls, k), v, t, problems, estimated)
        ov = (e.get('realization') or {}).get('openevv', {})
        for tmpl, trims in (ov.get('trim') or {}).items():
            _check_value(sid, 'trim.' + tmpl, trims, t, problems, estimated)
        # keys of this engine's own that no engine-neutral value stands for (a layer-made silence,
        # the implosive switch): each with its provenance like any value
        for k, v in (ov.get('keys') or {}).items():
            _check_value(sid, 'keys.' + k, v, t, problems, estimated)
        # a double articulation's keys added to each of its two stops (4g)
        for tmpl, pairs in (ov.get('double') or {}).items():
            for pair, how in pairs.items():
                if len(pair.split('͡')) != 2 or len(how.get('add') or []) != 2:
                    problems.append('%s double.%s.%s: two stops joined by ͡ and keys for each' % (sid, tmpl, pair))
                    continue
                bases = {x['ipa'] for x in t.sounds.values() if x.get('kind') == 'base'}
                for letter in pair.split('͡'):
                    if letter not in bases:
                        problems.append('%s double.%s.%s: %s is not a letter of the table' % (sid, tmpl, pair, letter))
                for n, add in enumerate(how['add']):
                    for k, v in (add or {}).items():
                        _check_value(sid, 'double.%s.%s.%d.%s' % (tmpl, pair, n + 1, k), v, t, problems, estimated)
    return problems, estimated


def full_bundle(t, features):
    """A letter's features with every default filled in, so equal sounds compare equal."""
    f = dict(features)
    cls = f.get('class')
    for group in (cls, 'both'):
        for k, spec in t.features.get(group, {}).items():
            if k not in f and 'default' in spec:
                f[k] = spec['default']
    return f


# ---- the validator's own proof -----------------------------------------------------------------

def _plants(t):
    """(what is planted, a function that plants it in a copy of the table)."""
    p, b, m = 'U+0070', 'U+0062', 'U+0303'

    def setv(sid, path, value):
        def go(c):
            node = c.sounds[sid]
            for k in path[:-1]:
                node = node.setdefault(k, {})
            node[path[-1]] = value
        return go

    return [
        ('an unknown field', setv(p, ['colour'], 'red')),
        ('a number without a tag', setv(p, ['spec', 'vot_ms'], 15)),
        ('a tag that is not a tag', setv(p, ['spec', 'vot_ms'], {'v': 15, 'tag': 'guessed'})),
        ('literature with no source', setv(p, ['spec', 'vot_ms'], {'v': 15, 'tag': 'literature', 'ref': 'nobody'})),
        ('literature not opened', lambda c: (c.sources.update({'unread': {'opened': False}}),
                                             setv(p, ['spec', 'vot_ms'],
                                                  {'v': 15, 'tag': 'literature', 'ref': 'unread'})(c))),
        ('measured with no proof', setv(p, ['spec', 'vot_ms'], {'v': 15, 'tag': 'measured'})),
        ('derived with no rule', setv(p, ['spec', 'vot_ms'], {'v': 15, 'tag': 'derived'})),
        ('approximate with no deviation', setv(p, ['approximate'], True)),
        ('two letters with one bundle', setv(b, ['features'], dict(t.sounds[p]['features']))),
        ('a feature value not in its scale', setv(p, ['features', 'place'], 'nose')),
        ('a feature not of its class', setv(p, ['features', 'height'], 'close')),
        ('a modifier with no class', setv(m, ['edit'], {})),
        ('an entry without tests', setv(p, ['tests'], {})),
        ('a state with no proof', setv(p, ['tests', 'proof'], 'ipa/proofs/none.json')),
        ('an id that is not its code points', setv(p, ['codepoints'], ['U+0071'])),
        ('a tone with bad levels', setv('U+02E5', ['levels'], [6])),
        ('a transform with no operation', setv('U+02B0', ['transform', 'consonant', 'vot_ms'], {'v': 60, 'tag': 'estimated'})),
        ('a transform for a class not edited', setv('U+02B0', ['transform', 'vowel'], {'vot_ms': {'add': 1, 'tag': 'estimated'}})),
        # parts that spell n̼̊ correctly, but one of them is a Tier B composite, not a letter
        ('a composite of a Tier B composite', lambda c: (
            setv('B:U+006E+U+033C+U+030A', ['parts'], ['B:U+006E+U+033C', 'U+030A'])(c),
            setv('B:U+006E+U+033C+U+030A', ['tests', 'bases'], ['B:U+006E+U+033C'])(c),
            setv('B:U+006E+U+033C+U+030A', ['tests', 'judged_by'], 'U+030A')(c),
            setv('B:U+006E+U+033C+U+030A', ['tests', 'shift'], [{'measure': 'voiced_frac', 'sign': -1}])(c))),
        ('a composite its parts do not spell', setv('B:U+0074+U+033C', ['parts'], ['U+0064', 'U+033C'])),
        ('a Tier B id that is not its points', setv('B:U+A78E', ['codepoints'], ['U+A78F'])),
        ('a composite judged by no mark of its', setv('B:U+0074+U+033C', ['tests', 'judged_by'], 'U+032A')),
        ('a composite with values of its own', setv('B:U+0074+U+033C', ['spec'], {'vot_ms': {'v': 9, 'tag': 'estimated'}})),
    ]


def selftest():
    t = load()
    base, _ = validate(t)
    failed = 0
    if base:
        print('FAIL  the table itself is refused: %s' % base[:3])
        failed += 1
    for what, plant in _plants(t):
        c = copy.deepcopy(t)
        plant(c)
        problems, _ = validate(c)
        ok = bool(problems)
        failed += not ok
        print('%-4s  %-34s %s' % ('ok' if ok else 'FAIL', what, problems[0] if problems else 'NOT refused'))
    print('validator: the table %s; %d planted faults, %d refused' % (
        'refused' if base else 'accepted', len(_plants(t)), len(_plants(t)) - (failed - (1 if base else 0))))
    return 1 if failed else 0


def main():
    if '--selftest' in sys.argv:
        return selftest()
    t = load()
    problems, estimated = validate(t)
    states = {}
    for e in t.sounds.values():
        states[e.get('state')] = states.get(e.get('state'), 0) + 1
    print('table: %d entries (%s); %d problems; %d estimated values queued for verification' % (
        len(t.sounds), ', '.join('%s %d' % kv for kv in sorted(states.items())), len(problems), len(estimated)))
    for p in problems:
        print('  ' + p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
