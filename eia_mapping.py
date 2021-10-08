import os
import pandas as pd

product_mapping = {
    # category to list of members
    'crude oil': ['crude oil'],
    'motor gasoline blending components': [
        'conventional other gasoline blending components',
        'conventional cbob gasoline blending components',
        'conventional gtab gasoline blending components',
        'gasoline blending components'],
    'fuel ethanol': [
        'fuel ethanol'],
    'finished motor gasoline': [
        'reformulated motor gasoline',
        'reformulated rbob',
        'reformulated rbob with alcohol',
        'conventional motor gasoline',
        'finished motor gasoline',
        'finished conventional motor gasoline',
        'finished conventional motor gasoline with ethanol',
        'finished reformulated motor gasoline',
        'finished reformulated motor gasoline with ethanol',
        'motor gasoline',
    ],
    'kerosene type jet fuel': [
        'kerosene-type jet fuel'],
    'distillate fuel oil': [
        'distillate fuel oil',
    ],
    'residual fuel oil': ['residual fuel oil'],
    'propane/propylene': ['propane/propylene',
                          'propane and propylene']
}

location_mapping = {
    'East Coast (PADD 1)': 'East Coast (PADD 1)',
    'Gulf Coast (PADD 3)': 'Gulf Coast (PADD 3)',
    'Midwest (PADD 2)': 'Midwest (PADD 2)',  # spacing change here
    'Midwest (PADD2)': 'Midwest (PADD 2)',
    'West Coast (PADD 5)': 'West Coast (PADD 5)',
    'Rocky Mountain (PADD 4)': 'Rocky Mountain (PADD 4)',
    'Rocky Mountains (PADD 4)': 'Rocky Mountain (PADD 4)',  # spelling change here
    'Lower 48 States': 'Lower 48 States',
    'U.S.': 'U.S.'
}

measure_mapping = {
    'Imports': 'Imports',
    'Crude Oil Production': 'Production',
    'Days of Supply (Number of Days)': 'Days of Supply',
    'Ethanol Plant Production': 'Production',
    'Exports': 'Exports',
    'Lower 48 Weekly Supply Estimates': 'Supply',
    'Net Imports (Including SPR)': 'Imports',
    'Product Supplied': 'Supply',
    'Refiner and Blender Net Inputs': 'Inputs',
    'Refiner and Blender Net Production': 'Production',
    'Refiner Inputs and Utilization': 'Inputs',
    'Stocks': 'Stocks',
    'Ultra Low Sulfur Distillate': 'Supply',
    'Weekly Preliminary Crude Imports by Top 10 Countries of Origin (ranking based on 2018 Petroleum Supply Monthly data)': 'Imports',
}


DESCRIPTION = 'description'
REMAINING_DESCRIPTION = 'remaining description'
TAB_DESCRIPTION = 'TabDescription'
LOCATION = 'Location'
MAP_PRODUCT = 'map_product'
MAP_MEASURE = 'map_measure'
MAP_LOCATION = 'map_location'

if __name__ == '__main__':
    filepath = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\jira\doe mapping'
    filename = r'eia_weekly_202110071437'
    filetype = r'.xlsx'

    # load the xls
    file = os.path.join(filepath, filename + filetype)
    raw_df = pd.read_excel(file)

    # standardise the label and the content
    raw_df[DESCRIPTION] = raw_df['Description'].str.lower()
    raw_df.drop('Description', axis='columns')

    df_analysis = raw_df.copy(deep=True)
    # append new columns
    df_analysis[REMAINING_DESCRIPTION] = ''
    df_analysis[MAP_PRODUCT] = ''
    df_analysis[MAP_MEASURE] = ''
    df_analysis[MAP_LOCATION] = ''
    df_analysis[REMAINING_DESCRIPTION] = df_analysis[DESCRIPTION].str.lower()

    # text search description to determine product
    for category, searches in product_mapping.items():
        for search in searches:
            # regex search returns series of boolean
            pattern = f'\\b({search})\\b'
            df = df_analysis[DESCRIPTION].str.contains(pattern)
            df.name = category + '|' + search
            # add a column with the boolean flag
            df_analysis = pd.concat([df_analysis, df], axis='columns')
            # remove the search text from the description so we can see whats left
            df_analysis[REMAINING_DESCRIPTION] = df_analysis[REMAINING_DESCRIPTION].str.replace(pattern, '', regex=True)
            # add the product mapping category
            df_analysis.loc[df.values, MAP_PRODUCT] = category
        # turn boolean into integer values so we can sum them
        df_analysis[[category + '|' + s for s in searches]] = df_analysis[[category + '|' + s for s in searches]].applymap(lambda x: int(x))

    df_analysis[MAP_MEASURE] = df_analysis[TAB_DESCRIPTION].map(measure_mapping)
    df_analysis[MAP_LOCATION] = df_analysis[LOCATION].map(location_mapping)

    df_analysis.to_clipboard()
    print()
