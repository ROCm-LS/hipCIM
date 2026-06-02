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


#include "cucim/io/device.h"

#include <regex>
#include <string>
#include <string_view>
#ifdef __HIP_PLATFORM_AMD__
#include <cctype>
#include <cassert>
#endif // __HIP_PLATFORM_AMD__

#include <fmt/format.h>

#include "cucim/macros/defines.h"


namespace cucim::io
{
#ifdef __HIP_PLATFORM_AMD__
// Helper functions for parsing and trimming
inline bool is_valid_type(const std::string& type) {
    if (type.empty()) return false;
    for (char c : type) {
        if (!std::islower(c)) return false;
    }
    return true;
}

inline bool is_valid_index(const std::string& index) {
    if (index.empty()) return false;
    if (index == "0") return true;
    if (index[0] == '0') return false; // leading zero not allowed except "0"
    for (char c : index)
        if (!std::isdigit(c)) return false;
    return true;
}

inline bool is_valid_shm(const std::string& shm) {
    if (shm.empty()) return false;
    for (char c : shm) {
        if (!(std::isalnum(c) || c == '-' || c == '_' || c == '.')) return false;
    }
    return true;
}
#endif // __HIP_PLATFORM_AMD__

Device::Device()
{
    // TODO: consider default case (how to handle -1 index?)
}

Device::Device(const Device& device) : type_(device.type_), index_(device.index_), shm_name_(device.shm_name_)
{
}

Device::Device(const std::string& device_name)
{
    // 'cuda', 'cuda:0', 'cpu[shm0]', 'cuda:0[cuda_shm0]'
#ifndef __HIP_PLATFORM_AMD__
    static const std::regex name_regex("([a-z]+)(?::(0|[1-9]\\d*))?(?:\\[([a-zA-Z0-9_\\-][a-zA-Z0-9_\\-\\.]*)\\])?");

    std::smatch match;
    if (std::regex_match(device_name, match, name_regex))
    {
        type_ = parse_type(match[1].str());
        if (match[2].matched)
        {
            index_ = std::stoi(match[2].str());
        }
        if (match[3].matched)
        {
            shm_name_ = match[3].str();
        }
    }
    else
    {
        CUCIM_ERROR("Device name doesn't match!");
    }
#else // __HIP_PLATFORM_AMD__
    std::string type, index, shm;

    size_t col_pos = device_name.find(':');
    size_t lbrack_pos = device_name.find('[');
    size_t rbrack_pos = device_name.find(']');

    // Extract type
    size_t type_end = (col_pos != std::string::npos) ? col_pos
                    : (lbrack_pos != std::string::npos ? lbrack_pos
                    : device_name.size());
    type = device_name.substr(0, type_end);

    // Optional index
    if (col_pos != std::string::npos) {
        size_t index_start = col_pos + 1;
        size_t index_end = lbrack_pos != std::string::npos ? lbrack_pos : device_name.size();
        index = device_name.substr(index_start, index_end - index_start);
    }

    // Optional shm
    if (lbrack_pos != std::string::npos && rbrack_pos != std::string::npos && lbrack_pos < rbrack_pos) {
        shm = device_name.substr(lbrack_pos + 1, rbrack_pos - lbrack_pos - 1);
    }

    // Validate and assign
    if (is_valid_type(type)
        && (index.empty() || is_valid_index(index))
        && (shm.empty() || is_valid_shm(shm)))
    {
        type_ = parse_type(type);
        if (!index.empty())
            index_ = std::stoi(index);
        if (!shm.empty())
            shm_name_ = shm;
    } else {
        CUCIM_ERROR("Device name doesn't match!");
    }
#endif // !__HIP_PLATFORM_AMD__
    validate_device();
}
Device::Device(const char* device_name) : Device::Device(std::string(device_name))
{
}

Device::Device(DeviceType type, DeviceIndex index)
{
    type_ = type;
    index_ = index;
    validate_device();
}

Device::Device(DeviceType type, DeviceIndex index, const std::string& param)
{
    type_ = type;
    index_ = index;
    shm_name_ = param;
    validate_device();
}

DeviceType Device::parse_type(const std::string& device_name)
{
    return lookup_device_type(device_name);
}
Device::operator std::string() const
{
    std::string_view device_type_str = lookup_device_type_str(type_);

    if (index_ == -1 && shm_name_.empty())
    {
        return fmt::format("{}", device_type_str);
    }
    else if (index_ != -1 && shm_name_.empty())
    {
        return fmt::format("{}:{}", device_type_str, index_);
    }
    else
    {
        return fmt::format("{}:{}[{}]", device_type_str, index_, shm_name_);
    }
}

DeviceType Device::type() const
{
    return type_;
};
DeviceIndex Device::index() const
{
    return index_;
}
const std::string& Device::shm_name() const
{
    return shm_name_;
}

void Device::set_values(DeviceType type, DeviceIndex index, const std::string& param)
{
    type_ = type;
    index_ = index;
    shm_name_ = param;
}

bool Device::validate_device()
{
    // TODO: implement this
    return true;
}

} // namespace cucim::io
