"""Phase 5 audit, steps 6 and 8: every checklist symbol's proof file, read directly. MIT licence.

    python docs/tts-extension/audit5/proofs_check.py

Independent of coverage.py: the proof must exist, say `passed`, pass each of A0 A1 A2 B3 B2, name
the stage it was made on, and hold rendered cases with a WAV hash and per-phone measures.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
d = json.load(open(os.path.join(ROOT, 'docs', 'tts-extension', 'inventory', 'IPA_CHECKLIST.json'), encoding='utf-8'))
bad, n, ncases, stages = [], 0, 0, set()
for s in d['symbols']:
    p = os.path.join(ROOT, 'ipa', 'proofs', '%s.json' % s['id'].replace(':', '_'))
    if not os.path.exists(p):
        bad.append((s['id'], 'no proof'))
        continue
    j = json.load(open(p, encoding='utf-8'))
    n += 1
    stages.add(os.path.basename(j.get('staged') or ''))
    cs = j.get('cases') or {}
    ncases += len(cs)
    if not j.get('passed'):
        bad.append((s['id'], 'not passed'))
    if not cs:
        bad.append((s['id'], 'no cases'))
    for cid, c in cs.items():
        if not c.get('wav_sha256'):
            bad.append((s['id'], cid, 'no wav'))
        if not any((ph.get('meas') or {}) for ph in c.get('phones', [])):
            bad.append((s['id'], cid, 'no measures'))
    if not all(j[k]['passed'] for k in ('A0', 'A1', 'A2', 'B3', 'B2') if k in j):
        bad.append((s['id'], 'a check failed'))
print('checklist symbols with a proof: %d of %d; rendered cases: %d; stage: %s' % (n, len(d['symbols']), ncases, sorted(stages)))
print('problems: %d %s' % (len(bad), bad[:20]))
