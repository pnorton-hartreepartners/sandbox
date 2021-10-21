import os
os.environ['IGNITE_HOST_OVERWRITE'] = 'jdbc.dev.mosaic.hartreepartners.com'
os.environ['TSDB_HOST'] = 'tsdb-dev.mosaic.hartreepartners.com'
os.environ['CRATE_HOST'] = 'ttda.cratedb-dev-cluster.mosaic.hartreepartners.com:4200'
os.environ['MOSAIC_ENV'] = 'DEV'

import pandas as pd
from analyst_data_views.common.db_flattener import getFlatRawDF

SOURCE_KEY = 'Sourcekey'
LOAD = 'load'
SAVE = 'save'
SUBTOTAL = 'subtotal'
CALCULATED = 'calculated'
DATE = 'date'
VALUE = 'value'

hierarchy_dict = {
    'WBCRI_NUS_2':  # 'Refiner and Blender Net Input of Gasoline Blending Components'
        ['W_EPOBGRR_YIR_NUS_MBBLD',
         'WO6RI_NUS_2',
         'WO7RI_NUS_2',
         'WO9RI_NUS_2'],
    'W_EPPO6_SAE_NUS_MBBL':  # Ending Stocks of Other Oils
        ['W_EPPA_SAE_NUS_MBBL',
         'W_EPPK_SAE_NUS_MBBL',
         'W_EPL0XP_SAE_NUS_MBBL',
         'WUOSTUS1'],
    'WTTSTUS1':  # Ending Stocks of Crude Oil and Petroleum Products
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
            'W_EPPO6_SAE_NUS_MBBL']
}

path = r'C:\Temp'
file_for_data = 'eia-weekly.pkl'
file_for_norm_data = 'eia-weekly-norm-data.pkl'
file_for_pivot_data = 'eia-weekly-pivot-data.pkl'


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
    return sub_total_df


def get_all_metadata_for_symbol(metadata_df, source_key):
    return list(metadata_df.loc[metadata_df[SOURCE_KEY] == source_key].values[0])


def get_single_metadata_for_all_symbols(metadata_df, label):
    return list(metadata_df[label].values)


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
    result_df = build_comparison(df, source_key=source_key, source_keys=selection)

    # extract metadata from the original dataset
    columns = [SOURCE_KEY, 'Description', 'TabDescription', 'Location']
    metadata_df = get_metadata_df(df, columns, selection)
    metadata = get_single_metadata_for_all_symbols(metadata_df, label='Description')

    # collect ts for all the component symbols and pivot
    df_norm = get_components_df(df, selection)
    df_norm.set_index(DATE, drop=True, inplace=True)
    df_norm = df_norm[[SOURCE_KEY, VALUE]]
    df_pivot = get_components_pivot_df(df_norm)

    # rename columns on pivot
    metadata = [m.replace('Ending Stocks of ', '') for m in metadata]
    metadata = [m.replace('Ending Stocks ', '') for m in metadata]
    mapper = dict(zip(selection, metadata))
    df_pivot.rename(columns=mapper, inplace=True)

    # save locally
    pathfile = os.path.join(path, file_for_norm_data)
    df_norm.to_pickle(pathfile)
    pathfile = os.path.join(path, file_for_pivot_data)
    df_pivot.to_pickle(pathfile)

    print('hello world')
