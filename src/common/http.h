// One HTTPS GET, through WinHTTP: the system's proxy settings and certificate
// store, no library of our own. Only OpenEvvConfig and the tools link it; the
// SAPI engine and the engine host never touch the network.
#pragma once

#include <string>

namespace evv {

struct HttpResponse
{
    int status = 0;    // the HTTP status, 0 when nothing was received
    std::string body;
    std::string error; // why nothing was received, or why the answer was refused
};

// Follows redirects, gives up on a silent server after about half a minute,
// and refuses a body larger than `max_bytes`. `headers` is extra request
// headers, "Name: value" separated by CRLF, or empty. True only for status 200.
bool http_get(const std::wstring& url, const std::wstring& headers, size_t max_bytes, HttpResponse& out);

} // namespace evv
