"""Coverage of the IPA chart by the master table (DESIGN.md 1 and 3.1; playbook Phase 4). MIT licence.

    python engine/ipa/coverage.py [--template dedx] [--quiet]

Driven by the checklist (docs/tts-extension/inventory/IPA_CHECKLIST.json). Every checklist symbol
must have an entry of its own under the same id; the table may hold nothing the checklist lacks
unless it is tier B or C. For each symbol it prints: the state (mapped / composed / created /
MISSING / BLOCKED), how this engine says it (the carrier phone and its keys, a modifier's
transform, a tone's levels), whether a rendered proof exists and passed (ipa/proofs/<id>.json,
written by sweep.py), the provenance of its specification's values, its level and whether it is
approximate. Then the counts to compare with Phase 0's exact count, and the secondary metric, the
Unicode net (DESIGN.md 1), when its data files are present.

Exit 1 if a checklist symbol has no entry or an entry has no checklist symbol; the project is
complete only when every checklist entry is mapped, composed or created with a proof (R19e, f).
"""

import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import table as T  # noqa: E402

CHECKLIST = os.path.join(T.ROOT, 'docs', 'tts-extension', 'inventory', 'IPA_CHECKLIST.json')
PROOFS = os.path.join(T.ROOT, 'ipa', 'proofs')
UNICODE = os.path.join(T.ROOT, 'docs', 'tts-extension', 'inventory', 'unicode')
NET = os.path.join(T.IPA, 'unicode_net.toml')
DONE = ('mapped', 'composed', 'created')
STATES = ['mapped', 'composed', 'created', 'MISSING', 'BLOCKED', 'no entry']


def tags(node, out):
    """Count the provenance tags of every value under a node of an entry."""
    if isinstance(node, dict):
        if 'tag' in node and ({'v', 'add', 'scale', 'set', 'toward'} & set(node)):
            out[node['tag']] += 1
        else:
            for v in node.values():
                tags(v, out)
    elif isinstance(node, list):
        for v in node:
            tags(v, out)
    return out


def recipe(t, sid, template):
    e = t.sounds[sid]
    if e['kind'] == 'base':
        import adapter as AD
        try:
            r = AD.realize(t, sid, template, (AD.loop_proof(sid) or {}).get('carrier_measured'))
        except Exception as x:  # noqa: BLE001  (shown, not hidden)
            return 'cannot realise: %s' % x
        keys = ' '.join('%s=%s' % kv for kv in sorted(r['keys'].items()))
        sub = ' SUBSTITUTE' if r['distance'] and not r['keys'] else ''
        return '%s%s%s' % (r['carrier'], ('{%s}' % keys) if keys else '', sub)
    if e['kind'] == 'modifier':
        ops = []
        for cls, tr in (e.get('transform') or {}).items():
            import adapter as AD
            o, _ = AD.mod_ops(t, sid, cls)
            ops.append('%s:%s' % (cls[0], ','.join(('%s~%g:%g' % (op[0], op[2][0], op[2][1])) if op[1] == '~'
                                                   else '%s%s%g' % op for op in (o or []))))
        return 'mod ' + ' '.join(ops) if ops else 'no transform'
    if e['kind'] == 'tone':
        if e.get('levels'):
            return 'levels ' + ''.join(str(x) for x in e['levels'])
        return 'register %s' % e.get('register') if e.get('register') else 'slope %s' % e.get('slope')
    return e['kind']


