# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Switch packs to the IPA master table's sounds: realization = "master" (Phase 11, playbook R21).

    python engine/packs/to_master.py <tag ...> | --all  [--dry-run] [--out DIR] [--faults FILE] [--report FILE]
    python engine/packs/to_master.py --check [--root DIR]    every master pack builds, no phoneme silent

For each pack read by eSpeak NG it writes, into packs/<tag>/pack.toml or, with --out, into a scratch
copy DIR/<tag>/pack.toml (the packs it extends copied beside it unchanged, so that DIR is a pack root
for `build_packs.py build <out> --root DIR`):

    [engine] realization = "master"
    [master.ipa]       each eSpeak NG phoneme of its sound map, as eSpeak NG's phoneme table states it
                       (OpenEvvFrontend --dump-phonemes)
    [master.kind]      v for a phoneme its table calls a vowel, c for any other
    [master.reading]   where eSpeak NG's phoneme file (phsource) says more than its IPA (the feature
                       `ejc`, ejective, on a phoneme whose IPA has no ʼ: read with ʼ, Abkhaz), and the
                       readings the human chose (HUMAN_READINGS), each with its reason
    [master.fallback]  the phonemes kept on their legacy line because of a fault (check A: silent,
                       swapped, unrendered), with the reason: --faults FILE adds them ({tag: {key: reason}})

and prints, per pack, what the master path made of it (R21f): phonemes from the table, composed,
created, fallen back (with the reasons), kept apart, said as nothing; the deviations the adapter
could not realise; the sounds changed against the legacy lines (how many, the largest move).
--dry-run writes nothing. --report FILE writes every line's before and after as JSON.

It refuses the native packs and the template packs (reader "module": their modules speak for
themselves, R21e) and a pack that is not read by eSpeak NG. Nothing under languages/ is written;
`build_packs.py build` compiles a pack, and only a release puts it into languages/.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import packlib as L  # noqa: E402
import master as M  # noqa: E402
import tomlio  # noqa: E402

FRONTEND = os.path.join(ROOT, 'dist', 'x64', 'OpenEvvFrontend.exe')
FE_DATA = os.path.join(ROOT, 'dist', 'espeak-ng-data')
PHSOURCE = os.path.join(ROOT, 'build_frontend_x64', 'espeak-ng-build', 'phsource')
BLOCK = '# ---- the master path: written by engine/packs/to_master.py; run it again rather than editing ----'


def dump_tables(frontend=FRONTEND, data=FE_DATA):
    r = subprocess.run([frontend, '--data', data, '--dump-phonemes'], capture_output=True, check=True)
    return {t['table']: {p['mnemonic']: p for p in t['phonemes']} for t in json.loads(r.stdout.decode('utf-8'))}


def phsource_features(folder):
    """{table: {phoneme: (ipa line or None, set of feature words)}} from eSpeak NG's phoneme sources;
    {} when they are not there (the reading below is then not made, and the report says so)."""
    top = os.path.join(folder, 'phonemes')
    if not os.path.isfile(top):
        return {}
    files, table = {}, None
    for line in open(top, encoding='utf-8', errors='replace'):
        w = line.split('//')[0].split()
        if len(w) >= 2 and w[0] == 'phonemetable':
            table = w[1]
        elif len(w) >= 2 and w[0] == 'include' and table:
            files.setdefault(w[1], table)
    out = {}
    for fn, table in files.items():
        path = os.path.join(folder, fn)
        if not os.path.isfile(path):
            continue
        cur, ipa, feats = None, None, set()
        for line in open(path, encoding='utf-8', errors='replace'):
            w = line.split('//')[0].split()
            if not w:
                continue
            if w[0] == 'phoneme' and len(w) > 1:
                cur, ipa, feats = w[1], None, set()
            elif w[0] == 'endphoneme' and cur:
                out.setdefault(table, {})[cur] = (ipa, feats)
                cur = None
            elif cur and w[0] == 'ipa' and len(w) > 1:
                ipa = w[1]
            elif cur and w[0].islower() and all(re.fullmatch(r'[a-z]{3}', x) for x in w):
                feats |= set(w)
    return out


