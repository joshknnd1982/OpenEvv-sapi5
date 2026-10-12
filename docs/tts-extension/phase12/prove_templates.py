# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 12: table entries proved on every template, not only on dedx (Q52, Q53, Q55; D97).

    python docs/tts-extension/phase12/prove_templates.py <ids ...> [--templates engx,esex,...] [--save-trims]

For each template, the sweep (engine/ipa/sweep.py: A0 A1 A2 B3 B2, the design loop of up to five
rounds) says the entries with the template's first pack's header lines (PACK below), under
EVV_STAGE. The proofs go to ipa/proofs/templates/<template>/<id>.json, so the reference proofs
(ipa/proofs/<id>.json, dedx, the doctor's "proof against map") are left as they are; dedx itself
is proved by the ordinary sweep. An entry's contrast partners are said with it, so that its B2
compares sounds of the same template. With --save-trims a correction that brought an entry within
its targets on a template is written as `trim.<template>` (tagged measured, its proof named), the
sweep's own rule; nothing else of the table is touched (no state, level or proof line: those are
the reference template's).
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'ipa'))
import sweep as SW  # noqa: E402
import table as T  # noqa: E402

# the first pack of each template in the staged golden (adapter.VOICE_F5's list, D87)
PACK = {'dedx': 'hi', 'engx': 'cy', 'enux': 'chr', 'esex': 'an', 'esux': 'gn', 'frfx': 'fr-be', 'itix': 'bn'}


def with_partners(t, ids):
    out = list(ids)
    for sid in ids:
        for c in (t.sounds[sid].get('tests') or {}).get('contrast', []):
            if c['with'] not in out:
                out.append(c['with'])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='+')
    ap.add_argument('--templates', default='engx,enux,esex,esux,frfx,itix')
    ap.add_argument('--save-trims', action='store_true')
    a = ap.parse_args()
    if not SW.E.STAGE:
        raise SystemExit('set EVV_STAGE')
    total = dict(n=0, passed=0)
    for template in a.templates.split(','):
        t = T.load()
        ids = with_partners(t, SW.select(t, a.ids))
        SW.PROOFS = os.path.join(ROOT, 'ipa', 'proofs', 'templates', template)
        res = SW.run(t, ids, template, PACK[template], apply=False)
        if a.save_trims:
            SW.save_trims(t, {k: v for k, v in res.items() if v.get('passed') and k in SW.select(t, a.ids)}, template)
            for name in sorted(set(t.where[k] for k, v in res.items() if v.get('passed') and v.get('trims'))):
                path = os.path.join(T.IPA, 'table', name)
                with open(path, encoding='utf-8') as f:
                    text = f.read()
                text = re.sub(r'(?m)^(trim\.%s = .*)$' % template,
                              lambda m: re.sub(r'proof = "ipa/proofs/(?!templates/)',
                                               'proof = "ipa/proofs/templates/%s/' % template, m.group(1)),
                              text)
                with open(path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(text)
        asked = SW.select(t, a.ids)
        for sid in ids:
            # a partner is said so that the entries asked for compare with it; its own contrasts name
            # partners not said here, so it is shown and not counted
            print('%-5s %s%s' % (template, SW.fmt(res[sid]), '' if sid in asked else '  (partner, not counted)'), flush=True)
        done = sum(1 for sid in asked if res[sid].get('passed'))
        print('%s: %d entries, %d passed every check, %d not yet (and %d partners said beside them); proofs in '
              'ipa/proofs/templates/%s/' % (template, len(asked), done, len(asked) - done, len(ids) - len(asked), template),
              flush=True)
        total['n'] += len(asked)
        total['passed'] += done
    print('prove_templates: %d entries over %d templates, %d passed every check, %d not yet' % (
        total['n'], len(a.templates.split(',')), total['passed'], total['n'] - total['passed']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
