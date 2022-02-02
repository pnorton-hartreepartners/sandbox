'''
extract jobs info from visual cron xml

conda install -c anaconda zipfile36
conda install -c anaconda beautifulsoup4
'''

import zipfile
from bs4 import BeautifulSoup
import os
import pandas as pd

servers = ['NYFOAPP01', 'NYFOAPP02', 'NYFOAPP04', 'NYFOAPPLEGACY', 'NYFOOPT01']
date = '2022-01-31'
path = r'\\gateway\hetco\P003\VisualCron'
temp_path = r'c:\temp'
filename_template = 'VCbackup {server} {date}.zip'
columns = ['server', 'cmd_line', 'arguments', 'active']

all_df = pd.DataFrame()
for server in servers:
    filename = filename_template.format(server=server, date=date)
    print(filename)
    pathfile = os.path.join(path, filename)
    try:
        archive = zipfile.ZipFile(pathfile, 'r')
        jobs = archive.read('Jobs.xml')
    except Exception as e:
        print(f'failed file is: {filename}')
        print(f'with error: {e}')
        break

    jobs = jobs.decode('utf-8')
    soup = BeautifulSoup(jobs, 'xml')
    executes = soup.find_all('Execute')

    # save the jobs file locally so you can search/inspect manually
    xml_filename = 'jobs ' + server + '.xml'
    xml_pathfile = os.path.join(temp_path, xml_filename)
    with open(xml_pathfile, mode='w', encoding='utf-8') as f:
        f.write(jobs)

    results = []
    for i, execute in enumerate(executes):
        print(i)
        cmd_line = execute.find('CmdLine').string
        arguments = execute.find('Arguments').string
        active = execute.parent.find('Active').string
        results.append((server, cmd_line, arguments, active))
    df = pd.DataFrame.from_records(results)
    all_df = pd.concat([all_df, df], axis='index')

# tidy up
all_df.columns = columns
for column in columns:
    all_df[column] = all_df[column].str.lower()
all_df['cmd_line'] = all_df['cmd_line'].str.replace('"', '')
all_df.sort_values(columns, inplace=True)

# save it
all_df.to_excel(excel_writer=r'c:\temp\visual_cron_search_results.xlsx', index=False)
all_df.to_clipboard(index=False)
