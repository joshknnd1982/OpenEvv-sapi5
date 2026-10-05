"""Measures speech signals (Phase 1, step 2). numpy and scipy only (both BSD).

Every measure takes a mono signal `x` (any numeric array) and its rate, and times in ms. They are
deliberately plain, so that selftest.py can prove each one on synthetic signals whose answer is
known, and praat_crosscheck.py can compare them with Praat:

    formants(x, rate, t)            F1..F4 and bandwidths at a moment (LPC, autocorrelation method)
    formant_track(x, rate, a, b)    the same every 5 ms over a stretch
    f0_track(x, rate, a, b)         F0 every 5 ms (normalised autocorrelation), None where unvoiced
    intensity_db(x, rate, a, b)     RMS level in dB re full scale
    spectrum_moments(x, rate, a, b) centroid, spread, skewness, kurtosis, peak, band edges
    stop_timing(x, rate, a, b)      closure, burst, voicing onset and VOT in a stop's stretch
    nasal_zero(x, rate, a, b)       the deepest spectral valley of a nasal murmur (antiformant)
    tone_contour(x, rate, a, b)     F0 at ten points, in Hz and in semitones

and `phone_metrics` picks the ones that suit a phone's class. Add a metric by writing a function and
calling it in `phone_metrics` for the classes it suits: every key it returns is stored by golden.py,
compared on every run (tolerance chosen by the key's unit suffix, _hz, _db or _ms) and can be
checked against references by naming it in reference.METRIC. Nothing else needs to change.
"""

import math

import numpy as np
from scipy import linalg, signal

STEP_MS = 5.0


def _seg(x, rate, a_ms, b_ms):
    a = max(0, int(round(a_ms * rate / 1000.0)))
    b = min(len(x), int(round(b_ms * rate / 1000.0)))
    return np.asarray(x[a:b], dtype=float)


def _frame(x, rate, t_ms, win_ms):
    n = int(round(win_ms * rate / 1000.0))
    c = int(round(t_ms * rate / 1000.0))
    a, b = c - n // 2, c - n // 2 + n
    if a < 0 or b > len(x):
        y = np.zeros(n)
        lo, hi = max(a, 0), min(b, len(x))
        if hi > lo:
            y[lo - a:hi - a] = x[lo:hi]
        return y
    return np.asarray(x[a:b], dtype=float)


# ---- formants ------------------------------------------------------------------------------------

def burg(y, order):
    """LPC coefficients [1, a1..ap] by Burg's method (as Praat's "To Formant (burg)"): less pulled
    towards a harmonic of the voice than the autocorrelation method (selftest.py, /u/ F1)."""
    f = np.asarray(y, dtype=float).copy()
    b = f.copy()
    a = np.array([1.0])
    for _ in range(order):
        ef, eb = f[1:], b[:-1]
        den = np.dot(ef, ef) + np.dot(eb, eb)
        if den <= 0:
            return None
        k = -2.0 * np.dot(ef, eb) / den
        a = np.concatenate([a, [0.0]])
        a = a + k * a[::-1]
        f, b = ef + k * eb, eb + k * ef
    return a


def lpc(y, order):
    """LPC coefficients [1, a1..ap] by the autocorrelation method."""
    r = np.correlate(y, y, mode='full')[len(y) - 1:len(y) + order]
    if r[0] <= 0:
        return None
    r = r.copy()
    r[0] *= 1.0 + 1e-9          # a hair of white noise keeps the system solvable
    try:
        a = linalg.solve_toeplitz((r[:-1], r[:-1]), -r[1:])
    except (linalg.LinAlgError, ValueError):
        return None
    return np.concatenate([[1.0], a])


