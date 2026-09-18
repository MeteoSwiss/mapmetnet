
Site sat-views
==============

The ``mapmetnet.site`` module is designed to generate so-called "sat-view" diagrams for
a given site, either from its latitude and longitude, or directly using a
`WIGOS ID <https://community.wmo.int/wigos-station-identifiers>`_. The diagrams include (as an
option) a series of reference circles related to the standard WMO site classification scheme for
temperature measurements (see `WMO-No.8, Vol. I, Chap. 1, Annex 1.D`_ for details).

.. plot::
    :include-source:

    # Option 1: using a WIGOS ID
    from mapmetnet.site import WigosSite
    mysite = WigosSite('0-20000-0-06610')

    # Option 2: using latitude and longitude
    #from mapmetnet.site import Site
    #mysite = Site(lat=+46.811578, lon=+6.942472, name='My secret site')

    # Either way, trigger the diagram using:
    mysite.site_view(show_ref_circles=True, save_fn=None, show=True)




.. _WMO-No.8, Vol. I, Chap. 1, Annex 1.D: https://library.wmo.int/idurl/4/68695