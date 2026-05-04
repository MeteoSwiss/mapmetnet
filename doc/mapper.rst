Network maps
============

GBON network maps
-----------------

The ``mapmetnet.mapper`` module primary goal is to assemble fully-fledged GBON compliance network
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
                         show=True)


For more information on the different parameters of the resulting map, users can refer to the
documentation of the :py:func:`mapmetnet.mapper.GBONMapper.generate_map` method.

.. autofunction:: mapmetnet.mapper.GBONMapper.generate_map
   :noindex:


Custom network maps
-------------------


.. inheritance-diagram:: mapmetnet.mapper.GBONMapper
    :caption: Fig. 1: Inheritance diagram for the GBONMapper class
    :top-classes: mapmetnet.mapper.NetworkMapper


Advanced options
----------------

Natural Earth background
........................

Exclusive Economic Zones (EEZ)
..............................