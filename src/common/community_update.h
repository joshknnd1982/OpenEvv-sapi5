// "Check for a newer version and install it" for the community dictionary.
//
// The newest commit of the repository's default branch is what "latest"
// means here, not the monthly release: a fix the maintainers made yesterday
// is worth having today. GitHub is asked for that commit (one small request);
// when it is the copy already in use nothing more happens, otherwise the
// branch's zip is downloaded, checked, and put in
// %ProgramData%\OpenEVV\community-dictionary, where every OpenEVV voice finds
// it on its next utterance with nothing restarted.
//
// If GitHub's API refuses (it allows a program without a token sixty requests
// an hour), the zip alone is enough: it carries its commit's hash. Nothing
// already installed is touched until the whole download has been read and
// every file in it has matched its checksum.
//
// This links WinHTTP, so only OpenEvvConfig and the tools include it.
#pragma once

#include <string>

#include "community_dict.h"

namespace evv {

enum class CommunityOutcome
{
    UpToDate, // the copy in use is the newest
    Updated,  // a newer one was installed
    Failed,   // nothing was changed
};

struct CommunityUpdate
{
    CommunityOutcome outcome = CommunityOutcome::Failed;
    std::wstring message;     // what happened, in words, for the person
    CommunitySnapshot in_use; // the copy in use afterwards
};

// Blocks for a few seconds; call it from a worker thread. OPENEVV_COMMUNITY_ZIP
// names a local zip to install instead of asking GitHub (the tests use it).
CommunityUpdate update_community_dictionary();

// The parts of it that need no network, for the tests: what a zip's commit is,
// and what would be installed from it.
bool community_zip_commit(const std::string& comment, std::string& commit);

} // namespace evv
