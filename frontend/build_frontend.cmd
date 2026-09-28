@echo off
rem Builds OpenEvvFrontend.exe for x86 and x64 with MSVC and Ninja, and eSpeak
rem NG's data with it, and stages both in dist\ the way they are installed:
rem
rem   dist\x86\OpenEvvFrontend.exe
rem   dist\x64\OpenEvvFrontend.exe
rem   dist\espeak-ng-data\
rem
rem eSpeak NG comes from ESPEAK_NG_GIT_REPOSITORY at ESPEAK_NG_GIT_TAG (see
rem frontend\CMakeLists.txt for the defaults), or from a local checkout:
rem
rem   set ESPEAK_NG_SOURCE_DIR=C:\path\to\espeak-ng
rem   frontend\build_frontend.cmd
setlocal
cd /d "%~dp0.."
set "ROOT=%CD%"

set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (echo vswhere.exe not found: install Visual Studio 2022 or its Build Tools & exit /b 1)
set "VSDIR="
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSDIR=%%i"
if not defined VSDIR (echo No Visual Studio with the C++ tools was found & exit /b 1)
set "NINJA_DIR=%VSDIR%\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja"

set "ESPEAK_ARGS="
if defined ESPEAK_NG_SOURCE_DIR call set "ESPEAK_ARGS=%%ESPEAK_ARGS%% "-DESPEAK_NG_SOURCE_DIR=%ESPEAK_NG_SOURCE_DIR%""
if defined ESPEAK_NG_GIT_REPOSITORY call set "ESPEAK_ARGS=%%ESPEAK_ARGS%% "-DESPEAK_NG_GIT_REPOSITORY=%ESPEAK_NG_GIT_REPOSITORY%""
if defined ESPEAK_NG_GIT_TAG call set "ESPEAK_ARGS=%%ESPEAK_ARGS%% "-DESPEAK_NG_GIT_TAG=%ESPEAK_NG_GIT_TAG%""

call :build x64 ON || exit /b 1
rem The data is the same for both bitnesses; only the 64-bit build compiles it.
call :build x86 OFF || exit /b 1

set "DATA_DIR="
for %%D in ("%ROOT%\build_frontend_x64\espeak-ng-build\espeak-ng-data" "%ROOT%\build_frontend_x64\_deps\espeak-ng-build\espeak-ng-data") do (
    if not defined DATA_DIR if exist "%%~D\phontab" set "DATA_DIR=%%~D"
)
if not defined DATA_DIR (echo The compiled eSpeak NG data was not found & exit /b 1)
if exist "%ROOT%\dist\espeak-ng-data" rmdir /s /q "%ROOT%\dist\espeak-ng-data"
robocopy "%DATA_DIR%" "%ROOT%\dist\espeak-ng-data" /E /NFL /NDL /NJH /NJS /NP >nul
if errorlevel 8 (echo Staging the eSpeak NG data failed & exit /b 1)
echo Front-end and eSpeak NG data staged in dist\
endlocal
exit /b 0

:build
setlocal
echo.
echo === eSpeak NG front-end, %1 ===
call "%VSDIR%\VC\Auxiliary\Build\vcvarsall.bat" %1 >nul || exit /b 1
set "PATH=%NINJA_DIR%;%PATH%"
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCOMPILE_INTONATIONS=%2 %ESPEAK_ARGS% -S "%ROOT%\frontend" -B "%ROOT%\build_frontend_%1" || exit /b 1
cmake --build "%ROOT%\build_frontend_%1" || exit /b 1
if not exist "%ROOT%\dist\%1" mkdir "%ROOT%\dist\%1"
copy /y "%ROOT%\build_frontend_%1\bin\OpenEvvFrontend.exe" "%ROOT%\dist\%1\" >nul || exit /b 1
endlocal
exit /b 0
