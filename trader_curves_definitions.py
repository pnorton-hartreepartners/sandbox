'''
json file generated using this api
http://trader-curves-api.dev.mosaic.hartreepartners.com/trader-curves/api/v1/getTraderCurveTopicDictionary/definitions

no, this one
https://github.com/hartreepartners/settles-data-schema/blob/master/settles_data_schema/data/etrm/tempest.json

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

# keys = sorted(list(data.keys()))
supported_types = ['Combo', 'Pull']
combo_keys = [d['symbol'] for d in data if d['type'] == 'Combo' and d['symbol'][-2:] != '-S']
pull_keys = [d['symbol'] for d in data if d['type'] == 'Pull']
# keys = [d['symbol'] for d in data if d['type'] in supported_types]
keys = sorted(pull_keys)
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
# because these are in tempest
keys_that_work = [key for key in keys if data[key]['definition']['type'] in ['Combo']]

print()

# doesnt work
key = 'RB-DATED-S'

