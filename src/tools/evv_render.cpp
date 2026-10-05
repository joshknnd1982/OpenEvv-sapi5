// Speaks a list of cases in one language pack, each into a WAV of its own,
// through the engine host exactly as evv_say does, and then ends the host
// cleanly. That last step is the point: the host lives in a job that kills it
// when its client leaves (host_client.cpp), and a killed host never flushes
// the frame log the module writes when EVV_KLATT_TAP names a file. Ended this
// way, the host leaves through ExitProcess and the log is complete.
//
//   evv_render [--annotated] <tag> <preset 1-8> <cases.tsv> <outdir> [32|64]
//
// --annotated, for a pack read by eSpeak NG: the cases are already the
// front-end's output (OpenEvvFrontend --text, or --phonemes for eSpeak NG's
// phoneme names), and go to the pack's own module and voices without the
// front-end, as the host would hand them on after translating.
//
// cases.tsv is UTF-8, one case a line: an id, a tab, the text (annotations
// such as `[.1ta] are spoken when the settings say Annotations=1). The tag may
// name a hidden template pack. Blank
// lines and lines starting with # are skipped. Every case is spoken by the
// same host, in order, after its warm-up; for each one a line
//
//   case <id> <samples> <rate>
//
// is printed, so that a reader of the frame log can tell the cases apart.
// The harness in docs/tts-extension/harness drives this.
#include <windows.h>

#include <cstdio>
#include <string>
#include <vector>

#include "common/ini.h"
#include "common/languages.h"
#include "common/render.h"
#include "common/settings.h"
#include "common/host_client.h"

using namespace evv;

namespace {

std::string read_file(const std::wstring& path)
{
    std::string bytes;
    FILE* f = _wfopen(path.c_str(), L"rb");
    if (!f) return bytes;
    char buf[4096];
    size_t n;
    while ((n = fread(buf, 1, sizeof buf, f)) > 0) bytes.append(buf, n);
    fclose(f);
    if (bytes.size() >= 3 && static_cast<unsigned char>(bytes[0]) == 0xEF) bytes.erase(0, 3);
    return bytes;
}

} // namespace

int wmain(int argc, wchar_t** argv)
{
    bool annotated = false;
    if (argc >= 2 && std::wstring(argv[1]) == L"--annotated") {
        annotated = true;
        ++argv;
        --argc;
    }
    if (argc < 5) {
        fprintf(stderr, "usage: evv_render [--annotated] <tag> <preset 1-8> <cases.tsv> <outdir> [32|64]\n");
        return 2;
    }
    // Hidden packs too: a template module (dedx, itix, ...) speaks the
    // annotated text the front-end writes, which is how a sound is measured
    // apart from eSpeak NG's reading of a text.
    LanguageInfo li;
    bool found = false;
    for (auto& l : scan_languages(nullptr, true)) {
        if (_wcsicmp(l.tag.c_str(), argv[1]) == 0) {
            li = std::move(l);
            found = true;
            break;
        }
    }
    if (!found) {
        fprintf(stderr, "no language pack %S\n", argv[1]);
        return 1;
    }
    if (annotated) li.fe_voice.clear(); // the host then speaks the text as it stands
    const int preset = _wtoi(argv[2]);
    const std::string cases = read_file(argv[3]);
    const std::wstring outdir = argv[4];
    int bitness = -1;
    if (argc >= 6) bitness = _wtoi(argv[5]) == 64 ? 1 : 0;
    Settings s = load_settings();
    if (annotated) s.annotations = true;

    int failed = 0;
    size_t pos = 0;
    while (pos < cases.size()) {
        size_t end = cases.find('\n', pos);
        if (end == std::string::npos) end = cases.size();
        std::string line = cases.substr(pos, end - pos);
        pos = end + 1;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty() || line[0] == '#') continue;
        const size_t tab = line.find('\t');
        if (tab == std::string::npos || tab == 0) {
            fprintf(stderr, "no id and tab: %s\n", line.c_str());
            ++failed;
            continue;
        }
        const std::string id = line.substr(0, tab);
        const std::wstring text = utf8_to_wide(line.substr(tab + 1));
        RenderResult r = render_voice(li, preset, s, text, bitness);
        if (!r.ok()) {
            fprintf(stderr, "%s: %s\n", id.c_str(), r.error.c_str());
            ++failed;
            continue;
        }
        if (!write_wav(outdir + L"\\" + utf8_to_wide(id) + L".wav", r.samples, r.sample_rate_hz)) {
            fprintf(stderr, "%s: cannot write the WAV\n", id.c_str());
            ++failed;
            continue;
        }
        printf("case %s %zu %d\n", id.c_str(), r.samples.size(), r.sample_rate_hz);
        fflush(stdout);
    }
    HostPool::get().shutdown_all();
    return failed ? 1 : 0;
}
