# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 12 continued (Q59): which part of the master path makes the switched packs hard to understand.

    EVV_STAGE=<stage-ipa> P12_PACK_ROOT=<switched packs root> \
        python docs/tts-extension/phase12/ablate.py <out.json> --tags id ru ... --variants master legacy ...

Each variant is the switched pack's sounds.map (stage-ipa) with one family of keys taken out of the
lines that one kind of phoneme (vowel or consonant) uses, or with that kind on its legacy lines
(languages/<tag>/sounds.map, release 1.3.0). Each map goes into a scratch stage holding that pack alone,
whose host runs the front-end as the product does; the 8 standard sentences are said and Whisper hears them with asr.py's settings, in one
process. Nothing in the tree is written but <out.json>; the maps go to EVV_HARNESS_WORK.
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'packs'))
import asr  # noqa: E402
import engine as E  # noqa: E402
import packlib as L  # noqa: E402

FORMANT = r'f[1-4]'
LEVEL = r'a[vh]'
TIME = r'(hold|dur)'
LOCUS = r'(l[1-4]|lk|ant)'
NOISE = r'a[2-6]'
# variant: (kinds affected, regex of keys taken out) or 'legacy:<kinds>'
VARIANTS = {
    'master': ('', None),
    'legacy': ('legacy', 'vc'),
    'v_legacy': ('legacy', 'v'),
    'c_legacy': ('legacy', 'c'),
    'v_unmoved': ('v', FORMANT + '|' + LEVEL),
    'v_nolevel': ('v', LEVEL),
    'v_notime': ('v', TIME),
    'c_notime': ('c', TIME),
    'c_noformant': ('c', FORMANT + '|' + LEVEL),
    'c_nolocus': ('c', LOCUS),
    'c_nonoise': ('c', NOISE),
    'notime': ('vc', TIME),
    'v_unmoved_notime': ('vc', None),     # composite, below
    'bare': ('vc', r'.*'),               # every master line said as its carrier, no keys at all
}
COMPOSITE = {'v_unmoved_notime': [('v', FORMANT + '|' + LEVEL + '|' + TIME), ('c', TIME)]}


def kinds_of(tag):
    flat = L.resolve(tag, os.environ.get('P12_PACK_ROOT'))[0]
    return (flat.get('master') or {}).get('kind') or {}


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read().split('\n')


def strip_map(lines, kinds, rules):
    """rules: [(kinds 'v'/'c'/'vc', regex)]: in the lines naming a sound for a phoneme of those kinds,
    the keys matching the regex taken out (a new sound line, or the bare phone if nothing is left)."""
    snd = {}
    for l in lines:
        m = re.match(r'sound (\S+) (.*?)(\s+#.*)?$', l)
        if m:
            snd[m.group(1)] = m.group(2).split()
    made, extra, res = {}, [], []
    for l in lines:
        w = l.split()
        k = kinds.get(w[0]) if w else None
        rule = [rx for ks, rx in rules if k and k in ks]
        if not rule or len(w) < 2 or not w[0].startswith('@'):
            res.append(l)
            continue
        rx = '|'.join('(?:%s)' % r for r in rule)
        parts = []
        for p in w[1:]:
            if p.startswith('#'):
                break
            ph, _, sid = p.partition('=')
            if sid in snd:
                keys = [x for x in snd[sid] if not re.fullmatch('(?:%s)=-?\\d+' % rx, x)]
                if not keys:
                    parts.append(ph)
                    continue
                kt = ' '.join(keys)
                if kt not in made:
                    made[kt] = 'x%d' % (len(made) + 1)
                    extra.append('sound %s %s' % (made[kt], kt))
                parts.append('%s=%s' % (ph, made[kt]))
            else:
                parts.append(p)
        res.append('%-16s %s' % (w[0], ' '.join(parts)))
    i = max(i for i, l in enumerate(res) if l.startswith('sound '))
    return res[:i + 1] + extra + res[i + 1:]


def legacy_map(master, legacy, kinds, which):
    """The phonemes of the kinds in `which` on their legacy lines, with the legacy sound lines."""
    leg = {l.split()[0]: l for l in legacy if l.startswith('@') and len(l.split()) > 1}
    res = [leg.get(l.split()[0], l) if l.startswith('@') and kinds.get(l.split()[0]) in which else l for l in master]
    snd = [l.replace('sound s', 'sound s', 1) for l in legacy if l.startswith('sound s')]
    i = max(i for i, l in enumerate(res) if l.startswith('sound '))
    return res[:i + 1] + snd + res[i + 1:]


