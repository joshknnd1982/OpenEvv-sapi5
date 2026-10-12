#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
# Phase 12, step 4: measure every switched pack under EVV_STAGE=stage-ipa (playbook Phase 12; D97).
#
#   bash docs/tts-extension/phase12/measure_all.sh build|golden|report|faults|asr|diag [tags...]
#
#   build    build_packs.py build <stage-ipa>/languages for the packs read by eSpeak NG (or the tags given)
#   golden   golden.py --record into harness/golden-ipa/ (every pack, or the tags given): an intended change, R8
#   report   report.py on golden-ipa/ (EVV_GOLDEN): check A and B, levels, results/status.json, LANGUAGE_STATUS.md
#   faults   the phonemes check A finds silent or swapped (A0, A1) -> phase12/faults.json, fed to to_master.py
#   asr      asr.py over every pack (results/asr.json)
#   diag     diag.py over every pack (results/diag.json)
# Logs in %USERPROFILE%\OpenEvvBuild-ttsext\p12_<step>.log; the last lines are printed.
set -u
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
W="$USERPROFILE/OpenEvvBuild-ttsext"
PY="$W/venv/Scripts/python.exe"
H="$REPO/docs/tts-extension/harness"
export PYTHONUTF8=1 EVV_STAGE="$W/stage-ipa" EVV_HARNESS_WORK="$W/p12-measure-work" EVV_GOLDEN="$H/golden-ipa"
step="$1"; shift
log="$W/p12_$step.log"
switched() { "$PY" -c "
import sys; sys.path.insert(0, r'$(cygpath -w "$REPO")\engine\packs')
import packlib as L
print(' '.join(t for t in L.list_tags() if (L.resolve(t)[0].get('engine') or {}).get('realization') == 'master'))"; }
start=$(date +%s)
case "$step" in
  build)  tags="${*:-$(switched)}"; [ -n "$tags" ] || { echo "no switched packs found"; exit 2; }; "$PY" "$REPO/engine/packs/build_packs.py" build "$W/stage-ipa/languages" $tags > "$log" 2>&1 ;;
  golden) "$PY" "$H/golden.py" --record --golden "$H/golden-ipa" "$@" > "$log" 2>&1 ;;
  report) "$PY" "$H/report.py" --no-pictures > "$log" 2>&1 ;;
  faults) "$PY" "$REPO/docs/tts-extension/phase12/faults.py" "$H/results/status.json" "$REPO/docs/tts-extension/phase12/faults.json" > "$log" 2>&1 ;;
  asr)    "$PY" "$H/asr.py" "$@" > "$log" 2>&1 ;;
  diag)   "$PY" "$H/diag.py" "$@" > "$log" 2>&1 ;;
  *) echo "unknown step $step"; exit 2 ;;
esac
rc=$?
echo "$step exit: $rc after $(( $(date +%s) - start )) s" >> "$log"
tail -4 "$log"
exit $rc
