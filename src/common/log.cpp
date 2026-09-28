#include "log.h"

#include <atomic>
#include <cstdarg>
#include <cstdio>
#include <mutex>
#include <shlobj.h>
#include <windows.h>

namespace evv {
namespace log {

namespace {

constexpr LONGLONG kMaxBytes = 2 * 1024 * 1024;

std::mutex g_lock;
std::atomic<int> g_level{kStandard};
HANDLE g_file = INVALID_HANDLE_VALUE;
std::wstring g_dir;
std::wstring g_path;
std::wstring g_component = L"openevv";
std::wstring g_app;

std::wstring exe_stem()
{
    wchar_t buf[MAX_PATH];
    const DWORD n = GetModuleFileNameW(nullptr, buf, MAX_PATH);
    std::wstring p(buf, n);
    const size_t slash = p.find_last_of(L"\\/");
    std::wstring name = slash == std::wstring::npos ? p : p.substr(slash + 1);
    const size_t dot = name.find_last_of(L'.');
    if (dot != std::wstring::npos) {
        name.resize(dot);
    }
    for (auto& c : name) {
        c = static_cast<wchar_t>(towlower(c));
        if (c == L' ') {
            c = L'_';
        }
    }
    return name.empty() ? L"unknown" : name;
}

bool ensure_dir(const std::wstring& dir)
{
    const int rc = SHCreateDirectoryExW(nullptr, dir.c_str(), nullptr);
    return rc == ERROR_SUCCESS || rc == ERROR_ALREADY_EXISTS || rc == ERROR_FILE_EXISTS;
}

HANDLE open_append(const std::wstring& path)
{
    return CreateFileW(path.c_str(), FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr,
                       OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
}

// Caller holds g_lock.
bool open_locked()
{
    if (g_file != INVALID_HANDLE_VALUE) {
        return true;
    }
    if (g_path.empty()) {
        wchar_t* pd = nullptr;
        std::wstring dir;
        if (SUCCEEDED(SHGetKnownFolderPath(FOLDERID_ProgramData, 0, nullptr, &pd)) && pd) {
            dir = std::wstring(pd) + L"\\OpenEVV\\Logs";
        }
        CoTaskMemFree(pd);
        const std::wstring file = g_component + L"-" + (g_app.empty() ? exe_stem() : g_app) + L".log";
        HANDLE h = INVALID_HANDLE_VALUE;
        if (!dir.empty() && ensure_dir(dir)) {
            h = open_append(dir + L"\\" + file);
        }
        if (h == INVALID_HANDLE_VALUE) {
            wchar_t tmp[MAX_PATH];
            const DWORD n = GetTempPathW(MAX_PATH, tmp);
            dir = std::wstring(tmp, n) + L"OpenEVV\\Logs";
            if (ensure_dir(dir)) {
                h = open_append(dir + L"\\" + file);
            }
        }
        if (h == INVALID_HANDLE_VALUE) {
            return false;
        }
        g_dir = dir;
        g_path = dir + L"\\" + file;
        g_file = h;
        return true;
    }
    g_file = open_append(g_path);
    return g_file != INVALID_HANDLE_VALUE;
}

// Caller holds g_lock.
void rotate_if_needed_locked()
{
    LARGE_INTEGER size{};
    if (g_file == INVALID_HANDLE_VALUE || !GetFileSizeEx(g_file, &size) || size.QuadPart < kMaxBytes) {
        return;
    }
    CloseHandle(g_file);
    g_file = INVALID_HANDLE_VALUE;
    std::wstring old = g_path;
    old.insert(old.size() - 4, L".old");
    MoveFileExW(g_path.c_str(), old.c_str(), MOVEFILE_REPLACE_EXISTING);
    open_locked();
}

std::string stamp()
{
    SYSTEMTIME t;
    GetLocalTime(&t);
    char b[96];
    snprintf(b, sizeof b, "%04u-%02u-%02u %02u:%02u:%02u.%03u [%5lu:%5lu] ", t.wYear, t.wMonth, t.wDay, t.wHour,
             t.wMinute, t.wSecond, t.wMilliseconds, GetCurrentProcessId(), GetCurrentThreadId());
    return b;
}

std::string vformat(const char* fmt, va_list ap)
{
    char local[1024]; // not "small": rpcndr.h defines that as a macro
    va_list ap2;
    va_copy(ap2, ap);
    const int n = vsnprintf(local, sizeof local, fmt, ap2);
    va_end(ap2);
    if (n < 0) {
        return "(log format error)";
    }
    if (static_cast<size_t>(n) < sizeof local) {
        return std::string(local, static_cast<size_t>(n));
    }
    std::string big(static_cast<size_t>(n) + 1, '\0');
    vsnprintf(big.data(), big.size(), fmt, ap);
    big.resize(static_cast<size_t>(n));
    return big;
}

void raw_write(const std::string& text)
{
    std::lock_guard<std::mutex> guard(g_lock);
    if (!open_locked()) {
        return;
    }
    rotate_if_needed_locked();
    if (g_file == INVALID_HANDLE_VALUE) {
        return;
    }
    DWORD written = 0;
    WriteFile(g_file, text.data(), static_cast<DWORD>(text.size()), &written, nullptr);
}

} // namespace

void init(const std::wstring& component, const std::wstring& app)
{
    std::lock_guard<std::mutex> guard(g_lock);
    if (g_file != INVALID_HANDLE_VALUE) {
        CloseHandle(g_file);
        g_file = INVALID_HANDLE_VALUE;
    }
    g_component = component;
    g_app.clear();
    for (wchar_t c : app) {
        // a client name goes into a file name
        g_app.push_back((iswalnum(c) || c == L'-' || c == L'_') ? static_cast<wchar_t>(towlower(c)) : L'_');
    }
    g_path.clear();
}

void set_level(int lvl)
{
    g_level = lvl < kOff ? kOff : (lvl > kFull ? kFull : lvl);
}

int level()
{
    return g_level;
}

bool enabled(int lvl)
{
    return lvl > kOff && g_level >= lvl;
}

void write(int lvl, const char* fmt, ...)
{
    if (!enabled(lvl)) {
        return;
    }
    va_list ap;
    va_start(ap, fmt);
    std::string line = stamp() + vformat(fmt, ap) + "\r\n";
    va_end(ap);
    raw_write(line);
}

std::wstring directory()
{
    std::lock_guard<std::mutex> guard(g_lock);
    open_locked();
    return g_dir;
}

std::wstring file_path()
{
    std::lock_guard<std::mutex> guard(g_lock);
    open_locked();
    return g_path;
}

Batch::~Batch()
{
    flush();
}

void Batch::add(int lvl, const char* fmt, ...)
{
    if (!enabled(lvl)) {
        return;
    }
    va_list ap;
    va_start(ap, fmt);
    lines_ += stamp() + vformat(fmt, ap) + "\r\n";
    va_end(ap);
}

void Batch::flush()
{
    if (!lines_.empty()) {
        raw_write(lines_);
        lines_.clear();
    }
}

} // namespace log
} // namespace evv
