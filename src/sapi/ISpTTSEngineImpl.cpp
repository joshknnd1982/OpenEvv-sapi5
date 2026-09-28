#include "ISpTTSEngineImpl.hpp"

#include <algorithm>
#include <cwctype>
#include <mutex>
#include <new>
#include <vector>

#include "common/host_client.h"
#include "common/log.h"
#include "common/paths.h"
#include "common/text_codec.h"
#include "common/version.h"
#include "common/voice_math.h"
#include "common/eci_module.h"
#include "utils.hpp"

namespace evv {
namespace sapi {

namespace {

constexpr unsigned kHungAfterMs = 10000; // no word from a host for this long: it is replaced
constexpr unsigned kPollMs = 30;         // how often SAPI's actions are looked at while waiting

double now_ms()
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return 1000.0 * static_cast<double>(c.QuadPart) / static_cast<double>(f.QuadPart);
}

std::string narrow(const wchar_t* s, size_t n)
{
    return utils::wstring_to_string(s, n);
}

const char* action_name(SPVACTIONS a)
{
    switch (a) {
    case SPVA_Speak: return "speak";
    case SPVA_Silence: return "silence";
    case SPVA_Pronounce: return "pronounce";
    case SPVA_Bookmark: return "bookmark";
    case SPVA_SpellOut: return "spell";
    case SPVA_Section: return "section";
    case SPVA_ParseUnknownTag: return "unknown-tag";
    default: return "?";
    }
}

void init_logging_once()
{
    static std::once_flag once;
    std::call_once(once, [] {
#if defined(_WIN64)
        log::init(L"sapi-x64");
#else
        log::init(L"sapi-x86");
#endif
        log::set_level(load_settings().log_level);
        log::write(log::kStandard, "OpenEVV SAPI5 %s (%s, engine %s) loaded into %S", EVV_VERSION_STRING,
#if defined(_WIN64)
                   "64-bit",
#else
                   "32-bit",
#endif
                   EVV_ENGINE_COMMIT, utils::wstring_to_string(exe_path()).c_str());
    });
}

int eci_rate_for_hz(DWORD hz, int fallback)
{
    for (const auto& r : kSampleRates) {
        if (static_cast<DWORD>(r.hz) == hz) return r.eci;
    }
    return fallback;
}

bool is_space(wchar_t c)
{
    return iswspace(c) != 0 || c == 0x00A0;
}

bool ends_sentence(wchar_t c)
{
    return c == L'.' || c == L'!' || c == L'?' || c == 0x3002 /* 。 */ || c == 0xFF01 || c == 0xFF1F;
}

// What an index mark stands for, by its position in the table (mark n is
// entry n-1).
struct Marker
{
    enum Kind
    {
        Word,
        Sentence,
        Bookmark,
        Silence,
    } kind = Word;
    ULONG src = 0;
    ULONG len = 0;
    std::wstring text;
    ULONG ms = 0;
};

// One Speak() call.
class Session
{
public:
    Session(ISpTTSEngineSite* site, const LanguageInfo& lang, int preset, const Settings& s, int sample_rate_eci,
            log::Batch& lb)
        : site_(site), lang_(lang), s_(s), lb_(lb)
    {
        ULONGLONG interest = 0;
        site_->GetEventInterest(&interest);
        want_word_ = (interest & (1ULL << SPEI_WORD_BOUNDARY)) != 0;
        want_sentence_ = (interest & (1ULL << SPEI_SENTENCE_BOUNDARY)) != 0;
        want_bookmark_ = (interest & (1ULL << SPEI_TTS_BOOKMARK)) != 0;
        long r = 0;
        site_->GetRate(&r);
        site_rate_ = r;
        USHORT v = 100;
        site_->GetVolume(&v);
        site_volume_ = v;

        effective_voice(lang, preset, s, voice_);
        req_.head.sample_rate = sample_rate_eci;
        req_.head.text_mode = s.text_mode;
        req_.head.number_mode = s.number_mode;
        req_.head.dictionary = s.abbreviations ? 1 : 0;
        req_.head.input_type = s.annotations ? 1 : 0;
        req_.head.user_dicts = s.user_dictionaries ? 1 : 0;
        req_.head.preset = preset;
        for (int i = 0; i < 8; ++i) req_.head.voice[i] = voice_[i];
        bytes_per_sample_ = 2;
        rate_hz_ = sample_rate_hz(sample_rate_eci);
    }

