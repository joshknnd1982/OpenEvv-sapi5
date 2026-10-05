"""Smoke check (Phase 1, step 8): the harness's quick self-tests and a slice of the golden
regression, in under a minute. Exit 0 when both pass.

    python docs/tts-extension/harness/smoke.py

Run it after any change under openevv/, languages/, engine/ or dist/espeak-ng-data/; the full
regression (golden.py with no arguments) before committing such a change (R8).
"""

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    t0 = time.time()
    failed = []
    for name, args in (('selftest --quick', ['selftest.py', '--quick']), ('golden --smoke', ['golden.py', '--smoke'])):
        r = subprocess.run([sys.executable] + [os.path.join(HERE, args[0])] + args[1:],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONUTF8='1'))
        out = r.stdout.decode('utf-8', 'replace').strip().splitlines()
        summary = [l for l in out if l.startswith(('==', 'golden:', 'FAIL', '***', '   FAILED'))]
        print('%s: exit %d' % (name, r.returncode))
        for l in summary[-8:]:
            print('   ' + l)
        if r.returncode != 0:
            failed.append(name)
    print('smoke: %s in %.0f s' % ('FAILED (%s)' % ', '.join(failed) if failed else 'passed', time.time() - t0))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
