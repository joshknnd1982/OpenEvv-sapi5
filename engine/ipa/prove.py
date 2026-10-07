"""Realise, render, measure (DESIGN.md 3.3 and the USP, capability C3). MIT licence.

    python engine/ipa/prove.py <id> [--template dedx] [--pack hi]

An entry is realised for the template (adapter.py), said by the real engine in its contexts (a
vowel alone and between b and d; a consonant between a, i and u), measured with the harness, and
compared with its specification. If a measure is off, a correction (`trim`) is worked out from
what was measured and the entry is said again: at most five rounds (playbook 1.6). What happened
in each round is written to ipa/proofs/<id>.json, with the modules that spoke (EVV_STAGE).

This is the loop the design asks C3 to show working for one vowel, one stop and one fricative.
It does not change an entry's state: an entry becomes `mapped`, `composed` or `created` in
Phase 4, when every test its plan names has passed.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
import adapter as AD  # noqa: E402
import table as T  # noqa: E402
import engine as E  # noqa: E402
import golden as G  # noqa: E402

PROOFS = os.path.join(ROOT, 'ipa', 'proofs', 'loop')
ROUNDS = 5
# how close a measure must come to its target (a formant: the harness's A2 tolerance)
FORMANT_TOL = 0.08
VOT_TOL_MS, VOT_TOL = 5.0, 0.25
PEAK_TOL = 0.10


def contexts(cls, phone):
    q = ("'%s'" % phone) if len(phone) > 1 else phone
    if cls == 'vowel':
        return [('alone', '{W .1 %s=m1^-}`[.1%s]' % (phone, q)),
                ('b_d', '{W .1 b %s=m1^- d}`[.1b%sd]' % (phone, q))]
    return [('%s_%s' % (v, v), '{W .1 %s^- .0 %s=m1 %s^-}`[.1%s.0%s%s]' % (v, phone, v, v, q, v))
            for v in ('a', 'i', 'u')]


def say(pack, line, cases, work, phone):
    head = '{A v=1}' + ('{D %s}' % line[len('sound '):] if line else '')
    res = E.render(pack, [(cid, 'annotated', head + text) for cid, text in cases], work=work)
    p = E.pack(pack)
    out = []
    for r in res:
        m = G.measure_case(r, p.phone_module)
        # the phone the case is about: the one carrying the definition, or (said plain) the carrier
        target = [ph for ph in m['phones'] if ph.get('sound') == 'm1'] or \
                 [ph for ph in m['phones'] if ph['name'] == phone and ph['cls'] != 'silence']
        out.append(dict(id=r['id'], phone=target[0] if target else None, diag=r.get('diag', [])))
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def measures(said, spec):
    """What was measured, over the contexts, for each target the spec names."""
    got = {}
    for k in ('F1', 'F2', 'F3'):
        if k in (spec.get('formants') or {}):
            got[k] = mean([s['phone']['meas'].get('%s_50_hz' % k) for s in said if s['phone']])
    if 'vot_ms' in spec:
        got['vot_ms'] = mean([s['phone']['meas'].get('vot_ms') for s in said if s['phone']])
    if 'peak_hz' in (spec.get('noise') or {}):
        got['peak_hz'] = mean([s['phone']['meas'].get('peak_hz') for s in said if s['phone']])
    return got


def targets(spec):
    v = lambda x: x['v'] if isinstance(x, dict) else x  # noqa: E731
    out = {k: v(x) for k, x in (spec.get('formants') or {}).items()}
    if 'vot_ms' in spec:
        out['vot_ms'] = v(spec['vot_ms'])
    if 'peak_hz' in (spec.get('noise') or {}):
        out['peak_hz'] = v(spec['noise']['peak_hz'])
    return out


def within(k, got, want):
    if got is None:
        return False
    if k.startswith('F'):
        return abs(got - want) <= FORMANT_TOL * want
    if k == 'vot_ms':
        return abs(got - want) <= max(VOT_TOL_MS, VOT_TOL * want)
    return abs(got - want) <= PEAK_TOL * want


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('id')
    ap.add_argument('--template', default='dedx')
    ap.add_argument('--pack', default='hi', help='a pack whose template is --template (its module speaks)')
    a = ap.parse_args()
    t = T.load()
    e = t.sounds[a.id]
    if E.pack(a.pack).template != a.template:
        raise SystemExit('%s is not on %s' % (a.pack, a.template))
    spec = e.get('spec') or {}
    want = targets(spec)
    cls = e['features']['class']
    work = os.path.join(E.WORK, 'prove', a.id.replace('+', '_'))
    car = AD.carrier(t, e, a.template)[0]
    # the carrier as the module says it: what the entry is realised from
    plain = say(a.pack, '', [(cid, text.replace('=m1', '')) for cid, text in contexts(cls, car)], work, car)
    for s in plain:
        if s['phone'] is None:
            raise SystemExit('the carrier %s was not found in %s' % (car, s['id']))
    carrier_meas = {k: mean([s['phone']['meas'].get(k) for s in plain]) for k in ('peak_hz', 'vot_ms')}
    trims, rounds, passed = {}, [], False
    for n in range(1, ROUNDS + 1):
        r = AD.realize(t, a.id, a.template, carrier_meas)
        keys = dict(r['keys'])
        for k, v in trims.items():
            keys[k] = int(round(v(keys.get(k))))
        line = AD.sound_line('m1', keys)
        said = say(a.pack, line, contexts(cls, r['carrier']), work, r['carrier'])
        got = measures(said, spec)
        ok = {k: within(k, got.get(k), w) for k, w in want.items()}
        rounds.append(dict(round=n, line=line, carrier=r['carrier'], measured=got, within=ok,
                           unrealised=r['unrealised'], diag=[d for s in said for d in s['diag']]))
        print('round %d: %s  measured %s  %s' % (n, line, {k: round(v, 1) if v else v for k, v in got.items()},
                                                   'pass' if all(ok.values()) else 'off'))
        if all(ok.values()):
            passed = True
            break
        # corrections from what was measured, for the next round
        for k, w in want.items():
            g = got.get(k)
            if g is None or ok[k]:
                continue
            if k.startswith('F'):
                key = 'f' + k[1]
                f = w / g
                prev = trims.get(key)
                trims[key] = (lambda f, prev: lambda x: (prev(x) if prev else x) * f)(f, prev)
            elif k == 'vot_ms':
                d = w - g
                prev = trims.get('vot')
                trims['vot'] = (lambda d, prev: lambda x: (prev(x) if prev else x) + d)(d, prev)
            elif k == 'peak_hz':
                f = w / g
                for key in ('f2', 'f3', 'f4'):
                    prev = trims.get(key)
                    trims[key] = (lambda f, prev: lambda x: (prev(x) if prev else x) * f)(f, prev)
    os.makedirs(PROOFS, exist_ok=True)
    proof = dict(id=a.id, ipa=e['ipa'], template=a.template, pack=a.pack, staged=E.STAGE or None,
                 frontend=E.FRONTEND, targets=want, carrier=car, carrier_measured=carrier_meas,
                 contexts=[c for c, _ in contexts(cls, car)], rounds=rounds, passed=passed,
                 tolerances=dict(formant=FORMANT_TOL, vot_ms=VOT_TOL_MS, vot=VOT_TOL, peak=PEAK_TOL))
    path = os.path.join(PROOFS, T.file_id(a.id) + '.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(proof, f, ensure_ascii=False, indent=1)
    print('%s %s: %s after %d round(s); %s' % (a.id, e['ipa'], 'PASS' if passed else 'not within tolerance',
                                              len(rounds), os.path.relpath(path, ROOT)))
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
