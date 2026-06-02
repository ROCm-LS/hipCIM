#
# SPDX-FileCopyrightText: Copyright (c) 2020-2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0
#

# =============================================================================
# MIT License
#
# Modifications Copyright (C) 2024-2026 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

if (NOT TARGET deps::libopenjpeg)

    FetchContent_Declare(
            deps-libopenjpeg
            GIT_REPOSITORY https://github.com/uclouvain/openjpeg.git
            GIT_TAG v2.5.3
            PATCH_COMMAND ${GIT_EXECUTABLE} apply "${CMAKE_CURRENT_LIST_DIR}/libopenjpeg.patch"
            GIT_SHALLOW TRUE
    )

    # Create static library
    # It build a static library when both BUILD_SHARED_LIBS and BUILD_STATIC_LIBS are ON
    # (build-debug/_deps/deps-libopenjpeg-src/src/lib/openjp2/CMakeLists.txt:94)
    #
    #     if(BUILD_SHARED_LIBS AND BUILD_STATIC_LIBS)
    cucim_set_build_shared_libs(ON)

    message(STATUS "Fetching libopenjpeg sources")
    FetchContent_MakeAvailable(deps-libopenjpeg)
    message(STATUS "Fetching libopenjpeg sources - done")

    ###########################################################################

    # Disable visibility to not expose unnecessary symbols
    set_target_properties(openjp2_static
        PROPERTIES
            C_VISIBILITY_PRESET hidden
            CXX_VISIBILITY_PRESET hidden
            VISIBILITY_INLINES_HIDDEN YES
    )
    # target_compile_options(openjp2_static PRIVATE $<$<CXX_COMPILER_ID:GNU>:-march=core-avx2>)

    # Set PIC to prevent the following error message
    # : /usr/bin/ld: lib/libopenjp2.a(cio.c.o): relocation R_X86_64_PC32 against symbol `opj_stream_read_skip' can not be used when making a shared object; recompile with -fPIC
    #   /usr/bin/ld: final link failed: bad value
    set_target_properties(openjp2_static PROPERTIES POSITION_INDEPENDENT_CODE ON)

    # Set proper RPATH on the shared openjp2 library
    if (TARGET openjp2)
        set_target_properties(openjp2 PROPERTIES
            BUILD_RPATH "$ORIGIN"
            INSTALL_RPATH "$ORIGIN"
        )
    endif()

    cucim_restore_build_shared_libs()

    add_library(deps::libopenjpeg INTERFACE IMPORTED GLOBAL)
    target_link_libraries(deps::libopenjpeg INTERFACE openjp2_static)
    target_include_directories(deps::libopenjpeg
        INTERFACE
            # openjpeg.h is not included in 'openjp2_static' so manually include
            ${deps-libopenjpeg_SOURCE_DIR}/src/lib/openjp2
            # opj_config.h is not included in openjp2_static so manually include
            ${deps-libopenjpeg_BINARY_DIR}/src/lib/openjp2
            # color.h is not included in 'openjp2_static' so manually include
            ${deps-libopenjpeg_SOURCE_DIR}/src/bin/common
            # opj_apps_config.h is not included in 'openjp2_static' so manually include
            ${deps-libopenjpeg_BINARY_DIR}/src/bin/common
    )

    set(deps-libopenjpeg_SOURCE_DIR ${deps-libopenjpeg_SOURCE_DIR} CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-libopenjpeg_SOURCE_DIR)
    set(deps-libopenjpeg_BINARY_DIR ${deps-libopenjpeg_BINARY_DIR} CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-libopenjpeg_BINARY_DIR)

    ###########################################################################
    # Build liblcms2 with the source in libopenjpeg
    ###########################################################################

    add_subdirectory(${deps-libopenjpeg_SOURCE_DIR}/thirdparty/liblcms2 ${deps-libopenjpeg_BINARY_DIR}/thirdparty/liblcms2)

    # Set PIC to prevent the following error message
    # : /usr/bin/ld: _deps/deps-libopenjpeg-build/thirdparty/lib/liblcms2.a(cmserr.c.o): relocation R_X86_64_PC32 against symbol `_cmsMemPluginChunk' can not be used when making a shared object; recompile with -fPIC
    #   /usr/bin/ld: final link failed: bad value
    set_target_properties(lcms2 PROPERTIES POSITION_INDEPENDENT_CODE ON)

    # Override the output library folder path
    set_target_properties(lcms2
        PROPERTIES
        OUTPUT_NAME "lcms2"
        ARCHIVE_OUTPUT_DIRECTORY ${deps-libopenjpeg_BINARY_DIR}/thirdparty/lib)

    # Override definition of OPJ_HAVE_LIBLCMS2 to build color_apply_icc_profile() method
    target_compile_definitions(lcms2
        PUBLIC
            OPJ_HAVE_LIBLCMS2=1
    )

    add_library(deps::libopenjpeg-lcms2 INTERFACE IMPORTED GLOBAL)
    target_link_libraries(deps::libopenjpeg-lcms2 INTERFACE lcms2)
    target_include_directories(deps::libopenjpeg-lcms2
        INTERFACE
            # lcms2.h is not included in 'lcms2' so manually include
            ${deps-libopenjpeg_SOURCE_DIR}/thirdparty/liblcms2/include
    )

    set(deps-libopenjpeg-lcms2_SOURCE_DIR ${deps-libopenjpeg_SOURCE_DIR}/thirdparty/liblcms2 CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-libopenjpeg-lcms2_SOURCE_DIR)
    set(deps-libopenjpeg-lcms2_BINARY_DIR ${deps-libopenjpeg_BINARY_DIR}/thirdparty/liblcms2 CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-libopenjpeg-lcms2_BINARY_DIR)
endif ()
