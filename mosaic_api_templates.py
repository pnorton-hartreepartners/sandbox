
MOSAIC_OPTION_VALUATION_API = 'getOptionPricesFromVolCurves'
MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API = 'getLMEForwardCurveSettlement'

template_url_dict = {
    # time series of all results for a single contract
    'getSettlementTS': r'{host}/api/v1/{api_name}/{instrument_key}',
    # exchange={exchange}&allow_indicative={allow_indicative}',

    # latest result for a single contract
    'getSettlement': r'{host}/api/v1/{api_name}/{instrument_key}',
    # ?exchange={exchange}&allow_indicative={allow_indicative}',

    # latest result for a collection of symbols on a given observation date
    'getFutureCurveSettlement': r'{host}/api/v1/{api_name}/{symbols}/{exchange}/{stamp}',

    # use regex to filter instruments and parse instrument name to contract month
    'getSettlementTSWithRegex': r'{host}/api/v1/{api_name}/{symbol}/{contract_regex}/{exchange}',

    # forward curve for base metals for balsamo
    'getLMEForwardCurveSettlement': r'{host}/api/v1/{api_name}/{symbol}/{stamp}',

    # vol surface for balsamo
    'getVolSurface': r'{host}/api/v1/{api_name}/{symbol}/{exchange}/{stamp}',

    # option valuation
    'getOptionPricesFromVolCurves': r'{host}/api/v1/{api_name}/{symbol}/{exchange}/{stamp}/{scheme}/{rf_rate}',

    # average price option
    'getPriceAPO': r'{host}/api/v1/{api_name}/{stamp}/{expiration_date}/{strike}/{parity}/{future_value}/{ivol}/{rf_rate}/{acc_days}/{acc_sum}/{rem_fixings}',

    # fundamental data series
    'tsdb': r'{host}/api/v1/{api_name}/source/{stage}/{source}'

}
