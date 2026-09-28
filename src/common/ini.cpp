#include "ini.h"

#include <windows.h>

#include <cstdio>
#include <cwchar>

namespace evv {

std::wstring utf8_to_wide(const std::string& s)
{
    if (s.empty()) return {};
    const int n = MultiByteToWideChar(CP_UTF8, 0, s.data(), static_cast<int>(s.size()), nullptr, 0);
    std::wstring w(static_cast<size_t>(n), L'\0');
    MultiByteToWideChar(CP_UTF8, 0, s.data(), static_cast<int>(s.size()), w.data(), n);
    return w;
}

std::string wide_to_utf8(const std::wstring& s)
{
    if (s.empty()) return {};
    const int n = WideCharToMultiByte(CP_UTF8, 0, s.data(), static_cast<int>(s.size()), nullptr, 0, nullptr, nullptr);
    std::string out(static_cast<size_t>(n), '\0');
    WideCharToMultiByte(CP_UTF8, 0, s.data(), static_cast<int>(s.size()), out.data(), n, nullptr, nullptr);
    return out;
}

std::wstring trim(const std::wstring& s)
{
    size_t b = 0, e = s.size();
    while (b < e && iswspace(s[b])) ++b;
    while (e > b && iswspace(s[e - 1])) --e;
    return s.substr(b, e - b);
}

bool Ini::load(const std::wstring& path)
{
    sections_.clear();
    HANDLE f = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr,
                           OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (f == INVALID_HANDLE_VALUE) return false;
    LARGE_INTEGER size{};
    GetFileSizeEx(f, &size);
    if (size.QuadPart > (4 << 20)) {
        CloseHandle(f);
        return false;
    }
    std::string bytes(static_cast<size_t>(size.QuadPart), '\0');
    DWORD got = 0;
    const BOOL ok = bytes.empty() || ReadFile(f, bytes.data(), static_cast<DWORD>(bytes.size()), &got, nullptr);
    CloseHandle(f);
    if (!ok) return false;
    bytes.resize(got);

    std::wstring text;
    if (bytes.size() >= 2 && static_cast<unsigned char>(bytes[0]) == 0xFF && static_cast<unsigned char>(bytes[1]) == 0xFE) {
        text.assign(reinterpret_cast<const wchar_t*>(bytes.data() + 2), (bytes.size() - 2) / 2);
    } else {
        size_t start = 0;
        if (bytes.size() >= 3 && static_cast<unsigned char>(bytes[0]) == 0xEF &&
            static_cast<unsigned char>(bytes[1]) == 0xBB && static_cast<unsigned char>(bytes[2]) == 0xBF) {
            start = 3;
        }
        text = utf8_to_wide(bytes.substr(start));
    }

    Section* current = nullptr;
    size_t pos = 0;
    while (pos <= text.size()) {
        size_t eol = text.find(L'\n', pos);
        if (eol == std::wstring::npos) eol = text.size();
        std::wstring line = trim(text.substr(pos, eol - pos));
        pos = eol + 1;
        if (line.empty() || line[0] == L';' || line[0] == L'#') continue;
        if (line[0] == L'[') {
            const size_t close = line.find(L']');
            const std::wstring name = trim(line.substr(1, close == std::wstring::npos ? std::wstring::npos : close - 1));
            current = find(name);
            if (!current) {
                sections_.emplace_back(name, Section{});
                current = &sections_.back().second;
            }
            continue;
        }
        const size_t eq = line.find(L'=');
        if (eq == std::wstring::npos || !current) continue;
        std::wstring value = trim(line.substr(eq + 1));
        // A trailing " ; comment" is dropped; a value may not contain " ;".
        const size_t comment = value.find(L" ;");
        if (comment != std::wstring::npos) value = trim(value.substr(0, comment));
        (*current)[trim(line.substr(0, eq))] = value;
    }
    return true;
}

bool Ini::save(const std::wstring& path, const std::string& header_comment) const
{
    std::string out;
    if (!header_comment.empty()) out += header_comment;
    for (const auto& [name, sec] : sections_) {
        out += "[" + wide_to_utf8(name) + "]\r\n";
        for (const auto& [k, v] : sec) out += wide_to_utf8(k) + "=" + wide_to_utf8(v) + "\r\n";
        out += "\r\n";
    }
    // Written to a temporary file and moved into place, so a reader never
    // sees half a file.
    const std::wstring tmp = path + L".tmp";
    HANDLE f = CreateFileW(tmp.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (f == INVALID_HANDLE_VALUE) return false;
    DWORD written = 0;
    const BOOL ok = WriteFile(f, out.data(), static_cast<DWORD>(out.size()), &written, nullptr);
    CloseHandle(f);
    if (!ok || written != out.size()) {
        DeleteFileW(tmp.c_str());
        return false;
    }
    return MoveFileExW(tmp.c_str(), path.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != 0;
}

Ini::Section* Ini::find(const std::wstring& name)
{
    for (auto& s : sections_) {
        if (_wcsicmp(s.first.c_str(), name.c_str()) == 0) return &s.second;
    }
    return nullptr;
}

const Ini::Section* Ini::find(const std::wstring& name) const
{
    for (const auto& s : sections_) {
        if (_wcsicmp(s.first.c_str(), name.c_str()) == 0) return &s.second;
    }
    return nullptr;
}

bool Ini::has(const std::wstring& section) const
{
    return find(section) != nullptr;
}

const Ini::Section* Ini::section(const std::wstring& name) const
{
    return find(name);
}

std::wstring Ini::get(const std::wstring& section, const std::wstring& key, const std::wstring& def) const
{
    const Section* s = find(section);
    if (!s) return def;
    const auto it = s->find(key);
    return it == s->end() ? def : it->second;
}

int Ini::get_int(const std::wstring& section, const std::wstring& key, int def) const
{
    const std::wstring v = get(section, key);
    if (v.empty()) return def;
    wchar_t* end = nullptr;
    const long n = wcstol(v.c_str(), &end, 0);
    return end == v.c_str() ? def : static_cast<int>(n);
}

bool Ini::get_bool(const std::wstring& section, const std::wstring& key, bool def) const
{
    const std::wstring v = get(section, key);
    if (v.empty()) return def;
    if (_wcsicmp(v.c_str(), L"yes") == 0 || _wcsicmp(v.c_str(), L"true") == 0 || _wcsicmp(v.c_str(), L"on") == 0) {
        return true;
    }
    if (_wcsicmp(v.c_str(), L"no") == 0 || _wcsicmp(v.c_str(), L"false") == 0 || _wcsicmp(v.c_str(), L"off") == 0) {
        return false;
    }
    return get_int(section, key, def ? 1 : 0) != 0;
}

void Ini::set(const std::wstring& section, const std::wstring& key, const std::wstring& value)
{
    Section* s = find(section);
    if (!s) {
        sections_.emplace_back(section, Section{});
        s = &sections_.back().second;
    }
    (*s)[key] = value;
}

void Ini::set_int(const std::wstring& section, const std::wstring& key, int value)
{
    set(section, key, std::to_wstring(value));
}

void Ini::remove_section(const std::wstring& section)
{
    for (auto it = sections_.begin(); it != sections_.end(); ++it) {
        if (_wcsicmp(it->first.c_str(), section.c_str()) == 0) {
            sections_.erase(it);
            return;
        }
    }
}

std::vector<std::wstring> Ini::sections() const
{
    std::vector<std::wstring> out;
    for (const auto& s : sections_) out.push_back(s.first);
    return out;
}

} // namespace evv
