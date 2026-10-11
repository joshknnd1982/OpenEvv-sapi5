# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 11's pilot: a few packs switched to the master path in a scratch stage, recorded, checked, compared.

    python docs/tts-extension/phase11/pilot.py <scratch folder> <tag ...> [--legacy] [--no-asr]

In <scratch folder> (outside the repository; nothing in languages/, dist/ or the goldens is written):
    packs/      to_master.py --out: the master copies (and the packs they extend)
    stage/      build_packs.py build --root packs: stage/languages/<tag>/, read before languages/ (EVV_STAGE)
    golden/     golden.py --record of the master build;   work/  the harness's scratch (EVV_HARNESS_WORK)
    faults.json the phonemes check A found at fault, fed back to to_master.py as legacy-fallback
    after_<tag>.json, before_<tag>.json   check_language.py --json, master and legacy (--legacy runs the
                legacy side: the shipped packs against harness/golden/, the golden of what ships)

Rounds: build, record, check A; a phoneme check A finds silent or swapped goes into faults.json with
the reason and the pack is built again (at most three rounds). Every command's output is printed (R16).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
HARNESS = os.path.join(ROOT, 'docs', 'tts-extension', 'harness')
PY = sys.executable


def run(cmd, env=None):
    print('>', ' '.join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(r.stdout.rstrip(), flush=True)
    if r.returncode:
        print(r.stderr.rstrip(), flush=True)
        raise SystemExit('pilot: a command failed (exit %d)' % r.returncode)
    return r.stdout


def env_for(scratch, stage=True):
    env = dict(os.environ, PYTHONUTF8='1')
    env.pop('EVV_STAGE', None)
    if stage:
        env['EVV_STAGE'] = os.path.join(scratch, 'stage')
        env['EVV_HARNESS_WORK'] = os.path.join(scratch, 'work')
    else:
        env['EVV_HARNESS_WORK'] = os.path.join(scratch, 'work-legacy')
    return env


def faults_of(js, ipa_keys):
    """check A's problems -> {phoneme key: reason}: a phone sounded for another (A0), or one with no
    sound (A1). A formant or F0 measured off the frames' (A2) is not a fault of the phoneme's line: the
    fallback rule is silent, swapped, unrendered (playbook Phase 11 step 3)."""
    out = {}
    for p in js['a']['problems']:
        if ' sounded for ' not in p and 'has no sounding frame' not in p:
            continue
        case = p.split(':', 1)[0].split('|')
        mn = case[1] if len(case) > 1 else case[0]
        tn = case[2] if len(case) > 2 else None      # `s|?|en`: a phoneme of the en table
        keys = [k for k in ipa_keys if k.split(':', 1)[1] == mn and (tn is None or k[1:].split(':')[0] == tn)]
        for k in keys:
            out.setdefault(k, 'check A (Phase 11 pilot): %s' % p)
    return out


def main(argv):
    scratch = os.path.abspath(argv[0])
    tags = [a for a in argv[1:] if not a.startswith('--')]
    asr = [] if '--no-asr' in argv else ['--asr']
    for d in ('packs', 'stage', 'golden', 'work'):
        os.makedirs(os.path.join(scratch, d), exist_ok=True)
    faults_path = os.path.join(scratch, 'faults.json')
    faults = json.load(open(faults_path, encoding='utf-8')) if os.path.exists(faults_path) else {}
    if '--legacy' in argv:
        for tag in tags:
            run([PY, os.path.join(HARNESS, 'check_language.py'), tag, '--golden', os.path.join(HARNESS, 'golden'),
                 '--json', os.path.join(scratch, 'before_%s.json' % tag)] + asr, env_for(scratch, stage=False))
        return 0
    todo = list(tags)
    for rnd in range(1, 4):
        print('==== round %d: %s' % (rnd, ' '.join(todo)), flush=True)
        json.dump(faults, open(faults_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        run([PY, os.path.join(ROOT, 'engine', 'packs', 'to_master.py')] + todo +
            ['--out', os.path.join(scratch, 'packs'), '--faults', faults_path,
             '--report', os.path.join(scratch, 'to_master_round%d.json' % rnd)], env_for(scratch))
        run([PY, os.path.join(ROOT, 'engine', 'packs', 'build_packs.py'), 'build',
             os.path.join(scratch, 'stage', 'languages'), '--root', os.path.join(scratch, 'packs')] + todo, env_for(scratch))
        run([PY, os.path.join(HARNESS, 'golden.py'), '--record', '--golden', os.path.join(scratch, 'golden')] + todo,
            env_for(scratch))
        again = []
        for tag in todo:
            out = os.path.join(scratch, 'after_%s.json' % tag)
            run([PY, os.path.join(HARNESS, 'check_language.py'), tag, '--golden', os.path.join(scratch, 'golden'),
                 '--json', out], env_for(scratch))
            js = json.load(open(out, encoding='utf-8'))
            if not js['a']['passed']:
                sys.path.insert(0, os.path.join(ROOT, 'engine', 'packs'))
                import packlib as L
                keys = list((L.resolve(tag, os.path.join(scratch, 'packs'))[0].get('master') or {}).get('ipa', {}))
                new = {k: v for k, v in faults_of(js, keys).items() if k not in faults.get(tag, {})}
                if new:
                    faults.setdefault(tag, {}).update(new)
                    again.append(tag)
                    print('check A: %s: %d phonemes to legacy-fallback: %s' % (tag, len(new), ' '.join(sorted(new))), flush=True)
        if not again:
            break
        todo = again
    json.dump(faults, open(faults_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if asr:
        for tag in tags:
            run([PY, os.path.join(HARNESS, 'check_language.py'), tag, '--golden', os.path.join(scratch, 'golden'),
                 '--json', os.path.join(scratch, 'after_%s.json' % tag)] + asr, env_for(scratch))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
