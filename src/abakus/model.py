from __future__ import annotations
from datetime import date
from dataclasses import dataclass
from typing import Mapping, Tuple
from enum import Enum
import decimal

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"


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
    brutto : decimal.Decimal
    sonderzahlung: decimal.Decimal


@dataclass(eq=True, frozen=True)
class GuS:
    """
        Entgeltgruppe, Stufe und Stufenanfangsdatum
    """
    gruppe : Entgeltgruppe
    stufe : Stufe


class AllGuS:
    E10_1 = GuS(Entgeltgruppe.E_10, Stufe.eins)
    E10_2 = GuS(Entgeltgruppe.E_10, Stufe.zwei)
    E10_3 = GuS(Entgeltgruppe.E_10, Stufe.drei)
    E10_4 = GuS(Entgeltgruppe.E_10, Stufe.vier)
    E10_5 = GuS(Entgeltgruppe.E_10, Stufe.fünf)
    E10_6 = GuS(Entgeltgruppe.E_10, Stufe.sechs)
    E13_1 = GuS(Entgeltgruppe.E_13, Stufe.eins)
    E13_2 = GuS(Entgeltgruppe.E_13, Stufe.zwei)
    E13_3 = GuS(Entgeltgruppe.E_13, Stufe.drei)
    E13_4 = GuS(Entgeltgruppe.E_13, Stufe.vier)
    E13_5 = GuS(Entgeltgruppe.E_13, Stufe.fünf)
    E13_6 = GuS(Entgeltgruppe.E_13, Stufe.sechs)


def printAllGuS():
    """ Create a copy and paste product of the static fields for GuS.
        Hacky help to set them in the code to avoid UnknownVariable
        when doing this dynamically with setattr.
    """
    import itertools
    for e, s in itertools.product(Entgeltgruppe, Stufe):
        print("    E{}_{} = GuS(Entgeltgruppe.{}, Stufe.{})".format(e.value, s.value, e.name, s.name))


@dataclass(eq=True, frozen=True)
class Stelle:
    gus : GuS
    beginn : date

    def am(self, datum : date) -> Stelle:
        """
            :param datum: das Datum, für das die dann gültige Stelle ermittelt werden soll
            :return: entweder diese Stelle, falls es keine Veränderung zum Argumentdatum
                gibt; oder eine neue mit mindestens einem Stufenaufstieg und aktualisiertem
                "beginn" (zwischen dem jetzigen "beginn" und dem Argumentdatum)
        """
        neueStufe, neuesSeit = self.gus.stufe, self.beginn
        
        nächstesSeit = self.gus.stufe.nächsterAufstieg(self.beginn)
        while nächstesSeit <= datum:
            neuesSeit = nächstesSeit
            neueStufe = neueStufe.nächste()
            nächstesSeit = neueStufe.nächsterAufstieg(nächstesSeit)

        return self if neueStufe == self.gus.stufe else Stelle(GuS(self.gus.gruppe, neueStufe), neuesSeit)

            
def dec(euros):
    return decimal.Decimal(euros).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_UP)


class ÖtvKosten:

    """
    ein fixer Prozentsatz, der als Kostenzuschlag genommen wird
    """
    arbeitgeberKostenZuschlag = 0.3

    gehälter : Mapping [ Tuple[int, GuS], Gehalt ]
    
    def __init__(self, gehälter):
        self.gehälter = gehälter
        self.zuschlag = decimal.Decimal(1. + ÖtvKosten.arbeitgeberKostenZuschlag)

    def summeMonatlich(self, jahr: int, gus : GuS):
        """
            :return: die monatlichen Gesamtkosten mit Arbeitgeberzuschlag,
                    aber ohne Jahressonderzahlung
        """
        return self.gehälter[(jahr, gus)].brutto * self.zuschlag

    def sonderzahlung(self, jahr: int, gus : GuS):
        """
            :return: die Jahressonderzahlung
        """
        return self.gehälter[(jahr, gus)].sonderzahlung

    
if __name__ == "__main__":
    printAllGuS()
