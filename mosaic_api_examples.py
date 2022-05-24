import json
import pandas as pd
from constants import URL_KWARGS, PARAMS_KWARGS, DEV, PROD
from mosaic_api_utils import prepare_inputs_for_api, post_any_api, process_new_chart_data
from mosaic_wapi import get_any_api

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
    'getSettlementTS': {
        URL_KWARGS: {'instrument_key': 'B 202206'},
        PARAMS_KWARGS: {'exchange': 'ICE',
                        'allow_indicative': False}
    },
    # old POST version
    'getTraderCurveTS': {
        URL_KWARGS: {},
    },
    # new GET version
    # 'getTraderCurveTS': {
    #     URL_KWARGS: {'symbol': 'BRT-F',
    #                  'contract': '202212'}},
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
    },
    'getMatchingArgusCodes': {
        URL_KWARGS: {'symbol': 'naphtha'},
        PARAMS_KWARGS: {}
    },
    'getArgusQuotes': {
        URL_KWARGS: {'symbol': 'naphtha'},
        PARAMS_KWARGS: {}
    },
    'getArgusQuoteTS': {
        URL_KWARGS:
            {'key': 'PA0001010',
             'field': 'Midpoint',
             'label': 'Houston Close'
             },
        PARAMS_KWARGS: {}
    },
    'getExpiry': {
        URL_KWARGS:
            {'key': 'CL 202012',
             },
        PARAMS_KWARGS: {'exchange': 'CME'}
    },
    'getHolidaysForCalendar': {
        URL_KWARGS:
            {},
        PARAMS_KWARGS: {'calendar': 'ICE'}
    }
}

xls_data_filepath = r'c:\temp\getTraderCurveTS.xlsx'
pkl_data_filepath = r'c:\temp\getTraderCurveTS.pkl'

if __name__ == '__main__':

    env = PROD
    key = 'getSettlementTS'
    key = 'getArgusQuoteTS'
    key = 'getTraderCurveTS'
    chart_example = 'seasonality'

    if key == 'getTraderCurveTS':
        with open('mosaic_chart_examples.json') as file:
            chart_examples = json.load(file)
        print(chart_examples.keys())
        payload = chart_examples[chart_example]
    else:
        payload = None

    example_kwargs_dict = {key: example_kwargs_dict[key]}
    for api_name in example_kwargs_dict:
        url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=example_kwargs_dict)

        if method == 'get':
            result, df, error = get_any_api(url, params)
            print(error)
            print(df)
            df.to_clipboard()
        elif method == 'post':
            result = post_any_api(url, payload=payload)
            if api_name == 'getTraderCurveTS':
                seasonality = payload['seasonality'] > 0
                title, df = process_new_chart_data(result)
                df.plot(kind='line')
        else:
            raise NotImplementedError

        with pd.ExcelWriter(xls_data_filepath, mode='w') as f:
            df.to_excel(excel_writer=f, sheet_name=api_name, index=True)

        df.to_pickle(pkl_data_filepath)

