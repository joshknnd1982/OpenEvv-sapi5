"""Proves the harness before anything is measured with it (Phase 1 exit: harness self-tests).

Part 1, the analyser on synthetic signals whose answers are known (synth.py): formants, F0,
fricative spectra, stop timing, a nasal zero, a tone contour.
Part 2, the engine path: the facts engine.py relies on, checked on the real engine.

    python docs/tts-extension/harness/selftest.py            everything
    python docs/tts-extension/harness/selftest.py --quick    part 1 and the fastest engine checks

Prints one line a check (expected, measured, verdict) and exits 1 if any fails.
"""

import argparse
import math
import os
import sys

import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysis as A    # noqa: E402
import synth as S       # noqa: E402

RESULTS = []


def check(name, ok, expected, measured):
    RESULTS.append((name, bool(ok)))
    print('%-4s %-46s expected %-28s measured %s' % ('ok' if ok else 'FAIL', name, expected, measured))


def near(m, e, rel=None, absol=None):
    if m is None:
        return False
    lim = max(rel * abs(e) if rel else 0, absol or 0)
    return abs(m - e) <= lim


# ---- part 1: the analyser ------------------------------------------------------------------------

# Hillenbrand et al. (1995) men's means, rounded, as plausible targets; the test is only that the
# analyser finds the formants the synthesiser was given.
VOWELS = {'i': [(342, 60), (2322, 90), (3000, 150)], 'ɑ': [(768, 80), (1333, 90), (2522, 150)],
          'u': [(378, 60), (997, 80), (2343, 150)], 'ɛ': [(580, 70), (1799, 90), (2605, 150)]}


def test_formants():
    for f0, scale, who in ((110.0, 1.0, 'm'), (210.0, 1.15, 'f')):
        for v, fs in VOWELS.items():
            fs2 = [(f * scale, b) for f, b in fs]
            y = S.vowel(fs2 + [(3500 * scale, 250)], f0=f0)
            got = A.formants(y, S.RATE, 150.0)
            for k in range(3):
                e = fs2[k][0]
                m = got[k][0] if len(got) > k else None
                # LPC is pulled towards the strongest harmonic near a narrow F1 (Praat's Burg gives the
                # same on these signals: /u/ 378 Hz at F0 110 reads 453 in Praat and 450 here), so F1
                # is held to three quarters of a harmonic spacing; F2 and F3 to 5 %.
                tol = (0.06, 0.75 * f0) if k == 0 else (0.05, 0)
                check('formant F%d /%s/ %s f0=%d' % (k + 1, v, who, f0), near(m, e, *tol),
                      '%.0f Hz +-%.0f' % (e, max(tol[0] * e, tol[1])), '%.0f' % m if m else None)


def test_f0():
    for f0 in (80.0, 120.0, 200.0, 320.0):
        y = S.vowel(VOWELS['ɑ'], f0=f0, dur_ms=400)
        ms = [A.f0_at(y, S.RATE, t) for t in (100, 200, 300)]
        ok = all(near(m, f0, 0.01) for m in ms)
        check('F0 steady %d Hz' % f0, ok, '%d +-1%%' % f0, ' '.join('%.1f' % m if m else '-' for m in ms))
    glide = lambda t: 100 + 250 * t      # 100 -> 200 Hz over 0.4 s
    y = S.vowel(VOWELS['ɑ'], f0=glide, dur_ms=400)
    ms = [(t, A.f0_at(y, S.RATE, t)) for t in (80, 200, 320)]
    ok = all(near(m, glide(t / 1000.0), 0.03) for t, m in ms)
    check('F0 glide 100->200 Hz', ok, ' '.join('%.0f' % glide(t / 1000.0) for t, _ in ms) + ' +-3%',
          ' '.join('%.0f' % m if m else '-' for _, m in ms))
    noise = S.noise_band(300, 5000, dur_ms=400)
    voiced = [A.f0_at(noise, S.RATE, t) for t in range(50, 350, 10)]
    rate = sum(1 for v in voiced if v) / len(voiced)
    check('F0 on noise is unvoiced', rate <= 0.1, '<=10% voiced', '%.0f%% voiced' % (100 * rate))
    c = A.tone_contour(S.vowel(VOWELS['ɑ'], f0=lambda t: 200 - 200 * t, dur_ms=400), S.RATE, 0, 400)
    hz = c['hz']
    mono = all(a is not None and b is not None and a > b for a, b in zip(hz, hz[1:]))
    ends = near(hz[0], 200 - 200 * 0.02, 0.03) and near(hz[-1], 200 - 200 * 0.38, 0.03)
    check('tone contour falling 200->120 Hz', mono and ends, 'falling, 196..124 +-3%',
          ' '.join('%.0f' % h if h else '-' for h in hz))


