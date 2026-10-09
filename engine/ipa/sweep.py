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
import math
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


def clipped(x):
    """(saturated samples, samples within 2 per cent of full scale). Saturation is a flat top (a
    sample equal to the one before it, 30000 or more from nought) or the 16-bit limit itself; a
    lone pulse near the ceiling is reported, not failed (D64)."""
    import numpy as np
    x = np.asarray(x).astype(int)
    a = np.abs(x)
    flat = int(((a[1:] >= 30000) & (x[1:] == x[:-1])).sum()) + int(((x >= 32767) | (x <= -32768)).sum())
    return flat, int((a >= 32000).sum())


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


def man_of(t, e):
    """The manner a sound is measured as: a letter's own, a Tier B composite's base's (D68)."""
    if e['kind'] == 'base':
        return manner(e)
    if e['kind'] == 'composite':
        return manner(t.sounds[e['tests']['bases'][0]])
    return None


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
    if e['kind'] == 'composite':
        # a Tier B spelling (D68): alone, and between vowels against its plain base (or the plain
        # spelling its tests name) in the same contexts, as its marks are judged
        b = t.sounds[tests['bases'][0]]
        out = [('alone', e['ipa'])]
        for variant, x in (('plain', tests.get('plain') or b['ipa']), ('marked', e['ipa'])):
            if manner(b) == 'vowel':
                out += [('%s_%s_%s' % (tests['bases'][0], variant, c), 'ˈ%s%s%s' % (c, x, c)) for c in CONSONANTS_AROUND]
            else:
                out += [('%s_%s_%s' % (tests['bases'][0], variant, v), 'ˈ%s%s%s' % (v, x, v)) for v in VOWELS_AROUND]
        return out
    out = []
    follow = t.sounds[tests['follow']]['ipa'] if tests.get('follow') else ''
    for base in tests.get('bases', []):
        b = t.sounds[base]
        # a mark written before its letter goes before it (Tier B, D70); a test may name the
        # forms said, `{}' for the base (the plain one aspirated, to show ˭ takes it away)
        marked = e['ipa'] + b['ipa'] if e.get('placement') == 'before' else b['ipa'] + e['ipa']
        for variant, x in (('plain', tests.get('plain_form', '{}').replace('{}', b['ipa'])),
                           ('marked', tests['marked_form'].replace('{}', b['ipa']) if tests.get('marked_form')
                            else marked)):
            if e['ipa'] == '\u0329':
                # a syllabic consonant: after a stressed syllable, the word ending in it
                out.append(('%s_%s_pa' % (base, variant), 'ˈpa%s%s' % ('p' if variant == 'marked' else 'pa', x)))
            elif e['ipa'] == '\u032f':
                # a non-syllabic vowel: after a syllabic [a], a diphthong; the plain vowel is a
                # syllable of its own there (`ˈpa.up'). On its own between consonants the marked
                # vowel left the word no nucleus and the front-end put a schwa in (D64)
                out.append(('%s_%s_au' % (base, variant), 'ˈpa%s%sp' % ('.' if variant == 'plain' else '', x)))
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
    if case_id.endswith('_au'):
        # `ˈpa.up' or `ˈpau̯p': the vowel after the [a], with the [a] before it and the p after
        if len(sounding) >= 4:
            return [sounding[-2]], sounding[-3], sounding[-1]
    if len(sounding) < 3:
        return sounding, None, None
    return sounding[1:-1], sounding[0], sounding[-1]


def ph_is_schwa(ph):
    return ph['name'] == '@' and ph.get('sound') in (None, '-')


