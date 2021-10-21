from mosaic_api_templates import template_url_dict
import requests
import pandas as pd
import datetime as dt
from constants import SETTLES, hosts, DEV

vol_surface_kwargs_dict = {
    'getVolSurface': {
        'symbol': 'ZN',
        'exchange': 'LME',
        'allow_cached_vols': 'true'
    }
}


def get_mosaic_surface(date, kwargs_dict, env=DEV):
    api_name = 'getVolSurface'

    kwargs = kwargs_dict[api_name]
    kwargs['host'] = hosts[SETTLES][env]
    kwargs['api_name'] = api_name
    kwargs['stamp'] = date

    template_url = template_url_dict[api_name]
    url = template_url.format(**kwargs)

    print(f'\nurl is:\n{url}')
    data_dict = requests.get(url).json()
    if data_dict.get('detail') == 'error : no vol slice was built':
        df = pd.DataFrame()
    else:
        contracts = list(map(lambda x: dt.datetime.strptime(x, '%Y%m'), data_dict['contracts']))
        columns = data_dict['moneyness']
        surface = data_dict['volatilities']
        df = pd.DataFrame(data=surface, index=contracts, columns=columns)

        value_date = dt.datetime.strptime(data_dict['dt'], '%Y-%m-%d')
        data_dict['days_to_maturity'] = [c - value_date for c in contracts]

    return data_dict, df


if __name__ == '__main__':
    date = '2021-10-20'
    df = get_mosaic_surface(date, kwargs_dict=vol_surface_kwargs_dict, env=DEV)
    print(df)


