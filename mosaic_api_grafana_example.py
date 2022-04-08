''' this is intended as a stand alone script to collect data from the charting api'''
import json
import pandas as pd
import requests
import copy

PROD = 'prod'
DEV = 'dev'
CHARTING = 'charting'

hosts = {
    CHARTING:
        {
            PROD: 'https://charting-api.mosaic.hartreepartners.com',
            DEV: 'https://charting-api.dev.mosaic.hartreepartners.com',
        }
}

api_config_dict = {
    # trader curve time-series backed by tempest for history used for charting
    'getTraderCurveTS': {'host': CHARTING,
                         'url_template': r'{host}/api/v1/{api_name}'}, }

chart_examples = {"seasonality": {
    "start_date": "2015-01-01",
    "end_date": "2024-01-01",
    "seasonality": 3,
    "chartlets": [
        {
            "name": "BRT-F | 202202",
            "curves": [
                {
                    "expression": "BRT-F",
                    "factor": 1,
                    "type": "Dynamic",
                    "contracts": [
                        "202201"
                    ]
                }
            ],
            "currency": "USD",
            "uom": "*",
            "axis": 0
        }
    ]
},}


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
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    return url


def post_any_api(url, payload):
    try:
        result = requests.post(url, json=payload, verify=False)
        df = pd.read_json(result.content)
    except Exception as e:
        print(f'error: {e}')
        df = pd.DataFrame()
    print(result.status_code)
    return df


def build_new_payload(payload, curves, season, name):
    new_payload = copy.deepcopy(payload)

    new_payload['chartlets'][0]['curves'] = curves
    new_payload['chartlets'][0]['name'] = name
    new_payload['seasonality'] = season

    return new_payload


if __name__ == '__main__':
    env = PROD
    api_name = 'getTraderCurveTS'

    curves = [{'factor': 1, 'expression': 'BRT-F', 'contracts': ['2022Q4']},
              {'factor': -1, 'expression': 'WTI-F', 'contracts': ['2022Q4']},]

    season = 3
    name = 'brent-wti swaps q4'

    url = prepare_inputs_for_api(api_name, env)
    payload = chart_examples['seasonality']

    modified_payload = build_new_payload(payload, curves, season, name)
    df = post_any_api(url, payload=modified_payload)
    df.to_clipboard()
    print()

