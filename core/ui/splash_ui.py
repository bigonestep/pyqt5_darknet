# -*-coding:utf-8-*-
# cython: language_level=3
import os
import sys
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QSplashScreen, QApplication

env_path = os.path.join(os.path.dirname(__file__), '..')


class SplashPanel(QSplashScreen):
    def __init__(self):
        super(SplashPanel, self).__init__()
        message_font = QFont()
        message_font.setBold(True)
        message_font.setPointSize(14)
        self.setFont(message_font)
        pixmap = QPixmap(os.path.join(env_path, "./db/img/4.jpg"))
        # pixmap = QPixmap("D:\\github\\bdmaster\\app\\resource\\images\\timg.png")
        self.setPixmap(pixmap)
        # self.showMessage('正在加载文件资源', alignment=Qt.AlignBottom, color=Qt.black)
        self.show()
        for i in range(1, 5):
            self.showMessage('正在加载文件资源{}'.format('.' * i), alignment=Qt.AlignBottom, color=Qt.black)
            time.sleep(0.15)

    def mousePressEvent(self, evt):
        pass
        # 重写鼠标点击事件，阻止点击后消失

    def mouseDoubleClickEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，阻止出现卡顿现象

    def enterEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，阻止出现卡顿现象

    def mouseMoveEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，阻止出现卡顿现象



if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)  # 创建GUI应用程序

    splash = SplashPanel()
    #QApplication.processEvents()  # 防止进程卡死


    sys.exit(app.exec_())
