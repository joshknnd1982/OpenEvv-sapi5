"""Render every preset voice of every language module with the engine's own
command-line driver, straight from the per-language build: no SAPI, no
registry, no installer (engine/build_modules.sh leaves an evv.exe beside each
language's modules). Writes one WAV per voice and one per language with all
eight voices in a row.
"""
import os
import struct
import subprocess
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("OPENEVV_WORK") or os.path.join(os.environ.get("LOCALAPPDATA", ROOT), "OpenEvvBuild")
MODULES = os.path.join(WORK, "modules")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "samples")

# tag: (ECI language id, display name, encoding, sample text)
LANGS = {
    "enus": (0x10000, "US English", "cp1252",
             "Hello. This is voice {n}, speaking US English through Open E V V. "
             "The quick brown fox jumps over the lazy dog, and 1,234 people arrived on March 5th."),
    "engb": (0x10001, "British English", "cp1252",
             "Hello. This is voice {n}, speaking British English through Open E V V. "
             "The colour of the programme was grey, and 1,234 people arrived on the 5th of March."),
    "dede": (0x40000, "German", "cp1252",
             "Guten Tag. Das ist Stimme {n}, sie spricht Deutsch. "
             "Zwölf Boxkämpfer jagen Viktor quer über den großen Sylter Deich."),
    "eses": (0x20000, "Castilian Spanish", "cp1252",
             "Hola. Esta es la voz {n}, hablando español de España. "
             "El veloz murciélago hindú comía feliz cardillo y kiwi."),
    "esus": (0x20001, "Latin American Spanish", "cp1252",
             "Hola. Esta es la voz {n}, hablando español de México. "
             "¿Cómo estás? Hoy es un buen día para aprender algo nuevo."),
    "frfr": (0x30000, "French", "cp1252",
             "Bonjour. Voici la voix {n}, qui parle français. "
             "Portez ce vieux whisky au juge blond qui fume."),
    "frca": (0x30001, "Canadian French", "cp1252",
             "Bonjour. Voici la voix {n}, qui parle français canadien. "
             "Il fait beau à Montréal aujourd'hui, et le hockey commence ce soir."),
    "itit": (0x50000, "Italian", "cp1252",
             "Buongiorno. Questa è la voce {n}, che parla italiano. "
             "Quel vituperabile xenofobo zelante assaggia il whisky ed esclama: alleluja!"),
    "plpl": (0x110000, "Polish", "utf-8",
             "Dzień dobry. To jest głos {n}, mówiący po polsku. "
             "Zażółć gęślą jaźń. Pchnąć w tę łódź jeża lub ośm skrzyń fig."),
    "jajp": (0x80000, "Japanese", "shift_jis",
             "こんにちは。これは音声{n}です。日本語を話しています。"
             "今日はいい天気ですね。"),
}


def read_wav(path):
    with wave.open(path, "rb") as w:
        return w.getframerate(), w.readframes(w.getnframes())


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_text.txt")
    report = []
    failures = 0
    for tag, (lang, name, enc, text) in LANGS.items():
        exe = os.path.join(MODULES, tag, f"evv-{tag}.exe")
        if not os.path.exists(exe):
            print(f"{tag}: no build", flush=True)
            failures += 1
            continue
        d = os.path.join(OUT, tag)
        os.makedirs(d, exist_ok=True)
        joined = b""
        rate = None
        for n in range(1, 9):
            with open(tmp, "wb") as f:
                f.write(text.format(n=n).encode(enc))
            out = os.path.join(d, f"{tag}-voice{n}.wav")
            r = subprocess.run([exe, "-v", str(n), "-f", tmp, "-o", out],
                               capture_output=True, timeout=120)
            ok = r.returncode == 0 and os.path.exists(out)
            secs = 0.0
            if ok:
                rate, pcm = read_wav(out)
                secs = len(pcm) / 2 / rate
                joined += pcm + b"\0\0" * int(rate * 0.6)
                ok = secs > 1.0
            if not ok:
                failures += 1
            line = f"{tag} voice {n}: {'OK ' if ok else 'FAIL'} {secs:6.2f} s  {r.stderr.decode(errors='replace').strip()}"
            print(line, flush=True)
            report.append(line)
        if joined:
            allp = os.path.join(OUT, f"{tag}-all-voices.wav")
            with wave.open(allp, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(rate)
                w.writeframes(joined)
    os.remove(tmp)
    with open(os.path.join(OUT, "render-report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print(f"failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
