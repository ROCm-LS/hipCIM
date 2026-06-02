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

if (NOT TARGET deps::googletest)
    FetchContent_Declare(
            deps-googletest
            GIT_REPOSITORY https://github.com/google/googletest.git
	    GIT_TAG main
            GIT_SHALLOW TRUE
            EXCLUDE_FROM_ALL
    )
    message(STATUS "Fetching googletest sources")
    # Create static library
    cucim_set_build_shared_libs(OFF)
    FetchContent_MakeAvailable(deps-googletest)
    message(STATUS "Fetching googletest sources - done")
    cucim_restore_build_shared_libs()

    add_library(deps::googletest INTERFACE IMPORTED GLOBAL)
    target_link_libraries(deps::googletest INTERFACE googletest)
    set(deps-googletest_SOURCE_DIR ${deps-googletest_SOURCE_DIR} CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-googletest_SOURCE_DIR)
endif ()

#CMake Warning (dev) in cmake-build-debug/_deps/deps-googletest-src/googlemock/CMakeLists.txt:
#  Policy CMP0082 is not set: Install rules from add_subdirectory() are
#  interleaved with those in caller.  Run "cmake --help-policy CMP0082" for
#  policy details.  Use the cmake_policy command to set the policy and
#  suppress this warning.
