// Per-user settings, in %APPDATA%\OpenEVV\settings.ini.
//
// The configuration utility writes the file on every change and every SAPI
// engine checks its timestamp before each utterance, so a change is heard on
// the next thing spoken, in every program, with nothing restarted.
//
// [General] holds what applies to every voice. [Voice.<tag>.<n>] holds a
// voice's own parameters where the user has changed them from the engine's
// preset; a key that is missing means "the preset's value".
#pragma once

#include <map>
#include <string>
#include <windows.h>

namespace evv {

// The engine's sample rates by its own numbers, in the order a person thinks
// of them.
struct SampleRateInfo
{
    int eci;
    int hz;
};
extern const SampleRateInfo kSampleRates[7];
int sample_rate_hz(int eci_value);

struct VoiceOverride
{
    bool set[8] = {};
    int value[8] = {};
    bool any() const
    {
        for (bool b : set) if (b) return true;
        return false;
    }
};

struct Settings
{
    // What the engine runs at: eciSampleRate 0..6 (8000, 11025, 22050, 16000,
    // 32000, 44100, 48000). Above 11025 the engine runs at 11025 and raises it.
    int sample_rate = 1;
    // How a rate above 11025 is reached: sinc, cubic, linear, hold, or none
    // (synthesise at that rate outright). Read by a host when it starts.
    std::wstring resampler = L"sinc";
    // Band-limit the noise source when synthesising above 11025 outright.
    bool noise_shaping = true;
    // English heteronym fixes (upstream's EVV_HETERO filter).
    bool heteronyms = false;
    // SAPI rate +10 reaches this engine speed (the engine takes 0..250).
    int max_speed = 156;
    bool rate_boost = false;      // +10 reaches 250 instead
    int min_speed = 0;            // SAPI rate -10 reaches this engine speed
    int pitch_step = 4;           // engine pitch units per SAPI pitch step
    bool abbreviations = true;    // the engine's abbreviation dictionary
    int number_mode = 1;          // eciNumberMode
    int text_mode = 0;            // eciTextMode 0..3
    bool annotations = false;     // honour `backquote tags in the text
    bool user_dictionaries = true;
    bool spell_lone_symbols = true; // name a lone punctuation character instead of silence
    int log_level = 1;
    std::map<std::wstring, VoiceOverride> voices; // key "enus.1"

    // What a host has to be started with; hosts started under different
    // values are replaced.
    std::wstring host_signature() const;
};

Settings load_settings();
bool save_settings(const Settings& s);
std::wstring voice_key(const std::wstring& tag, int preset);

// Re-reads the file when its timestamp changes. Cheap enough for every
// utterance: one attribute query.
class SettingsWatcher
{
public:
    // True when the settings changed since the last call (the first call is
    // always true).
    bool refresh();
    const Settings& get() const { return settings_; }

private:
    Settings settings_;
    FILETIME stamp_{};
    bool loaded_ = false;
    bool existed_ = false;
};

extern const wchar_t* const kVoiceParamKeys[8];
extern const wchar_t* const kVoiceParamLabels[8];
extern const int kVoiceParamMax[8];

} // namespace evv
