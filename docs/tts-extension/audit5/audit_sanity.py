# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 5 audit, step 7: can a wrong sound pass the harness?

Each case plants a fault in the realised map the sweep says an entry with (a key changed on the
entry's sound line, or its carrier swapped) and runs the sweep's own say_entry and the B2
contrasts on it. A case that still passes is a hole in the harness.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'ipa'))
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
os.environ.setdefault('EVV_STAGE', r'C:\Users\joshk\OpenEvvBuild-ttsext\stage-dev')
import table as T  # noqa: E402
import sweep as SW  # noqa: E402
import engine as E  # noqa: E402

SW.SWEEP_WORK = os.path.join(E.WORK, 'audit5sanity')
os.makedirs(SW.SWEEP_WORK, exist_ok=True)
t = T.load()

# (name, entry id, map id, sound-line edit {key: value or None to drop}, carrier swap or None)
CASES = [
    ('s said with voice (voi=1)', 'U+0073', 'u0073', {'voi': 1}, None),
    ('z said without voice (voi=0) [control]', 'U+007A', 'u007a', {'voi': 0}, None),
    ('a whispered (voi=0 whisper=44)', 'U+0061', 'u0061', {'voi': 0, 'whisper': 44}, None),
    ('a 30 dB down (av=-30 ah=-30)', 'U+0061', 'u0061', {'av': -30, 'ah': -30}, None),
    ('l said on j (no lateral) with l keys', 'U+006C', 'u006c', {}, 'j'),
    ('m said on b (no nasal) with m keys', 'U+006D', 'u006d', {}, 'b'),
    ('p aspirated (vot=80) [control]', 'U+0070', 'u0070', {'vot': 80}, None),
    ('r with no trill (trate tapms tdepth dropped) [control]', 'U+0072', 'u0072', {'trate': None, 'tapms': None, 'tdepth': None}, None),
    ('ʃ with s noise (a4=50 a5=30 f3=111 f4=135) [control]', 'U+0283', 'u0283', {'a2': 0, 'a3': 0, 'a4': 50, 'a5': 30, 'f3': 111, 'f4': 135}, None),
    ('n said on d (no nasal) with n keys', 'U+006E', 'u006e', {}, 'd'),
    ('i said with u keys', 'U+0069', 'u0069', 'u0075', None),
    ('t with no burst (said on n) [control]', 'U+0074', 'u0074', {}, 'n'),
]
ONLY = sys.argv[1:]            # run only the cases whose name holds one of these strings
if ONLY:
    CASES = [c for c in CASES if any(x in c[0] for x in ONLY)]
orig_test_map = SW.test_map
plant = {}


def patched_test_map(pack, template, work):
    p, out = orig_test_map(pack, template, work)
    if plant:
        with open(out, encoding='utf-8') as f:
            lines = f.read().split('\n')
        mid, edit, carrier = plant['mid'], plant['edit'], plant['carrier']
        for i, line in enumerate(lines):
            if line.startswith('sound %s ' % mid):
                if isinstance(edit, str):
                    # take another id's keys whole
                    other = [l for l in lines if l.startswith('sound %s ' % edit)][0]
                    keys = other.split('#')[0].split()[2:]
                else:
                    keys = line.split('#')[0].split()[2:]
                    kv = dict(k.split('=') for k in keys)
                    for k, v in edit.items():
                        if v is None:
                            kv.pop(k, None)
                        else:
                            kv[k] = str(v)
                    keys = ['%s=%s' % x for x in sorted(kv.items())]
                lines[i] = 'sound %s %s' % (mid, ' '.join(keys))
                plant['line'] = lines[i]
            elif carrier and re.match(r'^\S+\s+\S+=%s$' % mid, line):
                lines[i] = re.sub(r'\s(\S+)=%s$' % mid, ' %s=%s' % (carrier, mid), line)
                plant['letter'] = lines[i]
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines))
    return p, out


SW.test_map = patched_test_map


def b2(sid, res):
    out = {}
    for c in (t.sounds[sid].get('tests') or {}).get('contrast', []) or []:
        pf = os.path.join(ROOT, 'ipa', 'proofs', T.file_id(c['with']) + '.json')
        theirs = (json.load(open(pf, encoding='utf-8')).get('summary') or {}).get(c['measure']) if os.path.exists(pf) else None
        mine = (res.get('summary') or {}).get(c['measure'])
        ok, d = SW.contrast_ok(c['measure'], mine, theirs, c['sign'])
        out['%s vs %s' % (c['measure'], t.sounds[c['with']]['ipa'])] = dict(mine=mine, theirs=theirs, diff=d, ok=ok)
    return out


report = []
for name, sid, mid, edit, carrier in CASES:
    plant.clear()
    plant.update(mid=mid, edit=edit, carrier=carrier)
    try:
        res = SW.say_entry(t, sid, 'dedx', 'hi')
    except SystemExit as x:
        report.append(dict(case=name, error=str(x)))
        print('%-55s FRONT-END FAILED %s' % (name, x))
        continue
    contrasts = b2(sid, res)
    a0, a1, a2, b3 = res['A0']['passed'], res['A1']['passed'], res['A2']['passed'], res['B3']['passed']
    b2ok = all(v['ok'] for v in contrasts.values())
    passed = a0 and a1 and a2 and b3 and b2ok
    failed = [k for k, v in (('A0', res['A0']), ('A1', res['A1']), ('A2', res['A2']), ('B3', res['B3'])) if not v['passed']]
    failed += ['B2 ' + k for k, v in contrasts.items() if not v['ok']]
    b3_bad = {k: v for k, v in res['B3'].get('targets', {}).items() if not v.get('within')}
    print('%-55s %s  failed: %s  B3 misses: %s  line: %s %s' % (
        name, 'PASSES (hole)' if passed else 'caught', failed, {k: (v.get('target'), v.get('measured')) for k, v in b3_bad.items()},
        plant.get('line', '')[:80], plant.get('letter', '')))
    sys.stdout.flush()
    report.append(dict(case=name, id=sid, passed=passed, failed=failed, b3_misses=b3_bad, contrasts=contrasts,
                       summary=res.get('summary'), line=plant.get('line'), letter=plant.get('letter'),
                       A1=res['A1'], A2={k: res['A2'].get(k) for k in ('passed', 'note', 'a2_rate', 'problems')}))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audit_sanity%s.json' % ('_%d' % len(CASES) if ONLY else '')), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1, default=str)
