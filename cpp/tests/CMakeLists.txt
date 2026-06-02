#
# SPDX-FileCopyrightText: Copyright (c) 2020, NVIDIA CORPORATION.
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

include(CTest)
enable_testing()

message(CUCIM_PACKAGE_NAME="${CUCIM_PACKAGE_NAME}")
################################################################################
# Add executable: cucim_tests
################################################################################
add_executable(cucim_tests
        main.cpp
        test_read_region.cpp
        test_cufile.cpp
        test_metadata.cpp
        )

set_target_properties(cucim_tests
    PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
)
target_compile_definitions(cucim_tests PRIVATE __HIP_PLATFORM_AMD__)
target_compile_features(cucim_tests PRIVATE ${CUCIM_REQUIRED_FEATURES})

# Use generator expression to avoid `nvcc fatal   : Value '-std=c++17' is not defined for option 'Werror'`
#target_compile_options(cucim_tests PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-Werror -Wall -Wextra>)
target_compile_definitions(cucim_tests
    PUBLIC
        CUCIM_VERSION=${PROJECT_VERSION}
        CUCIM_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
        CUCIM_VERSION_MINOR=${PROJECT_VERSION_MINOR}
        CUCIM_VERSION_PATCH=${PROJECT_VERSION_PATCH}
        CUCIM_VERSION_BUILD=${PROJECT_VERSION_BUILD}
)

# Include pthread
# (https://cmake.org/cmake/help/v3.18/module/FindThreads.html)
set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
set(THREADS_PREFER_PTHREAD_FLAG TRUE)
find_package(Threads REQUIRED)

target_link_libraries(cucim_tests
        PRIVATE
            ${CUCIM_PACKAGE_NAME}
	    ${HIP_LIBRARIES}
            deps::catch2
            deps::openslide
            deps::taskflow
            Threads::Threads # -lpthread
        )

include(Catch)
# See https://github.com/catchorg/Catch2/blob/devel/docs/cmake-integration.md#catchcmake-and-catchaddtestscmake for other options
# Do not use catch_discover_tests() since it causes a test to be run at build time
# and somehow it causes a deadlock during the build.
# catch_discover_tests(cucim_tests)
