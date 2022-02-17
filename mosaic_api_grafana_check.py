'''
cd \dev\code\sandbox
activate mosaic2
python mosaic_api_grafana_check.py

looking for a happy result like this
==========
all api calls succeeded: True
'''

import json
import pandas as pd
from constants import PROD, DEV
from mosaic_api_examples import prepare_inputs_for_api, example_kwargs_dict
from mosaic_wapi import get_any_api, post_any_api

grafana_api_names = ['getTraderCurvesCatalog',
                     'getTraderCurveTS',
                     'getMatchingTraderCurves']

with open('mosaic_chart_examples.json') as file:
    chart_examples = json.load(file)
payload = chart_examples['seasonality']  # seasonality  platts

failure = False
for api_name in grafana_api_names:
    url, params, method = prepare_inputs_for_api(api_name, env=PROD)

    if method == 'get':
        result, df1, error = get_any_api(url, params)
        print('\n==========\n', api_name, '\n\n', result, '\n\n', df1.head(), '\n\n==========\n')
        if not(result.status_code == 200 and not df1.empty and not error):
            failure = True
    elif method == 'post' and api_name == 'getTraderCurveTS':
        result = post_any_api(url, payload=payload)
        if not(len(result) > 0):
            failure = True
        df2 = pd.DataFrame(result)
        print('\n==========\n', api_name, '\n\n', df2.head(), '\n\n==========\n')
    print('\n==========\n==========', f'\nall api calls succeeded: {not failure}')
