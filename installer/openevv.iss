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
; The languages are chosen on the standard "Select Components" page, reworded as "Select languages":
; one check box per language pack, and four ready-made choices (the ten OpenEVV languages, English
; only, all of them, custom). The list is generated from languages\ by make_components.py into
; generated\*.inc, and this script stops the build when languages\ holds a pack the list lacks. A
; pack that only lends its engine modules to other packs is installed when a language that speaks
; with it is chosen, and removed when none is. Installing over an earlier version offers the
; languages that are installed, so nothing goes unless it is unchecked, and installs and removes
; what is changed; /TYPE=full or /COMPONENTS=... on the command line choose for an unattended install.
;
; Registration is written by the [Registry] section rather than by regsvr32, so it is
; logged entry by entry and does not depend on loading the DLLs during setup. Uninstall
; removes it three independent ways: DllUnregisterServer, the [Registry] uninsdeletekey
; flags, and a sweep of both registry views in CurUninstallStepChanged.
;
; ISCC.exe /DProbe installer\openevv.iss builds the accessibility probe: the same wizard
; and pages under its own AppId, per user and without elevation, installing only a text
; file and each language pack's language.ini, and touching no registration, settings or
; logs. installer_a11y.exe walks it through MSAA on a private desktop, and
; test_language_choice.ps1 installs and upgrades it with different choices of languages.

; Bump MyAppVersion with src\common\version.h and project() in CMakeLists.txt.
#define MyAppVersion   "1.2.4"
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

