# -*- coding: utf-8 -*-
# @Time    : 2021/4/18 21:21
# @Author  : Wang.Zhihui
# @Email   : w-zhihui@qq.com
# @File    : play_sound.py
# @Software: PyCharm
import os
import time

from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication
from loguru import logger

from core.tools import get_log_level, clear_label_color, set_back_color
from lib.baidu_tts import get_mp3

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())

save_mp3_path = os.path.join(os.path.dirname(__file__), '../../db/mp3')


class PlaySound(QThread):
    def __init__(self, ui_obj):
        super(PlaySound, self).__init__()

        self.is_playing = False
        self.ui_obj = ui_obj
        self.label_text = None
        self._isPause = True
        self._close = False

    def is_pause(self):
        return self._isPause

    def pause(self):
        self.label_text = None
        self._isPause = True

    def resume(self):
        self.label_text = None
        self._isPause = False

    def close(self):
        self.label_text = None

    def speak(self, label_text, c="red"):
        if label_text:

            if c == "green":
                self.show_green(label_text)
                QApplication.processEvents()
                time.sleep(0.1)
            else:
                self.show_red()
            logger.debug("声音开始播放：{}".format(label_text))
            mp3_path = os.path.join(save_mp3_path, label_text + ".mp3")
            if os.path.exists(mp3_path):
                # playsound(mp3_path)
                try:
                    os.system('mpg123 -q {}'.format(mp3_path))
                except:
                    logger.info("Cannot open phone.mp3: File access error.")
            else:
                get_mp3(label_text)
                # playsound(mp3_path)
                try:
                    os.system('mpg123 -q {}'.format(mp3_path))
                except:
                    logger.info("Cannot open phone.mp3: File access error.")
            self.clear_show()
            logger.debug("声音结束播放：{}".format(label_text))
            self.is_playing = False

    def run(self):
        while not self._close:
            if not self._isPause:
                if self.label_text:
                    self.speak(self.label_text)
                    self.label_text = None
            elif self.label_text:
                if "不" in self.label_text or "没有" in self.label_text:
                    self.show_red()
                    time.sleep(2)
                    self.clear_show()
                else:
                    self.show_green()
                    time.sleep(2)
                    self.clear_show()


            else:
                logger.info("声音睡眠啦")

                time.sleep(0.3)

    def show_red(self):
        if self.ui_obj.roller_work and self.ui_obj.roller_work.detect_win:
            set_back_color(self.ui_obj.roller_work.detect_win, self.label_text, Qt.red, Qt.white)
        if self.ui_obj.height_work and self.ui_obj.height_work.detect_win:
            set_back_color(self.ui_obj.height_work.detect_win, self.label_text, Qt.red, Qt.white)
        if self.ui_obj.electric_welding and self.ui_obj.electric_welding.detect_win:
            set_back_color(self.ui_obj.electric_welding.detect_win, self.label_text, Qt.red, Qt.white)
        if self.ui_obj.gas_welding and self.ui_obj.gas_welding.detect_win:
            set_back_color(self.ui_obj.gas_welding.detect_win, self.label_text, Qt.red, Qt.white)

    def show_green(self, text=None):
        if text:
            self.label_text = text
        if self.ui_obj.roller_work and self.ui_obj.roller_work.detect_win:
            set_back_color(self.ui_obj.roller_work.detect_win, self.label_text, Qt.darkGreen, Qt.white)
        if self.ui_obj.height_work and self.ui_obj.height_work.detect_win:
            set_back_color(self.ui_obj.height_work.detect_win, self.label_text, Qt.darkGreen, Qt.white)
        if self.ui_obj.electric_welding and self.ui_obj.electric_welding.detect_win:
            set_back_color(self.ui_obj.electric_welding.detect_win, self.label_text, Qt.darkGreen, Qt.white)
        if self.ui_obj.gas_welding and self.ui_obj.gas_welding.detect_win:
            set_back_color(self.ui_obj.gas_welding.detect_win, self.label_text, Qt.darkGreen, Qt.white)
        self.label_text = None

    def clear_show(self):
        if self.ui_obj.roller_work and self.ui_obj.roller_work.detect_win:
            clear_label_color(self.ui_obj.roller_work.detect_win)
        if self.ui_obj.height_work and self.ui_obj.height_work.detect_win:
            clear_label_color(self.ui_obj.height_work.detect_win)
        if self.ui_obj.electric_welding and self.ui_obj.electric_welding.detect_win:
            clear_label_color(self.ui_obj.electric_welding.detect_win)
        if self.ui_obj.gas_welding and self.ui_obj.gas_welding.detect_win:
            clear_label_color(self.ui_obj.gas_welding.detect_win)
