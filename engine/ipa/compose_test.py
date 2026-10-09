"""The C4 test (DESIGN.md 4.3): the front-end's composition equals the adapter's, and each
fallback warns. MIT licence.

    python engine/ipa/compose_test.py [--template dedx] [--pack hi] [--letters ɹ̈ ɹ̺ ...]

A test map is made of the pack's own header lines (template, vowels, glides, schwa, accent: what
any map needs) and the realised map of the master table (ipa/realized/<template>.map, with its
`version 2`, `letter` and `mod` lines), so that every base letter is the table's. The front-end
(engine.FRONTEND, EVV_FRONTEND for another) reads IPA with `--ipa`; for each letter-and-marks the
sample holds, the sound it composed (its `composed` note) must have the keys the adapter composes,
each within 1 (the front-end rounds the base and each step; the adapter once at the end). Then
the fallbacks: a letter with no line (said as the nearest by features), a mark with no `mod` line
for its class (left off), a character that is no letter: each must be reported as a loss. A mark of
extIPA's own reading (`notation', Q18) is composed through the map with `notation extipa' in
front, and must be left off, and reported, by the map without it. The adapter is given the marks in
the order the front-end meets them (as written, in canonical order): where two marks set one key,
the one met last is the one said. Which letter and marks a string is, and that order, are the
reader's (engine/ipa/reader.py), which reads as the front-end does: `ɹ̈' with ̺ is written as `ɹ̺'
with ̈, and is that (D77). `--letters' tests only those letters (with every mark).
"""

import argparse
import itertools
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
import adapter as AD  # noqa: E402
import reader as R  # noqa: E402
import table as T  # noqa: E402
import engine as E  # noqa: E402

HEADER_KEYS = ('template', 'style', 'vowels', 'glides', 'schwa', 'secondary', 'accent')


def test_map(pack, template, work):
    p = E.pack(pack)
    lines = []
    with open(p.sounds_map, encoding='utf-8') as f:
        for line in f:
            if line.split() and line.split()[0] in HEADER_KEYS:
                lines.append(line.rstrip('\n'))
    with open(os.path.join(ROOT, 'ipa', 'realized', template + '.map'), encoding='utf-8') as f:
        lines += [l.rstrip('\n') for l in f]
    path = os.path.join(work, 'c4-%s.map' % template)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    return p, path