# Readings the human chose (HUMAN_ANSWERS.md, 2026-10-11, Q54): eSpeak NG gives Abkhaz p_ and t_ no IPA of
# their own (they import plain unaspirated stops), and the pattern of its names makes them the ejectives of
# k_ c_ C_ E_; read as ejectives, a recorded guess for a native reviewer to confirm
HUMAN_READINGS = {'@ab:p_': ('pʼ', 'the human\'s answer to Q54 (2026-10-11): read as the ejective pʼ, a recorded guess; '
                                   'eSpeak NG gives p_ no IPA of its own'),
                  '@ab:t_': ('tʼ', 'the human\'s answer to Q54 (2026-10-11): read as the ejective tʼ, a recorded guess; '
                                   'eSpeak NG gives t_ no IPA of its own')}


def master_block(flat, tables, phs):
    """-> {ipa, kind, reading} for every eSpeak NG phoneme the pack's sound map names."""
    ipa, kind, reading = {}, {}, {}
    for x in flat.get('sounds', {}).get('line', []):
        if x['kind'] != 'map' or not x['name'].startswith('@'):
            continue
        tn, mn = x['name'][1:].split(':', 1)
        ph = tables.get(tn, {}).get(mn)
        if ph is None:
            raise L.PackError('pack %r: %s is not in eSpeak NG\'s phoneme table %s' % (flat['pack']['tag'], x['name'], tn))
        ipa[x['name']] = ph['ipa']
        kind[x['name']] = 'v' if ph['type'] == 2 else 'c'
        src = phs.get(tn, {}).get(mn)
        if x['name'] in HUMAN_READINGS:
            ipa[x['name']], reading[x['name']] = HUMAN_READINGS[x['name']]
        elif src and 'ejc' in src[1] and M.EJECTIVE not in ph['ipa']:
            ipa[x['name']] = ph['ipa'] + M.EJECTIVE
            reading[x['name']] = ('eSpeak NG\'s phoneme file gives %s:%s the feature ejc (ejective) and the IPA %s: '
                                  'read %s' % (tn, mn, ph['ipa'], ipa[x['name']]))
    return dict(ipa=ipa, kind=kind, reading=reading)


def block_text(m, today):
    out = ['', BLOCK, '[master]', 'note = %s' % tomlio._str('switched to the IPA master table\'s sounds on %s (Phase 11, '
                                                             'playbook R21); realization = "legacy" goes back' % today)]
    for sec in ('ipa', 'kind', 'reading', 'fallback'):
        d = m.get(sec) or {}
        out += ['', '[master.%s]' % sec]
        out += ['%s = %s' % (tomlio._key(k), tomlio._str(v)) for k, v in sorted(d.items())]
    return '\n'.join(out) + '\n'


def rewrite(text, m, today):
    """The pack file with realization = "master" and the master block (replacing an earlier one)."""
    eol = '\r\n' if '\r\n' in text else '\n'
    text = text.replace('\r\n', '\n')
    if BLOCK in text:
        text = text[:text.index(BLOCK)].rstrip('\n') + '\n'
    if re.search(r'(?m)^realization = "[a-z]+"$', text):
        text = re.sub(r'(?m)^realization = "[a-z]+"$', 'realization = "master"', text, count=1)
    elif re.search(r'(?m)^\[engine\]$', text):
        text = re.sub(r'(?m)^\[engine\]$', '[engine]\nrealization = "master"', text, count=1)
    else:
        text = text.rstrip('\n') + '\n\n[engine]\nrealization = "master"\n'
    text = text.rstrip('\n') + '\n' + block_text(m, today)
    return text.replace('\n', eol)


def _keys(to, sounds):
    parts = []
    for w in to.split():
        phone, _, sid = w.partition('=')
        parts.append((phone, dict(sounds.get(sid, {})) if sid else {}))
    return parts


def compare(flat_legacy, flat_master, rows, template):
    """How the master lines differ from the legacy ones: (changed, carriers changed, largest move)."""
    import adapter as A
    ch = A.chassis(template)
    ls = {x['id']: x['keys'] for x in flat_legacy['sounds']['line'] if x['kind'] == 'sound'}
    ms = {x['id']: x['keys'] for x in flat_master['sounds']['line'] if x['kind'] == 'sound'}
    changed = carriers = 0
    big = (0.0, '')
    for r in rows:
        if r['kind'] in ('legacy-fallback', 'kept-apart', 'silent'):
            continue
        a, b = _keys(r['legacy'], ls), _keys(r['to'], ms)
        if [(p, {k: str(v) for k, v in d.items()}) for p, d in a] == [(p, {k: str(v) for k, v in d.items()}) for p, d in b]:
            continue
        changed += 1
        if [p for p, _ in a] != [p for p, _ in b]:
            carriers += 1
            continue
        for (p, ka), (_, kb) in zip(a, b):
            if p not in ch or 'f' not in ch[p]:
                continue
            for i in range(3):
                k = 'f%d' % (i + 1)
                ha = ch[p]['f'][i] * float(ka.get(k, 100)) / 100.0
                hb = ch[p]['f'][i] * float(kb.get(k, 100)) / 100.0
                d = 100.0 * (hb - ha) / ha
                if abs(d) > abs(big[0]):
                    big = (d, '%s F%d %d -> %d Hz on %s (%s)' % (r['key'], i + 1, ha, hb, p, r['ipa']))
    return changed, carriers, big


