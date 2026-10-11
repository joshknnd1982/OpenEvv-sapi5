"""Failure-layer triage of every language (Phase 6, part 2).

For each language, from measurements the harness already holds, name the layer where its fault
lies, with the evidence, or say that the evidence cannot say. Never a claim that a language
"sounds right": only a status level (LANGUAGE_STATUS.md) and a layer.

Evidence read (all under results/):
    status.json          check A (the engine did what it was asked), check B (against cited ranges), ASR, tones (Phase 1)
    asr.json             this engine's voice, Whisper large-v3, character error rate per language
    asr_espeak.json      eSpeak NG's own voice reading the same sentences with the same rules, scored the same way
    a3-staged.json       check A3 on the staged modules: voiceless sounds and pauses stay unvoiced (a3.py, EVV_STAGE)
    diag-golden-staged.json   the front-end's own report of what it could not place or sound (final front-end)

The layers, in the order they are tested, and what shows each:

    phoneme values    a measured fault in the sounds themselves: check A fails, check B fails (3 or more cited
                      vowels), check A3 fails (a voice where there should be none), or the engine meant a phone and
                      the map gave it no sound (diagnostic phone-unsounded)
    G2P               ASR error above 0.15 and eSpeak NG's own voice, reading the same sentences by the same rules,
                      is no better than 0.10 under this engine's. The fault is upstream of this engine (eSpeak NG's
                      rules for the language or its spelling) or in the recogniser or the reference sentences; these
                      cannot be told apart without a native reader.
    stress-or-tone    ASR error above 0.15 where eSpeak NG's own voice is at or under 0.15, in a language that has tones
    unknown           ASR error above 0.15 where eSpeak NG's own voice is at or under 0.15, no tones, no measured
                      fault: the fault is in what this engine does with the phonemes (stress, duration, coarticulation,
                      melody and the sound values nobody has a reference for), and the harness cannot yet tell which
    (none)            ASR at or under 0.15 and nothing measured against it
    not measured      no recogniser for the language: only checks A, B and A3 speak for it

    python docs/tts-extension/harness/triage.py      -> results/triage.json and the sections of LANGUAGE_STATUS.md
                                                       and TRIAGE_PHASE6.md between their markers
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DOCS))
RES = os.path.join(HERE, 'results')

PASS_CER = 0.15      # D16: the ASR pass mark
G2P_GAP = 0.10       # eSpeak NG's own voice within this of ours (or worse): the fault is not this engine's sounds
B_MIN_VOWELS = 3

BEGIN, END = '<!-- TRIAGE BEGIN (written by harness/triage.py) -->', '<!-- TRIAGE END -->'


def load(name, default=None):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def template_of(tag):
    try:
        with open(os.path.join(ROOT, 'languages', tag, 'language.ini'), encoding='utf-8') as f:
            m = re.search(r'^Template=(\S+)', f.read(), re.M)
        return m.group(1) if m else None
    except OSError:
        return None


def diag_counts(d):
    c = collections.Counter()
    for k, n in (d or {}).items():
        parts = k.split('\t')
        if len(parts) >= 3:
            c[parts[2]] += n
    return c


def triage():
    status = {r['tag']: r for r in load('status.json')}
    asr = (load('asr.json') or {}).get('languages', {})
    es = (load('asr_espeak.json') or {}).get('languages', {})
    a3 = load('a3-staged.json') or {}
    diag = load('diag-golden-staged.json') or {}
    out = {}
    for tag, st in sorted(status.items()):
        ours = asr.get(tag, {})
        cer = ours.get('cer') if ours.get('status') == 'scored' else None
        e = es.get(tag, {})
        ecer = e.get('cer') if e.get('status') == 'scored' else None
        a3r = a3.get(tag)
        dc = diag_counts(diag.get(tag))
        ev, defects = [], []
        if not st['a']['passed']:
            defects.append('check A fails: %s' % '; '.join(st['a'].get('problems', [])[:1] or ['see status.json']))
        b = st['b']
        if b.get('passed') is False:
            defects.append('check B fails: %d of %d values in range' % (b['in_range'], b['checks']))
        if a3r and a3r.get('failures'):
            defects.append('check A3 fails on the staged modules in %d case(s): a voiced pause after a breathy-release stop'
                           % len(a3r['failures']))
        if dc.get('phone-unsounded'):
            defects.append('%d phone(s) the engine meant had no sound (phone-unsounded)' % dc['phone-unsounded'])
        if cer is not None:
            ev.append('ASR CER %.2f (WER %s)' % (cer, 'n/a' if ours.get('wer') is None else '%.2f' % ours['wer']))
        if ecer is not None:
            ev.append("eSpeak NG's own voice CER %.2f" % ecer)
        layer, why = None, ''
        if defects:
            layer, why = 'phoneme values', '; '.join(defects)
        elif cer is None:
            layer, why = 'not measured', ours.get('reason') or 'no recogniser'
        elif cer <= PASS_CER:
            layer, why = '', 'ASR passes'
        elif ecer is None:
            layer, why = 'unknown', 'ASR fails; eSpeak NG own-voice score missing'
        elif ecer > PASS_CER and cer - ecer <= G2P_GAP:
            layer, why = 'G2P', "eSpeak NG's own voice fails these sentences too (CER %.2f against %.2f)" % (ecer, cer)
        elif st['tones']:
            layer, why = 'stress-or-tone', "the language has tones; eSpeak NG's own voice reads the sentences (CER %.2f) where this engine does not (%.2f)" % (ecer, cer)
        else:
            layer, why = 'unknown', "eSpeak NG's own voice reads the sentences (CER %.2f), this engine does not (%.2f): the fault is in what this engine does with the phonemes; stress, duration, coarticulation and the sound values cannot yet be told apart" % (ecer, cer)
        # a second layer when ASR also fails and the first was a measured fault
        second = ''
        if defects and cer is not None and cer > PASS_CER:
            if ecer is not None and ecer > PASS_CER and cer - ecer <= G2P_GAP:
                second = 'G2P'
            elif st['tones'] and ecer is not None:
                second = 'stress-or-tone'
            elif ecer is not None:
                second = 'unknown'
        out[tag] = dict(tag=tag, name=st['name'], kind=st['kind'], template=template_of(tag) or st.get('module'),
                        level=st['level'], tones=st['tones'], cer=cer, espeak_cer=ecer,
                        gap=None if cer is None or ecer is None else round(cer - ecer, 3),
                        layer=layer, second=second, why=why, evidence=ev, defects=defects,
                        a3_failures=len(a3r['failures']) if a3r else None,
                        unsounded=dc.get('phone-unsounded', 0), key_inert=dc.get('key-inert', 0))
    return out


def md_tables(t):
    L = []
    cnt = collections.Counter((r['layer'] or 'passes ASR') for r in t.values())
    L.append('| Failure layer | Languages |')
    L.append('|---|---|')
    order = ['phoneme values', 'G2P', 'stress-or-tone', 'unknown', 'not measured', 'passes ASR']
    for k in order:
        L.append('| %s | %d |' % (k, cnt.get(k, 0)))
    L.append('| all | %d |' % len(t))
    L.append('')
    L.append('| Tag | Language | Template | Level | ASR CER | eSpeak NG own voice | Layer | Evidence |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in t.values():
        lay = (r['layer'] or '') + (' (then %s)' % r['second'] if r['second'] else '')
        L.append('| %s | %s | %s | %d | %s | %s | %s | %s |' % (
            r['tag'], r['name'], r['template'] or '', r['level'],
            '' if r['cer'] is None else '%.2f' % r['cer'],
            '' if r['espeak_cer'] is None else '%.2f' % r['espeak_cer'],
            lay, r['why'].replace('|', '/')))
    return '\n'.join(L)


def splice(path, text, header):
    with open(path, encoding='utf-8', newline='') as f:
        old = f.read()
    eol = '\r\n' if '\r\n' in old else '\n'
    block = BEGIN + '\n' + text.strip() + '\n' + END
    block = block.replace('\n', eol)
    if BEGIN in old:
        new = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), lambda m: block, old, flags=re.S)
    else:
        new = old.rstrip() + eol + eol + header.replace('\n', eol) + eol + eol + block + eol
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new)


def fixlist(t):
    """Prioritized fixes grouped by shared root cause, and the languages that need a stronger model."""
    L = []
    lay = collections.defaultdict(list)
    for r in t.values():
        lay[r['layer'] or 'passes ASR'].append(r)
    a3 = sorted(r['tag'] for r in t.values() if r['a3_failures'])
    uns = sorted((r['unsounded'], r['tag']) for r in t.values() if r['unsounded'])
    b = sorted(r['tag'] for r in t.values() if any(d.startswith('check B') for d in r['defects']))
    a = sorted(r['tag'] for r in t.values() if any(d.startswith('check A fails') for d in r['defects']))
    g2p = sorted(lay['G2P'], key=lambda r: -(r['espeak_cer'] or 0))
    syn = sorted([r for r in t.values() if r['layer'] in ('unknown', 'stress-or-tone') or r['second'] in ('unknown', 'stress-or-tone')
                  if r['gap'] is not None], key=lambda r: -r['gap'])
    bytpl = collections.defaultdict(list)
    for r in syn:
        bytpl[r['template']].append(r['gap'])
    L.append('### Fixes, in the order to do them (grouped by shared root cause)')
    L.append('')
    n = 0

    def item(title, body):
        nonlocal n
        n += 1
        L.append('%d. **%s**' % (n, title))
        L.append('   %s' % body)
        L.append('')
    if a3:
        item('A voiced pause after a breathy-release stop (check A3 fails on the staged modules)',
             '%d languages: %s. One cause: the breathy-release key (`brth`) on a stop before a pause. A defect of the engine, not of a language; fix in the accent layer or the template, then re-run `a3.py` and the golden.' % (len(a3), ' '.join(a3)))
    if a:
        item('Check A fails (the engine made a meant vowel silent)', ' '.join(a) + '. Read the case in `status.json`; the sound definition or the map line for that vowel.')
    if uns:
        item('Phones the engine meant that the map gave no sound (phone-unsounded)',
             '%d events in %d languages (%s). The map line says `-` or names a sound the module lacks; add the sound to the pack or map the phoneme.' % (
                 sum(n for n, _ in uns), len(uns), ', '.join('%s %d' % (tg, n) for n, tg in sorted(uns, reverse=True))))
    if b:
        item('Check B fails (vowel or nasal values outside cited ranges)',
             '%s. Native modules and English or Spanish dialects, where cited ranges exist; the measured values are in `status.json`. Fix is a sound value (formant targets of the template or the pack), judged against the reference, not by ear.' % ' '.join(b))
    if g2p:
        item("The text is read wrongly, or the recogniser cannot judge it (own voice of eSpeak NG fails too)",
             '%d languages, worst first: %s. Nothing in the sounds of this engine explains these; the fix is the rules of eSpeak NG for the language, the own reader of a pack (DESIGN.md 8.2), or a better reference sentence set. A native reader is needed to tell which.' % (
                 len(g2p), ', '.join('%s (eSpeak %.2f, here %.2f)' % (r['tag'], r['espeak_cer'], r['cer']) for r in g2p[:25]) + (' ...' if len(g2p) > 25 else '')))
    if syn:
        tp = '; '.join('%s: %d languages, mean gap %.2f' % (k, len(v), sum(v) / len(v)) for k, v in sorted(bytpl.items(), key=lambda kv: -len(kv[1])))
        item("The voice of this engine is understood worse than that of eSpeak NG on the same phonemes",
             '%d languages. By template: %s. The widest gaps: %s. The cause is in what this engine does with the phonemes: stress, duration, coarticulation or sound values; the harness cannot yet separate them (the next measure to build: the same sentences with the own phoneme durations of eSpeak NG and stress, to see which of the two the engine gets wrong).' % (
                 len(syn), tp, ', '.join('%s +%.2f' % (r['tag'], r['gap']) for r in syn[:15])))
    nm = sorted(r['tag'] for r in t.values() if r['layer'] == 'not measured')
    item('Languages no recogniser can judge', '%d languages: %s. Level 2 at most until a native reader or another recogniser reads them (Phase 7 builds the review packets).' % (len(nm), ' '.join(nm)))
    L.append('### Needs escalation (reasoned, not guessed)')
    L.append('')
    tonal = sorted(r['tag'] for r in t.values() if r['tones'])
    L.append('- **Tonal languages, for Fable 5.1 at `high` (playbook Phase 6 rule): %s.** Reason: tone contours, tone sandhi and tone-bearing syllable length are set by the tone lines of the pack and the F0 control of the template; the harness measures a contour against the points asked, not whether the points are the language. Their layers above say where the ASR evidence points.' % ' '.join(tonal))
    L.append('- **Click languages: none**: no phoneme of the eSpeak NG tables of the 145 maps has a click letter (ǃ ǀ ǁ ǂ ʘ) in its IPA (checked over every `phonemes.map`); the clicks are in the master table (Phase 4) and no pack uses them.')
    L.append('- **Heavy allophony or sandhi, for Opus 5.5 at `high`:** languages whose written form leaves out what is said (Arabic and Hebrew vowels, Persian short vowels: `ar`, `he`, `fa`) and Indic schwa deletion and conjunct pronunciation (`hi`, `ur`, `bn`, `as`, `gu`, `kn`, `ml`, `mr`, `ne`, `or`, `pa`, `si`, `ta`, `te`, `sd`, `kok`, `bpy`). Reason: the fault, where there is one, is in how eSpeak NG reads the text (G2P layer), which needs the language own phonology to judge; an ASR score cannot say.')
    return '\n'.join(L)


def main():
    t = triage()
    with open(os.path.join(RES, 'triage.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(pass_cer=PASS_CER, g2p_gap=G2P_GAP, languages=t), f, ensure_ascii=False, indent=1, sort_keys=True)
    summary, rest = md_tables(t).split('\n\n', 1)
    head = ('Written by `harness/triage.py` from the measurements named in its header; the rules that give a layer are there too. '
            'Levels are those of the Phase 1 baseline: this phase measured no language afresh against references, so none changed. '
            'A3 on the final stage (`stage-dev`): 145 packs, 0 failures (20 packs failed it on the Phase 3 stage).\n\n')
    splice(os.path.join(DOCS, 'LANGUAGE_STATUS.md'), head + summary + '\n\n' + rest,
           '## Phase 6 (2026-10-11): failure-layer triage of every language')
    with open(os.path.join(DOCS, 'TRIAGE_PHASE6.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Phase 6 triage: fix list and needs-escalation list\n\n' + head + summary + '\n\n' + fixlist(t) + '\n')
    print(summary)
    return t


if __name__ == '__main__':
    main()
