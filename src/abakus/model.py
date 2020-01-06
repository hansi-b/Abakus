from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Mapping

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

    def nächsterAufstieg(self, letzterAufstieg: date) -> date:
        return date(letzterAufstieg.year + self.jahre,  #
                    letzterAufstieg.month,  #
                    letzterAufstieg.day)


class Entgeltgruppe(Enum):
    """
        Definition der Entgeltgruppen, für die Gehaltsdaten vorliegen
        Sonderzahlung laut https://oeffentlicher-dienst.info/tv-l/allg/jahressonderzahlung.html
    """
    E_10 = 10
    E_13 = 13
    

@dataclass(eq=True, frozen=True)
class GuS:
    """
        Entgeltgruppe und Stufe
    """
    gruppe: Entgeltgruppe
    stufe: Stufe


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
    """ Create a copy-&-paste product of the static fields for GuS.
        Hacky help to set them in the code to avoid UnknownVariable
        when doing this dynamically with setattr.
    """
    import itertools
    for e, s in itertools.product(Entgeltgruppe, Stufe):
        print("    {}_{} = GuS(Entgeltgruppe.{}, Stufe.{})".format(e.name.replace("_", ""), s.value, e.name, s.name))


def dec(euros:float):
    return Decimal(euros).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


DEC_100 = dec(100)


@dataclass(eq=True, frozen=True)
class Stelle:
    gus: GuS
    beginn: date
    umfangProzent: Decimal = DEC_100

    def anteilig(self, zahl: Decimal):
        return zahl * self.umfangProzent / DEC_100

    def am(self, datum: date) -> Stelle:  # @UndefinedVariable
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

        return self if neueStufe == self.gus.stufe else Stelle(GuS(self.gus.gruppe, neueStufe),
                                                               neuesSeit, self.umfangProzent)


@dataclass(eq=True, frozen=True)
class Gehälter:
    sonderZahlProzent: Decimal
    bruttoByStufe: Mapping[Stufe, Decimal]


class ÖtvKosten:
    
    """
    ein fixer Prozentsatz, der als Kostenzuschlag genommen wird
    """
    arbeitgeberKostenZuschlag = 0.3

    def __init__(self):
        # Mapping[Tuple[int, Entgeltgruppe], Gehälter]
        self.__gehälter = {}
        self.zuschlag = Decimal(1. + ÖtvKosten.arbeitgeberKostenZuschlag)

    def mitGehalt(self, jahr: int, gruppe : Entgeltgruppe, gehälter : Gehälter):
        """
            Setzt für das gegebene Jahr und die gegebene Gruppe und Stufe das gegebene Gehalt fest.
            :raise AssertionError: falls für Jahr, Gruppe und Stufe schon ein Gehalt gesetzt ist
        """
        key = (jahr, gruppe)
        assert key not in self.__gehälter, "Gehalt für {} in {} schon gesetzt (ist {})".format(jahr, gruppe, self.__gehälter[key])
        self.__gehälter[key] = gehälter

    def monatsGesamt(self, jahr: int, stelle: Stelle):
        return stelle.anteilig(self._monatsGesamt(jahr, stelle.gus))

    def _monatsGesamt(self, jahr: int, gus: GuS):
        """
            :return: die monatlichen Gesamtkosten mit Arbeitgeberzuschlag,
                    aber ohne Jahressonderzahlung
        """
        return dec(self.__getGehälter(jahr, gus.gruppe).bruttoByStufe[gus.stufe] * self.zuschlag)

    def sonderzahlung(self, jahr: int, stelle: Stelle):
        
        return self.monatsGesamt(jahr, stelle) * self._sonderZahlProzent(jahr, stelle.gus) / DEC_100

    def _sonderZahlProzent(self, jahr: int, gus: GuS):
        """
            :return: die Jahressonderzahlung in Prozent
        """
        return self.__getGehälter(jahr, gus.gruppe).sonderZahlProzent

    def __getGehälter(self, jahr: int, gruppe : Entgeltgruppe) -> Gehälter:
        """
            Look up the wanted Gehälter, with a fallback for the last year in which we have data.
        """
        key = (jahr, gruppe)
        if not key in self.__gehälter:
            mögliche = [(j, g) for j, g in self.__gehälter.keys() if g == gruppe]
            if not mögliche:
                raise AssertionError("Keine Gehaltsdaten für {} verfügbar".format(gruppe))
            key = max(mögliche)
        return self.__gehälter[key]


if __name__ == "__main__":
    printAllGuS()
