# SPDX-FileCopyrightText: 2009-2022 the scikit-image team
# SPDX-FileCopyrightText: Copyright (c) 2022-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND BSD-3-Clause

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

import cupy as cp
from cupy.testing import assert_array_equal

from cucim.skimage.segmentation import clear_border
import pytest


def test_clear_border():
    # fmt: off
    image = cp.array(
        [[0, 0, 0, 0, 0, 0, 0, 1, 0],
         [1, 1, 0, 0, 1, 0, 0, 1, 0],
         [1, 1, 0, 1, 0, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 1, 1, 1, 1, 1, 1, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    )
    # fmt: on

    # test default case
    result = clear_border(image.copy())
    ref = image.copy()
    ref[1:3, 0:2] = 0
    ref[0:2, -2] = 0
    assert_array_equal(result, ref)

    # test buffer
    result = clear_border(image.copy(), 1)
    assert_array_equal(result, cp.zeros(result.shape))

    # test background value
    result = clear_border(image.copy(), buffer_size=1, bgval=2)
    assert_array_equal(result, cp.full_like(image, 2))

    # test mask
    mask = cp.array(
        [
            [0, 0, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    ).astype(bool)
    result = clear_border(image.copy(), mask=mask)
    ref = image.copy()
    ref[1:3, 0:2] = 0
    assert_array_equal(result, ref)


def test_clear_border_3d():
    # fmt: off
    image = cp.array(
        [[[0, 0, 0, 0],
          [0, 0, 0, 0],
          [0, 0, 0, 0],
          [1, 0, 0, 0]],
         [[0, 0, 0, 0],
          [0, 1, 1, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 0]],
         [[0, 0, 0, 0],
          [0, 0, 0, 0],
          [0, 0, 0, 0],
          [0, 0, 0, 0]]]
    )
    # fmt: on
    # test default case
    result = clear_border(image.copy())
    ref = image.copy()
    ref[0, 3, 0] = 0
    assert_array_equal(result, ref)

    # test buffer
    result = clear_border(image.copy(), 1)
    assert_array_equal(result, cp.zeros(result.shape))

    # test background value
    result = clear_border(image.copy(), buffer_size=1, bgval=2)
    assert_array_equal(result, cp.full_like(image, 2))

    # test floating-point background value
    image_f32 = image.astype(cp.float32)
    result = clear_border(image_f32, buffer_size=1, bgval=2.5)
    assert_array_equal(result, cp.full_like(image_f32, 2.5))


def test_clear_border_non_binary():
    # fmt: off
    image = cp.array([[1, 2, 3, 1, 2],
                      [3, 3, 5, 4, 2],
                      [3, 4, 5, 4, 2],
                      [3, 3, 2, 1, 2]])

    result = clear_border(image)
    expected = cp.array([[0, 0, 0, 0, 0],
                         [0, 0, 5, 4, 0],
                         [0, 4, 5, 4, 0],
                         [0, 0, 0, 0, 0]])
    # fmt: on
    assert_array_equal(result, expected)
    assert not cp.all(image == result)


def test_clear_border_non_binary_3d():
    # fmt: off
    image3d = cp.array(
        [[[1, 2, 3, 1, 2],
          [3, 3, 3, 4, 2],
          [3, 4, 3, 4, 2],
          [3, 3, 2, 1, 2]],
         [[1, 2, 3, 1, 2],
          [3, 3, 5, 4, 2],
          [3, 4, 5, 4, 2],
          [3, 3, 2, 1, 2]],
         [[1, 2, 3, 1, 2],
          [3, 3, 3, 4, 2],
          [3, 4, 3, 4, 2],
          [3, 3, 2, 1, 2]]]
    )

    result = clear_border(image3d)
    expected = cp.array(
        [[[0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0],
          [0, 0, 5, 0, 0],
          [0, 0, 5, 0, 0],
          [0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0]]]
    )
    # fmt: on

    assert_array_equal(result, expected)
    assert not cp.all(image3d == result)


def test_clear_border_non_binary_inplace():
    # fmt: off
    image = cp.array([[1, 2, 3, 1, 2],
                      [3, 3, 5, 4, 2],
                      [3, 4, 5, 4, 2],
                      [3, 3, 2, 1, 2]])
    result = clear_border(image, out=image)
    expected = cp.array([[0, 0, 0, 0, 0],
                         [0, 0, 5, 4, 0],
                         [0, 4, 5, 4, 0],
                         [0, 0, 0, 0, 0]])
    # fmt: on
    assert_array_equal(result, expected)
    assert_array_equal(image, result)


def test_clear_border_non_binary_inplace_3d():
    # fmt: off
    image3d = cp.array(
        [[[1, 2, 3, 1, 2],
          [3, 3, 3, 4, 2],
          [3, 4, 3, 4, 2],
          [3, 3, 2, 1, 2]],
         [[1, 2, 3, 1, 2],
          [3, 3, 5, 4, 2],
          [3, 4, 5, 4, 2],
          [3, 3, 2, 1, 2]],
         [[1, 2, 3, 1, 2],
          [3, 3, 3, 4, 2],
          [3, 4, 3, 4, 2],
          [3, 3, 2, 1, 2]]]
    )

    result = clear_border(image3d, out=image3d)
    expected = cp.array(
        [[[0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0],
          [0, 0, 5, 0, 0],
          [0, 0, 5, 0, 0],
          [0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0]]]
    )
    # fmt: on
    assert_array_equal(result, expected)
    assert_array_equal(image3d, result)


def test_clear_border_non_binary_out():
    # fmt: off
    image = cp.array([[1, 2, 3, 1, 2],
                      [3, 3, 5, 4, 2],
                      [3, 4, 5, 4, 2],
                      [3, 3, 2, 1, 2]])
    out = cp.empty_like(image)
    result = clear_border(image, out=out)
    expected = cp.array([[0, 0, 0, 0, 0],
                         [0, 0, 5, 4, 0],
                         [0, 4, 5, 4, 0],
                         [0, 0, 0, 0, 0]])
    # fmt: on
    assert_array_equal(result, expected)
    assert_array_equal(out, result)


def test_clear_border_non_binary_out_3d():
    # fmt: off
    image3d = cp.array(
        [[[1, 2, 3, 1, 2],
          [3, 3, 3, 4, 2],
          [3, 4, 3, 4, 2],
          [3, 3, 2, 1, 2]],
         [[1, 2, 3, 1, 2],
          [3, 3, 5, 4, 2],
          [3, 4, 5, 4, 2],
          [3, 3, 2, 1, 2]],
         [[1, 2, 3, 1, 2],
          [3, 3, 3, 4, 2],
          [3, 4, 3, 4, 2],
          [3, 3, 2, 1, 2]]]
    )
    out = cp.empty_like(image3d)

    result = clear_border(image3d, out=out)
    expected = cp.array(
        [[[0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0],
          [0, 0, 5, 0, 0],
          [0, 0, 5, 0, 0],
          [0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0]]]
    )
    # fmt: on

    assert_array_equal(result, expected)
    assert_array_equal(out, result)
