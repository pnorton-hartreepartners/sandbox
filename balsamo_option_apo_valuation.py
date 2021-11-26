import requests
import json
import pandas as pd
from balsamo_vol_surface import get_mosaic_surface
from constants import DEV, BALSAMO, PORT, SETTLES, hosts, URL_KWARGS, PARAMS_KWARGS
from pprint import pprint as pp
import datetime as dt
from mosaic_api_templates import template_url_dict, MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API

'''
activate mosaic2
'''
# ======================================================================================================================
# my test

my_option = {
    'underlying': {'symbol': 'ZN', 'exchange': 'LME', 'term': '2023-01-01'},
    'expiry': 'asian',
    'index': {'start': '2022-01-01', 'end': '2022-12-31'},
    'putcall': 'call',
    'strike': 2400,
    'side': +1,
    'quantity': 1000,
    'rf_rate': 0
}
my_model_params = {
    'montecarlo': 'Y',
    'numberOfPaths': '2000'
}
valuation_date = '2021-11-01'

# ======================================================================================================================
# mappers

balsamo_put_call_mapper = {'put': 'S',
                           'call': 'P'}
balsamo_pricecode_mapper = {'ZN': 'LMEZNCB'}

# ======================================================================================================================
# dates

valuation_date = dt.date.fromisoformat(valuation_date)
mosaic_valuation_date = dt.datetime.strftime(valuation_date, '%Y-%m-%d')
balsamo_valuation_date = dt.datetime.strftime(valuation_date, '%d/%m/%Y')

term = my_option['underlying']['term']
term = dt.date.fromisoformat(term)
mosaic_term = dt.datetime.strftime(term, '%Y%m')

index_start = dt.date.fromisoformat(my_option['index']['start'])
index_end = dt.date.fromisoformat(my_option['index']['end'])
balsamo_index_start = dt.datetime.strftime(index_start, '%d/%m/%Y')
balsamo_index_end = dt.datetime.strftime(index_end, '%d/%m/%Y')

# ======================================================================================================================
# balsamo config

balsamo_option_valuation_api = 'getAsianOptionValuation'
balsamo_option_model = 'AsianOption'

balsamo_template_url_dict = {
    'getEuropeanOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/{api}',
    'getAsianOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/{api}',
}

balsamo_headers_dict = {
    'User': 'PNO',
    'Pwd': 'Gazprom2',
    'Company': 'Hartree Partners',
    'Commodity': 'METAL CONCENTRATES',
    'ClosingPeriod': balsamo_valuation_date
}

balsamo_payload_dict = {
    balsamo_option_model: [
        {'putcall': balsamo_put_call_mapper[my_option['putcall']],
         'pricecode': balsamo_pricecode_mapper[my_option['underlying']['symbol']],
         'premium': '0',
         'payableqty': str(my_option['quantity']),
         'qpstart': balsamo_index_start,
         'qpend': balsamo_index_end,
         'riskFreeRate': str(my_option['rf_rate']),
         'strike': str(my_option['strike']),
         'promptdate': None  # this is the expiry of the option; we dont know it yet
         }
    ],
    'fallbackToHistorical': 'N',
    'showDetailPrices': 'N',
    'montecarlo': my_model_params['montecarlo'],
    'numberOfPaths': my_model_params['numberOfPaths']
}

# ======================================================================================================================
# mosaic config

mosaic_option_valuation_api = 'getPriceAPO'
mosaic_url_dict = {'symbol': my_option['underlying']['symbol'],
                   'exchange': my_option['underlying']['exchange'],
                   'scheme': my_option['expiry'].capitalize(),
                   'rf_rate': my_option['rf_rate'],
                   'expiration_date': None,
                   'future_value': None,
                   'ivol': None,
                   'acc_days': 0,
                   'acc_sum': 0,
                   'rem_fixings': '2022-01-01',
                   'stamp': mosaic_valuation_date
                   }

mosaic_payload_dict = {'term': mosaic_term,
                       'parity': my_option['putcall'].capitalize(),
                       'strike': str(my_option['strike'])}

# this was separated for european options? not here:
mosaic_url_dict.update(mosaic_payload_dict)

mosaic_headers_dict = {'accept': 'application/json',
                       'Content-Type': 'application/json'}

mosaic_vol_surface_api = 'getVolSurface'
mosaic_vol_surface_url_dict = {'host': hosts[SETTLES]['dev'],
                               'api_name': mosaic_vol_surface_api,
                               'stamp': mosaic_valuation_date,
                               'symbol': my_option['underlying']['symbol'],
                               'exchange': my_option['underlying']['exchange'],
                               'allow_cached_vols': 'true'  # not used... not sure what to do here
                               }

# ======================================================================================================================


