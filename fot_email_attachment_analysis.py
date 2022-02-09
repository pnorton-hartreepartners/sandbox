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
xls_filepath = os.path.join(folder_results, xls_results)

# columns from new xls
formula_table_columns = ['Product', 'Def code', 'Factor', 'Period', 'Qty']
# mapper from old/otto xls processor where we parse the formula directly
column_name_mapper = {'symbol': 'Def code',
                      'signed_factor': 'Factor',
                      'quantity': 'Qty',
                      'formula_component': 'Formula component'}


# for when we read the formula
operator_mapper = {'+': operator.add,
                   '-': operator.sub,
                   '*': operator.mul,
                   r'/': operator.truediv,
                   '': operator.add
                   }


def get_stems_from_filename(filenames):
    return list(zip(*[file.split('.') for file in filenames]))[0]


def get_file_type_as_dict(filenames):
    # there is a filename foo.xls.broken that we need to exclude here
    return dict([file.split('.') for file in filenames if len(file.split('.')) == 2])


def prepend_pathname(path, filename, file_type):
    return os.path.join(path, filename + '.' + file_type)


def get_formula_from_old_xls(filepath):
    worksheet_df = pd.read_excel(filepath, sheet_name='Data', header=None, index_col=None, engine='xlrd')
    length = 25  # before start of timeseries; varies from workbook to workbook
    string_search = 'Month:'

    # find the start; the first column having a cell containing the string search text
    table_start_row = None
    for index, row in worksheet_df.T.iterrows():
        if string_search in row[:length].values:
            table_start_row = index
            break

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

        # start with the first entry
        string = selection_df.iloc[0].values[0]

        # read the formula directly and parse it here
        pattern = r"(?P<sign>[\+-]?)TimeSeries\('(?P<symbol>\w+)','(?P<start_date>\d{5})','(?P<end_date>\d{5})'\)\*(?P<factor>\d+\.?\d*)"
        p = re.compile(pattern=pattern)
        results = p.finditer(string)
        results = [r.groupdict() for r in results]
        print(string, '\n', results, '\n')

        # apply the sign to the factor and build some reporting fields
        formula_template = "{sign}TimeSeries('{symbol}','{start_date}','{end_date}')*{factor}"
        for r in results:
            r['formula_component'] = formula_template.format(**r)
            r['operator'] = operator_mapper[r['sign']]
            r['factor'] = float(r['factor'])
            r['signed_factor'] = r['operator'](0, r['factor'])
            r['quantity'] = 1
            
        # map the key names here to the standard used in the new xls processor
        return [{column_name_mapper.get(k): r.get(k) for k in r.keys() if column_name_mapper.get(k)}
                for r in results]
    else:
        return []


def get_formula_from_new_xls(filepath):
    worksheet_df = pd.read_excel(filepath, sheet_name='F', header=None, index_col=None, engine='pyxlsb')

    # find this table within the sheet
    length = len(formula_table_columns)

    # find the start
    table_start_row = None
    for index, row in worksheet_df.iterrows():
        if (row[:length].values == formula_table_columns).all():
            table_start_row = index
            break

    # find the end
    table_end_row = None
    if table_start_row:
        for index, row in worksheet_df.iloc[table_start_row:].iterrows():
            if row[0] == 'NOTHING':
                table_end_row = index
                break

    if table_start_row and table_end_row:
        # create a df
        selection_df = worksheet_df.iloc[table_start_row:table_end_row]
        columns = selection_df.iloc[0]
        data = selection_df.iloc[1:].values
        formula_table_df = pd.DataFrame(data=data, columns=columns)
        # remove columns labelled as nan
        mask = formula_table_df.columns.isna()
        formula_table_df = formula_table_df.loc[:, ~mask]
        # create list of dictionaries
        return formula_table_df.to_dict(orient='records')
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


if __name__ == '__main__':
    df2 = get_file_details()

    # add some columns
    df2['formula'] = None
    df2['formula'] = df2['formula'].astype('object')
    df2['def_codes'] = None
    df2['def_codes'] = df2['def_codes'].astype('object')

    func_mapper = {'old': get_formula_from_old_xls,
                   'new': get_formula_from_new_xls
                   }

    # single_file_selection = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline\RB Futs Butterflies.xls'
    # df2 = df2.loc[df2['xls_filepath'] == single_file_selection]

    for index, row in df2.iterrows():
        print(row['xls_filepath'])
        if row['helper'] in ['old', 'new']:
            # get the formula
            f = func_mapper[row['helper']]
            results = f(row['xls_filepath'])
            df2.at[index, 'formula'] = results
            # get the list of hdq codes
            df2.at[index, 'def_codes'] = list(set([result['Def code'] for result in results]))

    # save it locally
    df2.to_excel(excel_writer=xls_filepath, index=False)

    # get hdq symbols
    all_def_codes = []
    for def_code in df2['def_codes'].values:
        if def_code:
            all_def_codes.extend(def_code)
    all_def_codes = list(set(all_def_codes))
    all_def_codes.sort()

    pd.DataFrame(data=all_def_codes).to_clipboard(index=False)

    pass
