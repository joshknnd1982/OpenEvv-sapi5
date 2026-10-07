"""The symbol-by-symbol sweep (playbook Phase 4i, R19f; DESIGN.md 3.4 and 10). MIT licence.

    python engine/ipa/sweep.py [ids or sections ...] [--template dedx] [--pack hi] [--apply]

Every entry asked for (all, a section such as `pulmonic`, or ids such as U+0288) is said by the
real engine, from IPA, through the staged front-end and the staged reference module (EVV_STAGE):
a letter alone and in three vowel contexts, a vowel alone and between three consonants, a mark on
the base sounds its entry names. Each case is measured with the harness and the entry is judged:

  A0  nothing lost on the way (no `loss` from the front-end or the accent layer), and the letter
      is not a module phone standing in for it unmoved (a carrier at a feature distance with no
      key of the entry's own: a silent substitution, R7)
  A1  the sound sounded: frames with voice or noise over it (a stop: a closure and a burst found)
  A2  the signal carries what the frames asked for (report.check_a over the cases)
  B3  every target of the entry's specification is met within its tolerance (prove.py's)
  B2  every contrast the entry's tests name holds, in the direction named, by at least the
      smallest difference this harness can tell from its own error

The proof is written to ipa/proofs/<id>.json: the inputs, what the front-end made of them, what
was reported, the measures of the sound and its neighbours, every check and its evidence. With
`--apply` an entry that passes all of them takes the state its plan names (mapped, composed or
created), level 2 (engine-verified on the reference template) and its proof path; one that fails
is left as it was. Nothing else in the table is touched.
"""

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
import adapter as AD  # noqa: E402
import compose_test as CT  # noqa: E402
import prosody as PZ  # noqa: E402
import prove as PR  # noqa: E402
import table as T  # noqa: E402
import analysis as A  # noqa: E402
import engine as E  # noqa: E402
import golden as G  # noqa: E402
import report as RP  # noqa: E402

PROOFS = os.path.join(ROOT, 'ipa', 'proofs')
SWEEP_WORK = os.path.join(E.WORK, 'sweep')
VOWELS_AROUND = ('a', 'i', 'u')
CONSONANTS_AROUND = ('p', 't', 'k')
# the smallest difference a contrast must show to count: above what the harness tells apart from
# its own error on synthetic speech (D15: a low F1 near a harmonic; formants 2 to 4 per cent)
CONTRAST_MIN = {'hz_rel': 0.04, 'ms': 8.0, 'db': 2.0, 'count': 1}


def manner(e):
    """stop / nasal / trill / tap / fricative / approximant / vowel / click, from the features."""
    f = e['features']
    if f['class'] == 'vowel':
        return 'vowel'
    if f.get('airstream') == 'click':
        return 'click'
    s = f['stricture']
    if s == 'closure':
        return 'nasal' if f.get('nasal') else 'stop'
    return {'trill': 'trill', 'tap': 'tap', 'friction': 'fricative', 'approximation': 'approximant'}[s]


def contexts(t, sid):
    """[(case id, IPA, the index of the target segment among the said syllable nuclei...)]: the
    inputs of an entry. A letter alone and in three contexts; a mark on the bases its tests name."""
    e = t.sounds[sid]
    tests = e.get('tests') or {}
    if PZ.check_of(e):
        # tones, stress, boundaries, syllable breaks, ties: prosody.py
        return PZ.contexts(t, sid)
    if e['kind'] == 'base':
        x = e['ipa']
        if manner(e) == 'vowel':
            return [('alone', x)] + [('%s_%s' % (c, c), 'ˈ%s%s%s' % (c, x, c)) for c in CONSONANTS_AROUND]
        return [('alone', x)] + [('%s_%s' % (v, v), 'ˈ%s%s%s' % (v, x, v)) for v in VOWELS_AROUND]
    out = []
    follow = t.sounds[tests['follow']]['ipa'] if tests.get('follow') else ''
    for base in tests.get('bases', []):
        b = t.sounds[base]
        for variant, x in (('plain', b['ipa']), ('marked', b['ipa'] + e['ipa'])):
            if e['ipa'] == '\u0329':
                # a syllabic consonant: after a stressed syllable, the word ending in it
                out.append(('%s_%s_pa' % (base, variant), 'ˈpa%s%s' % ('p' if variant == 'marked' else 'pa', x)))
            elif manner(b) == 'vowel':
                out += [('%s_%s_%s' % (base, variant, c), 'ˈ%s%s%s' % (c, x, c)) for c in CONSONANTS_AROUND]
            else:
                out += [('%s_%s_%s' % (base, variant, v), 'ˈ%s%s%s%s' % (v, x, follow, v)) for v in VOWELS_AROUND]
    return out


def target_phones(phones, case_id, kind):
    """The phones a case is about: in a context, everything between the first and the last
    sounding phone (a vowel between consonants, a consonant between vowels, its pieces too);
    alone, every sounding phone but a schwa the front-end put in."""
    sounding = [i for i, ph in enumerate(phones) if ph['cls'] != 'silence']
    if not sounding:
        return [], None, None
    if case_id == 'alone':
        idx = [i for i in sounding if not (ph_is_schwa(phones[i]) and len(sounding) > 1)]
        return idx, None, None
    if case_id.endswith('_pa'):
        # `ˈpapn̩' (or `ˈpapan'): the last sounding phone, and a schwa just before it
        idx = [sounding[-1]]
        if len(sounding) >= 2 and phones[sounding[-2]]['name'] == '@':
            idx = [sounding[-2], sounding[-1]]
        return idx, None, None
    if len(sounding) < 3:
        return sounding, None, None
    return sounding[1:-1], sounding[0], sounding[-1]


def ph_is_schwa(ph):
    return ph['name'] == '@' and ph.get('sound') in (None, '-')


