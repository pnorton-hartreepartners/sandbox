import requests
import pandas as pd
import datetime as dt
import argparse
from constants import PROD, DEV, SETTLES, hosts


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env',
                        help='prod or dev',
                        choices=['prod', 'dev'],
                        required=True)
    return parser.parse_args()


def decorate_result(f):
    def decorated(*args, **kwargs):
        result = f(*args, **kwargs)
        if result.status_code != 200:
            print(result.text)
            #result.raise_for_status()
            return pd.DataFrame()
        return pd.DataFrame(result.json())
    return decorated


@decorate_result
def get_any_api(template_url, kwargs):
    url = template_url.format(**kwargs)
    print(f'\nurl is:\n{url}')
    return requests.get(url)


@decorate_result
def get_settles_w_status_ts(host, instrument_key, exchange, allow_indicative):
    url = f'{host}/settles/api/v1/getSettlementTS/{instrument_key}?exchange={exchange}&allow_indicative={allow_indicative}'
    return requests.get(url)


@decorate_result
def get_settles_ts(host, instrument_key, exchange):
    url = f'{host}/settles/api/v1/getSettlementTS/{instrument_key}?exchange={exchange}'
    return requests.get(url)


@decorate_result
def get_symbols(host, exchange):
    url = f'{host}/settles/api/v1/getSymbols/{exchange}'
    return requests.get(url)


def build_instrument_key(symbol, forward_date):
    forward_date_for_instrument_key = forward_date.strftime('%Y%m')
    blank_space = ' '
    return symbol + blank_space + forward_date_for_instrument_key


def build_symbol_df(host, exchange, symbol, forward_dates):
    dfs = pd.DataFrame()
    for forward_date in forward_dates:
        instrument_key = build_instrument_key(symbol=symbol,
                                              forward_date=forward_date)
        df = get_settles_ts(host=host,
                            instrument_key=instrument_key,
                            exchange=exchange)
        if not df.empty:
            df['symbol'] = symbol
            df['forward_date'] = forward_date
            dfs = pd.concat([dfs, df], axis='rows')
    if not dfs.empty:
        dfs = dfs[['symbol', 'date', 'forward_date', 'value']]
        dfs.sort_values(['symbol', 'date', 'forward_date', 'value'], inplace=True)
        dfs.rename(columns={'date': 'observation_date'}, inplace=True)
    return dfs


def build_from_curves_df(host, curves, start_date, periods):
    dfs = pd.DataFrame()
    for curve in curves:
        exchange, symbol = curve
        forward_dates = pd.date_range(start=start_date,
                                      periods=periods,
                                      freq='MS')
        df = build_symbol_df(host, exchange, symbol, forward_dates)
        dfs = pd.concat([dfs, df], axis='rows')
    return dfs


if __name__ == '__main__':
    '''
    >>>python mosaic_wapi.py -e dev
    '''

    template_url_dict = {
        # time series of all results for a single contract
        'getSettlementTS': r'{host}/settles/api/v1/getSettlementTS/{instrument_key}?exchange={exchange}&allow_indicative={allow_indicative}',

        # latest result for a single contract
        'getSettlement': r'{host}/settles/api/v1/getSettlement/{instrument_key}?exchange={exchange}&allow_indicative={allow_indicative}',

        # latest result for a collection of symbols on a given observation date
        'getFutureCurveSettlement': r'{host}/settles/api/v1/getFutureCurveSettlement/{symbols}/{exchange}/{stamp}?allow_indicative={allow_indicative}',

        # use regex to filter instruments and parse instrument name to contract month
        'getSettlementTSWithRegex': r'{host}/settles/api/v1/getSettlementTSWithRegex/{symbol}/{contract_regex}/{exchange}',
    }

    args = get_args()
    env = args.env
    host = hosts[SETTLES][env]

    template = template_url_dict['getSettlementTS']

    # example call data works for all apis so far
    kwargs = {'host': host,
              'instrument_key': 'CL 202012',
              'exchange': 'CME',
              'allow_indicative': 'true',
              'symbols': 'CL%2CHO',
              'stamp': '2021-09-14',
              'symbol': 'CL',
              'contract_regex': '2021SUMMER',
              }

    df = get_any_api(template_url=template, kwargs=kwargs)
    print(df)
    import pdb; pdb.set_trace()

    cme_european_naphtha_calendar_swap = ('CME', 'UN')
    ice_brent_1st_line_future = ('ICE', 'I')
    curves = [cme_european_naphtha_calendar_swap, ice_brent_1st_line_future]

    start_date = dt.date(2020, 10, 1)
    periods = 6

    df = build_from_curves_df(host, curves, start_date, periods)
    print()

    # exchange = 'ICE'
    # df = get_symbols(host=host, exchange=exchange)
    # print(df.head())
    # print()

    # instrument_key = 'JKM 202110'
    # exchange = 'ICE'
    # df = get_settles_ts(host=host, instrument_key=instrument_key, exchange=exchange)
    # print(df.head())
