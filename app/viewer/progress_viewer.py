from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QBrush, QColor
from collections import defaultdict
import time

class MyWidget(QtWidgets.QWidget):
    def __init__(self, status_dict):
        super().__init__()

        self.status_dict = status_dict

        self.__init_fetcher()
        self.__init_geometry()

        self.show()
        self.showing = True

        self.last_val_dict = defaultdict(int)

        self.time = time.time()
        self.time_set = False


    def __init_geometry(self):
        self.margin = 10

        self.setGeometry(30, 30, 600, 400)
        self.col_height = 50
        self.max_width = self.geometry().width() - 2 * self.margin

        self.pos_list = [[self.margin, self.margin],
                         [self.margin, self.col_height + self.margin]]


    def __init_fetcher(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1)  # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.fetch)  # each time timer counts a second, call self.blink
        self.color_flag = True

        self.timer.start()

    def paintEvent(self, event):


        for i in range(len(self.pos_list)):
            pos = self.pos_list[i]
            if ((i, "data_size") in self.status_dict):
                if (i, "status") in self.status_dict and (i, "train_result") in self.status_dict:
                    if self.status_dict[(i, "status")] == "training":
                        if not self.time_set:
                            self.time = time.time()
                            self.time_set = True

                        qp = QPainter()
                        qp.begin(self)
                        # qp.drawRect(pos[ 0 ], pos[ 1 ], self.max_width * self.status_dict[ (i, "data_size") ],
                        #             self.col_height)
                        current_width = self.max_width * (time.time() - self.time) / 30
                        qp.drawRect(pos[ 0 ], pos[ 1 ], current_width, self.col_height)

                        brush = QBrush()
                        brush.setColor(QColor("#FFD141"))
                        brush.setStyle(QtCore.Qt.BrushStyle.Dense1Pattern)
                        qp.setBrush(brush)
                        rect = QtCore.QRect(pos[0],
                                            pos[1],
                                            # int(
                                            #     self.max_width *
                                            #     self.status_dict[(i, "data_size")] *
                                            #     (self.status_dict[(i, "train_result")][1] / self.status_dict[(i, "train_result")][2])
                                            # ),
                                            int(
                                                current_width *
                                                (self.status_dict[(i, "train_result")][1] / self.status_dict[(i, "train_result")][2])
                                            ),
                                            self.col_height)
                        qp.drawRect(rect)
                        qp.setPen(QtCore.Qt.black)
                        qp.drawText(rect, QtCore.Qt.AlignCenter, str(self.status_dict[(i, "train_result")][1]) + "/" + str(self.status_dict[(i, "train_result")][2]))
                        qp.end()


    @QtCore.pyqtSlot()
    def fetch(self):
        self.update()

    def getShowing(self):
        return self.showing