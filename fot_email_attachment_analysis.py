'''
objective here is to get all spreadsheets from two locations (with different file types)
and a list of pdfs that were attachments to an email
and match the filename stems to find where the attachments came from
then create a df that associates those pdfs with the source xls as a clickable link
'''

import os
import pandas as pd
import re
import operator

# this is where i dumped the pdfs from one email
folder_attachment = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\work items\jira\TTDA-1499 Charting project\chart example pdf\gasoline email'

# this is the source of those files
folder_old = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline'
folder_new = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report'

# dump the results in an xls here
folder_results = r'c:\temp'
xls_results = 'results.xlsx'
pkl_results = 'results.pkl'
xls_filepath = os.path.join(folder_results, xls_results)
pkl_filepath = os.path.join(folder_results, pkl_results)

# regex to extract standard formula into grouped variables
formula_pattern_old = r"(?P<sign>[\+-]?)TimeSeries\('(?P<symbol>\w+)','(?P<start_date>\d{5})','(?P<end_date>\d{5})'\)\*(?P<factor>\d+\.?\d*)"
formula_pattern_new = r"(?P<factor>[\+-]?\d+\.?\d*)\*TimeSeries\('(?P<symbol>\w+)',(?P<start_date>\d{5}),(?P<end_date>\d{5})\)"
# regex to extract details from symbol
symbol_pattern = r"(?P<symbol_stem>\w+)(?P<contract_year>\d{2})(?P<month_symbol>\w)"


# for when we read the formula
operator_mapper = {'+': operator.add,
                   '-': operator.sub,
                   '*': operator.mul,
                   r'/': operator.truediv,
                   '': operator.add
                   }

example_spreadsheets = {
    'new_xls_example': r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report\Arb CL-CO Fut ($BBL).xlsb',
    'old_xls_example': r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline\Gasoline E-W.xls',
    'failing_xls_example1': r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report\Crs Cmdty RB-C4 ex RVO Swap (CPG).xlsb',
    'failing_xls_example2': r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report\Crs Cmdty RB-C5 ex RVO Swap (CPG).xlsb'
}

hdq_mosaic_symbol_mapping = [
    ('ArgGASFBARA', 'EBOB-S'),
    ('BRTCalSwap', 'BRT-S'),
    ('IPEBRT', 'BRT-F'),
    ('NAPphCIFNWE', 'NAP'),
    ('NYMHO', 'HO-F'),
    ('NYMHO_RINIncl', ''),
    ('NYMRBOB', 'RB-F'),
    ('NYMRBOBCalSwap', 'RB-S'),
    ('NYMWTI', 'WTI-F'),
    ('OPISButneNonTET', ''),
    ('OPISNonTETNGAS', 'C5'),
    ('RINRVOCost', 'RVO_21'),
    ('Sing92Ron', 'MOGAS'),
    ('TC2_USDMT_', 'TC2_USDMT'),
    ('DUBAI', 'DUBAI'),
]


def get_stems_from_filename(filenames):
    return list(zip(*[file.split('.') for file in filenames]))[0]


def get_file_type_as_dict(filenames):
    # there is a filename foo.xls.broken that we need to exclude here
    return dict([file.split('.') for file in filenames if len(file.split('.')) == 2])


def prepend_pathname(path, filename, file_type):
    return os.path.join(path, filename + '.' + file_type)


def parse_string_to_formula_details(string, formula_pattern):
    p = re.compile(pattern=formula_pattern)
    results = p.finditer(string)
    results = [r.groupdict() for r in results]
    print(string, '\n', results, '\n')

    # apply the sign to the factor and build some reporting fields
    formula_template = "{sign}TimeSeries('{symbol}','{start_date}','{end_date}')*{factor}"
    for r in results:
        r['sign'] = '+' if not r.get('sign') else r['sign']
        r['formula_component'] = formula_template.format(**r)
        r['operator'] = operator_mapper[r['sign']]
        r['factor'] = float(r['factor'])
        r['signed_factor'] = r['operator'](0, r['factor'])
        r['quantity'] = 1

    # map the key names here to the standard used in the new xls processor
    return results


def parse_full_symbol_into_parts(formula_details):
    for component in formula_details:
        string = component['symbol']
        p = re.compile(pattern=symbol_pattern)
        results = p.finditer(string)
        # asserts a single result
        [result] = [r.groupdict() for r in results]
        component.update(result)
    return formula_details


def get_formula_from_old_xls(filepath):
    worksheet_df = pd.read_excel(filepath, sheet_name='Data', header=None, index_col=None, engine='xlrd')

    # ============================
    # find the start; the first column having a cell containing the string search text
    string_search = 'Month:'
    length = 25  # before start of timeseries; varies from workbook to workbook

    table_start_row = None
    for index, row in worksheet_df.T.iterrows():
        if string_search in row[:length].values:
            table_start_row = index
            break

    # ============================
    # find the end; a column of nan's
    table_end_row = None
    if table_start_row:
        for index, row in worksheet_df.T.iloc[table_start_row:].iterrows():
            if row[:length].isna().all():
                table_end_row = index
                break

    if table_start_row and table_end_row:
        # create a df
        selection_df = worksheet_df.T.iloc[table_start_row:table_end_row].T
        # find the row where the first column startswith this text
        string_search = 'TimeSeries'
        mask = selection_df.loc[:length, selection_df.columns[0]].str.startswith(string_search).fillna(False)
        selection_df = selection_df.loc[:length].loc[mask].T
        selection_df.columns = ['formula']

        # capture the first entry
        formula_string = selection_df.iloc[0].values[0]

        # read the formula directly and parse it here
        formula_details = parse_string_to_formula_details(string=formula_string, formula_pattern=formula_pattern_old)
        # and break out the symbols
        formula_details = parse_full_symbol_into_parts(formula_details)

        return formula_details

    else:
        return []


