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

#include "common/community_dict.h"
#include "common/eci_module.h"
#include "common/ini.h"
#include "common/log.h"
#include "common/pauses.h"
#include "common/protocol.h"
#include "common/version.h"
#include "host/frontend_client.h"

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
    // a pack read by eSpeak NG: the front-end and what it is to read with
    std::wstring frontend, fe_data, fe_voice, fe_map;
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
        else if (k == L"--frontend") a.frontend = v;
        else if (k == L"--fe-data") a.fe_data = v;
        else if (k == L"--fe-voice") a.fe_voice = v;
        else if (k == L"--fe-map") a.fe_map = v;
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
FrontendClient g_fe;
bool g_use_fe = false;
TextDictionary g_text_dict;
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

// ---- dictionaries ---------------------------------------------------------
//
// The engine's dictionary is three volumes (main, root, abbreviations), and each is read
// from layers, lowest first: the community dictionary, where there is a file of it for this
// language (community_dict.h), then the user's own file, or the language pack's where the
// user has none. An entry in a later layer replaces the same word in an earlier one, so the
// user's own always wins. The layers of a volume are joined into one file and loaded with one
// call.

struct DictLayer
{
    std::wstring path;
    FILETIME stamp{};
    // The community's files are in the language's own code set (Windows 1252 for English and
    // German), whatever bytes they happen to hold; a user's file may be UTF-8 (Notepad's).
    bool in_code_set = false;
    bool operator==(const DictLayer& o) const
    {
        return path == o.path && CompareFileTime(&stamp, &o.stamp) == 0;
    }
};

struct DictState
{
    ECIDictHand dict = nullptr;
    std::vector<DictLayer> layers[3];
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

DictLayer layer_of(const std::wstring& path, bool in_code_set)
{
    DictLayer l;
    l.path = path;
    l.in_code_set = in_code_set;
    WIN32_FILE_ATTRIBUTE_DATA a{};
    if (GetFileAttributesExW(path.c_str(), GetFileExInfoStandard, &a)) l.stamp = a.ftLastWriteTime;
    return l;
}

std::vector<DictLayer> dict_layers(int volume, bool user, bool community, const CommunitySnapshot& snapshot)
{
    std::vector<DictLayer> layers;
    if (community) {
        const std::wstring f = community_file(snapshot, g_args.language, volume);
        if (!f.empty()) layers.push_back(layer_of(f, true));
    }
    if (user) {
        const std::wstring f = dict_file(volume);
        if (!f.empty()) layers.push_back(layer_of(f, false));
    }
    return layers;
}

// One layer as the engine wants it: in the language's code set, a line an entry, LF line ends.
// A file that may be UTF-8 (what Notepad writes) is converted; the engine cannot read it as it is.
bool read_layer(const DictLayer& layer, std::string& out)
{
    HANDLE f = CreateFileW(layer.path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr,
                           OPEN_EXISTING, 0, nullptr);
    if (f == INVALID_HANDLE_VALUE) return false;
    LARGE_INTEGER size{};
    GetFileSizeEx(f, &size);
    std::string bytes(static_cast<size_t>(size.QuadPart > (16 << 20) ? 0 : size.QuadPart), '\0');
    DWORD got = 0;
    if (!bytes.empty()) ReadFile(f, bytes.data(), static_cast<DWORD>(bytes.size()), &got, nullptr);
    CloseHandle(f);
    bytes.resize(got);
    std::string converted = bytes;
    if (!layer.in_code_set) {
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
            const int n = WideCharToMultiByte(g_args.codepage, 0, w.data(), static_cast<int>(w.size()), nullptr, 0,
                                              " ", nullptr);
            converted.assign(static_cast<size_t>(n > 0 ? n : 0), '\0');
            if (n > 0) {
                WideCharToMultiByte(g_args.codepage, 0, w.data(), static_cast<int>(w.size()), converted.data(), n, " ",
                                    nullptr);
            }
        } else if (utf8) {
            converted = bytes;
        }
    }
    out.clear();
    out.reserve(converted.size() + 1);
    for (char c : converted) {
        if (c != '\r') out.push_back(c);
    }
    if (!out.empty() && out.back() != '\n') out.push_back('\n'); // so the next layer starts a line
    return true;
}

