# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Phase 12: docs/tts-extension/IPA_SWITCH_REPORT.md, one row a language, before and after the switch.

    python docs/tts-extension/phase12/switch_report.py <to_master report.json> [--after STATUS] [--out FILE]
                                                       [--previous STATUS] [--note FILE]

Before: phase12/before/status.json (report.py's record of 1.3.0's languages on the staged golden, the one
LANGUAGE_STATUS.md showed when Phase 12 began). After: harness/results/status.json as report.py wrote it
on golden-ipa/ (EVV_GOLDEN) with this phase's asr.py. The to_master report gives each pack's counts and
its fallbacks with their reasons (R21f). At the top, plainly: the languages whose CER rose by more than
0.10 (the note says what the human was shown of them and chose) and every level that dropped.
--previous STATUS adds a column with an earlier switch's CER (D97's, phase12/ipa_status.json); --note FILE is the
paragraph said under the title in place of D97's (the state of the switch when the report was written).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def a_text(r):
    a = r.get('a') or {}
    if not a:
        return '-'
    return '%s %d/%d%s%s' % ('pass' if a.get('passed') else 'FAIL', a.get('a2_ok', 0), a.get('a2_checks', 0),
                             ', %d substituted' % a['substituted'] if a.get('substituted') else '',
                             ', %d silent' % a['a1_silent'] if a.get('a1_silent') else '')


def b_text(r):
    b = r.get('b') or {}
    if not b or not b.get('checks'):
        return 'none'
    return '%s %d/%d' % ({True: 'pass', False: 'FAIL'}.get(b.get('passed'), 'too few'), b.get('in_range', 0),
                         b.get('checks', 0))


def cer(r):
    return ((r or {}).get('asr') or {}).get('cer')


