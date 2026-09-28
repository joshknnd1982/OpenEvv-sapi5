// SAPI hands text over as UTF-16; a language module reads single bytes in
// its own code set (the Windows Western set for eight of IBM's nine
// languages, Shift-JIS for Japanese, UTF-8 for Polish).
#pragma once

#include <string>

namespace evv {

// Converts for a module. A character the code set cannot hold becomes a
// space rather than '?', which the engine would read out; characters that
// carry no sound (zero-width, soft hyphen) are dropped; line breaks and
// control characters become spaces.
std::string encode_text(const wchar_t* text, size_t length, unsigned codepage);

inline std::string encode_text(const std::wstring& text, unsigned codepage)
{
    return encode_text(text.data(), text.size(), codepage);
}

// A spoken name for a character the engine would otherwise render as
// silence when it is the whole utterance ("+" -> "plus"). English names; an
// empty string when the character needs none.
std::wstring symbol_name(wchar_t c, const std::wstring& language_tag);

} // namespace evv