def say_ipa(p, map_path, text):
    fd, tmp = tempfile.mkstemp(suffix='.txt')
    with os.fdopen(fd, 'wb') as f:
        f.write(text.encode('utf-8'))
    try:
        r = subprocess.run([E.FRONTEND, '--data', E.FE_DATA, '--voice', p.voice, '--map', map_path, '--file', tmp,
                            '--ipa'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    finally:
        os.remove(tmp)
    diags = E.parse_diag(r.stderr.decode('utf-8', 'replace').splitlines(), 'frontend')
    return r.returncode, r.stdout.decode('utf-8'), diags


def fe_form(ipa):
    """The IPA as the front-end keeps it: canonical decomposition (the marks of Unicode 14 put in
    order too, D77), then c and a cedilla put back together as the chart letter ç
    (frontend_main.c ipa_normalize, ipa/aliases.toml)."""
    # the cedilla may follow other marks of c in canonical order (an overlay comes first)
    return re.sub('c([\u0300-\u036f]*?)\u0327', '\u00e7\\1', R.canonical_order(unicodedata.normalize('NFD', ipa)))


def composed_keys(diags, said):
    """{ipa: {key: value}}: each `composed' note names the letter and the id it was composed as,
    and the definition is read under that id from what the front-end says (the note's own copy
    is cut at the front-end's 200 bytes of a note: a long one lost its last key, D72)."""
    out = {}
    for d in diags:
        if d['kind'] != 'composed':
            continue
        m = re.match(r'/(.+?)/ = .* as \{D (\S+)', d['detail'])
        if not m:
            continue
        df = re.search(r'\{D %s(?=[ }]) ?([^}]*)\}' % re.escape(m.group(2)), said)
        if df:
            out[m.group(1)] = {k: int(v) for k, v in (kv.split('=') for kv in df.group(1).split())}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--template', default='dedx')
    ap.add_argument('--pack', default='hi')
    ap.add_argument('--letters', nargs='*', help='only these letters (as IPA)')
    a = ap.parse_args()
    t = T.load()
    work = os.path.join(E.WORK, 'c4')
    os.makedirs(work, exist_ok=True)
    p, map_path = test_map(a.pack, a.template, work)
    without_letter(map_path, 'ɯ')
    # a mark of extIPA's own reading (Q18, D71: ingressive ↓) is composed only by a map that
    # declares extIPA: the same map with that one line in front
    with open(map_path, encoding='utf-8') as f:
        body = f.read()
    declared = {}
    for n in sorted({e['notation'] for e in t.sounds.values() if e.get('notation')}):
        declared[n] = map_path[:-4] + '-%s.map' % n
        with open(declared[n], 'w', encoding='utf-8', newline='\n') as f:
            f.write('notation %s\n' % n + body)
    # the sample: every realised letter with every modifier that has a transform for its class,
    # one at a time and in pairs
    # (not ɯ: its line is taken out, to show the fallback below)
    letters = [sid for sid, e in sorted(t.sounds.items()) if e.get('kind') == 'base' and e.get('spec') and e['ipa'] != 'ɯ'
               and (not a.letters or e['ipa'] in a.letters)]
    # marks written after a letter; the stress mark is not one of them (it stands before a
    # syllable), and is tested on its own below
    mods = [sid for sid, e in sorted(t.sounds.items()) if e.get('transform') and e.get('kind') == 'modifier']
    stress = [sid for sid, e in sorted(t.sounds.items()) if e.get('transform') and e.get('kind') == 'syllable-mark']
    sample = []
    for b in letters:
        cls = t.sounds[b]['features']['class']
        usable = [m for m in mods if cls in t.sounds[m]['transform']]
        for k in (1, 2):
            for ms in itertools.combinations(usable, k):
                sample.append((b, list(ms)))
        for m in stress:
            if cls in t.sounds[m]['transform']:
                sample.append((b, [m]))
    failures, compared, letters_of_two = [], 0, 0
    for b, ms in sample:
        # a mark written before its letter (Tier B, D70) goes before it
        ipa = ''.join(t.sounds[m]['ipa'] for m in ms if t.sounds[m].get('placement') == 'before') + \
            t.sounds[b]['ipa'] + ''.join(t.sounds[m]['ipa'] for m in ms if t.sounds[m].get('placement') != 'before')
        notation = next((t.sounds[m]['notation'] for m in ms if t.sounds[m].get('notation')), None)
        # the letter and its marks as the reader reads the string, the marks in the order met: as
        # written, put in canonical order (a mark below before a mark above), the letter's own
        # mark taken out wherever it stands (D74); where two set one key (◌͎ and ◌͋ the friction's
        # level, D71), the one met last is the one said
        if not (ms and t.sounds[ms[0]].get('kind') == 'syllable-mark'):
            rd = R.read(ipa, strict=False, t=t, notation=notation or 'ipa')
            seg = [it for it in rd['items'] if it['t'] == 'seg'][0]
            b, ms = seg['base'], seg['mods']
            if not ms and len(t.sounds[b]['ipa']) == 2 and len(rd['items']) == 1:
                # the letter and mark spell a letter of two characters (ɹ with ̺ is ɹ̺, D74),
                # nothing else read: it is said by its own line, not composed, and proved as its
                # own entry
                letters_of_two += 1
                continue
        want = AD.compose(t, b, ms, a.template, _carrier_meas(b))
        mp = declared[notation] if notation else map_path
        if ms and t.sounds[ms[0]].get('kind') == 'syllable-mark':
            # a stressed vowel: the front-end composes its nucleus with the stress mark after it
            code, out, diags = say_ipa(p, mp, ms and t.sounds[ms[0]]['ipa'] + t.sounds[b]['ipa'])
        else:
            # after a stressed syllable, so that the letter under test carries no stress of its own
            code, out, diags = say_ipa(p, mp, 'ˈpa' + ipa)
        # the front-end puts marks in canonical order (a mark below before a mark above)
        got = composed_keys(diags, out).get(fe_form(ipa))
        losses = [d for d in diags if d['level'] == 'loss']
        # equal keys, and the two agree on whether a transform could not be applied (ʰ on a
        # fricative: no voice onset to add to), which both must report
        ok = got is not None and set(got) == set(want['keys']) and \
            all(abs(got[k] - want['keys'][k]) <= 1 for k in got) and bool(losses) == bool(want['lost'])
        compared += 1
        print('%-4s %-6s front-end %-28s adapter %s' % ('ok' if ok else 'FAIL', ipa, got, want['keys']))
        if not ok:
            failures.append(ipa)
    # each fallback warns
    # (every mark has a transform now, D63: a mark on a class it has none for is left off, as ʼ on
    # a vowel; tʼ was this case until ʼ had one)
    # and a mark of extIPA's own reading is left off, and reported, where extIPA is not declared
    fallbacks = [('ɯ', 'nearest-letter'), ('aʰ', 'mark-left-off'), ('5', 'ipa-not-a-letter'),
                 ('aʼ', 'mark-left-off')] + [
        ('a' + e['ipa'], 'mark-left-off') for sid, e in sorted(t.sounds.items())
        if e.get('notation') and e.get('kind') == 'modifier' and 'vowel' in (e.get('transform') or {})]
    for ipa, kind in fallbacks:
        code, out, diags = say_ipa(p, map_path, ipa)
        kinds = sorted({d['kind'] for d in diags if d['level'] == 'loss'})
        ok = kind in kinds
        print('%-4s %-6s fallback reported: %s' % ('ok' if ok else 'FAIL', ipa, ', '.join(kinds) or 'nothing'))
        if not ok:
            failures.append(ipa)
    print('compose: %d compositions compared, %d fallbacks; %d failed (%d letters of two, not compositions)' % (
        compared, len(fallbacks), len(failures), letters_of_two))
    return 1 if failures else 0


def _carrier_meas(sid):
    return (AD.loop_proof(sid) or {}).get('carrier_measured')


def without_letter(map_path, ipa):
    """The test map with one letter's line taken out, so that saying it must fall back (the
    realised map gives every letter a line)."""
    with open(map_path, encoding='utf-8') as f:
        lines = [l for l in f.read().split('\n') if l.split()[:1] != [ipa]]
    with open(map_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    sys.exit(main())
