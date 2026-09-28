#include "IEnumSpObjectTokensImpl.hpp"

#include <algorithm>
#include <new>
#include <stdexcept>

namespace evv {
namespace sapi {

IEnumSpObjectTokensImpl::IEnumSpObjectTokensImpl(bool initialize)
{
    if (initialize) {
        voices_ = VoiceEntry::all();
    }
}

IEnumSpObjectTokensImpl::ISpObjectTokenPtr IEnumSpObjectTokensImpl::create_token(const VoiceEntry& v) const
{
    // The id a program (NVDA, for one) remembers the voice by.
    const std::wstring token_id = std::wstring(SPCAT_VOICES) + L"\\TokenEnums\\OpenEVV\\" + v.id;
    com::object<voice_token> obj_data_key(v);
    com::interface_ptr<ISpDataKey> int_data_key(obj_data_key);

    ISpObjectTokenInitPtr int_token_init(CLSID_SpObjectToken);
    if (!int_token_init) {
        throw std::runtime_error("Unable to create an object token");
    }
    if (FAILED(int_token_init->InitFromDataKey(SPCAT_VOICES, token_id.c_str(), int_data_key.get(false)))) {
        throw std::runtime_error("Unable to initialize an object token");
    }
    ISpObjectTokenPtr int_token = int_token_init;
    return int_token;
}

STDMETHODIMP IEnumSpObjectTokensImpl::Next(ULONG celt, ISpObjectToken** pelt, ULONG* pceltFetched)
{
    if (celt == 0) {
        return E_INVALIDARG;
    }
    if (!pelt) {
        return E_POINTER;
    }
    if (!pceltFetched && celt > 1) {
        return E_POINTER;
    }
    if (pceltFetched) {
        *pceltFetched = 0;
    }
    try {
        std::vector<ISpObjectTokenPtr> tokens;
        tokens.reserve(celt);
        const std::size_t next_index = (std::min)(index_ + static_cast<std::size_t>(celt), voices_.size());
        for (std::size_t i = index_; i < next_index; ++i) {
            tokens.push_back(create_token(voices_[i]));
        }
        for (std::size_t i = 0; i < tokens.size(); ++i) {
            tokens[i].AddRef();
            pelt[i] = tokens[i].GetInterfacePtr();
        }
        if (pceltFetched) {
            *pceltFetched = static_cast<ULONG>(tokens.size());
        }
        index_ += tokens.size();
        return (tokens.size() == celt) ? S_OK : S_FALSE;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (...) {
        return E_UNEXPECTED;
    }
}

STDMETHODIMP IEnumSpObjectTokensImpl::Skip(ULONG celt)
{
    const std::size_t remaining = voices_.size() - index_;
    const std::size_t skipped = (std::min)(remaining, static_cast<std::size_t>(celt));
    index_ += skipped;
    return (skipped == celt) ? S_OK : S_FALSE;
}

STDMETHODIMP IEnumSpObjectTokensImpl::Reset()
{
    index_ = 0;
    return S_OK;
}

STDMETHODIMP IEnumSpObjectTokensImpl::GetCount(ULONG* pulCount)
{
    if (!pulCount) {
        return E_POINTER;
    }
    *pulCount = static_cast<ULONG>(voices_.size());
    return S_OK;
}

STDMETHODIMP IEnumSpObjectTokensImpl::Item(ULONG Index, ISpObjectToken** ppToken)
{
    if (!ppToken) {
        return E_POINTER;
    }
    *ppToken = nullptr;
    if (Index >= voices_.size()) {
        return SPERR_NO_MORE_ITEMS;
    }
    try {
        ISpObjectTokenPtr int_token = create_token(voices_[Index]);
        int_token.AddRef();
        *ppToken = int_token.GetInterfacePtr();
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (...) {
        return E_UNEXPECTED;
    }
}

STDMETHODIMP IEnumSpObjectTokensImpl::Clone(IEnumSpObjectTokens** ppEnum)
{
    if (!ppEnum) {
        return E_POINTER;
    }
    *ppEnum = nullptr;
    try {
        com::object<IEnumSpObjectTokensImpl> obj(false);
        obj->voices_ = voices_;
        obj->index_ = index_;
        com::interface_ptr<IEnumSpObjectTokens> int_ptr(obj);
        *ppEnum = int_ptr.get();
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (...) {
        return E_UNEXPECTED;
    }
}

} // namespace sapi
} // namespace evv
