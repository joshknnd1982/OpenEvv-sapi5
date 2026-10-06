"""Golden regression (Phase 1, step 5): every phoneme every existing language uses, rendered and
measured, stored as metrics, and compared on every later run. Fails loudly on drift.

Cases, one a phoneme, each in a host of its own (engine.py):
    pack read by eSpeak NG  every eSpeak NG phoneme its sounds.map maps to the module (the `@table:name`
                            lines that do not map to `-`), said by name: a consonant C as ['aCa], a
                            vowel V as [t'Vta]
    native pack             every phone the module gives a rule or a settings number
                            (inventory/languages.json), in the module's annotation `[.1aXa]
    and, from Phase 3 (DESIGN.md 10.4), every consonant again before a voiceless consonant and at
    the end before the pause, ['aCsa 'aC] (`[.1aXsa] `[.1aX]), case id `x|...`: between two vowels
    the next sound is always voiced, which is how defect X-1 went unseen.

For each case it keeps, per phone the engine sounded: what was asked of the synthesiser (frames:
analysis.requested) and what came out (sound: analysis.phone_metrics), the hash of the case's
frames and of its sound, and the phone sequence. Metrics, not audio.

    python docs/tts-extension/harness/golden.py --record [tags...]    write golden/<tag>.json.gz
    python docs/tts-extension/harness/golden.py [tags...]             compare; exit 1 on drift
    python docs/tts-extension/harness/golden.py --smoke                a few phonemes of a few packs
    python docs/tts-extension/harness/golden.py --record-new [tags...] compare, and add the cases the
                                    golden lacks, only if every case it has is unchanged

Drift: a case missing or new, a phone sequence changed, a requested value changed by more than
REQ_TOL, or a measured value by more than MEAS_TOL. A case whose frames and sound are both
byte-identical to the golden's passes at once; the sound is compared because the frames are
logged before the synthesiser runs, and a change inside it would leave them as they were.
An intended change is recorded again with --record and written down in DECISIONS.md (R8).
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysis as A   # noqa: E402
import engine as E     # noqa: E402

# Two goldens, never mixed (DESIGN.md 11.2): golden/ describes the modules in languages/;
# golden-staged/ the rebuilt modules staged under EVV_STAGE, and is the one that moves when a
# change to them is approved. --golden names another (the baseline proof compares the staged
# modules with golden/).
GOLDEN = os.path.join(HERE, 'golden-staged' if E.STAGE else 'golden')
ESPEAK_TYPES = {2: 'vowel', 3: 'liquid', 4: 'stop', 5: 'stop', 6: 'fricative', 7: 'fricative', 8: 'nasal'}

# A requested value is the engine's own integer: any change beyond rounding is drift.
REQ_TOL = dict(rel=0.005, abs=1.0)
# A measured value comes from numpy on this machine; another machine's floating point may differ
# a little. Hz: 2 % or 15 Hz; dB: 1; ms: 3; everything else 5 %.
MEAS_TOL = dict(hz=(0.02, 15.0), db=(0.0, 1.0), ms=(0.0, 3.0), other=(0.05, 0.0))

SMOKE = {'enus': 6, 'dede': 4, 'hi': 6, 'cmn': 4, 'sw': 4, 'ar': 4}

# The voiceless consonant a context case puts after C: the first of these the table has.
FOLLOW = ('s', 't', 'k', 'p')


def follower(names):
    for n in FOLLOW:
        if n in names:
            return n
    return None


def table_chain(name):
    """A phoneme table and every table it includes (eSpeak NG: `includes` is the parent's index + 1)."""
    import ipa
    tables = ipa.dump()
    by_index = {t['index']: t for t in tables.values()}
    out = []
    t = tables.get(name)
    while t is not None and t['table'] not in out:
        out.append(t['table'])
        t = by_index.get(t['includes'] - 1) if t['includes'] else None
    return out


def map_words(line):
    """The words of a sounds.map line: a comment begins at a word that starts with '#'
    (docs/SOUNDS.md), not at any '#': eSpeak NG names phonemes `d#`, `#a`."""
    out = []
    for w in line.split():
        if w.startswith('#'):
            break
        out.append(w)
    return out


def espeak_cases(p):
    """(cases, not covered). Every `@table:name` line of the pack's sounds.map that maps to something.

    A phoneme of the voice's own table chain is said as it stands; one the pack borrows from
    another table (ru `@en:A:`, for English words in Russian text) is said after eSpeak NG's
    table switch, `_^_en`, exactly as the front-end meets it. Its case id is `kind|name|table`.
    Anything that cannot be said is listed as not covered, with the reason, never dropped quietly.
    """
    import ipa
    own = ipa.voice_table(p)
    chain = set(table_chain(own))
    tables = ipa.dump()
    cases, seen, uncovered = [], set(), []
    with open(p.sounds_map, encoding='utf-8') as f:
        for line in f:
            w = map_words(line)
            if len(w) < 2 or not w[0].startswith('@') or w[1] == '-':
                continue
            tname, _, name = w[0][1:].partition(':')
            if not name:
                continue
            src = own if tname in chain or not tname else tname
            if (src, name) in seen:
                continue
            seen.add((src, name))
            if src not in tables:
                uncovered.append(dict(entry=w[0], reason='no eSpeak NG table %s' % src))
                continue
            phon = {ph['mnemonic']: ph for ph in tables[src]['phonemes']}
            if name not in phon:
                uncovered.append(dict(entry=w[0], reason='table %s has no phoneme %s' % (src, name)))
                continue
            kind = ESPEAK_TYPES.get(phon[name]['type'])
            if kind is None:
                continue          # stress marks, pauses and other non-segments: nothing to sound
            body = "t'%sta" % name if kind == 'vowel' else "'a%sa" % name
            if src == own:
                cases.append(('%s|%s' % (kind[0], name), 'espeak', body))
            else:
                cases.append(('%s|%s|%s' % (kind[0], name, src), 'espeak', '_^_%s %s' % (src, body)))
            if kind == 'vowel':
                continue
            fol = follower(set().union(*({ph['mnemonic'] for ph in tables[t]['phonemes']}
                                         for t in table_chain(src) if t in tables)))
            if fol is None:
                uncovered.append(dict(entry=w[0], reason='context case: table %s has none of %s' % (src, ' '.join(FOLLOW))))
                continue
            body = "'a%s%sa 'a%s" % (name, fol, name)
            if src == own:
                cases.append(('x|%s' % name, 'espeak', body))
            else:
                cases.append(('x|%s|%s' % (name, src), 'espeak', '_^_%s %s' % (src, body)))
    return cases, uncovered


# Phones whose names hold ':' or '~' are spoken as text if written plainly (`[.1aE:a] lasts 5.6 s);
# in single quotes they are the phone (`[.1a'E:'a], DECISIONS.md D30), which is how they are said
# from Phase 3. These ordinary words that contain them stay as cases of their own.
TEXT_CASES = {
    'dede': ['Käse.', 'Mädchen.', 'Restaurant.', 'Bassin.', 'Parfum.', 'Balkon.'],
    'frfr': ['enfant.', 'vin.', 'bon.', 'brun.', 'un.'],
    'frca': ['enfant.', 'vin.', 'bon.', 'brun.', 'un.'],
}


def is_vowel(p, name):
    """By analysis.phone_class, which also knows the modules without a phone-to-IPA table
    (frca, plpl, jajp: analysis.CLASS_TABLE, JAJP_CLASS)."""
    # E: a~ OE~ ...: in these modules ':' and '~' mark only vowels (long, nasal), and the
    # phone-to-IPA table does not list them
    return ':' in name or '~' in name or A.phone_class(None, name, p.phone_module) == 'vowel'


def native_cases(p):
    """Every phone the module declares (inventory/languages.json): a vowel V in `[.1tVt], anything
    else X in `[.1aXa] (a vowel between two a's is measured as the a's: Phase 1, D17); see TEXT_CASES."""
    path = os.path.join(E.ROOT, 'docs', 'tts-extension', 'inventory', 'languages.json')
    with open(path, encoding='utf-8') as f:
        q = {x['tag']: x for x in json.load(f)['packs']}[p.module_tag]
    names = [ph['name'] for ph in q['phonemes'] if ph['name'] and ph['name'] != '#']
    carrier = 'a' if 'a' in names else names[0]
    def w(n):
        return "'%s'" % n if ':' in n or '~' in n else n
    cases = [('m|%s' % n, 'module', ('`[.1t%st]' % w(n)) if is_vowel(p, n) else '`[.1%s%s%s]' % (carrier, w(n), carrier))
             for n in names]
    fol = follower(names)
    if fol:
        cases += [('x|%s' % n, 'module', '`[.1%s%s%s%s] `[.1%s%s]' % (carrier, w(n), fol, carrier, carrier, w(n)))
                  for n in names if not is_vowel(p, n)]
    cases += [('t|%s' % w.rstrip('.'), 'text', w) for w in TEXT_CASES.get(p.tag, [])]
    return cases


def cases_for(tag):
    """(cases, not covered) for a pack."""
    p = E.pack(tag)
    return espeak_cases(p) if p.kind == 'espeak' else (native_cases(p), native_uncovered(p))


def native_uncovered(p):
    return []       # every phone the module declares has a case (names with ':' or '~' quoted)


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) and v is not None and np.isfinite(v) else None


