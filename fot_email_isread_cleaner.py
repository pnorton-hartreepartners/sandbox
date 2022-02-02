import os
import pandas as pd
from dateutil.parser import parse

folder_stem = r'\\hetco.com\htp\IT\Reports\Report Mailer_ReportsOnly'
folders = [r'01.31.2022-1400PM']
file = r'Results.csv'
pathfiles = [os.path.join(folder_stem, folder, file) for folder in folders]

columns = ['Subject or Title',
           'Subject or Title... cleaned',
           'Recipients in To line',
           'Sent',
           'Has Attachments',
           'Is Read',
           ]


def f(x):
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
        subject_column = 'Subject or Title'
        cleaned_subject_column = 'Subject or Title... cleaned'
        df[cleaned_subject_column] = df[subject_column].apply(lambda x: f(x))

        # save it
        df[columns].to_excel(excel_writer=r'c:\temp\results.xlsx', index=False)
