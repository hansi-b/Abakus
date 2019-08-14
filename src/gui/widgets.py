from PySide2 import  QtWidgets as qw

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"


class EnumCombo(qw.QWidget):

    def __init__(self, enumClass, pickerLabel, itemLabelFnc):
        super().__init__()

        zeile = qw.QHBoxLayout()
        zeile.addWidget(qw.QLabel(pickerLabel))

        self.comboBox = qw.QComboBox()
        for i in enumClass:
            self.comboBox.addItem(itemLabelFnc(i))
        zeile.addWidget(self.comboBox)

        zeile.addStretch(1)
        zeile.setContentsMargins(0, 0, 0, 0)
        self.setLayout(zeile)


if __name__ == '__main__':
    pass
