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

keys = list(data.keys())
pp(keys)

key = 'BRT-S'
pp(data[key])

print()
