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

if (NOT TARGET deps::abseil)
    FetchContent_Declare(
            deps-abseil
            GIT_REPOSITORY https://github.com/abseil/abseil-cpp.git
            GIT_TAG 20250127.1
            GIT_SHALLOW TRUE
            EXCLUDE_FROM_ALL
            SYSTEM
    )

    # Create static library
    cucim_set_build_shared_libs(OFF)
         # Disable BUILD_TESTING (cmake-build-debug/_deps/deps-abseil-src/CMakeLists.txt:97)
    set(BUILD_TESTING FALSE)
    message(STATUS "Fetching abseil sources")
    FetchContent_MakeAvailable(deps-abseil)
    message(STATUS "Fetching abseil sources - done")

    # Set PIC to prevent the following error message
    # : /usr/bin/ld: ../lib/libabsl_strings.a(escaping.cc.o): relocation R_X86_64_PC32 against symbol `_ZN4absl14lts_2020_02_2516numbers_internal8kHexCharE' can not be used when making a shared object; recompile with -fPIC
    set_target_properties(absl_strings absl_strings_internal absl_int128 absl_raw_logging_internal PROPERTIES POSITION_INDEPENDENT_CODE ON)
    cucim_restore_build_shared_libs()

    add_library(deps::abseil INTERFACE IMPORTED GLOBAL)
    target_link_libraries(deps::abseil INTERFACE absl::strings)
    set(deps-abseil_SOURCE_DIR ${deps-abseil_SOURCE_DIR} CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-abseil_SOURCE_DIR)
endif ()
