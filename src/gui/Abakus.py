import sys
import pathlib
import logging
import datetime
from PySide2 import  QtWidgets as qw
from PySide2.QtCore import QDate, QLocale, Qt
from PySide2.QtGui import QFontDatabase, QIcon
from gui.widgets import EnumCombo
from abakus.model import Entgeltgruppe, Stufe, Stelle, GuS
from abakus import laufend

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"


def pp(myStr):
    """
        pad string to avoid clipping in dropdowns
    """
    return " {}  ".format(myStr)


def offsetVonDate(fromDate):
    year, month = fromDate.year, fromDate.month + 2
    if month > 12:
        year, month = year + 1, month - 12
    return datetime.date(year, month , 1)


def offsetSeitDate(fromDate):
    year, month = fromDate.year, fromDate.month - 2
    if month < 1:
        year, month = year - 1, month + 12
    return datetime.date(year, month , 1)


def date2QDate(pyDate):
    return QDate(pyDate.year, pyDate.month, pyDate.day)


def germanDatePicker(selected: QDate) -> qw.QDateEdit:
    picker = qw.QDateEdit()
    
    picker.setDisplayFormat(pp("dd.MM.yyyy"))
    picker.setLocale(QLocale.German)

    picker.setCalendarPopup(True)
    calendar = picker.calendarWidget()
    calendar.setGridVisible(False)
    calendar.setFirstDayOfWeek(Qt.Monday)
    calendar.setHorizontalHeaderFormat(qw.QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
    calendar.setVerticalHeaderFormat(qw.QCalendarWidget.ISOWeekNumbers)
    
    picker.setDate(selected)
    return picker


def futurePicker(selected : QDate) -> qw.QDateEdit:

    picker = germanDatePicker(selected)
    picker.setMinimumDate(QDate.currentDate())
    return picker


def pastPicker(selected : QDate) -> qw.QDateEdit:
    picker = germanDatePicker(selected)
    picker.setMaximumDate(QDate.currentDate())
    return picker


class GruppeCombo(EnumCombo):

    def __init__(self):
        super().__init__(Entgeltgruppe, "Entgeltgruppe", lambda i : pp(i.name.replace("_", " ")))


class StufeCombo(EnumCombo):

    def __init__(self, label="Stufe"):
        super().__init__(Stufe, label, lambda i: pp(i.value))


class Beschäftigung(qw.QWidget):
    
    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()

        vonDate = date2QDate(offsetVonDate(datetime.date.today()))
        self.vonPicker = futurePicker(vonDate)
        
        bisDate = vonDate.addMonths(2)
        self.bisPicker = futurePicker(QDate(bisDate.year(), bisDate.month(), bisDate.daysInMonth()))

        zeile.addWidget(qw.QLabel("von"))
        zeile.addWidget(self.vonPicker)
        zeile.addWidget(qw.QLabel("bis"))
        zeile.addWidget(self.bisPicker)

        self.gruppe = GruppeCombo()
        zeile.addWidget(self.gruppe)

        self.stufe = StufeCombo()
        zeile.addWidget(self.stufe)

        zeile.addWidget(qw.QLabel("Umfang"))
        umfang = qw.QSpinBox()
        umfang.setRange(10, 100)
        umfang.setValue(100)
        umfang.setSuffix("% ")
        zeile.addWidget(umfang)

        zeile.addStretch(1)
        self.setLayout(zeile)


class Vorbeschäftigung(qw.QWidget):
    
    def __init__(self):
        super().__init__()

        stufenZeile = qw.QHBoxLayout()

        stufenZeile.addWidget(qw.QLabel("vorbeschäftigt"))
        istVor = qw.QCheckBox()
        istVor.click()
        stufenZeile.addWidget(istVor)

        seitLabel = qw.QLabel("seit")
        stufenZeile.addWidget(seitLabel)
        seitPicker = pastPicker(offsetSeitDate(datetime.date.today()))
        stufenZeile.addWidget(seitPicker)

        stufeAktuell = StufeCombo("Stufe aktuell")
        stufenZeile.addWidget(stufeAktuell)
        wechselPicker = futurePicker(offsetVonDate(datetime.date.today()))

        naechsterLabel = qw.QLabel("nächster Aufstieg")
        stufenZeile.addWidget(naechsterLabel)
        stufenZeile.addWidget(wechselPicker)

        stufenZeile.addStretch(1)
        self.setLayout(stufenZeile)

        elements = [seitLabel, seitPicker, stufeAktuell, naechsterLabel, wechselPicker]

        def toggle(state):
            for e in elements:
                e.setEnabled(state)
        
        istVor.stateChanged.connect(toggle)


class Abakus(qw.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abakus")

        layout = qw.QVBoxLayout()

        self.beschäftigung = Beschäftigung()
        layout.addWidget(self.beschäftigung)
        self.vorbeschäftigung = Vorbeschäftigung()
        layout.addWidget(self.vorbeschäftigung)
        
        berechnung = qw.QPushButton("Berechnung")
        berechnung.clicked.connect(self.berechne)
        layout.addWidget(berechnung)        

        layout.addStretch(1)
        self.setLayout(layout)
    
    def berechne(self):
        vonDate = qDateToPyDate(self.beschäftigung.vonPicker.date())
        bisDate = qDateToPyDate(self.beschäftigung.bisPicker.date())
        gruppe = self.beschäftigung.gruppe.currentItem()
        stufe = self.beschäftigung.stufe.currentItem()
        
        print("von = {}".format(vonDate))
        print("bis = {}".format(bisDate))
        print("gruppe = {}".format(gruppe))
        print("stufe = {}".format(stufe))

        for e in laufend.monatsListe(Stelle(GuS(gruppe, stufe), vonDate), vonDate, bisDate):
            print(e)

def qDateToPyDate(qDate : QDate) -> datetime.date:
    return datetime.date(qDate.year(), qDate.month(), qDate.day())

def resourcePath(resPath):
    targetPath = pathlib.Path(__file__).parent / "../../resources" / resPath
    targetPath = targetPath.resolve()
    if not targetPath.exists():
        logging.error("Ressource '{}' wurde nicht gefunden (gesucht in '{}')".format(resPath, targetPath))
    return str(targetPath)


if __name__ == "__main__":
    fontPath = resourcePath("NotoSansDisplay-Regular.ttf")
    iconPath = resourcePath("icon.svg")
    cssPath = resourcePath("stylesheet.css")
    with open(cssPath, "r") as styleFile:
        styleSheet = str(styleFile.read())

    app = qw.QApplication([])
    QFontDatabase().addApplicationFont(fontPath)
    
    app.setStyleSheet(styleSheet)
    app.setWindowIcon(QIcon(iconPath))

    widget = Abakus()
    widget.show()

    sys.exit(app.exec_())