ORIG_STAGE = E.STAGE


def variant_map(tag, name, work):
    master = read(os.path.join(ORIG_STAGE, 'languages', tag, 'sounds.map'))
    kinds = kinds_of(tag)
    if name == 'master':
        lines = master
    elif VARIANTS[name][0] == 'legacy':
        lines = legacy_map(master, read(os.path.join(ROOT, 'languages', tag, 'sounds.map')), kinds, VARIANTS[name][1])
    elif name in COMPOSITE:
        lines = strip_map(master, kinds, COMPOSITE[name])
    else:
        lines = strip_map(master, kinds, [VARIANTS[name]])
    os.makedirs(work, exist_ok=True)
    path = os.path.join(work, '%s-%s.map' % (tag, name))
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--tags', nargs='+', required=True)
    ap.add_argument('--variants', nargs='+', default=list(VARIANTS))
    ap.add_argument('--maps', help='a folder of ready maps <tag>-<variant>.map (variants not in VARIANTS)')
    a = ap.parse_args()
    sentences = asr.load_json('sentences.json')['languages']
    codes = asr.load_json('whisper_codes.json')
    model, device = asr.whisper(False)
    out = {}
    if os.path.exists(a.out):
        with open(a.out, encoding='utf-8') as f:
            out = json.load(f)
    for tag in a.tags:
        sents = [s['text'] for s in sentences[tag]['sentences']][:8]
        code = codes[tag]['whisper']
        for v in a.variants:
            work = os.path.join(E.WORK, 'ablate', tag, v)
            if a.maps and os.path.exists(os.path.join(a.maps, '%s-%s.map' % (tag, v))):
                mp = os.path.join(a.maps, '%s-%s.map' % (tag, v))
            else:
                mp = variant_map(tag, v, work)
            # a scratch stage of this pack alone, its sounds.map the variant's: the host runs the front-end
            # itself, as the product does (a map handed to the front-end by the harness is another route)
            st = os.path.join(work, 'stage')
            dst = os.path.join(st, 'languages', tag)
            os.makedirs(dst, exist_ok=True)
            src = os.path.join(ORIG_STAGE, 'languages', tag)
            for fn in os.listdir(src):
                shutil.copyfile(mp if fn == 'sounds.map' else os.path.join(src, fn), os.path.join(dst, fn))
            E.STAGE, E._packs = st, None
            rs = E.render(tag, [('s%d' % i, 'text', s) for i, s in enumerate(sents)], work=os.path.join(work, 'r'))
            E.STAGE, E._packs = ORIG_STAGE, None
            hyps = []
            for r in rs:
                segs, _ = model.transcribe(r['wav'], language=code, beam_size=5, condition_on_previous_text=False,
                                           vad_filter=False, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                                           compression_ratio_threshold=2.4)
                hyps.append(' '.join(s.text.strip() for s in segs))
            cer, wer = asr.score(sents, hyps, tag)
            # a sentence Whisper loops on scores far above 1 and outweighs the rest: for comparing variants, each
            # sentence's CER capped at 1 and averaged (the reported figure stays asr.py's, `cer`)
            capped = sum(min(1.0, asr.score([x], [y], tag)[0]) for x, y in zip(sents, hyps)) / len(sents)
            out.setdefault(tag, {})[v] = dict(cer=cer, capped=round(capped, 4), hyps=hyps)
            print('%-10s %-18s CER %.3f  capped %.3f' % (tag, v, cer, capped), flush=True)
            with open(a.out, 'w', encoding='utf-8') as f:
                json.dump(out, f, ensure_ascii=False, indent=1)
    print('\n%-10s ' % 'tag' + ' '.join('%8s' % v[:8] for v in a.variants))
    for tag in a.tags:
        print('%-10s ' % tag + ' '.join('%8.3f' % out[tag][v]['cer'] for v in a.variants) + '   capped ' + ' '.join(
            '%6.3f' % out[tag][v].get('capped', -1) for v in a.variants))
    return 0


if __name__ == '__main__':
    sys.exit(main())
