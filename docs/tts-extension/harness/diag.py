"""C1 "never silent" (DESIGN.md 4.3): what the front-end loses on the way, counted.

The front-end reports, as `diag` lines on stderr, everything it drops, cuts short, skips or says
as something else (frontend/src/evv_map.h): a `loss` is something the map did not ask for, a
`note` something it did (an entry given as `-`, a schwa put before a syllabic consonant). This
script runs it over every golden input of each pack read by eSpeak NG (each as a sentence of its
own) and over the pack's speech-recognition sentences, and counts what it reports.

    python docs/tts-extension/harness/diag.py [tags...]
        the count, written to results/diag.json
    python docs/tts-extension/harness/diag.py --compare OLD_FRONTEND.exe [tags...]
        also runs an older front-end on the same input and fails unless the text it hands the
        engine (with every word's position) is byte-identical: diagnostics change what is
        reported, never what is said

The front-end is engine.FRONTEND (EVV_FRONTEND to choose another).
"""

import argparse
import collections
import concurrent.futures
import gzip
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine  # noqa: E402

GOLDEN = os.path.join(HERE, 'golden')
SENTENCES = os.path.join(HERE, 'asr', 'sentences.json')


def golden_inputs(tag):
    path = os.path.join(GOLDEN, tag + '.json.gz')
    if not os.path.exists(path):
        return []
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        cases = json.load(f)['cases']
    return [c['input'] for _, c in sorted(cases.items()) if c.get('kind') == 'espeak']


def asr_sentences(tag):
    with open(SENTENCES, encoding='utf-8') as f:
        d = json.load(f)
    return [s['text'] for s in ((d['languages'].get(tag) or {}).get('sentences') or [])]


def run(exe, p, text, phonemes):
    """(stdout bytes, diagnostics as a list of (level, kind, detail, count), exit code)."""
    fd, path = tempfile.mkstemp(suffix='.txt', prefix='evvdiag')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(text.encode('utf-8'))
        cmd = [exe, '--data', engine.FE_DATA, '--voice', p.voice, '--map', p.sounds_map, '--file', path, '--anchors']
        if phonemes:
            cmd.append('--phonemes')
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    finally:
        os.remove(path)
    diags = []
    for line in r.stderr.decode('utf-8', 'replace').splitlines():
        f = line.split('\t')
        if len(f) == 5 and f[0] == 'diag':
            diags.append((f[1], f[2], f[3], int(f[4])))
    return r.stdout, diags, r.returncode


def one_pack(tag, old):
    p = engine.pack(tag)
    inputs = [('golden', ' '.join('[[%s]].' % t for t in golden_inputs(tag)), True),
              ('sentences', '\n'.join(asr_sentences(tag)), False)]
    res = {'tag': tag, 'template': p.template, 'differs': [], 'diags': {}}
    for name, text, phonemes in inputs:
        if not text.strip():
            continue
        out, diags, code = run(engine.FRONTEND, p, text, phonemes)
        if code != 0:
            res['differs'].append('%s: the front-end exited %d' % (name, code))
        if old:
            out_old, _, code_old = run(old, p, text, phonemes)
            if out_old != out or code_old != code:
                res['differs'].append('%s: the output differs from the old front-end\'s' % name)
        res['diags'][name] = diags
    return res


# ---- planted faults: each kind of loss must be reported ----------------------------------------

def _drop(*keys):
    """An edit that removes the map's lines whose first word is one of `keys`."""
    def edit(lines):
        return [l for l in lines if not (l.split() and l.split()[0] in keys)]
    return edit


def _add(*new):
    def edit(lines):
        return lines + list(new)
    return edit


def _both(*edits):
    def edit(lines):
        for e in edits:
            lines = e(lines)
        return lines
    return edit


def _keep(lines):
    return lines


ONE_WORD = "[['a%sa]]" % ('s' * 300)
SPELLED = ''.join('18Y%sY ' % c for c in 'abcdefghij' * 7)
S = ('s', '@hi:s')             # Hindi's s: an IPA key and its own table's
TH = ('tʰ', 'ʰ', '@hi:t#')     # and its aspirated t


def _drop_line(line):
    def edit(lines):
        return [l for l in lines if l.split() != line.split()]
    return edit


