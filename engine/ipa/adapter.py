"""The engine adapter (DESIGN.md 3.3, capability C3): an entry of the master table, realised for one
template module of this engine. MIT licence.

    python engine/ipa/adapter.py <id> [template]       the sound line, the carrier, what is not realised

For one entry and one template:
  1. the entry's feature bundle (a base letter's own; composed marks come with C4);
  2. the carrier: the entry's own choice (`realization.openevv.carrier`), or the module phone
     nearest by features (ipa/features.toml's weights; the module's phones read from their IPA in
     engine/espeak_phonemes.py with the IPA reader);
  3. targets in hertz become ratios of what the carrier measures in the module
     (engine/accent/chassis/<template>.json): F1 to F4 as f1..f4 per cent; a fricative's noise
     peak by moving the carrier's noise resonances (F2 to F4) by the ratio of the peaks;
  4. times: the inherent length as `dur` per cent of the carrier's; the voice onset time as `vot`
     in milliseconds;
  5. the entry's `trim` for this template (corrections found by measuring) is applied on top;
  6. the result is a `sound` line in the format the product reads (docs/SOUNDS.md).
What it cannot realise as specified (a formant above 5 kHz, a field it has no key for) is returned
in `unrealised`, never dropped: the entry then says `approximate` with that deviation.
"""

import json
import math
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import reader as R  # noqa: E402
import table as T  # noqa: E402

CHASSIS = os.path.join(ROOT, 'engine', 'accent', 'chassis')
BASE_OF = {'dedx': 'dede', 'esex': 'eses', 'itix': 'itit', 'engx': 'engb', 'esux': 'esus', 'frfx': 'frfr',
           'enux': 'enus'}
MAX_FORMANT_HZ = 5000      # F6 of DESIGN.md: the synthesiser places no formant above this


def chassis(template):
    with open(os.path.join(CHASSIS, template + '.json'), encoding='utf-8') as f:
        return json.load(f)['phones']


def module_phones(template):
    """{module phone: feature bundle}, for the phones whose IPA is one segment."""
    import espeak_phonemes as EP
    tm = EP.TEMPLATES[BASE_OF.get(template, template)]
    t = R.table()
    out = {}
    for name, ipa in list(tm.vowels.items()) + list(tm.consonants.items()):
        try:
            r = R.read(ipa, strict=False)
        except R.ReaderError:
            continue
        segs = [it for it in r['items'] if it['t'] == 'seg' and 'tied' not in it]
        if len(segs) == 1 and len(r['items']) == 1 and not r['warnings']:
            out[name] = segs[0]['features']
    return out


def distance(t, a, b):
    """The nearest-letter cost of ipa/features.toml between two bundles."""
    w = t.features['weights']
    if a.get('class') != b.get('class'):
        return w['class']
    if a['class'] == 'vowel':
        cv = w['vowel']
        scale = lambda k: t.features['vowel'][k]['scale']  # noqa: E731
        d = cv['height_step'] * abs(scale('height').index(a['height']) - scale('height').index(b['height']))
        d += cv['backness_step'] * abs(scale('backness').index(a['backness']) - scale('backness').index(b['backness']))
        d += cv['rounding'] * (a.get('rounding') != b.get('rounding'))
        return d
    cw = w['consonant']
    places = t.features['consonant']['place']['scale']
    d = cw['place_step'] * abs(places.index(a['place']) - places.index(b['place']))
    for k in ('stricture', 'airstream', 'nasal', 'lateral', 'sibilant', 'place2', 'voicing'):
        d += cw[k] * (a.get(k) != b.get(k))
    return d


def carrier(t, entry, template):
    own = ((entry.get('realization') or {}).get('openevv') or {}).get('carrier')
    f = T.full_bundle(t, entry['features'])
    if own:
        # a phone the layer makes beside a vowel is made for the entry; a module phone named by
        # the entry is still that phone, as far from the letter as its features say
        phones = module_phones(template)
        return own, 0 if own.startswith('<') or own not in phones else distance(t, f, T.full_bundle(t, phones[own]))
    measured = chassis(template)
    best = min(((distance(t, f, T.full_bundle(t, g)), name) for name, g in module_phones(template).items()
                if name in measured))
    return best[1], best[0]


def _v(x):
    return x['v'] if isinstance(x, dict) else x


