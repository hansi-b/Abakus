import sys
from PySide2 import  QtWidgets as qw
from PySide2.QtCore import QDate, QLocale, Qt
import datetime


def offsetVonDate(fromDate):
    year, month = fromDate.year, fromDate.month + 2
    if month > 12:
        year, month = year + 1, month - 12
    return datetime.date(year, month , 1)


def date2QDate(pyDate):
    return QDate.fromString(str(pyDate), "yyyy-MM-dd")


def germanDatePicker(selected: QDate) -> qw.QDateEdit:
    picker = qw.QDateEdit()
    
    picker.setDisplayFormat("dd.MM.yyyy")
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


class Zeitraum(qw.QWidget):
    
    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()

        self.vonPicker = futurePicker(offsetVonDate(datetime.date.today()))
        self.bisPicker = futurePicker(self.vonPicker.date().addMonths(3)) 

        zeile.addWidget(qw.QLabel("von"))
        zeile.addWidget(self.vonPicker)
        zeile.addWidget(qw.QLabel("bis"))
        zeile.addWidget(self.bisPicker)

        zeile.addStretch(1)
        self.setLayout(zeile)


class GruppeUndStufe(qw.QWidget):
    
    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()

        zeile.addWidget(qw.QLabel("Entgeltgruppe"))
        gruppe = qw.QComboBox()
        gruppe.addItem("E 10")
        gruppe.addItem("E 13")
        zeile.addWidget(gruppe)

        zeile.addWidget(qw.QLabel("Stufe"))
        stufe = qw.QComboBox()
        for s in "1 2 3 4 5 6".split():
            stufe.addItem(s)
        zeile.addWidget(stufe)

        zeile.addWidget(qw.QLabel("Umfang"))
        umfang = qw.QSpinBox()
        umfang.setRange(10, 100)
        umfang.setValue(100)
        umfang.setSuffix("%")
        zeile.addWidget(umfang)

        zeile.addStretch(1)
        self.setLayout(zeile)


class Vorbeschäftigung(qw.QWidget):
    
    def __init__(self):
        super().__init__()
        
        stufenZeile = qw.QHBoxLayout()

        stufenZeile.addWidget(qw.QLabel("beschäftigt seit"))
        seitPicker = pastPicker(offsetVonDate(datetime.date.today()))
        stufenZeile.addWidget(seitPicker)

        stufenZeile.addWidget(qw.QLabel("Stufe aktuell"))
        stufe = qw.QComboBox()
        for s in "1 2 3 4 5 6".split():
            stufe.addItem(s)
        stufenZeile.addWidget(stufe)
        wechselPicker = futurePicker(offsetVonDate(datetime.date.today()))

        stufenZeile.addWidget(qw.QLabel("nächster Aufstieg"))
        stufenZeile.addWidget(wechselPicker)

        stufenZeile.addStretch(1)
        self.setLayout(stufenZeile)


class Abakus(qw.QWidget):

    def __init__(self):
        super().__init__()

        self.layout = qw.QVBoxLayout()

        self.layout.addWidget(Zeitraum())
        self.layout.addWidget(GruppeUndStufe())
        self.layout.addWidget(Vorbeschäftigung())

        self.layout.addStretch(1)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = qw.QApplication([])
    widget = Abakus()
    # widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())

