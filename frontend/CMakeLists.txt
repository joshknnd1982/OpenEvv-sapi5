cmake_minimum_required(VERSION 3.20)
project(OpenEvvFrontend VERSION 1.1.0 LANGUAGES C CXX)

# OpenEvvFrontend: eSpeak NG's reading of a text, written as pronunciations in
# an openevv module's phoneme alphabet. It links eSpeak NG, so it is a program
# of its own under the GPL version 3 or later (COPYING), and the SAPI wrapper
# talks to it over pipes. One build tree per architecture; build_all.bat
# builds both.
#
# eSpeak NG is fetched from ESPEAK_NG_GIT_REPOSITORY at ESPEAK_NG_GIT_TAG, or
# taken from ESPEAK_NG_SOURCE_DIR when that is set (a local checkout, used as
# it stands).

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(ESPEAK_NG_SOURCE_DIR "" CACHE PATH "A local eSpeak NG checkout to build instead of fetching one")
set(ESPEAK_NG_GIT_REPOSITORY "https://github.com/joshknnd1982/espeak-ng.git" CACHE STRING "Where to fetch eSpeak NG from")
set(ESPEAK_NG_GIT_TAG "openevv-1.1.0" CACHE STRING "Branch, tag or commit of eSpeak NG to build")

set(USE_ASYNC OFF CACHE BOOL "" FORCE)
set(USE_MBROLA OFF CACHE BOOL "" FORCE)
set(USE_LIBSONIC OFF CACHE BOOL "" FORCE)
set(USE_LIBPCAUDIO OFF CACHE BOOL "" FORCE)
set(USE_SPEECHPLAYER OFF CACHE BOOL "" FORCE)
set(USE_KLATT OFF CACHE BOOL "" FORCE)
set(ENABLE_TESTS OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)

if(ESPEAK_NG_SOURCE_DIR)
    message(STATUS "eSpeak NG: local checkout ${ESPEAK_NG_SOURCE_DIR}")
    add_subdirectory(${ESPEAK_NG_SOURCE_DIR} espeak-ng-build)
    set(ESPEAK_SRC ${ESPEAK_NG_SOURCE_DIR})
else()
    include(FetchContent)
    FetchContent_Declare(espeak-ng
        GIT_REPOSITORY ${ESPEAK_NG_GIT_REPOSITORY}
        GIT_TAG ${ESPEAK_NG_GIT_TAG}
        GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(espeak-ng)
    set(ESPEAK_SRC ${espeak-ng_SOURCE_DIR})
endif()

if(MSVC)
    foreach(t espeak-ng espeak-ng-bin)
        if(TARGET ${t})
            target_compile_options(${t} PRIVATE /wd4244 /wd4267 /wd4018 /wd4996 /wd4146 /wd4305 /wd4101 /wd4090)
        endif()
    endforeach()
endif()

add_executable(OpenEvvFrontend
    src/frontend_main.c
    src/evv_map.c
)
target_include_directories(OpenEvvFrontend PRIVATE
    ${ESPEAK_SRC}/src/libespeak-ng
    ${ESPEAK_SRC}/src/include
    ${ESPEAK_SRC}/src/include/compat
    $<TARGET_PROPERTY:espeak-ng-config,INTERFACE_INCLUDE_DIRECTORIES>
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/common
)
target_compile_definitions(OpenEvvFrontend PRIVATE LIBESPEAK_NG_EXPORT=1 _CRT_SECURE_NO_WARNINGS)
target_link_libraries(OpenEvvFrontend PRIVATE espeak-ng)
if(MSVC)
    target_compile_options(OpenEvvFrontend PRIVATE /utf-8 /W3 /wd4996)
endif()
if(TARGET data)
    add_dependencies(OpenEvvFrontend data)
endif()

# Where the compiled eSpeak NG data ends up, for build_all.bat to stage.
if(TARGET data)
    get_target_property(_espeak_bin espeak-ng-bin BINARY_DIR)
endif()
