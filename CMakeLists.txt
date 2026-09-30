cmake_minimum_required(VERSION 3.20)
# Keep in step with src/common/version.h and installer/openevv.iss.
project(OpenEvvSAPI VERSION 1.2.2 LANGUAGES C CXX RC)

# The SAPI5 wrapper, the engine host, the configuration utility and the test
# tools, built with MSVC for one architecture per build tree (build_all.bat
# builds both). The engine itself -- one module per language -- is built by
# engine/build_modules.sh with mingw GCC from the openevv sources and ships
# prebuilt in languages/.

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(EVV_ARCH x64)
else()
    set(EVV_ARCH x86)
endif()
message(STATUS "OpenEVV SAPI5: building ${EVV_ARCH}")

add_compile_definitions(UNICODE _UNICODE NOMINMAX _CRT_SECURE_NO_WARNINGS)
if(MSVC)
    add_compile_options($<$<COMPILE_LANGUAGE:C,CXX>:/W3> $<$<COMPILE_LANGUAGE:C,CXX>:/MP>
                        $<$<COMPILE_LANGUAGE:C,CXX>:/utf-8>)
endif()
include_directories(${CMAKE_SOURCE_DIR}/src)

# --- shared by every binary ----------------------------------------------------
add_library(evv_common STATIC
    src/common/log.cpp
    src/common/paths.cpp
    src/common/ini.cpp
    src/common/settings.cpp
    src/common/languages.cpp
    src/common/text_codec.cpp
    src/common/pauses.cpp
    src/common/voice_math.cpp
    src/common/host_client.cpp
    src/common/render.cpp
    src/common/eci_module.cpp
)
target_link_libraries(evv_common PUBLIC shell32 ole32 advapi32)

# --- the engine host: one language module per process ---------------------------
# Never /CETCOMPAT: the engine backtracks through a landing place that restores
# the stack pointer itself, which a hardware shadow stack refuses.
add_executable(OpenEvvHost WIN32 src/host/host_main.cpp src/host/frontend_client.cpp src/host/host.rc)
target_link_libraries(OpenEvvHost PRIVATE evv_common)
target_link_options(OpenEvvHost PRIVATE /CETCOMPAT:NO)

# --- the SAPI5 engine ---------------------------------------------------------------
add_library(OpenEvvSAPI SHARED
    src/sapi/sapi_main.cpp
    src/sapi/com.cpp
    src/sapi/registry.cpp
    src/sapi/ISpDataKeyImpl.cpp
    src/sapi/IEnumSpObjectTokensImpl.cpp
    src/sapi/ISpTTSEngineImpl.cpp
    src/sapi/voice_token.cpp
    src/sapi/openevv_sapi.def
    src/sapi/openevv_sapi.rc
)
target_link_libraries(OpenEvvSAPI PRIVATE evv_common sapi ole32 oleaut32 advapi32 shell32)

# --- configuration utility ------------------------------------------------------------
if(EXISTS ${CMAKE_SOURCE_DIR}/src/config/config_main.cpp)
    add_executable(OpenEvvConfig WIN32
        src/config/config_main.cpp
        src/config/selftest.cpp
        src/config/config.rc
    )
    target_link_libraries(OpenEvvConfig PRIVATE evv_common comctl32 ole32 oleacc sapi shell32 winmm)
    target_link_options(OpenEvvConfig PRIVATE /MANIFEST:NO) # config.rc embeds its own manifest
endif()

# --- tools ------------------------------------------------------------------------------
add_executable(evv_probe src/tools/evv_probe.cpp)
target_link_libraries(evv_probe PRIVATE evv_common)
add_executable(evv_chars src/tools/evv_chars.cpp)
target_link_libraries(evv_chars PRIVATE evv_common)
add_executable(evv_say src/tools/evv_say.cpp)
target_link_libraries(evv_say PRIVATE evv_common)
add_dependencies(evv_say OpenEvvHost)
if(EXISTS ${CMAKE_SOURCE_DIR}/src/tools/evv_render.cpp)
    add_executable(evv_render src/tools/evv_render.cpp)
    target_link_libraries(evv_render PRIVATE evv_common)
    add_dependencies(evv_render OpenEvvHost)
endif()
if(EXISTS ${CMAKE_SOURCE_DIR}/src/tools/sapi_test.cpp)
    add_executable(sapi_test src/tools/sapi_test.cpp)
    target_link_libraries(sapi_test PRIVATE evv_common ole32 sapi shell32)
    add_dependencies(sapi_test OpenEvvSAPI OpenEvvHost)
    # The same tests inside a process that enforces CET shadow stacks, the way
    # 64-bit PowerShell and Narrator do: the engine must stay out of it.
    if(EVV_ARCH STREQUAL "x64")
        add_executable(sapi_test_cet src/tools/sapi_test.cpp)
        target_link_libraries(sapi_test_cet PRIVATE evv_common ole32 sapi shell32)
        target_link_options(sapi_test_cet PRIVATE /CETCOMPAT)
        add_dependencies(sapi_test_cet OpenEvvSAPI OpenEvvHost)
    endif()
endif()
if(EXISTS ${CMAKE_SOURCE_DIR}/src/tools/a11y_check.cpp)
    add_executable(a11y_check src/tools/a11y_check.cpp)
    target_link_libraries(a11y_check PRIVATE oleacc ole32 oleaut32 user32)
endif()
if(EXISTS ${CMAKE_SOURCE_DIR}/src/tools/installer_a11y.cpp)
    add_executable(installer_a11y src/tools/installer_a11y.cpp)
    target_link_libraries(installer_a11y PRIVATE oleacc ole32 oleaut32 user32 advapi32)
endif()
