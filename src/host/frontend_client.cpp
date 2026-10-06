#include "host/frontend_client.h"

#include <algorithm>
#include <cstring>

#include "common/ini.h"
#include "common/log.h"

namespace evv {

namespace {

std::wstring quote(const std::wstring& s)
{
    return L"\"" + s + L"\"";
}

bool read_exact(HANDLE h, void* buf, DWORD n)
{
    auto* p = static_cast<uint8_t*>(buf);
    while (n) {
        DWORD got = 0;
        if (!ReadFile(h, p, n, &got, nullptr) || got == 0) return false;
        p += got;
        n -= got;
    }
    return true;
}

bool write_all(HANDLE h, const void* buf, DWORD n)
{
    const auto* p = static_cast<const uint8_t*>(buf);
    while (n) {
        DWORD w = 0;
        if (!WriteFile(h, p, n, &w, nullptr) || w == 0) return false;
        p += w;
        n -= w;
    }
    return true;
}

} // namespace

bool FrontendClient::start(const std::wstring& exe, const std::wstring& data, const std::wstring& voice,
                           const std::wstring& map, std::string& error)
{
    exe_ = exe;
    data_ = data;
    voice_ = voice;
    map_ = map;
    return spawn(error) && set_voice(error);
}

bool FrontendClient::spawn(std::string& error)
{
    stop();
    SECURITY_ATTRIBUTES sa{sizeof sa, nullptr, TRUE};
    HANDLE child_in = nullptr, child_out = nullptr;
    if (!CreatePipe(&child_in, &to_, &sa, 1 << 16)) {
        error = "CreatePipe failed";
        return false;
    }
    if (!CreatePipe(&from_, &child_out, &sa, 1 << 16)) {
        CloseHandle(child_in);
        error = "CreatePipe failed";
        return false;
    }
    SetHandleInformation(to_, HANDLE_FLAG_INHERIT, 0);
    SetHandleInformation(from_, HANDLE_FLAG_INHERIT, 0);

    SIZE_T attr_size = 0;
    InitializeProcThreadAttributeList(nullptr, 1, 0, &attr_size);
    std::vector<uint8_t> attr_buf(attr_size);
    auto* attrs = reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(attr_buf.data());
    HANDLE inherit[2] = {child_in, child_out};
    const bool have_list = InitializeProcThreadAttributeList(attrs, 1, 0, &attr_size) &&
                           UpdateProcThreadAttribute(attrs, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST, inherit,
                                                     sizeof inherit, nullptr, nullptr);
    STARTUPINFOEXW si{};
    si.StartupInfo.cb = sizeof si;
    si.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
    si.StartupInfo.hStdInput = child_in;
    si.StartupInfo.hStdOutput = child_out;
    si.StartupInfo.hStdError = nullptr;
    si.lpAttributeList = have_list ? attrs : nullptr;

    std::wstring cmd = quote(exe_) + L" --data " + quote(data_) + L" --serve";
    std::vector<wchar_t> cmdline(cmd.begin(), cmd.end());
    cmdline.push_back(L'\0');
    PROCESS_INFORMATION pi{};
    // The host is in its client's job, and so is this: it cannot outlive it.
    const BOOL ok = CreateProcessW(exe_.c_str(), cmdline.data(), nullptr, nullptr, TRUE,
                                   CREATE_NO_WINDOW | (have_list ? EXTENDED_STARTUPINFO_PRESENT : 0), nullptr,
                                   nullptr, &si.StartupInfo, &pi);
    const DWORD create_error = GetLastError();
    if (have_list) DeleteProcThreadAttributeList(attrs);
    CloseHandle(child_in);
    CloseHandle(child_out);
    if (!ok) {
        error = "cannot start the eSpeak NG front-end (error " + std::to_string(create_error) + ")";
        CloseHandle(to_);
        CloseHandle(from_);
        to_ = from_ = nullptr;
        return false;
    }
    CloseHandle(pi.hThread);
    process_ = pi.hProcess;
    reported_.clear();
    log::write(log::kStandard, "host: front-end %lu started for %S", pi.dwProcessId, voice_.c_str());
    return true;
}

bool FrontendClient::request(uint32_t type, const std::string& payload, EvvMsgHeader& reply,
                             std::vector<uint8_t>& body)
{
    if (!to_ || !from_) return false;
    EvvMsgHeader h{EVV_FE_MAGIC, type, static_cast<uint32_t>(payload.size())};
    if (!write_all(to_, &h, sizeof h) ||
        (!payload.empty() && !write_all(to_, payload.data(), static_cast<DWORD>(payload.size()))))
        return false;
    if (!read_exact(from_, &reply, sizeof reply) || reply.magic != EVV_FE_MAGIC || reply.size > EVV_FE_MAX_PAYLOAD)
        return false;
    body.resize(reply.size);
    return reply.size == 0 || read_exact(from_, body.data(), reply.size);
}

bool FrontendClient::set_voice(std::string& error)
{
    std::string payload = wide_to_utf8(voice_);
    payload.push_back('\0');
    payload += wide_to_utf8(map_);
    payload.push_back('\0');
    EvvMsgHeader reply{};
    std::vector<uint8_t> body;
    if (!request(EVV_FE_VOICE, payload, reply, body) || reply.type != EVV_FE_STATUS ||
        body.size() < sizeof(EvvStatus)) {
        error = "the eSpeak NG front-end did not answer";
        // It may have said why before it went: a status is the whole of a
        // start-up failure.
        if (reply.type == EVV_FE_STATUS && body.size() >= sizeof(EvvStatus)) {
            EvvStatus st;
            memcpy(&st, body.data(), sizeof st);
            st.error[sizeof st.error - 1] = 0;
            error = st.error;
        }
        stop();
        return false;
    }
    EvvStatus st;
    memcpy(&st, body.data(), sizeof st);
    st.error[sizeof st.error - 1] = 0;
    if (!st.ok) {
        error = std::string("eSpeak NG: ") + st.error;
        stop();
        return false;
    }
    return true;
}

bool FrontendClient::translate(const std::string& utf8, uint32_t flags, std::string& out,
                               std::vector<EvvAnchor>& anchors, std::string& error)
{
    out.clear();
    anchors.clear();
    std::string payload(sizeof(uint32_t), '\0');
    memcpy(payload.data(), &flags, sizeof flags);
    payload += utf8;
    payload.push_back('\0');
    for (int attempt = 0; attempt < 2; ++attempt) {
        if (!running() && !(spawn(error) && set_voice(error))) return false;
        EvvMsgHeader reply{};
        std::vector<uint8_t> body;
        if (!request(EVV_FE_TRANSLATE, payload, reply, body)) {
            log::write(log::kStandard, "host: the front-end stopped answering; starting it again");
            stop();
            continue;
        }
        if (reply.type == EVV_FE_STATUS && body.size() >= sizeof(EvvStatus)) {
            EvvStatus st;
            memcpy(&st, body.data(), sizeof st);
            st.error[sizeof st.error - 1] = 0;
            error = std::string("eSpeak NG: ") + st.error;
            return false;
        }
        if (reply.type != EVV_FE_RESULT || body.size() < sizeof(EvvResultHead)) {
            error = "the front-end answered something else";
            stop();
            continue;
        }
        EvvResultHead head;
        memcpy(&head, body.data(), sizeof head);
        const size_t anchor_bytes = static_cast<size_t>(head.n_anchors) * sizeof(EvvAnchor);
        if (sizeof head + anchor_bytes + head.text_len > body.size()) {
            error = "the front-end's answer was short";
            stop();
            continue;
        }
        anchors.resize(head.n_anchors);
        if (anchor_bytes) memcpy(anchors.data(), body.data() + sizeof head, anchor_bytes);
        out.assign(reinterpret_cast<const char*>(body.data() + sizeof head + anchor_bytes), head.text_len);
        const size_t used = sizeof head + anchor_bytes + head.text_len;
        log_diagnostics(body.data() + used, body.size() - used);
        return true;
    }
    if (error.empty()) error = "the eSpeak NG front-end failed twice";
    return false;
}

// What the front-end lost on the way to a result (common/frontend_proto.h),
// each kind and detail written to the log once while the front-end runs.
void FrontendClient::log_diagnostics(const uint8_t* p, size_t n)
{
    uint32_t head[2];
    if (n < sizeof head) return;
    memcpy(head, p, sizeof head);
    if (head[0] != EVV_FE_DIAG_MAGIC || head[1] > n - sizeof head) return;
    const std::string all(reinterpret_cast<const char*>(p + sizeof head), head[1]);
    size_t at = 0;
    while (at < all.size()) {
        size_t end = all.find('\n', at);
        if (end == std::string::npos) end = all.size();
        const std::string line = all.substr(at, end - at);
        at = end + 1;
        // the count is the last field; the rest says what it was
        const size_t tab = line.rfind('\t');
        const std::string what = tab == std::string::npos ? line : line.substr(0, tab);
        if (what.empty() || !reported_.insert(what).second) continue;
        log::write(log::kStandard, "host: front-end %S: %s", voice_.c_str(), line.c_str());
    }
}

void FrontendClient::stop()
{
    if (to_) {
        EvvMsgHeader h{EVV_FE_MAGIC, EVV_FE_QUIT, 0};
        write_all(to_, &h, sizeof h);
        CloseHandle(to_);
        to_ = nullptr;
    }
    if (from_) {
        CloseHandle(from_);
        from_ = nullptr;
    }
    if (process_) {
        if (WaitForSingleObject(process_, 500) != WAIT_OBJECT_0) TerminateProcess(process_, 1);
        CloseHandle(process_);
        process_ = nullptr;
    }
}

// ---- the user's dictionaries, as words -----------------------------------------------

namespace {

std::wstring lower(std::wstring s)
{
    if (!s.empty()) CharLowerBuffW(s.data(), static_cast<DWORD>(s.size()));
    return s;
}

bool word_char(wchar_t c)
{
    return IsCharAlphaNumericW(c) || c == L'\'' || c == 0x2019;
}

std::wstring read_text_file(const std::wstring& path)
{
    HANDLE f = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0,
                           nullptr);
    if (f == INVALID_HANDLE_VALUE) return {};
    LARGE_INTEGER size{};
    GetFileSizeEx(f, &size);
    std::string bytes(static_cast<size_t>(size.QuadPart > (16 << 20) ? 0 : size.QuadPart), '\0');
    DWORD got = 0;
    if (!bytes.empty()) ReadFile(f, bytes.data(), static_cast<DWORD>(bytes.size()), &got, nullptr);
    CloseHandle(f);
    bytes.resize(got);
    if (bytes.size() >= 3 && static_cast<unsigned char>(bytes[0]) == 0xEF &&
        static_cast<unsigned char>(bytes[1]) == 0xBB && static_cast<unsigned char>(bytes[2]) == 0xBF)
        bytes.erase(0, 3);
    if (MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, bytes.data(), static_cast<int>(bytes.size()), nullptr,
                            0) > 0 ||
        bytes.empty())
        return utf8_to_wide(bytes);
    const int n = MultiByteToWideChar(CP_ACP, 0, bytes.data(), static_cast<int>(bytes.size()), nullptr, 0);
    std::wstring w(static_cast<size_t>(n > 0 ? n : 0), L'\0');
    if (n > 0) MultiByteToWideChar(CP_ACP, 0, bytes.data(), static_cast<int>(bytes.size()), w.data(), n);
    return w;
}

