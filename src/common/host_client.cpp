#include "host_client.h"

#include <windows.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstring>
#include <thread>

#include "log.h"
#include "paths.h"

namespace evv {

namespace {

constexpr int kMaxHostsPerModule = 3;
constexpr DWORD kGraceMs = 30000;
constexpr DWORD kPipeBytes = 1 << 20;
constexpr int kFrameSamples = 1024;

double now_ms()
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return 1000.0 * static_cast<double>(c.QuadPart) / static_cast<double>(f.QuadPart);
}

bool os_is_64bit()
{
#if defined(_WIN64)
    return true;
#else
    BOOL wow = FALSE;
    IsWow64Process(GetCurrentProcess(), &wow);
    return wow != FALSE;
#endif
}

constexpr bool kSelf64 = sizeof(void*) == 8;

std::wstring host_exe_for(bool x64)
{
    if (x64 == kSelf64) return host_exe_path();
    std::wstring dir = self_dir();
    const size_t slash = dir.find_last_of(L"\\/");
    if (slash != std::wstring::npos) dir.resize(slash);
    return dir + (x64 ? L"\\x64" : L"\\x86") + L"\\OpenEvvHost.exe";
}

// Every host lives in this job, so none outlives its client: the job dies
// with the last handle to it, which is this process's. The job also keeps
// Windows Error Reporting from putting a dialog in front of a screen reader
// if a host faults.
HANDLE host_job()
{
    static HANDLE job = [] {
        HANDLE j = CreateJobObjectW(nullptr, nullptr);
        if (j) {
            JOBOBJECT_EXTENDED_LIMIT_INFORMATION li{};
            li.BasicLimitInformation.LimitFlags =
                JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION;
            SetInformationJobObject(j, JobObjectExtendedLimitInformation, &li, sizeof li);
        }
        return j;
    }();
    return job;
}

std::wstring quote(const std::wstring& s)
{
    std::wstring t = s;
    while (!t.empty() && t.back() == L'\\') t.pop_back(); // "C:\x\" would escape the quote
    return L"\"" + t + L"\"";
}

// This process's environment with the host's switches set.
std::vector<wchar_t> host_environment(const Settings& s)
{
    std::vector<std::pair<std::wstring, std::wstring>> ours = {
        {L"EVV_UPSAMPLE", s.resampler},
        {L"EVV_NOISE", s.noise_shaping ? L"shaped" : L"flat"},
        {L"EVV_HETERO", s.heteronyms ? L"on" : L"off"},
    };
    std::vector<wchar_t> block;
    wchar_t* env = GetEnvironmentStringsW();
    for (const wchar_t* p = env; p && *p; p += wcslen(p) + 1) {
        bool replaced = false;
        for (const auto& kv : ours) {
            const size_t n = kv.first.size();
            if (_wcsnicmp(p, kv.first.c_str(), n) == 0 && p[n] == L'=') replaced = true;
        }
        if (!replaced) block.insert(block.end(), p, p + wcslen(p) + 1);
    }
    if (env) FreeEnvironmentStringsW(env);
    for (const auto& kv : ours) {
        const std::wstring e = kv.first + L"=" + kv.second;
        block.insert(block.end(), e.c_str(), e.c_str() + e.size() + 1);
    }
    block.push_back(L'\0');
    return block;
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

} // namespace

// ---- one host process ---------------------------------------------------------

class HostProcess : public std::enable_shared_from_this<HostProcess>
{
public:
    enum class State
    {
        Starting,
        Idle,
        Busy,
        Dead,
    };

    std::wstring module;
    std::wstring key;       // module and language: one DLL may carry several languages
    std::wstring signature;
    bool x64 = false;
    State state = State::Starting;  // guarded by the pool's mutex
    std::shared_ptr<Utterance> current; // guarded by the pool's mutex
    std::string error;              // guarded by the pool's mutex
    HostInfo info;
    double started_at = 0;

    ~HostProcess()
    {
        close_handles();
    }