def measure(r, p, case_id, man=None, layer=None):
    """The case measured: the harness's per-phone measures, the target and its neighbours, and the
    measures of DESIGN.md 10.2 that the class needs."""
    m = G.measure_case(r, p.phone_module)
    x, rate = E.read_wav(r['wav'])
    phones = m['phones']
    idx, before, after = target_phones(phones, case_id, None)
    if layer and layer.get('name') and case_id != 'alone' and len(idx) >= 2:
        # A sound the accent layer makes out of the start of the vowel after it (`<h', `<q') is
        # inside that vowel's phone: it is the stretch from the vowel's start while the frames
        # are its own (no voice, or, voiced, breath on the voice), at most the time it was given.
        v = phones[idx[1]]
        tt = E.frame_times(r['frames'])
        fr = r['frames']
        k = [i for i in range(len(tt)) if v['start_ms'] <= tt[i] < v['end_ms']]
        n = 0
        for i in k:
            av, ah = fr[i, E.P['av']], fr[i, E.P['ah']]
            mine = av == 0 or (layer.get('voi') and ah > 0)
            if not mine or tt[i] - v['start_ms'] >= layer['ms'] + 10:
                break
            n += 1
        made_end = v['start_ms'] + sum(fr[i, 0] for i in k[:n])
        made = dict(name=layer['name'], sound=v.get('sound'), cls='made', start_ms=v['start_ms'], end_ms=made_end,
                    meas=dict(A.phone_metrics(x, rate, dict(start_ms=v['start_ms'], end_ms=max(made_end, v['start_ms'] + 5)),
                                              'fricative')),
                    req=A.requested(r['frames'], tt, dict(start_ms=v['start_ms'], end_ms=max(made_end, v['start_ms'] + 5))))
        made['meas'] = {a: b for a, b in made['meas'].items() if not isinstance(b, list)}
        phones = phones[:idx[1]] + [made, dict(v, start_ms=made_end)] + phones[idx[1] + 1:]
        m = dict(m, phones=phones)
        idx, before, after = [idx[1]], idx[0], idx[1] + 1
    tgt = [phones[i] for i in idx]
    out = dict(phones=[dict(name=ph['name'], sound=ph.get('sound'), cls=ph['cls'], start_ms=ph['start_ms'],
                            end_ms=ph['end_ms'], meas=ph.get('meas'), req={k: v for k, v in (ph.get('req') or {}).items()
                                                                           if not isinstance(v, list)})
                       for ph in phones],
               target=idx, before=before, after=after, gold=m)
    if tgt and man in ('approximant', 'trill', 'tap', 'nasal'):
        for ph in tgt:
            me = ph.setdefault('meas', {}) if ph.get('meas') is not None else ph.setdefault('meas', {})
            if me.get('F1_50_hz') is None and ph['end_ms'] - ph['start_ms'] >= 20:
                fs = A.formants(x, rate, (ph['start_ms'] + ph['end_ms']) / 2.0)
                for i in range(3):
                    me['F%d_50_hz' % (i + 1)] = fs[i][0] if len(fs) > i else None
    if tgt and man == 'fricative':
        # the noise peak above the voice: a voiced fricative's own spectrum below 800 Hz is the
        # voice's (it read 601 Hz for every one); the literature's peaks are of the noise
        for ph in tgt:
            a_, b_ = ph['start_ms'], ph['end_ms']
            sm = A.spectrum_moments(x, rate, a_ + 0.2 * (b_ - a_), b_ - 0.2 * (b_ - a_),
                                    fmin=max(800.0, 0.6 * (layer or {}).get('peak_target', 0)))
            if sm:
                ph.setdefault('meas', {})['peak_hz'] = sm['peak_hz']
                ph['meas']['centroid_hz'] = sm['centroid_hz']
    if tgt:
        a, b = tgt[0]['start_ms'], tgt[-1]['end_ms']
        ex = dict(span_ms=[a, b])
        mod = A.modulation(x, rate, a, b)
        if mod:
            ex['modulation'] = mod
        if any(ph['cls'] in ('stop', 'affricate') for ph in tgt):
            ex['vot_long_ms'] = A.vot_long(x, rate, a, b)
            # a release (T-release): noise in the frames from where the closure shuts to 25 ms after
            # the stop (this module lets p, t, k go inside their own stretch); and the closure:
            # shut frames at least 20 ms long, the signal there 20 dB or more under the next phone
            t_ = E.frame_times(r['frames'])
            fr0 = r['frames']
            closed = [i for i in range(len(t_)) if a <= t_[i] < b and fr0[i, E.P['af']] == 0
                      and fr0[i, E.P['ah']] == 0 and fr0[i, E.P['av']] < 30]
            c0 = t_[closed[0]] if closed else b
            win = ((t_ > c0) if closed else (t_ >= b)) & (t_ < b + 25)
            # AF only: the synthesiser sounds the bypass (AB) only with AF on, and p's frames carry
            # AB with AF at nought
            ex['burst_found'] = int(bool((fr0[win, E.P['af']] > 0).any()))
            if closed and after is not None and phones[after]['cls'] != 'silence':
                c1 = t_[closed[-1]] + fr0[closed[-1], 0]
                nv = phones[after]
                if c1 - c0 >= 20 and nv['end_ms'] - nv['start_ms'] >= 30:
                    # from 10 ms in: the resonators ring on from the vowel before for that long
                    m_ = (nv['start_ms'] + nv['end_ms']) / 2.0
                    ex['closure_quiet'] = int(A.intensity_db(x, rate, c0 + 10, c1) <= A.intensity_db(x, rate, m_ - 15, m_ + 15) - 20)
            st = next((ph['meas'] for ph in tgt if (ph.get('meas') or {}).get('burst_ms') is not None), None)
            if st and st.get('voicing_onset_ms') is None:
                # a voice that begins more than 80 ms after the stop (an ejective's, an aspirated
                # stop's): the same timing looked for 250 ms past it, as vot_long does
                st = dict(st, **{k: v for k, v in (A.stop_timing(x, rate, a, b, after_ms=250.0) or {}).items()
                                 if k == 'voicing_onset_ms'})
            bm = st['burst_ms'] if st else None
            if case_id != 'alone':
                # T-airstream: the voice's level below 400 Hz through the closure, from 15 ms after
                # the closure begins (the module's stop includes the vowel's transition, so where
                # its frames stop asking for a vowel: voice under 40 or none; and the 10 ms
                # envelope reaches back) to the release: an implosive's swells, a plain voiced
                # stop's fades
                shut = [tt for tt, av in zip(t_, r['frames'][:, E.P['av']]) if a <= tt < (bm or b) and av < 40]
                if shut and (bm or b) - shut[0] >= 35:
                    ex['voicing_slope'] = A.voicing_slope(x, rate, shut[0] + 15.0, bm or b)
                # T-click: the release's transient: its RMS against the RMS of the middle 30 ms of
                # the vowel after it (miller_shah2009's relative amplitude), its length (at most to
                # the voice's onset) and its spectrum
                von = st.get('voicing_onset_ms') if st else None
                # a burst is measured over a silent closure only (30 dB clear of it): over a voice
                # bar the finder reads the voice's own pulses (b between a's: 0 to 3 ms, -30 dB)
                voiced_closure = any(av > 0 for tt, av in zip(t_, r['frames'][:, E.P['av']])
                                     if shut and shut[0] <= tt < (bm or b))
                bu = A.burst(x, rate, bm - 5.0, b + 40.0) if bm is not None and not voiced_closure else None
                # the vowel's onset: where the voice begins after the release, or where the next
                # phone begins (a prevoiced stop's voice begins before it)
                v0 = von if von and bu and von > bu['start_ms'] else (
                    phones[after]['start_ms'] if after is not None and phones[after]['cls'] != 'silence' else None)
                if bu and v0 and v0 - bu['start_ms'] >= 2.0:
                    # the burst lasts from its start until its level first falls 20 dB under its own
                    # peak: burst() alone counts from the closure's level, digital silence here,
                    # and ran on into the vowel
                    s0 = bu['start_ms']
                    env, st_ = A.envelope_db(x, rate, s0, v0, hop_ms=0.5, win_ms=1.0)
                    blen = 1.0
                    if len(env):
                        top = int(env.argmax())
                        end = next((i for i in range(top, len(env)) if env[i] < env[top] - 20.0), len(env))
                        blen = max(1.0, end * st_)
                    ex['burst_len_ms'] = blen
                    sm = A.spectrum_moments(x, rate, s0, s0 + max(2.0, blen), fmin=300.0)
                    ex['burst_centroid_hz'] = sm['centroid_hz'] if sm else None
                    nv = phones[after] if after is not None else None
                    if nv and nv['cls'] != 'silence' and nv['end_ms'] - nv['start_ms'] >= 40:
                        m_ = (nv['start_ms'] + nv['end_ms']) / 2.0
                        ex['burst_db'] = (A.intensity_db(x, rate, s0, s0 + blen)
                                          - A.intensity_db(x, rate, m_ - 15.0, m_ + 15.0))
                # the gap between the release and the voice: breath without voice in it
                # (aspiration) or none (an ejective's glottis held shut), as a share of its frames;
                # the module's vowels carry breath with their voice, which is not aspiration
                if bm is not None and von is not None and von - bm >= 10:
                    gap = (t_ >= bm + 5) & (t_ < von - 5)
                    if gap.any():
                        fr_ = r['frames'][gap]
                        ex['gap_breath_frac'] = float(((fr_[:, E.P['ah']] > 0) & (fr_[:, E.P['av']] == 0)).mean())
        last = tgt[-1]
        if last['cls'] in ('vowel', 'nasal', 'liquid', 'glide') and last['end_ms'] - last['start_ms'] >= 40:
            mid = (last['start_ms'] + last['end_ms']) / 2.0
            ex['h1h2_db'] = A.h1_h2(x, rate, mid)
            f1 = (last.get('meas') or {}).get('F1_50_hz')
            if f1:
                ex['a1_p0_db'] = A.a1_p0(x, rate, mid, f1)
        ex['schwa_ms'] = sum(ph['end_ms'] - ph['start_ms'] for ph in tgt if ph['name'] == '@')
        out['extra'] = ex
    # the vowels' formants at the consonant's edges, 12 ms from the boundary over 20 ms: where a
    # locus shows; at 20 per cent into the vowel the transition is mostly over
    edges = {}
    for which, i, at in (('prev', before, -12.0), ('next', after, 12.0)):
        if i is None or phones[i]['cls'] == 'silence' or phones[i]['end_ms'] - phones[i]['start_ms'] < 30:
            continue
        t_ = (phones[i]['end_ms'] if at < 0 else phones[i]['start_ms']) + at
        fs = A.formants(x, rate, t_, win_ms=20.0)
        for k in (1, 2, 3):
            edges['%s_F%d_%s' % (which, k, '80' if at < 0 else '20')] = fs[k - 1][0] if len(fs) >= k else None
    out['edges'] = edges
    return out


