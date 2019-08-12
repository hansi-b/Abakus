from __future__ import annotations
from datetime import date
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Tuple
from enum import Enum

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

# (Entgeltgruppe), Stufe x Jahr -> (Brutto, Jahressonderzahlung)


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
    
    def __init__(self, jahre):
        self.jahre = jahre
        
    def nächste(self):
        return Stufe(self.value + 1) if self.value < Stufe.sechs.value else self

    def nächsterAufstieg(self, letzterAufstieg : date) -> date:
        return date(letzterAufstieg.year + self.jahre,  #
                    letzterAufstieg.month,  #
                    letzterAufstieg.day)


class Entgeltgruppe(Enum):
    """
        Definition der Entgeltgruppen, für die Gehaltsdaten vorliegen
    """
    E_10 = 10
    E_13 = 13


@dataclass(eq=True, frozen=True)
class Gehalt:
    """
        Monatliche Gehaltsdaten: Bruttogehalt (ohne Arbeitgeberzuschlag) und Sonderzahlung.
    """
    brutto : Decimal
    sonderzahlung: Decimal


@dataclass(eq=True, frozen=True)
class GuS:
    """
        Entgeltgruppe, Stufe und Stufenanfangsdatum
        
        :param beginn: optional das Datum, seit dem die aktuelle Stufe gilt
    """
    gruppe : Entgeltgruppe
    stufe : Stufe
    beginn : date = None

    def am(self, datum : date) -> GuS:
        """
            :param datum: das Datum, für das die dann gültige GuS ermittelt werden soll
            :return: entweder diese GuS, falls es keine Veränderung zum Argumentdatum
                gibt; oder eine neue mit mindestens einem Stufenaufstieg und aktualisiertem
                "beginn" (zwischen dem jetzigen "beginn" und dem Argumentdatum)
        """
        neueStufe, neuesSeit = self.stufe, self.beginn
        
        nächstesSeit = self.stufe.nächsterAufstieg(self.beginn)
        while nächstesSeit <= datum:
            neuesSeit = nächstesSeit
            neueStufe = neueStufe.nächste()
            nächstesSeit = neueStufe.nächsterAufstieg(nächstesSeit)

        return self if neueStufe == self.stufe else GuS(self.gruppe, neueStufe, neuesSeit)

    def stufenAufstieg(self):
        return GuS(self.gruppe, self.stufe.nächste())


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
    s = Stufe.eins.nächsterAufstieg()
    print(s)

