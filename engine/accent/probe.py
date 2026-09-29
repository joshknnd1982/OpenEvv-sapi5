"""Drives an openevv probe and reads what it said.

The probe is upstream openevv's test driver (openevv/cli/probe.c), built for
one language module with `make win-probe'. It speaks a text into a wave file
and, with two environment variables set, writes down every frame of
parameters the synthesiser was given (EVV_KLATT_TAP) and which phone every
stretch of those frames was taken to be (EVV_ACCENT_TRACE). Those two files
are what the measurements in this folder are made from.

    from probe import Probe
    p = Probe('dede')
    r = p.speak('`[.1ta.0ta]')
    r.frames     the frames, a dict of parameter name to value each
    r.trace      the stretches, in order
    r.samples    the sound, as numpy int16
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

LANGUAGE = {
    'enus': 0x10000, 'engb': 0x10001, 'eses': 0x20000, 'esus': 0x20001,
    'frfr': 0x30000, 'frca': 0x30001, 'dede': 0x40000, 'itit': 0x50000,
    'plpl': 0x110000, 'jajp': 0x80000,
}

# Turns the accent layer on and says nothing else, so that a stretch is
# traced and no frame is changed.
INERT = '{A v=1}'


def probe_dirs():
    dirs = []
    if os.environ.get('OPENEVV_PROBES'):
        dirs.append(os.environ['OPENEVV_PROBES'])
    work = os.environ.get('OPENEVV_WORK') or os.path.join(os.environ.get('LOCALAPPDATA', ''), 'OpenEvvBuild')
    dirs.append(os.path.join(work, 'probes'))
    dirs.append(os.path.join(ROOT, 'openevv', 'build'))
    return dirs


def find_probe(tag):
    names = ['probe-%s.exe' % tag]
    if tag == 'enus':
        names.append('probe.exe')
    for d in probe_dirs():
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    raise SystemExit('no probe for %s: build one with engine\\build_probes.cmd %s' % (tag, tag))


class Said(object):
    pass


class Probe(object):
    def __init__(self, tag, language=None, exe=None):
        self.tag = tag
        self.exe = exe or find_probe(tag)
        self.language = language if language is not None else LANGUAGE.get(tag, 0)

    def speak(self, text, mode='a', encoding='utf-8', env=None, trace=True, keep=None):
        work = tempfile.mkdtemp(prefix='evv')
        try:
            with open(os.path.join(work, 'case.txt'), 'wb') as f:
                f.write(text.encode(encoding) if isinstance(text, str) else text)
            e = dict(os.environ)
            e['EVV_LANGUAGE'] = hex(self.language)
            e['EVV_KLATT_TAP'] = 'tap.tsv'
            if trace:
                e['EVV_ACCENT_TRACE'] = 'trace.tsv'
            if env:
                e.update(env)
            p = subprocess.run([self.exe, '@case.txt', 'case.wav', mode], cwd=work, env=e,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            r = Said()
            r.code = p.returncode
            r.said = p.stdout.decode('latin-1')
            r.err = p.stderr.decode('latin-1')
            r.phonemes = ''
            for line in r.said.splitlines():
                if line.startswith('speak: phonemes '):
                    r.phonemes = line[len('speak: phonemes '):]
            r.frames = []
            tap = os.path.join(work, 'tap.tsv')
            if os.path.exists(tap):
                with open(tap) as f:
                    names = f.readline().split()
                    for line in f:
                        if line.strip():
                            r.frames.append(dict(zip(names, map(int, line.split()))))
            t = 0
            for fr in r.frames:
                fr['at'] = t
                t += fr['step']
            r.length = t
            r.trace = []
            tr = os.path.join(work, 'trace.tsv')
            if os.path.exists(tr):
                with open(tr) as f:
                    for line in f:
                        c = line.rstrip('\n').split('\t')
                        if len(c) >= 10:
                            r.trace.append(dict(name=c[0], a=int(c[1]), b=int(c[2]), out_a=int(c[3]),
                                                out_b=int(c[4]), meant=c[5], sound=c[6], tone=c[7],
                                                stress=int(c[8]), flags=int(c[9])))
            r.samples = np.zeros(0, dtype=np.int16)
            r.rate = 11025
            wav = os.path.join(work, 'case.wav')
            if os.path.exists(wav) and os.path.getsize(wav) > 44:
                with wave.open(wav, 'rb') as w:
                    r.rate = w.getframerate()
                    r.samples = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).copy()
                if keep:
                    import shutil
                    shutil.copy(wav, keep)
            return r
        finally:
            for n in os.listdir(work):
                try:
                    os.remove(os.path.join(work, n))
                except OSError:
                    pass
            try:
                os.rmdir(work)
            except OSError:
                pass

    def frames_of(self, r, stretch):
        """The frames that sounded in one stretch of a trace."""
        return [f for f in r.frames if stretch['out_a'] <= f['at'] < stretch['out_b']]


def quote(phone):
    """A phone as an annotation writes it."""
    return "'%s'" % phone if len(phone) > 1 else phone