# (kind, pack, edit of its sounds.map, input, given as eSpeak NG phonemes?, control input)
# The control is the same pack's own map with the control input (the same input by default): the
# kind must not be reported there, so that what is reported is the planted fault's doing.
PLANTS = [
    ('phoneme-dropped', 'hi', _drop(*S), "[['asa]]", True, None),
    ('ipa-char-skipped', 'hi', _drop(*TH), "[['at#a]]", True, None),
    ('said-as-nothing', 'hi', _both(_drop(*S), _add('s -')), "[['asa]]", True, None),
    ('phones-cut', 'hi', _both(_drop('t', '@hi:t', *TH), _add('t t t t t t', 'ʰ t t t t')), "[['at#a]]", True, None),
    ('map-sound-undefined', 'hi', _both(_drop(*S), _add('s s=s999')), "[['asa]]", True, None),
    ('map-key-duplicate', 'hi', _add('s z'), "[['asa]]", True, None),
    ('map-id-duplicate', 'hi', _add('sound s1 f1=100'), "[['asa]]", True, None),
    ('map-ignored', 'hi', _add('style fancy'), "[['asa]]", True, None),
    ('map-ignored', 'hi', _add('secondary 7'), "[['asa]]", True, None),
    ('map-ignored', 'hi', _add('onset 9'), "[['asa]]", True, None),
    ('map-ignored', 'hi', _add('tonename 55'), "[['asa]]", True, None),
    ('map-ignored', 'hi', _add('sound'), "[['asa]]", True, None),
    ('map-ignored', 'hi', _add('says {X} a'), "[['asa]]", True, None),
    ('map-ignored', 'hi', _add('accent f0=own'), "[['asa]]", True, None),
    ('map-list-full', 'hi', _add(*['cluster p r'] * 17), "[['asa]]", True, None),
    ('map-name-cut', 'hi', _both(_drop(*S), _add('s sssssssss')), "[['asa]]", True, None),
    ('map-line-long', 'hi', _add('says a' + ' ' * 1100 + 'b'), "[['asa]]", True, None),
    ('map-tone-undefined', 'cmn', _add('tonename 99 77'), '妈', False, None),
    ('tone-unknown', 'cmn', _drop_line('tone 55 p=0:48,100:50'), '妈', False, None),
    ('tone-unsupported', 'cmn', _drop('tone', 'weaktones'), '妈', False, None),
    ('word-no-nucleus', 'hi', _drop('schwa'), '[[s]]', True, None),
    ('syllable-no-nucleus', 'en-us-nyc', _drop('schwa'), 'button', False, None),
    ('schwa-inserted', 'en-us-nyc', _keep, 'button', False, 'bat'),
    ('word-too-long', 'hi', _keep, ONE_WORD, True, "[['asa]]"),
    ('spelled-full', 'hi', _keep, SPELLED, False, 'abc'),
]

# Kinds no input can reach, kept as guards: the key `@table:mnemonic' longer than 63 bytes
# (eSpeak NG's names are a few bytes); memory running out; an annotation longer than its buffer
# (sized for the longest word); more than 256 kinds in one result; the text cut after 100,000
# clauses; more than 400 words in a clause (eSpeak NG ends a clause at 300, N_CLAUSE_WORDS); a
# word with no vowel too long to join its neighbour (a word holds 256 phones); a tone eSpeak NG
# has no phoneme for; a length mark said without its length (needs a lengthened phoneme whose
# map has no key for it plus `ː`, and every map gives `ː`).
GUARDS = ['key-cut', 'out-of-memory', 'annotation-cut', 'diagnostics-full', 'text-cut', 'clause-words-full',
          'word-too-long (joined)', 'tone-unknown (no phoneme)', 'length-dropped']


A = '{A v=1}'
W = '{W .1 a^-}`[.1a]'
# The accent layer's own (openevv/src/accent/evv_accent.c): annotated text with one fault each,
# said by a staged module with the trace on. (kind, text)
ACCENT_PLANTS = [
    ('key-unknown', A + '{D s1 colour=9}{W .1 a=s1^-}`[.1a]'),
    ('value-not-number', A + '{D s1 f2=abc}{W .1 a=s1^-}`[.1a]'),
    ('sound-unknown', A + '{W .1 a=s99^-}`[.1a]'),
    ('tone-unknown', A + '{W .1 a^t9}`[.1a]'),
    ('ending-unknown', A + W + '{P z}'),
    ('markup-before-accent', '{D s1 f2=90}' + A + W),
    ('markup-unclosed', A + '{W .1 a^- `[.1a]'),
    ('word-cut', A + '{D s1 f2=' + '9' * 80 + '}' + W),
    ('name-cut', A + '{D s123456789012345 f2=90}' + W),
    ('defs-full', A + ''.join('{D s%d f2=90}' % i for i in range(1, 390)) + W),
    ('tones-full', A + ''.join('{T t%d p=0:3,100:3}' % i for i in range(1, 70)) + W),
    ('tone-points', A + '{T t1 p=%s}' % ','.join('%d:3' % (i * 10) for i in range(10)) + W),
    ('tone-points', A + '{T t1 p=0:3,x}' + W),
    ('rules-full', A + ''.join('{X q%d a}' % i for i in range(1, 100)) + W),
    ('rule-cut', A + '{X q a b c d e f}' + W),
    ('rule-empty', A + '{X q}' + W),
    ('key-inert', '{A v=1 f0=own}{D s1 f0=-15}{W .1 a=s1^-}`[.1a]'),
    ('phone-unsounded', A + '{W .1 a^- x .0 i^-}`[.1a.0i]'),
]
ACCENT_GUARDS = ['machines-full (16 engines at once)', 'out-of-memory', 'pitch-points-full', 'line-up-full (a note)']


