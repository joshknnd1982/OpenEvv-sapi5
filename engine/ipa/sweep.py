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
    follow = t.sounds[tests['follow']]['ipa'] if tests.get('follow') else ''
    for base in tests.get('bases', []):
        b = t.sounds[base]
        for variant, x in (('plain', b['ipa']), ('marked', b['ipa'] + e['ipa'])):
            if e['ipa'] == '\u0329':
                # a syllabic consonant: after a stressed syllable, the word ending in it
                out.append(('%s_%s_pa' % (base, variant), 'ˈpa%s%s' % ('p' if variant == 'marked' else 'pa', x)))
            elif manner(b) == 'vowel':
                out += [('%s_%s_%s' % (base, variant, c), 'ˈ%s%s%s' % (c, x, c)) for c in CONSONANTS_AROUND]
            else:
                out += [('%s_%s_%s' % (base, variant, v), 'ˈ%s%s%s%s' % (v, x, follow, v)) for v in VOWELS_AROUND]
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
    if case_id.endswith('_pa'):
        # `ˈpapn̩' (or `ˈpapan'): the last sounding phone, and a schwa just before it
        idx = [sounding[-1]]
        if len(sounding) >= 2 and phones[sounding[-2]]['name'] == '@':
            idx = [sounding[-2], sounding[-1]]
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
            # a release: noise in the frames within 25 ms after the closure (T-release)
            t_ = E.frame_times(r['frames'])
            win = (t_ >= b) & (t_ < b + 25)
            ex['burst_found'] = int(bool(((r['frames'][win, E.P['af']] > 0) | (r['frames'][win, E.P['ab']] > 0)).any()))
        last = tgt[-1]
        if last['cls'] in ('vowel', 'nasal', 'liquid', 'glide') and last['end_ms'] - last['start_ms'] >= 40:
            mid = (last['start_ms'] + last['end_ms']) / 2.0
            ex['h1h2_db'] = A.h1_h2(x, rate, mid)
            f1 = (last.get('meas') or {}).get('F1_50_hz')
            if f1:
                ex['a1_p0_db'] = A.a1_p0(x, rate, mid, f1)
        ex['schwa_ms'] = sum(ph['end_ms'] - ph['start_ms'] for ph in tgt if ph['name'] == '@')
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
        # the median: one context's tracker error (a low F1 near a harmonic, D15; a burst read as
        # a formant in a short vowel) must not carry the summary
        xs.sort()
        n = len(xs)
        return (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0) if xs else None

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
    for k in ('h1h2_db', 'a1_p0_db', 'burst_found', 'schwa_ms'):
        v = vals(lambda c: (c.get('extra') or {}).get(k))
        if v is not None:
            s['%s' % k] = round(v, 2)
    if s.get('F2_50_hz') is not None:
        # how near the centre: for the centralizing marks (larger is nearer the table's ə)
        s['F2_toward_centre'] = round(-abs(s['F2_50_hz'] - 1454.0), 1)
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
        if man in ('stop', 'click') or all(ph['cls'] == 'stop' for ph in ts):
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
    # a trill's rate (the modulation of its level) within 15 per cent; a tap's or trill's closed
    # time within 40 per cent (the level measure finds the closure's edges only to a few ms)
    trill = spec.get('trill') or {}
    if 'rate_hz' in trill:
        got, w = s.get('mod_rate_hz'), v(trill['rate_hz'])
        out['trill_rate_hz'] = dict(target=w, measured=got, within=got is not None and abs(got - w) <= 0.15 * w)
    for k in ('trill', 'tap'):
        if 'closed_ms' in (spec.get(k) or {}):
            got, w = s.get('mod_closed_ms'), v(spec[k]['closed_ms'])
            out['%s_closed_ms' % k] = dict(target=w, measured=got,
                                           within=got is not None and abs(got - w) <= 0.4 * w)
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
    if e['kind'] == 'base':
        b3 = check_b3(e, s)
    elif e['kind'] == 'modifier':
        b3 = check_shift(t, sid, cases)
        s = b3.pop('summary')
        # every marked case must have been composed with the mark, not said without it
        marked = [c for cid, c in cases.items() if '_marked_' in cid]
        unc = [cid for cid, c in cases.items() if '_marked_' in cid and not any(
            d['kind'] == 'composed' or d['kind'] == 'tone-made' for d in c['diag'])]
        if unc and marked:
            a0 = dict(a0, passed=False, not_composed=unc[:6])
    else:
        b3 = dict(passed=True, empty=False, targets={})
    return dict(manner=man, summary=s, A0=a0, A1=a1, A2=a2, B3=b3)


