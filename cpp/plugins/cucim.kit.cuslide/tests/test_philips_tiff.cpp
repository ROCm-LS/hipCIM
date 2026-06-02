/*
 * SPDX-FileCopyrightText: Copyright (c) 2020, NVIDIA CORPORATION.
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


#include <cucim/memory/memory_manager.h>
#include <openslide/openslide.h>
#include "cuslide/tiff/tiff.h"
#include "config.h"

#include <catch2/catch_test_macros.hpp>
#include <chrono>

TEST_CASE("Verify philips tiff file", "[generic_tiff_000.tif]")
{
    fmt::print("Read Philips TIFF File\n");

    auto tif = std::make_shared<cuslide::tiff::TIFF>(g_config.get_input_path("private/generic_tiff_000.tif").c_str(),
                                                     O_RDONLY); // , cuslide::tiff::TIFF::kUseLibTiff
    tif->construct_ifds();

    int64_t test_sx = 1;
    int64_t test_sy = 1;

    int64_t test_width = 500;
    int64_t test_height = 500;

    cucim::io::format::ImageMetadata metadata{};
    cucim::io::format::ImageReaderRegionRequestDesc request{};
    cucim::io::format::ImageDataDesc image_data{};

    metadata.level_count(1).level_downsamples({ 1.0 }).level_ndim(3);

    int64_t request_location[2] = { test_sx, test_sy };
    request.location = request_location;
    request.level = 0;
    int64_t request_size[2] = { test_width, test_height };
    request.size = request_size;
    request.device = const_cast<char*>("cuda");

    tif->read(&metadata.desc(), &request, &image_data);

    request.associated_image_name = const_cast<char*>("label");
    tif->read(&metadata.desc(), &request, &image_data, nullptr /*out_metadata*/);

    tif->close();

    REQUIRE(1 == 1);
}
