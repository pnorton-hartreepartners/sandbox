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
where exchange = 'ICE'
and source = 'ICE'
and instrument_key like '{symbol} %'
and instrument_key < '{yearmonth}'

and char_length(instrument_key) = {length}  --<-- exclude options here
and field = 'Price'
and label = 'Settlement'
and date >= '2021-07-01'
group by exchange, "date", field, label, "source"
) prod
full outer join 
(
SELECT exchange, "date", field, label, "source", sum(value) as value, count(*) as curve_length
FROM settles.values_2
where exchange = 'ICE'
and source = 'TT'
and instrument_key like '{symbol} %'
and instrument_key < '{yearmonth}'

and char_length(instrument_key) = {length}  --<-- exclude options here
and field = 'Price'
and label = 'Settlement'
and date >= '2021-07-01'
group by exchange, "date", field, label, "source"
) uat
on prod.exchange = uat.exchange
	and prod.date = uat.date
	and prod.field = uat.field
	and prod.label = uat.label
order by prod.date
"""

sql_detail_template = """
select '{symbol}' as symbol, prod.*, uat.value,
prod.value - uat.value as value_diff
from 
(
SELECT *
FROM settles.values
where exchange = 'ICE'
and source = 'ICE'
and instrument_key like '{symbol} %'

and char_length(instrument_key) = {length}  --<-- exclude options here
and field = 'Price'
and label = 'Settlement'
and date = '{date}'

) prod
full outer join 
(
SELECT *
FROM settles.values_2
where exchange = 'ICE'
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
	and prod.label = uat.label
	and prod.instrument_key = uat.instrument_key
order by prod.date
"""


class Version(Enum):
    INDICATIVE = 'Settlement-Indicative'
    FINAL = 'Settlement'


def get_checksum(symbol, yearmonth, engine):
    length = len(symbol) + 7
    yearmonth = symbol + ' ' + yearmonth
    sql = sql_checksum_template.format(symbol=symbol, length=length, yearmonth=yearmonth)
    return pd.read_sql(sql, con=engine)


def get_detail(symbol, uat_label, date, engine):
    length = len(symbol) + 7
    sql = sql_detail_template.format(symbol=symbol, length=length, uat_label=uat_label, date=date)
    return pd.read_sql(sql, con=engine)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--eod_date',
                        help='format YYYY-MM-DD',
                        required=True,
                        type=dt.date.fromisoformat)
    parser.add_argument('-r', '--report',
                        help='detail or checksum',
                        choices=['detail', 'checksum'],
                        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    '''
    from the command prompt:
    >>> python settles_feed.py -d 2021-08-12 -r checksum
    >>> python settles_feed.py -d 2021-08-12 -r detail
    '''

    # ============================
    # some config

    symbols = ['TTF', 'UKF', 'NBP', 'G', 'EUA', 'B']

    path = r'c:\temp'
    yearmonth = '202301'  # a parameter to limit forward curve on advice of mathieu; checksum only
    # ============================

    # arguments from command line
    args = get_args()
    eod_date_sql = args.eod_date
    report_selection = args.report

    # report selection
    run_checksum = True if report_selection == 'checksum' else False
    run_detail = True if report_selection == 'detail' else False

    # variables used for setting file name
    eod_date_str = eod_date_sql.strftime('%Y%m%d')
    report_run_date_str = dt.datetime.today().strftime('%Y%m%d%H%M')

    checksum_filename = 'settle_checksum_{eod_date_str}_{report_run_date}.xlsx'
    detail_filename_dict = {Version.FINAL.value: 'settle_detail_final_{eod_date_str}_{report_run_date}.xlsx',
                            Version.INDICATIVE.value: 'settle_detail_indicative_{eod_date_str}_{report_run_date}.xlsx'}

    checksum_file = os.path.join(path, checksum_filename.format(eod_date_str=eod_date_str, report_run_date=report_run_date_str))
    eod_date_sql = eod_date_sql.strftime('%Y-%m-%d')

    # set up db connection
    os.environ['CRATE_HOST'] = 'ttda.storage.mosaic.hartreepartners.com:4200'
    engine = get_engine(EngineInstance.TTDA, timeout=20, debug=False)

    if run_checksum:
        with pd.ExcelWriter(checksum_file) as writer:
            for symbol in symbols:
                df = get_checksum(symbol, yearmonth, engine=engine)
                df.to_excel(writer, sheet_name=symbol)

    if run_detail:
        for version in Version:
            detail_file = os.path.join(path, detail_filename_dict[version.value].format(eod_date_str=eod_date_str, report_run_date=report_run_date_str))

            with pd.ExcelWriter(detail_file) as writer:
                for symbol in symbols:
                    df = get_detail(symbol, uat_label=version.value, date=eod_date_sql, engine=engine)
                    df.to_excel(writer, sheet_name=symbol)