def convert(tag, tables, phs, faults, today, out=None, dry=False):
    d = L.read_pack(tag)
    flat, _ = L.resolve(tag)
    eng = flat.get('engine', {})
    if eng.get('reader') == 'module' or eng.get('realization') == 'module':
        what = 'template' if flat['ini'].get('Language', {}).get('Hidden') == '1' else 'native'
        raise L.PackError('pack %r is a %s pack (reader "module"): its module speaks for itself; refused (R21e)' % (tag, what))
    if not eng.get('reader', '').startswith('espeak:'):
        raise L.PackError('pack %r is not read by eSpeak NG (reader %r): refused' % (tag, eng.get('reader')))
    m = master_block(flat, tables, phs)
    # the fallbacks: those the pack has, and those found since (--faults)
    fb = dict((flat.get('master') or {}).get('fallback') or {})
    fb.update(faults.get(tag, {}))
    m['fallback'] = fb
    # only what the chain does not already say (a dialect of a switched parent writes its own lines)
    inherited = {}
    if d['pack'].get('extends'):
        pflat, _ = L.resolve(d['pack']['extends'])
        inherited = pflat.get('master') or {}
    own = {k: {kk: vv for kk, vv in v.items() if (inherited.get(k) or {}).get(kk) != vv} for k, v in m.items()}
    mflat = dict(flat, engine=dict(eng, realization='master'), master=m)
    files = L.compile_pack(mflat)              # the whole build, overrides included: it must compile
    built, rep = M.realize(dict(mflat, override={}))
    lflat = flat
    if lflat.get('override'):
        import copy
        import overrides as O
        lflat = copy.deepcopy(flat)
        O.realize(lflat)
    changed, carriers, big = compare(lflat, built, rep['rows'], rep['template'])
    rep.update(changed=changed, carriers_changed=carriers, largest=big, files={k: len(v) for k, v in files.items()},
               no_phsource=not phs, readings=m['reading'])
    if not dry:
        src = L.pack_path(tag)
        text = open(src, encoding='utf-8', newline='').read()
        new = rewrite(text, own, today)
        if out:
            for t in [x['pack']['tag'] for x in L.chain_of(tag)][:-1]:
                dst = os.path.join(out, t, 'pack.toml')
                if not os.path.exists(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(L.pack_path(t), dst)
            dst = os.path.join(out, tag, 'pack.toml')
            os.makedirs(os.path.dirname(dst), exist_ok=True)
        else:
            dst = src
        with open(dst, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
        # what was written compiles to what was reported
        again = L.compile_pack(L.resolve(tag, out)[0] if out else L.resolve(tag)[0])
        if again != files:
            raise L.PackError('pack %r: the file written does not build to what was computed' % tag)
        rep['written'] = dst
    return rep


def summary(rep):
    c = rep['counts']
    fb = [r for r in rep['rows'] if r['kind'] in ('legacy-fallback', 'kept-apart')]
    dev = [r for r in rep['rows'] if r.get('deviations')]
    lines = ['%s (%s): table %d, composed %d, created %d, fallback %d, kept apart %d, said as nothing %d; '
             '%d sound lines (%d legacy lines kept)' % (
                 rep['tag'], rep['template'], c.get('table', 0), c.get('composed', 0), c.get('created', 0),
                 c.get('legacy-fallback', 0), c.get('kept-apart', 0), c.get('silent', 0), rep['sounds'],
                 rep['legacy_sounds_kept']),
             '    changed against the legacy lines: %d of %d (carrier changed %d); largest formant move %s' % (
                 rep['changed'], len(rep['rows']), rep['carriers_changed'],
                 ('%+.0f%%: %s' % rep['largest']) if rep['largest'][1] else 'none'),
             '    lines with a deviation the adapter could not realise: %d; readings: %d%s; problems: %d' % (
                 len(dev), len(rep['readings']) + sum(1 for r in rep['rows'] if r.get('readings')),
                 ' (eSpeak NG\'s phoneme sources not found: the ejc reading not made)' if rep['no_phsource'] else '',
                 len(rep['problems']))]
    for r in fb:
        lines.append('    %s %s: %s' % (r['kind'], r['key'], r['why']))
    for p in rep['problems']:
        lines.append('    PROBLEM %s' % p)
    return '\n'.join(lines)


def check(root=None):
    """Every pack at realization = "master" (packs/, the EVV_PACKS_EXTRA folders, or a scratch root)
    builds, and none of its phonemes is said as nothing unless its IPA holds no sound."""
    folders = [root] if root else [None] + L.extra_dirs()
    n, bad = 0, []
    for folder in folders:
        tags = L.list_tags(folder) if folder is None or os.path.isdir(folder) else []
        for tag in tags:
            try:
                # a pack of an EVV_PACKS_EXTRA folder may extend one of packs/: found through the normal
                # search; a scratch --root holds its chain itself (to_master.py --out copies it)
                flat, _ = L.resolve(tag, root)
                if flat.get('engine', {}).get('realization') != 'master':
                    continue
                n += 1
                L.compile_pack(flat)
                _, rep = M.realize(flat)
            except (L.PackError, M.MasterError) as e:
                bad.append('%s: %s' % (tag, e))
                continue
            for r in rep['rows']:
                if r['key'].startswith('@') and r['to'].strip() in ('', '-') and r['kind'] != 'silent':
                    bad.append('%s: %s (%s) is said as nothing' % (tag, r['key'], r.get('ipa') or r.get('why')))
            bad += ['%s: %s' % (tag, p) for p in rep['problems']]
    for b in bad:
        print('FAIL', b)
    print('master check: %d packs at realization "master"; %s' % (
        n, 'every one builds, no phoneme silent' if not bad else '%d FAILED' % len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('tags', nargs='*')
    ap.add_argument('--all', action='store_true', help='every pack read by eSpeak NG')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', help='write scratch copies here, not into packs/')
    ap.add_argument('--faults', help='JSON {tag: {phoneme: reason}}: phonemes to keep on their legacy line')
    ap.add_argument('--report', help='write every line\'s before and after here (JSON)')
    ap.add_argument('--frontend', default=FRONTEND)
    ap.add_argument('--phsource', default=PHSOURCE)
    ap.add_argument('--check', action='store_true', help='build every master pack (of packs/, or of --root); '
                    'none may have a silent phoneme')
    ap.add_argument('--root', help='with --check: a scratch pack root (to_master.py --out)')
    a = ap.parse_args(argv)
    if a.check:
        return check(a.root)
    tags = a.tags
    if a.all:
        tags = [t for t in L.list_tags() if L.resolve(t)[0].get('engine', {}).get('reader', '').startswith('espeak:')]
    if not tags:
        ap.error('name the packs, or --all')
    if a.out and os.path.normcase(os.path.realpath(a.out)).startswith(os.path.normcase(os.path.realpath(os.path.join(ROOT, 'languages')))):
        ap.error('--out is a scratch pack root, never languages/')
    tables = dump_tables(a.frontend)
    phs = phsource_features(a.phsource)
    faults = json.load(open(a.faults, encoding='utf-8')) if a.faults else {}
    today = datetime.date.today().isoformat()
    reports, bad = [], 0
    for tag in tags:
        try:
            rep = convert(tag, tables, phs, faults, today, a.out, a.dry_run)
        except (L.PackError, M.MasterError) as e:
            print('REFUSED %s' % e)
            bad += 1
            continue
        print(summary(rep))
        reports.append(rep)
    tot = {}
    for r in reports:
        for k, v in r['counts'].items():
            tot[k] = tot.get(k, 0) + v
    print('to_master: %d packs%s: table %d, composed %d, created %d, fallback %d, kept apart %d, said as nothing %d; '
          'problems %d; refused %d' % (len(reports), ' (dry run, nothing written)' if a.dry_run else '',
                                       tot.get('table', 0), tot.get('composed', 0), tot.get('created', 0),
                                       tot.get('legacy-fallback', 0), tot.get('kept-apart', 0), tot.get('silent', 0),
                                       sum(len(r['problems']) for r in reports), bad))
    if a.report:
        with open(a.report, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=1, default=str)
    return 1 if bad and not reports else 0


if __name__ == '__main__':
    sys.exit(main())