def summary(cases, man):
    """One number per measure for the entry, the median over its contexts (alone left out where a
    context exists, since an isolated consonant is said after a schwa the front-end puts in)."""
    def vals(fn):
        xs = []
        for cid, c in cases.items():
            if cid == 'alone' and len(cases) > 1 and man != 'vowel':
                continue
            v = fn(c)
            if v is not None:
                xs.append(v)
        # the median: one context's tracker error (a low F1 near a harmonic, D15; a burst read as
        # a formant in a short vowel) must not carry the summary
        xs.sort()
        n = len(xs)
        return (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0) if xs else None

    def tmeas(key):
        def fn(c):
            ts = [c['phones'][i] for i in c['target']]
            xs = [(ph.get('meas') or {}).get(key) for ph in ts]
            xs = [v for v in xs if v is not None]
            return xs[0] if xs else None
        return fn

    s = {}
    for k in ('F1_50_hz', 'F2_50_hz', 'F3_50_hz', 'F3_min_hz', 'peak_hz', 'centroid_hz', 'vot_ms', 'closure_ms',
              'murmur_F1_hz', 'antiformant_hz', 'intensity_db', 'f0_50_hz'):
        v = vals(tmeas(k))
        if v is not None:
            s[k] = round(v, 1)
    for k in (1, 2, 3):
        # the formants the engine made at the sound (its locus, for a consonant), from the frames
        v = vals(lambda c: _mean([(c['phones'][i].get('req') or {}).get('F%d_hz' % k) for i in c['target']]))
        if v is not None:
            s['req_F%d_hz' % k] = round(v, 1)
    if s.get('f0_50_hz'):
        s['f0_hz'] = s['f0_50_hz']
    s['duration_ms'] = vals(lambda c: (c['phones'][c['target'][-1]]['end_ms'] - c['phones'][c['target'][0]]['start_ms'])
                            if c['target'] else None)
    for k in (1, 2, 3):
        v = vals(lambda c: _mean([c['edges'].get('prev_F%d_80' % k), c['edges'].get('next_F%d_20' % k)]))
        if v is not None:
            s['edge_F%d' % k] = round(v, 1)
    v = vals(lambda c: (c.get('extra') or {}).get('vot_long_ms'))
    if v is not None:
        s['vot_long_ms'] = round(v, 1)
    for k in ('dips', 'rate_hz', 'closed_ms'):
        v = vals(lambda c: ((c.get('extra') or {}).get('modulation') or {}).get(k))
        if v is not None:
            s['mod_' + k] = round(v, 2)
    for k in ('h1h2_db', 'a1_p0_db', 'burst_found', 'schwa_ms', 'voicing_slope', 'burst_db', 'burst_len_ms',
              'burst_centroid_hz', 'gap_breath_frac'):
        v = vals(lambda c: (c.get('extra') or {}).get(k))
        if v is not None:
            s['%s' % k] = round(v, 2)
    for k in ('voicing_slope', 'burst_db', 'burst_len_ms', 'burst_centroid_hz'):
        # in how many contexts the measure was found: a median of one is not a proof (check_b3)
        s['n_' + k] = sum(1 for cid, c in cases.items() if cid != 'alone' and (c.get('extra') or {}).get(k) is not None)
    if s.get('F2_50_hz') is not None:
        # how near the centre: for the centralizing marks (larger is nearer the table's ə)
        s['F2_toward_centre'] = round(-abs(s['F2_50_hz'] - 1454.0), 1)
    vf = vals(lambda c: _voiced_frac(c))
    if vf is not None:
        s['voiced_frac'] = round(vf, 3)
    return s


