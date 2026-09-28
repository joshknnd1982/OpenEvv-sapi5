// OpenEvvConfig.exe: every adjustable OpenEVV parameter, for every voice of
// every language, saved to %APPDATA%\OpenEVV\settings.ini on each change.
// Every OpenEVV SAPI voice re-reads that file before it speaks, so a change is
// heard the next time any program speaks -- a screen reader already using the
// voice included. Nothing has to be applied or restarted.
//
//   OpenEvvConfig.exe                      the settings window
//   OpenEvvConfig.exe --selftest [--hosts-only | --sapi-only] [--report FILE]
//                                          speak every voice into memory, and
//                                          one through SAPI; the exit code is
//                                          the number of failures
//   OpenEvvConfig.exe --add-pack PATH      install the language pack(s) in a
//                                          .zip, a folder or a language.ini
//   OpenEvvConfig.exe --remove-pack DIR    delete a language pack (run elevated
//                                          by the window for a shipped pack)
#include <windows.h>
#include <commctrl.h>
#include <mmsystem.h>
#include <shellapi.h>
#include <shldisp.h>
#include <shlobj.h>
#include <shobjidl.h>
// Last among the system headers: initguid defines the Dynamic Annotation
// GUIDs oleacc.h declares, which no import library provides.
#include <initguid.h>
#include <oleacc.h>

#include <algorithm>
#include <atomic>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "common/host_client.h"
#include "common/ini.h"
#include "common/languages.h"
#include "common/log.h"
#include "common/paths.h"
#include "common/render.h"
#include "common/settings.h"
#include "common/version.h"
#include "common/voice_math.h"
#include "resource.h"
#include "selftest.h"

using namespace evv;

namespace {

constexpr UINT WM_APP_STATUS = WM_APP + 1;   // lParam: new std::wstring*, wParam: control id
constexpr UINT WM_APP_SELFTEST = WM_APP + 2; // lParam: new std::wstring*

Settings g_s;
std::vector<LanguageInfo> g_langs;
unsigned g_langs_generation = 1;
HWND g_sheet = nullptr;

const wchar_t kDefaultTest[] =
    L"Hello. This is the OpenEVV voice you are adjusting. The quick brown fox jumps over the lazy dog, at 3:45 p.m.";

std::wstring sample_for(const LanguageInfo& l)
{
    const std::wstring t = l.tag.substr(0, 2);
    if (t == L"de") return L"Guten Tag. Das ist die Stimme, die Sie gerade einstellen.";
    if (t == L"es") return L"Hola. Esta es la voz que está ajustando.";
    if (t == L"fr") return L"Bonjour. Voici la voix que vous réglez.";
    if (t == L"it") return L"Buongiorno. Questa è la voce che state regolando.";
    if (t == L"pl") return L"Dzień dobry. To jest głos, który ustawiasz.";
    if (t == L"ja") return L"こんにちは。これは調整中の声です。";
    return kDefaultTest;
}

void reload_languages()
{
    g_langs = scan_languages();
    ++g_langs_generation;
}

// Every change goes to the file at once; there is nothing to apply or cancel.
void save()
{
    if (!save_settings(g_s)) {
        MessageBoxW(g_sheet, (L"The settings could not be saved to " + settings_path()).c_str(), L"OpenEVV",
                    MB_OK | MB_ICONERROR);
        return;
    }
    log::set_level(g_s.log_level);
}

// One Close button. Cancel stays, hidden, so Escape still closes the window.
void setup_sheet_buttons(HWND sheet)
{
    if (!sheet) return;
    SetDlgItemTextW(sheet, IDOK, L"Close");
    ShowWindow(GetDlgItem(sheet, IDCANCEL), SW_HIDE);
    // The page tabs have no label of their own; name them for MSAA.
    IAccPropServices* props = nullptr;
    if (SUCCEEDED(CoCreateInstance(CLSID_AccPropServices, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&props)))) {
        props->SetHwndPropStr(PropSheet_GetTabControl(sheet), static_cast<DWORD>(OBJID_CLIENT), CHILDID_SELF,
                              PROPID_ACC_NAME, L"Settings pages");
        props->Release();
    }
}

void post_status(HWND dlg, int id, const std::wstring& text)
{
    PostMessageW(dlg, WM_APP_STATUS, static_cast<WPARAM>(id), reinterpret_cast<LPARAM>(new std::wstring(text)));
}

// ---- combo helpers ------------------------------------------------------------

void combo_add(HWND dlg, int id, const std::wstring& text, LPARAM data)
{
    HWND c = GetDlgItem(dlg, id);
    const LRESULT i = SendMessageW(c, CB_ADDSTRING, 0, reinterpret_cast<LPARAM>(text.c_str()));
    SendMessageW(c, CB_SETITEMDATA, static_cast<WPARAM>(i), data);
}

void combo_select(HWND dlg, int id, LPARAM data)
{
    HWND c = GetDlgItem(dlg, id);
    const LRESULT n = SendMessageW(c, CB_GETCOUNT, 0, 0);
    for (LRESULT i = 0; i < n; ++i) {
        if (SendMessageW(c, CB_GETITEMDATA, static_cast<WPARAM>(i), 0) == data) {
            SendMessageW(c, CB_SETCURSEL, static_cast<WPARAM>(i), 0);
            return;
        }
    }
    SendMessageW(c, CB_SETCURSEL, 0, 0);
}

int combo_data(HWND dlg, int id, int fallback)
{
    HWND c = GetDlgItem(dlg, id);
    const LRESULT i = SendMessageW(c, CB_GETCURSEL, 0, 0);
    return i == CB_ERR ? fallback : static_cast<int>(SendMessageW(c, CB_GETITEMDATA, static_cast<WPARAM>(i), 0));
}

void spin_range(HWND dlg, int spin, int lo, int hi)
{
    SendDlgItemMessageW(dlg, spin, UDM_SETRANGE32, static_cast<WPARAM>(lo), static_cast<LPARAM>(hi));
}

