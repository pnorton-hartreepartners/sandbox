from constants import TSDB, hosts, URL_KWARGS, PARAMS_KWARGS, DEV, PROD
from mosaic_api_templates import template_url_dict
from mosaic_wapi import build_url
import requests
import pandas as pd

SOURCE_KEY = 'sourcekey'

eia_weekly_dict = {
    URL_KWARGS:
        {'stage': 'raw',
         'source': 'eia_weekly'},
    PARAMS_KWARGS:
        {'filters': {'sourcekey':
            ['WCRSTUS1',
            'WGTSTUS1',
            # 'W_EPOOXE_SAE_NUS_MBBL',
            # 'WKJSTUS1',
            # 'WDISTUS1',
            # 'WRESTUS1',
            # 'WPRSTUS1',
            # 'W_EPPO6_SAE_NUS_MBBL'
        ]}}
}


def build_params(kwargs):
    SINGLE_QUOTE = '%27'
    EQUALS_SIGN = '='
    FILTERS = 'filters'
    sourcekeys = kwargs['filters'][SOURCE_KEY]
    param_as_strings = []
    for sourcekey in sourcekeys:
        param_as_strings.append(SOURCE_KEY + EQUALS_SIGN + SINGLE_QUOTE + sourcekey + SINGLE_QUOTE)
    params_as_string = '&'.join(param_as_strings)
    params = {'filters': params_as_string}
    params_as_string = '='.join([FILTERS, params_as_string])
    return params, params_as_string


if __name__ == '__main__':
    env = DEV
    api_name = TSDB
    host_name = TSDB
    host = hosts[host_name][env]

    template_url = template_url_dict[api_name]
    url_kwargs = eia_weekly_dict[URL_KWARGS]
    url_kwargs['host'] = host
    url_kwargs['api_name'] = api_name
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    params, params_as_string = build_params(eia_weekly_dict[PARAMS_KWARGS])

    extended_url = '?'.join([url, params_as_string])
    response = requests.get(url=extended_url)
    df = pd.DataFrame(response.json())
    pivot_df = df.pivot(index='date', columns=SOURCE_KEY, values='value')
    print(pivot_df)
