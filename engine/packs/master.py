# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""The master path of the pack compiler (Phase 11; DESIGN.md 3.3, 11.3 M3; playbook R21).

A pack with `realization = "master"` is built like a legacy pack, except that every phoneme's
`sound` line comes from the IPA master table (ipa/table) through the engine adapter
(engine/ipa/adapter.py) and not from the old generator (engine/accent/sounds.py):

  1. each map line's IPA: an eSpeak NG phoneme's (`@table:name`) as the pack's [master.ipa] states it
     (eSpeak NG's own phoneme table, written there by to_master.py), a letter line's its own name;
  2. read with the master path's readings (READINGS below: eSpeak NG's spellings that are not IPA),
     then with the IPA reader (engine/ipa/reader.py) into base letters and their marks;
  3. each segment realised on the pack's template: adapter.compose (the base entry, its marks
     applied); a diphthong is its first vowel gliding to the last one's formants; an affricate is
     the template's own affricate where the table names one, else the stop and the fricative
     sharing the tie's length;
  4. a `sound` line for each part that differs from its carrier, named m1, m2, ..., with a comment
     naming the table entries and the provenance of their values.

Kept from the old lines, by rule (D96): the melody, the stress and the tones (accent, tone,
weaktones, whwords), the `says` lines, the directives, language.ini, the sample, and the pack's
[[override]] blocks, which apply on top as before. A line said as nothing (`-`) whose IPA holds no
sound (a mark or a boundary alone) stays so.

Never in silence: a phoneme whose IPA cannot be read or realised keeps its legacy line, marked
`legacy-fallback` with the reason (a fault); so does one the pack lists in [master.fallback] (a fault
check A found: silent, swapped, unrendered). Two phonemes of one table that eSpeak NG writes
differently and the table realises alike are kept apart: the later keeps its legacy line, marked
`kept-apart`, or, when that is the same too, the merge is reported as a problem. What the adapter
could not realise as specified is listed per line (`deviations`), never dropped.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.dirname(HERE)
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.join(ENGINE, 'ipa'))
import espeak_phonemes as EP  # noqa: E402
import adapter as A  # noqa: E402
import reader as R  # noqa: E402
import table as T  # noqa: E402

TIE = 'U+0361'
EJECTIVE = 'ʼ'
CREAKY = '̰'
# secondary articulations: on an affricate they colour the stop as well as the fricative
SECONDARY = {'U+02B7', 'U+02B2', 'U+02E0', 'U+02E4'}
STOPS = set('ptkcqʈɖbdɡgɟɢʔ')

# The readings of eSpeak NG's spellings that are not IPA, applied after espeak_phonemes.normalise
# (which already reads its mnemonic letters, `.` of a retroflex, `;` of palatalisation, ph th kh ch,
# the backquote of an ejective). Each is recorded on the line it changes and in the report.
READINGS = (
    ('rhotic', 'ɚ and ɝ are ə and ɜ with the rhotic hook ˞ (the IPA chart writes rhoticity as the mark; '
               'ɚ, ɝ are not chart letters)'),
    ('ng', 'nɡ is ŋ: eSpeak NG names the velar nasal `ng` and, where a table gives no IPA, writes the name '
           'letter by letter (cmn, yue, my)'),
    ('h', 'an h after a stop or an affricate is its aspiration ʰ: eSpeak NG\'s mnemonic h, as in ph th kh ch '
          '(cmn, hak, shn)'),
    ('breathy', 'ʰ after a voiced stop or affricate (eSpeak NG\'s Hindi bʰ dʰ ɡʰ, the voiced aspirates) is breathy '
                'voice: the table\'s ̤ (the IPA writes them bʱ or b̤; the table has no breathy-release mark ʱ yet)'),
    ('apical', 'i̪ is eSpeak NG\'s apical vowel of Mandarin after s ts tsʰ, a syllabic coronal approximant '
               '(kong2024: coronal constriction, lowered dorsum, retracted root): said as ɨ, the chart vowel nearest '
               'it, approximate'),
    ('prenasal', 'ᵐ ᵑ ⁿ are prenasalisation, the nasal half of a prenasalised stop: said as the nasal, extra short '
                 '(the table\'s ̆); eSpeak NG\'s Sinhala m# N# are these halves'),
    ('syllabic', 'a phoneme its table calls a vowel and writes as one nasal or lateral carries the syllable: the table\'s '
                 'syllabic mark ̩ (Cantonese ng)'),
    ('stod', '? before a vowel is eSpeak NG\'s mark of Danish stød, a laryngealization of the vowel '
             '(groennum2013): the vowel with creaky voice ̰'),
)
READING_TEXT = dict(READINGS)

