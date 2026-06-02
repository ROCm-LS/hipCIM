#
# SPDX-FileCopyrightText: Copyright (c) 2020-2021, NVIDIA CORPORATION.
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

cucim_set_build_shared_libs(OFF)

# Disable visibility to not expose unnecessary symbols
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN YES)
find_package(HIP REQUIRED)
enable_language(HIP)
include_directories(${HIP_INCLUDE_DIRS})
set(FMT_INCLUDE_DIR "${CMAKE_BINARY_DIR}/_deps/deps-fmt-src/include")

# Find and enable HIP
find_package(HIP REQUIRED)
enable_language(HIP)
include_directories(${HIP_INCLUDE_DIRS})

# Set FMT include directory
set(FMT_INCLUDE_DIR "${CMAKE_BINARY_DIR}/_deps/deps-fmt-src/include")

# Set RPATH
if (NOT APPLE)
    set(CMAKE_INSTALL_RPATH $ORIGIN)
endif ()

# Find CUDA Toolkit for cudart and cufile.
#find_package(CUDAToolkit REQUIRED COMPONENTS cuFile)

################################################################################
# Add library: cufile_stub
################################################################################
add_library(cufile_stub
        include/cufile_stub.h
        include/cufile_amd.h
        src/cufile_stub.cpp
        )

# Compile options
set_target_properties(cufile_stub
    PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
        # To prevent the error message:
        # /usr/bin/ld: ../lib/libcufile_stub.a(cufile_stub.cpp.o): relocation R_X86_64_PC32 against symbol
        # __fatbinwrap_46_tmpxft_00005869_00000000_6_cufile_stub_cpp1_ii_1e2ddd49' can not be used when making
        # a shared object; recompile with -fPIC
        POSITION_INDEPENDENT_CODE ON
)
target_compile_definitions(cufile_stub PRIVATE __HIP_PLATFORM_AMD__)

# Add HIP platform definition
target_compile_definitions(cufile_stub PRIVATE __HIP_PLATFORM_AMD__)

# Note: Looks like the following line causes error on CMake 3.18.4 (it is working on 3.18.2). Keeping it for now.
set(CUCIM_REQUIRED_FEATURES cxx_std_17)
target_compile_features(cufile_stub PRIVATE ${CUCIM_REQUIRED_FEATURES})

# Use generator expression to avoid `nvcc fatal   : Value '-std=c++17' is not defined for option 'Werror'`
target_compile_options(cufile_stub
    PRIVATE
        $<$<COMPILE_LANGUAGE:CXX>:-Werror -Wall -Wextra>
        )

## Link libraries
target_link_libraries(cufile_stub
    PUBLIC
        ${CMAKE_DL_LIBS}
    PRIVATE
        # HIP runtime is implicitly linked when HIP is enabled
)

# Set GDS include path - for AMD/HIP, use local include directory
# (GDS is NVIDIA-specific, so we're not looking for CUDA paths)
set(GDS_INCLUDE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/include)
message("Set GDS_INCLUDE_PATH to '${GDS_INCLUDE_PATH}'.")

# Enabling CUCIM_STATIC_GDS assumes that lib/libcufile_static.a and include/cufile.h is available
# under ../temp/cuda folder.
# Note: For AMD/HIP builds, this is disabled by default as GDS is NVIDIA-specific
if (CUCIM_STATIC_GDS)
    add_library(deps::gds_static STATIC IMPORTED GLOBAL)
    if (DEFINED ENV{CONDA_BUILD})
        set(GDS_STATIC_LIB_PATH "$ENV{PREFIX}/lib/libcufile_static.a")
    elseif (DEFINED ENV{CONDA_PREFIX})
        set(GDS_STATIC_LIB_PATH "$ENV{CONDA_PREFIX}/lib/libcufile_static.a")
    elseif (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../temp/cuda/lib64/libcufile_static.a)
        set(GDS_STATIC_LIB_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../temp/cuda/lib64/libcufile_static.a)
    else ()
        set(GDS_STATIC_LIB_PATH /usr/local/cuda/lib64/libcufile_static.a)
    endif ()
    message("Set GDS_STATIC_LIB_PATH to '${GDS_STATIC_LIB_PATH}'.")

    set_target_properties(deps::gds_static
        PROPERTIES
            IMPORTED_LOCATION "${GDS_STATIC_LIB_PATH}"
            INTERFACE_INCLUDE_DIRECTORIES "${GDS_INCLUDE_PATH}"
    )

    # Use `dlopen` to load cuFile at runtime
    target_link_libraries(cufile_stub
        PUBLIC
            ${CMAKE_DL_LIBS}
        PRIVATE
            deps::gds_static
    )
endif()

target_compile_definitions(cufile_stub
PUBLIC
        CUCIM_SUPPORT_GDS=$<BOOL:${CUCIM_SUPPORT_GDS}>
        CUCIM_STATIC_GDS=$<BOOL:${CUCIM_STATIC_GDS}>
)

target_include_directories(cufile_stub
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/include>
        $<BUILD_INTERFACE:${GDS_INCLUDE_PATH}>
        ${FMT_INCLUDE_DIR}
    PRIVATE
        # Add path to cufile.h explicitly.
        # ${TOP}/temp/cuda would be available by ./run copy_gds_files_
        ${CMAKE_CURRENT_SOURCE_DIR}/../cpp/include  # for including helper.h in cucim/dynlib
)

add_library(deps::gds ALIAS cufile_stub)

# Do not generate SONAME as this would be used as a stub library for building on CentOS
# until cufile has a static library.
# Need to use IMPORTED_NO_SONAME when using this .so file.
# : https://stackoverflow.com/questions/27261288/cmake-linking-shared-c-object-from-externalproject-produces-binaries-with-rel
#set_target_properties(cufile_stub PROPERTIES NO_SONAME 1)
#target_link_options(cufile_stub PRIVATE "LINKER:-soname=cufile.so")

## Build a fake libcufile.so
#set_target_properties(cufile_stub PROPERTIES OUTPUT_NAME "cufile")


#
#################################################################################
## Add tests
#################################################################################
#add_subdirectory(tests)

cucim_restore_build_shared_libs()