int read_int(HWND dlg, int id, int lo, int hi, int fallback)
{
    BOOL ok = FALSE;
    const UINT v = GetDlgItemInt(dlg, id, &ok, FALSE);
    if (!ok) return fallback;
    return static_cast<int>(std::min<UINT>(std::max<UINT>(v, static_cast<UINT>(lo)), static_cast<UINT>(hi)));
}

// ---- test playback --------------------------------------------------------------

class Speaker
{
public:
    ~Speaker() { stop(); }

    void speak(HWND dlg, int status_id, const LanguageInfo& lang, int preset, const std::wstring& text)
    {
        stop();
        stop_ = false;
        const Settings s = g_s;
        thread_ = std::thread([this, dlg, status_id, lang, preset, text, s] {
            const RenderResult r = render_voice(lang, preset, s, text);
            if (!r.ok()) {
                post_status(dlg, status_id, L"Could not speak: " + utf8_to_wide(r.error));
                return;
            }
            wchar_t msg[200];
            swprintf_s(msg, L"Speaking %.1f seconds at %d Hz (the engine answered in %.1f ms).",
                       r.samples.size() / static_cast<double>(r.sample_rate_hz), r.sample_rate_hz, r.first_audio_ms);
            post_status(dlg, status_id, msg);
            play(r.samples, r.sample_rate_hz);
        });
    }

    void stop()
    {
        stop_ = true;
        {
            std::lock_guard<std::mutex> g(m_);
            if (wo_) waveOutReset(wo_);
        }
        if (thread_.joinable()) thread_.join();
    }

private:
    std::thread thread_;
    std::atomic<bool> stop_{false};
    std::mutex m_;
    HWAVEOUT wo_ = nullptr;

    void play(const std::vector<int16_t>& pcm, int hz)
    {
        if (pcm.empty() || stop_) return;
        WAVEFORMATEX fmt{WAVE_FORMAT_PCM, 1, static_cast<DWORD>(hz), static_cast<DWORD>(hz) * 2, 2, 16, 0};
        HANDLE done = CreateEventW(nullptr, FALSE, FALSE, nullptr);
        HWAVEOUT wo = nullptr;
        if (waveOutOpen(&wo, WAVE_MAPPER, &fmt, reinterpret_cast<DWORD_PTR>(done), 0, CALLBACK_EVENT) !=
            MMSYSERR_NOERROR) {
            CloseHandle(done);
            return;
        }
        {
            std::lock_guard<std::mutex> g(m_);
            wo_ = wo;
        }
        WAVEHDR h{};
        h.lpData = reinterpret_cast<LPSTR>(const_cast<int16_t*>(pcm.data()));
        h.dwBufferLength = static_cast<DWORD>(pcm.size() * 2);
        waveOutPrepareHeader(wo, &h, sizeof h);
        waveOutWrite(wo, &h, sizeof h);
        while (!(h.dwFlags & WHDR_DONE) && !stop_) WaitForSingleObject(done, 100);
        {
            std::lock_guard<std::mutex> g(m_);
            waveOutReset(wo);
            wo_ = nullptr;
        }
        waveOutUnprepareHeader(wo, &h, sizeof h);
        waveOutClose(wo);
        CloseHandle(done);
    }
};

Speaker g_speaker;

// ---- the Voices page ----------------------------------------------------------------

struct VoiceControl
{
    int edit, spin, param;
};
const VoiceControl kVoiceEdits[] = {
    {IDC_HEADSIZE, IDC_HEADSIZE_SPIN, 1},       {IDC_PITCH, IDC_PITCH_SPIN, 2},
    {IDC_INFLECTION, IDC_INFLECTION_SPIN, 3},   {IDC_ROUGHNESS, IDC_ROUGHNESS_SPIN, 4},
    {IDC_BREATHINESS, IDC_BREATHINESS_SPIN, 5}, {IDC_SPEED, IDC_SPEED_SPIN, 6},
    {IDC_VOLUME, IDC_VOLUME_SPIN, 7},
};

// Starts true: a dialog gets change notifications before WM_INITDIALOG (spin
// buttons push "0" into their edits while being created), and saving from a
// half-built page would write that over the real settings.
bool g_voices_loading = true;
unsigned g_voices_generation = 0;

const LanguageInfo* voices_language(HWND dlg)
{
    const int i = combo_data(dlg, IDC_LANGUAGE, -1);
    return (i >= 0 && i < static_cast<int>(g_langs.size())) ? &g_langs[static_cast<size_t>(i)] : nullptr;
}

void preset_defaults(const LanguageInfo& l, int preset, int out[8])
{
    Settings plain = g_s;
    plain.voices.clear();
    effective_voice(l, preset, plain, out);
}

void load_voice_values(HWND dlg)
{
    const LanguageInfo* l = voices_language(dlg);
    if (!l) return;
    const int preset = combo_data(dlg, IDC_VOICE, 1);
    int v[8];
    effective_voice(*l, preset, g_s, v);
    const bool was = g_voices_loading;
    g_voices_loading = true;
    combo_select(dlg, IDC_GENDER, v[0]);
    for (const auto& c : kVoiceEdits) SetDlgItemInt(dlg, c.edit, static_cast<UINT>(v[c.param]), FALSE);
    g_voices_loading = was;
    const bool custom = g_s.voices.count(voice_key(l->tag, preset)) != 0;
    SetDlgItemTextW(dlg, IDC_VOICE_STATUS,
                    custom ? L"This voice has been adjusted. Changes are saved at once and heard in every program."
                           : L"This voice is as the engine ships it. Changes are saved at once and heard in every "
                             L"program.");
}

void fill_voices(HWND dlg, int keep_preset)
{
    SendDlgItemMessageW(dlg, IDC_VOICE, CB_RESETCONTENT, 0, 0);
    const LanguageInfo* l = voices_language(dlg);
    if (!l) return;
    for (const PresetVoice& p : l->voices) combo_add(dlg, IDC_VOICE, p.name, p.number);
    combo_select(dlg, IDC_VOICE, keep_preset);
}

