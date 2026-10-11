"""Phase 5 audit, step 1 (MIT licence; python docs/tts-extension/audit5/audit_consistency.py): consistency of the master table (spec and measured).

Prints: vowel formant ordering by height / backness / rounding (spec and the proofs' measured
middles); consonant voiced/voiceless pairs and what differs; place ordering of loci and noise
peaks per manner; exact duplicates of realisation (carrier + keys) and of transforms; the
signatures of nasals, laterals and rhotics; the direction of each mark's transform.
"""
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'ipa'))
os.environ.setdefault('EVV_STAGE', r'C:\Users\joshk\OpenEvvBuild-ttsext\stage-dev')
import table as T  # noqa: E402
import adapter as AD  # noqa: E402

t = T.load()
H = ['close', 'near-close', 'close-mid', 'mid', 'open-mid', 'near-open', 'open']
B = ['front', 'near-front', 'central', 'near-back', 'back']
PLACES = ['bilabial', 'labiodental', 'linguolabial', 'dental', 'alveolar', 'postalveolar', 'retroflex',
          'alveolo-palatal', 'palatal', 'velar', 'uvular', 'pharyngeal', 'epiglottal', 'glottal']
findings = []


def V(x):
    return x['v'] if isinstance(x, dict) else x


def proof(e):
    p = (e.get('tests') or {}).get('proof')
    if not p:
        return None
    path = os.path.join(ROOT, p)
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def tierA(e):
    return e.get('tier') == 'A'


def flag(sev, text):
    findings.append((sev, text))
    print('  [%s] %s' % (sev, text))


# ---------------------------------------------------------------- vowels
print('\n== VOWELS: spec and measured (F1 F2 F3 at the middle, median over contexts)')
vow = {}
for sid, e in t.sounds.items():
    if e['kind'] != 'base' or e['features'].get('class') != 'vowel' or not tierA(e):
        continue
    f = e['features']
    sp = e.get('spec', {}).get('formants', {})
    pr = proof(e)
    s = (pr or {}).get('summary') or {}
    vow[sid] = dict(ipa=e['ipa'], h=f['height'], b=f['backness'], r=f['rounding'],
                    F1=V(sp.get('F1')), F2=V(sp.get('F2')), F3=V(sp.get('F3')),
                    m1=s.get('F1_50_hz'), m2=s.get('F2_50_hz'), m3=s.get('F3_50_hz'),
                    tags=tuple(sorted({x['tag'] for x in sp.values() if isinstance(x, dict)})))
    v_ = vow[sid]
    print('  %-3s %-10s %-10s %-10s spec %4s %4s %4s  meas %6s %6s %6s  %s' % (
        v_['ipa'], v_['h'], v_['b'], v_['r'], v_['F1'], v_['F2'], v_['F3'],
        v_['m1'], v_['m2'], v_['m3'], ','.join(v_['tags'])))

print('\n-- height ~ F1: within one backness column and rounding, F1 must rise with openness')
cols = collections.defaultdict(list)
for sid, v_ in vow.items():
    cols[(v_['b'], v_['r'])].append(v_)
for (b, r), lst in sorted(cols.items()):
    lst.sort(key=lambda x: H.index(x['h']))
    for a, c in zip(lst, lst[1:]):
        for k, lab in (('F1', 'spec'), ('m1', 'measured')):
            if a[k] is not None and c[k] is not None and c[k] < a[k]:
                flag('consistency', 'F1 %s: %s (%s) %s < %s (%s) %s in column %s %s' % (
                    lab, c['ipa'], c['h'], c[k], a['ipa'], a['h'], a[k], b, r))

print('-- backness ~ F2: within one height row and rounding, F2 must fall from front to back')
rows = collections.defaultdict(list)
for sid, v_ in vow.items():
    rows[(v_['h'], v_['r'])].append(v_)
