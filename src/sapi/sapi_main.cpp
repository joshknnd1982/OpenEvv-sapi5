#include <new>
#include <string>

#include <sapi.h>

#include "IEnumSpObjectTokensImpl.hpp"
#include "ISpTTSEngineImpl.hpp"
#include "com.hpp"
#include "common/host_client.h"
#include "registry.hpp"

namespace {

HINSTANCE g_dll_handle = nullptr;
evv::com::class_object_factory g_cls_obj_factory;

const wchar_t* const kVoicesPath = L"Software\\Microsoft\\Speech\\Voices";
const wchar_t* const kTokenEnumsPath = L"Software\\Microsoft\\Speech\\Voices\\TokenEnums";
const wchar_t* const kEnumName = L"OpenEVV";

std::wstring clsid_to_string(const GUID& clsid)
{
    wchar_t buf[64];
    StringFromGUID2(clsid, buf, 64);
    return std::wstring(buf);
}

// One enumerator entry makes every language pack's voices appear; SAPI asks
// it for the list each time a program enumerates voices. There are no static
// voice tokens beside it -- SAPI would list every voice twice.
void register_token_enumerator()
{
    using namespace evv::registry;
    key enums_key(HKEY_LOCAL_MACHINE, kTokenEnumsPath, KEY_CREATE_SUB_KEY | KEY_SET_VALUE, true);
    key enum_key(enums_key, kEnumName, KEY_SET_VALUE, true);
    enum_key.set(L"OpenEVV voices");
    enum_key.set(L"CLSID", clsid_to_string(__uuidof(evv::sapi::IEnumSpObjectTokensImpl)));
}

void unregister_token_enumerator() noexcept
{
    using namespace evv::registry;
    try {
        key enums_key(HKEY_LOCAL_MACHINE, kTokenEnumsPath, DELETE | KEY_ENUMERATE_SUB_KEYS | KEY_QUERY_VALUE);
        enums_key.delete_tree(kEnumName);
    } catch (...) {
    }
}

// A default voice left naming one of ours would stop SAPI speaking at all
// once we are gone, so it is cleared wherever it does.
void clear_default_voice(HKEY root) noexcept
{
    HKEY h = nullptr;
    if (RegOpenKeyExW(root, kVoicesPath, 0, KEY_QUERY_VALUE | KEY_SET_VALUE, &h) != ERROR_SUCCESS) return;
    wchar_t value[1024] = {};
    DWORD size = sizeof value - sizeof(wchar_t), type = 0;
    if (RegQueryValueExW(h, L"DefaultTokenId", nullptr, &type, reinterpret_cast<BYTE*>(value), &size) ==
            ERROR_SUCCESS &&
        type == REG_SZ && wcsstr(value, L"\\TokenEnums\\OpenEVV\\")) {
        RegDeleteValueW(h, L"DefaultTokenId");
    }
    RegCloseKey(h);
}

} // namespace

BOOL APIENTRY DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID)
{
    if (dwReason == DLL_PROCESS_ATTACH) {
        g_dll_handle = hInstance;
        DisableThreadLibraryCalls(hInstance);
        evv::HostPool::get().set_module(hInstance);
        try {
            g_cls_obj_factory.register_class<evv::sapi::IEnumSpObjectTokensImpl>();
            g_cls_obj_factory.register_class<evv::sapi::ISpTTSEngineImpl>();
        } catch (...) {
            return FALSE;
        }
    }
    // DLL_PROCESS_DETACH: nothing. At process exit the hosts die with their
    // job; on an ordinary unload DllCanUnloadNow has already said the pool is
    // empty.
    return TRUE;
}

STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, void** ppv)
{
    return g_cls_obj_factory.create(rclsid, riid, ppv);
}

STDAPI DllCanUnloadNow()
{
    return (evv::com::object_counter::is_zero() && !evv::HostPool::get().busy()) ? S_OK : S_FALSE;
}

STDAPI DllRegisterServer()
{
    try {
        evv::com::class_registrar r(g_dll_handle);
        r.register_class<evv::sapi::IEnumSpObjectTokensImpl>();
        r.register_class<evv::sapi::ISpTTSEngineImpl>();
        register_token_enumerator();
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (...) {
        return SELFREG_E_CLASS;
    }
}

STDAPI DllUnregisterServer()
{
    HRESULT hr = S_OK;
    unregister_token_enumerator();
    clear_default_voice(HKEY_LOCAL_MACHINE);
    clear_default_voice(HKEY_CURRENT_USER);
    try {
        evv::com::class_registrar r(g_dll_handle);
        r.unregister_class<evv::sapi::IEnumSpObjectTokensImpl>();
        r.unregister_class<evv::sapi::ISpTTSEngineImpl>();
    } catch (...) {
        hr = SELFREG_E_CLASS;
    }
    return hr;
}
