import os
import pandas as pd
import datetime as dt
from enum import Enum
from mosaic_sql.crate import EngineInstance, get_engine

symbols = ['TTF', 'UKF', 'NBP', 'G', 'EUA', 'B']

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
and instrument_key < '{yearmonth}'

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
and instrument_key < '{yearmonth}'

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


def get_detail(symbol, yearmonth, uat_label, date, engine):
    length = len(symbol) + 7
    yearmonth = symbol + ' ' + yearmonth
    sql = sql_detail_template.format(symbol=symbol, length=length, yearmonth=yearmonth, uat_label=uat_label, date=date)
    return pd.read_sql(sql, con=engine)


if __name__ == "__main__":
    run_checksum = False
    run_detail = True

    os.environ['CRATE_HOST'] = 'ttda.storage.mosaic.hartreepartners.com:4200'
    engine = get_engine(EngineInstance.TTDA, timeout=20, debug=False)

    path = r'c:\temp'
    checksum_filename = 'settle_checksum.xlsx'
    detail_filename = 'settle_detail.xlsx'
    checksum_file = os.path.join(path, checksum_filename)
    detail_file = os.path.join(path, detail_filename)
    yearmonth = '202301'

    if run_checksum:
        with pd.ExcelWriter(checksum_file) as writer:
            for symbol in symbols:
                df = get_checksum(symbol, yearmonth, engine=engine)
                df.to_excel(writer, sheet_name=symbol)

    if run_detail:
        with pd.ExcelWriter(detail_file) as writer:
            date = dt.date(2021, 8, 11)
            date = date.strftime('%Y-%m-%d')
            for symbol in symbols:
                df = get_detail(symbol, yearmonth, uat_label=Version.FINAL.value, date=date, engine=engine)
                df.to_excel(writer, sheet_name=symbol)

