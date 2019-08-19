import sys
import io
import csv
import pathlib
import logging
import datetime
from decimal import Decimal
from PySide2 import QtWidgets as qw
from PySide2.QtCore import QDate, QLocale, Qt
from PySide2.QtGui import QFontDatabase, QIcon, QKeySequence
from gui.widgets import EnumCombo
from gui.cssVars import varredCss2Css
from abakus.model import Entgeltgruppe, Stufe, Stelle, GuS
from abakus import laufend, excel
import decimal

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


def qDate2date(qDate : QDate) -> datetime.date:
    return datetime.date(qDate.year(), qDate.month(), qDate.day())


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


# don't want to have to rely on the right locale being available
monthNames = "Jan Feb Mär Apr Mai Jun Jul Aug Sep Okt Nov Dez".split()


class Details(qw.QWidget):

    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()      

        self.table = qw.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setEditTriggers(qw.QTableWidget.NoEditTriggers)
        
        for cIdx, label in enumerate("Monat Gruppe Stufe % Kosten(€)".split()):
            self.table.setHorizontalHeaderItem(cIdx, qw.QTableWidgetItem(label))

        self.table.horizontalHeader().setSectionResizeMode(qw.QHeaderView.ResizeMode.Stretch)
        self.table.setSizeAdjustPolicy(qw.QTableWidget.SizeAdjustPolicy.AdjustToContents)

        zeile.addWidget(self.table)
        zeile.setContentsMargins(0, 0, 0, 0)
        self.setLayout(zeile)

    def keyPressEvent(self, event):
        """
        copied from https://stackoverflow.com/a/40473855
        """
        if event.matches(QKeySequence.Copy):
            selection = self.table.selectedIndexes()
            if selection:
                rows = sorted(index.row() for index in selection)
                columns = sorted(index.column() for index in selection)
                rowcount = rows[-1] - rows[0] + 1
                colcount = columns[-1] - columns[0] + 1
                table = [[''] * colcount for _ in range(rowcount)]
                for index in selection:
                    row = index.row() - rows[0]
                    column = index.column() - columns[0]
                    table[row][column] = index.data()
                stream = io.StringIO()
                csv.writer(stream, delimiter='\t').writerows(table)
                qw.qApp.clipboard().setText(stream.getvalue())        
        super().keyPressEvent(event)

    def clear(self):
        while self.table.rowCount() > 0: 
            self.table.removeRow(self.table.rowCount() - 1)

    def addDetail(self, von : datetime.date, gruppe : Entgeltgruppe, stufe : Stufe, umfang: int, kosten : Decimal):
        self.table.insertRow(self.table.rowCount())
        row = self.table.rowCount() - 1
        self.__setItem(row, 0, "{} {}".format(monthNames[von.month - 1], von.year))
        self.__setItem(row, 1, "{}".format(gruppe.name.replace("_", " ")))
        self.__setItem(row, 2, "{}".format(stufe.value))
        self.__setItem(row, 3, "{}".format(umfang))
        self.__setItem(row, 4, "{}".format(kosten))

    def __setItem(self, row, col, content):
        item = qw.QTableWidgetItem(content)
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, item)


class Abakus(qw.QWidget):

    def __init__(self, ötv):
        super().__init__()
        self.setWindowTitle("Abakus")

        self.ötv = ötv

        layout = qw.QVBoxLayout()

        self.beschäftigung = Einstellung()
        layout.addWidget(self.beschäftigung)
        self.weiterOderNeu = WeiterOderNeu()
        layout.addWidget(self.weiterOderNeu)
        
        berechnung = qw.QPushButton("Berechnung")
        berechnung.clicked.connect(self.berechne)
        layout.addWidget(berechnung)
        self.details = Details()
        layout.addWidget(self.details)
        layout.addStretch(1)
        self.setLayout(layout)
    
    def berechne(self):
        bisDate = qDate2date(self.beschäftigung.bisPicker.date())
        gruppe = self.beschäftigung.gruppe.currentItem()
        stufe = self.weiterOderNeu.stufe.currentItem()
        umfang = self.beschäftigung.umfang.value()
        
        vonDate = qDate2date(self.beschäftigung.vonPicker.date())
        stufenStart = qDate2date(self.weiterOderNeu.seit()) if self.weiterOderNeu.istWeiter() else vonDate
        
        stelle = Stelle(GuS(gruppe, stufe), stufenStart)
        self.details.clear()
        total = Decimal(0)
        for stichtag, aktStelle in laufend.monatsListe(stelle, vonDate, bisDate):
            kosten = self.ötv.summeMonatlich(stichtag.year, stelle.gus)
            self.details.addDetail(stichtag, aktStelle.gus.gruppe, aktStelle.gus.stufe, umfang, kosten)
            total += kosten
        print(total)


def resourcePath(resPath):
    targetPath = pathlib.Path(__file__).parent / "../../resources" / resPath
    targetPath = targetPath.resolve()
    if not targetPath.exists():
        logging.error("Ressource '{}' wurde nicht gefunden (gesucht in '{}')".format(resPath, targetPath))
    return str(targetPath)


if __name__ == "__main__":
    
    fontPath = resourcePath("NotoSansDisplay-Regular.ttf")
    iconPath = resourcePath("icon.svg")
    varsCssPath = resourcePath("stylesheet.vars.css")
    with open(varsCssPath, "r") as styleFile:
        styleSheet = "\n".join(varredCss2Css(styleFile.readlines()))

    ötv = excel.createÖtv()
    
    app = qw.QApplication([])
    QFontDatabase().addApplicationFont(fontPath)
    
    app.setStyleSheet(styleSheet)
    app.setWindowIcon(QIcon(iconPath))

    widget = Abakus(ötv)
    widget.show()

    sys.exit(app.exec_())

