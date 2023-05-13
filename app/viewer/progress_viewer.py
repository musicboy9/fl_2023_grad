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
        self.showing = True

        self.last_val_dict = defaultdict(int)

        self.time = time.time()
        self.time_set = False

    def __init_option(self, option):
        self.round_num = option[ROUND_NUM]
        self.client_options = option[CLIENT_OPTIONS]
        self.client_num = len(self.client_options)

    def __init_geometry(self):
        self.margin = MARGIN

        self.col_height = 50
        self.round_width = 400
        self.server_width = 100

        window_height = (self.client_num + 1) * self.col_height + (self.client_num + 2) * self.margin
        window_width = (self.round_width + self.server_width) * self.round_num + self.margin * 2
        self.setGeometry(30, 30, window_width, window_height)
        self.max_width = self.geometry().width() - 2 * self.margin

    def __init_progress_box(self):
        self.box_info_dict = {}
        TRAIN = 0
        EVAL = 1
        type_list = [TRAIN, EVAL]

        def get_train_eval_width(width):
            return int(width * 5 / 6), width - int(width * 5 / 6)

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

    def __draw_box(self, box_info):
        qp = QPainter()
        qp.begin(self)
        qp.drawRect(*box_info)
        qp.end()
        self.update()

    def paintEvent(self, event):
        for key in self.box_info_dict.keys():
            self.__draw_box(self.box_info_dict[key])
        # for i in range(len(self.pos_list)):
        #     pos = self.pos_list[i]
        #     if (i, "data_size") in self.status_dict:
        #         if (i, "status") in self.status_dict and (i, "train_result") in self.status_dict:
        #             if self.status_dict[(i, "status")] == "training":
        #                 if not self.time_set:
        #                     self.time = time.time()
        #                     self.time_set = True
        #
        #                 qp = QPainter()
        #                 qp.begin(self)
        #                 qp.drawRect(pos[ 0 ], pos[ 1 ], self.max_width * self.status_dict[ (i, "data_size") ],
        #                             self.col_height)
        #
        #                 brush = QBrush()
        #                 brush.setColor(QColor("#FFD141"))
        #                 brush.setStyle(QtCore.Qt.BrushStyle.Dense1Pattern)
        #                 qp.setBrush(brush)
        #                 rect = QtCore.QRect(pos[0],
        #                                     pos[1],
        #                                     int(
        #                                         self.max_width *
        #                                         self.status_dict[(i, "data_size")] *
        #                                         (self.status_dict[(i, "train_result")][1] / self.status_dict[(i, "train_result")][2])
        #                                     ),
        #                                     self.col_height)
        #                 qp.drawRect(rect)
        #                 qp.setPen(QtCore.Qt.black)
        #                 qp.drawText(rect, QtCore.Qt.AlignCenter, str(self.status_dict[(i, "train_result")][1]) + "/" + str(self.status_dict[(i, "train_result")][2]))
        #                 qp.end()


    @QtCore.pyqtSlot()
    def fetch(self):
        self.update()

    def getShowing(self):
        return self.showing