# the superscript nasals of prenasalisation (eSpeak NG's Sinhala m# N#, which say the nasal half on its own):
# the nasal, extra short (the table's ̆)
PRENASAL = {'ᵐ': 'm̆', 'ᵑ': 'ŋ̆', 'ⁿ': 'n̆'}

_t = None
_memo = {}


class MasterError(Exception):
    """A phoneme the master path cannot realise (it then keeps its legacy line, with the reason)."""


def table():
    global _t
    if _t is None:
        _t = T.load()
    return _t


def read_ipa(ipa, is_vowel=None):
    """eSpeak NG's IPA for a phoneme -> (IPA text the reader is given, [readings applied])."""
    s = EP.normalise(ipa)
    used = []
    if any(c in s for c in PRENASAL):
        s = ''.join(PRENASAL.get(c, c) for c in s)
        used.append('prenasal')
    if 'ɚ' in s or 'ɝ' in s:
        s = s.replace('ɚ', 'ə˞').replace('ɝ', 'ɜ˞')
        used.append('rhotic')
    if 'nɡ' in s:
        s = s.replace('nɡ', 'ŋ')
        used.append('ng')
    if len(s) >= 2 and s.endswith('h') and s[-2] in STOPS | set('sʃɕʂzʒʑʐ') and is_vowel is not True:
        if s[-2] in STOPS or (len(s) >= 3 and s[-3] in STOPS):
            s = s[:-1] + 'ʰ'
            used.append('h')
    b = re.sub('([bdɡgɖɟɢ][zʒʐʑ]?)\u02b0', '\\1\u0324', s)
    if b != s:
        s = b
        used.append('breathy')
    if is_vowel is not False and 'i̪' in s:
        s = s.replace('i̪', 'ɨ')
        used.append('apical')
    if '?' in s:
        out = []
        for i, ch in enumerate(s):
            if ch == '?' and i + 1 < len(s) and s[i + 1] in EP.VOWELS:
                continue
            out.append(ch)
            if i > 0 and s[i - 1] == '?' and ch in EP.VOWELS:
                out.append(CREAKY)
        if ''.join(out) != s:
            s = ''.join(out)
            used.append('stod')
    return s, used


def _tags(d, out):
    """Count the provenance tags of every value under d."""
    if isinstance(d, dict):
        if 'tag' in d and ('v' in d or 'set' in d or 'add' in d or 'scale' in d or 'toward' in d):
            out[d['tag']] = out.get(d['tag'], 0) + 1
            return
        for v in d.values():
            _tags(v, out)
    elif isinstance(d, list):
        for v in d:
            _tags(v, out)


def provenance(sids):
    """{tag: count} over the values the entries bring: a base's specification and engine keys, a
    mark's transform."""
    t = table()
    out = {}
    for sid in sids:
        e = t.sounds[sid]
        _tags(e.get('spec') or {}, out)
        _tags(e.get('transform') or {}, out)
        ov = (e.get('realization') or {}).get('openevv') or {}
        _tags(ov.get('keys') or {}, out)
        _tags(ov.get('trim') or {}, out)
    return out


def _table_for(base, template):
    """The table, or, when the entry names a carrier this template has no measurement of (a dedx phone
    on esex), the table with that entry's choice left out: the nearest measured phone carries it."""
    k = ('t', base, template)
    if k not in _memo:
        t = table()
        e = t.sounds[base]
        own = ((e.get('realization') or {}).get('openevv') or {}).get('carrier')
        _memo[k] = (t, None)
        if own and not own.startswith('<') and own not in A.chassis(template):
            import copy
            e2 = copy.deepcopy(e)
            del e2['realization']['openevv']['carrier']
            t2 = T.Table(t.features, dict(t.sounds, **{base: e2}), t.sources, t.where)
            _memo[k] = (t2, 'the entry names the carrier %s, which %s has no measurement of: the nearest measured '
                            'phone carries it, with the entry\'s engine keys as they were set for %s' % (own, template, own))
    return _memo[k]


def _realize(base, template):
    k = ('r', base, template)
    if k not in _memo:
        _memo[k] = A.realize(_table_for(base, template)[0], base, template)
    return _memo[k]


def _compose(base, mods, template):
    k = ('c', base, tuple(mods), template)
    if k not in _memo:
        _memo[k] = A.compose(_table_for(base, template)[0], base, list(mods), template)
    return _memo[k]


