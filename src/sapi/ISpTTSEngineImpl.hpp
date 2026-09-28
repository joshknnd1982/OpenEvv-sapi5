#pragma once

#include <windows.h>
#include <sapi.h>
#include <sapiddk.h>
#include <sperror.h>
#include <comdef.h>
#include <comip.h>

#include <string>

#include "com.hpp"
#include "common/languages.h"
#include "common/settings.h"

namespace evv {
namespace sapi {

class __declspec(uuid("f3cc6ab4-c4c4-4ec6-aa1f-1a114367ae91")) ISpTTSEngineImpl : public ISpTTSEngine,
                                                                                   public ISpObjectWithToken
{
public:
    ISpTTSEngineImpl();
    ~ISpTTSEngineImpl();

    ISpTTSEngineImpl(const ISpTTSEngineImpl&) = delete;
    ISpTTSEngineImpl& operator=(const ISpTTSEngineImpl&) = delete;

    STDMETHOD(Speak)(DWORD dwSpeakFlags, REFGUID rguidFormatId, const WAVEFORMATEX* pWaveFormatEx,
                     const SPVTEXTFRAG* pTextFragList, ISpTTSEngineSite* pOutputSite) override;
    STDMETHOD(GetOutputFormat)(const GUID* pTargetFmtId, const WAVEFORMATEX* pTargetWaveFormatEx,
                               GUID* pOutputFormatId, WAVEFORMATEX** ppCoMemOutputWaveFormatEx) override;

    STDMETHOD(SetObjectToken)(ISpObjectToken* pToken) override;
    STDMETHOD(GetObjectToken)(ISpObjectToken** ppToken) override;

    static const wchar_t* class_description() { return L"OpenEVV SAPI5 text-to-speech engine"; }

protected:
    [[nodiscard]] void* get_interface(REFIID riid) noexcept
    {
        void* ptr = com::try_primary_interface<ISpTTSEngine>(this, riid);
        return ptr ? ptr : com::try_interface<ISpObjectWithToken>(this, riid);
    }

private:
    _COM_SMARTPTR_TYPEDEF(ISpObjectToken, __uuidof(ISpObjectToken));
    _COM_SMARTPTR_TYPEDEF(ISpDataKey, __uuidof(ISpDataKey));

    const Settings& current_settings();

    ISpObjectTokenPtr token_;
    LanguageInfo lang_;
    bool have_lang_ = false;
    int preset_ = 1;
    std::string voice_name_;
    SettingsWatcher settings_;
    unsigned long utterances_ = 0;
};

} // namespace sapi
} // namespace evv
