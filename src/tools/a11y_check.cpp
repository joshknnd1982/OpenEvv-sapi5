// a11y_check: what a screen reader sees in OpenEvvConfig.exe.
//
//   a11y_check PATH\OpenEvvConfig.exe
//
// Starts the utility on a private, invisible desktop (nothing appears in front
// of the user or takes the screen reader's focus), switches through every page
// of the property sheet, walks the tab order and prints each control's MSAA
// name, role, value and keyboard shortcut. Fails when a tab stop has no name
// or two controls on one page claim the same access key. Then changes a voice
// parameter and a speech setting the way the keyboard would and checks that
// the settings file follows at once. Works on a scratch settings file
// (OPENEVV_SETTINGS).
#include <windows.h>
#include <commctrl.h>
#include <oleacc.h>

#include <cstdio>
#include <fstream>
#include <map>
#include <sstream>
#include <string>

namespace {

const wchar_t kDesktop[] = L"OpenEVV_a11y_check";
const wchar_t kTitle[] = L"OpenEVV SAPI5 Configuration";

std::wstring bstr(BSTR b)
{
    std::wstring s = b ? std::wstring(b, SysStringLen(b)) : std::wstring();
    SysFreeString(b);
    return s;
}

std::string narrow(const std::wstring& w)
{
    std::string s;
    for (wchar_t c : w) s.push_back(c < 128 ? static_cast<char>(c) : '?');
    return s;
}

std::string read_file(const std::wstring& p)
{
    std::ifstream f(p, std::ios::binary);
    std::stringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

int walk(HWND sheet, const char* page_name)
{
    int failures = 0, n = 0;
    std::map<wchar_t, std::wstring> keys;
    printf("page \"%s\":\n", page_name);
    HWND first = GetNextDlgTabItem(sheet, nullptr, FALSE);
    HWND c = first;
    do {
        IAccessible* acc = nullptr;
        if (FAILED(AccessibleObjectFromWindow(c, static_cast<DWORD>(OBJID_CLIENT), IID_IAccessible,
                                              reinterpret_cast<void**>(&acc)))) {
            printf("  %2d  (no IAccessible)\n", ++n);
            ++failures;
        } else {
            VARIANT self;
            self.vt = VT_I4;
            self.lVal = CHILDID_SELF;
            BSTR b = nullptr;
            // one call per statement: arguments are evaluated right to left
            acc->get_accName(self, &b);
            const std::wstring name = bstr(b);
            b = nullptr;
            acc->get_accValue(self, &b);
            const std::wstring value = bstr(b);
            b = nullptr;
            acc->get_accKeyboardShortcut(self, &b);
            const std::wstring key = bstr(b);
            VARIANT role;
            VariantInit(&role);
            acc->get_accRole(self, &role);
            wchar_t roletext[64] = L"?";
            if (role.vt == VT_I4) GetRoleTextW(role.lVal, roletext, 64);
            printf("  %2d  %-14s name=\"%s\"%s%s%s%s\n", ++n, narrow(roletext).c_str(), narrow(name).c_str(),
                   value.empty() ? "" : " value=\"", narrow(value.substr(0, 60)).c_str(), value.empty() ? "" : "\"",
                   key.empty() ? "" : (" key=" + narrow(key)).c_str());
            if (name.empty()) {
                printf("      FAIL: no name\n");
                ++failures;
            }
            if (!key.empty()) {
                const wchar_t k = static_cast<wchar_t>(towupper(key.back()));
                if (keys.count(k)) {
                    printf("      FAIL: access key %c also used by \"%s\"\n", static_cast<char>(k),
                           narrow(keys[k]).c_str());
                    ++failures;
                }
                keys[k] = name;
            }
            acc->Release();
        }
        c = GetNextDlgTabItem(sheet, c, FALSE);
    } while (c && c != first && n < 80);
    return failures;
}

} // namespace

int wmain(int argc, wchar_t** argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: a11y_check PATH\\OpenEvvConfig.exe\n");
        return 2;
    }
    wchar_t tmp[MAX_PATH];
    GetTempPathW(MAX_PATH, tmp);
    const std::wstring ini = std::wstring(tmp) + L"openevv_a11y_check.ini";
    DeleteFileW(ini.c_str());
    SetEnvironmentVariableW(L"OPENEVV_SETTINGS", ini.c_str()); // inherited by the utility

