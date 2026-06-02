/*
 * SPDX-FileCopyrightText: Copyright (c) 2020-2021, NVIDIA CORPORATION.
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


#define CUCIM_EXPORTS // For exporting functions globally

#include "cucim/memory/memory_manager.h"

#include <memory_resource>

#include <cucim/cuda_runtime.h>
#include <fmt/format.h>

#include "cucim/io/device_type.h"
#include "cucim/profiler/nvtx3.h"
#include "cucim/util/cuda.h"

CUCIM_API void* cucim_malloc(size_t size)
{
    PROF_SCOPED_RANGE(PROF_EVENT_P(cucim_malloc, size));
    return malloc(size);
}

CUCIM_API void cucim_free(void* ptr)
{
    PROF_SCOPED_RANGE(PROF_EVENT(cucim_free));
    free(ptr);
}

namespace cucim::memory
{

void get_pointer_attributes(PointerAttributes& attr, const void* ptr)
{
    cudaError_t cuda_status;

    cudaPointerAttributes attributes;
    CUDA_TRY(cudaPointerGetAttributes(&attributes, ptr));
    if (cuda_status)
    {
        return;
    }

    cudaMemoryType& memory_type = attributes.type;
    switch (memory_type)
    {
    case cudaMemoryTypeUnregistered:
        attr.device = cucim::io::Device(cucim::io::DeviceType::kCPU, -1);
        attr.ptr = const_cast<void*>(ptr);
        break;
    case cudaMemoryTypeHost:
        attr.device = cucim::io::Device(cucim::io::DeviceType::kCUDAHost, attributes.device);
        attr.ptr = attributes.hostPointer;
        break;
    case cudaMemoryTypeDevice:
        attr.device = cucim::io::Device(cucim::io::DeviceType::kCUDA, attributes.device);
        attr.ptr = attributes.devicePointer;
        break;
    case cudaMemoryTypeManaged:
        attr.device = cucim::io::Device(cucim::io::DeviceType::kCUDAManaged, attributes.device);
        attr.ptr = attributes.devicePointer;
        break;
    case hipMemoryTypeArray:
        // Not handling this case yet
        break;
    case hipMemoryTypeUnified:
        // Not handling this case yet
        break;
    }
}

CUCIM_API bool move_raster_from_host(void** target, size_t size, const cucim::io::Device& dst_device)
{
    switch (dst_device.type())
    {
    case cucim::io::DeviceType::kCPU:
        break;
    case cucim::io::DeviceType::kCUDA: {
        cudaError_t cuda_status;
        void* host_mem = *target;
        void* cuda_mem;
        CUDA_TRY(cudaMalloc(&cuda_mem, size));
        if (cuda_status)
        {
            throw std::bad_alloc();
        }
        CUDA_TRY(cudaMemcpy(cuda_mem, host_mem, size, cudaMemcpyHostToDevice));
        if (cuda_status)
        {
            throw std::bad_alloc();
        }
        cucim_free(host_mem);
        *target = cuda_mem;
        break;
    }
    default:
        throw std::runtime_error("Unsupported device type");
    }
    return true;
}

CUCIM_API bool move_raster_from_device(void** target, size_t size, const cucim::io::Device& dst_device)
{
    switch (dst_device.type())
    {
    case cucim::io::DeviceType::kCPU: {
        cudaError_t cuda_status;
        void* cuda_mem = *target;
        void* host_mem = cucim_malloc(size);
        CUDA_TRY(cudaMemcpy(host_mem, cuda_mem, size, cudaMemcpyDeviceToHost));
        if (cuda_status)
        {
            throw std::bad_alloc();
        }
        CUDA_TRY(cudaFree(cuda_mem));
        *target = host_mem;
        break;
    }
    case cucim::io::DeviceType::kCUDA:
        break;
    default:
        throw std::runtime_error("Unsupported device type");
    }
    return true;
}

} // namespace cucim::memory