def _hz(sid, template):
    k = ('h', sid, template)
    if k not in _memo:
        _memo[k] = A.realised_hz(_table_for(sid, template)[0], sid, template)
    return _memo[k]


ASPIRATED, PREASPIRATED, H = 'U+02B0', 'B:U+02B0#pre', 'U+0068'


def _breath(mod, base, template):
    """ʰ on a sound with no release to delay (a vowel, a fricative, a sonorant: eSpeak NG's `#'
    variants): the breath next to it, the table's h as long as the table's aspiration (or
    pre-aspiration), after it (or before it)."""
    t = table()
    r = _realize(H, template)
    tr = t.sounds[mod]['transform']['consonant']
    ms = tr['vot_ms']['add'] if mod == ASPIRATED else tr['release']['preaspiration_ms']['set']
    keys = dict(r['keys'], ms=int(round(ms)))
    return (r['carrier'], keys, [H, mod], ['%s on %s: no release for it to delay; said as breath %s it, the table\'s h '
                                           'for %d ms' % (t.sounds[mod]['ipa'], t.sounds[base]['ipa'],
                                                          'after' if mod == ASPIRATED else 'before', ms)])


def _part(base, mods, template):
    """One segment on its carrier: (phone, keys, sids, deviations)."""
    try:
        r = _realize(base, template)
        c = _compose(base, mods, template)
    except (ValueError, KeyError) as e:
        raise MasterError('%s on %s: %s' % (table().sounds[base]['ipa'], template, e))
    dev = list(r['unrealised']) + list(c['lost'])
    why = _table_for(base, template)[1]
    if why:
        dev.append(why)
    if r['distance'] and not c['keys']:
        dev.append('carrier %s stands in unmoved, %s feature steps from %s' % (
            r['carrier'], r['distance'], table().sounds[base]['ipa']))
    return c['carrier'], dict(c['keys']), [base] + list(mods), dev


def _parts(base, mods, template):
    """A segment as one part, or, where an aspiration mark has nothing to act on, with its breath."""
    asp = [m for m in mods if m in (ASPIRATED, PREASPIRATED)]
    if asp:
        rest = [m for m in mods if m not in asp]
        plain = _part(base, rest, template)
        if plain[1] == _part(base, mods, template)[1]:
            out = [plain]
            for m in asp:
                b = _breath(m, base, template)
                out = out + [b] if m == ASPIRATED else [b] + out
            return out
    return [_part(base, mods, template)]


def _seg_parts(seg, template):
    return seg['base'], [m for m in seg.get('mods') or []]


def _affricate(stop, fric, template):
    """Two segments of one consonant phoneme read as an affricate."""
    t = table()
    tie = t.sounds[TIE]
    sb, sm = _seg_parts(stop, template)
    fb, fm = _seg_parts(fric, template)
    pair = t.sounds[sb]['ipa'] + '͡' + t.sounds[fb]['ipa']
    phone = ((tie.get('realization') or {}).get('openevv', {}).get('tied') or {}).get(template, {}).get(pair)
    if not phone:
        # a template the tie names no phones for: the module's own affricate of these two letters,
        # if it has one and it was measured (esex C J, itix T D C J; dedx's are the tie's own list)
        tm = EP.TEMPLATES[A.BASE_OF.get(template, template)]
        own = [ph for ph, ipa in sorted(tm.consonants.items())
               if EP.normalise(ipa).replace('͡', '') == pair.replace('͡', '') and ph in A.chassis(template)]
        phone = own[0] if own else None
    if phone:
        # the template's own affricate: the marks of both sides composed on it; a time added (an
        # aspiration's onset) is added to the one the phone was measured with
        keys, dev = {}, []
        own = A.chassis(template).get(phone) or {}
        for m in sm + fm:
            ops, lost = A.mod_ops(t, m, 'consonant', template=template)
            dev += lost
            if ops is None:
                dev.append('%s has no transform for a consonant' % t.sounds[m]['ipa'])
                continue
            for k, op, _ in ops:
                if op == '+' and k not in keys and own.get(k) is not None:
                    keys[k] = own[k]
            keys, l2 = A.merge(keys, ops)
            dev += l2
        return [(phone, keys, [TIE, sb, fb] + sm + fm, dev + ['the template\'s affricate %s for %s' % (phone, pair)])]
    # the stop and the fricative, sharing the tie's length (each part scaled alike)
    sm = sm + [m for m in fm if m in SECONDARY and m not in sm]
    p1 = _part(sb, sm, template)
    tail = _parts(fb, fm, template)
    p2 = [p for p in tail if p[2][0] == fb][0]
    total = ((tie.get('spec') or {}).get('duration') or {}).get('inherent_ms', {}).get('v')
    ch = A.chassis(template)
    if total and not p1[0].startswith('<') and not p2[0].startswith('<'):
        ms = [ch[p[0]]['ms'] * p[1].get('hold', 100) / 100.0 for p in (p1, p2)]
        k = total / float(sum(ms))
        for p in (p1, p2):
            p[1]['hold'] = int(round(p[1].get('hold', 100) * k))
    return [(p1[0], p1[1], p1[2] + [TIE], p1[3])] + tail


