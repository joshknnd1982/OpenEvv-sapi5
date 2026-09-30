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
;   * Every outcome - the registration, where the logs are - is stated in words on the last
;     page and in the log, never only by an icon or a colour. An incomplete registration is
;     also reported in a message box, which screen readers read out as soon as it appears.
;   * Setup does not speak the voices to test them: that took minutes after the files were
;     already installed. OpenEvvConfig.exe has a "Run the self-test" button for anyone who
;     wants it, and setup only checks the registration, which is a few registry reads.
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
#define MyAppVersion   "1.2.3"
#define AppName        "OpenEVV SAPI5"
#define AppPublisher   "OpenEVV SAPI5 project"
#define AppURL         "https://github.com/joshknnd1982/OpenEvv-sapi5"
#define DllName        "OpenEvvSAPI.dll"
#define HostName       "OpenEvvHost.exe"
#define ConfigName     "OpenEvvConfig.exe"
#define FrontendName   "OpenEvvFrontend.exe"
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
AppComments=The OpenEVV engine (IBM Embedded ViaVoice, the Eloquence voice, rebuilt as C) as SAPI 5 voices for 32-bit and 64-bit programs: openevv's ten languages and 145 more read by eSpeak NG, eight voices each, with a configuration utility.
UninstallDisplayName={#AppName}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductName={#AppName}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} {#MyAppVersion} setup
VersionInfoCopyright=Wrapper: GNU GPL v2. eSpeak NG front-end and data: GNU GPL v3. openevv engine: MIT. Language data: IBM, see NOTICE.
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

; Never close anybody's screen reader to win a file lock, and never make anybody restart
; Windows. A SAPI DLL that any program has merely listed voices through stays loaded, and
; a program speaking with an OpenEVV voice has engine hosts holding the language modules
; open. Windows will not delete or overwrite such a file but will rename it, so
; MoveAsideFilesInUse renames each one to *.N.old before the files are copied: the new
; version goes in under the real name, every program started from then on loads it, and
; the programs already running keep the old one until they are started again. The .old
; files are deleted by the next install or uninstall, or at the next restart, whichever
; comes first. restartreplace below is only the last resort, for a file that could not
; even be renamed.
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
; Logs, language packs a user drops in, user dictionaries, and a newer community dictionary
; downloaded by OpenEvvConfig live here, and must be writable by whoever uses the voices, not
; only by the administrator who installed them.
Name: "{commonappdata}\OpenEVV"; Permissions: users-modify
Name: "{commonappdata}\OpenEVV\Logs"; Permissions: users-modify
Name: "{commonappdata}\OpenEVV\languages"; Permissions: users-modify
Name: "{commonappdata}\OpenEVV\dictionaries"; Permissions: users-modify
Name: "{commonappdata}\OpenEVV\community-dictionary"; Permissions: users-modify

[Files]
; ---- 32-bit SAPI 5 interface: 32-bit programs load x86\OpenEvvSAPI.dll, which runs the
; engine in x86\OpenEvvHost.exe.
Source: "..\dist\x86\{#DllName}";    DestDir: "{app}\x86"; Flags: ignoreversion restartreplace uninsrestartdelete
Source: "..\dist\x86\{#HostName}";   DestDir: "{app}\x86"; Flags: ignoreversion restartreplace uninsrestartdelete
Source: "..\dist\x86\{#ConfigName}"; DestDir: "{app}\x86"; Flags: ignoreversion restartreplace uninsrestartdelete
Source: "..\dist\x86\{#FrontendName}"; DestDir: "{app}\x86"; Flags: ignoreversion restartreplace uninsrestartdelete

; ---- 64-bit SAPI 5 interface ------------------------------------------------------------
Source: "..\dist\x64\{#DllName}";    DestDir: "{app}\x64"; Flags: ignoreversion restartreplace uninsrestartdelete; Check: Is64BitInstallMode
Source: "..\dist\x64\{#HostName}";   DestDir: "{app}\x64"; Flags: ignoreversion restartreplace uninsrestartdelete; Check: Is64BitInstallMode
Source: "..\dist\x64\{#ConfigName}"; DestDir: "{app}\x64"; Flags: ignoreversion restartreplace uninsrestartdelete; Check: Is64BitInstallMode
Source: "..\dist\x64\{#FrontendName}"; DestDir: "{app}\x64"; Flags: ignoreversion restartreplace uninsrestartdelete; Check: Is64BitInstallMode

; ---- eSpeak NG's data, which OpenEvvFrontend.exe reads the languages made from it with --
Source: "..\dist\espeak-ng-data\*"; DestDir: "{app}\espeak-ng-data"; Flags: ignoreversion recursesubdirs createallsubdirs restartreplace uninsrestartdelete

; ---- every language: the engine modules (32-bit and 64-bit) and language.ini ----------
Source: "..\languages\*"; DestDir: "{app}\languages"; Flags: ignoreversion recursesubdirs createallsubdirs restartreplace uninsrestartdelete

; ---- the community pronunciation dictionary (CC0), and the record of which commit it is. A
; newer one that OpenEvvConfig downloads goes in %ProgramData%\OpenEVV\community-dictionary
; and is used instead for as long as it is the newer of the two.
Source: "..\dictionaries\community\*"; DestDir: "{app}\dictionaries\community"; Flags: ignoreversion

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

{ Deleting a file or an empty folder at the next restart, from setup and from the
  uninstaller alike: NewName 0 is NULL, which MoveFileEx takes for "delete". It only
  tidies up; nothing waits for that restart. }
function MoveFileEx(ExistingName: String; NewName: Cardinal; Flags: DWORD): BOOL;
  external 'MoveFileExW@kernel32.dll stdcall';

procedure DeleteAtNextRestart(const Path: String);
begin
  if not MoveFileEx(Path, 0, 4 { MOVEFILE_DELAY_UNTIL_REBOOT }) then
    Log('[openevv] could not queue for deletion at the next restart: ' + Path);
end;

const
  GW_HWNDPREV = 3;
  SWP_NOSIZE = $1;
  SWP_NOMOVE = $2;
  SWP_NOACTIVATE = $10;

var
  Summary: String;
  RegistrationOk: Boolean;
  RunListLabel: TNewStaticText;
  MovedAside: Integer;
  ProgramsUsingOld: String;

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

{ ---- files in use: renamed out of the way, so no restart is needed --------------------- }

{ A loaded DLL or a running program cannot be opened for writing. }
function InUse(const F: String): Boolean;
var
  S: TFileStream;
begin
  Result := False;
  try
    S := TFileStream.Create(F, fmOpenReadWrite or fmShareExclusive);
    S.Free;
  except
    Result := True;
  end;
end;

function IsOldCopy(const Name: String): Boolean;
begin
  Result := (Length(Name) > 4) and (Lowercase(Copy(Name, Length(Name) - 3, 4)) = '.old');
end;

function IsBinary(const Name: String): Boolean;
begin
  Result := (CompareText(ExtractFileExt(Name), '.dll') = 0) or (CompareText(ExtractFileExt(Name), '.exe') = 0);
end;

{ In Dir (and below it, if Recurse): .old copies left by an earlier install are deleted
  if nothing holds them any more, and every DLL or program something holds is renamed to
  the first free <name>.N.old and queued for deletion at the next restart - which only
  tidies up, and is never asked for. }
procedure MoveAsideIn(const Dir: String; Recurse: Boolean);
var
  FR: TFindRec;
  F, Old: String;
  N: Integer;
begin
  if not FindFirst(Dir + '\*', FR) then
    Exit;
  try
    repeat
      F := Dir + '\' + FR.Name;
      if (FR.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
      begin
        if Recurse and (FR.Name <> '.') and (FR.Name <> '..') then
          MoveAsideIn(F, True);
      end
      else if IsOldCopy(FR.Name) then
      begin
        if DeleteFile(F) then
          Note('removed an earlier copy nothing holds any more: ' + F);
      end
      else if IsBinary(FR.Name) and InUse(F) then
      begin
        N := 1;
        repeat
          Old := F + '.' + IntToStr(N) + '.old';
          N := N + 1;
        until not FileExists(Old);
        if RenameFile(F, Old) then
        begin
          Note('in use, renamed out of the way: ' + F + ' -> ' + ExtractFileName(Old));
          DeleteAtNextRestart(Old);
          MovedAside := MovedAside + 1;
        end
        else
          Note('in use and could not be renamed: ' + F + ' (it is replaced at the next restart)');
      end;
    until not FindNext(FR);
  finally
    FindClose(FR);
  end;
end;

{ Each folder under Dir and then Dir itself, deleted at the next restart if empty by then. }
procedure QueueFolderRemoval(const Dir: String);
var
  FR: TFindRec;
begin
  if FindFirst(Dir + '\*', FR) then
  try
    repeat
      if ((FR.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0) and (FR.Name <> '.') and (FR.Name <> '..') then
        QueueFolderRemoval(Dir + '\' + FR.Name);
    until not FindNext(FR);
  finally
    FindClose(FR);
  end;
  DeleteAtNextRestart(Dir);
end;

procedure MoveAsideFilesInUse;
begin
  MoveAsideIn(ExpandConstant('{app}\x64'), False);
  MoveAsideIn(ExpandConstant('{app}\x86'), False);
  MoveAsideIn(ExpandConstant('{app}\languages'), True);
end;

{ The programs that still have an OpenEVV SAPI DLL loaded, as "nvda.exe, notepad.exe";
  '' for none. OpenEvvConfig.exe --in-use looks in 32-bit and 64-bit programs alike;
  it runs elevated, as setup does, so it can see every user's programs. }
function ProgramsUsingOpenEvv(const Exe: String): String;
var
  ListFile: String;
  Lines: TArrayOfString;
  I, Code: Integer;
begin
  Result := '';
  ListFile := ExpandConstant('{tmp}\openevv-in-use.txt');
  if not Exec(Exe, '--in-use "' + ListFile + '"', '', SW_HIDE, ewWaitUntilTerminated, Code) or (Code <> 0) then
  begin
    Note(Format('could not list the programs using OpenEVV (%d)', [Code]));
    Exit;
  end;
  if LoadStringsFromFile(ListFile, Lines) then
    for I := 0 to GetArrayLength(Lines) - 1 do
      if Trim(Lines[I]) <> '' then
      begin
        if Result <> '' then
          Result := Result + ', ';
        Result := Result + Trim(Lines[I]);
      end;
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
    { A stand-in of realistic length, so the probe lays out the last page as setup does. }
    Summary := 'Accessibility probe: no voices were installed, so none were registered with Windows.';
  end;
#else
  if CurStep = ssInstall then
  begin
    MovedAside := 0;
    ProgramsUsingOld := '';
    MoveAsideFilesInUse;
    Note(Format('%d files in use renamed out of the way; no restart is needed for them', [MovedAside]));
  end
  else if CurStep = ssPostInstall then
  begin
    if MovedAside > 0 then
    begin
      if Is64BitInstallMode then
        ProgramsUsingOld := ProgramsUsingOpenEvv(ExpandConstant('{app}\x64\{#ConfigName}'))
      else
        ProgramsUsingOld := ProgramsUsingOpenEvv(ExpandConstant('{app}\x86\{#ConfigName}'));
      Note('programs still running the OpenEVV installed before: ' + ProgramsUsingOld);
    end;
    Note('checking the registration');
    RegistrationOk := True;
    if Is64BitInstallMode then
      RegistrationOk := CheckRegistration(HKEY_LOCAL_MACHINE_64, ExpandConstant('{app}\x64\{#DllName}'));
    RegistrationOk := CheckRegistration(HKEY_LOCAL_MACHINE_32, ExpandConstant('{app}\x86\{#DllName}')) and RegistrationOk;
    if RegistrationOk then
    begin
      Note('registration complete in every view');
      if Is64BitInstallMode then
        Summary := 'The voices are registered with Windows for 64-bit and for 32-bit programs.'
      else
        Summary := 'The voices are registered with Windows for 32-bit programs.';
    end
    else
    begin
      Note('REGISTRATION INCOMPLETE - see the entries above');
      Summary := 'The registration with Windows is incomplete: the entries that are missing or wrong are in install.log.';
    end;
    Note('the voices are not tested during setup; OpenEvvConfig.exe has a self-test button');

    { The log so far, where the configuration utility's "Open the log folder" button finds
      it. Copied again at the very end, complete. }
    CopyFile(ExpandConstant('{log}'), LogDir + '\install.log', False);

    if not RegistrationOk then
      SuppressibleMsgBox('OpenEVV SAPI5 is installed, but its registration with Windows is incomplete.' + #13#10#13#10 +
        Summary + #13#10#13#10 +
        'The details are in install.log in ' + LogDir + '.', mbError, MB_OK, IDOK);
  end
  else if CurStep = ssDone then
    CopyFile(ExpandConstant('{log}'), LogDir + '\install.log', False);
#endif
end;

{ The last page says what actually happened, in words a screen reader reads out. }
procedure CurPageChanged(CurPageID: Integer);
var
  S: String;
  Delta: Integer;
begin
  if CurPageID <> wpFinished then
    Exit;
  { No line may start with "#" here: the preprocessor would take it for a directive. }
  S := '{#AppName} {#MyAppVersion} is installed.' + #13#10#13#10 + Summary + #13#10#13#10 +
    'Choose any voice named OpenEVV in your screen reader or any SAPI 5 program. ' +
    'OpenEVV Configuration, on the desktop and in the Start menu, adjusts every voice, ' +
    'and its Diagnostics page can run a self-test that speaks them all.' + #13#10#13#10 +
    'Logs, including install.log: ' + LogDir;
  if ProgramsUsingOld <> '' then
    S := S + #13#10#13#10 + 'Windows does not need to restart. These programs were already running with ' +
      'the OpenEVV that was installed before, and keep using it until you close them and start them ' +
      'again: ' + ProgramsUsingOld + '. Every program started from now on uses this version.'
  else if MovedAside > 0 then
    S := S + #13#10#13#10 + 'Windows does not need to restart. A program that was already using an ' +
      'OpenEVV voice keeps the earlier version until you close it and start it again; every program ' +
      'started from now on uses this version.';
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
    { Files a running program still holds are renamed rather than left for a restart
      to delete, so uninstalling never asks for one either. }
    MovedAside := 0;
    MoveAsideFilesInUse;
    Log(Format('[openevv] %d files in use renamed out of the way, deleted at the next restart', [MovedAside]));
  end
  else if CurUninstallStep = usPostUninstall then
  begin
    { What is left is only those renamed files; their folders go with them at the next
      restart, after the files, in the order they were queued. }
    if DirExists(ExpandConstant('{app}')) then
    begin
      QueueFolderRemoval(ExpandConstant('{app}'));
      Log('[openevv] ' + ExpandConstant('{app}') + ' still holds files in use; it goes at the next restart');
    end;
    if RegKeyExists(HKEY_LOCAL_MACHINE_32, '{#TokenEnumsKey}') or
       (IsWin64 and RegKeyExists(HKEY_LOCAL_MACHINE_64, '{#TokenEnumsKey}')) then
      Log('[openevv] WARNING: an OpenEVV voice list key is still present')
    else
      Log('[openevv] the OpenEVV voices are no longer registered');
    { The logs go, and so does a community dictionary that was downloaded: it is a copy
      of what is on GitHub. Language packs and dictionaries a user added are theirs and
      stay; their folders are removed only if they are empty. }
    Data := ExpandConstant('{commonappdata}\OpenEVV');
    DelTree(Data + '\Logs', True, True, True);
    DelTree(Data + '\community-dictionary', True, True, True);
    RemoveDir(Data + '\languages');
    RemoveDir(Data + '\dictionaries');
    if RemoveDir(Data) then
      Log('[openevv] removed ' + Data)
    else
      Log('[openevv] kept ' + Data + ': it holds language packs or dictionaries you added');
  end;
#endif
end;
