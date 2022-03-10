import json
import pandas as pd
from constants import URL_KWARGS, PARAMS_KWARGS, DEV, PROD
from mosaic_api_templates import api_config_dict
from mosaic_wapi import build_url, get_any_api, build_partial_url_kwargs, post_any_api, process_chart_data

example_kwargs_dict = {
    'getFutureCurveSettlement': {
        URL_KWARGS:
            {'exchange': 'CME',
             'symbols': 'CL%2CHO',
             'stamp': '2021-09-14', },
        PARAMS_KWARGS:
            {'allow_indicative': 'true'}
    },
    'getVolSurface': {
        URL_KWARGS:
            {'symbol': 'ZN',
             'exchange': 'LME',
             'stamp': '2021-10-12'},
        PARAMS_KWARGS:
            {'allow_cached_vols': 'true'}
    },
    'tsdb': {
        URL_KWARGS:
            {'stage': 'raw',
             'source': 'eia_weekly'},
        PARAMS_KWARGS:
            {'filters': "sourcekey='WTTSTUS1'"}  # need single quotes
    },
    'getTraderCurvesCatalog': {
        URL_KWARGS:
            {},
        PARAMS_KWARGS:
            {}
    },
    'getTraderCurveDefinition': {
        URL_KWARGS:
            {'symbol': 'HO-GO-S',
             'source': 'hartree',
             'stamp': '2021-12-07'
             },
        PARAMS_KWARGS:
            {}
    },
    'getTraderCurveTS': {
        URL_KWARGS: {},
    },
    'getMatchingTraderCurves': {
        URL_KWARGS: {},
        PARAMS_KWARGS: {'search_string': 'BRT-F'}
    },
    'getEtrmCurveEval': {
        URL_KWARGS:
            {'symbol': 'RVO_22',
             'stamp': '2022-02-21'
             },
        PARAMS_KWARGS: {}
    }
}

xls_data_filepath = r'c:\temp\getTraderCurveTS.xlsx'
pkl_data_filepath = r'c:\temp\getTraderCurveTS.pkl'


def prepare_inputs_for_api(api_name, env):
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name, env=env)
    url_kwargs.update(example_kwargs_dict[api_name][URL_KWARGS])
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    params = example_kwargs_dict[api_name].get(PARAMS_KWARGS)
    method = api_config_dict[api_name].get('method', 'get')
    return url, params, method


if __name__ == '__main__':

    env = PROD
    key = 'getTraderCurveTS'
    chart_example = 'brooksbohn'

    example_kwargs_dict = {key: example_kwargs_dict[key]}
    with open('mosaic_chart_examples.json') as file:
        chart_examples = json.load(file)
    print(chart_examples.keys())
    payload = chart_examples[chart_example]

    for api_name in example_kwargs_dict:
        url, params, method = prepare_inputs_for_api(api_name, env)

        if method == 'get':
            result, df, error = get_any_api(url, params)
            print(error)
            print(df)
            df.to_clipboard()
        elif method == 'post':
            result = post_any_api(url, payload=payload)
            if api_name == 'getTraderCurveTS':
                seasonality = payload['seasonality'] > 0
                df = process_chart_data(result, seasonality)
                df.plot(kind='line')
        else:
            raise NotImplementedError

        with pd.ExcelWriter(xls_data_filepath, mode='w') as f:
            df.to_excel(excel_writer=f, sheet_name=api_name, index=True)

        df.to_pickle(pkl_data_filepath)