def realize_ipa(ipa, is_vowel, template):
    """eSpeak NG's IPA of one phoneme -> dict(parts=[(phone, keys, sids, deviations)], text, readings,
    notes). Raises MasterError for what cannot be read or realised."""
    text, used = read_ipa(ipa, is_vowel)
    k = ('i', text, is_vowel, template)
    if k in _memo:
        res = dict(_memo[k])
        res['readings'] = used
        return res
    try:
        r = R.read(text, strict=False, t=table())
    except R.ReaderError as e:
        raise MasterError('IPA %r not readable: %s' % (text, e))
    notes = []
    segs = []
    for it in r['items']:
        if it['t'] == 'seg':
            segs.append(it)
        elif it['t'] == 'unknown':
            raise MasterError('IPA %r: %s' % (text, '; '.join(r['warnings']) or 'a character the table does not know'))
        else:
            notes.append('%s in the phoneme\'s IPA is not a sound: left out' % it['t'])
    notes += r['warnings']
    if not segs:
        res = dict(parts=[], text=text, notes=notes)
        _memo[k] = res
        return dict(res, readings=used)
    t = table()
    f0 = segs[0].get('features') or {}
    if (is_vowel and len(segs) == 1 and 'tied' not in segs[0] and f0.get('class') == 'consonant'
            and (f0.get('nasal') or f0.get('lateral')) and 'U+0329' not in (segs[0].get('mods') or [])):
        # a phoneme its table calls a vowel, written as one nasal or lateral (Cantonese ng): the consonant
        # carries the syllable, the table's syllabic mark ̩ (a glide eSpeak NG types as a vowel, Abkhaz ɥ, does not)
        res = realize_ipa(ipa_syllabic(text), is_vowel, template)
        return dict(res, readings=used + ['syllabic'])
    cls = [('T' if 'tied' in s else 'V' if s['features']['class'] == 'vowel' else 'C') for s in segs]
    parts = []
    if is_vowel and cls.count('V') >= 2 and all(c == 'V' for c in cls):
        # a diphthong: the first vowel gliding to the second's formants; a third vowel (a triphthong)
        # is a vowel of its own after it, gliding to a fourth if there is one
        for j in range(0, len(segs), 2):
            pair = segs[j:j + 2]
            b, m = _seg_parts(pair[0], template)
            if len(pair) == 2:
                # a mark on the second vowel (aʊ̃, aɪː) is the diphthong's: composed on the whole of it
                m = m + [x for x in pair[1].get('mods') or [] if x not in m]
            phone, keys, sids, dev = _part(b, m, template)
            if len(pair) == 2:
                last = pair[1]
                hz = _hz(last['base'], template)
                ch = A.chassis(template).get(phone)
                if hz and ch and not phone.startswith('<'):
                    for i in range(3):
                        keys['g%d' % (i + 1)] = int(round(100.0 * hz[i] / ch['f'][i]))
                    keys['glide'] = 1
                else:
                    dev.append('the glide to %s: no formants to glide to on %s' % (last['ipa'], template))
                sids = sids + [last['base']]
            parts.append((phone, keys, sids, dev))
    else:
        i = 0
        while i < len(segs):
            s = segs[i]
            if 'tied' in s:
                a, b = s['tied'][0], s['tied'][1]
                b = dict(b, mods=list(b.get('mods') or []) + list(s.get('mods') or []))
                parts += _affricate(a, b, template)
                i += 1
                continue
            nxt = segs[i + 1] if i + 1 < len(segs) else None
            if (is_vowel is False and nxt is not None and 'tied' not in nxt and not s.get('mods')
                    and (s['ipa'], nxt['ipa']) in EP.AFFRICATES):
                parts += _affricate(s, nxt, template)
                i += 2
                continue
            parts += _parts(s['base'], s.get('mods') or [], template)
            i += 1
    if len(parts) > 8:
        raise MasterError('%s needs %d phones; a phoneme may have 8 (EVV_MAX_PHONES)' % (text, len(parts)))
    res = dict(parts=parts, text=text, notes=notes)
    _memo[k] = res
    return dict(res, readings=used)