void fill_languages(HWND dlg)
{
    const int keep = combo_data(dlg, IDC_LANGUAGE, 0);
    const std::wstring keep_tag = (keep >= 0 && keep < static_cast<int>(g_langs.size())) ? g_langs[keep].tag : L"";
    SendDlgItemMessageW(dlg, IDC_LANGUAGE, CB_RESETCONTENT, 0, 0);
    int select = 0;
    for (size_t i = 0; i < g_langs.size(); ++i) {
        combo_add(dlg, IDC_LANGUAGE, g_langs[i].name, static_cast<LPARAM>(i));
        if (g_langs[i].tag == keep_tag) select = static_cast<int>(i);
    }
    combo_select(dlg, IDC_LANGUAGE, select);
    g_voices_generation = g_langs_generation;
}

void store_voice(HWND dlg)
{
    if (g_voices_loading) return;
    const LanguageInfo* l = voices_language(dlg);
    if (!l) return;
    const int preset = combo_data(dlg, IDC_VOICE, 1);
    int def[8];
    preset_defaults(*l, preset, def);
    int v[8];
    v[0] = combo_data(dlg, IDC_GENDER, def[0]);
    for (const auto& c : kVoiceEdits) v[c.param] = read_int(dlg, c.edit, 0, kVoiceParamMax[c.param], def[c.param]);
    VoiceOverride o;
    for (int i = 0; i < 8; ++i) {
        if (v[i] != def[i]) {
            o.set[i] = true;
            o.value[i] = v[i];
        }
    }
    const std::wstring key = voice_key(l->tag, preset);
    if (o.any()) g_s.voices[key] = o;
    else g_s.voices.erase(key);
    save();
    SetDlgItemTextW(dlg, IDC_VOICE_STATUS,
                    o.any() ? L"This voice has been adjusted. Changes are saved at once and heard in every program."
                            : L"This voice is as the engine ships it.");
}

INT_PTR CALLBACK voices_proc(HWND dlg, UINT msg, WPARAM wp, LPARAM lp)
{
    switch (msg) {
    case WM_INITDIALOG:
        g_voices_loading = true;
        g_sheet = GetParent(dlg);
        setup_sheet_buttons(g_sheet);
        for (const auto& c : kVoiceEdits) spin_range(dlg, c.spin, 0, kVoiceParamMax[c.param]);
        combo_add(dlg, IDC_GENDER, L"Male", 0);
        combo_add(dlg, IDC_GENDER, L"Female", 1);
        fill_languages(dlg);
        fill_voices(dlg, 1);
        load_voice_values(dlg);
        if (const LanguageInfo* l = voices_language(dlg)) SetDlgItemTextW(dlg, IDC_TESTTEXT, sample_for(*l).c_str());
        g_voices_loading = false;
        return TRUE;
    case WM_COMMAND: {
        const int id = LOWORD(wp), code = HIWORD(wp);
        if (id == IDC_LANGUAGE && code == CBN_SELCHANGE) {
            g_voices_loading = true;
            fill_voices(dlg, combo_data(dlg, IDC_VOICE, 1));
            load_voice_values(dlg);
            if (const LanguageInfo* l = voices_language(dlg)) SetDlgItemTextW(dlg, IDC_TESTTEXT, sample_for(*l).c_str());
            g_voices_loading = false;
        } else if (id == IDC_VOICE && code == CBN_SELCHANGE) {
            load_voice_values(dlg);
        } else if (id == IDC_GENDER && code == CBN_SELCHANGE) {
            store_voice(dlg);
        } else if (code == EN_CHANGE) {
            for (const auto& c : kVoiceEdits) {
                if (c.edit == id) store_voice(dlg);
            }
        } else if (code == EN_KILLFOCUS) {
            // Show the value that was kept when the one typed was out of range.
            for (const auto& c : kVoiceEdits) {
                if (c.edit != id) continue;
                const int v = read_int(dlg, id, 0, kVoiceParamMax[c.param], 0);
                g_voices_loading = true;
                SetDlgItemInt(dlg, id, static_cast<UINT>(v), FALSE);
                g_voices_loading = false;
            }
        } else if (id == IDC_RESTORE && code == BN_CLICKED) {
            if (const LanguageInfo* l = voices_language(dlg)) {
                g_s.voices.erase(voice_key(l->tag, combo_data(dlg, IDC_VOICE, 1)));
                save();
                load_voice_values(dlg);
            }
        } else if (id == IDC_SPEAK && code == BN_CLICKED) {
            if (const LanguageInfo* l = voices_language(dlg)) {
                wchar_t text[2048];
                GetDlgItemTextW(dlg, IDC_TESTTEXT, text, 2048);
                SetDlgItemTextW(dlg, IDC_VOICE_STATUS, L"Speaking...");
                g_speaker.speak(dlg, IDC_VOICE_STATUS, *l, combo_data(dlg, IDC_VOICE, 1),
                                text[0] ? text : sample_for(*l));
            }
        } else if (id == IDC_STOP && code == BN_CLICKED) {
            g_speaker.stop();
            SetDlgItemTextW(dlg, IDC_VOICE_STATUS, L"Stopped.");
        }
        return TRUE;
    }
    case WM_NOTIFY:
        if (reinterpret_cast<NMHDR*>(lp)->code == PSN_SETACTIVE && g_voices_generation != g_langs_generation) {
            g_voices_loading = true;
            fill_languages(dlg);
            fill_voices(dlg, combo_data(dlg, IDC_VOICE, 1));
            load_voice_values(dlg);
            g_voices_loading = false;
        }
        return FALSE;
    case WM_APP_STATUS: {
        std::unique_ptr<std::wstring> text(reinterpret_cast<std::wstring*>(lp));
        SetDlgItemTextW(dlg, static_cast<int>(wp), text->c_str());
        return TRUE;
    }
    }
    return FALSE;
}

// ---- the Speech page ----------------------------------------------------------------

bool g_speech_loading = true;

