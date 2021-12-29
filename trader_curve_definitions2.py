import pandas as pd
from constants import DEV
from mosaic_api_templates import api_config_dict
from mosaic_wapi import build_url, get_any_api, build_partial_url_kwargs


def get_trader_curves_catalogue():
    api_name = 'getTraderCurvesCatalog'
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name)
    url = build_url(template_url=template_url, kwargs=url_kwargs)
    result, trader_curves_catalogue_df, error = get_any_api(url, params={})
    trader_curves_catalogue_df.set_index('symbol', drop=True, inplace=True)
    return trader_curves_catalogue_df


def get_trader_curve_definitions(trader_curves_catalogue_df, stamp):
    api_name = 'getTraderCurveDefinition'
    stamp_as_str = stamp.strftime('%Y-%m-%d')
    template_url = api_config_dict[api_name]['url_template']
    url_kwargs = build_partial_url_kwargs(api_name)
    url_kwargs.update({'source': 'hartree', 'stamp': stamp_as_str})

    trader_curves_definitions_dict = {}
    for symbol, row in trader_curves_catalogue_df.iterrows():
        print(symbol)
        url_kwargs['symbol'] = symbol
        url = build_url(template_url=template_url, kwargs=url_kwargs)
        result, trader_curve_definition_df, error = get_any_api(url, params={})
        trader_curves_definitions_dict[symbol] = trader_curve_definition_df
    return trader_curves_definitions_dict


def get_trader_curve_definitions_df(trader_curves_definitions_dict):
    trader_curves_definitions_df = pd.DataFrame()
    for symbol, df in trader_curves_definitions_dict.items():
        if not df.empty:
            trader_curves_definitions_df = pd.concat([trader_curves_definitions_df, df],
                                                     axis='index')

    # currently only one index and its unnamed
    trader_curves_definitions_df.index.name = 'attribute'
    # add symbol so now we have a multiindex
    trader_curves_definitions_df.set_index(keys=['symbol'], drop=True, append=True, inplace=True)
    # but order is wrong
    trader_curves_definitions_df.index = trader_curves_definitions_df.index.swaplevel('attribute', 'symbol')
    # finally
    trader_curves_definitions_df.sort_index(axis='index', inplace=True)
    return trader_curves_definitions_df


if __name__ == '__main__':
    '''
    join the catalogue w the definitions
    '''
    env = DEV
    stamp = pd.to_datetime('today')
    search_string = '-S'
    selection_flag = True

    # call the catalogue
    trader_curves_catalogue_df = get_trader_curves_catalogue()
    trader_curves_catalogue_df.sort_index(axis='index', inplace=True)
    print(trader_curves_catalogue_df)

    # select from the catalogue
    if selection_flag:
        mask = trader_curves_catalogue_df.index.str.contains(search_string)
        trader_curves_selection_df = trader_curves_catalogue_df[mask]
    else:
        trader_curves_selection_df = trader_curves_catalogue_df

    # get the definitions
    trader_curve_definitions_dict = get_trader_curve_definitions(trader_curves_selection_df, stamp)
    trader_curve_definitions_df = get_trader_curve_definitions_df(trader_curve_definitions_dict)

    # join them
    results_df = trader_curves_catalogue_df.merge(trader_curve_definitions_df, left_index=True, right_index=True)

    print(results_df)
    results_df.to_clipboard()
    pass