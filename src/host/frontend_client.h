// The eSpeak NG front-end, as the engine host sees it.
//
// A language pack made from an eSpeak NG language is spoken by its template's
// engine module, but read by eSpeak NG: OpenEvvFrontend.exe, a program of its
// own under the GPL version 3, which the host starts as a child and talks to
// over two pipes (common/frontend_proto.h). Given a text, it answers the text
// as pronunciation annotations in the template's phonemes, with where each
// word came from in the text, so that the host can put SAPI's marks back
// where they belong.
#pragma once

#include <windows.h>

#include <string>
#include <vector>

#include "common/frontend_proto.h"

namespace evv {

class FrontendClient
{
public:
    ~FrontendClient() { stop(); }

    // Starts the front-end and sets its voice. False, with a reason, if it
    // cannot be started or refuses the voice.
    bool start(const std::wstring& exe, const std::wstring& data, const std::wstring& voice, const std::wstring& map,
               std::string& error);

    // The text, UTF-8, as the template's annotated text. `flags' is
    // EVV_FE_FLAG_*. A front-end that has died is started again once.
    bool translate(const std::string& utf8, uint32_t flags, std::string& out, std::vector<EvvAnchor>& anchors,
                   std::string& error);

    void stop();
    bool running() const { return process_ != nullptr; }

private:
    bool spawn(std::string& error);
    bool set_voice(std::string& error);
    bool request(uint32_t type, const std::string& payload, EvvMsgHeader& reply, std::vector<uint8_t>& body);

    std::wstring exe_, data_, voice_, map_;
    HANDLE to_ = nullptr, from_ = nullptr, process_ = nullptr;
};

// Word-for-word replacements from a user's dictionaries, for a pack read by
// eSpeak NG, where the engine's own dictionaries never see the words: the
// main and abbreviation volumes replace whole words, the root volume the
// beginning of one. Files are read again when they change.
class TextDictionary
{
public:
    void set_files(const std::wstring files[3]);
    // Returns the text with every entry replaced; `utf8' in, UTF-8 out.
    std::string apply(const std::string& utf8);
    bool empty() const { return whole_.empty() && roots_.empty(); }

private:
    void reload_if_changed();
    std::wstring files_[3];
    FILETIME stamps_[3] = {};
    std::vector<std::pair<std::wstring, std::wstring>> whole_, roots_; // lower-case key, replacement
};

} // namespace evv
