#!/usr/bin/env python3
"""Measures speech: the fundamental frequency and the formants of a wave file.

Nothing here knows how the sound was made. It is the check on everything that
does: what the engine asked the synthesiser for is one thing, and what came
out of the loudspeaker is another, and a claim about how a language sounds is
a claim about the second.

    python measure.py f0 file.wav            pitch every 10 ms
    python measure.py formants file.wav      F1 to F4 every 10 ms

The pitch is tracked by normalised autocorrelation with a path chosen over
the whole utterance (so that an octave error in one frame cannot stand), and
the formants by linear prediction: autocorrelation method, order chosen for
the sample rate, roots of the predictor polynomial, narrow ones kept.
"""
import sys
import wave

import numpy as np


def read_wav(path):
    with wave.open(path, 'rb') as w:
        rate = w.getframerate()
        n = w.getnframes()
        ch = w.getnchannels()
        width = w.getsampwidth()
        raw = w.readframes(n)
    if width == 2:
        x = np.frombuffer(raw, dtype='<i2').astype(np.float64)
    elif width == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) * 256.0
    else:
        raise ValueError('unsupported sample width %d' % width)
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, rate


# ---- pitch ---------------------------------------------------------------

def _candidates(frame, rate, fmin, fmax, keep=4):
    """The strongest periods in one frame: (hertz, strength) pairs."""
    frame = frame - frame.mean()
    e = float(np.dot(frame, frame))
    if e < 1e-3:
        return []
    n = len(frame)
    size = 1
    while size < 2 * n:
        size *= 2
    spec = np.fft.rfft(frame * np.hanning(n), size)
    ac = np.fft.irfft(spec * np.conj(spec))[:n]
    wac = np.fft.irfft(np.abs(np.fft.rfft(np.hanning(n), size)) ** 2)[:n]
    wac[wac < 1e-9] = 1e-9
    ac = ac / wac
    if ac[0] <= 0:
        return []
    ac = ac / ac[0]
    lo = max(2, int(rate / fmax))
    hi = min(n - 2, int(rate / fmin))
    out = []
    for lag in range(lo, hi):
        if ac[lag] > ac[lag - 1] and ac[lag] >= ac[lag + 1] and ac[lag] > 0.25:
            a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]
            d = a - 2 * b + c
            shift = 0.5 * (a - c) / d if d != 0 else 0.0
            peak = b - 0.25 * (a - c) * shift
            out.append((rate / (lag + shift), min(peak, 1.0)))
    out.sort(key=lambda p: -p[1])
    return out[:keep]


def track_f0(x, rate, hop=0.010, window=0.040, fmin=50.0, fmax=500.0):
    """Answers (times, f0): f0 is nought where the frame is not voiced."""
    n = int(window * rate)
    step = int(hop * rate)
    peak = np.max(np.abs(x)) if len(x) else 0
    times, cands = [], []
    for start in range(0, max(1, len(x) - n), step):
        frame = x[start:start + n]
        rms = np.sqrt(np.mean(frame ** 2)) if len(frame) else 0
        c = _candidates(frame, rate, fmin, fmax) if peak > 0 and rms > 0.02 * peak else []
        times.append((start + n / 2.0) / rate)
        cands.append(c)
    # The path: each frame is unvoiced or one of its candidates, and a jump
    # in pitch between neighbouring frames costs what it is in octaves.
    m = len(cands)
    if m == 0:
        return np.array([]), np.array([])
    options = [[(0.0, 0.0)] + c for c in cands]   # (hz, strength); hz 0 = unvoiced
    cost = []
    back = []
    for i in range(m):
        ci, bi = [], []
        for hz, s in options[i]:
            local = 0.45 if hz == 0 else (1.0 - s)
            if i == 0:
                ci.append(local)
                bi.append(-1)
                continue
            best, arg = None, -1
            for j, (phz, ps) in enumerate(options[i - 1]):
                if hz == 0 and phz == 0:
                    t = 0.0
                elif hz == 0 or phz == 0:
                    t = 0.2
                else:
                    t = 1.2 * abs(np.log2(hz / phz))
                v = cost[i - 1][j] + t
                if best is None or v < best:
                    best, arg = v, j
            ci.append(best + local)
            bi.append(arg)
        cost.append(ci)
        back.append(bi)
    k = int(np.argmin(cost[-1]))
    f0 = np.zeros(m)
    for i in range(m - 1, -1, -1):
        f0[i] = options[i][k][0]
        k = back[i][k]
    return np.array(times), f0


# ---- formants ------------------------------------------------------------

def _lpc(frame, order):
    r = np.correlate(frame, frame, mode='full')[len(frame) - 1:len(frame) + order]
    if r[0] <= 0:
        return None
    a = np.zeros(order + 1)
    a[0] = 1.0
    e = r[0]
    for i in range(1, order + 1):
        acc = r[i] + np.dot(a[1:i], r[i - 1:0:-1])
        k = -acc / e
        prev = a.copy()
        for j in range(1, i):
            a[j] = prev[j] + k * prev[i - j]
        a[i] = k
        e *= (1.0 - k * k)
        if e <= 0:
            return None
    return a


def formants_of(frame, rate, order=None, max_bw=600.0):
    """The formants of one frame, lowest first: (hertz, bandwidth) pairs."""
    if order is None:
        order = 2 + int(rate / 1000)
    frame = frame - frame.mean()
    frame = np.append(frame[0], frame[1:] - 0.97 * frame[:-1])
    frame = frame * np.hamming(len(frame))
    a = _lpc(frame, order)
    if a is None:
        return []
    out = []
    for z in np.roots(a):
        if z.imag <= 0.01:
            continue
        hz = np.angle(z) * rate / (2 * np.pi)
        bw = -np.log(abs(z)) * rate / np.pi
        if hz > 90 and hz < rate / 2 - 50 and bw < max_bw:
            out.append((hz, bw))
    out.sort()
    return out


def track_formants(x, rate, hop=0.010, window=0.025, order=None):
    n = int(window * rate)
    step = int(hop * rate)
    peak = np.max(np.abs(x)) if len(x) else 0
    times, rows = [], []
    for start in range(0, max(1, len(x) - n), step):
        frame = x[start:start + n]
        rms = np.sqrt(np.mean(frame ** 2))
        times.append((start + n / 2.0) / rate)
        rows.append(formants_of(frame, rate, order) if peak > 0 and rms > 0.03 * peak else [])
    return np.array(times), rows


def formants_between(x, rate, t0, t1, order=None):
    """The median of each of the first four formants over a stretch."""
    times, rows = track_formants(x, rate, order=order)
    got = [[], [], [], []]
    for t, row in zip(times, rows):
        if t < t0 or t > t1 or len(row) < 3:
            continue
        for i in range(min(4, len(row))):
            got[i].append(row[i][0])
    return [float(np.median(g)) if g else 0.0 for g in got]


def semitones(hz, ref):
    return 12.0 * np.log2(hz / ref)


if __name__ == '__main__':
    what, path = sys.argv[1], sys.argv[2]
    x, rate = read_wav(path)
    if what == 'f0':
        t, f = track_f0(x, rate)
        for a, b in zip(t, f):
            print('%.3f\t%.1f' % (a, b))
    else:
        t, rows = track_formants(x, rate)
        for a, row in zip(t, rows):
            print('%.3f\t%s' % (a, '\t'.join('%.0f' % hz for hz, bw in row[:4])))