def check_shift(t, sid, cases):
    """T-shift and its kin: per base, the marked sound against the plain one in the same contexts;
    every named measure that applies to the base must move the stated way by at least the
    contrast minimum, and each base must have at least one."""
    tests = t.sounds[sid].get('tests') or {}
    per, targets, ok_all = {}, {}, True
    for base in tests.get('bases', []):
        man = manner(t.sounds[base])
        sp = summary({c: v for c, v in cases.items() if c.startswith(base + '_plain_')}, man)
        sm = summary({c: v for c, v in cases.items() if c.startswith(base + '_marked_')}, man)
        per[base] = dict(plain=sp, marked=sm)
        checked = 0
        for sh in tests.get('shift', []):
            m = sh['measure']
            if sp.get(m) is None and sm.get(m) is None:
                continue
            ok, d = contrast_ok(m, sm.get(m), sp.get(m), sh['sign']) if m != 'burst_found' else (
                (sm.get(m) is not None and sp.get(m) is not None and (sm[m] - sp[m]) * sh['sign'] >= 1),
                None if sm.get(m) is None or sp.get(m) is None else sm[m] - sp[m])
            targets['%s %s' % (t.sounds[base]['ipa'], m)] = dict(target='%+d' % sh['sign'], measured=d, within=ok,
                                                               plain=sp.get(m), marked=sm.get(m))
            checked += 1
            ok_all &= ok
        if not checked:
            targets['%s (none)' % t.sounds[base]['ipa']] = dict(target='a measure', measured=None, within=False)
            ok_all = False
    return dict(passed=ok_all and bool(per), targets=targets, empty=not per, summary=per)


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


def say_entry(t, sid, template, pack):
    """One entry said in its contexts and judged (B2 aside): the map written afresh from `t', so
    that a correction made in this run is the one that speaks."""
    AD.write(t, template, quiet=True)
    p, map_path = test_map(pack, template, SWEEP_WORK)
    with open(map_path, 'rb') as f:
        map_sha = hashlib.sha256(f.read()).hexdigest()
    e = t.sounds[sid]
    r = AD.realize(t, sid, template, (AD.loop_proof(sid) or {}).get('carrier_measured')) if e['kind'] == 'base' else None
    said_as = dict(pack=pack, carrier=r['carrier'] if r else None, keys=r['keys'] if r else None,
                   distance=r['distance'] if r else None,
                   substitute=('%s is said as the module phone %s, %s feature steps away, unmoved' % (
                       e['ipa'], r['carrier'], r['distance'])) if r and r['distance'] and not r['keys'] else None)
    inputs, diags = [], []
    for cid, text in contexts(t, sid):
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
    return dict(id=sid, ipa=e['ipa'], name=e['name'], template=template, pack=pack, staged=E.STAGE or None,
                frontend=E.FRONTEND, map=os.path.relpath(map_path, ROOT) if map_path.startswith(ROOT) else map_path,
                map_sha256=map_sha, said_as=said_as, cases=cases, **verdict)


# The USP's design loop (playbook 1.6, step 6): a target missed is corrected from what was measured
# and the entry said again, at most five rounds. A correction is a `trim' for this template only:
# the specification is never touched (DESIGN.md 5).
ROUNDS = 5
TRIM_KEYS = {'F1': ['f1'], 'F2': ['f2'], 'F3': ['f3'], 'peak_hz': ['f2', 'f3', 'f4']}


def corrections(res, trims):
    """New trims (key -> per cent, multiplied in) from the B3 targets this round missed, or None
    when nothing can be corrected this way."""
    out, any_ = dict(trims), False
    for k, tg in res['B3']['targets'].items():
        if tg['within'] or not tg['measured'] or k not in TRIM_KEYS:
            continue
        f = tg['target'] / tg['measured']
        for key in TRIM_KEYS[k]:
            out[key] = out.get(key, 100.0) * f
        any_ = True
    return out if any_ else None


def with_trims(t, sid, template, trims):
    e = t.sounds[sid]
    ov = e.setdefault('realization', {}).setdefault('openevv', {})
    ov.setdefault('trim', {})[template] = [dict(key=k, v=round(v, 1), scale=True, tag='measured',
                                                proof='ipa/proofs/%s.json' % sid) for k, v in sorted(trims.items())]