    static std::shared_ptr<HostProcess> spawn(const LanguageInfo& lang, bool use64, const Settings& s,
                                              std::string& err)
    {
        auto h = std::make_shared<HostProcess>();
        h->module = lang.module_for(use64);
        h->key = h->module + L"|" + std::to_wstring(lang.id);
        h->signature = s.host_signature();
        h->x64 = use64;
        h->info.module = h->module;
        h->info.x64 = use64;
        const std::wstring exe = host_exe_for(use64);
        if (!file_exists(exe)) {
            err = "the engine host is missing: " + wide_to_narrow(exe);
            return nullptr;
        }

        SECURITY_ATTRIBUTES sa{sizeof sa, nullptr, TRUE};
        HANDLE child_in = nullptr, child_out = nullptr;
        if (!CreatePipe(&child_in, &h->to_host_, &sa, kPipeBytes)) {
            err = "CreatePipe failed";
            return nullptr;
        }
        if (!CreatePipe(&h->from_host_, &child_out, &sa, kPipeBytes)) {
            CloseHandle(child_in);
            err = "CreatePipe failed";
            return nullptr;
        }
        SetHandleInformation(h->to_host_, HANDLE_FLAG_INHERIT, 0);
        SetHandleInformation(h->from_host_, HANDLE_FLAG_INHERIT, 0);

        // Only the two pipe ends are inherited, whatever else this process
        // (a screen reader, say) has marked inheritable.
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

        wchar_t cp[16];
        swprintf_s(cp, L"%u", lang.codepage);
        wchar_t id[16];
        swprintf_s(id, L"0x%x", lang.id);
        std::wstring cmd = quote(exe) + L" --module " + quote(h->module) + L" --lang " + id + L" --client " +
                           exe_stem() + L" --log " + std::to_wstring(s.log_level) + L" --codepage " + cp +
                           L" --frame " + std::to_wstring(kFrameSamples);
        const std::wstring user_dict = user_dictionary_dir(lang.tag);
        if (!user_dict.empty()) cmd += L" --dict-user " + quote(user_dict);
        cmd += L" --dict-pack " + quote(lang.dir + L"\\dict");
        std::vector<wchar_t> cmdline(cmd.begin(), cmd.end());
        cmdline.push_back(L'\0');
        std::vector<wchar_t> env = host_environment(s);

        PROCESS_INFORMATION pi{};
        const DWORD flags = CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT |
                            (have_list ? EXTENDED_STARTUPINFO_PRESENT : 0) | CREATE_SUSPENDED;
        const BOOL ok = CreateProcessW(exe.c_str(), cmdline.data(), nullptr, nullptr, TRUE, flags, env.data(),
                                       nullptr, &si.StartupInfo, &pi);
        const DWORD create_error = GetLastError();
        if (have_list) DeleteProcThreadAttributeList(attrs);
        CloseHandle(child_in);
        CloseHandle(child_out);
        if (!ok) {
            err = "cannot start the engine host (error " + std::to_string(create_error) + ")";
            return nullptr;
        }
        // Into the job before it runs a single instruction.
        if (HANDLE j = host_job()) AssignProcessToJobObject(j, pi.hProcess);
        ResumeThread(pi.hThread);
        CloseHandle(pi.hThread);
        h->process_ = pi.hProcess;
        h->pid_ = pi.dwProcessId;
        h->started_at = now_ms();
        h->reader_ = std::thread(&HostProcess::read_loop, h);
        log::write(log::kStandard, "pool: started %s host %lu for %S", use64 ? "64-bit" : "32-bit", pi.dwProcessId,
                   lang.tag.c_str());
        return h;
    }

    bool write(const std::vector<uint8_t>& payload, uint32_t type)
    {
        std::lock_guard<std::mutex> g(write_lock_);
        if (!to_host_) return false;
        proto::Header hd{type, static_cast<uint32_t>(payload.size())};
        DWORD w = 0;
        return WriteFile(to_host_, &hd, sizeof hd, &w, nullptr) &&
               (payload.empty() || WriteFile(to_host_, payload.data(), static_cast<DWORD>(payload.size()), &w, nullptr));
    }

    void send_cancel(uint32_t id)
    {
        proto::CancelReq c{id};
        std::vector<uint8_t> p(sizeof c);
        memcpy(p.data(), &c, sizeof c);
        write(p, proto::kCancel);
    }

