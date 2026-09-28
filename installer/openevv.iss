; OpenEVV SAPI5 - Windows installer (Inno Setup 6.3 or later)
;
; build_all.bat compiles this after staging dist\. By hand, from the repository root,
; once dist\ is staged:
;
;   ISCC.exe installer\openevv.iss
;
; Accessibility, since the people most likely to install these voices use a screen reader:
;   * Only standard Inno Setup pages built from real Win32 controls, in the plain light
;     "modern" style: no custom skin that could hide controls from MSAA, no splash screen,
;     no billboard. Nothing auto-advances and nothing steals focus.
;   * MSAA names each list after the text just before it. The list of things to run at
;     the end gets a short label of its own, so it is not named after the whole results
;     summary above it.
;   * Every outcome - the registration, the voice test in 32-bit and in 64-bit programs,
;     where the logs are - is stated in words on the last page and in the log, never only
;     by an icon or a colour. A failed voice test is also reported in a message box, which
;     screen readers read out as soon as it appears.
;   * SetupLogging and UninstallLogging are on, so every install and every uninstall
;     leaves a complete log behind; the install log is copied to the OpenEVV log folder.
;
; Registration is written by the [Registry] section rather than by regsvr32, so it is
; logged entry by entry and does not depend on loading the DLLs during setup. Uninstall
; removes it three independent ways: DllUnregisterServer, the [Registry] uninsdeletekey
; flags, and a sweep of both registry views in CurUninstallStepChanged.
;
; ISCC.exe /DProbe installer\openevv.iss builds the accessibility probe: the same wizard
; and pages under its own AppId, per user and without elevation, installing only a text
; file and touching no registration, settings or logs. installer_a11y.exe walks it
; through MSAA on a private desktop.

; Bump MyAppVersion with src\common\version.h and project() in CMakeLists.txt.
#define MyAppVersion   "1.0.0"
#define AppName        "OpenEVV SAPI5"
#define AppPublisher   "OpenEVV SAPI5 project"
#define AppURL         "https://github.com/joshknnd1982/OpenEvv-sapi5"
#define DllName        "OpenEvvSAPI.dll"
#define HostName       "OpenEvvHost.exe"
#define ConfigName     "OpenEvvConfig.exe"
; CLSIDs, as [Code] string literals and as [Registry] text (where "{{" is a literal brace)
#define EngineClsid    "{F3CC6AB4-C4C4-4EC6-AA1F-1A114367AE91}"
#define EnumClsid      "{90E5CEF9-18DD-435E-AE19-BEC9B58D3627}"
#define EngineClsidReg "{{F3CC6AB4-C4C4-4EC6-AA1F-1A114367AE91}"
#define EnumClsidReg   "{{90E5CEF9-18DD-435E-AE19-BEC9B58D3627}"
#define TokenEnumsKey  "Software\Microsoft\Speech\Voices\TokenEnums\OpenEVV"
#define RealAppId      "{A077FCBD-75CA-41BA-A4D9-D74433765FF2}"

#ifndef Probe
; Refuse to package binaries from a different build than this script describes.
#define BuiltVersion GetVersionNumbersString(AddBackslash(SourcePath) + "..\dist\x64\" + DllName)
#if BuiltVersion != MyAppVersion + ".0"
  #error dist\x64\OpenEvvSAPI.dll is missing or is not the version in MyAppVersion; run build_all.bat
#endif
#endif

