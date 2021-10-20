PROD = 'prod'
DEV = 'dev'

SETTLES = 'settles'
BALSAMO = 'balsamo'
PORT = 'port'

TTDA = 'ttda'

hosts = {
    SETTLES:
        {
            PROD: 'http://settles-api.mosaic.hartreepartners.com',
            DEV: 'http://settles-api.dev.mosaic.hartreepartners.com',
            PORT: 123
        },
    BALSAMO:
        {
            PROD: 'https://192.168.137.10',
            DEV: 'https://balsamotest.commoditiesengineering.com',
            PORT: 8443
        }
}

db_connections = {
    TTDA: {
        PROD: 'ttda.storage.mosaic.hartreepartners.com',
        DEV: 'ttda.cratedb-dev-cluster.mosaic.hartreepartners.com',
        PORT: 4200
    }
}
