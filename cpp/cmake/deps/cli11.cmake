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

if (NOT TARGET deps::cli11)
    FetchContent_Declare(
            deps-cli11
            GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
            GIT_TAG main
            GIT_SHALLOW TRUE
            EXCLUDE_FROM_ALL
    )
    message(STATUS "Fetching cli11 sources")
    set(CLI11_BUILD_DOCS OFF)
    set(CLI11_BUILD_EXAMPLES OFF)
    set(CLI11_BUILD_TESTS OFF)
    FetchContent_MakeAvailable(deps-cli11)
    message(STATUS "Fetching cli11 sources - done")

    add_library(deps::cli11 INTERFACE IMPORTED GLOBAL)
    target_link_libraries(deps::cli11 INTERFACE CLI11::CLI11)
    set(deps-cli11_SOURCE_DIR ${deps-cli11_SOURCE_DIR} CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-cli11_SOURCE_DIR)
endif ()

# Note that library had a failure with nvcc compiler and gcc 9.x headers
#  ...c++/9/tuple(553): error: pack "_UElements" does not have the same number of elements as "_Elements"
#            __and_<is_nothrow_assignable<_Elements&, _UElements>...>::value;
# Not using nvcc for main code that uses cli11 solved the issue.
