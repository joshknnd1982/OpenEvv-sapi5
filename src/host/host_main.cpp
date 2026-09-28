// OpenEvvHost.exe: runs one OpenEVV language module for one client.
//
// Started by OpenEvvSAPI.dll (or the configuration utility, or a tool) with
// two pipes as standard input and output; see common/protocol.h. It loads the
// module named on its command line, makes one engine instance, warms it up,
// says READY, and then speaks one request at a time for as long as its client
// keeps the input pipe open.
//
// Why a process of its own: the engine backtracks through a landing place that
// restores the stack pointer itself, which a CET-enforcing process (64-bit
// PowerShell, Narrator, Edge...) turns into a fast-fail; and nothing a
// transcribed 1999 engine does wrong should be able to take a screen reader
// down. This executable is deliberately built without /CETCOMPAT.
//
// Latency: the engine synthesises some 600 times faster than real time and
// hands over its first samples a millisecond or so after it is asked, so the
// host forwards every buffer the moment the engine produces it. A cancel does
// not interrupt the engine -- nothing can, safely -- it stops forwarding, and
// what is left of the utterance is finished in a few milliseconds.
#include <windows.h>

#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <cstdio>
#include <cstring>
#include <deque>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "common/eci_module.h"
#include "common/ini.h"
#include "common/log.h"
#include "common/protocol.h"
#include "common/version.h"

using namespace evv;

namespace {

double now_ms()
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return 1000.0 * static_cast<double>(c.QuadPart) / static_cast<double>(f.QuadPart);
}

struct Args
{
    std::wstring module;
    unsigned language = 0;
    std::wstring client = L"client";
    int log_level = 1;
    std::wstring dict_user, dict_pack;
    unsigned codepage = 1252;
    int frame = 1024;
};

Args parse_args()
{
    Args a;
    int argc = 0;
    wchar_t** argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    for (int i = 1; argv && i + 1 < argc; i += 2) {
        const std::wstring k = argv[i], v = argv[i + 1];
        if (k == L"--module") a.module = v;
        else if (k == L"--lang") a.language = static_cast<unsigned>(wcstoul(v.c_str(), nullptr, 0));
        else if (k == L"--client") a.client = v;
        else if (k == L"--log") a.log_level = _wtoi(v.c_str());
        else if (k == L"--dict-user") a.dict_user = v;
        else if (k == L"--dict-pack") a.dict_pack = v;
        else if (k == L"--codepage") a.codepage = static_cast<unsigned>(_wtoi(v.c_str()));
        else if (k == L"--frame") a.frame = _wtoi(v.c_str());
    }
    LocalFree(argv);
    if (a.frame < 128 || a.frame > 16384) a.frame = 1024;
    return a;
}

// ---- output ------------------------------------------------------------

HANDLE g_out = INVALID_HANDLE_VALUE;
std::mutex g_out_lock;

[[noreturn]] void quit(int code)
{
    log::write(log::kStandard, "host: exiting (%d)", code);
    ExitProcess(static_cast<UINT>(code));
}

void send(uint32_t type, const void* a, uint32_t na, const void* b = nullptr, uint32_t nb = 0)
{
    proto::Header h{type, na + nb};
    std::lock_guard<std::mutex> g(g_out_lock);
    DWORD w = 0;
    // One WriteFile per piece; a pipe keeps them in order.
    if (!WriteFile(g_out, &h, sizeof h, &w, nullptr) || (na && !WriteFile(g_out, a, na, &w, nullptr)) ||
        (nb && !WriteFile(g_out, b, nb, &w, nullptr))) {
        // The client has gone. Nobody is left to speak to.
        quit(0);
    }
}

// ---- the engine --------------------------------------------------------

EciModule g_eci;
ECIHand g_h = nullptr;
std::vector<short> g_buffer;
Args g_args;

