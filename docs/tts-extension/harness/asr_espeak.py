"""ASR round trip on eSpeak NG's own voice (Phase 6, triage): the same sentences, the same recogniser,
the same scoring as asr.py, but spoken by eSpeak NG itself with the voice a pack names.

Why: a pack's ASR error can come from the layer that reads the text (eSpeak NG's rules for the
language: G2P), from this engine's sounds, melody or timing, or from the recogniser and the
reference sentences. eSpeak NG's own voice reads the text with the same rules, so where it fails
the same sentences too, the fault is upstream of this engine (or the recogniser's). Where it does
not, the fault is in what this engine does with the phonemes. It is evidence, not a verdict: eSpeak NG's
own audio is a formant voice with its own faults.

    python docs/tts-extension/harness/asr_espeak.py [tag ...]      -> results/asr_espeak.json

Needs the venv (faster-whisper, jiwer), eSpeak NG's espeak-ng.exe (EVV_ESPEAK_EXE, default the
frontend build in %LOCALAPPDATA%\\OpenEvvBuild\\frontend-x64\\bin) and dist/espeak-ng-data.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import asr as A  # noqa: E402

EXE = os.environ.get('EVV_ESPEAK_EXE') or os.path.join(
    os.environ.get('LOCALAPPDATA', ''), 'OpenEvvBuild', 'frontend-x64', 'bin', 'espeak-ng.exe')
DATA = os.environ.get('EVV_ESPEAK_DATA') or os.path.join(ROOT, 'dist', 'espeak-ng-data')
RESULTS = os.path.join(HERE, 'results')
WORK = os.path.join(os.environ.get('TEMP', '.'), 'OpenEvvTests', 'asr_espeak')


def voice_of(tag):
    with open(os.path.join(ROOT, 'languages', tag, 'language.ini'), encoding='utf-8') as f:
        m = re.search(r'^Voice=(.+)$', f.read(), re.M)
    return m.group(1).strip() if m else None


def speak(voice, text, out):
    src = out[:-4] + '.txt'
    with open(src, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text + '\n')
    subprocess.run([EXE, '--path=' + os.path.dirname(DATA), '-v', voice, '-w', out, '-f', src],
                   check=True, capture_output=True, timeout=120)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tags', nargs='*')
    ap.add_argument('--limit', type=int, default=8)
    a = ap.parse_args()
    base = json.load(open(os.path.join(RESULTS, 'asr.json'), encoding='utf-8'))['languages']
    tags = a.tags or sorted(t for t, r in base.items() if r.get('status') == 'scored')
    codes = A.load_json('whisper_codes.json')
    model, device = A.whisper()
    out = {}
    os.makedirs(WORK, exist_ok=True)
    for tag in tags:
        voice = voice_of(tag)
        code = (codes.get(tag) or {}).get('whisper')
        refs = [p['ref'] for p in base[tag].get('pairs', [])][:a.limit]
        if not voice or not code or not refs:
            continue
        t0 = time.time()
        hyps = []
        try:
            for i, s in enumerate(refs):
                wav = os.path.join(WORK, '%s_%d.wav' % (tag, i))
                speak(voice, s, wav)
                segs, _ = model.transcribe(wav, language=code, beam_size=5, condition_on_previous_text=False,
                                           vad_filter=False, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                                           compression_ratio_threshold=2.4)
                hyps.append(' '.join(x.text.strip() for x in segs))
        except Exception as e:
            out[tag] = dict(tag=tag, status='unavailable', reason='%s: %s' % (type(e).__name__, e))
            print('%-8s unavailable: %s' % (tag, e), flush=True)
            continue
        cer, wer = A.score(refs, hyps, tag)
        out[tag] = dict(tag=tag, status='scored', voice=voice, device=device, n=len(refs), cer=cer,
                        wer=None if tag in A.NO_SPACES else wer, seconds=round(time.time() - t0, 1),
                        pairs=[dict(ref=x, hyp=y) for x, y in zip(refs, hyps)])
        print('%-8s eSpeak NG own voice %-18s CER %.3f   this engine CER %s' % (
            tag, voice, cer, base[tag].get('cer')), flush=True)
    path = os.path.join(RESULTS, 'asr_espeak.json')
    old = {}
    if a.tags and os.path.exists(path):
        old = json.load(open(path, encoding='utf-8')).get('languages', {})
    old.update(out)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(model=base_model(), date=time.strftime('%Y-%m-%d'), exe=os.path.basename(EXE), languages=old),
                  f, ensure_ascii=False, indent=1, sort_keys=True)
    print('asr_espeak: %d languages -> %s' % (len(out), path))


def base_model():
    return json.load(open(os.path.join(RESULTS, 'asr.json'), encoding='utf-8')).get('model')


if __name__ == '__main__':
    main()
