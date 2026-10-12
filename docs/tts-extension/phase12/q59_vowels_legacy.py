# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Write a sounds.map that says the phonemes of one kind (v or c) with their legacy lines, the rest master."""
import sys, re
sys.path.insert(0, 'engine/packs')
import packlib as L
tag, kind, legacy_map, master_map, out = sys.argv[1:6]
import os
# the switched pack (its [master.kind]); packs/ holds 1.3.0's after Q59: P12_PACK_ROOT names the switched copy
kinds = (L.resolve(tag, os.environ.get('P12_PACK_ROOT'))[0].get('master') or {}).get('kind') or {}
leg = open(legacy_map, encoding='utf-8').read().split('\n')
mas = open(master_map, encoding='utf-8').read().split('\n')
legmap = {l.split()[0]: l for l in leg if l.startswith('@') or (l and not l.startswith(('sound', '#', ' ')) and len(l.split()) > 1 and l.split()[0] in kinds)}
legsounds = [l for l in leg if l.startswith('sound s')]
res, n = [], 0
for l in mas:
    w = l.split()
    if w and w[0] in kinds and kinds[w[0]] == kind and w[0] in legmap:
        res.append(legmap[w[0]]); n += 1
    else:
        res.append(l)
i = max(i for i, l in enumerate(res) if l.startswith('sound m'))
res = res[:i + 1] + legsounds + res[i + 1:]
open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(res))
print('%d %s phonemes on their legacy lines' % (n, kind))
