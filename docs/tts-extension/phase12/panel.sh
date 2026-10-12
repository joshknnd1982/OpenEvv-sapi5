#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
# Phase 12 continued (D98): one iteration of the generator on a panel of languages, outside the repository.
#
#   bash docs/tts-extension/phase12/panel.sh <name> [tags...]
#
# to_master.py on the panel into %USERPROFILE%\OpenEvvBuild-ttsext\p12c\packs-<name> (packs/ is not written),
# build_packs.py build into p12c\stage-<name>\languages, the built maps copied to p12c\maps as <tag>-<name>.map,
# then ablate.py says the 8 standard sentences of each and Whisper hears them (results p12c\<name>.json, log
# p12c\<name>.log). The default panel: 12 languages Whisper understood well in 1.3.0, on all seven templates.
set -u
cd "$(dirname "$0")/../../.."
W="$USERPROFILE/OpenEvvBuild-ttsext"; WW="$(cygpath -w "$W")"; PY="$W/venv/Scripts/python.exe"
name="$1"; shift
T="${*:-id ru en-us-nyc en-029 hr sl nl hu ca sw fr-be pt-br}"
export PYTHONUTF8=1
"$PY" engine/packs/to_master.py $T --out "$WW\\p12c\\packs-$name" > "$W/p12c/to_master-$name.log" 2>&1 || { tail -5 "$W/p12c/to_master-$name.log"; exit 1; }
tail -1 "$W/p12c/to_master-$name.log"
mkdir -p "$W/p12c/stage-$name/languages" "$W/p12c/maps"
"$PY" engine/packs/build_packs.py build "$WW\\p12c\\stage-$name\\languages" $T --root "$WW\\p12c\\packs-$name" > "$W/p12c/build-$name.log" 2>&1 || { tail -5 "$W/p12c/build-$name.log"; exit 1; }
for t in $T; do cp "$W/p12c/stage-$name/languages/$t/sounds.map" "$W/p12c/maps/$t-$name.map"; done
EVV_STAGE="$WW\\stage-ipa" P12_PACK_ROOT="$WW\\p12-switched-packs\\packs" EVV_HARNESS_WORK="$WW\\p12c\\work" \
  "$PY" docs/tts-extension/phase12/ablate.py "$WW\\p12c\\$name.json" --maps "$WW\\p12c\\maps" --tags $T --variants "$name" \
  > "$W/p12c/$name.log" 2>&1
tail -$(( $(echo $T | wc -w) + 2 )) "$W/p12c/$name.log"
