"""Status of every language from the harness's results (Phase 1, steps 6 and 7).

Reads golden/<tag>.json.gz (every phoneme rendered and measured), results/asr.json and the reference
store, and writes:

    results/status.json                  everything below, per language
    ../LANGUAGE_STATUS.md                the table between its STATUS markers (the rest is kept)
    ../reports/index.html + *.png        tables, spectrograms with formant tracks, vowel charts

Check A, engine fidelity. Evidence: the frames are the request (the engine is parametric, so what
it asked the synthesiser for is ground truth), and the sound is measured to see that the
synthesiser realised them.
    A1 (frames)  every phone the engine meant to sound has frames that sound: voicing or noise.
    A2 (signal)  in every vowel, F1 and F2 measured from the sound match the frames' (F1 within
                 8 % or three quarters of F0, F2 within 8 % or 60 Hz) and F0 the frames' mean over
                 the middle 40 ms within 5 % (not for a vowel starting in the first 20 ms).
    Stops (their closure is silent by nature) and unlabelled runs are not held to A1.
    passes when A1 holds for every phone and A2 for at least A2_PASS of its checks.
Check B, target correctness: each measured value of a target phone against the reference store
(reference.py), preset 1 (adult male). Passes when at least B_PASS of the checks with a reference
are in range; "no reference" when none has one.
ASR: CER from asr.py; passes at or below CER_PASS.

Status level (playbook 1.5): 1 draft; 2 engine-verified (A passes); 3 reference-verified (and B
passes); 4 intelligibility-verified (and ASR passes); 5 native-validated only by a person, in
LANGUAGE_STATUS.md by hand. A level needs every level below it.

First-pass failure layer, for a language below level 4 with a failing check: 'phoneme values'
when A or B fails; when only ASR fails, 'stress-or-tone' for a pack with tones of its own,
otherwise 'unknown' (G2P, duration and coarticulation cannot yet be told apart: Phase 6 triage).
"""

import argparse
import html
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysis as A    # noqa: E402
import engine as E      # noqa: E402
import reference as R   # noqa: E402

DOCS = os.path.dirname(HERE)
REPORTS = os.path.join(DOCS, 'reports')
RESULTS = os.path.join(HERE, 'results')
A2_PASS, B_PASS, CER_PASS = 0.90, 0.80, 0.15
B_MEASURES = ('F1_50_hz', 'F2_50_hz', 'F3_50_hz', 'centroid_hz', 'peak_hz', 'vot_ms', 'antiformant_hz',
              'murmur_F1_hz', 'F3_min_hz')


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def check_a(gold):
    a1 = a1_bad = a2 = a2_ok = 0
    bad = []
    for cid, case in gold['cases'].items():
        for ph in case['phones']:
            if ph['cls'] == 'silence':
                continue
            req, meas = ph.get('req') or {}, ph.get('meas') or {}
            if not req:
                continue
            # a stop's closure is silent by nature (its burst is traced in the next phone), and an
            # unlabelled run is not known to be meant to sound
            if ph['cls'] in ('stop', 'affricate', 'other'):
                continue
            a1 += 1
            if req.get('voiced_frames', 0) + req.get('noise_frames', 0) == 0 and ph['end_ms'] > ph['start_ms']:
                a1_bad += 1
                bad.append('%s: %s has no sounding frame' % (cid, ph['name']))
            if ph['cls'] != 'vowel' or ph['end_ms'] - ph['start_ms'] < 50 or not req.get('av'):
                continue
            f0 = req.get('f0_hz') or 100.0
            for k, tol in (('F1', max(0.08 * (req.get('F1_hz') or 0), 0.75 * f0)),
                           ('F2', max(0.08 * (req.get('F2_hz') or 0), 60.0))):
                m, r = meas.get('%s_50_hz' % k), req.get('%s_hz' % k)
                if r:
                    a2 += 1
                    if m is not None and abs(m - r) <= tol:
                        a2_ok += 1
                    elif len(bad) < 40:
                        bad.append('%s: %s %s measured %s, frames %s' % (cid, ph['name'], k, m, r))
            # F0 against the frames' own over the window the measure hears; not within 20 ms of the
            # start, where that window would hang over the edge
            m, r = meas.get('f0_50_hz'), req.get('f0_mid40_hz')
            if r and ph['start_ms'] >= 20:
                a2 += 1
                if m is not None and abs(m - r) <= 0.05 * r:
                    a2_ok += 1
                elif len(bad) < 40:
                    bad.append('%s: %s F0 measured %s, frames %s' % (cid, ph['name'], m, r))
    ok = a1_bad == 0 and a1 > 0 and (a2 == 0 or a2_ok / a2 >= A2_PASS)
    return dict(passed=ok, a1_phones=a1, a1_silent=a1_bad, a2_checks=a2, a2_ok=a2_ok,
                a2_rate=round(a2_ok / a2, 3) if a2 else None, problems=bad[:40])


