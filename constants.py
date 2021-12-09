path = r'C:\Temp'
# json_for_trader_curves_definitions = 'trader_curves_definitions.json'
json_for_trader_curves_definitions = 'tempest.json'

PROD = 'prod'
DEV = 'dev'

SETTLES = 'settles'
TSDB = 'tsdb'
TRADER_CURVES = 'trader_curves'
BALSAMO = 'balsamo'
PORT = 'port'

TTDA = 'ttda'

URL_KWARGS = 'url_kwargs'
PARAMS_KWARGS = 'params_kwargs'
PAYLOAD = 'payload'

hosts = {
    SETTLES:
        {
            PROD: 'http://settles-api.mosaic.hartreepartners.com/settles',
            DEV: 'http://settles-api.dev.mosaic.hartreepartners.com/settles',
            PORT: 123
        },
    BALSAMO:
        {
            PROD: 'https://192.168.137.10',
            DEV: 'https://balsamotest.commoditiesengineering.com',
            PORT: 8443
        },
    TSDB:
        {
            PROD: 'http://time-series-api.mosaic.hartreepartners.com/data',
            DEV: 'http://time-series-api.dev.mosaic.hartreepartners.com/data',
            PORT: 123
        },
    TRADER_CURVES:
        {
            PROD: 'http://trader-curves-api.mosaic.hartreepartners.com/trader-curves',
            DEV: 'http://trader-curves-api.dev.mosaic.hartreepartners.com/trader-curves',
            PORT: 123
        }
}

db_connections = {
    TTDA: {
        PROD: 'ttda.storage.mosaic.hartreepartners.com',
        DEV: 'ttda.cratedb-dev-cluster.mosaic.hartreepartners.com',
        PORT: 4200
    }
}
