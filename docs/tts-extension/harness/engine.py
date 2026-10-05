"""Renders cases through the real engine and reads back what it did (Phase 1, step 1).

Every case is spoken by `evv_render.exe` (src/tools/evv_render.cpp) in a host of its own, after
the host's warm-up: the history the product gives its first utterance, and the one `evv_say`
gives. Three of the engine's own logs, all in the shipped modules, say what it did:

    EVV_KLATT_TAP     every frame the synthesiser received, 62 integers a frame (after the accent layer)
    EVV_ACCENT_TRACE  every phone: what it was meant to be, its sound, tone, stress and output span
    EVV_ARRAY_TAP     the breakpoints each frame was interpolated from, one run per phoneme

They are what "the engine realized what was asked" (check A) is read from. Nothing in the engine
is changed.

How a case's phones are found:

    trace   packs read by eSpeak NG, the template modules, and US English: the accent layer logs
            every phone. A native module is given `{A v=1}` (the layer on, nothing changed) only
            where that leaves the sound byte for byte as it was (`traces()` checks, once a module).
    runs    the other native modules (dede, engb, eses, esus, frfr, frca, itit, jajp, plpl) do
            not know the markup and would speak it, so their phones are the array log's runs,
            one a phoneme and a silence at the end of each sentence, labelled with the phones
            asked for when the input named them and `seg1`, `seg2`... when it was text.

The logs hold the warm-up too. The case is cut out of them by counting: the warm-up's frames are
known (from the trace where the host's front-end traced it, or from a calibration render of an
empty case) and every frame after them is the case's. Frames that do not add up exactly, or that
do not last as long as the sound, are an error and the case is spoken again (see `_one`).

Inputs (see `case_text`):
    text      plain text, read as the product reads it
    espeak    eSpeak NG phoneme names, said as they stand (packs read by eSpeak NG)
    ipa       IPA, turned into eSpeak NG phoneme names (packs read by eSpeak NG) or into the
              module's own phones (native packs); a symbol with no counterpart is an error
    module    the module's own annotation, `[.1ta.0ta] (native packs)
    annotated the front-end's output as it stands (packs read by eSpeak NG)

A pack read by eSpeak NG speaks `text` through the host's own front-end, exactly as the product
does. Every other input goes through `OpenEvvFrontend --phonemes` and then `evv_render
--annotated`: the same module, voice and settings without the host's front-end. Its frames are the
product's (selftest.py, 'annotated path'); its samples differ in the noise generator's state
because that host warmed up on different words.

Run from the repository root (any Python 3.8+ with numpy):

    python docs/tts-extension/harness/engine.py hi ipa "ʈəmaːʈər" out.wav
    python docs/tts-extension/harness/engine.py enus text "Hello there." out.wav --preset 2
    python docs/tts-extension/harness/engine.py hi text "नमस्ते" out.wav --override "s5 vot=80"

Each writes out.wav and out.json: the input, the annotated text, every frame and every phone.
"""

import argparse
import concurrent.futures
import configparser
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

RENDER = os.environ.get('EVV_RENDER') or os.path.join(ROOT, 'build_x64', 'bin', 'Release', 'evv_render.exe')
FRONTEND = os.environ.get('EVV_FRONTEND') or os.path.join(ROOT, 'dist', 'x64', 'OpenEvvFrontend.exe')
FE_DATA = os.path.join(ROOT, 'dist', 'espeak-ng-data')
LANGUAGES = os.path.join(ROOT, 'languages')

# Outside the repository: it sits in OneDrive, which should not sync scratch audio.
WORK = os.environ.get('EVV_HARNESS_WORK') or os.path.join(tempfile.gettempdir(), 'OpenEvvTests', 'harness')

# Staged modules (DESIGN.md 11.2): a data folder whose languages\<tag>\ holds rebuilt template
# modules. The product reads it before the shipped languages\ (F16), so a module staged there
# speaks instead of the shipped one, which is never touched. Unset: the shipped modules.
STAGE = os.environ.get('EVV_STAGE') or ''

INERT = '{A v=1}'