def proof_of(sid):
    path = os.path.join(PROOFS, sid + '.json')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def unicode_net(t, checklist):
    """The secondary metric (DESIGN.md 1): every assigned code point of the ten blocks in exactly
    one class. Needs Unicode's own UnicodeData.txt and Blocks.txt (Python 3.10 knows only
    Unicode 13) and ipa/unicode_net.toml (the classes)."""
    ud, bl = os.path.join(UNICODE, 'UnicodeData.txt'), os.path.join(UNICODE, 'Blocks.txt')
    if not (os.path.exists(ud) and os.path.exists(bl)):
        return 'Unicode net: not run: %s and Blocks.txt are not here (a download from unicode.org)' % (
            os.path.relpath(ud, T.ROOT))
    blocks = {}
    with open(bl, encoding='utf-8') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if ';' in line:
                rng, name = line.split(';')
                a, b = (int(x, 16) for x in rng.split('..'))
                blocks[name.strip()] = (a, b)
    wanted = ['IPA Extensions', 'Spacing Modifier Letters', 'Combining Diacritical Marks',
              'Combining Diacritical Marks Extended', 'Combining Diacritical Marks Supplement', 'Phonetic Extensions',
              'Phonetic Extensions Supplement', 'Modifier Tone Letters', 'Latin Extended-F', 'Latin Extended-G']
    assigned = collections.Counter()
    cps = []
    with open(ud, encoding='utf-8') as f:
        for line in f:
            cp = int(line.split(';')[0], 16)
            for name in wanted:
                a, b = blocks.get(name, (1, 0))
                if a <= cp <= b:
                    assigned[name] += 1
                    cps.append(cp)
    if not os.path.exists(NET):
        return 'Unicode net: %d assigned code points in the ten blocks; not classified yet (%s absent)' % (
            len(cps), os.path.relpath(NET, T.ROOT))
    import tomli
    with open(NET, 'rb') as f:
        net = tomli.load(f)
    cls = {}
    for c, ranges in net.get('class', {}).items():
        for r in ranges:
            a, _, b = r.partition('..')
            for cp in range(int(a[2:], 16), int((b or a)[2:], 16) + 1):
                cls[cp] = c
    known = sum(1 for cp in cps if cp in cls)
    by = collections.Counter(cls.get(cp, 'unknown') for cp in cps)
    return 'Unicode net: %d of %d classified; %s' % (known, len(cps), ', '.join('%s %d' % kv for kv in sorted(by.items())))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--template', default='dedx')
    ap.add_argument('--quiet', action='store_true', help='the counts only')
    a = ap.parse_args()
    t = T.load()
    with open(CHECKLIST, encoding='utf-8') as f:
        cl = json.load(f)['symbols']
    checklist = {e['id']: e for e in cl}
    missing = sorted(set(checklist) - set(t.sounds))
    extra = sorted(i for i in set(t.sounds) - set(checklist) if t.sounds[i].get('tier', 'A') == 'A')
    blocked = sorted(i for i, e in t.sounds.items() if e.get('state') == 'BLOCKED')
    if blocked:
        print('BLOCKED: %s' % ', '.join('%s %s' % (i, t.sounds[i]['ipa']) for i in blocked))
    by = collections.defaultdict(collections.Counter)
    rendered = measured = passed_proof = approx = 0
    prov = collections.Counter()
    rows = []
    for c in cl:
        sid = c['id']
        e = t.sounds.get(sid)
        st = e.get('state') if e else 'no entry'
        by[c['section']][st] += 1
        pr = proof_of(sid)
        has_r = bool(pr and pr.get('cases'))
        has_m = bool(pr and pr.get('summary'))
        rendered += has_r
        measured += has_r and has_m
        passed_proof += bool(pr and pr.get('passed'))
        tg = tags({k: e.get(k) for k in ('spec', 'transform', 'realization')}, collections.Counter()) if e else {}
        prov.update(tg)
        approx += bool(e and e.get('approximate'))
        rows.append((c['n'], c['symbol'], sid, c['section'], st, recipe(t, sid, a.template) if e else '-',
                     'pass' if pr and pr.get('passed') else ('fail' if has_r else '-'),
                     ' '.join('%s %d' % kv for kv in sorted(tg.items())) or '-', e.get('level') if e else '-',
                     'approx' if e and e.get('approximate') else ''))
    if not a.quiet:
        print('%-3s %-4s %-12s %-15s %-8s %-6s %-2s %-40s %s' % ('n', 'sym', 'id', 'section', 'state', 'proof', 'lv',
                                                                'provenance', 'how this engine says it'))
        for n, sym, sid, sec, st, rec, pf, pv, lv, ap in rows:
            print('%-3s %-4s %-12s %-15s %-8s %-6s %-2s %-40s %s %s' % (n, sym, sid, sec, st, pf, lv, pv[:40], rec, ap))
        print()
    print('%-16s %s %6s' % ('section', ' '.join('%9s' % s for s in STATES), 'all'))
    total = collections.Counter()
    for sec, cnt in by.items():
        total.update(cnt)
        print('%-16s %s %6d' % (sec, ' '.join('%9d' % cnt[s] for s in STATES), sum(cnt.values())))
    print('%-16s %s %6d' % ('all', ' '.join('%9d' % total[s] for s in STATES), sum(total.values())))
    done = sum(total[s] for s in DONE)
    print('coverage: %d of %d checklist entries done (mapped %d, composed %d, created %d); MISSING %d, BLOCKED %d; '
          'rendered and measured %d (proof passed %d); approximate %d' % (
              done, len(checklist), total['mapped'], total['composed'], total['created'], total['MISSING'],
              total['BLOCKED'], measured, passed_proof, approx))
    print('provenance of every value in the table: %s' % (', '.join('%s %d' % kv for kv in sorted(prov.items())) or 'none'))
    print('%d without an entry; %d entries not on the checklist' % (len(missing), len(extra)))
    for i in missing:
        print('  no entry: %s %s' % (i, checklist[i]['symbol']))
    for i in extra:
        print('  not on the checklist: %s %s' % (i, t.sounds[i]['ipa']))
    stale = [sid for sid, e in t.sounds.items() if e.get('state') not in ('MISSING', None)
             and not (proof_of(sid) or {}).get('passed')]
    print('state against proof: %s' % ('every entry that is not MISSING has a passing proof' if not stale else
                                      'NOT PROVED NOW: ' + ', '.join('%s %s' % (i, t.sounds[i]['ipa']) for i in stale)))
    print(unicode_net(t, checklist))
    return 1 if missing or extra or stale else 0


if __name__ == '__main__':
    sys.exit(main())
