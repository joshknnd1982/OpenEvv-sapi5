// How a module renders single characters: every printable ASCII character on
// its own, upper and lower case letters, and the engine's spelling mode.
// Finds the characters a screen reader user would hear as silence, and the
// capitals read as Roman numerals.
//
//   evv_chars <module.dll> <language-id>
#include <windows.h>

#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

#include "common/eci_module.h"

using namespace evv;

namespace {

std::vector<short> g_buf(1024);
size_t g_samples = 0;
double g_energy = 0;

int EVV_ECICALL on_message(ECIHand, int msg, int param, void*)
{
    if (msg == kMsgWaveform) {
        for (int i = 0; i < param; ++i) g_energy += static_cast<double>(g_buf[i]) * g_buf[i];
        g_samples += static_cast<size_t>(param);
    }
    return kDataProcessed;
}

struct Result
{
    size_t samples;
    double rms;
};

Result say(EciModule& m, ECIHand h, const std::string& text)
{
    g_samples = 0;
    g_energy = 0;
    m.AddText(h, text.c_str());
    m.Synthesize(h);
    m.Synchronize(h);
    return {g_samples, g_samples ? std::sqrt(g_energy / g_samples) : 0.0};
}

} // namespace

int wmain(int argc, wchar_t** argv)
{
    if (argc < 3) return 2;
    EciModule m;
    std::string err;
    if (!m.load(argv[1], err)) {
        printf("%s\n", err.c_str());
        return 1;
    }
    ECIHand h = m.NewEx(static_cast<int>(wcstol(argv[2], nullptr, 0)));
    m.RegisterCallback(h, on_message, nullptr);
    m.SetOutputBuffer(h, 1024, g_buf.data());
    m.SetParam(h, kParamSynthMode, 1);
    m.SetParam(h, kParamInputType, 0);
    say(m, h, "warm up.");

    printf("silent or near-silent single characters (samples, rms):\n");
    for (int c = 33; c < 127; ++c) {
        const Result r = say(m, h, std::string(1, static_cast<char>(c)));
        if (r.samples < 2500 || r.rms < 300) printf("  '%c' %zu %.0f\n", c, r.samples, r.rms);
    }
    printf("capital vs lower case (samples):\n");
    for (char c = 'A'; c <= 'Z'; ++c) {
        const Result up = say(m, h, std::string(1, c));
        const Result lo = say(m, h, std::string(1, static_cast<char>(c + 32)));
        const double ratio = lo.samples ? static_cast<double>(up.samples) / lo.samples : 0;
        printf("  %c %zu / %c %zu = %.2f%s\n", c, up.samples, c + 32, lo.samples, ratio, ratio > 1.25 ? "  <-- expanded" : "");
    }
    printf("spelling:\n");
    for (int mode = 0; mode <= 3; ++mode) {
        m.SetParam(h, kParamTextMode, mode);
        const Result r = say(m, h, "abc hello 12");
        printf("  text mode %d: \"abc hello 12\" %zu samples\n", mode, r.samples);
    }
    m.SetParam(h, kParamTextMode, 0);
    // Text mode changed between two stretches of one utterance.
    const Result plain = say(m, h, "hello hello");
    m.AddText(h, "hello ");
    m.SetParam(h, kParamTextMode, 2);
    const Result mixed = say(m, h, "hello");
    m.SetParam(h, kParamTextMode, 0);
    printf("  \"hello hello\" plain %zu; second word in text mode 2 within one utterance %zu\n", plain.samples,
           mixed.samples);
    const Result spaced = say(m, h, "h e l l o");
    printf("  \"h e l l o\" %zu\n", spaced.samples);
    // A backquote with annotations off and on.
    const Result bq0 = say(m, h, "`");
    m.SetParam(h, kParamInputType, 1);
    const Result bq1 = say(m, h, "a `vs200 b");
    m.SetParam(h, kParamInputType, 0);
    const Result bq2 = say(m, h, "a `vs200 b");
    printf("backquote alone (annotations off) %zu; \"a `vs200 b\" annotations on %zu, off %zu\n", bq0.samples,
           bq1.samples, bq2.samples);
    return 0;
}
