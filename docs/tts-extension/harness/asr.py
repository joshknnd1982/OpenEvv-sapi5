"""ASR round trip (Phase 1, step 4): synthesize test sentences per language, transcribe them with a
multilingual recogniser, and score character and word error rates (CER, WER).

    recogniser  OpenAI Whisper large-v3 (MIT weights) through faster-whisper / CTranslate2 (MIT),
                from EVV_WHISPER_MODEL (default %USERPROFILE%\\OpenEvvBuild-ttsext\\models\\
                faster-whisper-large-v3). The language is given, not detected: the question is
                whether the words are understood, not whether the language is recognised.
    sentences   asr/sentences.json: Common Voice sentence text (CC0) and, for languages it lacks,
                Tatoeba (CC BY 2.0 FR, each sentence's id and author kept). See REFERENCES.md.
    languages   asr/whisper_codes.json: our tag -> Whisper's code, or null where Whisper has none.

A language with no Whisper code or no sentences is recorded as "ASR unavailable" with the reason,
never given a score. A low score is not a verdict on its own: Whisper is weaker on some languages
than others, and a synthetic voice is far from its training data; the score is a baseline to
compare against later, and its failures are triaged by report.py.

    python docs/tts-extension/harness/asr.py                 every language -> results/asr.json
    python docs/tts-extension/harness/asr.py hi sw enus      some
    python docs/tts-extension/harness/asr.py --cpu           without the GPU

Needs the venv with faster-whisper and jiwer (PROJECT_STATE.md, Environment).
"""

import argparse
import json
import os
import re
import sys
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E   # noqa: E402

MODEL = os.environ.get('EVV_WHISPER_MODEL') or os.path.join(
    os.path.expanduser('~'), 'OpenEvvBuild-ttsext', 'models', 'faster-whisper-large-v3')
RESULTS = os.path.join(HERE, 'results')


def load_json(name):
    with open(os.path.join(HERE, 'asr', name), encoding='utf-8') as f:
        return json.load(f)


def whisper(cpu=False):
    """The model, on the GPU when it works (float16: CTranslate2 has no INT8 on sm_120), else CPU."""
    if not cpu:
        # pip's cuBLAS is not on the DLL search path on Windows (faster-whisper's README covers
        # Linux only): put it there before CTranslate2 loads.
        import site
        for sp in site.getsitepackages():
            d = os.path.join(sp, 'nvidia', 'cublas', 'bin')
            if os.path.isdir(d):
                os.add_dll_directory(d)
                os.environ['PATH'] = d + os.pathsep + os.environ.get('PATH', '')
    from faster_whisper import WhisperModel
    if not cpu:
        try:
            m = WhisperModel(MODEL, device='cuda', compute_type='float16')
            return m, 'cuda/float16'
        except Exception as e:      # no usable GPU: say so and go on
            print('GPU unavailable (%s); using the CPU' % e, file=sys.stderr)
    return WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=os.cpu_count() or 4), 'cpu/int8'


def normalise(s):
    """Lower case, NFC, punctuation and symbols out, runs of space as one. The same for both sides."""
    s = unicodedata.normalize('NFKC', s).lower()
    s = ''.join(ch if unicodedata.category(ch)[0] not in 'PS' else ' ' for ch in s)
    return re.sub(r'\s+', ' ', s).strip()


# Tags whose text is in a script Whisper does not write for that language: no score until the
# references are converted (Phase 6). asr/whisper_codes.json says which script Whisper writes.
OTHER_SCRIPT = {'cmn-latn-pinyin', 'yue-latn-jyutping', 'fa-latn'}

# Languages written without spaces: their WER means little, CER is the score.
NO_SPACES = {'cmn', 'yue', 'ja', 'jajp', 'th', 'lo', 'my', 'km', 'bo', 'hak'}


# Serbian is written in two alphabets that map one to one (Vuk Karadžić's Cyrillic and Gaj's
# Latin), and Whisper answers in Latin: both sides are compared in Latin.
SR_LATIN = dict(zip('абвгдђежзијклљмнњопрстћуфхцчџш',
                    ['a', 'b', 'v', 'g', 'd', 'đ', 'e', 'ž', 'z', 'i', 'j', 'k', 'l', 'lj', 'm', 'n', 'nj', 'o', 'p',
                     'r', 's', 't', 'ć', 'u', 'f', 'h', 'c', 'č', 'dž', 'š']))
