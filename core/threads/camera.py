from pprint import pprint
from queue import Full

import cv2
from PyQt5.QtCore import QThread
import time
from loguru import logger

from core.tools import get_log_level

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class CameraThread(QThread):
    """
    摄像机获取图像
    """

    def __init__(self, img_queue, darknet_queue, src=0):
        super(CameraThread, self).__init__()
        # self.setName("CameraThread")

        # self.ui_obj = ui_obj
        self.img_queue = img_queue
        self.darknet_queue = darknet_queue
        self.frame = None
        self.status = None
        self.capture = cv2.VideoCapture(src)  # 打开摄像机
        self._isPause = True  # 是否睡眠标志位
        self._close = False

    def pause(self):
        self.frame = None
        self.img_queue.queue.clear()
        self.darknet_queue.queue.clear()
        self._isPause = True

    def is_pause(self):
        return self._isPause

    def resume(self):
        self._isPause = False

    def close(self):
        self._close = True
        self.capture.release()

    def add_frame_to_queue(self):
        """
        将获取的图像推送队列
        :return:
        """
        start_time = time.time()
        if self.capture.isOpened():
            status, self.frame = self.capture.read()
            logger.info(self.frame.shape)
            if status:
                logger.info("转换图片格式")
                frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                if self.img_queue.full():
                    logger.info("img_queue满了")
                    try:
                        self.img_queue.get_nowait()
                    except Full as e:
                        logger.error(e)
                else:
                    logger.info("添加一帧到img_queue")
                    self.img_queue.put(frame_rgb)
                if self.darknet_queue.full():
                    logger.info("darknet_queue满了")
                    try:
                        self.darknet_queue.get_nowait()
                    except Full as e:
                        logger.error(e)
                else:
                    logger.info("添加一帧到darknet_queue")
                    self.darknet_queue.put(frame_rgb)

        if time.time() - start_time < 0.066:
            time.sleep(abs(0.066 - (time.time() - start_time)))

    def run(self):
        while not self._close:
            if not self._isPause:
                try:
                    self.add_frame_to_queue()
                except:
                    time.sleep(0.06)
            else:
                logger.info("摄像机睡眠啦")
                time.sleep(0.3)
        self.capture.release()
