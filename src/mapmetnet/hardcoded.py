"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: hardcoded elements
"""

# Import from Python
from pathlib import Path

#: float: Width of a 1-column plot [inches], to fit in scientific articles when scaled by 50%
WIDTH_ONECOL: float = 6.92

#: float: Width of a 2-column plot [inches], to fit in scientific articles when scaled by 50%
WIDTH_TWOCOL: float = 14.16

#: Path: (relative) path to usr backgrounds
USR_BKG_PATH = Path(__file__).parent / 'data' / 'backgrounds'

#: Path: (relative) path to EEZ shapefile
EEZ_PATH = Path(__file__).parent / 'data' / 'eez'

#: str: EEZ shapefile name
EEZ_FN = 'eez_boundaries_v12.shp'

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