    HDESK desk = CreateDesktopW(kDesktop, nullptr, nullptr, 0, GENERIC_ALL, nullptr);
    if (!desk) {
        fprintf(stderr, "CreateDesktop failed %lu\n", GetLastError());
        return 2;
    }
    STARTUPINFOW si{sizeof si};
    std::wstring deskname = kDesktop;
    si.lpDesktop = deskname.data();
    PROCESS_INFORMATION pi{};
    std::wstring cmd = L"\"" + std::wstring(argv[1]) + L"\"";
    if (!CreateProcessW(argv[1], cmd.data(), nullptr, nullptr, FALSE, 0, nullptr, nullptr, &si, &pi)) {
        fprintf(stderr, "cannot start %ls (%lu)\n", argv[1], GetLastError());
        return 2;
    }
    SetThreadDesktop(desk); // this thread has no windows yet, so it may move
    HWND sheet = nullptr;
    for (int i = 0; i < 100 && !sheet; ++i) {
        Sleep(50);
        sheet = FindWindowW(nullptr, kTitle);
    }
    int failures = 0;
    if (!sheet) {
        fprintf(stderr, "the window did not appear\n");
        TerminateProcess(pi.hProcess, 1);
        return 1;
    }
    Sleep(400);
    CoInitialize(nullptr);

    const char* const kPages[] = {"Voices", "Speech", "Languages", "Community dictionary", "Diagnostics"};
    int stops = 0;
    for (int p = 0; p < 5; ++p) {
        SendMessageW(sheet, PSM_SETCURSEL, static_cast<WPARAM>(p), 0);
        Sleep(250);
        failures += walk(sheet, kPages[p]);
        ++stops;
    }

    // A voice parameter typed into its box reaches the file at once.
    SendMessageW(sheet, PSM_SETCURSEL, 0, 0);
    Sleep(200);
    HWND page = reinterpret_cast<HWND>(SendMessageW(sheet, PSM_GETCURRENTPAGEHWND, 0, 0));
    SendMessageW(GetDlgItem(page, 1006 /* IDC_PITCH */), WM_SETTEXT, 0, reinterpret_cast<LPARAM>(L"88"));
    Sleep(200);
    std::string text = read_file(ini);
    bool saved = text.find("[Voice.enus.1]") != std::string::npos && text.find("Pitch=88") != std::string::npos;
    printf("typing 88 into the pitch box %s the settings file\n", saved ? "updated" : "did NOT update");
    if (!saved) ++failures;

    // A speech setting chosen as the keyboard would.
    SendMessageW(sheet, PSM_SETCURSEL, 1, 0);
    Sleep(200);
    page = reinterpret_cast<HWND>(SendMessageW(sheet, PSM_GETCURRENTPAGEHWND, 0, 0));
    HWND rate = GetDlgItem(page, 1101 /* IDC_SAMPLERATE */);
    SendMessageW(rate, CB_SETCURSEL, 3, 0); // 22050 Hz
    SendMessageW(page, WM_COMMAND, MAKEWPARAM(1101, CBN_SELCHANGE), reinterpret_cast<LPARAM>(rate));
    Sleep(200);
    text = read_file(ini);
    saved = text.find("SampleRate=2") != std::string::npos;
    printf("choosing 22050 Hz %s the settings file\n", saved ? "updated" : "did NOT update");
    if (!saved) ++failures;

    PostMessageW(sheet, WM_COMMAND, IDCANCEL, 0);
    if (WaitForSingleObject(pi.hProcess, 8000) != WAIT_OBJECT_0) {
        printf("FAIL: the window did not close\n");
        TerminateProcess(pi.hProcess, 1);
        ++failures;
    }
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    CoUninitialize();
    CloseDesktop(desk);
    DeleteFileW(ini.c_str());
    printf("%s: %d pages, %d problems\n", failures ? "FAIL" : "PASS", stops, failures);
    return failures ? 1 : 0;
}
