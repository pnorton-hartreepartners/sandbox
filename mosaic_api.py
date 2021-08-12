import os
from settles_api import static as st
from settles_api import prices as pr

os.environ['CRATE_HOST'] = 'ttda.storage.mosaic.hartreepartners.com:4200'

df = pr.get_settlement_ts(key='B 202012', exchange='ICE')
print(df.head())