def formants(x, rate, t_ms, win_ms=25.0, order=None, n=4, fmin=90.0, bmax=700.0, method='burg'):
    """[(F, B), ...] up to n, lowest first, at t_ms. Pre-emphasis from 50 Hz, Gaussian-like window,
    Burg's method (or method='autocorrelation').

    The order is 2 + rate/1000 rounded down to even (12 at 11025 Hz): two coefficients for every
    resonance below the Nyquist frequency, and two for the glottal source and radiation.
    """
    y = _frame(x, rate, t_ms, win_ms)
    if not np.any(y):
        return []
    y = np.append(y[0], y[1:] - math.exp(-2 * math.pi * 50.0 / rate) * y[:-1])
    y = y * signal.windows.gaussian(len(y), std=len(y) / 6.0)
    if order is None:
        order = int(2 + rate / 1000) // 2 * 2
    a = burg(y, order) if method == 'burg' else lpc(y, order)
    if a is None:
        return []
    out = []
    for z in np.roots(a):
        if z.imag <= 0:
            continue
        f = math.atan2(z.imag, z.real) * rate / (2 * math.pi)
        bw = -math.log(abs(z)) * rate / math.pi
        if fmin < f < rate / 2.0 - 50 and bw < bmax:
            out.append((f, bw))
    out.sort()
    return out[:n]


def formant_track(x, rate, a_ms, b_ms, step_ms=STEP_MS, **kw):
    """[(t, [(F, B), ...]), ...] every step_ms from a_ms to b_ms."""
    t = a_ms
    out = []
    while t <= b_ms:
        out.append((t, formants(x, rate, t, **kw)))
        t += step_ms
    return out


def formant_at(x, rate, t_ms, k, **kw):
    """Fk (1-based) at t_ms, or None."""
    f = formants(x, rate, t_ms, **kw)
    return f[k - 1][0] if len(f) >= k else None


# ---- F0 ------------------------------------------------------------------------------------------

def f0_at(x, rate, t_ms, fmin=50.0, fmax=600.0, threshold=0.45):
    """F0 at t_ms by the normalised autocorrelation of a window three periods of fmin long, or
    None if its best peak is below `threshold` (unvoiced). Parabolic interpolation of the peak."""
    y = _frame(x, rate, t_ms, 3000.0 / fmin)
    y = y - y.mean()
    if not np.any(y):
        return None
    w = np.hanning(len(y))
    yw = y * w
    n = len(yw)
    spec = np.fft.rfft(yw, 2 * n)
    r = np.fft.irfft(np.abs(spec) ** 2)[:n]
    rw = np.fft.irfft(np.abs(np.fft.rfft(w, 2 * n)) ** 2)[:n]
    r = r / r[0] / np.maximum(rw / rw[0], 1e-9)          # Boersma's window correction
    lo, hi = int(rate / fmax), min(int(rate / fmin), n - 2)
    if hi <= lo + 2:
        return None
    k = lo + int(np.argmax(r[lo:hi]))
    if r[k] < threshold:
        return None
    # prefer the shortest lag whose peak is almost as good: avoids octave errors downward
    for m in range(2, 6):
        km = int(round(k / m))
        if km >= lo:
            seg = r[max(lo, km - 2):km + 3]
            j = max(lo, km - 2) + int(np.argmax(seg))
            if r[j] > 0.9 * r[k]:
                k = j
    if 1 <= k < n - 1:
        a, b, c = r[k - 1], r[k], r[k + 1]
        d = (a - c) / (2 * (a - 2 * b + c)) if (a - 2 * b + c) != 0 else 0.0
    else:
        d = 0.0
    return rate / (k + d)


def f0_track(x, rate, a_ms, b_ms, step_ms=STEP_MS, **kw):
    t = a_ms
    out = []
    while t <= b_ms:
        out.append((t, f0_at(x, rate, t, **kw)))
        t += step_ms
    return out


def semitones(f, ref):
    return 12.0 * math.log2(f / ref)