def case_ipa(p, cid):
    """The IPA a golden case is about: the eSpeak NG phoneme's, or the module phone's."""
    kind, _, name = cid.partition('|')
    if kind == 't':
        return None
    if p.kind == 'espeak':
        import ipa
        return ipa.espeak_inventory(p).get(name)
    return A.module_ipa(p.phone_module).get(name)


def target(case, cid):
    """The phone a case is about: the vowel of [t'Vta], the consonant of ['aCa] / `[.1aXa]."""
    ph = [x for x in case['phones'] if x['cls'] != 'silence']
    if cid.startswith('v|'):
        vs = [x for x in ph if x['cls'] == 'vowel']
        return vs[0] if vs else None
    if len(ph) >= 3 and ph[0]['cls'] == 'vowel':
        rest = ph[1:]
        cons = [x for x in rest if x['cls'] != 'vowel']
        if cons and rest.index(cons[0]) == 0:
            return cons[0]
    return ph[1] if cid.startswith('m|') and len(ph) >= 3 else None


def check_b(p, gold, locale):
    import unicodedata
    rows = []
    for cid, case in gold['cases'].items():
        ipa = case_ipa(p, cid)
        t = target(case, cid)
        if not ipa or t is None:
            continue
        ipa = unicodedata.normalize('NFC', ipa)
        for mname in B_MEASURES:
            c = R.check(ipa, locale, 1, mname, (t.get('meas') or {}).get(mname))
            if c:
                c.update(case=cid, ipa=ipa, measure=mname)
                rows.append(c)
    n_in = sum(1 for r in rows if r['verdict'] == 'in range')
    if not rows:
        return dict(passed=None, checks=0, in_range=0, rows=[])
    return dict(passed=n_in / len(rows) >= B_PASS, checks=len(rows), in_range=n_in,
                rate=round(n_in / len(rows), 3), rows=rows)


def has_tones(p):
    if p.kind != 'espeak':
        return p.tag == 'jajp'      # pitch accent, made by the module itself
    with open(p.sounds_map, encoding='utf-8') as f:
        return any(line.startswith('tone ') for line in f)


def status(tag, asr):
    p = E.pack(tag)
    import golden
    gold = golden.read_golden(tag) if os.path.exists(golden.golden_path(tag)) else None
    locale = None
    ini = os.path.join(p.dir, 'language.ini')
    with open(ini, encoding='utf-8-sig') as f:
        for line in f:
            if line.startswith('Locale='):
                locale = line.split('=', 1)[1].strip()
    out = dict(tag=tag, name=p.name, kind=p.kind, module=p.module_tag, locale=locale, tones=has_tones(p))
    if gold is None:
        out.update(level=1, why='no golden data: not yet rendered')
        return out
    out['cases'] = len(gold['cases'])
    out['a'] = check_a(gold)
    out['b'] = check_b(p, gold, locale)
    ar = (asr or {}).get(tag)
    out['asr'] = {k: ar.get(k) for k in ('status', 'reason', 'whisper', 'cer', 'wer', 'n', 'source', 'note')} if ar else \
        dict(status='not run')
    asr_ok = ar is not None and ar.get('status') == 'scored' and ar.get('cer') is not None and ar['cer'] <= CER_PASS
    level = 1
    if out['a']['passed']:
        level = 2
        if out['b']['passed']:
            level = 3
            if asr_ok:
                level = 4
    out['level'] = level
    layer = None
    if not out['a']['passed'] or out['b']['passed'] is False:
        layer = 'phoneme values'
    elif ar and ar.get('status') == 'scored' and not asr_ok:
        layer = 'stress-or-tone' if out['tones'] else 'unknown'
    out['failure_layer'] = layer
    return out


LEVEL_NAME = {1: '1 draft', 2: '2 engine-verified', 3: '3 reference-verified', 4: '4 intelligibility-verified'}


