from bs4 import BeautifulSoup
from pprint import pprint as pp
import requests
import pandas as pd
import os
import datetime as dt

url = r'http://nyweb01/HdqReports/charts.aspx'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
all_links = soup.find_all('a', string='Open File Location')
total = len(all_links)

locations = [x.attrs['href'].lower() for x in all_links if x.attrs['href'].startswith(r'file://')]
locations = list(set(locations))
locations.sort()
# remove file: prefix and flip the slash so we can create a link for file explorer
locations = [location.replace('/', '\\')[5:] for location in locations]

pp(locations, width=200)
print(total)
print(locations)


# access all the file locations and get file details
folder_detailss = {}
for location in locations:
    try:
        folder_details = list(os.scandir(location))
        folder_detailss.update({location: {'details': folder_details}})
    except (PermissionError, FileNotFoundError) as err:
        folder_detailss.update({location: {'details': err}})


# get file details from files and save in list of dicts
report_file_types = ['xlsx',  'xlsb', 'xlsm',  'xls', 'pdf']
all_file_types = []
for location in locations:
    details = folder_detailss[location]['details']
    if isinstance(details, list):
        files = [obj for obj in details if obj.is_file()]

        file_types = [file.name.split('.')[-1] for file in files]
        all_file_types.extend(file_types)

        # we're only interested in spreadsheets and pdfs
        files = [file for file in files if file.name.split('.')[-1].lower() in report_file_types]

        access_times = [file.stat().st_atime for file in files]
        modified_times = [file.stat().st_mtime for file in files]

        if access_times:
            folder_detailss[location]['latest_access_time'] = dt.datetime.fromtimestamp(max(access_times))
        if modified_times:
            folder_detailss[location]['latest_modified_time'] = dt.datetime.fromtimestamp(max(modified_times))
        folder_detailss[location]['file_count'] = len(files)

all_file_types = list(set(all_file_types))


# build df
data = [{k: folder_detailss[location].get(k) for k in ['file_count', 'latest_access_time', 'latest_modified_time']}
        for location in locations]

df = pd.DataFrame(data, locations)
df.sort_index(inplace=True)
df.to_clipboard()

location = r'\\gateway\hetco\p003\tasks\excel reports\doe gasoline charts'
pp(folder_detailss[location])

pass
print()
