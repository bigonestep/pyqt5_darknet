import os
import sys

from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.uic import loadUi
from loguru import logger

from core.tools import get_log_level, get_log_path
from lib.AppQt.ui_conversion import Ui_Form

env_path = os.path.join(os.path.dirname(__file__), '../..')
if env_path not in sys.path:
    sys.path.append(env_path)

logger.add(get_log_path(), format="{time}{level}{message}", filter="my_module", level=get_log_level())


class ConversionUi(QWidget):

    def __init__(self, main_ui=None, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.parent = parent  # 获取上一个界面的对象
        self.main_ui = main_ui
        ui_file_path = os.path.join(os.path.dirname(__file__), '../../lib/AppQt/conversion.ui')
        loadUi(ui_file_path, self)
        self.ui = self
        # self.ui = Ui_Form()
        # ------------------------------设置全屏----------------------------------
        self.desktop = QApplication.desktop()
        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        self.screen_height = self.screenRect.height()
        self.screen_width = self.screenRect.width()
        # self.ui.resize(self.screen_width, self.screen_height)      //全屏
        self.resize(1080, 1920)
        self.add_top_img()
        self.add_middle_img()
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.add_middle_label_img()

        self.ui.close_btn.clicked.connect(self.do_close_btn)

    def add_top_img(self):
        img_path = os.path.join(os.path.dirname(__file__), "../../db/img/1_jpg.jpg")
        logger.info(img_path)
        top_img = QPixmap(img_path)
        top_img = top_img.scaled(QSize(700, 400),
                                 Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logger.info("图片1大小{} {}".format(top_img.width(), top_img.height()))
        self.ui.top_img_label.setPixmap(top_img)
        self.ui.top_img_label.setScaledContents(True)

    def add_middle_label_img(self):
        img_path = os.path.join(os.path.dirname(__file__), "../../db/img/2_jpg.jpg")
        logger.info(img_path)
        top_img = QPixmap(img_path)
        # top_img = top_img.scaled(QSize(800, 223),
        #                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logger.info("图片3大小{} {}".format(top_img.width(), top_img.height()))
        self.ui.middle_label.setPixmap(top_img)
        self.ui.middle_label.setScaledContents(True)

        # palette = QPalette()
        # img_path = os.path.join(os.path.dirname(__file__), "../../db/img/1_jpg.jpg")
        # middle_label_img = QPixmap(img_path)
        # # middle_label_img = middle_label_img.scaled(QSize(800, 223),
        # #                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #
        # palette.setBrush(QPalette.Background, QBrush(middle_label_img))
        # self.widget_2.setPalette(palette)

    def add_middle_img(self):
        img_path = os.path.join(os.path.dirname(__file__), "../../db/img/2_jpg.jpg")
        logger.info(img_path)
        top_img = QPixmap(img_path)
        # top_img = top_img.scaled(QSize(800, 223),
        #                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logger.info("图片2大小{} {}".format(top_img.width(), top_img.height()))
        self.ui.middle_img_label.setPixmap(top_img)
        self.ui.middle_img_label.setScaledContents(True)

    def do_close_btn(self):
        self.main_ui.current_btn = -1
        self.main_ui.hardware.pause_thread()
        self.close()

    def change_show_text(self, text):
        self.middle_label.setText(text)

    def closeEvent(self, event):
        logger.debug("ConversionUi关闭窗口")
        # self.do_close_btn()
        super().closeEvent(event)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)  # 创建GUI应用程序
    form = ConversionUi()  # 创建窗体
    form.show()
    sys.exit(app.exec_())
