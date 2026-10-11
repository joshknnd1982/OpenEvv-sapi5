"""Phase 5 audit, step 8: the IPA chart re-derived by the auditor and diffed against the Phase 0
checklist. MIT licence.

    python docs/tts-extension/audit5/checklist_rederived.py

The lists below are the auditor's own reading of the seven official 600 ppi sub-chart images of
the 2026 issue ("IPA Chart revised to 2015/2005", CC BY-SA 4.0; cited, not reproduced), made
without looking at inventory/IPA_CHECKLIST.json, then compared with it by code-point id.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
pulm = "p b t d ʈ ɖ c ɟ k ɡ q ɢ ʔ m ɱ n ɳ ɲ ŋ ɴ ʙ r ʀ ⱱ ɾ ɽ ɸ β f v θ ð s z ʃ ʒ ʂ ʐ ç ʝ x ɣ χ ʁ ħ ʕ h ɦ ɬ ɮ ʋ ɹ ɻ j ɰ l ɭ ʎ ʟ".split()
nonp = "ʘ ǀ ǃ ǂ ǁ ɓ ɗ ʄ ɠ ʛ ʼ".split()
other = "ʍ w ɥ ʜ ʢ ʡ ɕ ʑ ɺ ɧ".split() + ['͜', '͡']
vow = "i y ɨ ʉ ɯ u ɪ ʏ ʊ e ø ɘ ɵ ɤ o ə ɛ œ ɜ ɞ ʌ ɔ æ ɐ a ɶ ɑ ɒ".split()
diac = ['̥', '̊', '̬', 'ʰ', '̹', '̜', '̟', '̠', '̈', '̽', '̩',
        '̯', '˞', '̤', '̰', '̼', 'ʷ', 'ʲ', 'ˠ', 'ˤ', '̴', '̝',
        '̞', '̘', '̙', '̪', '̺', '̻', '̃', 'ⁿ', 'ˡ', '̚']
supra = ['ˈ', 'ˌ', 'ː', 'ˑ', '̆', '|', '‖', '.', '‿']
tones = ['̋', '˥', '́', '˦', '̄', '˧', '̀', '˨', '̏', '˩',
         '̌', '˩˥', '̂', '˥˩', '᷄', '˧˥', '᷅', '˩˧',
         '᷈', '˧˦˨', 'ꜜ', 'ꜛ', '↗', '↘']
SECTIONS = (('pulmonic', pulm), ('non_pulmonic', nonp), ('other_symbols', other), ('vowels', vow),
            ('diacritics', diac), ('suprasegmentals', supra), ('tones', tones))
mine = {}
for sec, lst in SECTIONS:
    for x in lst:
        mine['+'.join('U+%04X' % ord(c) for c in x)] = sec
print('auditor:', len(mine), {sec: len(lst) for sec, lst in SECTIONS})
d = json.load(open(os.path.join(ROOT, 'docs', 'tts-extension', 'inventory', 'IPA_CHECKLIST.json'), encoding='utf-8'))
theirs = {s['id']: s['section'] for s in d['symbols']}
print('checklist:', len(theirs), d['counts']['by_section'])
print('in the auditor\'s list, not in the checklist:', [k for k in mine if k not in theirs])
print('in the checklist, not in the auditor\'s list:', [k for k in theirs if k not in mine])
print('section differs:', [(k, mine[k], theirs[k]) for k in mine if k in theirs and mine[k] != theirs[k]])
