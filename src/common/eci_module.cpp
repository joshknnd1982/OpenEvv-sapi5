#include "eci_module.h"

#include <cstdio>

namespace evv {

namespace {

template<typename F>
bool resolve(HMODULE lib, const char* name, F& fn, std::string& missing)
{
    fn = reinterpret_cast<F>(GetProcAddress(lib, name));
    if (!fn) {
        if (!missing.empty()) missing += ", ";
        missing += name;
        return false;
    }
    return true;
}

} // namespace

bool EciModule::load(const std::wstring& module_path, std::string& error)
{
    unload();
    // The module's own folder first for anything it might load beside itself,
    // then the system; never the current directory.
    lib = LoadLibraryExW(module_path.c_str(), nullptr,
                         LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!lib) {
        const DWORD e = GetLastError();
        char b[64];
        snprintf(b, sizeof b, "LoadLibrary failed, error %lu", e);
        error = b;
        return false;
    }
    path = module_path;

    std::string missing;
    resolve(lib, "eciNew", New, missing);
    resolve(lib, "eciNewEx", NewEx, missing);
    resolve(lib, "eciDelete", Delete, missing);
    resolve(lib, "eciGetAvailableLanguages", GetAvailableLanguages, missing);
    resolve(lib, "eciAddText", AddText, missing);
    resolve(lib, "eciInsertIndex", InsertIndex, missing);
    resolve(lib, "eciSynthesize", Synthesize, missing);
    resolve(lib, "eciSynchronize", Synchronize, missing);
    resolve(lib, "eciSpeaking", Speaking, missing);
    resolve(lib, "eciStop", Stop, missing);
    resolve(lib, "eciClearInput", ClearInput, missing);
    resolve(lib, "eciSetOutputBuffer", SetOutputBuffer, missing);
    resolve(lib, "eciRegisterCallback", RegisterCallback, missing);
    resolve(lib, "eciGetParam", GetParam, missing);
    resolve(lib, "eciSetParam", SetParam, missing);
    resolve(lib, "eciCopyVoice", CopyVoice, missing);
    resolve(lib, "eciGetVoiceName", GetVoiceName, missing);
    resolve(lib, "eciGetVoiceParam", GetVoiceParam, missing);
    resolve(lib, "eciSetVoiceParam", SetVoiceParam, missing);
    resolve(lib, "eciVersion", Version, missing);
    // The dictionary calls are optional: a library that lacks them still speaks.
    std::string optional;
    resolve(lib, "eciNewDict", NewDict, optional);
    resolve(lib, "eciSetDict", SetDict, optional);
    resolve(lib, "eciDeleteDict", DeleteDict, optional);
    resolve(lib, "eciLoadDict", LoadDict, optional);

    if (!missing.empty()) {
        error = "not an ECI library; missing " + missing;
        unload();
        return false;
    }
    return true;
}

void EciModule::unload()
{
    if (lib) {
        FreeLibrary(lib);
    }
    *this = EciModule{};
}

} // namespace evv
