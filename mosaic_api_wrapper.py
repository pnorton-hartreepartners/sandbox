import datetime as dt
import os

os.environ['MOSAIC_ENV'] = 'PROD'
from mosaic_api_client.settles_api import SettlesApi as SA
from mosaic_api_client.trader_curves_api import TraderCurvesApi as TCA
import time


observation_date = dt.date.fromisoformat('2022-05-18')
source = 'hartree'

df = SA.get_future_curve_settlement(symbols=['B', 'TTF'], exchange='ICE', stamp=observation_date)
print(df)

s = time.time()
yy = TCA.get_eod_trader_curve_eval(symbol='BRT-F', stamp=observation_date, source=source, allow_indicative=False)
f = time.time()
print(yy)
print(f - s)
print()
