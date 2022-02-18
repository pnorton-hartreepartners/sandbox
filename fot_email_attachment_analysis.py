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
import datetime as dt
from dateutil.relativedelta import relativedelta

# this is where i dumped the pdfs from one email
folder_attachment = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\work items\jira\TTDA-1499 Charting project\chart example pdf\gasoline email'

# this is the source of those files
folder_old = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline'
folder_new = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report'

# dump the results in an xls/pkl here
folder_name = r'c:\temp'

pkl_scrape = 'results.pkl'   # result of the initial scrapes of all the xls
xls_report = 'results.xlsx'  # the giant df report
xls_grafana = 'chart_config2.xlsx'  # input into grafana charting

pkl_scrape_filepath = os.path.join(folder_name, pkl_scrape)
xls_report_filepath = os.path.join(folder_name, xls_report)
xls_grafana_filepath = os.path.join(folder_name, xls_grafana)

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
    'timespread_example': r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline\RB Futs Butterflies.xls',
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


def month_code_mapping():
    month_codes = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
    month_numbers = range(1, len(month_codes)+1)
    return zip(month_codes, month_numbers)


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


def build_contract_date(year, month_code):
    mapper = {k: v for (k, v) in month_code_mapping()}
    year = 2000 + int(year)
    assert 2000 <= year <= 2030
    month = mapper[month_code]
    return dt.datetime(year=year, month=month, day=1).date()


def build_mosaic_formula(df):
    mapper = {k.lower(): v for (k, v) in hdq_mosaic_symbol_mapping}

    # add some columns; initialise to accept lists/dictionaries
    df['mosaic_formula'] = None
    df['mosaic_formula'] = df['mosaic_formula'].astype('object')
    df['time_spreads'] = None
    df['time_spreads'] = df['time_spreads'].astype('object')
    for index, row in df.iterrows():
        if row['formula']:
            component_list = []
            for component in row['formula']:
                component_dict = {}
                component_dict.update({'product': mapper[component['symbol_stem'].lower()]})
                component_dict.update({'front_date': build_contract_date(year=component['contract_year'], month_code=component['month_symbol'])})
                component_dict.update({'factor': component['factor']})
                component_list.append(component_dict)

            # rebase the contract periods to current front month
            front_dates = [component['front_date'] for component in component_list]
            min_date = min(front_dates)
            front_month = dt.date.today() - dt.timedelta(days=dt.date.today().day - 1) + relativedelta(months=+1)
            month_spreads = [relativedelta(dt2=min_date, dt1=component['front_date']).months for component in component_list]
            front_month_rebase = [front_month + relativedelta(months=m) for m in month_spreads]
            for i, component in enumerate(component_list):
                component['front_date_rebase'] = front_month_rebase[i]
            component_list.sort(key=lambda x: x['front_date_rebase'])
            df.at[index, 'mosaic_formula'] = component_list
            df.at[index, 'time_spreads'] = month_spreads
            df.at[index, 'symbol_map_healthy'] = not(bool(len([c['product'] for c in component_list if c['product'] == ''])))

    component_counts = df['mosaic_formula'].apply(lambda x: len(x) if x else 0)
    month_counts = df['time_spreads'].apply(lambda x: len(set(x)) if x else 0)
    product_counts = df['mosaic_formula'].apply(lambda x: len(set(component['product'] for component in x)) if x else 0)
    combo = zip(component_counts, month_counts.values, product_counts.values)

    def _chart_type_translator(tt):
        component_count, month_count, product_count = tt
        if tt == (0, 0, 0):
            return 'empty'
        elif tt == (1, 1, 1):
            return 'outright'
        elif component_count == 2 and month_count == 2 and product_count == 1:
            return 'timespread'
        elif month_count == 1 and product_count > 1:
            return 'productspread'
        elif component_count == 2 and month_count == 2 and product_count == 2:
            return 'diagspread'
        elif component_count == 3 and month_count == 3 and product_count == 1:
            return 'fly'
        elif component_count == 4 and month_count == 2 and product_count == 2:
            return 'boxspread'
        else:
            return 'unidentified'

    df['component_count'] = component_counts.values
    df['product_count'] = product_counts.values
    df['month_count'] = month_counts.values
    df['chart_type'] = list(map(_chart_type_translator, combo))
    return df


def build_grafana_expressions_dict(df2):

    def _outright_component(component):
        front_date = int(component['front_date_rebase'].strftime('%Y%m'))
        matching_keys = ['factor', 'product']
        new_dict = {k: component[k] for k in matching_keys}
        new_dict.update({'front': front_date, 'middle': None, 'back': None})
        new_dict.update({'product_id': None})
        return new_dict

    def _timespread(formula):
        mapping = _outright_component(formula[0])
        back_date = int(formula[1]['front_date_rebase'].strftime('%Y%m'))
        mapping.update({'back': back_date})
        return [mapping]

    def _call_correct_func(chart_type, mosaic_formula):
        if not mosaic_formula:
            return []
        elif chart_type == 'timespread':
            return _timespread(mosaic_formula)
        else:
            return [_outright_component(f) for f in mosaic_formula]

    df2['grafana_expressions'] = df2.apply(
        lambda x: _call_correct_func(x['chart_type'], x['mosaic_formula']),
        axis='columns').values
    return df2