void load_speech(HWND dlg)
{
    g_speech_loading = true;
    combo_select(dlg, IDC_SAMPLERATE, g_s.sample_rate);
    const wchar_t* const kResamplers[] = {L"sinc", L"cubic", L"linear", L"hold", L"none"};
    for (int i = 0; i < 5; ++i) {
        if (_wcsicmp(g_s.resampler.c_str(), kResamplers[i]) == 0) combo_select(dlg, IDC_RESAMPLER, i);
    }
    CheckDlgButton(dlg, IDC_NOISE, g_s.noise_shaping ? BST_CHECKED : BST_UNCHECKED);
    SetDlgItemInt(dlg, IDC_MAXSPEED, static_cast<UINT>(g_s.max_speed), FALSE);
    SetDlgItemInt(dlg, IDC_MINSPEED, static_cast<UINT>(g_s.min_speed), FALSE);
    CheckDlgButton(dlg, IDC_BOOST, g_s.rate_boost ? BST_CHECKED : BST_UNCHECKED);
    SetDlgItemInt(dlg, IDC_PITCHSTEP, static_cast<UINT>(g_s.pitch_step), FALSE);
    CheckDlgButton(dlg, IDC_ABBREVIATIONS, g_s.abbreviations ? BST_CHECKED : BST_UNCHECKED);
    combo_select(dlg, IDC_NUMBERS, g_s.number_mode);
    combo_select(dlg, IDC_TEXTMODE, g_s.text_mode);
    CheckDlgButton(dlg, IDC_ANNOTATIONS, g_s.annotations ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(dlg, IDC_HETERONYMS, g_s.heteronyms ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(dlg, IDC_SYMBOLS, g_s.spell_lone_symbols ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(dlg, IDC_DICTIONARIES, g_s.user_dictionaries ? BST_CHECKED : BST_UNCHECKED);
    g_speech_loading = false;
}

void store_speech(HWND dlg)
{
    if (g_speech_loading) return;
    g_s.sample_rate = combo_data(dlg, IDC_SAMPLERATE, 1);
    const wchar_t* const kResamplers[] = {L"sinc", L"cubic", L"linear", L"hold", L"none"};
    g_s.resampler = kResamplers[std::max(0, std::min(4, combo_data(dlg, IDC_RESAMPLER, 0)))];
    g_s.noise_shaping = IsDlgButtonChecked(dlg, IDC_NOISE) == BST_CHECKED;
    g_s.max_speed = read_int(dlg, IDC_MAXSPEED, 50, 250, g_s.max_speed);
    g_s.min_speed = read_int(dlg, IDC_MINSPEED, 0, 100, g_s.min_speed);
    g_s.rate_boost = IsDlgButtonChecked(dlg, IDC_BOOST) == BST_CHECKED;
    g_s.pitch_step = read_int(dlg, IDC_PITCHSTEP, 0, 10, g_s.pitch_step);
    g_s.abbreviations = IsDlgButtonChecked(dlg, IDC_ABBREVIATIONS) == BST_CHECKED;
    g_s.number_mode = combo_data(dlg, IDC_NUMBERS, 1);
    g_s.text_mode = combo_data(dlg, IDC_TEXTMODE, 0);
    g_s.annotations = IsDlgButtonChecked(dlg, IDC_ANNOTATIONS) == BST_CHECKED;
    g_s.heteronyms = IsDlgButtonChecked(dlg, IDC_HETERONYMS) == BST_CHECKED;
    g_s.spell_lone_symbols = IsDlgButtonChecked(dlg, IDC_SYMBOLS) == BST_CHECKED;
    g_s.user_dictionaries = IsDlgButtonChecked(dlg, IDC_DICTIONARIES) == BST_CHECKED;
    save();
    SetDlgItemTextW(dlg, IDC_SPEECH_STATUS, L"Saved. Every OpenEVV voice uses this from its next utterance.");
}

INT_PTR CALLBACK speech_proc(HWND dlg, UINT msg, WPARAM wp, LPARAM)
{
    switch (msg) {
    case WM_INITDIALOG:
        g_speech_loading = true;
        for (const auto& r : kSampleRates) {
            wchar_t t[64];
            swprintf_s(t, L"%d Hz%s", r.hz, r.hz == 11025 ? L" (the engine's own)" : (r.hz == 8000 ? L" (telephone)" : L""));
            combo_add(dlg, IDC_SAMPLERATE, t, r.eci);
        }
        combo_add(dlg, IDC_RESAMPLER, L"Windowed sinc (clean, the default)", 0);
        combo_add(dlg, IDC_RESAMPLER, L"Cubic", 1);
        combo_add(dlg, IDC_RESAMPLER, L"Linear", 2);
        combo_add(dlg, IDC_RESAMPLER, L"Sample and hold (the vintage sound)", 3);
        combo_add(dlg, IDC_RESAMPLER, L"None: synthesise at the rate itself", 4);
        spin_range(dlg, IDC_MAXSPEED_SPIN, 50, 250);
        spin_range(dlg, IDC_MINSPEED_SPIN, 0, 100);
        spin_range(dlg, IDC_PITCHSTEP_SPIN, 0, 10);
        combo_add(dlg, IDC_NUMBERS, L"Years and pairs: 1999 as nineteen ninety-nine", 1);
        combo_add(dlg, IDC_NUMBERS, L"Whole numbers: 1999 as one thousand nine hundred...", 0);
        combo_add(dlg, IDC_TEXTMODE, L"Normal", 0);
        combo_add(dlg, IDC_TEXTMODE, L"Spell letters and digits", 1);
        combo_add(dlg, IDC_TEXTMODE, L"Spell everything, punctuation included", 2);
        combo_add(dlg, IDC_TEXTMODE, L"Spell with the radio alphabet", 3);
        load_speech(dlg);
        SetDlgItemTextW(dlg, IDC_SPEECH_STATUS,
                        L"These apply to every OpenEVV voice. Each change is saved and heard at once.");
        return TRUE;
    case WM_COMMAND: {
        const int id = LOWORD(wp), code = HIWORD(wp);
        if (id == IDC_SPEECH_DEFAULTS && code == BN_CLICKED) {
            const auto voices = g_s.voices;
            const int log_level = g_s.log_level;
            g_s = Settings{};
            g_s.voices = voices;
            g_s.log_level = log_level;
            save();
            load_speech(dlg);
            SetDlgItemTextW(dlg, IDC_SPEECH_STATUS, L"Speech settings restored to their defaults.");
        } else if ((code == CBN_SELCHANGE) || (code == BN_CLICKED && id != IDC_SPEECH_DEFAULTS) ||
                   (code == EN_CHANGE && (id == IDC_MAXSPEED || id == IDC_MINSPEED || id == IDC_PITCHSTEP))) {
            store_speech(dlg);
        }
        return TRUE;
    }
    }
    return FALSE;
}

// ---- the Languages page ------------------------------------------------------------------

bool in_user_dir(const LanguageInfo& l)
{
    const std::wstring u = user_language_dir();
    return !u.empty() && _wcsnicmp(l.dir.c_str(), u.c_str(), u.size()) == 0;
}

const LanguageInfo* selected_pack(HWND dlg)
{
    const LRESULT i = SendDlgItemMessageW(dlg, IDC_LANGLIST, LB_GETCURSEL, 0, 0);
    if (i == LB_ERR || i >= static_cast<LRESULT>(g_langs.size())) return nullptr;
    return &g_langs[static_cast<size_t>(i)];
}

void show_pack_info(HWND dlg)
{
    const LanguageInfo* l = selected_pack(dlg);
    if (!l) {
        SetDlgItemTextW(dlg, IDC_LANGINFO, L"");
        return;
    }
    wchar_t info[1200];
    swprintf_s(info, L"%s (%s, %s): ECI language 0x%05x, code page %u. 32-bit module %s, 64-bit module %s.\r\nFolder: %s",
               l->name.c_str(), l->tag.c_str(), l->locale.c_str(), l->id, l->codepage,
               l->module32.empty() ? L"missing" : L"present", l->module64.empty() ? L"missing" : L"present",
               l->dir.c_str());
    SetDlgItemTextW(dlg, IDC_LANGINFO, info);
}

void fill_pack_list(HWND dlg, const std::wstring& select_tag = L"")
{
    HWND list = GetDlgItem(dlg, IDC_LANGLIST);
    SendMessageW(list, LB_RESETCONTENT, 0, 0);
    int select = 0;
    for (size_t i = 0; i < g_langs.size(); ++i) {
        const LanguageInfo& l = g_langs[i];
        const std::wstring line = l.name + L" (" + l.tag + L"): " + std::to_wstring(l.voices.size()) + L" voices, " +
                                  (in_user_dir(l) ? L"added by you" : L"installed with OpenEVV");
        SendMessageW(list, LB_ADDSTRING, 0, reinterpret_cast<LPARAM>(line.c_str()));
        if (!select_tag.empty() && l.tag == select_tag) select = static_cast<int>(i);
    }
    SendMessageW(list, LB_SETCURSEL, static_cast<WPARAM>(select), 0);
    show_pack_info(dlg);
}

bool copy_tree(const std::wstring& from, const std::wstring& to)
{
    if (!ensure_dir(to)) return false;
    WIN32_FIND_DATAW fd;
    HANDLE h = FindFirstFileW((from + L"\\*").c_str(), &fd);
    if (h == INVALID_HANDLE_VALUE) return false;
    bool ok = true;
    do {
        if (fd.cFileName[0] == L'.' && (!fd.cFileName[1] || (fd.cFileName[1] == L'.' && !fd.cFileName[2]))) continue;
        const std::wstring a = from + L"\\" + fd.cFileName, b = to + L"\\" + fd.cFileName;
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) ok = copy_tree(a, b) && ok;
        else ok = CopyFileW(a.c_str(), b.c_str(), FALSE) && ok;
    } while (FindNextFileW(h, &fd));
    FindClose(h);
    return ok;
}

// To the recycle bin, so a mistake can be undone -- unless it is our own
// scratch folder.
bool delete_tree(const std::wstring& dir, HWND owner, bool recycle = true)
{
    std::wstring from = dir;
    from.push_back(L'\0');
    from.push_back(L'\0');
    SHFILEOPSTRUCTW op{};
    op.hwnd = owner;
    op.wFunc = FO_DELETE;
    op.pFrom = from.c_str();
    op.fFlags = (recycle ? FOF_ALLOWUNDO : 0) | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI;
    return SHFileOperationW(&op) == 0 && !op.fAnyOperationsAborted && !dir_exists(dir);
}

// A language pack as it is downloaded: a .zip, or language.ini inside an
// extracted folder.
std::wstring pick_pack(HWND owner)
{
    std::wstring out;
    IFileOpenDialog* d = nullptr;
    if (FAILED(CoCreateInstance(CLSID_FileOpenDialog, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&d)))) return out;
    const COMDLG_FILTERSPEC types[] = {{L"Language packs (.zip or language.ini)", L"*.zip;language.ini"},
                                       {L"All files", L"*.*"}};
    d->SetFileTypes(2, types);
    DWORD opts = 0;
    d->GetOptions(&opts);
    d->SetOptions(opts | FOS_FORCEFILESYSTEM | FOS_FILEMUSTEXIST);
    d->SetTitle(L"Choose a language pack: the .zip you downloaded, or language.ini in an extracted pack");
    if (SUCCEEDED(d->Show(owner))) {
        IShellItem* item = nullptr;
        if (SUCCEEDED(d->GetResult(&item))) {
            wchar_t* path = nullptr;
            if (SUCCEEDED(item->GetDisplayName(SIGDN_FILESYSPATH, &path)) && path) {
                out = path;
                CoTaskMemFree(path);
            }
            item->Release();
        }
    }
    d->Release();
    return out;
}

bool ends_with_i(const std::wstring& s, const wchar_t* tail)
{
    const size_t n = wcslen(tail);
    return s.size() >= n && _wcsicmp(s.c_str() + s.size() - n, tail) == 0;
}

// tar.exe has been part of Windows since Windows 10 version 1803; older
// systems go through the shell's own zip folder.
bool extract_zip(const std::wstring& zip, const std::wstring& dest)
{
    if (!ensure_dir(dest)) return false;
    wchar_t sys[MAX_PATH];
    GetSystemDirectoryW(sys, MAX_PATH);
    const std::wstring tar = std::wstring(sys) + L"\\tar.exe";
    if (file_exists(tar)) {
        std::wstring cmd = L"\"" + tar + L"\" -xf \"" + zip + L"\" -C \"" + dest + L"\"";
        STARTUPINFOW si{sizeof si};
        PROCESS_INFORMATION pi{};
        if (CreateProcessW(tar.c_str(), cmd.data(), nullptr, nullptr, FALSE, CREATE_NO_WINDOW, nullptr, nullptr, &si,
                           &pi)) {
            WaitForSingleObject(pi.hProcess, 120000);
            DWORD code = 1;
            GetExitCodeProcess(pi.hProcess, &code);
            CloseHandle(pi.hThread);
            CloseHandle(pi.hProcess);
            if (code == 0) return true;
        }
    }
    // The shell: Folder(zip).Items() copied into Folder(dest).
    bool ok = false;
    IShellDispatch* shell = nullptr;
    if (SUCCEEDED(CoCreateInstance(CLSID_Shell, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&shell)))) {
        VARIANT vz, vd;
        vz.vt = VT_BSTR;
        vz.bstrVal = SysAllocString(zip.c_str());
        vd.vt = VT_BSTR;
        vd.bstrVal = SysAllocString(dest.c_str());
        Folder* from = nullptr;
        Folder* to = nullptr;
        if (SUCCEEDED(shell->NameSpace(vz, &from)) && from && SUCCEEDED(shell->NameSpace(vd, &to)) && to) {
            FolderItems* items = nullptr;
            if (SUCCEEDED(from->Items(&items)) && items) {
                VARIANT vi, vopt;
                vi.vt = VT_DISPATCH;
                vi.pdispVal = items;
                vopt.vt = VT_I4;
                vopt.lVal = FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI;
                ok = SUCCEEDED(to->CopyHere(vi, vopt));
                items->Release();
            }
        }
        if (from) from->Release();
        if (to) to->Release();
        VariantClear(&vz);
        VariantClear(&vd);
        shell->Release();
    }
    return ok;
}

