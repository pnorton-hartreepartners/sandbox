import json
import pandas as pd
from constants import PROD
from mosaic_api_examples import prepare_inputs_for_api, example_kwargs_dict
from mosaic_wapi import get_any_api, post_any_api

grafana_api_names = ['getTraderCurvesCatalog',
                     'getTraderCurveTS',
                     'getMatchingTraderCurves']

with open('mosaic_chart_examples.json') as file:
    chart_examples = json.load(file)
payload = chart_examples['platts']

for api_name in grafana_api_names:
    url, params, method = prepare_inputs_for_api(api_name, env=PROD)

    if method == 'get':
        result, df, error = get_any_api(url, params)
        print('\n==========\n', api_name, '\n\n', result, '\n\n', df.head(), '\n\n==========\n')
    elif method == 'post' and api_name == 'getTraderCurveTS':
        result = post_any_api(url, payload=payload)
        print('\n==========\n', api_name, '\n\n', pd.DataFrame(result).head(), '\n\n==========\n')
