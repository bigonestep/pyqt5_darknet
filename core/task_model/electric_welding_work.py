# 焊工检测 Welder inspection
import os
import time

from PyQt5.QtCore import QTimer
from loguru import logger

from core.task_model.task_base import TaskBase
from core.tools import get_log_level, save_img
from lib.send_to_server.send_img_to_server import send

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class ElectricWeldingWork(TaskBase):
    TARGET_THING = "person"

    def __init__(self, main_ui):
        super().__init__(main_ui)
        self.sava_img_path = os.path.join(self.save_img_path, "electric_welding_work", self.cur_data)
        self.safety_officer_detect_timer = QTimer()  # 初始化定时器
        self.fire_extinguisher_task()

    # ================================= 灭火器检测 ======================================
    def fire_extinguisher_task(self):

        #  灭火器检测   Fire Extinguisher
        logger.debug("进入灭火器检测")
        self.detect_things("fire_extinguisher", self.finish_fire_extinguisher_task)

    def finish_fire_extinguisher_task(self, tar):
        # [('person', '69.61', (209.58120727539062, 239.00148010253906, 309.14349365234375, 402.7058410644531))]
        if len(tar[0]) != 0:
            if tar[0][0][0] == self.FIRE_EXTINGUISHER_TARGET:
                logger.debug("检测出来灭火器")
                s = "检测出来灭火器，将进行焊工证检测"
                logger.debug("show_thread:{}".format(self.detect_win.show_thread.isFinished))

                self.finish_detect_thing(self.finish_fire_extinguisher_task,
                                         self.detect_welder_license,
                                         s)
            else:
                cur_time = time.strftime("%H_%M_%S", time.localtime())
                img_name = cur_time + "_" + tar[0][0][0] + ".jpg"
                logger.info("img_name{}".format(img_name))
                save_img(self.sava_img_path, img_name, tar[1])
                send(os.path.join(self.sava_img_path, img_name), "2_"+self.cur_data + "_" + img_name)
                logger.debug("检测出来{}".format(tar[0][0][0]))
                self.main_ui.hardware.sound_task_thread.label_text = tar[0][0][0]
        else:
            logger.info("没有检测出灭火器")
            self.main_ui.hardware.sound_task_thread.label_text = "检测出没有灭火器"

    # ================================= 焊工证检测 ======================================
    def detect_welder_license(self):

        logger.debug("进入焊工证检测")
        self.timer.timeout.disconnect(self.detect_welder_license)
        time.sleep(1)
        self.detect_things("ocr", self.finish_detect_welder_license)

    def finish_detect_welder_license(self, tar):
        # 关闭
        logger.debug("ocr识别结果：{}".format(tar))
        if tar:  # 通过了
            self.ocr_detect_thread.date_signal.disconnect(self.finish_detect_welder_license)
            self.main_ui.hardware.pause_thread()
            self.ocr_detect_thread.close()  # 消费者先关
            self.main_ui.hardware.sound_task_thread.label_text = None
            time.sleep(1.5)
            logger.debug("检测焊工证合格")
            self.main_ui.hardware.sound_task_thread.speak("检测焊工证合格，接下来进行焊工人脸识别检测！", "green")
            # self.main_ui.hardware.sound_task_thread.label_text = "检测焊工人脸合格，检测完毕！"
            self.detect_win.close()
            self.main_ui.clear_queue()
            logger.debug("打开焊工人脸识别检测")
            self.conversion_ui.show()
            self.conversion_ui.change_show_text("检测焊工证合格，将进行焊工人脸识别检测")
            self.timer.timeout.connect(self.welder_face_detect_task)
            logger.debug("打开定时器！！！")
            self.timer.start(3 * 1000)
        else:
            logger.info("检测焊工证不成功")
            self.main_ui.hardware.sound_task_thread.label_text = "检测焊证不合格，请摆正后再次检测"

    # ================================= 焊工人脸识别检测 ======================================
    def welder_face_detect_task(self):

        # 焊工证人脸识别  Face recognition for welder's license
        logger.debug("进入焊工人脸识别检测")
        self.timer.timeout.disconnect(self.welder_face_detect_task)
        self.detect_things("face", self.finish_welder_face_detect_task)

    def finish_welder_face_detect_task(self, tar):
        _count = 0
        for i in tar:
            if i in self.face.get("welder_face").keys():
                logger.debug("检测焊工人脸合格")
                _count += 1
                # 满足了条件
                self.face_detect_thread.detect_face_result_signal.disconnect(self.finish_welder_face_detect_task)
                self.main_ui.hardware.pause_thread()
                self.face_detect_thread.close()  # 消费者先关
                self.main_ui.hardware.sound_task_thread.label_text = None
                # time.sleep(3)
                self.main_ui.hardware.sound_task_thread.speak("检测焊工人脸合格，接下来将进行焊工穿戴检测！", "green")
                # self.main_ui.hardware.sound_task_thread.label_text = "检测焊工人脸合格，检测完毕！"
                self.detect_win.close()
                self.main_ui.clear_queue()
                logger.debug("焊工面罩、有手套检测")
                self.conversion_ui.show()
                self.timer.timeout.connect(self.welder_wear_detect_task1)
                logger.debug("打开定时器！！！")
                self.timer.start(3 * 1000)
        else:
            logger.debug("没有检测到目标人脸")
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测到非焊工人脸!"
        if _count == 0:
            logger.info("没有检测到人脸")
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测到人脸!"

    # ================================= 焊工面罩、有手套检测 ======================================
    def welder_wear_detect_task1(self):

        logger.debug("进入焊工面罩、有手套检测")
        self.timer.timeout.disconnect(self.welder_wear_detect_task1)
        self.detect_things("mask_shoes", self.finish_welder_wear_detect_task1)

    def finish_welder_wear_detect_task1(self, tar):
        if len(tar[0]) != 0:
            if tar[0][0][0] == self.MASK_GLOVES_TARGET:
                logger.debug("检测出焊工有面罩，有手套")
                s = "检测出焊工有面罩，有手套，将进行焊工鞋检测！"
                self.finish_detect_thing(self.finish_welder_wear_detect_task1,
                                         self.welder_wear_detect_task2,
                                         s)
            else:
                cur_time = time.strftime("%H_%M_%S", time.localtime())
                img_name = cur_time + "_" + tar[0][0][0] + ".jpg"
                logger.info("img_name{}".format(img_name))
                save_img(self.sava_img_path, img_name, tar[1])
                send(os.path.join(self.sava_img_path, img_name), "2_"+self.cur_data + "_" + img_name)
                logger.debug("检测出{}".format(tar[0][0][0]))
                self.main_ui.hardware.sound_task_thread.label_text = tar[0][0][0]
        else:
            logger.info("没有检测出任何物体")
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测出任何物体，请重新检测！"

    # ================================= 焊工穿戴  鞋 检测 ======================================
    def welder_wear_detect_task2(self):

        logger.debug("进入焊工鞋检测")
        self.timer.timeout.disconnect(self.welder_wear_detect_task2)
        self.detect_things("shoes", self.finish_welder_wear_detect_task2)

    def finish_welder_wear_detect_task2(self, tar):
        if len(tar[0]) != 0:
            if tar[0][0][0] == self.SHOES_TARGET:
                logger.debug("检测焊工鞋成功")
                s = "检测出有焊工鞋，将进行安全员人脸识别！"
                self.finish_detect_thing(self.finish_welder_wear_detect_task2,
                                         self.safety_officer_face_detect_task,
                                         s)
            else:
                cur_time = time.strftime("%H_%M_%S", time.localtime())
                img_name = cur_time + "_" + tar[0][0][0] + ".jpg"
                logger.info("img_name{}".format(img_name))
                save_img(self.sava_img_path, img_name, tar[1])
                send(os.path.join(self.sava_img_path, img_name), "2_"+self.cur_data + "_" + img_name)
                logger.debug("检测出{}".format(tar[0][0][0]))
                self.main_ui.hardware.sound_task_thread.label_text = tar[0][0][0]
        else:
            logger.info("没有检测出任何物体")
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测出任何物体，请重新检测！"

    # ================================= 安全员人脸识别检测 ======================================

    def safety_officer_face_detect_task(self):

        logger.debug("安全员人脸识别检测")
        # 焊工证人脸识别  Face recognition for welder's license
        self.timer.timeout.disconnect(self.safety_officer_face_detect_task)
        self.detect_things("face", self.finish_safety_officer_face_detect_task)

    def finish_safety_officer_face_detect_task(self, tar):
        _count = 0
        for i in tar:
            if i in self.face.get("inspector_face").keys():
                logger.debug("检测出安全员人脸")
                _count += 1
                # 满足了条件
                self.face_detect_thread.detect_face_result_signal.disconnect(
                    self.finish_safety_officer_face_detect_task)
                self.main_ui.hardware.pause_thread()
                self.face_detect_thread.close()  # 消费者先关
                self.main_ui.hardware.sound_task_thread.label_text = None
                # time.sleep(3)
                self.main_ui.hardware.sound_task_thread.speak("检测安全员人脸合格，将进行安全员检测！", "green")
                # self.main_ui.hardware.sound_task_thread.label_text = "检测焊工人脸合格，检测完毕！"
                self.detect_win.close()
                self.main_ui.clear_queue()
                logger.debug("启动安全员检测定时器")
                self.conversion_ui.change_show_text("检测安全员人脸合格，将进行安全员检测")
                self.conversion_ui.show()
                self.timer.timeout.connect(self.safety_officer_detect_task)
                logger.debug("打开定时器！！！")
                self.timer.start(3 * 1000)
            else:
                self.main_ui.hardware.sound_task_thread.label_text = "没有检测到非安全员人脸!"
        if _count == 0:
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测到人脸!"

    # ===========================启动一个安全员检测定时器====================================================
    def safety_officer_detect_task(self):

        # 每隔5分钟唤醒一次，进行检测
        # 使用定时器
        logger.debug("定时器启动，进入安全员检测")
        self.timer.timeout.disconnect(self.safety_officer_detect_task)
        self.detect_things("person", self.finish_safety_officer_detect_task)

    def finish_safety_officer_detect_task(self, tar):
        if len(tar[0]) != 0:
            if tar[0][0][0] == self.SAFETY_OFFICER_TARGET:
                s = "安全员检测合格"
                if self._count == 0:
                    self.main_ui.hardware.sound_task_thread.speak(s, "green")
                    self.safe_timer.start(self.safer_wait_time * 1000)
                    self.speak_close()
                    logger.debug("声音：{}".format(self.main_ui.hardware.sound_task_thread.is_pause()))
                    self._count = 1
                else:
                    self.main_ui.hardware.sound_task_thread.label_text = s
            else:
                cur_time = time.strftime("%H_%M_%S", time.localtime())
                img_name = cur_time + "_" + tar[0][0][0] + ".jpg"
                logger.info("img_name{}".format(img_name))
                save_img(self.sava_img_path, img_name, tar[1])
                send(os.path.join(self.sava_img_path, img_name), "3_" + self.cur_data + "_" + img_name)
                self.main_ui.hardware.sound_task_thread.label_text = tar[0][0][0]
        else:
            self.main_ui.hardware.sound_task_thread.label_text = "安全员不存在"

    # ================================
    def end(self):
        logger.debug("进入到待机界面")
        self.standby_ui.show()
