# Option 1: using a WIGOS ID
from mapmetnet.site import WigosSite
mysite = WigosSite('0-20000-0-06610')

# Option 2: using latitude and longitude
#from mapmetnet.site import Site
#mysite = Site(lat=+46.811578, lon=+6.942472, name='My secret site')

# Either way, trigger the diagram using:
mysite.site_view(show_ref_circles=True, save_fn=None, show=True)