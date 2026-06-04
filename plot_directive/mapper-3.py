import polars as pl
import matplotlib.lines as mlines
from mapmetnet.mapper import CountryMapper

# Create a list of station coordinates as a polars DataFrame
stations = pl.DataFrame({
    'longitude': [6.943021, 7.415201, 8.62053],
    'latitude': [46.812724, 47.178870, 47.690021]
})

# Setup the map
mymap = CountryMapper('CHE')
mymap.create_fig(figid=1)

# Make it asymetric to better fit the country shape
mymap.set_map_lims(pad_frac=0.02, lat_max=47.8, lat_min=45.65, squarify=False)

# Further tweak the look of things
mymap.add_background(which=None)
mymap.highlight_country()
mymap.add_borders()
mymap.add_gridlines()

# Add the stations
comb, inter = mymap.add_stations(stations, influence_radius=None,
                                 marker='D', edgecolor='w', facecolor='k',
                                 size=100, label='Some special stations')

# Link stations and compute the mean separation ...
mean_sep = mymap.link_neighbors(stations, color='k', thres=100)
# ... and add this info to the legend
mymap._legend_handles['mean_sep'] = mlines.Line2D(
    [], [], color='none', ls='-', label=f'Mean sep.: {mean_sep:.1f} km')

# Finish up ...
mymap.add_copyright()
mymap.add_legend()
mymap.savefig('custom_network_map2.png')
mymap.show()