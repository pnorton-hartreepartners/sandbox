import copy
import json

import pandas as pd
import requests

from constants import DEV, URL_KWARGS, PARAMS_KWARGS, hosts
from mosaic_api_templates import api_config_dict


def build_url(template_url, kwargs):
    url = template_url.format(**kwargs)
    print(f'\nurl is:\n{url}')
    return url


def build_partial_url_kwargs(api_name, env=DEV):
    host_name = api_config_dict[api_name]['host']
    host_string = hosts[host_name][env]
    return {'host': host_string, 'api_name': api_name}


def prepare_inputs_for_api(api_name, env, kwargs_dict):
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name, env=env)
    url_kwargs.update(kwargs_dict[api_name][URL_KWARGS])
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    params = kwargs_dict[api_name].get(PARAMS_KWARGS)
    method = api_config_dict[api_name].get('method', 'get')
    return url, params, method


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


def post_any_api(url, payload):
    try:
        response = requests.post(url, json=payload, verify=False)
        content = json.loads(response.content.decode())
        print(response.status_code)
    except Exception as e:
        print(f'error: {e}')
        content = {}
    return content


@decorate_result
def get_any_api(url, params):
    return requests.get(url, params=params)


# yeah i know, i think i just wanted to write a decorator
def get_any_api2(url, params):
    try:
        response = requests.get(url, params=params)
        content = json.loads(response.content.decode())
        print(response.status_code)
    except Exception as e:
        print(f'error: {e}')
        content = {}
    return response, content


def process_new_chart_data(response_dict):
    if response_dict == {'detail': 'There was an error parsing the body'}:
        print(response_dict)
        title = ''
        df = pd.DataFrame()
    else:
        title = response_dict['title']
        df = response_dict['dataframe']
        df = pd.DataFrame(df)
    return title, df


def build_new_payload(payload, curves, season, name):
    new_payload = copy.deepcopy(payload)

    new_payload['chartlets'][0]['curves'] = curves
    new_payload['chartlets'][0]['name'] = name
    new_payload['seasonality'] = season

    return new_payload
