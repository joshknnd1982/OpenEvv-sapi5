"""Synthetic test signals whose answers are known, for proving the analyser (selftest.py).

Independent of the engine: a glottal pulse train through second-order resonators in cascade
(Klatt 1980's digital resonator, y[n] = A x[n] + B y[n-1] + C y[n-2]), noise through band-pass
filters, and an antiresonator for a nasal zero. Every signal is 16-bit-scaled float at `rate`.
"""

import math

import numpy as np
from scipy import signal

RATE = 11025


def resonator(x, f, bw, rate=RATE):
    c = -math.exp(-2 * math.pi * bw / rate)
    b = 2 * math.exp(-math.pi * bw / rate) * math.cos(2 * math.pi * f / rate)
    a = 1 - b - c
    return signal.lfilter([a], [1, -b, -c], x)


def antiresonator(x, f, bw, rate=RATE):
    c = -math.exp(-2 * math.pi * bw / rate)
    b = 2 * math.exp(-math.pi * bw / rate) * math.cos(2 * math.pi * f / rate)
    a = 1 - b - c
    return signal.lfilter([1 / a, -b / a, -c / a], [1], x)


def pulses(f0, dur_ms, rate=RATE, open_q=0.5):
    """A glottal source with F0 given as a number or a function of time in seconds: a
    Rosenberg-like pulse every period, differentiated (lip radiation)."""
    n = int(dur_ms * rate / 1000.0)
    out = np.zeros(n)
    t = 0.0
    while True:
        f = f0(t) if callable(f0) else f0
        i = int(t * rate)
        if i >= n:
            break
        period = rate / f
        op = int(period * open_q)
        k = np.arange(op)
        pulse = 0.5 * (1 - np.cos(math.pi * k / max(op, 1))) if op > 0 else np.zeros(0)
        seg = out[i:i + op]
        seg += pulse[:len(seg)]
        t += 1.0 / f
    return np.diff(out, prepend=0.0)


def vowel(formants, f0=120.0, dur_ms=300.0, rate=RATE):
    """formants: [(F, B), ...]. Cascade, then scaled to peak 20000."""
    y = pulses(f0, dur_ms, rate)
    for f, bw in formants:
        y = resonator(y, f, bw, rate)
    return 20000 * y / np.max(np.abs(y))


def noise_band(lo_hz, hi_hz, dur_ms=200.0, rate=RATE, seed=1):
    rng = np.random.default_rng(seed)
    y = rng.standard_normal(int(dur_ms * rate / 1000.0))
    sos = signal.butter(6, [lo_hz / (rate / 2.0), min(hi_hz / (rate / 2.0), 0.999)], 'band', output='sos')
    y = signal.sosfilt(sos, y)
    return 8000 * y / np.max(np.abs(y))


def stop_cv(closure_ms=80.0, vot_ms=40.0, prevoiced_ms=0.0, rate=RATE, seed=2):
    """Lead-in vowel, closure (silent, or voiced for its last prevoiced_ms), a 3 ms burst,
    aspiration noise for vot_ms, then a vowel. Returns the signal and the true times in ms."""
    rng = np.random.default_rng(seed)
    v = vowel([(700, 80), (1200, 90), (2600, 150)], dur_ms=150.0, rate=rate)
    clo = np.zeros(int(closure_ms * rate / 1000.0))
    if prevoiced_ms:
        n = int(prevoiced_ms * rate / 1000.0)
        clo[-n:] = 0.03 * resonator(pulses(110.0, prevoiced_ms, rate), 250, 100, rate)[:n] * 20000 / 3
    burst = rng.standard_normal(int(0.003 * rate)) * 12000
    n_asp = int(vot_ms * rate / 1000.0)
    asp = (signal.sosfilt(signal.butter(4, [500 / (rate / 2.0), 4500 / (rate / 2.0)], 'band', output='sos'),
                          rng.standard_normal(n_asp)) * 2500 if n_asp else np.zeros(0))
    v2 = vowel([(700, 80), (1200, 90), (2600, 150)], dur_ms=200.0, rate=rate)
    y = np.concatenate([v, clo, burst, asp, v2])
    t_burst = 150.0 + closure_ms
    return y, dict(closure_start_ms=150.0, burst_ms=t_burst, voicing_onset_ms=t_burst + 3.0 + vot_ms,
                   vot_ms=3.0 + vot_ms, stop_end_ms=t_burst + 3.0 + vot_ms)


def nasal(f1=280.0, zero=1200.0, f0=110.0, dur_ms=250.0, rate=RATE):
    y = pulses(f0, dur_ms, rate)
    for f, bw in ((f1, 60), (1100 if zero > 1500 else 1700, 120), (2500, 200)):
        y = resonator(y, f, bw, rate)
    y = antiresonator(y, zero, 80, rate)
    return 20000 * y / np.max(np.abs(y))