def fmt_b(b):
    if b['passed'] is None:
        return 'no reference'
    return '%s %d/%d' % ('pass' if b['passed'] else 'FAIL', b['in_range'], b['checks'])


def fmt_asr(a):
    if a.get('status') == 'scored':
        return 'CER %.2f%s' % (a['cer'], '' if a.get('wer') is None else ' WER %.2f' % a['wer'])
    return a.get('status', 'not run') + (' (%s)' % a['reason'] if a.get('reason') else '')


def write_status_md(rows):
    path = os.path.join(DOCS, 'LANGUAGE_STATUS.md')
    with open(path, encoding='utf-8') as f:
        text = f.read()
    begin, end = '<!-- STATUS BEGIN (written by harness/report.py) -->', '<!-- STATUS END -->'
    counts = {}
    for r in rows:
        counts[r['level']] = counts.get(r['level'], 0) + 1
    lines = [begin, '',
             'Measured %s by `harness/report.py`. Preset 1 (adult male), 64-bit, 11025 Hz. '
             'Levels: %s. Check A = engine fidelity (A1 frames, A2 sound vs frames), check B = against cited '
             'reference ranges, ASR = Whisper large-v3 character error rate. Pass marks: A2 >= %d %%, B >= %d %%, '
             'CER <= %.2f. A failure layer is a first-pass label, not a diagnosis.' % (
                 time.strftime('%Y-%m-%d'), ', '.join('%s: %d' % (LEVEL_NAME[k], v) for k, v in sorted(counts.items())),
                 A2_PASS * 100, B_PASS * 100, CER_PASS), '',
             '| Tag | Language | Kind | Level | Check A (A1 silent / A2) | Check B | ASR | Failure layer |',
             '|---|---|---|---|---|---|---|---|']
    for r in rows:
        a = r.get('a') or {}
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['tag'], r['name'], r['kind'], LEVEL_NAME[r['level']],
            ('%s (%d / %s)' % ('pass' if a.get('passed') else 'FAIL', a.get('a1_silent', 0),
                               '%.0f %%' % (100 * a['a2_rate']) if a.get('a2_rate') is not None else '-')) if a else '-',
            fmt_b(r['b']) if r.get('b') else '-', fmt_asr(r.get('asr') or {}), r.get('failure_layer') or ''))
    lines += ['', end]
    block = '\n'.join(lines)
    if begin in text:
        text = text[:text.index(begin)] + block + text[text.index(end) + len(end):]
    else:
        text = text.rstrip('\n') + '\n\n' + block + '\n'
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return path


# ---- pictures ------------------------------------------------------------------------------------

