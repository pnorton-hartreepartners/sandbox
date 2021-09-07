import datetime as dt
from mosaic_wapi import build_from_curves_df, SETTLES_API


if __name__ == '__main__':
    host = SETTLES_API

    cme_fuel_oil_crack_spread = ('CME', 'FO')
    ice_fuel_oil_crack_spread = ('ICE', 'BOA')
    cme_fuel_oil = ('CME', 'UV')
    ice_brent = ('ICE', 'B')

    curves = [ice_fuel_oil_crack_spread, ice_brent]

    start_date = dt.date(2021, 10, 1)
    periods = 1

    df = build_from_curves_df(host, curves, start_date, periods)
    print(df.head())
    print()

