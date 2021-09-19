import os

import cv2
from PyQt5.QtCore import QThread, pyqtSignal

from core.tools import yaml_file_path, get_log_level, get_yaml_data
from lib.darknet import darknet

from loguru import logger
logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class Parameters:
    """
    yolo检测网络的各项参数
    """

    def __init__(self, net_name):
        opt = self.get_conf(net_name)
        self.data_file_path = opt.get("data_file_path")
        self.config_file_path = opt.get("config_file_path")
        self.weights_path = opt.get("weights_path")
        self.thresh = float(opt.get("thresh"))
        # 上面是相对路径，下面转换成绝对路径
        self.get_absolute_path()

    @staticmethod
    def get_conf(net_name):
        conf_yaml = get_yaml_data(yaml_file_path)
        if conf_yaml is not None:
            opt = conf_yaml.get("net").get(net_name)
            return opt

    def get_absolute_path(self):
        path = os.path.join(os.path.dirname(__file__), '../../')
        self.data_file_path = os.path.join(path, self.data_file_path)
        logger.info(self.data_file_path)
        self.config_file_path = os.path.join(path, self.config_file_path)
        self.weights_path = os.path.join(path, self.weights_path)


class DetectBase:
    def __init__(self, net_name):
        self.opt = Parameters(net_name)

        self.network, self.class_names, self.class_colors = darknet.load_network(
            self.opt.config_file_path,
            self.opt.data_file_path,
            self.opt.weights_path
        )
        self.darknet_image = darknet.make_image(416, 416, 3)
        self.thresh = self.opt.thresh

    def detect_run(self, img):
        try:
            detections = darknet.detect_image(self.network, self.class_names, img,
                                              thresh=self.thresh)
            return detections
        except:
            logger.error("检测出错，返回[]")
            return []


class DetectThread(QThread):
    detect_result_signal = pyqtSignal(list)

    def __init__(self, net_obj, darknet_queue, target_queue):
        super(DetectThread, self).__init__()
        # self.setName("DetectThread")
        self.darknet_image = darknet.make_image(416, 416, 3)
        self.net_obj = net_obj
        self.darknet_queue = darknet_queue
        self.target_queue = target_queue
        self._close = False
        self._count = 0

    def close(self):
        # self.darknet_queue.queue.clear()
        # self.target_queue.queue.clear()
        self._close = True

    def run(self):
        while not self.darknet_queue.empty():
            self.darknet_queue.get()
        while not self.target_queue.empty():
            self.target_queue.get()
        while not self._close:
            img_rgb = self.darknet_queue.get()
            frame_resized = cv2.resize(img_rgb, (416, 416), interpolation=cv2.INTER_LINEAR)
            darknet.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())
            ret = self.net_obj.detect_run(self.darknet_image)
            image = darknet.draw_boxes(ret, frame_resized, self.net_obj.class_colors)
            self.target_queue.put(image)
            logger.debug("檢測完成")
            # [('person', '69.61', (209.58120727539062, 239.00148010253906, 309.14349365234375, 402.7058410644531))]
            # 这里不没帧都发
            self._count += 1
            if self._count == 16:

                self.detect_result_signal.emit([ret, image])  # 这里只负责把结果发出去，具体操作由使用房控制
                self._count = 0
