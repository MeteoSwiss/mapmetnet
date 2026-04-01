"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: utility functions related to EEZ maritime boundaries
"""

# Import from Python
import logging
import cartopy.io.shapereader as shpreader

# Import from this package
from .logger import log_func_call
from .hardcoded import EEZ_FN, EEZ_PATH

# Instantiate the module logger
logger = logging.getLogger(__name__)


@log_func_call(logger)
def get_eez_records():
    """ Wrapper routine to extract EEZ records.

    Return: iterator of Record, extracted from as shapefile.

    TODO:
        It is not allowed to share the EEZ file together with the code. A mechanism is required
        to allow user to set this up correctly.

    """

    # Load EEZ limits
    reader = shpreader.BasicReader(EEZ_PATH / EEZ_FN)

    return reader.records()


@log_func_call(logger)
def get_eez(mrgid: int) -> list:
    """ Small utility function to extract a target EEZ geometries.

    Args:
        mrgid (int): Marine Regions Geographic IDentifier of the target.

    Returns: list of eez records.

    """

    # If get a None, return an empty list
    if mrgid is None:
        return []

    matching_eezs = []
    # Loop through the EEZ, to find the relevant ones.
    for eez in get_eez_records():
        if mrgid in [eez.attributes['MRGID_SOV1'],
                     eez.attributes['MRGID_SOV2'],
                     eez.attributes['MRGID_SOV3']]:
            matching_eezs += [eez]

    return matching_eezs
