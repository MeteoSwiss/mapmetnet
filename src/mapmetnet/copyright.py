"""
Copyright (c) 2023-2024 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: relevant copyright notices
"""

# Import from Python
from textwrap import fill
from cartopy import __version__ as cartopy_version

# Import from this module
from . import __version__


def get_mmn_msg() -> str:
    """ Get the copyright statement for mapmetnet. """

    return f'Created with mapmetnet v{__version__}.'


def get_cartopy_msg(projection: str) -> str:
    """ Get the copyright statement for cartopy.

    Args:
        projection: The name of the cartopy projection used to generate the map.

    """

    return f'{projection} projection generated using cartopy v{cartopy_version}, Met Office.'


def get_ne_msg(features: list) -> str:
    """ Get the copyright statement for Natural Earth. """

    if len(features) == 0:
        return ''

    # Join the list of strings into a single one, separated by comma
    msg = ', '.join(features)

    # Capitalize the first letter of the message
    msg = msg[0].upper() + msg[1:]
    return f'{msg} from Natural Earth.'


def get_gibs_msg(feature: str) -> str:
    """ Get the copyright statement for NASA GIBS. """

    msg = f"{feature}, from NASA's Global Imagery Browse Services (GIBS), " + \
        "part of NASA's Earth Observing System Data and Information System (EOSDIS)."
    return msg


def get_eez_msg() -> str:
    """ Get the copyright statement for EEZ. """

    msg = "EEZ maritime boundaries from Flanders Marine Institute (2023), " + \
        "Maritime Boundaries Geodatabase: " + \
        "Maritime Boundaries and Exclusive Economic Zones (200NM), version 12."  # + \
    # "available online at https://www.marineregions.org/ (https://doi.org/10.14284/632)."
    return msg


def get_mch_msg() -> str:
    """ Get the disclaimer statement for MeteoSwiss. """

    msg = "Disclaimer: the designations employed in this map do not imply the expression of " + \
        "any opinion whatsoever on the part of MeteoSwiss concerning the legal status of any " + \
        "country, area, or territory or of its authorities, or concerning the delimitation of " + \
        "its borders. The depiction and use of boundaries, geographic names and related data " + \
        "are not warranted to be error free nor do they necessarily imply official endorsement " + \
        "by MeteoSwiss."
    return msg


def build_copyright_statement(which: dict) -> str:
    """ Build a copyright statement for the map, based on the different elements that are
    included in it.

    Args:
        which (dict): a dictionary with the different elements to include in the copyright
            statement. The keys of the dict should be the same as the names of the functions
            defined above, and the values should be the arguments to feed to those functions.

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

    # Join the parts and wrap them into a paragraph suitable for plotting
    return fill(' '.join(parts), width=160)
