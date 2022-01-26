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
email_filename = 'chart_email.html'

# urls
dashboard_url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/dashboards/db'
folder_url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/folders'
search_url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/search'
view_panel_url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/d/{dashboard_uid}/{db_name}?viewPanel={panel_id}'

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


def build_dashboard(panels_content, dashboard_template):
    # add the panels to the dashboard
    dashboard_dict = copy.deepcopy(dashboard_template)
    dashboard_dict['panels'] = list(panels_content.values())
    return dashboard_dict


def build_panels_content(templates, dfs):
    panel_template, target_template, product_template = templates
    panels_df, products_df, expressions_df = dfs

    # build data for each panel and update panels_content
    panels_content = build_from_template(panels_df, panel_template, panel_columns)
    for panel_id, panel in panels_df.iterrows():
        products_content = build_products_content_for_panel(products_df, expressions_df,
                                                            panel_id, product_template)

        # add the products list to the targets
        target_content = copy.deepcopy(target_template)
        target_content['backward']['seasonal'] = panel['seasonal']
        target_content['products'] = list(products_content.values())

        # in our model we only have one target
        panels_content[panel_id]['targets'] = [target_content]

        # we need to use a different chart object depending on the chart type
        panel_type = panel_type_is_seasonal[panel['seasonal'] > 0]
        panels_content[panel_id]['type'] = panel_type
        # and i own these id's which controls whether i update current or create new
        panels_content[panel_id]['id'] = panel_id

    return panels_content


def build_config_data(xls_file):
    # collect config data from xls
    panels_df, products_df, expressions_df = get_chart_config(xls_file)
    # expand for months forward
    return build_expanded_config(panels_df, products_df, expressions_df)


def get_templates(dashboard_template):
    # templates from grafana
    panel_template = dashboard_template['panels'][0]
    target_template = panel_template['targets'][0]
    product_template = target_template['products'][0]
    # remove id's from the old template
    panel_template = clean_template(panel_template, keys=cleanup_keys)
    return panel_template, target_template, product_template


def get_chart_config(xls_file):
    worksheets = pd.read_excel(io=xls_file, sheet_name=None)
    # clean n/a
    worksheets = clean_the_sheets(worksheets)
    # get the dataframes
    panels_df = worksheets['panels']
    products_df = worksheets['products']
    expressions_df = worksheets['expressions']
    # set indexes
    panels_df.set_index(keys='panel_id', drop=True, inplace=True)
    products_df.set_index(keys='product_id', drop=True, inplace=True)
    expressions_df.set_index(keys='expression_id', drop=True, inplace=True)
    return panels_df, products_df, expressions_df


def clean_the_sheets(workbook):
    for key, df in workbook.items():
        df.fillna("", inplace=True)
    return workbook


def build_expanded_config(panels_df, products_df, expressions_df):
    mapper = {
        'panel_id': 'original_panel_id',
        'product_id': 'original_product_id',
        'expression_id': 'original_expression_id'
    }
    new_panels_df = pd.DataFrame()
    for panel_id, row in panels_df.iterrows():
        months_forward = row['extend_count']
        df = row.to_frame().T
        # build a new df
        data = df.values.repeat(months_forward, axis=0)
        new_panel_df = pd.DataFrame(data=data, columns=panels_df.columns)
        # add the original id and we'll join on this later
        new_panel_df['original_panel_id'] = panel_id
        # add the month increment column
        new_panel_df['month_increment'] = range(months_forward)
        new_panels_df = pd.concat([new_panels_df, new_panel_df], axis='index')
    new_panels_df.reset_index(drop=True, inplace=True)
    new_panels_df.index.name = panels_df.index.name

    # products
    new_products_df = products_df.copy(deep=True)
    new_products_df.reset_index(inplace=True)
    new_products_df.rename(columns=mapper, inplace=True)
    new_products_df = pd.merge(new_panels_df.reset_index(), new_products_df, how='inner',
                               left_on='original_panel_id', right_on='original_panel_id')
    new_products_df.index.name = products_df.index.name

    # expressions
    new_expressions_df = expressions_df.copy(deep=True)
    new_expressions_df.reset_index(inplace=True)
    new_expressions_df.rename(columns=mapper, inplace=True)
    new_expressions_df = pd.merge(new_products_df.reset_index(), new_expressions_df, how='inner',
                                  left_on='original_product_id', right_on='original_product_id')
    new_expressions_df.index.name = expressions_df.index.name

    # add the month increments
    for column in ['front', 'middle', 'back']:
        if not (new_expressions_df[column] == '').any():
            dates = pd.to_datetime(new_expressions_df[column].astype(str).values, format='%Y%m')
            month_offsets = new_expressions_df['month_increment'].apply(lambda x: pd.DateOffset(months=x))
            dates = dates + month_offsets
            new_expressions_df[column] = dates.dt.strftime('%Y%m')

    # modify the title
    new_expressions_df['title'] = new_expressions_df.apply(lambda x: x['title'].format(front=x['front'], back=x['back']),
                                                           axis='columns')
    new_products_df = pd.merge(new_products_df[[c for c in new_products_df.columns if c != 'title']].reset_index(),
                               new_expressions_df[['title', 'product_id']],
                               how='inner',
                               left_on='product_id',
                               right_on='product_id')
    new_products_df.drop_duplicates(ignore_index=True, inplace=True)
    new_products_df.set_index(keys='product_id', drop=True, inplace=True)

    new_panels_df = pd.merge(new_panels_df[[c for c in new_panels_df.columns if c != 'title']].reset_index(),
                             new_products_df[['title', 'panel_id']],
                             how='inner',
                             left_on='panel_id',
                             right_on='panel_id')
    new_panels_df.drop_duplicates(ignore_index=True, inplace=True)
    new_panels_df.set_index(keys='panel_id', drop=True, inplace=True)

    return new_panels_df, new_products_df, new_expressions_df


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


