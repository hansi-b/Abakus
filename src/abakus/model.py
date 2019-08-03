__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Tuple
from enum import Enum

# (Entgeltgruppe), Stufe x Jahr -> (Brutto, Jahressonderzahlung)


@dataclass(eq=True, frozen=True)
class Gehalt:
    """
        Monatliche Gehaltsdaten: Bruttogehalt (ohne Arbeitgeberzuschlag) und Sonderzahlung.
    """
    brutto : Decimal
    sonderzahlung: Decimal


class Stufe(Enum):
    """
        definiert, mit welchen Stufen wir arbeiten können;
        eigentlich nur ein Typwrapper für die ganzzahlige Stufe
    """
    eins = 1
    zwei = 2
    drei = 3
    vier = 4
    fünf = 5
    sechs = 6


class Entgeltgruppe(Enum):
    """
        Definition der Entgeltgruppen, für die Gehaltsdaten vorliegen
    """
    E_10 = 10
    E_13 = 13


@dataclass(eq=True, frozen=True)
class GuS:
    """
        Kurz für Entgeltgruppe und Stufe
        Klein, aber wir werden ständig mit dieser Kombination arbeiten
    """
    gruppe : Entgeltgruppe
    stufe : Stufe


class ÖtvKosten:

    """
    ein fixer Prozentsatz, der als Kostenzuschlag genommen wird
    """
    arbeitgeberKostenZuschlag = 0.3

    gehälter : Mapping [ Tuple[int, GuS], Gehalt ]
    
    def __init__(self, gehälter):
        self.gehälter = gehälter

    def summeMonatlich(self, jahr: int, gus : GuS):
        """
            :return: die monatlichen Gesamtkosten mit Arbeitgeberzuschlag,
                    aber ohne Jahressonderzahlung
        """
        return self.gehälter[(jahr, gus)].brutto * (1. + ÖtvKosten.arbeitgeberKostenZuschlag)

    def sonderzahlung(self, jahr: int, gus : GuS):
        """
            :return: die Jahressonderzahlung
        """
        return self.gehälter[(jahr, gus)].sonderzahlung
    
    def summeMonatlichMitSonderzahlung(self, jahr: int, gus : GuS):
        
        return self.summeMonatlich(jahr, gus) + self.sonderzahlung(jahr, gus)

if __name__ == '__main__':
    ö = ÖtvKosten({})

