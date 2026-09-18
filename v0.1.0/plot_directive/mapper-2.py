import polars as pl
from mapmetnet.mapper import NetworkMapper

# Create a list of station coordinates as a polars DataFrame
stations = pl.DataFrame({
    'longitude': [6.943021, 0.943021, 12.943021, 6.943021, 6.943021],
    'latitude': [46.812724, 46.812724, 46.812724, 44.812724, 51.812724]
})

# Setup the map ... for this use case we need nothing more than the NetworkMapper class
mymap = NetworkMapper(lat=46.80111, lon=8.22667, extent=20)
mymap.create_fig(figid=1)
mymap.set_map_lims(squarify=True)

# Further tweak the look of things
mymap.add_background(which=None)
mymap.add_borders()
mymap.add_gridlines()

# Add the stations
comb, inter = mymap.add_stations(stations, influence_radius=None,
                                 marker='D', edgecolor='w', facecolor='k',
                                 size=100, label='Some special stations')

# Connect the stations
_ = mymap.link_neighbors(stations, color='k', thres=None)

# Finish up ...
mymap.add_copyright()
mymap.add_legend()
mymap.savefig('custom_network_map1.png')
mymap.show()