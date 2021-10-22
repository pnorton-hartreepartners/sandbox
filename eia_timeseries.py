import os
os.environ['IGNITE_HOST_OVERWRITE'] = 'jdbc.dev.mosaic.hartreepartners.com'
os.environ['TSDB_HOST'] = 'tsdb-dev.mosaic.hartreepartners.com'
os.environ['CRATE_HOST'] = 'ttda.cratedb-dev-cluster.mosaic.hartreepartners.com:4200'
os.environ['MOSAIC_ENV'] = 'DEV'

import pandas as pd
import datetime as dt
from analyst_data_views.common.db_flattener import getFlatRawDF

SOURCE_KEY = 'Sourcekey'
LOAD = 'load'
SAVE = 'save'
SUBTOTAL = 'subtotal'
CALCULATED = 'calculated'
DATE = 'date'
VALUE = 'value'

other_dict = {
    'WBCRI_NUS_2':  # 'Refiner and Blender Net Input of Gasoline Blending Components'
        ['W_EPOBGRR_YIR_NUS_MBBLD',
         'WO6RI_NUS_2',
         'WO7RI_NUS_2',
         'WO9RI_NUS_2'],
    'W_EPPO6_SAE_NUS_MBBL':  # Ending Stocks of Other Oils; this one doesn't add up
        ['W_EPPA_SAE_NUS_MBBL',
         'W_EPPK_SAE_NUS_MBBL',
         'W_EPL0XP_SAE_NUS_MBBL',
         'WUOSTUS1'],
    'WTTSTUS1':  # Ending Stocks of Crude Oil and Petroleum Products; at the most granular level
        ['WCESTUS1',
         'WCSSTUS1',
         'WG1ST_NUS_1',
         'WG3ST_NUS_1',
         'W_EPM0CAL55_SAE_NUS_MBBL',
         'W_EPM0CAG55_SAE_NUS_MBBL',
         'WG6ST_NUS_1',
         'W_EPOBGRR_SAE_NUS_MBBL',
         'WO4ST_NUS_1',
         'WO3ST_NUS_1',
         'WO6ST_NUS_1',
         'WO7ST_NUS_1',
         'WO9ST_NUS_1',
         'W_EPOOXE_SAE_NUS_MBBL',
         'WKJSTUS1',
         'WD0ST_NUS_1',
         'WD1ST_NUS_1',
         'WDGSTUS1',
         'WRESTUS1',
         'WPRSTUS1',
         'W_EPPO6_SAE_NUS_MBBL']}

hierarchy_dict = {
    # ======================================
    'WTTSTUS1':
        ['WCRSTUS1',  # Crude Oil (Including SPR)
         'WGTSTUS1',  # Total Motor Gasoline
         'W_EPOOXE_SAE_NUS_MBBL',  # Fuel Ethanol
         'WKJSTUS1',  # Kerosene-Type Jet Fuel
         'WDISTUS1',  # Distillate Fuel Oil
         'WRESTUS1',  # Residual Fuel Oil
         'WPRSTUS1',  # Propane/Propylene (Excl. Propylene at Terminal)
         'W_EPPO6_SAE_NUS_MBBL'  # Other Oils (Excluding Ethanol)
         ],
    # ======================================
    # Crude Oil (Including SPR)
    'WCRSTUS1':
        ['WCESTUS1',  # Commercial (Excl. Lease Stock )
        'WCSSTUS1',   # SPR
         ],
    # ======================================
    # Total Motor Gasoline
    'WGTSTUS1':
        ['WGFSTUS1'
         'WBCSTUS1'],
    # ======================================
    # Finished Motor Gasoline
    'WGFSTUS1':
        ['WGRSTUS1',
         'WG4ST_NUS_1'],
    'WGRSTUS1':
        ['WG1ST_NUS_1',
         'WG3ST_NUS_1'],
    'WG4ST_NUS_1':
        ['W_EPM0CAL55_SAE_NUS_MBBL',
         'W_EPM0CAG55_SAE_NUS_MBBL',
         'WG6ST_NUS_1'],
    # ======================================
    # Motor Gasoline Blending Components
    'WBCSTUS1':
        ['W_EPOBGRR_SAE_NUS_MBBL',
         'WO4ST_NUS_1',
         'WO3ST_NUS_1',
         'WO6ST_NUS_1',
         'WO7ST_NUS_1',
         'WO9ST_NUS_1'],
    # ======================================
    # Distillate Fuel Oil
    'WDISTUS1':
        ['WD0ST_NUS_1',
         'WD1ST_NUS_1',
         'WDGSTUS1']

}

