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