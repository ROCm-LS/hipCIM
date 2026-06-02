/*
 * SPDX-FileCopyrightText: Copyright (c) 2021, NVIDIA CORPORATION.
 * SPDX-License-Identifier: Apache-2.0
 */

// =============================================================================
// MIT License
//
// Modifications Copyright (C) 2024-2026 Advanced Micro Devices, Inc. All rights reserved.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
// =============================================================================

//
#ifndef CUCIM_UTIL_CUDA_H
#define CUCIM_UTIL_CUDA_H


#if CUCIM_SUPPORT_CUDA
#    include <cucim/cuda_runtime.h>
#endif

#define CUDA_TRY(stmt)                                                                                                 \
    {                                                                                                                  \
        cuda_status = stmt;                                                                                \
        if (cudaSuccess != cuda_status)                                                                                \
        {                                                                                                              \
            fmt::print(stderr, "[Error] CUDA Runtime call {} in line {} of file {} failed with '{}' ({}).\n", #stmt,   \
                       __LINE__, __FILE__, cudaGetErrorString(cuda_status), static_cast<int>(cuda_status));            \
        }                                                                                                              \
    }

#define CUDA_ERROR(stmt)                                                                                               \
    {                                                                                                                  \
        cudaError_t cuda_status = stmt;                                                                                \
        if (cudaSuccess != cuda_status)                                                                                \
        {                                                                                                              \
            throw std::runtime_error(                                                                                  \
                fmt::format("[Error] CUDA Runtime call {} in line {} of file {} failed with '{}' ({}).\n", #stmt,      \
                            __LINE__, __FILE__, cudaGetErrorString(cuda_status), static_cast<int>(cuda_status)));      \
        }                                                                                                              \
    }

#define NVJPEG_TRY(stmt)                                                                                               \
    {                                                                                                                  \
        nvjpegStatus_t _nvjpeg_status = stmt;                                                                          \
        if (_nvjpeg_status != NVJPEG_STATUS_SUCCESS)                                                                   \
        {                                                                                                              \
            fmt::print("[Error] NVJPEG call {} in line {} of file {} failed with the error code {}.\n", #stmt,         \
                __LINE__, __FILE__, static_cast<int>(_nvjpeg_status));                                                 \
        }                                                                                                              \
    }

#define NVJPEG_ERROR(stmt)                                                                                             \
    {                                                                                                                  \
        nvjpegStatus_t _nvjpeg_status = stmt;                                                                          \
        if (_nvjpeg_status != NVJPEG_STATUS_SUCCESS)                                                                   \
        {                                                                                                              \
            throw std::runtime_error(                                                                                  \
                fmt::format("[Error] NVJPEG call {} in line {} of file {} failed with the error code {}.\n", #stmt,    \
                            __LINE__, __FILE__, static_cast<int>(_nvjpeg_status)));                                    \
        }                                                                                                              \
    }

namespace cucim::util
{

} // namespace cucim::util

#endif // CUCIM_UTIL_CUDA_H
