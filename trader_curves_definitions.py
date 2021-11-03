'''
json file generated using this api
http://trader-curves-api.dev.mosaic.hartreepartners.com/trader-curves/api/v1/getTraderCurveTopicDictionary/definitions
use production definition by modifying this url
save the file in the path location defined here
'''

import json
from pprint import pprint as pp
import os
from constants import json_for_trader_curves_definitions, path

pathfile = os.path.join(path, json_for_trader_curves_definitions)

with open(pathfile) as json_file:
    data = json.load(json_file)

keys = sorted(list(data.keys()))
pp(keys)

types = [data[key]['definition']['type'] for key in keys]
'''
set(types)
{'Combo', 'TimeSpread', 'Dynamic', 'Swap', 'Outright'}
'''

key = 'BRT-S'
pp(data[key])
pp(data[key]['definition']['type'])

keys_not_swap = [key for key in keys if data[key]['definition']['type'] != 'Swap']
print()

# doesnt work
key = 'RB-DATED-S'

