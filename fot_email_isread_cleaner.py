'''
IT ran a report to identify email read-receipts for reports that are emailed to users
this script accesses the report and cleans the data
lots of emails include a date in the subject; need to clean that
'''

import os
import pandas as pd
from dateutil.parser import parse

folder_stem = r'\\hetco.com\htp\IT\Reports\Report Mailer_ReportsOnly'
folders = [r'01.31.2022-1400PM']
file = r'Results.csv'
pathfiles = [os.path.join(folder_stem, folder, file) for folder in folders]

# dump the results here
folder_name = r'c:\temp'
xls_report = 'fot_email_isread_results.xlsx'
xls_filepath = os.path.join(folder_name, xls_report)

columns = ['Subject or Title',
           'Subject or Title... cleaned',
           'Recipients in To line',
           'Sent',
           'Has Attachments',
           'Is Read',
           ]

subject_column = 'Subject or Title'
cleaned_subject_column = 'Subject or Title... cleaned'
fot_reports_email = 'FrontOfficeTechReports <FrontOfficeTechReports@Hartreepartners.com>'
recipients_in_line = 'Recipients in {who} line'
who_list = ['To', 'Cc', 'Bcc']


def parse_date(x):
    try:
        remaining_texts = parse(x, fuzzy_with_tokens=True)[1]
        return ''.join(remaining_texts).lstrip().rstrip()
    except Exception as e:
        print(e)
        return x


if __name__ == '__main__':
    for pathfile in pathfiles:
        # open it
        df = pd.read_csv(pathfile)

        # clean the date from the subject to group similar emails
        df[cleaned_subject_column] = df[subject_column].apply(lambda x: parse_date(x))

        # check if email is in list
        recipients_in_lines = [recipients_in_line.format(who=who) for who in who_list]
        df['fot_reports_email'] = df[recipients_in_lines].apply(lambda row: (row.str.contains(fot_reports_email)).any(),
                                                                axis='columns')

        # save it
        columns = columns + ['fot_reports_email'] + recipients_in_lines
        df[columns].to_excel(excel_writer=xls_filepath, index=False)
