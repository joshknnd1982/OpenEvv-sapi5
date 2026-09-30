#include "settings.h"

#include <algorithm>

#include "ini.h"
#include "paths.h"

namespace evv {

const SampleRateInfo kSampleRates[7] = {
    {0, 8000}, {1, 11025}, {3, 16000}, {2, 22050}, {4, 32000}, {5, 44100}, {6, 48000},
};

int sample_rate_hz(int eci_value)
{
    for (const auto& r : kSampleRates) {
        if (r.eci == eci_value) return r.hz;
    }
    return 11025;
}

const wchar_t* const kVoiceParamKeys[8] = {L"Gender",    L"HeadSize",    L"Pitch", L"Inflection",
                                           L"Roughness", L"Breathiness", L"Speed", L"Volume"};
const wchar_t* const kVoiceParamLabels[8] = {L"Gender",    L"Head size",   L"Pitch", L"Inflection",
                                             L"Roughness", L"Breathiness", L"Speed", L"Volume"};
const int kVoiceParamMax[8] = {1, 100, 100, 100, 100, 100, 250, 100};

namespace {

int clampi(int v, int lo, int hi)
{
    return v < lo ? lo : (v > hi ? hi : v);
}

bool valid_resampler(const std::wstring& r)
{
    for (const wchar_t* ok : {L"sinc", L"cubic", L"linear", L"hold", L"none"}) {
        if (_wcsicmp(r.c_str(), ok) == 0) return true;
    }
    return false;
}

} // namespace

std::wstring voice_key(const std::wstring& tag, int preset)
{
    return tag + L"." + std::to_wstring(preset);
}

std::wstring Settings::host_signature() const
{
    return resampler + L"|" + (noise_shaping ? L"1" : L"0") + L"|" + (heteronyms ? L"1" : L"0");
}

Settings load_settings()
{
    Settings s;
    Ini ini;
    if (!ini.load(settings_path())) return s;
    const wchar_t* G = L"General";
    const int rate = ini.get_int(G, L"SampleRate", s.sample_rate);
    s.sample_rate = (rate >= 0 && rate <= 6) ? rate : 1;
    const std::wstring r = ini.get(G, L"Resampler", s.resampler);
    s.resampler = valid_resampler(r) ? r : L"sinc";
    std::transform(s.resampler.begin(), s.resampler.end(), s.resampler.begin(), ::towlower);
    s.noise_shaping = ini.get_bool(G, L"NoiseShaping", s.noise_shaping);
    s.heteronyms = ini.get_bool(G, L"Heteronyms", s.heteronyms);
    s.max_speed = clampi(ini.get_int(G, L"MaxSpeed", s.max_speed), 50, 250);
    s.rate_boost = ini.get_bool(G, L"RateBoost", s.rate_boost);
    s.min_speed = clampi(ini.get_int(G, L"MinSpeed", s.min_speed), 0, 100);
    s.pitch_step = clampi(ini.get_int(G, L"PitchStep", s.pitch_step), 0, 10);
    s.abbreviations = ini.get_bool(G, L"Abbreviations", s.abbreviations);
    s.number_mode = clampi(ini.get_int(G, L"NumberMode", s.number_mode), 0, 1);
    s.text_mode = clampi(ini.get_int(G, L"TextMode", s.text_mode), 0, 3);
    s.annotations = ini.get_bool(G, L"Annotations", s.annotations);
    s.pause_mode = clampi(ini.get_int(G, L"PauseMode", s.pause_mode), 0, 2);
    s.user_dictionaries = ini.get_bool(G, L"UserDictionaries", s.user_dictionaries);
    s.community_dictionary = ini.get_bool(G, L"CommunityDictionary", s.community_dictionary);
    s.spell_lone_symbols = ini.get_bool(G, L"SpellLoneSymbols", s.spell_lone_symbols);
    s.log_level = clampi(ini.get_int(G, L"LogLevel", s.log_level), 0, 2);
    for (const std::wstring& sec : ini.sections()) {
        if (_wcsnicmp(sec.c_str(), L"Voice.", 6) != 0) continue;
        VoiceOverride o;
        for (int i = 0; i < 8; ++i) {
            const std::wstring v = ini.get(sec, kVoiceParamKeys[i]);
            if (v.empty()) continue;
            o.set[i] = true;
            o.value[i] = clampi(_wtoi(v.c_str()), 0, kVoiceParamMax[i]);
        }
        if (o.any()) s.voices[sec.substr(6)] = o;
    }
    return s;
}

bool save_settings(const Settings& s)
{
    Ini ini;
    const wchar_t* G = L"General";
    ini.set_int(G, L"SampleRate", s.sample_rate);
    ini.set(G, L"Resampler", s.resampler);
    ini.set_int(G, L"NoiseShaping", s.noise_shaping);
    ini.set_int(G, L"Heteronyms", s.heteronyms);
    ini.set_int(G, L"MaxSpeed", s.max_speed);
    ini.set_int(G, L"RateBoost", s.rate_boost);
    ini.set_int(G, L"MinSpeed", s.min_speed);
    ini.set_int(G, L"PitchStep", s.pitch_step);
    ini.set_int(G, L"Abbreviations", s.abbreviations);
    ini.set_int(G, L"NumberMode", s.number_mode);
    ini.set_int(G, L"TextMode", s.text_mode);
    ini.set_int(G, L"Annotations", s.annotations);
    ini.set_int(G, L"PauseMode", s.pause_mode);
    ini.set_int(G, L"UserDictionaries", s.user_dictionaries);
    ini.set_int(G, L"CommunityDictionary", s.community_dictionary);
    ini.set_int(G, L"SpellLoneSymbols", s.spell_lone_symbols);
    ini.set_int(G, L"LogLevel", s.log_level);
    for (const auto& [key, o] : s.voices) {
        if (!o.any()) continue;
        for (int i = 0; i < 8; ++i) {
            if (o.set[i]) ini.set_int(L"Voice." + key, kVoiceParamKeys[i], o.value[i]);
        }
    }
    return ini.save(settings_path(),
                    "; OpenEVV SAPI5 settings. Written by OpenEvvConfig.exe; every running\r\n"
                    "; OpenEVV voice re-reads this file before it speaks.\r\n\r\n");
}

bool SettingsWatcher::refresh()
{
    WIN32_FILE_ATTRIBUTE_DATA a{};
    const bool exists = GetFileAttributesExW(settings_path().c_str(), GetFileExInfoStandard, &a) != 0;
    if (loaded_ && exists == existed_ && (!exists || CompareFileTime(&a.ftLastWriteTime, &stamp_) == 0)) {
        return false;
    }
    settings_ = load_settings();
    stamp_ = exists ? a.ftLastWriteTime : FILETIME{};
    existed_ = exists;
    loaded_ = true;
    return true;
}

} // namespace evv
