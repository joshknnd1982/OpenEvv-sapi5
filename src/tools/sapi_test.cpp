// sapi_test: drives OpenEvvSAPI.dll's ISpTTSEngine through a mock
// ISpTTSEngineSite, so every behaviour can be checked without installing or
// registering anything.
//
//   sapi_test [--dll PATH] [--out DIR] [--only NAME] [--all-voices]
//
// Writes WAVs to DIR (default .\sapi_test_out) and exits non-zero if any check
// fails. The mock site leaves Write's pcbWritten untouched, as the real SAPI
// site does not reliably set it, and refuses a part sample as the real one
// does. Settings are redirected to a scratch file (OPENEVV_SETTINGS).
#include <windows.h>
#include <sapi.h>
#include <sapiddk.h>
#include <shlobj.h>
#include <tlhelp32.h>

#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdarg>
#include <cstdio>
#include <functional>
#include <map>
#include <string>
#include <vector>

#include "common/languages.h"

using evv::LanguageInfo;
using evv::scan_languages;

namespace {

const CLSID kEngineClsid = {0xf3cc6ab4, 0xc4c4, 0x4ec6, {0xaa, 0x1f, 0x1a, 0x11, 0x43, 0x67, 0xae, 0x91}};
const CLSID kEnumClsid = {0x90e5cef9, 0x18dd, 0x435e, {0xae, 0x19, 0xbe, 0xc9, 0xb5, 0x8d, 0x36, 0x27}};

double now_ms()
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return 1000.0 * static_cast<double>(c.QuadPart) / static_cast<double>(f.QuadPart);
}

struct Event
{
    SPEVENTENUM id;
    ULONGLONG offset;
    WPARAM wp;
    LPARAM lp;
    std::wstring text;
};

class MockSite : public ISpTTSEngineSite
{
public:
    std::vector<int16_t> audio;
    std::vector<Event> events;
    ULONGLONG interest = SPFEI(SPEI_TTS_BOOKMARK);
    long rate = 0;
    USHORT volume = 100;
    double abort_after_ms = -1; // raise SPVES_ABORT this long after the first write
    double t_start = 0, t_first_write = -1, t_abort_seen = -1;
    std::atomic<long> refs{1};

    STDMETHODIMP QueryInterface(REFIID riid, void** ppv) override
    {
        if (riid == IID_IUnknown || riid == __uuidof(ISpEventSink) || riid == __uuidof(ISpTTSEngineSite)) {
            *ppv = this;
            AddRef();
            return S_OK;
        }
        *ppv = nullptr;
        return E_NOINTERFACE;
    }
    STDMETHODIMP_(ULONG) AddRef() override { return ++refs; }
    STDMETHODIMP_(ULONG) Release() override { return --refs; }
    STDMETHODIMP AddEvents(const SPEVENT* e, ULONG n) override
    {
        for (ULONG i = 0; i < n; ++i) {
            Event ev{static_cast<SPEVENTENUM>(e[i].eEventId), e[i].ullAudioStreamOffset, e[i].wParam, e[i].lParam, L""};
            if (e[i].elParamType == SPET_LPARAM_IS_STRING && e[i].lParam) {
                ev.text = reinterpret_cast<const wchar_t*>(e[i].lParam);
                CoTaskMemFree(reinterpret_cast<void*>(e[i].lParam)); // as SAPI does
            }
            events.push_back(ev);
        }
        return S_OK;
    }
    STDMETHODIMP GetEventInterest(ULONGLONG* p) override
    {
        *p = interest;
        return S_OK;
    }
    STDMETHODIMP_(DWORD) GetActions() override
    {
        if (abort_after_ms >= 0 && t_first_write >= 0 && now_ms() - t_first_write >= abort_after_ms) {
            if (t_abort_seen < 0) t_abort_seen = now_ms();
            return SPVES_ABORT;
        }
        return SPVES_CONTINUE;
    }
    STDMETHODIMP Write(const void* p, ULONG cb, ULONG*) override
    {
        if (cb % 2) return E_INVALIDARG;
        if (t_first_write < 0) t_first_write = now_ms();
        const auto* s = static_cast<const int16_t*>(p);
        audio.insert(audio.end(), s, s + cb / 2);
        return S_OK; // pcbWritten deliberately not set
    }
    STDMETHODIMP GetRate(long* p) override
    {
        *p = rate;
        return S_OK;
    }
    STDMETHODIMP GetVolume(USHORT* p) override
    {
        *p = volume;
        return S_OK;
    }
    STDMETHODIMP GetSkipInfo(SPVSKIPTYPE* t, long* n) override
    {
        *t = SPVST_SENTENCE;
        *n = 0;
        return S_OK;
    }
    STDMETHODIMP CompleteSkip(long) override { return S_OK; }
};

struct Frags
{
    struct Item
    {
        SPVACTIONS action;
        std::wstring text;
        long rate_adj = 0;
        long pitch_adj = 0;
        ULONG volume = 100;
        ULONG silence_ms = 0;
    };
    std::vector<Item> items;
    std::vector<SPVTEXTFRAG> frags;
    std::wstring all;

