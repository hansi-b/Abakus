import csv
import datetime
import io
import sys

from PySide2 import QtWidgets as qw
from PySide2.QtCore import QDate, QLocale, Qt, QSettings
from PySide2.QtGui import QFontDatabase, QIcon, QKeySequence, QGuiApplication

from gui.cssVars import varredCss2Css
from gui.widgets import EnumCombo, percentSpinner

from abakus.laufend import Summierer, MonatsKosten, Anstellung
from abakus.model import Entgeltgruppe, Stufe, Stelle, GuS, dec
from abakus.csvÖtv import ÖtvCsvParser, ÖtvFormatException
from abakus import resources

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

ABAKUS = "Abakus"


def pp(myStr):
    """
        pad string to avoid clipping in dropdowns
    """
    return " {}  ".format(myStr)


def offsetVonDate(fromDate):
    year, month = fromDate.year, fromDate.month + 2
    if month > 12:
        year, month = year + 1, month - 12
    return datetime.date(year, month, 1)


def offsetSeitDate(fromDate: datetime.date) -> datetime.date:
    year, month = fromDate.year, fromDate.month - 2
    if month < 1:
        year, month = year - 1, month + 12
    return datetime.date(year, month, 1)


def date2QDate(pyDate: datetime.date) -> QDate:
    return QDate(pyDate.year, pyDate.month, pyDate.day)


def qDate2date(qDate: QDate) -> datetime.date:
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


def futurePicker(selected: QDate) -> qw.QDateEdit:
    picker = germanDatePicker(selected)
    picker.setMinimumDate(QDate.currentDate())
    return picker


def pastPicker(selected: QDate) -> qw.QDateEdit:
    picker = germanDatePicker(selected)
    picker.setMaximumDate(QDate.currentDate())
    return picker


class GruppeCombo(EnumCombo):

    def __init__(self):
        super().__init__(Entgeltgruppe, "Entgeltgruppe", lambda i: pp(i.name.replace("_", " ")))


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
        self.seitPicker = pastPicker(date2QDate(offsetSeitDate(datetime.date.today())))
        zeile.addWidget(self.seitPicker)

        umfang = qw.QLabel("Umfang")
        zeile.addWidget(umfang)
        self.umfangSpinner = percentSpinner()
        zeile.addWidget(self.umfangSpinner)

        weiterWidgets = [seitLabel, self.seitPicker, umfang, self.umfangSpinner]

        def clicked(btn):
            istWeiter = btn is self.weiterButton
            for ww in weiterWidgets: ww.setEnabled(istWeiter)

        self.group.buttonClicked.connect(clicked)
        neuButton.click()

        zeile.addStretch(1)
        zeile.setContentsMargins(-1, 0, -1, 0)
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
        self.umfang = percentSpinner()
        zeile.addWidget(self.umfang)

        zeile.addStretch(1)
        zeile.setContentsMargins(-1, 0, -1, 0)
        self.setLayout(zeile)


# don't want to have to rely on the right locale being available
monthNames = "Jan Feb Mär Apr Mai Jun Jul Aug Sep Okt Nov Dez".split()


class Details(qw.QWidget):

    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()

        self.table = qw.QTableWidget()
        self.table.setColumnCount(5)
        vH = self.table.verticalHeader()
        vH.setDefaultSectionSize(vH.fontMetrics().height() + 4)

        self.table.setEditTriggers(qw.QTableWidget.NoEditTriggers)

        for cIdx, label in enumerate("Monat Gruppe Stufe % Kosten(€)".split()):
            self.table.setHorizontalHeaderItem(cIdx, qw.QTableWidgetItem(label))

        self.table.horizontalHeader().setSectionResizeMode(qw.QHeaderView.ResizeMode.Stretch)
        self.table.setSizeAdjustPolicy(qw.QTableWidget.SizeAdjustPolicy.AdjustToContents)

        zeile.addWidget(self.table)
        zeile.setContentsMargins(-1, 0, -1, 0)
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
                rowCount = rows[-1] - rows[0] + 1
                colCount = columns[-1] - columns[0] + 1
                table = [[''] * colCount for _ in range(rowCount)]
                for index in selection:
                    row = index.row() - rows[0]
                    column = index.column() - columns[0]
                    table[row][column] = index.data()
                stream = io.StringIO()
                csv.writer(stream, delimiter='\t').writerows(table)
                QGuiApplication.clipboard().setText(stream.getvalue())
        super().keyPressEvent(event)

    def clear(self):
        while self.table.rowCount() > 0:
            self.table.removeRow(self.table.rowCount() - 1)

    def addDetail(self, mk: MonatsKosten):
        self.table.insertRow(self.table.rowCount())
        row = self.table.rowCount() - 1
        self.__setItem(row, 0, "{} {}".format(monthNames[mk.stichtag.month - 1], mk.stichtag.year),
                       align=Qt.AlignRight)
        gus = mk.stelle.gus
        self.__setItem(row, 1, "{}".format(gus.gruppe.name.replace("_", " ")))
        self.__setItem(row, 2, "{}".format(gus.stufe.value))
        self.__setItem(row, 3, "{}".format(mk.stelle.umfangProzent))
        self.__setItem(row, 4, "{0:n}".format(mk.kosten + mk.sonderzahlung),
                       align=Qt.AlignRight)

    def __setItem(self, row, col, content, align=Qt.AlignCenter):
        item = qw.QTableWidgetItem(content)
        item.setTextAlignment(align)
        self.table.setItem(row, col, item)