// The utterance in hand, as the callback sees it, and the last one the
// client cancelled. Discarding is "the one in hand is the one cancelled",
// never a flag: a late cancel for the previous utterance can then never
// silence the next one.
constexpr uint32_t kWarmId = 0xFFFFFFFFu;
std::atomic<uint32_t> g_current{0};
std::atomic<uint32_t> g_cancel_id{0xFFFFFFFEu};

bool discarding()
{
    return g_cancel_id.load(std::memory_order_acquire) == g_current.load(std::memory_order_acquire);
}
uint64_t g_delivered = 0;   // samples produced for the current utterance
double g_t_request = 0, g_first_audio = -1;

int EVV_ECICALL on_message(ECIHand, int msg, int param, void*)
{
    if (msg == kMsgWaveform) {
        if (param > 0 && !discarding()) {
            if (g_first_audio < 0) g_first_audio = now_ms() - g_t_request;
            proto::AudioMsg m{g_current.load()};
            send(proto::kAudio, &m, sizeof m, g_buffer.data(), static_cast<uint32_t>(param) * 2);
        }
        if (param > 0) g_delivered += static_cast<uint64_t>(param);
    } else if (msg == kMsgIndex) {
        if (!discarding()) {
            proto::IndexMsg m{g_current.load(), param, g_delivered};
            send(proto::kIndex, &m, sizeof m);
        }
    }
    // Always "processed": "not processed" makes the engine sleep 30 ms and
    // offer the same buffer again, which is what a full player means and not
    // what discarding means.
    return kDataProcessed;
}

// Engine calls are made through here so a fault inside the engine is caught
// and reported instead of silently killing the process. No C++ objects live
// in these frames, as __try requires.
struct SynthCall
{
    EciModule* m;
    ECIHand h;
};

int seh_filter(unsigned long code)
{
    return code == EXCEPTION_BREAKPOINT ? EXCEPTION_CONTINUE_SEARCH : EXCEPTION_EXECUTE_HANDLER;
}

bool guarded_synthesize(SynthCall* c, unsigned long* code)
{
    __try {
        c->m->Synthesize(c->h);
        c->m->Synchronize(c->h);
        return true;
    } __except (seh_filter(GetExceptionCode())) {
        *code = GetExceptionCode();
        return false;
    }
}

LONG WINAPI last_chance(EXCEPTION_POINTERS* ep)
{
    log::write(log::kStandard, "host: unhandled exception 0x%08lX at %p on thread %lu",
               ep->ExceptionRecord->ExceptionCode, ep->ExceptionRecord->ExceptionAddress, GetCurrentThreadId());
    // No Windows Error Reporting dialog: a modal box stealing focus from a
    // screen reader is worse than the crash. The client restarts us.
    TerminateProcess(GetCurrentProcess(), 3);
    return EXCEPTION_EXECUTE_HANDLER;
}

// ---- user dictionaries ---------------------------------------------------

struct DictState
{
    ECIDictHand dict = nullptr;
    FILETIME stamps[3] = {};
    std::wstring files[3];
    bool active = false;
};
DictState g_dict;
const wchar_t* const kDictFiles[3] = {L"main.dic", L"root.dic", L"abbr.dic"};

std::wstring dict_file(int volume)
{
    for (const std::wstring& dir : {g_args.dict_user, g_args.dict_pack}) {
        if (dir.empty()) continue;
        const std::wstring p = dir + L"\\" + kDictFiles[volume];
        const DWORD a = GetFileAttributesW(p.c_str());
        if (a != INVALID_FILE_ATTRIBUTES && !(a & FILE_ATTRIBUTE_DIRECTORY)) return p;
    }
    return {};
}