PARM_NAMES = [
    'step', 'f0', 'av', 'oq', 'tl', 'fl', 'di', 'ah', 'af', 'f1', 'b1', 'df1', 'db1', 'f2', 'b2', 'f3',
    'b3', 'f4', 'b4', 'f5', 'b5', 'f6', 'b6', 'f7', 'b7', 'f8', 'b8', 'fnp', 'bnp', 'fnz', 'bnz', 'ftp',
    'btp', 'ftz', 'btz', 'a1f', 'a2f', 'a3f', 'a4f', 'a5f', 'a6f', 'a7f', 'a8f', 'ab', 'b1f', 'b2f', 'b3f',
    'b4f', 'b5f', 'b6f', 'b7f', 'b8f', 'anv', 'a1v', 'a2v', 'a3v', 'a4v', 'a5v', 'a6v', 'a7v', 'a8v', 'atv']
P = {n: i for i, n in enumerate(PARM_NAMES)}

# The product's defaults, except that annotations are honoured (a module's own phones are an
# input) and no dictionary of the user's or the community's changes a word. OPENEVV_DATA points
# at an empty folder for the same reason.
SETTINGS = (
    '[General]\r\n'
    'SampleRate=1\r\n'          # eciSampleRate 1 = 11025 Hz, the synthesiser's own rate
    'Annotations=1\r\n'
    'UserDictionaries=0\r\n'
    'CommunityDictionary=0\r\n'
    'LogLevel=0\r\n'
)

# How far the sound's length may be from the frames'. Measured over the self-test's renders
# (selftest.py, 'frames against sound'): the frames outlast the sound by 1.6 to 3.6 ms (66 renders, 2026-10-05).
SAMPLE_SLACK_MS = 6
# ...and grows with length, each sentence being trimmed on its own (a 5.6 s case: 12.8 ms).
SAMPLE_SLACK_PER_S = 2.5

TRIES = 5


class HarnessError(Exception):
    pass


# ---- packs ---------------------------------------------------------------------------------------

class Pack(object):
    def __init__(self, tag, ini, folder):
        self.tag = tag
        self.dir = folder
        lang = ini['Language'] if ini.has_section('Language') else {}
        self.name = lang.get('Name', tag)
        self.template = lang.get('Template', '') or ''
        self.hidden = lang.get('Hidden', '0') == '1'
        fe = ini['Frontend'] if ini.has_section('Frontend') else None
        self.voice = fe.get('Voice', '') if fe is not None else ''
        sounds = fe.get('Sounds', '') if fe is not None else ''
        self.sounds_map = os.path.join(folder, sounds) if sounds else ''
        if self.voice:
            self.kind = 'espeak'
        elif self.hidden:
            self.kind = 'template'
        else:
            self.kind = 'native'
        self.module_tag = self.template or tag
        # the IBM module whose phone set this one has: a template module is a clone of one
        # (openevv/accents/<tag>/recipe, "template <tag>")
        self.phone_module = self.module_tag
        recipe = os.path.join(ROOT, 'openevv', 'accents', self.module_tag, 'recipe')
        if os.path.exists(recipe):
            with open(recipe, encoding='utf-8') as f:
                for line in f:
                    w = line.split('#', 1)[0].split()
                    if len(w) == 2 and w[0] == 'template':
                        self.phone_module = w[1]

    def module(self, bits):
        name = 'openevv-%s-x%s.dll' % (self.module_tag, '64' if bits == 64 else '86')
        staged = os.path.join(STAGE, 'languages', self.module_tag, name) if STAGE else ''
        return staged if staged and os.path.exists(staged) else os.path.join(LANGUAGES, self.module_tag, name)

    def __repr__(self):
        return 'Pack(%s, %s)' % (self.tag, self.kind)


_packs = None


def packs():
    global _packs
    if _packs is None:
        _packs = {}
        for tag in sorted(os.listdir(LANGUAGES)):
            ini_path = os.path.join(LANGUAGES, tag, 'language.ini')
            if not os.path.exists(ini_path):
                continue
            ini = configparser.ConfigParser(strict=False, interpolation=None)
            ini.optionxform = str
            with open(ini_path, encoding='utf-8-sig') as f:
                ini.read_file(f)
            _packs[tag] = Pack(tag, ini, os.path.join(LANGUAGES, tag))
    return _packs


def pack(tag):
    p = packs().get(tag)
    if p is None:
        raise HarnessError('no language pack %s' % tag)
    return p


# ---- the front-end and the inputs ----------------------------------------------------------------

