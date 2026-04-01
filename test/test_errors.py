"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

# Import from this module
from mapmetnet.errors import MapmetnetError, MapmetnetWarning


# Test the custom error and warning classes living in errors.py
def test_errors():
    """ Test the custom error and warning classes living in errors.py """

    # Test the error class
    try:
        raise MapmetnetError("This is a custom error.")
    except MapmetnetError as e:
        assert str(e) == "This is a custom error."

    # Test the warning class
    try:
        raise MapmetnetWarning("This is a custom warning.")
    except MapmetnetWarning as w:
        assert str(w) == "This is a custom warning."
