#include "community_update.h"

#include <windows.h>

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <vector>

#include "http.h"
#include "ini.h"
#include "log.h"
#include "paths.h"
#include "zip_reader.h"

namespace evv {

namespace {

constexpr size_t kMaxZip = 64u << 20;
constexpr uint32_t kMaxFile = 32u << 20;

struct Remote
{
    std::string commit;
    std::string date;
    std::string message;
    bool known = false;
};

bool is_hex40(const std::string& s)
{
    return s.size() == 40 && std::all_of(s.begin(), s.end(), [](unsigned char c) { return std::isxdigit(c) != 0; });
}

bool looks_like_iso_date(const std::string& s)
{
    // 2026-09-30T05:52:43Z
    if (s.size() != 20 || s[4] != '-' || s[7] != '-' || s[10] != 'T' || s[13] != ':' || s[16] != ':' || s[19] != 'Z') {
        return false;
    }
    for (size_t i : {0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18}) {
        if (!std::isdigit(static_cast<unsigned char>(s[i]))) return false;
    }
    return true;
}

std::string now_iso()
{
    SYSTEMTIME t;
    GetSystemTime(&t);
    char b[32];
    snprintf(b, sizeof b, "%04d-%02d-%02dT%02d:%02d:%02dZ", t.wYear, t.wMonth, t.wDay, t.wHour, t.wMinute, t.wSecond);
    return b;
}

// The string that follows `"key":` at or after `from`. GitHub's answer is JSON;
// three fields of it are all that is wanted, and they are plain strings.
bool json_string(const std::string& j, const char* key, size_t& from, std::string& value)
{
    const std::string needle = std::string("\"") + key + "\"";
    size_t at = j.find(needle, from);
    if (at == std::string::npos) return false;
    at += needle.size();
    while (at < j.size() && std::isspace(static_cast<unsigned char>(j[at]))) ++at;
    if (at >= j.size() || j[at] != ':') return false;
    ++at;
    while (at < j.size() && std::isspace(static_cast<unsigned char>(j[at]))) ++at;
    if (at >= j.size() || j[at] != '"') return false;
    ++at;
    value.clear();
    for (; at < j.size() && j[at] != '"'; ++at) {
        if (j[at] != '\\') {
            value.push_back(j[at]);
            continue;
        }
        if (++at >= j.size()) return false;
        switch (j[at]) {
        case 'n': value.push_back('\n'); break;
        case 't': value.push_back('\t'); break;
        case 'r': break;
        case 'u': at += 4; value.push_back('?'); break; // never in a hash or a date
        default: value.push_back(j[at]); break;
        }
    }
    if (at >= j.size()) return false;
    from = at + 1;
    return true;
}

// The newest commit of the branch: one small request.
Remote ask_github(std::string& why_not)
{
    Remote r;
    const std::wstring url = L"https://api.github.com/repos/" + utf8_to_wide(kCommunityRepository) +
                             L"/commits?per_page=1&sha=" + utf8_to_wide(kCommunityBranch);
    HttpResponse resp;
    if (!http_get(url, L"Accept: application/vnd.github+json\r\nX-GitHub-Api-Version: 2022-11-28\r\n", 1u << 20,
                  resp)) {
        why_not = resp.error;
        return r;
    }
    size_t at = 0;
    std::string sha;
    if (!json_string(resp.body, "sha", at, sha) || !is_hex40(sha)) {
        why_not = "GitHub's answer was not what was expected";
        return r;
    }
    // "commit":{"author":{...},"committer":{...,"date":"..."},"message":"..."}
    const size_t committer = resp.body.find("\"committer\"");
    std::string date, message;
    if (committer != std::string::npos) {
        size_t from = committer;
        json_string(resp.body, "date", from, date);
        json_string(resp.body, "message", from, message);
    }
    message = message.substr(0, message.find('\n'));
    r.commit = sha;
    r.date = looks_like_iso_date(date) ? date : std::string();
    r.message = message;
    r.known = true;
    return r;
}

// A file name that may be taken from the archive: one folder deep, plain
// characters, and something the English community dictionary is made of.
bool wanted_name(const std::string& path, std::string& name)
{
    const size_t slash = path.find('/');
    if (slash == std::string::npos || slash == 0 || slash + 1 >= path.size()) return false;
    name = path.substr(slash + 1);
    if (name.find('/') != std::string::npos || name[0] == '.') return false;
    for (unsigned char c : name) {
        if (!std::isalnum(c) && c != '.' && c != '_' && c != '-') return false;
    }
    std::string lower = name;
    std::transform(lower.begin(), lower.end(), lower.begin(), [](unsigned char c) { return std::tolower(c); });
    const bool dic = lower.size() > 4 && lower.compare(lower.size() - 4, 4, ".dic") == 0;
    // A dictionary file is taken only if it is for English: the repository holds German ones as well.
    return (dic && community_file_is_english(name)) || lower == "license.md" || lower == "readme.md";
}

bool is_dic(const std::string& name)
{
    return name.size() > 4 && _stricmp(name.c_str() + name.size() - 4, ".dic") == 0;
}

// A dictionary is a line an entry with a tab in it. Anything else that got
// this far under the name is not one.
bool looks_like_dictionary(const std::string& bytes)
{
    if (bytes.empty()) return false;
    size_t lines = 0, tabbed = 0;
    for (size_t at = 0; at < bytes.size() && lines < 200;) {
        size_t end = bytes.find('\n', at);
        if (end == std::string::npos) end = bytes.size();
        if (end > at) {
            ++lines;
            if (bytes.find('\t', at) < end) ++tabbed;
        }
        at = end + 1;
    }
    return tabbed > 0 && tabbed * 4 >= lines * 3;
}

bool write_file(const std::wstring& path, const std::string& bytes)
{
    HANDLE f = CreateFileW(path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (f == INVALID_HANDLE_VALUE) return false;
    DWORD wrote = 0;
    bool ok = bytes.empty() || WriteFile(f, bytes.data(), static_cast<DWORD>(bytes.size()), &wrote, nullptr);
    ok = ok && wrote == bytes.size() && FlushFileBuffers(f);
    CloseHandle(f);
    if (!ok) DeleteFileW(path.c_str());
    return ok;
}

bool read_file(const std::wstring& path, std::string& bytes, size_t max)
{
    HANDLE f = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
    if (f == INVALID_HANDLE_VALUE) return false;
    LARGE_INTEGER size{};
    bool ok = GetFileSizeEx(f, &size) && static_cast<uint64_t>(size.QuadPart) <= max;
    if (ok) {
        bytes.resize(static_cast<size_t>(size.QuadPart));
        DWORD got = 0;
        ok = bytes.empty() || (ReadFile(f, &bytes[0], static_cast<DWORD>(bytes.size()), &got, nullptr) && got == bytes.size());
    }
    CloseHandle(f);
    return ok;
}

// A file replaced whole: written beside the old one, then moved over it. An engine host reads a
// file for a moment when it notices a change, and Windows will not replace a file while it is
// open, so a refusal is tried again a few times before it is believed.
bool replace_file(const std::wstring& dir, const std::string& name, const std::string& bytes)
{
    const std::wstring final_path = dir + L"\\" + utf8_to_wide(name);
    const std::wstring temp = final_path + L".new";
    if (!write_file(temp, bytes)) return false;
    for (int attempt = 0; attempt < 20; ++attempt) {
        if (MoveFileExW(temp.c_str(), final_path.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) return true;
        Sleep(100);
    }
    DeleteFileW(temp.c_str());
    return false;
}

CommunityUpdate failure(const std::wstring& why, const CommunitySnapshot& in_use)
{
    CommunityUpdate u;
    u.outcome = CommunityOutcome::Failed;
    u.message = why + L" The community dictionary was left as it was.";
    u.in_use = in_use;
    return u;
}

std::wstring words_for(const std::string& commit, const std::string& date, const std::string& message)
{
    std::wstring w = L"commit " + utf8_to_wide(commit.substr(0, 7));
    const std::wstring d = community_date_words(date);
    if (!d.empty()) w += L" of " + d;
    if (!message.empty()) w += L" (“" + utf8_to_wide(message) + L"”)";
    return w;
}

} // namespace

bool community_zip_commit(const std::string& comment, std::string& commit)
{
    std::string c = comment;
    while (!c.empty() && std::isspace(static_cast<unsigned char>(c.back()))) c.pop_back();
    if (!is_hex40(c)) return false;
    std::transform(c.begin(), c.end(), c.begin(), [](unsigned char x) { return std::tolower(x); });
    commit = c;
    return true;
}

CommunityUpdate update_community_dictionary()
{
    const CommunitySnapshot in_use = community_snapshot();
    log::write(log::kStandard, "community dictionary: checking; in use %s (%s)",
               in_use.valid() ? (in_use.commit.empty() ? "an unnamed copy" : in_use.commit.c_str()) : "none",
               in_use.downloaded ? "downloaded" : "installed with OpenEVV");

    // ---- what is the newest, and where is it ---------------------------------
    std::string zip;
    Remote remote;
    wchar_t local[MAX_PATH];
    const DWORD n = GetEnvironmentVariableW(L"OPENEVV_COMMUNITY_ZIP", local, MAX_PATH);
    if (n > 0 && n < MAX_PATH) {
        if (!read_file(local, zip, kMaxZip)) return failure(L"The zip file " + std::wstring(local) + L" could not be read.", in_use);
    } else {
        std::string why;
        remote = ask_github(why);
        if (!remote.known) {
            log::write(log::kStandard, "community dictionary: GitHub's API did not answer (%s); going to the zip", why.c_str());
        } else if (in_use.valid() && in_use.commit == remote.commit) {
            CommunityUpdate u;
            u.outcome = CommunityOutcome::UpToDate;
            u.in_use = in_use;
            u.message = L"The community dictionary is already the newest: " +
                        words_for(in_use.commit, in_use.commit_date, in_use.message) + L".";
            log::write(log::kStandard, "community dictionary: already the newest");
            return u;
        }
        HttpResponse resp;
        const std::wstring url = L"https://codeload.github.com/" + utf8_to_wide(kCommunityRepository) +
                                 L"/zip/refs/heads/" + utf8_to_wide(kCommunityBranch);
        if (!http_get(url, L"", kMaxZip, resp)) {
            const std::string e = resp.error.empty() ? "no answer" : resp.error;
            log::write(log::kStandard, "community dictionary: download failed: %s", e.c_str());
            return failure(L"The newest community dictionary could not be downloaded: " + utf8_to_wide(e) + L".", in_use);
        }
        zip = std::move(resp.body);
    }

    // ---- read it, and check every file before anything is written -----------------
    ZipArchive archive;
    std::string error;
    if (!archive.open(zip, error)) {
        return failure(L"What was downloaded is not a usable zip file (" + utf8_to_wide(error) + L").", in_use);
    }
    std::string commit;
    if (!community_zip_commit(archive.comment(), commit)) {
        // Not one of GitHub's archives, or GitHub's answer is all there is to go by.
        commit = remote.known ? remote.commit : std::string();
    }
    if (!commit.empty() && in_use.valid() && in_use.commit == commit) {
        CommunityUpdate u;
        u.outcome = CommunityOutcome::UpToDate;
        u.in_use = in_use;
        u.message = L"The community dictionary is already the newest: " +
                    words_for(in_use.commit, in_use.commit_date, in_use.message) + L".";
        log::write(log::kStandard, "community dictionary: already the newest (by the zip)");
        return u;
    }

    struct File
    {
        std::string name, bytes;
    };
    std::vector<File> files;
    size_t dictionaries = 0;
    for (const ZipEntry& e : archive.entries()) {
        std::string name;
        if (e.is_directory() || !wanted_name(e.name, name)) continue;
        if (e.size > kMaxFile) return failure(utf8_to_wide(name) + L" is larger than a dictionary should be.", in_use);
        File f;
        f.name = name;
        if (!archive.read(e, f.bytes, error)) return failure(L"The download is damaged: " + utf8_to_wide(error) + L".", in_use);
        if (is_dic(name)) {
            if (!looks_like_dictionary(f.bytes)) {
                return failure(utf8_to_wide(name) + L" is not a pronunciation dictionary (no entries of a word, a tab and what to say).", in_use);
            }
            ++dictionaries;
        }
        files.push_back(std::move(f));
    }
    if (dictionaries == 0) return failure(L"The download holds no English dictionary files.", in_use);

    // ---- install ---------------------------------------------------------------------
    const std::wstring dir = community_downloaded_dir();
    if (dir.empty() || !ensure_dir(dir)) {
        return failure(L"The folder for the dictionary could not be made: " + dir + L".", in_use);
    }
    for (const File& f : files) {
        if (!replace_file(dir, f.name, f.bytes)) {
            return failure(L"A file could not be written to " + dir + L": " + utf8_to_wide(f.name) +
                               L". A program may be reading it, or the folder may not be writable for you.",
                           in_use);
        }
    }
    // A dictionary file the newest version no longer has must not go on being read.
    WIN32_FIND_DATAW fd;
    if (HANDLE h = FindFirstFileW((dir + L"\\*.dic").c_str(), &fd); h != INVALID_HANDLE_VALUE) {
        do {
            const std::string have = wide_to_utf8(fd.cFileName);
            const bool current = std::any_of(files.begin(), files.end(), [&](const File& f) {
                return _stricmp(f.name.c_str(), have.c_str()) == 0;
            });
            if (!current) DeleteFileW((dir + L"\\" + fd.cFileName).c_str());
        } while (FindNextFileW(h, &fd));
        FindClose(h);
    }
    // The record of what this is goes last: it is what makes the copy count as newer.
    const bool dated = remote.known && remote.commit == commit && !remote.date.empty();
    Ini ini;
    ini.set(L"Community", L"Source", L"https://github.com/" + utf8_to_wide(kCommunityRepository));
    ini.set(L"Community", L"Branch", utf8_to_wide(kCommunityBranch));
    ini.set(L"Community", L"Commit", utf8_to_wide(commit));
    ini.set(L"Community", L"CommitDate", utf8_to_wide(dated ? remote.date : now_iso()));
    if (remote.known && remote.commit == commit) ini.set(L"Community", L"Message", utf8_to_wide(remote.message));
    ini.set(L"Community", L"Downloaded", utf8_to_wide(now_iso()));
    if (!ini.save(dir + L"\\community-dictionary.ini",
                  "; Written by OpenEvvConfig.exe when it installed this copy of the community dictionary.\r\n\r\n")) {
        return failure(L"The record of the new version could not be written to " + dir + L".", in_use);
    }

    CommunityUpdate u;
    u.outcome = CommunityOutcome::Updated;
    u.in_use = community_snapshot();
    u.message = L"The community dictionary was updated to " +
                words_for(u.in_use.commit, u.in_use.commit_date, u.in_use.message) +
                L". Every OpenEVV voice uses it from its next utterance; nothing needs restarting.";
    log::write(log::kStandard, "community dictionary: updated to %s (%zu dictionary files)", u.in_use.commit.c_str(),
               dictionaries);
    return u;
}

} // namespace evv