def _voiced_frac(c):
    fr = sum((c['phones'][i].get('req') or {}).get('frames', 0) for i in c['target'])
    vo = sum((c['phones'][i].get('req') or {}).get('voiced_frames', 0) for i in c['target'])
    return vo / fr if fr else None


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def check_a1(cases, man):
    bad = []
    for cid, c in cases.items():
        if not c['target']:
            bad.append('%s: nothing sounded' % cid)
            continue
        ts = [c['phones'][i] for i in c['target']]
        if all(ph['cls'] == 'made' for ph in ts):
            if not any(ph['end_ms'] > ph['start_ms'] for ph in ts):
                bad.append('%s: the made sound has no frame of its own' % cid)
            continue
        if man in ('stop', 'click') or all(ph['cls'] == 'stop' for ph in ts):
            # a release in the signal: stop_timing's burst or closure, or a transient over a silent
            # closure (a weak, low burst, p's before [i], has no 12 dB jump above 1.5 kHz)
            if not any((ph.get('meas') or {}).get('burst_ms') is not None or (ph.get('meas') or {}).get('closure_ms')
                       for ph in ts) and (c.get('extra') or {}).get('burst_len_ms') is None                     and not (c.get('extra') or {}).get('closure_quiet') and cid != 'alone':
                bad.append('%s: no closure or burst found' % cid)
            continue
        if all((ph.get('req') or {}).get('voiced_frames', 0) + (ph.get('req') or {}).get('noise_frames', 0) == 0
               for ph in ts):
            bad.append('%s: %s has no sounding frame' % (cid, '+'.join(ph['name'] for ph in ts)))
    return dict(passed=not bad, problems=bad)


def check_b3(e, s):
    """The specification's targets against the summary measures (prove.py's tolerances)."""
    spec = e.get('spec') or {}
    v = lambda x: x['v'] if isinstance(x, dict) else x  # noqa: E731
    want = {}
    for k, x in (spec.get('formants') or {}).items():
        if k != 'F4':   # realised, but the harness measures F1 to F3 only
            want[k] = ('%s_50_hz' % k, v(x))
    if 'vot_ms' in spec:
        want['vot_ms'] = ('vot_ms', v(spec['vot_ms']))
    if 'peak_hz' in (spec.get('noise') or {}):
        want['peak_hz'] = ('peak_hz', v(spec['noise']['peak_hz']))
    dur = (spec.get('duration') or {}).get('inherent_ms')
    out = {}
    # a trill's rate (the modulation of its level) within 15 per cent; a tap's or trill's closed
    # time within 40 per cent (the level measure finds the closure's edges only to a few ms)
    trill = spec.get('trill') or {}
    if 'rate_hz' in trill:
        got, w = s.get('mod_rate_hz'), v(trill['rate_hz'])
        out['trill_rate_hz'] = dict(target=w, measured=got, within=got is not None and abs(got - w) <= 0.15 * w)
    for k in ('trill', 'tap'):
        if 'closed_ms' in (spec.get(k) or {}):
            got, w = s.get('mod_closed_ms'), v(spec[k]['closed_ms'])
            out['%s_closed_ms' % k] = dict(target=w, measured=got,
                                           within=got is not None and abs(got - w) <= 0.4 * w)
    for k, (mk, w) in want.items():
        got = s.get(mk)
        ok = PR.within(k if k != 'peak_hz' else 'peak', got, w)
        if k == 'F1' and got is not None:
            # a low F1 sits among the voice's harmonics, where the tracker is known to err (D15):
            # the tolerance check A uses for F1, the larger of 8 per cent and 0.75 F0
            ok = abs(got - w) <= max(0.08 * w, 0.75 * s.get('f0_hz', 110.0))
        out[k] = dict(target=w, measured=got, within=ok)
    if dur is not None:
        # a length is set as a share of the carrier's and the module's rhythm moves it by context:
        # within a quarter
        got = s.get('duration_ms')
        out['duration_ms'] = dict(target=v(dur), measured=got,
                                  within=got is not None and abs(got - v(dur)) <= 0.25 * v(dur))
    # T-click: the release's burst (DESIGN.md C10): its length within 40 per cent (and 5 ms, the
    # frame's step), its level against the vowel within 3 dB, its spectral centre within 25 per
    # cent (the sources' speakers spread so: miller_shah2009 figures 2 and 6)
    for k, mk in (('length_ms', 'burst_len_ms'), ('level_db', 'burst_db'), ('centroid_hz', 'burst_centroid_hz')):
        x = (spec.get('burst') or {}).get(k)
        if x is not None:
            # the median of the contexts, found in two of the three at least
            got, w, n = s.get(mk), v(x), s.get('n_' + mk, 0)
            tol = {'length_ms': max(0.4 * w, 5.0), 'level_db': 3.0, 'centroid_hz': 0.25 * w}[k]
            out['burst %s' % k] = dict(target=w, measured=got, contexts=n,
                                       within=got is not None and n >= 2 and abs(got - w) <= tol)
    # T-airstream: the voice's level through the closure, dB per 10 ms, within 1 (the measure's
    # own error is 0.4 on a synthetic swell, selftest.py; the source is a curve read from a figure)
    x = (spec.get('closure') or {}).get('voicing_slope_db10')
    if x is not None:
        got, w, n = s.get('voicing_slope'), v(x), s.get('n_voicing_slope', 0)
        out['closure voicing slope'] = dict(target=w, measured=got, contexts=n,
                                            within=got is not None and n >= 2 and abs(got - w) <= 1.0)
    for k, x in (spec.get('locus') or {}).items():
        # a locus is where the consonant sends the formants; a closure has no formants to measure in
        # the signal, so this is checked in the frames the engine made at the consonant (the
        # synthesiser realising them is check A2's business); the signal's evidence is B2's edges
        got = s.get('req_%s_hz' % k)
        out['locus %s (frames)' % k] = dict(target=v(x), measured=got,
                                            within=got is not None and abs(got - v(x)) <= 0.08 * v(x))
    # every entry carries its specification (R19b), even one the module already says: no spec, no
    # pass; and a specification none of whose targets could be checked passes nothing
    return dict(passed=bool(spec) and bool(out) and all(o['within'] for o in out.values()), targets=out,
                empty=not spec, unchecked=bool(spec) and not out)