def get_uom_from_filename(df):
    # use this to update mapping  --> unique_uoms = uoms.drop_duplicates().dropna().values
    # mapping from name in title to grafana standard
    source_labels = ['$BBL', 'CPG', '$MT']
    grafana_labels = ['bbl', 'gl', 'mt']
    mapper = dict(zip(source_labels, grafana_labels))
    # uom is contained in brackets
    pattern = r'(?P<uom>\(.+\))'
    uoms = df['attachment'].str.extract(pat=pattern, expand=False)
    # remove brackets
    uoms = uoms.str[1:-1]
    # apply mapping
    df['uom'] = uoms.map(mapper)
    # apply default
    df2['uom'].fillna(value='bbl', axis='index', inplace=True)
    return df


def build_chart_title(df):
    df['title'] = df['attachment'] + ' {front}'
    mask = df['chart_type'] == 'timespread'
    df.loc[mask, 'title'] = df.loc[mask, 'attachment'] + ' {front} - {back}'
    return df


def build_grafana_panels_dict(df):
    seasonal = 5  # years of history on chart
    extend_tenor = 'month'
    extend_count = 12  # months forward

    # add new column; initialise to accept lists/dictionaries
    df['grafana_panels'] = None
    df['grafana_panels'] = df['grafana_panels'].astype('object')

    for index, row in df.iterrows():
        title = row['title']
        df.at[index, 'grafana_panels'] = {'panel_id': index,
                                'title': title,
                                'seasonal': seasonal,
                                'extend_tenor': extend_tenor,
                                'extend_count': extend_count
                                }
    return df


def build_grafana_products_dict(df):
    # add new column; initialise to accept lists/dictionaries
    df['grafana_products'] = None
    df['grafana_products'] = df['grafana_products'].astype('object')

    for index, row in df.iterrows():
        df.at[index, 'grafana_products'] = {'panel_id': row['panel_id'],
                                          'currency': 'USD',
                                          'unit': '*',
                                          'legend': 'x',
                                          'axis': 'y1'}
    return df


def build_panels_df(df):
    # remove rows where symbol mapping isnt complete
    mask = df['symbol_map_healthy'] == True
    df = df[mask]
    # create the new df
    panels_df = pd.DataFrame.from_records(df['grafana_panels'].values)
    panels_df.set_index('panel_id', drop=True, inplace=True)
    # assume one entry per row of 'grafana_panels' but check here
    assert panels_df.shape[0] == df.shape[0]
    return panels_df


def build_products_df(df):
    products_df = pd.DataFrame.from_records(df['grafana_products'].values)
    products_df.index.name = 'product_id'
    return products_df


def build_expressions_df(df):
    all_df = pd.DataFrame()
    for index, row in df.iterrows():
        product_id = row['product_id']
        # add the product id to every dict in the list of expressions
        for expression in row['grafana_expressions']:
            expression.update({'product_id': product_id})
        df = pd.DataFrame.from_records(row['grafana_expressions'])
        all_df = pd.concat([all_df, df], axis='index')
    all_df.reset_index(drop=True, inplace=True)
    all_df.index.name = 'expression_id'
    return all_df


def add_panel_id_to_report(df):
    for index, row in df.iterrows():
        df.at[index, 'panel_id'] = row['grafana_panels']['panel_id']
    df = df.astype({'panel_id': int})
    return df


def add_product_id_to_report(df, products_df):
    products_df.reset_index(drop=False, inplace=True)
    combo_df = pd.merge(df, products_df[['product_id', 'panel_id']], left_on='panel_id', right_on='panel_id')
    products_df.set_index('product_id', drop=True, inplace=True)
    return combo_df


if __name__ == '__main__':
    build_from_scratch_selection = False

    # for debugging
    build_from_single_spreadsheet_selection = False
    report_from_single_spreadsheet_selection = False
    build_from_single_spreadsheet_path = example_spreadsheets['timespread_example']
    report_from_single_spreadsheet_path = example_spreadsheets['timespread_example']

    if build_from_scratch_selection:
        df2 = get_file_details()
        if build_from_single_spreadsheet_selection:
            df2 = df2.loc[df2['xls_filepath'] == build_from_single_spreadsheet_path]
        df2 = build_base_report(df2)
        df2.to_pickle(pkl_scrape_filepath)
    else:
        df2 = pd.read_pickle(pkl_scrape_filepath)

    if report_from_single_spreadsheet_selection:
        df2 = df2.loc[df2['xls_filepath'] == report_from_single_spreadsheet_path]
    symbols = get_unique_symbols(df2)
    df2 = build_mosaic_formula(df2)

    # hack hack hack; doing this excludes results from the final report and hides the mapping failures
    df2 = df2[df2['symbol_map_healthy']==True]

    df2 = build_grafana_expressions_dict(df2)
    # df2 = get_uom_from_filename(df2)
    df2 = build_chart_title(df2)

    # panels df
    df2 = build_grafana_panels_dict(df2)
    panels_df = build_panels_df(df2)
    df2 = add_panel_id_to_report(df2)

    # products df
    df2 = build_grafana_products_dict(df2)
    products_df = build_products_df(df2)
    df2 = add_product_id_to_report(df2, products_df)

    # expressions df
    expressions_df = build_expressions_df(df2)

    # save grafana dfs
    with pd.ExcelWriter(xls_grafana_filepath, mode='w') as f:
        panels_df.to_excel(excel_writer=f, sheet_name='panels', index=True)
        products_df.to_excel(excel_writer=f, sheet_name='products', index=True)
        expressions_df.to_excel(excel_writer=f, sheet_name='expressions', index=True)

    # save report
    with pd.ExcelWriter(xls_report_filepath, mode='w') as f:
        df2.to_excel(excel_writer=f, sheet_name='reports', index=False)
        pd.DataFrame(data=symbols).to_excel(excel_writer=f, sheet_name='symbols', index=False)
    pass
