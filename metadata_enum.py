from dataclasses import dataclass
from enum import Enum
from collections import namedtuple
import re


class Product(Enum):
    CRUDE = 'crude'
    GASOLINE = 'gasoline'
    NAPHTHA = 'naphtha'
    JETFUEL = 'jetfuel'
    HEATINGOIL = 'heating oil'  # ULSD
    DIESEL = 'diesel'
    FUEL_OIL = 'fuel oil'  # HSFO
    PROPANE = 'propane'
    BUTANE = 'butane'


class Hub(Enum):
    ROTTERDAM = 'rotterdam'
    MEDITERRANEAN = 'mediterranean'
    ARA = 'ara'
    NWE = 'nwe'
    NORTHSEA = 'north sea'
    SINGAPORE = 'singapore'
    NEWYORKHARBOUR = 'new york harbour'
    GULFCOAST = 'US gulf coast'
    CUSHING = 'cushing'
    ARABGULF = 'arab gulf'
    DUBAI = 'dubai'


class Source(Enum):
    ARGUS = 'argus'
    PLATTS = 'platts'
    CME = 'cme'
    ICE = 'ICE'


class Vessel(Enum):
    BARGES = 'barges'
    CARGOES = 'cargoes'


class Incoterm(Enum):
    FAS = 'fas'
    FOB = 'fob'
    CFR = 'cfr'
    CIF = 'cif'


class Price(Enum):
    HIGH = 'high'
    LOW = 'low'
    OPEN = 'open'
    CLOSE = 'close'
    SETTLE = 'settle'
    MID = 'mid'
    BID = 'bid'
    OFFER = 'offer'


class Contract(Enum):
    FORWARD = 'forward'
    FUTURES = 'futures'
    SWAP = 'swap'
    EUROPEAN = 'european'
    APO = 'apo'


class Tenor(Enum):
    BALMO = 'balmo'
    MONTH = 'month'
    QUARTER = 'quarter'


class PriceCalc(Enum):
    BASIS = 'basis'
    CRACK = 'crack'
    OUTRIGHT = 'outright'


class Size(Enum):
    MINI = 'mini'
    NORMAL = 'normal'


@dataclass
class Octane:
    RON: float

    def __post_init__(self):
        # do some validation here
        pass


class Sulphur:
    flavours = ['sweet', 'sour']
    percentages = [0.5, 3.5]

    @classmethod
    def flavour(cls, value):
        if value in Sulphur.flavours:
            return value

    @classmethod
    def ppm(cls, value):
        return value

    @classmethod
    def percent(cls, value):
        if value in Sulphur.percentages:
            return value


@dataclass
class Viscosity:
    viscosities = [180, 380]
    VALUE: float


# locations
BRAZIL = ['Manaus', 'Itaqui', 'Suape', 'Aratu', 'Santos', 'Paranagua', 'Tramandai', \
          'Guamare', 'Duque de Caxias', 'Betim', 'Cubatao', 'Maua', 'Paulinia', \
          'Sao Jose dos Campos', 'Araucaria', 'Canoas']


if __name__ == '__main__':
    brent = (Product.CRUDE, Hub.NORTHSEA)

    wti = (Product.CRUDE, Hub.CUSHING, Incoterm.FOB)

    dubai = (Product.CRUDE, Hub.DUBAI)

    rbob = (Product.GASOLINE, Hub.NEWYORKHARBOUR, Incoterm.FOB)

    ebob = (Product.GASOLINE, Hub.ROTTERDAM, Incoterm.FOB, Vessel.BARGES)

    Octane.RON = 95
    singapore_mogas_95 = (Product.GASOLINE, Hub.SINGAPORE, Octane.RON)

'''
    # regex definition of permitted strings of numbers
    p1 = r'^\d{2}\.\d{1}$'  # 2 integers and 1dp
    p2 = r'^\d{2}$'  # 2 integers only
    OCTANES = p1 + '|' + p2  # one patter or the other
    
    octanes = ['87', '87.5', '99', '0', '100']
    for octane in octanes:
        x = re.match(OCTANES, octane)
        try:
            print(x.group())
        except:
            print(x)
'''
