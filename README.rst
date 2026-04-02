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
developers (see contact information below) and we will be happy to help you get started.

For the daring users out there, here is a quick exemple to get you started:

.. code-block:: python

    import polars as pl
    from mapmetnet.core import NetworkMapper

    # Create a list of basic coordinates as polars DataFrame
    # Pro tip - you can use wmoutils.query.query_oscar_surface() to get real station coordinates
    sites = pl.DataFrame({
        'longitude': [3, 4, 5, 3],
        'latitude': [45, 46, 47, 48]
        })

    mymap = CountryMapper('CHE')
    mymap._create_fig(figid=1)
    mymap._set_map_extent(extent=7)
    mymap._center_map(pad_frac=0.25)
    mymap._add_background(which='ne')
    mymap._add_rivers_and_lakes()
    mymap._add_borders()
    mymap._add_coast()
    mymap._add_gridlines()
    comb1, inter1 = mymap._add_stations(sites, influence_radius=75, label='My sites')
    mean_sep1 = mymap._link_neighbors(sites, color='k', thres=150)
    mymap._add_geom_union_outline([comb1], label='Union')
    mymap._add_copyright()
    mymap._add_legend()
    mymap.show()


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
