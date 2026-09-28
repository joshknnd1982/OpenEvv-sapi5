// The language packs on this machine.
//
// A pack is a folder holding language.ini and the language's engine modules:
//
//   languages\enus\language.ini
//   languages\enus\openevv-enus-x86.dll
//   languages\enus\openevv-enus-x64.dll
//   languages\enus\dict\main.dic, root.dic, abbr.dic   (optional)
//
// Adding a language is dropping a folder in, removing one is deleting it: the
// SAPI voice list is built from whatever packs are present each time an
// application asks for it, so nothing has to be registered. docs/LANGUAGES.md
// describes the format.
#pragma once

#include <string>
#include <vector>

namespace evv {

struct PresetVoice
{
    int number = 0;              // 1..8, the engine's own preset
    std::wstring name;           // "Adult Male 1"
    std::wstring gender;         // "Male" / "Female"
    std::wstring age;            // "Adult" / "Child" / "Senior"
    int params[8] = {-1, -1, -1, -1, -1, -1, -1, -1}; // engine values, -1 unknown
};

struct LanguageInfo
{
    std::wstring tag;            // "enus"
    std::wstring name;           // "US English"
    std::wstring locale;         // "en-US"
    std::wstring lcid;           // SAPI Language attribute, hex, e.g. "409"
    unsigned id = 0;             // ECI language, e.g. 0x00010000
    unsigned codepage = 1252;    // how text is handed to the engine
    bool experimental = false;
    int order = 1000;
    std::wstring dir;            // the pack folder
    std::wstring module32, module64; // full paths ("" if the pack lacks one)
    std::vector<PresetVoice> voices; // the eight presets

    // The module this process would load a host for.
    const std::wstring& module_for_this_bitness() const;
    const std::wstring& module_for(bool x64) const { return x64 ? module64 : module32; }
    bool usable() const;
};

// Reads every pack. Packs in the user's drop-in folder win over shipped packs
// with the same tag. Sorted by Order, then name. Problems (a pack with no
// module, an unreadable ini) are reported in `problems` and the pack skipped.
std::vector<LanguageInfo> scan_languages(std::vector<std::wstring>* problems = nullptr);

// One pack by tag, from a fresh scan.
bool find_language(const std::wstring& tag, LanguageInfo& out);

// Reads one pack folder.
bool read_language_pack(const std::wstring& dir, LanguageInfo& out, std::wstring& problem);

// The standard preset names, genders and ages, used when a pack lists none.
PresetVoice default_preset(int number);

} // namespace evv
