#include "zip_reader.h"

#include <cstring>

namespace evv {

// ---- CRC-32 ------------------------------------------------------------------

namespace {

struct CrcTable
{
    uint32_t t[256];
    CrcTable()
    {
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t c = i;
            for (int k = 0; k < 8; ++k) c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
            t[i] = c;
        }
    }
};

} // namespace

uint32_t crc32_of(const void* data, size_t n)
{
    static const CrcTable table;
    const auto* p = static_cast<const uint8_t*>(data);
    uint32_t c = 0xFFFFFFFFu;
    for (size_t i = 0; i < n; ++i) c = table.t[(c ^ p[i]) & 0xFF] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

// ---- inflate ------------------------------------------------------------------
//
// The canonical-code decoder of RFC 1951: a code is read a bit at a time and
// compared with the first code of each length, which needs no tables larger
// than the alphabet. It is slower than a lookup table and fast enough for a
// 2 MB dictionary.

namespace {

constexpr int kMaxBits = 15;

struct Bits
{
    const uint8_t* in;
    size_t size;
    size_t pos = 0;
    uint32_t buffer = 0;
    int count = 0;
    bool overrun = false;

    uint32_t take(int need)
    {
        uint32_t value = buffer;
        while (count < need) {
            if (pos >= size) {
                overrun = true;
                return 0;
            }
            value |= static_cast<uint32_t>(in[pos++]) << count;
            count += 8;
        }
        buffer = value >> need;
        count -= need;
        return value & ((1u << need) - 1);
    }
};

struct Huffman
{
    uint16_t count[kMaxBits + 1];
    uint16_t symbol[288];
};

// Builds the decoder for `n` code lengths. 0 when the code is complete, a
// positive number when it is incomplete, negative when it is over-subscribed.
int build(Huffman& h, const uint8_t* length, int n)
{
    for (int len = 0; len <= kMaxBits; ++len) h.count[len] = 0;
    for (int s = 0; s < n; ++s) ++h.count[length[s]];
    if (h.count[0] == n) return 0;
    int left = 1;
    for (int len = 1; len <= kMaxBits; ++len) {
        left <<= 1;
        left -= h.count[len];
        if (left < 0) return left;
    }
    uint16_t offset[kMaxBits + 1];
    offset[1] = 0;
    for (int len = 1; len < kMaxBits; ++len) offset[len + 1] = static_cast<uint16_t>(offset[len] + h.count[len]);
    for (int s = 0; s < n; ++s) {
        if (length[s]) h.symbol[offset[length[s]]++] = static_cast<uint16_t>(s);
    }
    return left;
}

int decode(Bits& b, const Huffman& h)
{
    int code = 0, first = 0, index = 0;
    for (int len = 1; len <= kMaxBits; ++len) {
        code |= static_cast<int>(b.take(1));
        if (b.overrun) return -1;
        const int count = h.count[len];
        if (code - count < first) return h.symbol[index + (code - first)];
        index += count;
        first += count;
        first <<= 1;
        code <<= 1;
    }
    return -1;
}

const uint16_t kLengthBase[29] = {3,  4,  5,  6,  7,  8,  9,  10, 11,  13,  15,  17,  19,  23, 27,
                                  31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258};
const uint8_t kLengthExtra[29] = {0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0};
const uint16_t kDistBase[30] = {1,   2,   3,   4,   5,   7,    9,    13,   17,   25,   33,   49,   65,    97,    129,
                                193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577};
const uint8_t kDistExtra[30] = {0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13};

struct Output
{
    std::string* buf;
    size_t limit;
};

const char* codes(Bits& b, Output& o, const Huffman& lit, const Huffman& dist)
{
    for (;;) {
        int sym = decode(b, lit);
        if (sym < 0) return "damaged data (bad code)";
        if (sym < 256) {
            if (o.buf->size() >= o.limit) return "more data than the archive says";
            o.buf->push_back(static_cast<char>(sym));
        } else if (sym == 256) {
            return nullptr;
        } else {
            sym -= 257;
            if (sym >= 29) return "damaged data (bad length)";
            const size_t len = kLengthBase[sym] + b.take(kLengthExtra[sym]);
            const int ds = decode(b, dist);
            if (ds < 0 || ds >= 30) return "damaged data (bad distance code)";
            const size_t d = kDistBase[ds] + b.take(kDistExtra[ds]);
            if (b.overrun) return "the data ends too soon";
            if (d > o.buf->size()) return "damaged data (distance too far back)";
            if (o.buf->size() + len > o.limit) return "more data than the archive says";
            size_t from = o.buf->size() - d;
            for (size_t i = 0; i < len; ++i) o.buf->push_back((*o.buf)[from + i]);
        }
    }
}

struct FixedCodes
{
    Huffman lit, dist;
    FixedCodes()
    {
        uint8_t lengths[288];
        int s = 0;
        for (; s < 144; ++s) lengths[s] = 8;
        for (; s < 256; ++s) lengths[s] = 9;
        for (; s < 280; ++s) lengths[s] = 7;
        for (; s < 288; ++s) lengths[s] = 8;
        build(lit, lengths, 288);
        for (s = 0; s < 30; ++s) lengths[s] = 5;
        build(dist, lengths, 30);
    }
};

const char* fixed_block(Bits& b, Output& o)
{
    static const FixedCodes fixed; // built once, safely, by whichever thread comes first
    return codes(b, o, fixed.lit, fixed.dist);
}

const char* dynamic_block(Bits& b, Output& o)
{
    static const uint8_t order[19] = {16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15};
    const int nlen = static_cast<int>(b.take(5)) + 257;
    const int ndist = static_cast<int>(b.take(5)) + 1;
    const int ncode = static_cast<int>(b.take(4)) + 4;
    if (b.overrun || nlen > 286 || ndist > 30) return "damaged data (bad block header)";
    uint8_t lengths[286 + 30] = {};
    for (int i = 0; i < ncode; ++i) lengths[order[i]] = static_cast<uint8_t>(b.take(3));
    Huffman lencode;
    if (build(lencode, lengths, 19) != 0) return "damaged data (bad code lengths)";
    int index = 0;
    while (index < nlen + ndist) {
        int sym = decode(b, lencode);
        if (sym < 0) return "damaged data (bad code length code)";
        if (sym < 16) {
            lengths[index++] = static_cast<uint8_t>(sym);
        } else {
            int len = 0, repeat;
            if (sym == 16) {
                if (index == 0) return "damaged data (repeat with nothing before it)";
                len = lengths[index - 1];
                repeat = 3 + static_cast<int>(b.take(2));
            } else if (sym == 17) {
                repeat = 3 + static_cast<int>(b.take(3));
            } else {
                repeat = 11 + static_cast<int>(b.take(7));
            }
            if (index + repeat > nlen + ndist) return "damaged data (too many code lengths)";
            while (repeat--) lengths[index++] = static_cast<uint8_t>(len);
        }
    }
    if (lengths[256] == 0) return "damaged data (no end of block)";
    Huffman lit, dist;
    int err = build(lit, lengths, nlen);
    if (err < 0 || (err > 0 && nlen != lit.count[0] + lit.count[1])) return "damaged data (bad literal codes)";
    err = build(dist, lengths + nlen, ndist);
    if (err < 0 || (err > 0 && ndist != dist.count[0] + dist.count[1])) return "damaged data (bad distance codes)";
    return codes(b, o, lit, dist);
}

const char* stored_block(Bits& b, Output& o)
{
    b.buffer = 0; // what is left of the byte is dropped
    b.count = 0;
    if (b.pos + 4 > b.size) return "the data ends too soon";
    const uint32_t len = b.in[b.pos] | (b.in[b.pos + 1] << 8);
    const uint32_t inv = b.in[b.pos + 2] | (b.in[b.pos + 3] << 8);
    if (len != (~inv & 0xFFFF)) return "damaged data (bad stored block)";
    b.pos += 4;
    if (b.pos + len > b.size) return "the data ends too soon";
    if (o.buf->size() + len > o.limit) return "more data than the archive says";
    o.buf->append(reinterpret_cast<const char*>(b.in + b.pos), len);
    b.pos += len;
    return nullptr;
}

} // namespace

bool inflate_exact(const uint8_t* in, size_t in_size, size_t size, std::string& out, std::string& error)
{
    out.clear();
    out.reserve(size);
    Bits bits{in, in_size};
    Output o{&out, size};
    bool last = false;
    while (!last) {
        last = bits.take(1) != 0;
        const uint32_t type = bits.take(2);
        if (bits.overrun) {
            error = "the data ends too soon";
            return false;
        }
        const char* problem = type == 0 ? stored_block(bits, o)
                              : type == 1 ? fixed_block(bits, o)
                              : type == 2 ? dynamic_block(bits, o)
                                          : "damaged data (bad block type)";
        if (problem) {
            error = problem;
            return false;
        }
    }
    if (out.size() != size) {
        error = "less data than the archive says";
        return false;
    }
    return true;
}

// ---- the archive ------------------------------------------------------------------

namespace {

uint16_t u16(const std::string& s, size_t at)
{
    return static_cast<uint16_t>(static_cast<uint8_t>(s[at]) | (static_cast<uint8_t>(s[at + 1]) << 8));
}

uint32_t u32(const std::string& s, size_t at)
{
    return static_cast<uint32_t>(u16(s, at)) | (static_cast<uint32_t>(u16(s, at + 2)) << 16);
}

} // namespace

bool ZipArchive::open(const std::string& bytes, std::string& error)
{
    bytes_ = &bytes;
    comment_.clear();
    entries_.clear();
    // The end record is the last 22 bytes plus a comment of up to 65535.
    if (bytes.size() < 22) {
        error = "not a zip file";
        return false;
    }
    size_t eocd = std::string::npos;
    const size_t lowest = bytes.size() > 22 + 65535 ? bytes.size() - 22 - 65535 : 0;
    for (size_t at = bytes.size() - 22;; --at) {
        if (u32(bytes, at) == 0x06054B50u && at + 22 + u16(bytes, at + 20) == bytes.size()) {
            eocd = at;
            break;
        }
        if (at == lowest) break;
    }
    if (eocd == std::string::npos) {
        error = "not a zip file (no end record)";
        return false;
    }
    const uint16_t count = u16(bytes, eocd + 10);
    const uint32_t dir_size = u32(bytes, eocd + 12);
    const uint32_t dir_at = u32(bytes, eocd + 16);
    const uint16_t comment_len = u16(bytes, eocd + 20);
    if (count == 0xFFFF || dir_size == 0xFFFFFFFFu || dir_at == 0xFFFFFFFFu) {
        error = "zip64 archives are not supported";
        return false;
    }
    comment_.assign(bytes, eocd + 22, comment_len);
    if (static_cast<uint64_t>(dir_at) + dir_size > eocd) {
        error = "damaged zip file (directory out of range)";
        return false;
    }
    size_t at = dir_at;
    for (uint16_t i = 0; i < count; ++i) {
        if (at + 46 > eocd || u32(bytes, at) != 0x02014B50u) {
            error = "damaged zip file (bad directory entry)";
            return false;
        }
        const uint16_t flags = u16(bytes, at + 8);
        const uint16_t name_len = u16(bytes, at + 28), extra_len = u16(bytes, at + 30), note_len = u16(bytes, at + 32);
        if (at + 46 + name_len + extra_len + note_len > eocd) {
            error = "damaged zip file (bad directory entry)";
            return false;
        }
        ZipEntry e;
        e.method = u16(bytes, at + 10);
        e.crc = u32(bytes, at + 16);
        e.compressed_size = u32(bytes, at + 20);
        e.size = u32(bytes, at + 24);
        e.local_offset = u32(bytes, at + 42);
        e.name.assign(bytes, at + 46, name_len);
        if (flags & 1) {
            error = "encrypted zip files are not supported";
            return false;
        }
        entries_.push_back(std::move(e));
        at += 46u + name_len + extra_len + note_len;
    }
    return true;
}

bool ZipArchive::read(const ZipEntry& e, std::string& out, std::string& error) const
{
    out.clear();
    if (!bytes_) {
        error = "no archive open";
        return false;
    }
    const std::string& b = *bytes_;
    const size_t at = e.local_offset;
    if (at + 30 > b.size() || u32(b, at) != 0x04034B50u) {
        error = "damaged zip file (bad local header for " + e.name + ")";
        return false;
    }
    const size_t data = at + 30 + u16(b, at + 26) + u16(b, at + 28);
    if (data + e.compressed_size > b.size()) {
        error = "damaged zip file (" + e.name + " runs past the end)";
        return false;
    }
    const auto* p = reinterpret_cast<const uint8_t*>(b.data()) + data;
    if (e.method == 0) {
        if (e.compressed_size != e.size) {
            error = "damaged zip file (" + e.name + " has two sizes)";
            return false;
        }
        out.assign(reinterpret_cast<const char*>(p), e.size);
    } else if (e.method == 8) {
        std::string why;
        if (!inflate_exact(p, e.compressed_size, e.size, out, why)) {
            error = e.name + ": " + why;
            return false;
        }
    } else {
        error = e.name + " uses a compression method that is not supported";
        return false;
    }
    if (crc32_of(out.data(), out.size()) != e.crc) {
        error = e.name + " does not match its checksum";
        out.clear();
        return false;
    }
    return true;
}

} // namespace evv
