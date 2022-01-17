import json
import pandas as pd
import requests
import copy

url_template = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/dashboards/db'

headers_dict = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJrIjoiaHJ6M1B2TUQ5NmZOMFltMkN0TXZSdmlYVlNuYW9YUEkiLCJuIjoiYXBpYWNjZXNzIiwiaWQiOjF9'
}

dashboard_api_dict = {
    'dashboard': {
        # 'id': None,
        'uid': 'RmBVhP17k',
        'title': 'test',
        'tags': ['no tags'],
        'timezone': 'browser',
        'schemaVersion': 16,
        'version': 0,
        'refresh': '25s'
    },
    'folderId': 1,
    #'folderUid': None,
    'message': 'PN changes',
    'overwrite': 'True'
}

product_columns = ['currency', 'unit', 'legend', 'axis']
panel_columns = ['title']  # 'seasonal'


def clean_the_sheets(workbook):
    for key, df in workbook.items():
        df.fillna("", inplace=True)
    return workbook


def get_template(file):
    with open(file) as f:
        chart_template = json.load(f)
    return chart_template


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
    expressions = []
    for _, row in df[columns].iterrows():
        xx = row.to_dict(dict)
        xx = {k: str(v) for (k, v) in xx.items()}
        expressions.append(xx)
    return expressions


def create_grafana_panel(data):
    url = url_template
    rr = requests.post(url, headers=headers_dict, data=data, verify=False)
    print(url, '\n', rr)
    return rr


def search_grafana_panel():
    url = url_template + r'/api/search'
    rr = requests.get(url, headers=headers_dict, verify=False)
    print(url, '\n', rr)


def build_dashboard(xls_file, dashboard_template):
    # templates from grafana
    panel_template = dashboard_template['panels'][0]
    target_template = panel_template['targets'][0]
    product_template = target_template['products'][0]

    # user configured requirements
    worksheets = pd.read_excel(io=xls_file, sheet_name=None)
    worksheets = clean_the_sheets(worksheets)

    panels_df = worksheets['panels']
    products_df = worksheets['products']
    expressions_df = worksheets['expressions']

    products_df = pd.merge(panels_df, products_df, how='inner',
                           left_on='panel_id', right_on='panel_id')

    expressions_df = pd.merge(products_df, expressions_df, how='inner',
                              left_on='product_id', right_on='product_id')

    # build new dicts
    # for each panel build the products info based on the xls
    panels_content = build_from_template(panels_df, panel_template, panel_columns)
    for i, panel in panels_df.iloc[:1].iterrows():
        products_content = build_products_content(products_df, expressions_df, panel, product_template)

        # add the products list to the targets
        # in our model we only have one target
        target_content = copy.deepcopy(target_template)
        target_content['backward']['seasonal'] = panel['seasonal']
        target_content['products'] = list(products_content.values())

        # add the targets to the panel
        panel_content = copy.deepcopy(panel_template)
        panel_content['targets'] = [target_content]
        panels_content[i] = panel_content

    # add the panels to the dashboard
    dashboard_dict = copy.deepcopy(dashboard_template)
    dashboard_dict['panels'] = list(panels_content.values())

    return dashboard_dict


def build_products_content(products_df, expressions_df, panel, product_template):
    mask = products_df['panel_id'] == panel['panel_id']
    products_filtered_df = products_df[mask]

    # so that df index matches list slice
    products_filtered_df.reset_index(drop=True, inplace=True)

    products_content = build_from_template(products_filtered_df, product_template, product_columns)
    for j, product in products_filtered_df.iterrows():
        # for each product, build the expression list
        mask = expressions_df['product_id'] == product['product_id']
        expressions_filtered_df = expressions_df[mask]
        products_content[j]['expressions'] = build_expressions(expressions_filtered_df)

    return products_content


if __name__ == '__main__':
    build_dashboard_selection = False

    # build a json comparable to the grafana dashboard settings json
    filename = f'chart.json'
    if build_dashboard_selection:
        # user configuration is in this xls
        xls_file = 'chart_config.xlsx'
        # template copied from grafana app
        dashboard_template = get_template('chart_template.json')
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
    response = create_grafana_panel(dashboard_api_dict)
    with open('chart_response.html', 'w') as file:
        file.write(response.content.decode('utf-8'))

    # template = get_template('chart_template.json')
    # dashboard_api_dict['panels'] = template
    # response = create_grafana_panel(dashboard_api_dict)
    # with open('chart_response2.html', 'w') as file:
    #     file.write(response.content.decode('utf-8'))
