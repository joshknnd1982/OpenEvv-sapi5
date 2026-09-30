@echo off
rem OpenEVV SAPI5 - full build: x86 and x64 binaries, tests, staging, installer.
rem
rem   build_all.bat            build, test, stage dist\ and compile the installer
rem   build_all.bat notest     skip the test suites
rem   build_all.bat engine     rebuild the language modules first (needs MSYS2;
rem                            see engine\build_modules.cmd)
rem   build_all.bat packs      write the eSpeak NG language packs in languages\
rem                            again from the eSpeak NG sources (needs Python)
rem
rem Requires Visual Studio 2022 or its Build Tools with the C++ workload and a
rem Windows 10/11 SDK, CMake 3.20+ and Inno Setup 6. The language modules in
rem languages\ are prebuilt, so MSYS2 is only needed to rebuild them. The eSpeak
rem NG front-end is built here, from github.com/joshknnd1982/espeak-ng unless
rem ESPEAK_NG_SOURCE_DIR names a local checkout (frontend\build_frontend.cmd).
rem The eSpeak NG pack check wants a 64-bit Python and is skipped without one.
rem Programs are run by absolute path: some environments set
rem NoDefaultCurrentDirectoryInExePath, which hides programs in the current folder.
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "ROOT=%CD%"
set "RUN_TESTS=1"
rem The tests write their settings file and audio outside the source tree: a
rem sync client watching the tree (OneDrive) upsets the settings file's timestamps.
set "TESTOUT=%TEMP%\OpenEvvTests"
set "BUILD_ENGINE=0"
set "WRITE_PACKS=0"
for %%A in (%*) do (
    if /i "%%~A"=="notest" set "RUN_TESTS=0"
    if /i "%%~A"=="engine" set "BUILD_ENGINE=1"
    if /i "%%~A"=="packs" set "WRITE_PACKS=1"
)

if "%BUILD_ENGINE%"=="1" (
    echo.
    echo === Language modules, from openevv\ with MSYS2 mingw GCC ===
    call "%ROOT%\engine\build_modules.cmd" || goto :fail
)

rem Build Tools installs are only found with -products *.
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (echo vswhere.exe not found: install Visual Studio 2022 or its Build Tools & goto :fail)
set "VSDIR="
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSDIR=%%i"
if not defined VSDIR (echo No Visual Studio with the C++ tools was found & goto :fail)
echo Using Visual Studio at %VSDIR%

for %%A in (x86 x64) do (
    if "%%A"=="x86" (set "GEN_ARCH=Win32") else (set "GEN_ARCH=x64")
    echo.
    echo === Configuring and building %%A ===
    cmake -G "Visual Studio 17 2022" -A !GEN_ARCH! -S "%ROOT%" -B "%ROOT%\build_%%A" || goto :fail
    cmake --build "%ROOT%\build_%%A" --config Release || goto :fail
)

echo.
echo === The eSpeak NG front-end and data ===
call "%ROOT%\frontend\build_frontend.cmd" || goto :fail

set "PY="
for %%P in (python.exe py.exe) do if not defined PY (where %%P >nul 2>nul && set "PY=%%P")
if "%WRITE_PACKS%"=="1" (
    echo.
    echo === The eSpeak NG language packs, written again ===
    if not defined PY (echo Python is needed to write the packs & goto :fail)
    set "ESRC=%ESPEAK_NG_SOURCE_DIR%"
    if not defined ESPEAK_NG_SOURCE_DIR set "ESRC=%ROOT%\build_frontend_x64\_deps\espeak-ng-src"
    set PYTHONUTF8=1
    !PY! "%ROOT%\engine\make_espeak_packs.py" --espeak-src "!ESRC!" --frontend "%ROOT%\dist\x64\OpenEvvFrontend.exe" --data "%ROOT%\dist\espeak-ng-data" || goto :fail
    rem The installer offers each pack as a language to choose: its list is made from languages\.
    !PY! "%ROOT%\installer\make_components.py" || goto :fail
)
if "%RUN_TESTS%"=="1" if defined PY (
    echo.
    echo === Tests: every eSpeak NG language pack, through its template's own module ===
    set PYTHONUTF8=1
    !PY! "%ROOT%\engine\check_espeak_packs.py" "%ROOT%\dist\x64\OpenEvvFrontend.exe" "%ROOT%\dist\espeak-ng-data" || goto :fail
)

if "%RUN_TESTS%"=="1" (
    echo.
    echo === Tests: the SAPI engine through a mock SAPI site, both bitnesses ===
    "%ROOT%\build_x64\bin\Release\sapi_test.exe" --out "%TESTOUT%\build_x64_sapi_test_out" || goto :fail
    echo.
    echo === Tests: the same inside a process that enforces CET shadow stacks ===
    "%ROOT%\build_x64\bin\Release\sapi_test_cet.exe" --out "%TESTOUT%\build_x64_sapi_test_cet_out" || goto :fail
    echo.
    "%ROOT%\build_x86\bin\Release\sapi_test.exe" --out "%TESTOUT%\build_x86_sapi_test_out" || goto :fail
    echo.
    echo === Tests: every voice of every language through SAPI ===
    "%ROOT%\build_x64\bin\Release\sapi_test.exe" --only none --all-voices --out "%TESTOUT%\build_x64_sapi_test_voices" || goto :fail
    echo.
    echo === Tests: the configuration utility, as a screen reader sees it ===
    "%ROOT%\build_x64\bin\Release\a11y_check.exe" "%ROOT%\build_x64\bin\Release\OpenEvvConfig.exe" || goto :fail
)

