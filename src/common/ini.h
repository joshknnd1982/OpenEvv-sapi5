// A small INI reader and writer for UTF-8 files (with or without a BOM), so
// language.ini and settings.ini can be edited in Notepad. Section and key
// names are case-insensitive; ';' and '#' start a comment line.
#pragma once

#include <map>
#include <string>
#include <vector>

namespace evv {

struct CaseLess
{
    bool operator()(const std::wstring& a, const std::wstring& b) const
    {
        return _wcsicmp(a.c_str(), b.c_str()) < 0;
    }
};

class Ini
{
public:
    using Section = std::map<std::wstring, std::wstring, CaseLess>;

    bool load(const std::wstring& path);
    bool save(const std::wstring& path, const std::string& header_comment = std::string()) const;

    bool has(const std::wstring& section) const;
    std::wstring get(const std::wstring& section, const std::wstring& key, const std::wstring& def = L"") const;
    int get_int(const std::wstring& section, const std::wstring& key, int def) const;
    bool get_bool(const std::wstring& section, const std::wstring& key, bool def) const;
    void set(const std::wstring& section, const std::wstring& key, const std::wstring& value);
    void set_int(const std::wstring& section, const std::wstring& key, int value);
    void remove_section(const std::wstring& section);
    std::vector<std::wstring> sections() const;
    const Section* section(const std::wstring& name) const;

private:
    std::vector<std::pair<std::wstring, Section>> sections_; // keeps file order
    Section* find(const std::wstring& name);
    const Section* find(const std::wstring& name) const;
};

std::wstring utf8_to_wide(const std::string& s);
std::string wide_to_utf8(const std::wstring& s);
std::wstring trim(const std::wstring& s);

} // namespace evv
