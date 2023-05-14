from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui


class LogLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.__init_label()

        self.setWidgetResizable(True)
        self.setWidget(self.label)

    def __init_label(self):
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setFont(QtGui.QFont("Arial", 20))
        self.label.setAlignment(QtCore.Qt.AlignTop)

    def set_text(self, text):
        self.label.clear()
        self.label.setText(text)

