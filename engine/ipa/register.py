"""The register of created sounds (CREATED_SOUNDS.md; playbook 1.6 step 7; DESIGN.md 5). MIT licence.

    python engine/ipa/register.py

Every entry of the master table whose state is `created` gets a line in the register: its key (the
code points), a register number CS-0001 onward, given once and never reused or renumbered, and a
summary drawn from the entry (why no module phone was enough, where its specification is, the
provenance of its values, its proof, its status). Numbers already in the register are kept; a
sound that is no longer `created` keeps its line, marked as no longer created. Only the register
table in CREATED_SOUNDS.md is rewritten; the text above it is left as it is.
"""

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import table as T  # noqa: E402

PATH = os.path.join(T.ROOT, 'docs', 'tts-extension', 'CREATED_SOUNDS.md')
HEAD = '| Register no. | Key | Symbol | Code points | Why existing sounds were not enough | Specification (master-table entry) | Provenance | Test and proof files | Status | Revision | Open questions |'


def tags(node, out):
    if isinstance(node, dict):
        if 'tag' in node:
            out[node['tag']] += 1
        else:
            for v in node.values():
                tags(v, out)
    elif isinstance(node, list):
        for v in node:
            tags(v, out)
    return out


def main():
    t = T.load()
    with open(PATH, encoding='utf-8') as f:
        text = f.read()
    a = text.index(HEAD)
    rows = text[a:].split('\n')[2:]
    known = {}
    for r in rows:
        m = re.match(r'\| (CS-\d{4}) \| (\S+) \|', r)
        if m:
            known[m.group(2)] = m.group(1)
    nxt = max([int(n[3:]) for n in known.values()] or [0]) + 1
    out = [HEAD, '|' + '---|' * 11]
    created = sorted(i for i, e in t.sounds.items() if e.get('state') == 'created')
    for sid in sorted(set(created) | set(known), key=lambda i: known.get(i, 'CS-9999') + i):
        e = t.sounds.get(sid)
        if sid not in known:
            known[sid] = 'CS-%04d' % nxt
            nxt += 1
        if e is None or e.get('state') != 'created':
            out.append('| %s | %s | %s | | no longer created (now %s) | | | | | | |' % (
                known[sid], sid, e['ipa'] if e else '', e.get('state') if e else 'removed'))
            continue
        ov = ((e.get('realization') or {}).get('openevv') or {})
        pf = os.path.join(T.ROOT, (e.get('tests') or {}).get('proof') or 'none')
        if not ov.get('carrier') and os.path.exists(pf):
            with open(pf, encoding='utf-8') as f:
                ov = dict(ov, carrier=json.load(f).get('said_as', {}).get('carrier'))
        why ='none of the seven IBM modules read for the checklist has %s as a phone of its own (DESIGN.md 4.1); ' \
              'said on the reference template as `%s` moved by its specification' % (e['ipa'], ov.get('carrier') or 'its nearest phone')
        prov = ', '.join('%s %d' % kv for kv in sorted(tags(e.get('spec') or {}, collections.Counter()).items()))
        proof = (e.get('tests') or {}).get('proof') or ''
        status = 'level %s%s' % (e.get('level'), ', approximate: ' + e['deviation'] if e.get('approximate') else '')
        est = tags(e.get('spec') or {}, collections.Counter()).get('estimated', 0)
        out.append('| %s | %s | %s | %s | %s | `ipa/table/%s` [sound."%s"] | %s | `%s` | %s | %d | %s |' % (
            known[sid], sid, e['ipa'], ' '.join(e['codepoints']), why, t.where[sid], sid, prov or '-', proof, status,
            1 + len(((e.get('realization') or {}).get('openevv') or {}).get('trim', {})),
            '%d estimated value(s) queued (OPEN_QUESTIONS.md)' % est if est else '-'))
    text = text[:a] + '\n'.join(out) + '\n'
    with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('register: %d created sounds, %d lines' % (len(created), len(out) - 2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
