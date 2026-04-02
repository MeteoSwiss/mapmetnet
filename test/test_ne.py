"""
Copyright (c) 2023-2024 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module content: tests for the ne module
"""

# Import from this module
from mapmetnet.errors import MapmetnetError
from mapmetnet.ne import get_ne_country, get_ne_records


def test_ne_records():
    """ Test the get_ne_records function living in ne.py """

    # Test the default behavior
    out = get_ne_records(resolution='10m', category='cultural',
                         name='admin_0_boundary_lines_land', fmt='list')
    assert len(out) > 0

    # Make sure the attribute keys I care about are in capital letters
    assert 'FEATURECLA' in out[0].attributes.keys()


def test_ne_country():
    """ Test the get_ne_country function living in ne.py """

    # Test the default behavior
    out = get_ne_country('CHE')
    assert out.attributes['ISO_A3'] == 'CHE'
    assert out.attributes['NAME'] == 'Switzerland'

    # Test that a suitable error is raised when needed
    try:
        get_ne_country('CH')
    except MapmetnetError as e:
        assert str(e) == 'Country code "CH" not found in admin_0_map_units.'