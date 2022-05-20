'''
this was to test a new get api with url params which is easier to build for analysts
'''
import json
from mosaic_api_examples import prepare_inputs_for_api, example_kwargs_dict
from constants import PROD, DEV
from mosaic_api_utils import get_any_api, post_any_api, process_new_chart_data, build_new_payload

api_name = 'getTraderCurveTS'
old_skool = True

if old_skool:
    env = PROD

    curves = [{'factor': 1, 'expression': 'BRT-F', 'contracts': ['202212']}]
    season = 0
    name = 'brent futs dec-22'
    chart_example = 'ebob_swap'  # any simple structure to use as a template then modify

    url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=example_kwargs_dict)

    with open('mosaic_chart_examples.json') as file:
        chart_examples = json.load(file)
    print(chart_examples.keys())
    payload = chart_examples[chart_example]

    modified_payload = build_new_payload(payload, curves, season, name)
    response_dict = post_any_api(url, payload=modified_payload)
    title, df = process_new_chart_data(response_dict)
    print(df.head())
    df.to_clipboard()

else:
    env = DEV
    url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=example_kwargs_dict)
    result, df, error = get_any_api(url, params)
    print(df.head())
    df.to_clipboard()
pass


