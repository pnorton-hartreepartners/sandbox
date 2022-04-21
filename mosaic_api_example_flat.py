''' this is intended as a stand alone script to collect data from a non-charting api'''
import json
import pandas as pd
import requests
import copy

PROD = 'prod'
DEV = 'dev'
SETTLES = 'settles'
PORT = 'port'
URL_KWARGS = 'url_kwargs'
PARAMS_KWARGS = 'params_kwargs'

hosts = {
    SETTLES:
        {
            PROD: 'http://settles-api.mosaic.hartreepartners.com/settles',
            DEV: 'http://settles-api.dev.mosaic.hartreepartners.com/settles',
            PORT: 123
        },
}

api_config_dict = {
    'getArgusQuoteTS': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{key}/{field}/{label}'},}

example_kwargs_dict = {
    'getArgusQuoteTS': {
        URL_KWARGS:
            {'key': 'PA0001010',
             'field': 'Midpoint',
             'label': 'Houston Close'
             },
        PARAMS_KWARGS: {}
    }
}


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


def build_url(template_url, kwargs):
    url = template_url.format(**kwargs)
    print(f'\nurl is:\n{url}')
    return url


def build_partial_url_kwargs(api_name, env=DEV):
    host_name = api_config_dict[api_name]['host']
    host_string = hosts[host_name][env]
    return {'host': host_string, 'api_name': api_name}


def prepare_inputs_for_api(api_name, env):
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name, env=env)
    url_kwargs.update(example_kwargs_dict[api_name][URL_KWARGS])
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    params = example_kwargs_dict[api_name].get(PARAMS_KWARGS)
    method = api_config_dict[api_name].get('method', 'get')
    return url, params, method


@decorate_result
def get_any_api(url, params):
    return requests.get(url, params=params)


if __name__ == '__main__':
    env = PROD
    api_name = 'getArgusQuoteTS'

    url, params, method = prepare_inputs_for_api(api_name, env)

    result, df, status_code = get_any_api(url, params=params)
    df.to_clipboard()
    print()