SPEC_OF = {'peak_hz': ('noise', 'peak_hz'), 'centroid_hz': ('noise', 'peak_hz'), 'vot_ms': ('vot_ms',),
           'burst_centroid_hz': ('burst', 'centroid_hz'), 'burst_len_ms': ('burst', 'length_ms'),
           'burst_db': ('burst', 'level_db'),
           'duration_ms': ('duration', 'inherent_ms'), 'mod_rate_hz': ('trill', 'rate_hz')}
for _k in (1, 2, 3):
    SPEC_OF['F%d_50_hz' % _k] = ('formants', 'F%d' % _k)
    SPEC_OF['edge_F%d' % _k] = ('locus', 'F%d' % _k)


def _spec_value(t, sid, path):
    node = t.sounds[sid].get('spec') or {}
    for k in path:
        node = node.get(k) if isinstance(node, dict) else None
        if node is None:
            return None
    return node['v'] if isinstance(node, dict) else node


def specified(t, sid, c):
    """True when the two entries' specifications set this measure apart in the stated direction
    (by the contrast minimum), so that the engine must show it; otherwise why it is only reported.
    Voicing is a feature, always specified."""
    if c['measure'] == 'voiced_frac':
        return True
    if c['measure'] == 'voicing_slope' and t.sounds[sid]['features'].get('airstream') == 'implosive':
        # the airstream is a feature: an implosive's voice swells where the plain stop's does not
        return True
    path = SPEC_OF.get(c['measure'])
    if path is None:
        return 'no specification field for %s' % c['measure']
    mine, theirs = _spec_value(t, sid, path), _spec_value(t, c['with'], path)
    if mine is None or theirs is None:
        return 'reported only: %s has no %s in its specification' % (
            t.sounds[sid if mine is None else c['with']]['ipa'], '.'.join(path))
    ok, _ = contrast_ok(c['measure'], mine, theirs, c['sign'])
    return True if ok else 'reported only: the specifications differ by less than the contrast minimum (%s, %s)' % (
        mine, theirs)


def contrast_ok(measure, mine, theirs, sign, same_base=False):
    if mine is None or theirs is None:
        return False, None
    d = mine - theirs
    if measure == 'voiced_frac':
        # a share of the frames: a fifth of the sound voiced or not is the least that counts
        return (d * sign >= 0.2), round(d, 2)
    if measure == 'voicing_slope':
        # dB per 10 ms: twice the measure's error on a synthetic swell (0.4, selftest.py)
        return (d * sign >= 0.8), round(d, 2)
    if same_base and not (measure.endswith('_ms') or measure.endswith('_db') or measure.startswith('mod_dips')):
        # a mark against its own base in the same context: the context's variation cancels, so
        # a smaller move is real (1.5 per cent, at least 15 Hz)
        return (d * sign >= max(0.015 * abs(theirs), 15.0)), round(d, 1)
    if measure.endswith('_ms') or measure in ('duration_ms',):
        need = CONTRAST_MIN['ms']
    elif measure.endswith('_db'):
        need = CONTRAST_MIN['db']
    elif measure.startswith('mod_dips'):
        need = CONTRAST_MIN['count']
    else:
        need = CONTRAST_MIN['hz_rel'] * abs(theirs)
    return (d * sign >= need), round(d, 1)


def judge(t, sid, cases, diags, said_as):
    e = t.sounds[sid]
    man = manner(e) if e['kind'] == 'base' else None
    s = summary(cases, man) if e['kind'] == 'base' else {}
    losses = [d for d in diags if d['level'] == 'loss']
    a0 = dict(passed=not losses and not said_as.get('substitute'), losses=losses[:20],
              substitute=said_as.get('substitute'))
    a1 = check_a1(cases, man)
    # A2 on the phones under test: the vowels around a consonant are the context, not the sound
    # (a cardinal [i]'s F1, 217 Hz, sits on the voice's second harmonic, where the tracker fails, D15)
    a2 = RP.check_a(dict(cases={cid: dict(c['gold'], phones=[c['gold']['phones'][i] for i in c['target']
                                                              if i < len(c['gold']['phones'])])
                                for cid, c in cases.items()}), E.pack(said_as['pack']).phone_module)
    if a2['a1_phones'] == 0 and not a2['substituted']:
        a2 = dict(a2, passed=True, note='nothing check A measures in the sound under test (a stop, a made sound)')
    a2 = {k: a2[k] for k in ('passed', 'note', 'a1_phones', 'a1_silent', 'a2_checks', 'a2_ok', 'a2_rate', 'substituted',
                             'problems') if k in a2}
    if e['kind'] == 'base':
        b3 = check_b3(e, s)
        air = e['features'].get('airstream', 'pulmonic')
        need = {'click': 'burst ', 'implosive': 'closure voicing slope'}.get(air)
        if air != 'pulmonic' and not (need and any(k.startswith(need) for k in b3['targets'])):
            # what makes a click or an implosive is its airstream: without its own targets
            # (T-click, T-airstream) the generic checks prove the place, not the sound
            b3['targets']['airstream (T-click, T-airstream)'] = dict(target=air, measured=None, within=False)
            b3['passed'] = False
    elif e['kind'] == 'modifier':
        b3 = check_shift(t, sid, cases)
        s = b3.pop('summary')
        # every marked case must have been composed with the mark, not said without it
        marked = [c for cid, c in cases.items() if '_marked_' in cid]
        unc = [cid for cid, c in cases.items() if '_marked_' in cid and not any(
            d['kind'] == 'composed' or d['kind'] == 'tone-made' for d in c['diag'] + c.get('fe_diag', []))]
        if unc and marked:
            a0 = dict(a0, passed=False, not_composed=unc[:6])
    elif PZ.check_of(e):
        b3, s = PZ.judge(t, sid, cases)
    else:
        # no check is written for this kind of entry: nothing passes
        b3 = dict(passed=False, empty=False, targets={}, unchecked=True)
    return dict(manner=man, summary=s, A0=a0, A1=a1, A2=a2, B3=b3)


