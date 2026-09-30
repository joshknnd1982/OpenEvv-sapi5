#include "paths.h"

#include <shlobj.h>

namespace evv {

namespace {

std::wstring known_folder(REFKNOWNFOLDERID id)
{
    wchar_t* p = nullptr;
    std::wstring out;
    if (SUCCEEDED(SHGetKnownFolderPath(id, 0, nullptr, &p)) && p) {
        out = p;
    }
    CoTaskMemFree(p);
    return out;
}

std::wstring parent_of(const std::wstring& dir)
{
    const size_t slash = dir.find_last_of(L"\\/");
    return slash == std::wstring::npos ? std::wstring() : dir.substr(0, slash);
}

} // namespace

bool file_exists(const std::wstring& path)
{
    const DWORD a = GetFileAttributesW(path.c_str());
    return a != INVALID_FILE_ATTRIBUTES && !(a & FILE_ATTRIBUTE_DIRECTORY);
}

bool dir_exists(const std::wstring& path)
{
    const DWORD a = GetFileAttributesW(path.c_str());
    return a != INVALID_FILE_ATTRIBUTES && (a & FILE_ATTRIBUTE_DIRECTORY);
}

bool ensure_dir(const std::wstring& path)
{
    if (path.empty()) return false;
    const int rc = SHCreateDirectoryExW(nullptr, path.c_str(), nullptr);
    return rc == ERROR_SUCCESS || rc == ERROR_ALREADY_EXISTS || rc == ERROR_FILE_EXISTS;
}

std::wstring module_dir_of(const void* address)
{
    HMODULE h = nullptr;
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                            static_cast<LPCWSTR>(address), &h)) {
        return {};
    }
    std::wstring buf(32768, L'\0');
    const DWORD n = GetModuleFileNameW(h, buf.data(), static_cast<DWORD>(buf.size()));
    if (n == 0 || n >= buf.size()) {
        return {};
    }
    buf.resize(n);
    return parent_of(buf);
}

std::wstring self_dir()
{
    static const int anchor = 0;
    return module_dir_of(&anchor);
}

std::wstring install_root()
{
    wchar_t env[MAX_PATH];
    const DWORD n = GetEnvironmentVariableW(L"OPENEVV_ROOT", env, MAX_PATH);
    if (n > 0 && n < MAX_PATH && dir_exists(env)) {
        return env;
    }
    std::wstring dir = self_dir();
    for (int level = 0; level <= 5 && !dir.empty(); ++level) {
        if (dir_exists(dir + L"\\languages")) {
            return dir;
        }
        dir = parent_of(dir);
    }
    // Nothing found: the parent of an x86/x64 folder, else this folder.
    dir = self_dir();
    const size_t slash = dir.find_last_of(L"\\/");
    const std::wstring leaf = slash == std::wstring::npos ? dir : dir.substr(slash + 1);
    if (_wcsicmp(leaf.c_str(), L"x86") == 0 || _wcsicmp(leaf.c_str(), L"x64") == 0) {
        return parent_of(dir);
    }
    return dir;
}

std::wstring data_dir()
{
    // Tests point this at a scratch folder, never the machine's own.
    wchar_t env[MAX_PATH];
    const DWORD n = GetEnvironmentVariableW(L"OPENEVV_DATA", env, MAX_PATH);
    if (n > 0 && n < MAX_PATH) {
        ensure_dir(env);
        return env;
    }
    const std::wstring pd = known_folder(FOLDERID_ProgramData);
    if (pd.empty()) return {};
    const std::wstring dir = pd + L"\\OpenEVV";
    ensure_dir(dir);
    return dir;
}

std::wstring user_language_dir()
{
    const std::wstring d = data_dir();
    return d.empty() ? std::wstring() : d + L"\\languages";
}

std::vector<std::wstring> language_dirs()
{
    std::vector<std::wstring> dirs;
    const std::wstring user = user_language_dir();
    if (!user.empty()) dirs.push_back(user);
    const std::wstring shipped = install_root() + L"\\languages";
    if (_wcsicmp(shipped.c_str(), user.c_str()) != 0) dirs.push_back(shipped);
    return dirs;
}

std::wstring user_dictionary_dir(const std::wstring& tag)
{
    const std::wstring d = data_dir();
    return d.empty() ? std::wstring() : d + L"\\dictionaries\\" + tag;
}

std::wstring settings_path()
{
    // Asked before every utterance, and it cannot change while we run.
    static const std::wstring path = [] {
        // Tests point this at a scratch file, never the user's own.
        wchar_t env[MAX_PATH];
        const DWORD n = GetEnvironmentVariableW(L"OPENEVV_SETTINGS", env, MAX_PATH);
        if (n > 0 && n < MAX_PATH) return std::wstring(env);
        std::wstring appdata = known_folder(FOLDERID_RoamingAppData);
        if (appdata.empty()) {
            wchar_t tmp[MAX_PATH];
            const DWORD n = GetTempPathW(MAX_PATH, tmp);
            appdata.assign(tmp, n);
        }
        const std::wstring dir = appdata + L"\\OpenEVV";
        ensure_dir(dir);
        return dir + L"\\settings.ini";
    }();
    return path;
}

std::wstring host_exe_path()
{
    return self_dir() + L"\\OpenEvvHost.exe";
}

std::wstring exe_path()
{
    std::wstring buf(32768, L'\0');
    const DWORD n = GetModuleFileNameW(nullptr, buf.data(), static_cast<DWORD>(buf.size()));
    buf.resize(n < buf.size() ? n : 0);
    return buf;
}

std::wstring exe_stem()
{
    const std::wstring p = exe_path();
    const size_t slash = p.find_last_of(L"\\/");
    std::wstring name = slash == std::wstring::npos ? p : p.substr(slash + 1);
    const size_t dot = name.find_last_of(L'.');
    if (dot != std::wstring::npos) name.resize(dot);
    for (auto& c : name) c = static_cast<wchar_t>(towlower(c));
    return name.empty() ? L"unknown" : name;
}

} // namespace evv
