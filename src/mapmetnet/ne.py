"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: utility functions related to Natural Earth material
"""

# Import from Python
import logging
import cartopy.io.shapereader as shpreader

# Import from this package
from .logger import log_func_call
from .errors import MapmetnetError

# Instantiate the module logger
logger = logging.getLogger(__name__)


@log_func_call(logger)
def get_ne_records(resolution: str = '10m',
                   category: str = 'cultural',
                   name: str = 'admin_0_map_units',
                   fmt='iterator'):
    """ Wrapper routine to extract Natural Earth shapefile Records.

    For a list of available options, see: https://www.naturalearthdata.com/features/

    Args:
        resolution (str): defaults to '10m'.
        category (str): either 'cultural' or 'physical'
        name (str): the dataset name. Defaults to 'admin_0_map_units'
        fmt (str): output format, either 'iterator' (by default) or 'list'.

    """

    # Get the name of the files where those things get downloaded
    shpfilename = shpreader.natural_earth(resolution=resolution, category=category,
                                          name=name)
    # Read the file content
    # Using BasicReader for now, as FionaReader fail to extract accents properly.
    reader = shpreader.BasicReader(shpfilename)
    # Extract the individual entities
    entities = reader.records()

    # Turn the iterator into a list if needed
    if fmt == 'list':
        return list(entities)

    return entities


@log_func_call(logger)
def get_ne_country(country_code: str, resolution: str = '10m', is_map_unit: bool = True):
    """ Small utility function to extract a target country record from Natural Earth.

    Args:
        country_code (str): ISO 3166-1 alpha-3 country code.
            https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
        resolution (str, optional): the resolution of the data. Defaults to '10m'.
        is_map_unit (bool, optional): if True, will search the map_unit dataset. Else the country
            dataset. Defaults to True.

    Returns: country record

    """

    if is_map_unit:
        src = 'admin_0_map_units'
    else:
        src = 'admin_0_country'

    for country in get_ne_records(resolution=resolution, category='cultural',
                                  name=src):
        if country.attributes['ISO_A3'] == country_code:
            return country

    raise MapmetnetError(f'Country code "{country_code}" not found in {src}.')
