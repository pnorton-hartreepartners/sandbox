import json
import pandas as pd
import requests
import copy
from constants import PROD, DEV
from mosaic_api_examples import prepare_inputs_for_api


def post_any_api(url, payload):
    try:
        result = requests.post(url, json=payload, verify=False)
        df = pd.read_json(result.content)
    except Exception as e:
        print(e)
        df = pd.DataFrame()
    return df


def build_new_payload(payload, symbol, contract, season):
    new_payload = copy.deepcopy(payload)

    new_payload['chartlets'][0]['curves'][0]['expression'] = symbol
    new_payload['chartlets'][0]['curves'][0]['contracts'] = [contract]
    new_payload['chartlets'][0]['name'] = symbol + ' | ' + contract
    new_payload['seasonality'] = season

    return new_payload


if __name__ == '__main__':
    env = DEV
    api_name = 'getTraderCurveTS'

    symbol = 'BRT-F'
    contract = '202210'
    season = 0

    url, params, method = prepare_inputs_for_api(api_name, env)

    with open('mosaic_chart_examples.json') as file:
        chart_examples = json.load(file)
    payload = chart_examples['seasonality']

    modified_payload = build_new_payload(payload, symbol, contract, season)
    df = post_any_api(url, payload=modified_payload)
    df.to_clipboard()