// A dictionary file may be UTF-8 (what Notepad writes) or already in the
// language's code set. The engine wants the latter, and a path it can open
// with a narrow string, so every volume is loaded from a converted copy.
bool stage_dictionary(const std::wstring& src, const std::wstring& dst)
{
    HANDLE f = CreateFileW(src.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0,
                           nullptr);
    if (f == INVALID_HANDLE_VALUE) return false;
    LARGE_INTEGER size{};
    GetFileSizeEx(f, &size);
    std::string bytes(static_cast<size_t>(size.QuadPart > (16 << 20) ? 0 : size.QuadPart), '\0');
    DWORD got = 0;
    if (!bytes.empty()) ReadFile(f, bytes.data(), static_cast<DWORD>(bytes.size()), &got, nullptr);
    CloseHandle(f);
    bytes.resize(got);
    std::string out = bytes;
    bool utf8 = false;
    if (bytes.size() >= 3 && static_cast<unsigned char>(bytes[0]) == 0xEF &&
        static_cast<unsigned char>(bytes[1]) == 0xBB && static_cast<unsigned char>(bytes[2]) == 0xBF) {
        bytes.erase(0, 3);
        utf8 = true;
    } else if (MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, bytes.data(), static_cast<int>(bytes.size()),
                                   nullptr, 0) > 0) {
        utf8 = std::any_of(bytes.begin(), bytes.end(), [](char c) { return (c & 0x80) != 0; });
    }
    if (utf8 && g_args.codepage != CP_UTF8) {
        const std::wstring w = utf8_to_wide(bytes);
        const int n = WideCharToMultiByte(g_args.codepage, 0, w.data(), static_cast<int>(w.size()), nullptr, 0, " ",
                                          nullptr);
        out.assign(static_cast<size_t>(n > 0 ? n : 0), '\0');
        if (n > 0)
            WideCharToMultiByte(g_args.codepage, 0, w.data(), static_cast<int>(w.size()), out.data(), n, " ", nullptr);
    } else if (utf8) {
        out = bytes;
    }
    // The engine reads a line an entry: normalise line ends to LF.
    std::string norm;
    norm.reserve(out.size());
    for (char c : out) {
        if (c != '\r') norm.push_back(c);
    }
    HANDLE o = CreateFileW(dst.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_TEMPORARY, nullptr);
    if (o == INVALID_HANDLE_VALUE) return false;
    DWORD w = 0;
    WriteFile(o, norm.data(), static_cast<DWORD>(norm.size()), &w, nullptr);
    CloseHandle(o);
    return true;
}

void refresh_dictionaries(bool wanted)
{
    if (!g_eci.NewDict || !g_eci.LoadDict || !g_eci.SetDict) return;
    if (!wanted) {
        if (g_dict.active) {
            g_eci.SetDict(g_h, nullptr);
            g_dict.active = false;
            log::write(log::kStandard, "host: user dictionaries off");
        }
        return;
    }
    std::wstring files[3];
    FILETIME stamps[3] = {};
    bool any = false;
    for (int v = 0; v < 3; ++v) {
        files[v] = dict_file(v);
        WIN32_FILE_ATTRIBUTE_DATA a{};
        if (!files[v].empty() && GetFileAttributesExW(files[v].c_str(), GetFileExInfoStandard, &a)) {
            stamps[v] = a.ftLastWriteTime;
            any = true;
        }
    }
    bool same = g_dict.dict != nullptr;
    for (int v = 0; v < 3 && same; ++v) {
        same = files[v] == g_dict.files[v] && CompareFileTime(&stamps[v], &g_dict.stamps[v]) == 0;
    }
    if (same) {
        if (!g_dict.active && any) {
            g_eci.SetDict(g_h, g_dict.dict);
            g_dict.active = true;
        }
        return;
    }
    if (g_dict.dict) {
        g_eci.SetDict(g_h, nullptr);
        if (g_eci.DeleteDict) g_eci.DeleteDict(g_h, g_dict.dict);
        g_dict = DictState{};
    }
    for (int v = 0; v < 3; ++v) {
        g_dict.files[v] = files[v];
        g_dict.stamps[v] = stamps[v];
    }
    if (!any) return;
    g_dict.dict = g_eci.NewDict(g_h);
    if (!g_dict.dict) {
        log::write(log::kStandard, "host: eciNewDict refused");
        return;
    }
    wchar_t tmp[MAX_PATH];
    GetTempPathW(MAX_PATH, tmp);
    for (int v = 0; v < 3; ++v) {
        if (files[v].empty()) continue;
        wchar_t staged[MAX_PATH];
        swprintf_s(staged, L"%sopenevv-%lu-%d.dic", tmp, GetCurrentProcessId(), v);
        char narrow[MAX_PATH * 2] = {};
        wchar_t shortp[MAX_PATH] = {};
        if (!stage_dictionary(files[v], staged)) continue;
        // A narrow path the engine can open whatever the user's name is.
        if (!GetShortPathNameW(staged, shortp, MAX_PATH)) wcscpy_s(shortp, staged);
        WideCharToMultiByte(CP_ACP, 0, shortp, -1, narrow, sizeof narrow, nullptr, nullptr);
        const int rc = g_eci.LoadDict(g_h, g_dict.dict, v, narrow);
        DeleteFileW(staged);
        log::write(log::kStandard, "host: loaded %S as volume %d: %s", files[v].c_str(), v,
                   rc == 0 ? "ok" : ("error " + std::to_string(rc)).c_str());
    }
    g_eci.SetDict(g_h, g_dict.dict);
    g_dict.active = true;
}

