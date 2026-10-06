"""Coverage of the IPA chart by the master table (DESIGN.md 1 and 3.1). MIT licence.

    python engine/ipa/coverage.py

Every symbol of the checklist (docs/tts-extension/inventory/IPA_CHECKLIST.json) must have an entry
of its own, under the same id, and the table may hold nothing the checklist lacks unless it is
marked tier B or C. Prints the states by section; exit 1 if a checklist symbol has no entry or an
entry has no checklist symbol. The project is complete only when every checklist entry is
`mapped`, `composed` or `created` (R19e); MISSING is the start, BLOCKED is reported at the top.
"""

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import table as T  # noqa: E402

CHECKLIST = os.path.join(T.ROOT, 'docs', 'tts-extension', 'inventory', 'IPA_CHECKLIST.json')
DONE = ('mapped', 'composed', 'created')


def main():
    t = T.load()
    with open(CHECKLIST, encoding='utf-8') as f:
        checklist = {e['id']: e for e in json.load(f)['symbols']}
    missing = sorted(set(checklist) - set(t.sounds))
    extra = sorted(i for i in set(t.sounds) - set(checklist) if t.sounds[i].get('tier', 'A') == 'A')
    by = collections.defaultdict(collections.Counter)
    for sid in checklist:
        e = t.sounds.get(sid)
        by[checklist[sid]['section']][e.get('state') if e else 'no entry'] += 1
    blocked = sorted(i for i, e in t.sounds.items() if e.get('state') == 'BLOCKED')
    if blocked:
        print('BLOCKED: %s' % ', '.join('%s %s' % (i, t.sounds[i]['ipa']) for i in blocked))
    states = ['mapped', 'composed', 'created', 'MISSING', 'BLOCKED', 'no entry']
    print('%-16s %s %6s' % ('section', ' '.join('%9s' % s for s in states), 'all'))
    total = collections.Counter()
    for sec, c in by.items():
        total.update(c)
        print('%-16s %s %6d' % (sec, ' '.join('%9d' % c[s] for s in states), sum(c.values())))
    print('%-16s %s %6d' % ('all', ' '.join('%9d' % total[s] for s in states), sum(total.values())))
    done = sum(total[s] for s in DONE)
    print('coverage: %d of %d checklist entries done (%s); %d without an entry; %d entries not on the checklist'
          % (done, len(checklist), '/'.join(DONE), len(missing), len(extra)))
    for i in missing:
        print('  no entry: %s %s' % (i, checklist[i]['symbol']))
    for i in extra:
        print('  not on the checklist: %s %s' % (i, t.sounds[i]['ipa']))
    return 1 if missing or extra else 0


if __name__ == '__main__':
    sys.exit(main())
