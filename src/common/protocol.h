// Messages between a client (OpenEvvSAPI.dll, OpenEvvConfig.exe, the tools)
// and OpenEvvHost.exe.
//
// The engine runs in a helper process for two reasons. Its backtracking
// restores the stack pointer from a landing place of its own, which a process
// enforcing CET shadow stacks refuses; and a fault in transcribed 1999 code
// must never take a screen reader down with it.
//
// Two anonymous pipes, one per direction, inherited as the host's standard
// input and output, so a blocking read never holds up a write. Every message
// is a Header followed by `size` bytes of payload. Little-endian, packed, the
// same layout in both bitnesses, so either client can drive either host.
#pragma once

#include <cstdint>

namespace evv {
namespace proto {

constexpr uint32_t kVersion = 1;

enum MsgType : uint32_t
{
    // client -> host
    kSpeak = 1,  // SpeakReq + items; answered by kAudio/kIndex..., then kDone
    kCancel = 2, // CancelReq: throw the rest of that utterance away
    kQuit = 3,   // no payload
    // host -> client
    kReady = 10, // ReadyMsg, once, after the engine is up and warm
    kAudio = 11, // AudioMsg + int16 samples
    kIndex = 12, // IndexMsg: the engine reached a mark
    kDone = 13,  // DoneMsg: the utterance is finished (or cancelled)
};

// What a SpeakReq's items are.
enum ItemKind : uint8_t
{
    kItemText = 1,  // a = byte count; followed by that many bytes, in the language's code set
    kItemIndex = 2, // a = the mark's number
    kItemVoice = 3, // a = voice parameter, b = value: set on voice 0 from here on
    kItemParam = 4, // a = engine parameter, b = value (text mode, input type...)
    // a = the pause mode (pauses.h: 0 as the engine has them, 1 shorten the one at the end of the
    // text, 2 shorten all of them). Only a language read by eSpeak NG needs it: the host puts the
    // pause annotations into the front-end's text. A language the engine speaks itself has them
    // put into its text by the client, and a host that does not know this item ignores it.
    kItemPauses = 5,
};

#pragma pack(push, 1)

struct Header
{
    uint32_t type;
    uint32_t size;
};

struct ReadyMsg
{
    uint32_t version;
    int32_t ok;
    uint32_t language;
    double init_ms;
    char engine_version[32];
    char error[200];
    char voice_names[8][32];
    int32_t voice_params[8][8];
};

// What SpeakReq::user_dicts carries. Bit 0 is what it always was: the user's own dictionaries are
// on. Bit 1 switches the community dictionary OFF, so that a client that has never heard of it (an
// older OpenEvvSAPI.dll still loaded in a running program) leaves it on, which is its default.
constexpr int32_t kDictUser = 1;
constexpr int32_t kDictCommunityOff = 2;

struct SpeakReq
{
    uint32_t id;
    int32_t sample_rate;  // eciSampleRate 0..6
    int32_t text_mode;    // eciTextMode
    int32_t number_mode;  // eciNumberMode
    int32_t dictionary;   // 1 = the abbreviation dictionary on
    int32_t input_type;   // 1 = annotations honoured
    int32_t user_dicts;   // kDictUser | kDictCommunityOff
    int32_t preset;       // 1..8, copied onto voice 0 first
    int32_t voice[8];     // then these, where not -1
    uint32_t item_count;
};

struct Item
{
    uint8_t kind;
    int32_t a;
    int32_t b;
};

struct CancelReq
{
    uint32_t id;
};

struct AudioMsg
{
    uint32_t id; // followed by int16 samples
};

struct IndexMsg
{
    uint32_t id;
    int32_t value;
    uint64_t sample; // samples of this utterance delivered before the mark
};

enum DoneStatus : int32_t
{
    kDoneOk = 0,
    kDoneCancelled = 1,
    kDoneFailed = 2,
};

struct DoneMsg
{
    uint32_t id;
    int32_t status;
    uint64_t samples;
    int32_t sample_rate_hz;
    double first_audio_ms; // from the request arriving to the first samples
    double total_ms;       // from the request arriving to the end
    char error[160];
};

#pragma pack(pop)

constexpr uint32_t kMaxPayload = 8u << 20;

} // namespace proto
} // namespace evv
