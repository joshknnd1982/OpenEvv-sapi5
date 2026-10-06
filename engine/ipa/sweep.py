"""The symbol-by-symbol sweep (playbook Phase 4i, R19f; DESIGN.md 3.4 and 10). MIT licence.

    python engine/ipa/sweep.py [ids or sections ...] [--template dedx] [--pack hi] [--apply]

Every entry asked for (all, a section such as `pulmonic`, or ids such as U+0288) is said by the
real engine, from IPA, through the staged front-end and the staged reference module (EVV_STAGE):
a letter alone and in three vowel contexts, a vowel alone and between three consonants, a mark on
the base sounds its entry names. Each case is measured with the harness and the entry is judged:

  A0  nothing lost on the way (no `loss` from the front-end or the accent layer), and the letter
      is not a module phone standing in for it unmoved (a carrier at a feature distance with no
      key of the entry's own: a silent substitution, R7)
  A1  the sound sounded: frames with voice or noise over it (a stop: a closure and a burst found)
  A2  the signal carries what the frames asked for (report.check_a over the cases)
  B3  every target of the entry's specification is met within its tolerance (prove.py's)
  B2  every contrast the entry's tests name holds, in the direction named, by at least the
      smallest difference this harness can tell from its own error

The proof is written to ipa/proofs/<id>.json: the inputs, what the front-end made of them, what
was reported, the measures of the sound and its neighbours, every check and its evidence. With
`--apply` an entry that passes all of them takes the state its plan names (mapped, composed or
created), level 2 (engine-verified on the reference template) and its proof path; one that fails
is left as it was. Nothing else in the table is touched.
"""

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
import adapter as AD  # noqa: E402
import compose_test as CT  # noqa: E402
import prove as PR  # noqa: E402
import table as T  # noqa: E402
import analysis as A  # noqa: E402
import engine as E  # noqa: E402
import golden as G  # noqa: E402
import report as RP  # noqa: E402

PROOFS = os.path.join(ROOT, 'ipa', 'proofs')
SWEEP_WORK = os.path.join(E.WORK, 'sweep')
VOWELS_AROUND = ('a', 'i', 'u')
CONSONANTS_AROUND = ('p', 't', 'k')
# the smallest difference a contrast must show to count: above what the harness tells apart from
# its own error on synthetic speech (D15: a low F1 near a harmonic; formants 2 to 4 per cent)
CONTRAST_MIN = {'hz_rel': 0.04, 'ms': 8.0, 'db': 2.0, 'count': 1}


def manner(e):
    """stop / nasal / trill / tap / fricative / approximant / vowel / click, from the features."""
    f = e['features']
    if f['class'] == 'vowel':
        return 'vowel'
    if f.get('airstream') == 'click':
        return 'click'
    s = f['stricture']
    if s == 'closure':
        return 'nasal' if f.get('nasal') else 'stop'
    return {'trill': 'trill', 'tap': 'tap', 'friction': 'fricative', 'approximation': 'approximant'}[s]


def contexts(t, sid):
    """[(case id, IPA, the index of the target segment among the said syllable nuclei...)]: the
    inputs of an entry. A letter alone and in three contexts; a mark on the bases its tests name."""
    e = t.sounds[sid]
    tests = e.get('tests') or {}
    if e['kind'] == 'base':
        x = e['ipa']
        if manner(e) == 'vowel':
            return [('alone', x)] + [('%s_%s' % (c, c), 'ˈ%s%s%s' % (c, x, c)) for c in CONSONANTS_AROUND]
        return [('alone', x)] + [('%s_%s' % (v, v), 'ˈ%s%s%s' % (v, x, v)) for v in VOWELS_AROUND]
    out = []
    for base in tests.get('bases', []):
        b = t.sounds[base]
        marked = b['ipa'] + e['ipa']
        if manner(b) == 'vowel':
            out += [('%s_%s' % (base, c), 'ˈ%s%s%s' % (c, marked, c)) for c in CONSONANTS_AROUND[:1]]
        else:
            out += [('%s_%s' % (base, v), 'ˈ%s%s%s' % (v, marked, v)) for v in VOWELS_AROUND]
    return out


