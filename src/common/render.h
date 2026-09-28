// Speaking a voice into memory through the engine hosts, the way the SAPI
// engine would at SAPI rate, pitch and volume nought -- for the configuration
// utility's test button, its self-test and the render tool.
#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "languages.h"
#include "settings.h"

namespace evv {

struct RenderResult
{
    std::vector<int16_t> samples;
    int sample_rate_hz = 11025;
    double first_audio_ms = -1; // from the request to the first samples
    double total_ms = 0;
    std::string error;
    bool ok() const { return error.empty(); }
};

// bitness: -1 automatic, 0 the 32-bit engine, 1 the 64-bit one.
RenderResult render_voice(const LanguageInfo& lang, int preset, const Settings& s, const std::wstring& text,
                          int bitness = -1);

bool write_wav(const std::wstring& path, const std::vector<int16_t>& samples, int sample_rate_hz);

} // namespace evv
