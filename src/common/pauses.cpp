#include "pauses.h"

#include <windows.h>

#include <cwctype>
#include <vector>

namespace evv {

const wchar_t kShortPause[] = L"`p1";

namespace {

const char kShortPauseNarrow[] = "`p1";

bool is_space(wchar_t c)
{
    return iswspace(c) != 0 || c == 0x00A0;
}

// The C library's wide classification depends on the locale a program runs
// in; the Windows tables do not.
bool has_type(wchar_t c, WORD bits)
{
    WORD kind = 0;
    return GetStringTypeW(CT_CTYPE1, &c, 1, &kind) && (kind & bits) != 0;
}

bool is_alpha(wchar_t c)
{
    return has_type(c, C1_ALPHA);
}

bool is_digit(wchar_t c)
{
    return has_type(c, C1_DIGIT);
}

bool is_alnum(wchar_t c)
{
    return has_type(c, C1_ALPHA | C1_DIGIT);
}

// What may follow the mark that ends a phrase and still leave it at the end
// of one: He said "no." (ends a quotation or a bracket).
bool is_closer(wchar_t c)
{
    switch (c) {
    case L')':
    case L']':
    case L'}':
    case L'"':
    case L'\'':
    case 0x2019: // right single quotation mark
    case 0x201D: // right double quotation mark
    case 0x00BB: // right-pointing double angle quotation mark
        return true;
    }
    return false;
}

// What a mark cannot follow: (. is not the end of a phrase.
bool is_opener(wchar_t c)
{
    switch (c) {
    case L'(':
    case L'[':
    case L'{':
    case L'`':
    case 0x2018: // left single quotation mark
    case 0x201C: // left double quotation mark
    case 0x00AB: // left-pointing double angle quotation mark
        return true;
    }
    return false;
}

// The marks of Japanese and Chinese, which have no space after them.
bool is_cjk_mark(wchar_t c)
{
    return c == 0x3001 || c == 0x3002 || c == 0xFF0C || c == 0xFF0E || c == 0xFF1A || c == 0xFF1B || c == 0xFF1F ||
           c == 0xFF01;
}

// Titles and the like that are written with a full stop and that the engine's
// dictionary reads as a word ("Mr." as "Mister"). A word that a sentence could
// as easily end with (no, sun, sat, max...) is not here: its pause is then
// shortened, which costs nothing if it was the end of a sentence.
const wchar_t* const kAbbreviations[] = {
    // English
    L"mr", L"mrs", L"ms", L"dr", L"prof", L"st", L"jr", L"sr", L"vs", L"etc", L"inc", L"ltd", L"corp", L"mt", L"ft",
    L"gen", L"sgt", L"col", L"capt", L"lt", L"rev", L"hon", L"sen", L"gov", L"pres", L"ave", L"blvd", L"apt", L"dept",
    L"approx", L"tel", L"ext", L"cf", L"jan", L"feb", L"apr", L"jun", L"jul", L"aug", L"sept", L"oct", L"nov", L"dec",
    L"tue", L"tues", L"wed", L"thu", L"thur", L"thurs", L"fri",
    // German
    L"hr", L"bzw", L"usw", L"nr", L"str", L"evtl", L"ggf", L"inkl", L"vgl", L"zb",
    // Spanish, French, Italian, Polish
    L"sra", L"srta", L"dra", L"pág", L"págs", L"ud", L"uds", L"vd", L"vds", L"avda", L"mme", L"mlle", L"mm",
    L"sig", L"sigg", L"dott", L"ing", L"avv", L"itd", L"itp", L"np", L"tzw", L"ul", L"godz",
};

enum class Dot
{
    Sentence,     // it may end a sentence
    Abbreviation, // an initial or a title: the engine's dictionary reads it with its dot
    Number,       // 3. as in a list or a German date: an ordinal, read as one
};

// The full stop at t[dot], by the word before it.
Dot classify(const std::wstring& t, size_t dot)
{
    size_t start = dot;
    while (start > 0 && is_alnum(t[start - 1])) --start;
    const size_t len = dot - start;
    if (len == 0) return Dot::Sentence;
    bool digits = true, letters = true;
    for (size_t i = start; i < dot; ++i) {
        if (!is_digit(t[i])) digits = false;
        if (!is_alpha(t[i])) letters = false;
    }
    if (digits) return Dot::Number;
    if (!letters) return Dot::Sentence;
    if (len == 1) return Dot::Abbreviation; // an initial: J. Smith
    std::wstring word;
    for (size_t i = start; i < dot; ++i) word.push_back(static_cast<wchar_t>(towlower(t[i])));
    for (const wchar_t* a : kAbbreviations) {
        if (word == a) return Dot::Abbreviation;
    }
    return Dot::Sentence;
}

// Whether the marks t[i..j) end a phrase and are to have a pause put in front
// of them: what the driver's regular expression asks, with the marks of any
// kind counted as one run, closing quotes and brackets allowed after them, and
// the marks of East Asian text needing no space.
bool ends_phrase(const std::wstring& t, size_t i, size_t j, wchar_t before, bool at_end)
{
    const wchar_t b = i > 0 ? t[i - 1] : before;
    if (b == 0 || is_opener(b) || b == L'\\') return false;
    const bool cjk = is_cjk_mark(t[i]) || is_cjk_mark(t[j - 1]);
    size_t k = j;
    while (k < t.size() && is_closer(t[k])) ++k;
    if (!(cjk || k == t.size() || is_space(t[k]) || t[k] == L'\\' || t[k] == L'/')) return false;
    if (j == i + 1 && t[i] == L'.') {
        const Dot d = classify(t, i);
        if (d == Dot::Abbreviation) return false;
        if (d == Dot::Number && !at_end) return false;
    }
    return true;
}

// Whether what stands before t[end] is already a pause annotation.
bool short_pause_before(const std::wstring& t, size_t end)
{
    while (end > 0 && is_space(t[end - 1])) --end;
    const size_t n = sizeof kShortPause / sizeof kShortPause[0] - 1;
    return end >= n && t.compare(end - n, n, kShortPause) == 0;
}

} // namespace

bool is_pause_mark(wchar_t c)
{
    switch (c) {
    case L',':
    case L'.':
    case L':':
    case L';':
    case L'?':
    case L'!':
    case L'-':
    case 0x2013: // en dash
    case 0x2014: // em dash
    case 0x2026: // horizontal ellipsis
        return true;
    }
    return is_cjk_mark(c);
}

std::wstring without_backquotes(std::wstring text)
{
    for (wchar_t& c : text) {
        if (c == L'`') c = L' ';
    }
    return text;
}

std::wstring shorten_pauses(const std::wstring& text, wchar_t before)
{
    std::wstring out;
    out.reserve(text.size() + 16);
    const size_t n = text.size();
    for (size_t i = 0; i < n;) {
        if (!is_pause_mark(text[i])) {
            out.push_back(text[i++]);
            continue;
        }
        size_t j = i;
        while (j < n && is_pause_mark(text[j])) ++j;
        if (ends_phrase(text, i, j, before, false) && !short_pause_before(out, out.size())) {
            out.push_back(L' ');
            out.append(kShortPause);
        }
        out.append(text, i, j - i);
        i = j;
    }
    return out;
}

std::wstring shorten_final_pause(const std::wstring& text, wchar_t before)
{
    size_t end = text.size();
    while (end > 0 && is_space(text[end - 1])) --end;
    if (end == 0) return text;
    size_t marks_end = end;
    while (marks_end > 0 && is_closer(text[marks_end - 1])) --marks_end;
    size_t marks = marks_end;
    while (marks > 0 && is_pause_mark(text[marks - 1])) --marks;
    if (marks < marks_end) {
        // It ends with a mark: the pause goes in front of it, unless that
        // has been done or the mark is a dot the engine reads with its word.
        if (short_pause_before(text, marks) || !ends_phrase(text, marks, marks_end, before, true)) return text;
        std::wstring out = text.substr(0, marks);
        out.push_back(L' ');
        out.append(kShortPause);
        out.append(text, marks, std::wstring::npos);
        return out;
    }
    std::wstring out = text.substr(0, end);
    out.push_back(L' ');
    out.append(kShortPause);
    out.append(text, end, std::wstring::npos);
    return out;
}

std::wstring shorten_text(const std::wstring& text, int mode, bool keep_backquotes)
{
    if (mode <= kPausesKept) return text;
    std::wstring t = keep_backquotes ? text : without_backquotes(text);
    if (mode >= kPausesAll) t = shorten_pauses(t, 0);
    return shorten_final_pause(t, 0);
}

std::string shorten_annotated(const std::string& s, bool every_clause, bool at_end)
{
    // The marks that are not inside a pronunciation or a group.
    std::vector<size_t> marks;
    bool in_phones = false, in_group = false;
    for (size_t i = 0; i < s.size(); ++i) {
        const char c = s[i];
        if (in_phones) {
            if (c == ']') in_phones = false;
            continue;
        }
        if (in_group) {
            if (c == '}') in_group = false;
            continue;
        }
        if (c == '`' && i + 1 < s.size() && s[i + 1] == '[') {
            in_phones = true;
            ++i;
        } else if (c == '{') {
            in_group = true;
        } else if (c == ',' || c == '.' || c == '?' || c == '!') {
            marks.push_back(i);
        }
    }
    size_t last_content = s.size();
    while (last_content > 0 && (s[last_content - 1] == ' ' || s[last_content - 1] == '\t' ||
                                s[last_content - 1] == '\r' || s[last_content - 1] == '\n')) {
        --last_content;
    }
    const bool ends_with_mark = !marks.empty() && marks.back() + 1 == last_content;
    std::string out;
    out.reserve(s.size() + 16 * marks.size() + 8);
    size_t from = 0;
    for (const size_t m : marks) {
        const bool final_mark = ends_with_mark && m == marks.back();
        if (!every_clause && !(at_end && final_mark)) continue;
        out.append(s, from, m - from);
        out.push_back(' ');
        out.append(kShortPauseNarrow);
        from = m;
    }
    out.append(s, from, std::string::npos);
    if (at_end && !ends_with_mark && last_content > 0) {
        out.insert(out.size() - (s.size() - last_content), std::string(" ") + kShortPauseNarrow);
    }
    return out;
}

} // namespace evv
