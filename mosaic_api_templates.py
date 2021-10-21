template_url_dict = {
    # time series of all results for a single contract
    'getSettlementTS': r'{host}/settles/api/v1/{api_name}/{instrument_key}?exchange={exchange}&allow_indicative={allow_indicative}',

    # latest result for a single contract
    'getSettlement': r'{host}/settles/api/v1/{api_name}/{instrument_key}?exchange={exchange}&allow_indicative={allow_indicative}',

    # latest result for a collection of symbols on a given observation date
    'getFutureCurveSettlement': r'{host}/settles/api/v1/{api_name}/{symbols}/{exchange}/{stamp}?allow_indicative={allow_indicative}',

    # use regex to filter instruments and parse instrument name to contract month
    'getSettlementTSWithRegex': r'{host}/settles/api/v1/{api_name}/{symbol}/{contract_regex}/{exchange}',

    # forward curve for base metals for balsamo
    'getLMEForwardCurveSettlement': r'{host}/settles/api/v1/{api_name}/{symbol}/{stamp}',

    # vol surface for balsamo
    'getVolSurface': r'{host}/settles/api/v1/{api_name}/{symbol}/{exchange}/{stamp}?allow_cached_vols={allow_cached_vols}',

    # option valuation
    'getOptionPricesFromVolCurves': r'{host}/settles/api/v1/{api_name}/{symbol}/{exchange}/{stamp}/{scheme}/{rf_rate}',

}