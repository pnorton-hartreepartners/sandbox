import os
from shutil import copyfile
from zipfile import ZipFile
from bs4 import BeautifulSoup

mosaic_config = {
    'Formula': 'Mos.GetSettlementTS',
    'InstrumentKey': '"B 202301"',
    'Exchange': '"ICE"',
    'StartDate': '"01/06/2022"',
    'EndDate': '"30/06/2022"',
}

hdq_config = {
    'Function': 'TimeSeries',
    'Formula': '_xll.Hdq',
    'QuoteDef': 'IPEBRT23F',
    'StartDate': '01/06/2022',
    'EndDate': '30/06/2022',
}

# ===========================================================
# find the xlsx and rename as zip

rename_file = False

path = r'c:\temp'
filename = r'hdq search and replace2.xlsx'
filename_and_path = os.path.join(path, filename)

zip_extension = '.zip'
zip_filename_and_path = filename_and_path.split('.')[0] + zip_extension

# change the file extension from xlsx to zip
copyfile(filename_and_path, zip_filename_and_path)

# prepare names for updated version for use later
updated_filename = r'hdq search and replace2_updated.xlsx'
updated_filename_and_path = os.path.join(path, updated_filename)

# ===========================================================
# open the zip file and save the worksheets to a dict

worksheets = {}
with ZipFile(zip_filename_and_path) as zf:
    for file in zf.namelist():
        if file.startswith(r'xl/worksheets') and file.endswith(r'.xml'):
            with zf.open(file) as f:
                worksheets[f.name] = f.readlines()
                print(f.name)


# ===========================================================
# select a worksheet

worksheet_name = 'xl/worksheets/sheet1.xml'
ws = worksheets[worksheet_name][1]


# ===========================================================
# and search for the required formulae

soup = BeautifulSoup(ws, 'xml')
sheet_data = soup.find('sheetData')

value_tag = 'v'
values = sheet_data.find_all(value_tag)
value_search_string = hdq_config['Function']

formula_tag = 'f'
formulae = sheet_data.find_all(formula_tag)
formula_search_string = hdq_config['Formula']


def get_all_strings_starting_with(results, search_string):
    list_of_tags = []
    for r in results:
        if r.string.startswith(search_string):
            list_of_tags.append(r)
            print(f'cell: {r.parent.attrs["r"]} = {r.string}')
    return list_of_tags


hdq_values = get_all_strings_starting_with(results=values, search_string=value_search_string)
hdq_formulae = get_all_strings_starting_with(results=formulae, search_string=formula_search_string)

# ===========================================================
# pretend to do some mapping here

# get the definition of a single function call
hdq_value = hdq_values[0]
hdq_formula = hdq_formulae[0]

# build the mosaic equivalent
mosaic_value = '(' + ','.join([v for (k, v) in mosaic_config.items() if k != 'Formula']) + ')'
mosaic_formula = mosaic_config['Formula'] + mosaic_value

# update the formula
hdq_formula.string = mosaic_formula

# ===========================================================
# check that it worked

updated_sheet_data = soup.find('sheetData')
formula_search_string = mosaic_config['Formula']
formula_search_results = get_all_strings_starting_with(results=formulae, search_string=formula_search_string)

# ===========================================================
# update the file

with ZipFile(zip_filename_and_path, mode='w') as zf:
    file = worksheet_name
    with zf.open(file, mode='w') as f:
        f.writelines(worksheets[worksheet_name])

# and rename it
copyfile(zip_filename_and_path, updated_filename_and_path)

print()