if not exist "%ROOT%\dictionaries\community\ENUmain.dic" (echo dictionaries\community is missing: the installer ships it & goto :fail)

echo.
echo === Staging dist\ in the installed layout ===
if exist "%ROOT%\dist\x86" rmdir /s /q "%ROOT%\dist\x86"
if exist "%ROOT%\dist\x64" rmdir /s /q "%ROOT%\dist\x64"
if exist "%ROOT%\dist\docs" rmdir /s /q "%ROOT%\dist\docs"
for %%A in (x86 x64) do (
    mkdir "%ROOT%\dist\%%A"
    for %%F in (OpenEvvSAPI.dll OpenEvvHost.exe OpenEvvConfig.exe) do (
        copy /y "%ROOT%\build_%%A\bin\Release\%%F" "%ROOT%\dist\%%A\" >nul || goto :fail
    )
    copy /y "%ROOT%\build_frontend_%%A\bin\OpenEvvFrontend.exe" "%ROOT%\dist\%%A\" >nul || goto :fail
)
mkdir "%ROOT%\dist\docs"
copy /y "%ROOT%\README.md" "%ROOT%\dist\docs\README.txt" >nul || goto :fail
copy /y "%ROOT%\LICENSE" "%ROOT%\dist\docs\LICENSE.txt" >nul || goto :fail
copy /y "%ROOT%\NOTICE.md" "%ROOT%\dist\docs\NOTICE.txt" >nul || goto :fail
copy /y "%ROOT%\CREDITS.md" "%ROOT%\dist\docs\CREDITS.txt" >nul || goto :fail
copy /y "%ROOT%\CHANGELOG.md" "%ROOT%\dist\docs\CHANGELOG.txt" >nul || goto :fail
copy /y "%ROOT%\docs\LANGUAGES.md" "%ROOT%\dist\docs\LANGUAGES.txt" >nul || goto :fail
copy /y "%ROOT%\openevv\LICENSE" "%ROOT%\dist\docs\openevv-LICENSE.txt" >nul || goto :fail
copy /y "%ROOT%\openevv\NOTICE" "%ROOT%\dist\docs\openevv-NOTICE.txt" >nul || goto :fail
copy /y "%ROOT%\frontend\COPYING" "%ROOT%\dist\docs\eSpeak-NG-and-front-end-COPYING.txt" >nul || goto :fail
copy /y "%ROOT%\frontend\README.md" "%ROOT%\dist\docs\eSpeak-NG-front-end.txt" >nul || goto :fail
copy /y "%ROOT%\dictionaries\community\LICENSE.md" "%ROOT%\dist\docs\community-dictionary-LICENSE.txt" >nul || goto :fail
copy /y "%ROOT%\dictionaries\community\README.md" "%ROOT%\dist\docs\community-dictionary-README.txt" >nul || goto :fail

if "%RUN_TESTS%"=="1" (
    echo.
    echo === Tests: the staged layout, and the configuration utility's self-test ===
    "%ROOT%\build_x86\bin\Release\sapi_test.exe" --dll "%ROOT%\dist\x86\OpenEvvSAPI.dll" --only languages --out "%TESTOUT%\build_x86_sapi_test_dist" || goto :fail
    "%ROOT%\build_x64\bin\Release\sapi_test.exe" --dll "%ROOT%\dist\x64\OpenEvvSAPI.dll" --only languages --out "%TESTOUT%\build_x64_sapi_test_dist" || goto :fail
    start "" /wait "%ROOT%\dist\x64\OpenEvvConfig.exe" --selftest --hosts-only --report "%ROOT%\build_x64\selftest.txt"
    if errorlevel 1 (type "%ROOT%\build_x64\selftest.txt" & goto :fail)
    type "%ROOT%\build_x64\selftest.txt"
)

echo.
echo === Installer ===
rem The list of languages the wizard offers is generated from languages\; ISCC stops when a pack is
rem missing from it, and with Python this says so first, and also when a name or a count went stale.
if defined PY (
    !PY! "%ROOT%\installer\make_components.py" --check || goto :fail
)
set "ISCC="
for %%P in ("%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe") do (
    if not defined ISCC if exist "%%~P" set "ISCC=%%~P"
)
if not defined ISCC (echo Inno Setup 6 ISCC.exe not found & goto :fail)
"%ISCC%" /Q "%ROOT%\installer\openevv.iss" || goto :fail

if "%RUN_TESTS%"=="1" (
    echo.
    echo === Tests: the installer's pages, as a screen reader sees them ===
    rem The probe is the same wizard without elevation or payload; it is walked on a
    rem private desktop, installed per user into %%TEMP%%, and uninstalled again.
    "%ISCC%" /Q /DProbe /O"%ROOT%\build_x64" "%ROOT%\installer\openevv.iss" || goto :fail
    "%ROOT%\build_x64\bin\Release\installer_a11y.exe" "%ROOT%\build_x64\OpenEVV-SAPI5-AccessibilityProbe.exe" || goto :fail
    echo.
    echo === Tests: the choice of languages, by installing and upgrading the probe ===
    "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\installer\test_language_choice.ps1" -Probe "%ROOT%\build_x64\OpenEVV-SAPI5-AccessibilityProbe.exe" -Walker "%ROOT%\build_x64\bin\Release\installer_a11y.exe" || goto :fail
)

echo.
echo Build complete. Installer: %ROOT%\output\
endlocal
exit /b 0

:fail
echo.
echo BUILD FAILED
endlocal
exit /b 1
