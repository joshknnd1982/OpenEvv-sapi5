"""Render every language read by eSpeak NG, one WAV each, through the engine
hosts the way SAPI speaks it: the pack's own sample sentence and some numbers
in the first two presets (Adult Male 1 and Adult Female 1) one after the
other, then a word of the sample spelled, letter by letter, as a screen
reader's spell command has it, and then some punctuation marks spelled.

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

# What to spell where the sample has no word of letters: the first letters
# of the language's own alphabet (Bishnupriya Manipuri, Shan) or of its
# romanisation (Hakka, Xextan).
SPELL = {
    "bpy": "\u0995\u0996\u0997\u0998\u0999",
    "shn": "\u1075\u1076\u1004\u1078\u101e",
    "hak": "ngai",
    "xex": "bdfgh",
}


# Spelled after the word: the marks a screen reader user meets most.
PUNCTUATION = ". , ? ! ( ) - @ %"


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
        if not os.path.exists(ini) or (only and tag not in only):
            continue
        if "[Frontend]" not in open(ini, encoding="utf-8-sig").read():
            continue
        sample = ""
        sp = os.path.join(langs, tag, "sample.txt")
        if os.path.exists(sp):
            sample = open(sp, encoding="utf-8-sig").read().strip()
        if not sample:
            for line in open(ini, encoding="utf-8-sig"):
                if line.startswith("Name="):
                    sample = line.split("=", 1)[1].strip()
        text = sample + " 1 2 3, 25, 144, 2026, 1000000. -7, 50%."
        # the longest word of the sample, preferring one with a letter that is
        # not plain ASCII, to be spelled
        words = [w.strip(".,;:!?\"'()[]\u3002\uff0c\u0964") for w in sample.split()]
        letters = [w for w in words if len(w) >= 3 and all(ch.isalpha() or ord(ch) > 0x2ff for ch in w)]
        if not letters:
            # romanisations that write the tone as a digit: the digit is spelled too
            letters = [w for w in words if len(w) >= 3 and any(ch.isalpha() for ch in w)
                       and all(ch.isalnum() or ord(ch) > 0x2ff for ch in w)]
        letters.sort(key=lambda w: (any(ord(ch) > 0x7f for ch in w), len(w)), reverse=True)
        spelled = letters[0][:12] if letters else SPELL.get(tag, "")
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
            # a word, then punctuation marks, spelled as a screen reader spells
            for n, what in enumerate((spelled, PUNCTUATION) if len(pieces) >= 4 else ()):
                if not what:
                    continue
                sf = os.path.join(tmp, "s%d.txt" % n)
                with open(sf, "w", encoding="utf-8") as f:
                    f.write(what)
                wf = os.path.join(tmp, "spelled%d.wav" % n)
                r = subprocess.run([say, "--spell", tag, "1", "@" + sf, wf], capture_output=True)
                if r.returncode == 0:
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
