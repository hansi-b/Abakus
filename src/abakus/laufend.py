from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Tuple, Optional

from abakus.model import Stelle, ÖtvKosten, dec

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


@dataclass(eq=True, frozen=True)
class MonatsKosten:
    stichtag: date
    stelle: Stelle
    kosten: Decimal
    sonderzahlung: Decimal


class Anstellung:
    """
        Eine Geschichte von Stellen
    """
    
    def __init__(self, stelle: Stelle, von: date, bis: date):
        """
            :param stelle: die Stelle, auf deren Grundlage gerechnet werden soll.
                            Der Beginn der Stelle darf nicht nach dem "von" liegen.
            :param von: das Datum, ab dem iteriert werden soll. Darf nicht vor dem Beginn der Stelle liegen.
            :param bis: das Datum, bis zu dem iteriert werden soll. Im Moment wird nur der volle Monat berücksichtigt.
        """
        assert stelle.beginn <= von, "Der Beginn der Stelle {} liegt nach dem Anfangsdatum {}".format(stelle, von);
        assert von <= bis, "Das Anfangsdatum {} liegt nach dem Enddatum {}".format(von, bis)

        self.stelle = stelle
        self.von = von
        self.bis = bis
        
        self.monatsListe = self._initMonatsListe()

    def _initMonatsListe(self) -> List[Tuple[date, Stelle]]:
        """
            Gibt pro Monatsende für den gegebenen Zeitraum (beides inklusive) die dann gültige Stelle zurück
            als Paar (date, Stelle).

            :return: eine Liste von Paaren (Stichtag, Stelle) mit den monatsletzten Tagen und der dann gültigen Stelle
        """
        currDate = lastDateInMonth(self.von)
        currStelle = self.stelle
    
        result = []
        while currDate <= self.bis:
            currStelle = currStelle.am(currDate)
            result.append((currDate, currStelle))
            currDate = lastDateInNextMonth(currDate)
        return result

    def monateAngestellt(self, year: int) -> int:
        """
        :return: the number of months [0-12] for which this Anstellung applied in the argument year
        """
        return sum(1 for t, _s in self.monatsListe if t.year == year)

    def findBaseStellen(self, year: int) -> List[Stelle]:
        """
        :return: the Stellen which make up the Basis for the Sonderzahlung in the argument year
        """
        stellenImJahr = list(reversed([(t, s) for t, s in self.monatsListe if t.year == year and t.month < 12]))

        # default case: average over past
        if not stellenImJahr:
            raise Exception("Cannot compute BaseStellen - no data for {}".format(year))
        
        baseStellen = [None, None, None]
        for refTag, gültigeStelle in stellenImJahr:
            # Jul+Aug+Sep are the default base months
            for mIndx, mth in enumerate((7, 8, 9)):
                if not baseStellen[mIndx] and refTag.month == mth:
                    baseStellen[mIndx] = gültigeStelle
            if all(baseStellen):
                break

        # falls es keine Bases gab, dann gilt das letzte Gehalt
        if not any(baseStellen):
            baseStellen[2] = stellenImJahr[-1][1]

        return [s for s in baseStellen if s]

    def __iter__(self):
        return self.monatsListe.__iter__()


class Summierer:

    def __init__(self, ötv: ÖtvKosten):
        self.ötv = ötv

    def calc(self, anstellung : Anstellung) -> Tuple[Decimal, List[MonatsKosten]]:

        total, details = Decimal(0), []
        
        for stichtag, stelle in anstellung:
            kosten = self.ötv.monatsGesamt(stichtag.year, stelle)
            sonderzahlung = self.calcSonderzahlung(stichtag, anstellung)

            details.append(MonatsKosten(stichtag, stelle, kosten, sonderzahlung or Decimal(0.)))
            total += kosten

        return total, details

    def calcSonderzahlung(self, stichtag: date, anstellung : Anstellung) -> Optional[Decimal]:
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
        referenzJahr = stichtag.year
        if anstellung.bis < date(referenzJahr, 12, 1):
            return Decimal(0.)

        baseStellen = anstellung.findBaseStellen(referenzJahr)

        sonderzahlBases = [self.ötv.sonderzahlung(referenzJahr, stelle) for stelle in baseStellen]

        # be careful not to round the Anteil - this amplifies to many Euros
        anteil = Decimal(anstellung.monateAngestellt(referenzJahr) / 12.)

        return dec(anteil * sum(sonderzahlBases) / len(sonderzahlBases))


if __name__ == '__main__':
    pass
