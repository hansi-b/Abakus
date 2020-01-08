from PySide2 import QtWidgets as qw
from PySide2.QtCore import QDate

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"


def percentSpinner():
    pcnt = qw.QSpinBox()
    pcnt.setRange(10, 100)
    pcnt.setSingleStep(10)
    pcnt.setValue(100)
    pcnt.setSuffix("% ")
    return pcnt


class EnumCombo(qw.QWidget):

    def __init__(self, enumClass, pickerLabel, itemLabelFnc):
        super().__init__()

        zeile = qw.QHBoxLayout()
        zeile.addWidget(qw.QLabel(pickerLabel))

        self.itemByIndex = {}

        self.comboBox = qw.QComboBox()
        for idx, item in enumerate(enumClass):
            self.comboBox.addItem(itemLabelFnc(item))
            self.itemByIndex[idx] = item
        zeile.addWidget(self.comboBox)

        zeile.addStretch(1)
        zeile.setContentsMargins(0, 0, 0, 0)
        self.setLayout(zeile)

    def currentItem(self):
        idx = self.comboBox.currentIndex()
        return self.itemByIndex[idx]


def ensureBeforeAfter(before:qw.QDateEdit, after:qw.QDateEdit):
    """
        Wire the two date edit fields such that the "after" field always has
        a minimum of the "before" field.
        
        If the "before" field is set to a value after the current "after" date,
        the "after" date is also changed to that date.
    """
    
    def adaptAfter(beforeDate: QDate):
        if after.date() < beforeDate:
            after.setDate(beforeDate)
        after.setMinimumDate(beforeDate)

    before.dateChanged.connect(lambda : adaptAfter(before.date()))


if __name__ == '__main__':
    pass
