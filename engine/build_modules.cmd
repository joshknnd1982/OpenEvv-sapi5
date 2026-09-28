@echo off
rem Rebuilds the OpenEVV language modules from openevv\ and installs them as
rem language packs in languages\. The packs are already in the repository, so
rem this is only needed after changing the engine or a language, or to build a
rem new language.
rem
rem   engine\build_modules.cmd              every language
rem   engine\build_modules.cmd enus dede    just those
rem
rem Needs MSYS2 (C:\msys64, or set MSYS2_ROOT) with make, python and the two
rem mingw-w64 GCCs, and a 64-bit Windows Python on PATH for the last step.
setlocal
cd /d "%~dp0.."
set "ROOT=%CD%"
if not defined MSYS2_ROOT set "MSYS2_ROOT=C:\msys64"
if not exist "%MSYS2_ROOT%\usr\bin\bash.exe" (
    echo MSYS2 was not found at %MSYS2_ROOT%. Install it from https://www.msys2.org/ and run:
    echo   pacman -S --needed make python mingw-w64-x86_64-gcc mingw-w64-i686-gcc
    exit /b 1
)
if not defined OPENEVV_WORK set "OPENEVV_WORK=%LOCALAPPDATA%\OpenEvvBuild"
if not "%~1"=="" set "TAGS=%*"
set "MSYSTEM=MSYS"
set "CHERE_INVOKING=1"
"%MSYS2_ROOT%\usr\bin\bash.exe" -l "%ROOT%\engine\build_modules.sh" || exit /b 1

python "%ROOT%\engine\make_language_packs.py" "%OPENEVV_WORK%\modules" %* || exit /b 1
echo.
echo Language packs updated in %ROOT%\languages
endlocal