void read_entries(const std::wstring& path, std::vector<std::pair<std::wstring, std::wstring>>& into)
{
    const std::wstring text = read_text_file(path);
    size_t pos = 0;
    while (pos < text.size()) {
        size_t end = text.find(L'\n', pos);
        if (end == std::wstring::npos) end = text.size();
        std::wstring line = text.substr(pos, end - pos);
        pos = end + 1;
        if (!line.empty() && line.back() == L'\r') line.pop_back();
        const size_t tab = line.find(L'\t');
        if (tab == std::wstring::npos || tab == 0) continue;
        std::wstring key = line.substr(0, tab);
        std::wstring value = line.substr(tab + 1);
        while (!key.empty() && key.back() == L'.') key.pop_back(); // an abbreviation's own full stop
        if (!key.empty()) into.emplace_back(lower(key), value);
    }
    // longest first, so that the longer of two overlapping entries wins
    std::stable_sort(into.begin(), into.end(),
                     [](const auto& a, const auto& b) { return a.first.size() > b.first.size(); });
}

} // namespace

void TextDictionary::set_files(const std::wstring files[3])
{
    bool same = true;
    for (int v = 0; v < 3; ++v) same = same && files[v] == files_[v];
    if (same) {
        reload_if_changed();
        return;
    }
    for (int v = 0; v < 3; ++v) {
        files_[v] = files[v];
        stamps_[v] = FILETIME{};
    }
    reload_if_changed();
}

