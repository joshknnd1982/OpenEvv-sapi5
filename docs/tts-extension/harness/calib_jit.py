"""Q36 calibration: the accent layer's `jit' (tenths of a per cent, the most a frame's pitch is moved)
against the local jitter the harness measures (pulse_jitter_pct), on the long vowels the labels'
tests use ([a e ɛ] between p, as VoQS's tests say them). Prints, per jit, each vowel's measure, their
median, and the median's rise over jit 0 (D87; the run behind adapter.KEY_UNIT['jit'] is
results/calib_jit_d87.txt). Under EVV_STAGE, from the repository root:

    python docs/tts-extension/harness/calib_jit.py 0 20 40 60 80 100 140
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'ipa'))
sys.path.insert(0, HERE)
import sweep as S  # noqa: E402
import compose_test as CT  # noqa: E402
import engine as E  # noqa: E402

work = os.path.join(E.WORK, 'calib_jit')
os.makedirs(work, exist_ok=True)
p, map_path = S.test_map('hi', 'dedx', work)
words = {'a': 'ˈpaːp', 'e': 'ˈpeːp', 'ɛ': 'ˈpɛːp'}
said = {}
for v, w in words.items():
    rc, out, d = CT.say_ipa(p, map_path, w)
    said[v] = out
jits = [int(x) for x in sys.argv[1:]] or [0, 20, 40, 60, 80, 120]
cases = []
for j in jits:
    for v, out in said.items():
        # the vowel's own definition, `jit' added (the {D} that names the vowel's id)
        vid = re.search(r'[A-Za-z@:]+=(\S+?)\^', out).group(1)
        o2 = out.replace('{D %s ' % vid, '{D %s jit=%d ' % (vid, j)) if j else out
        cases.append(('j%d_%s' % (j, v), 'annotated', o2))
rend = E.render('hi', cases, work=work)
base = None
for j in jits:
    vals = []
    for v in words:
        r = rend[[c[0] for c in cases].index('j%d_%s' % (j, v))]
        m = S.measure(r, p, 'x_x', 'vowel')
        vals.append((m.get('extra') or {}).get('pulse_jitter_pct'))
    ok = sorted(x for x in vals if x is not None)
    med = ok[len(ok) // 2] if ok else None
    if base is None:
        base = med
    print('jit=%3d  %s  median %.2f  rise %.2f' % (j, '  '.join('%s %.2f' % (v, x) if x is not None else '%s -' % v
                                                              for v, x in zip(words, vals)), med, med - base))
