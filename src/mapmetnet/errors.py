"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: custom error and warning classes
"""


class MapmetnetError(Exception):
    """ The default error class for mapmetnet, which is a child of the :py:exc:`Exception` class.
    """


class MapmetnetWarning(Warning):
    """ The default warning class for mapmetnet, which is a child of the :py:class:`Warning` class.
    """