def check_shift(t, sid, cases):
    """T-shift and its kin: per base, the marked sound against the plain one in the same contexts;
    every named measure that applies to the base must move the stated way by at least the
    contrast minimum, and each base must have at least one."""
    tests = t.sounds[sid].get('tests') or {}
    per, targets, ok_all = {}, {}, True
    for base in tests.get('bases', []):
        man = manner(t.sounds[base])
        sp = summary({c: v for c, v in cases.items() if c.startswith(base + '_plain_')}, man)
        sm = summary({c: v for c, v in cases.items() if c.startswith(base + '_marked_')}, man)
        per[base] = dict(plain=sp, marked=sm)
        checked = 0
        for sh in tests.get('shift', []):
            m = sh['measure']
            if sp.get(m) is None and sm.get(m) is None:
                continue
            ok, d = contrast_ok(m, sm.get(m), sp.get(m), sh['sign'], same_base=True) if m != 'burst_found' else (
                (sm.get(m) is not None and sp.get(m) is not None and (sm[m] - sp[m]) * sh['sign'] >= 1),
                None if sm.get(m) is None or sp.get(m) is None else sm[m] - sp[m])
            targets['%s %s' % (t.sounds[base]['ipa'], m)] = dict(target='%+d' % sh['sign'], measured=d, within=ok,
                                                               plain=sp.get(m), marked=sm.get(m))
            checked += 1
            ok_all &= ok
        for lim in tests.get('limit', []):
            got = sm.get(lim['measure'])
            ok = got is not None and (got <= lim['max'] if 'max' in lim else got >= lim['min'])
            targets['%s %s %s' % (t.sounds[base]['ipa'], lim['measure'], '<= %s' % lim['max'] if 'max' in lim
                                  else '>= %s' % lim['min'])] = dict(target=lim.get('max', lim.get('min')),
                                                                     measured=got, within=ok, marked=got)
            ok_all &= ok
        if not checked:
            targets['%s (none)' % t.sounds[base]['ipa']] = dict(target='a measure', measured=None, within=False)
            ok_all = False
    return dict(passed=ok_all and bool(per), targets=targets, empty=not per, summary=per)


def test_map(pack, template, work):
    """compose_test's map (the pack's header lines and the realised master table), with the pack's
    `says` lines too: what the module says for its affricates, which the layer must be told."""
    p, path = CT.test_map(pack, template, work)
    with open(p.sounds_map, encoding='utf-8') as f:
        says = [l.rstrip('\n') for l in f if l.split()[:1] == ['says']]
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    out = os.path.join(work, 'sweep-%s.map' % template)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(says + lines))
    return p, out


def say_entry(t, sid, template, pack):
    """One entry said in its contexts and judged (B2 aside): the map written afresh from `t', so
    that a correction made in this run is the one that speaks."""
    AD.write(t, template, quiet=True)
    p, map_path = test_map(pack, template, SWEEP_WORK)
    with open(map_path, 'rb') as f:
        map_sha = hashlib.sha256(f.read()).hexdigest()
    e = t.sounds[sid]
    r = AD.realize(t, sid, template, (AD.loop_proof(sid) or {}).get('carrier_measured')) if e['kind'] == 'base' else None
    said_as = dict(pack=pack, carrier=r['carrier'] if r else None, keys=r['keys'] if r else None,
                   distance=r['distance'] if r else None,
                   substitute=('%s is said as the module phone %s, %s feature steps away, unmoved' % (
                       e['ipa'], r['carrier'], r['distance'])) if r and r['distance'] and not r['keys'] else None,
                   peak_key=r.get('peak_key') if r else None)
    layer = None
    if r and r['carrier'].startswith('<'):
        layer = dict(name=r['carrier'], ms=r['keys'].get('ms', 60), voi=r['keys'].get('voi') == 1)
    pk = ((e.get('spec') or {}).get('noise') or {}).get('peak_hz')
    if pk is not None:
        # the band a noise peak is looked for in starts at 60 per cent of its target: below it
        # are the voice's own formants, which a voiced fricative's spectrum is full of
        layer = dict(layer or {}, peak_target=pk['v'] if isinstance(pk, dict) else pk)
    inputs, diags = [], []
    for cid, text in contexts(t, sid):
        rc, out, d = CT.say_ipa(p, map_path, text)
        if rc != 0:
            raise SystemExit('front-end failed on %s %r' % (sid, text))
        inputs.append((cid, text, out, d))
        diags += d
    rend = E.render(pack, [(cid, 'annotated', out) for cid, _, out, _ in inputs],
                    work=os.path.join(SWEEP_WORK, sid.replace('+', '_')))
    cases = {}
    for (cid, text, out, d), r_ in zip(inputs, rend):
        diags += r_['diag'][len(d):] if r_['diag'][:len(d)] == d else r_['diag']
        c = measure(r_, p, cid, manner(e) if e['kind'] == 'base' else None, layer)
        c.update(ipa=text, said=out, diag=r_['diag'], fe_diag=d, wav_sha256=r_['wav_sha256'])
        if PZ.check_of(e):
            x_, rate_ = E.read_wav(r_['wav'])
            c['pros'] = PZ.measure(x_, rate_, c['phones'], r_['frames'])
        cases[cid] = c
    verdict = judge(t, sid, cases, diags, said_as)
    return dict(id=sid, ipa=e['ipa'], name=e['name'], template=template, pack=pack, staged=E.STAGE or None,
                frontend=E.FRONTEND, map=os.path.relpath(map_path, ROOT) if map_path.startswith(ROOT) else map_path,
                map_sha256=map_sha, said_as=said_as, cases=cases, **verdict)


# The USP's design loop (playbook 1.6, step 6): a target missed is corrected from what was measured
# and the entry said again, at most five rounds. A correction is a `trim' for this template only:
# the specification is never touched (DESIGN.md 5).
ROUNDS = 5
ABS_KEYS = ('vot', 'trate', 'tapms')     # corrected as values; every other key as a ratio
TRIM_KEYS = {'F1': ['f1'], 'F2': ['f2'], 'F3': ['f3'], 'peak_hz': ['f2', 'f3', 'f4'],
             'locus F2 (frames)': ['f2'], 'locus F3 (frames)': ['f3']}


