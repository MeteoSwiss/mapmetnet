"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: highest-level init magic
"""

# Import from Python
import os
import logging
from importlib.metadata import version as getversion

# Import from this module
from .hardcoded import USR_BKG_PATH

# Extract the version from the system, because it is set (upon release) by the CI/CD pipeline
# via the pyproject.toml file (using poetry).
__version__ = getversion("mapmetnet")

# Make sure users can do things like import mapmetnet -> mapmetnet.site.etc ...
# Side note: this also fixes a warning with Sphinx related to duplicated loggers ...
__all__ = ['site', 'mapper']

# Instantiate the module logger
logger = logging.getLogger(__name__)
# Hide any log messages if the user did not instantiate any handler
# For details, see: https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logger.addHandler(logging.NullHandler())

# Set the proper environment for cartopy, so that the custom background images can be found.
# TODO: this is not great, because we might force the users to reset something they care about.
os.environ['CARTOPY_USER_BACKGROUNDS'] = str(USR_BKG_PATH.absolute())