for (h, r), lst in sorted(rows.items()):
    lst.sort(key=lambda x: B.index(x['b']))
    for a, c in zip(lst, lst[1:]):
        for k, lab in (('F2', 'spec'), ('m2', 'measured')):
            if a[k] is not None and c[k] is not None and c[k] > a[k]:
                flag('consistency', 'F2 %s: %s (%s) %s > %s (%s) %s in row %s %s' % (
                    lab, c['ipa'], c['b'], c[k], a['ipa'], a['b'], a[k], h, r))

print('-- rounding lowers F2 and F3: rounded against unrounded at the same height and backness')
cells = collections.defaultdict(dict)
for sid, v_ in vow.items():
    cells[(v_['h'], v_['b'])][v_['r']] = v_
for (h, b), d in sorted(cells.items()):
    if 'rounded' in d and 'unrounded' in d:
        u, r = d['unrounded'], d['rounded']
        for k, lab in (('F2', 'spec'), ('m2', 'measured'), ('F3', 'spec'), ('m3', 'measured')):
            if u[k] is not None and r[k] is not None and r[k] >= u[k]:
                flag('consistency', '%s %s: rounded %s %s >= unrounded %s %s (%s %s)' % (
                    k.replace('m', 'F'), lab, r['ipa'], r[k], u['ipa'], u[k], h, b))
        print('  %s/%s: dF2 spec %s meas %s; dF3 spec %s meas %s' % (
            u['ipa'], r['ipa'], (r['F2'] or 0) - (u['F2'] or 0),
            None if None in (r['m2'], u['m2']) else round(r['m2'] - u['m2']),
            (r['F3'] or 0) - (u['F3'] or 0), None if None in (r['m3'], u['m3']) else round(r['m3'] - u['m3'])))

print('-- spacing: F1 < F2 < F3, F2 - F1 >= 150, F3 - F2 >= 200 (spec); measured within 8 % of spec')
for sid, v_ in vow.items():
    if None not in (v_['F1'], v_['F2'], v_['F3']):
        if not (v_['F1'] < v_['F2'] < v_['F3']) or v_['F2'] - v_['F1'] < 150 or v_['F3'] - v_['F2'] < 200:
            flag('consistency', 'spacing %s: %s %s %s' % (v_['ipa'], v_['F1'], v_['F2'], v_['F3']))
    for k, m in (('F1', 'm1'), ('F2', 'm2'), ('F3', 'm3')):
        if v_[k] and v_[m] and abs(v_[m] - v_[k]) > 0.08 * v_[k] and not (k == 'F1' and abs(v_[m] - v_[k]) <= 85):
            flag('measured-off', '%s %s spec %s measured %s (%.1f %%)' % (
                v_['ipa'], k, v_[k], v_[m], 100.0 * (v_[m] - v_[k]) / v_[k]))

# ---------------------------------------------------------------- consonants
print('\n== CONSONANTS: realisation on dedx (carrier + keys) and spec summary')
cons = {}
real = {}
for sid, e in sorted(t.sounds.items()):
    if e['kind'] != 'base':
        continue
    try:
        r = AD.realize(t, sid, 'dedx', (AD.loop_proof(sid) or {}).get('carrier_measured'))
        real[sid] = (r['carrier'], tuple(sorted(r['keys'].items())), r['distance'])
    except Exception as x:  # noqa: BLE001
        real[sid] = ('ERROR', str(x), None)
    if e['features'].get('class') != 'consonant' or not tierA(e):
        continue
    f = e['features']
    sp = e.get('spec') or {}
    pr = proof(e)
    s = (pr or {}).get('summary') or {}
    cons[sid] = dict(ipa=e['ipa'], f=f, sp=sp, s=s, real=real[sid])
    fm = sp.get('formants') or {}
    lo = sp.get('locus') or {}
    no = sp.get('noise') or {}
    print('  %-3s %-13s %-13s %-9s %-4s | F %s | locus %s | noise %s | vot %s dur %s | %s %s' % (
        e['ipa'], f.get('place'), f.get('stricture'), f.get('voicing'),
        ''.join(k[0] for k in ('nasal', 'lateral', 'sibilant') if f.get(k)),
        ' '.join('%s=%s' % (k, V(x)) for k, x in fm.items()),
        ' '.join('%s=%s' % (k, V(x)) for k, x in lo.items()),
        ' '.join('%s=%s' % (k, V(x)) for k, x in no.items()),
        V(sp.get('vot_ms')), V((sp.get('duration') or {}).get('inherent_ms')),
        real[sid][0], ' '.join('%s=%s' % kv for kv in real[sid][1])))

