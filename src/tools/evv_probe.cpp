// Measures an OpenEVV language module directly through its ECI exports:
// what it reports about itself, how fast it answers, and whether the ways the
// SAPI engine intends to drive it change the audio. No SAPI, no host, no
// registry: this is the module and nothing else.
//
//   evv_probe <module.dll> [language-id]
#include <windows.h>

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "common/eci_module.h"

using namespace evv;

namespace {

double now_ms()
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return 1000.0 * static_cast<double>(c.QuadPart) / static_cast<double>(f.QuadPart);
}

struct Capture
{
    std::vector<short> samples;
    std::vector<std::pair<size_t, int>> marks; // sample position, index value
    short* buffer = nullptr;
    double t_start = 0, t_first = -1;
    int callbacks = 0;
};

int EVV_ECICALL on_message(ECIHand, int msg, int param, void* data)
{
    auto* c = static_cast<Capture*>(data);
    ++c->callbacks;
    if (msg == kMsgWaveform) {
        if (c->t_first < 0) c->t_first = now_ms() - c->t_start;
        c->samples.insert(c->samples.end(), c->buffer, c->buffer + param);
    } else if (msg == kMsgIndex) {
        c->marks.emplace_back(c->samples.size(), param);
    }
    return kDataProcessed;
}

struct Engine
{
    EciModule m;
    ECIHand h = nullptr;
    std::vector<short> buf;
    Capture cap;

    bool open(const std::wstring& path, int lang, int frame)
    {
        std::string err;
        if (!m.load(path, err)) {
            printf("load failed: %s\n", err.c_str());
            return false;
        }
        h = lang ? m.NewEx(lang) : m.New();
        if (!h) {
            printf("eciNew failed\n");
            return false;
        }
        buf.assign(frame, 0);
        cap.buffer = buf.data();
        m.RegisterCallback(h, on_message, &cap);
        if (!m.SetOutputBuffer(h, frame, buf.data())) {
            printf("eciSetOutputBuffer refused\n");
            return false;
        }
        return true;
    }

    void reset_capture()
    {
        cap.samples.clear();
        cap.marks.clear();
        cap.callbacks = 0;
        cap.t_first = -1;
    }

    // Speaks what has been added; returns total wall time in ms.
    double run()
    {
        cap.t_start = now_ms();
        m.Synthesize(h);
        m.Synchronize(h);
        return now_ms() - cap.t_start;
    }
};

std::wstring widen(const char* s)
{
    std::wstring w;
    while (*s) w.push_back(static_cast<unsigned char>(*s++));
    return w;
}

void write_wav(const char* path, const std::vector<short>& s, int rate)
{
    FILE* f = fopen(path, "wb");
    if (!f) return;
    const unsigned bytes = static_cast<unsigned>(s.size() * 2);
    auto u32 = [&](unsigned v) { fwrite(&v, 4, 1, f); };
    auto u16 = [&](unsigned short v) { fwrite(&v, 2, 1, f); };
    fwrite("RIFF", 1, 4, f); u32(36 + bytes); fwrite("WAVEfmt ", 1, 8, f);
    u32(16); u16(1); u16(1); u32(rate); u32(rate * 2); u16(2); u16(16);
    fwrite("data", 1, 4, f); u32(bytes);
    fwrite(s.data(), 2, s.size(), f);
    fclose(f);
}

} // namespace

