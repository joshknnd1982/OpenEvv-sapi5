// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Josh Kennedy
// One version for every binary and the installer. Bump all three together:
// this file, project(... VERSION ...) in CMakeLists.txt, and MyAppVersion in
// installer/openevv.iss.
#pragma once

#define EVV_VERSION_MAJOR 1
#define EVV_VERSION_MINOR 4
#define EVV_VERSION_PATCH 0
#define EVV_VERSION_STRING "1.4.0"
#define EVV_VERSION_WSTRING L"1.4.0"

// The openevv engine the language modules were built from. Since 1.3.0 the seven
// template modules carry the TTS extension's accent layer on top of it (openevv/src).
#define EVV_ENGINE_COMMIT "7148737+tts-ext"
