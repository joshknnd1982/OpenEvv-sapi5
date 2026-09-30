// Shorter pauses at punctuation, as the IBMTTS driver for NVDA has them
// (github.com/davidacm/NVDA-IBMTTS-Driver, its "Pauses" setting).
//
// The engine pauses at a comma, a full stop, a question mark and the rest for
// about as long as a person reading aloud would. A screen reader wants to be
// quicker than that, and IBM's engine has one way of being told: a pause
// annotation, `p1, which asks for a pause of one unit. Put just before the
// punctuation mark it takes the place of the pause the mark would have made,
// and the mark still gives the phrase its intonation. The driver puts one in
// front of every mark in the text (its "Shorten all pauses") and one at the end
// of a text that does not end in a mark (its "Shorten at end of text only").
// Measured here on the ten languages the engine speaks itself, a full stop's
// pause goes from about 400 ms to about 40, a comma's from about 155 to 45, and
// the silence that follows the last word of every utterance goes with them.
//
// The three modes are the driver's:
//   0  Do not shorten: the engine's own pauses.
//   1  Shorten at end of text only: the pause after the last word goes, and
//      the ones between phrases stay.
//   2  Shorten all pauses.
//
// Two things differ from the driver. Mode 1 also takes the pause of a final
// mark away, as its documentation says it does (its code only does it for a text
// that ends without one). And a full stop that ends an abbreviation is left
// alone: `p1 between "Mr" and its dot stops the engine's dictionary from
// recognising it, and "Mr. Smith" is then not read as "Mister Smith".
//
// Languages the engine speaks itself take this in the text, which is what the
// functions on wide characters are for. Languages read by eSpeak NG have their
// text turned into the engine's own annotated form by the front-end first, and
// the host puts the annotation into that (shorten_annotated).
#pragma once

#include <string>

namespace evv {

enum PauseMode : int
{
    kPausesKept = 0,
    kPausesEndOnly = 1,
    kPausesAll = 2,
};

// The annotation itself.
extern const wchar_t kShortPause[];

// Whether a character is one the engine pauses at.
bool is_pause_mark(wchar_t c);

// An annotation begins with a backquote. Once annotations are honoured a
// backquote in the text is not text any more (`v1 changes the voice, `0 to `4
// are pauses), so text that somebody else wrote has them taken out first, as the
// driver does. Not for a user who asked for annotations.
std::wstring without_backquotes(std::wstring text);

// `text` with a pause annotation in front of every mark that ends a phrase.
// `before` is the character just before `text` in what is being spoken, or 0
// at its very start; the text is often only a word, and a mark on its own needs
// to know what it follows.
std::wstring shorten_pauses(const std::wstring& text, wchar_t before);

// The last stretch of text of an utterance, with the pause after its last word
// taken out: in front of the mark it ends with, or at its end where it has none.
std::wstring shorten_final_pause(const std::wstring& text, wchar_t before);

// A whole text, for a tool or a Speak button: sanitised, and shortened as the
// mode says. Unchanged in mode 0.
std::wstring shorten_text(const std::wstring& text, int mode, bool keep_backquotes);

// The front-end's annotated text for one stretch (UTF-8): its clauses end with
// a plain , . ? or !, and everything else is inside `[ ] or { }. Every mark
// gets the annotation when every_clause is set; the last stretch of a text
// (at_end) gets it in front of its final mark, or at its end where it has none.
std::string shorten_annotated(const std::string& annotated, bool every_clause, bool at_end);

} // namespace evv