def tone_contour(x, rate, a_ms, b_ms, points=10, ref_hz=None):
    """F0 at `points` evenly spaced moments of a stretch: Hz, and semitones re ref_hz (default
    the stretch's own median)."""
    if b_ms - a_ms < 10:
        return None
    ts = [a_ms + (b_ms - a_ms) * (i + 0.5) / points for i in range(points)]
    hz = [f0_at(x, rate, t) for t in ts]
    voiced = [h for h in hz if h]
    if not voiced:
        return dict(hz=hz, st=[None] * points, ref_hz=None)
    ref = ref_hz or float(np.median(voiced))
    return dict(hz=hz, st=[semitones(h, ref) if h else None for h in hz], ref_hz=ref)


# ---- level and spectrum --------------------------------------------------------------------------

def intensity_db(x, rate, a_ms, b_ms):
    y = _seg(x, rate, a_ms, b_ms)
    if len(y) == 0:
        return None
    rms = math.sqrt(float(np.mean(y * y)))
    return 20 * math.log10(rms / 32768.0) if rms > 0 else -120.0


def spectrum(x, rate, a_ms, b_ms, win_ms=20.0):
    """Mean power spectrum of a stretch (Hann windows, half overlapping), and its frequencies."""
    y = _seg(x, rate, a_ms, b_ms)
    n = int(round(win_ms * rate / 1000.0))
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    f, pxx = signal.welch(y, fs=rate, window='hann', nperseg=n, noverlap=n // 2, detrend='constant')
    return f, pxx


def spectrum_moments(x, rate, a_ms, b_ms, fmin=500.0, edge_db=10.0):
    """The first four spectral moments over fmin..Nyquist (as for fricatives, Jongman et al. 2000
    measure from 500 Hz to suppress voicing), the peak, and the band edges where the smoothed
    spectrum falls edge_db below its peak on either side."""
    f, p = spectrum(x, rate, a_ms, b_ms)
    keep = f >= fmin
    f, p = f[keep], p[keep]
    if len(p) == 0 or p.sum() <= 0:
        return None
    w = p / p.sum()
    c = float((f * w).sum())
    sd = float(math.sqrt(((f - c) ** 2 * w).sum()))
    skew = float(((f - c) ** 3 * w).sum() / sd ** 3) if sd > 0 else 0.0
    kurt = float(((f - c) ** 4 * w).sum() / sd ** 4 - 3) if sd > 0 else 0.0
    db = 10 * np.log10(np.maximum(np.convolve(p, np.ones(5) / 5, mode='same'), 1e-20))
    k = int(np.argmax(db))
    lo = k
    while lo > 0 and db[lo] > db[k] - edge_db:
        lo -= 1
    hi = k
    while hi < len(db) - 1 and db[hi] > db[k] - edge_db:
        hi += 1
    return dict(centroid_hz=c, sd_hz=sd, skewness=skew, kurtosis=kurt, peak_hz=float(f[k]),
                low_edge_hz=float(f[lo]), high_edge_hz=float(f[hi]))


def nasal_zero(x, rate, a_ms, b_ms, lo_hz=400.0, hi_hz=3500.0):
    """The deepest valley of a nasal murmur's smoothed spectrum between lo_hz and hi_hz: the
    antiformant, measured as the frequency of the lowest point relative to the straight line
    between its neighbouring peaks. With the murmur's first formant."""
    f, p = spectrum(x, rate, a_ms, b_ms, win_ms=30.0)
    db = 10 * np.log10(np.maximum(np.convolve(p, np.ones(3) / 3, mode='same'), 1e-20))
    band = np.nonzero((f >= lo_hz) & (f <= hi_hz))[0]
    if len(band) < 3:
        return None
    best, best_depth = None, 0.0
    for i in band:
        if i <= 0 or i >= len(db) - 1 or not (db[i] < db[i - 1] and db[i] <= db[i + 1]):
            continue
        left = db[:i].max() if i > 0 else db[i]
        right = db[i + 1:].max() if i + 1 < len(db) else db[i]
        lpk = int(np.argmax(db[:i]))
        rpk = i + 1 + int(np.argmax(db[i + 1:]))
        line = db[lpk] + (db[rpk] - db[lpk]) * (i - lpk) / max(rpk - lpk, 1)
        depth = line - db[i]
        if depth > best_depth:
            best, best_depth = i, depth
    mid = (a_ms + b_ms) / 2.0
    f1 = formant_at(x, rate, mid, 1)
    if best is None:
        return dict(zero_hz=None, depth_db=0.0, murmur_f1_hz=f1)
    return dict(zero_hz=float(f[best]), depth_db=float(best_depth), murmur_f1_hz=f1)


# ---- stops ---------------------------------------------------------------------------------------

def stop_timing(x, rate, a_ms, b_ms, after_ms=80.0, hop_ms=1.0, voicing=0.45):
    """Closure, burst and voicing onset in a stop's stretch [a_ms, b_ms] and up to after_ms past it.

    closure: the quiet part (RMS 25 dB or more below the stretch's loudest 5 ms) before the burst.
    burst:   the first 1 ms hop after the closure whose energy above 1.5 kHz jumps 12 dB or more
             over the closure's.
    voicing: prevoicing when a voice bar (energy below 400 Hz within 40 dB of the stretch's
             loudest) runs unbroken for 10 ms or more into the burst: its start is the onset.
             Otherwise the first moment after the burst from which F0 is found for 20 ms.
             Voicing carried over from the vowel before, which dies away in the closure, is not
             prevoicing (it made Hindi /p t k/ read -117 to -49 ms: the review of Phase 1).
    VOT = voicing onset - burst (negative when prevoiced).
    """
    y = _seg(x, rate, a_ms, b_ms + after_ms)
    if len(y) < rate * 0.01:
        return None
    hp = signal.sosfilt(signal.butter(4, 1500.0 / (rate / 2.0), 'high', output='sos'), y)
    hop = max(1, int(round(hop_ms * rate / 1000.0)))
    n = len(y) // hop
    e_all = np.array([np.mean(y[i * hop:(i + 1) * hop] ** 2) for i in range(n)]) + 1e-12
    e_hi = np.array([np.mean(hp[i * hop:(i + 1) * hop] ** 2) for i in range(n)]) + 1e-12
    db_all = 10 * np.log10(np.convolve(e_all, np.ones(5) / 5, mode='same'))
    db_hi = 10 * np.log10(e_hi)
    quiet = db_all < db_all.max() - 25
    burst = None
    for i in range(1, n):
        if quiet[:i].any():
            q = np.nonzero(quiet[:i])[0]
            base = np.median(db_hi[q])
            if not quiet[i] and db_hi[i] - base >= 12:
                burst = i
                break
    closure_ms = None
    if burst is not None:
        j = burst - 1
        while j >= 0 and not quiet[j]:
            j -= 1
        k = j
        while k >= 0 and quiet[k]:
            k -= 1
        closure_ms = (j - k) * hop_ms if j >= 0 else 0.0
    lo = signal.sosfilt(signal.butter(4, 400.0 / (rate / 2.0), 'low', output='sos'), y)
    e_lo = np.array([np.mean(lo[i * hop:(i + 1) * hop] ** 2) for i in range(n)]) + 1e-12
    db_lo = 10 * np.log10(np.convolve(e_lo, np.ones(5) / 5, mode='same'))
    bar = db_lo > db_lo.max() - 40
    onset = None
    t = 0.0
    if burst is not None:
        j = burst - 1
        while j >= 0 and bar[j]:
            j -= 1
        if (burst - 1 - j) * hop_ms >= 10:
            onset = (j + 1) * hop_ms           # prevoiced: the voice bar reaches the burst
        else:
            t = burst * hop_ms
    total = len(y) * 1000.0 / rate
    while onset is None and t < total - 20:
        if all(f0_at(y, rate, t + d, threshold=voicing) for d in (0.0, 5.0, 10.0, 15.0, 20.0)):
            onset = t
            break
        t += hop_ms * 2
    out = dict(closure_ms=closure_ms,
               burst_ms=(a_ms + burst * hop_ms) if burst is not None else None,
               voicing_onset_ms=(a_ms + onset) if onset is not None else None)
    out['vot_ms'] = (out['voicing_onset_ms'] - out['burst_ms']
                     if out['burst_ms'] is not None and out['voicing_onset_ms'] is not None else None)
    return out


# ---- per phone -----------------------------------------------------------------------------------

# Manner by IPA. The module's own phone record (class.voicing.sonority.manner.place in the accent
# trace) numbers manners differently in each module (English counts stops from 0, German from 1:
# selftest.py, 'phone classes'), so only its first field, 0 pause / 1 vowel / 2 consonant, is used
# from it, and the manner comes from the IPA engine/espeak_phonemes.py gives the module's phone.
MANNER = {}
for _m, _syms in (('stop', 'p b t d ʈ ɖ c ɟ k ɡ g q ɢ ʔ'), ('affricate', 'tʃ dʒ ts dz pf tɕ dʑ ʈʂ ɖʐ'),
                  ('fricative', 'ɸ β f v θ ð s z ʃ ʒ ʂ ʐ ç ʝ x ɣ χ ʁ ħ ʕ h ɦ ɕ ʑ ɬ ɮ'),
                  ('nasal', 'm ɱ n ɳ ɲ ŋ ɴ'), ('liquid', 'l ɭ ʎ ʟ ɫ r ɾ ɽ ɹ ɻ ʀ ɺ'), ('glide', 'j w ɥ ɰ ʋ')):
    for _s in _syms.split():
        MANNER[_s] = _m

_module_ipa = {}


def module_ipa(phone_module):
    """Module phone -> IPA, from engine/espeak_phonemes.py ({} for a module it does not cover)."""
    if phone_module not in _module_ipa:
        import os
        import sys
        import unicodedata
        from engine import ROOT
        sys.path.insert(0, os.path.join(ROOT, 'engine'))
        import espeak_phonemes
        t = espeak_phonemes.TEMPLATES.get(phone_module)
        table = {}
        if t is not None:
            for d in (t.vowels, t.consonants):
                for ph, i in d.items():
                    table[ph] = unicodedata.normalize('NFC', i)
        _module_ipa[phone_module] = table
    return _module_ipa[phone_module]


# Modules engine/espeak_phonemes.py has no table for: Canadian French has France's phone set and
# Polish began as a copy of Italian (NOTICE.md). Japanese's phones are named like romaji, which
# gives their manner (a class only; no acoustic value is taken from it).
CLASS_TABLE = {'frca': 'frfr', 'plpl': 'itit'}
JAJP_CLASS = dict([(n, 'vowel') for n in 'aiueo'] + [(n, 'stop') for n in 'bdgptk'] +
                  [(n, 'fricative') for n in 'zshfSZ'] + [('c', 'affricate')] +
                  [(n, 'nasal') for n in 'mnN'] + [('r', 'liquid'), ('y', 'glide'), ('w', 'glide')])


def phone_class(record=None, name=None, phone_module=None):
    """vowel / stop / affricate / fricative / nasal / liquid / glide / silence / consonant / other."""
    if name in ('#', '_', '-'):
        return 'silence'
    if record:
        if record[0] == 0:
            return 'silence'
        if record[0] == 1:
            return 'vowel'
    if phone_module == 'jajp':
        return JAJP_CLASS.get(name, 'consonant' if record and record[0] == 2 else 'other')
    phone_module = CLASS_TABLE.get(phone_module, phone_module)
    ipa = module_ipa(phone_module).get(name) if phone_module else None
    if ipa:
        if ipa in MANNER:
            return MANNER[ipa]
        if record is None:
            return 'vowel' if ipa in module_ipa(phone_module).values() and ipa not in MANNER else 'other'
    return 'consonant' if record and record[0] == 2 else 'other'


def phone_metrics(x, rate, ph, cls, nxt=None):
    """The metrics that suit a phone of class `cls`, measured over its span [start_ms, end_ms]."""
    a, b = float(ph['start_ms']), float(ph['end_ms'])
    mid = (a + b) / 2.0
    m = dict(duration_ms=b - a, intensity_db=intensity_db(x, rate, a, b))
    if cls in ('vowel', 'liquid', 'glide', 'nasal'):
        for k, t in (('20', a + 0.2 * (b - a)), ('50', mid), ('80', a + 0.8 * (b - a))):
            fs = formants(x, rate, t)
            for i in range(3):
                m['F%d_%s_hz' % (i + 1, k)] = fs[i][0] if len(fs) > i else None
        # Praat's default floor, 75 Hz: a 40 ms window. With 50 Hz (60 ms) a vowel at the start of
        # an utterance, whose F0 falls fast, is read an octave low (itit: 57 Hz for 112; Praat
        # finds nothing there at all): report.py, A2.
        m['f0_50_hz'] = f0_at(x, rate, mid, fmin=75.0)
        f3 = [f[2][0] for _, f in formant_track(x, rate, a, b) if len(f) >= 3]
        m['F3_min_hz'] = min(f3) if f3 else None
    if cls in ('fricative', 'affricate'):
        sm = spectrum_moments(x, rate, a + 0.2 * (b - a), b - 0.2 * (b - a))
        if sm:
            m.update({'%s' % k: v for k, v in sm.items()})
    if cls in ('stop', 'affricate'):
        st = stop_timing(x, rate, a, b)
        if st:
            m.update(st)
    if cls == 'nasal':
        nz = nasal_zero(x, rate, a + 0.2 * (b - a), b - 0.2 * (b - a))
        if nz:
            m.update(antiformant_hz=nz['zero_hz'], antiformant_depth_db=nz['depth_db'], murmur_F1_hz=nz['murmur_f1_hz'])
    if cls == 'vowel':
        tc = tone_contour(x, rate, a, b)
        if tc:
            m['f0_contour_hz'] = tc['hz']
    return m


def requested(frames, times, ph):
    """What the engine asked the synthesiser for over a phone: values at its middle frame, the
    formant trajectory at 20/50/80 %, and the frame-level timing of noise and voicing."""
    from engine import P
    a, b = ph['start_ms'], ph['end_ms']
    idx = np.nonzero((times >= a) & (times < b))[0]
    if len(idx) == 0:
        return {}
    def at(frac):
        return frames[idx[min(len(idx) - 1, int(frac * len(idx)))]]
    mid = at(0.5)
    r = dict(duration_ms=b - a, f0_hz=mid[P['f0']] / 10.0)
    # the frames' F0 over the 40 ms an F0 measurement at the middle hears (analysis.f0_at, 75 Hz)
    c = (a + b) / 2.0
    win = np.nonzero((times >= c - 20) & (times < c + 20) & (frames[:, P['av']] > 0))[0]
    r['f0_mid40_hz'] = float(frames[win, P['f0']].mean() / 10.0) if len(win) else None
    for n in ('av', 'ah', 'af', 'ab', 'oq', 'tl', 'fnp', 'bnp', 'fnz', 'bnz', 'a2f', 'a3f', 'a4f', 'a5f', 'a6f'):
        r[n] = int(mid[P[n]])
    for i in range(1, 6):
        r['F%d_hz' % i] = int(mid[P['f%d' % i]])
        r['B%d_hz' % i] = int(mid[P['b%d' % i]])
    for k, frac in (('20', 0.2), ('80', 0.8)):
        for i in range(1, 4):
            r['F%d_%s_hz' % (i, k)] = int(at(frac)[P['f%d' % i]])
    fr = frames[idx]
    voiced = fr[:, P['av']] > 0
    noisy = (fr[:, P['af']] > 0) | (fr[:, P['ab']] > 0) | (fr[:, P['ah']] > 0)
    r['voiced_frames'] = int(voiced.sum())
    r['noise_frames'] = int(noisy.sum())
    r['frames'] = int(len(idx))
    return r
