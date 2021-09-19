# 安全员 Security officer
import os
import time

from PyQt5.QtCore import QTimer
from loguru import logger

from core.task_model.task_base import TaskBase
from core.tools import get_log_level, save_img
from lib.send_to_server.send_img_to_server import send

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class HeightWork(TaskBase):
    TARGET_THING = "person"

    def __init__(self, main_ui):
        super().__init__(main_ui)
        self.sava_img_path = os.path.join(self.save_img_path, "height_work", self.cur_data)
        self.safety_officer_detect_timer = QTimer()  # 初始化定时器
        # self.safety_caps_detect_task()
        self.safety_officer_face_detect_task()

    # ================================= 人员穿戴 检测 ======================================
    def safety_caps_detect_task(self):
        logger.debug("进入人员穿戴检测")
        #  welder_wear_detect_task
        self.detect_things("height", self.finish_safety_caps_detect_task)

    def finish_safety_caps_detect_task(self, tar):
        if len(tar[0]) != 0:
            if tar[0][0][0] == self.SATE_HAT_TAPE_TARGET:
                logger.debug("检测出安全帽")
                s = "检测出安全帽、安全带，将进行安全员人脸识别！"
                self.finish_detect_thing(self.finish_safety_caps_detect_task,
                                         self.safety_officer_face_detect_task,
                                         s)
            else:
                cur_time = time.strftime("%H_%M_%S", time.localtime())
                img_name = cur_time + "_" + tar[0][0][0] + ".jpg"
                logger.info("img_name{}".format(img_name))
                save_img(self.sava_img_path, img_name, tar[1])
                send(os.path.join(self.sava_img_path, img_name), "1_"+self.cur_data + "_" + img_name)
                self.main_ui.hardware.sound_task_thread.label_text = tar[0][0][0]
        else:
            logger.info("没有检测出任何物体")
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测出任何物体，请重新检测！"

    # ================================= 安全员人脸识别检测 ======================================
    def safety_officer_face_detect_task(self):
        logger.debug("安全员人脸识别检测")
        # 焊工证人脸识别  Face recognition for welder's license
        # self.timer.timeout.disconnect(self.safety_officer_face_detect_task)
        # time.sleep(1)
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

                # self.safety_officer_detect_timer_task()
            else:
                self.main_ui.hardware.sound_task_thread.label_text = "没有检测到非安全员人脸!"
        if _count == 0:
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测到人脸!"

    # ===========================启动一个安全员检测定时器====================================================
    def safety_officer_detect_task(self):

        # 每隔5分钟唤醒一次，进行检测
        # 使用定时器
        logger.debug("进入安全员检测")
        self.timer.timeout.disconnect(self.safety_officer_detect_task)
        # time.sleep(1)
        # if self.standby_ui:
        #     self.standby_ui.close()
        self.detect_things("net0", self.finish_safety_officer_detect_task)

    def finish_safety_officer_detect_task(self, tar):
        if len(tar[0]) != 0:
            # if tar[0][0][0] == self.SAFETY_OFFICER_TARGET:
            if tar[0][0][0] == "人 ":
                s = "安全员检测合格"
                # self.safe_timer.timeout(self.main_ui.hardware.sound_task_thread.pause)
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
