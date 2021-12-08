'''
api doesnt support calling a list of symbols because filters use implicit logical AND
also cant just request all the data and then post-process because db server runs out of memory
so instead call one symbol at a time; yawn
'''
from constants import TSDB, hosts, URL_KWARGS, PARAMS_KWARGS, DEV, path, PROD
from mosaic_api_templates import api_config_dict
from mosaic_wapi import build_url
import os
import requests
import pandas as pd

SOURCE_KEY = 'sourcekey'
FILTERS = 'filters'
SINGLE_QUOTE = "'"
EQUALS_SIGN = '='

eia_weekly_dict = {
    URL_KWARGS:
        {'stage': 'raw',
         'source': 'eia_weekly'},
    PARAMS_KWARGS:
        {FILTERS: {SOURCE_KEY:
            ['WCRSTUS1',
            'WGTSTUS1',
            'W_EPOOXE_SAE_NUS_MBBL',
            'WKJSTUS1',
            'WDISTUS1',
            'WRESTUS1',
            'WPRSTUS1',
            'W_EPPO6_SAE_NUS_MBBL'
        ]}}
}


def build_kwargs_for_url():
    url_kwargs = eia_weekly_dict[URL_KWARGS]
    url_kwargs['host'] = host
    url_kwargs['api_name'] = api_name
    return url_kwargs


def build_params_list():
    source_keys = eia_weekly_dict[PARAMS_KWARGS][FILTERS][SOURCE_KEY]
    source_keys_as_filter = [f"{SOURCE_KEY}='{source_key}'" for source_key in source_keys]
    return [{FILTERS: source_key} for source_key in source_keys_as_filter]


def call_api_for_many_and_build_df(url, params_list):
    df = pd.DataFrame()
    for params in params_list:
        response = requests.get(url=url, params=params)
        new_df = pd.DataFrame(response.json())
        df = pd.concat([df, new_df], axis='rows')
    return df


if __name__ == '__main__':
    env = DEV
    api_name = TSDB
    host_name = TSDB
    host = hosts[host_name][env]

    # build url
    kwargs = build_kwargs_for_url()
    template_url = api_config_dict[api_name]['url_template']
    url = build_url(template_url, kwargs)

    # build params
    params_list = build_params_list()

    # build df for list of symbols
    df = call_api_for_many_and_build_df(url=url, params_list=params_list)

    # save as xls
    xlsx_for_fundamental_timeseries = 'fundamental_timeseries.xlsx'
    pathfile = os.path.join(path, xlsx_for_fundamental_timeseries)
    with pd.ExcelWriter(pathfile) as writer:
        df.to_excel(writer, sheet_name='timeseries')

    pivot_df = df.pivot(index='date', columns=SOURCE_KEY, values='value')
    print(pivot_df)
