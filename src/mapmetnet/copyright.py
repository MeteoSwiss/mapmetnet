"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: relevant copyright notices
"""

# Import from Python
import logging
from textwrap import fill
from cartopy import __version__ as cartopy_version

# Import from this module
from . import __version__
from .logger import log_func_call

# Instantiate the module logger
logger = logging.getLogger(__name__)


@log_func_call(logger)
def get_mmn_msg(when: str | None = None) -> str:
    """ Get the copyright statement for mapmetnet.

    Args:
        when: The date when the map was created, in a human-readable format. Optional.

    """

    if when is not None:
        msg = f' on {when}.'
    else:
        msg = '.'

    return f'Created with mapmetnet v{__version__}' + msg


@log_func_call(logger)
def get_cartopy_msg(projection: str | None = None) -> str:
    """ Get the copyright statement for cartopy.

    Args:
        projection: The name of the cartopy projection used to generate the map.

    """

    if projection is None:
        start = 'P'
    else:
        start = f'{projection} p'

    return start + f'rojection via cartopy v{cartopy_version}, Met Office.'


@log_func_call
def get_ne_msg(features: list) -> str:
    """ Get the copyright statement for Natural Earth. """

    if len(features) == 0:
        return ''

    # Join the list of strings into a single one, separated by comma
    msg = ', '.join(features)

    # Capitalize the first letter of the message
    msg = msg[0].upper() + msg[1:]
    return f'{msg} from Natural Earth.'


@log_func_call(logger)
def get_gibs_msg(feature: str) -> str:
    """ Get the copyright statement for NASA GIBS. """

    msg = f"{feature}, from NASA's Global Imagery Browse Services (GIBS), " + \
        "part of NASA's Earth Observing System Data and Information System (EOSDIS)."
    return msg


@log_func_call(logger)
def get_eez_msg() -> str:
    """ Get the copyright statement for EEZ. """

    msg = "EEZ maritime boundaries from Flanders Marine Institute (2023), " + \
        "Maritime Boundaries Geodatabase: " + \
        "Maritime Boundaries and Exclusive Economic Zones (200NM), version 12."  # + \
    # "available online at https://www.marineregions.org/ (https://doi.org/10.14284/632)."
    return msg


@log_func_call(logger)
def get_mch_msg() -> str:
    """ Get the disclaimer statement for MeteoSwiss. """

    msg = "Disclaimer: the designations employed in this map do not imply the expression of " + \
        "any opinion whatsoever on the part of MeteoSwiss concerning the legal status of any " + \
        "country, area, or territory or of its authorities, or concerning the delimitation of " + \
        "its borders. The depiction and use of boundaries, geographic names and related data " + \
        "are not warranted to be error free nor do they necessarily imply official endorsement " + \
        "by MeteoSwiss."
    return msg


@log_func_call(logger)
def build_copyright_statement(which: dict, width: int | None = 160) -> str:
    """ Build a copyright statement for the map, based on the different elements that are
    included in it.

    Args:
        which (dict): a dictionary with the different elements to include in the copyright
            statement. The keys of the dict should be the same as the names of the functions
            defined above, and the values should be the arguments to feed to those functions.
        width (int, optional): the width to use for wrapping the text. Defaults to 160. If None,
            no wrapping will be applied.

    """

    # Initialize an empty list to store the different parts of the copyright statement
    parts = []

    # Iterate over the possible dictionnary keys, and generate the relevant copyright if warranted.
    # Doing so allows to maintain a set order of sentences.

    for key in ['mmn', 'cartopy', 'ne', 'gibs', 'eez', 'mch']:
        if key in which:
            func = eval(f'get_{key}_msg')
            if which[key] is not None:
                part = func(which[key])
            else:
                part = func()
            parts.append(part)

    if width is None:
        return ' '.join(parts)

    # Join the parts and wrap them into a paragraph suitable for plotting
    return fill(' '.join(parts), width=width)
