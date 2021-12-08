import requests
import json
import pandas as pd
from balsamo_vol_surface import get_mosaic_surface
from constants import PROD, DEV, BALSAMO, PORT, SETTLES, hosts
from pprint import pprint as pp
import datetime as dt
from mosaic_api_templates import api_config_dict

'''
activate mosaic2
'''

# ======================================================================================================================
# balsamo config

balsamo_template_url_dict = {
    'getEuropeanOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/{api}',
    'getAsianOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/{api}',
}

balsamo_headers_dict = {
    'User': 'PNO',
    'Pwd': 'Gazprom1',
    'Company': 'Hartree Partners',
    'Commodity': 'METAL CONCENTRATES',
}

balsamo_payload_dict = {
    'EuropeanOption': [
        {'putcall': 'P',  # Put = Sell = S; Call = Purchase = P
         'pricecode': 'LMEZNCB',
         'premium': '12345',
         'payableqty': '1',
         'riskFreeRate': '0.00'
         }
    ],
    'fallbackToHistorical': 'N',
    'showDetailPrices': 'N',
    'montecarlo': 'N',
    'numberOfPaths': '2000'
}

# ======================================================================================================================
# mosaic config

mosaic_url_dict = {'symbol': 'ZN',
                   'exchange': 'LME',
                   'scheme': 'European',
                   'rf_rate': 0}

mosaic_headers_dict = {'accept': 'application/json',
                       'Content-Type': 'application/json'}

mosaic_payload_dict = {'term': '202701',
                       'parity': 'Call',
                       'strike': '2400'}

mosaic_vol_surface_kwargs_dict = {
    'getVolSurface': {
        'symbol': 'ZN',
        'exchange': 'LME',
        'allow_cached_vols': 'true'
    }
}

if __name__ == '__main__':
    GET_EUROPEAN_OPTION_VALUATION = 'getEuropeanOptionValuation'
    GET_ASIAN_OPTION_VALUATION = 'getAsianOptionValuation'

    balsamo_option_valuation_api = GET_EUROPEAN_OPTION_VALUATION
    mosaic_option_valuation_api = 'getOptionPricesFromVolCurves'
    mosaic_forward_curve_api = 'getLMEForwardCurveSettlement'
    env = DEV

    mosaic_valuation = True
    balsamo_valuation = True

    # value date
    stamp_as_date = dt.date(2021, 10, 22)
    mosaic_url_dict['stamp'] = dt.datetime.strftime(stamp_as_date, '%Y-%m-%d')
    balsamo_headers_dict['ClosingPeriod'] = dt.datetime.strftime(stamp_as_date, '%d/%m/%Y')

    # term date
    term_as_date = dt.datetime.strptime(mosaic_payload_dict['term'], '%Y%m')


    balsamo_payload_dict['EuropeanOption'][0]['strike'] = mosaic_payload_dict['strike']

    # ==================================================================================================================
    # mosaic valuation

    # get the forward curve just to validate results
    mosaic_url = api_config_dict[mosaic_forward_curve_api]['url_template'].format(host=hosts[SETTLES][env],
                                                                  api_name=mosaic_forward_curve_api,
                                                                  symbol=mosaic_url_dict['symbol'],
                                                                  stamp=mosaic_url_dict['stamp'])
    mosaic_forward_curve_response = requests.get(mosaic_url)
    mosaic_forward_curve_results_df = pd.DataFrame(json.loads(mosaic_forward_curve_response.content))

    # mosaic can accept a list of options but for now we will send just one
    mosaic_payload = [mosaic_payload_dict]

    # create the url
    mosaic_url = api_config_dict[mosaic_option_valuation_api]['url_template'].format(host=hosts[SETTLES][env],
                                                                     api_name=mosaic_option_valuation_api,
                                                                     symbol=mosaic_url_dict['symbol'],
                                                                     exchange=mosaic_url_dict['exchange'],
                                                                     stamp=mosaic_url_dict['stamp'],
                                                                     scheme=mosaic_url_dict['scheme'],
                                                                     rf_rate=mosaic_url_dict['rf_rate'])

    # call api and get results
    mosaic_option_valuation_response = requests.post(mosaic_url, json=mosaic_payload, headers=mosaic_headers_dict)
    mosaic_option_valuation_results = json.loads(mosaic_option_valuation_response.content)[0]

    # ===========================
    # get vol surface from mosaic
    data_dict, mosaic_vol_surface_df = get_mosaic_surface(date=mosaic_url_dict['stamp'],
                                                          kwargs_dict=mosaic_vol_surface_kwargs_dict, env=DEV)
    mapping = zip(data_dict['contracts'], data_dict['maturities'])
    expiry_date_from_vol_surface = dict(mapping)[mosaic_payload_dict['term']]
    expiry_date_as_datetime = dt.datetime.strptime(expiry_date_from_vol_surface, '%Y-%m-%d')

    # and get the smile from the surface using the contract date
    smile = mosaic_vol_surface_df.loc[term_as_date]

    # ==================================================================================================================
    # balsamo valuation

    # create the url
    balsamo_url = balsamo_template_url_dict[balsamo_option_valuation_api].format(host=hosts[BALSAMO][env],
                                                                                 port=hosts[BALSAMO][PORT],
                                                                                 api=balsamo_option_valuation_api)

    # we got this from mosaic
    balsamo_payload_dict['EuropeanOption'][0]['promptdate'] = dt.datetime.strftime(expiry_date_as_datetime, '%d/%m/%Y')

    # call api and get results
    balsamo_option_valuation_response = requests.post(balsamo_url, headers=balsamo_headers_dict, json=balsamo_payload_dict, verify=False)
    balsamo_option_valuation_results = json.loads(balsamo_option_valuation_response.content)
    # ==================================================================================================================
    # print some results

    print('=============================================================================')
    print(f'valuation_date: {stamp_as_date}')

    print('\n\n=============================================================================')
    print('mosaic')
    print('=============================================================================')

    print('\n\nmosaic_forward_curve_results:')
    pp(mosaic_forward_curve_results_df.tail())

    print('\n\nmosaic_option_valuation_request:')
    print(mosaic_option_valuation_response.request.url)
    print(mosaic_option_valuation_response.request.body)

    print('\n\nmosaic_option_valuation_results:')
    pp(mosaic_option_valuation_results)

    print('\n\nmosaic smile:')
    pp(smile)

    print('\n\n=============================================================================')
    print('balsamo')
    print('=============================================================================')

    print('\n\nbalsamo_option_valuation_request:')
    print(balsamo_option_valuation_response.request.url)
    print()
    print(balsamo_option_valuation_response.request.headers)
    print()
    print(balsamo_option_valuation_response.request.body)

    print('\n\nbalsamo_results:')
    pp(balsamo_option_valuation_results)

    days_to_maturity = expiry_date_as_datetime.date() - stamp_as_date
    print(f'\n\ncalculated days_to_maturity: {days_to_maturity.days}')

    print()