    void kill()
    {
        if (process_) TerminateProcess(process_, 4);
    }

    // Ends the host and waits for its reader. Never called on the reader.
    void stop()
    {
        {
            std::lock_guard<std::mutex> g(write_lock_);
            if (to_host_) {
                CloseHandle(to_host_); // the host sees end of input and leaves
                to_host_ = nullptr;
            }
        }
        if (process_ && WaitForSingleObject(process_, 1500) != WAIT_OBJECT_0) {
            log::write(log::kStandard, "pool: host %lu did not leave; ending it", pid_);
            TerminateProcess(process_, 5);
            WaitForSingleObject(process_, 2000);
        }
        if (reader_.joinable()) {
            if (reader_.get_id() == std::this_thread::get_id()) {
                reader_.detach();
            } else {
                reader_.join();
            }
        }
    }

    DWORD pid() const { return pid_; }

private:
    HANDLE to_host_ = nullptr;
    HANDLE from_host_ = nullptr;
    HANDLE process_ = nullptr;
    DWORD pid_ = 0;
    std::thread reader_;
    std::mutex write_lock_;

    static std::string wide_to_narrow(const std::wstring& w)
    {
        std::string s;
        for (wchar_t c : w) s.push_back(c < 128 ? static_cast<char>(c) : '?');
        return s;
    }

    void close_handles()
    {
        if (to_host_) CloseHandle(to_host_);
        if (from_host_) CloseHandle(from_host_);
        if (process_) CloseHandle(process_);
        to_host_ = from_host_ = process_ = nullptr;
    }