def get_mosaic_forward_curve(hosts, mosaic_url_dict):
    mosaic_url = template_url_dict[MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API] \
        .format(host=hosts[SETTLES][env],
                api_name=MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API,
                symbol=mosaic_url_dict['symbol'],
                stamp=mosaic_url_dict['stamp'])
    mosaic_forward_curve_response = requests.get(mosaic_url)
    return pd.DataFrame(json.loads(mosaic_forward_curve_response.content))


def process_response(r):
    if r.status_code == 200:
        try:
            results = json.loads(r.content)
        except Exception as e:
            print(f'request successful but failed to parse content with: {e}')
            results = None
    else:
        results = None
    return results


if __name__ == '__main__':
    env = DEV

    mosaic_valuation = True
    balsamo_valuation = True

    # ==================================================================================================================
    # get forward curve and vol surface from mosaic

    # get the forward curve
    mosaic_forward_curve_results_df = get_mosaic_forward_curve(hosts, mosaic_url_dict)

    # get vol surface for smile and expiry date
    data_dict, mosaic_vol_surface_df = get_mosaic_surface(
        date=mosaic_url_dict['stamp'],
        url_kwargs=mosaic_vol_surface_url_dict,
        env=DEV)
    # extract date
    mapping = zip(data_dict['contracts'], data_dict['maturities'])
    expiry_date_from_vol_surface = dict(mapping)[mosaic_payload_dict['term']]
    expiry_date_as_datetime = dt.datetime.strptime(expiry_date_from_vol_surface, '%Y-%m-%d')

    # and get the smile from the surface using the contract date
    smile = mosaic_vol_surface_df.loc[pd.to_datetime(term)]

    # ==================================================================================================================
    # add the option expiry date to balsamo payload

    # we got the option expiry date from mosaic
    balsamo_option_expiry_date = dt.datetime.strftime(expiry_date_as_datetime, '%d/%m/%Y')
    # update the payload
    balsamo_payload_dict[balsamo_option_model][0]['promptdate'] = balsamo_option_expiry_date

    # ==================================================================================================================
    # add the vol, forward price and expiry to the mosaic payload

    # we got the option expiry date from mosaic
    balsamo_option_expiry_date = dt.datetime.strftime(expiry_date_as_datetime, '%d/%m/%Y')

    # get the forward price
    index = 'expiration_date'
    columns = [index, 'value']
    df = mosaic_forward_curve_results_df[columns]
    df[index] = pd.to_datetime(df[index])
    df = df.set_index(keys=index, drop=True)
    df = df.resample('D').interpolate('linear')
    future_value = df.loc[pd.to_datetime(term)].values[0]

    # update the payload
    mosaic_url_dict['future_value'] = future_value
    mosaic_url_dict['ivol'] = smile[0.5]  # is this right?
    mosaic_url_dict['expiration_date'] = expiry_date_as_datetime.date().isoformat()

    # ==================================================================================================================
    # mosaic option valuation

    if mosaic_valuation:
        # mosaic can accept a list of options but for now we will send just one
        mosaic_payload = [mosaic_payload_dict]

        # create the url
        mosaic_url = template_url_dict[mosaic_option_valuation_api] \
            .format(host=hosts[SETTLES][env],
                    api_name=mosaic_option_valuation_api,
                    **mosaic_url_dict)

        # call api and get results
        mosaic_option_valuation_response = requests.get(mosaic_url, headers=mosaic_headers_dict)
        mosaic_option_valuation_results = process_response(mosaic_option_valuation_response)

        print('\n\n===========================================================================')
        print('mosaic_forward_curve_results:')
        pp(mosaic_forward_curve_results_df.tail())

        print('\n\nmosaic_option_valuation_request:')
        print(mosaic_option_valuation_response.request.url)

        print('\n\nmosaic_option_valuation_results:')
        pp(mosaic_option_valuation_results)

        print('\n\nmosaic smile:')
        pp(smile)

    # ==================================================================================================================
    # balsamo valuation

    if balsamo_valuation:

        # create the url
        balsamo_url = balsamo_template_url_dict[balsamo_option_valuation_api] \
            .format(host=hosts[BALSAMO][env],
                    port=hosts[BALSAMO][PORT],
                    api=balsamo_option_valuation_api)

        # call api and get results
        balsamo_option_valuation_response = requests.post(
            balsamo_url,
            headers=balsamo_headers_dict,
            json=balsamo_payload_dict,
            verify=False)
        balsamo_option_valuation_results = process_response(balsamo_option_valuation_response)

        print('\n\n===========================================================================')
        print('balsamo_payload_dict:')
        pp(balsamo_payload_dict)
        print()
        print('balsamo_option_valuation_request:')
        print(balsamo_option_valuation_response.request.url)
        print()
        print(balsamo_option_valuation_response.request.headers)
        print()
        print(balsamo_option_valuation_response.request.body)

        print('\n\nbalsamo_results:')
        pp(balsamo_option_valuation_results)


    # ==================================================================================================================
    # print some results
'''
    print('=============================================================================')
    print(f'valuation_date: {valuation_date}')

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
    '''