def plot_case(tag, kind, text, png, title):
    """Spectrogram with formant tracks: measured from the sound (dots), requested in the frames
    (lines), and the reference range where there is one (bands at the right)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r = E.render(tag, [('plot', kind, text)], jobs=1, work=os.path.join(E.WORK, 'report', tag))[0]
    x, rate = E.read_wav(r['wav'])
    t = E.frame_times(r['frames'])
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=90)
    ax.specgram(x.astype(float), NFFT=256, Fs=rate, noverlap=200, cmap='Greys', scale='dB', vmin=-20)
    for k, col in ((1, '#d62728'), (2, '#1f77b4'), (3, '#2ca02c')):
        ax.plot(t / 1000.0, r['frames'][:, E.P['f%d' % k]], color=col, lw=1.2, label='F%d requested' % k)
        tr = A.formant_track(x, rate, 0, r['case_ms'])
        ax.plot([tt / 1000.0 for tt, f in tr if len(f) >= k and A.intensity_db(x, rate, tt - 10, tt + 10) > -45],
                [f[k - 1][0] for tt, f in tr if len(f) >= k and A.intensity_db(x, rate, tt - 10, tt + 10) > -45],
                '.', color=col, ms=2.5, label='F%d measured' % k)
    p = E.pack(tag)
    for ph in r['phones']:
        ax.axvline(ph['start_ms'] / 1000.0, color='#999', lw=0.5)
        ax.text((ph['start_ms'] + ph['end_ms']) / 2000.0, rate / 2 - 300, ph['name'], ha='center', fontsize=8)
    ax.set_ylim(0, rate / 2)
    ax.set_xlabel('s')
    ax.set_ylabel('Hz')
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=6, ncol=3, loc='upper right', bbox_to_anchor=(1, 0.92))
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)


def vowel_chart(tag, png, rows):
    """F1/F2 of the golden vowels (preset 1) against the reference boxes of the same IPA."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import unicodedata
    import golden
    gold = golden.read_golden(tag)
    p = E.pack(tag)
    st = [r for r in rows if r['tag'] == tag][0]
    fig, ax = plt.subplots(figsize=(5.2, 4.4), dpi=90)
    for cid, case in gold['cases'].items():
        ipa = case_ipa(p, cid)
        t = target(case, cid)
        if not ipa or not t or t['cls'] != 'vowel':
            continue
        m = t.get('meas') or {}
        if m.get('F1_50_hz') and m.get('F2_50_hz'):
            ax.plot(m['F2_50_hz'], m['F1_50_hz'], 'o', color='#1f77b4', ms=4)
            ax.annotate(ipa, (m['F2_50_hz'], m['F1_50_hz']), fontsize=8, xytext=(3, 3), textcoords='offset points')
        e1 = R.lookup(unicodedata.normalize('NFC', ipa), st['locale'], 1, 'F1_50_hz')
        e2 = R.lookup(unicodedata.normalize('NFC', ipa), st['locale'], 1, 'F2_50_hz')
        if e1 and e2:
            lo1, hi1, _ = R.bounds(e1)
            lo2, hi2, _ = R.bounds(e2)
            ax.add_patch(plt.Rectangle((lo2, lo1), hi2 - lo2, hi1 - lo1, fill=False, ec='#d62728', lw=0.6))
            ax.annotate(ipa, (hi2, hi1), fontsize=7, color='#d62728')
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_xlabel('F2 (Hz)')
    ax.set_ylabel('F1 (Hz)')
    ax.set_title('%s vowels: measured (blue) vs reference range (red)' % tag, fontsize=9)
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)


PICTURES = [('enus', 'module', '`[.1hid] `[.1had] `[.1hud]', 'US English /hid had hud/ (module annotation)'),
            ('dede', 'module', '`[.1tit] `[.1tat] `[.1tut]', 'German /tit tat tut/'),
            ('hi', 'ipa', 'ˈpaːni ˈʈʰəɳɖa', 'Hindi from IPA: paːni ʈʰəɳɖa'),
            ('cmn', 'text', '妈妈骂马。', 'Mandarin, text (tones)'),
            ('ar', 'text', 'مرحبا بالعالم.', 'Arabic, text'),
            ('sw', 'text', 'Habari ya asubuhi.', 'Swahili, text')]


