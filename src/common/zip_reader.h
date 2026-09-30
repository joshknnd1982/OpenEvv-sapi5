// A reader for the zip files GitHub makes of a branch: stored and deflated
// entries, no encryption and no zip64 (a dictionary is a few megabytes).
//
// Nothing is written to disk from here. A caller asks for an entry by its
// name and gets its bytes, checked against the size and CRC-32 the archive
// records, so a download that was cut short or altered fails instead of
// being installed. The archive comment is available too: `git archive`
// puts the commit's hash there, which is how the community dictionary's
// update check knows which commit a download is.
#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace evv {

struct ZipEntry
{
    std::string name; // as stored, forward slashes
    uint16_t method = 0; // 0 stored, 8 deflated
    uint32_t crc = 0;
    uint32_t compressed_size = 0;
    uint32_t size = 0;
    uint32_t local_offset = 0;
    bool is_directory() const { return !name.empty() && name.back() == '/'; }
};

class ZipArchive
{
public:
    // `bytes` must outlive the archive: entries are read from it in place.
    bool open(const std::string& bytes, std::string& error);

    const std::string& comment() const { return comment_; }
    const std::vector<ZipEntry>& entries() const { return entries_; }

    // The named entry's bytes, or false with the reason in `error`.
    bool read(const ZipEntry& entry, std::string& out, std::string& error) const;

private:
    const std::string* bytes_ = nullptr;
    std::string comment_;
    std::vector<ZipEntry> entries_;
};

// Raw deflate (RFC 1951) of exactly `size` bytes, no more and no fewer.
bool inflate_exact(const uint8_t* in, size_t in_size, size_t size, std::string& out, std::string& error);

uint32_t crc32_of(const void* data, size_t n);

} // namespace evv