def measure(r, p, case_id, man=None, layer=None, base_man=None):
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
        if man == 'stop' and made_end - v['start_ms'] >= 15 and v['end_ms'] - made_end >= 30:
            # a closure the layer makes (ʔ): the signal there, from 10 ms in (the resonators ring on
            # from the sound before), 20 dB or more under the middle of the vowel after it
            m_ = (made_end + v['end_ms']) / 2.0
            made['meas']['closure_quiet'] = int(A.intensity_db(x, rate, v['start_ms'] + 10, made_end)
                                        <= A.intensity_db(x, rate, m_ - 15, m_ + 15) - 20)
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
            if (me.get('F1_50_hz') is None or me.get('F4_50_hz') is None) and ph['end_ms'] - ph['start_ms'] >= 20:
                # F1 to F3 where the phone's class gave none; F4 always (D74: an r's tongue shape shows
                # in F4 against F5, which the voice holds; checked only where an entry asks, check_F4)
                fs = A.formants(x, rate, (ph['start_ms'] + ph['end_ms']) / 2.0)
                for i in range(4):
                    if i == 3 or me.get('F%d_50_hz' % (i + 1)) is None:
                        me['F%d_50_hz' % (i + 1)] = fs[i][0] if len(fs) > i else None
    if tgt and (man or base_man) == 'nasal':
        # the energy above 3 kHz against the murmur's below 1 kHz: noise in the nose (extIPA's
        # nasal friction, D69) is aperiodic energy above 3 kHz (zajac2021); for a mark, on its
        # base's manner (`base_man': a mark has no manner of its own, its other measures as before)
        for ph in tgt:
            a_, b_ = ph['start_ms'], ph['end_ms']
            if b_ - a_ >= 20:
                f_, p_ = A.spectrum(x, rate, a_ + 0.2 * (b_ - a_), b_ - 0.2 * (b_ - a_))
                hi, lo = p_[f_ >= 3000.0].sum(), p_[f_ < 1000.0].sum()
                if hi > 0 and lo > 0:
                    ph.setdefault('meas', {})['hf_db'] = 10.0 * math.log10(hi / lo)
                # velopharyngeal friction (extIPA's ◌͌, D71; its noise on F2, about 1.2 kHz on a
                # nasal): the energy from 800 Hz to 2.5 kHz against the murmur's below 800 Hz, and,
                # since over a voice a level follows the voice (D72), the periodicity above 1 kHz
                # (D77)
                band, low = p_[(f_ >= 800.0) & (f_ < 2500.0)].sum(), p_[f_ < 800.0].sum()
                if band > 0 and low > 0:
                    ph.setdefault('meas', {})['band_db'] = 10.0 * math.log10(band / low)
                hp_ = A.signal.sosfilt(A.signal.butter(4, 1000.0 / (rate / 2.0), 'high', output='sos'), x)
                v_ = A.hnr_db(hp_, rate, a_ + 0.2 * (b_ - a_), b_ - 0.2 * (b_ - a_))
                if v_ is not None:
                    ph.setdefault('meas', {})['hnr_hi_db'] = v_
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
    if tgt and (man or base_man) == 'fricative':
        # how narrow the noise is, above the voice as the peak is read: its spread about the
        # centroid and the width of its band 10 dB under the peak (extIPA's whistled
        # articulation, D71); for a mark, on its base's manner as the nasal measure is
        for ph in tgt:
            a_, b_ = ph['start_ms'], ph['end_ms']
            sm = A.spectrum_moments(x, rate, a_ + 0.2 * (b_ - a_), b_ - 0.2 * (b_ - a_),
                                    fmin=max(800.0, 0.6 * (layer or {}).get('peak_target', 0)))
            if sm:
                ph.setdefault('meas', {})['noise_sd_hz'] = sm['sd_hz']
                ph['meas']['noise_bw_hz'] = sm['high_edge_hz'] - sm['low_edge_hz']
    if tgt:
        a, b = tgt[0]['start_ms'], tgt[-1]['end_ms']
        ex = dict(span_ms=[a, b])
        # where in the sound its voice and its creak are, from the frames: the share of each third's
        # frames with voice (AV) and with creak (DI) (extIPA's partial voicing, D70)
        t3 = E.frame_times(r['frames'])
        fr3 = r['frames']
        for name, lo, hi in (('head', 0.0, 1 / 3.0), ('mid', 1 / 3.0, 2 / 3.0), ('tail', 2 / 3.0, 1.0)):
            k3 = [i for i in range(len(t3)) if a + lo * (b - a) <= t3[i] + fr3[i, 0] / 2.0 < a + hi * (b - a)]
            if k3:
                ex['voiced_' + name] = sum(1 for i in k3 if fr3[i, E.P['av']] > 0) / float(len(k3))
                ex['creak_' + name] = sum(1 for i in k3 if fr3[i, E.P['di']] > 0) / float(len(k3))
        # how long the voice runs on into the sound from its start, and how long the sound ends
        # voiced: a consonant's span begins in the vowel before it, so its thirds cannot say where
        # a voicing mark put the voice; these runs, against the plain sound's, can (D70)
        k3 = [i for i in range(len(t3)) if a <= t3[i] + fr3[i, 0] / 2.0 < b]
        if k3:
            run = 0.0
            for i in k3:
                if fr3[i, E.P['av']] == 0:
                    break
                run += fr3[i, 0]
            ex['voice_in_ms'] = run
            run = 0.0
            for i in reversed(k3):
                if fr3[i, E.P['av']] == 0:
                    break
                run += fr3[i, 0]
            ex['voice_out_ms'] = run
        # the sound's own level: its middle third (a consonant's span begins in the vowel before
        # it) against the middle 30 ms of the vowel after it (extIPA's strong and weak
        # articulation, its denasal: a murmur, a noise or a closure louder or softer)
        nv_ = phones[after] if after is not None else None
        if nv_ and nv_['cls'] == 'vowel' and nv_['end_ms'] - nv_['start_ms'] >= 40 and b - a >= 30:
            m_ = (nv_['start_ms'] + nv_['end_ms']) / 2.0
            ex['mid_db'] = (A.intensity_db(x, rate, a + (b - a) / 3.0, a + 2 * (b - a) / 3.0)
                            - A.intensity_db(x, rate, m_ - 15.0, m_ + 15.0))
            if (man or base_man) == 'fricative':
                # a fricative's noise alone: the middle half of the frames in it whose friction is
                # at its full level, within 3 of the most (the middle third of a short one is
                # partly the vowel's, and so are the frames where the noise comes in and goes)
                tf = E.frame_times(r['frames'])
                kf = [i for i in range(len(tf)) if a <= tf[i] < b and r['frames'][i, E.P['af']] > 0]
                top = max([r['frames'][i, E.P['af']] for i in kf] or [0])
                kf = [i for i in kf if r['frames'][i, E.P['af']] >= top - 3]
                if kf:
                    n0, n1 = tf[kf[0]], tf[kf[-1]] + r['frames'][kf[-1], 0]
                    if n1 - n0 >= 20:
                        ex['noise_db'] = (A.intensity_db(x, rate, n0 + (n1 - n0) / 4.0, n1 - (n1 - n0) / 4.0)
                                          - A.intensity_db(x, rate, m_ - 15.0, m_ + 15.0))
        # a strike (extIPA's percussives, D78): two parts of the mouth heard hitting each other.
        # Where it is, the frames say: noise with no voice and no breath under it, just before a
        # closure begins (the lips or the teeth meeting, ʬ ʭ), or, in a sound with no closure, a
        # break of at most 10 ms in its voice (the tongue's slap on the floor of the mouth, ¡; a
        # voiceless fricative's noise is no strike); a click's slap (ǃ¡) is such noise from 10 to
        # 45 ms after the release, apart from the release's own (no such noise in the 10 ms
        # before it: ǃ's release goes on as noise 10 to 15 ms after it, 5 ms after its burst, as
        # loud as the vowel), that the signal shows within 10 dB of the vowel's peaks or louder
        # (word-finally, after a stressed schwa, the slap reads -6 dB: the engine's ceiling).
        # How loud and where in the spectrum, the signal says: its loudest 2 ms against the
        # loudest 2 ms of the middle 30 ms of the vowel after (of the vowel before, at a word's
        # end), peak against peak, as wright_etal_1995 compare the slap with the vowel; its
        # spectral centre; when it comes (from the closure's start, or the sound's) and how long
        # it lasts, from the frames
        tS, frS = E.frame_times(r['frames']), r['frames']
        P_ = E.P

        def bare_noise(i):
            return frS[i, P_['af']] > 0 and frS[i, P_['av']] == 0 and frS[i, P_['ah']] == 0
        inS = [i for i in range(len(tS)) if a <= tS[i] < b]
        shutS = [i for i in inS if frS[i, P_['af']] == 0 and frS[i, P_['ah']] == 0 and frS[i, P_['av']] < 30]
        if shutS:
            hits = [i for i in inS if bare_noise(i) and shutS[0] - 2 <= i < shutS[0]]
        else:
            hits, i = [], 0
            while i < len(inS):
                if not bare_noise(inS[i]):
                    i += 1
                    continue
                j = i
                while j + 1 < len(inS) and bare_noise(inS[j + 1]):
                    j += 1
                run_ = inS[i:j + 1]
                k0, k1 = run_[0] - 1, run_[-1] + 1
                if not hits and sum(frS[k, 0] for k in run_) <= 10.0 and k0 >= 0 and k1 < len(tS) \
                        and frS[k0, P_['av']] > 0 and frS[k1, P_['av']] > 0:
                    hits = run_
                i = j + 1
        refS = None
        # (the phones right after and right before the sound: a case alone names no neighbours, and
        # its schwa before is the only vowel it has)
        for vS in [phones[k_] for k_ in (idx[-1] + 1, idx[0] - 1) if 0 <= k_ < len(phones)]:
            if vS['cls'] == 'vowel' and vS['end_ms'] - vS['start_ms'] >= 40:
                mS = (vS['start_ms'] + vS['end_ms']) / 2.0
                env_, _ = A.envelope_db(x, rate, mS - 15.0, mS + 15.0, hop_ms=0.5, win_ms=2.0)
                if len(env_):
                    refS = float(env_.max())
                    break

        def level_at(i0, i1):
            s0, s1 = tS[i0], tS[i1] + frS[i1, 0]
            if refS is None:
                return None
            env_, _ = A.envelope_db(x, rate, s0, s1 + 3.0, hop_ms=0.5, win_ms=2.0)
            return float(env_.max()) - refS if len(env_) else None

        def strike_at(i0, i1, key):
            s0, s1 = tS[i0], tS[i1] + frS[i1, 0]
            lv_ = level_at(i0, i1)
            if lv_ is not None:
                ex[key + '_db'] = lv_
            ex[key + '_len_ms'] = float(s1 - s0)
            sm_ = A.spectrum_moments(x, rate, s0, s1, fmin=300.0)
            if sm_:
                ex[key + '_centroid_hz'] = float(sm_['centroid_hz'])
        ex['strike_found'] = int(bool(hits))
        if hits:
            strike_at(hits[0], hits[-1], 'strike')
            # from where the closure begins (the strike is its first moment) or the sound begins
            ex['strike_ms'] = 0.0 if shutS else float(tS[hits[0]] - a)
        ex['slap_found'] = 0    # (no closure, no release, no slap)
        if shutS:
            # the first closure's end (a click's own release follows it)
            run_ = [shutS[0]]
            for i in shutS[1:]:
                if i != run_[-1] + 1:
                    break
                run_.append(i)
            relS = tS[run_[-1]] + frS[run_[-1], 0]
            slaps = [i for i in range(len(tS)) if relS + 10.0 <= tS[i] < relS + 45.0 and bare_noise(i)
                     and not any(bare_noise(j) for j in range(len(tS)) if tS[i] - 10.0 <= tS[j] < tS[i])
                     and (level_at(i, i) if refS is not None else -99.0) >= -10.0]
            ex['slap_found'] = int(bool(slaps))
            if slaps:
                ex['slap_ms'] = float(tS[slaps[0]] - relS)
                strike_at(slaps[0], slaps[0], 'slap')
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
            if closed:
                # breath before the closure (pre-aspiration, D70): the frames just before it with
                # breath and no voice
                j_, pre_ = closed[0] - 1, 0.0
                while j_ >= 0 and fr0[j_, E.P['av']] == 0 and fr0[j_, E.P['ah']] > 0:
                    pre_ += fr0[j_, 0]
                    j_ -= 1
                ex['preasp_ms'] = pre_
            win = ((t_ > c0) if closed else (t_ >= b)) & (t_ < b + 25)
            # AF only: the synthesiser sounds the bypass (AB) only with AF on, and p's frames carry
            # AB with AF at nought
            ex['burst_found'] = int(bool((fr0[win, E.P['af']] > 0).any()))
            if closed:
                # a release into friction (extIPA's fricated releases, D72): from where the closure
                # opens, how long the frames ask for friction at a fricative's level without a
                # break (AF 50 or more: 5 dB under this template's weakest fricative, x at 55; a
                # plain stop's burst fades under it at once); and how periodic the signal above
                # 1.5 kHz is in the 30 ms after it, its harmonics-to-noise ratio (a lateral
                # friction's peak lies near 1.6 to 2 kHz, kye2025): a voiced stop's friction rides
                # on its voice, which it makes less periodic, while its level there may stay under
                # the vowel's harmonics; a voiceless stop's friction shows as a later voice onset
                c1_ = t_[closed[-1]] + fr0[closed[-1], 0]
                run_ = 0.0
                for i in range(len(t_)):
                    if t_[i] < c1_:
                        continue
                    if fr0[i, E.P['af']] < 50:
                        break
                    run_ += fr0[i, 0]
                ex['rel_af_ms'] = run_
                # the friction heard: the middle half of that run, its first 10 ms (the burst) left
                # out, against the vowel after's middle 30 ms; silence reads far under the 40 dB the
                # harness takes for nothing (stop_timing's voice), a weak fricative does not (θ's
                # own noise is 18 to 25 dB under the vowel)
                nv_ = phones[after] if after is not None else None
                n0_, n1_ = c1_ + 10.0, c1_ + run_
                if nv_ and nv_['cls'] == 'vowel' and nv_['end_ms'] - nv_['start_ms'] >= 40 and n1_ - n0_ >= 20:
                    m_ = (nv_['start_ms'] + nv_['end_ms']) / 2.0
                    ex['rel_noise_db'] = (A.intensity_db(x, rate, n0_ + (n1_ - n0_) / 4.0, n1_ - (n1_ - n0_) / 4.0)
                                          - A.intensity_db(x, rate, m_ - 15.0, m_ + 15.0))
                if n1_ - n0_ >= 20:
                    # the friction's spectrum over the same run (D73: two releases with the same
                    # noise bands told apart by the fricative's own resonances), from 500 Hz as for
                    # a fricative; on a voiced stop the voice's harmonics are in it too
                    mo_ = A.spectrum_moments(x, rate, n0_, n1_)
                    if mo_:
                        ex['rel_peak_hz'] = mo_['peak_hz']
                        ex['rel_centroid_hz'] = mo_['centroid_hz']
                if after is not None and phones[after]['cls'] != 'silence':
                    hp_ = A.signal.sosfilt(A.signal.butter(4, 1500.0 / (rate / 2.0), 'high', output='sos'), x)
                    v_ = A.hnr_db(hp_, rate, c1_ + 2.0, c1_ + 32.0)
                    if v_ is not None:
                        ex['rel_hnr_db'] = v_
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
                st = dict(st, **{k: v for k, v in (A.stop_timing(x, rate, a, b, after_ms=250.0, voice_db=40.0) or {}).items()
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
            # A1 at the F1 the frames asked for: in a nasalised vowel the tracker's lowest
            # resonance is the nasal pole, and A1 read there was P0 itself (0.0 dB, D64)
            f1 = (last.get('req') or {}).get('F1_hz') or (last.get('meas') or {}).get('F1_50_hz')
            if f1:
                ex['a1_p0_db'] = A.a1_p0(x, rate, mid, f1)
        ex['schwa_ms'] = sum(ph['end_ms'] - ph['start_ms'] for ph in tgt if ph['name'] == '@')
        out['extra'] = ex
    # the vowels' formants at the consonant's edges, 12 ms from the boundary over 20 ms: where a
    # locus shows; at 20 per cent into the vowel the transition is mostly over. The vowel after is
    # read from where its voice begins (a locus is the F2 at the first glottal pulse): the module
    # puts a stop's breath at the start of the vowel's own frames, and the tracker read F2 2483 Hz
    # for [u] in that noise after p (D64)
    edges = {}
    tt_ = E.frame_times(r['frames'])
    for which, i, at in (('prev', before, -12.0), ('next', after, 12.0)):
        if i is None or phones[i]['cls'] == 'silence' or phones[i]['end_ms'] - phones[i]['start_ms'] < 30:
            continue
        if at < 0:
            t_ = phones[i]['end_ms'] + at
        else:
            von = next((tt_[j] for j in range(len(tt_)) if phones[i]['start_ms'] <= tt_[j] < phones[i]['end_ms']
                        and r['frames'][j, E.P['av']] > 0), phones[i]['start_ms'])
            if phones[i]['end_ms'] - von < 30:
                continue
            t_ = von + at
        fs = A.formants(x, rate, t_, win_ms=20.0)
        for k in (1, 2, 3):
            edges['%s_F%d_%s' % (which, k, '80' if at < 0 else '20')] = fs[k - 1][0] if len(fs) >= k else None
    # the frames the engine made where the vowel after begins and at its middle: a place given as
    # a locus equation (Q21) is checked there, in every context (check_b3)
    if after is not None and phones[after]['cls'] == 'vowel':
        js = [j for j in range(len(tt_)) if phones[after]['start_ms'] <= tt_[j] < phones[after]['end_ms']]
        if js:
            for k in (1, 2, 3):
                edges['next_req_F%d_0' % k] = float(r['frames'][js[0], E.P['f%d' % k]])
                edges['next_req_F%d_mid' % k] = float(r['frames'][js[len(js) // 2], E.P['f%d' % k]])
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
    for k in ('F1_50_hz', 'F2_50_hz', 'F3_50_hz', 'F4_50_hz', 'F3_min_hz', 'peak_hz', 'centroid_hz', 'vot_ms', 'closure_ms',
              'murmur_F1_hz', 'antiformant_hz', 'intensity_db', 'f0_50_hz', 'hf_db', 'noise_sd_hz', 'noise_bw_hz',
              'band_db', 'hnr_hi_db'):
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
              'burst_centroid_hz', 'gap_breath_frac', 'voiced_head', 'voiced_mid', 'voiced_tail', 'creak_head',
              'creak_mid', 'creak_tail', 'preasp_ms', 'voice_in_ms', 'voice_out_ms', 'mid_db', 'noise_db',
              'rel_af_ms', 'rel_hnr_db', 'rel_noise_db', 'rel_peak_hz', 'rel_centroid_hz', 'strike_found',
              'strike_db', 'strike_centroid_hz', 'strike_ms', 'strike_len_ms', 'slap_found', 'slap_ms', 'slap_db',
              'slap_centroid_hz', 'slap_len_ms'):
        v = vals(lambda c: (c.get('extra') or {}).get(k))
        if v is not None:
            s['%s' % k] = round(v, 2)
    for k in (1, 2, 3):
        # per context: the frames where the vowel after begins and at its middle (check_b3, Q21)
        pairs = [[c['edges']['next_req_F%d_0' % k], c['edges']['next_req_F%d_mid' % k], cid]
                 for cid, c in sorted(cases.items()) if cid != 'alone' and 'next_req_F%d_0' % k in c.get('edges', {})]
        if pairs:
            s['next_req_F%d_pairs' % k] = pairs
    for k in ('voicing_slope', 'burst_db', 'burst_len_ms', 'burst_centroid_hz', 'strike_db', 'strike_centroid_hz',
              'strike_ms', 'strike_len_ms', 'slap_ms', 'slap_db', 'slap_len_ms'):
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
        if c.get('clipped'):
            # the signal at full scale: a distortion the frames did not ask for, and one that
            # spreads over the whole spectrum, so nothing measured in the case can be trusted (D64)
            bad.append('%s: %d samples saturated (clipped)' % (cid, c['clipped']))
        if not c['target']:
            bad.append('%s: nothing sounded' % cid)
            continue
        ts = [c['phones'][i] for i in c['target']]
        if all(ph['cls'] == 'made' for ph in ts):
            if not any(ph['end_ms'] > ph['start_ms'] for ph in ts):
                bad.append('%s: the made sound has no frame of its own' % cid)
            elif man == 'stop' and cid != 'alone' and not any((ph.get('meas') or {}).get('closure_quiet') for ph in ts):
                # a closure the layer makes is proved in the signal, as a module stop's is (D64)
                bad.append('%s: no closure found in the signal' % cid)
            continue
        if man in ('stop', 'click') or all(ph['cls'] == 'stop' for ph in ts):
            # a release in the signal: stop_timing's burst or closure, or a transient over a silent
            # closure (a weak, low burst, p's before [i], has no 12 dB jump above 1.5 kHz)
            if not any((ph.get('meas') or {}).get('burst_ms') is not None or (ph.get('meas') or {}).get('closure_ms')
                       for ph in ts) and (c.get('extra') or {}).get('burst_len_ms') is None \
                    and not (c.get('extra') or {}).get('closure_quiet') and cid != 'alone' \
                    and not ((c.get('extra') or {}).get('burst_found') and (_voiced_frac(c) or 0) >= 0.5):
                # (a voiced closure sounds by its voice, and over that voice bar the signal's burst
                # finder reads the pulses, D63: the frames' release is taken for it, D64)
                bad.append('%s: no closure or burst found' % cid)
            continue
        if all((ph.get('req') or {}).get('voiced_frames', 0) + (ph.get('req') or {}).get('noise_frames', 0) == 0
               for ph in ts):
            bad.append('%s: %s has no sounding frame' % (cid, '+'.join(ph['name'] for ph in ts)))
    return dict(passed=not bad, problems=bad)


_CONTEXT_HZ = {}


def _context_hz(k, template='dedx'):
    """{context vowel: its formant k (0 = F1) as the master table realises it}, for the sweep's
    own context vowels."""
    if k not in _CONTEXT_HZ:
        t = T.load()
        _CONTEXT_HZ[k] = {v: (AD.realised_hz(t, t.by_ipa()[v], template) or [None] * 3)[k] for v in VOWELS_AROUND}
    return _CONTEXT_HZ[k]


def check_b3(e, s):
    """The specification's targets against the summary measures (prove.py's tolerances)."""
    spec = e.get('spec') or {}
    v = lambda x: x['v'] if isinstance(x, dict) else x  # noqa: E731
    want = {}
    f4 = (e.get('tests') or {}).get('check_F4')
    for k, x in (spec.get('formants') or {}).items():
        if k != 'F4' or f4:   # F4 realised everywhere, measured for an approximant, checked where asked (D74)
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
    # T-percussive (D78): a strike's level against the vowel's peaks within 3 dB and its spectral
    # centre within 25 per cent (as a click's burst), when it comes and how long it lasts within 5
    # ms (the frame step); a click's slap, its time from the release and its length within 5 ms,
    # its level within 3 dB; each found in two contexts at least
    for grp, keys in (('strike', (('level_db', 'strike_db', 3.0), ('centroid_hz', 'strike_centroid_hz', None),
                                  ('delay_ms', 'strike_ms', 5.0), ('length_ms', 'strike_len_ms', 5.0))),
                      ('slap', (('delay_ms', 'slap_ms', 5.0), ('level_db', 'slap_db', 3.0),
                                ('length_ms', 'slap_len_ms', 5.0)))):
        for k, mk, tol in keys:
            x = (spec.get(grp) or {}).get(k)
            if x is not None:
                got, w, n = s.get(mk), v(x), s.get('n_' + mk, 0)
                tol_ = 0.25 * w if tol is None else tol
                out['%s %s' % (grp, k)] = dict(target=w, measured=got, contexts=n,
                                               within=got is not None and n >= 2 and abs(got - w) <= tol_)
    # T-airstream: the voice's level through the closure, dB per 10 ms, within 1 (the measure's
    # own error is 0.4 on a synthetic swell, selftest.py; the source is a curve read from a figure)
    x = (spec.get('closure') or {}).get('voicing_slope_db10')
    if x is not None:
        got, w, n = s.get('voicing_slope'), v(x), s.get('n_voicing_slope', 0)
        out['closure voicing slope'] = dict(target=w, measured=got, contexts=n,
                                            within=got is not None and n >= 2 and abs(got - w) <= 1.0)
    slopes = spec.get('locus_slope') or {}
    for k, x in (spec.get('locus') or {}).items():
        if k in slopes:
            # a locus with its equation (Q21): the consonant sends a vowel to locus + slope x (the
            # vowel's own - locus), never to the locus itself, so it is checked where the vowel
            # after begins, in every context (frames, as below), against the vowel's own formant as
            # the table realises it, which nothing here moves (the review of D67: the vowel's
            # middle frame was still on its way from the place in a short vowel, and a reference
            # that moves with the result loosens the check)
            pairs = s.get('next_req_%s_pairs' % k) or []
            own = _context_hz(int(k[1]) - 1)
            got = [(a, own.get(cid.split('_')[0])) for a, m, cid in pairs]
            dev = [round(a / (v(x) + v(slopes[k]) * (o - v(x))) - 1.0, 3) for a, o in got if o]
            out['locus %s (equation, frames)' % k] = dict(
                target='%s + %s x (vowel - %s)' % (v(x), v(slopes[k]), v(x)), measured=got, deviation=dev,
                within=len(dev) >= 2 and all(abs(d) <= 0.08 for d in dev))
            continue
        # a locus is where the consonant sends the formants; a closure has no formants to measure in
        # the signal, so this is checked in the frames the engine made at the consonant (the
        # synthesiser realising them is check A2's business); the signal's evidence is B2's edges
        got = s.get('req_%s_hz' % k)
        out['locus %s (frames)' % k] = dict(target=v(x), measured=got,
                                            within=got is not None and abs(got - v(x)) <= 0.08 * v(x))
    # An entry marked approximate (its deviation stated, R7) may hold a missed target to a stated
    # bound instead (tests.approximate: {target: {min, max}}): a miss inside it is only noted here,
    # so that the design loop still corrects it; prove_entry accepts it once the loop has had its
    # rounds (DESIGN.md 6: approximate after five), as approximate, never as met (D64)
    for k, b in ((e.get('tests') or {}).get('approximate') or {}).items():
        o = out.get(k)
        if e.get('approximate') and o and not o['within'] and o['measured'] is not None \
                and b.get('min', -1e9) <= o['measured'] <= b.get('max', 1e9):
            o['approx_ok'] = dict(bound=b, deviation=e.get('deviation'))
    # every entry carries its specification (R19b), even one the module already says: no spec, no
    # pass; and a specification none of whose targets could be checked passes nothing
    return dict(passed=bool(spec) and bool(out) and all(o['within'] for o in out.values()), targets=out,
                empty=not spec, unchecked=bool(spec) and not out)


SPEC_OF = {'peak_hz': ('noise', 'peak_hz'), 'centroid_hz': ('noise', 'peak_hz'), 'vot_ms': ('vot_ms',),
           'burst_centroid_hz': ('burst', 'centroid_hz'), 'burst_len_ms': ('burst', 'length_ms'),
           'burst_db': ('burst', 'level_db'),
           'duration_ms': ('duration', 'inherent_ms'), 'mod_rate_hz': ('trill', 'rate_hz')}
for _k in (1, 2, 3, 4):
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
    Voicing is a feature, always specified. Two symbols the chart tells apart (`distinct', D73) must
    not be said alike: their contrast is required whatever their specifications say (the human's
    rule, 2026-10-08)."""
    if c['measure'] == 'voiced_frac':
        return True
    if c.get('distinct'):
        return True
    if c['measure'] == 'voicing_slope' and t.sounds[sid]['features'].get('airstream') == 'implosive':
        # the airstream is a feature: an implosive's voice swells where the plain stop's does not
        return True
    if c['measure'] == 'edge_F3' and c['sign'] < 0 and t.sounds[sid]['features'].get('place') == 'retroflex' \
            and t.sounds[c['with']]['features'].get('place') != 'retroflex':
        # retroflexion is a feature, and its cue is a lower F3 at the vowel's edge (the checklist's
        # correlates; ʈ's F3 note): required whether or not the other letter states an F3 locus
        # (the review of D67: ʈ and ɖ had no required place contrast left)
        return True
    path = SPEC_OF.get(c['measure'])
    if path is None:
        return 'no specification field for %s' % c['measure']
    mine, theirs = _spec_value(t, sid, path), _spec_value(t, c['with'], path)
    if mine is None or theirs is None:
        return 'reported only: %s has no %s in its specification' % (
            t.sounds[sid if mine is None else c['with']]['ipa'], '.'.join(path))
    if path[0] == 'locus' and all(_spec_value(t, x, ('locus_slope', path[1])) is not None for x in (sid, c['with'])):
        # two loci with their equations (Q21): what the specifications say at a vowel's edge is
        # locus + slope x (vowel - locus), not the locus; compared at the sweep's own context
        # vowels (their F2 as the table realises them), the median of each
        k = int(path[1][1]) - 1
        vs = [AD.realised_hz(t, t.by_ipa()[v], 'dedx')[k] for v in VOWELS_AROUND]

        def at_edge(x):
            lo, sl = _spec_value(t, x, path), _spec_value(t, x, ('locus_slope', path[1]))
            return sorted(lo + sl * (v - lo) for v in vs)[len(vs) // 2]
        mine, theirs = round(at_edge(sid), 1), round(at_edge(c['with']), 1)
        ok, _ = contrast_ok(c['measure'], mine, theirs, c['sign'])
        return True if ok else ('reported only: by their locus equations the specifications differ at the edge '
                                'by less than the contrast minimum (%s, %s)' % (mine, theirs))
    ok, _ = contrast_ok(c['measure'], mine, theirs, c['sign'])
    return True if ok else 'reported only: the specifications differ by less than the contrast minimum (%s, %s)' % (
        mine, theirs)


def contrast_ok(measure, mine, theirs, sign, same_base=False):
    if mine is None or theirs is None:
        return False, None
    d = mine - theirs
    if measure == 'voiced_frac' or measure[:7] in ('voiced_', 'creak_h', 'creak_m', 'creak_t'):
        # a share of the frames: a fifth of the sound voiced or not is the least that counts
        return (d * sign >= 0.2), round(d, 2)
    if measure == 'voicing_slope':
        # dB per 10 ms: twice the measure's error on a synthetic swell (0.4, selftest.py)
        return (d * sign >= 0.8), round(d, 2)
    if measure.endswith('_found'):
        # found or not (in the median context): one against nought (D78)
        return (d * sign >= 1), round(d, 2)
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
    man = man_of(t, e)
    s = summary(cases, man) if e['kind'] == 'base' else {}
    losses = [d for d in diags if d['level'] == 'loss']
    a0 = dict(passed=not losses and not said_as.get('substitute'), losses=losses[:20],
              substitute=said_as.get('substitute'))
    a1 = check_a1(cases, man)
    # A2 on the phones under test: the vowels around a consonant are the context, not the sound
    # (a cardinal [i]'s F1, 217 Hz, sits on the voice's second harmonic, where the tracker fails, D15)
    creak = e['kind'] == 'modifier' and 'creaky_pct' in json.dumps(e.get('transform') or {})

    def a2_phone(cid, ph):
        # a stop the accent layer makes (ʔ's `<q') is a closure like any other: silent by nature,
        # its closure proved by A1, so check A passes over it as over the module's stops; a creaky
        # mark makes the voice's period irregular on purpose (diplophonia in the frames), so its
        # marked cases' F0 is not held to the frames' (D64)
        if man == 'stop' and ph['cls'] == 'made':
            ph = dict(ph, cls='stop')
        if creak and '_marked_' in cid:
            ph = dict(ph, req=dict(ph.get('req') or {}, f0_mid40_hz=None))
        if e['ipa'] == '̯' and '_marked_' in cid and ph['cls'] == 'vowel':
            # a non-syllabic vowel is a glide: check A compares a vowel's middle with its frames,
            # and a glide's middle is a transition, read off by the window's own width
            ph = dict(ph, cls='glide')
        return ph
    a2 = RP.check_a(dict(cases={cid: dict(c['gold'], phones=[a2_phone(cid, c['gold']['phones'][i]) for i in c['target']
                                                              if i < len(c['gold']['phones'])])
                                for cid, c in cases.items()}), E.pack(said_as['pack']).phone_module)
    if a2['a1_phones'] == 0 and not a2['substituted']:
        a2 = dict(a2, passed=True, note='nothing check A measures in the sound under test (a stop, a made sound)')
    a2 = {k: a2[k] for k in ('passed', 'note', 'a1_phones', 'a1_silent', 'a2_checks', 'a2_ok', 'a2_rate', 'substituted',
                             'problems') if k in a2}
    if e['kind'] == 'base':
        b3 = check_b3(e, s)
        air = e['features'].get('airstream', 'pulmonic')
        need = {'click': 'burst ', 'implosive': 'closure voicing slope', 'percussive': 'strike '}.get(air)
        if air != 'pulmonic' and not (need and any(k.startswith(need) for k in b3['targets'])):
            # what makes a click or an implosive is its airstream: without its own targets
            # (T-click, T-airstream, T-percussive) the generic checks prove the place, not the sound
            b3['targets']['airstream (T-click, T-airstream)'] = dict(target=air, measured=None, within=False)
            b3['passed'] = False
    elif e['kind'] == 'modifier' or (e['kind'] == 'tie' and not PZ.check_of(e)):
        # (a joining mark that is a mark of each side too, extIPA's sliding articulation, is
        # judged as a mark: the pair it joins against the same letters in sequence)
        b3 = check_shift(t, sid, cases)
        s = b3.pop('summary')
        # every marked case must have been composed with the mark, not said without it
        marked = [c for cid, c in cases.items() if '_marked_' in cid]
        unc = [cid for cid, c in cases.items() if '_marked_' in cid and not any(
            d['kind'] == 'composed' or d['kind'] == 'tone-made' for d in c['diag'] + c.get('fe_diag', []))]
        if unc and marked:
            a0 = dict(a0, passed=False, not_composed=unc[:6])
    elif e['kind'] == 'composite':
        # a Tier B spelling (D68): its mark's test against the plain base, and every marked case
        # said as written: composed by the front-end, or a line of its own (a letter standing for a
        # Tier A spelling), never taken apart
        b3 = check_shift(t, sid, cases)
        s = b3.pop('summary')
        unc = [cid for cid, c in cases.items() if ('_marked_' in cid or cid == 'alone') and not (
            e.get('said_as') or any(d['kind'] == 'composed' for d in c['diag'] + c.get('fe_diag', [])))]
        if unc:
            a0 = dict(a0, passed=False, not_composed=unc[:6])
        if e.get('said_as'):
            # its line is the spelling's composition, written by the adapter: a part of a mark's
            # transform it could not express is a loss like any other
            lost = AD.compose(t, e['parts'][0], e['parts'][1:], E.pack(said_as['pack']).template)['lost']
            if lost:
                a0 = dict(a0, passed=False, composition_lost=lost)
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
        # Q24: the mark against its base context by context, so that the context's variation
        # cancels: one summary a context, plain and marked, and their difference
        ctx = sorted(c[len(base + '_plain_'):] for c in cases if c.startswith(base + '_plain_')
                     and base + '_marked_' + c[len(base + '_plain_'):] in cases)
        pair = {x: (summary({x: cases[base + '_plain_' + x]}, man), summary({x: cases[base + '_marked_' + x]}, man))
                for x in ctx}

        def paired_median(m, sp=sp, sm=sm, pair=pair, ctx=ctx):
            """(the differences, the plain median moved by their median), or (None, the marked
            median) where fewer than two contexts have the measure on both, as before Q24."""
            diffs = sorted(pair[x][1][m] - pair[x][0][m] for x in ctx
                           if pair[x][0].get(m) is not None and pair[x][1].get(m) is not None)
            if len(diffs) < 2 or sp.get(m) is None:
                return None, sm.get(m)
            n = len(diffs)
            return diffs, sp[m] + (diffs[n // 2] if n % 2 else (diffs[n // 2 - 1] + diffs[n // 2]) / 2.0)
        checked = 0
        for sh in tests.get('shift', []):
            m = sh['measure']
            if sp.get(m) is None and sm.get(m) is None:
                continue
            if man == 'vowel' and m.startswith('edge_'):
                # a vowel's edges are its neighbours' places: since the consonant after a vowel
                # starts at its own ratios (D64, `ant'), a mark on the vowel reaches them no more,
                # and its middle (F2_50_hz) is what moves
                continue
            diffs, mine = paired_median(m)
            paired = diffs is not None
            ok, d = contrast_ok(m, mine, sp.get(m), sh['sign'], same_base=True) if m != 'burst_found' else (
                (mine is not None and sp.get(m) is not None and (mine - sp[m]) * sh['sign'] >= 1),
                None if mine is None or sp.get(m) is None else mine - sp[m])
            targets['%s %s' % (t.sounds[base]['ipa'], m)] = dict(target='%+d' % sh['sign'], measured=d, within=ok,
                                                               plain=sp.get(m), marked=sm.get(m),
                                                               paired=[round(x, 3) for x in diffs] if paired else None)
            checked += 1
            ok_all &= ok
        for m in tests.get('steady', []):
            # the other edge of the sound as it was (a voicing mark at one end, D70): the paired
            # difference under the contrast minimum
            diffs, mine = paired_median(m)
            d = None if mine is None or sp.get(m) is None else mine - sp[m]
            need = 0.2 if m.startswith(('voiced_', 'creak_')) else CONTRAST_MIN['ms'] if m.endswith('_ms') else \
                CONTRAST_MIN['db'] if m.endswith('_db') else CONTRAST_MIN['hz_rel'] * abs(sp.get(m) or 0)
            ok = d is not None and abs(d) < need
            targets['%s %s steady' % (t.sounds[base]['ipa'], m)] = dict(
                target='within %s' % need, measured=None if d is None else round(d, 2), within=ok, plain=sp.get(m),
                marked=sm.get(m), paired=[round(x, 3) for x in diffs] if diffs else None)
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
    # The chart's marks belong to no language: the pack's own lengths of stressed and unstressed
    # vowels (hi's profile: stressed=88 weak=112, which shortened every stressed vowel the stress
    # mark was proved on) are left out, so that the engine's neutral 100 per cent speaks (D64)
    lines = [' '.join(w for w in l.split(' ') if not re.match(r'(stressed|weak)=', w)) if l.startswith('accent ')
             else l for l in lines]
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
    if (t.sounds[sid].get('tests') or {}).get('notation'):
        # an entry of extIPA's own reading (Q18) is said by a map that declares extIPA: the
        # table's map with that one line in front, so the proof keeps the table's map's hash
        with open(map_path, encoding='utf-8') as f:
            body = f.read()
        map_path = map_path[:-4] + '-%s.map' % t.sounds[sid]['tests']['notation']
        with open(map_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('notation %s\n' % t.sounds[sid]['tests']['notation'] + body)
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
                    work=os.path.join(SWEEP_WORK, T.file_id(sid).replace('+', '_')))
    cases = {}
    for (cid, text, out, d), r_ in zip(inputs, rend):
        diags += r_['diag'][len(d):] if r_['diag'][:len(d)] == d else r_['diag']
        bm_ = t.sounds.get(cid.split('_')[0]) if e['kind'] in ('modifier', 'tie') else None
        c = measure(r_, p, cid, man_of(t, e), layer, base_man=manner(bm_) if bm_ and bm_['kind'] == 'base' else None)
        c.update(ipa=text, said=out, diag=r_['diag'], fe_diag=d, wav_sha256=r_['wav_sha256'])
        x_, rate_ = E.read_wav(r_['wav'])
        c['clipped'], c['near_full_scale'] = clipped(x_)
        if PZ.check_of(e):
            c['pros'] = PZ.measure(x_, rate_, c['phones'], r_['frames'],
                                   stops='T-double' in (e.get('tests') or {}).get('checks', []))
        cases[cid] = c
    verdict = judge(t, sid, cases, diags, said_as)
    return dict(id=sid, ipa=e['ipa'], name=e['name'], template=template, pack=pack, staged=E.STAGE or None,
                frontend=E.FRONTEND, map=os.path.relpath(map_path, ROOT) if map_path.startswith(ROOT) else map_path,
                map_sha256=map_sha, said_as=said_as, cases=cases, **verdict)


# The USP's design loop (playbook 1.6, step 6): a target missed is corrected from what was measured
# and the entry said again, at most five rounds. A correction is a `trim' for this template only:
# the specification is never touched (DESIGN.md 5).
ROUNDS = 5
ABS_KEYS = ('vot', 'trate', 'tapms', 'bgain', 'impl')     # corrected as values; every other key as a ratio
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
            # half the miss once the key has been corrected before: the measure moves in steps of
            # a pitch period (p: vot 16 read 6 ms, 22 read 18, 28 read 32), and the whole miss
            # jumped from one side of the target to the other every round (D64)
            nxt = cur + (tg['target'] - tg['measured']) * (0.5 if 'vot' in trims else 1.0)
            if nxt >= 0:
                out['vot'] = nxt
                any_ = True
            continue
        if k == 'burst level_db' and not tg['within'] and tg['measured'] is not None and tg.get('contexts', 0) >= 2:
            # a burst's level against the vowel after it: C12's gain moved by the dB missed, half
            # of it once corrected before (the vowels' level is held to the module's, D64, so a
            # gain chosen against the louder vowels before read 5 to 7 dB high); 0 to 40 as the
            # layer takes it
            cur = out.get('bgain', (res['said_as']['keys'] or {}).get('bgain', 0))
            out['bgain'] = min(40.0, max(0.0, cur + (tg['target'] - tg['measured']) * (0.5 if 'bgain' in trims else 1.0)))
            any_ = True
            continue
        if k == 'closure voicing slope' and not tg['within'] and tg['measured'] is not None \
                and tg.get('contexts', 0) >= 2:
            # an implosive's swell: `impl' is the dB the voice rises through the closure, the slope
            # dB per 10 ms over about 40 ms of it; chosen against the louder vowels before D64's
            # level hold. Never 1, which is the packs' own 14 dB
            cur = out.get('impl', (res['said_as']['keys'] or {}).get('impl', 12))
            nxt = cur + (tg['target'] - tg['measured']) * 4.0 * (0.5 if 'impl' in trims else 1.0)
            out['impl'] = min(40.0, max(2.0, nxt))
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
                                                proof='ipa/proofs/%s.json' % T.file_id(sid)) for k, v in sorted(trims.items())]


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
            spent = len(history) >= ROUNDS
            break
        nxt = corrections(res, trims)
        if nxt is None:
            spent = True
            break
        trims = nxt
        with_trims(t, sid, template, trims)
        res = say_entry(t, sid, template, pack)
    tg = res['B3']['targets']
    if spent and not res['B3']['passed'] and all(o['within'] or o.get('approx_ok') for o in tg.values()):
        # every target left is inside the bound its approximate entry states, after the rounds
        for o in tg.values():
            if not o['within']:
                o.update(within=True, approximate=o.pop('approx_ok'))
        res['B3']['passed'] = True
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
                path = os.path.join(PROOFS, T.file_id(c['with']) + '.json')
                other = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else None
            if c.get('base'):
                # a mark against another mark (or their spellings) on the same base, as said (D73):
                # the marked sounds' measures, each over the same contexts
                def marked(r, base=c['base']):
                    return (((r or {}).get('summary') or {}).get(base) or {}).get('marked') or {}
                mine, theirs = marked(res).get(c['measure']), marked(other).get(c['measure'])
            else:
                def flat(r):
                    # a composite's summary is per base, its plain and marked sounds: against one,
                    # its marked sound on its base (𝼀 against ʩ, D77); against one of several
                    # bases, nothing (the contrast must name its `base')
                    s_ = (r or {}).get('summary') or {}
                    if s_ and all(isinstance(v, dict) and 'marked' in v for v in s_.values()):
                        return (next(iter(s_.values()))['marked'] or {}) if len(s_) == 1 else {}
                    return s_
                mine, theirs = flat(res).get(c['measure']), flat(other).get(c['measure'])
            ok, d = contrast_ok(c['measure'], mine, theirs, c['sign'])
            why = specified(t, sid, c)
            row = dict(c, mine=mine, theirs=theirs, difference=d, holds=ok,
                       required=why is True, basis=why if why is not True else 'the specifications differ so')
            ap = c.get('approximate')
            # (never for two symbols the chart tells apart: `distinct', D73)
            if not ok and ap and not c.get('distinct') and t.sounds[sid].get('approximate') and d is not None \
                    and d * c['sign'] >= ap['min'] and res['B3']['passed']:
                # an entry marked approximate (its deviation stated, R7) may hold a contrast to a
                # smaller stated difference, once nothing in B3 is left to correct: reported as
                # approximate, never as met (D65)
                row.update(holds=True, approximate=dict(bound=ap, deviation=t.sounds[sid].get('deviation')))
            b2.append(row)
        res['B2'] = dict(passed=all(x['holds'] for x in b2 if x['required']), contrasts=b2)
        res['passed'] = all(res[k]['passed'] for k in ('A0', 'A1', 'A2', 'B3', 'B2'))
    for sid, res in results.items():
        # a Tier B composite stands on its parts (D68): one built on a letter not yet proved is not
        # yet (after every entry of the run is judged: a part may come later in the order)
        if 'summary' not in res:
            continue
        undone = [x for x in t.sounds[sid].get('parts') or [] if not (
            (results.get(x) or {}).get('passed') if x in results else t.sounds[x].get('state') in ('mapped', 'composed', 'created'))]
        if undone:
            res['A0'] = dict(res['A0'], passed=False, parts_not_done=undone)
            res['passed'] = False
    os.makedirs(PROOFS, exist_ok=True)
    for sid, res in results.items():
        if 'summary' not in res:
            continue
        slim = json.loads(json.dumps(res, default=float))
        for c in slim['cases'].values():
            c.pop('gold', None)
        with open(os.path.join(PROOFS, T.file_id(sid) + '.json'), 'w', encoding='utf-8', newline='\n') as f:
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
                k, v, 'false' if k in ABS_KEYS else 'true', T.file_id(sid))
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
        path = os.path.join(PROOFS, T.file_id(sid) + '.json')
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
            line = 'proof = "ipa/proofs/%s.json"' % T.file_id(sid)
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