    void fragment(const SPVTEXTFRAG* f)
    {
        ++fragments_;
        const SPVACTIONS a = f->State.eAction;
        if (log::enabled(log::kFull)) {
            lb_.add(log::kFull, "  fragment %s src=%lu len=%lu rateadj=%ld pitch=%ld vol=%u text=\"%s\"",
                    action_name(a), f->ulTextSrcOffset, f->ulTextLen, f->State.RateAdj, f->State.PitchAdj.MiddleAdj,
                    f->State.Volume, narrow(f->pTextStart, std::min<ULONG>(f->ulTextLen, 200)).c_str());
        }
        switch (a) {
        case SPVA_Bookmark: {
            Marker m;
            m.kind = Marker::Bookmark;
            m.src = f->ulTextSrcOffset;
            if (f->pTextStart) m.text.assign(f->pTextStart, f->ulTextLen);
            add_marker(std::move(m));
            break;
        }
        case SPVA_Silence: {
            Marker m;
            m.kind = Marker::Silence;
            m.ms = f->State.SilenceMSecs;
            add_marker(std::move(m));
            break;
        }
        case SPVA_Pronounce:
        case SPVA_Speak:
        case SPVA_SpellOut: {
            if (!f->pTextStart || f->ulTextLen == 0) break;
            prosody(f->State);
            const std::wstring text(f->pTextStart, f->ulTextLen);
            chars_ += f->ulTextLen;
            if (a == SPVA_SpellOut) {
                spell(text, f->ulTextSrcOffset);
            } else {
                speak(text, f->ulTextSrcOffset);
            }
            break;
        }
        default:
            break; // SPVA_Section, SPVA_ParseUnknownTag
        }
    }

    // Sends the request and plays what comes back. Returns false if the engine
    // failed (the host is replaced; the caller may retry once).
    bool run(bool allow_retry)
    {
        t0_ = now_ms();
        if (!has_text_) {
            // Only marks and pauses: nothing for the engine to do.
            for (const Marker& m : marks_) on_marker(m);
            return true;
        }
        std::string err;
        HostInfo info;
        auto utt = HostPool::get().speak(lang_, s_, req_, err, &info);
        if (!utt) {
            log::write(log::kStandard, "speak: %s", err.c_str());
            failed_ = true;
            return false;
        }
        host_ms_ = now_ms() - t0_;
        HostEvent ev;
        unsigned waited = 0;
        for (;;) {
            if (poll_actions()) {
                utt->cancel();
                break;
            }
            if (!utt->next(ev, kPollMs)) {
                waited += kPollMs;
                if (waited >= kHungAfterMs) {
                    log::write(log::kStandard, "speak: the engine host gave nothing for %u ms", waited);
                    utt->abandon();
                    failed_ = true;
                    return false;
                }
                continue;
            }
            waited = 0;
            if (ev.kind == HostEvent::kAudio) {
                write_audio(ev.samples.data(), ev.samples.size());
            } else if (ev.kind == HostEvent::kIndex) {
                if (ev.index >= 1 && static_cast<size_t>(ev.index) <= marks_.size()) {
                    on_marker(marks_[static_cast<size_t>(ev.index) - 1]);
                }
            } else {
                engine_first_audio_ms_ = ev.done.first_audio_ms;
                engine_total_ms_ = ev.done.total_ms;
                if (ev.done.status == proto::kDoneFailed) {
                    log::write(log::kStandard, "speak: engine failed: %s", ev.done.error);
                    failed_ = true;
                    return !(allow_retry && bytes_ == 0);
                }
                break;
            }
            if (write_failed_) {
                utt->cancel();
                break;
            }
        }
        finish_skip();
        return true;
    }

