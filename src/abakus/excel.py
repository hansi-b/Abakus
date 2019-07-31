'''
Created on Jul 23, 2019

@author: cb
'''
import pandas as pd
from pathlib import Path
from decimal import Decimal
from builtins import str
import re
import logging
from _decimal import ROUND_HALF_UP
from abakus.model import Stufe, ÖTV, Entgeltgruppe, Gehalt


def resource(relativePath):
    import os
    path = Path(os.path.dirname(__file__))
    return path / "../../resources" / relativePath


gehaltBlockStart = re.compile("Gehalt für (\d+)")


def isGehaltBlockStart(cellStr):
    m = gehaltBlockStart.search(cellStr)
    return int(m.group(1)) if m else None


entgeltgruppenZeile = re.compile("E\s(\d+)\s")


def isEntgeltgruppenZeile(row):
    m = entgeltgruppenZeile.search(str(row[1]))
    return [Stufe(int(x)) for x in row[2:]] if m else None


def isArbeitnehmerBrutto(row):
    if str(row[1]).startswith("Arbeitnehmer Brutto"):
        return [Decimal(x) for x in row[2:]]
    return None


def isJahressonderzahlung(row):
    if str(row[1]).startswith("Jahressonderzahlung"):
        return [Decimal(x) for x in row[2:]]
    return None


def iterGehälter(excel):
        
    aktJahr, aktStufen, aktBrutto, aktSonder = None, None, None, None
        
    for row in excel.itertuples():
        cellStr = str(row[1])
        if cellStr.startswith("Hilfstabelle"):
            logging.info("Found Hilfstabelle in row {}, finished.".format(row[0]))
            break

        jahr = isGehaltBlockStart(cellStr)
        if jahr:
            if aktJahr:
                logging.warning("Unerwartete weitere Jahresangabe {} gefunden, ignoriere vorige {}".format(jahr, aktJahr))
            aktJahr = jahr
            continue
        
        stufen = isEntgeltgruppenZeile(row)
        if stufen:
            if len(stufen) != len(Stufe):
                logging.error("Es wurden {} Stufen erwartet, aber {} ausgelesen: {}".format(len(Stufe), len(stufen), stufen))
            if aktStufen:
                logging.warning("Unerwartete weitere Stufenzeile {} gefunden, ignoriere vorige {}".format(stufen, aktStufen))
            aktStufen = stufen
            continue
        
        brutto = isArbeitnehmerBrutto(row)
        if brutto:
            if aktBrutto:
                logging.warning("Unerwartete weitere Gehaltszeile {} gefunden, ignoriere vorige {}".format(brutto, aktBrutto))
            aktBrutto = brutto
            continue
        
        sonder = isJahressonderzahlung(row)
        if sonder:
            if aktSonder:
                logging.warning("Unerwartete weitere Gehaltszeile {} gefunden, ignoriere vorige {}".format(aktSonder, sonder))
            aktSonder = sonder

            yield createJahrAndGruppe(aktJahr, aktStufen, aktBrutto, aktSonder)            
            aktJahr, aktStufen, aktBrutto, aktSonder = None, None, None, None
            continue


def dec(euros):
    return Decimal(euros).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def createJahrAndGruppe(jahr, stufen, brutto, sonder):
    eg = Entgeltgruppe({stu : Gehalt(dec(bru), dec(son)) for stu, bru, son in zip(stufen, brutto, sonder)})
    return jahr, eg


def createÖtv():
    ötv = ÖTV({})

    for excelName, sheetName in (("E10 Personalkosten 2019-2021.xlsx", "E10"),
                                ("E13 Personalkosten 2019-2021.xlsx", "E13")):
        excelDf = pd.read_excel(resource(excelName),
                         sheet_name=sheetName, engine="xlrd")
        for jahr, gruppe in iterGehälter(excelDf):
            ötv.gehälter[(jahr, sheetName)] = gruppe

    return ötv

    
if __name__ == '__main__':
    ötv = createÖtv()
    for k, v in ötv.gehälter.items():
        print(k)
        print(v)
