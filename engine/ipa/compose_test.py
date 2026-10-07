"""The C4 test (DESIGN.md 4.3): the front-end's composition equals the adapter's, and each
fallback warns. MIT licence.

    python engine/ipa/compose_test.py [--template dedx] [--pack hi]

A test map is made of the pack's own header lines (template, vowels, glides, schwa, accent: what
any map needs) and the realised map of the master table (ipa/realized/<template>.map, with its
`version 2`, `letter` and `mod` lines), so that every base letter is the table's. The front-end
(engine.FRONTEND, EVV_FRONTEND for another) reads IPA with `--ipa`; for each letter-and-marks the
sample holds, the sound it composed (its `composed` note) must have the keys the adapter composes,
each within 1 (the front-end rounds the base and each step; the adapter once at the end). Then
the fallbacks: a letter with no line (said as the nearest by features), a mark with no `mod` line
for its class (left off), a character that is no letter: each must be reported as a loss.
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
    """The IPA as the front-end keeps it: canonical decomposition, then c and a cedilla put back
    together as the chart letter ç (frontend_main.c ipa_normalize, ipa/aliases.toml)."""
    # the cedilla may follow other marks of c in canonical order (an overlay comes first)
    return re.sub('c([\u0300-\u036f]*?)\u0327', '\u00e7\\1', unicodedata.normalize('NFD', ipa))


def composed_keys(diags):
    """{ipa: {key: value}} from the front-end's `composed` notes."""
    out = {}
    for d in diags:
        if d['kind'] != 'composed':
            continue
        m = re.match(r'/(.+?)/ = .* as \{D \S+ ?(.*)\}$', d['detail'])
        if m:
            out[m.group(1)] = {k: int(v) for k, v in (kv.split('=') for kv in m.group(2).split())}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--template', default='dedx')
    ap.add_argument('--pack', default='hi')
    a = ap.parse_args()
    t = T.load()
    work = os.path.join(E.WORK, 'c4')
    os.makedirs(work, exist_ok=True)
    p, map_path = test_map(a.pack, a.template, work)
    without_letter(map_path, 'ɯ')
    # the sample: every realised letter with every modifier that has a transform for its class,
    # one at a time and in pairs
    # (not ɯ: its line is taken out, to show the fallback below)
    letters = [sid for sid, e in sorted(t.sounds.items()) if e.get('kind') == 'base' and e.get('spec') and e['ipa'] != 'ɯ']
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
    failures, compared = [], 0
    for b, ms in sample:
        # a mark written before its letter (Tier B, D70) goes before it
        ipa = ''.join(t.sounds[m]['ipa'] for m in ms if t.sounds[m].get('placement') == 'before') + \
            t.sounds[b]['ipa'] + ''.join(t.sounds[m]['ipa'] for m in ms if t.sounds[m].get('placement') != 'before')
        want = AD.compose(t, b, ms, a.template, _carrier_meas(b))
        if ms and t.sounds[ms[0]].get('kind') == 'syllable-mark':
            # a stressed vowel: the front-end composes its nucleus with the stress mark after it
            code, out, diags = say_ipa(p, map_path, ms and t.sounds[ms[0]]['ipa'] + t.sounds[b]['ipa'])
        else:
            # after a stressed syllable, so that the letter under test carries no stress of its own
            code, out, diags = say_ipa(p, map_path, 'ˈpa' + ipa)
        # the front-end puts marks in canonical order (a mark below before a mark above)
        got = composed_keys(diags).get(fe_form(ipa))
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
    fallbacks = [('ɯ', 'nearest-letter'), ('aʰ', 'mark-left-off'), ('5', 'ipa-not-a-letter'),
                 ('aʼ', 'mark-left-off')]
    for ipa, kind in fallbacks:
        code, out, diags = say_ipa(p, map_path, ipa)
        kinds = sorted({d['kind'] for d in diags if d['level'] == 'loss'})
        ok = kind in kinds
        print('%-4s %-6s fallback reported: %s' % ('ok' if ok else 'FAIL', ipa, ', '.join(kinds) or 'nothing'))
        if not ok:
            failures.append(ipa)
    print('compose: %d compositions compared, %d fallbacks; %d failed' % (compared, len(fallbacks), len(failures)))
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
