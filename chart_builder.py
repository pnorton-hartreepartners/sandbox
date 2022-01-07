import json
import pandas as pd


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
                           left_on='id', right_on='panel_id',
                           suffixes=['_panel', '_product']
                           )
    expressions_df = pd.merge(products_df, expressions_df, how='inner',
                              left_on='id_product', right_on='product_id',
                              suffixes=['_product', '_expression'])

    charts_list = build_from_template(panels_df, chart_template, panel_columns)
    for i, panel in panels_df.iterrows():
        mask = products_df['panel_id'] == panel['id']
        products_filtered_df = products_df[mask]

        # so that df index matches list slice
        products_filtered_df.reset_index(drop=True, inplace=True)

        products_list = build_from_template(products_filtered_df, product_template, product_columns)
        for j, product in products_filtered_df.iterrows():
            # for each product, build the expression list
            mask = expressions_df['product_id'] == product['id_product']
            expressions_filtered_df = expressions_df[mask]
            products_list[j]['expressions'] = build_expressions(expressions_filtered_df)

        charts_list[i]['targets'][0]['products'] = products_list

        file = f'chart_{i}.json'
        with open(file, 'w') as f:
            json.dump(charts_list[i], f)


if __name__ == '__main__':
    main()