TRANSLITERATE = {'sr': lambda s: ''.join(SR_LATIN.get(ch, ch) for ch in s)}


def score(refs, hyps, tag=None):
    import jiwer
    conv = TRANSLITERATE.get(tag, lambda s: s)
    r = [conv(normalise(x)) for x in refs]
    h = [conv(normalise(x)) for x in hyps]
    pairs = [(a, b) for a, b in zip(r, h) if a]
    if not pairs:
        return None, None
    r, h = zip(*pairs)
    cer = jiwer.cer(list(r), list(h))
    wer = jiwer.wer(list(r), list(h))
    return round(cer, 4), round(wer, 4)


def run(tags, cpu=False, limit=8, preset=1):
    sentences = load_json('sentences.json')['languages']
    codes = load_json('whisper_codes.json')
    model, device = None, None
    out = {}
    for tag in tags:
        code = (codes.get(tag) or {}).get('whisper')
        sents = [s['text'] for s in ((sentences.get(tag) or {}).get('sentences') or [])][:limit]
        rec = dict(tag=tag, whisper=code, note=(codes.get(tag) or {}).get('whisper_note', ''),
                   source=(sentences.get(tag) or {}).get('source'), n=len(sents))
        if not code:
            rec.update(status='ASR unavailable', reason='Whisper large-v3 has no language for this tag')
        elif not sents:
            rec.update(status='ASR unavailable', reason='no CC0 / CC BY sentence set has this language')
        elif tag in OTHER_SCRIPT:
            rec.update(status='ASR unavailable', reason='Whisper writes another script; references not converted yet')
        if 'status' in rec:
            out[tag] = rec
            print('%-8s %s: %s' % (tag, rec['status'], rec['reason']), flush=True)
            continue
        if model is None:
            model, device = whisper(cpu)
        t0 = time.time()
        renders = E.render(tag, [('s%d' % i, 'text', s) for i, s in enumerate(sents)], preset=preset,
                           work=os.path.join(E.WORK, 'asr', tag))
        hyps = []
        for r in renders:
            # Whisper's own defence against hallucinated repetition: fall back to higher
            # temperatures when the output compresses too well (am scored CER 2.29 without it)
            segs, _ = model.transcribe(r['wav'], language=code, beam_size=5, condition_on_previous_text=False,
                                       vad_filter=False, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                                       compression_ratio_threshold=2.4)
            hyps.append(' '.join(s.text.strip() for s in segs))
        cer, wer = score(sents, hyps, tag)
        rec.update(status='scored', device=device, preset=preset, cer=cer,
                   wer=None if tag in NO_SPACES else wer, seconds=round(time.time() - t0, 1),
                   pairs=[dict(ref=a, hyp=b) for a, b in zip(sents, hyps)])
        out[tag] = rec
        print('%-8s CER %.3f  WER %s  (%d sentences, %s, %.0f s)' % (
            tag, cer, '%.3f' % wer if rec['wer'] is not None else '  -  ', len(sents), device, rec['seconds']), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description='ASR round trip: synthesize, transcribe, score.')
    ap.add_argument('tags', nargs='*')
    ap.add_argument('--cpu', action='store_true')
    ap.add_argument('--limit', type=int, default=8)
    a = ap.parse_args()
    tags = a.tags or [t for t, p in E.packs().items() if p.kind != 'template']
    res = run(tags, cpu=a.cpu, limit=a.limit)
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, 'asr.json')
    old = {}
    if a.tags and os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            old = json.load(f).get('languages', {})
    old.update(res)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(model='whisper large-v3 (faster-whisper %s)' % __import__('faster_whisper').__version__,
                       date=time.strftime('%Y-%m-%d'), languages=old), f, ensure_ascii=False, indent=1, sort_keys=True)
    scored = [r for r in res.values() if r['status'] == 'scored']
    print('asr: %d languages, %d scored, %d unavailable -> %s' % (len(res), len(scored), len(res) - len(scored), path))


if __name__ == '__main__':
    main()
