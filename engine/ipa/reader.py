"""The IPA reader (DESIGN.md 2, capability C2). MIT licence.

IPA text in; out, in order, what it says: segments (a base letter with its marks and the feature
bundle they compose to, tied pairs kept together), stress marks, tones (a diacritic on its segment,
or tone letters read as one contour), register steps, phrase slopes, and boundaries (syllable,
linked, minor and major group, word). What it knows comes from the master table (ipa/table), so a
symbol added there is read without a change here.

    python engine/ipa/reader.py "ˈt͡sʰa˧˥ ŋ̊ɐ̃ː"      the reading, as JSON
    python engine/ipa/reader.py --test                  the C2 tests (DESIGN.md 4.3)

Nothing is lost without a word. In strict mode (the default) a character the table does not know,
or a mark that means nothing on its base (a rhotic hook on a consonant), raises ReaderError naming
it; otherwise it is kept in the reading as an `unknown` or `ignored` item with the reason, and
listed in `warnings`. Loose typing (`:` for ː, `'` for ˈ, ...) is read only when strict is off.
"""

import json
import os
import random
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import table as T  # noqa: E402

# Equal spellings, always: canonically equal input reads the same. NFD would take ç apart into c
# and a cedilla, which no chart symbol is, so it is put back; `g` is the chart's ɡ.
ALWAYS = {'g': 'ɡ'}
# Loose typing, off in strict mode.
LOOSE = {':': 'ː', "'": 'ˈ', ',': 'ˌ', '!': 'ǃ', '||': '‖', 'ɫ': 'l̴'}

# the order marks are composed in, whatever order they were typed in (DESIGN.md 2.2)
ORDER = {'place': 0, 'place_shift': 0, 'tongue_part': 0, 'stricture_shift': 1, 'quality_shift': 2,
         'rounding_shift': 2, 'rhotic': 2, 'tongue_root': 2, 'secondary': 3, 'airstream': 4, 'voicing': 5,
         'aspiration': 5, 'nasalized': 6, 'release': 6, 'length': 7, 'syllabic': 7}


class ReaderError(ValueError):
    pass


_table = None


def table():
    global _table
    if _table is None:
        _table = T.load()
    return _table


def normalize(text, strict=True):
    s = unicodedata.normalize('NFD', text).replace('ç', 'ç')
    for a, b in ALWAYS.items():
        s = s.replace(a, b)
    if not strict:
        for a, b in sorted(LOOSE.items(), key=lambda kv: -len(kv[0])):
            s = s.replace(a, b)
        s = unicodedata.normalize('NFD', s)
    return s


def _index(t):
    """symbol -> entry id, longest symbols first (tone-letter sequences are read letter by letter)."""
    out = {}
    for sid, e in t.sounds.items():
        if e['kind'] == 'tone' and len(e['ipa']) > 1:
            continue
        out[e['ipa']] = sid
    return out


def compose(t, base_features, mods, warn):
    """The base's bundle with each mark's edit for its class, in the fixed order."""
    f = T.full_bundle(t, base_features)
    cls = f['class']
    edits = []
    for mid in mods:
        e = t.sounds[mid]
        if e['kind'] != 'modifier':
            continue
        ed = (e.get('edit') or {}).get(cls)
        if ed is None:
            warn(mid, '%s (%s) means nothing on a %s; left off' % (e['ipa'], e['name'][:40], cls))
            continue
        for k, v in ed.items():
            edits.append((ORDER.get(k, 9), k, v, mid))
    done = {}
    for _, k, v, mid in sorted(edits, key=lambda x: x[0]):
        if isinstance(v, str) and v[:1] in '+-' and isinstance(f.get(k), list):
            lst = list(f[k])
            if v[0] == '+' and v[1:] not in lst:
                lst.append(v[1:])
            elif v[0] == '-' and v[1:] in lst:
                lst.remove(v[1:])
            f[k] = sorted(lst)
            continue
        if k in done and done[k][1] != v:
            warn(mid, '%s sets %s again (%s, then %s): the later in the fixed order wins' % (
                t.sounds[mid]['ipa'], k, done[k][1], v))
        f[k] = v
        done[k] = (mid, v)
    return f


