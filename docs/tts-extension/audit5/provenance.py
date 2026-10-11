"""Phase 5 audit, step 3: provenance honesty over every tagged value of the master table. MIT licence.

    python docs/tts-extension/audit5/provenance.py

Counts the tags; checks every `measured` value's proof file and key; every `estimated` entry's
presence in OPEN_QUESTIONS.md; the source ids a `derived` or `estimated` note names against
ipa/sources.toml; and lists `literature` values whose own note states a weakness (a reading of a
figure, a single token, a reconstructed table).
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

s = tomllib.load(open(os.path.join(ROOT, 'ipa', 'sources.toml'), 'rb'))['source']
oq = open(os.path.join(ROOT, 'docs', 'tts-extension', 'OPEN_QUESTIONS.md'), encoding='utf-8').read()
refs = open(os.path.join(ROOT, 'docs', 'tts-extension', 'REFERENCES.md'), encoding='utf-8').read()
WEAK = ['read from the figure', 'single token', 'a single token', 'not a mean', 'abstract only']
counts = collections.Counter()
used = collections.Counter()
lit_weak, meas_bad, est_not_queued, unlisted = [], [], [], collections.Counter()
tok = re.compile(r'\b([a-z][a-z0-9]*_[a-z0-9_]+|[a-z]+(?:19|20)\d\d[a-z]*)\b')
NOISE = re.compile(r'^(f[1-5]|b[1-5]|a[2-6]|rel|voice|noise|burst|strike|slap|mod|pulse|vot|edge|hnr|centroid|peak|duration|'
                   r'frames|hf|band|mid|gap|schwa|f0|jitter|creak|breath|voiced|h1h2|a1|stave|tone|closure|locus|inherent|'
                   r'fricated|whisper|open|over|raised|voicing|phonation|step|offset|st|min|max|plain|marked|next|prev|req|'
                   r'res|case|test|check|table|design|build|stage|proof|key|part|wrap|lost|pre|post|non|extra|sub|level|'
                   r'delay|length|rate|compose|per|sounds|extipa|voqs|[aiu])[_0-9]')
for f in sorted(glob.glob(os.path.join(ROOT, 'ipa', 'table', '*.toml'))):
    t = tomllib.load(open(f, 'rb'))
    for sid, e in t['sound'].items():
        def walk(n, path):
            if isinstance(n, dict):
                if 'tag' in n:
                    tag = n['tag']
                    counts[tag] += 1
                    note = (n.get('note') or '') + ' ' + (n.get('rule') or '')
                    if tag == 'literature':
                        used[n.get('ref')] += 1
                        hits = [w for w in WEAK if w in note.lower()]
                        if hits:
                            lit_weak.append((sid, e.get('ipa'), path, n.get('v'), n.get('ref'), hits))
                    elif tag == 'measured':
                        pf = os.path.join(ROOT, n.get('proof') or '')
                        ok = os.path.exists(pf)
                        if ok:
                            d = json.load(open(pf, encoding='utf-8'))
                            key = n.get('key')
                            ok = key is None or key in (d.get('trims') or {}) or key in ((d.get('said_as') or {}).get('keys') or {})
                        if not ok:
                            meas_bad.append((sid, e.get('ipa'), path, n.get('v'), n.get('proof'), n.get('key')))
                    elif tag == 'estimated':
                        if sid not in oq:
                            est_not_queued.append((sid, path))
                    if tag in ('derived', 'estimated', 'approximate', 'created'):
                        for m in set(tok.findall(note)):
                            if m not in s and not NOISE.match(m) and not m.startswith(('wp_', 'wikipedia_')):
                                unlisted[m] += 1
                else:
                    for k, v in n.items():
                        walk(v, path + '.' + str(k))
            elif isinstance(n, list):
                for v in n:
                    walk(v, path)
        walk(e, '')
print('tags:', dict(counts))
print('sources: %d, opened %d' % (len(s), sum(1 for v in s.values() if v.get('opened'))))
print('literature refs used: %d distinct; missing from ipa/sources.toml: %s; not opened: %s' % (
    len(used), [r for r in used if r not in s], [r for r in used if r in s and not s[r].get('opened')]))
print('literature refs used by the table but not named in REFERENCES.md: %d of %d: %s' % (
    sum(1 for r in used if r not in refs), len(used), sorted(r for r in used if r not in refs)))
print('\nliterature values whose note states a weakness (%d):' % len(lit_weak))
for x in lit_weak:
    print('  ', x)
print('\nmeasured values whose proof or key is missing (%d):' % len(meas_bad))
for x in meas_bad:
    print('  ', x)
print('\nestimated values whose entry is not in OPEN_QUESTIONS.md (%d): %s' % (
    len(est_not_queued), sorted(set(x[0] for x in est_not_queued))[:40]))
print('\nsource-like ids named in derived/estimated/approximate/created notes but not in ipa/sources.toml:')
for k, v in sorted(unlisted.items(), key=lambda x: -x[1]):
    print('  %-40s %d' % (k, v))
