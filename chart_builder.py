import json
import pandas as pd
import requests
import copy
from pprint import pprint as pp

url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/dashboards/db'
cleanup_keys = ['id', 'uid', 'title', 'version']

headers_dict = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJrIjoiaHJ6M1B2TUQ5NmZOMFltMkN0TXZSdmlYVlNuYW9YUEkiLCJuIjoiYXBpYWNjZXNzIiwiaWQiOjF9'
}

dashboard_api_dict = {
    'dashboard': {
        'title': 'crude',
        'tags': ['none'],
        'timezone': 'browser',
        'schemaVersion': 16,
        'version': 0,
        'refresh': '25s',
    },
    'folderUid': '1ei4hE17z',
    'message': 'PN changes',
    'overwrite': True
}

product_columns = ['currency', 'unit', 'legend', 'axis']
panel_columns = ['title']  # 'seasonal'
panel_type = 'mosaic-grafana-panel'
panel_type = 'timeseries'  # for seasonal


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


def build_dashboard(xls_file, dashboard_template):
    # templates from grafana
    panel_template = dashboard_template['panels'][0]
    target_template = panel_template['targets'][0]
    product_template = target_template['products'][0]

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

    # build new dicts
    selection_df = panels_df.iloc[:1]  # only while were playing/fixing/building
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
        panel_content['type'] = panel_type

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
    build_dashboard_selection = False

    # folders = requests.get("https://grafana.charting.dev.mosaic.hartreepartners.com/api/folders", headers=headers_dict,
    #                        verify=False)
    # print(folders.content.decode('utf-8'))

    # build a json comparable to the grafana dashboard settings json
    filename = f'chart.json'
    if build_dashboard_selection:
        # user configuration is in this xls
        xls_file = 'chart_config.xlsx'
        # template copied from grafana app
        dashboard_template = get_template('chart_template.json')
        dashboard_template = clean_template(dashboard_template, keys=cleanup_keys)
        # update it based on user requirements
        db = build_dashboard(xls_file, dashboard_template)
        # save it
        with open(filename, 'w') as f:
            json.dump(db, f)
    else:
        with open(filename) as f:
            db = json.load(f)

    # add this to the template from here
    # https://grafana.com/docs/grafana/latest/http_api/dashboard/#create--update-dashboard
    dashboard_api_dict['dashboard'].update(db)
    pp(dashboard_api_dict)

    # call the api
    dashboard_api_dict_json = json.dumps(dashboard_api_dict)
    rr = requests.post(url, headers=headers_dict, data=dashboard_api_dict_json, verify=False)
    print(rr)
    print(rr.content.decode('utf-8'))
