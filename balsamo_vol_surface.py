from mosaic_api_templates import api_config_dict
from mosaic_api_examples import kwargs_dict
import requests
import pandas as pd
import datetime as dt
from constants import SETTLES, hosts, DEV, URL_KWARGS, PARAMS_KWARGS
from mosaic_wapi import build_partial_url_kwargs, build_url


def get_mosaic_surface(url_kwargs, env=DEV):
    api_name = 'getVolSurface'
    template_url = api_config_dict[api_name]['url_template']
    partial_url_kwargs = build_partial_url_kwargs(api_name, env=env)
    url_kwargs.update(partial_url_kwargs)
    url = build_url(template_url=template_url, kwargs=url_kwargs)

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
    url_kwargs = kwargs_dict['getVolSurface'][URL_KWARGS]
    data_dict, df = get_mosaic_surface(date=date, url_kwargs=url_kwargs, env=DEV)
    print(df)


