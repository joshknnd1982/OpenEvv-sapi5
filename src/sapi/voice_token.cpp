#include "voice_token.hpp"

#include <new>

#include "ISpTTSEngineImpl.hpp"

namespace evv {
namespace sapi {

std::vector<VoiceEntry> VoiceEntry::all()
{
    std::vector<VoiceEntry> out;
    for (const LanguageInfo& lang : scan_languages()) {
        for (const PresetVoice& p : lang.voices) {
            VoiceEntry v;
            v.id = lang.tag + L"-" + std::to_wstring(p.number);
            v.name = L"OpenEVV " + lang.name + L" " + p.name;
            v.tag = lang.tag;
            v.preset = p.number;
            v.gender = p.gender;
            v.age = p.age;
            v.lcid = lang.lcid;
            out.push_back(std::move(v));
        }
    }
    return out;
}

voice_token::voice_token(const VoiceEntry& v)
{
    set(v.name);

    utils::out_ptr<wchar_t> clsid_str(CoTaskMemFree);
    StringFromCLSID(__uuidof(ISpTTSEngineImpl), clsid_str.address());
    set(L"CLSID", clsid_str.get());

    attributes_[L"Name"] = v.name;
    attributes_[L"Vendor"] = L"OpenEVV";
    attributes_[L"Language"] = v.lcid;
    attributes_[L"Gender"] = v.gender;
    attributes_[L"Age"] = v.age;
    // Read back by the engine to know which voice it is.
    attributes_[L"OpenEvvLanguage"] = v.tag;
    attributes_[L"OpenEvvPreset"] = std::to_wstring(v.preset);
}

STDMETHODIMP voice_token::OpenKey(LPCWSTR pszSubKeyName, ISpDataKey** ppSubKey)
{
    if (!pszSubKeyName) {
        return E_INVALIDARG;
    }
    if (!ppSubKey) {
        return E_POINTER;
    }
    *ppSubKey = nullptr;

    try {
        if (_wcsicmp(pszSubKeyName, L"Attributes") != 0) {
            return SPERR_NOT_FOUND;
        }
        com::object<ISpDataKeyImpl> obj;
        for (const auto& [key, value] : attributes_) {
            obj->set(key, value);
        }
        com::interface_ptr<ISpDataKey> int_ptr(obj);
        *ppSubKey = int_ptr.get();
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (...) {
        return E_UNEXPECTED;
    }
}

STDMETHODIMP voice_token::EnumKeys(ULONG Index, LPWSTR* ppszSubKeyName)
{
    if (!ppszSubKeyName) {
        return E_POINTER;
    }
    *ppszSubKeyName = nullptr;
    if (Index > 0) {
        return SPERR_NO_MORE_ITEMS;
    }
    try {
        *ppszSubKeyName = com::strdup(L"Attributes");
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (...) {
        return E_UNEXPECTED;
    }
}

} // namespace sapi
} // namespace evv