def realize(t, sid, template, carrier_meas=None):
    """{'keys': {key: value}, 'carrier': phone, 'distance': cost, 'unrealised': [...], 'rules': [...]}.

    carrier_meas: what the carrier measured when rendered (the loop passes it), for targets the
    chassis does not hold (a fricative's noise peak).

    A carrier named with `<` (`<q`, `<h`) is a sound the accent layer makes beside a vowel: it has
    no chassis, so only times and the engine's own keys apply to it."""
    e = t.sounds[sid]
    spec = e.get('spec') or {}
    car, dist = carrier(t, e, template)
    layer = car.startswith('<')
    ch = None if layer else chassis(template).get(car)
    if ch is None and not layer:
        raise ValueError('%s has no chassis measurement in %s' % (car, template))
    cls = e['features']['class']
    keys, unrealised, rules = {}, [], []
    keys_peak = None

    def ratio(key, hz, base, what):
        if hz > MAX_FORMANT_HZ:
            unrealised.append('%s %s Hz: above the %d Hz the synthesiser can place' % (what, hz, MAX_FORMANT_HZ))
            return
        keys[key] = int(round(100.0 * hz / base))
        rules.append('%s = %s target %s / carrier %s %d Hz' % (key, what, hz, car, base))

    if layer:
        for k in ('formants', 'locus', 'bandwidths', 'noise', 'glide'):
            if k in spec:
                unrealised.append('%s: the layer-made carrier %s takes no ratio' % (k, car))
    else:
        # steady targets (a vowel, a sonorant) against the carrier's own formants; an obstruent's
        # place against the carrier's locus: where the vowels beside it point
        for i, k in enumerate(('F1', 'F2', 'F3', 'F4')):
            target = (spec.get('formants') or {}).get(k)
            if target is not None:
                ratio('f%d' % (i + 1), _v(target), ch['f'][i], k)
            target = (spec.get('locus') or {}).get(k)
            slope = (spec.get('locus_slope') or {}).get(k)
            if target is not None and slope is not None and template not in VOICE_F5:
                # a locus with a slope is the point of an equation, not an edge: as a ratio to the
                # carrier it would send every vowel there (q x 0.36, the review of D67). Until the
                # template's F5 is measured the place is not realised, and said so.
                unrealised.append('locus %s: a locus equation, and the %s voice\'s F5 is not measured '
                                  '(adapter.VOICE_F5)' % (k, template))
            elif target is not None and slope is not None:
                # a locus with its equation's slope (Q21): the layer takes the vowel's edge to
                # locus + slope x (vowel - locus), the locus in the voice's own scale (per mille
                # of its F5), so a place far from a vowel never bends it past where it sends it
                if 'lk' in keys and keys['lk'] != int(round(100.0 * _v(slope))):
                    unrealised.append('locus_slope %s: the layer takes one slope for every locus' % k)
                    continue
                keys['l%d' % (i + 1)] = int(round(1000.0 * _v(target) / VOICE_F5[template]))
                keys['lk'] = int(round(100.0 * _v(slope)))
                rules.append('l%d = locus %s %s Hz / F5 %d Hz of the %s voice, per mille; lk = slope %s'
                             % (i + 1, k, _v(target), VOICE_F5[template], template, _v(slope)))
            elif target is not None:
                if 'locus' not in ch:
                    unrealised.append('locus %s: the carrier %s has no measured locus' % (k, car))
                else:
                    ratio('f%d' % (i + 1), _v(target), ch['locus'][i], 'locus ' + k)
        for i, k in enumerate(('B1', 'B2', 'B3')):
            target = (spec.get('bandwidths') or {}).get(k)
            if target is not None:
                if 'b' not in ch:
                    unrealised.append('bandwidth %s: the carrier %s has none measured' % (k, car))
                else:
                    keys['b%d' % (i + 1)] = int(round(100.0 * _v(target) / ch['b'][i]))
                    rules.append('b%d = %s %s / carrier %s %d Hz' % (i + 1, k, _v(target), car, ch['b'][i]))
        glide = spec.get('glide') or {}
        for i, k in enumerate(('F1', 'F2', 'F3')):
            if k in glide:
                keys['g%d' % (i + 1)] = int(round(100.0 * _v(glide[k]) / ch['f'][i]))
                keys['glide'] = 1
                rules.append('g%d = glide end %s %s / carrier %s %d Hz' % (i + 1, k, _v(glide[k]), car, ch['f'][i]))
        peak = (spec.get('noise') or {}).get('peak_hz')
        if peak is not None:
            # The noise on one resonance: the one of F2 to F4 nearest the peak is moved to it and
            # carries the noise, the others 20 dB under it. Moving all of them together leaves
            # a module's two noise peaks, and a measured peak that jumps between them (D58).
            hz = _v(peak)
            j = min((1, 2, 3), key=lambda i: abs(math.log(hz / ch['f'][i])))
            keys['f%d' % (j + 1)] = int(round(100.0 * hz / ch['f'][j]))
            level = max([a for a in ch.get('amp', [])[:5] if a] or [60])
            for i in range(5):
                own = (ch.get('amp') or [0] * 6)[i] or 0
                keys['a%d' % (i + 2)] = level if i == j - 1 else min(own, max(0, level - 20))
            rules.append('f%d = noise peak %s / carrier %s F%d %d Hz; the noise on it (a%d=%d, the others at most %d)' % (
                j + 1, hz, car, j + 1, ch['f'][j], j + 1, level, max(0, level - 20)))
            keys_peak = 'f%d' % (j + 1)
    dur = (spec.get('duration') or {}).get('inherent_ms')
    if dur is not None:
        if layer:
            keys['ms'] = int(round(_v(dur)))
            rules.append('ms = %s ms' % _v(dur))
        else:
            key = 'dur' if cls == 'vowel' else 'hold'
            keys[key] = int(round(100.0 * _v(dur) / ch['ms']))
            rules.append('%s = %s ms / carrier %s %d ms' % (key, _v(dur), car, ch['ms']))
    vot = spec.get('vot_ms')
    if vot is not None:
        keys['vot'] = int(round(_v(vot)))
        rules.append('vot = %s ms' % _v(vot))
    tap = spec.get('tap') or {}
    if 'closures' in tap:
        keys['tap'] = int(_v(tap['closures']))
        rules.append('tap = %s closures' % _v(tap['closures']))
    if 'closed_ms' in tap:
        keys['tapms'] = int(round(_v(tap['closed_ms'])))
        rules.append('tapms = %s ms' % _v(tap['closed_ms']))
    trill = spec.get('trill') or {}
    if 'rate_hz' in trill:
        # C11: closures at a stated rate, the count as the sound's length allows
        keys['trate'] = int(round(_v(trill['rate_hz'])))
        rules.append('trate = %s closures a second' % _v(trill['rate_hz']))
    if 'closures' in trill and 'rate_hz' not in trill:
        keys['tap'] = int(_v(trill['closures']))
        rules.append('tap = %s closures' % _v(trill['closures']))
    if 'closed_ms' in trill:
        # the layer's closure is flat for `tapms' with a 5 ms ramp either side, so it is down by
        # half its depth for tapms + 5 ms: that is the closed phase the specification states (D64)
        keys['tapms'] = max(1, int(round(_v(trill['closed_ms']) - 5)))
        rules.append('tapms = %s ms closed - 5 ms (half of each ramp of the layer\'s closure)' % _v(trill['closed_ms']))
    nas = (spec.get('nasal') or {}).get('open_pct')
    if nas is not None:
        keys['nas'] = int(round(_v(nas)))
        rules.append('nas = %s per cent' % _v(nas))
    for k in ('burst', 'closure'):
        if k in spec:
            # a click's burst and an implosive's closure (T-click, T-airstream): targets the sweep
            # measures, met through the entry's own engine keys (realization.openevv.keys)
            rules.append('%s: measured targets, realised by the engine keys below' % k)
    known = {'formants', 'locus', 'locus_slope', 'bandwidths', 'glide', 'noise', 'duration', 'vot_ms', 'tap',
             'nasal', 'trill', 'burst', 'closure'}
    for k in spec:
        if k not in known:
            unrealised.append('%s: the adapter has no key for it yet' % k)
    ov = (e.get('realization') or {}).get('openevv') or {}
    for k, v in (ov.get('keys') or {}).items():
        keys[k] = int(_v(v))
        rules.append('%s = %s (an engine key, %s)' % (k, _v(v), v.get('tag') if isinstance(v, dict) else ''))
    for tr in (ov.get('trim') or {}).get(template, []):
        keys[tr['key']] = keys.get(tr['key'], 100 if tr['key'] in RATIO_KEYS or tr['key'][0] in 'fbg' else 0)
        keys[tr['key']] = int(round(keys[tr['key']] * tr['v'] / 100.0)) if tr.get('scale') else int(tr['v'])
        rules.append('trim %s %s (%s)' % (tr['key'], tr['v'], tr.get('tag')))
    f = e['features']
    if not layer and cls == 'consonant' and ('locus' in spec or 'formants' in spec) and keys_peak is None \
            and (any(keys.get('f%d' % i, 100) != 100 for i in (1, 2, 3, 4)) or 'lk' in keys) and 'ant' not in keys:
        # the sound before ends at this one's formants: the accent layer otherwise moves only the
        # sound after, and the vowel before glided to the carrier's place (ʈ's to t's, D64)
        keys['ant'] = ANT_MS
        rules.append('ant = %d ms: the sound before meets this place over the engine\'s own transition time '
                     '(the profile\'s reach)' % ANT_MS)
    if not layer and 'av' not in keys and (cls == 'vowel' or (f.get('stricture') == 'approximation'
                                                             and f.get('voicing') == 'voiced')):
        rise = level_rise(ch, keys)
        if rise >= 1.0:
            # the voice and the breath on it both pass through the resonators: both are held
            keys['av'] = -int(math.ceil(rise))
            if 'ah' not in keys:
                keys['ah'] = keys['av']
            rules.append('av = ah = %d dB: the level held to the carrier %s\'s (with these formants the '
                         'resonators\' peak gain rises %.1f dB, level_rise)' % (keys['av'], car, rise))
    return dict(keys=keys, carrier=car, distance=dist, unrealised=unrealised, rules=rules, peak_key=keys_peak)


