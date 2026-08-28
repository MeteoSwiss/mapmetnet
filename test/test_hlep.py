"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

# Import from this module
from mapmetnet.hlep import info


def test_info():
    """ Test the high-level entry point in hlep.py """

    # Just call the function, to make sure it runs without errors.
    info()
