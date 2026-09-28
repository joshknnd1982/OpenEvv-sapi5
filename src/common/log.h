// Diagnostic log for the SAPI engine, the engine host, the configuration
// utility and the tools.
//
// Files live in %ProgramData%\OpenEVV\Logs (the installer grants users write
// access), falling back to %TEMP%\OpenEVV\Logs. Each component and host
// application gets its own file, e.g. "sapi-x64-nvda.log", so a report from one
// screen reader is not interleaved with another program's speech. Files are
// capped at 2 MB with one previous generation kept (*.old.log).
//
// Levels: 0 off, 1 standard (lifecycle, errors, one summary line per
// utterance with timings), 2 full (adds the spoken text, every fragment,
// event and engine call). Standard never records what was spoken.
#pragma once

#include <string>

namespace evv {
namespace log {

constexpr int kOff = 0;
constexpr int kStandard = 1;
constexpr int kFull = 2;

// component: short name such as "sapi-x64" or "config". The file is named
// component-app.log, app being this executable's name unless given (the
// engine host passes its client's name).
void init(const std::wstring& component, const std::wstring& app = std::wstring());
void set_level(int level);
int level();
bool enabled(int lvl);

// printf-style; UTF-8 text. Writes immediately.
void write(int lvl, const char* fmt, ...);

std::wstring directory();
std::wstring file_path();

// Collects lines and writes them in one go, so an utterance's details reach
// the disk after its audio has started rather than before.
class Batch
{
public:
    Batch() = default;
    ~Batch();
    Batch(const Batch&) = delete;
    Batch& operator=(const Batch&) = delete;
    void add(int lvl, const char* fmt, ...);
    void flush();

private:
    std::string lines_;
};

} // namespace log
} // namespace evv
