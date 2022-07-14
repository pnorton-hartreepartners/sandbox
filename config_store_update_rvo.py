from trader_curve_definitions2 import get_trader_curves_catalogue
from constants import PROD
import json

catalogue_df = get_trader_curves_catalogue(env=PROD)
mask = catalogue_df.index.str.startswith('RVO')
rvo_symbols = catalogue_df.loc[mask].index.to_list()

template_tempest_code = 'RINS{year}RVO'
rvo_symbols_dict = {s: template_tempest_code.format(year=s[-2:]) for s in rvo_symbols}

update_dicts = []
for mosaic_symbol, tempest_symbol in rvo_symbols_dict.items():
    update_dict = {'symbol': mosaic_symbol, 'type': 'Pull', 'tempest_code': tempest_symbol}
    update_dicts.append(update_dict)

with open(r'config_store_update_rvo.json', 'w') as file:
    json.dump(update_dicts, file)