def target_phones(phones, case_id, kind):
    """The phones a case is about: in a context, everything between the first and the last
    sounding phone (a vowel between consonants, a consonant between vowels, its pieces too);
    alone, every sounding phone but a schwa the front-end put in."""
    sounding = [i for i, ph in enumerate(phones) if ph['cls'] != 'silence']
    if not sounding:
        return [], None, None
    if case_id == 'alone':
        idx = [i for i in sounding if not (ph_is_schwa(phones[i]) and len(sounding) > 1)]
        return idx, None, None
    if len(sounding) < 3:
        return sounding, None, None
    return sounding[1:-1], sounding[0], sounding[-1]


def ph_is_schwa(ph):
    return ph['name'] == '@' and ph.get('sound') in (None, '-')


def measure(r, p, case_id):
    """The case measured: the harness's per-phone measures, the target and its neighbours, and the
    measures of DESIGN.md 10.2 that the class needs."""
    m = G.measure_case(r, p.phone_module)
    x, rate = E.read_wav(r['wav'])
    phones = m['phones']
    idx, before, after = target_phones(phones, case_id, None)
    tgt = [phones[i] for i in idx]
    out = dict(phones=[dict(name=ph['name'], sound=ph.get('sound'), cls=ph['cls'], start_ms=ph['start_ms'],
                            end_ms=ph['end_ms'], meas=ph.get('meas'), req={k: v for k, v in (ph.get('req') or {}).items()
                                                                           if not isinstance(v, list)})
                       for ph in phones],
               target=idx, before=before, after=after, gold=m)
    if tgt:
        a, b = tgt[0]['start_ms'], tgt[-1]['end_ms']
        ex = dict(span_ms=[a, b])
        mod = A.modulation(x, rate, a, b)
        if mod:
            ex['modulation'] = mod
        if any(ph['cls'] in ('stop', 'affricate') for ph in tgt):
            ex['vot_long_ms'] = A.vot_long(x, rate, a, b)
        out['extra'] = ex
    edges = {}
    if before is not None:
        for k in (1, 2, 3):
            edges['prev_F%d_80' % k] = (phones[before].get('meas') or {}).get('F%d_80_hz' % k)
    if after is not None:
        for k in (1, 2, 3):
            edges['next_F%d_20' % k] = (phones[after].get('meas') or {}).get('F%d_20_hz' % k)
    out['edges'] = edges
    return out


def summary(cases, man):
    """One number per measure for the entry, the mean over its contexts (alone left out where a
    context exists, since an isolated consonant is said after a schwa the front-end puts in)."""
    def vals(fn):
        xs = []
        for cid, c in cases.items():
            if cid == 'alone' and len(cases) > 1 and man != 'vowel':
                continue
            v = fn(c)
            if v is not None:
                xs.append(v)
        return sum(xs) / len(xs) if xs else None

    def tmeas(key):
        def fn(c):
            ts = [c['phones'][i] for i in c['target']]
            xs = [(ph.get('meas') or {}).get(key) for ph in ts]
            xs = [v for v in xs if v is not None]
            return xs[0] if xs else None
        return fn

    s = {}
    for k in ('F1_50_hz', 'F2_50_hz', 'F3_50_hz', 'F3_min_hz', 'peak_hz', 'centroid_hz', 'vot_ms', 'closure_ms',
              'murmur_F1_hz', 'antiformant_hz', 'intensity_db'):
        v = vals(tmeas(k))
        if v is not None:
            s[k] = round(v, 1)
    s['duration_ms'] = vals(lambda c: (c['phones'][c['target'][-1]]['end_ms'] - c['phones'][c['target'][0]]['start_ms'])
                            if c['target'] else None)
    for k in (1, 2, 3):
        v = vals(lambda c: _mean([c['edges'].get('prev_F%d_80' % k), c['edges'].get('next_F%d_20' % k)]))
        if v is not None:
            s['edge_F%d' % k] = round(v, 1)
    v = vals(lambda c: (c.get('extra') or {}).get('vot_long_ms'))
    if v is not None:
        s['vot_long_ms'] = round(v, 1)
    for k in ('dips', 'rate_hz', 'closed_ms'):
        v = vals(lambda c: ((c.get('extra') or {}).get('modulation') or {}).get(k))
        if v is not None:
            s['mod_' + k] = round(v, 2)
    vf = vals(lambda c: _voiced_frac(c))
    if vf is not None:
        s['voiced_frac'] = round(vf, 3)
    return s


