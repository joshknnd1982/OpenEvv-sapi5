"""The sweep's checks for what is not one segment (playbook Phase 4e, 4g; DESIGN.md 10.2). MIT licence.

T-tone      a tone letter or tone mark on a syllable: its F0 at the start and the end of the vowel against
            the voice's own five-level stave, measured on the same syllable in the same run
T-register  downstep, upstep: the syllables after the mark against the same phrase unmarked
T-slope     global rise, fall: the slope of F0 over the syllables, marked against unmarked
T-stress    a stress mark: the syllable it marks against the same syllable unstressed (and secondary
            against primary)
T-boundary  a group boundary or a link: the pause and the pre-boundary vowel, marked against the plain
            word boundary; a link: the consonant before it begins the next syllable and no pause parts them
T-syllable  a syllable break: the syllable begins where it is typed, and the signal differs from the
            other division
T-sequence  a tie bar: the tied pair is one segment (no loss reported, said as one phone where the template
            has one), shorter than the untied pair, its friction shorter than the plain fricative's
T-double    a double articulation joined by a tie bar (k͡p): one segment with one closure and one release,
            its closure against the second stop's alone, the vowel before nearer the first stop's F2 and
            the vowel after beginning lower than after the second (4g, D66)

Each check compares two renders of the same text but for the mark, so the voice's own pitch and timing
cancel; its numbers are the entry's specification (`spec`), each with its provenance.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'docs', 'tts-extension', 'harness'))
import analysis as A  # noqa: E402

# not [i]: its F1 (217 Hz on this voice) sits on the second harmonic, where the trackers fail (D15)
VOWELS = ('a', 'e', 'u')
CHECKS = ('T-tone', 'T-register', 'T-slope', 'T-stress', 'T-boundary', 'T-syllable', 'T-sequence', 'T-double')
MIN_MS = 8.0     # the contrast minimum of sweep.py for a time
MIN_ST = 1.0     # a pitch difference that counts: about a third of a Chao step on a 9-semitone stave


def check_of(e):
    # the marks written on one segment (̩ ̯ and the like name T-syllable too) are the sweep's own
    if e.get('kind') not in ('tone', 'syllable-mark', 'boundary', 'tie'):
        return None
    for c in (e.get('tests') or {}).get('checks', []):
        if c in CHECKS:
            return c
    return None


def _v(x):
    return x['v'] if isinstance(x, dict) else x


def _tone_text(e, v, levels_of=None):
    """`mV` with the entry's tone written as the chart writes it: a diacritic over the vowel, a letter
    after the syllable."""
    return 'm%s%s' % (v, e['ipa'])


def contexts(t, sid):
    e = t.sounds[sid]
    chk = check_of(e)
    x = e['ipa']
    out = []
    if chk == 'T-tone':
        # the tone on a syllable of each vowel, and the five level letters on the same syllable: the stave
        for v in VOWELS:
            out.append(('tone_%s' % v, 'm%s%s' % (v, x)))
            for lv, letter in zip((1, 2, 3, 4, 5), '˩˨˧˦˥'):
                out.append(('stave%d_%s' % (lv, v), 'm%s%s' % (v, letter)))
    elif chk == 'T-register':
        lv = '˥' if e.get('register') == 'down' else '˩'
        for v in VOWELS:
            s = 'p%s%s' % (v, lv)
            out.append(('plain_%s' % v, s * 4))
            out.append(('marked_%s' % v, s * 2 + x + s * 2))
    elif chk == 'T-slope':
        for v in VOWELS:
            out.append(('plain_%s' % v, ('p%s' % v) * 6))
            out.append(('marked_%s' % v, x + ('p%s' % v) * 6))
    elif chk == 'T-stress':
        for v in VOWELS:
            s = 'p%s' % v
            out.append(('unstressed_%s' % v, s + s + 'ˈ' + s))
            out.append(('primary_%s' % v, s + 'ˈ' + s + s))
            if e.get('stress') == 'secondary':
                out.append(('marked_%s' % v, s + x + s + 'ˈ' + s))
    elif chk == 'T-boundary':
        for v in VOWELS:
            if e.get('boundary') == 'linked':
                # a word-final consonant before a vowel-initial word: linked, it is the next syllable's onset
                out.append(('plain_%s' % v, 'p%sk %s' % (v, v)))
                out.append(('marked_%s' % v, 'p%sk%s%s' % (v, x, v)))
            else:
                w = 'p%sm%s' % (v, v)
                out.append(('plain_%s' % v, w + ' ' + w))
                out.append(('marked_%s' % v, w + x + w))
                if e.get('boundary') == 'major':
                    out.append(('minor_%s' % v, w + '|' + w))
    elif chk == 'T-syllable':
        for v in VOWELS:
            out.append(('plain_%s' % v, 'ˈ%sp%st%s' % (v, x, v)))     # ap.ta: the other division
            out.append(('marked_%s' % v, 'ˈ%s%spt%s' % (v, x, v)))    # a.pta
    elif chk == 'T-sequence':
        for pair in (e.get('tests') or {}).get('pairs', []):
            tied = pair.replace('͡', x)
            untied = pair.replace('͡', '')
            fric = untied[-1]
            for v in VOWELS:
                out.append(('tied_%s_%s' % (untied, v), 'ˈ%s%s%s' % (v, tied, v)))
                out.append(('untied_%s_%s' % (untied, v), 'ˈ%s%s%s' % (v, untied, v)))
                out.append(('fric_%s_%s' % (untied, v), 'ˈ%s%s%s' % (v, fric, v)))
    if 'T-double' in (e.get('tests') or {}).get('checks', []):
        # a double articulation: tied, untied, and each of its two stops alone, in the same contexts
        for pair in (e.get('tests') or {}).get('doubles', []):
            one, two = pair.split('͡')
            for v in VOWELS:
                for k, s in (('dbl', pair.replace('͡', x)), ('dblu', one + two), ('dbl1', one), ('dbl2', two)):
                    out.append(('%s_%s%s_%s' % (k, one, two, v), 'ˈ%s%s%s' % (v, s, v)))
    return out


def _f0s(x, rate, a, b, asked=None):
    """F0 (semitones re 100 Hz) over a stretch. A value an octave from what the frames asked for at
    that moment is folded back: the tracker's octave error, not the voice's (the frames settle which
    octave; the value itself is the signal's)."""
    out = []
    for t, f in A.f0_track(x, rate, a, b, step_ms=5.0, fmin=70.0):
        if not f:
            continue
        s = A.semitones(f, 100.0)
        ref = asked(t) if asked else None
        rel = (t - a) / float(b - a) if b > a else 0.0
        if ref is not None:
            while s - ref < -8:
                s += 12.0
            while s - ref > 8:
                s -= 12.0
        out.append((rel, s))
    return out


def _median(xs):
    xs = sorted(x for x in xs if x is not None)
    n = len(xs)
    return None if not n else (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0)


def measure(x, rate, phones, frames=None, stops=False):
    """Per syllable nucleus (each vowel phone): its time, length, level, and F0 at its start, middle
    and end (semitones re 100 Hz: the medians of its first, middle and last 30 per cent); the pauses
    inside the text; the said string's syllables are the front-end's business (`said')."""
    syl, pauses = [], []
    asked = None
    if frames is not None:
        import engine as E
        tt = E.frame_times(frames)
        f0 = frames[:, E.P['f0']] / 10.0

        def asked(t):
            k = max(0, min(len(tt) - 1, int((tt <= t).sum()) - 1))
            return A.semitones(f0[k], 100.0) if f0[k] > 0 else None
    sounding = [i for i, ph in enumerate(phones) if ph['cls'] != 'silence']
    first, last = (sounding[0], sounding[-1]) if sounding else (0, -1)
    for i, ph in enumerate(phones):
        a, b = ph['start_ms'], ph['end_ms']
        if ph['cls'] == 'silence':
            if first < i < last:
                pauses.append(b - a)
            continue
        if ph['cls'] != 'vowel':
            continue
        n = b - a
        tr = _f0s(x, rate, a + 0.05 * n, b - 0.05 * n, asked) if n >= 30 else []
        st = [v for _, v in tr]
        k = max(1, int(round(len(st) * 0.3)))
        syl.append(dict(i=i, name=ph['name'], start_ms=a, ms=n, db=A.intensity_db(x, rate, a, b) if n > 5 else None,
                        f0_start=_median(st[:k]) if st else None, f0_mid=_median(st) if st else None,
                        f0_end=_median(st[-k:]) if st else None,
                        track=[(round(0.05 + 0.9 * r, 3), round(v, 2)) for r, v in tr]))
    cons = [dict(i=i, name=ph['name'], ms=ph['end_ms'] - ph['start_ms']) for i, ph in enumerate(phones)
            if ph['cls'] not in ('silence', 'vowel')]
    out = dict(syllables=syl, pauses=pauses, consonants=cons,
               span_ms=(phones[last]['end_ms'] - phones[first]['start_ms']) if sounding else 0)
    if stops and frames is not None and len(syl) >= 2:
        out['stops'] = stop_span(x, rate, phones, frames, syl[0]['i'], syl[1]['i'])
    return out


def stop_span(x, rate, phones, frames, iv1, iv2):
    """T-double: the consonants between two vowels as one stretch. Its closure (the quiet part before
    the burst, A.stop_timing), how many releases it has (rises of the energy above 1.5 kHz by 12 dB or
    more over the stretch's quietest, each with 5 ms or more under 6 dB over it since the last one, in
    all, not in a row: a voice bar keeps a voiced closure above that line for most of its length), and the F2 at the
    vowels' edges as the sweep reads a locus: 12 ms from the end of the vowel before over 20 ms, and
    12 ms after the voice begins in the vowel after."""
    import numpy as np
    from scipy import signal
    import engine as E
    a, b = phones[iv1]['end_ms'], phones[iv2]['start_ms']
    if b - a < 10:
        return None
    st = A.stop_timing(x, rate, a, b) or {}
    y = A._seg(x, rate, a, b + 10.0)
    hp = signal.sosfilt(signal.butter(4, 1500.0 / (rate / 2.0), 'high', output='sos'), y)
    hop = max(1, int(round(rate / 1000.0)))
    db = 10 * np.log10(np.array([np.mean(hp[i * hop:(i + 1) * hop] ** 2) for i in range(len(hp) // hop)]) + 1e-12)
    floor = float(np.sort(db)[:max(1, len(db) // 5)].mean())
    releases, low = 0, 0
    for d in db:
        if d < floor + 6:
            low += 1
        elif d >= floor + 12 and low >= 5:
            releases += 1
            low = 0
    tt = E.frame_times(frames)
    von = next((tt[j] for j in range(len(tt)) if phones[iv2]['start_ms'] <= tt[j] < phones[iv2]['end_ms']
                and frames[j, E.P['av']] > 0), phones[iv2]['start_ms'])
    f_prev = A.formants(x, rate, a - 12.0, win_ms=20.0)
    f_next = A.formants(x, rate, von + 12.0, win_ms=20.0)
    return dict(ms=b - a, closure_ms=st.get('closure_ms'), vot_ms=st.get('vot_ms'), releases=releases,
                prev_F2=f_prev[1][0] if len(f_prev) >= 2 else None, next_F2=f_next[1][0] if len(f_next) >= 2 else None)


def _tgt(name, target, measured, ok, **kw):
    return name, dict(target=target, measured=None if measured is None else round(measured, 2), within=bool(ok), **kw)


def judge(t, sid, cases):
    e = t.sounds[sid]
    spec = e.get('spec') or {}
    chk = check_of(e)
    P = {cid: c['pros'] for cid, c in cases.items()}
    out = {}
    summ = {}

    def put(*a, **kw):
        k, v = _tgt(*a, **kw)
        out[k] = v

    if chk == 'T-tone':
        levels = e['levels']
        tol = _v(spec.get('tolerance_steps', 0.5))
        for v in VOWELS:
            stave, drift = {}, {}
            for lv in range(1, 6):
                s = (P.get('stave%d_%s' % (lv, v)) or {}).get('syllables') or [{}]
                stave[lv] = (s[-1].get('f0_start'), s[-1].get('f0_end'))
                if None not in stave[lv] and s[-1].get('ms'):
                    # the level's own movement across the syllable (st/s), from the middle of its
                    # start window to the middle of its end window: the phrase's ending and declination
                    drift[lv] = (stave[lv][1] - stave[lv][0]) / (0.63 * s[-1]['ms'] / 1000.0)
            st1 = [x for x in (stave[1][0], stave[5][0]) if x is not None]
            if len(st1) < 2:
                put('%s: the stave' % v, 'levels 1 and 5 measured', None, False)
                continue
            step_s = (stave[5][0] - stave[1][0]) / 4.0
            step_e = (stave[5][1] - stave[1][1]) / 4.0 if None not in (stave[5][1], stave[1][1]) else step_s
            span = stave[5][0] - stave[1][0]
            summ['stave_span_st_%s' % v] = round(span, 2)
            want = _v(spec.get('stave_span_st')) if spec.get('stave_span_st') else None
            if want is not None and len(levels) == 1 and levels[0] in (1, 5):
                # the two ends of the stave: their distance is the voice's tonal range
                put('%s: stave span (st)' % v, want, span, abs(span - want) <= 0.25 * want)
            s = ((P.get('tone_%s' % v) or {}).get('syllables') or [{}])[-1]
            a, b = s.get('f0_start'), s.get('f0_end')
            # where the voice should be: level L on the stave at the same moment of the same syllable
            ws = stave[1][0] + (levels[0] - 1) * step_s
            we = stave[1][1] + (levels[-1] - 1) * step_e if stave[1][1] is not None else None
            summ['tone_%s' % v] = dict(start=a, end=b, want_start=round(ws, 2), want_end=we and round(we, 2))
            if len(levels) == 1 and levels[0] in (1, 5):
                # level 1 and level 5 are the stave's own ends (the same text): their check is the span
                continue
            if len(levels) == 1:
                put('%s: start (st re 100 Hz)' % v, round(ws, 2), a, a is not None and abs(a - ws) <= tol * abs(step_s))
            if len(levels) > 1:
                # A contour is a movement with a speed (xu1999): from where the first leg turns (the
                # extreme of the first half: a fall's peak, a rise's trough, which real speech reaches
                # late) to the end window, in the direction the levels say, at least the speed the
                # specification asks. A three-level contour: each leg in its direction. Both read against the
                # stave (D65).
                tr = s.get('track') or []
                ms = s.get('ms') or 0
                legs = list(zip(levels[:-1], levels[1:]))
                d0 = math.copysign(1, legs[0][1] - legs[0][0])
                half = [(r, v) for r, v in tr if r <= 0.5]
                ext = (max(half, key=lambda p: p[1] * d0 * -1) if half else None)
                put('%s: start (st re 100 Hz)' % v, round(ws, 2), ext and ext[1],
                    ext is not None and abs(ext[1] - ws) <= 2 * tol * abs(step_s))
                if len(legs) == 1:
                    # The speed is the speakers' (xu1999, a syllable inside the sentence), so it is
                    # read against the stave as every other target is: less the drift its own levels
                    # show over the same syllable, which is the phrase's ending, not the tone (D65).
                    want_rate = _v(spec['min_rate_st_s'][('rise' if d0 > 0 else 'fall')]) if spec.get(
                        'min_rate_st_s') else 10.0
                    dt = (0.815 - ext[0]) * ms / 1000.0 if ext else 0
                    own = [drift[lv] for lv in sorted(set(levels)) if lv in drift]
                    sd = sum(own) / len(own) if len(own) == len(set(levels)) else None
                    raw = (b - ext[1]) / dt if ext and b is not None and dt > 0.02 else None
                    rate_ = raw - sd if raw is not None and sd is not None else None
                    summ['tone_%s' % v].update(rate_st_s=rate_ and round(rate_, 1), raw_rate_st_s=raw and round(raw, 1),
                                               stave_drift_st_s=sd and round(sd, 1))
                    put('%s: speed of the %s (st/s)' % (v, 'rise' if d0 > 0 else 'fall'), '%+.0f or more' % (
                        d0 * want_rate), rate_, rate_ is not None and rate_ * d0 >= want_rate)
                else:
                    d1 = math.copysign(1, legs[1][1] - legs[1][0])
                    mid = [(r, v_) for r, v_ in tr if 0.25 <= r <= 0.75]
                    turn = max(mid, key=lambda p: p[1] * d1 * -1) if mid else None
                    l1 = None if not (ext and turn) else turn[1] - ext[1]
                    l2 = None if not (turn and b is not None) else b - turn[1]
                    summ['tone_%s' % v]['raw_legs_st'] = [l1, l2]
                    # each leg less the drift its own two levels show on the stave over the leg's
                    # time, as the speed is (D65, the review's finding 1)
                    for n_, (lv0, lv1) in enumerate(legs):
                        dl = [drift[x] for x in (lv0, lv1) if x in drift]
                        span_r = (turn[0] - ext[0]) if n_ == 0 and ext and turn else (
                            (0.815 - turn[0]) if n_ == 1 and turn else None)
                        if len(dl) < 2 or span_r is None:
                            l1, l2 = (None, l2) if n_ == 0 else (l1, None)
                        elif n_ == 0 and l1 is not None:
                            l1 -= sum(dl) / 2.0 * span_r * ms / 1000.0
                        elif n_ == 1 and l2 is not None:
                            l2 -= sum(dl) / 2.0 * span_r * ms / 1000.0
                    summ['tone_%s' % v]['legs_st'] = [l1, l2]
                    for name, leg, d in (('first', l1, d0), ('second', l2, d1)):
                        put('%s: %s leg (st)' % (v, name), '%s at least %.1f' % ('+' if d > 0 else '-', _v(spec.get('legs_min_st', 0.5))),
                            leg, leg is not None and leg * d >= _v(spec.get('legs_min_st', 0.5)))
            else:
                lvl_end = b is not None and we is not None and abs(b - we) <= tol * abs(step_e) * 1.5
                put('%s: end (st re 100 Hz)' % v, we and round(we, 2), b, lvl_end)
    elif chk in ('T-register', 'T-slope'):
        for v in VOWELS:
            sp = [s.get('f0_mid') for s in (P.get('plain_%s' % v) or {}).get('syllables', [])]
            sm = [s.get('f0_mid') for s in (P.get('marked_%s' % v) or {}).get('syllables', [])]
            if len(sp) != len(sm) or not sp:
                put('%s: syllables' % v, len(sp), len(sm), False)
                continue
            d = [None if None in (a, b) else b - a for a, b in zip(sp, sm)]
            summ['difference_st_%s' % v] = [None if x is None else round(x, 2) for x in d]
            if chk == 'T-register':
                want = _v(spec['step_st'])
                # the step: the syllables after the mark; it lasts to the end of the phrase
                after = [x for x in d[2:] if x is not None]
                put('%s: step after the mark (st)' % v, want, _median(after),
                    bool(after) and abs(_median(after) - want) <= max(1.0, 0.4 * abs(want)))
                put('%s: still there on the last syllable' % v, '%+d' % (1 if want > 0 else -1), d[-1],
                    d[-1] is not None and d[-1] * want >= 0.5 * want * want)
                put('%s: nothing before the mark' % v, 0, _median([x for x in d[:2] if x is not None]),
                    all(x is not None and abs(x) < MIN_ST for x in d[:2]))
            else:
                want = _v(spec['st_per_syllable'])
                pts = [(i, x) for i, x in enumerate(d) if x is not None]
                if len(pts) < 3:
                    put('%s: slope (st a syllable)' % v, want, None, False)
                    continue
                n = len(pts)
                mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
                k = sum((p[0] - mx) * (p[1] - my) for p in pts) / sum((p[0] - mx) ** 2 for p in pts)
                summ['slope_st_%s' % v] = round(k, 2)
                put('%s: slope against unmarked (st a syllable)' % v, want, k, abs(k - want) <= 0.5 * abs(want))
    elif chk == 'T-stress':
        ratio = _v(spec['duration_ratio']) if spec.get('duration_ratio') else None
        for v in VOWELS:
            mid = lambda cid: (((P.get(cid) or {}).get('syllables') or [{}, {}, {}])[1:2] or [{}])[0]  # noqa: E731
            un, pri = mid('unstressed_%s' % v), mid('primary_%s' % v)
            if e.get('stress') == 'primary':
                a, b = pri.get('ms'), un.get('ms')
                summ['middle_ms_%s' % v] = dict(stressed=a, unstressed=b, f0=[pri.get('f0_mid'), un.get('f0_mid')],
                                               db=[pri.get('db'), un.get('db')])
                put('%s: stressed longer than unstressed (ms)' % v, '+%d' % MIN_MS, None if None in (a, b) else a - b,
                    None not in (a, b) and a - b >= MIN_MS)
                if ratio is not None and None not in (a, b) and b:
                    put('%s: stressed / unstressed length' % v, ratio, a / b, abs(a / b - ratio) <= 0.25 * ratio)
            else:
                sec = mid('marked_%s' % v)
                a, b, c = sec.get('ms'), un.get('ms'), pri.get('ms')
                summ['middle_ms_%s' % v] = dict(secondary=a, unstressed=b, primary=c)
                put('%s: secondary longer than unstressed (ms)' % v, '+%d' % MIN_MS, None if None in (a, b) else a - b,
                    None not in (a, b) and a - b >= MIN_MS)
                put('%s: primary longer than secondary (ms)' % v, '+%d' % MIN_MS, None if None in (a, c) else c - a,
                    None not in (a, c) and c - a >= MIN_MS)
    elif chk == 'T-boundary':
        kind = e.get('boundary')
        for v in VOWELS:
            pp, pm = P.get('plain_%s' % v) or {}, P.get('marked_%s' % v) or {}
            gp, gm = sum(pp.get('pauses', [])), sum(pm.get('pauses', []))
            summ['pause_ms_%s' % v] = dict(plain=gp, marked=gm)
            if kind == 'linked':
                put('%s: no pause where linked (ms)' % v, '< 20', gm, gm < 20)
                # the consonant before the link is the onset of the vowel after it (front-end), and the
                # signal differs from the unlinked words
                said = cases['marked_%s' % v].get('said', '')
                ok = '.0k%s' % {'a': 'A'}.get(v, v) in said or '.0k' in said
                put('%s: the linked consonant begins the next syllable' % v, 'k as onset', None, ok)
                kp = [c['ms'] for c in pp.get('consonants', []) if c['name'] == 'k']
                km = [c['ms'] for c in pm.get('consonants', []) if c['name'] == 'k']
                d = (km[0] - kp[0]) if kp and km else None
                put('%s: the consonant differs from the unlinked one (ms)' % v, '|d| >= %d' % MIN_MS, d,
                    d is not None and abs(d) >= MIN_MS)
            else:
                lo, hi = _v(spec.get('pause_min_ms', 0)), _v(spec.get('pause_max_ms', 1e9))
                # a pause the plain word boundary does not have, within what the languages measured span
                put('%s: pause at the mark (ms)' % v, '%g to %g, more than unmarked' % (lo, hi), gm,
                    lo <= gm <= hi and gm - gp >= MIN_MS)
                if kind == 'major':
                    gn = sum((P.get('minor_%s' % v) or {}).get('pauses', []))
                    summ['pause_ms_%s' % v]['minor'] = gn
                    put('%s: longer than a minor group\'s pause (ms)' % v, '+%d' % MIN_MS, gm - gn, gm - gn >= MIN_MS)
                # the vowel before the boundary is longer than before a plain word boundary
                sp, sm = pp.get('syllables', []), pm.get('syllables', [])
                if len(sp) >= 2 and len(sm) >= 2:
                    put('%s: pre-boundary vowel longer (ms)' % v, '+%d' % MIN_MS, sm[1]['ms'] - sp[1]['ms'],
                        sm[1]['ms'] - sp[1]['ms'] >= MIN_MS)
                    summ['prelengthening_ratio_%s' % v] = round(sm[1]['ms'] / sp[1]['ms'], 2) if sp[1]['ms'] else None
    elif chk == 'T-syllable':
        for v in VOWELS:
            said = cases['marked_%s' % v].get('said', '')
            ok = '.0pt' in said
            put('%s: the syllable begins where the mark is' % v, '.0pt', None, ok)
            pp, pm = P.get('plain_%s' % v) or {}, P.get('marked_%s' % v) or {}
            durs_p = [s['ms'] for s in pp.get('syllables', [])] + [c['ms'] for c in pp.get('consonants', [])]
            durs_m = [s['ms'] for s in pm.get('syllables', [])] + [c['ms'] for c in pm.get('consonants', [])]
            d = max((abs(a - b) for a, b in zip(durs_m, durs_p)), default=None) if len(durs_m) == len(durs_p) else None
            summ['largest_change_ms_%s' % v] = d
            put('%s: the signal differs from the other division (ms)' % v, '>= %d' % MIN_MS, d,
                d is not None and d >= MIN_MS)
    elif chk == 'T-sequence':
        for pair in (e.get('tests') or {}).get('pairs', []):
            untied = pair.replace('͡', '')
            for v in VOWELS:
                ct = cases.get('tied_%s_%s' % (untied, v))
                pt, pu, pf = (P.get('%s_%s_%s' % (k, untied, v)) or {} for k in ('tied', 'untied', 'fric'))
                if ct is None:
                    continue
                lost = [d for d in ct['diag'] + ct.get('fe_diag', []) if d['level'] == 'loss']
                put('%s %s: one segment, nothing lost' % (pair, v), 'no loss', len(lost), not lost)
                ct_ms = sum(c['ms'] for c in pt.get('consonants', []))
                cu_ms = sum(c['ms'] for c in pu.get('consonants', []))
                said_t = ct.get('said', '').split('`')[-1]
                said_u = (cases.get('untied_%s_%s' % (untied, v)) or {}).get('said', '').split('`')[-1]
                put('%s %s: said as one segment, not as the untied pair' % (pair, v), 'differs from %s' % said_u.strip(),
                    None, said_t != said_u)
                put('%s %s: not longer than the untied pair (ms)' % (pair, v), '<= 0', ct_ms - cu_ms, ct_ms <= cu_ms)
                ft = (pt.get('consonants') or [{}])[-1].get('ms')
                ff = (pf.get('consonants') or [{}])[-1].get('ms')
                put('%s %s: its friction shorter than the plain fricative (ms)' % (pair, v), '-%d' % MIN_MS,
                    None if None in (ft, ff) else ft - ff, None not in (ft, ff) and ff - ft >= MIN_MS)
                summ.setdefault('ms', {})['%s_%s' % (untied, v)] = dict(tied=ct_ms, untied=cu_ms, friction=ft,
                                                                       plain_fricative=ff)
    else:
        put('no check', chk, None, False)
    if 'T-double' in (e.get('tests') or {}).get('checks', []):
        # a double articulation (4g): one segment with one closure and one release; its closure longer
        # than the second stop's alone, within the ratio the specification gives, and shorter than the
        # untied pair; the vowel before nearer the first stop's F2 (connell_1991: most often velar-like),
        # the vowel after beginning lower than after the second stop (connell_1991; burns_shaw_2023 Table 1b);
        # the vowel before is the first stop's by construction (its part carries the first stop's keys)
        lo = _v(spec.get('double_closure_ratio_min', 1.0))
        hi = _v(spec.get('double_closure_ratio_max', 1.3))
        for pair in (e.get('tests') or {}).get('doubles', []):
            one, two = pair.split('͡')
            near_in, ratios = [], []
            for v in VOWELS:
                key = '%s%s_%s' % (one, two, v)
                ct = cases.get('dbl_' + key)
                if ct is None:
                    continue
                s_t, s_u, s_1, s_2 = ((P.get('%s_%s' % (k, key)) or {}).get('stops') or {}
                                      for k in ('dbl', 'dblu', 'dbl1', 'dbl2'))
                lost = [d for d in ct['diag'] + ct.get('fe_diag', []) if d['level'] == 'loss']
                put('%s %s: one segment, nothing lost' % (pair, v), 'no loss', len(lost), not lost)
                put('%s %s: one release' % (pair, v), 1, s_t.get('releases'), s_t.get('releases') == 1)
                c_t, c_2, u_ms, t_ms = s_t.get('closure_ms'), s_2.get('closure_ms'), s_u.get('ms'), s_t.get('ms')
                put('%s %s: shorter than the untied pair (ms)' % (pair, v), '< %s' % u_ms, t_ms,
                    None not in (t_ms, u_ms) and t_ms < u_ms)
                if None not in (c_t, c_2) and c_2 > 0:
                    ratios.append(c_t / c_2)
                p_t, p_1, p_2 = s_t.get('prev_F2'), s_1.get('prev_F2'), s_2.get('prev_F2')
                n_t, n_2 = s_t.get('next_F2'), s_2.get('next_F2')
                if None not in (p_t, p_1, p_2):
                    near_in.append(abs(p_t - p_1) < abs(p_t - p_2))
                # lower than the plain second stop's by what the harness tells in the same context
                # (sweep.contrast_ok's 1.5 per cent, at least 15 Hz): the cited cue is a lower locus
                need = max(0.015 * n_2, 15.0) if n_2 is not None else None
                put('%s %s: the vowel after begins lower than after %s (F2 Hz)' % (pair, v, two),
                    '<= %s' % (n_2 and round(n_2 - need)), n_t, None not in (n_t, n_2) and n_2 - n_t >= need)
                summ.setdefault('double', {})[key] = dict(
                    closure_ms=c_t, plain_closure_ms=c_2, ms=t_ms, untied_ms=u_ms, releases=s_t.get('releases'),
                    vot_ms=s_t.get('vot_ms'), prev_F2=[p_t, p_1, p_2], next_F2=[n_t, s_1.get('next_F2'), n_2])
            r = _median(ratios)
            put('%s: closure against the plain %s\'s (median ratio)' % (pair, two), '%.2f to %.2f' % (lo, hi), r,
                r is not None and lo <= r <= hi)
            put('%s: the vowel before nearer the %s\'s F2 (contexts)' % (pair, one), 'most of %d' % len(near_in),
                sum(near_in), bool(near_in) and sum(near_in) * 2 > len(near_in))
    return dict(passed=bool(out) and all(o['within'] for o in out.values()), targets=out, empty=not spec,
                unchecked=not out), summ
