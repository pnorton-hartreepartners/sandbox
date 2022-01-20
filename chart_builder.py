'''
reference this
https://grafana.com/docs/grafana/latest/http_api/dashboard/#create-update-dashboard

use an xls to build charts
'''

import json
import pandas as pd
import requests
import copy
from pprint import pprint as pp

# filenames
template_filename = 'chart_template.json'  # copied verbatim from grafana; needs to incl some panels
dashboard_filename = 'chart.json'  # modified equivalent; this can be copied directly into grafana app
dashboard_api_filename = 'chart_api.json'  # same but with additional api details
dashboard_api_test_filename = 'chart_api_test.json'  # for manual adjustment and testing
xls_filename = 'chart_config.xlsx'  # the xls configuration of the new required charts

# urls
dashboard_url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/dashboards/db'
folder_url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/folders'

# api structures
headers_dict = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJrIjoiaHJ6M1B2TUQ5NmZOMFltMkN0TXZSdmlYVlNuYW9YUEkiLCJuIjoiYXBpYWNjZXNzIiwiaWQiOjF9'
}

dashboard_api_dict = {
    'dashboard': {
        'title': None,  # populate this
        'tags': ['none'],
        'timezone': 'browser',
        'schemaVersion': 16,
        'version': 0,
        'refresh': '25s',
    },
    'folderUid': None,  # populate this
    'message': 'PN changes',
    'overwrite': True
}

# required config data
cleanup_keys = ['id', 'uid', 'title', 'version']
product_columns = ['currency', 'unit', 'legend', 'axis']
panel_columns = ['title']
panel_type_is_seasonal = {True: 'timeseries',
                          False: 'mosaic-grafana-panel'}


def clean_the_sheets(workbook):
    for key, df in workbook.items():
        df.fillna("", inplace=True)
    return workbook


def get_template(file):
    with open(file) as f:
        chart_template = json.load(f)
    return chart_template


def clean_template(dashboard_template, keys):
    for key in keys:
        dashboard_template.pop(key, None)
    return dashboard_template


def build_from_template(df, template, columns):
    results = {}
    for index, row in df[columns].iterrows():
        xx = row.to_dict(dict)
        yy = copy.deepcopy(template)
        yy.update(xx)
        results[index] = yy
    return results


def build_expressions(df):
    columns = ['factor', 'product', 'front', 'middle', 'back']
    expressions = {}
    for index, row in df[columns].iterrows():
        xx = row.to_dict(dict)
        xx = {k: str(v) for (k, v) in xx.items()}
        expressions[index] = xx
    return expressions


def build_dashboard(xls_file, dashboard_template, number=None):
    # templates from grafana
    panel_template = dashboard_template['panels'][0]
    target_template = panel_template['targets'][0]
    product_template = target_template['products'][0]

    # remove id's from the old template
    panel_template = clean_template(panel_template, keys=cleanup_keys)

    # =====================================================
    # build data from xls

    # user configured requirements
    worksheets = pd.read_excel(io=xls_file, sheet_name=None)
    worksheets = clean_the_sheets(worksheets)

    # get them
    panels_df = worksheets['panels']
    products_df = worksheets['products']
    expressions_df = worksheets['expressions']

    # join them
    products_df = pd.merge(panels_df, products_df, how='inner',
                           left_on='panel_id', right_on='panel_id')

    expressions_df = pd.merge(products_df, expressions_df, how='inner',
                              left_on='product_id', right_on='product_id')

    # set indexes
    panels_df.set_index(keys='panel_id', drop=True, inplace=True)
    products_df.set_index(keys='product_id', drop=True, inplace=True)
    expressions_df.set_index(keys='expression_id', drop=True, inplace=True)

    # =====================================================
    # build new dictionaries

    # create fewer panels if we're testing or developing
    selection_df = panels_df if not number else panels_df.iloc[:number]

    # build data for each panel and update panels_content
    panels_content = build_from_template(selection_df, panel_template, panel_columns)
    for panel_id, panel in selection_df.iterrows():
        products_content = build_products_content_for_panel(products_df, expressions_df,
                                                            panel_id, product_template)

        # add the products list to the targets
        target_content = copy.deepcopy(target_template)
        target_content['backward']['seasonal'] = panel['seasonal']
        target_content['products'] = list(products_content.values())

        # add the targets to the panel
        panel_content = panels_content[panel_id]
        # in our model we only have one target
        panel_content['targets'] = [target_content]

        # this is not in the xls config
        panel_type = panel_type_is_seasonal[panel['seasonal'] > 0]
        panel_content['type'] = panel_type
        # and i own these id's which controls whether i update current or create new
        panel_content['id'] = panel_id

    # add the panels to the dashboard
    dashboard_dict = copy.deepcopy(dashboard_template)
    dashboard_dict['panels'] = list(panels_content.values())

    return dashboard_dict


def build_products_content_for_panel(products_df, expressions_df, panel_id, product_template):
    mask = products_df['panel_id'] == panel_id
    products_filtered_df = products_df[mask]

    products_content = build_from_template(products_filtered_df, product_template, product_columns)
    for product_id, product in products_filtered_df.iterrows():
        # for each product, build the expression list
        mask = expressions_df['product_id'] == product_id
        expressions_filtered_df = expressions_df[mask]
        expressions = build_expressions(expressions_filtered_df)
        products_content[product_id]['expressions'] = list(expressions.values())

    return products_content


if __name__ == '__main__':
    # user config
    folder_uid = '1ei4hE17z'

    dashboard_details = {
        'crude': {'id': 42,
                  'uid': 'SETQfq17z',
                  }
        }

    # user selection
    build_dashboard_selection = True
    get_folder_details_selection = False
    run_api_selection = True
    dashboard_title = 'crude'
    refresh_interval = ''

    # created but not used at the moment
    dashboard_id = dashboard_details[dashboard_title]['id']
    dashboard_uid = dashboard_details[dashboard_title]['uid']

    # just to validate the additional api details
    if get_folder_details_selection:
        folders = requests.get(folder_url, headers=headers_dict, verify=False)
        print(folders.content.decode('utf-8'))

    # build a json comparable to the grafana dashboard settings json
    if build_dashboard_selection:
        # user configuration is in this xls
        # template copied from grafana app
        dashboard_template = get_template(template_filename)
        # not sure why it needs an id
        dashboard_template = clean_template(dashboard_template, keys=cleanup_keys)
        # update it based on user requirements
        db = build_dashboard(xls_filename, dashboard_template)
        db['title'] = dashboard_title
        db['refresh'] = refresh_interval
        # save it
        with open(dashboard_filename, 'w') as f:
            json.dump(db, f)
    else:
        with open(dashboard_filename) as f:
            db = json.load(f)

    # update the api header template
    dashboard_api_dict['dashboard']['title'] = dashboard_title
    dashboard_api_dict['folderUid'] = folder_uid
    pp(dashboard_api_dict)

    #  and then add the dashboard json
    dashboard_api_dict['dashboard'].update(db)

    # print it and save it for review/debugging
    with open(dashboard_api_filename, 'w') as f:
        json.dump(dashboard_api_dict, f)

    # call the api
    dashboard_api_dict_json = json.dumps(dashboard_api_dict)
    if run_api_selection:
        rr = requests.post(dashboard_url, headers=headers_dict, data=dashboard_api_dict_json, verify=False)
        print(rr)
        print(rr.content.decode('utf-8'))

    print()

