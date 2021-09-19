# -*- coding: utf-8 -*-

import os
import sys
import time
from os import path as os_path
from queue import Queue

from PyQt5.QtGui import QPixmap

from core.threads.face_detect import FaceDetectBase
from core.hardware import ManageHardware
from core.task_model.electric_welding_work import ElectricWeldingWork
from core.task_model.gas_welding_work import GasWeldingWork
from core.task_model.height_work import HeightWork
from core.task_model.roller_work import RollerWork
from core.threads.ocr import OcrBase
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QSplashScreen

from lib.AppQt.ui_welcomewindow import Ui_Form

env_path = os_path.join(os_path.dirname(__file__), '../..')
if env_path not in sys.path:
    sys.path.append(env_path)

from core.tools import yaml_file_path, get_yaml_data, get_log_level, open_unqualified_folders, get_file_folder_size
from core.threads.detect import DetectBase

from loguru import logger

logger.add('runtime.log', format="{time}{level}{message}", filter="my_module", level=get_log_level())


class QWelcomeWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ------------------------------设置全屏----------------------------------
        self.desktop = QApplication.desktop()
        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        self.screen_height = self.screenRect.height()
        self.screen_width = self.screenRect.width()
        ui_file_path = os.path.join(os.path.dirname(__file__), '../lib/AppQt/conversion1.ui')
        loadUi(ui_file_path, self)
        self.ui = self
        self.add_top_img()
        self.add_middle_img()
        # self.ui = Ui_Form()
        # self.resize(1080, 1920)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.delete_warning()
        # self.ui.resize(self.screen_width, self.screen_height)    # 设置软件启动为全屏
        #  得到配置文件
        self.conf = get_yaml_data(yaml_file_path)
        self.roller_work = None
        self.height_work = None
        self.electric_welding = None
        self.gas_welding = None
        # ----------------------------四个检测任务按钮的槽函数------------------------------------
        self.ui.detect_task_one_btn.clicked.connect(self.do_roller_work_window)
        self.ui.detect_task_two_btn.clicked.connect(self.do_height_work_window)
        self.ui.detect_task_three_btn.clicked.connect(self.do_electric_welding_window)
        self.ui.detect_task_four_btn.clicked.connect(self.do_gas_welding_window)

        # ---------------------------- 功能按键 --------------------------------
        self.ui.copy_button.clicked.connect(self.do_copy_btn)
        self.ui.delete_button.clicked.connect(self.do_delet_btn)
        self.ui.close_button.clicked.connect(self.do_close_btn)

        self.current_btn = -1  # 记录当前按钮，初始化为-1，即没有一个按钮按下
        # ##################################################################
        # 加载网络
        self.net_conf_dic = self.conf.get("net")
        self.net_dic = {}
        self.load_all_net()

        # 创建全局队列
        self.img_queue, self.darknet_queue, self.target_queue = (None, None, None)
        self.create_queue(15)

        # 初始化  摄像机和声音
        self.hardware = ManageHardware(self.ui, self.img_queue, self.darknet_queue)

    def add_top_img(self):
        img_path = os.path.join(os.path.dirname(__file__), "../db/img/1_jpg.jpg")
        logger.info(img_path)
        top_img = QPixmap(img_path)
        top_img = top_img.scaled(QSize(700, 400),
                                 Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logger.info("图片1大小{} {}".format(top_img.width(), top_img.height()))
        self.ui.top_img_label.setPixmap(top_img)
        self.ui.top_img_label.setScaledContents(True)

    def add_middle_img(self):
        img_path = os.path.join(os.path.dirname(__file__), "../db/img/2_jpg.jpg")
        logger.info(img_path)
        top_img = QPixmap(img_path)
        # top_img = top_img.scaled(QSize(800, 223),
        #                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logger.info("图片2大小{} {}".format(top_img.width(), top_img.height()))
        self.ui.middle_img_label.setPixmap(top_img)
        self.ui.middle_img_label.setScaledContents(True)

    # 判断图片是否太多
    def delete_warning(self):
        file_path = os.path.join(env_path, "pyqt5_darknet/db/unqualified/")
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        filter_size = get_file_folder_size(file_path)
        if filter_size > 500 * 1000 * 1000:
            dlg_title = u"警告"
            str_info = u"保存的不合格图片过多，点击确定前去清理，清理后再次运行！"
            result = QMessageBox.question(self, dlg_title, str_info,
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if result == QMessageBox.Yes:
                open_unqualified_folders(file_path)
            exit(0)
        else:
            logger.debug("目前文件夹大小：{}M".format(filter_size // 1024 // 1024))

    # 加载网络函数
    def load_all_net(self):
        for k in self.net_conf_dic:
            logger.info("加载网络：{}".format(k))
            self.net_dic[k] = DetectBase(k)
            time.sleep(0.5)
        logger.info("加载面部识别网络")
        self.net_dic["face"] = FaceDetectBase()
        logger.info("加载OCR识别网络")
        self.net_dic["ocr"] = OcrBase()

    def create_queue(self, num):
        self.img_queue, self.darknet_queue, self.target_queue = Queue(num), Queue(num), Queue(num)

    def clear_queue(self):
        for i in (self.img_queue, self.darknet_queue, self.target_queue):
            i.queue.clear()

    # ============ 槽函数 ==============================
    def do_roller_work_window(self):
        logger.info("按鈕1按下".format(self.current_btn))
        if self.current_btn != 0:  # 如果该按钮已经按下过，再次按下则无效
            self.current_btn = 0
            # 开始第一项任务
            self.roller_work = RollerWork(self.ui)
            time.sleep(0.1)

            logger.info("任務一界面开启 ")

    def do_height_work_window(self):
        # 同上
        if self.current_btn != 1:
            self.current_btn = 1
            logger.info("按鈕2按下")
            # 开启检测界面
            self.height_work = HeightWork(self.ui)
            time.sleep(0.1)

            logger.info("任務二界面开启")

    def do_electric_welding_window(self):
        if self.current_btn != 2:
            self.current_btn = 2
            logger.info("按鈕3按下")
            # 开启检测界面
            self.electric_welding = ElectricWeldingWork(self.ui)
            time.sleep(0.1)

            logger.info("任務三界面开启")

    def do_gas_welding_window(self):
        logger.info("按鈕4按下".format(self.current_btn))
        if self.current_btn != 3:
            self.current_btn = 3
            # 开启检测界面
            self.gas_welding = GasWeldingWork(self.ui)
            time.sleep(0.1)

            logger.info("任務四界面开启")

    # ***************************拷贝图片按钮*****************************
    def do_copy_btn(self):
        file_path = os.path.join(env_path, "pyqt5_darknet/db/unqualified/")
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        open_unqualified_folders(file_path)

    # ***************************删除图片按钮****************************
    def do_delet_btn(self):
        file_path = os.path.join(env_path, "pyqt5_darknet/db/unqualified/")
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        open_unqualified_folders(file_path)

    # *************************** 关闭按钮 ******************************
    def do_close_btn(self):
        self.close()

    def close_task(self):
        if self.roller_work:
            self.roller_work.close_show_window(True)
        if self.height_work:
            self.height_work.close_show_window(True)
        if self.electric_welding:
            self.electric_welding.close_show_window(True)
        if self.gas_welding:
            self.gas_welding.close_show_window(True)

    # ============ 事件处理 =============================
    # 窗口关闭
    def closeEvent(self, event):
        self.hardware.close_thread()
        self.close_task()
        super().closeEvent(event)
        sys.exit(0)


#  ============窗体测试程序 ================================
if __name__ == "__main__":  # 用于当前窗体测试
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)  # 创建GUI应用程序
    splash_path = os.path.join(os.path.dirname(__file__), '../db/img/4.png')
    print(splash_path)
    splash = QSplashScreen(QPixmap(splash_path))
    splash.show()  # 展示启动图片
    QApplication.processEvents()  # 防止进程卡死
    form = QWelcomeWindow()  # 创建窗体
    form.show()
    splash.finish(form)
    sys.exit(app.exec_())