    bool aborted() const { return aborted_; }
    bool failed() const { return failed_ || write_failed_; }
    ULONGLONG bytes() const { return bytes_; }
    size_t fragments() const { return fragments_; }
    size_t chars() const { return chars_; }
    double first_audio_ms() const { return first_audio_ms_; }
    double engine_first_audio_ms() const { return engine_first_audio_ms_; }
    double host_ms() const { return host_ms_; }
    int rate_hz() const { return rate_hz_; }
    int speed() const { return cur_speed_; }
    void reset_for_retry()
    {
        failed_ = false;
    }

private:
    ISpTTSEngineSite* site_;
    const LanguageInfo& lang_;
    const Settings& s_;
    log::Batch& lb_;
    RequestBuilder req_;
    std::vector<Marker> marks_;
    int voice_[8] = {};
    bool want_word_ = false, want_sentence_ = false, want_bookmark_ = false;
    long site_rate_ = 0;
    USHORT site_volume_ = 100;
    bool started_ = false, has_text_ = false;
    int cur_speed_ = -1, cur_pitch_ = -1, cur_volume_ = -1;
    ULONGLONG bytes_ = 0;
    int bytes_per_sample_ = 2;
    int rate_hz_ = 11025;
    bool aborted_ = false, failed_ = false, write_failed_ = false;
    long skip_left_ = 0, skip_done_ = 0;
    bool skipping_ = false;
    size_t fragments_ = 0, chars_ = 0;
    double t0_ = 0, first_audio_ms_ = -1, engine_first_audio_ms_ = -1, engine_total_ms_ = 0, host_ms_ = 0;

    void finish_skip()
    {
        if (!skipping_) return;
        site_->CompleteSkip(skip_done_);
        skipping_ = false;
    }

    void add_marker(Marker m)
    {
        marks_.push_back(std::move(m));
        req_.index(static_cast<int32_t>(marks_.size()));
    }

    void prosody(const SPVSTATE& st)
    {
        const int speed = engine_speed(voice_[kVoiceSpeed], static_cast<int>(site_rate_ + st.RateAdj), s_);
        const int pitch = engine_pitch(voice_[kVoicePitchBaseline], st.PitchAdj.MiddleAdj, s_);
        const int volume = engine_volume(voice_[kVoiceVolume], site_volume_, st.Volume);
        if (!started_) {
            req_.head.voice[kVoiceSpeed] = speed;
            req_.head.voice[kVoicePitchBaseline] = pitch;
            req_.head.voice[kVoiceVolume] = volume;
            started_ = true;
        } else {
            if (speed != cur_speed_) req_.voice(kVoiceSpeed, speed);
            if (pitch != cur_pitch_) req_.voice(kVoicePitchBaseline, pitch);
            if (volume != cur_volume_) req_.voice(kVoiceVolume, volume);
        }
        cur_speed_ = speed;
        cur_pitch_ = pitch;
        cur_volume_ = volume;
    }

    void add_text(const std::wstring& t)
    {
        const std::string bytes = encode_text(t, lang_.codepage);
        if (bytes.empty()) return;
        req_.text(bytes);
        has_text_ = true;
    }

    void sentence_mark(ULONG src, ULONG len)
    {
        Marker m;
        m.kind = Marker::Sentence;
        m.src = src;
        m.len = len;
        add_marker(std::move(m));
    }

