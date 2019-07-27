'''
Created on Jul 23, 2019

@author: cb
'''
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from decimal import Decimal
from builtins import str
from typing import Mapping
import re


def resource(relativePath):
    import os
    path = Path(os.path.dirname(__file__))
    return path / "../../resources" / relativePath


def readExcel(excelName, sheetName):
    return pd.read_excel(resource(excelName),
                         sheet_name=sheetName, engine="xlrd")

# (Gruppe), Stufe x Jahr -> (Brutto, Jahressonderzahlung)


@dataclass
class Gehalt:
    """
        Die Monatsgehaltsdaten: Bruttogehalt (ohne Arbeitgeberzuschlag) und Sonderzahlung.
    """
    brutto : Decimal
    sonderzahlung: Decimal


@dataclass
class Entgeltgruppe:
    name : str
    jahr : int
    stufen : Mapping [ str, Gehalt]


gehaltBlockStart = re.compile("Gehalt für (\d+)")


def isGehaltBlockStart(cellStr):
    m = gehaltBlockStart.search(cellStr)
    return int(m.group(1)) if m else None


entgeltgruppenZeile = re.compile("E\s(\d+)\s")


def isEntgeltgruppenZeile(row):
    m = entgeltgruppenZeile.search(str(row[1]))
    return [str(int(x)) for x in row[2:]] if m else None


def isArbeitnehmerBrutto(row):
    if str(row[1]).startswith("Arbeitnehmer Brutto"):
        return [Decimal(x) for x in row[2:]]
    return None


def isJahressonderzahlung(row):
    if str(row[1]).startswith("Jahressonderzahlung"):
        return [Decimal(x) for x in row[2:]]
    return None

def parseGehälter(excel):
    
    jahr = None    
    for row in excel.itertuples():
        cellStr = str(row[1])
        if cellStr.startswith("Hilfstabelle"):
            print("Found Hilfstabelle in row {}, finished.".format(row[0]))
            break

        jahr = isGehaltBlockStart(cellStr)
        if jahr:
            print(jahr)
            continue
        
        stufen = isEntgeltgruppenZeile(row)
        if stufen:
            print(stufen)
            continue
        
        brutto = isArbeitnehmerBrutto(row)
        if brutto:
            print(brutto)
            continue
        
        sonder = isJahressonderzahlung(row)
        if sonder:
            print(sonder)
            continue


if __name__ == '__main__':
    excel = readExcel("E10 Personalkosten 2019-2021.xlsx", "E10")
    parseGehälter(excel)