def _truth(lo, hi, fmin=500.0, edge_db=10.0):
    """The filter's own centroid above fmin, and where its response is edge_db below its peak."""
    sos = signal.butter(6, [lo / (S.RATE / 2.0), min(hi / (S.RATE / 2.0), 0.999)], 'band', output='sos')
    w, h = signal.sosfreqz(sos, worN=4096, fs=S.RATE)
    p = np.abs(h) ** 2
    keep = w >= fmin
    c = float((w[keep] * p[keep]).sum() / p[keep].sum())
    db = 10 * np.log10(np.maximum(p, 1e-20))
    inside = np.nonzero(db >= db.max() - edge_db)[0]
    return c, float(w[inside[0]]), float(w[inside[-1]])


def test_fricatives():
    for lo, hi, label in ((3500, 5200, 's-like'), (2000, 3500, 'ʃ-like'), (900, 5400, 'f-like')):
        y = S.noise_band(lo, hi, dur_ms=300)
        m = A.spectrum_moments(y, S.RATE, 50, 250)
        e, e_lo, e_hi = _truth(lo, hi)
        check('fricative centroid %s %d-%d Hz' % (label, lo, hi), near(m['centroid_hz'], e, 0.04),
              '%.0f +-4%%' % e, '%.0f (peak %.0f, edges %.0f-%.0f)' % (m['centroid_hz'], m['peak_hz'],
                                                                     m['low_edge_hz'], m['high_edge_hz']))
        check('fricative -10 dB edges %s' % label, near(m['low_edge_hz'], e_lo, 0.12) and
              near(m['high_edge_hz'], e_hi, 0.12),
              '%.0f / %.0f +-12%%' % (e_lo, e_hi), '%.0f / %.0f' % (m['low_edge_hz'], m['high_edge_hz']))


def test_stops():
    for clo, vot, pre in ((80, 60, 0), (90, 12, 0), (100, 0, 60)):
        y, truth = S.stop_cv(closure_ms=clo, vot_ms=vot, prevoiced_ms=pre)
        st = A.stop_timing(y, S.RATE, truth['closure_start_ms'], truth['stop_end_ms'])
        e_vot = truth['vot_ms'] if not pre else -float(pre)
        label = 'aspirated' if vot > 30 else 'short lag' if not pre else 'prevoiced'
        check('stop burst (%s)' % label, near(st['burst_ms'], truth['burst_ms'], absol=3),
              '%.0f ms +-3' % truth['burst_ms'], st['burst_ms'])
        check('stop closure (%s)' % label, near(st['closure_ms'], clo, absol=6),
              '%d ms +-6' % clo, st['closure_ms'])
        check('stop VOT (%s)' % label, near(st['vot_ms'], e_vot, absol=8),
              '%.0f ms +-8' % e_vot, '%.1f' % st['vot_ms'] if st['vot_ms'] is not None else None)


def test_nasal():
    for zero in (900.0, 1500.0, 2200.0):
        y = S.nasal(zero=zero)
        nz = A.nasal_zero(y, S.RATE, 30, 220)
        check('nasal antiformant %d Hz' % zero, near(nz['zero_hz'], zero, 0.08), '%.0f +-8%%' % zero,
              '%.0f (depth %.0f dB)' % (nz['zero_hz'], nz['depth_db']) if nz['zero_hz'] else None)
        check('nasal murmur F1 (%d Hz zero)' % zero, near(nz['murmur_f1_hz'], 280, 0.15), '280 +-15%',
              '%.0f' % nz['murmur_f1_hz'] if nz['murmur_f1_hz'] else None)


# ---- part 2: the engine path ---------------------------------------------------------------------

