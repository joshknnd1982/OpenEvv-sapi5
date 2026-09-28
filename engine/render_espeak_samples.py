"""Render every language read by eSpeak NG, one WAV each, through the engine
hosts the way SAPI speaks it: the pack's own sample sentence and a number, in
the first two presets (Adult Male 1 and Adult Female 1) one after the other.

    python engine/render_espeak_samples.py <evv_say.exe> <out-dir> [tag ...]

evv_say.exe is built by CMake (build_x64\\bin\\Release\\evv_say.exe) and
finds the packs, the hosts and the front-end the way the SAPI engine does.
"""
import os
import struct
import subprocess
import sys
import tempfile
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_wav(path):
    with wave.open(path, "rb") as w:
        return w.getframerate(), w.readframes(w.getnframes())


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    say, out = argv[0], argv[1]
    only = set(argv[2:])
    os.makedirs(out, exist_ok=True)
    langs = os.path.join(ROOT, "languages")
    done = 0
    for tag in sorted(os.listdir(langs)):
        ini = os.path.join(langs, tag, "language.ini")
        if not os.path.exists(os.path.join(langs, tag, "phonemes.map")) or (only and tag not in only):
            continue
        sample = ""
        sp = os.path.join(langs, tag, "sample.txt")
        if os.path.exists(sp):
            sample = open(sp, encoding="utf-8-sig").read().strip()
        if not sample:
            for line in open(ini, encoding="utf-8-sig"):
                if line.startswith("Name="):
                    sample = line.split("=", 1)[1].strip()
        text = sample + " 1 2 3, 25, 2026."
        pieces, rate = [], 11025
        with tempfile.TemporaryDirectory() as tmp:
            tf = os.path.join(tmp, "t.txt")
            with open(tf, "w", encoding="utf-8") as f:
                f.write(text)
            for preset in (1, 2):
                wf = os.path.join(tmp, "%d.wav" % preset)
                r = subprocess.run([say, tag, str(preset), "@" + tf, wf], capture_output=True)
                if r.returncode != 0:
                    print("%s: %s" % (tag, r.stderr.decode("utf-8", "replace").strip()))
                    break
                rate, frames = read_wav(wf)
                pieces.append(frames)
                pieces.append(b"\0\0" * (rate // 2))
        if len(pieces) < 4:
            continue
        with wave.open(os.path.join(out, tag + ".wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(b"".join(pieces))
        done += 1
    print("%d samples in %s" % (done, out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