def measure_case(r, phone_module):
    x, rate = E.read_wav(r['wav'])
    t = E.frame_times(r['frames'])
    phones = []
    for ph in r['phones']:
        cls = A.phone_class(ph.get('record'), ph['name'], phone_module)
        if cls == 'silence':
            phones.append(dict(name=ph['name'], cls=cls, start_ms=ph['start_ms'], end_ms=ph['end_ms']))
            continue
        req = A.requested(r['frames'], t, ph)
        meas = A.phone_metrics(x, rate, ph, cls)
        meas = {k: (round(v, 2) if _num(v) is not None else None) for k, v in meas.items() if not isinstance(v, list)}
        phones.append(dict(name=ph['name'], meant=ph.get('meant'), sound=ph.get('sound'), tone=ph.get('tone'),
                           cls=cls, start_ms=ph['start_ms'], end_ms=ph['end_ms'],
                           req={k: (float(v) if _num(v) is not None else v) for k, v in req.items()}, meas=meas))
    return dict(input=r['input']['said'] if r['input']['kind'] == 'module' else r['input']['text'],
                kind=r['input']['kind'], case_ms=r['case_ms'], attempts=r['attempts'],
                segmentation=r['segmentation'],
                frames_sha256=hashlib.sha256(np.ascontiguousarray(r['frames']).tobytes()).hexdigest(),
                wav_sha256=r['wav_sha256'], phones=phones)


