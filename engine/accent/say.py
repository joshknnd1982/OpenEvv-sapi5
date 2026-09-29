#!/usr/bin/env python3
"""Says a text the way an installed language pack would, and keeps what the
engine did: for measuring a language without anybody listening.

The text is read by OpenEvvFrontend with the pack's eSpeak NG voice and its
map, and what that writes is spoken by the probe of the pack's module. What
comes back is the probe's: the frames the synthesiser was given, which phone
each stretch of them was, and the sound.

    python engine/accent/say.py <pack folder> "text" [out.wav]
    python engine/accent/say.py <pack folder> @file.txt [out.wav]
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from probe import Probe  # noqa: E402

FRONTEND = os.environ.get('OPENEVV_FRONTEND') or os.path.join(ROOT, 'dist', 'x64', 'OpenEvvFrontend.exe')
DATA = os.environ.get('OPENEVV_ESPEAK_DATA') or os.path.join(ROOT, 'dist', 'espeak-ng-data')


def read_ini(path):
    out = {}
    sec = None
    for line in open(path, encoding='utf-8-sig'):
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        if line.startswith('['):
            sec = line.strip('[]')
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            out[(sec, k.strip())] = v.strip()
    return out


class Pack(object):
    def __init__(self, folder):
        self.folder = folder
        ini = read_ini(os.path.join(folder, 'language.ini'))
        self.tag = ini.get(('Language', 'Tag'))
        self.template = ini.get(('Language', 'Template'))
        self.voice = ini.get(('Frontend', 'Voice'))
        self.map = os.path.join(folder, ini.get(('Frontend', 'Sounds'), ini.get(('Frontend', 'Map'), 'sounds.map')))
        self.language = int(ini.get(('Language', 'Id'), '0'), 16)
        self.probe = Probe(self.template, language=self.language)

    def written(self, text, spell=False, punctuation=False, phonemes=False, frontend=None, data=None):
        """What the front-end makes of a text."""
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.txt', delete=False) as f:
            f.write(text)
            tmp = f.name
        try:
            cmd = [frontend or FRONTEND, '--data', data or DATA, '--voice', self.voice, '--map', self.map,
                   '--file', tmp]
            if spell:
                cmd.append('--spell')
            if punctuation:
                cmd.append('--punctuation')
            if phonemes:
                cmd.append('--phonemes')
            r = subprocess.run(cmd, capture_output=True, timeout=120)
            if r.returncode != 0:
                raise RuntimeError(r.stderr.decode('utf-8', 'replace'))
            return r.stdout.decode('utf-8', 'replace').strip()
        finally:
            os.unlink(tmp)

    def say(self, text, keep=None, voice='`vb65 `vf30 ', **how):
        """Says the text with the first of the pack's voices: its pitch and
        its pitch fluctuation go before the text as the engine's own
        annotations, which is how the speech engine sets them."""
        w = self.written(text, **how)
        r = self.probe.speak(voice + w, keep=keep)
        r.written = w
        return r


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    pack = Pack(argv[0])
    text = argv[1]
    if text.startswith('@'):
        text = open(text[1:], encoding='utf-8').read()
    r = pack.say(text, keep=argv[2] if len(argv) > 2 else None)
    print(r.written)
    for t in r.trace:
        print('%-4s %5d %5d  %-5s %-6s %-5s stress %d' % (t['name'], t['out_a'], t['out_b'], t['meant'],
                                                          t['sound'], t['tone'], t['stress']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
