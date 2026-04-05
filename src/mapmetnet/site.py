"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: classes related to individual sites
"""

# Import from Python
import copy
import logging
from datetime import datetime, UTC

from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from shapely.geometry import Polygon
from cartopy.geodesic import Geodesic
from cartopy.io.img_tiles import GoogleTiles, OSM
import cartopy.crs as ccrs
from astropy.coordinates import Angle
from astropy.units import deg as deg_unit
from wmoutils.query import query_oscar_surface

# Import from this package
from .logger import log_func_call
from .errors import MapmetnetError
from .hardcoded import WIDTH_TWOCOL
from .copyright import build_copyright_statement
from .utils import set_mplstyle, crosshair
from .core import Plotter

# Instantiate the module logger
logger = logging.getLogger(__name__)


class Site(Plotter):
    """ Parent Site class. """

    @log_func_call(logger)
    def __init__(self, lat: float, lon: float, name: str | None = None) -> None:
        """ Basic init routine.

            Args:
                lat (float): The latitude of the map center.
                lon (float): The longitude of the map center.
                name (str, optional): The name of the site. Defaults to None.

        """

        # Trigger the base class init
        super().__init__(when=datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S %Z"))

        # Set the central coordinates and the extent of the map
        self._lat = lat
        self._lon = lon

        # Create a basic Geodesic to compute distances down the line
        self._geo = Geodesic()

        # Let's also create the other atribute that will become relevant later on
        self._panels = None
        # self._copyright['cartopy'] = None
        self._name = name

    @set_mplstyle
    def _create_fig(self, figid: int | None = None,
                    panels: dict | None = None) -> None:
        """ Creation of plotting areas.

        Args:
            figid (int, optional): the matplotlib figure ID.
                Will first close it if it already exists.
            panels (dict, optional): len(4) dict with the half size of the panels in m as keys,
                and the tile zoom level as values. If None, defaults to
                {40: 20, 150: 18, 500: 17, 5000: 13}.

        """
        if panels is None:
            # Half size of panels, in m, and tiles zoom level
            panels = {40: 20, 150: 18, 500: 17, 5000: 13}

        # Check that the panel dict has a length of 4 and raise an Error otherwise
        if len(panels) != 4:
            raise MapmetnetError('The "panels" dict should have a length of 4.')

        # Store them for later use
        self._panels = panels

        # If a fig id was specified, let's close the plot
        if figid is not None:
            plt.close(figid)

        # Create the Figure and store it for later
        self._fig = plt.figure(figid, figsize=(WIDTH_TWOCOL, 15))

        # Create the axes
        gs = GridSpec(2, 2, width_ratios=[1]*2, height_ratios=[1]*2,
                      left=0.04, right=0.98, top=0.93, bottom=0.04, hspace=0.1, wspace=0.1)

        # Prepare the image tiles
        sat_imgs = [GoogleTiles(style='satellite')] * 3
        # street_img = GoogleTiles(style='street')
        street_img = OSM()
        imgs = sat_imgs + [street_img]

        # Create the axes
        axs = [plt.subplot(gs[0, i], projection=img.crs) for (i, img) in enumerate(imgs[:2])]
        axs += [plt.subplot(gs[1, i], projection=img.crs) for (i, img) in enumerate(imgs[2:])]

        # Start filling each panel
        previous_edges = None

        for (i, (key, scale)) in enumerate(self._panels.items()):
            # Compute the extent given the scale
            # First, find the coordinates of the edges
            edge_coords = self._geo.direct([self._lon, self._lat], [270, 90, 180, 0], key)

            # Define the extent ...
            this_extent = (edge_coords[0][0], edge_coords[1][0],
                           edge_coords[2][1], edge_coords[3][1])

            # ... and set it
            axs[i].set_extent(this_extent, crs=ccrs.PlateCarree())

            # Add the image
            axs[i].add_image(imgs[i], scale)

            # Add the image copyright
            if i in [0, 1, 2]:
                txt = '© Google Maps'
            else:
                txt = '© OpenStreetMap'
            axs[i].text(0.99, 0.01, txt, transform=axs[i].transAxes,
                        fontsize=8, color='k', ha='right', va='bottom',
                        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', pad=2))

            # Plot the station location
            axs[i].scatter([self._lon], [self._lat], marker=crosshair(pa=45),
                           facecolor='none', edgecolor='w', s=300,
                           lw=2, transform=ccrs.PlateCarree())
            # axs[i].scatter([self._lon], [self._lat], marker=crosshair(pa=45),
            #               facecolor='none', edgecolor='k', s=300,
            #               lw=1, transform=ccrs.PlateCarree())

            # Draw  circles of 30m and 10m in radius, for class 2 and class 3 sites (T + RH)
            if i in [0, 1]:
                for r in [100, 30, 10]:
                    circle = Geodesic().circle(lon=self._lon, lat=self._lat, radius=r,
                                               n_samples=360, endpoint=True)
                    geom = Polygon(circle)
                    axs[i].add_geometries((geom,),
                                          crs=ccrs.PlateCarree(), facecolor='none', ls='-',
                                          edgecolor='w', linewidth=1)
                    axs[i].text(circle[0][0], circle[0][1], rf'R={r} m',
                                fontsize=8, fontweight='bold', color='w',
                                ha='center', va='bottom', transform=ccrs.PlateCarree())

            # Add the scale of the frame as a title
            if (scl := 2*key) >= 1000:
                scl /= 1000
                unt = 'km'
            else:
                unt = 'm'

            axs[i].set_title(label=rf'{scl} {unt} $\times$ {scl} {unt}')

            # Draw the footprint of the previous image, if any
            if previous_edges is not None:
                if i == 3:
                    col = 'k'
                else:
                    col = 'w'
                axs[i].plot([previous_edges[0], previous_edges[0],
                             previous_edges[1], previous_edges[1],
                             previous_edges[0]],
                            [previous_edges[2], previous_edges[3],
                             previous_edges[3], previous_edges[2],
                             previous_edges[2]],
                            ls='--', c=col, lw=1, transform=ccrs.PlateCarree())

            previous_edges = copy.copy(this_extent)

        # Add the station info
        self._fig.text(0.03, 0.99, f'{self._name}',
                       fontsize=20, fontweight='bold', va='top', ha='left')

        # Add the coordinates
        lat_angle = Angle(self._lat, unit=deg_unit)
        lon_angle = Angle(self._lon, unit=deg_unit)

        full_coords = f"{lat_angle.to_string(unit=deg_unit,
                                             sep=":", precision=3, alwayssign=True)} N | " \
                      f'{lon_angle.to_string(unit=deg_unit,
                                             sep=":", precision=3, alwayssign=True)} E'
        self._fig.text(0.97, 0.99,
                       full_coords, va='top', fontsize=20, fontweight='bold', ha='right')
        self._fig.text(0.97, 0.965,
                       rf'{self._lat:+.6f} | {self._lon:+.6f}',
                       # | {alt:+.1f} m',
                       fontsize=11, fontweight='normal', va='top', ha='right')

        # Let's also add the time of creation at the bottom of the figure, including the timezone
        self._fig.text(0.97, 0.01, build_copyright_statement(self._copyright, width=None),
                       va='bottom', ha='right', fontsize=11, color='gray')


class WigosSite(Site):
    """ Class for WIGOS sites. """

    @log_func_call(logger)
    def __init__(self, wigosId: str) -> None:
        """ Basic init routine.

            Args:
                wigosId (str): The WIGOS ID of the site.

            Raises: MapmetnetError

        """

        # USe wmoutils to derive the coordinatesof the WigosSite
        entry = query_oscar_surface(wigosId=wigosId)

        if len(entry) == 0:
            raise MapmetnetError(f'No entry found for WIGOS ID {wigosId}.')
        elif len(entry) > 1:
            raise MapmetnetError(f'Multiple entries found for WIGOS ID {wigosId} ?!')

        super().__init__(entry.item(row=0, column='latitude'),
                         entry.item(row=0, column='longitude'),
                         name=f'{entry.item(row=0, column="wigosId")} ' +
                              f'{entry.item(row=0, column="name")}')