def main(argv):
    rep = load(argv[0])
    after_path = argv[argv.index('--after') + 1] if '--after' in argv else os.path.join(DOCS, 'harness', 'results', 'status.json')
    out = argv[argv.index('--out') + 1] if '--out' in argv else os.path.join(DOCS, 'IPA_SWITCH_REPORT.md')
    before = {r['tag']: r for r in load(os.path.join(HERE, 'before', 'status.json'))}
    prev = {r['tag']: r for r in load(argv[argv.index('--previous') + 1])} if '--previous' in argv else None
    note = open(argv[argv.index('--note') + 1], encoding='utf-8').read().strip() if '--note' in argv else None
    after = {r['tag']: r for r in load(after_path)}
    packs = {p['tag']: p for p in (rep['packs'] if isinstance(rep, dict) and 'packs' in rep else rep)}
    rows, rose, dropped, fell, tot = [], [], [], [], {}
    for tag in sorted(packs):
        p = packs[tag]
        b, a = before.get(tag, {}), after.get(tag, {})
        for k, v in p['counts'].items():
            tot[k] = tot.get(k, 0) + v
        fb = [r for r in p['rows'] if r['kind'] == 'legacy-fallback']
        ka = [r for r in p['rows'] if r['kind'] == 'kept-apart']
        cb, ca = cer(b), cer(a)
        d = None if cb is None or ca is None else ca - cb
        if d is not None and d > 0.10:
            rose.append((tag, cb, ca, d))
        if d is not None and d < -0.02:
            fell.append((tag, cb, ca, d))
        lb, la = b.get('level'), a.get('level')
        if lb is not None and la is not None and la < lb:
            dropped.append((tag, lb, la))
        rows.append('| %s | %s | %s | %s | %s | %s | %s%s | %s | %s | %s | %s | %s |' % (
            tag, a.get('name') or b.get('name', ''), p['template'],
            '%d%s' % (len(fb), (': ' + ', '.join('`%s`' % r['key'] for r in fb)) if fb else ''),
            len(ka), '-' if cb is None else '%.3f' % cb,
            ('-' if cer(prev.get(tag)) is None else '%.3f' % cer(prev.get(tag))) + ' | ' if prev is not None else '',
            '-' if ca is None else '%.3f' % ca,
            '-' if d is None else '%+.3f' % d, a_text(b), a_text(a), '%s / %s' % (b_text(b), b_text(a)),
            '%s / %s' % (lb if lb is not None else '-', la if la is not None else '-')) +
            ' %s |' % (a.get('failure_layer') or '-'))
    scored = [r for r in rows]
    lines = ['# The switch to the IPA sounds (Phase 12)', '',
             'Every language, dialect and accent read by eSpeak NG (%d packs) was switched from the old sound generator to the IPA '
             'master table\'s sounds (`realization = "master"`, `engine/packs/to_master.py`; the human\'s order, D96, D97). The ten '
             'native languages and the seven templates were not touched. Before: release 1.3.0 as Phase 12 found it '
             '(`phase12/before/status.json`, the staged golden); after: the switched packs on the same modules (`golden-ipa/`, '
             'this phase\'s `asr.py`). Written by `docs/tts-extension/phase12/switch_report.py`; nothing here was judged by ear.'
             % len(packs), '',
             note or ('**Measured, not shipped.** Shown these numbers, the human chose to stop and investigate (Q59, 2026-10-11): '
             '`languages/`, `packs/`, `golden/` and `golden-staged/` stay as release 1.3.0 has them, and a new session finds '
             'and fixes the causes before the switch is measured again. The largest cause found so far is in the master path '
             'itself: a language\'s plain vowel said as the table\'s cardinal vowel (D97, Q59). The after-figures are '
             '`phase12/ipa_status.json` and `phase12/ipa_asr.json`.'), '',
             '## Plainly', '']
    lines.append('**Recognition worse by more than 0.10 CER (%d languages; what the human was shown of them, and chose, is said in the note above):** %s.' % (
        len(rose), ', '.join('%s %.3f -> %.3f' % (t, x, y) for t, x, y, _ in sorted(rose, key=lambda r: -r[3])) or 'none'))
    lines.append('')
    lines.append('**Levels that dropped (%d):** %s.' % (len(dropped), ', '.join('%s %d -> %d' % r for r in dropped) or 'none'))
    lines.append('')
    lines.append('**Recognition better by more than 0.02 CER (%d):** %s.' % (
        len(fell), ', '.join('%s %.3f -> %.3f' % (t, x, y) for t, x, y, _ in sorted(fell, key=lambda r: r[3])) or 'none'))
    lines.append('')
    ds = [(cer(after.get(t)) - cer(before.get(t))) for t in packs if cer(after.get(t)) is not None and cer(before.get(t)) is not None]
    if ds:
        ds.sort()
        med = (ds[(len(ds) - 1) // 2] + ds[len(ds) // 2]) / 2.0
        lines.append('**CER over the %d languages Whisper scores:** median change %+.3f, mean %+.3f; worse in %d, better in %d.' % (
            len(ds), med, sum(ds) / len(ds), sum(1 for x in ds if x > 0), sum(1 for x in ds if x < 0)))
        lines.append('')
    lines.append('**Where the sounds came from (R21f, `to_master.py --all`):** %s.' % ', '.join(
        '%s %d' % kv for kv in sorted(tot.items())))
    lines += ['', '## Every language', '',
              'Fallbacks: phonemes on their old line because of a fault, each with its reason in the pack\'s map and in `to_master.py`\'s '
              'report. Kept apart: phonemes kept on their old line so as not to merge with another (D96). Check A: pass or FAIL, the '
              'formant and F0 checks met / made. Check B: against reference ranges. Level: before / after (`report.py`; nothing above '
              '4 without a native signature).', '',
              '| Tag | Language | Template | Fallbacks | Kept apart | CER 1.3.0 | %sCER now | Change | Check A before | Check A after | '
              'Check B before / after | Level before / after | Failure layer |' % ('CER D97 | ' if prev is not None else ''),
              '|---|---|---|---|---|---|---|---|---|---|---|---|---|' + ('---|' if prev is not None else '')] + scored
    reasons = []
    for tag in sorted(packs):
        for r in packs[tag]['rows']:
            if r['kind'] in ('legacy-fallback', 'kept-apart'):
                reasons.append('- %s `%s` (%s): %s' % (tag, r['key'], r['kind'], r.get('why', '')))
    lines += ['', '## Each fallback and each phoneme kept apart, with its reason', ''] + (reasons or ['none'])
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('switch report: %d packs; CER rose > 0.10 in %d, fell > 0.02 in %d; levels dropped %d; wrote %s' % (
        len(packs), len(rose), len(fell), len(dropped), os.path.relpath(out)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
