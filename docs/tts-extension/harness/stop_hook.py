"""A Claude Code Stop hook (Phase 1, step 8): a turn may not end while the smoke check fails,
but only when the engine or its language data has changed.

Scope: uncommitted changes (git status) under openevv/, languages/, engine/, frontend/ or
dist/espeak-ng-data/. With none, it says nothing and lets the turn end at once. With some, it
runs smoke.py (under a minute) and, if that fails, exits 2 with the reason on stderr, which keeps
Claude working. A second stop in a row (`stop_hook_active`) is let through, so it can never loop.

It is not installed by itself: OPEN_QUESTIONS.md has the settings lines for the human to add.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WATCHED = ['openevv', 'languages', 'engine', 'frontend', 'dist/espeak-ng-data']
VENV_PYTHON = os.path.join(os.path.expanduser('~'), 'OpenEvvBuild-ttsext', 'venv', 'Scripts', 'python.exe')


def main():
    try:
        event = json.loads(sys.stdin.read() or '{}')
    except ValueError:
        event = {}
    if event.get('stop_hook_active'):
        return 0
    r = subprocess.run(['git', 'status', '--porcelain', '--'] + WATCHED, cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    changed = [l for l in r.stdout.decode('utf-8', 'replace').splitlines() if l.strip()]
    if not changed:
        return 0
    python = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    s = subprocess.run([python, os.path.join(HERE, 'smoke.py')], cwd=ROOT, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONUTF8='1'), timeout=300)
    if s.returncode == 0:
        return 0
    tail = '\n'.join(s.stdout.decode('utf-8', 'replace').splitlines()[-12:])
    sys.stderr.write('The harness smoke check fails after changes to %s:\n%s\n'
                     'Fix it, or say why the change is intended (DECISIONS.md) and record the golden again.\n'
                     % (', '.join(sorted({l[3:].split('/')[0] for l in changed})), tail))
    return 2


if __name__ == '__main__':
    sys.exit(main())
