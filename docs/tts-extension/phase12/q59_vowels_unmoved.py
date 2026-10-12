# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""A master sounds.map whose vowel phonemes keep the table's line but without the move toward the cardinal
formants (f1..f4) and its level hold (av, ah): the template's own vowel, the table's other keys kept."""
import sys, re
sys.path.insert(0, 'engine/packs')
import packlib as L
tag, master_map, out = sys.argv[1:4]
import os
# the switched pack (its [master.kind]); packs/ holds 1.3.0's after Q59: P12_PACK_ROOT names the switched copy
kinds = (L.resolve(tag, os.environ.get('P12_PACK_ROOT'))[0].get('master') or {}).get('kind') or {}
lines = open(master_map, encoding='utf-8').read().split('\n')
snd = {}
for l in lines:
    m = re.match(r'sound (m\d+) (.*?)(\s+#.*)?$', l)
    if m:
        snd[m.group(1)] = m.group(2).split()
new, made, n = [], {}, 0
def strip(sid):
    keys = [k for k in snd[sid] if not re.match(r'(f[1-4]|av|ah)=', k)]
    if sid not in made:
        made[sid] = 'v%s' % sid[1:]
    return made[sid], keys
res = []
for l in lines:
    w = l.split()
    if w and w[0] in kinds and kinds[w[0]] == 'v' and len(w) > 1:
        parts = []
        for p in w[1:]:
            if p.startswith('#'):
                break
            if '=' in p and p.split('=', 1)[1] in snd:
                ph, sid = p.split('=', 1)
                vid, keys = strip(sid)
                parts.append('%s=%s' % (ph, vid) if keys else ph)
            else:
                parts.append(p)
        rest = l[l.index('#'):] if '#' in l else ''
        res.append('%-16s %s %s' % (w[0], ' '.join(parts), rest)); n += 1
    else:
        res.append(l)
i = max(i for i, l in enumerate(res) if l.startswith('sound m'))
extra = ['sound %s %s' % (vid, ' '.join(strip(sid)[1])) for sid, vid in made.items() if strip(sid)[1]]
res = res[:i + 1] + extra + res[i + 1:]
open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(res))
print('%d vowel phonemes on their template vowel (no cardinal move)' % n)