def _voiced_frac(c):
    fr = sum((c['phones'][i].get('req') or {}).get('frames', 0) for i in c['target'])
    vo = sum((c['phones'][i].get('req') or {}).get('voiced_frames', 0) for i in c['target'])
    return vo / fr if fr else None


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def check_a1(cases, man):
    bad = []
    for cid, c in cases.items():
        if not c['target']:
            bad.append('%s: nothing sounded' % cid)
            continue
        ts = [c['phones'][i] for i in c['target']]
        if man in ('stop', 'click'):
            if not any((ph.get('meas') or {}).get('burst_ms') is not None or (ph.get('meas') or {}).get('closure_ms')
                       for ph in ts) and cid != 'alone':
                bad.append('%s: no closure or burst found' % cid)
            continue
        if all((ph.get('req') or {}).get('voiced_frames', 0) + (ph.get('req') or {}).get('noise_frames', 0) == 0
               for ph in ts):
            bad.append('%s: %s has no sounding frame' % (cid, '+'.join(ph['name'] for ph in ts)))
    return dict(passed=not bad, problems=bad)


def check_b3(e, s):
    """The specification's targets against the summary measures (prove.py's tolerances)."""
    spec = e.get('spec') or {}
    v = lambda x: x['v'] if isinstance(x, dict) else x  # noqa: E731
    want = {}
    for k, x in (spec.get('formants') or {}).items():
        want[k] = ('%s_50_hz' % k, v(x))
    if 'vot_ms' in spec:
        want['vot_ms'] = ('vot_ms', v(spec['vot_ms']))
    if 'peak_hz' in (spec.get('noise') or {}):
        want['peak_hz'] = ('peak_hz', v(spec['noise']['peak_hz']))
    dur = (spec.get('duration') or {}).get('inherent_ms')
    out = {}
    for k, (mk, w) in want.items():
        got = s.get(mk)
        out[k] = dict(target=w, measured=got, within=PR.within(k if k != 'peak_hz' else 'peak', got, w))
    if dur is not None:
        # a length is set as a share of the carrier's and the module's rhythm moves it by context:
        # within a quarter
        got = s.get('duration_ms')
        out['duration_ms'] = dict(target=v(dur), measured=got,
                                  within=got is not None and abs(got - v(dur)) <= 0.25 * v(dur))
    # every entry carries its specification (R19b), even one the module already says: no spec, no pass
    return dict(passed=bool(spec) and all(o['within'] for o in out.values()), targets=out, empty=not spec)


def contrast_ok(measure, mine, theirs, sign):
    if mine is None or theirs is None:
        return False, None
    d = mine - theirs
    if measure.endswith('_ms') or measure in ('duration_ms',):
        need = CONTRAST_MIN['ms']
    elif measure.endswith('_db'):
        need = CONTRAST_MIN['db']
    elif measure.startswith('mod_dips'):
        need = CONTRAST_MIN['count']
    else:
        need = CONTRAST_MIN['hz_rel'] * abs(theirs)
    return (d * sign >= need), round(d, 1)


def judge(t, sid, cases, diags, said_as):
    e = t.sounds[sid]
    man = manner(e) if e['kind'] == 'base' else None
    s = summary(cases, man) if e['kind'] == 'base' else {}
    losses = [d for d in diags if d['level'] == 'loss']
    a0 = dict(passed=not losses and not said_as.get('substitute'), losses=losses[:20],
              substitute=said_as.get('substitute'))
    a1 = check_a1(cases, man)
    a2 = RP.check_a(dict(cases={cid: c['gold'] for cid, c in cases.items()}), E.pack(said_as['pack']).phone_module)
    a2 = {k: a2[k] for k in ('passed', 'a1_phones', 'a1_silent', 'a2_checks', 'a2_ok', 'a2_rate', 'substituted',
                             'problems')}
    b3 = check_b3(e, s) if e['kind'] == 'base' else dict(passed=True, empty=False, targets={})
    return dict(manner=man, summary=s, A0=a0, A1=a1, A2=a2, B3=b3)


