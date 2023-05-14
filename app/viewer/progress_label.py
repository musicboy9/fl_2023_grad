from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QBrush, QColor

from app.common_fixture import *


class ProgressLabel(QtWidgets.QWidget):

    def __init__(self, status_dict, option):
        super().__init__()

        self.status_dict = status_dict

        self.__init_option(option)
        self.__init_geometry()
        self.__init_progress_box()

    def __init_option(self, option):
        self.round_num = option[ROUND_NUM]
        self.client_options = option[CLIENT_OPTIONS]
        self.client_num = self.status_dict[CLIENT_NUM]

    def __init_geometry(self):
        self.margin = MARGIN

        self.col_height = 100
        self.round_width = 600

        self.window_height = self.client_num * self.col_height + (self.client_num + 1) * self.margin
        self.window_width = self.round_width * self.round_num + (self.round_num + 1) * self.margin
        self.setGeometry(0,0,self.window_width, self.window_height)
        self.max_width = self.geometry().width() - 2 * self.margin

    def __init_progress_box(self):
        self.box_info_dict = {}

        def get_train_eval_width(width):
            return int(width * 2 / 3), width - int(width * 2 / 3)

        def get_x_pos(round, type):
            if type == TRAIN:
                return self.margin + (self.round_width + self.margin) * round
            else:
                return self.margin + (self.round_width + self.margin) * round +\
                       get_train_eval_width(self.round_width * self.client_options[client_i][DATA_SIZE])[0]

        def get_y_pos(client_i):
            return self.margin * (client_i+1) + self.col_height * client_i

        def get_width_pos(type):
            return get_train_eval_width(self.round_width * self.client_options[client_i][DATA_SIZE])[type]

        def get_height_pos():
            return self.col_height

        for client_i in range(self.client_num):
            for round in range(self.round_num):
                for type in TYPE_LIST:
                    self.box_info_dict[(client_i, round, type)] = (get_x_pos(round, type),
                                                                   get_y_pos(client_i),
                                                                   get_width_pos(type),
                                                                   get_height_pos())

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
                for type in TYPE_LIST:
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

    def get_width(self):
        return self.window_width

    def get_height(self):
        return self.window_height
