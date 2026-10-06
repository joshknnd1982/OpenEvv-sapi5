"""Check A3 (DESIGN.md 10.1): did what was meant to be voiceless or silent stay so?

Each context case of a pack (golden.py, the `x|...` cases: every consonant before a voiceless
consonant and at the end before the pause) is rendered twice: with the pack's sounds.map, and with
the same map with every `sound` definition emptied (`sound s11`, no keys), which is what the module
gives by itself. A phone is held to A3 when it is a pause, or when it is not a vowel, its own sound
definition does not ask for voice (`voi=1`), and the module by itself voices less than half of its
time. It passes when the pack's definitions add no voiced
time there: voiced time with the map is at most the module's own, plus one frame; when a definition
lengthens the phone, the module's own voiced time is scaled up with it (never down: a shortened
sound keeps the voicing it had at its edge, which the definitions did not add). Friction lost in those phones is reported beside it, not judged.

    python docs/tts-extension/harness/a3.py [tags...]      every pack read by eSpeak NG by default

Writes results/a3.json (results/a3-staged.json under EVV_STAGE). Native packs carry no markup, so
the layer does nothing to them and A3 holds by construction; they are not run.
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E     # noqa: E402
import golden as G     # noqa: E402

RESULTS = os.path.join(HERE, 'results')
HELD_BELOW = 0.5        # a non-vowel the module voices for less than this share of its time


def bare_map(p, work):
    """The pack's map with every sound definition emptied: the module by itself."""
    with open(p.sounds_map, encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'(?m)^sound (\S+)[^\n]*$', r'sound \1', text)
    os.makedirs(work, exist_ok=True)
    path = os.path.join(work, 'bare.map')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return path


def definitions(p):
    """sound id -> {key: value} of the pack's sounds.map."""
    out = {}
    with open(p.sounds_map, encoding='utf-8') as f:
        for line in f:
            w = G.map_words(line)
            if len(w) >= 2 and w[0] == 'sound':
                out[w[1]] = dict(kv.split('=', 1) for kv in w[2:] if '=' in kv)
    return out


def spans(r):
    """Per phone: (name, class, length ms, voiced ms, noisy ms, step ms)."""
    fr = r['frames']
    t = E.frame_times(fr)
    out = []
    for ph in r['phones']:
        idx = np.nonzero((t >= ph['start_ms']) & (t < ph['end_ms']))[0]
        steps = fr[idx, E.P['step']]
        voiced = fr[idx, E.P['av']] > 0
        noisy = (fr[idx, E.P['af']] > 0) | (fr[idx, E.P['ah']] > 0)
        cls = 'silence' if (ph.get('record') or [None])[0] == 0 or ph['name'] in ('#', '_', '-') else \
            ('vowel' if (ph.get('record') or [None])[0] == 1 else 'other')
        out.append((ph['name'], cls, float(steps.sum()), float(steps[voiced].sum()), float(steps[noisy].sum()),
                    float(steps.max()) if len(steps) else 5.0))
    return out


