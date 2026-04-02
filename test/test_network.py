"""
Copyright (c) 2023-2024 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module content: tests for the gbon module
"""

# Import from Python
import pytest
import numpy as np
from cartopy.geodesic import Geodesic

# Import from this package
from mapmetnet.errors import MapmetnetError
from mapmetnet.network import get_delaunay_vertices, get_sep_vertices, compute_mean_sep


def test_get_delaunay_vertices():
    """ Test the ability to assemble a list of Delaunay vertices given a set of coordinates. """

    # Basic test with 3 points
    assert len(get_delaunay_vertices(np.array([0, 1, 0]),
                                     np.array([0, 0.5, 1]))) == 3

    # Test that the vertices are independant of the projection.
    # This should be true according to Saalfeld, Cartography and Geographic Information Science,
    # Vol. 26, No.4, 1999, pp. 289-296
    # https://www.tandfonline.com/doi/pdf/10.1559/152304099782294168

    # Assemble a list of some dummy coordinates ...
    pts = np.array([[15.442, -4.387], [13.583, -5.517], [17.350, -3.300], [18.800, -5.033],
                    [17.067, -4.917], [16.817, -6.483], [19.000, -7.333], [18.267, -1.267],
                    [19.750, -3.417], [18.450, +0.083], [19.840, +1.217], [18.483, +1.483]])
    lons = pts[:, 0]
    lats = pts[:, 1]

    out1 = get_delaunay_vertices(lons, lats, central_latitude=0, central_longitude=0)
    out2 = get_delaunay_vertices(lons, lats, central_latitude=90, central_longitude=0)
    out3 = get_delaunay_vertices(lons, lats, central_latitude=0, central_longitude=90)

    assert out1 == out2
    assert out1 == out3


def test_compute_mean_sep():
    """ Test the ability to compute the mean vertex lengths given a dict of vertices. """

    assert compute_mean_sep({(0, 1): 1, (0, 2): 2, (1, 2): 6}) == 3


def test_get_sep_vertices():
    """ Test the ability to derive lists of separation vertices between locations. """

    # Setup a basic Geodesic to play with Great Circles
    geo = Geodesic()

    scale = 200  # Scale of the grid, in km

    # Assemble a set of basic coordinates with known separations
    pts = [np.zeros(2)]  # Start at the Equator
    pts += [geo.direct(pts[0], 0, scale*1e3)[0][:2]]  # 200km North
    pts += [geo.direct(pts[0], 90, scale*1e3)[0][:2]]  # 200km East
    pts += [geo.direct(pts[2], 0, scale*1e3)[0][:2]]  # 200km North of the East point
    pts = np.array(pts)

    # This square should not be quite a square. Let's compute the distance between the two points
    # North of the Equator (in km).
    dist13, _, _ = geo.inverse(pts[1], pts[3])[0]/1e3

    # If all goes well, the mean distance between these points should be:
    md = 1/4 * (scale*3 + dist13)

    # Test it
    good_verts, bad_verts, not_so_bad_verts = get_sep_vertices(pts[:, 0], pts[:, 1])

    assert len(good_verts) == 4
    assert len(bad_verts) == 0
    assert len(not_so_bad_verts) == 1

    assert np.round(np.mean([item/1e3 for _, item in good_verts.items()]), 3) == np.round(md, 3)

    # Check that the code issues an error if some of the points are duplicated
    pts = np.concatenate((pts, pts[:1]))
    with pytest.raises(MapmetnetError):
        get_sep_vertices(pts[:, 0], pts[:, 1])
