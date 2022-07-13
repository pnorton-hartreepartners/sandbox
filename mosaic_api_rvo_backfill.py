from constants import URL_KWARGS, PARAMS_KWARGS, PROD, month_code_mapper, month_numbers
from mosaic_api_utils import prepare_inputs_for_api, get_any_api2
import pandas as pd

kwargs_dict = {
    'getTraderCurvesCatalog': {
        URL_KWARGS: {},
        PARAMS_KWARGS: {}
    },
    'getCurveTS': {
        URL_KWARGS: {'symbol': 'RVO_20',
                     'contract': '202103'}},
}

if __name__ == '__main__':

    env = PROD

    # ===========================================================
    # get the list of symbols
    api_name = 'getTraderCurvesCatalog'
    url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=kwargs_dict)
    response, content = get_any_api2(url, params)
    catalogue_df = pd.DataFrame(content)
    catalogue_df.sort_values(by='symbol', inplace=True)
    mask = catalogue_df['symbol'].str.startswith('RVO')
    rvo_symbols = catalogue_df.loc[mask, 'symbol'].values.tolist()

    # ===========================================================
    # build the contract labels for each symbol

    # year strings and month strings
    yyyys = ['20' + s[-2:] for s in rvo_symbols]
    mms = ['{:02d}'.format(m) for m in month_numbers]
    # we want the same year and three months of the next year
    same_year_contracts = [[y+m for m in mms] for y in yyyys]
    next_year_contracts = [[str(int(y) + 1) + m for m in mms[:3]] for y in yyyys]
    # join them together and relate to the symbol in a dict
    all_contracts = [same + next for (same, next) in zip(same_year_contracts, next_year_contracts)]
    all_contracts_dict = {symbol: contracts for (symbol, contracts) in zip(rvo_symbols, all_contracts)}

    # ===========================================================
    # call the api and get the stats

    api_name = 'getCurveTS'
    describe_dfs = []
    describe_columns = ['count', 'min', 'max']
    for symbol in rvo_symbols:
        kwargs_dict['getCurveTS'][URL_KWARGS]['symbol'] = symbol
        contracts = all_contracts_dict[symbol]
        for contract in contracts:
            kwargs_dict['getCurveTS'][URL_KWARGS]['contract'] = contract
            url, params, method = prepare_inputs_for_api(api_name, env, kwargs_dict=kwargs_dict)
            response, content = get_any_api2(url, params)
            if response.status_code == 200:
                contract = kwargs_dict[api_name][URL_KWARGS]['contract']
                df = pd.DataFrame(data=content)
                try:
                    describe_df = df.describe().T[describe_columns]
                except ValueError as v:
                    print(v)
                    describe_df = pd.DataFrame(data=[{key: 0 for key in describe_columns}])
            else:
                describe_df = pd.DataFrame(data=[{key: 0 for key in describe_columns}])

            describe_df.insert(loc=0, column='symbol', value=symbol)
            describe_df.insert(loc=1, column='contract', value=contract)
            describe_df.insert(loc=2, column='status_code', value=response.status_code)
            describe_df.set_index(keys=['symbol', 'contract'], inplace=True, drop=True)
            describe_dfs.append(describe_df)
    all_describe_df = pd.concat(describe_dfs)
    all_describe_df.to_clipboard()
    all_describe_df.to_excel(r'c:\temp\rvo_describe.xlsx', merge_cells=False)

    print()
