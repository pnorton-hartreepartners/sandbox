import requests
import pandas as pd
import datetime as dt
import argparse
from constants import hosts, URL_KWARGS, PARAMS_KWARGS, DEV, PROD
from mosaic_api_templates import api_config_dict


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env',
                        help='prod or dev',
                        choices=['prod', 'dev'],
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
            return result, pd.DataFrame(), result.status_code
        else:
            try:
                return result, pd.DataFrame(result.json()), None
            except Exception as e:
                return result, pd.DataFrame(), e
    return decorated


@decorate_result
def get_any_api(url, params):
    return requests.get(url, params=params)


def post_any_api(url, payload):
    result = requests.post(url, json=payload)
    return result.json()


def build_partial_url_kwargs(api_name, env=DEV):
    host_name = api_config_dict[api_name]['host']
    host_string = hosts[host_name][env]
    return {'host': host_string, 'api_name': api_name}


def build_url(template_url, kwargs):
    url = template_url.format(**kwargs)
    print(f'\nurl is:\n{url}')
    return url


def process_chart_data(response_dict, seasonality):
    if response_dict == {'detail': 'There was an error parsing the body'}:
        print('detail: There was an error parsing the body')
        pivot_df = None
    else:
        if not seasonality:
            all_df = process_nonseasonal_data(response_dict)
            pivot_df = all_df.pivot(index='time', columns='name')
            pivot_df.columns = pivot_df.columns.droplevel(level=None)
        else:  # it is a seasonality chart and already a pivot
            pivot_df = pd.DataFrame.from_dict(response_dict)
            pivot_df['time'] = pd.to_datetime(pivot_df['time'])
            pivot_df.set_index(keys=['time'], drop=True, inplace=True)
    return pivot_df


def process_nonseasonal_data(response_dict):
    all_df = pd.DataFrame()
    for chartlet in response_dict:
        df = pd.DataFrame.from_dict(chartlet['data'])
        df['name'] = chartlet['name']
        if chartlet['name'] != 'predicted':
            all_df = pd.concat([all_df, df], axis='index')
    all_df['time'] = pd.to_datetime(all_df['time'])
    return all_df


def build_instrument_key(symbol, forward_date):
    forward_date_for_instrument_key = forward_date.strftime('%Y%m')
    blank_space = ' '
    return symbol + blank_space + forward_date_for_instrument_key


def build_symbol_df(host, exchange, symbol, forward_dates):
    dfs = pd.DataFrame()
    for forward_date in forward_dates:
        instrument_key = build_instrument_key(symbol=symbol,
                                              forward_date=forward_date)
        url_template = api_config_dict['getSettlementTS']['url_template']
        kwargs = {'host': host, 'instrument_key': instrument_key, 'exchange': exchange}
        result, df, error = get_any_api(url_template, kwargs)
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


def build_list_of_expiries(symbol, start=None, end=None, periods=None, env=PROD):
    api_name = 'getExpiry'
    kwargs = {'start': start, 'end': end, 'periods': periods}
    months = pd.date_range(**kwargs, freq='MS')
    expiration_dates = {}
    for m in months:
        key = build_instrument_key(symbol, forward_date=m)
        template_url = api_config_dict[api_name]['url_template']
        url_kwargs = build_partial_url_kwargs(api_name, env=env)
        url_kwargs.update({'key': key})
        url = build_url(template_url=template_url, kwargs=url_kwargs)
        result, df, e = get_any_api(url=url, params=None)
        xx = result.json()
        expiration_dates.update({m: xx['ExpirationDate']})
    df = pd.DataFrame.from_dict(expiration_dates, orient='index')
    df.index.name = 'contract'
    df.columns = ['expiry_date']
    return df


if __name__ == '__main__':
    '''
    >>>python mosaic_wapi.py -e dev --api tsdb
    '''
    from mosaic_api_examples import kwargs_dict

    df = build_list_of_expiries(symbol='G', start='2021-10-01', periods=12)
    df.to_clipboard()

    args = get_args()
    env = args.env
    api_name = args.api

    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name, env=env)
    url_kwargs.update(kwargs_dict[api_name][URL_KWARGS])
    url = build_url(template_url=template_url, kwargs=url_kwargs)

    params = kwargs_dict[api_name][PARAMS_KWARGS]

    result, df, error = get_any_api(url=url, params=params)
    df.to_clipboard()
    print(df)

    cme_european_naphtha_calendar_swap = ('CME', 'UN')
    ice_brent_1st_line_future = ('ICE', 'I')
    curves = [cme_european_naphtha_calendar_swap, ice_brent_1st_line_future]

    start_date = dt.date(2020, 10, 1)
    periods = 6

    # df = build_from_curves_df(host, curves, start_date, periods)
    print()