    void read_loop()
    {
        auto self = shared_from_this();
        HostPool& pool = HostPool::get();
        std::vector<uint8_t> payload;
        for (;;) {
            proto::Header hd{};
            if (!read_exact(from_host_, &hd, sizeof hd) || hd.size > proto::kMaxPayload) break;
            payload.resize(hd.size);
            if (hd.size && !read_exact(from_host_, payload.data(), hd.size)) break;

            if (hd.type == proto::kReady && hd.size >= sizeof(proto::ReadyMsg)) {
                proto::ReadyMsg r;
                memcpy(&r, payload.data(), sizeof r);
                std::lock_guard<std::mutex> g(pool.m_);
                info.engine_version = r.engine_version;
                info.init_ms = r.init_ms;
                if (r.ok && r.version == proto::kVersion) {
                    state = State::Idle;
                    log::write(log::kStandard, "pool: host %lu ready in %.1f ms (engine %s, spawn to ready %.1f ms)",
                               pid_, r.init_ms, r.engine_version, now_ms() - started_at);
                } else {
                    state = State::Dead;
                    error = r.ok ? "the engine host is from a different version" : r.error;
                    log::write(log::kStandard, "pool: host %lu failed to start: %s", pid_, error.c_str());
                }
                pool.cv_.notify_all();
                continue;
            }

            std::shared_ptr<Utterance> u;
            {
                std::lock_guard<std::mutex> g(pool.m_);
                u = current;
            }
            if (hd.type == proto::kAudio && hd.size >= sizeof(proto::AudioMsg)) {
                proto::AudioMsg a;
                memcpy(&a, payload.data(), sizeof a);
                if (u && u->id_ == a.id) {
                    HostEvent ev;
                    ev.kind = HostEvent::kAudio;
                    const size_t n = (hd.size - sizeof a) / 2;
                    ev.samples.resize(n);
                    memcpy(ev.samples.data(), payload.data() + sizeof a, n * 2);
                    u->deliver(std::move(ev));
                }
            } else if (hd.type == proto::kIndex && hd.size >= sizeof(proto::IndexMsg)) {
                proto::IndexMsg im;
                memcpy(&im, payload.data(), sizeof im);
                if (u && u->id_ == im.id) {
                    HostEvent ev;
                    ev.kind = HostEvent::kIndex;
                    ev.index = im.value;
                    ev.sample = im.sample;
                    u->deliver(std::move(ev));
                }
            } else if (hd.type == proto::kDone && hd.size >= sizeof(proto::DoneMsg)) {
                HostEvent ev;
                ev.kind = HostEvent::kDone;
                memcpy(&ev.done, payload.data(), sizeof ev.done);
                {
                    std::lock_guard<std::mutex> g(pool.m_);
                    if (current && current->id_ == ev.done.id) {
                        current.reset();
                        if (state == State::Busy) state = State::Idle;
                    }
                    pool.cv_.notify_all();
                }
                if (u && u->id_ == ev.done.id) u->deliver(std::move(ev));
            }
        }

        // The host has gone: crashed, hung and killed, or told to leave.
        std::shared_ptr<Utterance> orphan;
        {
            std::lock_guard<std::mutex> g(pool.m_);
            if (state != State::Dead && error.empty()) error = "the engine host ended unexpectedly";
            const bool was_live = state == State::Busy || state == State::Idle || state == State::Starting;
            state = State::Dead;
            orphan = std::move(current);
            if (was_live) {
                DWORD code = 0;
                if (process_) GetExitCodeProcess(process_, &code);
                log::write(log::kStandard, "pool: host %lu ended (exit code %lu)", pid_, code);
            }
            pool.cv_.notify_all();
        }
        if (orphan) {
            HostEvent ev;
            ev.kind = HostEvent::kDone;
            ev.done.id = orphan->id_;
            ev.done.status = proto::kDoneFailed;
            strncpy_s(ev.done.error, "the engine host ended", _TRUNCATE);
            orphan->deliver(std::move(ev));
        }
    }
};

// ---- an utterance -------------------------------------------------------------

void Utterance::deliver(HostEvent&& ev)
{
    std::lock_guard<std::mutex> g(m_);
    if (done_) return;
    if (ev.kind == HostEvent::kDone) {
        done_ = true;
        q_.push_back(std::move(ev));
    } else if (!cancelled_) {
        q_.push_back(std::move(ev));
    }
    cv_.notify_all();
}

bool Utterance::next(HostEvent& ev, unsigned timeout_ms)
{
    std::unique_lock<std::mutex> g(m_);
    if (!cv_.wait_for(g, std::chrono::milliseconds(timeout_ms), [&] { return !q_.empty(); })) return false;
    ev = std::move(q_.front());
    q_.pop_front();
    return true;
}

bool Utterance::done() const
{
    std::lock_guard<std::mutex> g(m_);
    return done_;
}

void Utterance::cancel()
{
    {
        std::lock_guard<std::mutex> g(m_);
        if (done_ || cancelled_) return;
        cancelled_ = true;
        q_.clear();
    }
    if (auto h = host_.lock()) h->send_cancel(id_);
}

void Utterance::abandon()
{
    if (auto h = host_.lock()) {
        log::write(log::kStandard, "pool: host %lu stopped answering; replacing it", h->pid());
        h->kill();
    }
}

// ---- building a request ----------------------------------------------------------

RequestBuilder::RequestBuilder()
{
    head.sample_rate = 1;
    head.text_mode = 0;
    head.number_mode = 1;
    head.dictionary = 1;
    head.input_type = 0;
    head.user_dicts = 1;
    head.preset = 1;
    for (int& v : head.voice) v = -1;
}

void RequestBuilder::text(const std::string& bytes)
{
    if (bytes.empty()) return;
    proto::Item it{proto::kItemText, static_cast<int32_t>(bytes.size()), 0};
    const size_t at = items_.size();
    items_.resize(at + sizeof it + bytes.size());
    memcpy(items_.data() + at, &it, sizeof it);
    memcpy(items_.data() + at + sizeof it, bytes.data(), bytes.size());
    ++head.item_count;
}

void RequestBuilder::index(int32_t value)
{
    proto::Item it{proto::kItemIndex, value, 0};
    const size_t at = items_.size();
    items_.resize(at + sizeof it);
    memcpy(items_.data() + at, &it, sizeof it);
    ++head.item_count;
}

void RequestBuilder::voice(int which, int value)
{
    proto::Item it{proto::kItemVoice, which, value};
    const size_t at = items_.size();
    items_.resize(at + sizeof it);
    memcpy(items_.data() + at, &it, sizeof it);
    ++head.item_count;
}

void RequestBuilder::param(int which, int value)
{
    proto::Item it{proto::kItemParam, which, value};
    const size_t at = items_.size();
    items_.resize(at + sizeof it);
    memcpy(items_.data() + at, &it, sizeof it);
    ++head.item_count;
}

std::vector<uint8_t> RequestBuilder::finish(uint32_t id) const
{
    proto::SpeakReq h = head;
    h.id = id;
    std::vector<uint8_t> out(sizeof h + items_.size());
    memcpy(out.data(), &h, sizeof h);
    if (!items_.empty()) memcpy(out.data() + sizeof h, items_.data(), items_.size());
    return out;
}

// ---- the pool --------------------------------------------------------------------

HostPool& HostPool::get()
{
    // Never destroyed: at process exit the hosts die with the job, and a
    // static destructor here could run after the threads it would join.
    static HostPool* pool = new HostPool();
    return *pool;
}

void HostPool::add_user()
{
    std::lock_guard<std::mutex> g(m_);
    ++users_;
    if (grace_running_ && grace_event_) SetEvent(static_cast<HANDLE>(grace_event_));
}

void HostPool::release_user()
{
    std::lock_guard<std::mutex> g(m_);
    if (--users_ > 0) return;
    users_ = 0;
    if (grace_running_ || hosts_.empty()) return;
    if (!grace_event_) grace_event_ = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    ResetEvent(static_cast<HANDLE>(grace_event_));
    // The grace thread keeps the DLL loaded until it has finished.
    HMODULE pin = nullptr;
    if (module_) {
        GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, reinterpret_cast<LPCWSTR>(&HostPool::grace_entry),
                           &pin);
    }
    HANDLE t = CreateThread(nullptr, 0, &HostPool::grace_entry, pin, 0, nullptr);
    if (t) {
        grace_running_ = true;
        CloseHandle(t);
    } else if (pin) {
        FreeLibrary(pin);
    }
}

