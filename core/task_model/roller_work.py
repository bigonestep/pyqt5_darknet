# 氧气瓶距离检测 Distance detection of oxygen cylinder
import os.path
import time

from PyQt5.QtCore import Qt
from loguru import logger

from core.task_model.task_base import TaskBase
from core.tools import get_log_level, save_img, set_back_color
from lib.send_to_server.send_img_to_server import send

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class RollerWork(TaskBase):
    TARGET_THING = "person"

    def __init__(self, main_ui):
        super().__init__(main_ui)

        self.sava_img_path = os.path.join(self.save_img_path, "roller_work", self.cur_data)
        logger.info("roller_work, save img path: {}".format(self.sava_img_path))

        self.safety_caps_detect_task()

    # ================================= 人员穿戴 检测 ======================================
    def safety_caps_detect_task(self):
        logger.debug("进入焊工面罩、有手套检测")
        #  welder_wear_detect_task
        self.detect_things("mask_shoes", self.finish_safety_caps_detect_task)

    def finish_safety_caps_detect_task(self, tar):

        if len(tar[0]) != 0:
            if tar[0][0][0] == self.SAFE_HAT_SHOES_TARGET:
                logger.debug("检测出安全帽")
                s = "检测出安全帽，将进行标志牌、锁检测！"
                self.finish_detect_thing(self.finish_safety_caps_detect_task,
                                         self.signage_detect_task,
                                         s)
            else:
                cur_time = time.strftime("%H_%M_%S", time.localtime())
                img_name = cur_time + "_" + tar[0][0][0] + ".jpg"
                logger.info("img_name{}".format(img_name))
                save_img(self.sava_img_path, img_name, tar[1])
                send(os.path.join(self.sava_img_path, img_name), "0_" + self.cur_data + "_" + img_name)
                self.main_ui.hardware.sound_task_thread.label_text = tar[0][0][0]
        else:
            logger.info("没有检测出任何物体")
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测出任何物体，请重新检测！"

    # ================================= 安全帽 检测 ======================================
    def signage_detect_task(self):
        logger.debug("进入标志牌、锁检测")
        self.timer.timeout.disconnect(self.signage_detect_task)

        self.detect_things("sign_file", self.finish_signage_detect_task)

    def finish_signage_detect_task(self, tar):
        if len(tar[0]) != 0:
            if tar[0][0][0] == self.SIGNAGE_LOCKS_TARGET:
                logger.debug("检测标志牌、锁成功")
                s = "检测出有标志牌、锁，检测结束"
                self.finish_detect_thing(self.finish_signage_detect_task,
                                         self.end,
                                         s)
            else:
                cur_time = time.strftime("%H_%M_%S", time.localtime())
                img_name = cur_time + "_" + tar[0][0][0] + ".jpg"
                logger.info("img_name{}".format(img_name))
                save_img(self.sava_img_path, img_name, tar[1])
                send(os.path.join(self.sava_img_path, img_name), "0_" + self.cur_data + "_" + img_name)
                logger.debug("检测出{}".format(tar[0][0][0]))
                self.main_ui.hardware.sound_task_thread.label_text = tar[0][0][0]
        else:
            logger.info("没有检测出任何物体")
            self.main_ui.hardware.sound_task_thread.label_text = "没有检测出任何物体，请重新检测！"

    def end(self):
        pass