def get_formula_from_new_xls(filepath):
    worksheet_df = pd.read_excel(filepath, sheet_name='F', header=None, index_col=None, engine='pyxlsb')

    # ============================
    # find the start; look for these header columns
    formula_table_columns = ['Product', 'Def code', 'Factor', 'Period', 'Qty']
    length = len(formula_table_columns)

    table_start_row = None
    for index, row in worksheet_df.iterrows():
        if (row[:length].values == formula_table_columns).all():
            table_start_row = index
            break

    # ============================
    # find the end; look for a cell containing this string
    string_search = 'NOTHING'

    table_end_row = None
    if table_start_row:
        for index, row in worksheet_df.iloc[table_start_row:].iterrows():
            if row[0] == string_search:
                table_end_row = index
                break

    if table_start_row and table_end_row:
        # create a df
        selection_df = worksheet_df.iloc[table_start_row:table_end_row]
        columns = selection_df.iloc[0]
        data = selection_df.iloc[1:].values
        formula_table_df = pd.DataFrame(data=data, columns=columns)
        # remove columns labelled as nan; but actually these are also related definitions
        mask = formula_table_df.columns.isna()
        formula_table_df = formula_table_df.loc[:, ~mask]

        # get the complete formula and parse it; from this single column
        formula_string = ''.join(formula_table_df['Formula component'].values)

        # read the formula directly and parse it here
        formula_details = parse_string_to_formula_details(string=formula_string, formula_pattern=formula_pattern_new)
        # and break out the symbols
        formula_details = parse_full_symbol_into_parts(formula_details)

        return formula_details
    else:
        return []


def get_file_details():
    # attachments
    pdfs = os.listdir(folder_attachment)
    stems = get_stems_from_filename(pdfs)
    attachment_stems = [stem[:-11] for stem in stems]
    attachment_df = pd.DataFrame(data=attachment_stems, columns=['attachment'])

    # get all filenames in old-style (otto) xls location
    xlss_old = os.listdir(folder_old)
    xlss_old_stems = get_stems_from_filename(xlss_old)
    xlss_old_file_types_dict = get_file_type_as_dict(xlss_old)
    xls_old_df = pd.DataFrame(data=xlss_old_stems, columns=['xls_old'])

    # get all filenames in new-style xls location
    xlss_new = os.listdir(folder_new)
    xlss_new_stems = get_stems_from_filename(xlss_new)
    xlss_new_file_types_dict = get_file_type_as_dict(xlss_new)
    xls_new_df = pd.DataFrame(data=xlss_new_stems, columns=['xls_new'])

    # merge everything
    df1 = pd.merge(attachment_df, xls_old_df, how='left', left_on='attachment', right_on='xls_old')
    df2 = pd.merge(df1, xls_new_df, how='left', left_on='attachment', right_on='xls_new')

    # if neither source matches the attachment name then we have a problem
    df2['bad'] = df2[['xls_old', 'xls_new']].isna().all(axis='columns')

    # create the full clickable pathname
    mask = ~df2['xls_old'].isna()
    df2.loc[mask, 'xls_filepath'] = df2.loc[mask, 'xls_old'] \
        .apply(lambda x: prepend_pathname(folder_old, x, xlss_old_file_types_dict[x]))
    df2.loc[mask, 'helper'] = 'old'

    mask = ~df2['xls_new'].isna()
    df2.loc[mask, 'xls_filepath'] = df2.loc[mask, 'xls_new'] \
        .apply(lambda x: prepend_pathname(folder_new, x, xlss_new_file_types_dict[x]))
    df2.loc[mask, 'helper'] = 'new'

    return df2


func_mapper = {'old': get_formula_from_old_xls,
               'new': get_formula_from_new_xls
               }


def build_base_report(df):
    # add some columns; initialise to accept lists/dictionaries
    df['formula'] = None
    df['formula'] = df['formula'].astype('object')
    df['def_codes'] = None
    df['def_codes'] = df['def_codes'].astype('object')

    for index, row in df.iterrows():
        print('\n================')
        print(row['xls_filepath'])
        if row['helper'] in ['old', 'new']:
            # get the formula
            f = func_mapper[row['helper']]
            results = f(row['xls_filepath'])
            df.at[index, 'formula'] = results
            # get the list of hdq codes
            df.at[index, 'def_codes'] = list(set([result['symbol_stem'] for result in results]))
    return df


def get_unique_symbols(df):
    all_def_codes = []
    for def_code in df['def_codes'].values:
        if def_code:
            all_def_codes.extend(def_code)
    all_def_codes = list(set(all_def_codes))
    all_def_codes.sort()
    return all_def_codes


if __name__ == '__main__':
    build_from_scratch_selection = False
    build_from_single_spreadsheet_selection = False
    build_from_single_spreadsheet_path = example_spreadsheets['old_xls_example']

    if build_from_scratch_selection:
        df2 = get_file_details()
        if build_from_single_spreadsheet_selection:
            df2 = df2.loc[df2['xls_filepath'] == build_from_single_spreadsheet_path]
        df2 = build_base_report(df2)
        symbols = get_unique_symbols(df2)

        # save to excel
        with pd.ExcelWriter(xls_filepath, mode='w') as f:
            df2.to_excel(excel_writer=f, sheet_name='reports', index=False)
            pd.DataFrame(data=symbols).to_excel(excel_writer=f, sheet_name='symbols', index=False)

        # save to pickle
        df2.to_pickle(pkl_filepath)

    else:
        df2 = pd.read_pickle(pkl_filepath)
        pass