    // Plain text: a sentence mark at each sentence, and a word mark before
    // each word when the program wants word events. Marks do not change the
    // audio; each stretch between them is handed to the engine as it stands.
    void speak(const std::wstring& text, ULONG src)
    {
        // A lone character the engine would render as silence is named.
        size_t first = 0, last = text.size();
        while (first < last && is_space(text[first])) ++first;
        while (last > first && is_space(text[last - 1])) --last;
        if (last == first + 1 && s_.spell_lone_symbols) {
            const std::wstring name = symbol_name(text[first], lang_.tag);
            if (!name.empty()) {
                sentence_mark(src + static_cast<ULONG>(first), 1);
                if (want_word_) word_mark(src + static_cast<ULONG>(first), 1);
                add_text(name);
                return;
            }
        }

        size_t i = 0;
        const size_t n = text.size();
        size_t sentence_start = first;
        bool at_sentence_start = true;
        std::wstring pending;
        while (i < n) {
            // leading space belongs to the stretch before the next word
            size_t ws = i;
            while (ws < n && is_space(text[ws])) ++ws;
            if (ws >= n) {
                pending.append(text, i, n - i);
                break;
            }
            size_t we = ws;
            while (we < n && !is_space(text[we])) ++we;
            if (at_sentence_start) {
                if (!pending.empty()) {
                    add_text(pending);
                    pending.clear();
                }
                // Sentence length: up to the end of this sentence.
                size_t se = we;
                size_t probe = ws;
                while (probe < n) {
                    size_t e = probe;
                    while (e < n && !is_space(text[e])) ++e;
                    se = e;
                    size_t t = e;
                    while (t > probe && (text[t - 1] == L'"' || text[t - 1] == L'\'' || text[t - 1] == L')')) --t;
                    if (t > probe && ends_sentence(text[t - 1])) break;
                    while (e < n && is_space(text[e])) ++e;
                    probe = e;
                }
                sentence_start = ws;
                sentence_mark(src + static_cast<ULONG>(sentence_start), static_cast<ULONG>(se - sentence_start));
                at_sentence_start = false;
            }
            if (want_word_) {
                pending.append(text, i, ws - i);
                if (!pending.empty()) {
                    add_text(pending);
                    pending.clear();
                }
                word_mark(src + static_cast<ULONG>(ws), static_cast<ULONG>(we - ws));
                add_text(text.substr(ws, we - ws));
            } else {
                pending.append(text, i, we - i);
            }
            size_t t = we;
            while (t > ws && (text[t - 1] == L'"' || text[t - 1] == L'\'' || text[t - 1] == L')')) --t;
            if (t > ws && ends_sentence(text[t - 1])) at_sentence_start = true;
            i = we;
        }
        if (!pending.empty()) add_text(pending);
    }

    void word_mark(ULONG src, ULONG len)
    {
        Marker m;
        m.kind = Marker::Word;
        m.src = src;
        m.len = len;
        add_marker(std::move(m));
    }

    // <spell>: the engine's own spelling mode for everything it names, and a
    // spoken name for the characters it would leave silent.
    void spell(const std::wstring& text, ULONG src)
    {
        sentence_mark(src, static_cast<ULONG>(text.size()));
        std::wstring run;
        auto flush = [&]() {
            if (run.empty()) return;
            req_.param(kParamTextMode, 2);
            add_text(run);
            req_.param(kParamTextMode, s_.text_mode);
            run.clear();
        };
        for (size_t i = 0; i < text.size(); ++i) {
            const wchar_t c = text[i];
            if (is_space(c)) {
                if (!run.empty()) run.push_back(L' ');
                continue;
            }
            const std::wstring name = s_.spell_lone_symbols ? symbol_name(c, lang_.tag) : std::wstring();
            if (!name.empty()) {
                flush();
                if (want_word_) word_mark(src + static_cast<ULONG>(i), 1);
                add_text(name + L" ");
                continue;
            }
            if (want_word_) {
                flush();
                word_mark(src + static_cast<ULONG>(i), 1);
            }
            // Lower case: a screen reader signals capitals itself, and the
            // engine then never reads a lone capital as anything but a letter.
            run.push_back(static_cast<wchar_t>(towlower(c)));
            run.push_back(L' ');
        }
        flush();
    }

