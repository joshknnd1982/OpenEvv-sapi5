#!/usr/bin/env bash
# Builds one OpenEVV engine module per language, 32-bit and 64-bit, from the
# openevv sources in ../openevv, with MSYS2's mingw-w64 GCC and upstream's own
# Makefile. Run it through engine/build_modules.cmd, which finds MSYS2 and then
# turns the results into language packs under ../languages.
#
#   TAGS="enus dede" engine/build_modules.sh     just those languages
#
# Seven of the modules are not languages: dedx, itix, esex, esux, engx, enux
# and frfx are the German, Italian, Spanish, English and French modules with
# the rules of their own language's phonology taken out, so that they say the
# phones they are given. They speak the languages eSpeak NG reads, and are
# made from openevv/accents/<tag> by tools/module/clone.py before they are
# built.
#   OPENEVV_WORK=/c/somewhere                     where to build (default:
#                                                 %LOCALAPPDATA%\OpenEvvBuild)
#   RULES=bytecode                                interpret the rules instead of
#                                                 compiling them (faster build,
#                                                 slower engine)
#
# Needs, in MSYS2: make, python, mingw-w64-x86_64-gcc and mingw-w64-i686-gcc
# (pacman -S --needed make python mingw-w64-x86_64-gcc mingw-w64-i686-gcc).
#
# The build happens in a copy of the sources, not in the repository: upstream's
# build writes thirteen megabytes of generated C per language into lang/<tag>,
# and hundreds of objects, none of which belong in a checkout (or in a folder a
# sync client is watching).
set -eu

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/openevv"
if [ -z "${OPENEVV_WORK:-}" ]; then
  if [ -n "${LOCALAPPDATA:-}" ]; then
    OPENEVV_WORK="$(cygpath -u "$LOCALAPPDATA")/OpenEvvBuild"
  else
    OPENEVV_WORK="$ROOT/build_engine"
  fi
else
  OPENEVV_WORK="$(cygpath -u "$OPENEVV_WORK")"  # the .cmd passes a Windows path
fi
WORK="$OPENEVV_WORK/openevv"
OUT="$OPENEVV_WORK/modules"
TAGS="${TAGS:-enus engb dede eses esus frfr frca itit plpl jajp dedx itix esex esux engx enux frfx}"
JOBS="${JOBS:-$(nproc)}"
RULES="${RULES:-c}"

export PATH="/mingw64/bin:/mingw32/bin:$PATH"
for tool in make python3 x86_64-w64-mingw32-gcc i686-w64-mingw32-gcc; do
  command -v "$tool" >/dev/null || { echo "build_modules: $tool is missing (see the top of this script)" >&2; exit 1; }
done
[ -f "$SRC/Makefile" ] || { echo "build_modules: no openevv sources at $SRC" >&2; exit 1; }

echo "build_modules: sources $SRC"
echo "build_modules: building in $WORK"
mkdir -p "$WORK" "$OUT"
# Update the copy; generated rules and objects from earlier runs are kept, so
# only what changed is rebuilt.
cp -au "$SRC/." "$WORK/"

cd "$WORK"
for tag in $TAGS; do
  if [ -f "accents/$tag/recipe" ]; then
    python3 tools/module/clone.py "$tag" || { echo "build_modules: $tag could not be made from its recipe" >&2; exit 1; }
  fi
  [ -d "lang/$tag" ] || { echo "build_modules: no language $tag in the sources" >&2; exit 1; }
  echo "=== $tag"
  start=$(date +%s)
  make -j"$JOBS" LANGS="lang/$tag" RULES="$RULES" \
    WINDRES=/mingw64/bin/windres ARWIN=/mingw64/bin/ar \
    WINDRES32=/mingw32/bin/windres ARWIN32=/mingw32/bin/ar \
    build/eci.dll build/eci32.dll build/evv.exe
  mkdir -p "$OUT/$tag"
  cp build/eci.dll   "$OUT/$tag/openevv-$tag-x64.dll"
  cp build/eci32.dll "$OUT/$tag/openevv-$tag-x86.dll"
  cp build/evv.exe   "$OUT/$tag/evv-$tag.exe"
  echo "=== $tag built in $(( $(date +%s) - start )) s"
done
echo "build_modules: modules are in $OUT"
