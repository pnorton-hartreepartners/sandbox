import json
from constants import URL_KWARGS, PARAMS_KWARGS, DEV
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
    }
}


def prepare_inputs_for_api(api_name, env):
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name, env=env)
    url_kwargs.update(example_kwargs_dict[api_name][URL_KWARGS])
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    params = example_kwargs_dict[api_name].get(PARAMS_KWARGS)
    method = api_config_dict[api_name].get('method', 'get')
    return url, params, method


if __name__ == '__main__':

    env = DEV

    key = 'getTraderCurveTS'
    example_kwargs_dict = {key: example_kwargs_dict[key]}
    with open('mosaic_chart_examples.json') as file:
        chart_examples = json.load(file)
    print(chart_examples.keys())
    payload = chart_examples['seasonality']

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
                seasonality = payload['seasonality']
                seasonality = seasonality > 0
                df = process_chart_data(result, seasonality)
                df.to_clipboard()
                df.plot(kind='line')
                pass
        else:
            raise NotImplementedError


