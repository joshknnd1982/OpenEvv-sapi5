#include "selftest.h"

#include <windows.h>
#include <sapi.h>

#include <cstdio>

#include "common/host_client.h"
#include "common/languages.h"
#include "common/log.h"
#include "common/paths.h"
#include "common/render.h"
#include "common/settings.h"

namespace evv {

namespace {

bool host_present(bool x64)
{
    const bool self64 = sizeof(void*) == 8;
    if (x64 == self64) return file_exists(host_exe_path());
    std::wstring dir = self_dir();
    dir.resize(dir.find_last_of(L"\\/"));
    return file_exists(dir + (x64 ? L"\\x64" : L"\\x86") + L"\\OpenEvvHost.exe");
}

bool windows_is_64bit()
{
#if defined(_WIN64)
    return true;
#else
    BOOL wow = FALSE;
    IsWow64Process(GetCurrentProcess(), &wow);
    return wow != FALSE;
#endif
}

// A short sentence in each language's own words; digits say the most.
std::wstring sample_text(const LanguageInfo& l)
{
    const std::wstring t = l.tag.substr(0, 2);
    if (t == L"de") return L"Guten Tag. Eins, zwei, drei.";
    if (t == L"es") return L"Hola. Uno, dos, tres.";
    if (t == L"fr") return L"Bonjour. Un, deux, trois.";
    if (t == L"it") return L"Buongiorno. Uno, due, tre.";
    if (t == L"pl") return L"Dzień dobry. Jeden, dwa, trzy.";
    if (t == L"ja") return L"こんにちは。一、二、三。";
    return L"Hello. One, two, three.";
}

// Through SAPI itself: the voices it lists, and one of them speaking into
// memory through SpVoice, exactly as a screen reader would use it.
std::wstring sapi_check(size_t expected_voices, int& failures)
{
    const wchar_t* bits = sizeof(void*) == 8 ? L"64-bit" : L"32-bit";
    wchar_t line[400];
    ISpObjectTokenCategory* cat = nullptr;
    IEnumSpObjectTokens* en = nullptr;
    ULONG count = 0;
    if (FAILED(CoCreateInstance(CLSID_SpObjectTokenCategory, nullptr, CLSCTX_ALL, IID_PPV_ARGS(&cat))) ||
        FAILED(cat->SetId(SPCAT_VOICES, FALSE)) || FAILED(cat->EnumTokens(L"Vendor=OpenEVV", nullptr, &en)) || !en) {
        if (cat) cat->Release();
        ++failures;
        swprintf_s(line, L"SAPI, %s programs: the voice list could not be read.\r\n", bits);
        return line;
    }
    en->GetCount(&count);
    ISpObjectToken* token = nullptr;
    if (count) en->Item(0, &token);
    en->Release();
    cat->Release();
    double seconds = 0;
    HRESULT hr = E_FAIL;
    if (token) {
        ISpVoice* voice = nullptr;
        ISpStream* stream = nullptr;
        IStream* mem = nullptr;
        if (SUCCEEDED(CoCreateInstance(CLSID_SpVoice, nullptr, CLSCTX_ALL, IID_PPV_ARGS(&voice))) &&
            SUCCEEDED(CoCreateInstance(CLSID_SpStream, nullptr, CLSCTX_ALL, IID_PPV_ARGS(&stream))) &&
            SUCCEEDED(CreateStreamOnHGlobal(nullptr, TRUE, &mem))) {
            WAVEFORMATEX wfx{WAVE_FORMAT_PCM, 1, 11025, 22050, 2, 16, 0};
            if (SUCCEEDED(stream->SetBaseStream(mem, SPDFID_WaveFormatEx, &wfx)) &&
                SUCCEEDED(voice->SetVoice(token)) && SUCCEEDED(voice->SetOutput(stream, TRUE))) {
                hr = voice->Speak(L"Testing the OpenEVV voices through SAPI five.", SPF_DEFAULT, nullptr);
                STATSTG st{};
                if (SUCCEEDED(mem->Stat(&st, STATFLAG_NONAME))) seconds = st.cbSize.QuadPart / 22050.0;
            }
        }
        if (voice) voice->Release();
        if (stream) stream->Release();
        if (mem) mem->Release();
        token->Release();
    }
    const bool ok = count == expected_voices && SUCCEEDED(hr) && seconds > 1.0;
    if (!ok) ++failures;
    swprintf_s(line, L"SAPI, %s programs: %lu OpenEVV voices listed (%zu expected); the first spoke %.1f seconds%s.\r\n",
               bits, count, expected_voices, seconds, ok ? L"" : L" - PROBLEM");
    return line;
}

} // namespace

SelfTestResult run_selftest(bool hosts, bool sapi, const std::function<void(const std::wstring&)>& progress)
{
    SelfTestResult r;
    const HRESULT co = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    Settings s = load_settings();
    // Every voice as the engine ships it, whatever the user has changed.
    s.voices.clear();
    std::vector<std::wstring> problems;
    const std::vector<LanguageInfo> langs = scan_languages(&problems);
    size_t voices = 0;
    for (const LanguageInfo& l : langs) voices += l.voices.size();
    HostPool::get().add_user();
    for (const std::wstring& p : problems) {
        r.report += L"Problem: " + p + L"\r\n";
        ++r.failures;
    }
    if (langs.empty()) {
        r.report += L"No language packs were found.\r\n";
        ++r.failures;
    }
    int bitnesses = 0;
    for (const LanguageInfo& l : hosts ? langs : std::vector<LanguageInfo>{}) {
        for (const int bits : {1, 0}) {
            const bool x64 = bits == 1;
            if (l.module_for(x64).empty()) continue;
            if (x64 && !windows_is_64bit()) continue;
            if (!host_present(x64)) continue;
            if (progress) progress(l.name + (x64 ? L", 64-bit" : L", 32-bit"));
            int ok = 0;
            std::string last_error;
            for (int preset = 1; preset <= 8; ++preset) {
                ++r.tried;
                const RenderResult rr = render_voice(l, preset, s, sample_text(l), bits);
                const double secs = rr.samples.size() / static_cast<double>(rr.sample_rate_hz);
                if (rr.ok() && secs > 0.5) {
                    ++ok;
                    ++r.spoken;
                } else {
                    ++r.failures;
                    last_error = rr.ok() ? "no audio" : rr.error;
                }
            }
            wchar_t line[400];
            swprintf_s(line, L"%s, %s engine: %d of 8 voices speak%s%S\r\n", l.name.c_str(),
                       x64 ? L"64-bit" : L"32-bit", ok, ok == 8 ? L"" : L" - ", ok == 8 ? "" : last_error.c_str());
            r.report += line;
            log::write(log::kStandard, "selftest: %S", line);
            bitnesses |= x64 ? 2 : 1;
        }
        // Each language's hosts are finished with; do not keep twenty.
        HostPool::get().shutdown_all();
    }
    std::wstring sapi_line;
    if (sapi) {
        if (progress) progress(L"SAPI");
        sapi_line = sapi_check(voices, r.failures);
        r.report += sapi_line;
        log::write(log::kStandard, "selftest: %S", sapi_line.c_str());
        HostPool::get().shutdown_all();
    }
    HostPool::get().release_user();
    std::wstring summary = L"RESULT: ";
    if (hosts) {
        wchar_t t[200];
        swprintf_s(t, L"%d of %d voice tests spoke (%s). ", r.spoken, r.tried,
                   bitnesses == 3 ? L"32-bit and 64-bit engines" : (bitnesses == 2 ? L"64-bit engine" : L"32-bit engine"));
        summary += t;
    }
    if (sapi) {
        summary += sapi_line.substr(0, sapi_line.size() - 2) + L" ";
    }
    summary += r.failures == 0 ? L"Everything works." : L"Some problems: see above and the log folder.";
    r.report += summary + L"\r\n";
    if (SUCCEEDED(co)) CoUninitialize();
    return r;
}

} // namespace evv
