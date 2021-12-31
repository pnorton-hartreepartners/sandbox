from constants import SETTLES, TSDB, TRADER_CURVES, BALSAMO

MOSAIC_OPTION_VALUATION_API = 'getOptionPricesFromVolCurves'
MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API = 'getLMEForwardCurveSettlement'

api_config_dict = {
    # time series of all results for a single contract
    'getSettlementTS': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{instrument_key}'},
    # exchange={exchange}&allow_indicative={allow_indicative}',

    # latest result for a single contract
    'getSettlement': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{instrument_key}'},
    # ?exchange={exchange}&allow_indicative={allow_indicative}',

    # latest result for a collection of symbols on a given observation date
    'getFutureCurveSettlement': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{symbols}/{exchange}/{stamp}'},

    # use regex to filter instruments and parse instrument name to contract month
    'getSettlementTSWithRegex': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{symbol}/{contract_regex}/{exchange}'},

    # forward curve for base metals for balsamo
    'getLMEForwardCurveSettlement': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{symbol}/{stamp}'},

    # vol surface for balsamo
    'getVolSurface': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{symbol}/{exchange}/{stamp}'},

    # option valuation
    'getOptionPricesFromVolCurves': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{symbol}/{exchange}/{stamp}/{scheme}/{rf_rate}'},

    # average price option
    'getPriceAPO': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}/{stamp}/{expiration_date}/{strike}/{parity}/{future_value}/{ivol}/{rf_rate}/{acc_days}/{acc_sum}/{rem_fixings}'},

    # fundamental data series
    'tsdb': {
        'host': TSDB,
        'url_template': r'{host}/api/v1/{api_name}/{source}/{stage}/{source}'},

    # trader curve details incl conversions
    'getTraderCurvesCatalog': {
        'host': SETTLES,
        'url_template': r'{host}/api/v1/{api_name}'},

    # returns the json recipe for curves
    'getTraderCurveDefinition': {
        'host': TRADER_CURVES,
        'url_template': r'{host}/api/v1/{api_name}/{symbol}/{source}/{stamp}'},

    # identical? EOD version
    'getEODTraderCurveDefinition': {
        'host': TRADER_CURVES,
        'url_template': r'{host}/api/v1/{api_name}/{symbol}/{source}/{stamp}'},

    # recipe for evaluating a curve in realtime
    'getTraderCurveEval': {'host': TRADER_CURVES,
                           'url_template': r'{host}/api/v1/{api_name}/{symbol}/{source}/{stamp}'
                           },

    # trader curve time-series backed by tempest for history
    # used for charting
    'getTraderCurveTS': {'host': SETTLES,
                         'method': 'post',
                         'url_template': r'{host}/api/v1/{api_name}'},
}
