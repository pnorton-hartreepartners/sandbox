import os
from analyst_data_views.common.db_flattener import getFlatRawDF

os.environ['CRATE_HOST'] = 'ttda.storage.mosaic.hartreepartners.com:4200'
df = getFlatRawDF(source='eia-weekly')