print('\n-- voiced / voiceless pairs: place values should agree; voiced shorter; voiced VOT smaller')
pairs = collections.defaultdict(dict)
for sid, c in cons.items():
    f = c['f']
    key = (f.get('place'), f.get('place2', 'none'), f.get('stricture'), f.get('nasal', False), f.get('lateral', False),
           f.get('sibilant', False), f.get('airstream', 'pulmonic'))
    pairs[key][f.get('voicing')] = c
for key, d in sorted(pairs.items(), key=lambda kv: str(kv[0])):
    if 'voiced' in d and 'voiceless' in d:
        a, b = d['voiceless'], d['voiced']
        notes = []
        for grp in ('locus', 'formants', 'noise'):
            for k in set((a['sp'].get(grp) or {})) | set((b['sp'].get(grp) or {})):
                x, y = V((a['sp'].get(grp) or {}).get(k)), V((b['sp'].get(grp) or {}).get(k))
                if x is None or y is None:
                    notes.append('%s.%s only in %s' % (grp, k, a['ipa'] if x is not None else b['ipa']))
                elif isinstance(x, (int, float)) and abs(x - y) > 0.10 * abs(x):
                    notes.append('%s.%s %s vs %s' % (grp, k, x, y))
        da, db = V((a['sp'].get('duration') or {}).get('inherent_ms')), V((b['sp'].get('duration') or {}).get('inherent_ms'))
        if da is not None and db is not None and db >= da:
            notes.append('duration voiced %s >= voiceless %s' % (db, da))
        va, vb = V(a['sp'].get('vot_ms')), V(b['sp'].get('vot_ms'))
        if va is not None and vb is not None and vb >= va:
            notes.append('VOT voiced %s >= voiceless %s' % (vb, va))
        ma, mb = a['s'], b['s']
        for mk in ('peak_hz', 'centroid1k_hz', 'duration_ms', 'F2_50_hz', 'F3_50_hz'):
            if ma.get(mk) is not None and mb.get(mk) is not None:
                notes.append('meas %s %s/%s' % (mk, round(ma[mk]), round(mb[mk])))
        print('  %s/%s: %s' % (a['ipa'], b['ipa'], '; '.join(notes) or 'no spec difference beyond voicing'))
        for n in notes:
            if ' vs ' in n or 'only in' in n or '>=' in n:
                flag('pair', '%s/%s: %s' % (a['ipa'], b['ipa'], n))

print('\n-- place ordering per manner (spec locus F2, noise peak, F2/F3), front to back')
by_manner = collections.defaultdict(list)
for sid, c in cons.items():
    f = c['f']
    man = f.get('stricture') + ('-nasal' if f.get('nasal') else '') + ('-lateral' if f.get('lateral') else '')
    if f.get('airstream', 'pulmonic') != 'pulmonic' or f.get('place2', 'none') != 'none':
        continue
    by_manner[(man, f.get('voicing'))].append(c)
