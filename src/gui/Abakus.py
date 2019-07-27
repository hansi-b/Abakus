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


def futureDatePicker(selected : QDate) -> qw.QDateEdit:
    picker = qw.QDateEdit()
    
    picker.setDisplayFormat("dd.MM.yyyy")
    picker.setLocale(QLocale.German)

    picker.setCalendarPopup(True)
    calendar = picker.calendarWidget()
    calendar.setGridVisible(False)
    calendar.setFirstDayOfWeek(Qt.Monday)
    calendar.setHorizontalHeaderFormat(qw.QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
    calendar.setVerticalHeaderFormat(qw.QCalendarWidget.ISOWeekNumbers)
    
    picker.setMinimumDate(QDate.currentDate())
    picker.setDate(selected)

    return picker


class Zeitraum(qw.QWidget):
    
    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()

        self.vonPicker = futureDatePicker(offsetVonDate(datetime.date.today()))
        self.bisPicker = futureDatePicker(self.vonPicker.date().addMonths(3)) 

        zeile.addWidget(qw.QLabel("von"))
        zeile.addWidget(self.vonPicker)
        zeile.addWidget(qw.QLabel("bis"))
        zeile.addWidget(self.bisPicker)

        zeile.addStretch(1)
        self.setLayout(zeile)


class Gruppe(qw.QWidget):
    
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
        stufe.addItem("1")
        stufe.addItem("2")
        stufe.addItem("3")
        stufe.addItem("4")
        stufe.addItem("5")
        stufe.addItem("6")
        zeile.addWidget(stufe)

        zeile.addStretch(1)
        self.setLayout(zeile)


class Abakus(qw.QWidget):

    def __init__(self):
        super().__init__()

        self.layout = qw.QVBoxLayout()

        self.layout.addWidget(Zeitraum())
        self.layout.addWidget(Gruppe())

        self.layout.addStretch(1)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = qw.QApplication([])
    widget = Abakus()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())