def corrections(res, trims):
    """New trims (key -> per cent, multiplied in) from the B3 targets this round missed, or None
    when nothing can be corrected this way."""
    out, any_ = dict(trims), False
    for k, tg in res['B3']['targets'].items():
        if k == 'vot_ms' and not tg['within'] and tg['measured'] is not None:
            # the voice onset: the key moved by what was missed (it has a floor, the module's own
            # onset in that context: D47, Q13; a key below nought is not asked for)
            cur = out.get('vot', (res['said_as']['keys'] or {}).get('vot', tg['target']))
            nxt = cur + (tg['target'] - tg['measured'])
            if nxt >= 0:
                out['vot'] = nxt
                any_ = True
            continue
        if tg['within'] or not tg['measured'] or k not in TRIM_KEYS:
            continue
        f = (tg['target'] / tg['measured']) ** 0.7   # damped: a measure that jumps must not flip the key
        for key in ([res['said_as'].get('peak_key')] if k == 'peak_hz' and res['said_as'].get('peak_key')
                    else TRIM_KEYS[k]):
            out[key] = out.get(key, 100.0) * f
        any_ = True
    for k, key in (('trill_rate_hz', 'trate'), ('tap_closed_ms', 'tapms'), ('trill_closed_ms', 'tapms')):
        tg = res['B3']['targets'].get(k)
        if tg and not tg['within'] and tg['measured']:
            cur = out.get(key, (res['said_as']['keys'] or {}).get(key, tg['target']))
            out[key] = max(1.0, cur * (tg['target'] / tg['measured']) ** 0.7)
            any_ = True
    tg = res['B3']['targets'].get('trill_rate_hz')
    if tg and not tg['within'] and tg['measured'] is None:
        # fewer than two closures: the sound is too short to trill at its rate; lengthen it
        out['hold'] = out.get('hold', 100.0) * 1.3
        any_ = True
    return out if any_ else None


def with_trims(t, sid, template, trims):
    e = t.sounds[sid]
    ov = e.setdefault('realization', {}).setdefault('openevv', {})
    ov.setdefault('trim', {})[template] = [dict(key=k, v=round(v, 1), scale=k not in ABS_KEYS, tag='measured',
                                                proof='ipa/proofs/%s.json' % sid) for k, v in sorted(trims.items())]


def prove_entry(t, sid, template, pack, rounds=ROUNDS):
    """Say an entry; while a specification target is missed, correct and say it again."""
    old = ((t.sounds[sid].get('realization') or {}).get('openevv') or {}).get('trim', {}).get(template)
    trims = {tr['key']: tr['v'] for tr in old or []}
    history = []
    res = say_entry(t, sid, template, pack)
    while True:
        history.append(dict(round=len(history) + 1, trims=dict(trims), B3=res['B3']['targets'],
                            keys=res['said_as']['keys']))
        if res['B3']['passed'] or len(history) >= rounds:
            break
        nxt = corrections(res, trims)
        if nxt is None:
            break
        trims = nxt
        with_trims(t, sid, template, trims)
        res = say_entry(t, sid, template, pack)
    res['rounds'] = history
    ok = all(res[k]['passed'] for k in ('A0', 'A1', 'A2', 'B3'))
    res['trims'] = {k: round(v, 1) for k, v in trims.items()} if ok and trims else {}
    if not res['trims'] and trims:
        # not through: the entry speaks for the rest of the run as it was before, the rounds kept as
        # the evidence; a correction is kept only if it got the entry through
        ov = ((t.sounds[sid].get('realization') or {}).get('openevv') or {})
        if old is None:
            ov.get('trim', {}).pop(template, None)
        else:
            ov['trim'][template] = old
    return res


def run(t, ids, template, pack, apply=False, rounds=ROUNDS):
    os.makedirs(SWEEP_WORK, exist_ok=True)
    results = {}
    for sid in ids:
        e = t.sounds[sid]
        if not contexts(t, sid):
            results[sid] = dict(id=sid, ipa=e['ipa'], skipped='no inputs for this kind of entry yet')
            continue
        results[sid] = prove_entry(t, sid, template, pack, rounds if e['kind'] == 'base' else 1)
    AD.write(t, template, quiet=True)
    # B2: the contrasts the entries' tests name, against the partner's own measures (this run's,
    # or its proof file's)
    for sid, res in results.items():
        if 'summary' not in res:
            continue
        b2 = []
        for c in (t.sounds[sid].get('tests') or {}).get('contrast', []):
            other = results.get(c['with'])
            if other is None:
                path = os.path.join(PROOFS, c['with'] + '.json')
                other = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else None
            theirs = (other or {}).get('summary', {}).get(c['measure'])
            ok, d = contrast_ok(c['measure'], res['summary'].get(c['measure']), theirs, c['sign'])
            why = specified(t, sid, c)
            b2.append(dict(c, mine=res['summary'].get(c['measure']), theirs=theirs, difference=d, holds=ok,
                           required=why is True, basis=why if why is not True else 'the specifications differ so'))
        res['B2'] = dict(passed=all(x['holds'] for x in b2 if x['required']), contrasts=b2)
        res['passed'] = all(res[k]['passed'] for k in ('A0', 'A1', 'A2', 'B3', 'B2'))
    os.makedirs(PROOFS, exist_ok=True)
    for sid, res in results.items():
        if 'summary' not in res:
            continue
        slim = json.loads(json.dumps(res, default=float))
        for c in slim['cases'].values():
            c.pop('gold', None)
        with open(os.path.join(PROOFS, sid + '.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(slim, f, ensure_ascii=False, indent=1)
    if apply:
        apply_states(t, results)
        save_trims(t, results, template)
    # the realised map from the table as it stands on disk: never with a correction that was not kept
    AD.write(T.load(), template, quiet=True)
    return results


def save_trims(t, results, template):
    """A correction that brought an entry within its targets (A0 to B3) is written into the entry's
    realisation (`trim.<template>', tagged measured, its proof named), and nothing else. It is the
    rule prove_entry keeps a correction by for the rest of the run, so the map the later entries
    were said with is the map saved (D62 8: a correction kept in the run but not saved, because
    the entry then failed a contrast, left every later proof made on a map that never existed)."""
    for sid, res in results.items():
        if not res.get('trims'):
            continue
        path = os.path.join(T.IPA, 'table', t.where[sid])
        with open(path, encoding='utf-8') as f:
            text = f.read()
        line = 'trim.%s = [%s]' % (template, ', '.join(
            '{ key = "%s", v = %s, scale = %s, tag = "measured", proof = "ipa/proofs/%s.json" }' % (
                k, v, 'false' if k in ABS_KEYS else 'true', sid)
            for k, v in sorted(res['trims'].items())))
        head = '[sound."%s".realization.openevv]' % sid
        if head in text:
            a = text.index(head) + len(head)
            b = text.find('\n[', a)
            b = len(text) if b < 0 else b
            block = re.sub(r'(?m)^trim\.%s = .*\n?' % template, '', text[a:b])
            text = text[:a] + block.rstrip('\n') + '\n' + line + '\n' + text[b:]
        else:
            th = '[sound."%s".tests]' % sid
            ta = text.index(th)
            tb = text.find('\n[sound."', ta)
            add = '\n\n%s\n%s\n' % (head, line)
            text = text.rstrip('\n') + add if tb < 0 else text[:tb].rstrip('\n') + add + text[tb:]
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)


def map_sha(t, template, pack):
    """The SHA-256 of the map an entry would be said with now, from the table `t'."""
    AD.write(t, template, quiet=True)
    _, path = test_map(pack, template, SWEEP_WORK)
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def on_other_map(t, template, pack):
    """Ids whose passing proof was made on a map other than the one the table makes now. A failing
    proof is left out: its last round is said with a trial correction that is then not kept, so
    its map is never the saved one."""
    now = map_sha(t, template, pack)
    out = []
    for sid in sorted(t.sounds):
        path = os.path.join(PROOFS, sid + '.json')
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                pr = json.load(f)
            if pr.get('pack') == pack and pr.get('passed') and pr.get('map_sha256') != now:
                out.append(sid)
    return out


def apply_states(t, results):
    """For each entry that passed: state = its plan's end state, level 2, tests.proof. Edits the
    TOML text in place, only those three lines of the entry (the table is otherwise by hand)."""
    files = {}
    for sid, res in results.items():
        e = t.sounds[sid]
        if res.get('passed'):
            files.setdefault(t.where[sid], []).append((sid, e['plan']['end_state']))
        elif 'summary' in res and e.get('state') not in ('MISSING', None):
            # it passed before and does not now: back to MISSING, its proof saying why
            files.setdefault(t.where[sid], []).append((sid, 'MISSING'))
    for name, items in files.items():
        path = os.path.join(T.IPA, 'table', name)
        with open(path, encoding='utf-8') as f:
            text = f.read()
        for sid, state in items:
            head = '[sound."%s"]' % sid
            a = text.index(head)
            # the entry ends where another entry begins, not at its own sub-tables ([sound."X".spec])
            m = re.compile(r'\n\[sound\."(?!%s")' % re.escape(sid)).search(text, a + len(head))
            b = m.start() if m else len(text)
            block = text[a:b]
            block = re.sub(r'(?m)^state = ".*"$', 'state = "%s"' % state, block, count=1)
            lv = int(re.search(r'(?m)^level = (\d+)$', block).group(1))
            block = re.sub(r'(?m)^level = \d+$', 'level = %d' % (1 if state == 'MISSING' else max(lv, 2)), block,
                           count=1)
            tests_head = '[sound."%s".tests]' % sid
            ta = block.index(tests_head)
            tb = block.find('\n[', ta + len(tests_head))
            tb = len(block) if tb < 0 else tb
            tests = block[ta:tb]
            line = 'proof = "ipa/proofs/%s.json"' % sid
            tests = re.sub(r'(?m)^proof = ".*"$', line, tests) if re.search(r'(?m)^proof = ', tests) \
                else tests.rstrip('\n') + '\n' + line + '\n'
            block = block[:ta] + tests + block[tb:]
            text = text[:a] + block + text[b:]
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)


