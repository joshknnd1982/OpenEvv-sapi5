#include "render.h"

#include <windows.h>

#include <cstdio>

#include "eci_module.h"
#include "host_client.h"
#include "text_codec.h"
#include "voice_math.h"

namespace evv {

namespace {

double now_ms()
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return 1000.0 * static_cast<double>(c.QuadPart) / static_cast<double>(f.QuadPart);
}

} // namespace

RenderResult render_voice(const LanguageInfo& lang, int preset, const Settings& s, const std::wstring& text,
                          int bitness)
{
    RenderResult out;
    out.sample_rate_hz = sample_rate_hz(s.sample_rate);
    RequestBuilder req;
    int voice[8];
    effective_voice(lang, preset, s, voice);
    req.head.sample_rate = s.sample_rate;
    req.head.text_mode = s.text_mode;
    req.head.number_mode = s.number_mode;
    req.head.dictionary = s.abbreviations ? 1 : 0;
    req.head.input_type = s.annotations ? 1 : 0;
    req.head.user_dicts = s.user_dictionaries ? 1 : 0;
    req.head.preset = preset;
    for (int i = 0; i < 8; ++i) req.head.voice[i] = voice[i];
    req.head.voice[kVoiceSpeed] = engine_speed(voice[kVoiceSpeed], 0, s);
    req.text(encode_text(text, lang.codepage));

    const double t0 = now_ms();
    auto utt = HostPool::get().speak(lang, s, req, out.error, nullptr, 10000, bitness);
    if (!utt) return out;
    HostEvent ev;
    for (;;) {
        if (!utt->next(ev, 10000)) {
            utt->abandon();
            out.error = "the engine host stopped answering";
            break;
        }
        if (ev.kind == HostEvent::kAudio) {
            if (out.first_audio_ms < 0) out.first_audio_ms = now_ms() - t0;
            out.samples.insert(out.samples.end(), ev.samples.begin(), ev.samples.end());
        } else if (ev.kind == HostEvent::kDone) {
            if (ev.done.status == proto::kDoneFailed) out.error = ev.done.error[0] ? ev.done.error : "engine failure";
            break;
        }
    }
    out.total_ms = now_ms() - t0;
    return out;
}

bool write_wav(const std::wstring& path, const std::vector<int16_t>& a, int hz)
{
    FILE* f = _wfopen(path.c_str(), L"wb");
    if (!f) return false;
    const uint32_t rate = static_cast<uint32_t>(hz);
    const uint32_t data = static_cast<uint32_t>(a.size() * 2), riff = 36 + data, fmtlen = 16, bps = rate * 2;
    const uint16_t pcm = 1, ch = 1, align = 2, bits = 16;
    fwrite("RIFF", 1, 4, f); fwrite(&riff, 4, 1, f); fwrite("WAVEfmt ", 1, 8, f); fwrite(&fmtlen, 4, 1, f);
    fwrite(&pcm, 2, 1, f); fwrite(&ch, 2, 1, f); fwrite(&rate, 4, 1, f); fwrite(&bps, 4, 1, f);
    fwrite(&align, 2, 1, f); fwrite(&bits, 2, 1, f); fwrite("data", 1, 4, f); fwrite(&data, 4, 1, f);
    fwrite(a.data(), 2, a.size(), f);
    fclose(f);
    return true;
}

} // namespace evv
