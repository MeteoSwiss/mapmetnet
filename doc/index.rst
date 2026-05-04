mapmetnet
=========

Welcome to the documentation of ``mapmetnet``. This Python library has 3 primary intended uses:

1. the assembly of meteorological :doc:`network maps <mapper>`,
2. the computation of the :doc:`horizontal resolution <mean_sep>` (in the `GBON`_ sense) of a given network, and
3. the generation of :doc:`sat-view <site>` diagrams for individual observing sites.

Please refer to the relevant sections of the documentation below to learn more.

.. note::
   ``mapmetnet`` is being developed at MeteoSwiss on Github. If you encounter trouble while
   using ``mapmetnet``, please report the issue on the `GitHub repository`_. If you wish to
   contribute to the development of ``mapmetnet``, please refer to the `contributing guidelines`_.

.. _GBON: https://wmo.int/activities/global-basic-observing-network-gbon
.. _GitHub repository: https://github.com/MeteoSwiss/mapmetnet/issues
.. _contributing guidelines: https://github.com/MeteoSwiss/mapmetnet/blob/main/CONTRIBUTING.md


.. toctree::
   :maxdepth: 2
   :caption: Table of contents

   Start <self>
   install
   mapper
   mean_sep
   site
   changelog