; ISCC.exe /DProbe /DProbeFullPacks installs each pack's files as the real installer does, but per
; user and with no registration: to check what each choice of languages really brings with it.
#if defined(Probe) && !defined(ProbeFullPacks)
#define PackMask "language.ini"
#else
#define PackMask "*"
#endif

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
AppComments=The OpenEVV engine (IBM Embedded ViaVoice, the Eloquence voice, rebuilt as C) as SAPI 5 voices for 32-bit and 64-bit programs: openevv's ten languages and 145 more read by eSpeak NG to choose from, eight voices each, with a configuration utility.
UninstallDisplayName={#AppName}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductName={#AppName}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} {#MyAppVersion} setup
VersionInfoCopyright=Wrapper: MIT. eSpeak NG front-end and data: GNU GPL v3. openevv engine: MIT. Language data: IBM, see NOTICE.
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

[Messages]
; The standard Select Components page, worded for what it chooses. Its first control is the list of
; ready-made choices, then the check boxes, one per language.
WizardSelectComponents=Select languages
SelectComponentsDesc=Which languages should be installed?
SelectComponentsLabel2=Every language adds eight voices to every SAPI 5 program, so install only the languages you will use. Choose a type of installation, or Custom to check languages one by one. Run this installer again to add or remove languages. Click Next to continue.

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut to OpenEVV Configuration"; GroupDescription: "Additional shortcuts:"

; ---- the languages. generated\*.inc is written by make_components.py from languages\*\language.ini.
[Types]
#include "generated\types.inc"

; A pack in languages\ that the generated list does not know would be left out of the installer
; without a word, so the build stops instead.
#define FindHandle
#define FindResult
#sub CheckPackListed
  #define PackFolder FindGetFileName(FindHandle)
  #if (PackFolder != ".") && (PackFolder != "..") && (Pos("|" + PackFolder + "|", LangTags) == 0)
    #expr Error("languages\" + PackFolder + " is not in installer\generated: run  python installer\make_components.py")
  #endif
#endsub
#for {FindHandle = FindResult = FindFirst(AddBackslash(SourcePath) + "..\languages\*", faDirectory); FindResult; FindResult = FindNext(FindHandle)} CheckPackListed

[Components]
#include "generated\components.inc"

#ifdef Probe
[Files]
Source: "before_install.txt"; DestDir: "{app}"
#include "generated\files.inc"
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

; ---- the languages that were chosen: each pack's engine modules (32-bit and 64-bit) and
; language.ini, and the packs that only lend their modules to the languages that need them.
#include "generated\files.inc"

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
  TypesLabel, LanguagesLabel: TNewStaticText;
  SelectAllButton, SelectNoneButton: TNewButton;
  LanguagePageLaidOut: Boolean;
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

{ ---- the choice of languages ----------------------------------------------------------- }

{ Every pack that languages\ holds, as generated\code.inc lists them. A pack that has a
  component is a language; one that has none only lends its engine modules, and is wanted
  when a language that names it as its template is installed. }
var
  PackCount: Integer;
  PackTag, PackComp, PackTemplate, PackName: array of String;
  SelectionDir: String;      { the folder whose installed languages were last offered }
  LanguagesText: String;     { what the last page says about the languages }

procedure AddPack(const Tag, Comp, Template, Name: String);
begin
  SetArrayLength(PackTag, PackCount + 1);
  SetArrayLength(PackComp, PackCount + 1);
  SetArrayLength(PackTemplate, PackCount + 1);
  SetArrayLength(PackName, PackCount + 1);
  PackTag[PackCount] := Tag;
  PackComp[PackCount] := Comp;
  PackTemplate[PackCount] := Template;
  PackName[PackCount] := Name;
  PackCount := PackCount + 1;
end;

#include "generated\code.inc"

function PackFolder(const AppDir, Tag: String): String;
begin
  Result := AppDir + '\languages\' + Tag;
end;

function PackInstalled(const AppDir, Tag: String): Boolean;
begin
  Result := FileExists(PackFolder(AppDir, Tag) + '\language.ini');
end;

{ The person installing named the languages on the command line: /TYPE=full, or
  /COMPONENTS="openevv\enus,espeak\nb". Nothing then overrides that. }
function LanguagesChosenOnCommandLine: Boolean;
begin
  Result := (ExpandConstant('{param:TYPE|}') <> '') or (ExpandConstant('{param:COMPONENTS|}') <> '');
end;

function CountSelectedLanguages: Integer;
var
  I: Integer;
begin
  Result := 0;
  for I := 0 to PackCount - 1 do
    if (PackComp[I] <> '') and WizardIsComponentSelected(PackComp[I]) then
      Result := Result + 1;
end;

{ The list of types of installation says which type the languages that are checked make up: all
  of them, the ten the engine speaks itself, English only, or else Custom. Setup does this when
  a check box is clicked, but not when the checks are set here, and a list that says "the ten
  OpenEVV languages" over 157 checked languages would be wrong for whoever reads it. }
procedure ShowTypeOfSelection;
var
  I, Total, Selected, Native, NativeSelected, EnglishSelected: Integer;
  Checked: Boolean;
begin
  Total := 0;
  Selected := 0;
  Native := 0;
  NativeSelected := 0;
  EnglishSelected := 0;
  for I := 0 to PackCount - 1 do
    if PackComp[I] <> '' then
    begin
      Checked := WizardIsComponentSelected(PackComp[I]);
      Total := Total + 1;
      if Copy(PackComp[I], 1, 8) = 'openevv\' then
        Native := Native + 1;
      if Checked then
      begin
        Selected := Selected + 1;
        if Copy(PackComp[I], 1, 8) = 'openevv\' then
          NativeSelected := NativeSelected + 1;
        if IsEnglishTag(PackTag[I]) then
          EnglishSelected := EnglishSelected + 1;
      end;
    end;
  if Selected = Total then
    WizardForm.TypesCombo.ItemIndex := TypeFull
  else if (Selected = Native) and (NativeSelected = Native) then
    WizardForm.TypesCombo.ItemIndex := TypeOpenevv
  else if (Selected = 2) and (EnglishSelected = 2) then
    WizardForm.TypesCombo.ItemIndex := TypeEnglish
  else
    WizardForm.TypesCombo.ItemIndex := TypeCustom;
end;

{ Every language checked, or none: the two buttons under the list. The groups are set too,
  since a group cannot be checked without one of its languages, nor a language without its group. }
procedure SelectEveryLanguage(All: Boolean);
var
  I: Integer;
  List: String;
begin
  List := '';
  for I := 0 to PackCount - 1 do
    if PackComp[I] <> '' then
    begin
      if List <> '' then
        List := List + ',';
      if All then
        List := List + PackComp[I]
      else
        List := List + '!' + PackComp[I];
    end;
  if All then
    List := '*openevv,*espeak,' + List
  else
    List := List + ',!openevv,!espeak';
  WizardSelectComponents(List);
  ShowTypeOfSelection;
end;

procedure SelectAllButtonClick(Sender: TObject);
begin
  SelectEveryLanguage(True);
end;

procedure SelectNoneButtonClick(Sender: TObject);
begin
  SelectEveryLanguage(False);
end;

{ Upgrading: the wizard offers the languages that are installed in AppDir, and only those, so
  that installing over an earlier version never removes or adds a language nobody asked about.
  Earlier versions installed them all and recorded nothing about it, so what is on disk is
  the only record there is. A folder with no OpenEVV languages in it changes nothing. }
procedure SelectInstalledLanguages(const AppDir: String);
var
  I, Found: Integer;
  List: String;
begin
  SelectionDir := AppDir;
  Found := 0;
  List := '';
  for I := 0 to PackCount - 1 do
    if PackComp[I] <> '' then
    begin
      if List <> '' then
        List := List + ',';
      if PackInstalled(AppDir, PackTag[I]) then
      begin
        List := List + PackComp[I];
        Found := Found + 1;
      end
      else
        List := List + '!' + PackComp[I];
    end;
  if Found = 0 then
  begin
    Note('no OpenEVV language is installed in ' + AppDir + ': the standard choice is offered');
    Exit;
  end;
  WizardSelectComponents(List);
  ShowTypeOfSelection;
  Note(Format('%d languages are installed in %s and are offered again', [Found, AppDir]));
end;

procedure RemovePack(const Dir: String);
begin
  { language.ini first: from that moment the pack is in no program's voice list }
  DeleteFile(Dir + '\language.ini');
  if DelTree(Dir, True, True, True) then
    Note('removed ' + Dir)
  else
    Note('removed what could be of ' + Dir + '; a file a program still holds is left until that program has closed');
end;

{ True if a pack in Root\languages, other than the ones this setup knows, speaks with the
  module pack Tag: one a person dropped in by hand, or added with OpenEVV Configuration. }
function OtherPackUses(const Root, Tag: String): Boolean;
var
  FR: TFindRec;
  Ini: String;
begin
  Result := False;
  if not FindFirst(Root + '\languages\*', FR) then
    Exit;
  try
    repeat
      if ((FR.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0) and (FR.Name <> '.') and (FR.Name <> '..') then
      begin
        Ini := Root + '\languages\' + FR.Name + '\language.ini';
        if FileExists(Ini) and (CompareText(GetIniString('Language', 'Template', '', Ini), Tag) = 0) then
        begin
          Result := True;
          Exit;
        end;
      end;
    until not FindNext(FR);
  finally
    FindClose(FR);
  end;
end;

{ A module pack is wanted while a language that is being installed, or one that is already
  there, speaks with it. }
function ModulePackWanted(const Tag: String): Boolean;
var
  I: Integer;
begin
  Result := True;
  for I := 0 to PackCount - 1 do
    if (PackComp[I] <> '') and (CompareText(PackTemplate[I], Tag) = 0) and WizardIsComponentSelected(PackComp[I]) then
      Exit;
  if OtherPackUses(ExpandConstant('{app}'), Tag) or OtherPackUses(ExpandConstant('{commonappdata}\OpenEVV'), Tag) then
    Exit;
  Result := False;
end;

{ Installing over an earlier version installs what is checked and removes what is not: the
  installer only copies files, so the languages that were unchecked would stay in every voice list. }
procedure RemoveUnselectedLanguages;
var
  I, Removed: Integer;
  AppDir: String;
begin
  AppDir := ExpandConstant('{app}');
  if CountSelectedLanguages = 0 then
  begin
    Note('no language is selected: none is removed');
    Exit;
  end;
  Removed := 0;
  for I := 0 to PackCount - 1 do
    if (PackComp[I] <> '') and not WizardIsComponentSelected(PackComp[I]) and DirExists(PackFolder(AppDir, PackTag[I])) then
    begin
      Note('language not selected, removed: ' + PackName[I] + ' (' + PackTag[I] + ')');
      RemovePack(PackFolder(AppDir, PackTag[I]));
      Removed := Removed + 1;
    end;
  { after the languages: a module pack goes when the last language that used it has gone }
  for I := 0 to PackCount - 1 do
    if (PackComp[I] = '') and DirExists(PackFolder(AppDir, PackTag[I])) and not ModulePackWanted(PackTag[I]) then
    begin
      Note('module pack no language uses any more, removed: ' + PackTag[I]);
      RemovePack(PackFolder(AppDir, PackTag[I]));
    end;
  Note(Format('%d unselected languages removed', [Removed]));
end;

{ What is installed now, stated for the last page and the log. }
procedure DescribeInstalledLanguages;
var
  I, N: Integer;
  Names, AppDir: String;
begin
  AppDir := ExpandConstant('{app}');
  N := 0;
  Names := '';
  for I := 0 to PackCount - 1 do
    if (PackComp[I] <> '') and PackInstalled(AppDir, PackTag[I]) then
    begin
      N := N + 1;
      if Names <> '' then
        Names := Names + ', ';
      Names := Names + PackName[I];
      Note('language installed: ' + PackName[I] + ' (' + PackTag[I] + ')');
    end;
  Note(Format('%d languages installed, %d voices', [N, N * 8]));
  if N = 1 then
    LanguagesText := 'Installed: 1 language, 8 voices: ' + Names + '.'
  else if N <= 4 then
    LanguagesText := Format('Installed: %d languages, %d voices: %s.', [N, N * 8, Names])
  else
    LanguagesText := Format('Installed: %d languages, %d voices.', [N, N * 8]);
  LanguagesText := LanguagesText + ' Run this installer again to add or remove languages.';
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

  RegisterPacks;
  if not LanguagesChosenOnCommandLine then
    SelectInstalledLanguages(WizardDirValue);
end;

{ A setup with no language chosen would remove every language there is on an upgrade. }
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  { Next on the languages page, and Install after it: the page that has none checked stays. }
  if ((CurPageID = wpSelectComponents) or (CurPageID = wpReady)) and (CountSelectedLanguages = 0) then
  begin
    MsgBox('No language is selected. Select at least one language, or choose one of the types of installation, ' +
      'before you go on: OpenEVV cannot be installed without a language.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
#ifdef Probe
  if CurStep = ssInstall then
    RemoveUnselectedLanguages
  else if CurStep = ssPostInstall then
  begin
    { A stand-in of realistic length, so the probe lays out the last page as setup does. }
    Summary := 'Accessibility probe: no voices were installed, so none were registered with Windows.';
    DescribeInstalledLanguages;
  end;
#else
  if CurStep = ssInstall then
  begin
    MovedAside := 0;
    ProgramsUsingOld := '';
    MoveAsideFilesInUse;
    Note(Format('%d files in use renamed out of the way; no restart is needed for them', [MovedAside]));
    RemoveUnselectedLanguages;
  end
  else if CurStep = ssPostInstall then
  begin
    DescribeInstalledLanguages;
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

{ MSAA names a list after the static text just before it in the z-order. On the languages page
  the list of types and the list of languages have none: a screen reader would say "combo box"
  and "list" and nothing more, or read the whole paragraph above as the combo box's name. Each
  gets a short label of its own, directly before it; the page is made room for them. It is done
  when the page is first shown, after setup has laid the page out itself. }
procedure LayoutLanguagePage;
var
  Gap, Shift: Integer;
begin
  if LanguagePageLaidOut then
    Exit;
  LanguagePageLaidOut := True;
  Gap := ScaleY(4);

  TypesLabel := TNewStaticText.Create(WizardForm);
  TypesLabel.Parent := WizardForm.SelectComponentsPage;
  TypesLabel.Caption := 'Type of installation:';
  TypesLabel.Left := WizardForm.TypesCombo.Left;
  TypesLabel.Top := WizardForm.TypesCombo.Top;
  WizardForm.TypesCombo.Top := TypesLabel.Top + TypesLabel.Height + Gap;
  SetWindowPos(TypesLabel.Handle, GetWindow(WizardForm.TypesCombo.Handle, GW_HWNDPREV), 0, 0, 0, 0,
    SWP_NOSIZE or SWP_NOMOVE or SWP_NOACTIVATE);

  LanguagesLabel := TNewStaticText.Create(WizardForm);
  LanguagesLabel.Parent := WizardForm.SelectComponentsPage;
  LanguagesLabel.Caption := 'Languages to install:';
  LanguagesLabel.Left := WizardForm.ComponentsList.Left;
  LanguagesLabel.Top := WizardForm.TypesCombo.Top + WizardForm.TypesCombo.Height + Gap * 2;
  Shift := LanguagesLabel.Top + LanguagesLabel.Height + Gap - WizardForm.ComponentsList.Top;
  WizardForm.ComponentsList.Top := WizardForm.ComponentsList.Top + Shift;
  WizardForm.ComponentsList.Height := WizardForm.ComponentsList.Height - Shift;
  SetWindowPos(LanguagesLabel.Handle, GetWindow(WizardForm.ComponentsList.Handle, GW_HWNDPREV), 0, 0, 0, 0,
    SWP_NOSIZE or SWP_NOMOVE or SWP_NOACTIVATE);

  { Two buttons under the list, taking their room from it. They are made last, so they come
    after the list when Tab is pressed. }
  SelectAllButton := TNewButton.Create(WizardForm);
  SelectAllButton.Parent := WizardForm.SelectComponentsPage;
  SelectAllButton.Caption := 'Select &all languages';
  SelectAllButton.Width := ScaleX(140);
  SelectAllButton.Height := ScaleY(23);
  SelectAllButton.OnClick := @SelectAllButtonClick;
  SelectNoneButton := TNewButton.Create(WizardForm);
  SelectNoneButton.Parent := WizardForm.SelectComponentsPage;
  SelectNoneButton.Caption := 'Select n&o languages';
  SelectNoneButton.Width := ScaleX(140);
  SelectNoneButton.Height := ScaleY(23);
  SelectNoneButton.OnClick := @SelectNoneButtonClick;
  Shift := SelectAllButton.Height + Gap * 2;
  WizardForm.ComponentsList.Height := WizardForm.ComponentsList.Height - Shift;
  SelectAllButton.Left := WizardForm.ComponentsList.Left;
  SelectAllButton.Top := WizardForm.ComponentsList.Top + WizardForm.ComponentsList.Height + Gap;
  SelectNoneButton.Left := SelectAllButton.Left + SelectAllButton.Width + ScaleX(8);
  SelectNoneButton.Top := SelectAllButton.Top;
end;

{ The directory can be changed on the page before the languages; the languages installed there
  are then the ones to offer. Going back and forth without changing it keeps what was checked.
  The last page says what actually happened, in words a screen reader reads out. }
procedure CurPageChanged(CurPageID: Integer);
var
  S: String;
  Delta: Integer;
begin
  if CurPageID = wpSelectComponents then
  begin
    LayoutLanguagePage;
    if not LanguagesChosenOnCommandLine and (CompareText(WizardDirValue, SelectionDir) <> 0) then
      SelectInstalledLanguages(WizardDirValue);
  end;
  if CurPageID <> wpFinished then
    Exit;
  { No line may start with "#" here: the preprocessor would take it for a directive. }
  S := '{#AppName} {#MyAppVersion} is installed.' + #13#10#13#10 + Summary + #13#10#13#10 +
    LanguagesText + #13#10#13#10 +
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