    Frags& text(const std::wstring& t, long rate_adj = 0, long pitch_adj = 0, ULONG vol = 100)
    {
        items.push_back({SPVA_Speak, t, rate_adj, pitch_adj, vol});
        return *this;
    }
    Frags& spell(const std::wstring& t)
    {
        items.push_back({SPVA_SpellOut, t});
        return *this;
    }
    Frags& mark(const std::wstring& t)
    {
        items.push_back({SPVA_Bookmark, t});
        return *this;
    }
    Frags& silence(ULONG ms)
    {
        Item i{SPVA_Silence, L""};
        i.silence_ms = ms;
        items.push_back(i);
        return *this;
    }
    const SPVTEXTFRAG* build()
    {
        all.clear();
        for (const auto& i : items) all += i.text;
        frags.assign(items.size(), SPVTEXTFRAG{});
        size_t off = 0;
        for (size_t k = 0; k < items.size(); ++k) {
            SPVTEXTFRAG& f = frags[k];
            f.pNext = k + 1 < items.size() ? &frags[k + 1] : nullptr;
            f.State.eAction = items[k].action;
            f.State.LangID = 0x409;
            f.State.RateAdj = items[k].rate_adj;
            f.State.Volume = items[k].volume;
            f.State.PitchAdj.MiddleAdj = items[k].pitch_adj;
            f.State.SilenceMSecs = items[k].silence_ms;
            f.pTextStart = all.c_str() + off;
            f.ulTextLen = static_cast<ULONG>(items[k].text.size());
            f.ulTextSrcOffset = static_cast<ULONG>(off);
            off += items[k].text.size();
        }
        return frags.empty() ? nullptr : frags.data();
    }
};

std::wstring g_dll_path, g_out, g_settings;
int g_fail = 0, g_pass = 0;
int g_rate_hz = 11025;

void check(bool ok, const char* what, const std::string& detail = "")
{
    printf("  [%s] %s%s%s\n", ok ? "pass" : "FAIL", what, detail.empty() ? "" : ": ", detail.c_str());
    (ok ? g_pass : g_fail)++;
}

std::string fmt(const char* f, ...)
{
    char b[1024];
    va_list ap;
    va_start(ap, f);
    vsnprintf(b, sizeof b, f, ap);
    va_end(ap);
    return b;
}

std::string narrow(const std::wstring& w)
{
    std::string s;
    for (wchar_t c : w) s.push_back(c < 128 ? static_cast<char>(c) : '?');
    return s;
}

using GetClassObjectFn = HRESULT(STDAPICALLTYPE*)(REFCLSID, REFIID, void**);
HMODULE g_dll = nullptr;
GetClassObjectFn g_gco = nullptr;

struct Voice
{
    ISpTTSEngine* engine = nullptr;
    ISpObjectWithToken* with_token = nullptr;
    std::wstring name;
    double set_token_ms = 0;
    void release()
    {
        if (with_token) with_token->Release();
        if (engine) engine->Release();
        engine = nullptr;
        with_token = nullptr;
    }
};

IEnumSpObjectTokens* enumerator()
{
    IClassFactory* cf = nullptr;
    g_gco(kEnumClsid, IID_IClassFactory, reinterpret_cast<void**>(&cf));
    IEnumSpObjectTokens* en = nullptr;
    cf->CreateInstance(nullptr, __uuidof(IEnumSpObjectTokens), reinterpret_cast<void**>(&en));
    cf->Release();
    return en;
}

std::wstring token_attr(ISpObjectToken* t, const wchar_t* name)
{
    ISpDataKey* attrs = nullptr;
    std::wstring out;
    if (SUCCEEDED(t->OpenKey(L"Attributes", &attrs)) && attrs) {
        wchar_t* v = nullptr;
        if (SUCCEEDED(attrs->GetStringValue(name, &v)) && v) {
            out = v;
            CoTaskMemFree(v);
        }
        attrs->Release();
    }
    return out;
}

// Voice by language tag and preset.
Voice load_voice(const std::wstring& tag, int preset)
{
    Voice v;
    IEnumSpObjectTokens* en = enumerator();
    ULONG count = 0;
    en->GetCount(&count);
    ISpObjectToken* token = nullptr;
    for (ULONG i = 0; i < count && !token; ++i) {
        ISpObjectToken* t = nullptr;
        if (FAILED(en->Item(i, &t))) continue;
        if (token_attr(t, L"OpenEvvLanguage") == tag && token_attr(t, L"OpenEvvPreset") == std::to_wstring(preset)) {
            token = t;
        } else {
            t->Release();
        }
    }
    en->Release();
    if (!token) {
        printf("no voice %s-%d\n", narrow(tag).c_str(), preset);
        return v;
    }
    v.name = token_attr(token, L"Name");
    IClassFactory* cf = nullptr;
    g_gco(kEngineClsid, IID_IClassFactory, reinterpret_cast<void**>(&cf));
    cf->CreateInstance(nullptr, __uuidof(ISpTTSEngine), reinterpret_cast<void**>(&v.engine));
    cf->Release();
    v.engine->QueryInterface(__uuidof(ISpObjectWithToken), reinterpret_cast<void**>(&v.with_token));
    const double t0 = now_ms();
    v.with_token->SetObjectToken(token);
    v.set_token_ms = now_ms() - t0;
    token->Release();
    return v;
}

struct Run
{
    std::vector<int16_t> audio;
    std::vector<Event> events;
    double first_ms = -1, total_ms = 0, abort_to_return_ms = -1;
    HRESULT hr = S_OK;
};

Run speak(Voice& v, Frags& f, std::function<void(MockSite&)> setup = nullptr, DWORD hz = 0)
{
    MockSite site;
    if (setup) setup(site);
    const SPVTEXTFRAG* list = f.build();
    const DWORD rate = hz ? hz : g_rate_hz;
    WAVEFORMATEX wfx{WAVE_FORMAT_PCM, 1, rate, rate * 2, 2, 16, 0};
    site.t_start = now_ms();
    Run r;
    r.hr = v.engine->Speak(0, SPDFID_WaveFormatEx, &wfx, list, &site);
    const double end = now_ms();
    r.total_ms = end - site.t_start;
    r.first_ms = site.t_first_write < 0 ? -1 : site.t_first_write - site.t_start;
    if (site.t_abort_seen >= 0) r.abort_to_return_ms = end - site.t_abort_seen;
    r.audio = std::move(site.audio);
    r.events = std::move(site.events);
    return r;
}

