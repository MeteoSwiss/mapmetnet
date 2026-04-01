"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module content: tests for the core module
"""

# Import from Python
import pytest

# Import from this package
from mapmetnet.core import CountryMapper


def test_CountryMapper_init():
    """ Basic __init__ tests for the CountryMapper base class. """

    # Default behavior
    out = CountryMapper('CHE')
    assert out.country_code == 'CHE'
    assert out.mrgid is None
    # TODO: the following test fail on Github, because I cannot include the EEZ dataset as part of
    # the package. WOuld be good to find a workaround - e.g. trigger a proper warning/error ?
    #out = CountryMapper('CHE', mrgid=37)
    #assert out.mrgid == 37

    # Suitable errors are raised when needed
    with pytest.raises(TypeError):
        CountryMapper(37)
    with pytest.raises(ValueError):
        CountryMapper('CH')
    with pytest.raises(TypeError):
        CountryMapper('CHE', mrgid='37')