def run_pack(tag, jobs=2, skip_from=None):
    p = E.pack(tag)
    cases = [c for c in G.cases_for(tag)[0] if c[0].startswith('x|')]
    if skip_from:
        skip = G.known_ids(skip_from, tag)
        cases = [c for c in cases if c[0] not in skip]
    if not cases:
        return dict(tag=tag, module=p.module_tag, cases=0, held=0, failures=[], mismatched=[], errors={},
                    friction_lost=0, seconds=0)
    work = os.path.join(E.WORK, 'a3', tag)
    t0 = time.time()
    out = dict(tag=tag, module=p.module_tag, cases=len(cases), held=0, failures=[], mismatched=[], errors={},
               friction_lost=0)
    try:
        with_map = {r['id']: r for r in E.render(tag, cases, jobs=jobs, work=os.path.join(work, 'map'))}
        bare = {r['id']: r for r in E.render(tag, cases, jobs=jobs, work=os.path.join(work, 'bare'),
                                             map_path=bare_map(p, work))}
    except Exception as e:      # reported as this pack's, never a clean pass
        out['errors']['*'] = '%s: %s' % (type(e).__name__, e)
        return out
    defs = definitions(p)
    for cid, _kind, text in cases:
        a, b = spans(with_map[cid]), spans(bare[cid])
        if [x[0] for x in a] != [x[0] for x in b]:
            out['mismatched'].append(dict(case=cid, map=' '.join(x[0] for x in a), bare=' '.join(x[0] for x in b)))
            continue
        for i, (wa, wb) in enumerate(zip(a, b)):
            name, cls, len_a, v_a, n_a, step = wa
            _n, _c, len_b, v_b, n_b, _s = wb
            own = defs.get(with_map[cid]['phones'][i].get('sound'), {})
            if not (cls == 'silence' or (cls != 'vowel' and own.get('voi') != '1' and len_b > 0
                                         and v_b < HELD_BELOW * len_b)):
                continue
            out['held'] += 1
            allowed = v_b * max(1.0, len_a / len_b if len_b > 0 else 1.0) + step
            if n_a < n_b * (len_a / len_b if len_b > 0 else 1.0) - step:
                out['friction_lost'] += 1
            if v_a > allowed:
                before = with_map[cid]['phones'][i - 1].get('sound') if i else None
                keys = defs.get(before, {})
                out['failures'].append(dict(case=cid, input=text, phone=i, name=name,
                                            after_release_key=' '.join(k for k in ('vot', 'brth') if k in keys) or None,
                                            voiced_ms=v_a, module_voiced_ms=v_b, length_ms=len_a,
                                            module_length_ms=len_b, noisy_ms=n_a, module_noisy_ms=n_b,
                                            sound=with_map[cid]['phones'][i].get('sound'), before=before))
    out['seconds'] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('tags', nargs='*')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 4) // 2))
    ap.add_argument('--only-missing-from', metavar='FOLDER',
                    help='only the x| cases that golden folder lacks; results go to results/a3[-staged]-new.json')
    a = ap.parse_args()
    skip_from = os.path.abspath(a.only_missing_from) if a.only_missing_from else None
    tags = a.tags or [t for t, p in E.packs().items() if p.kind == 'espeak']
    print('modules: %s' % ('staged in %s, else shipped' % E.STAGE if E.STAGE else 'shipped (languages/)'), flush=True)
    results = {}
    t0 = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_pack, t, 2, skip_from): t for t in tags}
        for f in concurrent.futures.as_completed(futs):
            try:
                r = f.result()
            except Exception as e:
                r = dict(tag=futs[f], cases=0, held=0, failures=[], mismatched=[], friction_lost=0,
                         errors={'*': '%s: %s' % (type(e).__name__, e)})
            results[r['tag']] = r
            print('%-12s %-5s %4d cases %5d phones held %4d FAIL (%d after vot/brth) %3d not comparable %4d friction lost %s'
                  % (r['tag'], 'PASS' if not r['failures'] and not r['errors'] else 'FAIL', r['cases'], r['held'],
                     len(r['failures']), sum(1 for x in r['failures'] if x.get('after_release_key')),
                     len(r['mismatched']), r['friction_lost'],
                     ('errors: %s' % r['errors']) if r['errors'] else ''), flush=True)
    path = os.path.join(RESULTS, ('a3-staged' if E.STAGE else 'a3') + ('-new' if skip_from else '') + '.json')
    old = {}
    if a.tags and os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            old = json.load(f)
    old.update(results)
    os.makedirs(RESULTS, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(old, f, ensure_ascii=False, indent=1, sort_keys=True)
    bad = [t for t, r in results.items() if r['failures'] or r['errors']]
    print('A3: %d packs, %d pass, %d fail; %d phones held, %d failed, %d cases not comparable; %.0f s -> %s'
          % (len(results), len(results) - len(bad), len(bad), sum(r['held'] for r in results.values()),
             sum(len(r['failures']) for r in results.values()),
             sum(len(r['mismatched']) for r in results.values()), time.time() - t0, os.path.relpath(path, HERE)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
