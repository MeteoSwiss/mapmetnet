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


Advanced options
----------------

Natural Earth background
........................

Exclusive Economic Zones (EEZ)
..............................