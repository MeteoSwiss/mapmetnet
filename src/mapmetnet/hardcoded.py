"""
Copyright (c) 2023-2024 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: hardcoded elements
"""

# Import from Python
from pathlib import Path
from cartopy import __version__ as cartopy_version

# Import from this module
from .__init__ import __version__

#: float: Width of a 1-column plot [inches], to fit in scientific articles when scaled by 50%
WIDTH_ONECOL: float = 6.92

#: float: Width of a 2-column plot [inches], to fit in scientific articles when scaled by 50%
WIDTH_TWOCOL: float = 14.16

#: Path: (relative) path to usr backgrounds
USR_BKG_PATH = Path(__file__).parent / 'user_backgrounds'

#: Path: (relative) path to EEZ shapefile
EEZ_PATH = Path(__file__).parent / 'eez'

#: str: EEZ shapefile name
EEZ_FN = 'eez_boundaries_v12.shp'

#: str: Copyright statement for soffmapper
COPY_MAPMETNET = f'Created with mapmetnet v{__version__} (https://github.com/MeteoSwiss/mapmetnet).'

#: str: Copyright statement for cartopy
COPY_CARTOPY = 'Transverse Mercator projection generated using cartopy v' + cartopy_version + \
    ', Met Office (https://doi.org/10.5281/zenodo.1182735).'

#: str: Copyright Natural Earth
COPY_NE = "Natural Earth."

#: str: Copyright statement for GIBS products
COPY_GIBS = "NASA's Global Imagery Browse Services (GIBS),\n" + \
    "part of NASA's Earth Observing System Data and Information System (EOSDIS)."

#: str: Copyright statement for EEZ
COPY_EEZ = "EEZ maritime boundaries from Flanders Marine Institute (2023),\n" + \
    "Maritime Boundaries Geodatabase: " + \
    "Maritime Boundaries and Exclusive Economic Zones (200NM), version 12,\n" + \
    "available online at https://www.marineregions.org/ (https://doi.org/10.14284/632)."

#: str: Disclaimer statement for MeteoSwiss
DISC_MCH = "Disclaimer: the designations employed in this map do not imply the expression of " + \
    "any opinion whatsoever\non the part of MeteoSwiss concerning the legal status of any " + \
    "country, area, or territory or of its authorities,\nor concerning the delimitation of its " + \
    "borders. The depiction and use of boundaries, geographic names and related\ndata are not " + \
    "warranted to be error free nor do they necessarily imply official endorsement by MeteoSwiss."

#: dict: WDQMS color codes
WDQMS_COLORS = {
    'black': {'marker': 's', 'facecolor': 'k', 'edgecolor': 'w', 'hatch': 'xx',
              'size': 30, 'label': 'No data'},
    'red': {'marker': 'v', 'facecolor': 'firebrick', 'edgecolor': 'w', 'hatch': '//',
            'size': 40, 'label': 'Issues (<30%)'},
    'orange': {'marker': '^', 'facecolor': 'darkorange', 'edgecolor': 'w', 'hatch': '//',
               'size': 40, 'label': 'Issues (≥30%)'},
    'green': {'marker': 'o', 'facecolor': 'limegreen', 'edgecolor': 'w', 'hatch': 'oo',
              'size': 40, 'label': 'Compliant (≥80%)'}}
