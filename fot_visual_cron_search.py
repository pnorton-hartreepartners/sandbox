'''
extract jobs info from visual cron xml
deliver an xls report that shows the job details including whether
its active or not

conda install -c anaconda zipfile36
conda install -c anaconda beautifulsoup4
'''

import zipfile
from bs4 import BeautifulSoup
import os
import pandas as pd

date = '2022-01-31'
temp_path = r'c:\temp'
columns = ['server', 'cmd_line', 'arguments', 'active']

# dump the results in an xls here
xls_report = 'fot_visual_cron_search_analysis.xlsx'
xls_filepath = os.path.join(temp_path, xls_report)

servers = ['NYFOAPP01', 'NYFOAPP02', 'NYFOAPP04', 'NYFOAPPLEGACY', 'NYFOOPT01']


def extract_from_zip():
    zip_filename_template = 'VCbackup {server} {date}.zip'
    zip_path = r'\\gateway\hetco\P003\VisualCron'
    jobs_filename = 'Jobs.xml'

    jobs_dict = {}
    for server in servers:
        zip_filename = zip_filename_template.format(server=server, date=date)
        zip_pathfile = os.path.join(zip_path, zip_filename)
        try:
            archive = zipfile.ZipFile(zip_pathfile, 'r')
            jobs = archive.read(jobs_filename)
            jobs_dict[server] = {}
            jobs_dict[server].update({'jobs': jobs})
        except Exception as e:
            print(f'failed file is: {jobs_filename}')
            print(f'with error: {e}')
            break
    return jobs_dict


def get_execution_tags(jobs_dict):
    for server, jobs in jobs_dict.items():
        jobs = jobs['jobs'].decode('utf-8')
        soup = BeautifulSoup(jobs, 'xml')
        executes = soup.find_all('Execute')
        jobs_dict[server].update({'executes': executes})
    return jobs_dict


def save_files_for_inspection(jobs_dict):
    for server, jobs in jobs_dict.items():
        jobs = jobs['jobs'].decode('utf-8')
        # save the jobs file locally so you can search/inspect manually
        xml_filename = 'jobs ' + server + '.xml'
        xml_pathfile = os.path.join(temp_path, xml_filename)
        with open(xml_pathfile, mode='w', encoding='utf-8') as f:
            f.write(jobs)


def load_files_for_inspection(servers):
    for server in servers:
        xml_filename = 'jobs ' + server + '.xml'
        xml_pathfile = os.path.join(temp_path, xml_filename)
        with open(xml_pathfile, mode='r', encoding='utf-8') as f:
            yield f.read()


def build_df_report(jobs_dict):
    all_df = pd.DataFrame()
    for server, jobs in jobs_dict.items():
        executes = jobs_dict[server]['executes']
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
    return all_df


if __name__ == '__main__':
    extract_and_find_selection = True
    collect_from_local_xml = True

    if extract_and_find_selection:
        jobs_dict = extract_from_zip()
        jobs_dict = get_execution_tags(jobs_dict)
        save_files_for_inspection(jobs_dict)
        df = build_df_report(jobs_dict)
        df.to_excel(excel_writer=xls_filepath, index=False)

    if collect_from_local_xml:
        x = load_files_for_inspection(servers=servers)
        print(next(x))
        pass
        print()

