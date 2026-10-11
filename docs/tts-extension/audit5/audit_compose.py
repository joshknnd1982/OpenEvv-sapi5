# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 5 audit, steps 4 and 8: a sample of compositions said by the real engine and measured.

Every Tier A mark with a shift test is composed on bases its own proof did NOT use (three new
bases each), said plain and marked in three contexts, measured with the sweep's measures and
judged by the sweep's own paired-difference rule (check_shift). The suprasegmentals and tones
are said on a different set of vowels from their proofs (i, o, ɛ instead of a, e, u) and judged by
prosody.judge. Writes audit_compose.json beside this script and prints a table.
"""
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'ipa'))
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
os.environ.setdefault('EVV_STAGE', r'C:\Users\joshk\OpenEvvBuild-ttsext\stage-dev')
import table as T  # noqa: E402
import adapter as AD  # noqa: E402
import sweep as SW  # noqa: E402
import compose_test as CT  # noqa: E402
import prosody as PZ  # noqa: E402
import engine as E  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
t = T.load()
WORK = os.path.join(E.WORK, 'audit5')
os.makedirs(WORK, exist_ok=True)
AD.write(t, 'dedx', quiet=True)
p, MAP = SW.test_map('hi', 'dedx', WORK)
random.seed(5)
ONLY = set(sys.argv[1:])          # ids to run alone (the default: every entry); the output is then audit_compose_<n>.json

BY_IPA = {e['ipa']: sid for sid, e in t.sounds.items() if e.get('tier') == 'A' and e['kind'] == 'base'}
V = [BY_IPA[x] for x in 'i e ɛ ɔ o u y ø ɨ ʌ æ ɪ ʊ ɯ'.split()]
STOPS_VL = [BY_IPA[x] for x in 'p t k c q ʈ'.split()]
STOPS = [BY_IPA[x] for x in 'p t k b d ɡ'.split()]
VOICELESS = [BY_IPA[x] for x in 'p t k s f ʃ θ x'.split()]
VOICED_SON = [BY_IPA[x] for x in 'm n l r j w ŋ'.split()]
OBSTR = [BY_IPA[x] for x in 'p t k b d ɡ s z f m n l ʃ'.split()]
APPROX = [BY_IPA[x] for x in 'ɹ l j w ʋ'.split()]
SON_C = [BY_IPA[x] for x in 'm n l r ŋ'.split()]
POOL = {
    'ʰ': STOPS_VL, 'ʼ': STOPS_VL, '̚': STOPS_VL, 'ˡ': STOPS, 'ⁿ': STOPS,
    '̬': VOICELESS, '̥': VOICED_SON + V, '̊': VOICED_SON + V,
    'ʲ': OBSTR, 'ʷ': OBSTR, 'ˠ': OBSTR, 'ˤ': OBSTR, '̴': OBSTR, '̪': OBSTR, '̺': OBSTR, '̻': OBSTR, '̼': OBSTR,
    '̝': V + APPROX, '̩': SON_C, '̯': V, 'ː': V + SON_C + [BY_IPA['s'], BY_IPA['f']],
    'ˑ': V + SON_C, '̆': V + SON_C, '̃': V,
}
results = []
n_pairs = 0


def say_cases(ctx, label):
    inputs, diags = [], []
    for cid, text in ctx:
        rc, out, d = CT.say_ipa(p, MAP, text)
        if rc != 0:
            raise SystemExit('front-end failed on %s %r' % (label, text))
        inputs.append((cid, text, out, d))
        diags += d
    rend = E.render('hi', [(cid, 'annotated', out) for cid, _, out, _ in inputs],
                    work=os.path.join(WORK, label.replace('+', '_').replace(':', '_')))
    return inputs, rend, diags


# ------------------------------------------------------------------ marks on new bases
for sid, e in sorted(t.sounds.items()):
    if e.get('tier') != 'A' or e['kind'] != 'modifier' or (ONLY and sid not in ONLY):
        continue
    tests = e.get('tests') or {}
    if not tests.get('shift'):
        continue
    pool = POOL.get(e['ipa'])
    if pool is None:
        ed = e.get('edit') or {}
        pool = (V if 'vowel' in ed else []) + (OBSTR if 'consonant' in ed else [])
    new = [b for b in pool if b not in tests.get('bases', [])]
    random.shuffle(new)
    bases = new[:3]
    if not bases:
        continue
    saved = tests.get('bases')
    tests['bases'] = bases
    try:
        ctx = SW.contexts(t, sid)
        inputs, rend, diags = say_cases(ctx, sid)
        cases = {}
        for (cid, text, out, d), r_ in zip(inputs, rend):
            bm = t.sounds.get(cid.split('_')[0])
            c = SW.measure(r_, p, cid, SW.man_of(t, e), None, base_man=SW.manner(bm) if bm and bm['kind'] == 'base' else None)
            c.update(ipa=text, said=out, diag=r_['diag'], fe_diag=d)
            cases[cid] = c
        not_composed = [cid for cid, c in cases.items() if '_marked_' in cid and not any(
            d['kind'] == 'composed' for d in c['diag'] + c.get('fe_diag', []))]
        losses = [d for d in diags if d['level'] == 'loss']
        b3 = SW.check_shift(t, sid, cases)
        b3.pop('summary', None)
    finally:
        tests['bases'] = saved
    for k, v in b3['targets'].items():
        base_ipa = k.split(' ')[0]
        results.append(dict(kind='mark', mark=e['ipa'], id=sid, base=base_ipa, target=k, want=v.get('target'),
                            plain=v.get('plain'), marked=v.get('marked'), diff=v.get('measured'), within=v['within'],
                            paired=v.get('paired')))
    for b in bases:
        n_pairs += 1
        ok = all(v['within'] for k, v in b3['targets'].items() if k.startswith(t.sounds[b]['ipa'] + ' '))
        print('%-3s on %-3s %s  %s%s' % (e['ipa'], t.sounds[b]['ipa'], 'OK ' if ok else 'NOT',
                                       '; '.join('%s %s->%s (%s)' % (k.split(' ', 1)[1], v.get('plain'), v.get('marked'), v.get('measured'))
                                                 for k, v in b3['targets'].items() if k.startswith(t.sounds[b]['ipa'] + ' ')),
                                       ' NOT COMPOSED %s' % not_composed if not_composed else '', ), ' LOSS %s' % losses[:2] if losses else '')
        sys.stdout.flush()

# ------------------------------------------------------------------ prosody on other vowels
PZ.VOWELS = ('i', 'o', 'ɛ')
n_pros = 0
for sid, e in sorted(t.sounds.items()):
    if e.get('tier') != 'A' or not PZ.check_of(e) or (ONLY and sid not in ONLY):
        continue
    ctx = PZ.contexts(t, sid)
    if not ctx:
        continue
    inputs, rend, diags = say_cases(ctx, sid)
    cases = {}
    for (cid, text, out, d), r_ in zip(inputs, rend):
        c = SW.measure(r_, p, cid, SW.man_of(t, e), None)
        c.update(ipa=text, said=out, diag=r_['diag'], fe_diag=d)
        x_, rate_ = E.read_wav(r_['wav'])
        c['pros'] = PZ.measure(x_, rate_, c['phones'], r_['frames'], stops='T-double' in (e.get('tests') or {}).get('checks', []))
        cases[cid] = c
    b3, summ = PZ.judge(t, sid, cases)
    n_pros += 1
    ok = b3.get('passed')
    bad = [k for k, v in b3['targets'].items() if not v['within']]
    print('%-5s %-14s %s  targets %d, not met: %s' % (e['ipa'], e['kind'], 'OK ' if ok else 'NOT', len(b3['targets']), bad[:4]))
    for k, v in b3['targets'].items():
        results.append(dict(kind='prosody', mark=e['ipa'], id=sid, target=k, want=v.get('target'), measured=v.get('measured'),
                            within=v['within']))
    sys.stdout.flush()

with open(os.path.join(HERE, 'audit_compose%s.json' % ('_%d' % len(ONLY) if ONLY else '')), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
marks = [r for r in results if r['kind'] == 'mark']
pros = [r for r in results if r['kind'] == 'prosody']
print('\nmark-on-new-base pairs: %d; mark targets %d, in the intended direction %d' % (
    n_pairs, len(marks), sum(1 for r in marks if r['within'])))
print('prosody entries on i o ɛ: %d; targets %d, met %d' % (n_pros, len(pros), sum(1 for r in pros if r['within'])))
