# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""The doctor: is this tree healthy enough to add or change a language? (playbook Phase 8, step 3)

    python engine/doctor.py            everything, with the full golden regression (about 25 to 40 minutes)
    python engine/doctor.py --quick    the same with the golden's smoke subset instead (about 2 minutes)
    python engine/doctor.py --print-queue   the verification queue as OPEN_QUESTIONS.md Q15 lists it

Run it with the harness venv's Python from the repository root (ADDING_A_LANGUAGE.md, "Setup"). It
changes no tracked file: the renders go to %TEMP%, and the checks it runs only read the tree (coverage
rewrites ipa/realized/<template>.map from the table, to the same bytes; the doctor says if it did not).

The checks, each PASS, WARN or FAIL; the exit code is 1 if any FAILED:
  env        the venv's modules, the built tools, the stage (EVV_STAGE, default
             %USERPROFILE%/OpenEvvBuild-ttsext/stage-dev), the eSpeak NG data, the Whisper model (WARN only)
  harness    harness/selftest.py --quick (the analyser on known signals and the engine facts)
  golden     harness/golden.py against golden-staged/ (--quick: golden.py --smoke)
  packs      engine/packs/test_packs.py; build_packs.py check (every pack builds to languages/)
  validate   validate_packs.py on every dialect and accent pack, then on the packs waiting to ship
             (packs-proposed/) and the worked examples (docs/tts-extension/examples/packs), and the self-tests of the validator, the
             normalizer and the feedback reader
  table      engine/ipa/table.py and its self-test (the master table's own rules)
  coverage   engine/ipa/coverage.py: every checklist symbol done, MISSING 0, BLOCKED 0, every proof on the map
  estimated  every `estimated` value of the master table is queued in OPEN_QUESTIONS.md Q15; one that is
             not, in an entry first committed more than --stale-days ago (default 14), FAILS (newer: WARN)
  docs       engine/check_readme.py (README links, paths, version, MIT wording) and engine/check_licences.py
             --headers (every tracked file in one licence class; Phase 10)
  placed     engine/check_espeak_packs.py: each pack read by eSpeak NG through its template's module, every
             phone placed where its map put it (Phase 13, D99); --quick: three packs whose diphthongs once
             lost their place (vi, en-gb-x-rp, en-us-nyc), the full run every pack (as build_all.bat does)
"""
import argparse
import datetime
import importlib
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HARNESS = os.path.join(ROOT, "docs", "tts-extension", "harness")
EXAMPLES = os.path.join(ROOT, "docs", "tts-extension", "examples", "packs")
PROPOSED = os.path.join(ROOT, "packs-proposed")
OPEN_QUESTIONS = os.path.join(ROOT, "docs", "tts-extension", "OPEN_QUESTIONS.md")
BUILD = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "OpenEvvBuild-ttsext")
STAGE = os.environ.get("EVV_STAGE") or os.path.join(BUILD, "stage-dev")
MODEL = os.environ.get("EVV_WHISPER_MODEL") or os.path.join(BUILD, "models", "faster-whisper-large-v3")

results = []


def report(name, state, line, detail=()):
    results.append((name, state))
    print("%-5s %-10s %s" % (state, name, line), flush=True)
    for d in detail:
        print("                 " + d, flush=True)


def run(args, timeout, env=None):
    """(exit code, every line printed, seconds)."""
    e = dict(os.environ, PYTHONUTF8="1", EVV_STAGE=STAGE)
    e.update(env or {})
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, "-B"] + args, cwd=ROOT, env=e, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        out = (p.stdout + p.stderr).splitlines()
        return p.returncode, out, time.time() - t0
    except subprocess.TimeoutExpired:
        return -1, ["timed out after %d s" % timeout], time.time() - t0


def last(lines, pattern):
    for line in reversed(lines):
        if re.search(pattern, line):
            return line.strip()
    return (lines[-1].strip() if lines else "(nothing printed)")


def step(name, args, timeout, ok_pattern, env=None, show=None):
    """Run one command: PASS when it exits 0 and prints its success line; the line (or the one matching
    `show`) is shown either way."""
    code, out, secs = run(args, timeout, env)
    good = code == 0 and re.search(ok_pattern, last(out, ok_pattern)) is not None
    line = last(out, show or ok_pattern)
    fails = [x.strip() for x in out if re.search(r"FAIL|REJECTED|Error|STOP", x)][:8]
    report(name, "PASS" if good else "FAIL", "%s  (%s, %.0f s)" % (
        line, " ".join([os.path.relpath(args[0], ROOT)] + args[1:2]), secs),
           [] if good else fails or out[-8:])
    return good, out


def check_env():
    missing = []
    for m in ("numpy", "scipy", "soundfile", "jiwer", "tomli"):
        try:
            importlib.import_module(m)
        except ImportError:
            missing.append(m)
    tools = [os.path.join(ROOT, "build_x64", "bin", "Release", x) for x in ("evv_render.exe", "evv_say.exe")]
    need = tools + [os.path.join(STAGE, "x64", "OpenEvvFrontend.exe"), os.path.join(STAGE, "languages", "dedx"),
                    os.path.join(ROOT, "dist", "espeak-ng-data", "phontab")]
    absent = [p for p in need if not os.path.exists(p)]
    line = "Python %s at %s; stage %s" % (sys.version.split()[0], sys.executable, STAGE)
    if missing or absent:
        report("env", "FAIL", line, ["module missing: %s" % m for m in missing] + ["missing: %s" % p for p in absent])
    else:
        report("env", "PASS", line)
    if not os.path.isdir(MODEL):
        report("env", "WARN", "no Whisper model at %s: asr.py cannot run (level 4 needs it)" % MODEL)


def queue_from_q15():
    """{(id, path)} listed in Q15, and the date it was written."""
    text = open(OPEN_QUESTIONS, encoding="utf-8").read()
    start = text.index("**Q15.")
    end = text.find("\n**Q16.", start)
    block = text[start:end]
    listed = set(re.findall(r"^- `([^`]+)` .*?: `([^`]+)`\s*$", block, re.M))
    when = re.search(r"values on (\d{4}-\d{2}-\d{2})", block)
    return listed, when.group(1) if when else None


def check_estimated(stale_days):
    sys.path.insert(0, os.path.join(ROOT, "engine", "ipa"))
    import table as T
    t = T.load()
    _, estimated = T.validate(t)
    now = set(tuple(x.split(" ", 1)) for x in estimated)
    listed, when = queue_from_q15()
    unqueued = sorted(now - listed)
    stale, fresh = [], []
    for sid, path in unqueued:
        days = age_days(os.path.join("ipa", "table", t.where[sid]), '[sound."%s"]' % sid)
        (fresh if days <= stale_days else stale).append("%s %s (%s, entry first committed %d days ago)" % (
            sid, path, t.where[sid], days))
    gone = sorted(listed - now)
    line = "%d estimated values in the table, %d queued in Q15 (written %s)" % (len(now), len(now & listed), when)
    if stale:
        report("estimated", "FAIL", line + "; %d not queued past %d days" % (len(stale), stale_days),
               stale[:8] + ["python engine/doctor.py --print-queue gives the list to paste into Q15"])
    elif fresh:
        report("estimated", "WARN", line + "; %d new, not yet queued" % len(fresh), fresh[:8])
    else:
        report("estimated", "PASS", line)
    if gone:
        report("estimated", "WARN", "%d entries of Q15 are no longer estimated (verified or changed): "
               "regenerate Q15 with --print-queue" % len(gone), ["%s %s" % g for g in gone[:5]])


def age_days(path, text):
    """Days since the first commit that added `text` (an entry's header) to the file: a later edit of
    the file does not reset it. 0 if no commit has it yet."""
    p = subprocess.run(["git", "log", "--reverse", "--format=%cs", "-S", text, "--", path], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
    s = p.stdout.split()
    if not s:
        return 0
    return (datetime.date.today() - datetime.date.fromisoformat(s[0])).days


def print_queue():
    sys.path.insert(0, os.path.join(ROOT, "engine", "ipa"))
    import table as T
    t = T.load()
    _, estimated = T.validate(t)
    print("Written by `python engine/doctor.py --print-queue` (the validator of `engine/ipa/table.py`); "
          "%d values on %s:" % (len(estimated), datetime.date.today().isoformat()))
    print()
    for x in estimated:
        sid, path = x.split(" ", 1)
        print("- `%s` %s: `%s`" % (sid, t.sounds[sid].get("ipa", ""), path))
    return 0


def git_realized():
    p = subprocess.run(["git", "status", "--porcelain", "--", "ipa/realized"], cwd=ROOT, capture_output=True, text=True)
    return p.stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true", help="the golden's smoke subset instead of the full run")
    ap.add_argument("--stale-days", type=int, default=14)
    ap.add_argument("--print-queue", action="store_true")
    a = ap.parse_args()
    if a.print_queue:
        return print_queue()
    t0 = time.time()
    print("doctor: %s, %s, stage %s" % (ROOT, "quick" if a.quick else "full", STAGE), flush=True)
    check_env()
    step("harness", [os.path.join(HARNESS, "selftest.py"), "--quick"], 900, r"== \d+ checks, \d+ passed, 0 failed")
    step("packs", [os.path.join(ROOT, "engine", "packs", "test_packs.py")], 900, r"^OK$", show=r"^Ran \d+ tests")
    step("packs", [os.path.join(ROOT, "engine", "packs", "build_packs.py"), "check"], 900,
         r"check: every file identical to languages/")
    step("master", [os.path.join(ROOT, "engine", "packs", "to_master.py"), "--check"], 1800,
         r"master check: \d+ packs at realization \"master\"; every one builds, no phoneme silent",
         env={"EVV_PACKS_EXTRA": os.pathsep.join((PROPOSED, EXAMPLES))})
    step("validate", [os.path.join(ROOT, "engine", "packs", "validate_packs.py")], 600, r"validate: \d+ packs, \d+ accepted, 0 rejected")
    for folder in (PROPOSED, EXAMPLES):
        tags = sorted(t for t in os.listdir(folder) if os.path.isfile(os.path.join(folder, t, "pack.toml")))             if os.path.isdir(folder) else []
        if tags:
            step("validate", [os.path.join(ROOT, "engine", "packs", "validate_packs.py")] + tags, 600,
                 r"validate: \d+ packs, \d+ accepted, 0 rejected",
                 env={"EVV_PACKS_EXTRA": os.pathsep.join((PROPOSED, EXAMPLES))})
    step("validate", [os.path.join(ROOT, "engine", "packs", "validate_packs.py"), "--selftest"], 600,
         r"validate selftest: (\d+) of \1 pass")
    step("validate", [os.path.join(ROOT, "engine", "authenticity", "normalize.py"), "--selftest"], 300,
         r"normalize selftest: (\d+) of \1 pass")
    step("validate", [os.path.join(ROOT, "engine", "review", "ingest_feedback.py"), "--selftest"], 600,
         r"ingest selftest: pass")
    step("table", [os.path.join(ROOT, "engine", "ipa", "table.py")], 300, r"; 0 problems;")
    step("table", [os.path.join(ROOT, "engine", "ipa", "table.py"), "--selftest"], 300,
         r"(\d+) planted faults, \1 refused")
    before = git_realized()
    good, out = step("coverage", [os.path.join(ROOT, "engine", "ipa", "coverage.py"), "--quiet"], 900,
                     r"MISSING 0, BLOCKED 0")
    if good:
        for pat in (r"state against proof: every entry", r"proof against map: every proof"):
            line = last(out, pat)
            report("coverage", "PASS" if re.search(pat, line) else "FAIL", line)
    after = git_realized()
    if after != before:
        report("coverage", "FAIL", "coverage changed ipa/realized/ (the table and the realized map disagree)",
               after.splitlines()[:5])
    check_estimated(a.stale_days)
    step("docs", [os.path.join(ROOT, "engine", "check_readme.py")], 120, r"check: pass")
    step("docs", [os.path.join(ROOT, "engine", "check_licences.py"), "--headers"], 120, r"check: pass")
    placed = [os.path.join(ROOT, "engine", "check_espeak_packs.py"), os.path.join(ROOT, "dist", "x64", "OpenEvvFrontend.exe"),
              os.path.join(ROOT, "dist", "espeak-ng-data")]
    step("placed", placed + (["vi", "en-gb-x-rp", "en-us-nyc"] if a.quick else []), 600 if a.quick else 3600,
         r"\d+ packs checked, 0 failed")
    if a.quick:
        step("golden", [os.path.join(HARNESS, "golden.py"), "--smoke"], 1200, r"golden: .* 0 FAILED")
    else:
        step("golden", [os.path.join(HARNESS, "golden.py")], 6000, r"golden: \d+ packs, \d+ cases, 0 FAILED")
    failed = [n for n, s in results if s == "FAIL"]
    warned = [n for n, s in results if s == "WARN"]
    print("doctor: %d checks, %d passed, %d warnings, %d FAILED (%s), %.0f s" % (
        len(results), len(results) - len(failed) - len(warned), len(warned), len(failed),
        ", ".join(sorted(set(failed))) or "none", time.time() - t0))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
