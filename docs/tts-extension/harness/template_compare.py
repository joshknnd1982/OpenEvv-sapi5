"""The template comparison (DESIGN.md 13.2, step (e) of Phase 3A). MIT licence.

A handful of languages that Whisper knows well, each built with the present generator
(engine/make_espeak_packs.py, unchanged) for every one of the seven template modules, into a
scratch stage, never into languages/; each built pack is measured as every pack is: check A
(engine fidelity) and check B (reference ranges) over its golden cases, and the speech-recognition
round trip over its eight sentences. It settles which template carries the proofs of the master
table (DESIGN.md 3.4), and how much of the German-based template's low scores (F13) is the
template's doing.

    python docs/tts-extension/harness/template_compare.py [--langs nl pt ru tr id] [--no-asr]

The scratch stage is <harness work>/tcmp: the staged template modules (EVV_STAGE's, the defect
fixed) copied in, and the built packs beside them as <lang>-x-t<template>. Results go to
results/template_compare.json and a table on the screen.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SOURCE_STAGE = os.environ.get('EVV_STAGE') or ''
WORK = os.environ.get('EVV_HARNESS_WORK') or os.path.join(tempfile.gettempdir(), 'OpenEvvTests', 'harness')
TCMP = os.path.join(WORK, 'tcmp')
# the comparison's own stage: set before the harness is imported, which reads it once
os.environ['EVV_STAGE'] = TCMP
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'engine'))
sys.path.insert(0, os.path.join(ROOT, 'engine', 'accent'))
import engine as E  # noqa: E402

TEMPLATES = ['dede', 'eses', 'itit', 'engb', 'esus', 'frfr', 'enus']
ESPEAK_SRC = os.environ.get('ESPEAK_NG_SOURCE_DIR') or os.path.join(os.environ.get('LOCALAPPDATA', ''), 'OpenEvvBuild',
                                                                    'dev', 'espeak-ng')


def build(langs):
    """Each language for each template, with the generator's own functions and its choice
    replaced by each template in turn. Returns {(lang, template): tag}."""
    import make_espeak_packs as MP
    import espeak_phonemes as EP
    import mapwriter
    import prosody
    import subprocess
    if not SOURCE_STAGE or not os.path.isdir(os.path.join(SOURCE_STAGE, 'languages')):
        raise SystemExit('set EVV_STAGE to the stage holding the seven template modules')
    if os.path.isdir(TCMP):
        shutil.rmtree(TCMP)
    shutil.copytree(SOURCE_STAGE, TCMP)
    lang_dir = os.path.join(TCMP, 'languages')
    dump = subprocess.run([E.FRONTEND, '--data', E.FE_DATA, '--dump-phonemes'], capture_output=True, check=True)
    tables = dict((t['table'], t) for t in json.loads(dump.stdout.decode('utf-8')))
    samples = MP.test_sentences(ESPEAK_SRC)
    voices = {v['tag']: v for v in MP.all_voices(ESPEAK_SRC) if not MP.is_duplicate(v)}
    out = {}
    for lang in langs:
        v = voices[lang]
        text, source = MP.sample_text(v, samples, ESPEAK_SRC)
        stats = MP.run_stats(E.FRONTEND, E.FE_DATA, v['id'], text)
        best, _ = EP.choose_template(stats)
        counts = {}
        for s in stats:
            counts[s['table']] = counts.get(s['table'], 0) + s['count']
        table_names = sorted(counts, key=lambda k: -counts[k])
        for tmpl in TEMPLATES:
            clone = mapwriter.CLONE.get(tmpl, tmpl)
            tag = '%s-x-t%s' % (lang, clone)
            dst = os.path.join(lang_dir, tag)
            os.makedirs(dst, exist_ok=True)
            t = EP.TEMPLATES[tmpl]
            EP.write_map(os.path.join(dst, 'phonemes.map'), t, table_names, tables, stats, v['id'], v['name'])
            mapwriter.write_map(os.path.join(dst, 'sounds.map'), lang, tmpl, table_names, tables, stats, v['id'],
                                v['name'], prosody.load_profile(lang))
            MP.write_ini(os.path.join(dst, 'language.ini'), v, t, MP.lcid_for(v['code']), 900, source)
            ini = os.path.join(dst, 'language.ini')
            with open(ini, encoding='utf-8') as f:
                s = f.read().replace('Tag=%s\n' % lang, 'Tag=%s\n' % tag)
            with open(ini, 'w', encoding='utf-8', newline='\n') as f:
                f.write(s)
            out[(lang, clone)] = tag
        print('%-4s built for 7 templates (the generator would choose %s; shipped: %s)' % (
            lang, mapwriter.CLONE.get(best, best), E.pack(lang).template), flush=True)
    return out


def measure(lang, tag, asr_model):
    import golden as G
    import report as RP
    import asr as AS
    p = E.pack(tag)
    r = G.run_pack(tag, jobs=4)
    gold = dict(cases=r['cases'])
    a = RP.check_a(gold, p.phone_module)
    b = RP.check_b(p, gold, RP.locale_of(E.pack(lang)))
    res = dict(tag=tag, cases=len(r['cases']), errors=len(r['errors']), a_passed=a['passed'],
               a2_rate=a['a2_rate'], a0_substituted=a['substituted'], a1_silent=a['a1_silent'],
               b_passed=b['passed'], b_rate=b.get('rate'), b_checks=b['checks'], b_why=b.get('why'))
    if asr_model is not None:
        model, device = asr_model
        sentences = AS.load_json('sentences.json')['languages']
        code = (AS.load_json('whisper_codes.json').get(lang) or {}).get('whisper')
        sents = [s['text'] for s in ((sentences.get(lang) or {}).get('sentences') or [])][:8]
        renders = E.render(tag, [('s%d' % i, 'text', s) for i, s in enumerate(sents)],
                           work=os.path.join(E.WORK, 'tcmp-asr', tag))
        hyps = []
        for rr in renders:
            segs, _ = model.transcribe(rr['wav'], language=code, beam_size=5, condition_on_previous_text=False,
                                       vad_filter=False, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                                       compression_ratio_threshold=2.4)
            hyps.append(' '.join(s.text.strip() for s in segs))
        cer, wer = AS.score(sents, hyps, lang)
        res.update(cer=round(cer, 3), wer=round(wer, 3) if wer is not None else None,
                   pairs=[dict(ref=x, hyp=y) for x, y in zip(sents, hyps)])
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--langs', nargs='*', default=['nl', 'pt', 'ru', 'tr', 'id'])
    ap.add_argument('--no-asr', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    built = build(a.langs)
    E._packs = None          # read the packs again, the built ones with them
    model = None
    if not a.no_asr:
        import asr as AS
        model = AS.whisper()
    results = {}
    for (lang, clone), tag in sorted(built.items()):
        r = measure(lang, tag, model)
        r.update(lang=lang, template=clone, shipped=E.pack(lang).template)
        results[tag] = r
        print('%-4s %-5s%s  A %-4s (A2 %s)  B %-4s (%s of %d)  CER %s' % (
            lang, clone, '*' if clone == r['shipped'] else ' ', 'pass' if r['a_passed'] else 'FAIL', r['a2_rate'],
            {True: 'pass', False: 'FAIL', None: '-'}[r['b_passed']], r['b_rate'], r['b_checks'], r.get('cer')),
            flush=True)
    out = os.path.join(HERE, 'results', 'template_compare.json')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(langs=a.langs, templates=TEMPLATES, stage_from=SOURCE_STAGE, seconds=round(time.time() - t0),
                       results=results), f, ensure_ascii=False, indent=1, sort_keys=True)
    # the summary: each template's median over the languages
    print('\ntemplate  CER median (by language)                      A pass  B rate median')
    for clone in sorted({r['template'] for r in results.values()}):
        rows = [r for r in results.values() if r['template'] == clone]
        cers = sorted(r['cer'] for r in rows if r.get('cer') is not None)
        brs = sorted(r['b_rate'] for r in rows if r.get('b_rate') is not None)
        med = lambda xs: xs[len(xs) // 2] if xs else None  # noqa: E731
        print('%-8s  %-6s %-38s %d/%d    %s' % (clone, med(cers), ' '.join('%s %.2f' % (r['lang'], r['cer'])
                                                                         for r in sorted(rows, key=lambda r: r['lang'])
                                                                         if r.get('cer') is not None),
                                           sum(1 for r in rows if r['a_passed']), len(rows), med(brs)))
    print('written %s; %.0f s' % (os.path.relpath(out, ROOT), time.time() - t0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
