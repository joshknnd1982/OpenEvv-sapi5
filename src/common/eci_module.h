// An OpenEVV language module, loaded by path and called through the names IBM
// published for its ECI interface.
//
// A module is the whole engine plus one language, built by upstream's
// Makefile as eci.dll / eci32.dll and renamed openevv-<tag>-x64.dll /
// openevv-<tag>-x86.dll. Nothing is linked against it: every entry point is
// looked up by name, which is also what lets any ECI-compatible library stand
// in as a module. On x86 the interface is stdcall with undecorated names;
// on x64 there is one convention.
#pragma once

#include <windows.h>
#include <string>

namespace evv {

#if defined(_WIN64)
#define EVV_ECICALL
#else
#define EVV_ECICALL __stdcall
#endif

using ECIHand = void*;
using ECIDictHand = void*;

enum EciMessage : int
{
    kMsgWaveform = 0,
    kMsgPhoneme = 1,
    kMsgIndex = 2,
};

enum EciReturn : int
{
    kDataNotProcessed = 0,
    kDataProcessed = 1,
    kDataAbort = 2,
};

// Engine parameters, by IBM's numbers.
enum EciParam : int
{
    kParamSynthMode = 0,
    kParamInputType = 1,
    kParamTextMode = 2,
    kParamDictionary = 3, // 1 turns the dictionary OFF
    kParamSampleRate = 5,
    kParamRealWorldUnits = 8,
    kParamLanguageDialect = 9,
    kParamNumberMode = 10,
};

// A voice's parameters.
enum EciVoiceParam : int
{
    kVoiceGender = 0,
    kVoiceHeadSize = 1,
    kVoicePitchBaseline = 2,
    kVoicePitchFluctuation = 3,
    kVoiceRoughness = 4,
    kVoiceBreathiness = 5,
    kVoiceSpeed = 6,
    kVoiceVolume = 7,
    kVoiceParamCount = 8,
};

constexpr int kUnicodeCodeSet = 0x800;
constexpr int kMainDict = 0, kRootDict = 1, kAbbvDict = 2;

using EciCallback = int(EVV_ECICALL*)(ECIHand, int msg, int param, void* data);

struct EciModule
{
    HMODULE lib = nullptr;
    std::wstring path;

    ECIHand(EVV_ECICALL* New)() = nullptr;
    ECIHand(EVV_ECICALL* NewEx)(int language) = nullptr;
    ECIHand(EVV_ECICALL* Delete)(ECIHand) = nullptr;
    int(EVV_ECICALL* GetAvailableLanguages)(unsigned int* langs, int* count) = nullptr;
    int(EVV_ECICALL* AddText)(ECIHand, const void* text) = nullptr;
    int(EVV_ECICALL* InsertIndex)(ECIHand, int index) = nullptr;
    int(EVV_ECICALL* Synthesize)(ECIHand) = nullptr;
    int(EVV_ECICALL* Synchronize)(ECIHand) = nullptr;
    int(EVV_ECICALL* Speaking)(ECIHand) = nullptr;
    int(EVV_ECICALL* Stop)(ECIHand) = nullptr;
    int(EVV_ECICALL* ClearInput)(ECIHand) = nullptr;
    int(EVV_ECICALL* SetOutputBuffer)(ECIHand, int samples, short* buffer) = nullptr;
    void(EVV_ECICALL* RegisterCallback)(ECIHand, EciCallback, void* data) = nullptr;
    int(EVV_ECICALL* GetParam)(ECIHand, int which) = nullptr;
    int(EVV_ECICALL* SetParam)(ECIHand, int which, int value) = nullptr;
    int(EVV_ECICALL* CopyVoice)(ECIHand, int from, int to) = nullptr;
    int(EVV_ECICALL* GetVoiceName)(ECIHand, int voice, void* name) = nullptr;
    int(EVV_ECICALL* GetVoiceParam)(ECIHand, int voice, int which) = nullptr;
    int(EVV_ECICALL* SetVoiceParam)(ECIHand, int voice, int which, int value) = nullptr;
    void(EVV_ECICALL* Version)(char* buffer) = nullptr;
    ECIDictHand(EVV_ECICALL* NewDict)(ECIHand) = nullptr;
    int(EVV_ECICALL* SetDict)(ECIHand, ECIDictHand) = nullptr;
    ECIDictHand(EVV_ECICALL* DeleteDict)(ECIHand, ECIDictHand) = nullptr;
    int(EVV_ECICALL* LoadDict)(ECIHand, ECIDictHand, int volume, const void* filename) = nullptr;

    // Loads the library and resolves every name above. On failure the reason
    // is in error and nothing stays loaded.
    bool load(const std::wstring& module_path, std::string& error);
    void unload();
};

} // namespace evv