for (man, voi), lst in sorted(by_manner.items()):
    lst.sort(key=lambda c: PLACES.index(c['f'].get('place')) if c['f'].get('place') in PLACES else 99)
    line = []
    for c in lst:
        sp = c['sp']
        lo = V((sp.get('locus') or {}).get('F2'))
        pk = V((sp.get('noise') or {}).get('peak_hz'))
        f2 = V((sp.get('formants') or {}).get('F2'))
        f3 = V((sp.get('formants') or {}).get('F3'))
        m = c['s']
        line.append('%s[%s] locus2=%s pk=%s F2=%s F3=%s | meas pk=%s F2=%s F3=%s' % (
            c['ipa'], c['f'].get('place')[:5], lo, pk, f2, f3,
            m.get('peak_hz') and round(m['peak_hz']), m.get('F2_50_hz') and round(m['F2_50_hz']),
            m.get('F3_50_hz') and round(m['F3_50_hz'])))
    print('  %s %s:\n     %s' % (man, voi, '\n     '.join(line)))

print('\n-- exact duplicates of realisation (same carrier and keys) under different ids')
dup = collections.defaultdict(list)
for sid, (car, keys, dist) in real.items():
    dup[(car, keys)].append(sid)
for (car, keys), sids in dup.items():
    if len(sids) > 1:
        eq = {t.sounds[s].get('equivalent_to') for s in sids}
        flag('duplicate' if not (eq & set(sids)) else 'duplicate-equivalent',
             '%s said alike: %s %s' % (' '.join(t.sounds[s]['ipa'] for s in sids), car, ' '.join('%s=%s' % kv for kv in keys)))
print('-- unmoved carriers (distance > 0 and no keys): a silent substitution')
for sid, (car, keys, dist) in real.items():
    if dist and not keys:
        flag('substitution', '%s is the module phone %s unmoved (%s steps)' % (t.sounds[sid]['ipa'], car, dist))

print('\n-- exact duplicates of transforms among marks (different ids, not equivalent)')
tr = collections.defaultdict(list)
for sid, e in t.sounds.items():
    if e['kind'] in ('modifier', 'tone', 'syllable-mark', 'boundary', 'tie', 'label') and e.get('transform'):
        tr[json.dumps(e['transform'], sort_keys=True)].append(sid)
for k, sids in tr.items():
    if len(sids) > 1:
        eq = {t.sounds[s].get('equivalent_to') for s in sids}
        flag('duplicate' if not (eq & set(sids)) else 'duplicate-equivalent',
             'marks with one transform: %s' % ' '.join('%s(%s)' % (t.sounds[s]['ipa'], s) for s in sids))

print('\n-- nasals, laterals, rhotics: spec, realised keys and measured signature')
for sid, c in sorted(cons.items()):
    f = c['f']
    rh = c['ipa'] in 'ɹɻɽɖʈʂʐɳɭr' or f.get('place') == 'retroflex'
    if f.get('nasal') or f.get('lateral') or rh:
        s = c['s']
        kind = 'nasal' if f.get('nasal') else 'lateral' if f.get('lateral') else 'rhotic/retroflex'
        print('  %-3s %-16s keys %-55s spec %s | meas F2 %s F3 %s hnr_hi %s band %s' % (
            c['ipa'], kind, ' '.join('%s=%s' % kv for kv in c['real'][1]),
            ' '.join('%s=%s' % (k, V(x)) for k, x in (c['sp'].get('formants') or {}).items()),
            s.get('F2_50_hz') and round(s['F2_50_hz']), s.get('F3_50_hz') and round(s['F3_50_hz']),
            s.get('hnr_hi_db'), s.get('band_db')))
        if kind == 'rhotic/retroflex' and s.get('F3_50_hz') and s['F3_50_hz'] > 2300 and c['ipa'] not in 'r':
            flag('signature', '%s measured F3 %s is not lowered' % (c['ipa'], round(s['F3_50_hz'])))

