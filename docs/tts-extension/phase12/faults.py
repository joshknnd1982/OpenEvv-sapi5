# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 12: the phonemes check A found at fault in the switched packs, for to_master.py --faults.

    python docs/tts-extension/phase12/faults.py <status.json> <faults.json>

Reads report.py's status.json (check A on golden-ipa/) and, for every pack at realization "master",
takes the problems that are faults of a phoneme's line by the Phase 11 rule (silent, swapped: A0, A1;
an A2 miss is not a fault): `<case>: ... sounded for ...` and `... has no sounding frame`. Each is mapped
to the pack's [master.ipa] keys (phase11/pilot.py's faults_of) and merged into faults.json
({tag: {key: reason}}), which to_master.py --faults writes into the pack as [master.fallback].
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'packs'))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'phase11'))
import packlib as L  # noqa: E402
import pilot  # noqa: E402


def main(argv):
    with open(argv[0], encoding='utf-8') as f:
        status = json.load(f)
    old = {}
    if os.path.exists(argv[1]):
        with open(argv[1], encoding='utf-8') as f:
            old = json.load(f)
    new_n = 0
    for r in status:
        if r.get('kind') != 'espeak':
            continue
        flat = L.resolve(r['tag'])[0]
        if (flat.get('engine') or {}).get('realization') != 'master':
            continue
        keys = list((flat.get('master') or {}).get('ipa', {}))
        found = pilot.faults_of({'a': r['a']}, keys)
        for k, why in found.items():
            if k not in old.get(r['tag'], {}):
                old.setdefault(r['tag'], {})[k] = why.replace('Phase 11 pilot', 'Phase 12, golden-ipa')
                new_n += 1
                print('%s %s: %s' % (r['tag'], k, why[:160]))
    with open(argv[1], 'w', encoding='utf-8', newline='\n') as f:
        json.dump(old, f, ensure_ascii=False, indent=1, sort_keys=True)
    print('faults: %d new, %d in all, in %d packs; written to %s' % (
        new_n, sum(len(v) for v in old.values()), len(old), argv[1]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
