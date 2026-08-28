"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: high-level entry points
"""

from .__init__ import __version__ as VERSION
from .hardcoded import USR_BKG_PATH, EEZ_PATH


def info():
    """
    High-level utility function to inform users on where to place supplementary material.
    """

    # High-level entry points could in principle benefit from argparse.
    # Here, we just want to print reference information, so let's not bother with it (for now).

    print(f'\nmapmetnet {VERSION}')
    print('\nReference locations for supplementary material:')
    print(f'\n* Natural Earth: {USR_BKG_PATH}')
    print(f'\n* EEZ shapefiles: {EEZ_PATH}')

    print('\nFor more info: https://MeteoSwiss.github.io/mapmetnet\n')
