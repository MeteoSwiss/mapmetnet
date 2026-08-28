"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS.

Distributed under the terms of the 3-Clause BSD License.

SPDX-License-Identifier: BSD-3-Clause

Module contains: mapper package classes
"""

# Import from Python
import logging
import warnings

import numpy as np
import polars as pl

from matplotlib import pyplot as plt
from matplotlib.figure import Figure as mplfig
from matplotlib.gridspec import GridSpec
import matplotlib.patheffects as mplpe
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

import shapely
from shapely import geometry as sgeom
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes
from owslib.wmts import WebMapTileService

import wmoutils

# Import from this package
from .copyright import build_copyright_statement
from .hardcoded import WDQMS_COLORS, WIDTH_TWOCOL
from .errors import MapmetnetError, MapmetnetWarning
from .logger import log_func_call
from .ne import get_ne_records, get_ne_country
from . import network, gibs, utils
from .eez import get_eez
from .utils import set_mplstyle, format_var_name

# Instantiate the module logger
logger = logging.getLogger(__name__)


class Plotter():
    """ Great Great Great Grand Parent Mapper class, holding basic plotting utilities. """

    @log_func_call(logger)
    def __init__(self, when: str | None = None) -> None:
        """ Basic init routine.

        Args:
            when: The date when the map was created, in a human-readable format. Optional.

        """

        # Let's also create the other atribute that will become relevant later on
        self._fig: mplfig | None = None
        self._axs: list = []
        self._copyright: dict = {'mmn': when}

    @property
    def fig(self) -> mplfig:
        """ The Matplotlib figure instance holding the map. """
        if self._fig is None:
            raise MapmetnetError("Figure not created yet.")
        return self._fig

    @property
    def axs(self) -> list:
        """ The list of Matplotlib axes holding the various figure elements. """
        return self._axs

    def _get_ax(self, ax_id: int) -> plt.Axes | GeoAxes:
        """ Get a sepcific ax given its id. """
        if len(self.axs) < ax_id + 1:
            warnings.warn(f'len(self.axs) [{len(self.axs)}] < ax_id + 1 [{ax_id + 1}].',
                          MapmetnetWarning)
            raise MapmetnetError(f"No ax with id {ax_id}.")
        return self._axs[ax_id]

    @staticmethod
    def show() -> None:
        """ Wrapper around plt.show() """
        plt.show()

    @staticmethod
    @set_mplstyle
    def savefig(fname: str | None, dpi: int | None = None) -> None:
        """ Wrapper around plt.savefig() """

        if fname is not None:
            plt.savefig(fname, dpi=dpi)


class Mapper(Plotter):
    """ Great Grand Parent Mapper, class tuned for plotting a map with little else. """

    @log_func_call(logger)
    def __init__(self, lat: float, lon: float, extent: float | None) -> None:
        """ Basic init routine.

            Args:
                lat (float): The latitude of the map center.
                lon (float): The longitude of the map center.
                extent (float | None): The map extent in degrees.

            Raises: ValueError, TypeError

        """

        # Trigger the base class init
        super().__init__()

        # Set the central coordinates and the extent of the map
        self._center_lat = lat
        self._center_lon = lon

        # Compute and store the map limits
        if extent is not None:
            self._lon_lims = np.array([-extent/2., extent/2.]) + self._center_lon
            self._lat_lims = np.array([-extent/2., extent/2.]) + self._center_lat
        else:
            self._lat_lims = np.array([np.nan, np.nan])
            self._lon_lims = np.array([np.nan, np.nan])

        # Set the default map projection
        self._proj = ccrs.Orthographic(central_longitude=self._center_lon,
                                       central_latitude=self._center_lat)

        # Let's also create the other atribute that will become relevant later on
        self._legend_handles: dict = {}
        self._copyright['cartopy'] = 'Orthographic'
        self._copyright['ne'] = []

    @property
    def ax_map(self) -> GeoAxes:
        """ The Matplotlib axis holding the map. """
        return self._get_ax(0)

    @property
    def ax_leg(self) -> plt.Axes:
        """ The Matplotlib axis holding the legend. """
        return self._get_ax(1)

    @property
    def ax_clb(self) -> plt.Axes:
        """ The Matplotlib axis holding the colorbar. """
        return self._get_ax(2)

    @set_mplstyle
    def create_fig(self, figid: int | None = None) -> None:
        """ Creation of plotting areas.

        Args:
            figid (int, optional): the matplotlib figure ID.
                Will first close it if it already exists.

        """

        # If a fig id was specified, let's close the plot
        if figid is not None:
            plt.close(figid)

        # Create the Figure and store it for later
        self._fig = plt.figure(figid, figsize=(WIDTH_TWOCOL, 10))

        # Create the axes
        gs = GridSpec(2, 2, width_ratios=[1, 0.3], height_ratios=[2, 1],
                      left=0.06, right=0.98, top=0.92, bottom=0.04, hspace=0, wspace=0.1)

        # First, the ax that will hold the map
        ax0 = plt.subplot(gs[:, 0], projection=self._proj)

        # Then the supplementary "legend" ax
        axl = plt.subplot(gs[0, 1])
        # Then the supplementary "legend" ax
        axc = plt.subplot(gs[1, 1])

        # Store the axes for later use.
        self._axs = [ax0, axl, axc]

    @log_func_call(logger)
    def apply_extent(self) -> None:
        """ Set the map extent (symetric along N-S and E-W).
        """

        #  ... to finally be able to set the plot extent
        if self.ax_map is not None:
            self.ax_map.set_extent(tuple(self._lon_lims)+tuple(self._lat_lims))

    @log_func_call(logger)
    def set_map_lims(self,
                     lon_min: float | None = None,
                     lon_max: float | None = None,
                     lat_min: float | None = None,
                     lat_max: float | None = None,
                     squarify: bool = True) -> None:
        """ Adjust the map limits.

        Args:
            lon_min (foat, optional): if set, will override the minimum longitude of the map.
            lon_max (foat, optional): if set, will override the maximum longitude of the map.
            lat_min (foat, optional): if set, will override the minimum latitude of the map.
            lat_max (foat, optional): if set, will override the maximum latitude of the map.
            squarify (bool, optional): if True, the map will be squarified. Defaults to True.
        """

        # Start from the country extent ...
        lon_lims = self._lon_lims
        lat_lims = self._lat_lims

        # ... deal with user-set limits
        for lon_id, lon in enumerate([lon_min, lon_max]):
            if lon is not None:
                lon_lims[lon_id] = lon
        for lat_id, lat in enumerate([lat_min, lat_max]):
            if lat is not None:
                lat_lims[lat_id] = lat

        # ... and make it square ...
        if squarify:
            lon_lims, lat_lims = utils.squarify_extent(lon_lims, lat_lims)

        # .. to finally store it back.
        self._lon_lims = lon_lims
        self._lat_lims = lat_lims

        # And apply them
        self.apply_extent()

    @property
    def true_lon_lims(self) -> tuple:
        """ The longitude limits of the map. """
        if self.ax_map is None:
            return (None, None)
        return self.ax_map.get_extent(crs=ccrs.PlateCarree())[:2]

    @property
    def true_lat_lims(self) -> tuple:
        """ The latitude limits of the map. """
        if self.ax_map is None:
            return (None, None)
        return self.ax_map.get_extent(crs=ccrs.PlateCarree())[2:]

    @log_func_call(logger)
    def add_background(self, which: str | None = None) -> None:
        """ Add a background to the map.

        Args:
            which (str | None, optional): the background to add. If None (default), will use the
                default Natural Earth "land" feature. If 'ne', will use the Natural Earth Relief
                tiles. If 'elevation', 'lightning', 'pop-density', 'croplands' or 'human-footprint',
                will use the corresponding NASA GIBS layer. Defaults to None.

        For more information on the different NASA GIBS layers, please refer to:
        https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/#visualization-product-catalog

        """

        if which is None:
            # Use the Natural Earth "land" feature as default background.
            self.ax_map.add_feature(cfeature.OCEAN.with_scale('10m'))
            self.ax_map.add_feature(cfeature.LAND.with_scale('10m'),
                                    facecolor=(0.95, 0.95, 0.95))
            # No colorbar required
            self.ax_clb.axis('off')

        elif which == 'ne':
            lon_lims = np.array(self.true_lon_lims)
            lat_lims = np.array(self.true_lat_lims)

            self.ax_map.background_img(name='NaturalEarthRelief', resolution='high',
                                       extent=list(utils.pad_angular_range(lon_lims, 0.1)) +
                                       list(utils.pad_angular_range(lat_lims, 0.1)))
            # Add the relevant copyright notice
            self._copyright['ne'] += ['terrain']

            # No colorbar required
            self.ax_clb.axis('off')

        elif which in ['elevation', 'lightning', 'pop-density', 'croplands', 'human-footprint']:
            # Deal with all the NASA GIBS layers
            url = 'http://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi'
            wmts = WebMapTileService(url)

            if which == 'elevation':
                self.ax_map.add_wmts(wmts, 'SRTM_Color_Index')
                self._copyright['gibs'] = 'Terrain elevation by NASA SRTM (v3)'
                # Load the png, and get it ready for plotting
                cb_img = gibs.get_cb_img('SRTM_Color_Index_V.svg')

            elif which == 'lightning':
                self.ax_map.add_wmts(
                    wmts, 'LIS_Very_High_Resolution_Lightning_Full_Climatology_LIS_Mean_Flash_Rate')
                self._copyright['gibs'] = 'Mean Lightning Flash Rate (1998-2014) by the LIS'
                # Load the png, and get it ready for plotting
                cb_img = gibs.get_cb_img(
                    'LIS_Very_High_Resolution_Lightning_Full_Climatology_LIS_Mean_Flash_Rate_V.svg')

            elif which == 'pop-density':
                self.ax_map.add_wmts(wmts, 'GPW_Population_Density_2020')
                self._copyright['gibs'] = 'UN-Adjusted pop. density (2020)'
                # Load the png, and get it ready for plotting
                cb_img = gibs.get_cb_img('GPW_Population_Density_2000_V.svg')

            elif which == 'croplands':
                self.ax_map.add_wmts(wmts, 'Agricultural_Lands_Croplands_2000')
                self._copyright['gibs'] = 'Global Agricultural Lands, v1 (2000)'
                # Load the png, and get it ready for plotting
                cb_img = gibs.get_cb_img('Agricultural_Lands_Croplands_2000_V.svg')

            elif which == 'human-footprint':
                self.ax_map.add_wmts(wmts, 'Human_Footprint_1995-2004')
                self._copyright['gibs'] = 'Global Human Footprint (Geographic), v2 (1995-2004)'
                # Load the png, and get it ready for plotting
                cb_img = gibs.get_cb_img('Human_Footprint_1995-2004_V.svg')

            else:
                raise MapmetnetError(f"Unknown background: {which}")

            # Finally, plot the colorbar
            self.ax_clb.imshow(cb_img)
            self.ax_clb.axis('off')

        else:
            raise MapmetnetError(f"Unknown background: {which}")

    @log_func_call(logger)
    def add_rivers_and_lakes(self) -> None:
        """ Add rivers and lakes to the map. """

        self.ax_map.add_feature(cfeature.RIVERS.with_scale('10m'))
        self.ax_map.add_feature(cfeature.LAKES.with_scale('10m'))
        self._copyright['ne'] += ['rivers', 'lakes']

    @log_func_call(logger)
    def draw_border(self, item, is_disputed: bool = False) -> None:
        """ Draw a border on the map.

        Args:
            item: a Natural Earth record containing the geometry to add, and the relevant
                attributes to build the legend handle.
            is_disputed (bool, optional): if True, the border will be drawn with a dotted line
                anbd tagged accordingly.

        .. Warning::
            This function is used both for the regular borders and the disputed area borders, and
            it assesses the nature of the border based on both the Natural Earth attributes and
            the ISO attributes. If any of these sources flags a border as disputed, then it will
            be drawn as such, and a warning will be triggered to make sure the user is aware of
            this.

        """

        # Check if the country bounds overlap with the extent of the map
        if not utils.is_overlapping(item.geometry,
                                    self.ax_map.get_extent(crs=ccrs.PlateCarree())):
            return

        # Assess the nature of the border
        # 1) according to Natural Earth
        is_ne_disputed = item.attributes['FEATURECLA'] != 'International boundary (verify)'
        # 2) according to ISO
        is_iso_disputed = item.attributes['FCLASS_ISO'] in ['Unrecognized',
                                                            'Disputed (please verify)']

        # Tweak the look of things depending on the border type ...
        if is_disputed or is_ne_disputed or is_iso_disputed:
            ls = ':'
            lbl = 'Borders (unsettled)'

            # Trigger a warning, to make sure the user is aware that one border is problematic
            msg = f"Unsettled border [{item.attributes['NAME']}]: " +\
                f"{item.attributes['ADM0_LEFT']} - " + \
                f"{item.attributes['ADM0_RIGHT']}"
            logger.warning(msg)
            # This is sufficiently important to raise a visible warning as well ...
            warnings.warn(msg, MapmetnetWarning)

        else:
            ls = '-'
            lbl = 'Borders'

        self._legend_handles[lbl.lower().replace(' ', '_')] = mlines.Line2D(
            [], [], color='k', ls=ls, lw=0.75, label=lbl)

        # Actually draw the borders
        self.ax_map.add_geometries(
                item.geometry, crs=ccrs.PlateCarree(), facecolor='none', edgecolor='k',
                ls=ls, lw=0.75)

    @log_func_call(logger)
    def add_borders(self) -> None:
        """ Add the relevant borders on the map, including the disputed ones. """

        # Loop through all the boundary lines, and only deal with those that overlap with
        # the plotting area
        for item in get_ne_records(resolution='10m', category='cultural',
                                   name='admin_0_boundary_lines_land'):
            self.draw_border(item, is_disputed=False)

        # Then, loop through the officially disputed area boundaries,
        # and draw these if applicable...
        for item in get_ne_records(resolution='10m', category='cultural',
                                   name='admin_0_boundary_lines_disputed_areas'):

            self.draw_border(item, is_disputed=True)

        self._copyright['ne'] += ['borders']

    @log_func_call(logger)
    def add_coast(self) -> None:
        """ Add the coastline to the map. """
        self.ax_map.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='k', lw=0.75)

    @log_func_call(logger)
    def highlight_country(self, iso_alpha3: str | list, show_names: bool = False) -> None:
        """ Highlight a given set of countries on the map, by covering the other ones with
        a semi-transparent white layer.

        Args:
            iso_alpha3 (str | list): the 3-letter ISO code of the country (or countries) to
                highlight.
            show_names (bool, optional): if True, will display the names of non-highlighted
                countries. Defaults to False.

        """

        if isinstance(iso_alpha3, str):
            iso_alpha3 = [iso_alpha3]

        # Loop through all the countries, and only deal with those that overlap with
        # the plotting area
        for item in get_ne_records(resolution='10m', category='cultural',
                                   name='admin_0_countries'):

            # Check if the country bounds overlap with the extent of the map
            if not utils.is_overlapping(item.geometry,
                                        self.ax_map.get_extent(crs=ccrs.PlateCarree())):
                continue

            # Fill the neighboring countries with semi-transparent white
            # TODO: Checking ISO_A3 is not enough. We should also check SOV_A3 and maybe
            # some other attributes, because not everyone has an ISO_A3 ...
            if item.attributes['ISO_A3'] not in iso_alpha3:
                self.ax_map.add_geometries(item.geometry, crs=ccrs.PlateCarree(),
                                           facecolor=(1, 1, 1), alpha=0.7,
                                           edgecolor='none',
                                           label=item.attributes['ADM0_A3'])

            # Add the names of the countries, but only if the country centroid falls within the map.
            lon_lims = np.array(self.true_lon_lims)
            lat_lims = np.array(self.true_lat_lims)

            if lon_lims[0] < item.geometry.centroid.x < lon_lims[1] and \
               lat_lims[0] < item.geometry.centroid.y < lat_lims[1] and \
               item.attributes['LABELRANK'] < 10 and \
               item.attributes['ISO_A3'] not in iso_alpha3 and \
               show_names:

                self.ax_map.annotate(item.attributes['NAME'],
                                     xy=(item.geometry.centroid.x, item.geometry.centroid.y),
                                     xytext=(0, 0), textcoords='offset fontsize',
                                     color=(0.25, 0.25, 0.25), fontsize=11,
                                     ha='center', va='center',
                                     path_effects=[mplpe.withStroke(linewidth=0.2, foreground="w")],
                                     transform=ccrs.PlateCarree())

    @log_func_call(logger)
    def add_gridlines(self) -> None:
        """ Add the lat/lon gridlines. """

        gl = self.ax_map.gridlines(draw_labels=True, ls='-', lw=0.25, color='k')
        gl.xlabel_style = {'size': 12, 'color': 'k'}
        gl.ylabel_style = {'size': 12, 'color': 'k'}
        gl.bottom_labels = False  # To make space for the copyright statement

    @log_func_call(logger)
    def add_copyright(self) -> None:
        """ Add the copyright notice, based on the content of self._copyright_statement. """

        self._copyright['mch'] = None
        txt = build_copyright_statement(self._copyright)

        self.ax_map.text(0.5, -0.03, txt,
                         ha='center', va='bottom', transform=self.ax_map.transAxes,
                         wrap=True, fontsize=7,
                         bbox={'boxstyle': 'Round', 'pad': 1, 'ec': 'k', 'fc': 'w'}, zorder=100)

    @log_func_call(logger)
    def add_legend(self) -> None:
        """ Add the legend to to figure, based on the content of self._leg_handles. """

        self.ax_leg.legend(handles=[handle for (_, handle) in self._legend_handles.items()],
                           fontsize=12,
                           loc='lower center', title=r'Legend',
                           title_fontproperties={'weight': 'bold', 'size': 12})
        self.ax_leg.axis('off')

    @log_func_call(logger)
    def add_title(self, title: str, subtitle: str | None = None) -> None:
        """ Add a title (and posibly a subtitle) to the plot.

        Args:
            title (str): the title.
            subtitle (str, optional): the subtitle.

        """

        self.ax_leg.text(0.5, 1.1, title,
                         transform=self.ax_leg.transAxes, weight='bold',
                         ha='center', va='top', fontsize=13)
        if subtitle is not None:
            self.ax_leg.text(0.5, 1.0, subtitle, transform=self.ax_leg.transAxes,
                             ha='center', va='top', fontsize=12)


class NetworkMapper(Mapper):
    """ Grand Parent Mapper class, designed to plot and characterize custom stations
    from a given list. """

    @set_mplstyle
    @log_func_call(logger)
    def add_stations(self, stations: pl.DataFrame,
                     influence_radius: float | int | None = None,
                     facecolor: str | tuple = 'k',
                     edgecolor: str | tuple = 'w',
                     marker: str = 's', size: int = 30,
                     linewidth: float = 0.5,
                     label: str | None = None,
                     ) -> shapely.geometry:
        """ Add a series of stations to the map.

        Args:
            stations (polars.DataFrame): DataFrame of stations to plot. Must contain the columns
                'longitude' and 'latitude' at the very least.
            influence_radius (int|float, optional): influence radius of each station, in km.
                Defaults to None, in which case no radius will be drawn.
            facecolor (str|tuple, optional): marker facecolor.
            edgecolor (str|tuple, optional): marker edgecolor.
            marker (str, optional): marker shape, fed to scatter(). If None, then no points are
                drawn.
            size (int, optional): marker size, in pts, fed to scatter().
            linewidth (float, optional): marker edge linewidth, fed to scatter().
            label (str|tuple, optional): station label. Defaults to None (= no legend).
            legend (str, optional): if 'generic', the country overlap values will not be shown.
                Useful for regional maps. Defaults to 'specific'.

        Returns: (shapely.geometry, area) - a tuple of the combined gemoetry of all the station
            areas of influence, and country fractional area covered by the stations.

        """

        # Draw the stations if warranted
        if marker is not None:
            self.ax_map.scatter(stations.get_column('longitude').to_numpy(),
                                stations.get_column('latitude').to_numpy(),
                                marker=marker, facecolor=facecolor, s=size,
                                edgecolor=edgecolor, transform=ccrs.PlateCarree(),
                                linewidth=linewidth,
                                zorder=101)

            # Deal with the legend if warranted
            if label is not None:

                self._legend_handles[f'stations_{label}'] = \
                    mlines.Line2D([], [], markerfacecolor=facecolor,
                                  markeredgecolor=edgecolor,
                                  ls='', marker=marker, markersize=10,
                                  label=f'{label} [{len(stations)}]')

        # If no influence radius was specified, we are done here
        if influence_radius is None:
            return None, None

        # Assemble circle geometries for each point
        geoms = []
        for row in stations.select(pl.col('longitude', 'latitude')).iter_rows():
            geoms += [utils.get_circle_geom(row[0], row[1], influence_radius)]

        # Merge them all into a single layer ...
        combined_geoms = shapely.union_all(geoms)
        # ... and also find the overlap area ...
        intersect_geoms = utils.get_overlap_geom(geoms)

        # ... that I can then plot on the map.
        self.ax_map.add_geometries(combined_geoms, crs=ccrs.PlateCarree(),
                                   facecolor=facecolor,
                                   edgecolor=edgecolor,
                                   linewidth=0, ls='-', alpha=0.2)

        # ... add it to the legend
        self._legend_handles[f'stations_{label}_zone'] = \
            mpatches.Patch(facecolor=facecolor, edgecolor=edgecolor,
                           alpha=0.2, label=r'$R$ = ' + f'{influence_radius} km')

        # CHeck if the intersect geometry is null
        if not intersect_geoms.is_empty:
            self.ax_map.add_geometries(intersect_geoms, crs=ccrs.PlateCarree(),
                                       facecolor='none',
                                       edgecolor=facecolor,
                                       hatch='////',
                                       linewidth=0, ls='-', alpha=1)

            # self._legend_handles[f'stations_{label}_zone_intersect'] = \
            #    mpatches.Patch(facecolor='none', edgecolor=facecolor, lw=0,
            #                   hatch='////',
            #                   alpha=1, label='Overlap')

        return combined_geoms, intersect_geoms

    @log_func_call(logger)
    def add_geom_union_outline(self, geoms: list, label: str | None = None) -> None:
        """ Given a list of geometries, draw the outline of their union.

        Args:
            geoms (list): list of shapely geometries to merge before drawing their outline.
            label (str, optional): label of the union. Defaults to None (= no legend).

        """

        # First, merge the geometries ...
        combined_geoms = shapely.union_all(geoms)

        # ... then plot it as an outline and add it to the legend
        self.ax_map.add_geometries(combined_geoms, crs=ccrs.PlateCarree(),
                                   facecolor='none',
                                   edgecolor='k',
                                   linewidth=0.5, ls='-')

        # Add a label if warranted
        if label is not None:
            # area = self.get_surface_fraction(combined_geoms)
            self._legend_handles['stations_outline'] = \
                mpatches.Patch(facecolor='none', edgecolor='k',
                               label=f'{label}')

    @log_func_call(logger)
    def link_neighbors(self, stations: pl.DataFrame,
                       color: str | tuple = (0.35, 0.35, 0.35),
                       thres: float | None = None,
                       drop_not_so_bad: bool = False,
                       **kwargs: str) -> float:
        """ Given a set of stations, compute the neighbors and draw the connection on the map.

        Args:
            stations (polars.DataFrame): DataFrame of stations to plot. Must contain the columns
                'longitude' and 'latitude' at the very least.
            color (str|tuple, optional): line color. Defaults to 'k'.
            thres (float, optional): if set, vertices longer than this value (in km) will be drawned
                with dashes instead.
            drop_not_so_bad (bool, optional): if True, the not_so_bad vertices will be ignored.
                Defaults to False.
            **kwargs (optional): all other arguments will be fed to the plot() function.

        Returns:
            float: the mean separation between stations.

        """

        # First, identify the neighbor stations and their connectinfg vertices
        pts = stations.select(pl.col("longitude", "latitude")).to_numpy()

        # Next, find the (good) neighbor vertices and their mean separation
        mean_sep, _, neighbor_verts = network.get_mean_sep(pts[:, 0], pts[:, 1],
                                                           drop_not_so_bad=drop_not_so_bad)

        # Add these to the map
        for vert, dist in neighbor_verts.items():
            if thres is not None and dist > thres*1e3:
                ls = '--'
            else:
                ls = '-'

            self.ax_map.plot(pts[vert, 0], pts[vert, 1], transform=ccrs.Geodetic(),
                             ls=ls, c=color, **kwargs)

        # Add the legend
        if thres is not None:
            self._legend_handles['neighbor_vertices'] = \
                mlines.Line2D([], [], color=color, ls='-',
                              label=rf'Neighbors ($d\leq{thres:.0f}$ km)')
            self._legend_handles['neighbor_vertices_thres'] = \
                mlines.Line2D([], [], color=color, ls='--',
                              label=rf'Neighbors ($d>{thres:.0f}$ km)')
        else:
            self._legend_handles['neighbor_vertices'] = \
                mlines.Line2D([], [], color=color, ls='-',
                              label='Neighbors')

        return mean_sep


class CountryMapper(NetworkMapper):
    """ Parent Mapper class, tuned for focusing the plot on a specific country. """

    @log_func_call(logger)
    def __init__(self, country_code: str, mrgid: int | None = None) -> None:
        """ Basic init routine.

            Args:
                country_code (str): a len(3) str containing the country code.
                mrgid (int, optional): a Marine Regions Geographic IDengifier, used to identify
                    the maritime boundaries of an applicable Exclusive Economic Zone (EEZ).
                    See https://www.marineregions.org/mrgid.php for details.

            Raises: ValueError, TypeError

        """

        # Some basic sanity checks
        match country_code:
            case str():
                if len(country_code) != 3:
                    raise ValueError('country_code should be str of len(3).')
            case _:
                raise TypeError("country_code must be a str")
        match mrgid:
            case None:
                pass
            case int():
                pass
            case _:
                raise TypeError("mrgid should be an int")

        # Assign the values to attibutes
        self._country_code = country_code
        self._mrgid = mrgid

        # Fetch and set the country record from Natural Earth and store it, while I'm at it
        self._country = get_ne_country(self.country_code)

        # Fetch the EEZ if warranted
        self._eez = get_eez(self.mrgid)

        # Let's now trigger the Parent init
        super().__init__(lat=self.country.geometry.centroid.y,
                         lon=self.country.geometry.centroid.x,
                         extent=None)

        # Override the map limits based on the country bounds ...
        self._lon_lims = np.array(self.country.bounds[0::2])
        self._lat_lims = np.array(self.country.bounds[1::2])

        # ... then expand them further with the EEZ ...
        for item in self.eez:
            if item.bounds[0] < self._lon_lims[0]:
                self._lon_lims[0] = item.bounds[0]
            if item.bounds[1] < self._lat_lims[0]:
                self._lat_lims[0] = item.bounds[1]
            if item.bounds[2] > self._lon_lims[1]:
                self._lon_lims[1] = item.bounds[2]
            if item.bounds[3] > self._lat_lims[1]:
                self._lat_lims[1] = item.bounds[3]

    @property
    def country_code(self) -> str:
        """ Country code as a 3 letter string. """
        return self._country_code

    @property
    def country(self):
        """ Return the target country Record. """
        return self._country

    @property
    def eez(self) -> list:
        """ Return the list of EEZ geometries associated with the target country. """
        return self._eez

    @property
    def mrgid(self) -> int | None:
        """ Marine Regions Geographic IDentifier. """
        return self._mrgid

    @log_func_call(logger)
    def set_map_lims(self,
                     lon_min: float | None = None,
                     lon_max: float | None = None,
                     lat_min: float | None = None,
                     lat_max: float | None = None,
                     squarify: bool = True,
                     pad_frac: float = 0.1) -> None:
        """ Adjust the map limits.

        Args:
            pad_frac (float, optional): padding fraction around the edges. Defaults to 0.1 (=10%).
            lon_min (foat, optional): if set, will override the minimum longitude of the map.
            lon_max (foat, optional): if set, will override the maximum longitude of the map.
            lat_min (foat, optional): if set, will override the minimum latitude of the map.
            lat_max (foat, optional): if set, will override the maximum latitude of the map.
            squarify (bool, optional): if True, the map will be squarified. Defaults to True.
        """

        # Add some padding all around ...
        self._lon_lims = utils.pad_angular_range(self._lon_lims, pad_frac)
        self._lat_lims = utils.pad_angular_range(self._lat_lims, pad_frac)

        # Then use the Parent method to apply the other requests
        super().set_map_lims(lon_min=lon_min, lon_max=lon_max, lat_min=lat_min, lat_max=lat_max,
                             squarify=squarify)

    @log_func_call(logger)
    def highlight_country(self, iso_alpha3: str | list | None = None,
                          show_names: bool = False) -> None:
        """ Highlight a given (set of) country(ies) on the map, by covering the other ones with a
        semi-transparent white layer.

        Args:
            iso_alpha3 (str | list | None, optional): the 3-letter ISO code of the country
                (or countries) to highlight. If None (default), will use self.country_code.
            show_names (bool, optional): if True, will display the names of neighboring countries.
                Defaults to False.

        """

        # If nothign specified, highlight the target country
        if iso_alpha3 is None:
            iso_alpha3 = self.country_code

        # Call the relevant Parent method to do the actual work
        super().highlight_country(iso_alpha3=iso_alpha3, show_names=show_names)

    @log_func_call(logger)
    def add_eez(self) -> None:
        """ Add the EEZ Maritime boundaries. """

        if len(self.eez) == 0:
            if self.mrgid is not None:
                warnings.warn(f"No EEZ found (mgrid = {self.mrgid})", MapmetnetWarning)
            return

        # Plot the EEZ boundaries
        for item in self.eez:
            # Check if the bounary is disputed
            ls = '-'
            label = 'EEZ limit'

            if 'Unsettled' in item.attributes['LINE_TYPE']:
                ls = '--'
                label += ' (unsettled)'
                self._legend_handles['EEZ'] = mlines.Line2D([], [], color='firebrick', ls='--',
                                                            label='EEZ (200 NM, unsettled)')
            else:
                self._legend_handles['EEZ unsettled'] = mlines.Line2D([], [], color='firebrick',
                                                                      label='EEZ (200 NM)')
            # Plot it acordingly
            self.ax_map.add_geometries(item.geometry, crs=ccrs.PlateCarree(),
                                       edgecolor='firebrick', facecolor='none', ls=ls,
                                       label=label)

        # Include a dedicated copyright statement if I have some EEZ boundaries
        self._copyright['eez'] = None

    @log_func_call(logger)
    def add_capital(self, ref_radius: int | float | None = None) -> None:
        """ Add a marker for the target country's capital city. Optionally draw a reference circle
        around it.

        Args:
            ref_radius (int|float, optional): if set, will draw a circle of 'ref_radius' km in
                radius around the capital. Defaults to None.

        """
        # Loop through all the cities from Natural Earth until I find the correct one ...
        for place in get_ne_records(resolution='10m', category='cultural',
                                    name='populated_places'):
            if place.attributes['ADM0_A3'] == self.country_code and \
              'Admin-0 capital' in place.attributes['FEATURECLA']:
                self.ax_map.scatter(place.geometry.x, place.geometry.y,
                                    transform=ccrs.PlateCarree(),
                                    marker='*', edgecolor='w', lw=0.5, s=100,
                                    facecolor='k', zorder=100)
                self.ax_map.annotate(place.attributes['NAME_EN'],
                                     xy=(place.geometry.x, place.geometry.y),
                                     transform=ccrs.PlateCarree(),
                                     xytext=(0.5, 0), textcoords='offset fontsize',
                                     va='center', ha='left', color='k',
                                     path_effects=[mplpe.withStroke(linewidth=0.5, foreground="w")],
                                     fontsize=10)
                capital = place
                break

            capital = None

        # Raise an error if I could not find the capital city
        if capital is None:
            warnings.warn(f"Could not find the capital city for {self.country_code}",
                          MapmetnetWarning)
            return

        # Drawing a proper circle around specific coordinates
        if ref_radius is not None:
            self.ax_map.add_geometries(utils.get_circle_geom(capital.geometry.x,
                                                             capital.geometry.y,
                                                             ref_radius),
                                       crs=ccrs.PlateCarree(),
                                       facecolor='none', edgecolor='k', linewidth=1, ls='-.')
            self._legend_handles['scale'] = mlines.Line2D([], [], color='k', ls='-.',
                                                          label=rf'$R$ = {ref_radius} km')

    @log_func_call(logger)
    def get_surface_fraction(self, geom: sgeom) -> float:
        """ Compute the target country's surface fraction of a given geometry.set

        Args:
            geom (shapely geometry): the geometry to assess

        Returns:
            float: the fraction of the target country's surface that is covered by the
                input geometry.
        """

        area = shapely.area(shapely.intersection(self.country.geometry, geom))
        return area/shapely.area(self.country.geometry)


class GBONMapper(CountryMapper):
    """ Child Mapper class, tuned for automatically plotting a given country's GBON information.
    """

    @log_func_call(logger)
    def add_wdqms(self,
                  station_type: str = 'surface',
                  var_name: str = 'temperature',
                  interval: str = 'monthly',
                  category: str = 'availability',
                  date: str = '2026-01',
                  iso_a3: str | None = None,
                  wigos_ids: str | list | None = None,
                  show_influence_area: bool = True,
                  high_density: bool = False) -> tuple[float, float | None]:
        """ Add all WDQMS station statistics of the target country to the map.

        Args:
            station_type (str, optional): either 'surface' (default) or 'upper-air'.
            var_name (str, optional): name of variable to plot. Defaults to 'temperature'.
            interval (str, optional): assessment interval, i.e. one of
                ['monthly', 'daily', 'six_hour']. Defaults to 'monthly'.
            category (str, optional): assessment category. Defaults to 'availability'.
            date (str, optional): date of the availability assessment. Defaults to '2023-11'.
            iso_a3 (str, optional): station country code as ISO alpha 3.
                Defaults to None = target country.
            wigos_ids (list, optional): Defaults to None. If specified, will be combined with the
                country code using OR to select stations to be drawn.
            show_influence_area (bool, optional): if True (default), will draw the baseline
                influence area of the network.
            high_density (bool, optional):  if True, will use the GBON high-density
                (a.k.a "should") criteria for deriving the area of influence of stations.

        Returns:
            float, float: the network horizontal resolution and country coverage fraction

        TODO:
            - allow users to select the high-density/sea parameters for the influence area.
            - allow users to feed parameters to _link_neighbors().
            - clarify var_name for upper-stations (should be None).

        """

        # First deal with the influence radius.
        influence_radius = None
        if show_influence_area:
            # TODO: allow to select marine stations too ...
            influence_radius = wmoutils.gbon.get_influence_radius(station_type, over='land',
                                                                  high_density=high_density)
            influence_radius = int(np.round(influence_radius, 0))

        # Get the data straight from WDQMS
        # TODO: allow to select other parameters
        if category == 'availability':
            which = 'gbon'
        else:
            which = 'nwp'
        pdf = wmoutils.query.query_wdqms(which, station_type, interval, category,
                                         var_name, date)

        # Filter the values needed for the country
        if iso_a3 is None:
            iso_a3 = self.country_code
        if wigos_ids is None:
            wigos_ids = ['not-a-wigos-id']
        elif isinstance(wigos_ids, str):
            wigos_ids = [wigos_ids]

        # Filter the values as a function of country and WIGOS ids using the OR criteria
        pdf = pdf.filter((pl.col('country code') == iso_a3) |
                         (pl.col('wigosid').str.contains('|'.join(wigos_ids))))
        # pdf = pdf.filter(pl.col('latitude') > -60)  # used for Argentina

        # Now deal with each WDQMS color individually - store them so that I can compute the
        # full (combine) surface fraction as well.
        combined_geoms = []
        # TODO: the following essentially assumes that we are looking at availability. If we
        # want to look at quality, we need to look at another column ('rms'), etc ...
        for lvls in WDQMS_COLORS.items():
            sub_pdf = pdf.filter(pl.col('color code') == lvls[0])

            # Draw the stations
            if len(sub_pdf) > 0:
                geom, _ = self.add_stations(sub_pdf, influence_radius=influence_radius,
                                            facecolor=lvls[1]['facecolor'],
                                            edgecolor=lvls[1]['edgecolor'],
                                            marker=lvls[1]['marker'], size=lvls[1]['size'],
                                            label=lvls[1]['label'])

                # Store the geomettry for later
                combined_geoms += [geom]

            # Export the station list to file.
            # sub_pdf.write_csv(f'WDQMS_{iso_a3}_{station_type}_{var_name}_{interval}' +
            #                  f'_{date}_{lvls[0]}.csv')

        # Let's add the network horizontal resolution to the legend ...
        # ... after we compute it, evidently.
        # TODO: allow to differentiate between land and marine stations ...
        mean_sep = self.link_neighbors(pdf, thres=wmoutils.gbon.get_resolution(
            station_type, high_density=high_density))
        self._legend_handles['mean_sep'] = mlines.Line2D(
                [], [], color='none', ls='-', label=f'Mean sep.: {mean_sep:.1f} km')

        # Let's also compute the combined surface fraction from all layers ...
        # ... draw the outline ...
        # ... and add the relevant entry to the legend.
        if influence_radius is not None:
            self.add_geom_union_outline(combined_geoms)
            cov_frac = self.get_surface_fraction(shapely.union_all(combined_geoms))
            self._legend_handles['coverage'] = mlines.Line2D(
                [], [], color='none', ls='-', label=f'{iso_a3} coverage: {cov_frac:.1%}')
        else:
            cov_frac = None

        return mean_sep, cov_frac

    @log_func_call(logger)
    def generate_map(self, figid: int = 1, pad_frac: float = 0.2,
                     background: str | None = None,
                     station_type: str = 'surface',
                     var_name: str = 'temperature',
                     interval: str = 'monthly',
                     category: str = 'availability',
                     date: str = '2026-01',
                     wigos_ids: str | list | None = None,
                     show_influence_area: bool = False,
                     high_density: bool = False,
                     show_country_names: bool = False,
                     ref_radius: float | int | None = None,
                     save_fmts: str | list | None = None,
                     show: bool = False) -> str | None:
        """ All-in-one routine to generate a fully-fledged GBON Country map.

        Args:
            figid (int, optional): the matplotlib figure ID.
                Will first close it if it already exists.
            pad_frac (float, optional): padding fraction around the edges. Defaults to 0.1 (=10%).
            background (str, None): map background. See :py:func:`Mapper._add_background` for
                supported options. Defaults to None.
            station_type (str): either 'surface' or 'upper-air'.
            var_name (str): name of variable, e.g. 'Temperature'.
            interval (str, optional): assessment interval, i.e. one of
                ['monthly', 'daily', 'six_hour']. Defaults to 'monthly'.
            category (str, optional): WDQMS category to query. Defaults to 'availability'.
            date (str, optional): date of the availability assessment. Defaults to '2023-11'.
            wigos_ids (list, optional): Defaults to None. If specified, will be combined with the
                country code using OR to select stations to be drawn.
            show_influence_area (bool, optional): if True, will draw the baseline
                influence area of each station. Defaults to False.
            high_density (bool, optional): if True, will use the GBON high-density
                (a.k.a "should") criteria for deriving the area of influence of stations.
            show_country_names (bool, optional): if True, will draw the names of countries on the
                map. Defaults to False.
            ref_radius (int|float, optional): if set, will draw a circle of 'ref_radius' km in
                radius around the capital.
            save_fmts (str|list, optional): a str or list of str of formats to save the map to,
                e.g. ['pdf', 'png']. Defaults to None (= no figure saved).
            show (bool, optional): if True, will call plt.show() at the end. Defaults to False.

        Returns:
            str: the filename of the saved figure, if save_fmts was not None. Otherwise, None.

        Note:
            The concept of **baseline area of influence** for a GBON station was introduced by
            `Vogt et al., 2024`_, to which we refer the interested reader for details (see their
            Appendix A). In short, it corresponds to the area in the immediate vicinty of a station
            for which the GBON requirements (in terms station proximity) are met.

            By setting ``show_influence_area`` to True, the map will include a visual representation
            of the GBON baseline area of influence of every station. It will also add to the legend
            the percentage of the country that is covered by the combined GBON baseline area of
            influence of the total network.

            While this criteria (i.e. total country coverage) is NOT a formal GBON requirement per
            se (only the mean station separation is), we believe that it can still serve as a
            ueful indicator of the extent to which a given country is effectively covered by the
            GBON network, and which region, if any, may benefit most from the addition of new
            stations.

            .. _Vogt et al., 2024: https://www.un-soff.org/wp-content/uploads/2025/02/Democratic-Republic-of-Congo-GBON-National-Gap-Analysis.pdf.


        """

        self.create_fig(figid=figid)  # from Mapper class
        self.set_map_lims(pad_frac=pad_frac, squarify=True)  # from CountryMapper <- Mapper class
        self.add_background(which=background)  # from Mapper class
        self.add_rivers_and_lakes()  # from Mapper class
        self.add_borders()  # from Mapper class
        self.highlight_country(show_names=show_country_names)  # from CountryMapper <- Mapper class
        self.add_coast()  # from Mapper class
        self.add_capital(ref_radius=ref_radius)  # from CountryMapper class
        self.add_eez()  # from CountryMapper class
        self.add_gridlines()  # from Mapper class
        _ = self.add_wdqms(station_type=station_type, var_name=var_name, interval=interval,
                           category=category,
                           date=date, wigos_ids=wigos_ids,
                           high_density=high_density,
                           show_influence_area=show_influence_area)  # ... from GBONMapper class
        self.add_copyright()  # ... from Mapper class
        self.add_legend()  # ... from Mapper class
        hd_txt = ', high-density' if high_density else ''
        self.add_title(f'GBON compliance\n({station_type}{hd_txt})',
                       subtitle=f'{format_var_name(var_name)}\n{interval} {category} ({date})' +
                       '\n\nSource: https://wdqms.wmo.int/\n')  # ... from Mapper class

        if save_fmts is None:
            return None
        elif isinstance(save_fmts, str):
            save_fmts = [save_fmts]

        fn = f"GBON_map_{self.country_code}_{station_type}_{var_name.replace(' ', '-')}"
        if high_density:
            fn += '_high-density'
        if background is None:
            background = 'no-bkg'
        fn += f"_availability_{interval}_{date}_{background.replace('_', '-')}"

        for fmt in save_fmts:
            self.savefig(fn + f'.{fmt}', dpi=300)  # ... from Plotter class

        if show:
            self.show()  # ... from Plotter class

        return fn
