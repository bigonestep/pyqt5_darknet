import os
import time

from PyQt5.QtCore import QTimer, QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication
from loguru import logger

from core.threads.detect import DetectThread
from core.threads.face_detect import FaceDetectThread
from core.threads.ocr import DetectDateThread
from core.tools import get_log_level, set_back_color
from core.ui.conversion_ui import ConversionUi
from core.ui.detect_window import QDetectWindowDetectThing
from core.ui.standby_ui import StandbyUi

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())

"fire_extinguisher"
"oxygen_cylinder"
"security_officer"
"welder_model"

"roller_work    滚筒作业"
"height_work 高空作业"
"electric_welding_work 电焊作业"
"gas_welding_work  气焊作业"


class TaskBase(QObject):
    def __init__(self, main_ui):
        super().__init__()
        self.main_ui = main_ui
        self.data = self.main_ui.conf
        self.TARGET_THING = "person"
        # 灭火器
        self.FIRE_EXTINGUISHER_TARGET = self.data.get("net").get("fire_extinguisher").get("target_name")

        # TODO: 氧气瓶没有权重
        self.OXYGEN_CYLINDER_TARGET = self.data.get("net").get("oxygen_cylinder").get("target_name")

        # 锁、标志牌
        self.SIGNAGE_LOCKS_TARGET = self.data.get("net").get("sign_file").get("target_name")

        # 面罩手套
        self.MASK_GLOVES_TARGET = self.data.get("net").get("mask_shoes").get("target_name")

        # TODO: 焊工鞋没有
        self.SHOES_TARGET = self.data.get("net").get("shoes").get("target_name")

        # 安全帽 鞋子
        self.SAFE_HAT_SHOES_TARGET = self.data.get("net").get("roller").get("target_name")

        # 安全帽 安全带Seat belts
        self.SATE_HAT_TAPE_TARGET = self.data.get("net").get("height").get("target_name")

        # 安全员
        self.SAFETY_OFFICER_TARGET = self.data.get("net").get("person").get("target_name")

        self.face = self.data.get("face")
        self.main_ui = main_ui
        self.timer = QTimer()
        self.safer_wait_time = int(self.data.get("safer_detect_wait_time"))  #
        self.conversion_time = int(self.data.get("conversion_time"))
        self.safe_timer = QTimer()
        self.safe_timer.timeout.connect(self.speak_start)
        self._count = 0
        # self.standby_ui = StandbyUi(self.main_ui, self.safer_wait_time)
        self.conversion_ui = ConversionUi(self.main_ui)

        self.detect_win = None
        self.detect_thread = None
        self.face_detect_thread = None
        self.ocr_detect_thread = None
        self.save_img_path = os.path.join(os.path.dirname(__file__), '../../db/unqualified/')
        self.cur_data = time.strftime("%Y-%m-%d", time.localtime())

    def close_show_window(self, sig):
        logger.info("进入检测任务关闭")
        if sig:
            if self.detect_thread:
                logger.debug("检测物体关闭")
                self.detect_thread.close()
            if self.ocr_detect_thread:
                self.ocr_detect_thread.close()
                logger.debug("OCR关闭")
            if self.face_detect_thread:
                self.face_detect_thread.close()
            if self.face_detect_thread:
                logger.debug("人脸检测关闭")
                self.face_detect_thread.close()
            if self.safe_timer:
                self.safe_timer.stop()

    def detect_things(self, net_name, finish_func):
        self.main_ui.clear_queue()
        self.detect_win = QDetectWindowDetectThing(self.main_ui)
        self.detect_win.close_window_signal.connect(self.close_show_window)
        self.main_ui.hardware.resume_thread()
        logger.info("camera_thread, sound_task_thread:{}, {}".format(self.main_ui.hardware.camera_thread.is_pause(),
                                                                     self.main_ui.hardware.sound_task_thread.is_pause()))
        if self.conversion_ui.isVisible():
            try:
                self.conversion_ui.close()
            except:
                pass
        self.detect_win.show()

        # self.main_ui.hardware.resume_thread()
        if net_name == "face":
            self.face_detect_thread = FaceDetectThread(self.main_ui.net_dic["face"],
                                                       self.main_ui.img_queue,
                                                       self.main_ui.target_queue)
            self.face_detect_thread.detect_face_result_signal.connect(finish_func)
            self.face_detect_thread.daemon = True
            self.face_detect_thread.start()
        elif net_name == "ocr":
            self.ocr_detect_thread = DetectDateThread(self.main_ui, self.main_ui.net_dic["ocr"],
                                                      self.main_ui.img_queue,
                                                      self.main_ui.darknet_queue,
                                                      self.main_ui.target_queue)
            self.ocr_detect_thread.date_signal.connect(finish_func)
            self.ocr_detect_thread.daemon = True
            self.ocr_detect_thread.start()
        else:
            self.detect_thread = DetectThread(self.main_ui.net_dic[net_name], self.main_ui.darknet_queue,
                                              self.main_ui.target_queue)
            # 绑定信号与槽函数
            self.detect_thread.detect_result_signal.connect(finish_func)
            self.detect_thread.daemon = True
            self.detect_thread.start()

    def finish_detect_thing(self, finish_func, next_task, speak_text):
        # QApplication.processEvents()
        logger.debug("检测出目标物体，展示标签：{}".format(speak_text))
        self.main_ui.hardware.pause_thread()
        self.detect_thread.detect_result_signal.disconnect(finish_func)
        self.detect_thread.close()  # 消费者先关
        self.main_ui.hardware.sound_task_thread.label_text = None
        self.main_ui.hardware.sound_task_thread.speak(speak_text, "green")
        while self.main_ui.hardware.sound_task_thread.is_playing:
            pass
        self.detect_win.close()
        logger.info("next函数名为：{}".format(next_task.__name__))
        self.main_ui.clear_queue()
        if next_task.__name__ != "end":
            self.conversion_ui.change_show_text(speak_text)
            self.conversion_ui.show()
            self.timer.timeout.connect(next_task)
            logger.debug("打开定时器！！！")
            self.timer.start(self.conversion_time * 1000)
        else:
            next_task()

    def speak_start(self):
        self._count = 0
        self.main_ui.hardware.sound_task_thread.resume()

    def speak_close(self):
        self.main_ui.hardware.sound_task_thread.pause()
