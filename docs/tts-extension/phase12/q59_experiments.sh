#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
# Phase 12, Q59: what makes the switched packs hard to understand. Scratch stages outside the repository
# (%USERPROFILE%\OpenEvvBuild-ttsext\p12-q59\<variant>\languages\<tag>), each holding one pack's built files
# from stage-ipa with one change; the templates and front-end come from what ships. Whisper hears each pack's
# 8 standard sentences (harness/asr/sentences.json) through asr_try.py, or the sentences named.
cd "$(dirname "$0")/../../.."
W="$USERPROFILE/OpenEvvBuild-ttsext"; WW="$(cygpath -w "$W")"; PY="$W/venv/Scripts/python.exe"; E="$W/p12-q59"
export PYTHONUTF8=1 P12_PACK_ROOT="$WW\p12-switched-packs\packs"
variant() {  # name tag: make E/name/languages/tag from stage-ipa
  mkdir -p "$E/$1/languages/$2"; cp "$W/stage-ipa/languages/$2/"* "$E/$1/languages/$2/"; }
try() {  # label stage tag sentences...
  local label="$1" st="$2" tag="$3"; shift 3
  local r; r=$(EVV_STAGE="$st" EVV_HARNESS_WORK="$E/work-$label-$tag" "$PY" docs/tts-extension/harness/asr_try.py "$tag" "$@" 2>&1)
  echo "---- $tag, $label"; echo "$r" | grep -E "^(said|heard|asr_try)"; }
std() { "$PY" -c "
import json
d=json.load(open('docs/tts-extension/harness/asr/sentences.json',encoding='utf-8'))['languages']['$1']
print('\n'.join(x['text'] if isinstance(x,dict) else x for x in d['sentences'][:8]))"; }
echo "== 1. the 8 standard sentences: 1.3.0 (what ships), the switch (stage-ipa), the switch with its vowels unmoved"
for tag in id ru en-us-nyc; do
  variant unmoved $tag
  "$PY" docs/tts-extension/phase12/q59_vowels_unmoved.py $tag "$WW/stage-ipa/languages/$tag/sounds.map" "$WW/p12-q59/unmoved/languages/$tag/sounds.map"
  mapfile -t S < <(std $tag)
  try shipped "" $tag "${S[@]}"; try switched "$W/stage-ipa" $tag "${S[@]}"; try unmoved "$E/unmoved" $tag "${S[@]}"
done
ID3=("Ada baiknya tidak asal bicara." "Ibu ada di rumah." "Ada banyak bangunan tua yang terkenal di Kyoto.")
echo "== 2. id, three sentences: the switch; its level hold taken out (av, ah on every master line); its vowels on their legacy lines"
variant nohold id; sed -i -E '/^sound m[0-9]+ /{s/ ah=-?[0-9]+//; s/ av=-?[0-9]+//}' "$E/nohold/languages/id/sounds.map"
variant legacyvowels id
"$PY" docs/tts-extension/phase12/q59_vowels_legacy.py id v languages/id/sounds.map "$WW/stage-ipa/languages/id/sounds.map" "$WW/p12-q59/legacyvowels/languages/id/sounds.map"
try switched "$W/stage-ipa" id "${ID3[@]}"; try nohold "$E/nohold" id "${ID3[@]}"; try legacyvowels "$E/legacyvowels" id "${ID3[@]}"
echo "== 3. id on the switch: a sentence beginning with a vowel against one with the vowel inside"
try switched "$W/stage-ipa" id "Baiknya tidak asal bicara." "Kami ada di sini." "Ada baiknya tidak asal bicara." "Ibu ada di rumah."
