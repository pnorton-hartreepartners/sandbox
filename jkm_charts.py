import pandas as pd
import datetime as dt
from mosaic_wapi import SETTLES_API, get_settles_ts


def build_instruments_df(symbol, start, end=dt.date.today(), freq='MS', date_format='%Y%m'):
    data = pd.date_range(start=start, freq=freq, end=end)
    index = [symbol + ' ' + dt.datetime.strftime(d, date_format) for d in data]
    index = pd.Index(data=index, name='instrument_key')
    df = pd.DataFrame(data=data, index=index, columns=['forward_date'])
    df['symbol'] = symbol
    return df


def concat_df(dfs):
    return pd.concat(dfs, axis='rows')


def save_to_file(data_df, lookup_df, location):
    with pd.ExcelWriter(location) as writer:
        data_df.to_excel(writer, sheet_name='data', merge_cells=False)
        lookup_df.to_excel(writer, sheet_name='lookup')


if __name__ == '__main__':
    symbol = 'JKM'
    exchange = 'ICE'
    start_date = '01-09-2021'
    start_date = dt.datetime.strptime(start_date, '%d-%m-%Y')
    end_date = '01-01-2022'
    end_date = dt.datetime.strptime(end_date, '%d-%m-%Y')
    pathfile = r'c:\temp\charts.xlsx'

    instruments_df = build_instruments_df(symbol=symbol, start=start_date, end=end_date)
    instruments = instruments_df.index
    dfs = []
    for instrument in instruments:
        df = get_settles_ts(host=SETTLES_API, instrument_key=instrument, exchange=exchange)
        df['instrument_key'] = instrument
        df.rename(columns={'date': 'observation_date'}, inplace=True)
        dfs.append(df)
    df = concat_df(dfs)
    df.set_index(keys=['instrument_key', 'observation_date'], inplace=True, drop=True)
    save_to_file(data_df=df, lookup_df=instruments_df, location=pathfile)

