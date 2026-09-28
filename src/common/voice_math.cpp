#include "voice_math.h"

#include <cmath>

namespace evv {

namespace {

int clampi(int v, int lo, int hi)
{
    return v < lo ? lo : (v > hi ? hi : v);
}

// The engine's own values for its presets, used when a language pack does
// not list them (these are US English's, which the other languages share).
const int kDefaultPresetParams[8][8] = {
    {0, 50, 65, 30, 0, 0, 50, 92},  {1, 50, 81, 30, 0, 50, 50, 100}, {1, 22, 93, 35, 0, 0, 50, 90},
    {0, 89, 52, 43, 0, 0, 50, 93},  {0, 50, 69, 34, 0, 0, 70, 92},   {1, 56, 89, 35, 0, 40, 70, 95},
    {1, 45, 68, 30, 3, 40, 50, 90}, {0, 30, 61, 44, 18, 20, 50, 90},
};

} // namespace

void effective_voice(const LanguageInfo& lang, int preset, const Settings& s, int out[8])
{
    preset = clampi(preset, 1, 8);
    for (int i = 0; i < 8; ++i) out[i] = kDefaultPresetParams[preset - 1][i];
    for (const PresetVoice& v : lang.voices) {
        if (v.number != preset) continue;
        for (int i = 0; i < 8; ++i) {
            if (v.params[i] >= 0) out[i] = v.params[i];
        }
    }
    const auto it = s.voices.find(voice_key(lang.tag, preset));
    if (it != s.voices.end()) {
        for (int i = 0; i < 8; ++i) {
            if (it->second.set[i]) out[i] = it->second.value[i];
        }
    }
}

int engine_speed(int voice_speed, int sapi_rate, const Settings& s)
{
    const int r = clampi(sapi_rate, -10, 10);
    const double base = clampi(voice_speed, 0, 250);
    double speed;
    if (r >= 0) {
        double top = s.rate_boost ? 250.0 : s.max_speed;
        if (top < base) top = base;
        speed = base + (top - base) * r / 10.0;
    } else {
        double bottom = s.min_speed;
        if (bottom > base) bottom = base;
        speed = base + (base - bottom) * r / 10.0;
    }
    return clampi(static_cast<int>(std::lround(speed)), 0, 250);
}

int engine_pitch(int voice_pitch, int sapi_pitch, const Settings& s)
{
    return clampi(voice_pitch + clampi(sapi_pitch, -10, 10) * s.pitch_step, 0, 100);
}

int engine_volume(int voice_volume, unsigned site_volume, unsigned fragment_volume)
{
    const double v = voice_volume * (site_volume > 100 ? 100 : site_volume) / 100.0 *
                     (fragment_volume > 100 ? 100 : fragment_volume) / 100.0;
    return clampi(static_cast<int>(std::lround(v)), 0, 100);
}

} // namespace evv