def known_ids(folder, tag):
    """The case ids a golden folder holds for a pack (empty if it has none)."""
    import gzip
    path = os.path.join(folder, '%s.json.gz' % tag)
    if not os.path.exists(path):
        return set()
    with open(path, 'rb') as f:
        return set(json.loads(gzip.decompress(f.read()).decode('utf-8'))['cases'])


def run_pack(tag, limit=None, jobs=2, skip_from=None):
    p = E.pack(tag)
    cases, uncovered = cases_for(tag)
    if limit:
        cases = cases[:limit]
    if skip_from:
        skip = known_ids(skip_from, tag)
        cases = [c for c in cases if c[0] not in skip]
    out, errors = {}, {}
    t0 = time.time()
    try:
        rendered = E.render(tag, cases, jobs=jobs, work=os.path.join(E.WORK, 'golden', tag))
    except Exception:
        rendered = []
        for c in cases:      # one at a time, so that one bad case does not hide the others
            try:
                rendered += E.render(tag, [c], jobs=1, work=os.path.join(E.WORK, 'golden', tag))
            except Exception as e:      # whatever it is, it is this case's, and it is reported
                errors[c[0]] = '%s: %s' % (type(e).__name__, e)
    diag = {}       # C1: what the front-end and the accent layer reported, over all the cases
    for r in rendered:
        for d in r.get('diag', []):
            k = '	'.join((d['source'], d['level'], d['kind'], d['detail']))
            diag[k] = diag.get(k, 0) + d['count']
        try:
            out[r['id']] = measure_case(r, p.phone_module)
        except Exception as e:     # a measurement bug must not pass for a clean run
            errors[r['id']] = 'measuring failed: %r' % e
    return dict(tag=tag, kind=p.kind, module=p.module_tag, phone_module=p.phone_module, preset=1, bits=64,
                cases=out, errors=errors, not_covered=uncovered, seconds=round(time.time() - t0, 1), diag=diag)


