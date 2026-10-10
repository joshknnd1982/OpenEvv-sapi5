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
    # the last case: voicing carried over from the vowel into the closure, dying away in 25 ms,
    # must not read as prevoicing (it did: the review of Phase 1)
    for clo, vot, pre, carry in ((80, 60, 0, 0), (90, 12, 0, 0), (100, 0, 60, 0), (90, 12, 0, 25)):
        y, truth = S.stop_cv(closure_ms=clo, vot_ms=vot, prevoiced_ms=pre, carry_ms=carry)
        st = A.stop_timing(y, S.RATE, truth['closure_start_ms'], truth['stop_end_ms'])
        e_vot = truth['vot_ms'] if not pre else -float(pre)
        label = 'aspirated' if vot > 30 else 'prevoiced' if pre else 'short lag, voicing carried over' if carry else 'short lag'
        check('stop burst (%s)' % label, near(st['burst_ms'], truth['burst_ms'], absol=3),
              '%.0f ms +-3' % truth['burst_ms'], st['burst_ms'])
        if not carry:      # with carried-over voicing the quiet part is shorter than the closure
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


def test_phase3():
    """The measures added in Phase 3A (analysis.py, DESIGN.md 10.2), each on a signal whose answer
    is known."""
    R = S.RATE
    t = np.arange(int(0.4 * R)) / R
    rng = np.random.default_rng(7)
    # T-trill: a vowel shut for 12 ms every 40 ms, three times (25 Hz)
    v = S.vowel([(600, 80), (1100, 90), (2500, 150)], dur_ms=400.0)
    gate = np.ones(len(v))
    for k in range(3):
        a = int((0.15 + 0.04 * k) * R)
        gate[a:a + int(0.012 * R)] = 0.05
    m = A.modulation(v * gate, R, 20, 380)
    check('trill dips (3 closures, 25 Hz)', m and m['dips'] == 3 and near(m['rate_hz'], 25.0, absol=2.5)
          and near(m['closed_ms'], 12.0, absol=5), '3 dips, 25 +-2.5 Hz, 12 +-5 ms',
          m and '%d dips, %s Hz, %.0f ms' % (m['dips'], m['rate_hz'] and round(m['rate_hz'], 1), m['closed_ms']))
    # T-phonation: H1-H2 of two harmonics 6.02 dB apart; and a longer open phase gives a larger one
    y = 8000 * np.sin(2 * np.pi * 120 * t) + 4000 * np.sin(2 * np.pi * 240 * t)
    h = A.h1_h2(y, R, 200, f0=120.0)
    check('H1-H2 of known harmonics', near(h, 6.02, absol=0.5), '6.0 +-0.5 dB', h and round(h, 2))
    hs = []
    for oq in (0.3, 0.8):
        y = S.resonator(S.pulses(120.0, 400.0, R, open_q=oq), 700, 80, R) * 20000
        hs.append(A.h1_h2(y, R, 200, f0=120.0))
    check('H1-H2 rises with the open phase', hs[0] is not None and hs[1] is not None and hs[1] > hs[0] + 3,
          'open 0.8 > open 0.3 + 3 dB', ' / '.join('%.1f' % x if x is not None else '-' for x in hs))
    # T-phonation: harmonics-to-noise of a tone in white noise at a known ratio
    for snr in (20.0, 10.0):
        sig = 8000 * np.sin(2 * np.pi * 150 * t)
        noise = rng.standard_normal(len(t)) * np.sqrt(np.mean(sig ** 2) / 10 ** (snr / 10.0))
        h = A.hnr_db(sig + noise, R, 50, 350)
        check('HNR of a tone at %d dB SNR' % snr, near(h, snr, absol=2.0), '%d +-2 dB' % snr, h and round(h, 1))
    # T-phonation: jitter of glottal pulses whose periods alternate 3 % either side. Each pulse has
    # the same open phase (46 samples), so its closure, the sharp event of a cycle, alternates as
    # its start does (with the open phase a share of each period, the closures would be evenly
    # spaced and the true jitter about nought: a fault found in the first version of this test)
    starts, tt = [], 0.0
    while tt < 0.4:
        starts.append(int(tt * R))
        tt += (0.97 if len(starts) % 2 else 1.03) / 120.0
    src = np.zeros(int(0.4 * R) + 64)
    for a in starts:
        src[a:a + 46] += 0.5 * (1 - np.cos(np.pi * np.arange(46) / 46.0))
    y = np.diff(src, prepend=0.0)
    for f, bw in ((600, 80), (1100, 90), (2500, 150)):
        y = S.resonator(y, f, bw, R)
    y = 20000 * y / np.max(np.abs(y))
    at = np.array([a + 46 for a in starts if int(0.05 * R) <= a < int(0.35 * R)])
    per = np.diff(at).astype(float)
    truth = 100.0 * np.mean(np.abs(np.diff(per))) / np.mean(per)
    j = A.jitter_pct(y, R, 50, 350)
    check('jitter of periods alternating +-3 %', near(j, truth, absol=1.0), '%.2f +-1 %%' % truth, j and round(j, 2))
    y = S.vowel([(600, 80), (1100, 90), (2500, 150)], f0=120.0, dur_ms=400.0)
    j0 = A.jitter_pct(y, R, 50, 350)
    check('jitter of a steady 120 Hz voice', j0 is not None and j0 < 1.0, 'under 1 %', j0 and round(j0, 2))
    # T-phonation (D83): glottal pulses one by one where no pitch tracker follows: vocal fry with
    # every second period later and weaker (24 and 17.5 ms, the second at 0.6 of the first), and a
    # steady 120 Hz voice
    starts, tt = [], 0.0
    while tt < 0.4:
        starts.append(int(tt * R))
        tt += 0.024 if len(starts) % 2 else 0.0175
    src = np.zeros(int(0.4 * R) + 64)
    for k, a in enumerate(starts):
        src[a:a + 46] += (1.0 if k % 2 == 0 else 0.6) * 0.5 * (1 - np.cos(np.pi * np.arange(46) / 46.0))
    y = np.diff(src, prepend=0.0)
    for f, bw in ((600, 80), (1100, 90), (2500, 150)):
        y = S.resonator(y, f, bw, R)
    y = 20000 * y / np.max(np.abs(y))
    at = np.array([a for a in starts if int(0.05 * R) <= a < int(0.35 * R)])
    per = np.diff(at).astype(float) / R
    pu = A.pulses(y, R, 50, 350)
    rate_t, jit_t = 1.0 / np.mean(per), 100.0 * np.mean(np.abs(np.diff(per))) / np.mean(per)
    check('pulses of vocal fry, every second later and weaker', pu is not None and near(pu[0], rate_t, 0.03)
          and near(pu[1], jit_t, absol=4.0), '%.1f Hz +-3%%, %.1f %% +-4' % (rate_t, jit_t),
          pu and '%.1f Hz, %.1f %%' % pu[:2])
    y = S.vowel([(600, 80), (1100, 90), (2500, 150)], f0=120.0, dur_ms=400.0)
    pu = A.pulses(y, R, 50, 350)
    check('pulses of a steady 120 Hz voice', pu is not None and near(pu[0], 120.0, 0.03) and pu[1] < 2.0,
          '120 Hz +-3%, under 2 %', pu and '%.1f Hz, %.1f %%' % pu[:2])
    # T-nasality: A1-P0 of harmonics whose levels are set
    y = np.zeros(len(t))
    for hk in range(1, 30):
        amp = {2: 2000.0, 5: 4000.0}.get(hk, 300.0)
        y += amp * np.sin(2 * np.pi * 100 * hk * t)
    an = A.a1_p0(y, R, 200, 500.0, p0_hz=200.0, f0=100.0)
    check('A1-P0 of set harmonics', near(an, 6.02, absol=0.5), '6.0 +-0.5 dB', an and round(an, 2))
    # T-airstream: voicing that swells 20 dB over 100 ms, and one that fades
    tt = np.arange(int(0.1 * R)) / R
    for sign, label in ((1, 'swelling'), (-1, 'fading')):
        amp = 10 ** (sign * 20 * tt / 0.1 / 20.0)
        y = 3000 * amp * np.sin(2 * np.pi * 120 * tt)
        sl = A.voicing_slope(y, R, 0, 100)
        check('voicing slope, %s 2 dB/10 ms' % label, near(sl, 2.0 * sign, absol=0.4), '%+.1f +-0.4' % (2.0 * sign),
              sl and round(sl, 2))
    # T-click: a 5 ms transient at 2 kHz, decaying 40 dB, in near-silence
    y = rng.standard_normal(int(0.1 * R)) * 2.0
    a = int(0.04 * R)
    tb = np.arange(int(0.005 * R)) / R
    y[a:a + len(tb)] += 20000 * np.exp(-tb / 0.005 * math.log(100)) * np.sin(2 * np.pi * 2000 * tb)
    b = A.burst(y, R, 0, 100)
    check('click burst: start, length, peak', b and near(b['start_ms'], 40.0, absol=1.5) and
          near(b['length_ms'], 5.0, absol=3.0) and near(b['peak_hz'], 2000.0, 0.12),
          '40 +-1.5 ms, 5 +-3 ms, 2000 +-12 %', b and '%.1f ms, %.1f ms, %.0f Hz' % (b['start_ms'], b['length_ms'], b['peak_hz']))
    # VOT past the stop's own stretch (D48): a 120 ms aspiration, the stop's span ending 10 ms after the burst
    y, truth = S.stop_cv(closure_ms=80, vot_ms=120)
    end = truth['burst_ms'] + 10.0
    short = A.stop_timing(y, R, truth['closure_start_ms'], end)
    long_ = A.vot_long(y, R, truth['closure_start_ms'], end)
    check('VOT found past the stop (aspirated 123 ms)', near(long_, truth['vot_ms'], absol=8),
          '%.0f +-8 ms (80 ms reach: %s)' % (truth['vot_ms'], short and short.get('vot_ms')), long_)
    # T-syllable: three vowels with silence between
    v = S.vowel([(700, 80), (1200, 90), (2600, 150)], dur_ms=150.0)
    gap = np.zeros(int(0.08 * R))
    y = np.concatenate([gap, v, gap, v, gap, v, gap])
    n = A.syllable_peaks(y, R, 0, len(y) * 1000.0 / R)
    check('syllable peaks (three vowels)', n == 3, '3', n)
    # T-slope: F0 gliding 100 -> 200 Hz over 1 s is 12 semitones a second
    y = S.vowel([(600, 80), (1100, 90), (2500, 150)], f0=lambda s: 100.0 * 2 ** s, dur_ms=1000.0)
    sl = A.f0_slope(y, R, 100, 900)
    check('F0 slope of a 1-octave-a-second glide', sl and near(sl['st_per_s'], 12.0, absol=1.0), '12 +-1 st/s',
          sl and round(sl['st_per_s'], 2))


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
    test_phase3()
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