// Folders under root (root included) holding language.ini, two levels deep:
// a zip may hold one pack at its top, a folder with one pack, or several.
void find_packs(const std::wstring& root, int depth, std::vector<std::wstring>& out)
{
    if (file_exists(root + L"\\language.ini")) {
        out.push_back(root);
        return;
    }
    if (depth <= 0) return;
    WIN32_FIND_DATAW fd;
    HANDLE h = FindFirstFileW((root + L"\\*").c_str(), &fd);
    if (h == INVALID_HANDLE_VALUE) return;
    do {
        if ((fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) && fd.cFileName[0] != L'.') {
            find_packs(root + L"\\" + fd.cFileName, depth - 1, out);
        }
    } while (FindNextFileW(h, &fd));
    FindClose(h);
}

// Installs every pack found at path (a .zip, a language.ini, or a folder) into
// the user's language folder. `owner` null means no questions: replace.
// Returns how many were added; `message` says what happened, in words.
int install_packs(const std::wstring& path, HWND owner, std::wstring& message)
{
    std::wstring root = path, temp;
    if (ends_with_i(path, L".zip")) {
        wchar_t tmp[MAX_PATH];
        GetTempPathW(MAX_PATH, tmp);
        temp = std::wstring(tmp) + L"openevv-pack-" + std::to_wstring(GetTickCount64());
        if (!extract_zip(path, temp)) {
            message = L"The zip file could not be opened: " + path;
            return 0;
        }
        root = temp;
    } else if (ends_with_i(path, L"language.ini")) {
        root = path.substr(0, path.find_last_of(L"\\/"));
    }
    std::vector<std::wstring> dirs;
    find_packs(root, 2, dirs);
    int added = 0;
    std::wstring names;
    if (dirs.empty()) message = L"No language pack (a folder holding language.ini) was found in " + path;
    for (const std::wstring& src : dirs) {
        LanguageInfo li;
        std::wstring problem;
        if (!read_language_pack(src, li, problem)) {
            message += L"Not a usable language pack: " + problem + L"\n";
            continue;
        }
        const std::wstring dst = user_language_dir() + L"\\" + li.tag;
        if (dir_exists(dst)) {
            if (owner && MessageBoxW(owner, (L"A language pack called " + li.tag + L" was added before. Replace it?").c_str(),
                                     L"OpenEVV", MB_YESNO | MB_ICONQUESTION) != IDYES) {
                continue;
            }
            if (!delete_tree(dst, owner)) {
                message += L"The earlier " + li.name + L" pack could not be replaced: a program is probably speaking "
                           L"with it. Close programs using OpenEVV voices and try again.\n";
                continue;
            }
        }
        if (!copy_tree(src, dst)) {
            message += L"The pack could not be copied to " + dst + L"\n";
            continue;
        }
        log::write(log::kStandard, "languages: added %S from %S", li.tag.c_str(), path.c_str());
        names += (names.empty() ? L"" : L", ") + li.name;
        ++added;
    }
    if (!temp.empty()) delete_tree(temp, nullptr, false);
    if (added) {
        message = names + (added == 1 ? L" was" : L" were") +
                  L" added. The voices are in every SAPI 5 program's voice list now.\n" + message;
    }
    return added;
}

