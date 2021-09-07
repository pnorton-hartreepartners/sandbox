from enum import Enum
from collections import namedtuple


class Vessel(enum):
    BARGES = 'barges'
    CARGOES = 'cargoes'


class Product(enum):
    CRUDE = 'crude'
    FUEL_OIL = 'fuel oil'
    GASOIL = 'gasoil'
    HEATING_OIL = 'heating oil'
    RBOB = 'RBOB'
    EBOB = 'EBOB'
    VGO = 'VGO'
    PROPANE = 'propane'
    BUTANE = 'butane'


class Incoterm(enum):
    '''
    https://www.trade.gov/know-your-incoterms
    '''
    FAS = 'fas'
    FOB = 'fob'
    CFR = 'cfr'
    CIF = 'cif'


class Hub(enum):
    ROTTERDAM = 'rotterdam'
    MEDITERRANEAN = 'mediterranean'
    ARA = 'ara'
    NWE = 'nwe'
    SINGAPORE = 'singapore'


class Price(enum):
    HIGH = 'high'
    LOW = 'low'
    OPEN = 'open'
    CLOSE = 'close'
    SETTLE = 'settle'
    MID = 'mid'
    BID = 'bid'
    OFFER = 'offer'


SULPHURS = [0.5, 3.5]
VISCOSITIES = [180, 380]
OCTANES = [95, 97]