void TextDictionary::reload_if_changed()
{
    FILETIME now[3] = {};
    bool changed = false;
    for (int v = 0; v < 3; ++v) {
        WIN32_FILE_ATTRIBUTE_DATA a{};
        if (!files_[v].empty() && GetFileAttributesExW(files_[v].c_str(), GetFileExInfoStandard, &a))
            now[v] = a.ftLastWriteTime;
        changed = changed || CompareFileTime(&now[v], &stamps_[v]) != 0;
    }
    if (!changed) return;
    whole_.clear();
    roots_.clear();
    for (int v = 0; v < 3; ++v) {
        stamps_[v] = now[v];
        if (files_[v].empty()) continue;
        read_entries(files_[v], v == 1 ? roots_ : whole_);
    }
    log::write(log::kStandard, "host: %zu words and %zu roots from the user dictionaries", whole_.size(),
               roots_.size());
}

std::string TextDictionary::apply(const std::string& utf8)
{
    if (empty()) return utf8;
    const std::wstring text = utf8_to_wide(utf8);
    const std::wstring low = lower(text);
    std::wstring out;
    out.reserve(text.size());
    size_t i = 0;
    while (i < text.size()) {
        if (!word_char(text[i])) {
            out.push_back(text[i++]);
            continue;
        }
        size_t j = i;
        while (j < text.size() && word_char(text[j])) ++j;
        const std::wstring word = low.substr(i, j - i);
        bool done = false;
        for (const auto& e : whole_) {
            if (e.first == word) {
                out += e.second;
                done = true;
                break;
            }
        }
        if (!done) {
            for (const auto& e : roots_) {
                if (word.size() > e.first.size() && word.compare(0, e.first.size(), e.first) == 0) {
                    out += e.second + text.substr(i + e.first.size(), j - i - e.first.size());
                    done = true;
                    break;
                }
            }
        }
        if (!done) out.append(text, i, j - i);
        i = j;
    }
    return wide_to_utf8(out);
}

} // namespace evv