# How long a vowel takes to reach its formants from the consonant before it: the accent layer's
# `reach' as every profile has it (evv_accent.c, 50 ms); the way into a consonant takes as long.
ANT_MS = 50

# What every voiced frame of the dedx module carries above F4 (the sweep's frames): F5 and the
# bandwidths of F4 and F5; and the bandwidths of a carrier that has none measured.
F5_HZ, B4_HZ, B5_HZ = 3900, 330, 260
B_DEFAULT = [120, 100, 150]
# The voice's own F5 at preset 1, per template: the scale a locus is given in (`l2`, Q21). Only
# the reference template's is measured; another template keeps the ratio until its F5 is.
VOICE_F5 = {'dedx': F5_HZ}


def level_rise(ch, keys):
    """How much louder, in dB at the waveform's peak, the carrier's voice comes out of the cascade
    of resonators with the line's formants than with its own: the largest rise over F0 90 to 200 Hz.

    Moving F2 and F3 up towards the fixed F4 and F5 stacks resonances: the table's [i] (F3 3654,
    and the accent layer's F4 >= F3 + 200 makes F4 3854, beside F5 3900) came out 16 dB above the
    module's own [i] and clipped (D64). The rise is computed, not measured: Klatt's resonators
    (synth.py) driven by the same pulse train, F4 raised as the accent layer raises it."""
    b0 = ch.get('b') or B_DEFAULT
    own = [ch['f'][i] for i in range(4)]
    new = [ch['f'][i] * keys.get('f%d' % (i + 1), 100) / 100.0 for i in range(4)]
    bw = [b0[i] * keys.get('b%d' % (i + 1), 100) / 100.0 for i in range(3)]
    for fs in (own, new):
        for i in (1, 2, 3):
            fs[i] = max(fs[i], fs[i - 1] + 200)
    return _level_rise(tuple(int(round(x)) for x in own), tuple(int(round(x)) for x in new),
                       tuple(int(round(x)) for x in b0[:3]), tuple(int(round(x)) for x in bw))


