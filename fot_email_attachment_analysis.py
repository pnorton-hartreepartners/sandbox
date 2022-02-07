import os
import pandas as pd

# this is where i dumped the pdfs from one email
folder_attachment = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\work items\jira\TTDA-1499 Charting project\chart example pdf\gasoline email'

# this is the source of those files
folder_old = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline'
folder_new = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report'
file_type_old = '.xls'
file_type_new = '.xlsb'


def get_stems_from_filename(filenames):
    return list(zip(*[file.split('.') for file in filenames]))[0]


def prepend_pathname(path, filename, file_type):
    return os.path.join(path, filename + file_type)


# attachments
pdfs = os.listdir(folder_attachment)
stems = get_stems_from_filename(pdfs)
attachment_stems = [stem[:-11] for stem in stems]
attachment_df = pd.DataFrame(data=attachment_stems, columns=['attachment'])

# get all filenames in old-style (otto) xls location
xlss_old = os.listdir(folder_old)
xlss_old_stems = get_stems_from_filename(xlss_old)
xls_old_df = pd.DataFrame(data=xlss_old_stems, columns=['xls_old'])

# get all filenames in new-style xls location
xlss_new = os.listdir(folder_new)
xlss_new_stems = get_stems_from_filename(xlss_new)
xls_new_df = pd.DataFrame(data=xlss_new_stems, columns=['xls_new'])

# merge everything
df1 = pd.merge(attachment_df, xls_old_df, how='left', left_on='attachment', right_on='xls_old')
df2 = pd.merge(df1, xls_new_df, how='left', left_on='attachment', right_on='xls_new')

# if neither source matches the attachment name then we have a problem
df2['bad'] = df2[['xls_old', 'xls_new']].isna().all(axis='columns')

# create the full clickable pathname
mask = ~df2['xls_old'].isna()
df2.loc[mask, 'xls_filepath'] = df2.loc[mask, 'xls_old']\
    .apply(lambda x: prepend_pathname(folder_old, x, file_type_old))

mask = ~df2['xls_new'].isna()
df2.loc[mask, 'xls_filepath'] = df2.loc[mask, 'xls_new']\
    .apply(lambda x: prepend_pathname(folder_new, x, file_type_new))

df2.to_clipboard()
pass