def write_html(rows, pictures=True):
    os.makedirs(REPORTS, exist_ok=True)
    figs = []
    if pictures:
        for i, (tag, kind, text, title) in enumerate(PICTURES):
            png = 'case_%d_%s.png' % (i, tag)
            plot_case(tag, kind, text, os.path.join(REPORTS, png), title)
            figs.append((png, title))
        for tag in ('enus', 'dede', 'es', 'pt', 'fr'):
            if any(r['tag'] == tag and r.get('b') for r in rows) and os.path.exists(os.path.join(HERE, 'golden', '%s.json.gz' % tag)):
                png = 'vowels_%s.png' % tag
                vowel_chart(tag, os.path.join(REPORTS, png), rows)
                figs.append((png, '%s vowels against the reference store' % tag))
    esc = html.escape
    trs = []
    for r in rows:
        a, b = r.get('a') or {}, r.get('b') or {}
        trs.append('<tr class="l%d"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            r['level'], esc(r['tag']), esc(r['name']), r['kind'], esc(LEVEL_NAME[r['level']]),
            esc('%s, %d silent, A2 %s' % ('pass' if a.get('passed') else 'FAIL', a.get('a1_silent', 0),
                                          '%.0f%%' % (100 * a['a2_rate']) if a.get('a2_rate') is not None else '-')) if a else '-',
            esc(fmt_b(b)) if b else '-', esc(fmt_asr(r.get('asr') or {})), esc(r.get('failure_layer') or '')))
    brows = []
    for r in rows:
        for c in (r.get('b') or {}).get('rows', []):
            if c['verdict'] != 'in range':
                brows.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%.0f</td><td>%.0f .. %.0f</td><td>%s</td></tr>' % (
                    esc(r['tag']), esc(c['case']), esc(c['ipa']), esc(c['measure']), c['value'], c['lo'], c['hi'],
                    esc('%s (%s)' % (c['source'], c['variety']))))
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Harness report</title>
<style>
:root {{ --bg:#fff; --fg:#1b1b1b; --mute:#666; --line:#ddd; --l1:#fde2e2; --l2:#fff4d6; --l3:#e3f2e1; --l4:#d4ecd0; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141414; --fg:#eee; --mute:#aaa; --line:#333; --l1:#4a2323; --l2:#4a3f1f; --l3:#24402a; --l4:#1f4a26; }} }}
body {{ background:var(--bg); color:var(--fg); font:14px/1.45 system-ui, sans-serif; margin:0 16px 40px; max-width:1200px; }}
h1 {{ font-size:22px; }} h2 {{ font-size:17px; margin-top:28px; }} p.m {{ color:var(--mute); }}
table {{ border-collapse:collapse; width:100%; font-size:12.5px; }} td, th {{ border-bottom:1px solid var(--line); padding:3px 6px; text-align:left; }}
tr.l1 td:nth-child(4) {{ background:var(--l1); }} tr.l2 td:nth-child(4) {{ background:var(--l2); }}
tr.l3 td:nth-child(4) {{ background:var(--l3); }} tr.l4 td:nth-child(4) {{ background:var(--l4); }}
.wrap {{ overflow-x:auto; }} figure {{ margin:12px 0; }} img {{ max-width:100%; height:auto; background:#fff; }}
</style></head><body>
<h1>OpenEVV harness report</h1>
<p class="m">Written {date} by docs/tts-extension/harness/report.py. Preset 1 (adult male), 64-bit, 11025 Hz. Levels and checks are defined at the top of report.py; LANGUAGE_STATUS.md holds the same table. Nothing here was judged by ear.</p>
<h2>Languages</h2><div class="wrap"><table><tr><th>Tag</th><th>Language</th><th>Kind</th><th>Level</th><th>Check A</th><th>Check B</th><th>ASR</th><th>Failure layer</th></tr>
{rows}</table></div>
<h2>Pictures</h2><p class="m">Spectrograms: lines are the formants the engine asked the synthesiser for (its frames), dots the formants measured from the sound. Vowel charts: blue dots are measured vowels, red boxes the cited reference ranges for the same IPA symbol.</p>
{figs}
<h2>Check B: values out of range</h2><div class="wrap"><table><tr><th>Tag</th><th>Case</th><th>IPA</th><th>Measure</th><th>Value</th><th>Range</th><th>Source</th></tr>
{brows}</table></div>
</body></html>'''.format(date=time.strftime('%Y-%m-%d'), rows='\n'.join(trs),
                         figs='\n'.join('<figure><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>' % (f, esc(t), esc(t)) for f, t in figs),
                         brows='\n'.join(brows) or '<tr><td colspan="7">none</td></tr>')
    path = os.path.join(REPORTS, 'index.html')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-pictures', action='store_true')
    a = ap.parse_args()
    asr = (load(os.path.join(RESULTS, 'asr.json'), {}) or {}).get('languages', {})
    tags = [t for t, p in E.packs().items() if p.kind != 'template']
    rows = [status(t, asr) for t in tags]
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, 'status.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    md = write_status_md(rows)
    page = write_html(rows, pictures=not a.no_pictures)
    counts = {}
    for r in rows:
        counts[r['level']] = counts.get(r['level'], 0) + 1
    layers = {}
    for r in rows:
        if r.get('failure_layer'):
            layers[r['failure_layer']] = layers.get(r['failure_layer'], 0) + 1
    print('levels: %s' % ', '.join('%s: %d' % (LEVEL_NAME[k], v) for k, v in sorted(counts.items())))
    print('check A pass: %d of %d' % (sum(1 for r in rows if (r.get('a') or {}).get('passed')), len(rows)))
    print('check B: pass %d, fail %d, no reference %d' % (
        sum(1 for r in rows if (r.get('b') or {}).get('passed') is True),
        sum(1 for r in rows if (r.get('b') or {}).get('passed') is False),
        sum(1 for r in rows if (r.get('b') or {}).get('passed') is None)))
    print('failure layers: %s' % layers)
    print('wrote %s, %s, %s' % (md, page, os.path.join(RESULTS, 'status.json')))


if __name__ == '__main__':
    main()
