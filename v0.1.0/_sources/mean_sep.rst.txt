Horizontal resolution
=======================

tl;dr
-----

``mapmetnet`` allows to compute the **mean separation between neighboring stations** of a given
network (i.e. the *horizontal resolution* of the network, in the `GBON`_ sense), using
:py:func:`mapmetnet.network.get_mean_sep`:

.. code-block:: python

    import numpy as np
    from mapmetnet.network import get_mean_sep

    lats = np.array([0., 1., 2.])  # Station latitudes, in fractional degrees
    lons = np.array([0., 1., 2.])  # Station longitudes, in fractional degrees

    mean_sep, _, _ = get_mean_sep(lats, lons)

    print(f'Mean separation: {mean_sep:.2f} km')

.. _GBON: https://wmo.int/activities/global-basic-observing-network-gbon


Neighbors, where art thou ?
---------------------------

The challenge in computing the mean separation between stations/nodes in a given network lies in the
identification of a given node's *neighbors*. In ``mapmetnet``, the function
:py:func:`mapmetnet.network.get_mean_sep` relies on :py:func:`mapmetnet.network.get_neighbors` to do
so.

.. autofunction:: mapmetnet.network.get_neighbors
   :noindex:

The concept of **good neighbor**, **bad neighbor**, and **not-so-bad neighbor** nodes is illustrated in
the following diagram:

.. plot::

    import numpy as np
    from scipy.spatial import Voronoi, voronoi_plot_2d
    import matplotlib.pyplot as plt
    from mapmetnet import network

    # Setup a demo set of coordinates
    pts = np.array([[0, 0], [0.25, 1], [0.5, -0.5], [0.5, 0.5], [1, 0], [1.5, -0.4],
                    [1.5, 0.75], [2, 0], [3, 0], [3, 2]])

    # Compute the Voronoi diagram (for visualization purposes only)
    vor = Voronoi(pts)

    # Identify the nearest neighbors
    neighbors, not_neighbors, not_so_bad_neighbors = network.get_neighbors(pts[:, 0], pts[:, 1])

    # Plot it all

    # Start with the Voronoi cells
    fig = voronoi_plot_2d(vor, show_vertices=False, line_colors='gray',
                      line_width=0.5, point_size=2)

    # Add the neighbor vertices
    for vert, _ in neighbors.items():
        plt.plot(pts[vert, 0], pts[vert, 1], color='k', ls='-', lw=1)
    for vert, _ in not_so_bad_neighbors.items():
        plt.plot(pts[vert, 0], pts[vert, 1], color='orange', ls='--', lw=1)
    for vert, _ in not_neighbors.items():
        plt.plot(pts[vert, 0], pts[vert, 1], color='red', ls=':', lw=1)

    # Show the nodes, nice and clear
    plt.scatter(pts[:, 0], pts[:, 1], color='k', facecolor='k',
                edgecolor='k', marker='o', zorder=10)

    # Add manual legend handles
    handles = [plt.Line2D([0], [0], color='k', marker='o', ls='', label='Node'),
               plt.Line2D([0], [0], color='k', ls='-', label='Good neighbors'),
               plt.Line2D([0], [0], color='orange', ls='--', label='Not-so-bad neighbors'),
               plt.Line2D([0], [0], color='red', ls=':', label='Bad neighbors'),
               plt.Line2D([0], [0], color='gray', ls='-', lw=0.5, label='Voronoi cell edges')]
    plt.legend(handles=handles)


Working on the Sphere
---------------------

``mapmetnet`` was built to work with network of stations located on a sphere (i.e. the Earth), which
evidently does matter for the identifiation of neighbors. The necessary adjustments are
implemented in the function :py:func:`mapmetnet.network.get_delaunay_vertices`, which is
used within :py:func:`mapmetnet.network.get_neighbors` to run a Delaunay triangulation.

.. autofunction:: mapmetnet.network.get_delaunay_vertices
   :noindex: