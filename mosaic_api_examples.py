import json
import pandas as pd
from constants import URL_KWARGS, PARAMS_KWARGS, DEV, PROD
from mosaic_api_utils import prepare_inputs_for_api, post_any_api, process_new_chart_data, get_any_api2
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
    'getCurveTS': {
        URL_KWARGS: {'symbol': 'TC5_USDMT',
                     'contract': '202108'}},
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
        URL_KWARGS: {'key': 'CL 202207'},
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


list_of_dicts1 = [{'getCurveTS': {
    URL_KWARGS: {'symbol': 'WTI-S',
                 'contract': '202201'}},},
{'getCurveTS': {
    URL_KWARGS: {'symbol': 'WTI-S',
                 'contract': '202202'}},},
{'getCurveTS': {
    URL_KWARGS: {'symbol': 'WTI-S',
                 'contract': '202203'}},},
{'getCurveTS': {
    URL_KWARGS: {'symbol': 'WTI-S',
                 'contract': '2023Q1'}},},
]

list_of_dicts2 = [
    {'getCurveTS': {
    URL_KWARGS: {'symbol': 'WTI-F',
                 'contract': '1NB'}},},
    {'getCurveTS': {
        URL_KWARGS: {'symbol': 'WTI-F',
                     'contract': '2NB'}},},
    {'getCurveTS': {
        URL_KWARGS: {'symbol': 'WTI-F',
                     'contract': 'SPOT'}},}
]


if __name__ == '__main__':

    env = PROD
    key = 'getSettlementTS'
    key = 'getArgusQuoteTS'
    key = 'getTraderCurveTS'
    key = 'getExpiry'
    key = 'getCurveTS'
    key = 'getTraderCurvesCatalog'
    list_of_dicts = list_of_dicts1
    list_of_dicts = None
    chart_example = 'seasonality'

    if key == 'getTraderCurveTS':
        with open('mosaic_chart_examples.json') as file:
            chart_examples = json.load(file)
        print(chart_examples.keys())
        payload = chart_examples[chart_example]
        payload['start_date'] = '2000-01-01'
        payload['seasonality'] = 21
    else:
        payload = None

    if list_of_dicts:
        example_kwargs_dict = {key: example_kwargs_dict[key]}
        list_of_dfs = []
        for example_kwargs_dict in list_of_dicts:
            for api_name in example_kwargs_dict:
                url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=example_kwargs_dict)

                if method == 'get':
                    result, df, error = get_any_api(url, params)
                    print(error)
                    print(df)
                    list_of_dfs.append(df)
                    df.to_clipboard()
                elif method == 'post':
                    result = post_any_api(url, payload=payload)
                    if api_name == 'getTraderCurveTS':
                        seasonality = payload['seasonality'] > 0
                        title, df = process_new_chart_data(result)
                        df.plot(kind='line')
                else:
                    raise NotImplementedError

        for df in list_of_dfs:
            df.set_index(keys='date', drop=True, inplace=True)

        columns = [x['getCurveTS'][URL_KWARGS]['symbol'] + ' | ' + x['getCurveTS'][URL_KWARGS]['contract'] for x in list_of_dicts]
        df2 = pd.concat(list_of_dfs, axis='columns')
        df2.columns = columns
        df2.to_clipboard()
    else:
        api_name = key
        url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=example_kwargs_dict)
        response, content = get_any_api2(url, params)
        kwargs = example_kwargs_dict[api_name][URL_KWARGS]
        print(kwargs['key'])
        print(content)
        print()


    with pd.ExcelWriter(xls_data_filepath, mode='w') as f:
        df.to_excel(excel_writer=f, sheet_name=api_name, index=True)

    df.to_pickle(pkl_data_filepath)

'''
hack

for df in list_of_dfs:
    df.set_index(keys='date', drop=True, inplace=True)

df2 = pd.concat(list_of_dfs, axis='columns')
df2.to_clipboard()


'''