int wmain(int argc, wchar_t** argv)
{
    if (argc < 2) {
        printf("usage: evv_probe <module.dll> [language-id]\n");
        return 2;
    }
    const std::wstring path = argv[1];
    const int lang = argc > 2 ? static_cast<int>(wcstol(argv[2], nullptr, 0)) : 0;

    double t0 = now_ms();
    Engine e;
    if (!e.open(path, lang, 1024)) return 1;
    printf("load + eciNew: %.1f ms\n", now_ms() - t0);

    char ver[64] = {};
    e.m.Version(ver);
    printf("version: %s\n", ver);
    int n = 0;
    e.m.GetAvailableLanguages(nullptr, &n);
    std::vector<unsigned> langs(n > 0 ? n : 1);
    e.m.GetAvailableLanguages(langs.data(), &n);
    printf("languages:");
    for (int i = 0; i < n; ++i) printf(" 0x%x", langs[i]);
    printf("\nlanguage in force: 0x%x\n", e.m.GetParam(e.h, kParamLanguageDialect));
    for (int p = 0; p <= 10; ++p) printf("param %d = %d\n", p, e.m.GetParam(e.h, p));
    for (int v = 1; v <= 8; ++v) {
        char name[64] = {};
        e.m.GetVoiceName(e.h, v, name);
        printf("voice %d \"%s\":", v, name);
        for (int p = 0; p < kVoiceParamCount; ++p) printf(" %d", e.m.GetVoiceParam(e.h, v, p));
        printf("\n");
    }

    const char* text = "The quick brown fox jumps over the lazy dog. It was 3:45 on May 5th.";
    const char* text2 = "Hello.";

    // First utterance cold, then warm, at several buffer sizes.
    for (int round = 0; round < 3; ++round) {
        e.reset_capture();
        e.m.AddText(e.h, text);
        const double total = e.run();
        const double secs = e.cap.samples.size() / 11025.0;
        printf("round %d: first audio %.2f ms, total %.2f ms, %.2f s audio, x%.0f realtime, %d callbacks\n",
               round, e.cap.t_first, total, secs, secs * 1000.0 / total, e.cap.callbacks);
    }
    for (int round = 0; round < 3; ++round) {
        e.reset_capture();
        e.m.AddText(e.h, text2);
        const double total = e.run();
        printf("short \"Hello.\": first audio %.2f ms, total %.2f ms, %zu samples\n", e.cap.t_first, total,
               e.cap.samples.size());
    }

    // Reference render and marks between words. Each case gets its own
    // instance history: the engine's second utterance is not its first, so
    // every comparison is made on a fresh instance.
    auto fresh = [&](Engine& x) { return x.open(path, lang, 1024); };
    std::vector<short> ref, marked;
    {
        Engine a; if (!fresh(a)) return 1;
        a.m.SetParam(a.h, kParamSynthMode, 1);
        a.m.AddText(a.h, text); a.run(); ref = a.cap.samples;
    }
    {
        Engine b; if (!fresh(b)) return 1;
        b.m.SetParam(b.h, kParamSynthMode, 1);
        // text split at every space, with a mark before each word
        std::string s = text;
        size_t pos = 0; int k = 1;
        while (pos < s.size()) {
            size_t sp = s.find(' ', pos);
            std::string piece = s.substr(pos, sp == std::string::npos ? std::string::npos : sp - pos + 1);
            b.m.InsertIndex(b.h, k++);
            b.m.AddText(b.h, piece.c_str());
            pos = sp == std::string::npos ? s.size() : sp + 1;
        }
        b.run(); marked = b.cap.samples;
        printf("marks between words: %zu samples vs %zu reference, %s, %zu marks back\n", marked.size(), ref.size(),
               marked == ref ? "IDENTICAL" : "DIFFERENT", b.cap.marks.size());
        for (auto& mk : b.cap.marks) printf(" [%d@%zu]", mk.second, mk.first);
        printf("\n");
    }
    // UTF-16 input: the same text as wide characters with the code set bit.
    if (lang) {
        Engine c; if (!fresh(c)) return 1;
        c.m.SetParam(c.h, kParamSynthMode, 1);
        const int r = c.m.SetParam(c.h, kParamLanguageDialect, lang | kUnicodeCodeSet);
        std::wstring w = widen(text);
        c.m.AddText(c.h, w.c_str()); c.run();
        printf("UTF-16 input (set answered %d): %zu samples, %s\n", r, c.cap.samples.size(),
               c.cap.samples == ref ? "IDENTICAL to bytes" : "DIFFERENT from bytes");
    }
    // Queued prosody: speed changed between two stretches in synth mode 1.
    {
        Engine d; if (!fresh(d)) return 1;
        d.m.SetParam(d.h, kParamSynthMode, 1);
        d.m.AddText(d.h, "One two three four five. ");
        d.m.SetVoiceParam(d.h, 0, kVoiceSpeed, 150);
        d.m.AddText(d.h, "One two three four five.");
        d.run();
        Engine d2; if (!fresh(d2)) return 1;
        d2.m.SetParam(d2.h, kParamSynthMode, 1);
        d2.m.AddText(d2.h, "One two three four five. One two three four five.");
        d2.run();
        printf("queued speed change: %zu samples vs %zu unchanged (shorter means it applied mid-utterance)\n",
               d.cap.samples.size(), d2.cap.samples.size());
        write_wav("probe_speed_change.wav", d.cap.samples, 11025);
    }
    // Sample rates.
    for (int rate : {0, 1, 3, 2, 4, 5, 6}) {
        Engine r; if (!fresh(r)) return 1;
        const int old = r.m.SetParam(r.h, kParamSampleRate, rate);
        r.m.AddText(r.h, text2); r.run();
        printf("sample rate %d (set answered %d, reads %d): %zu samples\n", rate, old, r.m.GetParam(r.h, kParamSampleRate),
               r.cap.samples.size());
    }
    return 0;
}
