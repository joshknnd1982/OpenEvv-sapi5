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
import re
import sys
import itertools
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import table as T  # noqa: E402

def _aliases():
    """ipa/aliases.toml: equal spellings (always) and loose typing (only when not strict)."""
    import tomli
    with open(os.path.join(T.IPA, 'aliases.toml'), 'rb') as f:
        d = tomli.load(f)
    return d.get('always', {}), d.get('loose', {})


ALWAYS, LOOSE = _aliases()

# the order marks are composed in, whatever order they were typed in (DESIGN.md 2.2)
ORDER = {'place': 0, 'place_shift': 0, 'tongue_part': 0, 'stricture_shift': 1, 'quality_shift': 2,
         'rounding_shift': 2, 'rhotic': 2, 'tongue_root': 2, 'secondary': 3, 'airstream': 4, 'voicing': 5,
         'aspiration': 5, 'voicing_part': 5, 'nasalized': 6, 'release': 6, 'length': 7, 'syllabic': 7}


class ReaderError(ValueError):
    pass


_table = None


def table():
    global _table
    if _table is None:
        _table = T.load()
    return _table


# combining marks of Unicode 14 (extIPA's partial voicing ◌᫃ ◌᫄ among them) with their canonical
# class (UnicodeData.txt, 18.0.0): Python 3.10's tables (13.0) and Windows' NormalizeString know
# none of them and leave them where they stand, so canonically equal text would read differently
# (D77). The front-end has the same list (frontend_main.c ipa_normalize).
LATE_CCC = {0x1AC1: 230, 0x1AC2: 230, 0x1AC3: 220, 0x1AC4: 220, 0x1AC5: 230, 0x1AC6: 230, 0x1AC7: 230,
            0x1AC8: 230, 0x1AC9: 230, 0x1ACA: 220, 0x1ACB: 230, 0x1ACC: 230, 0x1ACD: 230, 0x1ACE: 230}


def canonical_order(s):
    """Canonical ordering (Unicode 3.11) with LATE_CCC added: each run of marks sorted, stably, by
    class."""
    ccc = [LATE_CCC.get(ord(c)) or unicodedata.combining(c) for c in s]
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and ccc[j]:
            j += 1
        if j > i:
            out += [c for _, c in sorted(zip(ccc[i:j], s[i:j]), key=lambda x: x[0])]
            i = j
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def _cedilla(s):
    """c and a cedilla put back together as the chart letter ç, wherever the cedilla stands among
    c's marks (canonical order puts an overlay, class 1, before it), as the front-end does
    (frontend_main.c ipa_normalize; D77)."""
    import re
    return re.sub('c([\u0300-\u036f]*?)\u0327', '\u00e7\\1', s)


def normalize(text, strict=True):
    s = _cedilla(canonical_order(unicodedata.normalize('NFD', text))).replace('ç', 'ç')
    for a, b in ALWAYS.items():
        s = s.replace(a, b)
    if not strict:
        for a, b in sorted(LOOSE.items(), key=lambda kv: -len(kv[0])):
            s = s.replace(a, b)
        # (and ç put back together again: the second decomposition splits it, D77)
        s = _cedilla(canonical_order(unicodedata.normalize('NFD', s)))
    return s


def _index(t, notation='ipa'):
    """symbol -> entry id, longest symbols first (tone-letter sequences are read letter by letter).
    An entry of extIPA's own reading of a character the IPA reads otherwise (`notation', Q18) is
    known only in text that declares extIPA."""
    out = {}
    for sid, e in t.sounds.items():
        if (e['kind'] == 'tone' and len(e['ipa']) > 1) or e['kind'] in ('composite', 'label', 'pause') or (
                e['kind'] == 'modifier' and e.get('placement') == 'before') or (
                e.get('notation') and e['notation'] != notation):
            continue
        out[e['ipa']] = sid
    return out


def _label_index(t):
    """label spelling -> entry id (D83): every label of its own, by its spelling and its others."""
    out = {}
    for sid, e in t.sounds.items():
        ov = (e.get('realization') or {}).get('openevv', {})
        if e['kind'] == 'label' and ov.get('label') and not e.get('parts'):
            for sp in [ov['label']] + list(ov.get('spellings') or []):
                # as the text is read: allegro's g is ɡ; and loosely, where ! is read as the click ǃ
                out[normalize(sp)] = sid
                out.setdefault(normalize(sp, strict=False), sid)
    return out