double seconds(const std::vector<int16_t>& a, int hz = 0)
{
    return a.size() / static_cast<double>(hz ? hz : g_rate_hz);
}

double rms(const std::vector<int16_t>& a)
{
    double s = 0;
    for (int16_t x : a) s += static_cast<double>(x) * x;
    return a.empty() ? 0 : std::sqrt(s / a.size());
}

void save(const std::vector<int16_t>& a, const std::wstring& name, int hz = 0)
{
    const std::wstring path = g_out + L"\\" + name;
    FILE* f = _wfopen(path.c_str(), L"wb");
    if (!f) return;
    const uint32_t rate = hz ? hz : g_rate_hz;
    const uint32_t data = static_cast<uint32_t>(a.size() * 2), riff = 36 + data, fmtlen = 16, bps = rate * 2;
    const uint16_t pcm = 1, ch = 1, align = 2, bits = 16;
    fwrite("RIFF", 1, 4, f); fwrite(&riff, 4, 1, f); fwrite("WAVEfmt ", 1, 8, f); fwrite(&fmtlen, 4, 1, f);
    fwrite(&pcm, 2, 1, f); fwrite(&ch, 2, 1, f); fwrite(&rate, 4, 1, f); fwrite(&bps, 4, 1, f);
    fwrite(&align, 2, 1, f); fwrite(&bits, 2, 1, f); fwrite("data", 1, 4, f); fwrite(&data, 4, 1, f);
    fwrite(a.data(), 2, a.size(), f);
    fclose(f);
}

// Median F0 by normalised autocorrelation over voiced 40 ms frames.
double f0(const std::vector<int16_t>& a, int hz)
{
    const int fr = hz / 25;
    std::vector<double> v;
    for (size_t i = 0; i + 2 * static_cast<size_t>(fr) < a.size(); i += fr / 2) {
        double e = 0;
        for (int k = 0; k < fr; ++k) e += static_cast<double>(a[i + k]) * a[i + k];
        if (std::sqrt(e / fr) < 1500) continue;
        int best = 0;
        double best_c = 0;
        for (int lag = hz / 420; lag <= hz / 42; ++lag) {
            double c = 0, e1 = 0, e2 = 0;
            for (int k = 0; k < fr; ++k) {
                c += static_cast<double>(a[i + k]) * a[i + k + lag];
                e1 += static_cast<double>(a[i + k]) * a[i + k];
                e2 += static_cast<double>(a[i + k + lag]) * a[i + k + lag];
            }
            const double n = c / std::sqrt(e1 * e2 + 1e-9);
            if (n > best_c + 1e-6) {
                best_c = n;
                best = lag;
            }
        }
        if (best && best_c > 0.6) v.push_back(static_cast<double>(hz) / best);
    }
    if (v.empty()) return 0;
    std::sort(v.begin(), v.end());
    return v[v.size() / 2];
}

void write_settings(const std::string& body)
{
    FILE* f = _wfopen(g_settings.c_str(), L"wb");
    if (!f) return;
    fwrite(body.data(), 1, body.size(), f);
    fclose(f);
    Sleep(20); // a new timestamp even on coarse file systems
}

std::vector<DWORD> host_pids()
{
    std::vector<DWORD> out;
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    PROCESSENTRY32W pe{sizeof pe};
    for (BOOL ok = Process32FirstW(snap, &pe); ok; ok = Process32NextW(snap, &pe)) {
        if (_wcsicmp(pe.szExeFile, L"OpenEvvHost.exe") == 0 && pe.th32ParentProcessID == GetCurrentProcessId()) {
            out.push_back(pe.th32ProcessID);
        }
    }
    CloseHandle(snap);
    return out;
}

bool want(const char* name, const std::string& only)
{
    return only.empty() || only == name;
}

struct LangSample
{
    const wchar_t* tag;
    const wchar_t* text;
};

// A pack's own sample sentence (sample.txt, UTF-8), or its name.
// A pack's own sample sentence, and some numbers, which eSpeak NG reads in
// the language: never too short to measure, even where the sentence is a word.
std::wstring pack_sample(const LanguageInfo& li)
{
    const std::wstring w = evv::pack_sample_text(li);
    return (w.empty() ? li.name : w) + L" 1, 2, 3, 10, 25.";
}

const LangSample kLangSamples[] = {
    {L"enus", L"Hello. This is OpenEVV speaking US English through SAPI five."},
    {L"engb", L"Hello. This is OpenEVV speaking British English. The colour is grey."},
    {L"dede", L"Guten Tag. Das ist OpenEVV. Zwölf Boxkämpfer jagen Viktor über den großen Deich."},
    {L"eses", L"Hola. Esto es OpenEVV hablando español. ¿Cómo estás?"},
    {L"esus", L"Hola. Esto es OpenEVV hablando español de México."},
    {L"frfr", L"Bonjour. Ceci est OpenEVV qui parle français. Ça va très bien."},
    {L"frca", L"Bonjour. Ceci est OpenEVV qui parle français canadien."},
    {L"itit", L"Buongiorno. Questo è OpenEVV che parla italiano. Perché no?"},
    {L"plpl", L"Dzień dobry. To jest OpenEVV. Zażółć gęślą jaźń."},
    {L"jajp", L"こんにちは。これは日本語の音声です。"},
};

} // namespace

