"""Try sentences of your own through the ASR round trip, for a diagnosis: nothing is written in the tree.

    python docs/tts-extension/harness/asr_try.py <tag> "<sentence>" ["<sentence>" ...] [--like TAG] [--cpu]

Each sentence is said by the engine (under EVV_STAGE like every render), heard by Whisper with
asr.py's own settings, and scored with asr.py's own normalisation: the reference, what Whisper
heard, and the sentence's CER and WER, then the totals. Whisper's language is the tag's (or --like's,
from asr/whisper_codes.json). Use it to test a hypothesis: the same sentence with a comma at a word
boundary, a word alone, a variant spelling. asr.py and check_language.py --asr say the standard
sentences; this says yours.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asr  # noqa: E402
import engine as E  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tag")
    ap.add_argument("sentences", nargs="+")
    ap.add_argument("--like")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    code = (asr.load_json("whisper_codes.json").get(a.like or a.tag) or {}).get("whisper")
    if not code:
        sys.exit("STOP: Whisper has no language for %s (asr/whisper_codes.json)" % (a.like or a.tag))
    model, device = asr.whisper(a.cpu)
    renders = E.render(a.tag, [("t%d" % i, "text", s) for i, s in enumerate(a.sentences)],
                       work=os.path.join(E.WORK, "asr_try", a.tag))
    hyps = []
    for s, r in zip(a.sentences, renders):
        segs, _ = model.transcribe(r["wav"], language=code, beam_size=5, condition_on_previous_text=False,
                                   vad_filter=False, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                                   compression_ratio_threshold=2.4)
        h = " ".join(x.text.strip() for x in segs)
        hyps.append(h)
        cer, wer = asr.score([s], [h], a.like or a.tag)
        print("said:  %s\nheard: %s\n       CER %.3f  WER %.3f" % (s, h, cer, wer))
    cer, wer = asr.score(a.sentences, hyps, a.like or a.tag)
    print("asr_try %s: %d sentences, CER %.3f, WER %.3f (%s, Whisper language %s)" % (
        a.tag, len(a.sentences), cer, wer, device, code))
    return 0


if __name__ == "__main__":
    sys.exit(main())