def frontend(p, text, phonemes=False, map_path=None):
    """What the front-end hands the module for this text: annotated text, as the host gets it."""
    if p.kind != 'espeak':
        raise HarnessError('%s is not read by eSpeak NG' % p.tag)
    fd, path = tempfile.mkstemp(suffix='.txt', prefix='evvfe')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(text.encode('utf-8'))
        cmd = [FRONTEND, '--data', FE_DATA, '--voice', p.voice, '--map', map_path or p.sounds_map, '--file', path]
        if phonemes:
            cmd.append('--phonemes')
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    finally:
        os.remove(path)
    if r.returncode != 0:
        raise HarnessError('front-end failed for %s: %s' % (p.tag, r.stderr.decode('utf-8', 'replace').strip()))
    return r.stdout.decode('utf-8').rstrip('\r\n')


def override_map(p, overrides, work):
    """A copy of the pack's sounds.map with `sound` lines replaced or added: ["s5 vot=80", ...].

    Each override names a sound and gives its whole definition, as a `sound` line of
    docs/SOUNDS.md does; the pack's own file is never touched."""
    if p.kind != 'espeak':
        raise HarnessError('overrides need a pack read by eSpeak NG')
    with open(p.sounds_map, encoding='utf-8') as f:
        lines = f.read().split('\n')
    for ov in overrides:
        sid, _, body = ov.strip().partition(' ')
        line = 'sound %s %s' % (sid, body.strip())
        for i, l in enumerate(lines):
            w = l.split()
            if len(w) >= 2 and w[0] == 'sound' and w[1] == sid:
                lines[i] = line
                break
        else:
            lines.append(line)
    os.makedirs(work, exist_ok=True)
    path = os.path.join(work, 'override-%s.map' % hashlib.sha256('\n'.join(overrides).encode()).hexdigest()[:12])
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    return path


def case_text(p, kind, text, bits, map_path=None):
    """(text for evv_render, annotated?, front-end output, module phones asked for)."""
    if p.kind == 'espeak':
        if kind == 'text' and not map_path:
            return text, False, None, None
        if kind == 'text':
            out = frontend(p, text, map_path=map_path)
        elif kind == 'annotated':
            out = text
        elif kind == 'espeak':
            out = frontend(p, '[[%s]]' % text, phonemes=True, map_path=map_path)
        elif kind == 'ipa':
            import ipa as ipa_mod
            out = frontend(p, '[[%s]]' % ipa_mod.to_espeak(p, text), phonemes=True, map_path=map_path)
        else:
            raise HarnessError('input %s needs a native pack; %s is read by eSpeak NG' % (kind, p.tag))
        return out, True, out, None
    if kind in ('espeak', 'annotated'):
        raise HarnessError('input %s needs a pack read by eSpeak NG; %s is %s' % (kind, p.tag, p.kind))
    asked = None
    if kind == 'ipa':
        import ipa as ipa_mod
        text = ipa_mod.to_module(p, text)
    if kind in ('ipa', 'module'):
        import ipa as ipa_mod
        asked = ipa_mod.module_phones(p, text)
    elif kind != 'text':
        raise HarnessError('unknown input kind %s' % kind)
    if traces(p, bits):
        text = INERT + text
    return text, False, None, asked


# ---- one render ----------------------------------------------------------------------------------

def _settings(work):
    s = os.path.join(work, 'settings.ini')
    if not os.path.exists(s):
        os.makedirs(os.path.join(work, 'data'), exist_ok=True)
        with open(s, 'w', newline='') as f:
            f.write(SETTINGS)
    return s


