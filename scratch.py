import json
import pandas as pd

template_symbol = 'RVO_{year}'
template_tempest_code = 'RINS{year} RVO'
format = '{:02}'

list_of_contracts = []
for y in range(9, 20):
    year = format.format(y)
    contract_dict = {'symbol': template_symbol.format(year=year),
                     'type': 'Pull',
                     'tempest_code': template_tempest_code.format(year=year)}
    list_of_contracts.append(contract_dict)

df = pd.DataFrame(data=[[c['symbol'], c['tempest_code']] for c in list_of_contracts],
                  columns=['symbol', 'tempest_code'])
json_string = json.dumps(list_of_contracts)

x = [
    {
        "symbol": "RVO_17",
        "type": "Pull",
        "tempest_code": "RINS17 RVO"
    },
    {
        "symbol": "RVO_18",
        "type": "Pull",
        "tempest_code": "RINS18 RVO"
    },
    {
        "symbol": "RVO_19",
        "type": "Pull",
        "tempest_code": "RINS19 RVO"
    },
    {
        "symbol": "RVO_20",
        "type": "Pull",
        "tempest_code": "RINS20RVO"
    },
]

y = [{"symbol": "RVO_09", "type": "Pull", "tempest_code": "RINS09 RVO"},
     {"symbol": "RVO_10", "type": "Pull", "tempest_code": "RINS10 RVO"},
     {"symbol": "RVO_11", "type": "Pull", "tempest_code": "RINS11 RVO"},
     {"symbol": "RVO_12", "type": "Pull", "tempest_code": "RINS12 RVO"},
     {"symbol": "RVO_13", "type": "Pull", "tempest_code": "RINS13 RVO"},
     {"symbol": "RVO_14", "type": "Pull", "tempest_code": "RINS14 RVO"},
     {"symbol": "RVO_15", "type": "Pull", "tempest_code": "RINS15 RVO"},
     {"symbol": "RVO_16", "type": "Pull", "tempest_code": "RINS16 RVO"},
     {"symbol": "RVO_17", "type": "Pull", "tempest_code": "RINS17 RVO"},
     {"symbol": "RVO_18", "type": "Pull", "tempest_code": "RINS18 RVO"},
     {"symbol": "RVO_19", "type": "Pull", "tempest_code": "RINS19 RVO"}]