def read(text, strict=True, t=None):
    """The reading: {'items': [...], 'warnings': [...], 'text': the normalized text}."""
    t = t or table()
    idx = _index(t)
    s = normalize(text, strict)
    items, warnings = [], []
    i = 0
    tie_next = None

    def fail(msg, at):
        if strict:
            raise ReaderError('%s (at %d in %r)' % (msg, at, s))
        warnings.append(msg)

    def last_segment():
        for it in reversed(items):
            if it['t'] == 'seg':
                return it
            if it['t'] not in ('tone',):
                return None
        return None

    while i < len(s):
        ch = s[i]
        if ch in ' \t\n':
            j = i
            while j < len(s) and s[j] in ' \t\n':
                j += 1
            if items and items[-1]['t'] == 'boundary' and items[-1]['value'] == 'word':
                items[-1]['src'][1] = j
            else:
                items.append(dict(t='boundary', value='word', src=[i, j]))
            i = j
            continue
        sid = idx.get(ch)
        if sid is None:
            cp = 'U+%04X' % ord(ch)
            fail('%s %s is not in the table (%s)' % (cp, ch, unicodedata.name(ch, 'no name')), i)
            items.append(dict(t='unknown', cp=cp, char=ch, src=[i, i + 1]))
            i += 1
            continue
        e = t.sounds[sid]
        kind = e['kind']
        if kind == 'base':
            seg = dict(t='seg', base=sid, ipa=ch, mods=[], src=[i, i + 1])
            if tie_next is not None:
                first = items.pop(tie_next)
                items.append(dict(t='seg', tied=[first, seg], tie=first.pop('tie_mark'), src=[first['src'][0], i + 1]))
                tie_next = None
            else:
                items.append(seg)
            i += 1
            continue
        target = last_segment()
        if target is not None and 'tied' in target:
            target = target['tied'][1]
        if kind == 'tie':
            if target is None or i + 1 >= len(s) or idx.get(s[i + 1]) is None or t.sounds[idx[s[i + 1]]]['kind'] != 'base':
                fail('the tie bar %s joins nothing' % e['ipa'], i)
                items.append(dict(t='ignored', id=sid, why='a tie bar with no letter on one side', src=[i, i + 1]))
            else:
                target['tie_mark'] = sid
                tie_next = len(items) - 1 if items[-1] is target else items.index(target)
                target['src'][1] = i + 1
            i += 1
            continue
        if kind == 'modifier' or (kind == 'tone' and e.get('placement') == 'over'):
            if target is None:
                fail('%s (%s) has no letter to mark' % (e['ipa'], sid), i)
                items.append(dict(t='ignored', id=sid, why='a mark with no letter before it', src=[i, i + 1]))
            elif kind == 'tone':
                target.setdefault('tone_ids', []).append(sid)
                target['tone'] = list(e['levels'])
                target['src'][1] = i + 1
            else:
                target['mods'].append(sid)
                target['src'][1] = i + 1
            i += 1
            continue
        if kind == 'tone' and e.get('levels'):
            # tone letters: as many as follow one another are one contour
            levels, ids, j = [], [], i
            while j < len(s) and idx.get(s[j]) and t.sounds[idx[s[j]]]['kind'] == 'tone' \
                    and t.sounds[idx[s[j]]].get('levels') and t.sounds[idx[s[j]]].get('placement') != 'over':
                ids.append(idx[s[j]])
                levels += t.sounds[idx[s[j]]]['levels']
                j += 1
            whole = '+'.join(ids)
            items.append(dict(t='tone', levels=levels, ids=ids, entry=whole if whole in t.sounds else None,
                              src=[i, j]))
            i = j
            continue
        if kind == 'tone':
            what = 'register' if e.get('register') else 'slope'
            items.append(dict(t=what, value=e.get(what), id=sid, src=[i, i + 1]))
        elif kind == 'syllable-mark':
            items.append(dict(t='stress', value=e['stress'], id=sid, src=[i, i + 1]))
        elif kind == 'boundary':
            items.append(dict(t='boundary', value=e['boundary'], id=sid, src=[i, i + 1]))
        i += 1
    if tie_next is not None:
        fail('a tie bar at the end joins nothing', len(s))
    # each segment's bundle, now that all its marks are known; a tied pair spans both letters
    # and every mark on them
    for it in items:
        if it['t'] == 'seg' and 'tied' in it:
            it['src'] = [it['tied'][0]['src'][0], max(x['src'][1] for x in it['tied'])]
        for seg in (it['tied'] if 'tied' in it else [it]) if it['t'] == 'seg' else []:
            def warn(mid, msg, seg=seg):
                fail(msg, seg['src'][0])
                seg.setdefault('ignored', []).append(mid)
            seg['features'] = compose(t, t.sounds[seg['base']]['features'], seg['mods'], warn)
    return dict(text=s, items=items, warnings=warnings)


