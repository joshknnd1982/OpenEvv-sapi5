#include "languages.h"

#include <windows.h>

#include <algorithm>

#include "ini.h"
#include "paths.h"

namespace evv {

const std::wstring& LanguageInfo::module_for_this_bitness() const
{
#if defined(_WIN64)
    return module64;
#else
    return module32;
#endif
}

bool LanguageInfo::usable() const
{
    // A 32-bit client can always fall back to a 64-bit host on 64-bit
    // Windows and vice versa, so either module will do.
    return !module32.empty() || !module64.empty();
}

PresetVoice default_preset(int number)
{
    static const struct
    {
        const wchar_t* name;
        const wchar_t* gender;
        const wchar_t* age;
    } kPresets[8] = {
        {L"Adult Male 1", L"Male", L"Adult"},      {L"Adult Female 1", L"Female", L"Adult"},
        {L"Child 1", L"Female", L"Child"},         {L"Adult Male 2", L"Male", L"Adult"},
        {L"Adult Male 3", L"Male", L"Adult"},      {L"Adult Female 2", L"Female", L"Adult"},
        {L"Elderly Female 1", L"Female", L"Senior"}, {L"Elderly Male 1", L"Male", L"Senior"},
    };
    PresetVoice v;
    v.number = number;
    if (number >= 1 && number <= 8) {
        v.name = kPresets[number - 1].name;
        v.gender = kPresets[number - 1].gender;
        v.age = kPresets[number - 1].age;
    }
    return v;
}

bool read_language_pack(const std::wstring& dir, LanguageInfo& out, std::wstring& problem)
{
    Ini ini;
    if (!ini.load(dir + L"\\language.ini")) {
        problem = dir + L": no readable language.ini";
        return false;
    }
    LanguageInfo li;
    li.dir = dir;
    const size_t slash = dir.find_last_of(L"\\/");
    const std::wstring folder = slash == std::wstring::npos ? dir : dir.substr(slash + 1);
    li.tag = ini.get(L"Language", L"Tag", folder);
    li.name = ini.get(L"Language", L"Name", li.tag);
    li.locale = ini.get(L"Language", L"Locale");
    li.lcid = ini.get(L"Language", L"LCID", L"409");
    li.id = static_cast<unsigned>(wcstoul(ini.get(L"Language", L"Id", L"0").c_str(), nullptr, 0));
    li.codepage = static_cast<unsigned>(ini.get_int(L"Language", L"Codepage", 1252));
    li.experimental = ini.get_bool(L"Language", L"Experimental", false);
    li.order = ini.get_int(L"Language", L"Order", 1000);
    if (li.id == 0) {
        problem = dir + L": language.ini gives no Id";
        return false;
    }
    for (const bool x64 : {false, true}) {
        const std::wstring file = ini.get(L"Language", x64 ? L"Module64" : L"Module32");
        if (file.empty()) continue;
        const std::wstring full = (file.find(L':') != std::wstring::npos || file.rfind(L"\\\\", 0) == 0)
                                      ? file
                                      : dir + L"\\" + file;
        if (file_exists(full)) (x64 ? li.module64 : li.module32) = full;
    }
    if (!li.usable()) {
        problem = dir + L": neither module named in language.ini is present";
        return false;
    }
    for (int n = 1; n <= 8; ++n) {
        PresetVoice v = default_preset(n);
        const std::wstring sec = L"Voice" + std::to_wstring(n);
        v.name = ini.get(sec, L"Name", v.name);
        v.gender = ini.get(sec, L"Gender", v.gender);
        v.age = ini.get(sec, L"Age", v.age);
        const std::wstring params = ini.get(sec, L"Params");
        if (!params.empty()) {
            size_t pos = 0;
            for (int i = 0; i < 8 && pos <= params.size(); ++i) {
                size_t comma = params.find(L',', pos);
                if (comma == std::wstring::npos) comma = params.size();
                v.params[i] = _wtoi(params.substr(pos, comma - pos).c_str());
                pos = comma + 1;
            }
        }
        li.voices.push_back(v);
    }
    out = std::move(li);
    return true;
}

std::vector<LanguageInfo> scan_languages(std::vector<std::wstring>* problems)
{
    std::vector<LanguageInfo> found;
    for (const std::wstring& root : language_dirs()) {
        WIN32_FIND_DATAW fd;
        HANDLE h = FindFirstFileW((root + L"\\*").c_str(), &fd);
        if (h == INVALID_HANDLE_VALUE) continue;
        do {
            if (!(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) || fd.cFileName[0] == L'.') continue;
            const std::wstring dir = root + L"\\" + fd.cFileName;
            if (!file_exists(dir + L"\\language.ini")) continue;
            LanguageInfo li;
            std::wstring problem;
            if (!read_language_pack(dir, li, problem)) {
                if (problems) problems->push_back(problem);
                continue;
            }
            const bool dup = std::any_of(found.begin(), found.end(), [&](const LanguageInfo& o) {
                return _wcsicmp(o.tag.c_str(), li.tag.c_str()) == 0;
            });
            if (dup) {
                if (problems) problems->push_back(dir + L": a pack with tag " + li.tag + L" was already read; skipped");
                continue;
            }
            found.push_back(std::move(li));
        } while (FindNextFileW(h, &fd));
        FindClose(h);
    }
    std::sort(found.begin(), found.end(), [](const LanguageInfo& a, const LanguageInfo& b) {
        if (a.order != b.order) return a.order < b.order;
        return _wcsicmp(a.name.c_str(), b.name.c_str()) < 0;
    });
    return found;
}

bool find_language(const std::wstring& tag, LanguageInfo& out)
{
    for (auto& li : scan_languages()) {
        if (_wcsicmp(li.tag.c_str(), tag.c_str()) == 0) {
            out = std::move(li);
            return true;
        }
    }
    return false;
}

} // namespace evv
