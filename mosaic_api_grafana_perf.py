import json
import time
import pandas as pd
import requests
import copy
from constants import PROD, DEV
from mosaic_api_examples import prepare_inputs_for_api

filepath = r'c:\temp\charting_performance_results.xlsx'


symbol_stems = ['BRT-', 'GO-', 'RB-']
contract_types = ['F', 'S']
contract_periods = [
    {'template': '2022{period}',
     'count': 12,
     'strf': '{:02d}',
     'complexity': 1},
    {'template': '2022Q{period}',
     'count': 4,
     'strf': '{:01d}',
     'complexity': 3}]
contract_type_complexity = {'F': 1, 'S': 2}

seasons = range(0, 11, 2)


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r]' % (f.__name__, args, kw))
        print('took: %2.4f sec' % (te-ts))
        return result
    return timed


def post_any_api(url, payload):
    ts = time.time()
    try:
        result = requests.post(url, json=payload, verify=False)
        result = result.json()
    except Exception as e:
        print(e)
        print(payload, '\n')
        result = 'error'
    te = time.time()
    return result, te-ts


def modify_payload(payload):
    payloads = []
    for symbol_stem, contract_type, contract_period, season in ((symbol_stem, contract_type, contract_period, season)
                               for symbol_stem in symbol_stems
                               for contract_type in contract_types
                               for contract_period in contract_periods
                               for season in list(seasons)):

        expression = symbol_stem + contract_type
        for period in range(1, contract_period['count'] + 1):
            new_payload = copy.deepcopy(payload)

            template = contract_period['template']
            strf = contract_period['strf']
            contract = template.format(period=strf.format(period))

            new_payload['chartlets'][0]['curves'][0]['expression'] = expression
            new_payload['chartlets'][0]['curves'][0]['contracts'] = [contract]
            new_payload['chartlets'][0]['name'] = expression + ' | ' + contract
            new_payload['seasonality'] = season

            # future/swap * month/quarter * seasons
            complexity_score = contract_type_complexity[contract_type] * contract_period['complexity'] * (season + 1)

            payloads.append([new_payload, complexity_score])

            print(expression, contract, period, season)
    return payloads


if __name__ == '__main__':
    env = PROD
    api_name = 'getTraderCurveTS'

    url, params, method = prepare_inputs_for_api(api_name, env)

    with open('mosaic_chart_examples.json') as file:
        chart_examples = json.load(file)
    payload = chart_examples['seasonality']

    modified_payloads = modify_payload(payload)
    # modified_payloads = [modified_payloads[-1]]

    all_df = pd.DataFrame()
    for payload, complexity_score in modified_payloads:
        result, elapsed_time = post_any_api(url, payload=payload)

        expression = payload['chartlets'][0]['curves'][0]['expression']
        [contract] = payload['chartlets'][0]['curves'][0]['contracts']
        seasonality = payload['seasonality']

        row = {'expression': expression,
               'contract': contract,
               'seasonality': seasonality,
               'elapsed_time': elapsed_time,
               'complexity_score': complexity_score
               }

        df = pd.DataFrame(data=row, index=[0])
        print(df)
        all_df = pd.concat([all_df, df], axis='index')
    all_df.reset_index(inplace=True)
    all_df.to_clipboard()

    with pd.ExcelWriter(filepath) as writer:
        all_df.to_excel(writer, sheet_name='results')

    pass
    print()





