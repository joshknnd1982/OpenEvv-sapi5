// installer_a11y: what a screen reader sees in the installer, page by page.
//
//   installer_a11y PATH\OpenEVV-SAPI5-AccessibilityProbe.exe [options]
//
//     --dir DIR            install into DIR (default: a folder in %TEMP%)
//     --upgrade            DIR already holds an installation of the probe: walk the wizard over it
//                          as a person upgrading would, without removing it first
//     --expect-checked N   the languages page must show N items checked when it first appears
//                          (a group, "OpenEVV" or "eSpeak NG", counts only when all of its languages are:
//                          otherwise it is shown half checked)
//     --expect-type TEXT   the list of types of installation must read TEXT (a part of it) when the
//                          languages page first appears
//     --screenshot PREFIX  write each page of the wizard as PREFIX<n>.bmp, for a person to look at
//     --expect-packs N     when setup is done, DIR\languages must hold N packs (folders with a language.ini)
//     --buttons            on the languages page: press "Select no languages" (nothing may stay checked),
//                          press Next (an error must say that at least one language is needed, and the
//                          page must stay), press "Select all languages" (every item must be checked),
//                          and go on
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
// static text just before it). The page that chooses the languages is held to the
// same: its type list and its language list are named "Type of installation" and
// "Languages to install", and what it shows checked is read item by item.
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

