"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: utility functions related to network characterization
"""

# Import from Python
import logging
from itertools import combinations
import numpy as np
from scipy.spatial import Delaunay  # pylint: disable=no-name-in-module
import cartopy.crs as ccrs
from cartopy.geodesic import Geodesic
from shapely import LineString, polygonize

# Import from this package
from .errors import MapmetnetError
from .logger import log_func_call

# Instantiate the module logger
logger = logging.getLogger(__name__)


@log_func_call(logger)
def get_mean_sep(lons: np.ndarray, lats: np.ndarray, drop_not_so_bad: bool = False) -> tuple:
    """ Compute the mean separation between a series of coordinates on Earth.

    Args:
        lons (np.ndarray): array of longitudes, in fractional degrees.
        lats (np.ndarray): array of latitudes, in fractional degrees.
        drop_not_so_bad (bool, optional): if True, the not_so_bad neighbors will be ignored.
            Defaults to False.

    Returns:
        float, float, dict: the mean separation (in km), the median separation (in km), and the
        neighbor vertices used to compute the mean separation.

    See :py:func:`get_neighbors` for more details on the identification of neighbor vertices used
    to compute the mean separation.
    """

    # Step 1: find the vertices connecting the different locations
    neighbors, _, not_so_bad_neighbors = get_neighbors(lons, lats)

    # Step 2: merge the not-so-bad vertices if warranted
    if not drop_not_so_bad:
        neighbors = neighbors | not_so_bad_neighbors

    # Step 3: compute the mean separation along all the good vertices
    mean_sep, median_sep = compute_mean_sep(neighbors)
    mean_sep /= 1.e3  # m to km
    median_sep /= 1.e3  # m to km

    return mean_sep, median_sep, neighbors


@log_func_call(logger)
def get_neighbors(lons: np.ndarray, lats: np.ndarray) -> tuple[dict, dict, dict]:
    """ Assemble a list of vertices separating a series of coordinates on Earth.

    Args:
        lons (np.ndarray): array of longitudes, in fractional degrees.
        lats (np.ndarray): array of latitudes, in fractional degrees.

    Returns:
        dict, dict, dict: "good" neighbor vertices, "bad" neighbor vertices, and "not so bad"
        neighbor vertices, where the dict keys are len(2)-lists of the (original) point indices, and
        the entries are their respective lengths (measured along Great Circles).

    Raises:
        MapmetnetError: if some of the input points are duplicated.

    This function implements a robust and unambiguous method for identifying "neighboring" nodes
    in a given network. It was first introduced in Appendix A of the SOFF National Contribution Plan
    for the Democratic Republic of Congo (see `Vogt et al., 2024`_) to which we refer the
    interested reader for more details. What follows is a summary of this document.

    The "potentially neighboring" vertices are identified via a Delaunay triangulation
    (see :py:func:`get_delaunay_vertices`).

    This approach is warranted by the fact that the Delaunay triangulation is the dual graph of
    the Voronoi tessellation: a most natural way to define the "immediate neighborhood" of a set of
    nodes. Specifically, a Voronoi tessellation defines unique polygons around each node in a set,
    where each polygon contains all the locations that are closer to one specific node than to any
    other node in the set. Neighboring nodes are those that share a common Voronoi cell edge - a
    criteria which essentially corresponds to the Delaunay triangulation.

    While a Delaunay triangulation allows to identify "mathematical" neighbors, not all of these
    would typically be considered as being neighbors in the "physical" sense (thinking of stations
    in the real world). To sort the "true" neighboring vertices from the rest, we use the following
    *mid-point criteria*:

    **Vertices listed as "good" neighbors are those for which the mid-point is closest (strictly) to
    its end nodes than to any other node in the set.**

    Vertices that do not respect this criterium are provided in "bad" neighbors and
    "not so bad" neighbors. The only difference between these two sets is that vertices inside
    "not so bad" neighbors are located within a (closed) polygon formed by "good" neighbors.

    Essentially, this mid-point criteria is used as a simple way to cull vertices towards the outer
    edges of the network, that one would not typically associated to the concept of "neighboring"
    stations.

    .. _Vogt et al., 2024: https://www.un-soff.org/wp-content/uploads/2025/02/Democratic-Republic-of-Congo-GBON-National-Gap-Analysis.pdf.

    """

    # Check that there are no duplicated sets of coordinates, as this could cause trouble.
    if len(np.unique(np.stack([lons, lats], axis=-1), axis=0)) != len(lons):
        raise MapmetnetError('Duplicated sets of (lat, lon) coordinates.')

    # Begin by performing a Delaunay triangulation, adn extract a list of vertices.
    verts = get_delaunay_vertices(lons, lats)

    # Stack the coordinates in a list of stations, for easier handling
    pts = np.stack((lons, lats), axis=-1)

    # If the network is no convex, some of the outer vertices will bias the mean distance
    # calculation by connecting (possibly) far away stations.
    # Let us find those, so that they can be ignored.

    # Set a basic Geodesic, so that we can toy around with Great Circles.
    geo = Geodesic()

    # Let's now make two piles of vertices. The ones we like, and the ones we do not.
    neighbors: dict = {}
    not_neighbors: dict = {}

    # Let's check them all one by one, and decide which is which
    for vert in verts:

        # Compute the distance of the vertice, and get the starting azimuth while we're at it.
        # Note here thast this is the "true" distance along the Great Circle.
        dist, az0, _ = geo.inverse(pts[vert[0]], pts[vert[1]])[0]

        # Next we compute the coordinates of the half-way point along the same Great Circle
        mid_pt = geo.direct(pts[vert[0]], az0, dist/2)[0][:2]

        # Now for the good/bad selection. We compute the distance from this mid-point to
        # all station nodes ...
        mid_dists = [geo.inverse(mid_pt, pt)[0][0] for pt in pts]
        # ... then find what is the smallest distance of all ...
        min_mid_dist = min(mid_dists)
        # ... so that we can find the indices of the stations nodes that are the closest to
        # this mid point.
        min_dist_ids = [i for i, d in enumerate(mid_dists) if d == min_mid_dist]

        # For a good vertice, this mid point will be closest from one of its starting node.
        # If it is not the case, we have a found a "bad" vertex.
        if not all([item in vert for item in min_dist_ids]):
            # Keep a dictionnary where the vertex nodes are the key, and the vertex distance the
            # value.
            not_neighbors[vert] = dist
            continue

        # ... ok, seems, like we have a "good" vertex. Let's store it for later.
        neighbors[vert] = dist

    # The good/bad criteria above works well to cull the *outer* vertices of the default
    # Delaunay triangulation that one would not typically associate with "neighbor" sites.
    # However, it can at times also cull *inner* vertices that some users
    # may possibly want to keep. To circumvent this, we build a polygon from the good neighbor
    # vertices, and keep track of the *bad* ones that are covered by it ... and are therefore "not
    # that bad".

    # First, we assemble the good polygons.
    good_segs = [LineString(pts[vert, :]) for vert in neighbors]
    good_polys = polygonize(good_segs)

    # Now check which bad line segments are contained within the geometry
    not_so_bad_neighbors: dict = {}
    for (vert, dist) in not_neighbors.items():
        if good_polys.covers(LineString(pts[vert, :])):
            # This bad vertex does not look so bad after all ... !
            not_so_bad_neighbors[vert] = dist

    # Let's adjust the list of not_neighbors, to avoid duplicates
    not_neighbors = {key: item for key, item in not_neighbors.items()
                     if key not in not_so_bad_neighbors}

    return neighbors, not_neighbors, not_so_bad_neighbors


@log_func_call(logger)
def get_delaunay_vertices(lons: np.ndarray, lats: np.ndarray, **kwargs: str) -> set:
    """ Run a Delaunay triangulation on a series of coordinates, and assemble the list of
    resulting vertices.

    Args:
        lons (np.ndarray): array of longitudes, in fractional degrees.
        lats (np.ndarray): array of latitudes, in fractional degrees.
        **kwargs: any other keyword arguments will be fed to cartopy.crs.Stereographic()

    Return:
        list: the list of individual vertices, provided as len(2)-lists of (original) point indices.


    This routine performs a Delaunay triangulation using the point coordinates converted to a
    Stereographic projection. This allows to run a 2D (instead of 3D) Delaunay triangulation where
    the identified pairs of *neighbor* stations are the same as those that would be ientified if
    the triangulation was performed on the surface of the sphere.

    See Saalfeld, Cartography and Geographic Information Science, Vol. 26, No.4, 1999, pp. 289-296.

    https://www.tandfonline.com/doi/pdf/10.1559/152304099782294168

    """

    assert len(lats) == len(lons), "Length mismatch for lons and lats"

    # First things first: transform the lon-lat "PlateCarree" coordinates
    # onto a Stereographic projection.
    stereo = ccrs.Stereographic(**kwargs)
    stereo_pts = stereo.transform_points(ccrs.PlateCarree(), lons, lats)

    # Run the Delauney triangulation on these coordinates
    tri = Delaunay(stereo_pts[:, :2])

    # Assemble the list of vertices derived from Delaunay
    # All credits go to https://stackoverflow.com/questions/64530316 for this great line
    verts = set([tuple(sorted(edge)) for item in tri.simplices for edge in combinations(item, 2)])

    return verts


@log_func_call(logger)
def compute_mean_sep(verts: dict) -> tuple[float, float]:
    """ Compute the mean and median vertex length given a set of vertices.

    Args:
        verts (dict): dictionnary of vertices, where each key contains a single vertex nodes, and
            the entries are their respective lengths (computed elsewhere).

    Returns:
        tuple[float, float]: the mean and median vertex lengths.

    """

    # Assemble a list of separations
    seps = [item for _, item in verts.items()]

    return np.mean(seps), np.median(seps)
