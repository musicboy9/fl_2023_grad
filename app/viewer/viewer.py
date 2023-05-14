from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from app.viewer.progress_label import ProgressLabel
from app.viewer.log_label import LogLabel
from app.common_fixture import *


class Viewer(QWidget):

    def __init__(self, status_dict, option, screen_size):
        super().__init__()

        self.setWindowTitle("FL Viewer")
        self.status_dict = status_dict
        self.option = option

        self.setMaximumSize(screen_size)
        self.screen_size = screen_size

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)

        self.__init_progress_label()
        self.__init_log_label()
        self.__init_fetcher()

        self.setLayout(self.layout)

    def __init_progress_label(self):
        self.progress_label = ProgressLabel(self.status_dict, self.option)

        self.window_width = self.progress_label.get_width() + MARGIN * 2
        self.window_height = self.progress_label.get_height() + 340 + MARGIN * 2
        self.setGeometry(0, 0, self.window_width, self.window_height)

        s = QScrollArea()
        s.setWidget(self.progress_label)
        self.layout.addWidget(s)

    def __init_log_label(self):
        self.log_label = LogLabel()
        self.log_label.setFixedHeight(300)
        self.log_label.setMaximumWidth(self.window_width)
        self.layout.addWidget(self.log_label)

    def __init_fetcher(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1)  # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.fetch)  # each time timer counts a second, call self.blink
        self.color_flag = True

        self.timer.start()

    @pyqtSlot()
    def fetch(self):
        self.progress_label.update()

        self.log_label.set_text(self.status_dict[LOG])
