import json
import pandas as pd
import requests

url_template = r'https://grafana.charting.dev.mosaic.hartreepartners.com/d/Y-bj-x2nz/peter-norton'

headers_dict = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def clean_the_sheets(workbook):
    for key, df in workbook.items():
        df.fillna("", inplace=True)
    return workbook


def get_templates(file):
    with open(file) as f:
        chart_template = json.load(f)
    product_template = chart_template['targets'][0]['products'][0]
    return chart_template, product_template


def build_from_template(df, template, columns):
    results = []
    for _, row in df[columns].iterrows():
        for _, row in df[columns].iterrows():
            xx = row.to_dict(dict)
            yy = template.copy()
            yy.update(xx)
            results.append(yy)
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
    response = requests.post(url, headers=headers_dict, json=data, verify=False)
    print(response.content)
    pass


def search_grafana_panel():
    url = url_template + r'/api/search'
    response = requests.get(url, headers=headers_dict, verify=False)
    print(response.content)


def main():
    product_columns = ['currency', 'unit', 'legend', 'axis']
    panel_columns = ['title', 'seasonal']

    file = 'chart_example.json'
    chart_template, product_template = get_templates(file)

    file = 'chart_config.xlsx'
    worksheets = pd.read_excel(io=file, sheet_name=None)
    worksheets = clean_the_sheets(worksheets)

    panels_df = worksheets['panels']
    products_df = worksheets['products']
    expressions_df = worksheets['expressions']

    products_df = pd.merge(panels_df, products_df, how='inner',
                           left_on='panel_id', right_on='panel_id')

    expressions_df = pd.merge(products_df, expressions_df, how='inner',
                              left_on='product_id', right_on='product_id')

    charts_list = build_from_template(panels_df, chart_template, panel_columns)
    for i, panel in panels_df.iterrows():
        mask = products_df['panel_id'] == panel['panel_id']
        products_filtered_df = products_df[mask]

        # so that df index matches list slice
        products_filtered_df.reset_index(drop=True, inplace=True)

        products_list = build_from_template(products_filtered_df, product_template, product_columns)
        for j, product in products_filtered_df.iterrows():
            # for each product, build the expression list
            mask = expressions_df['product_id'] == product['product_id']
            expressions_filtered_df = expressions_df[mask]
            products_list[j]['expressions'] = build_expressions(expressions_filtered_df)

        charts_list[i]['targets'][0]['products'] = products_list

        # save json locally
        file = f'chart_{i}.json'
        with open(file, 'w') as f:
            json.dump(charts_list[i], f)

        # search_grafana_panel()
        # create_grafana_panel(charts_list[i])


if __name__ == '__main__':
    main()