# ---------------------------------------------------------------- marks: direction
print('\n== MARKS (Tier A): every transform operation, for a direction check')
EXPECT = {  # ipa: [(class, path-substring, op, predicate description, predicate)]
    '̹': [('vowel', 'F2', lambda op, x: (op == 'scale' and x < 1) or (op == 'add' and x < 0))],
    '̜': [('vowel', 'F2', lambda op, x: (op == 'scale' and x > 1) or (op == 'add' and x > 0))],
    '̟': [('vowel', 'F2', lambda op, x: (op == 'scale' and x > 1) or (op == 'add' and x > 0))],
    '̠': [('vowel', 'F2', lambda op, x: (op == 'scale' and x < 1) or (op == 'add' and x < 0))],
    '̝': [('vowel', 'F1', lambda op, x: (op == 'scale' and x < 1) or (op == 'add' and x < 0))],
    '̞': [('vowel', 'F1', lambda op, x: (op == 'scale' and x > 1) or (op == 'add' and x > 0) or (op == 'toward' and x > 600))],
    'ʷ': [('consonant', 'F2', lambda op, x: (op == 'scale' and x < 1) or (op == 'add' and x < 0))],
    'ʲ': [('consonant', 'F2', lambda op, x: (op == 'scale' and x > 1) or (op == 'add' and x > 0))],
    'ˠ': [('consonant', 'F2', lambda op, x: (op == 'scale' and x < 1) or (op == 'add' and x < 0))],
    'ˤ': [('consonant', 'F1', lambda op, x: (op == 'scale' and x > 1) or (op == 'add' and x > 0))],
    '̘': [('vowel', 'F1', lambda op, x: (op == 'scale' and x < 1) or (op == 'add' and x < 0))],
    '̙': [('vowel', 'F1', lambda op, x: (op == 'scale' and x > 1) or (op == 'add' and x > 0) or (op == 'toward' and x > 600))],
    'ː': [('vowel', 'inherent_ms', lambda op, x: op == 'scale' and x > 1)],
    'ˑ': [('vowel', 'inherent_ms', lambda op, x: op == 'scale' and x > 1)],
    '̆': [('vowel', 'inherent_ms', lambda op, x: op == 'scale' and x < 1)],
    'ʰ': [('consonant', 'vot', lambda op, x: op in ('add', 'set') and x > 0)],
    '̥': [('consonant', 'voiced', lambda op, x: op == 'set' and x == 0)],
    '̬': [('consonant', 'voiced', lambda op, x: op == 'set' and x == 1)],
}
for sid, e in sorted(t.sounds.items()):
    if e['kind'] != 'modifier' or not tierA(e):
        continue
    flat = []
    for cls, tr_ in (e.get('transform') or {}).items():
        def walk(n, path):
            if isinstance(n, dict):
                if 'tag' in n:
                    op = [k for k in n if k in T.TRANSFORM_OPS]
                    flat.append((cls, path, op[0] if op else '?', n.get(op[0]) if op else None, n['tag']))
                else:
                    for k, v in n.items():
                        walk(v, path + '.' + k if path else k)
        walk(tr_, '')
    print('  %-3s %-40s %s' % (e['ipa'], e['name'][:40], '; '.join('%s:%s %s %s [%s]' % x for x in flat)))
    for cls, sub, pred in EXPECT.get(e['ipa'], []):
        hits = [x for x in flat if x[0] == cls and sub in x[1]]
        if not hits:
            flag('direction', '%s: no %s transform on %s found' % (e['ipa'], sub, cls))
        for x in hits:
            if isinstance(x[3], (int, float)) and not pred(x[2], x[3]):
                flag('direction', '%s: %s %s %s %s is not in the expected direction' % (e['ipa'], x[0], x[1], x[2], x[3]))

print('\n== TONES: levels')
for sid, e in sorted(t.sounds.items()):
    if e['kind'] == 'tone' and tierA(e):
        print('  %-5s levels %-12s %s' % (e['ipa'], e.get('levels'), e['name'][:70]))

print('\n== FINDINGS: %d' % len(findings))
for sev, text in findings:
    print('  [%s] %s' % (sev, text))