path = r'C:\Temp'
file_for_data = 'eia-weekly.pkl'
# we add the aggregation details to the filename here
file_for_norm_data = 'eia-weekly-norm-data '
file_for_pivot_data = 'eia-weekly-pivot-data '


def build_comparison(df, source_key, source_keys):
    # subtotal
    sub_total_df = get_subtotal_df(df, source_key)
    sub_total_df.columns = [SUBTOTAL]

    # calculation
    calc_total_df = get_components_df(df, source_keys)
    calc_total_df = get_components_sum_df(calc_total_df)
    calc_total_df.columns = [CALCULATED]

    # join, calculation difference and clean
    report_df = sub_total_df.join(calc_total_df)
    report_df['diff'] = report_df[SUBTOTAL] - report_df[CALCULATED]
    report_df.dropna(axis='index', how='any', inplace=True)
    report_df.sort_index(axis='index', inplace=True)

    return report_df


def get_components_df(df, source_keys):
    mask = df[SOURCE_KEY].isin(source_keys)
    return df[mask]


def get_components_sum_df(df):
    return df.groupby(DATE).sum()


def get_components_pivot_df(df):
    df = df.pivot(columns=SOURCE_KEY)
    df.columns = df.columns.droplevel(0)
    return df


def get_subtotal_df(df, source_key):
    mask = df[SOURCE_KEY] == source_key
    sub_total_df = df.loc[mask, [DATE, VALUE]]
    sub_total_df.set_index(DATE, drop=True, inplace=True)
    sub_total_df.columns = [source_key]
    return sub_total_df


def get_all_metadata_for_symbol(metadata_df, source_key):
    return list(metadata_df.loc[metadata_df[SOURCE_KEY] == source_key].values[0])


def get_single_metadata_dict_for_all_symbols(metadata_df, label):
    return dict(zip(metadata_df.index, metadata_df[label].values))


def get_metadata_df(df, columns, selection):
    metadata_df = df[columns].drop_duplicates()
    metadata_df.set_index(SOURCE_KEY, drop=True, inplace=True)
    mask = metadata_df.index.isin(selection)
    return metadata_df[mask]


if __name__ == '__main__':
    data_mode = LOAD
    source_key = 'WTTSTUS1'

    pathfile = os.path.join(path, file_for_data)
    if data_mode == SAVE:
        df = getFlatRawDF(source='eia-weekly')
        df.to_pickle(pathfile)
    elif data_mode == LOAD:
        df = pd.read_pickle(pathfile)
    else:
        raise NotImplementedError

    # select which hierarchy mapping to look at and build comparison to calc diffs
    selection = hierarchy_dict[source_key]
    comparison_df = build_comparison(df, source_key=source_key, source_keys=selection)
    mask = comparison_df.index > dt.date(2015, 1, 1)
    comparison_df[mask].to_clipboard()

    # get all metadata for all keys
    all_keys = selection + [source_key]
    columns = [SOURCE_KEY, 'Description', 'TabDescription', 'Location']
    metadata_df = get_metadata_df(df, columns, all_keys)

    # select just one field here and get a dict mapping source_key to label
    label = 'Description'
    metadata_dict = get_single_metadata_dict_for_all_symbols(metadata_df, label=label)

    # collect timeseries for all the component symbols and pivot
    df_norm = get_components_df(df, selection)
    df_norm.set_index(DATE, drop=True, inplace=True)
    df_norm = df_norm[[SOURCE_KEY, VALUE]]
    df_pivot = get_components_pivot_df(df_norm)

    # get total
    df_total = get_subtotal_df(df, source_key)

    # append the total to the pivot
    df_combo = pd.concat([df_pivot, df_total], axis='columns')

    # rename columns on pivot
    mapper = {k: v.replace('Ending Stocks of ', '') for k, v in metadata_dict.items()}
    mapper = {k: v.replace('Ending Stocks', '') for k, v in mapper.items()}
    df_combo.rename(columns=mapper, inplace=True)

    # sort on date & filter to remove dodgy history
    df_combo.sort_index(inplace=True)
    mask = df_combo.index > dt.date(2015, 1, 1)
    df_combo[mask].to_clipboard()

    # save locally
    suffix = source_key + '.pkl'
    pathfile = os.path.join(path, file_for_norm_data)
    df_norm.to_pickle(pathfile + suffix)
    pathfile = os.path.join(path, file_for_pivot_data)
    df_combo.to_pickle(pathfile + suffix)

    chart_title = metadata_dict[source_key]

    print('hello world')
