import requests
import pandas as pd
import datetime as dt
import argparse
from constants import SETTLES, TSDB, hosts, URL_KWARGS, PARAMS_KWARGS
from mosaic_api_templates import template_url_dict

# example call data works by api
kwargs_dict = {
    'getFutureCurveSettlement': {
        URL_KWARGS:
            {'exchange': 'CME',
             'symbols': 'CL%2CHO',
             'stamp': '2021-09-14', },
        PARAMS_KWARGS:
            {'allow_indicative': 'true'}
    },
    'getVolSurface': {
        URL_KWARGS:
            {'symbol': 'ZN',
             'exchange': 'LME',
             'stamp': '2021-10-12'},
        PARAMS_KWARGS:
            {'allow_cached_vols': 'true'}
    },
    'tsdb': {
        URL_KWARGS:
            {'stage': 'raw',
             'source': 'eia_weekly'},
        PARAMS_KWARGS:
            {'filters': "sourcekey='WTTSTUS1'"}  # need single quotes
    },
    'getTraderCurvesCatalog': {
        URL_KWARGS:
            {},
        PARAMS_KWARGS:
            {}
    },
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env',
                        help='prod or dev',
                        choices=['prod', 'dev'],
                        required=True)
    parser.add_argument('--host',
                        help='settles or tsdb',
                        choices=['settles', 'tsdb'],
                        required=True)
    parser.add_argument('-a', '--api',
                        help='name of the api',
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
def get_any_api(url, params):
    return requests.get(url, params=params)


def build_url(template_url, kwargs):
    url = template_url.format(**kwargs)
    print(f'\nurl is:\n{url}')
    return url


def build_instrument_key(symbol, forward_date):
    forward_date_for_instrument_key = forward_date.strftime('%Y%m')
    blank_space = ' '
    return symbol + blank_space + forward_date_for_instrument_key


def build_symbol_df(host, exchange, symbol, forward_dates):
    dfs = pd.DataFrame()
    for forward_date in forward_dates:
        instrument_key = build_instrument_key(symbol=symbol,
                                              forward_date=forward_date)
        template_url = template_url_dict['getSettlementTS']
        kwargs = {'host': host, 'instrument_key': instrument_key, 'exchange': exchange}
        df = get_any_api(template_url, kwargs)
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
    >>>python mosaic_wapi.py -e dev --host tsdb --api tsdb
    '''

    args = get_args()
    env = args.env
    api_name = args.api
    host_name = args.host
    host = hosts[host_name][env]

    template_url = template_url_dict[api_name]
    url_kwargs = kwargs_dict[api_name][URL_KWARGS]
    url_kwargs['host'] = host
    url_kwargs['api_name'] = api_name
    url = build_url(template_url=template_url, kwargs=url_kwargs)

    params = kwargs_dict[api_name][PARAMS_KWARGS]
    # to chain them; something like this
    # params = {'filters': [f'{k}={v} for k, v in filters.items()]}

    df = get_any_api(url=url, params=params)
    print(df)

    cme_european_naphtha_calendar_swap = ('CME', 'UN')
    ice_brent_1st_line_future = ('ICE', 'I')
    curves = [cme_european_naphtha_calendar_swap, ice_brent_1st_line_future]

    start_date = dt.date(2020, 10, 1)
    periods = 6

    # df = build_from_curves_df(host, curves, start_date, periods)
    print()