unsigned long __stdcall HostPool::grace_entry(void* pin)
{
    HostPool::get().grace_thread();
    if (pin) FreeLibraryAndExitThread(static_cast<HMODULE>(pin), 0);
    return 0;
}

void HostPool::grace_thread()
{
    const DWORD r = WaitForSingleObject(static_cast<HANDLE>(grace_event_), kGraceMs);
    bool stop = false;
    {
        std::lock_guard<std::mutex> g(m_);
        stop = r == WAIT_TIMEOUT && users_ == 0;
    }
    if (stop) {
        log::write(log::kStandard, "pool: no voice in use for %lu s; stopping the engine hosts", kGraceMs / 1000);
        shutdown_all();
    }
    std::lock_guard<std::mutex> g(m_);
    grace_running_ = false;
}

bool HostPool::busy() const
{
    std::lock_guard<std::mutex> g(m_);
    return !hosts_.empty() || grace_running_;
}

void HostPool::host_changed()
{
    cv_.notify_all();
}

void HostPool::shutdown_all()
{
    std::vector<std::shared_ptr<HostProcess>> all;
    {
        std::lock_guard<std::mutex> g(m_);
        all.swap(hosts_);
    }
    for (auto& h : all) h->stop();
}

namespace {

// Which module a client of this bitness uses for a language: its own
// bitness when the pack has it, else the other one if this Windows can run
// it and its host is installed.
bool choose_bitness(const LanguageInfo& lang, int want, bool& use64, std::string& error)
{
    if (want == 0 || want == 1) {
        use64 = want == 1;
        if (lang.module_for(use64).empty()) {
            error = use64 ? "the language pack has no 64-bit module" : "the language pack has no 32-bit module";
            return false;
        }
        if (use64 && !os_is_64bit()) {
            error = "64-bit modules need 64-bit Windows";
            return false;
        }
        if (!file_exists(host_exe_for(use64))) {
            error = use64 ? "the 64-bit engine host is not installed" : "the 32-bit engine host is not installed";
            return false;
        }
        return true;
    }
    const bool own = kSelf64;
    if (!lang.module_for(own).empty() && file_exists(host_exe_for(own))) {
        use64 = own;
        return true;
    }
    const bool other = !own;
    if (!lang.module_for(other).empty() && (!other || os_is_64bit()) && file_exists(host_exe_for(other))) {
        use64 = other;
        return true;
    }
    error = "the language pack has no module this system can run, or the engine host is missing";
    return false;
}

} // namespace

