"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: classes related to individual sites
"""

# Import from Python
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

        # Default panel total widths, zoom levels, and imgs
        self._panel_widths = [80, 300, 1000, 10000]
        self._panel_zooms = [20, 18, 17, 13]
        self._panel_types = ['satellite'] * 3 + ['street']
        self._panel_imgs = [self._panel_type_to_img(pt) for pt in self._panel_types]
        self._panel_extents = [None] * 4
        self._copyright['cartopy'] = None
        self._name = name

    def _panel_type_to_img(self, panel_type: str) -> list:
        """ Convert a panel type to a cartopy image.

        Args:
            panel_type (str): The type of the panel, either 'satellite' or 'street'.

        Returns:
            list: A list containing the cartopy image tile and the
                corresponding copyright statement.
        """

        if panel_type == 'satellite':
            return [GoogleTiles(style='satellite'), '© Google Maps']
        elif panel_type == 'street':
            return [OSM(), '© OpenStreetMap']
        else:
            raise MapmetnetError(f'Unknown panel type {panel_type}.')

    @set_mplstyle
    def _create_fig(self, figid: int | None = None) -> None:
        """ Creation of plotting areas.

        Args:
            figid (int, optional): the matplotlib figure ID.
                Will first close it if it already exists.

        """

        # If a fig id was specified, let's close the plot
        if figid is not None:
            plt.close(figid)

        # Create the Figure and store it for later
        self._fig = plt.figure(figid, figsize=(WIDTH_TWOCOL, 15))

        # Create the axes
        gs = GridSpec(2, 2, width_ratios=[1]*2, height_ratios=[1]*2,
                      left=0.03, right=0.97, top=0.93, bottom=0.04, hspace=0.05, wspace=0.05)

        # Create the axes
        self._axs = [plt.subplot(gs[i//2, i % 2], projection=img[0].crs)
                     for (i, img) in enumerate(self._panel_imgs)]

        for (i, _) in enumerate(self._axs):

            # Setup the axis
            self._setup_ax(i)

    def _setup_ax(self, which: int) -> None:
        """ Set up the axes of the figure.

        Args:
            which (int): The index of the axis to set up.
        """

        # First, find the coordinates of the edges
        edge_coords = self._geo.direct([self._lon, self._lat], [270, 90, 180, 0],
                                       self._panel_widths[which]/2)

        # Define the extent ...
        this_extent = (edge_coords[0][0], edge_coords[1][0],
                       edge_coords[2][1], edge_coords[3][1])

        # ... and set it
        self.axs[which].set_extent(this_extent, crs=ccrs.PlateCarree())
        self._panel_extents[which] = this_extent

        # Add the image
        self.axs[which].add_image(self._panel_imgs[which][0], self._panel_zooms[which])

        # Add the image copyright
        self.axs[which].text(0.99, 0.01, self._panel_imgs[which][1],
                             transform=self.axs[which].transAxes,
                             fontsize=8, color='k', ha='right', va='bottom',
                             bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', pad=2))

        # Add the scale of the frame as a title
        if (width := self._panel_widths[which]) >= 1000:
            scl = 1.0e-3
            unt = 'km'
        else:
            scl = 1.0
            unt = 'm'

        # self._axs[which].set_title(
        #    label=rf'{width*scl} {unt} $\times$ {width*scl} {unt}')
        self.axs[which].text(0.01, 0.99, rf'{width*scl} {unt} $\times$ {width*scl} {unt}',
                             ha='left', va='top', transform=self.axs[which].transAxes,
                             # wrap=True,
                             fontsize=12,
                             bbox=dict(facecolor='white', alpha=1, edgecolor='none', pad=3),
                             zorder=100)

    def _show_footprints(self) -> None:
        """ Show the footprints of the previous panels on the current panel. """

        # Start looping over the applicable panels
        for (which, ax) in enumerate(self._axs[1:], start=1):
            if which == 3:
                col = 'k'
            else:
                col = 'w'

            # Get the previous edges
            previous_edges = self._panel_extents[which-1]
            # ... and plot them
            ax.plot([previous_edges[0], previous_edges[0], previous_edges[1], previous_edges[1],
                     previous_edges[0]],
                    [previous_edges[2], previous_edges[3], previous_edges[3], previous_edges[2],
                     previous_edges[2]],
                    ls='--', c=col, lw=1, transform=ccrs.PlateCarree())

    def _tag_site(self) -> None:
        """ Tag the site on the figure. """

        for (which, ax) in enumerate(self._axs):
            if which == 0:
                scl = 1000
            else:
                scl = 300

            # Plot the station location
            ax.scatter([self._lon], [self._lat], marker=crosshair(pa=45),
                       facecolor='none', edgecolor='w', s=scl,
                       lw=1.5, transform=ccrs.PlateCarree())

    def _draw_circle(self, radius: float, ax: plt.Axes) -> None:
        """ Draw a circle of a given radius around the central location.

        Args:
            radius (float): The radius of the circle in meters.
            ax (plt.Axes): The axis to draw the circle on.
        """

        # Draw  circles of 30m and 10m in radius, for class 2 and class 3 sites (T + RH)
        circle = Geodesic().circle(lon=self._lon, lat=self._lat, radius=radius,
                                   n_samples=360, endpoint=True)
        geom = Polygon(circle)
        ax.add_geometries((geom,),
                          crs=ccrs.PlateCarree(), facecolor='none', ls='-',
                          edgecolor='w', linewidth=1)
        ax.text(circle[0][0], circle[0][1], rf'R={radius} m',
                fontsize=8, fontweight='bold', color='w',
                ha='center', va='bottom', transform=ccrs.PlateCarree())

    def _add_title(self, title: str | None = None) -> None:
        """ Add a title to the figure.

        Args:
            title (str, optional): The title to add. Defaults to None = self._name.
        """

        if title is None:
            title = self._name if self._name is not None else ''

        self._fig.text(0.03, 0.99, f'{title}',
                       fontsize=20, fontweight='bold', va='top', ha='left')

    def _add_coords(self) -> None:
        """ Add the coordinates of the site to the figure. """

        # Add the coordinates
        lat_angle = Angle(self._lat, unit=deg_unit)
        lon_angle = Angle(self._lon, unit=deg_unit)

        full_coords = f"{lat_angle.to_string(unit=deg_unit,
                                             sep=':', precision=3, alwayssign=True)} N | " + \
                      f'{lon_angle.to_string(unit=deg_unit,
                                             sep=":", precision=3, alwayssign=True)} E'
        self._fig.text(0.97, 0.99,
                       full_coords, va='top', fontsize=20, fontweight='bold', ha='right')
        self._fig.text(0.97, 0.965,
                       rf'{self._lat:+.6f} N | {self._lon:+.6f} E',
                       # | {alt:+.1f} m',
                       fontsize=11, fontweight='normal', va='top', ha='right')

    def _add_copyright(self) -> None:
        """ Add the necessary copyright statement. """

        # Let's also add the time of creation at the bottom of the figure, including the timezone
        self._fig.text(0.97, 0.01, build_copyright_statement(self._copyright, width=None),
                       va='bottom', ha='right', fontsize=11, color='gray')

    def site_view(self, figid: int | None = None,
                  show_ref_circles: bool = True,
                  save_fn: str | None = None,
                  show: bool = False) -> None:
        """ Create the default mapmetnet site view.

        Args:
            figid (int, optional): the matplotlib figure ID.
                Will first close it if it already exists.
            show_ref_circles (bool, optional): whether to show the reference circles
                of 100m, 30m, and 10m in radius. Defaults to True.
            save_fn (str, optional): the filename to save the figure as.
                If None, the figure will not be saved. Defaults to None.
            show (bool, optional): whether to show the figure. Defaults to False.
        """

        self._create_fig(figid=figid)
        self._show_footprints()
        self._tag_site()
        for (which, ax) in enumerate(self._axs):
            if which in [0, 1] and show_ref_circles:
                for r in [100, 30, 10]:
                    self._draw_circle(r, ax)
        self._add_title()
        self._add_coords()
        self._add_copyright()
        self.savefig(save_fn)
        if show:
            self.show()


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
