// installer_a11y: what a screen reader sees in the installer, page by page.
//
//   installer_a11y PATH\OpenEVV-SAPI5-AccessibilityProbe.exe
//
// The probe is installer\openevv.iss compiled with /DProbe: the same wizard
// pages and [Code] as the real installer, but installing only a text file, per
// user and without elevation, and touching no registration, settings or logs.
// It runs on a private desktop, so nothing appears in front of the user or takes
// their screen reader's focus. Every visible control of every page is read
// through MSAA, which is what NVDA and JAWS use. The wizard is driven with each
// page's own button, by its MSAA default action - Next, Install, Finish, the
// keys a keyboard user presses - all the way through the last page, and the
// probe is uninstalled again afterwards.
//
// Fails when a focusable control has no accessible name, when a page does not
// advance, when the last page does not state the registration result, or when a
// check list is not named for what it is (MSAA takes a list's name from the
// static text just before it).
#include <windows.h>
#include <oleacc.h>

#include <cstdio>
#include <filesystem>
#include <string>
#include <vector>

namespace {

const wchar_t kDesktop[] = L"OpenEVV_installer_a11y";
const wchar_t kProbeKey[] =
    L"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{DB3F06B0-C03E-4F87-9739-B953FC329AAF}_is1";

struct Control
{
    HWND hwnd = nullptr;
    std::wstring cls, name, value;
    long role = 0;
    long state = 0;
    IAccessible* acc = nullptr;
};

std::wstring bstr(BSTR b)
{
    std::wstring s = b ? std::wstring(b, SysStringLen(b)) : std::wstring();
    SysFreeString(b);
    return s;
}

std::string narrow(const std::wstring& w, size_t max = 400)
{
    std::string s;
    for (wchar_t c : w) {
        if (c == L'\r') continue;
        if (c == L'\n') {
            s += " / ";
            continue;
        }
        s.push_back(c >= 32 && c < 127 ? static_cast<char>(c) : '?');
    }
    if (s.size() > max) s = s.substr(0, max - 3) + "...";
    return s;
}

std::wstring without_amp(std::wstring s)
{
    std::wstring o;
    for (wchar_t c : s)
        if (c != L'&') o.push_back(c);
    return o;
}

BOOL CALLBACK collect(HWND h, LPARAM lp)
{
    reinterpret_cast<std::vector<HWND>*>(lp)->push_back(h);
    return TRUE;
}

void release_all(std::vector<Control>& cs)
{
    for (auto& c : cs)
        if (c.acc) c.acc->Release();
    cs.clear();
}

std::vector<Control> controls(HWND form)
{
    std::vector<HWND> hs;
    EnumChildWindows(form, collect, reinterpret_cast<LPARAM>(&hs));
    std::vector<Control> out;
    for (HWND h : hs) {
        if (!IsWindowVisible(h)) continue;
        IAccessible* acc = nullptr;
        if (FAILED(AccessibleObjectFromWindow(h, static_cast<DWORD>(OBJID_CLIENT), IID_IAccessible,
                                              reinterpret_cast<void**>(&acc))) ||
            !acc) {
            continue;
        }
        Control c;
        c.hwnd = h;
        wchar_t cls[128] = L"";
        GetClassNameW(h, cls, 128);
        c.cls = cls;
        VARIANT self;
        self.vt = VT_I4;
        self.lVal = CHILDID_SELF;
        BSTR b = nullptr;
        // one call per statement: arguments are evaluated right to left
        acc->get_accName(self, &b);
        c.name = bstr(b);
        b = nullptr;
        acc->get_accValue(self, &b);
        c.value = bstr(b);
        VARIANT v;
        VariantInit(&v);
        if (SUCCEEDED(acc->get_accRole(self, &v)) && v.vt == VT_I4) c.role = v.lVal;
        VariantClear(&v);
        if (SUCCEEDED(acc->get_accState(self, &v)) && v.vt == VT_I4) c.state = v.lVal;
        VariantClear(&v);
        if (c.state & STATE_SYSTEM_INVISIBLE) {
            acc->Release();
            continue;
        }
        c.acc = acc;
        out.push_back(std::move(c));
    }
    return out;
}

// What distinguishes one page from the next: every visible name, in order.
std::wstring signature(HWND form)
{
    std::vector<Control> cs = controls(form);
    std::wstring s;
    for (const auto& c : cs) s += c.name + L"|";
    release_all(cs);
    return s;
}

struct FindWizard
{
    HWND hit = nullptr;
};

BOOL CALLBACK find_wizard(HWND h, LPARAM lp)
{
    wchar_t cls[64] = L"";
    GetClassNameW(h, cls, 64);
    if (wcscmp(cls, L"TWizardForm") == 0 && IsWindowVisible(h)) {
        reinterpret_cast<FindWizard*>(lp)->hit = h;
        return FALSE;
    }
    return TRUE;
}

bool is_container(long role)
{
    return role == ROLE_SYSTEM_WINDOW || role == ROLE_SYSTEM_CLIENT || role == ROLE_SYSTEM_GROUPING ||
           role == ROLE_SYSTEM_SEPARATOR || role == ROLE_SYSTEM_PANE;
}

// The last page is laid out in [Code]; a sighted helper reading over the user's
// shoulder should not find text drawn over a list, or a list cut off by the page.
// Checks that no two controls on a wizard page overlap and each fits its page.
int layout_problems(const std::vector<Control>& cs)
{
    int problems = 0;
    std::vector<const Control*> on_page;
    for (const auto& c : cs) {
        if (is_container(c.role)) continue;
        wchar_t parent_cls[64] = L"";
        GetClassNameW(GetParent(c.hwnd), parent_cls, 64);
        if (wcscmp(parent_cls, L"TNewNotebookPage") != 0) continue;
        RECT r, page;
        GetWindowRect(c.hwnd, &r);
        GetWindowRect(GetParent(c.hwnd), &page);
        if (r.left < page.left || r.top < page.top || r.right > page.right || r.bottom > page.bottom) {
            printf("    FAIL: \"%s\" extends past the edge of its page\n", narrow(c.name, 60).c_str());
            ++problems;
        }
        on_page.push_back(&c);
    }
    for (size_t i = 0; i < on_page.size(); ++i) {
        for (size_t j = i + 1; j < on_page.size(); ++j) {
            RECT a, b, x;
            GetWindowRect(on_page[i]->hwnd, &a);
            GetWindowRect(on_page[j]->hwnd, &b);
            if (IntersectRect(&x, &a, &b)) {
                printf("    FAIL: \"%s\" overlaps \"%s\"\n", narrow(on_page[i]->name, 60).c_str(),
                       narrow(on_page[j]->name, 60).c_str());
                ++problems;
            }
        }
    }
    return problems;
}

bool run_on_desktop(const std::wstring& exe, const std::wstring& args, DWORD wait_ms, DWORD* exit_code)
{
    STARTUPINFOW si{sizeof si};
    std::wstring deskname = kDesktop;
    si.lpDesktop = deskname.data();
    PROCESS_INFORMATION pi{};
    std::wstring cmd = L"\"" + exe + L"\" " + args;
    if (!CreateProcessW(exe.c_str(), cmd.data(), nullptr, nullptr, FALSE, 0, nullptr, nullptr, &si, &pi)) {
        return false;
    }
    CloseHandle(pi.hThread);
    const bool done = WaitForSingleObject(pi.hProcess, wait_ms) == WAIT_OBJECT_0;
    if (exit_code) GetExitCodeProcess(pi.hProcess, exit_code);
    CloseHandle(pi.hProcess);
    return done;
}

bool probe_installed()
{
    HKEY k = nullptr;
    if (RegOpenKeyExW(HKEY_CURRENT_USER, kProbeKey, 0, KEY_QUERY_VALUE, &k) != ERROR_SUCCESS) return false;
    RegCloseKey(k);
    return true;
}

// Runs the probe's own uninstaller and waits for its registration to go.
bool uninstall_probe()
{
    HKEY k = nullptr;
    if (RegOpenKeyExW(HKEY_CURRENT_USER, kProbeKey, 0, KEY_QUERY_VALUE, &k) != ERROR_SUCCESS) return true;
    wchar_t buf[1024] = L"";
    DWORD size = sizeof buf - sizeof(wchar_t);
    DWORD type = 0;
    const LONG rc = RegQueryValueExW(k, L"UninstallString", nullptr, &type, reinterpret_cast<BYTE*>(buf), &size);
    RegCloseKey(k);
    if (rc != ERROR_SUCCESS) return false;
    std::wstring exe = buf;
    if (!exe.empty() && exe.front() == L'"') exe = exe.substr(1, exe.find(L'"', 1) - 1);
    run_on_desktop(exe, L"/VERYSILENT /SUPPRESSMSGBOXES /NORESTART", 60000, nullptr);
    // The uninstaller hands over to a copy of itself in %TEMP% and returns early.
    for (int i = 0; i < 300 && probe_installed(); ++i) Sleep(100);
    return !probe_installed();
}

} // namespace

