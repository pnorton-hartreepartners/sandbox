'''
there's an old webpage with over a thousand links to files and charts
this script accesses all the file locations referenced on the website
and reports the latest modified date and latest access date
'''
from bs4 import BeautifulSoup
from pprint import pprint as pp
import requests
import pandas as pd
import os
import datetime as dt

# this is the url to the web catalogue of reports
url = r'http://nyweb01/HdqReports/charts.aspx'

# dump the results here
folder_name = r'c:\temp'
xls_report = 'fot_catalogue_file_search.xlsx'
xls_filepath = os.path.join(folder_name, xls_report)


def get_all_links_for_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.find_all('a', string='Open File Location')


def get_all_folder_locations(tags):
    locations = [x.attrs['href'].lower() for x in tags if x.attrs['href'].startswith(r'file://')]
    locations = list(set(locations))
    locations.sort()
    # remove file: prefix and flip the slash so we can create a link for file explorer
    return [location.replace('/', '\\')[5:] for location in locations]


def initialise_dict_of_file_details(locations):
    # access all the file locations and get file details
    folder_detailss = {}
    for location in locations:
        try:
            folder_details = list(os.scandir(location))
            folder_detailss.update({location: {'details': folder_details}})
        except (PermissionError, FileNotFoundError) as err:
            folder_detailss.update({location: {'details': err}})
    return folder_detailss


def populate_dict_of_file_details(folder_details):
    # there are lots of other file types we're not interested in
    report_file_types = ['xlsx',  'xlsb', 'xlsm',  'xls', 'pdf']
    locations = list(folder_details.keys())
    all_file_types = []
    for location in locations:
        details = folder_details[location]['details']
        if isinstance(details, list):
            files = [obj for obj in details if obj.is_file()]
    
            file_types = [file.name.split('.')[-1] for file in files]
            all_file_types.extend(file_types)
    
            # we're only interested in spreadsheets and pdfs
            files = [file for file in files if file.name.split('.')[-1].lower() in report_file_types]
    
            access_times = [file.stat().st_atime for file in files]
            modified_times = [file.stat().st_mtime for file in files]
    
            if access_times:
                folder_details[location]['latest_access_time'] = dt.datetime.fromtimestamp(max(access_times))
            if modified_times:
                folder_details[location]['latest_modified_time'] = dt.datetime.fromtimestamp(max(modified_times))
            folder_details[location]['file_count'] = len(files)
    return folder_details, all_file_types


def build_df_of_results(folder_details):
    locations = list(folder_details.keys())
    data = [{k: folder_details[location].get(k)
            for k in ['file_count', 'latest_access_time', 'latest_modified_time']}
            for location in locations]
    df = pd.DataFrame(data, locations)
    df.sort_index(inplace=True)
    return df


if __name__ == '__main__':
    # build report and save locally
    all_links = get_all_links_for_url(url=url)
    locations = get_all_folder_locations(tags=all_links)
    folder_details = initialise_dict_of_file_details(locations=locations)
    folder_details, all_file_types = populate_dict_of_file_details(folder_details)
    df = build_df_of_results(folder_details)
    df.to_excel(excel_writer=xls_filepath)
    # done

    # from here, its just faffing
    df.to_clipboard(index=False)
    total = len(all_links)
    pp(locations, width=200)
    print(total)
    all_file_types = list(set(all_file_types))
    # investigate a single folder location
    location = r'\\gateway\hetco\p003\tasks\excel reports\doe gasoline charts'
    pp(folder_details[location])
    print()
