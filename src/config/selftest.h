// Speaks every voice of every installed language into memory, through the
// same engine hosts the SAPI engine uses, in every bitness installed. Used by
// the Diagnostics page and by the installer (OpenEvvConfig.exe --selftest).
#pragma once

#include <functional>
#include <string>

namespace evv {

struct SelfTestResult
{
    int spoken = 0;
    int tried = 0;
    int failures = 0;
    std::wstring report; // one line per language and bitness, then a summary
};

// hosts: speak every voice through the engine hosts in every bitness.
// sapi: list the OpenEVV voices through SAPI itself, in this process's
// bitness, and speak one through SpVoice -- which proves the installed
// registration. The report's last line starts "RESULT: ".
SelfTestResult run_selftest(bool hosts = true, bool sapi = true,
                            const std::function<void(const std::wstring&)>& progress = nullptr);

} // namespace evv
