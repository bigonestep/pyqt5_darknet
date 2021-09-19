# -*- coding: utf-8 -*-
import os
import sys
from os import path as os_path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen

from core.welcome_window import QWelcomeWindow

"""
人员穿戴：     安全帽、安全带
灭火器检测     有无
氧气瓶卧倒检测  是否
氧气瓶距离检测  是否大于五米
焊工穿戴检测    面罩、手套
焊工鞋         有无
安全员检测      有无
"""

env_path = os_path.join(os_path.dirname(__file__), '..')
if env_path not in sys.path:
    sys.path.append(env_path)

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)  # 创建GUI应用程序
    form = QWelcomeWindow()  # 创建窗体
    form.show()
    sys.exit(app.exec_())