def plant_accent(tag='hi'):
    if not engine.STAGE:
        print('plant-accent needs EVV_STAGE: the accent layer that reports is in the staged modules')
        return 1
    cases = [('%02d' % i, 'annotated', text) for i, (_, text) in enumerate(ACCENT_PLANTS)]
    control = engine.render(tag, [('c', 'annotated', A + '{D s1 f2=90}{W .1 a=s1^-}`[.1a]')],
                            work=os.path.join(engine.WORK, 'diag-accent'))[0]
    res = engine.render(tag, cases, work=os.path.join(engine.WORK, 'diag-accent'))
    failed = 0
    print('control: %s' % (', '.join(sorted({d['kind'] for d in control['diag']})) or 'nothing reported'))
    for (kind, _), r in zip(ACCENT_PLANTS, res):
        kinds = sorted({d['kind'] for d in r['diag'] if d['source'] == 'accent'})
        ok = kind in kinds and not control['diag']
        failed += not ok
        print('%-4s %-22s reported: %s' % ('ok' if ok else 'FAIL', kind, ', '.join(kinds) or 'nothing'))
    print('accent layer: planted %d, reported %d; guards not reached by these cases: %s' % (
        len(ACCENT_PLANTS), len(ACCENT_PLANTS) - failed, '; '.join(ACCENT_GUARDS)))
    return 1 if failed else 0


def plant(work):
    os.makedirs(work, exist_ok=True)
    failed = 0
    for i, (kind, tag, edit, text, phonemes, control_text) in enumerate(PLANTS):
        p = engine.pack(tag)
        with open(p.sounds_map, encoding='utf-8') as f:
            lines = f.read().split('\n')
        path = os.path.join(work, 'plant-%02d.map' % i)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(edit(lines)))
        planted = type(p)(p.tag, _ini_of(p), p.dir)
        planted.sounds_map = path
        _, control, _ = run(engine.FRONTEND, p, control_text or text, phonemes)
        _, diags, code = run(engine.FRONTEND, planted, text, phonemes)
        kinds = [d[1] for d in diags]
        before = [d[1] for d in control]
        ok = kind in kinds and kind not in before
        failed += not ok
        print('%-4s %-20s %-10s reported: %s%s' % ('ok' if ok else 'FAIL', kind, tag,
                                                  ', '.join(sorted(set(kinds))) or 'nothing',
                                                  '   (already without the fault)' if kind in before else ''))
    print('planted %d, reported %d; guards not reachable by input: %s' % (
        len(PLANTS), len(PLANTS) - failed, ', '.join(GUARDS)))
    return 1 if failed else 0


def _ini_of(p):
    import configparser
    ini = configparser.ConfigParser(strict=False, interpolation=None)
    ini.optionxform = str
    with open(os.path.join(p.dir, 'language.ini'), encoding='utf-8-sig') as f:
        ini.read_file(f)
    return ini


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('tags', nargs='*')
    ap.add_argument('--compare', metavar='OLD_FRONTEND')
    ap.add_argument('--plant', action='store_true', help='plant each kind of fault and check it is reported')
    ap.add_argument('--plant-accent', action='store_true',
                    help='the same for the accent layer, through the staged modules (EVV_STAGE)')
    ap.add_argument('--jobs', type=int, default=os.cpu_count())
    a = ap.parse_args()
    if a.plant:
        return plant(os.path.join(engine.WORK, 'diag-plant'))
    if a.plant_accent:
        return plant_accent()
    # read every pack before the threads start: engine.packs() fills its table lazily
    all_packs = engine.packs()
    tags = a.tags or [t for t, p in sorted(all_packs.items()) if p.kind == 'espeak']
    results = {}
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(lambda t: one_pack(t, a.compare), tags):
            results[r['tag']] = r
    # the count: events, by level and kind, over all packs; and how many packs have any
    events = collections.Counter()
    packs_with = collections.defaultdict(set)
    loss_packs = set()
    for tag, r in results.items():
        for name, diags in r['diags'].items():
            for level, kind, detail, count in diags:
                events[(level, kind, name)] += count
                packs_with[(level, kind, name)].add(tag)
                if level == 'loss':
                    loss_packs.add(tag)
    differs = {t: r['differs'] for t, r in results.items() if r['differs']}
    print('diag: %d packs; %d with a loss; %d whose output %s' % (
        len(results), len(loss_packs), len(differs),
        'differs from the old front-end\'s or failed' if a.compare else 'failed'))
    for t, why in sorted(differs.items()):
        print('  %s: %s' % (t, '; '.join(why)))
    print('%-5s %-22s %-10s %8s %6s' % ('level', 'kind', 'input', 'events', 'packs'))
    for (level, kind, name), n in sorted(events.items(), key=lambda kv: (kv[0][0] != 'loss', -kv[1])):
        print('%-5s %-22s %-10s %8d %6d' % (level, kind, name, n, len(packs_with[(level, kind, name)])))
    out = os.path.join(HERE, 'results', 'diag%s.json' % ('-compare' if a.compare else ''))
    if not a.tags:
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'frontend': engine.FRONTEND, 'compared_with': a.compare, 'packs': results}, f,
                      ensure_ascii=False, indent=1, sort_keys=True)
        print('written', os.path.relpath(out, engine.ROOT))
    return 1 if differs else 0


if __name__ == '__main__':
    sys.exit(main())
