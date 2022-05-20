''' this is intended as a stand alone script to collect data from a non-charting api'''

from mosaic_api_utils import prepare_inputs_for_api, get_any_api
from constants import hosts, PROD, DEV, SETTLES, PORT, URL_KWARGS, PARAMS_KWARGS


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

if __name__ == '__main__':
    env = PROD
    api_name = 'getArgusQuoteTS'

    url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=example_kwargs_dict)
    result, df, status_code = get_any_api(url, params=params)
    df.to_clipboard()
    print(df.head())
    print()

