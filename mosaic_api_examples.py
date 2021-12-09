from constants import URL_KWARGS, PARAMS_KWARGS, DEV
from mosaic_api_templates import api_config_dict
from mosaic_wapi import build_url, get_any_api, build_partial_url_kwargs, post_any_api, process_chart_data

kwargs_dict = {
    'getFutureCurveSettlement': {
        URL_KWARGS:
            {'exchange': 'CME',
             'symbols': 'CL%2CHO',
             'stamp': '2021-09-14', },
        PARAMS_KWARGS:
            {'allow_indicative': 'true'}
    },
    'getVolSurface': {
        URL_KWARGS:
            {'symbol': 'ZN',
             'exchange': 'LME',
             'stamp': '2021-10-12'},
        PARAMS_KWARGS:
            {'allow_cached_vols': 'true'}
    },
    'tsdb': {
        URL_KWARGS:
            {'stage': 'raw',
             'source': 'eia_weekly'},
        PARAMS_KWARGS:
            {'filters': "sourcekey='WTTSTUS1'"}  # need single quotes
    },
    'getTraderCurvesCatalog': {
        URL_KWARGS:
            {},
        PARAMS_KWARGS:
            {}
    },
    'getTraderCurveDefinition': {
        URL_KWARGS:
            {'symbol': 'HO-GO-S',
             'source': 'hartree',
             'stamp': '2021-12-07'
             },
        PARAMS_KWARGS:
            {}
    },
    'getTraderCurveTS': {
        URL_KWARGS:
            {},
    }
}


j = '''{
  "start_date": "2021-01-01",
  "end_date": "2023-01-01",
  "seasonality": 0,
  "chartlets": [
    {
      "name": "my legend",
      "curves": [
        {
          "expression": "BRT-F",
          "factor": 1,
          "type": "Outright",
          "contracts": [
            "202201"
          ]
        }
      ],
      "currency": "USD",
      "uom": "*",
      "axis": 0
    }
  ]
}'''

if __name__ == '__main__':

    env = DEV

    key = 'getTraderCurveTS'
    kwargs_dict = {key: kwargs_dict[key]}

    for api_name in kwargs_dict:
        template_url = api_config_dict[api_name]['url_template']

        url_kwargs = build_partial_url_kwargs(api_name, env=env)
        url_kwargs.update(kwargs_dict[api_name][URL_KWARGS])
        url = build_url(template_url=template_url, kwargs=url_kwargs)

        params = kwargs_dict[api_name].get(PARAMS_KWARGS)
        method = api_config_dict[api_name].get('method', 'get')

        if method == 'get':
            result, df, error = get_any_api(url, params)
            print(error)
            print(df)
            df.to_clipboard()
        elif method == 'post':
            payload = j
            result = post_any_api(url, payload=payload)
            if api_name == 'getTraderCurveTS':
                process_chart_data(result)
        else:
            raise NotImplementedError


