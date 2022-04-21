import os
# import analyst_data_views

os.environ['CRATE_HOST'] = 'ttda.storage.mosaic.hartreepartners.com:4200'
#os.environ['CRATE_HOST'] = 'ttda.cratedb-dev-cluster.mosaic.hartreepartners.com:4200'

from analyst_data_views.common.db_flattener import getFlatMappedDF
from analyst_data_views.common.converter import addUnits
from analyst_data_views.common.db_flattener import getFlatRawDF

source = "iea-mods"
raw_data = getFlatRawDF(source)
df = raw_data[raw_data['FILE'] == 'iea-mods-summary'].sort_values('date', ascending=False)
print(df)
pass


