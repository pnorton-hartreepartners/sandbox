import requests
import pandas as pd

SETTLES_API = 'http://settles-api.mosaic.hartreepartners.com'


def get_settles_ts(host, instrument_key, exchange):
    url = f'{host}/settles/api/v1/getSettlementTS/{instrument_key}?exchange={exchange}'
    result = requests.get(url)
    if result.status_code != 200:
        print(result.text)
        result.raise_for_status()
    return pd.DataFrame(result.json())


if __name__ == '__main__':
    instrument_key = 'JKM 202110'
    exchange = 'ICE'
    df = get_settles_ts(host=SETTLES_API, instrument_key=instrument_key, exchange=exchange)
    print(df.head())