def test_map(pack, template, work):
    """compose_test's map (the pack's header lines and the realised master table), with the pack's
    `says` lines too: what the module says for its affricates, which the layer must be told."""
    p, path = CT.test_map(pack, template, work)
    with open(p.sounds_map, encoding='utf-8') as f:
        says = [l.rstrip('\n') for l in f if l.split()[:1] == ['says']]
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    out = os.path.join(work, 'sweep-%s.map' % template)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(says + lines))
    return p, out


def run(t, ids, template, pack, apply=False):
    os.makedirs(SWEEP_WORK, exist_ok=True)
    p, map_path = test_map(pack, template, SWEEP_WORK)
    with open(map_path, 'rb') as f:
        map_sha = hashlib.sha256(f.read()).hexdigest()
    realized = {sid: AD.realize(t, sid, template, (AD.loop_proof(sid) or {}).get('carrier_measured'))
                for sid in ids if t.sounds[sid]['kind'] == 'base'}
    results = {}
    for sid in ids:
        e = t.sounds[sid]
        cs = contexts(t, sid)
        if not cs:
            results[sid] = dict(id=sid, ipa=e['ipa'], skipped='no inputs for this kind of entry yet')
            continue
        r = realized.get(sid)
        said_as = dict(pack=pack, carrier=r['carrier'] if r else None, keys=r['keys'] if r else None,
                       distance=r['distance'] if r else None,
                       substitute=('%s is said as the module phone %s, %s feature steps away, unmoved' % (
                           e['ipa'], r['carrier'], r['distance'])) if r and r['distance'] and not r['keys'] else None)
        inputs, diags = [], []
        for cid, text in cs:
            rc, out, d = CT.say_ipa(p, map_path, text)
            if rc != 0:
                raise SystemExit('front-end failed on %s %r' % (sid, text))
            inputs.append((cid, text, out, d))
            diags += d
        rend = E.render(pack, [(cid, 'annotated', out) for cid, _, out, _ in inputs],
                        work=os.path.join(SWEEP_WORK, sid.replace('+', '_')))
        cases = {}
        for (cid, text, out, d), r_ in zip(inputs, rend):
            diags += r_['diag'][len(d):] if r_['diag'][:len(d)] == d else r_['diag']
            c = measure(r_, p, cid)
            c.update(ipa=text, said=out, diag=r_['diag'], wav_sha256=r_['wav_sha256'])
            cases[cid] = c
        verdict = judge(t, sid, cases, diags, said_as)
        results[sid] = dict(id=sid, ipa=e['ipa'], name=e['name'], template=template, pack=pack, staged=E.STAGE or None,
                            frontend=E.FRONTEND, map=os.path.relpath(map_path, ROOT) if map_path.startswith(ROOT) else
                            map_path, map_sha256=map_sha, said_as=said_as, cases=cases, **verdict)
    # B2: the contrasts the entries' tests name, against the partner's own measures (this run's,
    # or its proof file's)
    for sid, res in results.items():
        if 'summary' not in res:
            continue
        b2 = []
        for c in (t.sounds[sid].get('tests') or {}).get('contrast', []):
            other = results.get(c['with'])
            if other is None:
                path = os.path.join(PROOFS, c['with'] + '.json')
                other = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else None
            theirs = (other or {}).get('summary', {}).get(c['measure'])
            ok, d = contrast_ok(c['measure'], res['summary'].get(c['measure']), theirs, c['sign'])
            b2.append(dict(c, mine=res['summary'].get(c['measure']), theirs=theirs, difference=d, holds=ok))
        res['B2'] = dict(passed=all(x['holds'] for x in b2), contrasts=b2)
        res['passed'] = all(res[k]['passed'] for k in ('A0', 'A1', 'A2', 'B3', 'B2'))
    os.makedirs(PROOFS, exist_ok=True)
    for sid, res in results.items():
        if 'summary' not in res:
            continue
        slim = json.loads(json.dumps(res, default=float))
        for c in slim['cases'].values():
            c.pop('gold', None)
        with open(os.path.join(PROOFS, sid + '.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(slim, f, ensure_ascii=False, indent=1)
    if apply:
        apply_states(t, results)
    return results


def apply_states(t, results):
    """For each entry that passed: state = its plan's end state, level 2, tests.proof. Edits the
    TOML text in place, only those three lines of the entry (the table is otherwise by hand)."""
    files = {}
    for sid, res in results.items():
        if not res.get('passed'):
            continue
        e = t.sounds[sid]
        files.setdefault(t.where[sid], []).append((sid, e['plan']['end_state']))
    for name, items in files.items():
        path = os.path.join(T.IPA, 'table', name)
        with open(path, encoding='utf-8') as f:
            text = f.read()
        for sid, state in items:
            head = '[sound."%s"]' % sid
            a = text.index(head)
            b = text.find('\n[sound."', a + len(head))
            b = len(text) if b < 0 else b
            block = text[a:b]
            block = re.sub(r'(?m)^state = ".*"$', 'state = "%s"' % state, block, count=1)
            block = re.sub(r'(?m)^level = \d+$', 'level = 2', block, count=1)
            tests_head = '[sound."%s".tests]' % sid
            ta = block.index(tests_head)
            tb = block.find('\n[', ta + len(tests_head))
            tb = len(block) if tb < 0 else tb
            tests = block[ta:tb]
            line = 'proof = "ipa/proofs/%s.json"' % sid
            tests = re.sub(r'(?m)^proof = ".*"$', line, tests) if re.search(r'(?m)^proof = ', tests) \
                else tests.rstrip('\n') + '\n' + line + '\n'
            block = block[:ta] + tests + block[tb:]
            text = text[:a] + block + text[b:]
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)


def fmt(res):
    if 'summary' not in res:
        return '%-8s %-3s %s' % (res['id'], res['ipa'], res.get('skipped'))
    flags = ' '.join('%s:%s' % (k, 'ok' if res[k]['passed'] else 'FAIL') for k in ('A0', 'A1', 'A2', 'B3', 'B2'))
    s = res['summary']
    keys = [k for k in ('F1_50_hz', 'F2_50_hz', 'F3_50_hz', 'edge_F2', 'edge_F3', 'vot_ms', 'peak_hz', 'murmur_F1_hz',
                        'mod_rate_hz', 'duration_ms') if s.get(k) is not None]
    why = []
    if res['A0']['substitute']:
        why.append('substitute')
    why += ['%s %s' % (d['kind'], d['detail'][:40]) for d in res['A0']['losses'][:2]]
    why += res['A1']['problems'][:1]
    if res['B3'].get('empty'):
        why.append('no specification')
    why += ['%s %s≠%s' % (k, v['measured'], v['target']) for k, v in res['B3']['targets'].items() if not v['within']]
    why += ['%s %s vs %s %s' % (c['measure'], c['mine'], c['with'], c['theirs']) for c in res['B2']['contrasts']
            if not c['holds']]
    return '%-8s %-3s %-4s %s  %s%s' % (res['id'], res['ipa'], 'PASS' if res['passed'] else 'fail', flags,
                                       ' '.join('%s=%s' % (k, round(s[k])) for k in keys),
                                       ('  [' + '; '.join(why) + ']') if why else '')


def select(t, args):
    if not args:
        return sorted(t.sounds)
    out = []
    for a in args:
        if a in t.sounds:
            out.append(a)
        else:
            out += sorted(i for i, e in t.sounds.items() if e.get('section') == a)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('which', nargs='*', help='ids (U+0288) or sections (pulmonic); default: all')
    ap.add_argument('--template', default='dedx')
    ap.add_argument('--pack', default='hi', help='a pack on --template: its header lines make the test map')
    ap.add_argument('--apply', action='store_true', help='set state, level and proof of the entries that pass')
    a = ap.parse_args()
    if not E.STAGE:
        raise SystemExit('set EVV_STAGE: the proofs are of the staged modules and front-end')
    t = T.load()
    ids = select(t, a.which)
    if E.pack(a.pack).template != a.template:
        raise SystemExit('%s is not on %s' % (a.pack, a.template))
    AD.write(t, a.template)
    res = run(t, ids, a.template, a.pack, a.apply)
    for sid in ids:
        print(fmt(res[sid]))
    done = [r for r in res.values() if r.get('passed')]
    print('sweep: %d entries, %d rendered, %d passed every check, %d not yet; proofs in ipa/proofs/' % (
        len(ids), sum('summary' in r for r in res.values()), len(done),
        sum('summary' in r and not r.get('passed') for r in res.values())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