def ipa_syllabic(text):
    return text + '̩'


def kind_of(sids, parts):
    """table | composed | created, for R21f's counts: created if any entry used was made under the USP,
    composed if marks, a tie or a glide made it, else the table's own letter."""
    t = table()
    if any(t.sounds[s].get('state') == 'created' for s in sids):
        return 'created'
    if len(parts) > 1 or len(sids) > 1 or any(t.sounds[s].get('kind') != 'base' for s in sids):
        return 'composed'
    return 'table'


def _canon(text):
    """What a reading says, for telling two phonemes apart: its segments' bases and marks."""
    try:
        r = R.read(text, strict=False, t=table())
    except R.ReaderError:
        return text
    out = []
    for it in r['items']:
        if it['t'] == 'seg':
            for s in it.get('tied') or [it]:
                out.append((s.get('base'), tuple(sorted(s.get('mods') or []))))
            if it.get('tied'):
                out.append(('tie', tuple(sorted(it.get('mods') or []))))
    return tuple(out)


def _keys_text(keys):
    return ' '.join('%s=%s' % (k, keys[k]) for k in sorted(keys))


def realize(flat):
    """Rewrites flat['sounds'] for realization = "master" (a copy is returned) -> (flat, report)."""
    import copy
    flat = copy.deepcopy(flat)
    tag = flat['pack']['tag']
    template = flat['ini']['Language']['Template']
    master = flat.get('master') or {}
    ipas = master.get('ipa') or {}
    kinds = master.get('kind') or {}
    fallback = master.get('fallback') or {}
    lines = flat['sounds']['line']
    legacy_sounds = {x['id']: x for x in lines if x['kind'] == 'sound'}
    defs, users = {}, {}          # keys text -> id; id -> [(IPA, entries)] of every line that names it
    rows = []
    out = []

    def sound_id(keys, text, used):
        kt = _keys_text(keys)
        if kt not in defs:
            defs[kt] = 'm%d' % (len(defs) + 1)
            users[defs[kt]] = []
        u = (text, tuple(used))
        if u not in users[defs[kt]]:
            users[defs[kt]].append(u)
        return defs[kt]

    def note_of(sid):
        """Every table entry behind a shared line, and the provenance of all their values."""
        us = users[sid]
        names = ['%s: %s' % (text, '+'.join(used)) for text, used in us[:4]]
        if len(us) > 4:
            names.append('and %d more' % (len(us) - 4))
        prov = provenance(sorted(set(x for _, used in us for x in used)))
        return '%s; values %s' % ('; '.join(names), ', '.join('%s %d' % kv for kv in sorted(prov.items())) or 'none')

    def legacy(x, why, mark):
        rows.append(dict(key=x['name'], ipa=None, kind=mark, why=why, legacy=x['to'], to=x['to'], deviations=[]))
        return dict(x, note=('%s  [%s: %s]' % (x.get('note', ''), mark, why)).strip())

    at = None
    for x in lines:
        if x['kind'] == 'sound':
            if at is None:
                at = len(out)
            continue
        if x['kind'] != 'map':
            out.append(x)
            continue
        name = x['name']
        if name.startswith('@'):
            if name not in ipas:
                raise MasterError('pack %r: [master.ipa] has no IPA for %s (run to_master.py)' % (tag, name))
            ipa = ipas[name]
            is_vowel = {'v': True, 'c': False}.get(kinds.get(name))
        else:
            ipa, is_vowel = name, None
        if name in fallback:
            out.append(legacy(x, fallback[name], 'legacy-fallback'))
            continue
        if not ''.join(ch for ch in ipa if ch.isprintable()).strip() and x['to'].strip() in ('-', ''):
            rows.append(dict(key=name, ipa=ipa, kind='silent', why='eSpeak NG gives it no IPA (%r): no sound to '
                             'realise, said as nothing as before' % ipa, legacy=x['to'], to=x['to'], deviations=[]))
            out.append(x)
            continue
        try:
            res = realize_ipa(ipa, is_vowel, template)
        except MasterError as e:
            out.append(legacy(x, str(e), 'legacy-fallback'))
            continue
        if not res['parts']:
            if x['to'].strip() not in ('-', ''):
                out.append(legacy(x, 'IPA %r holds no sound to realise' % res['text'], 'legacy-fallback'))
            else:
                rows.append(dict(key=name, ipa=res['text'], kind='silent', why='no sound in %r (a mark or a boundary '
                                 'alone): said as nothing, as before' % res['text'], legacy=x['to'], to=x['to'],
                                 deviations=[]))
                out.append(x)
            continue
        said, sids, devs = [], [], []
        for phone, keys, used, dev in res['parts']:
            sids += [s for s in used if s not in sids]
            devs += dev
            if keys:
                said.append('%s=%s' % (phone, sound_id(keys, res['text'], used)))
            else:
                said.append(phone)
        to = ' '.join(said)
        devs += res['notes']
        kind = kind_of(sids, res['parts'])
        # eSpeak NG's own statement: its IPA, and a nasal or lateral its table calls a vowel is syllabic
        raw = EP.normalise(ipa) + ('̩' if 'syllabic' in res['readings'] else '')
        rows.append(dict(key=name, ipa=res['text'], raw=raw, kind=kind, readings=res['readings'],
                         legacy=x['to'], to=to,
                         sids=sids, deviations=devs, parts=[(p, k) for p, k, _, _ in res['parts']]))
        note = x.get('note', '')
        if res['readings']:
            note = ('%s  [read: %s]' % (note, ', '.join(res['readings']))).strip()
        out.append(dict(x, to=to, note=note))
    # two phonemes of one table that eSpeak NG writes differently must not come out alike: told apart by
    # eSpeak NG's own IPA, before the readings (a reading may make two spellings one)
    problems = []
    by_to = {}
    for row in rows:
        if row['key'].startswith('@') and row['kind'] not in ('legacy-fallback', 'silent', 'kept-apart'):
            by_to.setdefault((row['key'][1:].split(':')[0], row['to']), []).append(row)
    for (tn, to), group in sorted(by_to.items()):
        seen = {}
        for row in sorted(group, key=lambda r: r['key']):
            c = _canon(row['raw'])
            if not seen or c in seen:
                seen.setdefault(c, row)
                continue
            first = next(iter(seen.values()))
            seen[c] = row
            if row['legacy'] != first['legacy'] and row['legacy'] != to:
                why = 'kept apart from %s (%s): eSpeak NG writes %s and %s, which come out alike on %s' % (
                    first['key'], first['raw'], row['raw'], first['raw'], template)
                i = [j for j, y in enumerate(out) if y['kind'] == 'map' and y['name'] == row['key']][0]
                old = dict(out[i], to=row['legacy'], note=[y for y in lines if y['kind'] == 'map'
                                                           and y['name'] == row['key']][0].get('note', ''))
                out[i] = dict(old, note=('%s  [kept-apart: %s]' % (old['note'], why)).strip())
                row.update(kind='kept-apart', why=why, to=row['legacy'])
            else:
                problems.append('%s (%s) and %s (%s) come out alike (%s), in the legacy lines as well' % (
                    first['key'], first['ipa'], row['key'], row['ipa'], to))
    # the legacy sound lines a kept line still names
    keep = set()
    for y in out:
        if y['kind'] == 'map':
            for w in y['to'].split():
                if '=' in w and w.split('=', 1)[1] in legacy_sounds:
                    keep.add(w.split('=', 1)[1])
    snd = [legacy_sounds[i] for i in sorted(keep, key=lambda s: int(s[1:]) if s[1:].isdigit() else 0)]
    snd += [dict(kind='sound', id=i, keys={k: v for k, v in (w.split('=', 1) for w in kt.split())}, note=note_of(i))
            for kt, i in sorted(defs.items(), key=lambda kv: int(kv[1][1:]))]
    # the sound lines go where the legacy ones were, after a comment saying what they are
    head = [dict(kind='comment', key='master-c1', text='# realization master (engine/packs/master.py): each sound '
                 'from the IPA master table (ipa/table) through the'),
            dict(kind='comment', key='master-c2', text='# adapter, as it differs from the template\'s phone; its '
                 'comment names the table entries and the provenance of their values')]
    if at is None:
        at = len(out)
    flat['sounds']['line'] = out[:at] + head + snd + out[at:]
    counts = {}
    for row in rows:
        counts[row['kind']] = counts.get(row['kind'], 0) + 1
    report = dict(tag=tag, template=template, rows=rows, counts=counts, problems=problems, sounds=len(defs),
                  legacy_sounds_kept=len(keep))
    return flat, report

