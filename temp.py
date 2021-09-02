import json
from pprint import pprint as pp

# Opening JSON file
with open('trader_curves_definitions.json', ) as f:
    data = json.load(f)

pp(data.keys())

print()

