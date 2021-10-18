import os
import pandas as pd
from oil_data_etl.common.model.Hierarchy import Hierarchy
from oil_data_etl.default_entities.geo import getDefaultHierarchy as geoHierarchy
from oil_data_etl.default_entities.products import getDefaultHierarchy as productsHierarchy
from oil_data_etl.default_entities.measures import getDefaultHierarchy as measuresHierarchy

if __name__ == '__main__':
    p = productsHierarchy()

    # explore
    for e in p.edges:
        if e['parent'] == 'ROOT:ROOT':
            print(e)

    # this one is interesting
    # {'parent': 'ROOT:ROOT', 'child': 'product_group:gasoline & naphtha'}

    aa = p.getAttributes(node='product_group:gasoline & naphtha')
    print(aa)
    # {'conversion': 8.45, 'source_unit': 'bbl', 'destination_unit': 'mt'}

    ee = p.getEntity(node='product_group:gasoline & naphtha')
    print(ee)
    # {'node': 'product_group:gasoline & naphtha', 'conversion': 8.45, 'source_unit': 'bbl', 'destination_unit': 'mt'}

    dd = p.getDescendants(node='product_group:gasoline & naphtha', strict=False)
    print(dd)
    # ['product_group:gasoline & naphtha', 'product:blending components', 'sub_product:blending components@reformulated', 'product_grade:blending components@reformulated@rbob', 'sub_product:blending components@conventional', 'product_grade:blending components@conventional@cbob', 'product_grade:gtab', 'product:gasoline', 'sub_product:gasoline@reformulated', 'product_grade:gasoline@reformulated@rbob', 'sub_product:gasoline@conventional', 'product_grade:gasoline@conventional@cbob', 'contract:rbob', 'contract_spec:nymex rbob', 'product_grade:a', 'product_grade:c', 'product:naphtha']

    [print(d) for d in dd if d.startswith('sub_product')]
    # sub_product: blending components @ reformulated
    # sub_product: blending components @ conventional
    # sub_product: gasoline @ reformulated





    print('hello world')
