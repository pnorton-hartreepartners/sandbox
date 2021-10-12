import os
import pandas as pd
from oil_data_etl.common.model.Hierarchy import Hierarchy
from oil_data_etl.default_entities.geo import getDefaultHierarchy as geoHierarchy
from oil_data_etl.default_entities.products import getDefaultHierarchy as productsHierarchy
from oil_data_etl.default_entities.measures import getDefaultHierarchy as measuresHierarchy

if __name__ == '__main__':
    filepath = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\jira\doe mapping'
    filename = r'hierarchies'
    filetype = r'.txt'

    # load the xls
    file = os.path.join(filepath, filename + filetype)
    with open(file, 'r') as file:
        lines = file.readlines()

    columns = [lines[0]]
    # columns = columns.replace('"', '').replace('\n', '').split(',')

    data = lines[1:]
    # rows = [r.split('"') for r in data]

    df = pd.DataFrame(data=data, columns=columns)
    print('hello world')