// ---- requests --------------------------------------------------------------

struct Request
{
    proto::SpeakReq req{};
    std::vector<uint8_t> items;
};

std::mutex g_q_lock;
std::condition_variable g_q_cv;
std::deque<Request> g_queue;
bool g_quit = false;

int g_rate = -1, g_text_mode = -1, g_number_mode = -1, g_dictionary = -1, g_input_type = -1;

void set_param_cached(int which, int value, int& cache)
{
    if (value < 0 || value == cache) return;
    if (g_eci.SetParam(g_h, which, value) >= 0) cache = value;
}

void send_done(uint32_t id, int status, const char* error)
{
    proto::DoneMsg d{};
    d.id = id;
    d.status = status;
    d.samples = g_delivered;
    d.sample_rate_hz = 0;
    d.first_audio_ms = g_first_audio;
    d.total_ms = now_ms() - g_t_request;
    if (error) strncpy_s(d.error, error, _TRUNCATE);
    send(proto::kDone, &d, sizeof d);
}

void run(Request& r)
{
    const proto::SpeakReq& q = r.req;
    g_t_request = now_ms();
    g_first_audio = -1;
    g_delivered = 0;
    g_current.store(q.id, std::memory_order_release);

    set_param_cached(kParamSampleRate, q.sample_rate, g_rate);
    set_param_cached(kParamTextMode, q.text_mode, g_text_mode);
    set_param_cached(kParamNumberMode, q.number_mode, g_number_mode);
    // eciDictionary is inverted: one turns the dictionary off.
    set_param_cached(kParamDictionary, q.dictionary ? 0 : 1, g_dictionary);
    set_param_cached(kParamInputType, q.input_type, g_input_type);
    refresh_dictionaries(q.user_dicts != 0);

    if (q.preset >= 1 && q.preset <= 8) g_eci.CopyVoice(g_h, q.preset, 0);
    for (int i = 0; i < kVoiceParamCount; ++i) {
        if (q.voice[i] >= 0) g_eci.SetVoiceParam(g_h, 0, i, q.voice[i]);
    }

    // Items: text, marks and prosody changes, in order. Synth mode 1 queues
    // each stretch with the voice in force when it was added.
    size_t pos = 0;
    std::string text;
    const bool full = log::enabled(log::kFull);
    std::string preview;
    for (uint32_t i = 0; i < q.item_count && pos + sizeof(proto::Item) <= r.items.size(); ++i) {
        proto::Item it;
        memcpy(&it, r.items.data() + pos, sizeof it);
        pos += sizeof it;
        switch (it.kind) {
        case proto::kItemText:
            if (it.a <= 0 || pos + static_cast<size_t>(it.a) > r.items.size()) break;
            text.assign(reinterpret_cast<const char*>(r.items.data() + pos), static_cast<size_t>(it.a));
            pos += static_cast<size_t>(it.a);
            g_eci.AddText(g_h, text.c_str());
            if (full && preview.size() < 400) preview += text;
            break;
        case proto::kItemIndex:
            g_eci.InsertIndex(g_h, it.a);
            break;
        case proto::kItemVoice:
            if (it.a >= 0 && it.a < kVoiceParamCount) g_eci.SetVoiceParam(g_h, 0, it.a, it.b);
            break;
        case proto::kItemParam:
            if (it.a == kParamTextMode) set_param_cached(kParamTextMode, it.b, g_text_mode);
            else if (it.a == kParamInputType) set_param_cached(kParamInputType, it.b, g_input_type);
            else g_eci.SetParam(g_h, it.a, it.b);
            break;
        default:
            break;
        }
    }

    SynthCall call{&g_eci, g_h};
    unsigned long code = 0;
    const bool ok = guarded_synthesize(&call, &code);
    const bool cancelled = discarding();
    if (!ok) {
        char b[96];
        snprintf(b, sizeof b, "engine fault 0x%08lX", code);
        log::write(log::kStandard, "host: request %u: %s; restarting", q.id, b);
        send_done(q.id, proto::kDoneFailed, b);
        // The engine's state cannot be trusted after a fault: end this host
        // and let the client start a fresh one.
        quit(3);
    }
    send_done(q.id, cancelled ? proto::kDoneCancelled : proto::kDoneOk, nullptr);
    log::write(log::kStandard, "host: #%u %s: %llu samples, first audio %.2f ms, done in %.2f ms", q.id,
               cancelled ? "cancelled" : "spoken", static_cast<unsigned long long>(g_delivered), g_first_audio,
               now_ms() - g_t_request);
    if (full) log::write(log::kFull, "host: #%u text \"%s\"", q.id, preview.c_str());
}

