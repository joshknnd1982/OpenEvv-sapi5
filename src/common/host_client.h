// The client side of OpenEvvHost.exe: starting hosts, keeping them warm, and
// streaming an utterance's audio and marks back.
//
// One pool per process. A host serves one language module; the pool keeps as
// many as are needed at once (normally one per language in use), starts one
// ahead of the first utterance when a voice is chosen, replaces any that die
// or hang, and replaces them all when a setting only a starting host can read
// changes. Hosts outlive the last voice by a grace period, so switching voices
// does not pay for a new process.
#pragma once

#include <condition_variable>
#include <cstdint>
#include <deque>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

#include "languages.h"
#include "protocol.h"
#include "settings.h"

namespace evv {

struct HostEvent
{
    enum Kind
    {
        kAudio,
        kIndex,
        kDone,
    } kind = kDone;
    std::vector<int16_t> samples; // kAudio
    int32_t index = 0;            // kIndex
    uint64_t sample = 0;          // kIndex: samples delivered before the mark
    proto::DoneMsg done{};        // kDone
};

class HostProcess;

// One request's stream of events.
class Utterance
{
public:
    // Waits up to timeout_ms for the next event. False on timeout. After the
    // kDone event there are no more.
    bool next(HostEvent& ev, unsigned timeout_ms);
    // Throws the rest away. Safe to call at any time, more than once.
    void cancel();
    bool done() const;
    uint32_t id() const { return id_; }
    // Marks the host hung: it is killed and replaced, and this stream ends.
    void abandon();

private:
    friend class HostProcess;
    friend class HostPool;
    void deliver(HostEvent&& ev);

    uint32_t id_ = 0;
    std::weak_ptr<HostProcess> host_;
    mutable std::mutex m_;
    std::condition_variable cv_;
    std::deque<HostEvent> q_;
    bool done_ = false;
    bool cancelled_ = false;
};

// Builds a SpeakReq and its items.
class RequestBuilder
{
public:
    proto::SpeakReq head{};
    RequestBuilder();
    // Adds a stretch of text and answers where it is, for replace_text.
    size_t text(const std::string& bytes);
    // Puts other bytes in place of the stretch of text that text() put at `at`.
    void replace_text(size_t at, const std::string& bytes);
    void index(int32_t value);
    void voice(int which, int value);
    void param(int which, int value);
    void pauses(int mode);
    bool empty() const { return head.item_count == 0; }
    std::vector<uint8_t> finish(uint32_t id) const;

private:
    std::vector<uint8_t> items_;
};

struct HostInfo
{
    std::string engine_version;
    std::wstring module;
    double init_ms = 0;
    bool x64 = false;
};

class HostPool
{
public:
    static HostPool& get();

    // Engines and tools register while they may speak. The pool shuts its
    // hosts down a grace period after the last one leaves.
    void add_user();
    void release_user();

    // Starts a host for the language if none is running or starting. Does not
    // wait.
    // bitness: -1 this process's own (falling back to the other), 0 the 32-bit
    // module and host, 1 the 64-bit ones.
    void warm(const LanguageInfo& lang, const Settings& s, int bitness = -1);

    // Sends one request to an idle host (starting one if needed, waiting up to
    // wait_ms for it) and returns its event stream, or null with the reason.
    std::shared_ptr<Utterance> speak(const LanguageInfo& lang, const Settings& s, const RequestBuilder& req,
                                     std::string& error, HostInfo* info = nullptr, unsigned wait_ms = 10000,
                                     int bitness = -1);

    // Stops every host now (used at shutdown and by tools).
    void shutdown_all();

    // True while the pool holds hosts or a thread, i.e. the DLL must stay.
    bool busy() const;

    // For a DLL: the module to pin while the grace thread runs.
    void set_module(void* hmodule) { module_ = hmodule; }

private:
    HostPool() = default;
    friend class HostProcess;
    void host_changed();
    void grace_thread();
    static unsigned long __stdcall grace_entry(void* p);

    mutable std::mutex m_;
    std::condition_variable cv_;
    std::vector<std::shared_ptr<HostProcess>> hosts_;
    int users_ = 0;
    uint32_t next_id_ = 1;
    void* module_ = nullptr;
    void* grace_event_ = nullptr;   // HANDLE
    bool grace_running_ = false;
};

} // namespace evv