// The wizard window as it is drawn, written as a 24-bit bitmap.
void save_window(HWND h, const std::wstring& path)
{
    RECT r;
    GetWindowRect(h, &r);
    const int w = r.right - r.left, hgt = r.bottom - r.top;
    if (w <= 0 || hgt <= 0) return;
    HDC screen = GetDC(nullptr);
    HDC dc = CreateCompatibleDC(screen);
    HBITMAP bmp = CreateCompatibleBitmap(screen, w, hgt);
    HGDIOBJ old = SelectObject(dc, bmp);
    PrintWindow(h, dc, 2 /* PW_RENDERFULLCONTENT */);
    BITMAPINFOHEADER bi{sizeof bi, w, -hgt, 1, 24, BI_RGB, 0, 0, 0, 0, 0};
    const int stride = (w * 3 + 3) & ~3;
    std::vector<unsigned char> px(static_cast<size_t>(stride) * hgt);
    GetDIBits(dc, bmp, 0, static_cast<UINT>(hgt), px.data(), reinterpret_cast<BITMAPINFO*>(&bi), DIB_RGB_COLORS);
    SelectObject(dc, old);
    DeleteObject(bmp);
    DeleteDC(dc);
    ReleaseDC(nullptr, screen);
    BITMAPFILEHEADER fh{0x4D42, static_cast<DWORD>(sizeof fh + sizeof bi + px.size()), 0, 0, sizeof fh + sizeof bi};
    bi.biHeight = -hgt;
    HANDLE f = CreateFileW(path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (f == INVALID_HANDLE_VALUE) return;
    DWORD got = 0;
    WriteFile(f, &fh, sizeof fh, &got, nullptr);
    WriteFile(f, &bi, sizeof bi, &got, nullptr);
    WriteFile(f, px.data(), static_cast<DWORD>(px.size()), &got, nullptr);
    CloseHandle(f);
}

struct Item
{
    std::wstring name;
    long state = 0;
};

// The items of a check list, as a screen reader reads them: each one's name and state.
std::vector<Item> list_items(IAccessible* list)
{
    std::vector<Item> out;
    long n = 0;
    if (FAILED(list->get_accChildCount(&n))) return out;
    for (long i = 1; i <= n; ++i) {
        VARIANT child;
        child.vt = VT_I4;
        child.lVal = i;
        Item it;
        BSTR b = nullptr;
        list->get_accName(child, &b);
        it.name = bstr(b);
        VARIANT st;
        VariantInit(&st);
        if (SUCCEEDED(list->get_accState(child, &st)) && st.vt == VT_I4) it.state = st.lVal;
        VariantClear(&st);
        out.push_back(std::move(it));
    }
    return out;
}

// Folders of DIR\languages that hold a language.ini.
int count_packs(const std::wstring& dir)
{
    int n = 0;
    std::error_code ec;
    for (const auto& e : std::filesystem::directory_iterator(dir + L"\\languages", ec)) {
        if (e.is_directory(ec) && std::filesystem::exists(e.path() / L"language.ini", ec)) ++n;
    }
    return n;
}

struct FindDialog
{
    HWND wizard = nullptr;
    DWORD pid = 0; // the setup program's own windows only: the desktop has system windows of its own
    HWND hit = nullptr;
    std::wstring cls;
    std::wstring seen;
};

// A message box setup shows: a visible top-level window of the private desktop that is not the wizard.
BOOL CALLBACK find_dialog(HWND h, LPARAM lp)
{
    auto* f = reinterpret_cast<FindDialog*>(lp);
    if (h == f->wizard || !IsWindowVisible(h)) return TRUE;
    DWORD pid = 0;
    GetWindowThreadProcessId(h, &pid);
    if (pid != f->pid) return TRUE;
    wchar_t cls[64] = L"";
    GetClassNameW(h, cls, 64);
    if (wcscmp(cls, L"TWizardForm") == 0 || wcscmp(cls, L"TMainForm") == 0 || wcscmp(cls, L"TApplication") == 0) {
        return TRUE;
    }
    // Windows' own helper windows (the input indicator, the IME) are in every process on a desktop
    if (wcsncmp(cls, L"UAC", 3) == 0 || wcsncmp(cls, L"MSCTFIME", 8) == 0 || wcsstr(cls, L"IME") != nullptr) {
        return TRUE;
    }
    wchar_t title[128] = L"";
    GetWindowTextW(h, title, 128);
    f->seen += std::wstring(cls) + L" \"" + title + L"\"; ";
    f->hit = h;
    f->cls = cls;
    return FALSE;
}

int count_checked(const std::vector<Item>& items)
{
    int n = 0;
    for (const Item& it : items)
        if (it.state & STATE_SYSTEM_CHECKED) ++n;
    return n;
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
        fprintf(stderr,
                "usage: installer_a11y PATH\\OpenEVV-SAPI5-AccessibilityProbe.exe [--dir DIR] [--upgrade] "
                "[--expect-checked N] [--expect-type TEXT] [--expect-packs N] [--buttons]\n");
        return 2;
    }
    std::wstring dir_arg;
    bool upgrade = false;
    int expect_checked = -1, expect_packs = -1;
    bool buttons = false;
    std::wstring expect_type, shot_prefix;
    for (int i = 2; i < argc; ++i) {
        const std::wstring a = argv[i];
        if (a == L"--upgrade") upgrade = true;
        else if (a == L"--buttons") buttons = true;
        else if (a == L"--screenshot" && i + 1 < argc) shot_prefix = argv[++i];
        else if (a == L"--expect-type" && i + 1 < argc) expect_type = argv[++i];
        else if (a == L"--dir" && i + 1 < argc) dir_arg = argv[++i];
        else if (a == L"--expect-checked" && i + 1 < argc) expect_checked = _wtoi(argv[++i]);
        else if (a == L"--expect-packs" && i + 1 < argc) expect_packs = _wtoi(argv[++i]);
        else {
            fprintf(stderr, "unknown argument %ls\n", a.c_str());
            return 2;
        }
    }
    SetProcessDPIAware(); // window rectangles are the real ones, so that a screenshot is the whole window
    HDESK desk = CreateDesktopW(kDesktop, nullptr, nullptr, 0, GENERIC_ALL, nullptr);
    if (!desk) {
        fprintf(stderr, "CreateDesktop failed %lu\n", GetLastError());
        return 2;
    }
    SetThreadDesktop(desk); // before COM makes a window on this thread
    CoInitialize(nullptr);

    if (probe_installed() && !upgrade) {
        printf("removing a probe left installed by an earlier run\n");
        uninstall_probe();
    }

    wchar_t tmp[MAX_PATH];
    GetTempPathW(MAX_PATH, tmp);
    const std::wstring dir = dir_arg.empty() ? std::wstring(tmp) + L"OpenEVV_installer_a11y" : dir_arg;
    const std::wstring setup_log = std::wstring(tmp) + L"OpenEVV_installer_a11y_setup.log";
    // An existing folder would add a "folder already exists" question to the walk.
    std::error_code ec;
    if (!upgrade) std::filesystem::remove_all(dir, ec);

    STARTUPINFOW si{sizeof si};
    std::wstring deskname = kDesktop;
    si.lpDesktop = deskname.data();
    PROCESS_INFORMATION pi{};
    std::wstring cmd = L"\"" + std::wstring(argv[1]) + L"\" /DIR=\"" + dir + L"\" /LOG=\"" + setup_log + L"\"";
    // Setup starts a copy of itself from %TEMP%. A walk that fails must not leave that copy waiting
    // on a message box on this desktop for the next walk to find: everything setup starts goes
    // with this job when this program ends.
    HANDLE job = CreateJobObjectW(nullptr, nullptr);
    if (job) {
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION li{};
        li.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        SetInformationJobObject(job, JobObjectExtendedLimitInformation, &li, sizeof li);
    }
    if (!CreateProcessW(argv[1], cmd.data(), nullptr, nullptr, FALSE, CREATE_SUSPENDED, nullptr, nullptr, &si, &pi)) {
        fprintf(stderr, "cannot start %ls (%lu)\n", argv[1], GetLastError());
        return 2;
    }
    if (job) AssignProcessToJobObject(job, pi.hProcess);
    ResumeThread(pi.hThread);
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
    bool saw_types_name = false, saw_languages_name = false, saw_languages_stated = false;
    int checked_shown = -1;
    std::wstring type_shown;
    bool type_seen = false;
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
            if (c.role == ROLE_SYSTEM_COMBOBOX && c.name.rfind(L"Type of installation", 0) == 0) {
                saw_types_name = true;
                printf("          selected type: \"%s\"\n", narrow(c.value).c_str());
                if (!type_seen) type_shown = c.value;
                type_seen = true;
            }
            if (c.role == ROLE_SYSTEM_OUTLINE && c.name.rfind(L"Languages to install", 0) == 0) {
                saw_languages_name = true;
                const std::vector<Item> items = list_items(c.acc);
                int checked = 0;
                std::string names;
                for (const Item& it : items) {
                    if (it.state & STATE_SYSTEM_CHECKED) {
                        ++checked;
                        if (checked <= 12) names += (names.empty() ? "" : ", ") + narrow(it.name, 40);
                    }
                }
                if (checked_shown < 0) checked_shown = checked;
                printf("          %d items, %d checked%s%s\n", static_cast<int>(items.size()), checked,
                       checked ? ": " : "", names.c_str());
                // 155 languages to choose from, and the groups they are in
                if (items.size() < 155) {
                    printf("    FAIL: the languages page lists only %d items; there are 155 languages\n",
                           static_cast<int>(items.size()));
                    ++failures;
                }
            }
            if (c.role == ROLE_SYSTEM_STATICTEXT && c.name.find(L"Accessibility probe: no voices") != std::wstring::npos &&
                c.name.find(L"Logs, including install.log") != std::wstring::npos) {
                saw_summary = true;
            }
            if (c.role == ROLE_SYSTEM_STATICTEXT && c.name.find(L"Installed: ") != std::wstring::npos &&
                c.name.find(L"languages") != std::wstring::npos) {
                saw_languages_stated = true;
            }
            if (c.role == ROLE_SYSTEM_PUSHBUTTON && enabled) {
                const std::wstring n = without_amp(c.name);
                if (n.rfind(L"Next", 0) == 0 || n.rfind(L"Install", 0) == 0 || n.rfind(L"Finish", 0) == 0) {
                    advance = &c;
                }
            }
        }
        failures += layout_problems(cs);
        if (!shot_prefix.empty()) save_window(form, shot_prefix + std::to_wstring(page) + L".bmp");
        const std::wstring before = signature(form);
        Control* languages_list = nullptr;
        Control* select_all = nullptr;
        Control* select_none = nullptr;
        for (auto& c : cs) {
            if (c.role == ROLE_SYSTEM_OUTLINE && c.name.rfind(L"Languages to install", 0) == 0) languages_list = &c;
            if (c.role == ROLE_SYSTEM_PUSHBUTTON) {
                const std::wstring n = without_amp(c.name);
                if (n.rfind(L"Select all languages", 0) == 0) select_all = &c;
                if (n.rfind(L"Select no languages", 0) == 0) select_none = &c;
            }
        }
        if (languages_list && !select_all) {
            printf("    FAIL: no \"Select all languages\" button on the languages page\n");
            ++failures;
        }
        if (languages_list && !select_none) {
            printf("    FAIL: no \"Select no languages\" button on the languages page\n");
            ++failures;
        }
        if (buttons && languages_list && select_all && select_none && advance) {
            VARIANT self;
            self.vt = VT_I4;
            self.lVal = CHILDID_SELF;
            const auto wait_checked = [&](bool all) {
                for (int i = 0; i < 40; ++i) {
                    const std::vector<Item> items = list_items(languages_list->acc);
                    const int n = count_checked(items);
                    if (all ? n == static_cast<int>(items.size()) : n == 0) return n;
                    Sleep(100);
                }
                return count_checked(list_items(languages_list->acc));
            };
            printf("    pressing \"Select no languages\"\n");
            select_none->acc->accDoDefaultAction(self);
            const int none = wait_checked(false);
            printf("          %d items checked\n", none);
            if (none != 0) {
                printf("    FAIL: \"Select no languages\" left %d items checked\n", none);
                ++failures;
            }
            printf("    pressing \"%s\" with nothing selected\n", narrow(without_amp(advance->name)).c_str());
            advance->acc->accDoDefaultAction(self);
            FindDialog d;
            d.wizard = form;
            GetWindowThreadProcessId(form, &d.pid);
            for (int i = 0; i < 50 && !d.hit; ++i) {
                Sleep(100);
                EnumDesktopWindows(desk, find_dialog, reinterpret_cast<LPARAM>(&d));
            }
            if (!d.hit) {
                printf("    FAIL: no error appeared when no language was selected\n");
                ++failures;
            } else {
                std::vector<Control> dc = controls(d.hit);
                std::wstring text;
                Control* ok = nullptr;
                for (auto& x : dc) {
                    if (x.role == ROLE_SYSTEM_STATICTEXT) text += x.name + L" ";
                    if (x.role == ROLE_SYSTEM_PUSHBUTTON && !ok) ok = &x;
                }
                printf("    a dialog (%s) says: \"%s\"\n", narrow(d.cls).c_str(), narrow(text, 300).c_str());
                printf("          (windows of setup: %s)\n", narrow(d.seen, 300).c_str());
                if (text.find(L"at least one language") == std::wstring::npos) {
                    printf("    FAIL: the error does not ask for at least one language\n");
                    ++failures;
                }
                if (ok) {
                    printf("    pressing \"%s\" in the dialog\n", narrow(without_amp(ok->name)).c_str());
                    ok->acc->accDoDefaultAction(self);
                } else {
                    printf("    FAIL: the error has no button\n");
                    ++failures;
                }
                release_all(dc);
                for (int i = 0; i < 30 && IsWindow(d.hit) && IsWindowVisible(d.hit); ++i) Sleep(100);
            }
            Sleep(300);
            if (signature(form) != before) {
                printf("    FAIL: the page went on with no language selected\n");
                ++failures;
            }
            printf("    pressing \"Select all languages\"\n");
            select_all->acc->accDoDefaultAction(self);
            const int all = wait_checked(true);
            const int total = static_cast<int>(list_items(languages_list->acc).size());
            printf("          %d of %d items checked\n", all, total);
            if (all != total) {
                printf("    FAIL: \"Select all languages\" left %d of %d items unchecked\n", total - all, total);
                ++failures;
            }
            buttons = false;
        }
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
    if (!saw_types_name) {
        printf("FAIL: the list of types of installation is not named \"Type of installation\"\n");
        ++failures;
    }
    if (!saw_languages_name) {
        printf("FAIL: the list of languages is not named \"Languages to install\"\n");
        ++failures;
    }
    if (!saw_languages_stated) {
        printf("FAIL: the last page did not say how many languages were installed\n");
        ++failures;
    }
    if (expect_checked >= 0 && checked_shown != expect_checked) {
        printf("FAIL: the languages page first showed %d items checked, %d expected\n", checked_shown, expect_checked);
        ++failures;
    }
    if (!expect_type.empty() && type_shown.find(expect_type) == std::wstring::npos) {
        printf("FAIL: the languages page first showed the type \"%s\", \"%s\" expected\n", narrow(type_shown).c_str(),
               narrow(expect_type).c_str());
        ++failures;
    }
    if (expect_packs >= 0) {
        const int packs = count_packs(dir);
        printf("%d language packs installed\n", packs);
        if (packs != expect_packs) {
            printf("FAIL: %d language packs expected\n", expect_packs);
            ++failures;
        }
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