int wmain(int argc, wchar_t** argv)
{
    std::string only;
    bool all_voices = false;
    for (int i = 1; i < argc; ++i) {
        const std::wstring a = argv[i];
        if (a == L"--dll" && i + 1 < argc) g_dll_path = argv[++i];
        else if (a == L"--out" && i + 1 < argc) g_out = argv[++i];
        else if (a == L"--only" && i + 1 < argc) only = narrow(argv[++i]);
        else if (a == L"--all-voices") all_voices = true;
    }
    wchar_t here[MAX_PATH];
    GetModuleFileNameW(nullptr, here, MAX_PATH);
    std::wstring dir(here);
    dir = dir.substr(0, dir.find_last_of(L'\\'));
    if (g_dll_path.empty()) g_dll_path = dir + L"\\OpenEvvSAPI.dll";
    if (g_out.empty()) g_out = dir + L"\\sapi_test_out";
    SHCreateDirectoryExW(nullptr, g_out.c_str(), nullptr);
    g_settings = g_out + L"\\test_settings.ini";
    DeleteFileW(g_settings.c_str());
    SetEnvironmentVariableW(L"OPENEVV_SETTINGS", g_settings.c_str());
    write_settings("[General]\r\nLogLevel=1\r\n");
    CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    printf("sapi_test (%s) on %s\n", sizeof(void*) == 8 ? "64-bit" : "32-bit", narrow(g_dll_path).c_str());

    g_dll = LoadLibraryExW(g_dll_path.c_str(), nullptr, LOAD_WITH_ALTERED_SEARCH_PATH);
    if (!g_dll) {
        printf("cannot load the DLL (%lu)\n", GetLastError());
        return 2;
    }
    g_gco = reinterpret_cast<GetClassObjectFn>(GetProcAddress(g_dll, "DllGetClassObject"));

    // ---- the voice list -------------------------------------------------------
    std::vector<std::pair<std::wstring, int>> voices;
    {
        printf("voice list\n");
        IEnumSpObjectTokens* en = enumerator();
        ULONG count = 0;
        en->GetCount(&count);
        std::map<std::wstring, int> per_lang;
        bool attrs_ok = true;
        for (ULONG i = 0; i < count; ++i) {
            ISpObjectToken* t = nullptr;
            if (FAILED(en->Item(i, &t))) continue;
            const std::wstring tag = token_attr(t, L"OpenEvvLanguage");
            const int preset = _wtoi(token_attr(t, L"OpenEvvPreset").c_str());
            per_lang[tag]++;
            voices.emplace_back(tag, preset);
            wchar_t* id = nullptr;
            t->GetId(&id);
            if (token_attr(t, L"Name").empty() || token_attr(t, L"Gender").empty() ||
                token_attr(t, L"Language").empty() || !id || !wcsstr(id, L"TokenEnums\\OpenEVV\\")) {
                attrs_ok = false;
            }
            if (i < 3 || i == count - 1) {
                printf("    %s  [%s, %s, lang %s]\n", narrow(token_attr(t, L"Name")).c_str(),
                       narrow(token_attr(t, L"Gender")).c_str(), narrow(token_attr(t, L"Age")).c_str(),
                       narrow(token_attr(t, L"Language")).c_str());
            }
            CoTaskMemFree(id);
            t->Release();
        }
        en->Release();
        // Every language pack's eight presets: the ten built-in languages and
        // every pack read by eSpeak NG.
        const std::vector<LanguageInfo> packs = scan_languages();
        size_t expected = 0;
        for (const LanguageInfo& li : packs) expected += li.voices.size();
        check(count == expected && expected >= 80, "every preset of every language pack is a voice",
              fmt("%lu voices from %zu languages; the packs have %zu", count, per_lang.size(), expected));
        for (const LanguageInfo& li : packs) {
            if (!per_lang.count(li.tag)) printf("    missing from the voice list: %s\n", narrow(li.tag).c_str());
        }
        check(attrs_ok, "every token has a name, gender, language and an OpenEVV token id");
    }

    Voice en = load_voice(L"enus", 1);
    if (!en.engine) return 2;
    printf("voice %s: SetObjectToken %.1f ms (starts the engine host)\n", narrow(en.name).c_str(), en.set_token_ms);

    // ---- latency ---------------------------------------------------------------
    if (want("latency", only)) {
        printf("latency\n");
        Frags f;
        f.text(L"Hello.");
        Run cold = speak(en, f);
        std::vector<double> firsts;
        for (int i = 0; i < 20; ++i) {
            Frags g;
            g.text(i % 2 ? L"Line down." : L"x");
            firsts.push_back(speak(en, g).first_ms);
        }
        std::sort(firsts.begin(), firsts.end());
        check(cold.first_ms >= 0 && cold.first_ms < 500, "first utterance speaks promptly after the voice is chosen",
              fmt("%.2f ms to the first audio", cold.first_ms));
        check(firsts[10] < 20, "warm: Speak() to the first audio",
              fmt("median %.2f ms, best %.2f, worst %.2f", firsts[10], firsts.front(), firsts.back()));
        // A language read by eSpeak NG pays for the reading as well.
        LanguageInfo sw;
        if (evv::find_language(L"sw", sw)) {
            Voice v = load_voice(L"sw", 1);
            Frags w0;
            w0.text(L"Habari.");
            speak(v, w0);
            std::vector<double> fe;
            for (int i = 0; i < 20; ++i) {
                Frags g;
                g.text(i % 2 ? L"Mstari chini." : L"x");
                fe.push_back(speak(v, g).first_ms);
            }
            std::sort(fe.begin(), fe.end());
            check(fe[10] < 25, "warm, a language read by eSpeak NG: Speak() to the first audio",
                  fmt("median %.2f ms, best %.2f, worst %.2f", fe[10], fe.front(), fe.back()));
            v.release();
        }
    }

    // ---- every language -----------------------------------------------------------
    if (want("languages", only)) {
        printf("languages\n");
        for (const auto& ls : kLangSamples) {
            Voice v = load_voice(ls.tag, 1);
            if (!v.engine) {
                check(false, "voice loads", narrow(ls.tag));
                continue;
            }
            Frags f;
            f.text(ls.text);
            Run r = speak(v, f);
            save(r.audio, std::wstring(L"lang_") + ls.tag + L".wav");
            check(r.hr == S_OK && seconds(r.audio) > 1.0 && rms(r.audio) > 500,
                  fmt("%s speaks", narrow(ls.tag).c_str()).c_str(),
                  fmt("%.2f s, rms %.0f, first audio %.1f ms", seconds(r.audio), rms(r.audio), r.first_ms));
            v.release();
        }
        // Every pack read by eSpeak NG, with its own sample sentence.
        int fe_ok = 0, fe_total = 0;
        double worst_first = 0;
        for (const LanguageInfo& li : scan_languages()) {
            if (!li.has_frontend()) continue;
            ++fe_total;
            Voice v = load_voice(li.tag, 1);
            if (!v.engine) {
                printf("    %s: the voice does not load\n", narrow(li.tag).c_str());
                continue;
            }
            Frags f;
            f.text(pack_sample(li));
            Run r = speak(v, f);
            save(r.audio, std::wstring(L"lang_") + li.tag + L".wav");
            if (r.hr == S_OK && seconds(r.audio) > 0.5 && rms(r.audio) > 300) {
                ++fe_ok;
                worst_first = std::max(worst_first, r.first_ms);
            } else {
                printf("    %s: %.2f s, rms %.0f\n", narrow(li.tag).c_str(), seconds(r.audio), rms(r.audio));
            }
            v.release();
        }
        check(fe_ok == fe_total && fe_total > 0, "every language read by eSpeak NG speaks its sample through SAPI",
              fmt("%d of %d, slowest first audio %.1f ms (a cold host each)", fe_ok, fe_total, worst_first));
    }

    if (all_voices) {
        printf("every voice\n");
        int ok = 0;
        for (const auto& [tag, preset] : voices) {
            Voice v = load_voice(tag, preset);
            const LangSample* ls = nullptr;
            for (const auto& s : kLangSamples) {
                if (tag == s.tag) ls = &s;
            }
            Frags f;
            LanguageInfo li;
            if (ls) f.text(ls->text);
            else if (evv::find_language(tag, li)) f.text(pack_sample(li));
            else f.text(L"Hello.");
            Run r = speak(v, f);
            save(r.audio, L"voice_" + tag + L"_" + std::to_wstring(preset) + L".wav");
            if (seconds(r.audio) > 1.0) ++ok;
            else printf("    %s-%d: %.2f s\n", narrow(tag).c_str(), preset, seconds(r.audio));
            v.release();
        }
        check(ok == static_cast<int>(voices.size()), "every voice speaks through SAPI",
              fmt("%d of %zu", ok, voices.size()));
    }

    // ---- events ------------------------------------------------------------------------
    if (want("bookmarks", only)) {
        printf("bookmarks\n");
        Frags a;
        a.text(L"Hello, this is a test. ").mark(L"127").text(L"And here is more. ").mark(L"128");
        Run r = speak(en, a);
        Frags b;
        b.text(L"Hello, this is a test. ").text(L"And here is more. ");
        Run plain = speak(en, b);
        std::vector<Event> marks;
        for (const auto& e : r.events) {
            if (e.id == SPEI_TTS_BOOKMARK) marks.push_back(e);
        }
        check(marks.size() == 2 && marks[0].text == L"127" && marks[1].text == L"128" && marks[0].wp == 127,
              "bookmarks arrive as events with their names and numbers", fmt("%zu events", marks.size()));
        check(r.audio.size() == plain.audio.size(), "bookmarks are not spoken",
              fmt("%zu samples with, %zu without", r.audio.size(), plain.audio.size()));
        check(marks.size() == 2 && marks[0].offset > 0 && marks[0].offset < marks[1].offset &&
                  marks[1].offset <= r.audio.size() * 2,
              "bookmark offsets are inside the audio, in order",
              marks.size() == 2 ? fmt("%llu, %llu of %zu bytes", marks[0].offset, marks[1].offset, r.audio.size() * 2)
                                : "");
    }

    if (want("words", only)) {
        printf("word and sentence events\n");
        Frags a;
        a.text(L"The quick brown fox. Jumps over the lazy dog!");
        Run r = speak(en, a, [](MockSite& s) {
            s.interest = SPFEI(SPEI_WORD_BOUNDARY) | SPFEI(SPEI_SENTENCE_BOUNDARY) | SPFEI(SPEI_TTS_BOOKMARK);
        });
        Frags b;
        b.text(L"The quick brown fox. Jumps over the lazy dog!");
        Run plain = speak(en, b);
        int words = 0, sentences = 0;
        bool ordered = true;
        ULONGLONG last = 0;
        std::wstring spoken;
        for (const auto& e : r.events) {
            if (e.id == SPEI_WORD_BOUNDARY) {
                ++words;
                if (e.offset < last) ordered = false;
                last = e.offset;
                spoken += a.all.substr(e.lp, e.wp) + L"|";
            }
            if (e.id == SPEI_SENTENCE_BOUNDARY) ++sentences;
        }
        check(words == 9, "a word event for each word", fmt("%d: %s", words, narrow(spoken).c_str()));
        check(sentences == 2, "a sentence event for each sentence", fmt("%d", sentences));
        check(ordered, "word events in audio order");
        check(r.audio.size() == plain.audio.size(), "word marks do not change the audio",
              fmt("%zu with, %zu without", r.audio.size(), plain.audio.size()));

        // The same for a language read by eSpeak NG: its words are read as one
        // text and the marks put back in front of the word each belongs to.
        LanguageInfo sw;
        if (evv::find_language(L"sw", sw)) {
            Voice v = load_voice(L"sw", 1);
            const wchar_t* text = L"Watu wote wamezaliwa huru. Nina miaka 25, je?";
            Frags c;
            c.text(text);
            Run rw = speak(v, c, [](MockSite& s) {
                s.interest = SPFEI(SPEI_WORD_BOUNDARY) | SPFEI(SPEI_SENTENCE_BOUNDARY);
            });
            Frags d;
            d.text(text);
            Run pw = speak(v, d);
            int w = 0, sent = 0;
            bool in_order = true;
            ULONGLONG at = 0;
            std::wstring heard;
            for (const auto& e : rw.events) {
                if (e.id == SPEI_WORD_BOUNDARY) {
                    ++w;
                    if (e.offset < at) in_order = false;
                    at = e.offset;
                    heard += c.all.substr(e.lp, e.wp) + L"|";
                }
                if (e.id == SPEI_SENTENCE_BOUNDARY) ++sent;
            }
            check(w == 8 && sent == 2 && in_order, "eSpeak NG language: a word event for each word, in order",
                  fmt("%d words, %d sentences: %s", w, sent, narrow(heard).c_str()));
            check(rw.audio.size() == pw.audio.size() && !pw.audio.empty(),
                  "eSpeak NG language: word marks do not change the audio",
                  fmt("%zu with, %zu without", rw.audio.size(), pw.audio.size()));
            v.release();
        }
    }

    if (want("silence", only)) {
        printf("silence\n");
        Frags a;
        a.text(L"Before the pause.").silence(700).text(L"After it.");
        Frags b;
        b.text(L"Before the pause.").text(L"After it.");
        Run r = speak(en, a), p = speak(en, b);
        const double added = seconds(r.audio) - seconds(p.audio);
        check(added > 0.65 && added < 0.75, "<silence msec=700/> adds 700 ms", fmt("%.3f s", added));
    }

    // ---- shorter pauses at punctuation (pauses.h) ---------------------------------------------
    if (want("pauses", only)) {
        printf("shorter pauses at punctuation\n");
        // One text at one of the three pause modes: 0 as the engine has them, 1 the
        // pause after the last word shortened, 2 all of them.
        auto say = [&](Voice& v, const std::wstring& text, int mode, bool events = false) {
            write_settings(fmt("[General]\r\nLogLevel=1\r\nPauseMode=%d\r\n", mode));
            Frags f;
            f.text(text);
            return speak(v, f, [&](MockSite& site) {
                if (events) site.interest = SPFEI(SPEI_WORD_BOUNDARY) | SPFEI(SPEI_SENTENCE_BOUNDARY);
            });
        };
        const size_t n_native = sizeof kLangSamples / sizeof kLangSamples[0];
        size_t native_ok = 0;
        std::string native_detail;
        for (const auto& ls : kLangSamples) {
            Voice v = load_voice(ls.tag, 1);
            if (!v.engine) continue;
            const double a0 = seconds(say(v, ls.text, 0).audio), a1 = seconds(say(v, ls.text, 1).audio),
                         a2 = seconds(say(v, ls.text, 2).audio);
            // Mode 1 takes away about the silence after the last word, mode 2 that and the ones between phrases.
            const bool ok = a0 - a1 > 0.2 && a0 - a1 < 0.7 && a1 - a2 > 0.3 && a2 > 0.5;
            if (ok) ++native_ok;
            else native_detail += fmt(" %s %.2f/%.2f/%.2f", narrow(ls.tag).c_str(), a0, a1, a2);
            v.release();
        }
        check(native_ok == n_native,
              "every language the engine speaks itself: mode 1 shortens the end, mode 2 the rest as well",
              native_detail.empty() ? fmt("%zu of %zu", native_ok, n_native) : native_detail);
        // Languages read by eSpeak NG: the host puts the annotations into the front-end's text.
        const struct
        {
            const wchar_t* tag;
            const wchar_t* text;
        } fe[] = {{L"sw", L"Watu wote wamezaliwa huru. Nina miaka 25, je? Ndiyo."},
                  {L"nl", L"Nou, dat is goed. Is het waar? Ja!"}};
        for (const auto& f : fe) {
            LanguageInfo li;
            if (!evv::find_language(f.tag, li)) continue;
            Voice v = load_voice(f.tag, 1);
            const double a0 = seconds(say(v, f.text, 0).audio), a1 = seconds(say(v, f.text, 1).audio),
                         a2 = seconds(say(v, f.text, 2).audio);
            check(a0 - a1 > 0.2 && a0 - a1 < 0.7 && a1 - a2 > 0.3 && a2 > 0.5,
                  fmt("%s, read by eSpeak NG: mode 1 shortens the end, mode 2 the rest as well", narrow(f.tag).c_str())
                      .c_str(),
                  fmt("%.2f / %.2f / %.2f s", a0, a1, a2));
            v.release();
        }
        // "Mr." and "Dr." are read by the engine's dictionary as words only with their dot beside them,
        // so those dots keep the engine's own pauses, and the sentence reads as it did.
        {
            const std::wstring t = L"Mr. Smith and Dr. Jones live near the park";
            const double a0 = seconds(say(en, t, 0).audio), a1 = seconds(say(en, t, 1).audio),
                         a2 = seconds(say(en, t, 2).audio);
            check(a0 - a1 > 0.25 && a0 - a1 < 0.6 && std::fabs(a1 - a2) < 0.01,
                  "an abbreviation's dot is left alone: Mr. and Dr. are still Mister and Doctor",
                  fmt("%.3f / %.3f / %.3f s", a0, a1, a2));
        }
        // A lone letter is still read as a letter (not as a word), and a text without a mark is still shortened.
        {
            const double a0 = seconds(say(en, L"a", 0).audio), a2 = seconds(say(en, L"a", 2).audio);
            check(a0 - a2 > 0.3 && a2 > 0.2, "a lone letter is still spoken, without the silence after it",
                  fmt("%.3f s, %.3f s", a0, a2));
        }
        // Backquotes are annotations once the engine honours them, so somebody else's text has them
        // taken out: it says what the same text with a space in place of each says.
        {
            const Run a = say(en, L"Hello `v1 there. Bye `vs250 now.", 2);
            const Run b = say(en, L"Hello  v1 there. Bye  vs250 now.", 2);
            check(a.audio.size() == b.audio.size() && !a.audio.empty(),
                  "a backquote in the text is not an annotation while pauses are shortened",
                  fmt("%zu and %zu samples", a.audio.size(), b.audio.size()));
        }
        // Word and sentence events, and marks, work as they did, and do not change the audio.
        {
            const std::wstring t = L"The quick brown fox, they said. Jumps over the lazy dog!";
            const Run with = say(en, t, 2, true), plain = say(en, t, 2);
            int words = 0, sentences = 0;
            for (const auto& e : with.events) {
                if (e.id == SPEI_WORD_BOUNDARY) ++words;
                if (e.id == SPEI_SENTENCE_BOUNDARY) ++sentences;
            }
            check(words == 11 && sentences == 2 && with.audio.size() == plain.audio.size() && !plain.audio.empty(),
                  "word and sentence events are unchanged, and do not change the audio",
                  fmt("%d words, %d sentences, %zu with, %zu without", words, sentences, with.audio.size(),
                      plain.audio.size()));
        }
        // Spelling has a pace of its own: nothing is added to it, or the annotation would be spelled out.
        {
            write_settings("[General]\r\nLogLevel=1\r\nPauseMode=0\r\n");
            Frags a, b;
            a.spell(L"Hello, ok.");
            b.spell(L"Hello, ok.");
            const Run r0 = speak(en, a);
            write_settings("[General]\r\nLogLevel=1\r\nPauseMode=2\r\n");
            const Run r2 = speak(en, b);
            check(r0.audio.size() == r2.audio.size() && !r0.audio.empty(), "<spell> is not changed by shorter pauses",
                  fmt("%zu and %zu samples", r0.audio.size(), r2.audio.size()));
        }
        write_settings("[General]\r\nLogLevel=1\r\n");
    }

    // ---- prosody ---------------------------------------------------------------------------
    if (want("prosody", only)) {
        printf("rate, pitch and volume\n");
        const wchar_t* t = L"The rate of speech can be changed by the program that is speaking.";
        double len[3];
        const long rates[3] = {-10, 0, 10};
        for (int i = 0; i < 3; ++i) {
            Frags f;
            f.text(t);
            Run r = speak(en, f, [&](MockSite& s) { s.rate = rates[i]; });
            len[i] = seconds(r.audio);
            save(r.audio, L"sapirate_" + std::to_wstring(rates[i]) + L".wav");
        }
        check(len[0] > len[1] * 2.0 && len[1] > len[2] * 3.0, "SAPI rate -10 / 0 / +10",
              fmt("%.2f / %.2f / %.2f s", len[0], len[1], len[2]));
        Frags lo, hi;
        lo.text(t, 0, -10);
        hi.text(t, 0, 10);
        Run rl = speak(en, lo), rh = speak(en, hi);
        const double fl = f0(rl.audio, g_rate_hz), fh = f0(rh.audio, g_rate_hz);
        check(fh > fl * 1.2, "SAPI pitch -10 / +10 (fragment pitch, as NVDA sets it)", fmt("%.0f / %.0f Hz", fl, fh));
        Frags v1, v2;
        v1.text(t, 0, 0, 100);
        v2.text(t, 0, 0, 40);
        Run r1 = speak(en, v1), r2 = speak(en, v2);
        Run r3;
        {
            Frags v3;
            v3.text(t);
            r3 = speak(en, v3, [](MockSite& s) { s.volume = 40; });
        }
        check(rms(r2.audio) < rms(r1.audio) * 0.6, "fragment volume 40%", fmt("rms %.0f / %.0f", rms(r2.audio), rms(r1.audio)));
        check(rms(r3.audio) < rms(r1.audio) * 0.6, "SAPI volume 40%", fmt("rms %.0f / %.0f", rms(r3.audio), rms(r1.audio)));
        // A change in the middle of an utterance, as <rate> and <pitch> tags make.
        Frags mid;
        mid.text(L"One two three four. ", 0).text(L"One two three four.", 10);
        Frags same;
        same.text(L"One two three four. One two three four.");
        Run rm = speak(en, mid), rs = speak(en, same);
        check(seconds(rm.audio) < seconds(rs.audio) * 0.85, "a rate change mid-utterance applies from there on",
              fmt("%.2f s against %.2f s", seconds(rm.audio), seconds(rs.audio)));
    }

    // ---- spelling and single characters ---------------------------------------------------------
    if (want("spell", only)) {
        printf("spelling\n");
        Frags a, b;
        a.spell(L"Hello");
        b.text(L"Hello");
        Run rs = speak(en, a), rt = speak(en, b);
        save(rs.audio, L"spell_hello.wav");
        check(seconds(rs.audio) > seconds(rt.audio) * 1.4, "<spell> spells the letters",
              fmt("%.2f s spelled, %.2f s as a word", seconds(rs.audio), seconds(rt.audio)));
        Frags c;
        c.text(L"-");
        Run rc = speak(en, c);
        check(seconds(rc.audio) > 0.2, "a lone hyphen is named, not silent", fmt("%.2f s", seconds(rc.audio)));
        Voice ja = load_voice(L"jajp", 1);
        if (ja.engine) {
            int silent = 0;
            std::string which;
            for (wchar_t ch : std::wstring(L"!\"#$%'()*+,-./:;<=>?[\\]^_`{|}~")) {
                Frags g;
                g.text(std::wstring(1, ch));
                Run r = speak(ja, g);
                if (seconds(r.audio) < 0.15) {
                    ++silent;
                    which.push_back(static_cast<char>(ch));
                }
            }
            check(silent == 0, "Japanese names every lone ASCII symbol", which);
            ja.release();
        }
        // A language read by eSpeak NG: eSpeak NG spells, and names symbols.
        LanguageInfo ru;
        if (evv::find_language(L"ru", ru)) {
            Voice v = load_voice(L"ru", 1);
            Frags s, w;
            s.spell(L"мама");
            w.text(L"мама");
            Run rs2 = speak(v, s), rw2 = speak(v, w);
            check(seconds(rs2.audio) > seconds(rw2.audio) * 1.4, "eSpeak NG language: <spell> spells the letters",
                  fmt("%.2f s spelled, %.2f s as a word", seconds(rs2.audio), seconds(rw2.audio)));
            int silent = 0;
            std::string which;
            for (wchar_t ch : std::wstring(L"?,-@#%+")) {
                Frags g;
                g.text(std::wstring(1, ch));
                Run r = speak(v, g);
                if (seconds(r.audio) < 0.15) {
                    ++silent;
                    which.push_back(static_cast<char>(ch));
                }
            }
            check(silent == 0, "eSpeak NG language: a lone symbol is named", which);
            v.release();
        }
    }

    // ---- cancelling ----------------------------------------------------------------------------------
    if (want("abort", only)) {
        printf("cancelling\n");
        std::wstring longtext;
        for (int i = 0; i < 20; ++i) longtext += L"This is a long passage of text that goes on for a while. ";
        std::vector<double> stops;
        bool next_ok = true;
        for (int i = 0; i < 10; ++i) {
            Frags f;
            f.text(longtext);
            Run r = speak(en, f, [](MockSite& s) { s.abort_after_ms = 10; });
            stops.push_back(r.abort_to_return_ms);
            Frags g;
            g.text(L"Still speaking after the cancel.");
            Run after = speak(en, g);
            if (seconds(after.audio) < 1.0) next_ok = false;
        }
        std::sort(stops.begin(), stops.end());
        check(stops.back() >= 0 && stops.back() < 60, "Speak() returns promptly after SPVES_ABORT",
              fmt("median %.2f ms, worst %.2f ms", stops[5], stops.back()));
        check(next_ok, "the utterance after each cancel speaks in full");
    }

    // ---- sample rates ------------------------------------------------------------------------------------
    if (want("rates", only)) {
        printf("sample rates\n");
        bool ok = true;
        std::string detail;
        size_t base = 0;
        for (const int hz : {8000, 11025, 16000, 22050, 32000, 44100, 48000}) {
            Frags f;
            f.text(L"Sample rate test.");
            Run r = speak(en, f, nullptr, static_cast<DWORD>(hz));
            if (hz == 11025) base = r.audio.size();
            save(r.audio, L"rate_" + std::to_wstring(hz) + L".wav", hz);
            detail += fmt("%d:%.2fs ", hz, seconds(r.audio, hz));
            if (seconds(r.audio, hz) < 0.8) ok = false;
        }
        check(ok, "every sample rate speaks at the right speed", detail);
        (void)base;
    }

    // ---- settings take effect at once -------------------------------------------------------------------
    if (want("settings", only)) {
        printf("settings\n");
        const wchar_t* t = L"Settings change the voice at once.";
        Frags a;
        a.text(t);
        Run before = speak(en, a);
        write_settings("[General]\r\nLogLevel=1\r\n[Voice.enus.1]\r\nPitch=95\r\nSpeed=120\r\n");
        Frags b;
        b.text(t);
        Run after = speak(en, b);
        const double fb = f0(before.audio, g_rate_hz), fa = f0(after.audio, g_rate_hz);
        check(fa > fb * 1.15 && seconds(after.audio) < seconds(before.audio) * 0.8,
              "a voice changed in the settings file is heard on the next utterance",
              fmt("F0 %.0f -> %.0f Hz, %.2f -> %.2f s", fb, fa, seconds(before.audio), seconds(after.audio)));
        write_settings("[General]\r\nLogLevel=1\r\nResampler=hold\r\n");
        Frags c;
        c.text(t);
        Run held = speak(en, c, nullptr, 22050);
        check(seconds(held.audio, 22050) > 1.0, "a host setting (resampler) restarts the host and still speaks",
              fmt("%.2f s", seconds(held.audio, 22050)));
        write_settings("[General]\r\nLogLevel=1\r\n");
    }

    // ---- a host that dies is replaced ---------------------------------------------------------------------
    if (want("recovery", only)) {
        printf("recovery\n");
        const std::vector<DWORD> pids = host_pids();
        for (DWORD pid : pids) {
            HANDLE p = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
            if (p) {
                TerminateProcess(p, 9);
                CloseHandle(p);
            }
        }
        Sleep(50);
        Frags f;
        f.text(L"Speaking again after the engine host was killed.");
        Run r = speak(en, f);
        check(!pids.empty() && seconds(r.audio) > 1.0, "a killed engine host is replaced and speech continues",
              fmt("%zu hosts killed, %.2f s spoken", pids.size(), seconds(r.audio)));
    }

    en.release();
    printf("\n%d passed, %d failed\n", g_pass, g_fail);
    return g_fail ? 1 : 0;
}