_RISE = {}


def _level_rise(own, new, b_own, b_new):
    k = (own, new, b_own, b_new)
    if k not in _RISE:
        import numpy as np
        sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
        import synth as S

        def peak(fs, bs, f0):
            x = S.pulses(f0, 300)
            for fr, b in zip(list(fs) + [F5_HZ], list(bs) + [B4_HZ, B5_HZ]):
                x = S.resonator(x, fr, b)
            return float(np.abs(x[len(x) // 2:]).max())
        _RISE[k] = max(20 * math.log10(peak(new, b_new, f0) / peak(own, b_own, f0)) for f0 in (90, 110, 130, 160, 200))
    return _RISE[k]


def sound_line(name, keys):
    return 'sound %s %s' % (name, ' '.join('%s=%d' % kv for kv in sorted(keys.items())))


# ---- C4: composition when speaking (DESIGN.md 2.3) -----------------------------------------------
# A modifier's transform (ipa/table: `transform.<class>`) in the engine's own terms: a ratio key is
# multiplied, a time is added. The front-end merges these into a base letter's line; the adapter
# composes the same thing exactly; a test holds the two together (compose_test.py).
OPS = {('vot_ms', 'add'): ('vot', '+'), ('duration.inherent_ms', 'scale'): ('dur', '*')}
for _i in (1, 2, 3, 4):
    OPS[('formants.F%d' % _i, 'scale')] = ('f%d' % _i, '*')
    OPS[('locus.F%d' % _i, 'scale')] = ('f%d' % _i, '*')
# set: a value the sound takes whatever the base had (DESIGN.md 2.2's fourth operation). These
# are engine-neutral in meaning and proportional in this engine's own units: the nose open so far,
# phonation so far from modal, voicing on or off, the release there or not.
OPS.update({('nasal.open_pct', 'set'): ('nas', '='), ('phonation.breathy_pct', 'set'): ('breathy', '='),
            ('phonation.creaky_pct', 'set'): ('creak', '='), ('voicing.voiced', 'set'): ('voi', '='),
            ('release.unreleased', 'set'): ('noburst', '='), ('release.ejective_silence_ms', 'set'): ('ej', '='),
            ('release.burst_ms', 'set'): ('burstms', '='), ('release.burst_gain_db', 'set'): ('bgain', '='),
            ('release.implosive', 'set'): ('impl', '='), ('breath.whisper_db', 'set'): ('whisper', '='),
            ('trill.rate_hz', 'set'): ('trate', '='), ('tap.closures', 'set'): ('tap', '=')})
# noise added with the voice kept (D69: extIPA's nasal friction): its level, and its level on each
# resonance of the parallel branch (F2 to F6) and on the flat bypass, in this engine's dB
OPS.update({('noise.level_db', 'set'): ('fric', '='), ('noise.flat_db', 'set'): ('ab', '=')})
for _i in (2, 3, 4, 5, 6):
    OPS[('noise.F%d_db' % _i, 'set')] = ('a%d' % _i, '=')
# the part of the sound a voicing or phonation mark is said over (extIPA's partial voicing and
# devoicing, its displaced voicing and creaky offglide), in per cent of it; breath before a stop's
# closure (its pre-aspiration); an onset time the sound takes whatever the base had (unaspirated)
OPS.update({('voicing.part_from_pct', 'set'): ('vfrom', '='), ('voicing.part_to_pct', 'set'): ('vto', '='),
            ('release.preaspiration_ms', 'set'): ('pre', '='), ('vot_ms', 'set'): ('vot', '=')})
# levels moved from the base's own, in this engine's dB (extIPA's strong and weak articulation,
# its denasal): the voice, the friction (its noise, a stop's burst too) and the breath, added to the
# base's own offset (a sound without one has 0 dB of it, LEVEL_KEYS); the tilt
# of the voice's spectrum the sound takes (the layer's 0 to 41, a voiced closure's being 24 to 35);
# a resonance's bandwidth scaled (the cascade's, F1 to F4)
OPS.update({('voice.level_db', 'add'): ('av', '+'), ('noise.gain_db', 'add'): ('af', '+'),
            ('breath.gain_db', 'add'): ('ah', '+'), ('phonation.tilt_db', 'set'): ('tl', '=')})
LEVEL_KEYS = {'av', 'ah', 'af'}
for _i in (1, 2, 3, 4):
    OPS[('bandwidths.B%d' % _i, 'scale')] = ('b%d' % _i, '*')
# a sound's own pitch, away from the voice's line (extIPA's ingressive airflow): semitones in the
# table, tenths of one in the layer's `pst'
OPS[('pitch.offset_st', 'set')] = ('pst', '=')
# a stop released into friction (extIPA's fricated releases, D72): how long after the release, and
# its level in this engine's dB, and the voice under it moved (a voiced stop's); its spectrum is the noise
# keys above (a2 to a6, ab)
OPS.update({('release.fricated_ms', 'set'): ('frel', '='), ('release.fricated_db', 'set'): ('frelaf', '='),
            ('release.fricated_voice_db', 'set'): ('frelav', '=')})
# and the friction's own F2 and F3, the named fricative's (D73: k with a superscript velar lateral
# against k with a superscript x, whose noise bands are the same): hertz in the table, per mille of
# the voice's own F5 in the layer's `frelf2', `frelf3' (as a place's `l2', `l3' are, Q21)
OPS.update({('release.fricated_F2', 'set'): ('frelf2', '='), ('release.fricated_F3', 'set'): ('frelf3', '=')})
VOICE_SCALE_KEYS = {'frelf2', 'frelf3'}
KEY_UNIT = {'pst': 10.0}
# a consonant's length is `hold', a vowel's `dur'
CLASS_KEY = {('consonant', 'dur'): 'hold'}
RATIO_KEYS = {'f1', 'f2', 'f3', 'f4', 'dur', 'hold', 'b1', 'b2', 'b3', 'b4'}      # absent: the carrier's own, 100


def _flat(tr, prefix=''):
    for k, v in tr.items():
        if isinstance(v, dict) and not ({'add', 'scale', 'set', 'toward'} & set(v)):
            yield from _flat(v, prefix + k + '.')
        else:
            yield prefix + k, v


def mod_ops(t, mid, cls, own=False, template='dedx'):
    """[(key, op, value)] for one modifier and class, or None if it has no transform for it;
    with what it could not express. A mark of two characters (`after_mark', Tier B) is its first
    mark's ops and then its own; `own' asks for its own alone (its map line, under its last
    character). A frequency in the voice's own scale needs the template's F5 (VOICE_F5)."""
    tr = ((t.sounds[mid].get('transform') or {}).get(cls))
    if tr is None:
        return None, []
    ops, lost = [], []
    am = t.sounds[mid].get('after_mark')
    if am and not own:
        ops, lost = mod_ops(t, am, cls, template=template)
        ops, lost = list(ops or []), list(lost)
    for path, v in _flat(tr):
        op = 'add' if 'add' in v else 'set' if 'set' in v else 'toward' if 'toward' in v else 'scale'
        if op == 'toward':
            m = re.match(r'(formants|locus)\.F([1-4])$', path)
            if not m:
                lost.append('%s toward: only a formant moves towards a target' % path)
                continue
            ops.append(('f' + m.group(2), '~', (v['toward'], v.get('part', 50))))
            continue
        key = OPS.get((path, op))
        if key is None:
            lost.append('%s %s: no engine key' % (path, op))
            continue
        if key[0] in VOICE_SCALE_KEYS:
            if template not in VOICE_F5:
                lost.append('%s: the %s voice\'s F5 is not measured (adapter.VOICE_F5)' % (path, template))
                continue
            ops.append((key[0], key[1], v[op] * 1000.0 / VOICE_F5[template]))
            continue
        ops.append((CLASS_KEY.get((cls, key[0]), key[0]), key[1],
                    v[op] * (100.0 if key[1] == '*' else KEY_UNIT.get(key[0], 1.0))))
    return ops, lost


def merge(keys, ops, exact=False, base_hz=None):
    """A base's keys with a modifier's ops. Ratios multiply (absent = 100), times add (absent: lost,
    since the module's own value is not known here). Returns (keys, lost)."""
    out, lost = dict(keys), []
    for key, op, val in ops:
        if op == '*':
            out[key] = out.get(key, 100) * val / 100.0
        elif op == '~':
            hz = (base_hz or {}).get(key)
            if not hz:
                lost.append('%s~: the letter has no %shz to move from' % (key, key))
                continue
            out[key] = out.get(key, 100) * (hz + (val[0] - hz) * val[1] / 100.0) / hz
        elif op == '=':
            out[key] = val
        elif key in out or key in LEVEL_KEYS:
            out[key] = out.get(key, 0) + val
        else:
            lost.append('%s+%s: the base has no %s to add to' % (key, val, key))
    return ({k: v if exact else int(round(v)) for k, v in out.items()}, lost)


def compose(t, base_sid, mod_sids, template, carrier_meas=None):
    """The adapter's own composition: the base realised unrounded, each modifier applied, rounded
    once at the end (the front-end rounds the base and each op first: they may differ by 1)."""
    r = realize(t, base_sid, template, carrier_meas)
    keys = dict(r['keys'])
    cls = t.sounds[base_sid]['features']['class']
    lost = []
    for m in mod_sids:
        ops, l1 = mod_ops(t, m, cls, template=template)
        lost += l1
        if ops is None:
            lost.append('%s has no transform for a %s' % (t.sounds[m]['ipa'], cls))
            continue
        hz = realised_hz(t, base_sid, template) if cls == 'vowel' else None
        keys, l2 = merge(keys, ops, exact=True, base_hz={'f%d' % (i + 1): x for i, x in enumerate(hz or [])})
        lost += l2
    return dict(keys={k: int(round(v + 1e-9)) for k, v in keys.items()}, carrier=r['carrier'], lost=lost)


def realised_hz(t, sid, template):
    """A vowel's F1 to F3 as its line realises it: the carrier's chassis times the entry's ratios."""
    r = realize(t, sid, template)
    ch = chassis(template).get(r['carrier'])
    if not ch or r['carrier'].startswith('<'):
        return None
    return [int(round(ch['f'][i] * r['keys'].get('f%d' % (i + 1), 100) / 100.0)) for i in range(3)]


def letter_line(t, sid, template='dedx', features=None, ipa=None):
    """A letter's `letter' line; a Tier B letter standing for a spelling gives that spelling's bundle."""
    f = features or T.full_bundle(t, t.sounds[sid]['features'])
    ipa = ipa or t.sounds[sid]['ipa']
    if f['class'] == 'vowel':
        v = t.features['vowel']
        hz = realised_hz(t, sid, template)
        return 'letter %s v height=%d backness=%d rounding=%s%s' % (
            ipa, v['height']['scale'].index(f['height']), v['backness']['scale'].index(f['backness']),
            f['rounding'], ''.join(' f%dhz=%d' % (i + 1, x) for i, x in enumerate(hz or [])))
    c = t.features['consonant']
    return 'letter %s c place=%d %s' % (ipa, c['place']['scale'].index(f['place']), ' '.join(
        '%s=%s' % (k, str(f[k]).lower()) for k in ('stricture', 'airstream', 'nasal', 'lateral', 'sibilant', 'place2',
                                                    'voicing')))


def weights_line(t):
    w = t.features['weights']
    return 'weights %s class=%d' % (' '.join('%s=%d' % kv for kv in list(w['consonant'].items()) +
                                             list(w['vowel'].items())), w['class'])


def map_name(sid):
    """The name a realised entry has in a map: `u` and its code points, within the 11 bytes a
    sound id may have (EVV_ID_LEN)."""
    import hashlib
    name = 'u' + '_'.join(sid.split(':', 1)[-1].replace('U+', '').lower().split('+'))  # a Tier B id's `B:' left out
    return name if len(name) <= 11 else 'u' + hashlib.sha1(sid.encode('ascii')).hexdigest()[:10]


def loop_proof(sid):
    """What prove.py's loop found for an entry (ipa/proofs/loop/<id>.json), or None."""
    path = os.path.join(ROOT, 'ipa', 'proofs', 'loop', T.file_id(sid) + '.json')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write(t, template, quiet=False):
    """ipa/realized/<template>.map: every letter of the table as this template's lines, so that the
    front-end can say any of them: the carrier, and a sound line where the entry moves it. A noise
    target uses the carrier's peak as the entry's loop measured it. A carrier at a feature distance
    with nothing to move it is written with a warning: it is the module's phone, not the letter."""
    lines = ['# The master table realised for %s (engine/ipa/adapter.py --write). Generated: do not edit.' % template,
             '# Each letter: its sound line (if it differs from the carrier), and its IPA said as the carrier.', '']
    n, unrealised, bare = 0, 0, 0
    for sid, e in sorted(t.sounds.items()):
        if e.get('kind') != 'base':
            continue
        pr = loop_proof(sid)
        meas = pr.get('carrier_measured') if pr else None
        failed = bool(pr) and pr.get('template') == template and pr.get('passed') is False
        r = realize(t, sid, template, meas)
        if r['keys']:
            name = map_name(sid)
            lines.append('%s    # %s %s' % (sound_line(name, r['keys']), sid, e['name']))
            said = '%s=%s' % (r['carrier'], name)
        else:
            lines.append('#   %s %s: the carrier as it is' % (sid, e['name']))
            said = r['carrier']
        if failed:
            # written, so that the line can be seen, but not proved: its measure stayed off target
            lines.append('#   NOT PROVED: ipa/proofs/loop/%s.json did not reach its targets on %s' % (sid, template))
            unrealised += 1
        if r['distance'] and not r['keys']:
            lines.append('#   SUBSTITUTE: the carrier %s is %s feature steps away and nothing moves it' % (
                r['carrier'], r['distance']))
            bare += 1
        for u in r['unrealised']:
            lines.append('#   not realised: %s' % u)
            unrealised += 1
        lines.append('%-12s %s' % (e['ipa'], said))
        n += 1
    # tied pairs (DESIGN.md 2.4): an affricate the template has is one segment, said as its phone;
    # the tie below says the same as the tie above
    made = set()
    for sid, e in sorted(t.sounds.items()):
        if e.get('kind') != 'tie':
            continue
        src = e if (e.get('realization') or {}).get('openevv', {}).get('tied') else t.sounds.get(e.get('equivalent_to'), {})
        pairs = ((src.get('realization') or {}).get('openevv', {}).get('tied') or {}).get(template, {})
        if pairs:
            lines += ['', '# tied pairs said as one phone of the module (%s %s)' % (e['ipa'], sid)]
        for pair, phone in sorted(pairs.items()):
            lines.append('%-12s %s' % (pair.replace('͡', e['ipa']), phone))
        # double articulations (4g): the two stops as they are realised, one after the other, each
        # with the keys the table adds to make them one closure with one release
        doubles = ((src.get('realization') or {}).get('openevv', {}).get('double') or {}).get(template, {})
        if doubles:
            lines += ['', '# double articulations, two phones under one closure (%s %s)' % (e['ipa'], sid)]
        by_ipa = {x['ipa']: s for s, x in t.sounds.items() if x.get('kind') == 'base'}
        for pair, how in sorted(doubles.items()):
            if any(letter not in by_ipa for letter in pair.split('͡')):
                lines.append('#   not realised: %s: a letter the table does not have' % pair)
                unrealised += 1
                continue
            said = []
            for k, letter in enumerate(pair.split('͡')):
                lsid = by_ipa[letter]
                r = realize(t, lsid, template, (loop_proof(lsid) or {}).get('carrier_measured'))
                keys = dict(r['keys'])
                keys.update({kk: _v(vv) for kk, vv in (how['add'][k] or {}).items()})
                # named for the pair and the part, so that a letter in two pairs is two sounds
                name = map_name('+'.join('U+%04X' % ord(c) for c in pair) + '+%d' % (k + 1))
                if name not in made:
                    made.add(name)
                    lines.append('%s    # %s, part %d of %s' % (sound_line(name, keys), lsid, k + 1, pair))
                said.append('%s=%s' % (r['carrier'], name))
            lines.append('%-12s %s' % (pair.replace('͡', e['ipa']), ' '.join(said)))
    # Tier B (D68): a new letter that stands for a Tier A spelling is that spelling as the front-end
    # composes it, a line of its own; marks after it compose on it like on any letter
    stands = [(sid, e) for sid, e in sorted(t.sounds.items()) if e.get('kind') == 'composite' and e.get('said_as')
              and len(e['ipa']) == 1]
    if stands:
        lines += ['', '# Tier B letters that stand for a Tier A spelling (ipa/table/tierb.toml, D68)']
    for sid, e in stands:
        c = compose(t, e['parts'][0], e['parts'][1:], template, (loop_proof(e['parts'][0]) or {}).get('carrier_measured'))
        for l in c['lost']:
            lines.append('#   not realised: %s %s' % (e['ipa'], l))
            unrealised += 1
        name = map_name(sid.split(':', 1)[1])
        lines.append('%s    # %s %s = %s' % (sound_line(name, c['keys']), sid, e['name'][:50], e['said_as']))
        lines.append('%-12s %s=%s' % (e['ipa'], c['carrier'], name))
        n += 1
    # C4: what the front-end needs to compose when speaking, and to fall back with a warning
    lines += ['', '# composition when speaking (C4): read only by a map with `version 2`',
              'version 2', weights_line(t)]
    for sid, e in sorted(t.sounds.items()):
        if e.get('kind') == 'base':
            lines.append(letter_line(t, sid, template))
    for sid, e in stands:
        # the letter of the spelling it stands for: a mark after it composes for that class
        import reader as RD
        f = RD.compose(t, t.sounds[e['parts'][0]]['features'], e['parts'][1:], lambda *_: None)
        lines.append(letter_line(t, e['parts'][0], template, features=f, ipa=e['ipa']))
    written = {}
    for sid, e in sorted(t.sounds.items(), key=lambda x: (x[1].get('tier') == 'B', x[0])):
        for cls in sorted((e.get('transform') or {})):
            ops, lost = mod_ops(t, sid, cls, own=True, template=template)
            for l in lost:
                lines.append('#   not realised: %s %s' % (e['ipa'], l))
                unrealised += 1
            if ops:
                # a mark of two characters has its own line under its second (`after_mark'); a
                # mark written before its letter a `premod' line (Tier B); one line a mark and class
                kind = 'premod' if e.get('placement') == 'before' else 'mod'
                mark = e['ipa'][-1] if e.get('after_mark') else e['ipa']
                body = ' '.join(('%s~%d:%d' % (k, v[0], v[1])) if op == '~' else '%s%s%d' % (k, op, int(round(v)))
                                for k, op, v in ops)
                was = written.get((kind, mark, cls))
                if was is not None:
                    if was[0] != body:
                        raise SystemExit('%s and %s ask for two %s lines for %s on a %s: %r, %r' % (
                            was[1], sid, kind, mark, cls, was[0], body))
                    continue
                written[(kind, mark, cls)] = (body, sid)
                # extIPA's own reading of a character the IPA reads otherwise (Q18): a line the
                # front-end reads only under `notation extipa'
                lines.append('%s%s %s %s %s    # %s' % ('extipa ' if e.get('notation') == 'extipa' else '', kind, mark,
                                                       cls[0], body, sid))
    # a mark the reader takes as another (ipa/aliases.toml `always'): the same line under it, since
    # the front-end composes by the character it is given (U+033E for U+034B, Q26)
    import reader as RD
    for alias, real in sorted(RD.ALWAYS.items()):
        for (kind, mark, cls), (body, sid) in sorted(written.items()):
            if mark == real and len(alias) == 1:
                lines.append('%s %s %s %s    # %s, spelt %s' % (kind, alias, cls[0], body, sid, 'U+%04X' % ord(alias)))
    # extIPA's reiteration (p\p\p, Tier B): what the front-end says at each `\', after a consonant
    # and after a vowel, before the sound is said again
    for sid, e in sorted(t.sounds.items()):
        for cls, ipa in sorted(((e.get('realization') or {}).get('openevv', {}).get('reiterate') or {}).items()):
            lines.append('reiterate %s %s    # %s' % (cls[0], ipa, sid))
    lines += pitch_lines(t)
    syl = ((t.sounds.get('U+0329') or {}).get('realization') or {}).get('openevv', {}).get('schwa_keys')
    if syl:
        lines += ['', '# a consonant marked syllabic (C7): the schwa that carries its syllable, said this short',
                  'sound usyl %s' % ' '.join('%s=%d' % (k, int(x['v'])) for k, x in sorted(syl.items())),
                  'syllabic usyl']
    os.makedirs(os.path.join(ROOT, 'ipa', 'realized'), exist_ok=True)
    path = os.path.join(ROOT, 'ipa', 'realized', template + '.map')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    if not quiet:
        print('%s: %d letters realised, %d targets not realised, %d carriers standing in unmoved' % (
            os.path.relpath(path, ROOT), n, unrealised, bare))


# The pitch marks typed in IPA (C2, C5). The front-end works in tenths of a Chao level; a voice's
# five levels span `range` tenths of a semitone (the accent line's key: 90 in the packs this is
# proved with), so a semitone is 40 / (range / 10) tenths of a level.
RANGE_ST = 9.0


def pitch_lines(t, range_st=RANGE_ST):
    per_st = 40.0 / range_st
    out = ['', '# pitch typed in IPA (C2, C5): tone letters and marks, register steps, slopes; tenths of a Chao',
           '# level, a semitone being %.2f of them (a range of %g semitones)' % (per_st, range_st)]
    for sid, e in sorted(t.sounds.items()):
        if e.get('kind') != 'tone' or len(e['codepoints']) != 1:
            continue
        spec = e.get('spec') or {}
        if e.get('levels'):
            out.append('tonemark %s %s    # %s' % (e['ipa'], ''.join(str(x) for x in e['levels']), sid))
        elif e.get('register'):
            st = (spec.get('step_st') or {}).get('v')
            if st is None:
                out.append('#   not realised: %s %s: no step in its specification' % (e['ipa'], sid))
            else:
                out.append('register %s %d    # %s, %g semitones' % (e['ipa'], int(round(st * per_st)), sid, st))
        elif e.get('slope'):
            st = (spec.get('st_per_syllable') or {}).get('v')
            if st is None:
                out.append('#   not realised: %s %s: no slope in its specification' % (e['ipa'], sid))
            else:
                out.append('slope %s %d    # %s, %g semitones a syllable' % (e['ipa'], int(round(st * per_st)), sid,
                                                                            st))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    t = T.load()
    if sys.argv[1] == '--write':
        for template in sys.argv[2:] or ['dedx']:
            write(t, template)
        return 0
    r = realize(t, sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'dedx')
    print(json.dumps(dict(r, line=sound_line('m1', r['keys'])), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