// ---- input -------------------------------------------------------------------

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

void reader(HANDLE in)
{
    std::vector<uint8_t> payload;
    for (;;) {
        proto::Header h{};
        if (!read_exact(in, &h, sizeof h) || h.size > proto::kMaxPayload) break;
        payload.resize(h.size);
        if (h.size && !read_exact(in, payload.data(), h.size)) break;
        if (h.type == proto::kSpeak && h.size >= sizeof(proto::SpeakReq)) {
            Request r;
            memcpy(&r.req, payload.data(), sizeof r.req);
            r.items.assign(payload.begin() + sizeof r.req, payload.end());
            std::lock_guard<std::mutex> g(g_q_lock);
            g_queue.push_back(std::move(r));
            g_q_cv.notify_one();
        } else if (h.type == proto::kCancel && h.size >= sizeof(proto::CancelReq)) {
            proto::CancelReq c;
            memcpy(&c, payload.data(), sizeof c);
            g_cancel_id.store(c.id, std::memory_order_release);
            std::lock_guard<std::mutex> g(g_q_lock);
            for (auto it = g_queue.begin(); it != g_queue.end(); ++it) {
                if (it->req.id == c.id) {
                    // Never started: answer it at once.
                    proto::DoneMsg d{};
                    d.id = c.id;
                    d.status = proto::kDoneCancelled;
                    send(proto::kDone, &d, sizeof d);
                    g_queue.erase(it);
                    break;
                }
            }
        } else if (h.type == proto::kQuit) {
            break;
        }
    }
    // Input closed: the client is finished with us (or has died).
    std::lock_guard<std::mutex> g(g_q_lock);
    g_quit = true;
    g_q_cv.notify_one();
}