# ---- the C2 tests -------------------------------------------------------------------------------

def _expect(t, base_sid, mod_sids):
    """What a base and marks must read to, worked out apart from the reader: each edit applied."""
    f = T.full_bundle(t, t.sounds[base_sid]['features'])
    for m in sorted(mod_sids, key=lambda m: min([ORDER.get(k, 9) for k in
                                                   (t.sounds[m].get('edit') or {}).get(f['class'], {})] or [9])):
        for k, v in ((t.sounds[m].get('edit') or {}).get(f['class']) or {}).items():
            if isinstance(v, str) and v[:1] == '+':
                f[k] = sorted(set(f[k]) | {v[1:]})
            else:
                f[k] = v
    return f


def _segments(r):
    out = []
    for it in r['items']:
        if it['t'] == 'seg':
            out += it['tied'] if 'tied' in it else [it]
    return out


def test(n_random=20000, seed=1):
    t = table()
    ipa = t.by_ipa()
    fails = []

    def check(ok, what):
        if not ok:
            fails.append(what)

    # 1. every one of the 175 entries is read to the bundle the table (from the checklist) gives
    read_ok = 0
    for sid, e in sorted(t.sounds.items()):
        kind, before = e['kind'], len(fails)
        if kind == 'base':
            r = read(e['ipa'], t=t)
            segs = _segments(r)
            check(len(segs) == 1 and segs[0]['features'] == T.full_bundle(t, e['features']),
                  '%s %s read as %s' % (sid, e['ipa'], [s.get('features') for s in segs]))
        elif kind == 'modifier':
            cls = 'vowel' if 'vowel' in e['edit'] and 'consonant' not in e['edit'] else 'consonant'
            base = ipa['ə'] if cls == 'vowel' else ipa['t' if sid != 'U+02BC' else 'p']
            if sid in ('U+0303', 'U+02DE', 'U+0339', 'U+031C', 'U+0308', 'U+033D'):
                base = ipa['ɔ'] if sid in ('U+0339', 'U+031C') else ipa['e']
            r = read(t.sounds[base]['ipa'] + e['ipa'], t=t)
            segs = _segments(r)
            check(len(segs) == 1 and segs[0]['features'] == _expect(t, base, [sid]),
                  '%s on %s read as %s' % (sid, t.sounds[base]['ipa'], segs and segs[0].get('features')))
        elif kind == 'tie':
            r = read('t' + e['ipa'] + 's', t=t)
            check(len(r['items']) == 1 and len(r['items'][0].get('tied', [])) == 2, '%s did not tie t and s' % sid)
        elif kind == 'syllable-mark':
            r = read(e['ipa'] + 'ta', t=t)
            check(r['items'][0] == dict(t='stress', value=e['stress'], id=sid, src=[0, 1]), '%s: %s' % (sid, r['items'][:1]))
        elif kind == 'boundary':
            r = read('ta' + e['ipa'] + 'ta', t=t)
            check(any(it['t'] == 'boundary' and it['value'] == e['boundary'] for it in r['items']), sid)
        elif kind == 'tone' and e.get('placement') == 'over':
            r = read('a' + e['ipa'], t=t)
            check(_segments(r)[0].get('tone') == e['levels'], '%s on a read as %s' % (sid, _segments(r)[0].get('tone')))
        elif kind == 'tone' and e.get('levels'):
            r = read('ma' + e['ipa'], t=t)
            tones = [it for it in r['items'] if it['t'] == 'tone']
            check(len(tones) == 1 and tones[0]['levels'] == e['levels'], '%s read as %s' % (sid, tones))
            if len(e['codepoints']) > 1:
                check(tones and tones[0]['entry'] == sid, '%s: the contour is not its own entry' % sid)
        elif kind == 'tone':
            what = 'register' if e.get('register') else 'slope'
            r = read(e['ipa'] + 'ma', t=t)
            check(r['items'][0]['t'] == what and r['items'][0]['value'] == e.get(what), sid)
        read_ok += len(fails) == before
    # equal marks give equal bundles; the chart's equivalent pairs are read alike
    for sid, e in t.sounds.items():
        other = e.get('equivalent_to')
        if not other or e['kind'] != 'modifier':
            continue
        a, b = read('n' + e['ipa'], t=t), read('n' + t.sounds[other]['ipa'], t=t)
        check(_segments(a)[0]['features'] == _segments(b)[0]['features'], '%s and %s read differently' % (sid, other))

    # 2. canonically equal input reads the same
    samples = ['ç', 'çʰ', 'é', 'ẽ', 'ȅ', 'ɑ̃ː', 'ŋ̊', 'ǹ', 'ŝ', 'ā˥', 'ˈt͡sʰa˧˥ ŋ̊ɐ̃ː', 'ɡ', 'ɛ̃̀', 'ü', 'ö̤']
    canon = 0
    for x in samples:
        # canonical equivalence only: NFKC would make ʰ a plain h, which is another symbol
        forms = {unicodedata.normalize(f, x) for f in ('NFC', 'NFD')} | {x.replace('ɡ', 'g')}
        readings = set()
        for y in forms:
            try:
                readings.add(json.dumps(read(y, strict=False, t=t)['items'], sort_keys=True, ensure_ascii=False))
            except ReaderError as err:
                readings.add('error ' + str(err))
        check(len(readings) == 1, '%r: %d different readings of its equal forms' % (x, len(readings)))
        canon += len(readings) == 1

    # 3. random input never crashes and never drops a character without a word
    rnd = random.Random(seed)
    alphabet = [e['ipa'] for e in t.sounds.values()] + list("abc :'!|.‿ ") + \
        [chr(rnd.randrange(0x20, 0x3000)) for _ in range(200)]
    crashes = silent = 0
    for _ in range(n_random):
        x = ''.join(rnd.choice(alphabet) for _ in range(rnd.randrange(1, 12)))
        try:
            r = read(x, strict=False, t=t)
        except Exception as err:  # noqa: BLE001 - any crash is the finding
            crashes += 1
            if crashes <= 3:
                fails.append('crash on %r: %r' % (x, err))
            continue
        covered = [False] * len(r['text'])
        for it in r['items']:
            for k in range(*it['src']):
                covered[k] = True
        if not all(covered):
            silent += 1
            if silent <= 3:
                fails.append('characters of %r not accounted for: %s' % (
                    x, [r['text'][k] for k, c in enumerate(covered) if not c]))
        try:
            read(x, strict=True, t=t)
        except ReaderError:
            pass
        except Exception as err:  # noqa: BLE001
            crashes += 1
            fails.append('strict crash on %r: %r' % (x, err))
    print('reader: %d of %d entries read to their bundle; %d of %d equal spellings read alike; '
          '%d random inputs: %d crashes, %d with a character unaccounted for' % (
              read_ok, len(t.sounds), canon, len(samples), n_random, crashes, silent))
    for f in fails[:20]:
        print('  FAIL ' + f)
    return 1 if fails else 0


def main():
    if '--test' in sys.argv:
        return test()
    strict = '--loose' not in sys.argv
    text = ' '.join(a for a in sys.argv[1:] if not a.startswith('--'))
    try:
        r = read(text, strict=strict)
    except ReaderError as err:
        print('refused: %s' % err)
        return 1
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
