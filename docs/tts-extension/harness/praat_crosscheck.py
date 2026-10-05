# SPDX-License-Identifier: GPL-3.0-or-later
#
# This one file is under the GNU General Public License version 3 or later, not the MIT licence
# of the rest of docs/tts-extension/harness: it imports Parselmouth (praat-parselmouth), which is
# GPL v3 and contains Praat. Nothing else in the harness imports it. (DECISIONS.md D9.)
"""A second opinion from Praat on the harness's own analyser (analysis.py).

Measures the same signals with both: the synthetic vowels of selftest.py (formants known) and
real engine renders (US English vowels, Hindi, German), and prints the difference. Praat's
"To Formant (burg)" with 5 formants up to 5000 Hz (the synthesiser runs at 11025 Hz), a 25 ms
window and pre-emphasis from 50 Hz; "To Pitch" with its defaults (75-600 Hz).

    python docs/tts-extension/harness/praat_crosscheck.py

Exits 1 if any formant or F0 differs from Praat by more than 5 % (F1 by more than 60 Hz).
"""

import os
import sys

import parselmouth

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysis as A   # noqa: E402
import engine as E     # noqa: E402
import synth as S      # noqa: E402

ROWS = []


def compare(label, x, rate, t_ms, truth=None):
    """truth: {1: F1, 2: F2, 3: F3, 0: F0} for a synthetic signal; where Praat and the harness
    disagree, the one nearer the truth is right, and if it is ours the row passes ('ok*')."""
    snd = parselmouth.Sound(x / 32768.0, sampling_frequency=rate)
    fm = snd.to_formant_burg(time_step=0.005, max_number_of_formants=5, maximum_formant=5000,
                             window_length=0.025, pre_emphasis_from=50)
    pitch = snd.to_pitch(time_step=0.005, pitch_floor=75, pitch_ceiling=600)
    ours = A.formants(x, rate, t_ms)
    bad = False
    noted = [False]
    cells = []
    for k in (1, 2, 3):
        p = fm.get_value_at_time(k, t_ms / 1000.0)
        o = ours[k - 1][0] if len(ours) >= k else None
        lim = 60.0 if k == 1 else 0.05 * p if p == p else 0
        ok = o is not None and p == p and abs(o - p) <= max(lim, 0.05 * p)
        if not ok and truth and o is not None and abs(o - truth[k]) < abs(p - truth[k]):
            ok, noted[0] = True, True
        bad |= not ok
        cells.append('F%d %5.0f/%5.0f' % (k, o or 0, p if p == p else 0))
    pp = pitch.get_value_at_time(t_ms / 1000.0)
    po = A.f0_at(x, rate, t_ms)
    if pp == pp and po:
        ok = abs(po - pp) <= 0.05 * pp
        if not ok and truth and abs(po - truth[0]) < abs(pp - truth[0]):
            ok, noted[0] = True, True
        bad |= not ok
        cells.append('F0 %5.1f/%5.1f' % (po, pp))
    ROWS.append((label, not bad))
    print('%-4s %-24s %s' % ('DIFF' if bad else 'ok*' if noted[0] else 'ok', label, '  '.join(cells)))


def main():
    print('ours/praat in Hz')
    for v, fs in (('i', [(342, 60), (2322, 90), (3000, 150)]), ('u', [(378, 60), (997, 80), (2343, 150)]),
                  ('a', [(768, 80), (1333, 90), (2522, 150)])):
        for f0 in (110.0, 210.0):
            truth = {1: fs[0][0], 2: fs[1][0], 3: fs[2][0], 0: f0}
            compare('synthetic /%s/ f0=%d' % (v, f0), S.vowel(fs + [(3500, 250)], f0=f0), S.RATE, 150.0, truth)
    renders = E.render('enus', [('v_%d' % i, 'module', '`[.1h%sd]' % v) for i, v in enumerate('iaEAuU')], jobs=4)
    renders += E.render('enus', [('f_%d' % i, 'module', '`[.1h%sd]' % v) for i, v in enumerate('iau')], preset=2, jobs=3)
    renders += E.render('hi', [('h_%d' % i, 'ipa', s) for i, s in enumerate(['ˈpaːni', 'ˈbiːs', 'ˈduːdʰ'])], jobs=3)
    renders += E.render('dede', [('d_%d' % i, 'module', '`[.1t%st]' % v) for i, v in enumerate('ieaou')], jobs=3)
    for r in renders:
        x, rate = E.read_wav(r['wav'])
        for ph in r['phones']:
            cls = A.phone_class(ph.get('record'), ph['name'], E.pack(r['tag']).phone_module)
            if cls == 'vowel' and ph['end_ms'] - ph['start_ms'] >= 60:
                compare('%s preset %d /%s/' % (r['tag'], r['preset'], ph['name']), x, rate,
                        (ph['start_ms'] + ph['end_ms']) / 2.0)
    bad = [l for l, ok in ROWS if not ok]
    print('(ok* = Praat and the harness disagree and the harness is nearer the known answer)')
    print('== %d compared, %d agree within 5 %% (F1 60 Hz), %d differ' % (len(ROWS), len(ROWS) - len(bad), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
