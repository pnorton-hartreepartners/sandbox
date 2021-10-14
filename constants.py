PROD = 'prod'
DEV = 'dev'
SETTLES = 'settles'
BALSAMO = 'balsamo'
PORT = 'port'

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
