import os
from zipfile import ZipFile
from bs4 import BeautifulSoup

# ===========================================================
# find the xlsx and rename as zip

rename_file = False

path = r'c:\temp'
filename = r'hdq search and replace.xlsx'
filename_and_path = os.path.join(path, filename)

zip_extension = '.zip'
zip_filename_and_path = filename_and_path.split('.')[0] + zip_extension

if rename_file:
    os.rename(filename_and_path, zip_filename_and_path)

# ===========================================================
# open the zip file and save the worksheets to a dict

worksheets = {}
with ZipFile(zip_filename_and_path) as zf:
    for file in zf.namelist():
        if file.startswith(r'xl/worksheets') and file.endswith(r'.xml'):
            with zf.open(file) as f:
                data = f.readlines()
                worksheets[f.name] = [data]
                print(f.name)


# ===========================================================
# select a worksheet

worksheet_name = 'xl/worksheets/sheet1.xml'
ws = worksheets[worksheet_name][0][1]


# ===========================================================
# and search for the required formulae

soup = BeautifulSoup(ws, 'xml')
sheet_data = soup.find('sheetData')

value_tag = 'v'
values = sheet_data.find_all(value_tag)
value_search_string = r'TimeSeries'

formula_tag = 'f'
formulae = sheet_data.find_all(formula_tag)
formula_search_string = '_xll.Hdq'


def get_all_strings_starting_with(results, search_string):
    list_of_tags = []
    for r in results:
        if r.string.startswith(search_string):
            list_of_tags.append(r)
            print(f'cell: {r.parent.attrs["r"]} = {r.string}')
    return list_of_tags


hdq_values = get_all_strings_starting_with(results=values, search_string=value_search_string)
hdq_formulae = get_all_strings_starting_with(results=formulae, search_string=formula_search_string)

hdq_value = hdq_values[0]


print()

