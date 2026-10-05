"""Stage rebuilt template modules in a data folder (DESIGN.md 11.2), never in languages/.

    python docs/tts-extension/harness/stage.py <built modules> <stage folder> [tags...]

<built modules> is engine/build_modules.sh's output folder (<tag>/openevv-<tag>-x64.dll and -x86.dll).
Each template is staged as <stage folder>/languages/<tag>/ with the shipped language.ini beside the
rebuilt DLLs; the product and the harness (EVV_STAGE=<stage folder>) read it before languages/.
Prints the size and SHA-256 of each staged file against the shipped one.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E     # noqa: E402

TEMPLATES = ['dedx', 'itix', 'esex', 'esux', 'engx', 'enux', 'frfx']


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    built, stage = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    if os.path.normcase(stage).startswith(os.path.normcase(E.LANGUAGES)):
        print('stage: refusing to stage inside languages/')
        return 2
    for tag in argv[2:] or TEMPLATES:
        dst = os.path.join(stage, 'languages', tag)
        os.makedirs(dst, exist_ok=True)
        shutil.copyfile(os.path.join(E.LANGUAGES, tag, 'language.ini'), os.path.join(dst, 'language.ini'))
        for bits in ('x64', 'x86'):
            name = 'openevv-%s-%s.dll' % (tag, bits)
            src = os.path.join(built, tag, name)
            if not os.path.exists(src):
                print('stage: %s was not built' % src)
                return 1
            shutil.copyfile(src, os.path.join(dst, name))
            shipped = os.path.join(E.LANGUAGES, tag, name)
            print('%-22s staged %9d %s   shipped %9d %s' % (name, os.path.getsize(src), sha(src)[:16],
                                                          os.path.getsize(shipped), sha(shipped)[:16]))
    print('staged in %s' % stage)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
