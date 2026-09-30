#include "community_dict.h"

#include <windows.h>

#include "ini.h"
#include "paths.h"

namespace evv {

namespace {

const wchar_t kIniName[] = L"community-dictionary.ini";

// IBM's language codes, by ECI language (eci.h). The community dictionary is for English and only
// English: a file for any other language is neither read nor installed, whatever the repository holds
// (it has German files too). ENG is British English, which the repository has no files for today;
// they would be used for it if it ever has.
const struct
{
    unsigned id;
    const wchar_t* code;
    const wchar_t* name;
} kCodes[] = {
    {0x00010000, L"ENU", L"US English"},
    {0x00010001, L"ENG", L"British English"},
};

// main, root, abbreviations: the volume numbers of eciLoadDict.
const wchar_t* const kSuffix[3] = {L"main", L"Root", L"abbr"};

bool holds_dictionary(const std::wstring& dir)
{
    WIN32_FIND_DATAW fd;
    HANDLE h = FindFirstFileW((dir + L"\\*.dic").c_str(), &fd);
    if (h == INVALID_HANDLE_VALUE) return false;
    FindClose(h);
    return true;
}

} // namespace

std::wstring community_shipped_dir()
{
    return install_root() + L"\\dictionaries\\community";
}

std::wstring community_downloaded_dir()
{
    const std::wstring d = data_dir();
    return d.empty() ? std::wstring() : d + L"\\community-dictionary";
}

CommunitySnapshot read_community_snapshot(const std::wstring& dir, bool downloaded)
{
    CommunitySnapshot s;
    if (dir.empty() || !holds_dictionary(dir)) return s;
    s.dir = dir;
    s.downloaded = downloaded;
    Ini ini;
    if (ini.load(dir + L"\\" + kIniName)) {
        s.commit = wide_to_utf8(ini.get(L"Community", L"Commit"));
        s.commit_date = wide_to_utf8(ini.get(L"Community", L"CommitDate"));
        s.message = wide_to_utf8(ini.get(L"Community", L"Message"));
    }
    return s;
}

CommunitySnapshot community_snapshot()
{
    const CommunitySnapshot shipped = read_community_snapshot(community_shipped_dir(), false);
    const CommunitySnapshot got = read_community_snapshot(community_downloaded_dir(), true);
    if (!got.valid()) return shipped;
    if (!shipped.valid()) return got;
    // ISO 8601 in UTC sorts as text. A copy that does not say when it is from
    // loses to one that does.
    return got.commit_date >= shipped.commit_date ? got : shipped;
}

const wchar_t* community_language_code(unsigned eci_language)
{
    for (const auto& c : kCodes) {
        if (c.id == eci_language) return c.code;
    }
    return nullptr;
}

std::wstring community_file(const CommunitySnapshot& snapshot, unsigned eci_language, int volume)
{
    const wchar_t* code = community_language_code(eci_language);
    if (!snapshot.valid() || !code || volume < 0 || volume > 2) return {};
    const std::wstring path = snapshot.dir + L"\\" + code + kSuffix[volume] + L".dic";
    return file_exists(path) ? path : std::wstring();
}

std::wstring community_describe(const CommunitySnapshot& s)
{
    if (!s.valid()) {
        return L"No community dictionary is installed. Press \"Check for a newer version and install it\" to download it.";
    }
    std::wstring t = L"In use: ";
    if (s.commit.empty()) {
        t += L"a copy that does not say which version it is";
    } else {
        t += L"commit " + utf8_to_wide(s.commit.substr(0, 7));
        const std::wstring d = community_date_words(s.commit_date);
        if (!d.empty()) t += L" of " + d;
        if (!s.message.empty()) t += L" (“" + utf8_to_wide(s.message) + L"”)";
    }
    t += s.downloaded ? L", downloaded by you." : L", installed with OpenEVV.";
    std::wstring langs;
    for (const auto& c : kCodes) {
        bool has = false;
        for (int v = 0; v < 3 && !has; ++v) has = !community_file(s, c.id, v).empty();
        if (has) langs += (langs.empty() ? L"" : L", ") + std::wstring(c.name) + L" (" + c.code + L")";
    }
    if (!langs.empty()) t += L"\r\nFor: " + langs + L".";
    t += L"\r\nFolder: " + s.dir;
    return t;
}

bool community_file_is_english(const std::string& file_name)
{
    for (const auto& c : kCodes) {
        const std::string code = wide_to_utf8(c.code);
        if (file_name.size() > code.size() && _strnicmp(file_name.c_str(), code.c_str(), code.size()) == 0) return true;
    }
    return false;
}

std::wstring community_date_words(const std::string& iso)
{
    static const wchar_t* const kMonths[12] = {L"January", L"February", L"March",     L"April",   L"May",      L"June",
                                               L"July",    L"August",   L"September", L"October", L"November", L"December"};
    if (iso.size() < 10 || iso[4] != '-' || iso[7] != '-') return {};
    const int year = atoi(iso.substr(0, 4).c_str());
    const int month = atoi(iso.substr(5, 2).c_str());
    const int day = atoi(iso.substr(8, 2).c_str());
    if (year < 2000 || month < 1 || month > 12 || day < 1 || day > 31) return {};
    return std::to_wstring(day) + L" " + kMonths[month - 1] + L" " + std::to_wstring(year);
}

} // namespace evv