def build_products_content_for_panel(products_df, expressions_df, panel_id, product_template):
    products_filtered_df = products_df.loc[panel_id]
    if isinstance(products_filtered_df, pd.Series):
        products_filtered_df = products_filtered_df.to_frame().T

    products_content = build_from_template(products_filtered_df, product_template, product_columns)
    for product_id, product in products_filtered_df.iterrows():
        # for each product, build the expression list
        mask = expressions_df['product_id'] == product_id
        expressions_filtered_df = expressions_df[mask]
        expressions = build_expressions_content_for_product(expressions_filtered_df)
        products_content[product_id]['expressions'] = list(expressions.values())

    return products_content


def build_expressions_content_for_product(df):
    columns = ['factor', 'product', 'front', 'middle', 'back']
    expressions = {}
    for index, row in df[columns].iterrows():
        xx = row.to_dict(dict)
        xx = {k: str(v) for (k, v) in xx.items()}
        expressions[index] = xx
    return expressions


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
    build_html_selection = True

    # user settings
    dashboard_title = 'crude'
    refresh_interval = ''
    time_axis = {'from': '2021-01-01', 'to': '2022-06-01'}

    # just to validate the additional api details
    if get_folder_details_selection:
        folders = requests.get(folder_url, headers=headers_dict, verify=False)
        print(folders.content.decode('utf-8'))

    # build a json comparable to the grafana dashboard settings json
    if build_dashboard_selection:
        # build it
        dfs = build_config_data(xls_file=xls_filename)
        dashboard_template = get_template(template_filename)
        dashboard_template = clean_template(dashboard_template, keys=cleanup_keys)
        templates = get_templates(dashboard_template)
        panels_content = build_panels_content(templates, dfs)
        db = build_dashboard(panels_content, dashboard_template)

        # update some fields
        db['title'] = dashboard_title
        db['refresh'] = refresh_interval
        db['time'] = time_axis

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

    # save it for review/debugging
    with open(dashboard_api_filename, 'w') as f:
        json.dump(dashboard_api_dict, f)

    # call the api
    dashboard_api_dict_json = json.dumps(dashboard_api_dict)
    if run_api_selection:
        rr = requests.post(dashboard_url, headers=headers_dict, data=dashboard_api_dict_json, verify=False)
        print(rr)
        print(rr.content.decode('utf-8'))

    if build_html_selection and build_dashboard_selection:
        htmls = []
        dashboard_uid = dashboard_details[dashboard_title]['uid']
        for panel in dashboard_api_dict['dashboard']['panels']:
            panel_id = panel['id']
            view_panel_dict = {'dashboard_uid': dashboard_uid,
                               'db_name': dashboard_title,
                               'panel_id': panel_id}
            url = view_panel_url.format(**view_panel_dict)
            title = dashboard_api_dict['dashboard']['panels'][panel_id]['title']
            html_template = '<a href="{url}">{text}</a>'
            html = html_template.format(url=url, text=title)
            htmls.append(html)
    html_str = '<br>'.join(htmls)

    with open(email_filename, 'w') as f:
        f.write(html_str)

