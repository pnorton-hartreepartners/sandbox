import json


# existing config-store
with open('config_store.json') as file:
    config_store = json.load(file)

# candidates for addition
found_in_tempest = ['Coal - API 2',
                    'Ethanol',
                    'LSCR1%NYHCARGO',
                    'NaphtaSing',
                    'WTI Houston', ]

# build the dict of updates and check they're not already there
update_dicts = []
config_store_keys = {c.get('tempest_code') for c in config_store['curves']}
for symbol in found_in_tempest:
    symbol_present = symbol in config_store_keys
    print(f'symbol: {symbol} is already there: --> {symbol_present}')
    if not symbol_present:
        update_dict = {'symbol': symbol, 'type': 'Pull', 'tempest_code': symbol}
        update_dicts.append(update_dict)

# update to existing config-store
with open('config_store_update.json', 'w') as file:
    json.dump(update_dicts, file)

# not added these yet
exchange_details = {"Coal - API 2": {"mos_symbol": "ATW", "mos_exchange": "ICE"}}
