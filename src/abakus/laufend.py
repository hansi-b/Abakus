from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Tuple, Union, Optional

from abakus.model import Stelle, GuS, dec, ÖtvKosten

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

"""
* gegeben einen Monat in der Zukunft wollen wir die Kosten
  wissen
    * vor dem/im Zeitraum kann ein Stufenaufstieg erfolgen

* separat berücksichtigen:
  * im November gibt es u.U. eine Jahressonderzahlung
"""


def lastDateInMonth(d: date):
    return date(d.year, d.month, monthrange(d.year, d.month)[1])


def lastDateInNextMonth(d: date):
    m, y = d.month, d.year
    newM, newY = (m + 1, y) if m < 12 else (1, y + 1)
    return lastDateInMonth(date(newY, newM, 1))


def monatsListe(stelle: Stelle, von: date, bis: date) -> List[Tuple[date, Stelle]]:
    """
        Gibt pro Monatsende für den gegebenen Zeitraum (beides inklusive) die dann gültige Stelle zurück
        als Paar (date, Stelle).

        :param stelle: die Stelle, auf deren Grundlage gerechnet werden soll.
                        Der Beginn der Stelle darf nicht nach dem "von" liegen.
        :param von: das Datum, ab dem iteriert werden soll. Darf nicht vor dem Beginn der Stelle liegen.
        :param bis: das Datum, bis zu dem iteriert werden soll. Im Moment wird nur der volle Monat berücksichtigt.
        :return: eine Liste von Paaren (Stichtag, Stelle) mit den monatsletzten Tagen und der dann gültigen Stelle
    """
    assert stelle.beginn <= von, "Der Beginn der Stelle {} liegt nach dem Anfangsdatum {}".format(stelle, von);
    assert von <= bis, "Das Anfangsdatum {} liegt nach dem Enddatum {}".format(von, bis)

    currDate = lastDateInMonth(von)
    currStelle = stelle

    result = []
    while currDate <= bis:
        currStelle = currStelle.am(currDate)
        result.append((currDate, currStelle))
        currDate = lastDateInNextMonth(currDate)
    return result


@dataclass(eq=True, frozen=True)
class MonatsKosten:
    stichtag: date
    gus: GuS
    umfang: int
    kosten: Decimal
    sonderzahlung: Decimal


class Summierer:

    def __init__(self, ötv: ÖtvKosten):
        self.ötv = ötv

    def calc(self, stelle: Stelle, von: date, bis: date, umfang: int) -> Tuple[Decimal, List[MonatsKosten]]:
        """
        :param umfang: a positive integer up to including 100, indicating the percentage of work
        """

        stellePerMonat = monatsListe(stelle, von, bis)
        umfangFaktor = Decimal(umfang / 100.)

        total, details = Decimal(0), []
        for i, (stichtag, aktStelle) in enumerate(stellePerMonat):
            kosten = dec(umfangFaktor * self.ötv.summeMonatlich(stichtag.year, aktStelle.gus))
            sonderzahlung = self.calcSonderzahlung(stichtag, bis, stellePerMonat[:i])
            details.append(MonatsKosten(stichtag, aktStelle.gus, umfang, kosten, sonderzahlung or Decimal(0.)))
            total += kosten

        return total, details

    def calcSonderzahlung(self, stichtag: date, bis: date, vorgeschichte: List[Tuple[date, Stelle]]) -> Optional[Decimal]:
        """
        Calculate the Jahressonderzahlung according to
        https://oeffentlicher-dienst.info/tv-l/allg/jahressonderzahlung.html
        
        :return: None if Sonderzahlung does not apply (i.e., Stichtag is not November),
                    or a Decimal denoting the Sonderzahlung
        """
        # if not Nov, nothing to do here
        if stichtag.month != 11:
            return None
        # if end date is before Dez, it's zero
        if bis < date(stichtag.year, 12, 1):
            return Decimal(0.)

        # default case: average over past
        if len(vorgeschichte) == 0:
            raise Exception("Cannot compute Sonderzahlung without Vorgeschichte")

        baseStellen = [None, None, None]
        for refTag, gültigeStelle in reversed(vorgeschichte):
            # Jul+Aug+Sep are the default base months
            for mIndx, mth in enumerate((7, 8, 9)):
                if not baseStellen[mIndx] and refTag < date(stichtag.year, mth + 1, 1):
                    baseStellen[mIndx] = gültigeStelle
            if all(baseStellen):
                break

        # falls es keine Bases gab, dann gilt das letzte Gehalt
        if not any(baseStellen):
            baseStellen[2] = vorgeschichte[-1][1]

        sonderzahls = [self.ötv.sonderzahlung(stichtag.year, stelle.gus) for stelle in baseStellen if stelle]
        # print(sonderzahls)
        return sum(sonderzahls) / len(sonderzahls)


if __name__ == '__main__':
    pass