bool start_engine(proto::ReadyMsg& ready)
{
    std::string err;
    if (!g_eci.load(g_args.module, err)) {
        snprintf(ready.error, sizeof ready.error, "cannot load the language module: %s", err.c_str());
        return false;
    }
    g_h = g_args.language ? g_eci.NewEx(static_cast<int>(g_args.language)) : g_eci.New();
    if (!g_h && g_args.language) g_h = g_eci.New();
    if (!g_h) {
        snprintf(ready.error, sizeof ready.error, "the module would not make an engine instance for 0x%x",
                 g_args.language);
        return false;
    }
    g_buffer.assign(static_cast<size_t>(g_args.frame), 0);
    g_eci.RegisterCallback(g_h, on_message, nullptr);
    if (!g_eci.SetOutputBuffer(g_h, g_args.frame, g_buffer.data())) {
        snprintf(ready.error, sizeof ready.error, "the engine refused a sample buffer");
        return false;
    }
    g_eci.SetParam(g_h, kParamSynthMode, 1);
    g_eci.SetParam(g_h, kParamInputType, 0);
    g_input_type = 0;
    g_rate = g_eci.GetParam(g_h, kParamSampleRate);
    ready.language = static_cast<uint32_t>(g_eci.GetParam(g_h, kParamLanguageDialect));
    char ver[64] = {};
    g_eci.Version(ver);
    strncpy_s(ready.engine_version, ver, _TRUNCATE);
    for (int v = 1; v <= 8; ++v) {
        char name[64] = {};
        g_eci.GetVoiceName(g_h, v, name);
        strncpy_s(ready.voice_names[v - 1], name, _TRUNCATE);
        for (int p = 0; p < kVoiceParamCount; ++p) ready.voice_params[v - 1][p] = g_eci.GetVoiceParam(g_h, v, p);
    }
    // Warm up: the first utterance an instance speaks pays for touching its
    // memory. Pay it now, into nothing, rather than on the user's first word.
    g_current = kWarmId;
    g_cancel_id = kWarmId;
    g_eci.AddText(g_h, "Ready. 1 2 3.");
    SynthCall call{&g_eci, g_h};
    unsigned long code = 0;
    if (!guarded_synthesize(&call, &code)) {
        snprintf(ready.error, sizeof ready.error, "engine fault 0x%08lX while warming up", code);
        return false;
    }
    g_current = 0;
    return true;
}

} // namespace

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int)
{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    SetUnhandledExceptionFilter(last_chance);
    const double t0 = now_ms();
    g_args = parse_args();
    log::init(
#if defined(_WIN64)
        L"host-x64",
#else
        L"host-x86",
#endif
        g_args.client);
    log::set_level(g_args.log_level);

    HANDLE in = GetStdHandle(STD_INPUT_HANDLE);
    g_out = GetStdHandle(STD_OUTPUT_HANDLE);
    if (in == INVALID_HANDLE_VALUE || !in || g_out == INVALID_HANDLE_VALUE || !g_out) {
        log::write(log::kStandard, "host: started without pipes; nothing to do");
        return 2;
    }
    // Speech is time-critical; the engine is idle almost all the time.
    SetPriorityClass(GetCurrentProcess(), ABOVE_NORMAL_PRIORITY_CLASS);

    proto::ReadyMsg ready{};
    ready.version = proto::kVersion;
    const bool ok = start_engine(ready);
    ready.ok = ok ? 1 : 0;
    ready.init_ms = now_ms() - t0;
    log::write(log::kStandard, "host: OpenEVV SAPI5 %s, engine %s, module %S, language 0x%x: %s in %.1f ms%s%s",
               EVV_VERSION_STRING, ready.engine_version, g_args.module.c_str(), ready.language,
               ok ? "ready" : "FAILED", ready.init_ms, ok ? "" : " - ", ok ? "" : ready.error);
    send(proto::kReady, &ready, sizeof ready);
    if (!ok) return 1;

    std::thread(reader, in).detach();
    for (;;) {
        Request r;
        {
            std::unique_lock<std::mutex> g(g_q_lock);
            g_q_cv.wait(g, [] { return g_quit || !g_queue.empty(); });
            if (g_queue.empty()) break;
            r = std::move(g_queue.front());
            g_queue.pop_front();
        }
        run(r);
    }
    log::write(log::kStandard, "host: client closed the pipe");
    // Leaving through ExitProcess rather than tearing the engine down: the
    // process is ending and the engine's own threads may still be parked.
    quit(0);
}
