"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module content: tests for the utils module
"""

# Import from Python
import pytest
import numpy as np

# Import from this package
from mapmetnet.utils import pad_angular_range, squarify_extent


@pytest.mark.parametrize('val, frac, val_out',
                         [([-1, 1], 0, [-1, 1]),
                          ((-1, 1), 0, (-1, 1)),
                          (np.array([-1, 1]), 0, np.array([-1, 1])),
                          ([0, 2], 0.5, [-1, 3]),
                          ([-1., 3.], 1, [-5., 7.])])
def test_pad_angular_range(val, frac, val_out):
    """ Test the pad_angular_range utility function. """

    # Make sure that the type is conserved
    assert isinstance(pad_angular_range(val, frac), type(val))

    # Check that the padding works as intended
    if isinstance(val, np.ndarray):
        assert (pad_angular_range(val, frac) == val_out).all()
    else:
        assert pad_angular_range(val, frac) == val_out


# test the squariying of the map extent in utils.py
def test_squarify_extent():
    """ Test the squarify_extent utility function. """

    # Test that the function returns the expected output for a simple case
    lon_lims = np.array([-10, 10])
    lat_lims = np.array([-5, 5])
    lon_lims_out, lat_lims_out = squarify_extent(lon_lims, lat_lims)
    assert (np.round(lon_lims_out, 5) == np.array([-10., 10.])).all()
    assert (np.round(lat_lims_out, 5) == np.array([-10., 10.])).all()