class Summe(qw.QWidget):

    def __init__(self):
        super().__init__()
        zeile = qw.QHBoxLayout()

        self.berechnung = qw.QPushButton("Berechnung")
        zeile.addWidget(self.berechnung)

        zeile.addStretch(1)
        label = qw.QLabel("Summe:")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        zeile.addWidget(label)

        self.total = qw.QLineEdit()
        self.total.setReadOnly(True)
        self.total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        zeile.addWidget(self.total)

        zeile.setContentsMargins(-1, 0, -1, 0)
        self.setLayout(zeile)


class Abakus(qw.QWidget):

    def __init__(self, settings, summierer):
        super().__init__()
        self.setWindowTitle(ABAKUS)

        self._settings = settings
        self.summierer = summierer

        layout = qw.QVBoxLayout()

        self.beschäftigung = Einstellung()
        layout.addWidget(self.beschäftigung)
        self.weiterOderNeu = WeiterOderNeu()
        layout.addWidget(self.weiterOderNeu)

        self.summe = Summe()
        layout.addWidget(self.summe)

        self.summe.berechnung.clicked.connect(self.berechne)

        self.details = Details()
        layout.addWidget(self.details)
        layout.addStretch(1)
        self.setLayout(layout)

    def berechne(self):
        bisDate = qDate2date(self.beschäftigung.bisPicker.date())
        gruppe = self.beschäftigung.gruppe.currentItem()
        stufe = self.weiterOderNeu.stufe.currentItem()
        umfang = dec(self.beschäftigung.umfang.value())
        
        vonDate = qDate2date(self.beschäftigung.vonPicker.date())
        stufenStart = qDate2date(self.weiterOderNeu.seit()) if self.weiterOderNeu.istWeiter() else vonDate

        anst = Anstellung(Stelle(GuS(gruppe, stufe), stufenStart, umfang), vonDate, bisDate)
        summe, details = self.summierer.calc(anst)
        self.details.clear()
        for monatsKosten in details:
            self.details.addDetail(monatsKosten)
        self.summe.total.setText("{0:n} €".format(summe))

    
class AbakusSettings():

    def __init__(self):
        self._settings = QSettings("HansB", ABAKUS)

    def _val(self, key, defVal=None):
        return self._settings.value("{}/{}".format(ABAKUS, key), defVal)

    def _setVal(self, key, val):
        self._settings.setValue("{}/{}".format(ABAKUS, key), val)

    def isShownLicense(self):
        # Booleans are not properly stored/read, see
        # e.g., https://bugreports.qt.io/browse/PYSIDE-820
        return self._val("isShownLicense", "false").lower() == "true"

    def setIsShownLicense(self, shown):
        self._setVal("isShownLicense", shown)


def checkLicenseAgreement(appSettings):
    if appSettings.isShownLicense():
        return

    licenseBox = qw.QMessageBox()
    licenseBox.setWindowTitle("{} Lizenz".format(ABAKUS))
    licenseBox.setTextFormat(Qt.TextFormat.RichText)
    licenseBox.setStyleSheet("QLabel{min-width: 20em;}");

    with open(resources.path("README.html"), 'rt', encoding="utf-8") as lFile:
        licenseText = lFile.read()
    licenseBox.setText(licenseText)
    licenseBox.addButton(qw.QMessageBox.No)
    yes = licenseBox.addButton(qw.QMessageBox.Yes)
    licenseBox.exec()
    accepted = licenseBox.clickedButton() == yes
    appSettings.setIsShownLicense(accepted)

    if not accepted:
        sys.exit()


def getÖtv():
    try:
        return resources.load("ötv.csv",
                       ÖtvCsvParser().parse)
    except ÖtvFormatException as ö:
        for e in ö.errors:
            print(e)


if __name__ == "__main__":

    # deal with resources early:
    fontPath = resources.path("NotoSansDisplay-Regular.ttf")
    iconPath = resources.path("icon.svg")
    
    styleSheet = resources.load("stylesheet.vars.css",
                                lambda f:"\n".join(varredCss2Css(f.readlines())))

    settings = AbakusSettings()
    rechner = Summierer(getÖtv())

    QLocale.setDefault(QLocale(QLocale.German, QLocale.Germany))
    app = qw.QApplication([])
    QFontDatabase().addApplicationFont(fontPath)

    app.setStyleSheet(styleSheet)
    app.setWindowIcon(QIcon(iconPath))
    checkLicenseAgreement(settings)

    widget = Abakus(settings, rechner)
    widget.show()

    sys.exit(app.exec_())