void add_pack(HWND dlg)
{
    const std::wstring src = pick_pack(dlg);
    if (src.empty()) return;
    std::wstring message;
    const int added = install_packs(src, dlg, message);
    reload_languages();
    fill_pack_list(dlg);
    MessageBoxW(dlg, message.c_str(), L"OpenEVV", MB_OK | (added ? MB_ICONINFORMATION : MB_ICONWARNING));
}

void remove_pack(HWND dlg)
{
    const LanguageInfo* l = selected_pack(dlg);
    if (!l) return;
    const LanguageInfo pack = *l;
    if (MessageBoxW(dlg,
                    (L"Remove " + pack.name + L" and its eight voices? The folder goes to the Recycle Bin.\n\n" + pack.dir)
                        .c_str(),
                    L"OpenEVV", MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2) != IDYES) {
        return;
    }
    g_speaker.stop();
    HostPool::get().shutdown_all(); // our own hosts may have the module open
    bool ok;
    if (in_user_dir(pack)) {
        ok = delete_tree(pack.dir, dlg);
    } else {
        // Installed with OpenEVV, under Program Files: that needs an administrator.
        const std::wstring args = L"--remove-pack \"" + pack.dir + L"\"";
        SHELLEXECUTEINFOW sei{sizeof sei};
        sei.fMask = SEE_MASK_NOCLOSEPROCESS;
        sei.hwnd = dlg;
        sei.lpVerb = L"runas";
        const std::wstring exe = exe_path();
        sei.lpFile = exe.c_str();
        sei.lpParameters = args.c_str();
        sei.nShow = SW_HIDE;
        ok = ShellExecuteExW(&sei) != FALSE;
        if (ok && sei.hProcess) {
            WaitForSingleObject(sei.hProcess, 60000);
            DWORD code = 1;
            GetExitCodeProcess(sei.hProcess, &code);
            CloseHandle(sei.hProcess);
            ok = code == 0;
        }
    }
    log::write(log::kStandard, "languages: remove %S (%S): %s", pack.tag.c_str(), pack.dir.c_str(), ok ? "done" : "failed");
    reload_languages();
    fill_pack_list(dlg);
    if (!ok) {
        MessageBoxW(dlg, L"The language could not be removed. A program may be speaking with one of its voices: "
                         L"close programs using OpenEVV voices and try again.",
                    L"OpenEVV", MB_OK | MB_ICONWARNING);
    }
}

