// One version for every binary and the installer. Bump all three together:
// this file, project(... VERSION ...) in CMakeLists.txt, and MyAppVersion in
// installer/openevv.iss.
#pragma once

#define EVV_VERSION_MAJOR 1
#define EVV_VERSION_MINOR 0
#define EVV_VERSION_PATCH 0
#define EVV_VERSION_STRING "1.0.0"
#define EVV_VERSION_WSTRING L"1.0.0"

// The openevv engine the language modules were built from.
#define EVV_ENGINE_COMMIT "7148737"
