import requests
import json
from constants import PROD, DEV, BALSAMO, PORT, SETTLES, hosts

balsamo_template_url_dict = {
    'getEuropeanOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/{api}',
    'getAsianOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/{api}',
}

balsamo_headers_dict = {
    'User': 'PNO',
    'Pwd': '***',
    'Company': 'Hartree Partners',
    'Commodity': 'METAL CONCENTRATES',
    'Content-Type': 'application/json'
}

balsamo_body_dict = {
    'Putcall': 'P',  # Put = Sell = S; Call = Purchase = P
    'PriceCode': 'LMEZNCB',
    'Strike': '6662.23',
     #'MaturityDate': '2027-01-06'
    'MaturityDate': '06/01/2027'
}

mosaic_template_url_dict = {
    'getOptionPricesFromVolCurves': r'{host}/settles/api/v1/{api}/{symbol}/{exchange}/{stamp}/{scheme}/{rf_rate}',
}

mosaic_url_dict = {'symbol': 'ZN',
                   'exchange': 'LME',
                   'stamp': '2021-10-14',
                   'scheme': 'European',
                   'rf_rate': 0}

mosaic_header_dict = {'accept': 'application/json',
                      'Content-Type': 'application/json'}

mosaic_body_dict = {'term': '202701',
                       'parity': 'Call',
                       'strike': '6662.23'}

mosaic_payload_dict = {}
mosaic_payload_dict.update(mosaic_header_dict)
mosaic_payload_dict.update(mosaic_body_dict)

if __name__ == '__main__':
    balsamo_api = 'getEuropeanOptionValuation'
    mosaic_api = 'getOptionPricesFromVolCurves'
    env = DEV

    mosaic_url = mosaic_template_url_dict[mosaic_api].format(host=hosts[SETTLES][env],
                                                             api=mosaic_api,
                                                             symbol=mosaic_url_dict['symbol'],
                                                             exchange=mosaic_url_dict['exchange'],
                                                             stamp=mosaic_url_dict['stamp'],
                                                             scheme=mosaic_url_dict['scheme'],
                                                             rf_rate=mosaic_url_dict['rf_rate'])
    response = requests.post(mosaic_url, data=json.dumps([mosaic_payload_dict]))
    mosaic_results = json.loads(response.content)[0]
    print(mosaic_results)

    balsamo_url = balsamo_template_url_dict[balsamo_api].format(host=hosts[BALSAMO][env],
                                                                port=hosts[BALSAMO][PORT],
                                                                api=balsamo_api)
    params_dict = {}
    params_dict.update(balsamo_body_dict)
    params_dict.update(balsamo_headers_dict)
    response = requests.get(balsamo_url, json=params_dict, verify=False)
    print(response)
    print('hello world')


