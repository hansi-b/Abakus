from typing import Sequence
from decimal import Decimal
from babel.numbers import parse_decimal
from abakus.model import ÖtvKosten, Entgeltgruppe, Gehalt, GuS, Stufe

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"


def asEntgeltgruppe(vStr):
    return Entgeltgruppe[vStr.upper().replace("E1", "E_1").replace("E ", "E_")]


def asPerc(vStr):
    v = parse_decimal(vStr, locale="de")
    if v > 100 or 0 > v: raise ValueError
    return v


def asGehalt(vStr):
    v = parse_decimal(vStr, locale="de")
    if v < 0 : raise ValueError
    return v


class ÖtvFormatException(Exception):
    
    def __init__(self, errors):
        super().__init__("Fehler im ÖTV-Format")
        self.errors = errors


class ÖtvCsvParser:
    
    expectedPartCount = 3 + 6

    def __init__(self):

        self._lNo = None
        self.errors = []
        self.ötv = ÖtvKosten()

    def parse(self, csvLines : Sequence[str]) -> ÖtvKosten:
        """
            Read ÖTV Tarife from a custom CSV format and add the
            information to this ötv object
        """

        for lNo, rawLine in enumerate(csvLines, start=1):
            self._lNo = lNo
            
            parts = rawLine.strip().split()
            if not len(parts) or parts[0].startswith('#'):
                continue
    
            if len(parts) != ÖtvCsvParser.expectedPartCount:
                self._newErr(" hat {} Felder ({} erwartet): {}".format(len(parts), ÖtvCsvParser.expectedPartCount, parts))
                continue
            
            try :
                year, gruppe, gehälter = self._parseParts(parts)
                for gIdx, g in enumerate(gehälter, start=1):
                    self.ötv.mitGehalt(year, GuS(gruppe, Stufe(gIdx)), g)
            except ValueError:
                continue
                    
        if len(self.errors):
            raise ÖtvFormatException(self.errors)
    
        return self.ötv

    def _parseParts(self, parts):
        
        def part2Val(idx, valFunc, errMsg):
            try:
                return valFunc(parts[idx])
            except (ValueError, KeyError):
                self._newErr(", Feld {}: {} '{}'".format(idx + 1, errMsg, parts[idx]))
                return None
        
        year = part2Val(0, int, "Ungültige Jahreszahl")
        gruppe = part2Val(1, asEntgeltgruppe,
                          "Unbekannte Gruppe (bekannt sind: {})".format([e.name for e in Entgeltgruppe]))
        sonderProzent = part2Val(2, asPerc, "Ungültige Prozentangabe für Jahressonderzahlung")

        bruttos = [part2Val(p, asGehalt, "Ungültiges Bruttogehalt") for p in range(3, 9)]

        if not all([year, gruppe, sonderProzent] + bruttos): raise ValueError

        gehälter = [Gehalt.by(b, b * sonderProzent / Decimal(100.)) for b in bruttos]
        
        return year, gruppe, gehälter
        
    def _newErr(self, msg):
        self.errors.append("Zeile {}{}".format(self._lNo, msg))


if __name__ == '__main__':
    from abakus import resources
    try:
        with open(resources.path("ötv.csv")) as csvFile:
            ÖtvCsvParser().parse(csvFile)
    except ÖtvFormatException as ö:
        for e in ö.errors:
            print(e)
    else:
        print("ok!")
