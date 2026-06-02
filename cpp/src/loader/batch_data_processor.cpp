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


#include "cucim/loader/batch_data_processor.h"

#include <cucim/cuda_runtime.h>
#include <fmt/format.h>

#include "cucim/cache/image_cache_manager.h"

namespace cucim::loader
{

BatchDataProcessor::BatchDataProcessor(const uint32_t batch_size) : batch_size_(batch_size), processed_index_count_(0)
{
}

BatchDataProcessor::~BatchDataProcessor()
{
}


void BatchDataProcessor::add_tile(const TileInfo& tile)
{
    tiles_.emplace_back(tile);
    ++total_index_count_;
}

TileInfo BatchDataProcessor::remove_front_tile()
{
    const TileInfo tile = tiles_.front();
    tiles_.pop_front();
    ++processed_index_count_;
    return tile;
}

uint32_t BatchDataProcessor::request(std::deque<uint32_t>& batch_item_counts, const uint32_t num_remaining_patches)
{
    (void)batch_item_counts;
    (void)num_remaining_patches;
    return 0;
}

uint32_t BatchDataProcessor::wait_batch(const uint32_t index_in_task,
                                        std::deque<uint32_t>& batch_item_counts,
                                        const uint32_t num_remaining_patches)
{
    (void)index_in_task;
    (void)batch_item_counts;
    (void)num_remaining_patches;
    return 0;
}

std::shared_ptr<cucim::cache::ImageCacheValue> BatchDataProcessor::wait_for_processing(const uint32_t)
{
    return std::shared_ptr<cucim::cache::ImageCacheValue>();
}

void BatchDataProcessor::shutdown()
{
}

} // namespace cucim::loader