// The layers of a volume, joined, in a file the engine can open.
bool stage_dictionary(const std::vector<DictLayer>& layers, const std::wstring& dst)
{
    std::string all;
    for (const DictLayer& l : layers) {
        std::string one;
        if (read_layer(l, one)) all += one;
    }
    if (all.empty()) return false;
    HANDLE o = CreateFileW(dst.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_TEMPORARY, nullptr);
    if (o == INVALID_HANDLE_VALUE) return false;
    DWORD w = 0;
    WriteFile(o, all.data(), static_cast<DWORD>(all.size()), &w, nullptr);
    CloseHandle(o);
    return true;
}

std::string names_of(const std::vector<DictLayer>& layers)
{
    std::string s;
    for (const DictLayer& l : layers) {
        const size_t slash = l.path.find_last_of(L"\\/");
        if (!s.empty()) s += " + ";
        s += wide_to_utf8(slash == std::wstring::npos ? l.path : l.path.substr(slash + 1));
    }
    return s;
}

void refresh_dictionaries(bool user, bool community)
{
    if (!g_eci.NewDict || !g_eci.LoadDict || !g_eci.SetDict) return;
    if (!user && !community) {
        if (g_dict.active) {
            g_eci.SetDict(g_h, nullptr);
            g_dict.active = false;
            log::write(log::kStandard, "host: dictionaries off");
        }
        return;
    }
    const CommunitySnapshot snapshot = community ? community_snapshot() : CommunitySnapshot{};
    std::vector<DictLayer> layers[3];
    bool any = false;
    for (int v = 0; v < 3; ++v) {
        layers[v] = dict_layers(v, user, community, snapshot);
        any = any || !layers[v].empty();
    }
    bool same = g_dict.dict != nullptr;
    for (int v = 0; v < 3 && same; ++v) same = layers[v] == g_dict.layers[v];
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
    for (int v = 0; v < 3; ++v) g_dict.layers[v] = layers[v];
    if (!any) return;
    g_dict.dict = g_eci.NewDict(g_h);
    if (!g_dict.dict) {
        log::write(log::kStandard, "host: eciNewDict refused");
        return;
    }
    wchar_t tmp[MAX_PATH];
    GetTempPathW(MAX_PATH, tmp);
    for (int v = 0; v < 3; ++v) {
        if (layers[v].empty()) continue;
        const double t0 = now_ms();
        wchar_t staged[MAX_PATH];
        swprintf_s(staged, L"%sopenevv-%lu-%d.dic", tmp, GetCurrentProcessId(), v);
        char narrow[MAX_PATH * 2] = {};
        wchar_t shortp[MAX_PATH] = {};
        if (!stage_dictionary(layers[v], staged)) continue;
        // A narrow path the engine can open whatever the user's name is.
        if (!GetShortPathNameW(staged, shortp, MAX_PATH)) wcscpy_s(shortp, staged);
        WideCharToMultiByte(CP_ACP, 0, shortp, -1, narrow, sizeof narrow, nullptr, nullptr);
        const int rc = g_eci.LoadDict(g_h, g_dict.dict, v, narrow);
        DeleteFileW(staged);
        log::write(log::kStandard, "host: loaded %s as volume %d: %s (%.0f ms)", names_of(layers[v]).c_str(), v,
                   rc == 0 ? "ok" : ("error " + std::to_string(rc)).c_str(), now_ms() - t0);
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

// ---- a pack read by eSpeak NG ---------------------------------------------------
//
// The request's text goes to the front-end whole -- the stretches between
// marks are often single words, and eSpeak NG reads a number or an
// abbreviation by what is around it -- and comes back as the template's
// annotated text, with where each word began in what was sent. Marks, voice
// changes and parameters are put back in front of the first word at or after
// the place they stood.

size_t count_code_points(const std::string& utf8)
{
    size_t n = 0;
    for (unsigned char c : utf8) n += (c & 0xC0) != 0x80;
    return n;
}

struct Placed
{
    proto::Item item;
    uint32_t at; // code points of text before it
};

// The engine's spelling modes -- 1 letters and digits, 2 everything, 3 the
// radio alphabet -- are eSpeak NG's to do in these languages: a character on
// its own is read by its name in the language.
bool spelling_mode(int text_mode)
{
    return text_mode >= 1 && text_mode <= 3;
}

std::string spaced_out(const std::string& utf8)
{
    std::string out;
    out.reserve(utf8.size() * 2);
    for (size_t i = 0; i < utf8.size();) {
        size_t n = 1;
        const unsigned char c = static_cast<unsigned char>(utf8[i]);
        if (c >= 0xF0) n = 4;
        else if (c >= 0xE0) n = 3;
        else if (c >= 0xC0) n = 2;
        n = std::min(n, utf8.size() - i);
        out.append(utf8, i, n);
        if (!(n == 1 && (c == ' ' || c == '\t' || c == '\n' || c == '\r'))) out.push_back(' ');
        i += n;
    }
    return out;
}

// What is spelled is said by eSpeak NG character by character, each by its
// name in the language and an accented letter with its accent: "a con
// acento", "a fada". eSpeak NG is told by the command it keeps for that, the
// character with the number one, the number of the way of saying (18:
// characters) and Y; the same without a number ends it. Without it a letter
// on its own is read as the word it may also be, or as its sound.
const char kSayCharacters[] = "\001" "18Y";
const char kSayWords[] = "\001" "Y";

std::string spelled(const std::string& utf8)
{
    return kSayCharacters + spaced_out(utf8) + kSayWords;
}

// Whether the text is one letter and nothing else: somebody moving through a
// line a character at a time, or hearing what they type. A letter and the
// accent written after it as a character of its own are one letter where
// Unicode has the two as one.
bool lone_letter(const std::string& utf8)
{
    size_t first = 0, last = utf8.size();
    auto blank = [](char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\r'; };
    while (first < last && blank(utf8[first])) ++first;
    while (last > first && blank(utf8[last - 1])) --last;
    if (last == first || last - first > 32) return false;
    const std::wstring w = utf8_to_wide(utf8.substr(first, last - first));
    if (w.empty()) return false;
    wchar_t one[16];
    const int n = NormalizeString(NormalizationC, w.data(), static_cast<int>(w.size()), one, 16);
    if (n <= 0) return false;
    const bool pair = n == 2 && one[0] >= 0xD800 && one[0] < 0xDC00 && one[1] >= 0xDC00 && one[1] < 0xE000;
    if (n != 1 && !pair) return false;
    WORD kind[2] = {0, 0}, mark[2] = {0, 0};
    if (!GetStringTypeW(CT_CTYPE1, one, n, kind) || !GetStringTypeW(CT_CTYPE3, one, n, mark)) return false;
    if (kind[0] & C1_DIGIT) return false; // a number is read as a number
    return (kind[0] & C1_ALPHA) != 0 || (mark[0] & (C3_NONSPACING | C3_DIACRITIC | C3_VOWELMARK)) != 0;
}

std::string text_of(const Request& r)
{
    std::string all;
    size_t pos = 0;
    for (uint32_t i = 0; i < r.req.item_count && pos + sizeof(proto::Item) <= r.items.size(); ++i) {
        proto::Item it;
        memcpy(&it, r.items.data() + pos, sizeof it);
        pos += sizeof it;
        if (it.kind != proto::kItemText) continue;
        if (it.a <= 0 || pos + static_cast<size_t>(it.a) > r.items.size()) break;
        all.append(reinterpret_cast<const char*>(r.items.data() + pos), static_cast<size_t>(it.a));
        pos += static_cast<size_t>(it.a);
    }
    return all;
}

void apply_item(const proto::Item& it);

bool add_translated(const Request& r, std::string& preview, std::string& error)
{
    const proto::SpeakReq& q = r.req;
    std::string all;
    uint32_t at = 0;
    std::vector<Placed> placed;
    int text_mode = q.text_mode;
    // The pauses at punctuation (pauses.h), which the client asks for as an item.
    // Spelling puts a comma between letters that is the pace of spelling, not a
    // pause to shorten, so a request that spells anything keeps its pauses.
    int pause_mode = 0;
    bool spells = false;
    // one letter and nothing else is named, whatever the mode
    const bool lone = !spelling_mode(text_mode) && lone_letter(text_of(r));
    // punctuation is named when everything is spelled, not only letters and digits
    bool name_punctuation = text_mode == 2 || text_mode == 3;
    size_t pos = 0;
    for (uint32_t i = 0; i < q.item_count && pos + sizeof(proto::Item) <= r.items.size(); ++i) {
        proto::Item it;
        memcpy(&it, r.items.data() + pos, sizeof it);
        pos += sizeof it;
        if (it.kind == proto::kItemText) {
            if (it.a <= 0 || pos + static_cast<size_t>(it.a) > r.items.size()) break;
            std::string t(reinterpret_cast<const char*>(r.items.data() + pos), static_cast<size_t>(it.a));
            pos += static_cast<size_t>(it.a);
            if (spelling_mode(text_mode) || lone) {
                t = spelled(t);
                spells = spells || !lone; // a lone letter has no comma between letters to keep
            } else if (q.user_dicts & proto::kDictUser) {
                t = g_text_dict.apply(t);
            }
            all += t;
            at += static_cast<uint32_t>(count_code_points(t));
            continue;
        }
        if (it.kind == proto::kItemParam && it.a == kParamTextMode) {
            // the engine never spells the annotations; eSpeak NG spells the letters
            text_mode = it.b;
            name_punctuation = name_punctuation || it.b == 2 || it.b == 3;
            continue;
        }
        if (it.kind == proto::kItemParam && it.a == kParamInputType) continue;
        if (it.kind == proto::kItemPauses) {
            pause_mode = std::max(0, std::min(2, it.a));
            continue;
        }
        placed.push_back({it, at});
    }
    std::string out;
    std::vector<EvvAnchor> anchors;
    if (!g_fe.translate(all, name_punctuation ? EVV_FE_FLAG_PUNCTUATION : 0, out, anchors, error)) return false;
    size_t next = 0;
    const bool shorten = pause_mode != 0 && !spells && !name_punctuation;
    auto add = [&](size_t from, size_t to) {
        if (to <= from) return;
        std::string piece = out.substr(from, to - from);
        // The clause that ends a piece ends with a mark; the last piece ends the text.
        if (shorten) piece = shorten_annotated(piece, pause_mode == 2, to >= out.size());
        g_eci.AddText(g_h, piece.c_str());
        if (log::enabled(log::kFull) && preview.size() < 400) preview += piece;
    };
    size_t done = 0;
    for (size_t k = 0; k < anchors.size(); ++k) {
        const size_t start = std::min<size_t>(anchors[k].out_offset, out.size());
        const bool fresh = k == 0 || anchors[k].src_offset != anchors[k - 1].src_offset;
        if (fresh && next < placed.size() && placed[next].at <= anchors[k].src_offset) {
            add(done, start);
            done = start;
            while (next < placed.size() && placed[next].at <= anchors[k].src_offset) apply_item(placed[next++].item);
        }
    }
    add(done, out.size());
    while (next < placed.size()) apply_item(placed[next++].item);
    return true;
}

void run(Request& r)
{
    const proto::SpeakReq& q = r.req;
    g_t_request = now_ms();
    g_first_audio = -1;
    g_delivered = 0;
    g_current.store(q.id, std::memory_order_release);

    if (g_use_fe) {
        set_param_cached(kParamSampleRate, q.sample_rate, g_rate);
        set_param_cached(kParamTextMode, 0, g_text_mode);
        set_param_cached(kParamInputType, 1, g_input_type);
        if (q.preset >= 1 && q.preset <= 8) g_eci.CopyVoice(g_h, q.preset, 0);
        for (int i = 0; i < kVoiceParamCount; ++i) {
            if (q.voice[i] >= 0) g_eci.SetVoiceParam(g_h, 0, i, q.voice[i]);
        }
        // A language with a melody or tones of its own has its pitch made
        // from the voice's pitch and pitch fluctuation, which the engine
        // only ever says when they are set: so they are set, to what they
        // are already.
        for (const int i : {kVoicePitchBaseline, kVoicePitchFluctuation}) {
            const int v = g_eci.GetVoiceParam(g_h, 0, i);
            if (v >= 0) g_eci.SetVoiceParam(g_h, 0, i, v);
        }
        if (q.user_dicts & proto::kDictUser) {
            std::wstring files[3];
            for (int v = 0; v < 3; ++v) files[v] = dict_file(v);
            g_text_dict.set_files(files);
        }
        std::string preview, error;
        if (!add_translated(r, preview, error)) {
            log::write(log::kStandard, "host: request %u: %s", q.id, error.c_str());
            send_done(q.id, proto::kDoneFailed, error.c_str());
            return;
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
            quit(3);
        }
        send_done(q.id, cancelled ? proto::kDoneCancelled : proto::kDoneOk, nullptr);
        log::write(log::kStandard, "host: #%u %s: %llu samples, first audio %.2f ms, done in %.2f ms", q.id,
                   cancelled ? "cancelled" : "spoken", static_cast<unsigned long long>(g_delivered), g_first_audio,
                   now_ms() - g_t_request);
        if (log::enabled(log::kFull)) log::write(log::kFull, "host: #%u annotated \"%s\"", q.id, preview.c_str());
        return;
    }

    set_param_cached(kParamSampleRate, q.sample_rate, g_rate);
    set_param_cached(kParamTextMode, q.text_mode, g_text_mode);
    set_param_cached(kParamNumberMode, q.number_mode, g_number_mode);
    // eciDictionary is inverted: one turns the dictionary off.
    set_param_cached(kParamDictionary, q.dictionary ? 0 : 1, g_dictionary);
    set_param_cached(kParamInputType, q.input_type, g_input_type);
    refresh_dictionaries((q.user_dicts & proto::kDictUser) != 0, (q.user_dicts & proto::kDictCommunityOff) == 0);

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

// A mark, a voice change or a parameter, for a pack read by eSpeak NG.
void apply_item(const proto::Item& it)
{
    switch (it.kind) {
    case proto::kItemIndex:
        g_eci.InsertIndex(g_h, it.a);
        break;
    case proto::kItemVoice:
        if (it.a >= 0 && it.a < kVoiceParamCount) g_eci.SetVoiceParam(g_h, 0, it.a, it.b);
        break;
    case proto::kItemParam:
        if (it.a != kParamTextMode && it.a != kParamInputType && it.a != kParamNumberMode &&
            it.a != kParamDictionary)
            g_eci.SetParam(g_h, it.a, it.b);
        break;
    default:
        break;
    }
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
    if (!g_args.frontend.empty()) {
        // A pack read by eSpeak NG: its front-end, and annotations always.
        std::string err;
        if (!g_fe.start(g_args.frontend, g_args.fe_data, g_args.fe_voice, g_args.fe_map, err)) {
            snprintf(ready.error, sizeof ready.error, "%s", err.c_str());
            return false;
        }
        g_use_fe = true;
        g_eci.SetParam(g_h, kParamInputType, 1);
        g_input_type = 1;
    }
    // Warm up: the first utterance an instance speaks pays for touching its
    // memory. Pay it now, into nothing, rather than on the user's first word.
    g_current = kWarmId;
    g_cancel_id = kWarmId;
    if (g_use_fe) {
        std::string out, err;
        std::vector<EvvAnchor> anchors;
        if (!g_fe.translate("1 2 3.", 0, out, anchors, err)) {
            snprintf(ready.error, sizeof ready.error, "%s", err.c_str());
            return false;
        }
        g_eci.AddText(g_h, out.c_str());
    } else {
        g_eci.AddText(g_h, "Ready. 1 2 3.");
    }
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
