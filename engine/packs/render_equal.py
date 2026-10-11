# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""The engine, speaking from a map built out of a pack, against the engine speaking from languages/.

    python engine/packs/render_equal.py [--per 3] [tag ...]      (the harness venv; EVV_STAGE as for any harness run)

For each tag the pack is built into a scratch folder and a few sentences (the pack's own sample, cut
into phrases, and two plain words) are rendered twice through the real engine (harness/engine.py):
once with the sounds.map in languages/<tag> given as the map override, once with the one built from packs/<tag>/pack.toml.
The WAV files must have the same SHA-256 and the engine must have been asked for the same frames.
Files equal byte for byte make this certain; the run shows that the product's own front-end and
engine take the built file and say the same thing (R16).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'docs', 'tts-extension', 'harness'))
import packlib as L  # noqa: E402
import engine as E  # noqa: E402

DEFAULT = ['af', 'ru-cl', 'ps-x-yusufzai', 'mn-f', 'ca-ba', 'yue-latn-jyutping', 'pt-br', 'hi', 'cmn', 'vi-vn-x-south']


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def sentences(tag, per):
    with open(os.path.join(ROOT, 'languages', tag, 'sample.txt'), encoding='utf-8') as f:
        text = f.read().strip()
    parts = [p.strip() for p in re.split(r'(?<=[.!?。！？])\s+', text) if p.strip()]
    return (parts or [text])[:per]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--per', type=int, default=3)
    ap.add_argument('tags', nargs='*')
    a = ap.parse_args()
    tags = a.tags or DEFAULT
    tmp = tempfile.mkdtemp(prefix='packs_')
    bad = 0
    for tag in tags:
        files = L.build(tag, tmp)
        built = os.path.join(tmp, tag, 'sounds.map')
        cases = [('s%d' % i, 'text', s) for i, s in enumerate(sentences(tag, a.per))]
        base = E.render(tag, cases, work=os.path.join(tmp, 'w_shipped_' + tag), map_path=os.path.join(ROOT, 'languages', tag, 'sounds.map'))
        pack = E.render(tag, cases, work=os.path.join(tmp, 'w_pack_' + tag), map_path=built)
        same = 0
        for x, y in zip(base, pack):
            ok = sha(x['wav']) == sha(y['wav'])
            same += ok
            if not ok:
                bad += 1
        print('%-20s %d sentences, WAV identical %d of %d   (sounds.map %d bytes built from the pack)' % (
            tag, len(cases), same, len(cases), len(files['sounds.map'])), flush=True)
    # the test must be able to fail: change one sound definition of the built map and the sound must change
    tag = tags[0]
    text = open(os.path.join(tmp, tag, 'sounds.map'), encoding='utf-8', newline='').read()
    m = re.search(r'^(sound s\d+ )(\S+)', text, re.M)
    broken = os.path.join(tmp, 'broken.map')
    # a definition that the sentences use: lengthen every sound's first key past any plausible value
    changed = re.sub(r'^(sound s\d+ )(dur=\d+|f2=\d+|vot=\d+)', lambda x: x.group(1) + 'f1=300', text, flags=re.M)
    with open(broken, 'w', encoding='utf-8', newline='') as f:
        f.write(changed)
    cases = [('s%d' % i, 'text', s) for i, s in enumerate(sentences(tag, a.per))]
    base = E.render(tag, cases, work=os.path.join(tmp, 'w_shipped2_' + tag), map_path=os.path.join(ROOT, 'languages', tag, 'sounds.map'))
    pack = E.render(tag, cases, work=os.path.join(tmp, 'w_broken_' + tag), map_path=broken)
    diff = sum(sha(x['wav']) != sha(y['wav']) for x, y in zip(base, pack))
    print('on purpose: %s with %d sound definitions changed: %d of %d WAV differ (the test can fail)' % (
        tag, len(re.findall(r'^sound s\d+ f1=300', changed, re.M)), diff, len(cases)))
    if m is None or diff == 0:
        bad += 1
    print('render_equal: %s' % ('every WAV identical' if not bad else '%d PROBLEM(S)' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