void HostPool::warm(const LanguageInfo& lang, const Settings& s, int bitness)
{
    bool use64 = false;
    std::string err;
    if (!choose_bitness(lang, bitness, use64, err)) return;
    const std::wstring key = lang.module_for(use64) + L"|" + std::to_wstring(lang.id);
    const std::wstring sig = s.host_signature();
    std::lock_guard<std::mutex> g(m_);
    for (const auto& h : hosts_) {
        if (h->state != HostProcess::State::Dead && h->key == key && h->signature == sig) return;
    }
    auto h = HostProcess::spawn(lang, use64, s, err);
    if (h) {
        hosts_.push_back(h);
    } else {
        log::write(log::kStandard, "pool: warm-up for %S failed: %s", lang.tag.c_str(), err.c_str());
    }
}

std::shared_ptr<Utterance> HostPool::speak(const LanguageInfo& lang, const Settings& s, const RequestBuilder& req,
                                           std::string& error, HostInfo* info, unsigned wait_ms, int bitness)
{
    bool use64 = false;
    if (!choose_bitness(lang, bitness, use64, error)) return nullptr;
    const std::wstring key = lang.module_for(use64) + L"|" + std::to_wstring(lang.id);
    const std::wstring sig = s.host_signature();

    auto u = std::make_shared<Utterance>();
    std::shared_ptr<HostProcess> host;
    std::vector<std::shared_ptr<HostProcess>> retired;
    int failed_starts = 0;
    {
        std::unique_lock<std::mutex> g(m_);
        const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(wait_ms);
        for (;;) {
            // Retire the dead, and idle hosts started under settings that
            // have since changed.
            for (auto it = hosts_.begin(); it != hosts_.end();) {
                HostProcess& h = **it;
                const bool stale = h.state == HostProcess::State::Idle && h.signature != sig;
                if (h.state == HostProcess::State::Dead || stale) {
                    if (h.state == HostProcess::State::Dead && h.key == key && !h.error.empty()) {
                        error = h.error;
                        if (h.info.engine_version.empty()) ++failed_starts; // died before READY
                    }
                    retired.push_back(*it);
                    it = hosts_.erase(it);
                } else {
                    ++it;
                }
            }
            if (failed_starts >= 2) {
                error = "the engine host could not start: " + error;
                break;
            }
            int matching = 0;
            bool starting = false;
            for (const auto& h : hosts_) {
                if (h->key != key || h->signature != sig) continue;
                ++matching;
                if (h->state == HostProcess::State::Idle && !host) host = h;
                if (h->state == HostProcess::State::Starting) starting = true;
            }
            if (host) break;
            if (!starting && matching < kMaxHostsPerModule) {
                std::string err;
                auto h = HostProcess::spawn(lang, use64, s, err);
                if (!h) {
                    error = err;
                    break;
                }
                hosts_.push_back(h);
            }
            if (cv_.wait_until(g, deadline) == std::cv_status::timeout) {
                // One last look before giving up.
                for (const auto& h : hosts_) {
                    if (h->key == key && h->signature == sig && h->state == HostProcess::State::Idle) {
                        host = h;
                        break;
                    }
                }
                if (!host && error.empty()) error = "no engine host became ready in time";
                break;
            }
        }
        if (host) {
            host->state = HostProcess::State::Busy;
            u->id_ = next_id_++;
            if (next_id_ >= 0xFFFFFF00u) next_id_ = 1;
            u->host_ = host;
            host->current = u;
            if (info) *info = host->info;
        }
    }
    for (auto& h : retired) h->stop();
    if (!host) {
        log::write(log::kStandard, "pool: cannot speak in %S: %s", lang.tag.c_str(), error.c_str());
        return nullptr;
    }
    if (!host->write(req.finish(u->id_), proto::kSpeak)) {
        // The host is gone; its reader will end the stream as failed.
        host->kill();
    }
    return u;
}

} // namespace evv
