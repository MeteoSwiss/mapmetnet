Network maps
============

GBON network maps
-----------------

The primary goal of the ``mapmetnet.mapper`` module is to assemble fully-fledged GBON compliance network
maps, as illustrated in the following example:

.. plot::
    :include-source:

    from mapmetnet.mapper import GBONMapper

    che_map = GBONMapper('CHE', mrgid=None)
    che_map.generate_map(figid=1,
                         pad_frac=0.025,
                         station_type='surface',
                         var_name='temperature',
                         interval='daily',
                         category='availability',
                         date='2026-04-13',
                         high_density=True,
                         show_influence_area=False,
                         show=True)


For more information on the different parameters of the resulting map, users can refer to the
documentation of the :py:func:`mapmetnet.mapper.GBONMapper.generate_map` method.

.. autofunction:: mapmetnet.mapper.GBONMapper.generate_map
   :noindex:


Customizing network maps
------------------------

The :py:func:`mapmetnet.mapper.GBONMapper.generate_map` provides a high-level entry point, with a
limited set of parameters to minimze complexity. In itself, this routine is little more than a
wrapper around a set of lower-level functions to build and customize a map step-by-step.

Users with specific needs (and feeling adventurous) may thus be interested to build their own custom
map by replicating, adjusting and expanding the different steps implemented in
:py:func:`mapmetnet.mapper.GBONMapper.generate_map`. For specific exemples, see the :ref:`exemple1`
and :ref:`exemple2`.

We shall not describe here the different steps/options in details, but instead refer interested
users to the relevant function docstrings instead. We shall merely note that these different steps
are located in distinct hierarchical classes, as illustrated below.

.. inheritance-diagram:: mapmetnet.mapper.GBONMapper
    :caption: Fig. 1: Inheritance diagram for the GBONMapper class
    :top-classes: mapmetnet.mapper.NetworkMapper


.. _exemple1:

Custom example 1: international network
.......................................

.. plot::
    :include-source:

    import polars as pl
    from mapmetnet.mapper import NetworkMapper

    # Create a list of station coordinates as a polars DataFrame
    stations = pl.DataFrame({
        'longitude': [6.943021, 0.943021, 12.943021, 6.943021, 6.943021],
        'latitude': [46.812724, 46.812724, 46.812724, 44.812724, 51.812724]
    })

    # Setup the map ... for this use case we need nothing more than the NetworkMapper class
    mymap = NetworkMapper(lat=46.80111, lon=8.22667, extent=20)
    mymap.create_fig(figid=1)
    mymap.set_map_lims(squarify=True)

    # Further tweak the look of things
    mymap.add_background(which=None)
    mymap.add_borders()
    mymap.add_gridlines()

    # Add the stations
    comb, inter = mymap.add_stations(stations, influence_radius=None,
                                     marker='D', edgecolor='w', facecolor='k',
                                     size=100, label='Some special stations')

    # Connect the stations
    _ = mymap.link_neighbors(stations, color='k', thres=None)

    # Finish up ...
    mymap.add_copyright()
    mymap.add_legend()
    mymap.savefig('custom_network_map1.png')
    mymap.show()


.. _exemple2:

Custom example 2: non-GBON stations
...................................

.. plot::
    :include-source:

    import polars as pl
    import matplotlib.lines as mlines
    from mapmetnet.mapper import CountryMapper

    # Create a list of station coordinates as a polars DataFrame
    stations = pl.DataFrame({
        'longitude': [6.943021, 7.415201, 8.62053],
        'latitude': [46.812724, 47.178870, 47.690021]
    })

    # Setup the map
    mymap = CountryMapper('CHE')
    mymap.create_fig(figid=1)

    # Make it asymetric to better fit the country shape
    mymap.set_map_lims(pad_frac=0.02, lat_max=47.8, lat_min=45.65, squarify=False)

    # Further tweak the look of things
    mymap.add_background(which=None)
    mymap.highlight_country()
    mymap.add_borders()
    mymap.add_gridlines()

    # Add the stations
    comb, inter = mymap.add_stations(stations, influence_radius=None,
                                     marker='D', edgecolor='w', facecolor='k',
                                     size=100, label='Some special stations')

    # Link stations and compute the mean separation ...
    mean_sep = mymap.link_neighbors(stations, color='k', thres=100)
    # ... and add this info to the legend
    mymap._legend_handles['mean_sep'] = mlines.Line2D(
        [], [], color='none', ls='-', label=f'Mean sep.: {mean_sep:.1f} km')

    # Finish up ...
    mymap.add_copyright()
    mymap.add_legend()
    mymap.savefig('custom_network_map2.png')
    mymap.show()


Advanced options (for adventurous users)
----------------------------------------

Exclusive Economic Zones (EEZ)
..............................

It is possible to draw the Exclusive Economic Zones (EEZ) of target countries on the map, by
specifying the relevant Marine Regions Geographic IDengifier (MRGID) number when instantianting
either the :py:class:`mapmetnet.mapper.GBONMapper` or :py:class:`mapmetnet.mapper.CountryMapper`
classes:

.. code-block:: python

    from mapmetnet.mapper import GBONMapper

    alb_map = GBONMapper('ALB', mrgid=2153)
    alb_map.generate_map(...)

The MRGID number for a given country can be found on the `Marine Regions website`_. For exemple,
Albania has the MRGID number `2153`_.

Doing so requires, in turn, to install the relevant EEZ shapefiles locally, which cannot be shipped
with the code for `legal reasons`_. To identify the correct install location, use the ``mapmetnet``
entry point from a terminal:

.. code-block:: bash

    $ mapmetnet

    mapmetnet X.Y

    Reference locations for supplementary material:

    * Natural Earth: /Some/where/locally/src/mapmetnet/data/backgrounds

    * EEZ shapefile: /Some/where/locally/src/mapmetnet/data/eez

    For more info: https://MeteoSwiss.github.io/mapmetnet


Detailed install instructions can then be found under the ``README.md`` file located at the
designated EEZ location.

.. _Marine Regions website: https://www.marineregions.org/mrgid.php
.. _2153: http://marineregions.org/mrgid/2153
.. _legal reasons: https://marineregions.org/disclaimer.php

Natural Earth background
........................

``mapmetnet`` can use the `Natural Earth`_ I with Shaded Relief, Water, and Drainages
high-resolution map as background via the ``background='ne'`` parameter in the
:py:class:`mapmetnet.mapper.GBONMapper.generate_map` call. Doing so requires, in turn,
to place the relevant Natural Earth data locally (its large size prevents us from shipping it
with the code).

Here as well, use the ``mapmetnet`` high-level entry point to identify the correct install location and associated
``README.md``.

.. _Natural Earth: https://www.naturalearthdata.com/downloads/10m-natural-earth-1/10m-natural-earth-1-with-shaded-relief-water-and-drainages/
