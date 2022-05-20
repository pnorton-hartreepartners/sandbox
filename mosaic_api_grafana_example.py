''' this is intended as a stand alone script to collect data from the charting api'''
from mosaic_api_examples import example_kwargs_dict
from mosaic_api_utils import post_any_api, prepare_inputs_for_api, process_new_chart_data, build_new_payload
from constants import PROD

chart_examples = {"seasonality": {
    "start_date": "2015-01-01",
    "end_date": "2024-01-01",
    "seasonality": 3,
    "chartlets": [
        {
            "name": "BRT-F | 202212",
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

if __name__ == '__main__':
    env = PROD
    api_name = 'getTraderCurveTS'

    curves = [{'factor': 1, 'expression': 'BRT-F', 'contracts': ['2022Q4']},
              {'factor': -1, 'expression': 'WTI-F', 'contracts': ['2022Q4']},]
    curves = [{'factor': 1, 'expression': 'BRT-F', 'contracts': ['202212']}]

    season = 3
    name = 'brent futs dec-22'

    url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=example_kwargs_dict)
    payload = chart_examples['seasonality']

    modified_payload = build_new_payload(payload, curves, season, name)
    response_dict = post_any_api(url, payload=modified_payload)
    title, df = process_new_chart_data(response_dict)
    df.to_clipboard()
    print(df.head())
    print()

