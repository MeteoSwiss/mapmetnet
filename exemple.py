
import polars as pl
from mapmetnet.core import NetworkMapper

# Create a list of basic coordinates as polars DataFrame
# Pro tip - you can use wmoutils.query.query_oscar_surface() to get real station coordinates
sites = pl.DataFrame({
        'longitude': [3, 4, 5, 3],
        'latitude': [45, 46, 47, 48]
})

mymap = NetworkMapper(46.5, 4)
mymap._create_fig(figid=1)
mymap._set_map_extent(extent=5)
mymap._add_background(which=None)
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