def _pause_index(t):
    """pause spelling -> (entry id, ms) (D83), and the id of the timed pause."""
    out, timed = {}, None
    for sid, e in t.sounds.items():
        ov = (e.get('realization') or {}).get('openevv', {})
        if e['kind'] == 'pause':
            for sp in ov.get('pause') or []:
                out[sp] = (sid, e['spec']['pause_ms']['v'])
            if ov.get('timed'):
                timed = sid
    return out, timed


def read_labels(tok, lidx):
    """[(label id, degree)] for a label as written (VoQS's {L̞1V! ...}: L̞, and V! at degree 1),
    the longest spelling first; a degree goes on the symbol written after it, a base label and
    the marks after it (a label that is a mark, `#label', keeps its base's degree), 2 where none
    is written, as the front-end reads it; None if any of it is no label."""
    out, i, pending, cur = [], 0, 0, 2
    while i < len(tok):
        if tok[i] in '123' and i + 1 < len(tok):
            pending = int(tok[i])
            i += 1
            continue
        k = next((k for k in range(len(tok), i, -1) if tok[i:k] in lidx), None)
        if k is None:
            return None
        if not lidx[tok[i:k]].endswith('#label') or pending:
            cur = pending or 2
        pending = 0
        out.append((lidx[tok[i:k]], cur))
        i = k
    return out or None


def _group(t, sid):
    return ((t.sounds[sid].get('realization') or {}).get('openevv', {})).get('group')


def span_labels(t, spans):
    """The labels a letter in these stretches is said with, outermost first: a label of a group
    (extIPA's loudness, its tempo) gives way to one of its group in a stretch inside it."""
    out = []
    for k, (_, ls) in enumerate(spans):
        inner = {_group(t, x) for _, ls2 in spans[k + 1:] for x, _ in ls2} - {None}
        out += [(x, d) for x, d in ls if _group(t, x) not in inner]
    return out


TIMED = re.compile(r'\((\d+(?:\.\d+)?) ?(?:sec|s)?\)')


def _pre_index(t):
    """mark -> entry id, for the marks written before their letter (extIPA's ʰp, ˬz: Tier B)."""
    return {e['ipa']: sid for sid, e in t.sounds.items() if e['kind'] == 'modifier' and e.get('placement') == 'before'}


def compose(t, base_features, mods, warn):
    """The base's bundle with each mark's edit for its class, in the fixed order."""
    f = T.full_bundle(t, base_features)
    cls = f['class']
    edits = []
    for mid in mods:
        e = t.sounds[mid]
        if e['kind'] != 'modifier' and not (e['kind'] == 'tie' and e.get('edit')):
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


