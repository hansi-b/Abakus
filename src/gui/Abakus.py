__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

import sys
from PySide2 import  QtWidgets as qw
from PySide2.QtCore import QDate, QLocale, Qt
import datetime
from PySide2.QtGui import QFontDatabase, QFont, QIcon
import pathlib
import logging


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

        zeile.addWidget(qw.QLabel("Entgeltgruppe"))
        gruppe = qw.QComboBox()
        gruppe.addItem(pp("E 10"))
        gruppe.addItem(pp("E 13"))
        zeile.addWidget(gruppe)

        zeile.addWidget(qw.QLabel("Stufe"))
        stufe = qw.QComboBox()
        for s in "1 2 3 4 5 6".split():
            stufe.addItem(pp(s))
        zeile.addWidget(stufe)

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

        stufeLabel = qw.QLabel("Stufe aktuell")
        stufenZeile.addWidget(stufeLabel)
        stufe = qw.QComboBox()
        for s in "1 2 3 4 5 6".split():
            stufe.addItem(pp(s))
        stufenZeile.addWidget(stufe)
        wechselPicker = futurePicker(offsetVonDate(datetime.date.today()))

        naechsterLabel = qw.QLabel("nächster Aufstieg")
        stufenZeile.addWidget(naechsterLabel)
        stufenZeile.addWidget(wechselPicker)

        stufenZeile.addStretch(1)
        self.setLayout(stufenZeile)

        elements = [seitLabel, seitPicker, stufeLabel, stufe, naechsterLabel, wechselPicker]

        def toggle(state):
            for e in elements:
                e.setEnabled(state)
        
        istVor.stateChanged.connect(toggle)


class Abakus(qw.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abakus")

        self.layout = qw.QVBoxLayout()

        self.layout.addWidget(Beschäftigung())
        self.layout.addWidget(Vorbeschäftigung())

        self.layout.addStretch(1)
        self.setLayout(self.layout)


def resourcePath(resPath):
    targetPath = pathlib.Path(__file__).parent / "../../resources" / resPath
    targetPath = targetPath.resolve()
    if not targetPath.exists():
        logging.error("Ressource '{}' wurde nicht gefunden (gesucht in '{}')".format(resPath, targetPath))
    return targetPath


if __name__ == "__main__":
    fontPath = resourcePath("NotoSansDisplay-Regular.ttf")
    iconPath = resourcePath("icon.svg")
    
    app = qw.QApplication([])
    QFontDatabase().addApplicationFont(str(fontPath))
    app.setFont(QFont("Noto Sans Display", 12))
    app.setWindowIcon(QIcon(str(iconPath)))
#     print(app.font())

    widget = Abakus()
    widget.show()

    sys.exit(app.exec_())

