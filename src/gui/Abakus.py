import sys
import pathlib
import logging
import datetime
from PySide2 import QtWidgets as qw
from PySide2.QtCore import QDate, QLocale, Qt
from PySide2.QtGui import QFontDatabase, QIcon
from gui.widgets import EnumCombo
from abakus.model import Entgeltgruppe, Stufe, Stelle, GuS
from abakus import laufend
from gui.cssVars import varredCss2Css

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


class WeiterOderNeu(qw.QWidget):
    
    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()

        neuButton = qw.QRadioButton("Neueinstellung")
        self.weiterButton = qw.QRadioButton("Weiterbeschäftigung")

        # strangely, the group signal is not emitted
        self.group = qw.QButtonGroup()
        self.group.addButton(neuButton)
        self.group.addButton(self.weiterButton)

        zeile.addWidget(neuButton)
        zeile.addWidget(self.weiterButton)

        self.stufe = StufeCombo("Stufe")
        zeile.addWidget(self.stufe)

        seitLabel = qw.QLabel("seit")
        zeile.addWidget(seitLabel)
        self.seitPicker = pastPicker(offsetSeitDate(datetime.date.today()))
        zeile.addWidget(self.seitPicker)

        def clicked(btn):
            istWeiter = btn is self.weiterButton
            seitLabel.setEnabled(istWeiter)
            self.seitPicker.setEnabled(istWeiter)

        self.group.buttonClicked.connect(clicked)
        neuButton.click()

        zeile.addStretch(1)
        self.setLayout(zeile)
    
    def istWeiter(self):
        return self.group.checkedButton() is self.weiterButton

    def seit(self):
        return self.seitPicker.date()


class Einstellung(qw.QWidget):
    
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

        zeile.addWidget(qw.QLabel("Umfang"))
        self.umfang = qw.QSpinBox()
        self.umfang.setRange(10, 100)
        self.umfang.setSingleStep(10)
        self.umfang.setValue(100)
        self.umfang.setSuffix("% ")
        zeile.addWidget(self.umfang)

        zeile.addStretch(1)
        self.setLayout(zeile)


class Abakus(qw.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abakus")

        layout = qw.QVBoxLayout()

        self.beschäftigung = Einstellung()
        layout.addWidget(self.beschäftigung)
        self.weiterOderNeu = WeiterOderNeu()
        layout.addWidget(self.weiterOderNeu)
        
        berechnung = qw.QPushButton("Berechnung")
        berechnung.clicked.connect(self.berechne)
        layout.addWidget(berechnung)        

        layout.addStretch(1)
        self.setLayout(layout)
    
    def berechne(self):
        bisDate = qDateToPyDate(self.beschäftigung.bisPicker.date())
        gruppe = self.beschäftigung.gruppe.currentItem()
        stufe = self.weiterOderNeu.stufe.currentItem()
        umfang = self.beschäftigung.umfang.value()
        
        vonDate = qDateToPyDate(self.beschäftigung.vonPicker.date())
        stufenStart = qDateToPyDate(self.weiterOderNeu.seit()) if self.weiterOderNeu.istWeiter() else vonDate
        
        stelle = Stelle(GuS(gruppe, stufe), stufenStart)

        for e in laufend.monatsListe(stelle, vonDate, bisDate):
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
    cssTmplPath = resourcePath("stylesheet.vars.css")
    with open(cssTmplPath, "r") as styleFile:
        styleSheet = "\n".join(varredCss2Css(styleFile.readlines()))

    app = qw.QApplication([])
    QFontDatabase().addApplicationFont(fontPath)
    
    app.setStyleSheet(styleSheet)
    app.setWindowIcon(QIcon(iconPath))

    widget = Abakus()
    widget.show()

    sys.exit(app.exec_())