def fmt(res):
    if 'summary' not in res:
        return '%-8s %-3s %s' % (res['id'], res['ipa'], res.get('skipped'))
    flags = ' '.join('%s:%s' % (k, 'ok' if res[k]['passed'] else 'FAIL') for k in ('A0', 'A1', 'A2', 'B3', 'B2'))
    # a mark's summary is per base (plain and marked); its numbers are in its B3 lines instead
    s = {} if any(isinstance(v, dict) for v in res['summary'].values()) else res['summary']
    keys = [k for k in ('F1_50_hz', 'F2_50_hz', 'F3_50_hz', 'edge_F2', 'edge_F3', 'vot_ms', 'peak_hz', 'murmur_F1_hz',
                        'mod_rate_hz', 'duration_ms') if s.get(k) is not None]
    why = []
    if res['A0']['substitute']:
        why.append('substitute')
    why += ['%s %s' % (d['kind'], d['detail'][:40]) for d in res['A0']['losses'][:2]]
    why += res['A1']['problems'][:1]
    if res['B3'].get('empty'):
        why.append('no specification')
    why += ['%s %s≠%s' % (k, v['measured'], v['target']) for k, v in res['B3']['targets'].items() if not v['within']]
    why += ['%s %s vs %s %s' % (c['measure'], c['mine'], c['with'], c['theirs']) for c in res['B2']['contrasts']
            if not c['holds'] and c['required']]
    return '%-8s %-3s %-4s %s  %s%s' % (res['id'], res['ipa'], 'PASS' if res['passed'] else 'fail', flags,
                                       ' '.join('%s=%s' % (k, round(s[k])) for k in keys),
                                       ('  [' + '; '.join(why) + ']') if why else '')


def select(t, args):
    if not args:
        return sorted(t.sounds)
    out = []
    for a in args:
        if a in t.sounds:
            out.append(a)
        else:
            out += sorted(i for i, e in t.sounds.items() if e.get('section') == a)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('which', nargs='*', help='ids (U+0288) or sections (pulmonic); default: all')
    ap.add_argument('--template', default='dedx')
    ap.add_argument('--pack', default='hi', help='a pack on --template: its header lines make the test map')
    ap.add_argument('--apply', action='store_true', help='set state, level and proof of the entries that pass, and '
                    'write the corrections that got them there')
    ap.add_argument('--rounds', type=int, default=ROUNDS, help='design rounds an entry may take (1: no correction)')
    ap.add_argument('--settle', type=int, default=3, help='with --apply: passes that re-say the entries whose proof is '
                    'of another map than the one saved (0: none)')
    a = ap.parse_args()
    if not E.STAGE:
        raise SystemExit('set EVV_STAGE: the proofs are of the staged modules and front-end')
    t = T.load()
    ids = select(t, a.which)
    if E.pack(a.pack).template != a.template:
        raise SystemExit('%s is not on %s' % (a.pack, a.template))
    res = run(t, ids, a.template, a.pack, a.apply, a.rounds)
    for k in range(a.settle if a.apply else 0):
        # a correction saved in this run changed the map the entries said before it were proved on:
        # say those again, until every proof is of the map as it stands (D62 8)
        t = T.load()
        again = on_other_map(t, a.template, a.pack)
        print('settle %d: %d proofs made on another map%s' % (k + 1, len(again), (': ' + ' '.join(again)) if again else ''))
        if not again:
            break
        res.update(run(t, again, a.template, a.pack, a.apply, a.rounds))
        ids += [i for i in again if i not in ids]
    for sid in ids:
        print(fmt(res[sid]))
    done = [r for r in res.values() if r.get('passed')]
    print('sweep: %d entries, %d rendered, %d passed every check, %d not yet; proofs in ipa/proofs/' % (
        len(ids), sum('summary' in r for r in res.values()), len(done),
        sum('summary' in r and not r.get('passed') for r in res.values())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