[Setup]
#ifdef Probe
AppId={{DB3F06B0-C03E-4F87-9739-B953FC329AAF}
#else
AppId={{A077FCBD-75CA-41BA-A4D9-D74433765FF2}
#endif
AppName={#AppName}
AppVersion={#MyAppVersion}
AppVerName={#AppName} {#MyAppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
AppComments=The OpenEVV engine (IBM Embedded ViaVoice, the Eloquence voice, rebuilt as C) as SAPI 5 voices for 32-bit and 64-bit programs: ten languages, eight voices each, with a configuration utility.
UninstallDisplayName={#AppName}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductName={#AppName}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} {#MyAppVersion} setup
VersionInfoCopyright=Wrapper: GNU GPL v2. openevv engine: MIT. Language data: IBM, see NOTICE.
DefaultDirName={autopf}\OpenEVV SAPI5
DefaultGroupName=OpenEVV SAPI5
DisableProgramGroupPage=yes
OutputDir=..\output
#ifdef Probe
OutputBaseFilename=OpenEVV-SAPI5-AccessibilityProbe
#else
OutputBaseFilename=OpenEVV-SAPI5-Setup-{#MyAppVersion}
#endif
Compression=lzma2/ultra64
SolidCompression=yes
LZMANumBlockThreads=4
WizardStyle=modern
InfoBeforeFile=before_install.txt

; SAPI 5 reads its voice list only from HKLM.
#ifdef Probe
PrivilegesRequired=lowest
#else
PrivilegesRequired=admin
#endif
; 64-bit mode on 64-bit Windows, so {sys} is the 64-bit System32 and HKLM64 is the
; native view. On 32-bit Windows only the 32-bit half is installed.
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=6.1sp1

SetupLogging=yes
UninstallLogging=yes

; Never close anybody's screen reader to win a file lock. A SAPI DLL that any program has
; merely listed voices through stays loaded, and a program speaking with an OpenEVV voice
; has engine hosts holding the language modules open; restartreplace below queues such
; files to be swapped at the next restart instead of failing half-way and leaving a mix
; of versions.
CloseApplications=no
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut to OpenEVV Configuration"; GroupDescription: "Additional shortcuts:"

#ifdef Probe
[Files]
Source: "before_install.txt"; DestDir: "{app}"
#else
[Dirs]
; Logs, language packs a user drops in, and user dictionaries live here, and must be
; writable by whoever uses the voices, not only by the administrator who installed them.
Name: "{commonappdata}\OpenEVV"; Permissions: users-modify
Name: "{commonappdata}\OpenEVV\Logs"; Permissions: users-modify
Name: "{commonappdata}\OpenEVV\languages"; Permissions: users-modify
Name: "{commonappdata}\OpenEVV\dictionaries"; Permissions: users-modify

[Files]
; ---- 32-bit SAPI 5 interface: 32-bit programs load x86\OpenEvvSAPI.dll, which runs the
; engine in x86\OpenEvvHost.exe.
Source: "..\dist\x86\{#DllName}";    DestDir: "{app}\x86"; Flags: ignoreversion restartreplace uninsrestartdelete
Source: "..\dist\x86\{#HostName}";   DestDir: "{app}\x86"; Flags: ignoreversion restartreplace uninsrestartdelete
Source: "..\dist\x86\{#ConfigName}"; DestDir: "{app}\x86"; Flags: ignoreversion restartreplace uninsrestartdelete

; ---- 64-bit SAPI 5 interface ------------------------------------------------------------
Source: "..\dist\x64\{#DllName}";    DestDir: "{app}\x64"; Flags: ignoreversion restartreplace uninsrestartdelete; Check: Is64BitInstallMode
Source: "..\dist\x64\{#HostName}";   DestDir: "{app}\x64"; Flags: ignoreversion restartreplace uninsrestartdelete; Check: Is64BitInstallMode
Source: "..\dist\x64\{#ConfigName}"; DestDir: "{app}\x64"; Flags: ignoreversion restartreplace uninsrestartdelete; Check: Is64BitInstallMode

; ---- every language: the engine modules (32-bit and 64-bit) and language.ini ----------
Source: "..\languages\*"; DestDir: "{app}\languages"; Flags: ignoreversion recursesubdirs createallsubdirs restartreplace uninsrestartdelete

; ---- documentation --------------------------------------------------------------------
Source: "..\dist\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
; ---- 64-bit programs ------------------------------------------------------------------
Root: HKLM64; Subkey: "Software\Classes\CLSID\{#EngineClsidReg}"; ValueType: string; ValueName: ""; ValueData: "OpenEVV SAPI5 text-to-speech engine"; Flags: uninsdeletekey; Check: Is64BitInstallMode
Root: HKLM64; Subkey: "Software\Classes\CLSID\{#EngineClsidReg}\InprocServer32"; ValueType: string; ValueName: ""; ValueData: "{app}\x64\{#DllName}"; Check: Is64BitInstallMode
Root: HKLM64; Subkey: "Software\Classes\CLSID\{#EngineClsidReg}\InprocServer32"; ValueType: string; ValueName: "ThreadingModel"; ValueData: "Both"; Check: Is64BitInstallMode
Root: HKLM64; Subkey: "Software\Classes\CLSID\{#EnumClsidReg}"; ValueType: string; ValueName: ""; ValueData: "OpenEVV SAPI5 voice enumerator"; Flags: uninsdeletekey; Check: Is64BitInstallMode
Root: HKLM64; Subkey: "Software\Classes\CLSID\{#EnumClsidReg}\InprocServer32"; ValueType: string; ValueName: ""; ValueData: "{app}\x64\{#DllName}"; Check: Is64BitInstallMode
Root: HKLM64; Subkey: "Software\Classes\CLSID\{#EnumClsidReg}\InprocServer32"; ValueType: string; ValueName: "ThreadingModel"; ValueData: "Both"; Check: Is64BitInstallMode
Root: HKLM64; Subkey: "{#TokenEnumsKey}"; ValueType: string; ValueName: ""; ValueData: "OpenEVV voices"; Flags: uninsdeletekey; Check: Is64BitInstallMode
Root: HKLM64; Subkey: "{#TokenEnumsKey}"; ValueType: string; ValueName: "CLSID"; ValueData: "{#EnumClsidReg}"; Check: Is64BitInstallMode

; ---- 32-bit programs (the WOW6432Node view on 64-bit Windows) ---------------------------
Root: HKLM32; Subkey: "Software\Classes\CLSID\{#EngineClsidReg}"; ValueType: string; ValueName: ""; ValueData: "OpenEVV SAPI5 text-to-speech engine"; Flags: uninsdeletekey
Root: HKLM32; Subkey: "Software\Classes\CLSID\{#EngineClsidReg}\InprocServer32"; ValueType: string; ValueName: ""; ValueData: "{app}\x86\{#DllName}"
Root: HKLM32; Subkey: "Software\Classes\CLSID\{#EngineClsidReg}\InprocServer32"; ValueType: string; ValueName: "ThreadingModel"; ValueData: "Both"
Root: HKLM32; Subkey: "Software\Classes\CLSID\{#EnumClsidReg}"; ValueType: string; ValueName: ""; ValueData: "OpenEVV SAPI5 voice enumerator"; Flags: uninsdeletekey
Root: HKLM32; Subkey: "Software\Classes\CLSID\{#EnumClsidReg}\InprocServer32"; ValueType: string; ValueName: ""; ValueData: "{app}\x86\{#DllName}"
Root: HKLM32; Subkey: "Software\Classes\CLSID\{#EnumClsidReg}\InprocServer32"; ValueType: string; ValueName: "ThreadingModel"; ValueData: "Both"
Root: HKLM32; Subkey: "{#TokenEnumsKey}"; ValueType: string; ValueName: ""; ValueData: "OpenEVV voices"; Flags: uninsdeletekey
Root: HKLM32; Subkey: "{#TokenEnumsKey}"; ValueType: string; ValueName: "CLSID"; ValueData: "{#EnumClsidReg}"

[Icons]
Name: "{group}\OpenEVV Configuration"; Filename: "{app}\x64\{#ConfigName}"; Comment: "Adjust the OpenEVV voices, languages and dictionaries"; Check: Is64BitInstallMode
Name: "{group}\OpenEVV Configuration"; Filename: "{app}\x86\{#ConfigName}"; Comment: "Adjust the OpenEVV voices, languages and dictionaries"; Check: not Is64BitInstallMode
Name: "{autodesktop}\OpenEVV Configuration"; Filename: "{app}\x64\{#ConfigName}"; Comment: "Adjust the OpenEVV voices, languages and dictionaries"; Tasks: desktopicon; Check: Is64BitInstallMode
Name: "{autodesktop}\OpenEVV Configuration"; Filename: "{app}\x86\{#ConfigName}"; Comment: "Adjust the OpenEVV voices, languages and dictionaries"; Tasks: desktopicon; Check: not Is64BitInstallMode
Name: "{group}\OpenEVV logs"; Filename: "{commonappdata}\OpenEVV\Logs"; Comment: "The folder the OpenEVV voices, the engine hosts, the configuration utility and the installer write their logs to"
Name: "{group}\OpenEVV language packs folder"; Filename: "{commonappdata}\OpenEVV\languages"; Comment: "Drop a language pack folder in here and its voices appear in every SAPI 5 program"
Name: "{group}\OpenEVV read me"; Filename: "{win}\notepad.exe"; Parameters: """{app}\docs\README.txt"""; Comment: "About OpenEVV SAPI5"
; /LOG: UninstallLogging only covers uninstalls started from Windows Settings.
Name: "{group}\Uninstall OpenEVV SAPI5"; Filename: "{uninstallexe}"; Parameters: "/LOG"
#endif

[Run]
; runasoriginaluser: open the utility as the person who will use the voices, not elevated.
Filename: "{app}\x64\{#ConfigName}"; Description: "Open OpenEVV Configuration now"; Flags: postinstall nowait skipifsilent unchecked runasoriginaluser; Check: Is64BitInstallMode
Filename: "{app}\x86\{#ConfigName}"; Description: "Open OpenEVV Configuration now"; Flags: postinstall nowait skipifsilent unchecked runasoriginaluser; Check: not Is64BitInstallMode

[Code]
{ MSAA names a list after the static text just before it in the z-order - on the last page
  that is the whole results summary, which a screen reader would then read a second time
  as the name of the "run now" list. A short label of its own goes directly before it. }
function GetWindow(Wnd: HWND; Cmd: UINT): HWND;
  external 'GetWindow@user32.dll stdcall';
function SetWindowPos(Wnd, InsertAfter: HWND; X, Y, CX, CY: Integer; Flags: UINT): BOOL;
  external 'SetWindowPos@user32.dll stdcall';

const
  GW_HWNDPREV = 3;
  SWP_NOSIZE = $1;
  SWP_NOMOVE = $2;
  SWP_NOACTIVATE = $10;

var
  Summary64: String;
  Summary32: String;
  TestFailed: Boolean;
  RegistrationOk: Boolean;
  RunListLabel: TNewStaticText;

procedure Note(const S: String);
begin
  Log('[openevv] ' + S);
end;

function LogDir: String;
begin
  Result := ExpandConstant('{commonappdata}\OpenEVV\Logs');
end;

function ArchName: String;
begin
  case ProcessorArchitecture of
    paX86:   Result := 'x86';
    paX64:   Result := 'x64';
    paArm64: Result := 'ARM64';
  else
    Result := 'unknown processor';
  end;
end;

{ ---- registration checks ------------------------------------------------------------ }

function ViewName(Root: Integer): String;
begin
  if Root = HKEY_LOCAL_MACHINE_64 then
    Result := 'HKLM64'
  else
    Result := 'HKLM32';
end;

function CheckValue(Root: Integer; const Subkey, Name, Expected: String): Boolean;
var
  V, Shown: String;
begin
  Shown := Name;
  if Shown = '' then
    Shown := '(default)';
  Result := RegQueryStringValue(Root, Subkey, Name, V);
  if not Result then
    Note(Format('%s\%s  %s: MISSING', [ViewName(Root), Subkey, Shown]))
  else if (Expected <> '') and (CompareText(V, Expected) <> 0) then
  begin
    Note(Format('%s\%s  %s = "%s": WRONG, expected "%s"', [ViewName(Root), Subkey, Shown, V, Expected]));
    Result := False;
  end
  else
    Note(Format('%s\%s  %s = "%s"', [ViewName(Root), Subkey, Shown, V]));
end;

function CheckRegistration(Root: Integer; const DllPath: String): Boolean;
var
  Ok: Boolean;
begin
  Ok := CheckValue(Root, 'Software\Classes\CLSID\{#EngineClsid}\InprocServer32', '', DllPath);
  Ok := CheckValue(Root, 'Software\Classes\CLSID\{#EngineClsid}\InprocServer32', 'ThreadingModel', 'Both') and Ok;
  Ok := CheckValue(Root, 'Software\Classes\CLSID\{#EnumClsid}\InprocServer32', '', DllPath) and Ok;
  Ok := CheckValue(Root, 'Software\Classes\CLSID\{#EnumClsid}\InprocServer32', 'ThreadingModel', 'Both') and Ok;
  Ok := CheckValue(Root, '{#TokenEnumsKey}', 'CLSID', '{#EnumClsid}') and Ok;
  if FileExists(DllPath) then
    Note(DllPath + ' is present')
  else
  begin
    Note(DllPath + ' is MISSING');
    Ok := False;
  end;
  Result := Ok;
end;

{ ---- the voice test ------------------------------------------------------------------ }

{ Runs OpenEvvConfig.exe --selftest. The 64-bit utility speaks every voice of every
  language through both the 64-bit and the 32-bit engine, and one through SAPI in a
  64-bit process; the 32-bit utility then checks SAPI in a 32-bit process. It runs as
  the user who started setup, so it also proves that user can write the logs. }
function RunVoiceTest(const Exe, Args, Bits: String): String;
var
  Report: String;
  Lines: TArrayOfString;
  I, Code: Integer;
begin
  Result := '';
  Report := LogDir + '\selftest-' + Bits + '.txt';
  DeleteFile(Report);
  WizardForm.StatusLabel.Caption := 'Testing the voices in ' + Bits + ' programs...';
  WizardForm.FilenameLabel.Caption := '';
  Note('voice test (' + Bits + '): ' + Exe + ' --selftest ' + Args + ' --report "' + Report + '"');
  if not ExecAsOriginalUser(Exe, '--selftest ' + Args + ' --report "' + Report + '"', '', SW_HIDE,
                            ewWaitUntilTerminated, Code) then
  begin
    Note('voice test (' + Bits + ') could not start: ' + SysErrorMessage(Code));
    TestFailed := True;
    Result := 'The voice test for ' + Bits + ' programs could not be started.';
    Exit;
  end;
  if LoadStringsFromFile(Report, Lines) then
    for I := 0 to GetArrayLength(Lines) - 1 do
    begin
      Note('  ' + Lines[I]);
      if Pos('RESULT: ', Lines[I]) > 0 then
        Result := Copy(Lines[I], Pos('RESULT: ', Lines[I]) + 8, Length(Lines[I]));
    end
  else
    Note('voice test (' + Bits + ') wrote no report at ' + Report);
  Note(Format('voice test (%s) exit code %d', [Bits, Code]));
  if Code <> 0 then
    TestFailed := True;
  if Result = '' then
    Result := Format('The voice test for %s programs ended with code %d and wrote no result.', [Bits, Code]);
end;

{ ---- setup events --------------------------------------------------------------------- }

function InitializeSetup: Boolean;
var
  Previous: String;
begin
  Note('{#AppName} {#MyAppVersion} setup starting');
  Note('Windows ' + GetWindowsVersionString + ' on ' + ArchName +
       ', 64-bit install mode: ' + IntToStr(Ord(Is64BitInstallMode)));
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
       'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#RealAppId}_is1',
       'DisplayVersion', Previous) then
    Note('upgrading an existing installation, version ' + Previous)
  else
    Note('no earlier installation found');
  Result := True;
end;

procedure InitializeWizard;
begin
  RunListLabel := TNewStaticText.Create(WizardForm);
  RunListLabel.Parent := WizardForm.FinishedPage;
  RunListLabel.Caption := 'Things to do now:';
  RunListLabel.Left := WizardForm.RunList.Left;
  RunListLabel.Visible := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
#ifdef Probe
  if CurStep = ssPostInstall then
  begin
    { Stand-ins of realistic length, so the probe lays out the last page as setup does. }
    Summary64 := 'Accessibility probe: no voices were installed, so none were tested in 64-bit programs.';
    Summary32 := 'Accessibility probe: no voices were installed, so none were tested in 32-bit programs.';
  end;
#else
  if CurStep = ssPostInstall then
  begin
    Note('checking the registration');
    RegistrationOk := True;
    if Is64BitInstallMode then
      RegistrationOk := CheckRegistration(HKEY_LOCAL_MACHINE_64, ExpandConstant('{app}\x64\{#DllName}'));
    RegistrationOk := CheckRegistration(HKEY_LOCAL_MACHINE_32, ExpandConstant('{app}\x86\{#DllName}')) and RegistrationOk;
    if RegistrationOk then
      Note('registration complete in every view')
    else
      Note('REGISTRATION INCOMPLETE - see the entries above');

    TestFailed := False;
    if Is64BitInstallMode then
    begin
      Summary64 := RunVoiceTest(ExpandConstant('{app}\x64\{#ConfigName}'), '', '64-bit');
      Summary32 := RunVoiceTest(ExpandConstant('{app}\x86\{#ConfigName}'), '--sapi-only', '32-bit');
    end
    else
      Summary32 := RunVoiceTest(ExpandConstant('{app}\x86\{#ConfigName}'), '', '32-bit');

    { The log so far, where the configuration utility's "Open the log folder" button finds
      it. Copied again at the very end, complete. }
    CopyFile(ExpandConstant('{log}'), LogDir + '\install.log', False);

    if TestFailed or not RegistrationOk then
      SuppressibleMsgBox('OpenEVV SAPI5 is installed, but the voice test found a problem.' + #13#10#13#10 +
        Summary64 + #13#10 + Summary32 + #13#10#13#10 +
        'The details are in install.log in ' + LogDir + '.', mbError, MB_OK, IDOK);
  end
  else if CurStep = ssDone then
    CopyFile(ExpandConstant('{log}'), LogDir + '\install.log', False);
#endif
end;

{ The last page says what actually happened, in words a screen reader reads out. }
procedure CurPageChanged(CurPageID: Integer);
var
  S, Tests: String;
  Delta: Integer;
begin
  if CurPageID <> wpFinished then
    Exit;
  Tests := Summary32;
  if Summary64 <> '' then
    Tests := Summary64 + #13#10 + Summary32;
  { No line may start with "#" here: the preprocessor would take it for a directive. }
  S := '{#AppName} {#MyAppVersion} is installed.' + #13#10#13#10 + Tests + #13#10#13#10 +
    'Choose any voice named OpenEVV in your screen reader or any SAPI 5 program. ' +
    'OpenEVV Configuration, on the desktop and in the Start menu, adjusts every voice.' + #13#10#13#10 +
    'Logs, including install.log: ' + LogDir;
  if WizardForm.YesRadio.Visible then
    S := S + #13#10#13#10 + 'Some files were in use and will be replaced when Windows restarts.';
  WizardForm.FinishedLabel.Caption := S;
  Delta := WizardForm.AdjustLabelHeight(WizardForm.FinishedLabel);
  WizardForm.YesRadio.Top := WizardForm.YesRadio.Top + Delta;
  WizardForm.NoRadio.Top := WizardForm.NoRadio.Top + Delta;
  if WizardForm.RunList.Visible then
  begin
    RunListLabel.Top := WizardForm.RunList.Top + Delta;
    RunListLabel.Visible := True;
    Delta := Delta + RunListLabel.Height + ScaleY(4);
    SetWindowPos(RunListLabel.Handle, GetWindow(WizardForm.RunList.Handle, GW_HWNDPREV), 0, 0, 0, 0,
      SWP_NOSIZE or SWP_NOMOVE or SWP_NOACTIVATE);
  end;
  WizardForm.RunList.Top := WizardForm.RunList.Top + Delta;
  if WizardForm.RunList.Height - Delta > ScaleY(24) then
    WizardForm.RunList.Height := WizardForm.RunList.Height - Delta;
end;

{ ---- uninstall ----------------------------------------------------------------------- }

procedure Unregister(const Regsvr32, DllPath: String);
var
  Code: Integer;
begin
  if not FileExists(DllPath) then
  begin
    Log('[openevv] not present, nothing to unregister: ' + DllPath);
    Exit;
  end;
  Exec(Regsvr32, '/s /u "' + DllPath + '"', '', SW_HIDE, ewWaitUntilTerminated, Code);
  Log(Format('[openevv] %s /s /u "%s" -> %d', [Regsvr32, DllPath, Code]));
end;

procedure SweepView(Root: Integer);
begin
  if RegDeleteKeyIncludingSubkeys(Root, '{#TokenEnumsKey}') then
    Log('[openevv] removed ' + ViewName(Root) + '\{#TokenEnumsKey}');
  if RegDeleteKeyIncludingSubkeys(Root, 'Software\Classes\CLSID\{#EngineClsid}') then
    Log('[openevv] removed ' + ViewName(Root) + '\Software\Classes\CLSID\{#EngineClsid}');
  if RegDeleteKeyIncludingSubkeys(Root, 'Software\Classes\CLSID\{#EnumClsid}') then
    Log('[openevv] removed ' + ViewName(Root) + '\Software\Classes\CLSID\{#EnumClsid}');
end;

{ A default voice that no longer exists would leave SAPI programs without one. }
procedure ClearDefaultVoice(Root: Integer; const RootName: String);
var
  V: String;
begin
  if RegQueryStringValue(Root, 'Software\Microsoft\Speech\Voices', 'DefaultTokenId', V) and
     (Pos('\TOKENENUMS\OPENEVV\', Uppercase(V)) > 0) then
    if RegDeleteValue(Root, 'Software\Microsoft\Speech\Voices', 'DefaultTokenId') then
      Log('[openevv] cleared ' + RootName + ' DefaultTokenId ' + V);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Data: String;
begin
#ifdef Probe
  { The probe registered nothing, and must never unregister a real installation. }
  Log('[openevv] accessibility probe uninstalled');
#else
  if CurUninstallStep = usUninstall then
  begin
    Log('[openevv] uninstalling {#AppName} {#MyAppVersion}');
    if IsWin64 then
    begin
      Unregister(ExpandConstant('{sys}\regsvr32.exe'), ExpandConstant('{app}\x64\{#DllName}'));
      Unregister(ExpandConstant('{syswow64}\regsvr32.exe'), ExpandConstant('{app}\x86\{#DllName}'));
      SweepView(HKEY_LOCAL_MACHINE_64);
      ClearDefaultVoice(HKEY_LOCAL_MACHINE_64, 'HKLM64');
    end
    else
      Unregister(ExpandConstant('{sys}\regsvr32.exe'), ExpandConstant('{app}\x86\{#DllName}'));
    SweepView(HKEY_LOCAL_MACHINE_32);
    ClearDefaultVoice(HKEY_LOCAL_MACHINE_32, 'HKLM32');
    ClearDefaultVoice(HKEY_CURRENT_USER, 'HKCU');
  end
  else if CurUninstallStep = usPostUninstall then
  begin
    if RegKeyExists(HKEY_LOCAL_MACHINE_32, '{#TokenEnumsKey}') or
       (IsWin64 and RegKeyExists(HKEY_LOCAL_MACHINE_64, '{#TokenEnumsKey}')) then
      Log('[openevv] WARNING: an OpenEVV voice list key is still present')
    else
      Log('[openevv] the OpenEVV voices are no longer registered');
    { The logs go. Language packs and dictionaries a user added are theirs and stay;
      their folders are removed only if they are empty. }
    Data := ExpandConstant('{commonappdata}\OpenEVV');
    DelTree(Data + '\Logs', True, True, True);
    RemoveDir(Data + '\languages');
    RemoveDir(Data + '\dictionaries');
    if RemoveDir(Data) then
      Log('[openevv] removed ' + Data)
    else
      Log('[openevv] kept ' + Data + ': it holds language packs or dictionaries you added');
  end;
#endif
end;
