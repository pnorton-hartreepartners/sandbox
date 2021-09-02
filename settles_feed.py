import os
import pandas as pd
import datetime as dt
from enum import Enum
import argparse
from mosaic_sql.crate import EngineInstance, get_engine


sql_checksum_template = """
select '{symbol}' as symbol, prod.*, uat.value, uat.curve_length,
prod.value - uat.value as value_diff,
prod.curve_length - uat.curve_length as curve_length_diff
from 
(
SELECT exchange, "date", field, label, "source", sum(value) as value, count(*) as curve_length
FROM settles.values
where exchange = '{exchange}'
and source = '{exchange}'
and instrument_key like '{symbol} %'
and instrument_key < '{yearmonth}'

and char_length(instrument_key) = {length}  --<-- exclude options here
and field = 'Price'
and label = 'Settlement'
and date >= '{date}'
group by exchange, "date", field, label, "source"
) prod
full outer join 
(
SELECT exchange, "date", field, label, "source", sum(value) as value, count(*) as curve_length
FROM settles.values
where exchange = '{exchange}'
and source = 'TT'
and instrument_key like '{symbol} %'
and instrument_key < '{yearmonth}'

and char_length(instrument_key) = {length}  --<-- exclude options here
and field = 'Price'
and label = 'Settlement'
and date >= '{date}'
group by exchange, "date", field, label, "source"
) uat
on prod.exchange = uat.exchange
	and prod.date = uat.date
	and prod.field = uat.field
	and prod.label = uat.label
order by prod.date
"""

sql_detail_template = """
select '{symbol}' as symbol,
nullif(uat.exchange, prod.exchange) as exchange,
uat.instrument_key as uat_instrument_key,
prod.instrument_key as prod_instrument_key,
nullif(uat.date, prod.date) as date,
nullif(uat.field, prod.field) as field,
uat.source as uat_source,
prod.source as prod_source,
uat.label as uat_label,
prod.value as prod_value,
uat.value as uat_value,
prod.value - uat.value as value_diff
from 
(
SELECT *
FROM settles.values
where exchange = '{exchange}'
and source = '{exchange}'
and instrument_key like '{symbol} %'

and char_length(instrument_key) = {length}  --<-- exclude options here
and field = 'Price'
and label = 'Settlement'
and date = '{date}'

) prod
full outer join 
(
SELECT *
FROM settles.values
where exchange = '{exchange}'
and source = 'TT'
and instrument_key like '{symbol} %'

and char_length(instrument_key) = {length}  --<-- exclude options here
and field = 'Price'
and label = '{uat_label}'
and date = '{date}'
) uat
on prod.exchange = uat.exchange
	and prod.date = uat.date
	and prod.field = uat.field
	and prod.instrument_key = uat.instrument_key
order by prod.date
"""


class Version(Enum):
    INDICATIVE = 'Settlement-Indicative'
    FINAL = 'Settlement'

class Exchange(Enum):
    ICE = 'ICE'
    CME = 'CME'


def get_checksum(exchange, symbol, date, yearmonth, engine):
    length = len(symbol) + 7
    yearmonth = symbol + ' ' + yearmonth
    sql = sql_checksum_template.format(exchange=exchange, symbol=symbol, date=date, length=length, yearmonth=yearmonth)
    return pd.read_sql(sql, con=engine)


def get_detail(exchange, symbol, uat_label, date, engine):
    length = len(symbol) + 7
    sql = sql_detail_template.format(exchange=exchange, symbol=symbol, length=length, uat_label=uat_label, date=date)
    return pd.read_sql(sql, con=engine)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--eod_date',
                        help='format YYYY-MM-DD',
                        type=dt.date.fromisoformat,
                        required=True)
    parser.add_argument('-r', '--report',
                        help='detail or checksum',
                        choices=['detail', 'checksum'],
                        required=True)
    parser.add_argument('-v', '--version',
                        help='indicative or final',
                        choices=['indicative', 'final'])
    parser.add_argument('-x', '--exchange',
                        help='CME or ICE',
                        choices=['CME', 'ICE'],
                        required=True)
    parser.add_argument('-e', '--env',
                        help='prod or dev',
                        choices=['prod', 'dev'],
                        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    '''
    from the command prompt:
    
    this runs checksum for every day since the given date
    >>> python settles_feed.py -x ICE -d 2021-08-20 -r checksum -e prod
    
    test the indicative feed for current date (today is 2-sep)
    >>> python settles_feed.py -x ICE -d 2021-09-02 -r detail -v indicative -e prod
    
    test the final version for yesterday
    >>> python settles_feed.py -x ICE -d 2021-09-01 -r detail -v final -e prod
    '''

    # ============================
    # some config
    prod_str = 'ttda.storage.mosaic.hartreepartners.com:4200'
    dev_str = 'ttda.cratedb-dev-cluster.mosaic.hartreepartners.com:4200'

    ice_symbols = ['TTF', 'UKF', 'NBP', 'G', 'EUA', 'B']
    cme_symbols = ['CL', 'NG', 'HO', 'XAU']

    path = r'c:\temp'
    yearmonth = '202301'  # a parameter to limit forward curve on advice of mathieu; checksum only
    # ============================

    # arguments from command line
    args = get_args()
    try:
        eod_date_sql = args.eod_date
        report_selection = args.report
        exchange = args.exchange
        version = args.version
        env = args.env
    except Exception as e:
        pass

    symbols_dict = {Exchange.ICE.value: ice_symbols,
                    Exchange.CME.value: cme_symbols
                    }
    symbols = symbols_dict[exchange]

    conn_dict = {'dev': dev_str,
                 'prod': prod_str}
    conn_str = conn_dict[env]

    # report selection
    run_checksum = True if report_selection == 'checksum' else False
    run_detail = True if report_selection == 'detail' else False
    if version == 'indicative':
        version = Version.INDICATIVE.value
    elif version == 'final':
        version = Version.FINAL.value

    # variables used for setting file name
    eod_date_str = eod_date_sql.strftime('%Y%m%d')
    report_run_date_str = dt.datetime.today().strftime('%Y%m%d%H%M')

    checksum_filename = 'settle_checksum_{eod_date_str}_{exchange}_{report_run_date}.xlsx'
    detail_filename_dict = {Version.FINAL.value: 'settle_detail_final_{eod_date_str}_{exchange}_{report_run_date}.xlsx',
                            Version.INDICATIVE.value: 'settle_detail_indicative_{eod_date_str}_{exchange}_{report_run_date}.xlsx'}

    checksum_file = os.path.join(path, checksum_filename.format(eod_date_str=eod_date_str, exchange=exchange, report_run_date=report_run_date_str))
    eod_date_sql = eod_date_sql.strftime('%Y-%m-%d')

    # set up db connection
    os.environ['CRATE_HOST'] = conn_str
    engine = get_engine(EngineInstance.TTDA, timeout=20, debug=False)

    if run_checksum:
        with pd.ExcelWriter(checksum_file) as writer:
            for symbol in symbols:
                df = get_checksum(exchange=exchange, symbol=symbol, date=eod_date_sql, yearmonth=yearmonth, engine=engine)
                df.to_excel(writer, sheet_name=symbol)

    if run_detail:
        detail_file = os.path.join(path, detail_filename_dict[version].format(eod_date_str=eod_date_str, exchange=exchange, report_run_date=report_run_date_str))
        with pd.ExcelWriter(detail_file) as writer:
            for symbol in symbols:
                df = get_detail(exchange=exchange, symbol=symbol, uat_label=version, date=eod_date_sql, engine=engine)
                df.to_excel(writer, sheet_name=symbol)