def _close(a, b, key):
    if a is None or b is None:
        return a is None and b is None
    if key.endswith('_hz') or key in ('centroid_hz', 'sd_hz'):
        rel, ab = MEAS_TOL['hz']
    elif key.endswith('_db'):
        rel, ab = MEAS_TOL['db']
    elif key.endswith('_ms'):
        rel, ab = MEAS_TOL['ms']
    else:
        rel, ab = MEAS_TOL['other']
    return abs(a - b) <= max(rel * abs(b), ab)


def compare(gold, now):
    """[(case, severity, message)], severity 'FAIL' or 'note'."""
    out = []
    for cid in sorted(set(gold['cases']) | set(now['cases']) | set(now['errors'])):
        g, n = gold['cases'].get(cid), now['cases'].get(cid)
        if cid in now['errors']:
            out.append((cid, 'FAIL', 'could not be rendered: %s' % now['errors'][cid]))
            continue
        if g is None:
            out.append((cid, 'FAIL', 'new case (not in the golden)'))
            continue
        if n is None:
            out.append((cid, 'FAIL', 'missing case (in the golden, not rendered now)'))
            continue
        # The frames are logged before the synthesiser runs, so the sound is compared too: a change
        # in the synthesiser itself (resonators, sources, noise) leaves the frames as they were.
        if g['frames_sha256'] == n['frames_sha256'] and g['wav_sha256'] == n['wav_sha256']:
            continue
        gs, ns = [p['name'] for p in g['phones']], [p['name'] for p in n['phones']]
        if gs != ns:
            out.append((cid, 'FAIL', 'phones %s, golden %s' % (' '.join(ns), ' '.join(gs))))
            continue
        msgs = []
        for gp, np_ in zip(g['phones'], n['phones']):
            for k, gv in (gp.get('req') or {}).items():
                nv = (np_.get('req') or {}).get(k)
                if isinstance(gv, (int, float)) and isinstance(nv, (int, float)):
                    if abs(nv - gv) > max(REQ_TOL['rel'] * abs(gv), REQ_TOL['abs']):
                        msgs.append('%s requested %s %g -> %g' % (gp['name'], k, gv, nv))
            for k, gv in (gp.get('meas') or {}).items():
                nv = (np_.get('meas') or {}).get(k)
                if not _close(nv, gv, k):
                    msgs.append('%s measured %s %s -> %s' % (gp['name'], k, gv, nv))
        what = 'frames' if g['frames_sha256'] != n['frames_sha256'] else 'sound (same frames)'
        if msgs:
            out.append((cid, 'FAIL', '%s changed: ' % what + '; '.join(msgs[:6]) +
                        (' (+%d more)' % (len(msgs) - 6) if len(msgs) > 6 else '')))
        else:
            out.append((cid, 'note', '%s changed, every value within tolerance' % what))
    return out


def all_tags():
    return [t for t, p in E.packs().items() if p.kind != 'template']


def golden_path(tag):
    return os.path.join(GOLDEN, '%s.json.gz' % tag)


def write_golden(tag, r):
    """Compact JSON, gzip with no timestamp: the same data gives the same bytes (43 MB as text, 4 MB so)."""
    import gzip
    data = json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    with open(golden_path(tag), 'wb') as f:
        f.write(gzip.compress(data, 9, mtime=0))


