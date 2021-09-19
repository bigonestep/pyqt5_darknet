import sys
import os
from os import path as os_path
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from loguru import logger

from PyQt5.QtCore import QThread, Qt, pyqtSignal

from core.threads.show_img import ShowImageThread
from core.tools import get_log_level
from lib.AppQt.ui_detectwindow import Ui_MainWindow

env_path = os_path.join(os_path.dirname(__file__), '../../..')
if env_path not in sys.path:
    sys.path.append(env_path)

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class QDetectWindowDetectThing(QMainWindow):
    # TODO：这里只负责检测展示界面，只控制一个展示线程
    close_window_signal = pyqtSignal(bool)

    def __init__(self, main_ui, parent=None):
        super().__init__(parent)
        self.main_ui = main_ui

        self.parent = parent  # 获取上一个界面的对象
        ui_file_path = os.path.join(os.path.dirname(__file__), '../../lib/AppQt/detectwindow.ui')
        loadUi(ui_file_path, self)
        self.ui = self
        # self.ui = Ui_MainWindow()

        self.img_queue = self.main_ui.img_queue
        self.target_queue = self.main_ui.target_queue

        # ------------------------------设置全屏----------------------------------
        self.desktop = QApplication.desktop()
        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        self.screen_height = self.screenRect.height()
        self.screen_width = self.screenRect.width()
        # self.ui.resize(self.screen_width, self.screen_height)      //全屏
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.resize(1080, 1920)
        # ##################################################################
        self.ui.close_btn.clicked.connect(self.do_close_btn)
        self.show_image_thread()

    def show_image_thread(self):
        self.show_thread = ShowImageThread(self.ui, self.img_queue, self.target_queue)
        self.show_thread.daemon = True
        self.show_thread.start()

        q = QLabel()

    # ============ 事件处理 =============================
    # 窗口关闭
    def closeEvent(self, event):
        # 这里还是要关闭所有的线程
        # 发送界面关闭的信号
        self.close_window_signal.emit(True)
        self.main_ui.current_btn = -1
        self.main_ui.hardware.pause_thread()
        self.show_thread.close()
        # stop_thread(self.show_thread)

        # self.main_ui.clear_queue()
        super().closeEvent(event)
        logger.info("关闭窗口展示窗口")

    # 关闭按钮
    def do_close_btn(self):
        self.close()
