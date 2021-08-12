import os
import pandas as pd
# imports from other Mosaic modules
from mosaic_sql.crate import EngineInstance, get_engine

# Imports from this repo
DEV = True
if_dev = '.dev' if DEV else ''
if if_dev:
    os.environ['CRATE_HOST'] = 'ttda.cratedb-dev-cluster.mosaic.hartreepartners.com:4200'
else:
    os.environ['CRATE_HOST'] = 'ttda.storage.mosaic.hartreepartners.com:4200'
ENGINE = get_engine(EngineInstance.TTDA, timeout=20, debug=False)


def compare_data():
    sql = """
        select * from settles.values_2 where date='2021-08-06'
    """
    df = pd.read_sql(sql, con=ENGINE)
    print(df.head(100))


if __name__ == "__main__":
    compare_data()
    print()

