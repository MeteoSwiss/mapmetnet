"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module content: tests for the copyright module
"""

# Import from this module
from mapmetnet.copyright import get_ne_msg, build_copyright_statement, get_mmn_msg


# Test the get_ne_copyright function living in copyright.py
def test_get_ne_copyright():
    """ Test the get_ne_copyright function living in copyright.py """

    assert get_ne_msg(['one', 'two']) == "One, two from Natural Earth."


# Test the mmn function
def test_build_copyright_statement():
    """ Test the build_copyright_statement function living in copyright.py """

    which = {'mmn': None}
    out = build_copyright_statement(which)
    assert out == get_mmn_msg()
