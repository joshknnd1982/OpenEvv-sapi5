#!/usr/bin/env python3
"""Measurements that say whether a sound is the sound it was meant to be.

Two things are measured and they are kept apart. What the engine asked the
synthesiser for is read off the frames, and is exact. What came out is
measured in the sound itself, the same way whoever made it: the engine's
rendering and eSpeak NG's rendering of the same word are put through the
same code, so that a difference between them is a difference in the speech
and not in the measuring.

    from verify import espeak_wav, release_and_voice, formants_at
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import measure  # noqa: E402

ESPEAK = os.environ.get('OPENEVV_ESPEAK') or os.path.join(ROOT, 'build_frontend_x64', 'bin', 'espeak-ng.exe')
ESPEAK_PATH = os.environ.get('OPENEVV_ESPEAK_PATH') or os.path.join(ROOT, 'dist')


def espeak_wav(voice, text, speed=None, phonemes=False):
    """eSpeak NG's own rendering of a text: (samples, rate)."""
    work = tempfile.mkdtemp(prefix='esp')
    try:
        src = os.path.join(work, 't.txt')
        out = os.path.join(work, 't.wav')
        with open(src, 'w', encoding='utf-8') as f:
            f.write(text)
        cmd = [ESPEAK, '--path=' + ESPEAK_PATH, '-v', voice, '-w', out, '-f', src]
        if speed:
            cmd += ['-s', str(speed)]
        subprocess.run(cmd, capture_output=True, timeout=120)
        x, rate = measure.read_wav(out)
        return x, rate
    finally:
        for n in os.listdir(work):
            try:
                os.remove(os.path.join(work, n))
            except OSError:
                pass
        try:
            os.rmdir(work)
        except OSError:
            pass


def espeak_ipa(voice, text):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.txt', delete=False) as f:
        f.write(text)
        tmp = f.name
    try:
        r = subprocess.run([ESPEAK, '--path=' + ESPEAK_PATH, '-v', voice, '--ipa', '-q', '-f', tmp],
                           capture_output=True, timeout=60)
        return r.stdout.decode('utf-8', 'replace').strip()
    finally:
        os.unlink(tmp)


def lowpass_half(x):
    """Half the sample rate, with what is above the new half taken out."""
    n = 63
    k = np.arange(n) - (n - 1) / 2.0
    h = np.sinc(k / 2.0) * np.hamming(n) / 2.0
    y = np.convolve(x, h, mode='same')
    return y[::2]


def at_rate(x, rate, want=11025):
    while rate >= want * 2 - 100:
        x = lowpass_half(x)
        rate //= 2
    return x, rate


