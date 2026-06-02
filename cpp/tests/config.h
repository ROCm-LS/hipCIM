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

#ifndef CUCIM_TESTS_CONFIG_H
#define CUCIM_TESTS_CONFIG_H

#include <string>
#include <cstdlib>

#define XSTR(x) STR(x)
#define STR(x) #x

struct AppConfig
{
    std::string test_folder;
    std::string test_file;
    std::string temp_folder = "/tmp";
    std::string get_input_path(const std::string default_value = "generated/tiff_stripe_4096x4096_256.tif") const
    {
        // If `test_file` is absolute path
        if (!test_folder.empty() && test_file.substr(0, 1) == "/")
        {
            return test_file;
        }
        else
        {
            std::string test_data_folder = test_folder;
            if (test_data_folder.empty())
            {
                if (const char* env_p = std::getenv("CUCIM_TESTDATA_FOLDER"))
                {
                    test_data_folder = env_p;
                }
                else
                {
                    test_data_folder = "test_data";
                }
            }
            if (test_file.empty())
            {
                return test_data_folder + "/" + default_value;
            }
            else
            {
                return test_data_folder + "/" + test_file;
            }
        }
    }
    std::string get_plugin_path(const char* default_value = "hipcim.kit.hipslide@" XSTR(CUCIM_VERSION) ".so")
    {
        std::string plugin_path = default_value;
        if (const char* env_p = std::getenv("CUCIM_TEST_PLUGIN_PATH"))
        {
            plugin_path = env_p;
        }
        return plugin_path;
    }
};

extern AppConfig g_config;

#endif // CUCIM_TESTS_CONFIG_H
