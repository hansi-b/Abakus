'''
Created on Jul 28, 2019

@author: cb
'''
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Tuple
from enum import Enum

# (Gruppe), Stufe x Jahr -> (Brutto, Jahressonderzahlung)


@dataclass
class Gehalt:
    """
        Monatliche Gehaltsdaten: Bruttogehalt (ohne Arbeitgeberzuschlag) und Sonderzahlung.
    """
    brutto : Decimal
    sonderzahlung: Decimal


class Stufe(Enum):
    """
        eigentlich nur ein Typwrapper für die ganzzahlige Stufe
    """
    eins = 1
    zwei = 2
    drei = 3
    vier = 4
    fünf = 5
    sechs = 6


@dataclass
class Entgeltgruppe:
    """
        die Zuordnung von Stufen zu Gehältern
    """
    stufen : Mapping [ Stufe, Gehalt ]


@dataclass
class ÖTV:
    """
        Der Tarif ist eine Festlegung von Gehältern pro Gruppe und Jahr
    """
    gehälter : Mapping [ Tuple[int, str], Entgeltgruppe ]


if __name__ == '__main__':
    ö = ÖTV({})
    ö.gehälter[(123, "hello")] = Entgeltgruppe({})
    print(ö)

