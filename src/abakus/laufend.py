import decimal
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from typing import List, Tuple

from abakus.model import Stelle, GuS

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
    umfang: float
    kosten: decimal.Decimal
    sonderzahlung: decimal.Decimal


class Summierer:

    def __init__(self, ötv):
        self.ötv = ötv

    def calc(self, stelle: Stelle, von: date, bis: date, umfang: float) -> Tuple[decimal.Decimal, List[MonatsKosten]]:
        total = decimal.Decimal(0)
        details = []
        for stichtag, aktStelle in monatsListe(stelle, von, bis):
            kosten = self.ötv.summeMonatlich(stichtag.year, aktStelle.gus)
            details.append(MonatsKosten(stichtag, aktStelle.gus, umfang, kosten, decimal.Decimal(0)))
            total += kosten

        return total, details


if __name__ == '__main__':
    pass
