"""The engine adapter (DESIGN.md 3.3, capability C3): an entry of the master table, realised for one
template module of this engine. MIT licence.

    python engine/ipa/adapter.py <id> [template]       the sound line, the carrier, what is not realised

For one entry and one template:
  1. the entry's feature bundle (a base letter's own; composed marks come with C4);
  2. the carrier: the entry's own choice (`realization.openevv.carrier`), or the module phone
     nearest by features (ipa/features.toml's weights; the module's phones read from their IPA in
     engine/espeak_phonemes.py with the IPA reader);
  3. targets in hertz become ratios of what the carrier measures in the module
     (engine/accent/chassis/<template>.json): F1 to F4 as f1..f4 per cent; a fricative's noise
     peak by moving the carrier's noise resonances (F2 to F4) by the ratio of the peaks;
  4. times: the inherent length as `dur` per cent of the carrier's; the voice onset time as `vot`
     in milliseconds;
  5. the entry's `trim` for this template (corrections found by measuring) is applied on top;
  6. the result is a `sound` line in the format the product reads (docs/SOUNDS.md).
What it cannot realise as specified (a formant above 5 kHz, a field it has no key for) is returned
in `unrealised`, never dropped: the entry then says `approximate` with that deviation.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import reader as R  # noqa: E402
import table as T  # noqa: E402

CHASSIS = os.path.join(ROOT, 'engine', 'accent', 'chassis')
BASE_OF = {'dedx': 'dede', 'esex': 'eses', 'itix': 'itit', 'engx': 'engb', 'esux': 'esus', 'frfx': 'frfr',
           'enux': 'enus'}
MAX_FORMANT_HZ = 5000      # F6 of DESIGN.md: the synthesiser places no formant above this


def chassis(template):
    with open(os.path.join(CHASSIS, template + '.json'), encoding='utf-8') as f:
        return json.load(f)['phones']


def module_phones(template):
    """{module phone: feature bundle}, for the phones whose IPA is one segment."""
    import espeak_phonemes as EP
    tm = EP.TEMPLATES[BASE_OF.get(template, template)]
    t = R.table()
    out = {}
    for name, ipa in list(tm.vowels.items()) + list(tm.consonants.items()):
        try:
            r = R.read(ipa, strict=False)
        except R.ReaderError:
            continue
        segs = [it for it in r['items'] if it['t'] == 'seg' and 'tied' not in it]
        if len(segs) == 1 and len(r['items']) == 1 and not r['warnings']:
            out[name] = segs[0]['features']
    return out


def distance(t, a, b):
    """The nearest-letter cost of ipa/features.toml between two bundles."""
    w = t.features['weights']
    if a.get('class') != b.get('class'):
        return w['class']
    if a['class'] == 'vowel':
        cv = w['vowel']
        scale = lambda k: t.features['vowel'][k]['scale']  # noqa: E731
        d = cv['height_step'] * abs(scale('height').index(a['height']) - scale('height').index(b['height']))
        d += cv['backness_step'] * abs(scale('backness').index(a['backness']) - scale('backness').index(b['backness']))
        d += cv['rounding'] * (a.get('rounding') != b.get('rounding'))
        return d
    cw = w['consonant']
    places = t.features['consonant']['place']['scale']
    d = cw['place_step'] * abs(places.index(a['place']) - places.index(b['place']))
    for k in ('stricture', 'airstream', 'nasal', 'lateral', 'sibilant', 'place2', 'voicing'):
        d += cw[k] * (a.get(k) != b.get(k))
    return d


def carrier(t, entry, template):
    own = ((entry.get('realization') or {}).get('openevv') or {}).get('carrier')
    if own:
        return own, 0
    f = T.full_bundle(t, entry['features'])
    best = min(((distance(t, f, T.full_bundle(t, g)), name) for name, g in module_phones(template).items()))
    return best[1], best[0]


def _v(x):
    return x['v'] if isinstance(x, dict) else x


def realize(t, sid, template, carrier_meas=None):
    """{'keys': {key: value}, 'carrier': phone, 'distance': cost, 'unrealised': [...], 'rules': [...]}.

    carrier_meas: what the carrier measured when rendered (the loop passes it), for targets the
    chassis does not hold (a fricative's noise peak)."""
    e = t.sounds[sid]
    spec = e.get('spec') or {}
    car, dist = carrier(t, e, template)
    ch = chassis(template).get(car)
    if ch is None:
        raise ValueError('%s has no chassis measurement in %s' % (car, template))
    keys, unrealised, rules = {}, [], []
    for i, k in enumerate(('F1', 'F2', 'F3', 'F4')):
        target = (spec.get('formants') or {}).get(k)
        if target is None:
            continue
        hz = _v(target)
        if hz > MAX_FORMANT_HZ:
            unrealised.append('%s %s Hz: above the %d Hz the synthesiser can place' % (k, hz, MAX_FORMANT_HZ))
            continue
        keys['f%d' % (i + 1)] = int(round(100.0 * hz / ch['f'][i]))
        rules.append('f%d = %s target / carrier %s %d Hz' % (i + 1, k, car, ch['f'][i]))
    peak = (spec.get('noise') or {}).get('peak_hz')
    if peak is not None:
        if not carrier_meas or not carrier_meas.get('peak_hz'):
            unrealised.append('noise peak: the carrier %s has no measured peak to move from' % car)
        else:
            ratio = _v(peak) / carrier_meas['peak_hz']
            for i in (1, 2, 3):
                keys['f%d' % (i + 1)] = int(round(100.0 * ratio))
            rules.append('f2..f4 = noise peak %s / carrier %s peak %.0f Hz' % (_v(peak), car, carrier_meas['peak_hz']))
    dur = (spec.get('duration') or {}).get('inherent_ms')
    if dur is not None:
        keys['dur'] = int(round(100.0 * _v(dur) / ch['ms']))
        rules.append('dur = %s ms / carrier %s %d ms' % (_v(dur), car, ch['ms']))
    vot = spec.get('vot_ms')
    if vot is not None:
        keys['vot'] = int(round(_v(vot)))
        rules.append('vot = %s ms' % _v(vot))
    known = {'formants', 'noise', 'duration', 'vot_ms'}
    for k in spec:
        if k not in known:
            unrealised.append('%s: the adapter has no key for it yet' % k)
    for tr in (((e.get('realization') or {}).get('openevv') or {}).get('trim') or {}).get(template, []):
        keys[tr['key']] = keys.get(tr['key'], 100 if tr['key'].startswith('f') or tr['key'] == 'dur' else 0)
        keys[tr['key']] = int(round(keys[tr['key']] * tr['v'] / 100.0)) if tr.get('scale') else int(tr['v'])
        rules.append('trim %s %s (%s)' % (tr['key'], tr['v'], tr.get('tag')))
    return dict(keys=keys, carrier=car, distance=dist, unrealised=unrealised, rules=rules)


def sound_line(name, keys):
    return 'sound %s %s' % (name, ' '.join('%s=%d' % kv for kv in sorted(keys.items())))


# ---- C4: composition when speaking (DESIGN.md 2.3) -----------------------------------------------
# A modifier's transform (ipa/table: `transform.<class>`) in the engine's own terms: a ratio key is
# multiplied, a time is added. The front-end merges these into a base letter's line; the adapter
# composes the same thing exactly; a test holds the two together (compose_test.py).
OPS = {('vot_ms', 'add'): ('vot', '+'), ('duration.inherent_ms', 'scale'): ('dur', '*')}
for _i in (1, 2, 3, 4):
    OPS[('formants.F%d' % _i, 'scale')] = ('f%d' % _i, '*')
RATIO_KEYS = {'f1', 'f2', 'f3', 'f4', 'dur'}      # absent means the carrier's own: 100


def _flat(tr, prefix=''):
    for k, v in tr.items():
        if isinstance(v, dict) and not ({'add', 'scale'} & set(v)):
            yield from _flat(v, prefix + k + '.')
        else:
            yield prefix + k, v


def mod_ops(t, mid, cls):
    """[(key, op, value)] for one modifier and class, or None if it has no transform for it;
    with what it could not express."""
    tr = ((t.sounds[mid].get('transform') or {}).get(cls))
    if tr is None:
        return None, []
    ops, lost = [], []
    for path, v in _flat(tr):
        op = 'add' if 'add' in v else 'scale'
        key = OPS.get((path, op))
        if key is None:
            lost.append('%s %s: no engine key' % (path, op))
            continue
        ops.append((key[0], key[1], v[op] * (100.0 if key[1] == '*' else 1.0)))
    return ops, lost


def merge(keys, ops, exact=False):
    """A base's keys with a modifier's ops. Ratios multiply (absent = 100), times add (absent: lost,
    since the module's own value is not known here). Returns (keys, lost)."""
    out, lost = dict(keys), []
    for key, op, val in ops:
        if op == '*':
            out[key] = out.get(key, 100) * val / 100.0
        elif key in out:
            out[key] = out[key] + val
        else:
            lost.append('%s+%s: the base has no %s to add to' % (key, val, key))
    return ({k: v if exact else int(round(v)) for k, v in out.items()}, lost)


def compose(t, base_sid, mod_sids, template, carrier_meas=None):
    """The adapter's own composition: the base realised unrounded, each modifier applied, rounded
    once at the end (the front-end rounds the base and each op first: they may differ by 1)."""
    r = realize(t, base_sid, template, carrier_meas)
    keys = dict(r['keys'])
    cls = t.sounds[base_sid]['features']['class']
    lost = []
    for m in mod_sids:
        ops, l1 = mod_ops(t, m, cls)
        lost += l1
        if ops is None:
            lost.append('%s has no transform for a %s' % (t.sounds[m]['ipa'], cls))
            continue
        keys, l2 = merge(keys, ops, exact=True)
        lost += l2
    return dict(keys={k: int(round(v + 1e-9)) for k, v in keys.items()}, carrier=r['carrier'], lost=lost)


def letter_line(t, sid):
    f = T.full_bundle(t, t.sounds[sid]['features'])
    if f['class'] == 'vowel':
        v = t.features['vowel']
        return 'letter %s v height=%d backness=%d rounding=%s' % (
            t.sounds[sid]['ipa'], v['height']['scale'].index(f['height']), v['backness']['scale'].index(f['backness']),
            f['rounding'])
    c = t.features['consonant']
    return 'letter %s c place=%d %s' % (t.sounds[sid]['ipa'], c['place']['scale'].index(f['place']), ' '.join(
        '%s=%s' % (k, str(f[k]).lower()) for k in ('stricture', 'airstream', 'nasal', 'lateral', 'sibilant', 'place2',
                                                    'voicing')))


def weights_line(t):
    w = t.features['weights']
    return 'weights %s class=%d' % (' '.join('%s=%d' % kv for kv in list(w['consonant'].items()) +
                                             list(w['vowel'].items())), w['class'])


def map_name(sid):
    """The name a realised entry has in a map: `u` and its code points, within the 11 bytes a
    sound id may have (EVV_ID_LEN)."""
    import hashlib
    name = 'u' + '_'.join(sid.replace('U+', '').lower().split('+'))
    return name if len(name) <= 11 else 'u' + hashlib.sha1(sid.encode('ascii')).hexdigest()[:10]


def write(t, template):
    """ipa/realized/<template>.map: every entry with a specification, as this template's lines. A
    noise target uses the carrier's peak as the entry's proof measured it."""
    lines = ['# The master table realised for %s (engine/ipa/adapter.py --write). Generated: do not edit.' % template,
             '# Each entry: its sound line, and its IPA said as the carrier with that sound.', '']
    n, unrealised = 0, 0
    for sid, e in sorted(t.sounds.items()):
        if not e.get('spec') or e.get('kind') != 'base':
            continue
        meas = None
        proof = os.path.join(ROOT, 'ipa', 'proofs', sid + '.json')
        if os.path.exists(proof):
            with open(proof, encoding='utf-8') as f:
                meas = json.load(f).get('carrier_measured')
        r = realize(t, sid, template, meas)
        name = map_name(sid)
        lines.append('%s    # %s %s' % (sound_line(name, r['keys']), sid, e['name']))
        for u in r['unrealised']:
            lines.append('#   not realised: %s' % u)
            unrealised += 1
        lines.append('%-12s %s=%s' % (e['ipa'], r['carrier'], name))
        n += 1
    # C4: what the front-end needs to compose when speaking, and to fall back with a warning
    lines += ['', '# composition when speaking (C4): read only by a map with `version 2`',
              'version 2', weights_line(t)]
    for sid, e in sorted(t.sounds.items()):
        if e.get('kind') == 'base':
            lines.append(letter_line(t, sid))
    for sid, e in sorted(t.sounds.items()):
        for cls in sorted((e.get('transform') or {})):
            ops, lost = mod_ops(t, sid, cls)
            for l in lost:
                lines.append('#   not realised: %s %s' % (e['ipa'], l))
                unrealised += 1
            if ops:
                lines.append('mod %s %s %s    # %s' % (e['ipa'], cls[0], ' '.join(
                    '%s%s%d' % (k, op, int(round(v))) for k, op, v in ops), sid))
    os.makedirs(os.path.join(ROOT, 'ipa', 'realized'), exist_ok=True)
    path = os.path.join(ROOT, 'ipa', 'realized', template + '.map')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('%s: %d entries realised, %d targets not realised' % (os.path.relpath(path, ROOT), n, unrealised))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    t = T.load()
    if sys.argv[1] == '--write':
        for template in sys.argv[2:] or ['dedx']:
            write(t, template)
        return 0
    r = realize(t, sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'dedx')
    print(json.dumps(dict(r, line=sound_line('m1', r['keys'])), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