void edit_dictionary(HWND dlg, const wchar_t* file)
{
    const LanguageInfo* l = selected_pack(dlg);
    if (!l) return;
    const std::wstring dir = user_dictionary_dir(l->tag);
    if (!ensure_dir(dir)) {
        MessageBoxW(dlg, (L"Cannot create " + dir).c_str(), L"OpenEVV", MB_OK | MB_ICONERROR);
        return;
    }
    const std::wstring path = dir + L"\\" + file;
    if (!file_exists(path)) {
        HANDLE h = CreateFileW(path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
        if (h != INVALID_HANDLE_VALUE) CloseHandle(h);
    }
    std::wstring cmd = L"notepad.exe \"" + path + L"\"";
    STARTUPINFOW si{sizeof si};
    PROCESS_INFORMATION pi{};
    if (CreateProcessW(nullptr, cmd.data(), nullptr, nullptr, FALSE, 0, nullptr, nullptr, &si, &pi)) {
        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);
    }
}

INT_PTR CALLBACK languages_proc(HWND dlg, UINT msg, WPARAM wp, LPARAM lp)
{
    switch (msg) {
    case WM_INITDIALOG:
        fill_pack_list(dlg);
        return TRUE;
    case WM_COMMAND: {
        const int id = LOWORD(wp), code = HIWORD(wp);
        if (id == IDC_LANGLIST && code == LBN_SELCHANGE) show_pack_info(dlg);
        else if (id == IDC_ADDLANG && code == BN_CLICKED) add_pack(dlg);
        else if (id == IDC_REMOVELANG && code == BN_CLICKED) remove_pack(dlg);
        else if (id == IDC_OPENLANGS && code == BN_CLICKED) {
            const std::wstring d = user_language_dir();
            ensure_dir(d);
            ShellExecuteW(dlg, L"open", d.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
        } else if (id == IDC_DICT_MAIN && code == BN_CLICKED) edit_dictionary(dlg, L"main.dic");
        else if (id == IDC_DICT_ROOT && code == BN_CLICKED) edit_dictionary(dlg, L"root.dic");
        else if (id == IDC_DICT_ABBR && code == BN_CLICKED) edit_dictionary(dlg, L"abbr.dic");
        return TRUE;
    }
    case WM_NOTIFY:
        if (reinterpret_cast<NMHDR*>(lp)->code == PSN_SETACTIVE) {
            reload_languages();
            fill_pack_list(dlg);
        }
        return FALSE;
    }
    return FALSE;
}

// ---- the Diagnostics page -----------------------------------------------------------------

std::thread g_selftest;

INT_PTR CALLBACK diagnostics_proc(HWND dlg, UINT msg, WPARAM wp, LPARAM lp)
{
    switch (msg) {
    case WM_INITDIALOG: {
        combo_add(dlg, IDC_LOGLEVEL, L"Off", 0);
        combo_add(dlg, IDC_LOGLEVEL, L"Standard (no spoken text)", 1);
        combo_add(dlg, IDC_LOGLEVEL, L"Full (includes the spoken text)", 2);
        combo_select(dlg, IDC_LOGLEVEL, g_s.log_level);
        wchar_t about[1600];
        swprintf_s(about,
                   L"OpenEVV SAPI5 %s, %s. Engine: openevv %S, the Embedded ViaVoice (Eloquence) engine rebuilt as C. "
                   L"%zu languages installed.\r\nSettings: %s\r\nLogs: %s",
                   EVV_VERSION_WSTRING, sizeof(void*) == 8 ? L"64-bit" : L"32-bit", EVV_ENGINE_COMMIT, g_langs.size(),
                   settings_path().c_str(), log::directory().c_str());
        SetDlgItemTextW(dlg, IDC_ABOUT, about);
        return TRUE;
    }
    case WM_COMMAND: {
        const int id = LOWORD(wp), code = HIWORD(wp);
        if (id == IDC_LOGLEVEL && code == CBN_SELCHANGE) {
            g_s.log_level = combo_data(dlg, IDC_LOGLEVEL, 1);
            save();
        } else if (id == IDC_OPENLOGS && code == BN_CLICKED) {
            ShellExecuteW(dlg, L"open", log::directory().c_str(), nullptr, nullptr, SW_SHOWNORMAL);
        } else if (id == IDC_SELFTEST && code == BN_CLICKED) {
            if (g_selftest.joinable()) g_selftest.join();
            g_speaker.stop();
            EnableWindow(GetDlgItem(dlg, IDC_SELFTEST), FALSE);
            SetDlgItemTextW(dlg, IDC_SELFTEST_RESULT, L"Running: every voice of every language is spoken into memory...");
            g_selftest = std::thread([dlg] {
                const SelfTestResult r = run_selftest(true, true);
                PostMessageW(dlg, WM_APP_SELFTEST, 0, reinterpret_cast<LPARAM>(new std::wstring(r.report)));
            });
        }
        return TRUE;
    }
    case WM_APP_SELFTEST: {
        std::unique_ptr<std::wstring> text(reinterpret_cast<std::wstring*>(lp));
        SetDlgItemTextW(dlg, IDC_SELFTEST_RESULT, text->c_str());
        EnableWindow(GetDlgItem(dlg, IDC_SELFTEST), TRUE);
        SetFocus(GetDlgItem(dlg, IDC_SELFTEST_RESULT));
        return TRUE;
    }
    }
    return FALSE;
}

int CALLBACK sheet_callback(HWND sheet, UINT msg, LPARAM)
{
    if (msg == PSCB_INITIALIZED) g_sheet = sheet;
    return 0;
}

int run_window(HINSTANCE inst)
{
    PROPSHEETPAGEW pages[4] = {};
    const struct
    {
        int id;
        DLGPROC proc;
    } kPages[4] = {{IDD_VOICES, voices_proc}, {IDD_SPEECH, speech_proc}, {IDD_LANGUAGES, languages_proc},
                   {IDD_DIAGNOSTICS, diagnostics_proc}};
    for (int i = 0; i < 4; ++i) {
        pages[i].dwSize = sizeof pages[i];
        pages[i].hInstance = inst;
        pages[i].pszTemplate = MAKEINTRESOURCEW(kPages[i].id);
        pages[i].pfnDlgProc = kPages[i].proc;
    }
    PROPSHEETHEADERW h{};
    h.dwSize = sizeof h;
    h.dwFlags = PSH_PROPSHEETPAGE | PSH_NOAPPLYNOW | PSH_USECALLBACK | PSH_NOCONTEXTHELP;
    h.hInstance = inst;
    h.pszCaption = L"OpenEVV SAPI5 Configuration";
    h.nPages = 4;
    h.ppsp = pages;
    h.pfnCallback = sheet_callback;
    PropertySheetW(&h);
    g_speaker.stop();
    if (g_selftest.joinable()) g_selftest.join();
    return 0;
}

int run_selftest_cli(const std::wstring& report_path, bool hosts, bool sapi)
{
    const SelfTestResult r = run_selftest(hosts, sapi);
    std::wstring path = report_path;
    if (path.empty()) path = log::directory() + L"\\selftest.txt";
    const std::string bytes = wide_to_utf8(r.report);
    HANDLE f = CreateFileW(path.c_str(), GENERIC_WRITE, FILE_SHARE_READ, nullptr, CREATE_ALWAYS, 0, nullptr);
    if (f != INVALID_HANDLE_VALUE) {
        DWORD w = 0;
        WriteFile(f, "\xEF\xBB\xBF", 3, &w, nullptr);
        WriteFile(f, bytes.data(), static_cast<DWORD>(bytes.size()), &w, nullptr);
        CloseHandle(f);
    }
    return r.failures;
}

} // namespace

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE, PWSTR, int)
{
    int argc = 0;
    wchar_t** argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    std::wstring mode, arg;
    bool hosts = true, sapi = true;
    for (int i = 1; argv && i < argc; ++i) {
        const std::wstring a = argv[i];
        if (a == L"--selftest") mode = a;
        else if (a == L"--hosts-only") sapi = false;
        else if (a == L"--sapi-only") hosts = false;
        else if ((a == L"--report" || a == L"--remove-pack" || a == L"--add-pack") && i + 1 < argc) {
            if (a != L"--report") mode = a;
            arg = argv[++i];
        }
    }
    LocalFree(argv);

    log::init(L"config");
    g_s = load_settings();
    log::set_level(g_s.log_level);
    log::write(log::kStandard, "OpenEVV configuration %s (%s) started%s%S", EVV_VERSION_STRING,
               sizeof(void*) == 8 ? "64-bit" : "32-bit", mode.empty() ? "" : " with ",
               mode.empty() ? L"" : mode.c_str());

    if (mode == L"--remove-pack") {
        // Only a folder holding a language pack, and only inside a languages folder.
        LanguageInfo li;
        std::wstring problem;
        const bool is_pack = read_language_pack(arg, li, problem) || file_exists(arg + L"\\language.ini");
        const bool in_languages = arg.find(L"\\languages\\") != std::wstring::npos;
        if (!is_pack || !in_languages) return 2;
        return delete_tree(arg, nullptr) ? 0 : 1;
    }

    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    HostPool::get().add_user();
    int rc;
    if (mode == L"--selftest") {
        rc = run_selftest_cli(arg, hosts, sapi);
    } else if (mode == L"--add-pack") {
        std::wstring message;
        rc = install_packs(arg, nullptr, message) > 0 ? 0 : 1;
        log::write(log::kStandard, "languages: %S", message.c_str());
    } else {
        INITCOMMONCONTROLSEX icc{sizeof icc, ICC_STANDARD_CLASSES | ICC_UPDOWN_CLASS | ICC_TAB_CLASSES};
        InitCommonControlsEx(&icc);
        reload_languages();
        rc = run_window(inst);
    }
    HostPool::get().release_user();
    HostPool::get().shutdown_all();
    CoUninitialize();
    return rc;
}
