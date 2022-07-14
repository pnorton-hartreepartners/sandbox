'''
1) build some sql that young showed me; although i think its overcomplicated
way to test for symbol in tempest
2) read config-store and make sure proposed symbols don't already exist
3) build new entries for config-store
'''
import json

# constants
FIND = 'find'
TEST = 'test'
BUILD = 'build'


# build the sql templates
sql_select = "SELECT p.sort_dt,fqd.period_cd,qd.quote_def_cd AS mtm_quote_def_cd,fqd.end_dt AS expire_dt, \n \
    fqd.end_dt AS option_expire_dt,'' AS quote_def_cd FROM QUOTE_DEFINITION qd \n \
    INNER JOIN FORWARD_QUOTE_DEF fqd ON qd.fwd_curve_cd=fqd.fwd_curve_cd \n \
    LEFT JOIN PERIOD p ON fqd.period_cd=p.period_cd \n"
sql_where_with_lower_template = "WHERE lower(qd.quote_def_cd)=lower('{symbol}') AND qd.status='A' AND fqd.status='A' AND p.status='A' \n"
sql_where_without_lower_template = "WHERE qd.quote_def_cd='{symbol}' AND qd.status='A' AND fqd.status='A' AND p.status='A' \n"
sql_order_by = "ORDER BY p.sort_dt"

sql_find_template = sql_select + sql_where_with_lower_template + sql_order_by
sql_test_template = sql_select + sql_where_without_lower_template + sql_order_by


# copy the existing config-store here
with open('config_store.json') as file:
    config_store = json.load(file)

# ============================================================
# candidates for addition, with actual tempest name
# tuples of hdq_symbol, tempest_quote_def_cd, proposed_mosaic_name

found_in_tpt_cmdty_cd = [
    ('Coal - API 2', 'Coal - API 2', ''),
    ('Ethanol', 'ETHANOL', ''),
    ('LSCR1%NYHCARGO', 'LSCR1%NYHCARGO', ''),
    ('NaphtaSing', 'NaphtaSing', ''),
    ('WTI Houston', 'WTI Houston', ''), ]

found_in_pfs_cmdty_cd = [
    ('ArgFarEastIndex', 'ARGFarEastIndex', ''),
    ('ArgSaudiAramco', 'ARGSaudiAramco', ''),
    ('JetFobRott', 'JETFOBrott', ''),
    ('Urals NWE', 'Urals NWE', ''),
]

# ============================================================
# user config here

# try to find the symbol... or double check the result... or build the config store json
mode = BUILD
# choose the list
list_of_symbols = found_in_pfs_cmdty_cd

# ============================================================
# write the sql

if mode == FIND:
    sql_template = sql_find_template
elif mode in [TEST, BUILD]:
    sql_template = sql_test_template
else:
    raise NotImplementedError

sql = ''
for _, tempest_quote_def_cd, _ in list_of_symbols:
    sql = sql + '\n' + '\n' + sql_template.format(symbol=tempest_quote_def_cd)


# ============================================================
# save the sql here and open in dbeaver to check that rows of data are returned

with open(r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\tools\SQL\tempest... config_store_update analysis.sql', 'w') as file:
    file.write(sql)

# ============================================================
# check the symbol isnt already there and build the dict of updates

update_dicts = []
config_store_keys = {c.get('tempest_code') for c in config_store['curves']}
for _, tempest_quote_def_cd, proposed_mosaic_name in list_of_symbols:
    symbol_present = tempest_quote_def_cd in config_store_keys
    print(f'symbol: {tempest_quote_def_cd} is already there: --> {symbol_present}')
    if not symbol_present:
        if not proposed_mosaic_name:
            proposed_mosaic_name = tempest_quote_def_cd
        update_dict = {'symbol': proposed_mosaic_name, 'type': 'Pull', 'tempest_code': tempest_quote_def_cd}
        update_dicts.append(update_dict)

# ============================================================
# update to existing config-store

if mode == BUILD:
    with open('config_store_update.json', 'w') as file:
        json.dump(update_dicts, file)

# ============================================================
# not added these yet
exchange_details = {"Coal - API 2": {"mos_symbol": "ATW", "mos_exchange": "ICE"}}
