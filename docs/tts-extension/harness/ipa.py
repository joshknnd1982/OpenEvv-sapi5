"""IPA in, the engine's own phoneme names out. Never a silent substitution.

For a pack read by eSpeak NG, IPA becomes eSpeak NG phoneme names from the pack's own phoneme
table (as `OpenEvvFrontend --dump-phonemes` lists it), which the front-end then says as they
stand (`--phonemes`, `[[...]]`). For a native pack, IPA becomes the module's phones in its own
annotation, ``[.1ta.0ta]``, from the phone-to-IPA tables in engine/espeak_phonemes.py.

The IPA is read longest match first. A symbol the table has no phoneme for is an error that
names it: a harness that quietly said something else would measure the wrong sound (playbook R7).

    ˈ ˌ    stress (eSpeak NG ' and ,; a module syllable .1 and .2, others .0)
    .      syllable break (eSpeak NG -; a module syllable)
    space  word break
"""

import json
import os
import re
import subprocess
import unicodedata

import engine

STRESS = {'ˈ': "'", 'ˌ': ','}

_dump = None


def dump():
    """Every eSpeak NG phoneme table, as the front-end lists them (cached beside the work files)."""
    global _dump
    if _dump is None:
        cache = os.path.join(engine.WORK, 'espeak_phonemes.json')
        stamp = os.path.getmtime(os.path.join(engine.FE_DATA, 'phontab'))
        if not os.path.exists(cache) or os.path.getmtime(cache) < stamp:
            os.makedirs(engine.WORK, exist_ok=True)
            r = subprocess.run([engine.FRONTEND, '--data', engine.FE_DATA, '--dump-phonemes'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            if r.returncode != 0:
                raise engine.HarnessError('--dump-phonemes failed: %s' % r.stderr.decode('utf-8', 'replace'))
            with open(cache, 'wb') as f:
                f.write(r.stdout)
        with open(cache, encoding='utf-8') as f:
            _dump = {t['table']: t for t in json.load(f)}
    return _dump


def voice_table(p):
    """The phoneme table an eSpeak NG voice uses: its last `phonemes` line naming a table that
    exists, else its language."""
    path = os.path.join(engine.FE_DATA, 'lang', *p.voice.split('/'))
    language, named = None, []
    with open(path, encoding='utf-8') as f:
        for line in f:
            w = line.split()
            if len(w) >= 2 and w[0] == 'phonemes':
                named.append(w[1])
            if len(w) >= 2 and w[0] == 'language' and language is None:
                language = w[1]
    tables = dump()
    # a voice may name several (art/xex: pt-br, which does not exist, then pt): the last that exists
    for name in reversed(named):
        if name in tables:
            return name
    for name in (language, (language or '').split('-')[0], os.path.basename(path)):
        if name and name in tables:
            return name
    raise engine.HarnessError('no phoneme table found for voice %s' % p.voice)


def espeak_inventory(p):
    """mnemonic -> IPA for every phoneme the pack's table can say (a later entry overrides)."""
    phon = {}
    for ph in dump()[voice_table(p)]['phonemes']:
        if ph['mnemonic'] and ph['ipa'] and not ph['mnemonic'].startswith('_'):
            phon[ph['mnemonic']] = unicodedata.normalize('NFD', ph['ipa'])
    return phon


def _longest(s, i, keys):
    for k in sorted(keys, key=len, reverse=True):
        if s.startswith(k, i):
            return k
    return None


def to_espeak(p, ipa):
    """eSpeak NG phoneme names for an IPA string, for the pack's table."""
    phon = espeak_inventory(p)
    by_ipa = {}
    for m, i in phon.items():
        if i in STRESS or i in ('ː', '-', '%', '%%', '=', '1'):
            continue
        # the shortest name for each IPA: eSpeak NG's own variants (R2, R3) are longer
        if i not in by_ipa or len(m) < len(by_ipa[i]):
            by_ipa[i] = m
    s = unicodedata.normalize('NFD', ipa)
    out, i = [], 0
    while i < len(s):
        ch = s[i]
        if ch in STRESS:
            out.append(STRESS[ch]); i += 1; continue
        if ch == ' ':
            out.append(' '); i += 1; continue
        if ch == '.':
            out.append('-'); i += 1; continue
        k = _longest(s, i, by_ipa)
        if k is None:
            if ch == 'ː' and out:
                out.append(':'); i += 1; continue
            raise engine.HarnessError('%s (table %s) has no phoneme for %r (U+%04X) in %r'
                                      % (p.tag, voice_table(p), ch, ord(ch), ipa))
        out.append(by_ipa[k])
        i += len(k)
    names = ''.join(out)
    # eSpeak NG reads [[...]] longest name first too: the names joined must read back the same,
    # or two phonemes would merge into a third (t + S read as tS).
    back, j, mnems = [], 0, set(phon) | {"'", ',', ' ', '-', ':'}
    while j < len(names):
        k = _longest(names, j, mnems)
        if k is None:
            break
        back.append(k)
        j += len(k)
    if back != out:
        raise engine.HarnessError('%r would be read back by eSpeak NG as %s, not %s'
                                  % (ipa, ' '.join(back), ' '.join(out)))
    return names


def module_inventory(p):
    """IPA -> module phone for a native pack, from engine/espeak_phonemes.py."""
    import sys
    sys.path.insert(0, os.path.join(engine.ROOT, 'engine'))
    import espeak_phonemes
    t = espeak_phonemes.TEMPLATES.get(p.module_tag)
    if t is None:
        raise engine.HarnessError('no phone-to-IPA table for module %s (engine/espeak_phonemes.py has %s)'
                                  % (p.module_tag, ', '.join(sorted(espeak_phonemes.TEMPLATES))))
    inv = {}
    for table in (t.vowels, t.consonants):
        for phone, i in table.items():
            inv.setdefault(unicodedata.normalize('NFD', i), phone)
    # Phones those tables give no IPA of their own (English e o Y W O F, German aj aw oj E:) take
    # it from the mapping eSpeak NG's vowels are said with, but never a key that is the start of
    # another key for the same phone: /e/ is not English e, which is [eɪ].
    own = set(inv.values())
    extra = {}
    for table in (t.diphthongs, t.longs):
        for i, phone in table.items():
            if ' ' not in phone and phone not in own:
                extra.setdefault(phone, set()).add(unicodedata.normalize('NFD', i))
    for phone, keys in extra.items():
        for k in keys:
            if not any(o != k and o.startswith(k) for o in keys):
                inv.setdefault(k, phone)
    if 'ɡ' in inv:
        inv.setdefault('g', inv['ɡ'])
    return inv


_module_names = {}


def module_names(tag):
    """Every phone name a native module declares (docs/tts-extension/inventory/languages.json)."""
    if tag not in _module_names:
        path = os.path.join(engine.ROOT, 'docs', 'tts-extension', 'inventory', 'languages.json')
        with open(path, encoding='utf-8') as f:
            packs = {q['tag']: q for q in json.load(f)['packs']}
        _module_names[tag] = {ph['name'] for ph in packs.get(tag, {}).get('phonemes', []) if ph['name']}
    return _module_names[tag]


def module_phones(p, annotation):
    """The module phones an annotation asks for, in order; None if it holds anything but `[...] words."""
    names = module_names(p.module_tag)
    out = []
    rest = annotation.strip()
    for word in rest.split():
        m = re.fullmatch(r'`\[(.*)\]', word)
        if not m or not names:
            return None
        body = re.sub(r'\.\d', '', m.group(1))
        i = 0
        while i < len(body):
            if body[i] == "'":
                # a phone name in single quotes, as written for E: a~ (DECISIONS.md D30)
                j = body.find("'", i + 1)
                if j < 0 or body[i + 1:j] not in names:
                    raise engine.HarnessError('module %s has no phone %r in %r' % (p.module_tag, body[i:j + 1], annotation))
                out.append(body[i + 1:j])
                i = j + 1
                continue
            k = _longest(body, i, names)
            if k is None:
                raise engine.HarnessError('module %s has no phone at %r in %r' % (p.module_tag, body[i:], annotation))
            out.append(k)
            i += len(k)
    return out


def to_module(p, ipa):
    """A native module's annotation for an IPA string: `[.1ta.0ta] (one word a [...])."""
    inv = module_inventory(p)
    words = []
    for word in unicodedata.normalize('NFD', ipa).split():
        sylls, cur, stress, i = [], [], None, 0
        while i < len(word):
            ch = word[i]
            if ch in STRESS or ch == '.':
                if cur:
                    sylls.append((stress, cur))
                cur, stress = [], {'ˈ': 1, 'ˌ': 2}.get(ch)
                i += 1
                continue
            k = _longest(word, i, inv)
            if k is None:
                raise engine.HarnessError('module %s has no phone for %r (U+%04X) in %r'
                                          % (p.module_tag, ch, ord(ch), ipa))
            cur.append(inv[k])
            i += len(k)
        if cur:
            sylls.append((stress, cur))
        if all(s is None for s, _ in sylls):
            sylls[0] = (1, sylls[0][1])     # no stress written: the first syllable carries it
        words.append('`[' + ''.join('.%d%s' % (s or 0, ''.join(c)) for s, c in sylls) + ']')
    return ' '.join(words)
