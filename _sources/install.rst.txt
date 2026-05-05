Installation
============

``mapmetnet`` is **not yet** available on `PyPI`_, and can **not** be installed using ``pip``:

.. code-block:: bash

   pip install mapmetnet

If you are so inclined, you can also install ``mapmetnet`` from source, via a local clone of
the relevant `Github`_ repository:

.. code-block:: bash

   git clone https://github.com/MeteoSwiss/mapmetnet.git
   cd mapmetnet
   pip install -e .

Please refer to the code `contributing guidelines`_ for more details, inclduing on how to set
up a suitable development environment for ``mapmetnet`` (should you be interested to contribute).

.. _PyPI: https://pypi.org/project/mapmetnet/
.. _Github: https://github.com/MeteoSwiss/mapmetnet
.. _contributing guidelines: https://github.com/MeteoSwiss/mapmetnet/blob/main/CONTRIBUTING.rst


Logging
=======

``mapmetnet`` comes with a built-in logging setup relying on a `NullHandler`_ to avoid bothering
users with unwanted messages. Should you wish to see/record the log messages (e.g. for debugging
purposes), you can do so by setting up your own handler, e.g. via:

.. code-block:: python

      import logging

      logging.basicConfig(level=logging.INFO)
      logging.getLogger('mapmetnet').setLevel(logging.DEBUG)

      # ... your code using mapmetnet here ...


.. _NullHandler: https://docs.python.org/3/library/logging.handlers.html#logging.NullHandler