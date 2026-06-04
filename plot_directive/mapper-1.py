from mapmetnet.mapper import GBONMapper

che_map = GBONMapper('CHE', mrgid=None)
che_map.generate_map(figid=1,
                     pad_frac=0.025,
                     station_type='surface',
                     var_name='temperature',
                     interval='daily',
                     category='availability',
                     date='2026-04-13',
                     high_density=True,
                     show_influence_area=False,
                     show=True)