def highpass(x, rate, hz=2000.0):
    n = 101
    k = np.arange(n) - (n - 1) / 2.0
    fc = hz / rate
    h = -2 * fc * np.sinc(2 * fc * k) * np.hamming(n)
    h[(n - 1) // 2] += 1.0
    return np.convolve(x, h, mode='same')


def energy_db(x, rate, hop=0.002, window=0.006):
    n = max(8, int(window * rate))
    step = max(1, int(hop * rate))
    out = []
    for start in range(0, max(1, len(x) - n), step):
        f = x[start:start + n]
        out.append(10 * np.log10(np.mean(f * f) + 1e-3))
    return np.array(out), step / float(rate)


def voiced_track(x, rate, hop=0.002, window=0.030, fmin=70.0, fmax=250.0, strength=0.6):
    """Where the sound is periodic: a boolean every `hop' seconds. Only what is
    below 1 kHz is looked at, as the voice bar behind a closure is all there,
    and only periods a voice can have: breath through the first formant
    repeats itself at the formant's own rate, three hundred times a second
    and more, and is not voice."""
    n = int(window * rate)
    step = max(1, int(hop * rate))
    k = np.arange(101) - 50.0
    fc = 1000.0 / rate
    h = 2 * fc * np.sinc(2 * fc * k) * np.hamming(101)
    low = np.convolve(x, h, mode='same')
    peak = np.max(np.abs(low)) if len(low) else 0
    lo = int(rate / fmax)
    hi = int(rate / fmin)
    out = []
    for start in range(0, max(1, len(low) - n), step):
        f = low[start:start + n]
        f = f - f.mean()
        e = float(np.dot(f, f))
        if peak <= 0 or np.sqrt(e / len(f)) < 0.01 * peak:
            out.append(False)
            continue
        best = 0.0
        for lag in range(lo, min(hi, n - 2)):
            a = f[:-lag]
            b = f[lag:]
            d = np.sqrt(float(np.dot(a, a)) * float(np.dot(b, b)))
            if d > 0:
                c = float(np.dot(a, b)) / d
                if c > best:
                    best = c
        out.append(best >= strength)
    return np.array(out), step / float(rate), window


def release_and_voice(x, rate, after=0.0, before=None):
    """The release of the stop a word begins with and the start of the voice,
    in seconds, looked for between `after' and `before'.

    A word said by itself begins in silence. If the first sound out of the
    silence is periodic, the stop is voiced behind its closure, and its
    release is where the noise above 2 kHz comes up: the voice onset time is
    negative, by as long as the voice had been going. If the first sound is
    noise, that is the release, and the voice begins where the sound becomes
    periodic and stays so. Answers (release, voice)."""
    if before is None:
        before = len(x) / float(rate)
    full, dt = energy_db(x, rate)
    i0 = int(after / dt)
    i1 = min(len(full), int(before / dt))
    if i1 - i0 < 10:
        return None, None
    seg = full[i0:i1]
    top = np.percentile(seg, 95)
    if top - np.min(seg) < 15:
        return None, None
    # the first sound that is within 38 dB of the loudest: a burst is some
    # 20 dB below the vowel after it, and the silence before it far below
    level = top - 38
    first = None
    for i in range(i0, i1 - 2):
        if full[i] > level and full[i + 1] > level and full[i + 2] > level:
            first = i * dt
            break
    if first is None:
        return None, None
    v, vdt, win = voiced_track(x, rate)

    def voiced_from(t):
        run = 0
        for j in range(int(max(0.0, t - win / 2) / vdt), min(len(v), int(before / vdt))):
            if v[j]:
                run += 1
                if run >= 6:
                    return (j - run + 1) * vdt + win / 2
            else:
                run = 0
        return None

    voice = voiced_from(first)
    if voice is None:
        return first, None
    hp = highpass(x, rate)
    e, _ = energy_db(hp, rate)
    k0 = int(first / dt)
    k1 = min(len(e), k0 + 5)
    # what the first sound is made of: a burst is noise, and most of it is
    # above 2 kHz; the voice behind a closure has nothing up there
    low_first = np.mean(full[k0:k1]) - np.mean(e[k0:k1]) > 15
    if voice - first < win / 2 + 0.008 and low_first:
        # the voice was there from the first: a voiced closure. The release
        # is where the noise of the burst comes up, or the vowel opens
        j0 = int(first / dt)
        j1 = min(len(e), int(min(before, first + 0.25) / dt))
        if j1 - j0 > 8:
            quiet = np.percentile(e[j0:j0 + max(4, (j1 - j0) // 4)], 50)
            for j in range(j0 + 4, j1 - 1):
                if e[j] > quiet + 10 and e[j + 1] > quiet + 10:
                    return j * dt, first
        return first, first
    return first, voice


def formants_at(x, rate, t, window=0.025):
    """F1 to F4 about a moment."""
    n = int(window * rate)
    start = int(t * rate) - n // 2
    start = max(0, min(len(x) - n, start))
    got = measure.formants_of(x[start:start + n], rate)
    hz = [f for f, b in got]
    return (hz + [0, 0, 0, 0])[:4]


def steady_formants(x, rate, t0, t1):
    return measure.formants_between(x, rate, t0, t1)


def frames_between(frames, a, b):
    return [f for f in frames if a <= f['at'] < b]


def frame_release(frames, stop, after):
    """From the frames: when the stop lets go and when the voice begins, in
    milliseconds of what sounded. `stop' and `after' are the stretches of
    the stop and of what follows it."""
    own = frames_between(frames, stop['out_a'], stop['out_b'])
    nxt = frames_between(frames, after['out_a'], after['out_b'])
    release = None
    shut = False
    began = None
    for f in own:
        closed = f['af'] == 0 and f['ah'] == 0 and (f['av'] < 30 or f['f1'] <= 250 and f['av'] < 40)
        if closed:
            shut = True
            if f['av'] > 0 and began is None:
                began = f['at']
        elif shut and (f['af'] > 0 or f['ah'] > 0) and release is None:
            release = f['at']
    if release is None:
        for f in nxt:
            if f['af'] > 0 or f['ah'] > 0 or f['av'] >= 30:
                release = f['at']
                break
    voice = None
    for f in nxt:
        if f['av'] >= 30:
            voice = f['at']
            break
    if began is not None and release is not None:
        # the voice was going behind the closure
        voice = began
    return release, voice


def write_wav(path, x, rate):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(np.clip(x, -32768, 32767).astype('<i2').tobytes())
