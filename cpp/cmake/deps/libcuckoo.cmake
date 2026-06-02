#
# SPDX-FileCopyrightText: Copyright (c) 2021, NVIDIA CORPORATION.
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

if (NOT TARGET deps::libcuckoo)
    FetchContent_Declare(
            deps-libcuckoo
            GIT_REPOSITORY https://github.com/efficient/libcuckoo
            GIT_TAG master
            GIT_SHALLOW TRUE
    )
    FetchContent_GetProperties(deps-libcuckoo)
    message(STATUS "Patch directory: ${deps-libcuckoo_SOURCE_DIR}")
    if (NOT deps-libcuckoo_POPULATED)
        message(STATUS "Fetching libcuckoo sources")
        FetchContent_Populate(deps-libcuckoo)
        message(STATUS "Fetching libcuckoo sources - done")

        message(STATUS "Applying patch for libcuckoo")
        find_package(Git)
            execute_process(
                COMMAND bash -c "${GIT_EXECUTABLE} reset HEAD --hard && ${GIT_EXECUTABLE} apply --verbose ${CMAKE_CURRENT_LIST_DIR}/libcuckoo.patch"
                WORKING_DIRECTORY "${deps-libcuckoo_SOURCE_DIR}"
                RESULT_VARIABLE exec_result
                ERROR_VARIABLE exec_error
                ERROR_STRIP_TRAILING_WHITESPACE
                OUTPUT_VARIABLE exec_output
                OUTPUT_STRIP_TRAILING_WHITESPACE
                )
            if(exec_result EQUAL 0)
                message(STATUS "Applying patch for libcuckoo - done")
            else()
                message(STATUS "Applying patch for libcuckoo - failed")
                message(FATAL_ERROR "${exec_output}\n${exec_error}")
            endif()
    endif ()

    # Create static library
    cucim_set_build_shared_libs(OFF)
    add_subdirectory(${deps-libcuckoo_SOURCE_DIR} ${deps-libcuckoo_BINARY_DIR} EXCLUDE_FROM_ALL)
    # libcuckoo's CMakeLists.txt is not compatible with `add_subdirectory` method (it uses ${CMAKE_SOURCE_DIR} instead of ${CMAKE_CURRENT_SOURCE_DIR})
    # so add include directories explicitly.
    target_include_directories(libcuckoo INTERFACE
        $<BUILD_INTERFACE:${deps-libcuckoo_SOURCE_DIR}>
    )

    # This prevents 'unused parameter' and 'reorder-ctor' warnings from being treated as errors
    target_compile_options(libcuckoo INTERFACE
            -Wno-unused-parameter
            -Wno-reorder-ctor
    )

    cucim_restore_build_shared_libs()

    add_library(deps::libcuckoo INTERFACE IMPORTED GLOBAL)
    target_link_libraries(deps::libcuckoo INTERFACE libcuckoo)
    set(deps-libcuckoo_SOURCE_DIR ${deps-libcuckoo_SOURCE_DIR} CACHE INTERNAL "" FORCE)
    mark_as_advanced(deps-libcuckoo_SOURCE_DIR)
endif ()