int wmain(int argc, wchar_t** argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: installer_a11y PATH\\OpenEVV-SAPI5-AccessibilityProbe.exe\n");
        return 2;
    }
    HDESK desk = CreateDesktopW(kDesktop, nullptr, nullptr, 0, GENERIC_ALL, nullptr);
    if (!desk) {
        fprintf(stderr, "CreateDesktop failed %lu\n", GetLastError());
        return 2;
    }
    SetThreadDesktop(desk); // before COM makes a window on this thread
    CoInitialize(nullptr);

    if (probe_installed()) {
        printf("removing a probe left installed by an earlier run\n");
        uninstall_probe();
    }

    wchar_t tmp[MAX_PATH];
    GetTempPathW(MAX_PATH, tmp);
    const std::wstring dir = std::wstring(tmp) + L"OpenEVV_installer_a11y";
    const std::wstring setup_log = std::wstring(tmp) + L"OpenEVV_installer_a11y_setup.log";
    // An existing folder would add a "folder already exists" question to the walk.
    std::error_code ec;
    std::filesystem::remove_all(dir, ec);

    STARTUPINFOW si{sizeof si};
    std::wstring deskname = kDesktop;
    si.lpDesktop = deskname.data();
    PROCESS_INFORMATION pi{};
    std::wstring cmd = L"\"" + std::wstring(argv[1]) + L"\" /DIR=\"" + dir + L"\" /LOG=\"" + setup_log + L"\"";
    if (!CreateProcessW(argv[1], cmd.data(), nullptr, nullptr, FALSE, 0, nullptr, nullptr, &si, &pi)) {
        fprintf(stderr, "cannot start %ls (%lu)\n", argv[1], GetLastError());
        return 2;
    }
    CloseHandle(pi.hThread);

    // Setup relaunches itself from a temporary folder, so find the window by class.
    FindWizard f;
    for (int i = 0; i < 300 && !f.hit; ++i) {
        Sleep(100);
        EnumDesktopWindows(desk, find_wizard, reinterpret_cast<LPARAM>(&f));
    }
    int failures = 0;
    if (!f.hit) {
        printf("FAIL: the wizard window never appeared\n");
        TerminateProcess(pi.hProcess, 1);
        return 1;
    }
    const HWND form = f.hit;
    Sleep(800);

    bool saw_tasks_name = false, saw_run_name = false, saw_summary = false, finished = false;
    int pages = 0, stops = 0;
    for (int page = 1; page <= 12 && !finished; ++page) {
        std::vector<Control> cs = controls(form);
        ++pages;
        printf("--- page %d\n", page);
        Control* advance = nullptr;
        for (auto& c : cs) {
            wchar_t roletext[64] = L"?";
            GetRoleTextW(static_cast<DWORD>(c.role), roletext, 64);
            const bool focusable = (c.state & STATE_SYSTEM_FOCUSABLE) != 0;
            const bool enabled = (c.state & STATE_SYSTEM_UNAVAILABLE) == 0;
            if (focusable && enabled) ++stops;
            std::string line = "    ";
            line += focusable ? "[tab] " : "      ";
            char head[160];
            snprintf(head, sizeof head, "%-16s %-22s ", narrow(roletext).c_str(), narrow(c.cls).c_str());
            line += head;
            line += "\"" + narrow(c.name) + "\"";
            if (!c.value.empty() && c.role == ROLE_SYSTEM_TEXT) {
                line += "  (" + std::to_string(c.value.size()) + " characters of text)";
            }
            if (focusable && enabled && c.name.empty() && !is_container(c.role)) {
                line += "   <== FAIL: focusable, no accessible name";
                ++failures;
            }
            printf("%s\n", line.c_str());
            if (c.role == ROLE_SYSTEM_OUTLINE && c.name.rfind(L"Select the additional tasks", 0) == 0) {
                saw_tasks_name = true;
            }
            if (c.role == ROLE_SYSTEM_OUTLINE && c.name.rfind(L"Things to do now", 0) == 0) saw_run_name = true;
            if (c.role == ROLE_SYSTEM_STATICTEXT && c.name.find(L"Accessibility probe: no voices") != std::wstring::npos &&
                c.name.find(L"Logs, including install.log") != std::wstring::npos) {
                saw_summary = true;
            }
            if (c.role == ROLE_SYSTEM_PUSHBUTTON && enabled) {
                const std::wstring n = without_amp(c.name);
                if (n.rfind(L"Next", 0) == 0 || n.rfind(L"Install", 0) == 0 || n.rfind(L"Finish", 0) == 0) {
                    advance = &c;
                }
            }
        }
        failures += layout_problems(cs);
        const std::wstring before = signature(form);
        if (advance) {
            const bool last = without_amp(advance->name).rfind(L"Finish", 0) == 0;
            printf("    pressing \"%s\"\n", narrow(without_amp(advance->name)).c_str());
            VARIANT self;
            self.vt = VT_I4;
            self.lVal = CHILDID_SELF;
            advance->acc->accDoDefaultAction(self);
            if (last) {
                finished = true;
                release_all(cs);
                break;
            }
        } else {
            printf("    (no Next button: waiting for the page to move on by itself)\n");
        }
        release_all(cs);
        bool moved = false;
        for (int i = 0; i < 1200 && !moved; ++i) { // up to two minutes, for the Installing page
            Sleep(100);
            if (!IsWindow(form)) break;
            moved = signature(form) != before;
        }
        if (!moved) {
            printf("FAIL: the page did not change\n");
            ++failures;
            break;
        }
        Sleep(600); // let the page finish laying itself out
    }

    if (!finished) {
        printf("FAIL: never reached a Finish button\n");
        ++failures;
        TerminateProcess(pi.hProcess, 1);
    } else if (WaitForSingleObject(pi.hProcess, 30000) != WAIT_OBJECT_0) {
        printf("FAIL: setup did not exit after Finish\n");
        TerminateProcess(pi.hProcess, 1);
        ++failures;
    }
    CloseHandle(pi.hProcess);

    if (!saw_tasks_name) {
        printf("FAIL: the additional tasks list is not named after its instructions\n");
        ++failures;
    }
    if (!saw_run_name) {
        printf("FAIL: the list on the last page is not named \"Things to do now\"\n");
        ++failures;
    }
    if (!saw_summary) {
        printf("FAIL: the last page did not state the registration result and the log folder\n");
        ++failures;
    }
    const bool removed = uninstall_probe();
    printf("probe %s\n", removed ? "uninstalled" : "could NOT be uninstalled");
    if (!removed) ++failures;

    CoUninitialize();
    CloseDesktop(desk);
    printf("%s: %d pages, %d enabled tab stops, %d problems\n", failures ? "FAIL" : "PASS", pages, stops, failures);
    return failures ? 1 : 0;
}