def test_engine(quick):
    import engine as E
    if not os.path.exists(E.RENDER):
        check('evv_render.exe is built', False, E.RENDER, 'missing')
        return
    # inert markup: the sound byte for byte the same, and phones traced, where engine.py uses it
    for tag, want in (('enus', True), ('dede', False)):
        got = E.traces(E.pack(tag), 64)
        check('inert markup traced and harmless: %s' % tag, got == want, want, got)
    # the annotated path makes the product's frames
    for tag, text in (('hi', 'टमाटर ठंडा'), ('sw', 'Habari ya asubuhi.')) if not quick else (('hi', 'टमाटर'),):
        fe = E.frontend(E.pack(tag), text)
        r = E.render(tag, [('host', 'text', text), ('anno', 'annotated', fe)], jobs=2)
        same = r[0]['frames'].shape == r[1]['frames'].shape and (r[0]['frames'] == r[1]['frames']).all()
        check('annotated path = product frames: %s' % tag, same, 'identical frames',
              'identical' if same else 'differ')
    # every render checks frames against sound itself; this records the spread
    cases = [('enus', 'text', 'Hello there.'), ('dede', 'module', '`[.1ta.0ta]'), ('hi', 'ipa', 'ʈəˈmaːʈər')]
    gaps = []
    for tag, kind, text in cases:
        r = E.render(tag, [('gap', kind, text)], jobs=1)[0]
        gaps.append(r['case_ms'] - r['n_samples'] * 1000.0 / r['rate'])
    check('frames against sound', all(0 <= g <= E.SAMPLE_SLACK_MS for g in gaps),
          '0..%d ms' % E.SAMPLE_SLACK_MS, ' '.join('%.2f' % g for g in gaps))
    # labels from runs where the module has no trace
    r = E.render('dede', [('runs', 'module', '`[.1ta.0sa]')], jobs=1)[0]
    names = [p['name'] for p in r['phones']]
    check('run labels (dede `[.1ta.0sa])', names == ['t', 'a', 's', 'a', '#'], 't a s a #', ' '.join(names))
    # the golden regression fails on drift: Hindi /t/ rendered with its sound changed (s12, vot
    # 15 -> 60 ms, through an override map) against the recorded case; and passes unchanged
    import golden
    if os.path.exists(golden.golden_path('hi')):
        gold = golden.read_golden('hi')
        gold['cases'] = {'s|t': gold['cases']['s|t']}
        verdicts = []
        for label, ov in (('unchanged', None), ('s12 vot=60', ['s12 f2=91 burst=-4 vot=60'])):
            mp = E.override_map(E.pack('hi'), ov, os.path.join(E.WORK, 'hi')) if ov else None
            r = E.render('hi', [('s|t', 'espeak', "'ata")], jobs=1, map_path=mp, work=os.path.join(E.WORK, 'drift'))[0]
            now = dict(cases={'s|t': golden.measure_case(r, 'dede')}, errors={})
            verdicts.append([sev for _, sev, _ in golden.compare(gold, now)])
        check('golden passes unchanged, fails on drift (hi /t/ vot)', verdicts[0] == [] and verdicts[1] == ['FAIL'],
              'pass, then FAIL', '%s, then %s' % (verdicts[0] or 'pass', verdicts[1] or 'pass'))
    if quick:
        return
    # phone classes from the trace records (analysis.phone_class)
    want = {'a': 'vowel', 't': 'stop', 's': 'fricative', 'n': 'nasal', 'l': 'liquid', 'm': 'nasal',
            'f': 'fricative', 'k': 'stop', 'C': 'affricate', 'y': 'glide', 'w': 'glide', 'r': 'liquid',
            'S': 'fricative', 'd': 'stop'}
    r = E.render('enus', [('cls_%s' % c, 'module', '`[.1a%sa]' % c) for c in want if c != 'a'], jobs=4)
    seen = {}
    for q in r:
        for p in q['phones']:
            seen.setdefault(p['name'], (tuple(p['record']), A.phone_class(p['record'], p['name'], 'enus')))
    # English's own rules change some of what is asked (intervocalic t is a flap F; C comes out
    # as t S), so every phone that sounded must have its class, and the main classes must occur.
    bad = {c: seen.get(c) for c in want if c in seen and seen[c][1] != want[c]}
    classes = {v[1] for v in seen.values()}
    need = {'vowel', 'stop', 'fricative', 'nasal', 'liquid', 'glide', 'silence'}
    check('phone classes (enus, by module IPA)', not bad and need <= classes,
          ', '.join(sorted(need)), 'as expected; seen %s' % ', '.join(sorted(classes)) if not bad else 'mismatch %s' % bad)
    print('     records seen: %s' % ', '.join('%s=%s' % (k, '.'.join(map(str, v[0]))) for k, v in sorted(seen.items())))
    # the synthesiser realises the frames it is given (check A's signal evidence): F1/F2 measured
    # from the sound against F1/F2 requested in the frames, mid-vowel
    r = E.render('enus', [('v_%s' % v, 'module', '`[.1h%sd]' % v) for v in ('i', 'a', 'u', 'E', 'A')], jobs=4)
    for q in r:
        x = q['samples'] if 'samples' in q else E.read_wav(q['wav'])[0]
        t = E.frame_times(q['frames'])
        vow = [p for p in q['phones'] if A.phone_class(p['record'], p['name'], 'enus') == 'vowel'][0]
        req = A.requested(q['frames'], t, vow)
        mid = (vow['start_ms'] + vow['end_ms']) / 2.0
        got = A.formants(x, q['rate'], mid)
        for k in (1, 2):
            e = req['F%d_hz' % k]
            m = got[k - 1][0] if len(got) >= k else None
            check('engine realises F%d of %s' % (k, vow['name']), near(m, e, 0.08, 40), '%d +-8%%' % e,
                  '%.0f' % m if m else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--no-engine', action='store_true')
    a = ap.parse_args()
    print('== part 1: the analyser on synthetic signals')
    test_formants()
    test_f0()
    test_fricatives()
    test_stops()
    test_nasal()
    if not a.no_engine:
        print('== part 2: the engine path')
        test_engine(a.quick)
    failed = [n for n, ok in RESULTS if not ok]
    print('== %d checks, %d passed, %d failed' % (len(RESULTS), len(RESULTS) - len(failed), len(failed)))
    for n in failed:
        print('   FAILED: %s' % n)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
