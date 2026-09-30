// The community pronunciation dictionary.
//
// IBMTTSDictionaries (github.com/eigencrow/IBMTTSDictionaries, CC0) is the
// pronunciation dictionary the IBMTTS driver community keeps for the ECI
// engine: a main, a root and an abbreviation dictionary (ENU*.dic for US
// English; the repository has German files too, which are not used here: this
// is for English only), in the format the engine's eciLoadDict reads, one
// entry a line, the word, a tab and what to say instead. It is a new layer
// under the user's own dictionaries: the engine host loads it first and the
// user's main.dic, root.dic and abbr.dic after it, so a user's entry wins
// wherever the two disagree.
//
// Two copies can exist, and the newer is the one in use:
//
//   {app}\dictionaries\community\               installed with OpenEVV
//   %ProgramData%\OpenEVV\community-dictionary\ put there by "Check for a newer
//                                               version" in OpenEvvConfig.exe
//
// Each folder holds the .dic files and community-dictionary.ini, which names
// the commit they are from. The SAPI engine and the host only ever read; the
// update itself is community_update.h and is linked into OpenEvvConfig alone.
#pragma once

#include <string>

namespace evv {

// One installed copy of the dictionary, as its community-dictionary.ini
// describes it.
struct CommunitySnapshot
{
    std::wstring dir;          // empty when there is no copy
    std::string commit;        // the 40 hex digits of the commit it is from
    std::string commit_date;   // when it was committed, "2026-09-30T05:52:43Z" (UTC, sorts as text)
    std::string message;       // the commit's own summary line
    bool downloaded = false;   // false: installed with OpenEVV
    bool valid() const { return !dir.empty(); }
};

constexpr const char* kCommunityRepository = "eigencrow/IBMTTSDictionaries";
constexpr const char* kCommunityBranch = "master";

std::wstring community_shipped_dir();
std::wstring community_downloaded_dir();

// Reads one folder; not valid() when it holds no .dic file.
CommunitySnapshot read_community_snapshot(const std::wstring& dir, bool downloaded);

// The copy in use: the newer of the two, the downloaded one when they are the
// same age, and not valid() when neither is there.
CommunitySnapshot community_snapshot();

// The three letters IBM's dictionary files are named by for an ECI language
// ("ENU" for 0x00010000), or null for a language the community dictionary is
// not for: it is for English only.
const wchar_t* community_language_code(unsigned eci_language);

// Whether a file of the repository is for English (its name starts with an
// English language code). The update installs those and no others.
bool community_file_is_english(const std::string& file_name);

// The file of a volume (0 main, 1 root, 2 abbreviations) for a language in a
// snapshot, or an empty string when it has none.
std::wstring community_file(const CommunitySnapshot& snapshot, unsigned eci_language, int volume);

// What a snapshot is, in words for a person: its commit, its date, where it came from, the
// languages it has files for and the folder it is in.
std::wstring community_describe(const CommunitySnapshot& snapshot);

// "30 September 2026" from a snapshot's commit date, or an empty string.
std::wstring community_date_words(const std::string& iso_date);

} // namespace evv
