import requests
import json
import pandas as pd
import datetime as dt
from getpass import getpass
from pprint import pprint as pp
from balsamo_vol_surface import get_mosaic_surface
from constants import DEV, BALSAMO, PORT, SETTLES, hosts
from mosaic_api_templates import api_config_dict, MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API

'''
activate mosaic2

example mosaic call
http://settles-api.dev.mosaic.hartreepartners.com/settles/api/v1/getPriceAPO/2021-11-01/2023-01-04/2400/Call/3138.595714285714/0.2685/0/0/0/2022-01-01

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
    'numberOfPaths': '100000',
    "seed": "42"
}
# TODO: calc fixings data
my_valuation_params = {
    'valuation_date': '2021-12-01',
    # these are required for mosaic valuation (not for balsamo)
    'acc_days': 0,
    'acc_sum': 0,
    'rem_fixings': '2022-01-01',
}

# overrides for mosaic
my_market_data = {
    'forward_price': 3173.61,
    'volatility': 0.28484939933483794,
}

# ======================================================================================================================
# mappers

balsamo_put_call_mapper = {'put': 'S',
                           'call': 'P'}
balsamo_pricecode_mapper = {'ZN': 'LMEZNCB'}

# ======================================================================================================================
# dates

valuation_date = dt.date.fromisoformat(my_valuation_params['valuation_date'])
mosaic_valuation_date = dt.datetime.strftime(valuation_date, '%Y-%m-%d')
balsamo_valuation_date = dt.datetime.strftime(valuation_date, '%d/%m/%Y')

term = my_option['underlying']['term']
term = dt.date.fromisoformat(term)
term = pd.to_datetime(term)
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
    'Pwd': None,
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
    'numberOfPaths': my_model_params['numberOfPaths'],
    "seed": my_model_params['seed'],
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
                   'acc_days': my_valuation_params['acc_days'],
                   'acc_sum': my_valuation_params['acc_sum'],
                   'rem_fixings': my_valuation_params['rem_fixings'],
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
    mosaic_url = api_config_dict[MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API]['url_template'] \
        .format(host=hosts[SETTLES][env],
                api_name=MOSAIC_GET_LME_FORWARD_CURVE_SETTLEMENT_API,
                symbol=mosaic_url_dict['symbol'],
                stamp=mosaic_url_dict['stamp'])
    mosaic_forward_curve_response = requests.get(mosaic_url)
    return pd.DataFrame(json.loads(mosaic_forward_curve_response.content))


def process_response(r):
    if 200 <= r.status_code <= 299:
        try:
            results = json.loads(r.content)
        except Exception as e:
            results = f'request successful but failed to parse content with: {e}'
    else:
        results = f'request failed with: {r}'
    return results


if __name__ == '__main__':
    env = DEV
    balsamo_headers_dict['Pwd'] = getpass(prompt='enter balsamo password')

    mosaic_valuation = True
    balsamo_valuation = True
    use_my_forward_price_override = True
    use_my_volatility_override = True

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
    smile = mosaic_vol_surface_df.loc[term]

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

    # interpolate the forward price
    index = pd.to_datetime(mosaic_forward_curve_results_df['expiration_date'])
    data = mosaic_forward_curve_results_df['value'].values
    mosaic_forward_curve_interp_df = pd.DataFrame(data=data, index=index)
    mosaic_forward_curve_interp_df = mosaic_forward_curve_interp_df.resample('D').ffill()

    # get the forward price
    if use_my_forward_price_override:
        forward_price = my_market_data['forward_price']
    else:
        forward_price = mosaic_forward_curve_interp_df.loc[term].values[0]

    # get the volatility
    if use_my_volatility_override:
        volatility = my_market_data['volatility']
    else:
        volatility = smile[0.5]  # is this right?

    # update the payload
    mosaic_url_dict['future_value'] = forward_price
    mosaic_url_dict['ivol'] = volatility
    mosaic_url_dict['expiration_date'] = expiry_date_as_datetime.date().isoformat()

    # ==================================================================================================================
    # mosaic option valuation

    if mosaic_valuation:
        # mosaic can accept a list of options but for now we will send just one
        mosaic_payload = [mosaic_payload_dict]

        # create the url
        mosaic_url = api_config_dict[mosaic_option_valuation_api]['url_template'] \
            .format(host=hosts[SETTLES][env],
                    api_name=mosaic_option_valuation_api,
                    **mosaic_url_dict)

        # call api and get results
        mosaic_option_valuation_response = requests.get(mosaic_url, headers=mosaic_headers_dict)
        mosaic_option_valuation_results = process_response(mosaic_option_valuation_response)

        print('\n\n===========================================================================')
        print('===========================================================================')
        print('mosaic valuation\n\n')

        print('mosaic_forward_curve_results:')
        pp(mosaic_forward_curve_interp_df.loc[term])

        print('\n\nmosaic_option_url_dict')
        pp(mosaic_url_dict)

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
        print('===========================================================================')
        print('balsamo valuation\n\n')

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
        print()