    // SAPI's actions. True when the utterance must stop now.
    bool poll_actions()
    {
        if (aborted_) return true;
        const DWORD a = site_->GetActions();
        if (a & SPVES_ABORT) {
            aborted_ = true;
            return true;
        }
        if ((a & SPVES_SKIP) && !skipping_) {
            SPVSKIPTYPE type = SPVST_SENTENCE;
            long count = 0;
            site_->GetSkipInfo(&type, &count);
            if (type == SPVST_SENTENCE && count > 0) {
                skipping_ = true;
                skip_left_ = count;
                skip_done_ = 0;
            } else {
                site_->CompleteSkip(0);
            }
        }
        if (a & SPVES_RATE) {
            long r = 0;
            if (SUCCEEDED(site_->GetRate(&r))) site_rate_ = r; // applies from the next utterance
        }
        if (a & SPVES_VOLUME) {
            USHORT v = 100;
            if (SUCCEEDED(site_->GetVolume(&v))) site_volume_ = v;
        }
        return false;
    }

    void write_bytes(const void* p, size_t n)
    {
        if (!n || write_failed_ || aborted_) return;
        if (first_audio_ms_ < 0) first_audio_ms_ = now_ms() - t0_;
        // Write takes the whole buffer or fails; its pcbWritten is not
        // reliable, so it is not asked for.
        const HRESULT hr = site_->Write(p, static_cast<ULONG>(n), nullptr);
        if (FAILED(hr)) {
            write_failed_ = true;
            log::write(log::kStandard, "speak: ISpTTSEngineSite::Write failed 0x%08lX", static_cast<unsigned long>(hr));
            return;
        }
        bytes_ += n;
    }

    void write_audio(const int16_t* s, size_t n)
    {
        if (skipping_) return; // dropped until the next sentence mark(s)
        // Small pieces, so a cancel is noticed within 20 ms of audio.
        const size_t piece = static_cast<size_t>(rate_hz_ / 50);
        size_t pos = 0;
        while (pos < n && !write_failed_) {
            if (poll_actions()) return;
            if (skipping_) return;
            const size_t k = std::min(piece, n - pos);
            write_bytes(s + pos, k * sizeof(int16_t));
            pos += k;
        }
    }

    void write_silence(ULONG ms)
    {
        static const int16_t zeros[2400] = {};
        size_t left = static_cast<size_t>(static_cast<double>(ms) * rate_hz_ / 1000.0);
        while (left && !write_failed_) {
            if (poll_actions() || skipping_) return;
            const size_t k = std::min<size_t>(left, rate_hz_ / 50);
            write_bytes(zeros, k * sizeof(int16_t));
            left -= k;
        }
    }

    void event(SPEVENTENUM id, WPARAM wp, LPARAM lp, SPEVENTLPARAMTYPE type)
    {
        SPEVENT e{};
        e.eEventId = id;
        e.elParamType = type;
        e.ullAudioStreamOffset = bytes_;
        e.wParam = wp;
        e.lParam = lp;
        site_->AddEvents(&e, 1);
    }