def prove_entry(t, sid, template, pack, rounds=ROUNDS):
    """Say an entry; while a specification target is missed, correct and say it again."""
    old = ((t.sounds[sid].get('realization') or {}).get('openevv') or {}).get('trim', {}).get(template)
    trims = {tr['key']: tr['v'] for tr in old or [] if tr.get('scale')}
    history = []
    res = say_entry(t, sid, template, pack)
    while True:
        history.append(dict(round=len(history) + 1, trims=dict(trims), B3=res['B3']['targets'],
                            keys=res['said_as']['keys']))
        if res['B3']['passed'] or len(history) >= rounds:
            break
        nxt = corrections(res, trims)
        if nxt is None:
            break
        trims = nxt
        with_trims(t, sid, template, trims)
        res = say_entry(t, sid, template, pack)
    res['rounds'] = history
    res['trims'] = {k: round(v, 1) for k, v in trims.items()} if res['B3']['passed'] and trims else {}
    if not res['trims'] and trims and old is None:
        # nothing converged: the entry is left as it was, the rounds kept as the evidence
        ((t.sounds[sid].get('realization') or {}).get('openevv') or {}).get('trim', {}).pop(template, None)
    return res


def run(t, ids, template, pack, apply=False, rounds=ROUNDS):
    os.makedirs(SWEEP_WORK, exist_ok=True)
    results = {}
    for sid in ids:
        e = t.sounds[sid]
        if not contexts(t, sid):
            results[sid] = dict(id=sid, ipa=e['ipa'], skipped='no inputs for this kind of entry yet')
            continue
        results[sid] = prove_entry(t, sid, template, pack, rounds if e['kind'] == 'base' else 1)
    AD.write(t, template, quiet=True)
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
        save_trims(t, results, template)
    return results


def save_trims(t, results, template):
    """A correction that brought an entry within its targets is written into the entry's
    realisation (`trim.<template>', tagged measured, its proof named), and nothing else."""
    for sid, res in results.items():
        if not res.get('passed') or not res.get('trims'):
            continue
        path = os.path.join(T.IPA, 'table', t.where[sid])
        with open(path, encoding='utf-8') as f:
            text = f.read()
        line = 'trim.%s = [%s]' % (template, ', '.join(
            '{ key = "%s", v = %s, scale = true, tag = "measured", proof = "ipa/proofs/%s.json" }' % (k, v, sid)
            for k, v in sorted(res['trims'].items())))
        head = '[sound."%s".realization.openevv]' % sid
        if head in text:
            a = text.index(head) + len(head)
            b = text.find('\n[', a)
            b = len(text) if b < 0 else b
            block = re.sub(r'(?m)^trim\.%s = .*\n?' % template, '', text[a:b])
            text = text[:a] + block.rstrip('\n') + '\n' + line + '\n' + text[b:]
        else:
            th = '[sound."%s".tests]' % sid
            ta = text.index(th)
            tb = text.find('\n[sound."', ta)
            add = '\n\n%s\n%s\n' % (head, line)
            text = text.rstrip('\n') + add if tb < 0 else text[:tb].rstrip('\n') + add + text[tb:]
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)


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
    # a mark's summary is per base (plain and marked); its numbers are in its B3 lines instead
    s = {} if any(isinstance(v, dict) for v in res['summary'].values()) else res['summary']
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
    ap.add_argument('--apply', action='store_true', help='set state, level and proof of the entries that pass, and '
                    'write the corrections that got them there')
    ap.add_argument('--rounds', type=int, default=ROUNDS, help='design rounds an entry may take (1: no correction)')
    a = ap.parse_args()
    if not E.STAGE:
        raise SystemExit('set EVV_STAGE: the proofs are of the staged modules and front-end')
    t = T.load()
    ids = select(t, a.which)
    if E.pack(a.pack).template != a.template:
        raise SystemExit('%s is not on %s' % (a.pack, a.template))
    res = run(t, ids, a.template, a.pack, a.apply, a.rounds)
    for sid in ids:
        print(fmt(res[sid]))
    done = [r for r in res.values() if r.get('passed')]
    print('sweep: %d entries, %d rendered, %d passed every check, %d not yet; proofs in ipa/proofs/' % (
        len(ids), sum('summary' in r for r in res.values()), len(done),
        sum('summary' in r and not r.get('passed') for r in res.values())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
