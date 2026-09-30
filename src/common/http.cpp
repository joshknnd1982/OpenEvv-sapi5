#include "http.h"

#include <windows.h>
#include <winhttp.h>

#include <cstdio>

#include "version.h"

namespace evv {

namespace {

struct HInternet
{
    HINTERNET h = nullptr;
    ~HInternet()
    {
        if (h) WinHttpCloseHandle(h);
    }
    explicit operator bool() const { return h != nullptr; }
};

std::string describe(DWORD e)
{
    switch (e) {
    case ERROR_WINHTTP_TIMEOUT: return "the server did not answer in time";
    case ERROR_WINHTTP_NAME_NOT_RESOLVED: return "the server's name could not be found; is this computer online?";
    case ERROR_WINHTTP_CANNOT_CONNECT: return "could not connect to the server";
    case ERROR_WINHTTP_CONNECTION_ERROR: return "the connection to the server was lost";
    case ERROR_WINHTTP_SECURE_FAILURE: return "the server's certificate was not accepted";
    default: {
        char b[64];
        snprintf(b, sizeof b, "network error %lu", e);
        return b;
    }
    }
}

} // namespace

bool http_get(const std::wstring& url, const std::wstring& headers, size_t max_bytes, HttpResponse& out)
{
    out = HttpResponse{};

    URL_COMPONENTS uc{};
    uc.dwStructSize = sizeof uc;
    wchar_t host[256], path[2048];
    uc.lpszHostName = host;
    uc.dwHostNameLength = 256;
    uc.lpszUrlPath = path;
    uc.dwUrlPathLength = 2048;
    if (!WinHttpCrackUrl(url.c_str(), 0, 0, &uc) || uc.nScheme != INTERNET_SCHEME_HTTPS) {
        out.error = "only https addresses are read";
        return false;
    }

    const std::wstring agent = L"OpenEVV-SAPI5/" + std::wstring(EVV_VERSION_WSTRING);
    HInternet session;
    // The proxy the system is set up with (Windows 8.1 and later; earlier ones use the default).
    session.h = WinHttpOpen(agent.c_str(), WINHTTP_ACCESS_TYPE_AUTOMATIC_PROXY, WINHTTP_NO_PROXY_NAME,
                            WINHTTP_NO_PROXY_BYPASS, 0);
    if (!session) {
        session.h = WinHttpOpen(agent.c_str(), WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME,
                                WINHTTP_NO_PROXY_BYPASS, 0);
    }
    if (!session) {
        out.error = describe(GetLastError());
        return false;
    }
    // TLS 1.2 is not on by default before Windows 8; the option is refused where it is unknown.
    DWORD protocols = 0x00000800; // WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_2
    WinHttpSetOption(session.h, WINHTTP_OPTION_SECURE_PROTOCOLS, &protocols, sizeof protocols);
    WinHttpSetTimeouts(session.h, 10000, 10000, 20000, 30000);

    HInternet connection;
    connection.h = WinHttpConnect(session.h, host, uc.nPort, 0);
    if (!connection) {
        out.error = describe(GetLastError());
        return false;
    }
    HInternet request;
    request.h = WinHttpOpenRequest(connection.h, L"GET", path, nullptr, WINHTTP_NO_REFERER,
                                   WINHTTP_DEFAULT_ACCEPT_TYPES, WINHTTP_FLAG_SECURE);
    if (!request) {
        out.error = describe(GetLastError());
        return false;
    }
    if (!WinHttpSendRequest(request.h, headers.empty() ? WINHTTP_NO_ADDITIONAL_HEADERS : headers.c_str(),
                            headers.empty() ? 0 : static_cast<DWORD>(-1L), WINHTTP_NO_REQUEST_DATA, 0, 0, 0) ||
        !WinHttpReceiveResponse(request.h, nullptr)) {
        out.error = describe(GetLastError());
        return false;
    }
    DWORD status = 0, size = sizeof status;
    WinHttpQueryHeaders(request.h, WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                        WINHTTP_HEADER_NAME_BY_INDEX, &status, &size, WINHTTP_NO_HEADER_INDEX);
    out.status = static_cast<int>(status);
    if (status != 200) {
        out.error = "the server answered " + std::to_string(status);
        return false;
    }
    for (;;) {
        DWORD available = 0;
        if (!WinHttpQueryDataAvailable(request.h, &available)) {
            out.error = describe(GetLastError());
            out.body.clear();
            return false;
        }
        if (available == 0) break;
        if (out.body.size() + available > max_bytes) {
            out.error = "the answer is larger than expected; refused";
            out.body.clear();
            return false;
        }
        const size_t at = out.body.size();
        out.body.resize(at + available);
        DWORD got = 0;
        if (!WinHttpReadData(request.h, &out.body[at], available, &got)) {
            out.error = describe(GetLastError());
            out.body.clear();
            return false;
        }
        out.body.resize(at + got);
    }
    return true;
}

} // namespace evv
