#pragma once

#include <map>
#include <string>
#include <vector>

#include "ISpDataKeyImpl.hpp"
#include "common/languages.h"

namespace evv {
namespace sapi {

// One SAPI voice: a language pack and one of its eight presets.
struct VoiceEntry
{
    std::wstring id;       // "enus-1", the last part of the token id
    std::wstring name;     // "OpenEVV US English Adult Male 1"
    std::wstring tag;      // "enus"
    int preset = 1;
    std::wstring gender, age, lcid;

    static std::vector<VoiceEntry> all(); // every voice of every pack present
};

class voice_token : public ISpDataKeyImpl
{
public:
    explicit voice_token(const VoiceEntry& v);

    STDMETHOD(OpenKey)(LPCWSTR pszSubKeyName, ISpDataKey** ppSubKey) override;
    STDMETHOD(EnumKeys)(ULONG Index, LPWSTR* ppszSubKeyName) override;

private:
    std::map<std::wstring, std::wstring, str_less> attributes_;
};

} // namespace sapi
} // namespace evv