    void on_marker(const Marker& m)
    {
        if (aborted_ || write_failed_) return;
        switch (m.kind) {
        case Marker::Sentence:
            if (skipping_) {
                // Skipping n sentences stops at the n-th sentence start ahead.
                if (++skip_done_ < skip_left_) break;
                finish_skip();
            }
            if (want_sentence_) event(SPEI_SENTENCE_BOUNDARY, m.len, m.src, SPET_LPARAM_IS_UNDEFINED);
            break;
        case Marker::Word:
            if (!skipping_ && want_word_) event(SPEI_WORD_BOUNDARY, m.len, m.src, SPET_LPARAM_IS_UNDEFINED);
            break;
        case Marker::Bookmark:
            // Fired even while skipping: a screen reader tracks its place by these.
            if (want_bookmark_) {
                // SAPI frees a string lParam with CoTaskMemFree.
                auto* copy = static_cast<wchar_t*>(CoTaskMemAlloc((m.text.size() + 1) * sizeof(wchar_t)));
                if (copy) {
                    std::copy(m.text.begin(), m.text.end(), copy);
                    copy[m.text.size()] = L'\0';
                    event(SPEI_TTS_BOOKMARK, static_cast<WPARAM>(_wtol(m.text.c_str())),
                          reinterpret_cast<LPARAM>(copy), SPET_LPARAM_IS_STRING);
                }
            }
            if (log::enabled(log::kFull)) {
                lb_.add(log::kFull, "  bookmark \"%s\" at byte %llu", narrow(m.text.data(), m.text.size()).c_str(),
                        bytes_);
            }
            break;
        case Marker::Silence:
            if (!skipping_) write_silence(m.ms);
            break;
        }
    }
};

} // namespace

ISpTTSEngineImpl::ISpTTSEngineImpl()
{
    init_logging_once();
    HostPool::get().add_user();
}

ISpTTSEngineImpl::~ISpTTSEngineImpl()
{
    HostPool::get().release_user();
}

const Settings& ISpTTSEngineImpl::current_settings()
{
    if (settings_.refresh()) {
        const Settings& s = settings_.get();
        log::set_level(s.log_level);
        log::write(log::kStandard,
                   "settings: rate %d Hz (%S), max speed %d%s, pitch step %d, abbreviations %d, numbers %d, text mode "
                   "%d, annotations %d, dictionaries %d, heteronyms %d, %zu voices adjusted, log %d",
                   sample_rate_hz(s.sample_rate), s.resampler.c_str(), s.max_speed, s.rate_boost ? " (boost)" : "",
                   s.pitch_step, s.abbreviations, s.number_mode, s.text_mode, s.annotations, s.user_dictionaries,
                   s.heteronyms, s.voices.size(), s.log_level);
    }
    return settings_.get();
}

STDMETHODIMP ISpTTSEngineImpl::SetObjectToken(ISpObjectToken* pToken)
{
    if (!pToken) {
        return E_INVALIDARG;
    }
    try {
        token_ = pToken;
        ISpDataKeyPtr attr;
        std::wstring tag, preset;
        if (SUCCEEDED(pToken->OpenKey(L"Attributes", &attr)) && attr) {
            utils::out_ptr<wchar_t> t(CoTaskMemFree);
            if (SUCCEEDED(attr->GetStringValue(L"OpenEvvLanguage", t.address())) && t.get()) tag = t.get();
            utils::out_ptr<wchar_t> p(CoTaskMemFree);
            if (SUCCEEDED(attr->GetStringValue(L"OpenEvvPreset", p.address())) && p.get()) preset = p.get();
        }
        if (tag.empty()) tag = L"enus";
        preset_ = preset.empty() ? 1 : std::max(1, std::min(8, _wtoi(preset.c_str())));
        have_lang_ = find_language(tag, lang_);
        if (!have_lang_) {
            log::write(log::kStandard, "voice: the language pack \"%S\" is not installed", tag.c_str());
            return SPERR_NOT_FOUND;
        }
        voice_name_ = utils::wstring_to_string(L"OpenEVV " + lang_.name + L" " + lang_.voices[preset_ - 1].name);
        const Settings& s = current_settings();
        // Start the engine host now, so the first word does not wait for it.
        HostPool::get().warm(lang_, s);
        log::write(log::kStandard, "voice: %s selected", voice_name_.c_str());
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (...) {
        return E_UNEXPECTED;
    }
}

STDMETHODIMP ISpTTSEngineImpl::GetObjectToken(ISpObjectToken** ppToken)
{
    if (!ppToken) {
        return E_POINTER;
    }
    *ppToken = nullptr;
    if (!token_) {
        return E_UNEXPECTED;
    }
    token_.AddRef();
    *ppToken = token_.GetInterfacePtr();
    return S_OK;
}

STDMETHODIMP ISpTTSEngineImpl::GetOutputFormat(const GUID*, const WAVEFORMATEX*, GUID* pOutputFormatId,
                                               WAVEFORMATEX** ppCoMemOutputWaveFormatEx)
{
    if (!pOutputFormatId || !ppCoMemOutputWaveFormatEx) {
        return E_POINTER;
    }
    *pOutputFormatId = SPDFID_WaveFormatEx;
    *ppCoMemOutputWaveFormatEx = nullptr;
    auto* w = static_cast<WAVEFORMATEX*>(CoTaskMemAlloc(sizeof(WAVEFORMATEX)));
    if (!w) {
        return E_OUTOFMEMORY;
    }
    const Settings& s = current_settings();
    w->wFormatTag = WAVE_FORMAT_PCM;
    w->nChannels = 1;
    w->nSamplesPerSec = static_cast<DWORD>(sample_rate_hz(s.sample_rate));
    w->wBitsPerSample = 16;
    w->nBlockAlign = 2;
    w->nAvgBytesPerSec = w->nSamplesPerSec * 2;
    w->cbSize = 0;
    *ppCoMemOutputWaveFormatEx = w;
    log::write(log::kFull, "format: %lu Hz", w->nSamplesPerSec);
    return S_OK;
}

STDMETHODIMP ISpTTSEngineImpl::Speak(DWORD dwSpeakFlags, REFGUID, const WAVEFORMATEX* pWaveFormatEx,
                                     const SPVTEXTFRAG* pTextFragList, ISpTTSEngineSite* pOutputSite)
{
    if (!pTextFragList || !pOutputSite) {
        return E_INVALIDARG;
    }
    if (!have_lang_) {
        return E_UNEXPECTED;
    }
    const double t0 = now_ms();
    try {
        const Settings& s = current_settings();
        // The format SAPI is expecting is the one to speak in: a sample rate
        // changed in the configuration utility takes effect as soon as SAPI
        // asks for the format again.
        const int rate = pWaveFormatEx ? eci_rate_for_hz(pWaveFormatEx->nSamplesPerSec, s.sample_rate)
                                       : s.sample_rate;
        log::Batch lb; // written after the audio, never before it
        const unsigned long n = ++utterances_;
        if (log::enabled(log::kFull)) {
            lb.add(log::kFull, "speak #%lu on %s, flags 0x%08lX", n, voice_name_.c_str(), dwSpeakFlags);
        }
        Session session(pOutputSite, lang_, preset_, s, rate, lb);
        for (const SPVTEXTFRAG* f = pTextFragList; f; f = f->pNext) {
            session.fragment(f);
        }
        if (!session.run(true)) {
            // The host died before any audio: once more, on a fresh host.
            session.reset_for_retry();
            session.run(false);
        }
        lb.add(log::kStandard,
               "speak #%lu %s: %zu fragments, %zu chars, speed %d, %d Hz, host in %.2f ms, engine first audio %.2f ms, "
               "first write %.2f ms, %.2f s of audio in %.1f ms%s%s",
               n, voice_name_.c_str(), session.fragments(), session.chars(), session.speed(), session.rate_hz(),
               session.host_ms(), session.engine_first_audio_ms(), session.first_audio_ms(),
               session.bytes() / (2.0 * session.rate_hz()), now_ms() - t0, session.aborted() ? ", cancelled" : "",
               session.failed() ? ", FAILED" : "");
        return S_OK;
    } catch (const std::bad_alloc&) {
        log::write(log::kStandard, "speak: out of memory");
        return E_OUTOFMEMORY;
    } catch (const std::exception& e) {
        log::write(log::kStandard, "speak: unexpected error: %s", e.what());
        return E_FAIL;
    } catch (...) {
        log::write(log::kStandard, "speak: unexpected error");
        return E_UNEXPECTED;
    }
}

} // namespace sapi
} // namespace evv
