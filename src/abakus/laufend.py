from datetime import date
from abakus.model import Stelle
from calendar import monthrange
from typing import List, Tuple

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


def lastDateInMonth(d : date):
    return date(d.year, d.month, monthrange(d.year, d.month)[1])


def lastDateInNextMonth(d : date):
    m, y = d.month, d.year
    newM, newY = (m + 1, y) if m < 12 else (1, y + 1)
    return lastDateInMonth(date(newY, newM, 1)) 


def monatsListe(stelle : Stelle, von : date , bis : date) -> List[Tuple[date, Stelle]]:
    """
        Gibt pro Monatsende für den gegebenen Zeitraum (beides inklusive) die dann gültige Stelle zurück
        als Paar (date, Stelle).

        :param stelle: die Stelle, auf deren Grundlage gerechnet werden soll. Der Beginn der Stelle muß vor dem "von" liegen.
        :param von: das Datum, ab dem iteriert werden soll. Darf nicht vor dem Beginn der Stelle liegen.
        :param bis: das Datum, bis zu dem iteriert werden soll. Im Moment wird nur der Monat berücksichtigt.
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


if __name__ == '__main__':
    pass
