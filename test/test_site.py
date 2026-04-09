"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module content: tests for the site module
"""

from mapmetnet.site import WigosSite


# Simple all-in-one test to create the diagram for a given Wigos site
def test_wigos_site():
    """ Test the WigosSite class. """

    # Create a WigosSite object for the station of Payerne, Switzerland
    site = WigosSite('0-20000-0-06610')
    site.site_view()
    assert True