def read(text, strict=True, t=None, notation='ipa'):
    """The reading: {'items': [...], 'warnings': [...], 'text': the normalized text}. `notation':
    'extipa' for text that declares extIPA (its ↓ is ingressive airflow, Q18), as a map's
    `notation extipa' line tells the front-end."""
    t = t or table()
    idx = _index(t, notation)
    pre_idx = _pre_index(t)
    pre = []                # marks read before the letter they belong to
    s = normalize(text, strict)
    # a Tier B letter that stands for a Tier A spelling (ꞯ for q̠, D68) is read as that spelling;
    # every other Tier B composite is its own parts already
    # (the longest first: ʩ̬ stands for ŋ͌, ʩ for ŋ̊͌, D77)
    for e in sorted(t.sounds.values(), key=lambda e: -len(e['ipa'])):
        if e['kind'] == 'composite' and e.get('said_as'):
            s = s.replace(e['ipa'], e['said_as'])
    items, warnings = [], []
    i = 0
    tie_next = None
    lidx = _label_index(t)
    pidx, timed_id = _pause_index(t)
    spans = []              # the stretches open: (what closes it, [(label id, degree)])

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
        # braces, a stretch's labels, and pauses (D83), as the front-end reads them
        if spans and spans[-1][0] == '}' and (i == 0 or s[i - 1] in ' \t\n'):
            # the same labels written again just before the closing brace, in any order
            j = i
            while j < len(s) and s[j] not in ' \t\n}':
                j += 1
            k = j
            while k < len(s) and s[k] in ' \t\n':
                k += 1
            if j > i and s.startswith('}', k) and sorted(read_labels(s[i:j], lidx) or []) == sorted(spans[-1][1]):
                items.append(dict(t='label', again=s[i:j], src=[i, k]))
                i = k
                continue
        if ch == '{':
            j = i + 1
            while j < len(s) and s[j] in ' \t\n':
                j += 1
            k = j
            while k < len(s) and s[k] not in ' \t\n}':
                k += 1
            labels = read_labels(s[j:k], lidx)
            if labels is None:
                fail('the label %r is no label the table lists' % s[j:k], i)
                labels = []
            spans.append(('}', labels))
            items.append(dict(t='label', open=labels, src=[i, k]))
            i = k
            continue
        if ch in '})\u2e29':
            if spans and spans[-1][0] == ch:
                spans.pop()
                items.append(dict(t='label', close=ch, src=[i, i + 1]))
            else:
                fail('%s closes no stretch' % ch, i)
                items.append(dict(t='ignored', char=ch, why='closes no stretch', src=[i, i + 1]))
            i += 1
            continue
        if ch == '(':
            e_ = s.find(')', i)
            m_ = TIMED.match(s, i)
            if e_ > 0 and s[i:e_ + 1] in pidx:
                items.append(dict(t='pause', id=pidx[s[i:e_ + 1]][0], ms=pidx[s[i:e_ + 1]][1], src=[i, e_ + 1]))
                i = e_ + 1
                continue
            if m_ and timed_id and float(m_.group(1)) <= 60:
                items.append(dict(t='pause', id=timed_id, ms=float(m_.group(1)) * 1000.0, src=[i, m_.end()]))
                i = m_.end()
                continue
            # extIPA's silent articulation: a stretch under the label `()', which the table may lack
            spans.append((')', [(lidx['()'], 2)] if '()' in lidx else []))
            items.append(dict(t='label', open=spans[-1][1], src=[i, i + 1]))
            i += 1
            continue
        if ch == '\u2e28':
            spans.append(('\u2e29', [(lidx['\u2e28\u2e29'], 2)] if '\u2e28\u2e29' in lidx else []))
            items.append(dict(t='label', open=spans[-1][1], src=[i, i + 1]))
            i += 1
            continue
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
        sid, n = idx.get(ch), 1

        def makes_letter(k):
            # the mark at k makes a letter of two with ch, unless it begins a mark of two
            # characters (𝼀̬᪽ is 𝼀 with ◌̬᪽, not 𝼀̬ with ᪽), as in the front-end (D77)
            return ch + s[k] in idx and t.sounds[idx[ch + s[k]]]['kind'] == 'base' and not (
                k + 1 < len(s) and s[k:k + 2] in idx and t.sounds[idx[s[k:k + 2]]]['kind'] == 'modifier')
        if sid is not None and t.sounds[sid]['kind'] == 'base':
            # a letter of three characters, a letter and two marks its own entry reads otherwise
            # (extIPA's bidental fricatives h̪͆ ɦ̪͆, D79): the two marks, in their order, wherever
            # they stand among the letter's marks, are moved next to it, as the front-end finds them
            run3 = []
            k3 = i + 1
            # (extIPA's marks of Unicode 14, ◌᫃ ◌᫄, are combining too: Python 3.10 does not know them)
            while k3 < len(s) and (unicodedata.combining(s[k3]) or ord(s[k3]) in LATE_CCC or (
                    s[k3] in idx and t.sounds[idx[s[k3]]]['kind'] == 'modifier')):
                run3.append(k3)
                k3 += 1

            def begins_two(k):
                # a mark that begins a mark of two characters makes no letter (as in the front-end)
                return k + 1 < len(s) and s[k:k + 2] in idx and t.sounds[idx[s[k:k + 2]]]['kind'] == 'modifier'
            # (and of four, a letter and three marks: extIPA's bidental aspiration tʰ̪͆, D80; the most
            # marks first, the earliest first, every one of them beginning no mark of two)
            free = [k for k in run3 if not begins_two(k)]
            found3 = next((c for w in (3, 2) for c in itertools.combinations(free, w)
                           if ch + ''.join(s[k] for k in c) in idx
                           and t.sounds[idx[ch + ''.join(s[k] for k in c)]]['kind'] == 'base'), None)
            if found3:
                rest = ''.join(s[k] for k in run3 if k not in found3)
                s = s[:i + 1] + ''.join(s[k] for k in found3) + rest + s[k3:]
        # a letter of four or three characters (the above; or a tied letter, extIPA's buccal trill
        # ↀ͡r: a character, a tie bar and a letter, D80)
        for w in (4, 3):
            if n == 1 and i + w - 1 < len(s) and s[i:i + w] in idx and t.sounds[idx[s[i:i + w]]]['kind'] == 'base'                     and not (i + w < len(s) and s[i + w - 1:i + w + 1] in idx
                             and t.sounds[idx[s[i + w - 1:i + w + 1]]]['kind'] == 'modifier'):
                sid, n = idx[s[i:i + w]], w
        if sid is not None and n == 1 and t.sounds[sid]['kind'] == 'base':
            # a letter of two characters whose mark canonical order has put behind another mark
            # (ɹ̩̈ comes as ɹ, ̩, ̈: a mark below before one above): the mark is moved next to its
            # letter, as the front-end finds it wherever it stands among the letter's marks (D74)
            # the first mark that makes a letter is the letter's, as in the front-end: ɹ̺̈ is ɹ̺
            # with ̈ on it, not ɹ̈ with ̺ (D77)
            j = i + 1 if not (i + 1 < len(s) and makes_letter(i + 1)) else len(s)
            # (over the second character of a mark of two, ◌̥᪽, too: ɹ̥᪽̈ is ɹ̈ with ◌̥᪽, D77)
            while j < len(s) and any(x in idx and t.sounds[idx[x]]['kind'] == 'modifier'
                                     for x in (s[j], s[j - 1:j + 1])):
                if j > i + 1 and makes_letter(j):
                    s = s[:i + 1] + s[j] + s[i + 1:j] + s[j + 1:]
                    break
                j += 1
        if n == 1 and i + 1 < len(s) and s[i:i + 2] in idx and (t.sounds[idx[s[i:i + 2]]]['kind'] == 'modifier' or (
                t.sounds[idx[s[i:i + 2]]]['kind'] == 'base' and makes_letter(i + 1))):
            # a mark of two characters (extIPA's ◌̥᪽, ◌ʰʰ: Tier B) is one; so is a letter of two (a
            # letter and a mark that the letter's own entry reads otherwise: extIPA's ɹ̈ ɹ̺, D74)
            sid, n = idx[s[i:i + 2]], 2
        if n == 1 and ch in pre_idx:
            # a mark written before a letter: it is the letter's when the letter before it (if
            # any) has no meaning for it, and a letter follows (aʰpa: a pre-aspirated p), as in the
            # front-end (frontend_main.c translate_ipa)
            tg = last_segment()
            if tg is not None and 'tied' in tg:
                tg = tg['tied'][0]      # a tied pair: its first letter's class, as the front-end's
            cls = t.sounds[tg['base']]['features']['class'] if tg is not None and 'base' in tg else None
            j = i + 1
            while j < len(s) and s[j] in pre_idx and not (idx.get(s[j]) and t.sounds[idx[s[j]]]['kind'] == 'base'):
                j += 1
            nxt = idx.get(s[j]) if j < len(s) else None
            if nxt is None and s[j:j + 3] in idx and t.sounds[idx[s[j:j + 3]]]['kind'] == 'base':
                nxt = idx[s[j:j + 3]]      # a tied letter (ʰↀ͡r), as the front-end has it (D80)
            if (sid is None or tg is None or cls not in (t.sounds[sid].get('edit') or {})) \
                    and nxt is not None and t.sounds[nxt]['kind'] == 'base':
                pre.append((pre_idx[ch], i))
                i += 1
                continue
        if sid is None:
            cp = 'U+%04X' % ord(ch)
            fail('%s %s is not in the table (%s)' % (cp, ch, unicodedata.name(ch, 'no name')), i)
            items.append(dict(t='unknown', cp=cp, char=ch, src=[i, i + 1]))
            i += 1
            continue
        e = t.sounds[sid]
        kind = e['kind']
        if kind == 'base':
            seg = dict(t='seg', base=sid, ipa=s[i:i + n], mods=[m for m, _ in pre], src=[pre[0][1] if pre else i, i + n])
            if spans:
                # the labels of every stretch it is in (D83), outermost first
                seg['labels'] = span_labels(t, spans)
            pre = []
            if tie_next is not None:
                first = items.pop(tie_next)
                items.append(dict(t='seg', tied=[first, seg], tie=first.pop('tie_mark'), src=[first['src'][0], i + n]))
                tie_next = None
            else:
                items.append(seg)
            i += n
            continue
        target = last_segment()
        if target is not None and 'tied' in target:
            target = target['tied'][1]
        if kind == 'tie':
            # a tie joins two letters: one after a pair already tied joins nothing more (D69)
            if target is None or target not in items or i + 1 >= len(s) or idx.get(s[i + 1]) is None \
                    or t.sounds[idx[s[i + 1]]]['kind'] != 'base':
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
                items.append(dict(t='ignored', id=sid, why='a mark with no letter before it', src=[i, i + n]))
            elif kind == 'tone':
                target.setdefault('tone_ids', []).append(sid)
                target['tone'] = list(e['levels'])
                target['src'][1] = i + 1
            else:
                target['mods'].append(sid)
                target['src'][1] = i + n
            i += n
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
    if spans:
        fail('a stretch opened is not closed (%s)' % spans[-1][0], len(s))
    for m, at in pre:
        fail('%s (%s) has no letter after it' % (t.sounds[m]['ipa'], m), at)
        items.append(dict(t='ignored', id=m, why='a mark with no letter after it', src=[at, at + 1]))
    # each segment's bundle, now that all its marks are known; a tied pair spans both letters
    # and every mark on them
    for it in items:
        if it['t'] == 'seg' and 'tied' in it:
            it['src'] = [it['tied'][0]['src'][0], max(x['src'][1] for x in it['tied'])]
            if t.sounds[it['tie']].get('edit'):
                # a joining mark that is a mark of each side as well (extIPA's sliding
                # articulation, U+0362: the two in the time of one segment), as in the front-end
                for seg in it['tied']:
                    seg['mods'].append(it['tie'])
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
        elif kind == 'label' and ((e.get('realization') or {}).get('openevv', {}).get('label') or e.get('parts')):
            # a label (D83): each letter in its braces carries it, and the letters outside do not
            sp = ''.join(t.sounds[x]['realization']['openevv']['label'] for x in e['parts']) if e.get('parts') \
                else e['realization']['openevv']['label']
            r = read('pa {%s ˈpa %s} pa' % (sp, sp), t=t)
            segs = _segments(r)
            want = [(x, 2) for x in e.get('parts') or [sid]]
            got = [sg.get('labels') for sg in segs]
            check(got == [None, None, want, want, None, None], '%s {%s ...} read as %s' % (sid, sp, got))
        elif kind == 'pause' and (e.get('realization') or {}).get('openevv', {}).get('pause'):
            for sp in e['realization']['openevv']['pause']:
                r = read('pa %s pa' % sp, t=t)
                ps = [it for it in r['items'] if it['t'] == 'pause']
                check(len(ps) == 1 and ps[0]['ms'] == e['spec']['pause_ms']['v'], '%s %s read as %s' % (sid, sp, ps))
        elif kind == 'pause':
            r = read('pa (1.3 sec) pa (0.4) pa', t=t)
            check([it['ms'] for it in r['items'] if it['t'] == 'pause'] == [1300.0, 400.0], '%s timed' % sid)
        elif kind == 'modifier':
            cls = 'vowel' if 'vowel' in e['edit'] and 'consonant' not in e['edit'] else 'consonant'
            base = ipa['ə'] if cls == 'vowel' else ipa['t' if sid != 'U+02BC' else 'p']
            if sid in ('U+0303', 'U+02DE', 'U+0339', 'U+031C', 'U+0308', 'U+033D'):
                base = ipa['ɔ'] if sid in ('U+0339', 'U+031C') else ipa['e']
            r = read(e['ipa'] + t.sounds[base]['ipa'] if e.get('placement') == 'before'
                     else t.sounds[base]['ipa'] + e['ipa'], t=t, notation=e.get('notation', 'ipa'))
            segs = _segments(r)
            if e.get('notation'):
                # extIPA's own reading (Q18): strict IPA does not know it
                try:
                    read(t.sounds[base]['ipa'] + e['ipa'], t=t)
                    check(False, '%s read without its notation declared' % sid)
                except ReaderError:
                    pass
            check(len(segs) == 1 and segs[0]['features'] == _expect(t, base, [sid]),
                  '%s on %s read as %s' % (sid, t.sounds[base]['ipa'], segs and segs[0].get('features')))
        elif kind == 'tie':
            r = read('t' + e['ipa'] + 's', t=t)
            check(len(r['items']) == 1 and len(r['items'][0].get('tied', [])) == 2, '%s did not tie t and s' % sid)
            if e.get('edit'):
                # a joining mark that is a mark of each side (extIPA's sliding articulation)
                check(all(x['features'] == _expect(t, x['base'], [sid]) for x in r['items'][0].get('tied', [])),
                      '%s: the sides of t%ss do not carry it' % (sid, e['ipa']))
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
        elif kind == 'composite':
            # a Tier B spelling (D68) reads as its parts do
            r = read(e['ipa'], t=t)
            want = read(''.join(t.sounds[x]['ipa'] for x in e['parts']), t=t)
            check([s.get('features') for s in _segments(r)] == [s.get('features') for s in _segments(want)]
                  and _segments(r), '%s %s read as %s' % (sid, e['ipa'], [s.get('features') for s in _segments(r)]))
        elif kind == 'tone':
            what = 'register' if e.get('register') else 'slope'
            r = read(e['ipa'] + 'ma', t=t)
            check(r['items'][0]['t'] == what and r['items'][0]['value'] == e.get(what), sid)
        read_ok += len(fails) == before
    # the braces (D83): a degree goes on one symbol; a word spelt like a label is kept unless the
    # stretch's own labels are written again; an inner label of a group replaces the outer one; a
    # timed pause is 60 s at most
    lid = _label_index(t)
    if {'V', '!', 'L̞', 'f', 'p'} <= set(lid):
        segs = _segments(read('{1V!L̞ ˈpa 1V!L̞}', t=t))
        check(segs and segs[0].get('labels') == [(lid['V'], 1), (lid['!'], 1), (lid['L̞'], 2)],
              '{1V!L̞ ...} read as %s' % (segs and segs[0].get('labels')))
        segs = _segments(read('{V! ˈma p}', t=t))
        check([g['base'] for g in segs] == [ipa['m'], ipa['a'], ipa['p']], '{V! ˈma p}: the word p kept, read %s'
              % [g['base'] for g in segs])
        segs = _segments(read('{f ˈma {p ˈna p} ˈla f}', t=t))
        check([g.get('labels') for g in segs] == [[(lid['f'], 2)]] * 2 + [[(lid['p'], 2)]] * 2 + [[(lid['f'], 2)]] * 2,
              'nested f and p read as %s' % [g.get('labels') for g in segs])
    if _pause_index(t)[1]:
        r = read('pa (70 sec) pa', strict=False, t=t)
        check(not [it for it in r['items'] if it['t'] == 'pause'], '(70 sec) read as a pause')
    # equal marks give equal bundles; the chart's equivalent pairs are read alike
    for sid, e in t.sounds.items():
        other = e.get('equivalent_to')
        if not other or e['kind'] != 'modifier':
            continue
        a, b = read('n' + e['ipa'], t=t), read('n' + t.sounds[other]['ipa'], t=t)
        check(_segments(a)[0]['features'] == _segments(b)[0]['features'], '%s and %s read differently' % (sid, other))

    # a mark written before a letter goes to it only when the letter before has no meaning for it
    # (D70): aʰpa is a pre-aspirated p; tʰa and a tied t͡sʰa keep Tier A's aspiration
    pre_sid = next((s_ for s_, e in t.sounds.items() if e['kind'] == 'modifier' and e['ipa'] == 'ʰ'
                    and e.get('placement') == 'before'), None)
    if pre_sid:
        for x, want in (('aʰpa', pre_sid), ('tʰa', 'U+02B0'), ('t͡sʰa', 'U+02B0')):
            got = [m for s_ in _segments(read(x, t=t)) for m in s_['mods']]
            check(got == [want], '%s: ʰ read as %s' % (x, got))

    # a letter of two characters (ɹ̈ ɹ̺, D74) stays itself with a mark after it, and with a mark
    # below that canonical order puts before its own mark (ɹ̩̈ comes as ɹ, ̩, ̈); a letter of two
    # letters (ǃ¡, D78) takes its marks after its second (one between is the first letter's)
    for sid, e in t.sounds.items():
        if e['kind'] == 'base' and len(e['ipa']) == 2:
            mark2 = unicodedata.combining(e['ipa'][1]) != 0
            for x, mark in ((e['ipa'] + 'ː', 'U+02D0'),
                            (e['ipa'][0] + '̩' + e['ipa'][1] if mark2 else e['ipa'] + '̩', 'U+0329'),
                            (e['ipa'][0] + '̥' + e['ipa'][1] if mark2 else e['ipa'] + '̥', 'U+0325')):
                sg = _segments(read(unicodedata.normalize('NFD', x), t=t))
                check(len(sg) == 1 and sg[0]['base'] == sid and sg[0]['mods'] == [mark],
                      '%s read as %s' % (x, [(g.get('base'), g.get('mods')) for g in sg]))
    # a letter of three characters (h̪͆ ɦ̪͆, D79) or four (tʰ̪͆, D80) stays itself with a mark after
    # it, and with a mark of its next-to-last mark's class typed before its last (canonical order
    # keeps it there); a tied letter (ↀ͡r, D80) with marks after it
    for sid, e in t.sounds.items():
        if e['kind'] == 'base' and len(e['ipa']) in (3, 4):
            tied = e['ipa'][1] in '͜͡'
            for x, mark in ((e['ipa'] + 'ː', 'U+02D0'), (e['ipa'] + '̥' if tied else e['ipa'][:-1] + '̥' + e['ipa'][-1],
                                                        'U+0325')):
                sg = _segments(read(unicodedata.normalize('NFD', x), t=t))
                check(len(sg) == 1 and sg[0]['base'] == sid and sg[0]['mods'] == [mark],
                      '%s read as %s' % (x, [(g.get('base'), g.get('mods')) for g in sg]))
    # two marks that each make a letter of ɹ: the first in canonical order is the letter's, as in
    # the front-end (D77)
    sg = _segments(read('ɹ̺̈', strict=False, t=t))
    check(len(sg) == 1 and sg[0]['base'] == ipa.get('ɹ̺') and sg[0]['mods'] == ['U+0308'],
          'ɹ̺̈ read as %s' % [(g.get('base'), g.get('mods')) for g in sg])
    # and the letter's own mark is found behind a mark of two characters (ɹ̈ with ◌̥᪽: ɹ, ̥, ᪽, ̈)
    sg = _segments(read(unicodedata.normalize('NFD', 'ɹ̥᪽̈'), t=t))
    check(len(sg) == 1 and sg[0]['base'] == ipa.get('ɹ̈') and sg[0]['mods'] == ['B:U+0325+U+1ABD'],
          'ɹ̥᪽̈ read as %s' % [(g.get('base'), g.get('mods')) for g in sg])
    # a mark that begins a mark of two makes no letter of two (𝼀̬᪽ is 𝼀 with ◌̬᪽); ç stays ç in
    # loose reading too, its cedilla behind an overlay (D77, the review)
    sg = _segments(read('𝼀̬᪽', strict=False, t=t))
    check(len(sg) == 1 and sg[0]['base'] == ipa.get('𝼀') and sg[0]['mods'] == ['B:U+032C+U+1ABD'],
          '𝼀̬᪽ read as %s' % [(g.get('base'), g.get('mods')) for g in sg])
    for st in (True, False):
        sg = _segments(read('ç̴', strict=st, t=t))
        check(len(sg) == 1 and sg[0]['base'] == ipa.get('ç') and sg[0]['mods'] == ['U+0334'],
              'ç̴ (strict %s) read as %s' % (st, [(g.get('base'), g.get('mods')) for g in sg]))
    # a mark of Unicode 14 is put in canonical order, as Python's tables (13.0) do not (D77): the
    # two orders of ◌̈ and extIPA's ◌̥᫃ on t read alike, the mark of two characters kept whole
    a, b = read('ẗ̥᫃', strict=False, t=t), read('ẗ̥᫃', strict=False, t=t)
    check(a['items'] == b['items'] and 'B:U+0325+U+1AC3' in _segments(a)[0]['mods'],
          'ẗ̥᫃ and ẗ̥᫃ read %s and %s' % (_segments(a)[0].get('mods'), _segments(b)[0].get('mods')))

    # a mark spelt two ways (ipa/aliases.toml) reads alike on a letter (U+033E for U+034B, Q26)
    for alias, real in ALWAYS.items():
        if len(alias) == 1 and real in ipa and t.sounds[ipa[real]]['kind'] == 'modifier':
            a, b = read('n' + alias, t=t), read('n' + real, t=t)
            check(_segments(a)[0]['features'] == _segments(b)[0]['features'], '%s and %s read differently' % (alias, real))

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
