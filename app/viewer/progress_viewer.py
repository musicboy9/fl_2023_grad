from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QBrush, QColor
from collections import defaultdict
import time

from app.common_fixture import *

MARGIN = 10


class ProgressViewer(QtWidgets.QWidget):

    def __init__(self, status_dict, option):
        super().__init__()

        self.status_dict = status_dict

        self.__init_option(option)
        self.__init_geometry()
        self.__init_progress_box()
        self.__init_fetcher()

        self.show()

    def __init_option(self, option):
        self.round_num = option[ROUND_NUM]
        self.client_options = option[CLIENT_OPTIONS]
        self.client_num = len(self.client_options)

    def __init_geometry(self):
        self.margin = MARGIN

        self.col_height = 50
        self.round_width = 600
        self.server_width = 100

        window_height = (self.client_num + 1) * self.col_height + (self.client_num + 2) * self.margin
        window_width = (self.round_width + self.server_width) * self.round_num + self.margin * 2
        self.setGeometry(30, 30, window_width, window_height)
        self.max_width = self.geometry().width() - 2 * self.margin

    def __init_progress_box(self):
        self.box_info_dict = {}

        def get_train_eval_width(width):
            return int(width * 2 / 3), width - int(width * 2 / 3)

        def get_x_pos(round, type):
            if type == TRAIN:
                return self.margin + (self.round_width + self.server_width) * round
            else:
                return self.margin + (self.round_width + self.server_width) * round +\
                       get_train_eval_width(self.round_width * self.client_options[client_i][DATA_SIZE])[0]

        def get_y_pos(client_i):
            return self.margin * (client_i+1) + self.col_height * client_i

        def get_width_pos(type):
            return get_train_eval_width(self.round_width * self.client_options[client_i][DATA_SIZE])[type]

        def get_height_pos():
            return self.col_height

        for client_i in range(self.client_num):
            for round in range(self.round_num):
                for type in type_list:
                    self.box_info_dict[(client_i, round, type)] = (get_x_pos(round, type),
                                                                   get_y_pos(client_i),
                                                                   get_width_pos(type),
                                                                   get_height_pos())
        self.server_id = -1
        for round in range(self.round_num):
            self.box_info_dict[(self.server_id, round)] = (self.margin + self.round_width + (self.round_width + self.server_width) * round,
                                                           (self.margin + self.col_height) * self.client_num + self.margin,
                                                           self.server_width,
                                                           self.col_height)

    def __init_fetcher(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1)  # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.fetch)  # each time timer counts a second, call self.blink
        self.color_flag = True

        self.timer.start()

    def __draw_box(self, box_info, progress=False, result=(1, 1)):
        qp = QPainter()
        qp.begin(self)
        rect = QtCore.QRect(*box_info)
        if progress:
            brush = QBrush()
            brush.setColor(QColor("#FFD141"))
            brush.setStyle(QtCore.Qt.BrushStyle.Dense1Pattern)
            qp.setBrush(brush)
        qp.drawRect(rect)
        if progress:
            qp.setPen(QtCore.Qt.black)
            qp.drawText(rect, QtCore.Qt.AlignCenter, str(result[0]) + "/" + str(result[1]))
        qp.end()
        self.update()

    def paintEvent(self, event):
        for key in self.box_info_dict.keys():
            self.__draw_box(self.box_info_dict[key])

        for client_i in range(self.client_num):
            for round in range(self.round_num):
                for type in type_list:
                    key = (client_i, round, type)
                    if key not in self.status_dict:
                        continue
                    default_box_info = list(self.box_info_dict[key])
                    default_width = default_box_info[2]
                    progress = self.status_dict[key][1]
                    data_len = self.status_dict[key][2]
                    progress_width = default_width * progress / data_len
                    default_box_info[2] = progress_width
                    progress_box_info = tuple(default_box_info)
                    self.__draw_box(progress_box_info, True, (progress, data_len))

    @QtCore.pyqtSlot()
    def fetch(self):
        self.update()