def read_golden(tag):
    import gzip
    with open(golden_path(tag), 'rb') as f:
        return json.loads(gzip.decompress(f.read()).decode('utf-8'))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('tags', nargs='*')
    ap.add_argument('--record', action='store_true', help='write the golden files instead of comparing')
    ap.add_argument('--record-new', action='store_true',
                    help='compare, and add the cases the golden lacks to it if every case it has is unchanged')
    ap.add_argument('--smoke', action='store_true', help='a few phonemes of a few packs (under a minute)')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 4) // 2))
    ap.add_argument('--golden', help='the golden folder (default: golden/, or golden-staged/ under EVV_STAGE)')
    ap.add_argument('--only-missing-from', metavar='FOLDER',
                    help='render only the cases that golden folder lacks, and compare only those')
    a = ap.parse_args()
    global GOLDEN
    if a.golden:
        GOLDEN = os.path.abspath(a.golden)
    print('modules: %s; golden: %s' % ('staged in %s, else shipped' % E.STAGE if E.STAGE else 'shipped (languages/)',
                                      os.path.relpath(GOLDEN, HERE)), flush=True)
    if a.smoke:
        plan = list(SMOKE.items())
    else:
        plan = [(t, None) for t in (a.tags or all_tags())]
    t0 = time.time()
    results = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:
        skip_from = os.path.abspath(a.only_missing_from) if a.only_missing_from else None
        futs = {ex.submit(run_pack, tag, limit, 2, skip_from): tag for tag, limit in plan}
        for f in concurrent.futures.as_completed(futs):
            try:
                r = f.result()
            except Exception as e:     # a pack that crashed is a failure, not the end of the run
                tag = futs[f]
                r = dict(tag=tag, kind=E.pack(tag).kind, cases={}, errors={'*': '%s: %s' % (type(e).__name__, e)}, seconds=0)
            results[r['tag']] = r
            print('%-8s %3d cases %2d errors %2d not covered %6.1f s' % (r['tag'], len(r['cases']), len(r['errors']),
                                                                    len(r.get('not_covered', [])), r['seconds']), flush=True)
    # C1: the count of what was reported lost on the way, beside the golden, never inside it
    if not a.tags and not a.only_missing_from and not getattr(a, 'smoke', False):
        out = os.path.join(HERE, 'results', 'diag-golden%s.json' % ('-staged' if E.STAGE else ''))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({t: r.pop('diag', {}) for t, r in sorted(results.items())}, f, ensure_ascii=False, indent=1,
                      sort_keys=True)
    for r in results.values():
        r.pop('diag', None)
    fails = notes = 0
    if a.record:
        os.makedirs(GOLDEN, exist_ok=True)
        for tag, r in sorted(results.items()):
            if r['errors']:
                print('NOT RECORDED %s: %d cases could not be rendered: %s' % (tag, len(r['errors']), list(r['errors'].items())[:3]))
                fails += 1
                continue
            write_golden(tag, r)
        print('recorded %d packs in %.0f s; %d not recorded' % (len(results) - fails, time.time() - t0, fails))
        sys.exit(1 if fails else 0)
    added = 0
    for tag, r in sorted(results.items()):
        if not os.path.exists(golden_path(tag)):
            print('FAIL %s: no golden file (run --record)' % tag)
            fails += 1
            continue
        gold = read_golden(tag)
        if a.smoke or a.only_missing_from:
            gold['cases'] = {k: v for k, v in gold['cases'].items() if k in r['cases'] or k in r['errors']}
        found = compare(gold, r)
        new = [cid for cid, sev, msg in found if sev == 'FAIL' and msg == 'new case (not in the golden)']
        if a.record_new and new and len(new) == sum(sev == 'FAIL' for _c, sev, _m in found):
            # Every case the golden has is unchanged: the new ones join it, the old ones stay as they were.
            if a.only_missing_from:
                gold = read_golden(tag)     # the whole of it, not the part compared
            for cid in new:
                gold['cases'][cid] = r['cases'][cid]
            gold['not_covered'] = r.get('not_covered', gold.get('not_covered', []))
            write_golden(tag, gold)
            print('ADDED %s: %d new cases; the %d it had are %s' % (tag, len(new), len(gold['cases']) - len(new),
                  'not rendered again (--only-missing-from)' if a.only_missing_from else 'unchanged'))
            added += len(new)
            found = [f for f in found if f[0] not in new]
        for cid, sev, msg in found:
            print('%s %s %s: %s' % (sev, tag, cid, msg))
            fails += sev == 'FAIL'
            notes += sev == 'note'
    if a.record_new:
        print('record-new: %d cases added' % added)
    n = sum(len(r['cases']) + len(r['errors']) for r in results.values())
    print('golden: %d packs, %d cases, %d FAILED, %d changed within tolerance, %.0f s'
          % (len(results), n, fails, notes, time.time() - t0))
    if fails:
        print('*** GOLDEN REGRESSION FAILED: the engine or its data changed. If intended, record again '
              'with --record and write the change down in DECISIONS.md. ***')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
