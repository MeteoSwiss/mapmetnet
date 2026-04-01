"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: general utility functions
"""

# Import from Python
from typing import Union, Callable
from functools import wraps
import logging
from pathlib import Path

import yaml
import numpy as np
from numpy import ndarray
from astropy.coordinates import angular_separation
import matplotlib.pyplot as plt
import shapely
from shapely import geometry as sgeom
from cartopy import geodesic


# Import from soffmapper
from .logger import log_func_call

# Instantiate the module logger
logger = logging.getLogger(__name__)


@log_func_call(logger)
def pad_angular_range(ang_range: Union[list, tuple, ndarray], pad_fraction: float):
    """ Pad a given angular range by a fraction of the range (on both sides).

    Args:
        ang_range (list, tuple, ndarray): len(2) list/tuple/ndarray with lower and higher angular
             bounds.
        pad_fraction (float): padding fraction. Setting pad_fraction to 0 returns the same range.

    Return: list or tuple or ndarray, padded by the requested amount.

    """
    start_type = type(ang_range)
    ang_range = np.array(ang_range)
    # WARNING: doing a += here leads to problems in case of integer arrays
    ang_range = ang_range + np.array([-1., 1.]) * np.diff(ang_range) * pad_fraction
    if start_type == list:
        return ang_range.tolist()
    if start_type == tuple:
        return tuple(ang_range)
    if start_type == ndarray:
        return ang_range

    raise TypeError('ang_range is of unknown type: {start_type}')


@log_func_call(logger)
def squarify_extent(lon_lims: ndarray, lat_lims: ndarray):
    """ Adjust longitude and latitude limits to get a squar-ish map extent.

    Args:
        lon_lims (tuple): min/max longitudes
        lat_lims (tuple): min/max latitudes

    Return: tuple of (lon_lims, lat_lims) with the narrowest direction suitably expanded.

    """

    # First, compute the lat-lon angular ratio ...
    lon_mean = np.mean(lon_lims)
    lat_mean = np.mean(lat_lims)
    lon_sep = angular_separation(np.radians(lon_lims[0]), np.radians(lat_mean),
                                 np.radians(lon_lims[1]), np.radians(lat_mean))
    lat_sep = angular_separation(np.radians(lon_mean), np.radians(lat_lims[0]),
                                 np.radians(lon_mean), np.radians(lat_lims[1]))

    # ... and ue it to boost the narrowest direction to get a square-ish area plot
    # WARNING: doing a += below leads to problems in case of integer arrays
    if lat_sep > lon_sep:
        lon_lims = lon_lims + np.array([-1, 1]) * np.diff(lon_lims) * (lat_sep/lon_sep-1)/2
    elif lon_sep > lat_sep:
        lat_lims = lat_lims + np.array([-1, 1]) * np.diff(lat_lims) * (lon_sep/lat_sep-1)/2

    return lon_lims, lat_lims


@log_func_call(logger)
def is_overlapping(geom: sgeom, extent: tuple) -> bool:
    """ Utility function to check if a given geometry overlapps with a plot extent.

    Args:
        geom (shapely geometry): a geometry to check
        extent (tuple): the map extent, from ax.get_extent(crs=ccrs.PlateCarree())

    Returns: bool

    """

    map_area = sgeom.Polygon([[extent[0], extent[2]],
                              [extent[0], extent[3]],
                              [extent[1], extent[3]],
                              [extent[1], extent[2]],
                              [extent[0], extent[2]]])

    return geom.convex_hull.intersects(map_area)


@log_func_call(logger)
def get_circle_geom(lon: float, lat: float, radius: float):
    """ Given a lat-lon positon and radius, build a circle geometry.

    Args:
        lon (float): center longitude
        lat (float): center latitude
        radius (float): radius in km

    Returns: shapely.geometry

    """

    circle = geodesic.Geodesic().circle(lon=lon, lat=lat, radius=radius * 1000,
                                        n_samples=100, endpoint=False)
    return sgeom.Polygon(circle)


@log_func_call(logger)
def get_overlap_geom(geoms: list) -> sgeom:
    """ Given a list of geometries, assemble the region where two (or more) overlap. It does not
    need to be a contiguous region.

    Args:
        geoms (list): list of shapely geometries to process.


    Returns:
        sgeom: the shapely geometry of the overlaps

    """

    # Create some empty geometries to start with
    union = sgeom.Polygon([])
    overlap = sgeom.Polygon([])

    # Next, loop through each geometry, compute the overlap, and keep track of it
    for geom in geoms:
        overlap = shapely.union(overlap, shapely.intersection(union, geom))
        union = shapely.union(union, geom)

    return overlap


def set_mplstyle(func: Callable) -> Callable:
    """ Intended to be used as a decorator around plotting functions, to set the plotting style.

    Returns:
        Callable: the decorator.

    Adapted from the ampycloud source code: https://github.com/MeteoSwiss/ampycloud

    This is a simpler version of the Decorator that only loads the basic matplotlib style
    specified in mpl_styles/base.mplstyle.

    """

    @wraps(func)  # This black magic is required for Sphinx to still pickup the func docstrings.
    def inner_deco(*args, **kwargs) -> Callable:
        """ The core function, where the magic happens. """

        # Where are all the plotting parameter files ?
        pth = Path(__file__).parent / 'mpl_styles'

        # First, always extract the 'base' soffmapper plotting parameters
        with open(pth / 'base.mplstyle', encoding='utf-8') as fil:
            logger.debug("Loading the 'base' plotting style")
            prms = yaml.safe_load(fil)

        # Finally, apply the base plotting style
        with plt.style.context(prms):
            out = func(*args, **kwargs)
            return out

    return inner_deco
