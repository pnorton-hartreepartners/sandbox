'''
objective here is to get all spreadsheets from two locations (with different file types)
and a list of pdfs that were attachments to an email
and match the filename stems to find where the attachments came from
then create a df that associates those pdfs with the source xls as a clickable link
'''

import os
import pandas as pd
import re

# this is where i dumped the pdfs from one email
folder_attachment = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\work items\jira\TTDA-1499 Charting project\chart example pdf\gasoline email'

# this is the source of those files
folder_old = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline'
folder_new = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report'

# dump the results in an xls here
folder_results = r'c:\temp'
xls_results = 'results.xlsx'
xls_filepath = os.path.join(folder_results, xls_results)

def get_stems_from_filename(filenames):
    return list(zip(*[file.split('.') for file in filenames]))[0]


def get_file_type_as_dict(filenames):
    # there is a filename foo.xls.broken that we need to exclude here
    return dict([file.split('.') for file in filenames if len(file.split('.')) == 2])


def prepend_pathname(path, filename, file_type):
    return os.path.join(path, filename + '.' + file_type)


def get_formula_from_old_xls(filepath):
    worksheet_df = pd.read_excel(filepath, sheet_name='Data', header=None, index_col=None, engine='xlrd')
    length = 10  # kinda arbitrary cutoff
    string_search = 'Month:'

    # find the start
    table_start_row = None
    for index, row in worksheet_df.T.iterrows():
        if string_search in row[:length].values:
            table_start_row = index
            break

    # find the end
    table_end_row = None
    if table_start_row:
        for index, row in worksheet_df.T.iloc[table_start_row:].iterrows():
            if row[:length].isna().all():
                table_end_row = index
                break

    if table_start_row and table_end_row:
        # create a df
        selection_df = worksheet_df.T.iloc[table_start_row:table_end_row].T
        # look for this string in the first column
        string_search = 'AUTO_CALC'
        mask = selection_df.loc[:, selection_df.columns[0]].values == string_search
        end_of_selection = mask.nonzero()[0][0]
        selection_df = selection_df.iloc[:end_of_selection].to_dict(orient='records')

        string = selection_df.iloc[14].iloc[0]
        pattern = r'(\+)|(\-)'
        # this split captures the plus or minus operator
        rr = re.split(pattern, string)
        rr = [r for r in rr if r]  # exclude None
        # now we need to recombine the operators
        



    else:
        return []


def get_formula_from_new_xls(filepath):
    worksheet_df = pd.read_excel(filepath, sheet_name='F', header=None, index_col=None, engine='pyxlsb')

    # find this table within the sheet
    formula_table_columns = ['Product', 'Def code', 'Factor', 'Period', 'Qty']
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
