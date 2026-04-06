.. image:: https://img.shields.io/pypi/v/mapmetnet.svg
    :target: https://pypi.org/project/mapmetnet/

.. image:: https://img.shields.io/pypi/pyversions/mapmetnet.svg
    :target: https://pypi.org/project/mapmetnet/

.. image:: https://img.shields.io/pypi/l/mapmetnet.svg
    :target: https://pypi.org/project/mapmetnet/

.. image:: https://github.com/MeteoSwiss/mapmetnet/actions/workflows/github-code-scanning/codeql/badge.svg
    :target: https://github.com/MeteoSwiss/mapmetnet/actions/workflows/github-code-scanning/codeql

.. image:: https://github.com/MeteoSwiss/mapmetnet/actions/workflows/CI_test.yaml/badge.svg
    :target: https://github.com/MeteoSwiss/mapmetnet/actions/workflows/CI_test.yaml

.. image:: https://github.com/MeteoSwiss/mapmetnet/actions/workflows/CI_publish_dev_documentation.yaml/badge.svg
    :target: https://github.com/MeteoSwiss/mapmetnet/actions/workflows/CI_publish_dev_documentation.yaml

===============
Getting Started
===============

This package is under active development. You can expect regular breaking changes, poor
documentation, and rapidly evolving APIs. If you want to use the package, please reach out to the
developers and we will be happy to help you get started.

For the daring users out there, here is a quick exemple to get you started with network maps:

.. literalinclude:: ./exemple.py

Alternatively, if you want to create a site diagnostic plot, you can do it like this:

.. code-block:: python

    from mapmetnet.site import WigosSite

    mysite = WigosSite('0-20000-0-06610')
    # Alternarively, if you the site does not have a WIGOS ID:
    # mysite = Site(lat=+46.811578, lon=+6.942472, name='My secret site')
    mysite.site_view(save_fn='tmp.pdf', show=False)


Development Setup with Poetry
-----------------------------

Building the Project
''''''''''''''''''''
.. code-block:: console

    $ cd mapmetnet
    $ poetry install

Run Tests
'''''''''

.. code-block:: console

    $ poetry run pytest

Run Quality Tools
'''''''''''''''''

.. code-block:: console

    $ poetry run pylint mapmetnet
    $ poetry run mypy mapmetnet

Generate Documentation
''''''''''''''''''''''

.. code-block:: console

    $ poetry run sphinx-build doc doc/_build

Then open the index.html file generated in *mapmetnet/doc/_build/*.

Build wheels
''''''''''''

.. code-block:: console

    $ poetry build

Using the Library
-----------------

To install mapmetnet in your project, run this command in your terminal:

.. code-block:: console

    $ poetry add mapmetnet

You can then use the library in your project through

    import mapmetnet

Release the Project
-------------------

The project follows the **GitOps concept**: releases are triggered whenever a Git TAG is created.

The TAG must follow the `semantic version <https://semver.org/>`__ format and `PEP 440 <https://peps.python.org/pep-0440/>`__ , otherwise the release task will fail.

Follow these steps to create a new release:

* Adapt CHANGELOG.rst with release information
* Adapt ``doc/_static/switcher_config.json`` adding the new documentation URL for the release
* Create a new Release in the Github project
