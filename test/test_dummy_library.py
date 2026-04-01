"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

from mapmetnet.main import dummy_func


def test_dummy_func():
    """Test the correctness of dummy_func.
    """

    assert dummy_func(3.2) == 3
