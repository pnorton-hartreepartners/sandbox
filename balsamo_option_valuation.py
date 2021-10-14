import requests
import pandas as pd
import datetime as dt
import argparse
from constants import PROD, DEV, BALSAMO, PORT, hosts

template_url_dict = {
    'getEuropeanOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/getEuropeanOptionValuation',
    'getAsianOptionValuation': r'{host}:{port}/balsacore/balsarest/risk/getAsianOptionValuation',
}

payload_dict = {
    'User': 'PNO',
    'Pwd': 'Gazprom1',
    'Company': 'Hartree Partners',
    'Commodity': 'METAL CONCENTRATES',
    'PutCall': 'P',  # Put = Sell = S; Call = Purchase = P
    'PriceCode': 'LMEZNCB',
    'Strike': 6662.23,
    'MaturityDate': '2027-01-06'
}

if __name__ == '__main__':
    api = 'getEuropeanOptionValuation'
    url = template_url_dict[api].format(host=hosts[BALSAMO][DEV], port=hosts[BALSAMO][PORT])

    response = requests.post(url, json=payload_dict)
    print('hello world')


