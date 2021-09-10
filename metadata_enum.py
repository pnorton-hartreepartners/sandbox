from dataclasses import dataclass
from enum import Enum
from collections import namedtuple
import re


class Source(Enum):
    ARGUS = 'argus'
    PLATTS = 'platts'
    CME = 'cme'
    ICE = 'ICE'


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


class UnderlyingTenor(Enum):
    DATED = 'dated'
    DAY = 'day'
    MONTH = 'month'


class UnderlyingSource(Enum):
    PLATTS = 'platts'


class PriceCalc(Enum):
    BASIS = 'basis'
    CRACK = 'crack'
    OUTRIGHT = 'outright'


class Size(Enum):
    MINI = 'mini'
    NORMAL = 'normal'


class Index(Enum):
    MA1 = 'month ahead average'
    MA1_ADJ = 'month ahead average with roll adjust'


class Deliver(Enum):
    CASH = 'cash'
    PHYSICAL = 'physical'


@dataclass
class Octane:
    RON: float

    def __post_init__(self):
        # do some validation here
        pass


class Sulphur:
    flavours = ['sweet', 'sour']
    percentages = [0.5, 3.5]

    def __init__(self, key, value):
        self.key = key
        if self.key == 'flavour' and value in Sulphur.flavours:
            self.value = value
        elif self.key == 'percentage' and value in Sulphur.percentages:
            self.value = value
        elif self.key == 'ppm':
            self.value = value
        else:
            raise NotImplementedError


@dataclass
class Viscosity:
    viscosities = [180, 380]
    VALUE: float

    def __init__(self, value):
        if value in Viscosity.viscosities:
            self.VALUE = value


class Gravity(Enum):
    HEAVY = 'heavy'
    INTERMEDIATE = 'intermediate'
    LIGHT = 'light'


# locations
BRAZIL = ['Manaus', 'Itaqui', 'Suape', 'Aratu', 'Santos', 'Paranagua', 'Tramandai', \
          'Guamare', 'Duque de Caxias', 'Betim', 'Cubatao', 'Maua', 'Paulinia', \
          'Sao Jose dos Campos', 'Araucaria', 'Canoas']


if __name__ == '__main__':

    # https://www.theice.com/products/219/Brent-Crude-Futures
    ice_brent_futures = (Source.ICE, Product.CRUDE, Hub.NORTHSEA, Contract.FUTURES)

    # https://www.theice.com/products/6753532/Brent-1st-Line-Future
    ice_brent_first_line = (Source.ICE, Product.CRUDE, Hub.NORTHSEA, Contract.SWAP, Index.MA1_ADJ)

    # https://www.theice.com/products/6753541
    ice_brent_dated = (Source.ICE, Product.CRUDE, Hub.NORTHSEA, Contract.FUTURES, UnderlyingTenor.DATED)

    # https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.html
    cme_wti = (Source.CME, Product.CRUDE, Hub.CUSHING)

    # https://www.cmegroup.com/markets/energy/crude-oil/dubai-crude-oil-calendar-swap-futures.contractSpecs.html
    dubai = (Source.CME, Product.CRUDE, Hub.DUBAI, PriceCalc.OUTRIGHT)

    # https://www.cmegroup.com/markets/energy/refined-products/rbob-gasoline.html
    rbob = (Source.CME, Product.GASOLINE, Hub.NEWYORKHARBOUR, Incoterm.FOB)

    # https://www.theice.com/products/6753470/Argus-Eurobob-Oxy-FOB-Rotterdam-Barges-Future
    ebob = (Source.ICE, Product.GASOLINE, Hub.ROTTERDAM, Incoterm.FOB, Vessel.BARGES)

    # https://www.theice.com/products/6753545/Singapore-Mogas-95-Unleaded-Platts-Future
    Octane.RON = 95
    singapore_mogas_95 = (Source.ICE, Product.GASOLINE, Hub.SINGAPORE, Octane.RON)

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
