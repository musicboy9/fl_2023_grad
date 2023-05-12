from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter

class MyWidget(QtWidgets.QWidget):
    def __init__(self, status_dict):
        super().__init__()

        self.status_dict = status_dict

        self.setGeometry(30,30,600,400)
        self.pos1 = [0,0]
        self.pos2 = [0,0]
        self.show()
        self.showing = True

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)  # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.fetch)  # each time timer counts a second, call self.blink
        self.color_flag = True

        self.timer.start()

    def paintEvent(self, event):
        width = self.pos2[0]-self.pos1[0]
        height = self.pos2[1] - self.pos1[1]

        qp = QPainter()
        qp.begin(self)
        qp.drawRect(self.pos1[0], self.pos1[1], width, height)
        qp.end()

    def mousePressEvent(self, event):
        self.pos1[0], self.pos1[1] = event.pos().x(), event.pos().y()
        print("clicked")

    def mouseReleaseEvent(self, event):
        self.pos2[0], self.pos2[1] = event.pos().x(), event.pos().y()
        print("released")
        self.update()

    @QtCore.pyqtSlot()
    def fetch(self):
        try:
            for key in self.status_dict.keys():
                if len(str(self.status_dict[key])) > 10:
                    print(str(self.status_dict[key])[:10])
                else:
                    print(self.status_dict[key])
        except:
            pass

        self.update()

    def getShowing(self):
        return self.showing