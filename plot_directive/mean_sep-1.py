import numpy as np
import matplotlib.pyplot as plt
from mapmetnet import network

# Setup a demo set of coordinates
pts = np.array([[0, 0], [0.25, 1], [0.5, -0.5], [0.5, 0.5], [1, 0], [1.5, -0.5],
                [1.5, 0.75], [2, 0], [3, 0], [3, 2]])

# Identify the nearest neighbors
neighbors, not_neighbors, not_so_bad_neighbors = network.get_neighbors(pts[:, 0], pts[:, 1])

# Plot them
plt.close(1)
plt.figure(1)
for vert, _ in neighbors.items():
    plt.plot(pts[vert, 0], pts[vert, 1], color='k', ls='-', lw=1)
for vert, _ in not_so_bad_neighbors.items():
    plt.plot(pts[vert, 0], pts[vert, 1], color='orange', ls='--', lw=1)
for vert, _ in not_neighbors.items():
    plt.plot(pts[vert, 0], pts[vert, 1], color='red', ls=':', lw=1)

plt.scatter(pts[:, 0], pts[:, 1], color='k', facecolor='k',
            edgecolor='k', marker='o', zorder=10)

# Add manual legend handles
handles = [plt.Line2D([0], [0], color='k', marker='o', ls='', label='Node'),
           plt.Line2D([0], [0], color='k', ls='-', label='Good neighbors'),
           plt.Line2D([0], [0], color='orange', ls='--', label='Not-so-bad neighbors'),
           plt.Line2D([0], [0], color='red', ls=':', label='Bad neighbors')]
plt.legend(handles=handles)