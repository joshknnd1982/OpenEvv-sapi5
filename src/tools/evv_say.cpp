// Speaks a text in one language pack through the engine hosts, the way the
// configuration utility's Speak button does, and writes the audio to a WAV.
// Every kind of pack goes the same way, a module of its own or one read by
// eSpeak NG, so this is what samples/ and the eSpeak NG packs' checks use.
//
//   evv_say [--spell] <tag> <preset 1-8> <text | @file.txt> <out.wav> [32|64]
//   evv_say --list
//
// --spell has the text spelled, every character by its name, as a screen
// reader's spell command has it through SAPI (the engine's text mode 2:
// letters, digits and punctuation, each by its name).
#include <windows.h>

#include <cstdio>
#include <string>

#include "common/ini.h"
#include "common/languages.h"
#include "common/render.h"
#include "common/settings.h"

using namespace evv;

namespace {

std::wstring read_utf8_file(const std::wstring& path)
{
    HANDLE f = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
    if (f == INVALID_HANDLE_VALUE) return {};
    LARGE_INTEGER size{};
    GetFileSizeEx(f, &size);
    std::string bytes(static_cast<size_t>(size.QuadPart), '\0');
    DWORD got = 0;
    if (!bytes.empty()) ReadFile(f, bytes.data(), static_cast<DWORD>(bytes.size()), &got, nullptr);
    CloseHandle(f);
    bytes.resize(got);
    if (bytes.size() >= 3 && static_cast<unsigned char>(bytes[0]) == 0xEF) bytes.erase(0, 3);
    return utf8_to_wide(bytes);
}

} // namespace

int wmain(int argc, wchar_t** argv)
{
    if (argc >= 2 && std::wstring(argv[1]) == L"--list") {
        std::vector<std::wstring> problems;
        for (const LanguageInfo& li : scan_languages(&problems)) {
            printf("%-20S %-40S %s%S\n", li.tag.c_str(), li.name.c_str(), li.has_frontend() ? "eSpeak NG via " : "",
                   li.has_frontend() ? li.template_tag.c_str() : L"");
        }
        for (const std::wstring& p : problems) printf("problem: %S\n", p.c_str());
        return 0;
    }
    bool spell = false;
    if (argc >= 2 && std::wstring(argv[1]) == L"--spell") {
        spell = true;
        ++argv;
        --argc;
    }
    if (argc < 5) {
        fprintf(stderr, "usage: evv_say [--spell] <tag> <preset 1-8> <text | @file> <out.wav> [32|64]\n");
        return 2;
    }
    LanguageInfo li;
    if (!find_language(argv[1], li)) {
        fprintf(stderr, "no language pack %S\n", argv[1]);
        return 1;
    }
    const int preset = _wtoi(argv[2]);
    std::wstring text = argv[3];
    if (!text.empty() && text[0] == L'@') text = read_utf8_file(text.substr(1));
    int bitness = -1;
    if (argc >= 6) bitness = _wtoi(argv[5]) == 64 ? 1 : 0;
    Settings s = load_settings();
    if (spell) s.text_mode = 2;
    RenderResult r = render_voice(li, preset, s, text, bitness);
    if (!r.ok()) {
        fprintf(stderr, "%S: %s\n", argv[1], r.error.c_str());
        return 1;
    }
    if (!write_wav(argv[4], r.samples, r.sample_rate_hz)) {
        fprintf(stderr, "cannot write %S\n", argv[4]);
        return 1;
    }
    printf("%S: %zu samples at %d Hz, first audio %.1f ms, %.1f ms in all\n", argv[1], r.samples.size(),
           r.sample_rate_hz, r.first_audio_ms, r.total_ms);
    return 0;
}
