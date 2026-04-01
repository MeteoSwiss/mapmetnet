"""
Copyright (c) 2023-2024 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: relevant copyright notices
"""

from cartopy import __version__ as cartopy_version

# Import from this module
from . import __version__


#: str: Copyright statement for mapmetnet
COPY_MAPMETNET = f'Created with mapmetnet v{__version__} (https://github.com/MeteoSwiss/mapmetnet).'

#: str: Copyright statement for cartopy
# TODO: we should tie the name of the projection to the actual code ...
COPY_CARTOPY = 'Orthographic projection generated using cartopy v' + cartopy_version + \
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