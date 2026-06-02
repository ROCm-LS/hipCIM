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


#ifndef CUCIM_PLUGIN_PLUGIN_CONFIG_H
#define CUCIM_PLUGIN_PLUGIN_CONFIG_H

#include "cucim/core/framework.h"

#include <string>
#include <vector>

namespace cucim::plugin
{

#define XSTR(x) STR(x)
#define STR(x) #x

struct EXPORT_VISIBLE PluginConfig
{
    void load_config(const void* json_obj);

    std::vector<std::string> plugin_names{ std::string("hipcim.kit.hipslide@" XSTR(CUCIM_VERSION) ".so"),
                                           std::string("hipcim.kit.hipmed@" XSTR(CUCIM_VERSION) ".so") };
};

#undef STR
#undef XSTR

} // namespace cucim::plugin

#endif // CUCIM_PLUGIN_PLUGIN_CONFIG_H
