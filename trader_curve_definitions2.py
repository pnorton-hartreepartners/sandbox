import pandas as pd

from constants import DEV
from mosaic_api_templates import api_config_dict
from mosaic_wapi import build_url, get_any_api, build_partial_url_kwargs

if __name__ == '__main__':
    '''
    join the catalogue w the definitions
    '''
    env = DEV

    # call the catalogue
    api_name = 'getTraderCurvesCatalog'
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name)
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    result, trader_curves_catalogue_df, error = get_any_api(url, params={})
    trader_curves_catalogue_df.set_index('symbol', drop=True, inplace=True)
    print(trader_curves_catalogue_df)

    # call the definitions
    api_name = 'getTraderCurveDefinition'
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name)
    url_kwargs.update({'source': 'hartree', 'stamp': '2021-12-07'})

    results_df = pd.DataFrame(data=[], index=pd.Index([], name='symbol'))
    for symbol, row in trader_curves_catalogue_df.iterrows():
        print(symbol)
        url_kwargs['symbol'] = symbol
        url = build_url(template_url=template_url, kwargs=url_kwargs)
        result, trader_curves_definitions_df, error = get_any_api(url, params={})
        if not trader_curves_definitions_df.empty:
            definition = trader_curves_definitions_df.loc['type']['definition']
            print(definition)
            results_df.loc[symbol, 'definition'] = definition

    # join them
    results_df = trader_curves_catalogue_df.merge(results_df, left_index=True, right_index=True)

    
    print(results_df)
    results_df.to_clipboard()
    pass