def _run(p, preset, bits, case_id, text, annotated, d, trace=True, array=False):
    """evv_render once, in folder d. Returns the paths and the sound; raises on a failed run."""
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    with open(os.path.join(d, 'case.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('%s\t%s\n' % (case_id, text.replace('\n', ' ')))
    work = os.path.dirname(d)
    env = dict(os.environ)
    env['OPENEVV_SETTINGS'] = _settings(work)
    env['OPENEVV_DATA'] = STAGE or os.path.join(work, 'data')
    out = dict(tap=os.path.join(d, 'tap.tsv'), trace=os.path.join(d, 'trace.tsv') if trace else None,
               array=os.path.join(d, 'array.txt') if array else None, wav=os.path.join(d, case_id + '.wav'))
    env['EVV_KLATT_TAP'] = out['tap']
    for var, key in (('EVV_ACCENT_TRACE', 'trace'), ('EVV_ARRAY_TAP', 'array')):
        if out[key]:
            env[var] = out[key]
        else:
            env.pop(var, None)
    cmd = ([RENDER] + (['--annotated'] if annotated else []) +
           [p.tag, str(preset), os.path.join(d, 'case.tsv'), d, str(bits)])
    t0 = time.time()
    r = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    out['elapsed'] = time.time() - t0
    if r.returncode != 0:
        raise HarnessError('%s %s: evv_render failed: %s' % (p.tag, case_id, r.stderr.decode('utf-8', 'replace').strip()))
    if os.path.exists(out['wav']):
        out['x'], out['rate'] = read_wav(out['wav'])
    else:
        out['x'], out['rate'] = np.zeros(0, np.int16), 11025
    return out


def read_tap(path):
    if not os.path.exists(path):
        raise HarnessError('no frame log %s' % path)
    with open(path) as f:
        head = f.readline().split()
        if head != PARM_NAMES:
            raise HarnessError('frame log header is not the 62 names expected: %s' % path)
        rows = [line.split('\t') for line in f if line.strip()]
    bad = [i for i, r in enumerate(rows) if len(r) != 62]
    if bad:
        raise HarnessError('frame log cut short at row %d' % bad[0])
    try:
        return np.array(rows, dtype=np.int64).reshape(-1, 62)
    except ValueError:      # cut exactly at a tab: 62 fields, the last one empty
        raise HarnessError('frame log cut short (a row that is not 62 numbers)')


def read_trace(path):
    phones = []
    if not path or not os.path.exists(path):
        return phones
    with open(path, encoding='utf-8') as f:
        for line in f:
            c = line.rstrip('\n').split('\t')
            if len(c) < 13:
                continue        # "sentence: ..." lines: the module's own settings, said again
            phones.append(dict(name=c[0], eng_a=int(c[1]), eng_b=int(c[2]), out_a=int(c[3]), out_b=int(c[4]),
                               meant=c[5], sound=c[6], tone=c[7], stress=int(c[8]), flags=int(c[9]),
                               on=c[10], off=c[11], record=[int(x) for x in c[12].split('.')], source='trace'))
    return phones


def read_runs(path):
    """The array log's runs, in order: [number of frames in each]. Each 'run' line opens one."""
    runs = []
    if not os.path.exists(path):
        raise HarnessError('no array log %s' % path)
    with open(path) as f:
        for line in f:
            if line.startswith('run '):
                runs.append(0)
            elif line.startswith('frame ') and runs:
                runs[-1] += 1
    return runs


def sentences(phones):
    """The trace in sentences: the output clock starts again at each one."""
    out, cur = [], []
    for ph in phones:
        if cur and ph['out_a'] < cur[-1]['out_b']:
            out.append(cur)
            cur = []
        cur.append(ph)
    if cur:
        out.append(cur)
    return out


def frame_times(frames):
    """Start of each frame in ms from the start of the case."""
    return np.concatenate([[0], np.cumsum(frames[:, 0])[:-1]]).astype(float)


def read_wav(path):
    with wave.open(path, 'rb') as w:
        rate = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).copy()
    return x, rate


# ---- what a module can do, and its warm-up (measured once, cached) -------------------------------

_cache_lock = threading.Lock()
_key_locks = {}


def _cache_file():
    return os.path.join(WORK, 'module_facts.json')


def _load_cache():
    try:
        with open(_cache_file(), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _facts(key, measure):
    """A fact about a module, measured once per DLL build (cached under its size and time).

    Threads asking for the same fact wait for one measurement; processes (golden.py runs packs
    in several) merge into the cache file and replace it whole, so it is never half written."""
    with _cache_lock:
        lock = _key_locks.setdefault(key, threading.Lock())
    with lock:
        cache = _load_cache()
        if key in cache:
            return cache[key]
        value = measure(os.path.join(WORK, '_facts', hashlib.sha256(key.encode()).hexdigest()[:16]))
        with _cache_lock:
            cache = _load_cache()
            cache[key] = value
            os.makedirs(WORK, exist_ok=True)
            tmp = '%s.%d.%d.tmp' % (_cache_file(), os.getpid(), threading.get_ident())
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=1, sort_keys=True)
            for _ in range(20):
                try:
                    os.replace(tmp, _cache_file())
                    break
                except PermissionError:      # another process is reading it this instant
                    time.sleep(0.05)
        return value


def _stamp(p, bits):
    st = os.stat(p.module(bits))
    return '%d-%d' % (st.st_size, int(st.st_mtime))


def traces(p, bits):
    """Whether the module logs its phones under `{A v=1}` and sounds byte for byte the same."""
    if p.kind != 'native':
        return True

    def measure(d):
        plain = _run(p, 1, bits, 'plain', '`[.1ta.0ta]', False, os.path.join(d, 'plain'), trace=False)
        marked = _run(p, 1, bits, 'marked', INERT + '`[.1ta.0ta]', False, os.path.join(d, 'marked'))
        same = np.array_equal(plain['x'], marked['x'])
        return bool(same and read_trace(marked['trace']))
    return _facts('traces/%s/%d/%s' % (p.tag, bits, _stamp(p, bits)), measure)


def warmup(p, preset, bits, annotated):
    """How many frames the host's warm-up makes before a case, from a render of nothing."""
    def measure(d):
        for attempt in range(TRIES):
            r = _run(p, preset, bits, 'empty', '', annotated, os.path.join(d, 'empty'), trace=False)
            try:
                return int(len(read_tap(r['tap'])))
            except HarnessError:
                continue
        raise HarnessError('%s: no complete warm-up log in %d attempts' % (p.tag, TRIES))
    return _facts('warmup/%s/%d/%d/%d/%s' % (p.tag, preset, bits, int(annotated), _stamp(p, bits)), measure)


# ---- cutting the case out of the logs ------------------------------------------------------------

def split_by_trace(frames, phones, warm):
    """warm: the warm-up's frames, or None where the warm-up is the trace's first sentence."""
    sents = sentences(phones)
    if warm is None:
        if not sents:
            raise HarnessError('no warm-up in the trace')
        warm_ms = sents[0][-1]['out_b']
        sents = sents[1:]
        steps = np.cumsum(frames[:, 0])
        hit = np.nonzero(steps == warm_ms)[0]
        if len(hit) == 0:
            raise HarnessError('no frame ends the traced warm-up at %d ms' % warm_ms)
        warm = int(hit[-1]) + 1      # after any frame of no length at the boundary
    if not sents:
        raise HarnessError('the trace has no phones for the case')
    case = frames[warm:]
    case_ms = sum(s[-1]['out_b'] for s in sents)
    if int(case[:, 0].sum()) != case_ms:
        raise HarnessError('the case\'s frames last %d ms and its traced phones %d ms'
                           % (int(case[:, 0].sum()), case_ms))
    out, base = [], 0
    for s in sents:
        for ph in s:
            q = dict(ph)
            q['start_ms'] = base + ph['out_a']
            q['end_ms'] = base + ph['out_b']
            out.append(q)
        base += s[-1]['out_b']
    return case, out


def split_by_runs(frames, runs, warm, asked):
    if sum(runs) != len(frames):
        raise HarnessError('the array log has %d frames and the frame log %d' % (sum(runs), len(frames)))
    case = frames[warm:]
    edges = np.cumsum([0] + runs)
    if warm not in edges:
        raise HarnessError('no run starts where the warm-up ends (frame %d)' % warm)
    first = int(np.nonzero(edges == warm)[0][-1])
    case_runs = runs[first:]
    t = frame_times(case)
    ends = np.cumsum(case[:, 0])
    labels = None
    if asked is not None and len(case_runs) == len(asked) + 1:
        labels = list(asked) + ['#']
    out, i = [], 0
    for k, n in enumerate(case_runs):
        if n == 0:
            continue
        name = labels[k] if labels else 'seg%d' % (k + 1)
        out.append(dict(name=name, meant=name if labels else '-', sound='-', tone='-', stress=-1, flags=-1,
                        on='-', off='-', record=None, source='runs',
                        start_ms=int(t[i]), end_ms=int(ends[i + n - 1])))
        i += n
    return case, out


def _one(p, preset, bits, case_id, text, annotated, asked, work, folder):
    """One case in a host of its own; spoken again if its logs do not add up.

    Under load the wrapper sometimes ends a host that has not left within its grace
    (HostPool::stop, 1.5 s), and the frame log then loses its last buffer. That shows as a cut
    last line, or frames that do not add up to the warm-up and the case, or frames that do not
    last as long as the sound. The engine is deterministic for a given history, so a retry gives
    the same case or fails the same way.
    """
    by_trace = p.kind == 'espeak' or traces(p, bits)
    fe_in_host = p.kind == 'espeak' and not annotated
    warm = None if fe_in_host else warmup(p, preset, bits, annotated)
    last = None
    for attempt in range(1, TRIES + 1):
        r = _run(p, preset, bits, 'case', text, annotated, os.path.join(work, folder),
                 trace=by_trace, array=not by_trace)
        x, rate = r['x'], r['rate']
        try:
            frames = read_tap(r['tap'])
            if by_trace:
                case, phones = split_by_trace(frames, read_trace(r['trace']), warm)
            else:
                case, phones = split_by_runs(frames, read_runs(r['array']), warm, asked)
            case_ms = int(case[:, 0].sum())
            gap = case_ms - len(x) * 1000.0 / rate
            if not 0 <= gap <= SAMPLE_SLACK_MS + SAMPLE_SLACK_PER_S * case_ms / 1000.0:
                raise HarnessError('the frames last %d ms and the sound %.1f ms' % (case_ms, len(x) * 1000.0 / rate))
        except HarnessError as e:
            last = '%s (attempt %d, %.2f s)' % (e, attempt, r['elapsed'])
            continue
        return dict(wav=r['wav'], rate=rate, n_samples=int(len(x)), case_ms=case_ms,
                    warmup_frames=int(len(frames) - len(case)), attempts=attempt,
                    segmentation='trace' if by_trace else 'runs',
                    wav_sha256=hashlib.sha256(open(r['wav'], 'rb').read()).hexdigest(),
                    frames=case, phones=phones)
    raise HarnessError('%s %s: no complete logs in %d attempts; last: %s' % (p.tag, case_id, TRIES, last))


def render(tag, cases, preset=1, bits=64, jobs=None, work=None, map_path=None):
    """Speaks each (id, kind, text) case in a host of its own. Returns one dict a case, in order.

    map_path: a sounds.map to read instead of the pack's (see override_map).
    """
    p = pack(tag)
    work = work or os.path.join(WORK, tag)
    os.makedirs(work, exist_ok=True)
    # Each case's folder is numbered: Windows folder names ignore case, and `v_a` and `v_A` would
    # otherwise share one (it happened: selftest.py, 'engine realises F2').
    prepared = []
    for i, (case_id, kind, text) in enumerate(cases):
        said, annotated, fe_out, asked = case_text(p, kind, text, bits, map_path)
        folder = '%04d_%s' % (i, re.sub(r'[^A-Za-z0-9_.-]', '_', case_id))[:60]
        prepared.append((case_id, kind, text, said, annotated, fe_out, asked, folder))
    jobs = jobs or min(8, os.cpu_count() or 2)

    def go(item):
        case_id, kind, text, said, annotated, fe_out, asked, folder = item
        r = _one(p, preset, bits, case_id, said, annotated, asked, work, folder)
        r.update(id=case_id, tag=tag, pack_kind=p.kind, module=p.module_tag, preset=preset, bits=bits,
                 input=dict(kind=kind, text=text, said=said, annotated=annotated, frontend_output=fe_out,
                            map=map_path or p.sounds_map or None))
        return r

    if jobs == 1 or len(prepared) == 1:
        return [go(i) for i in prepared]
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        return list(ex.map(go, prepared))


def to_json(r):
    """A rendering as JSON: what was asked, what the engine used, where the sound is."""
    q = {k: v for k, v in r.items() if k != 'frames'}
    q['frames'] = dict(names=PARM_NAMES, rows=r['frames'].tolist())
    return q


def main():
    ap = argparse.ArgumentParser(description='Render one case through the real engine: WAV + JSON of what it used.')
    ap.add_argument('tag')
    ap.add_argument('kind', choices=['text', 'espeak', 'ipa', 'module', 'annotated'])
    ap.add_argument('text')
    ap.add_argument('out_wav')
    ap.add_argument('--preset', type=int, default=1)
    ap.add_argument('--bits', type=int, default=64, choices=[32, 64])
    ap.add_argument('--override', action='append', default=[],
                    help='"sN key=value ..." replaces or adds a sound in a copy of the pack\'s sounds.map')
    a = ap.parse_args()
    map_path = override_map(pack(a.tag), a.override, os.path.join(WORK, a.tag)) if a.override else None
    r = render(a.tag, [('case', a.kind, a.text)], preset=a.preset, bits=a.bits, jobs=1, map_path=map_path)[0]
    shutil.copy(r['wav'], a.out_wav)
    r['wav'] = os.path.abspath(a.out_wav)
    with open(os.path.splitext(a.out_wav)[0] + '.json', 'w', encoding='utf-8') as f:
        json.dump(to_json(r), f, ensure_ascii=False)
    print('%s: %d samples at %d Hz, %d ms, %d frames, %d phones (%s): %s' % (
        a.tag, r['n_samples'], r['rate'], r['case_ms'], len(r['frames']), len(r['phones']), r['segmentation'],
        ' '.join(ph['name'] for ph in r['phones'])))
    if r['input']['frontend_output']:
        print('front-end: %s' % r['input']['frontend_output'])


if __name__ == '__main__':
    main()
