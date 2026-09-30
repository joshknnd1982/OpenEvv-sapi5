// Where everything is at run time.
//
// Installed layout:
//   {app}\x86\  OpenEvvSAPI.dll, OpenEvvHost.exe, OpenEvvConfig.exe (32-bit)
//   {app}\x64\  the same, 64-bit
//   {app}\languages\<tag>\  language.ini and the two module DLLs
//   %ProgramData%\OpenEVV\languages\<tag>\  languages a user dropped in
//   %ProgramData%\OpenEVV\dictionaries\<tag>\  user dictionaries
//   {app}\dictionaries\community\  the community dictionary installed with OpenEVV, and
//   %ProgramData%\OpenEVV\community-dictionary\  a newer one downloaded (community_dict.h)
//   %ProgramData%\OpenEVV\Logs\  logs
//   %APPDATA%\OpenEVV\settings.ini  per-user settings
//
// A build tree is found the same way: the root is the nearest folder above
// the binary that holds a "languages" folder. OPENEVV_ROOT overrides it, and
// OPENEVV_DATA stands in for %ProgramData%\OpenEVV.
#pragma once

#include <string>
#include <vector>
#include <windows.h>

namespace evv {

// Directory (no trailing slash) of the module containing `address`.
std::wstring module_dir_of(const void* address);
// Directory of this binary.
std::wstring self_dir();

bool file_exists(const std::wstring& path);
bool dir_exists(const std::wstring& path);
bool ensure_dir(const std::wstring& path);

// The folder holding "languages" (and, installed, x86/x64).
std::wstring install_root();
// %ProgramData%\OpenEVV, created if missing (may be empty on failure).
std::wstring data_dir();
// Every folder language packs are read from, in priority order: the user's
// drop-in folder first, so a pack there can replace a shipped one.
std::vector<std::wstring> language_dirs();
// Where a user drops a new language (%ProgramData%\OpenEVV\languages).
std::wstring user_language_dir();
// %ProgramData%\OpenEVV\dictionaries\<tag>
std::wstring user_dictionary_dir(const std::wstring& tag);
// %APPDATA%\OpenEVV\settings.ini
std::wstring settings_path();
// The engine host beside this binary.
std::wstring host_exe_path();

std::wstring exe_path();
// This process's executable name, lower-case, no extension.
std::wstring exe_stem();

} // namespace evv
