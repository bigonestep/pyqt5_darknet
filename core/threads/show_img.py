import time
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QSize, QThread
from loguru import logger


from core.tools import get_log_level
logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class ShowImageThread(QThread):
    # TODO： 这里做展示图片，不对图片做任何的处理操作。包括格式转换等等
    def __init__(self, ui_obj, img_queue, target_queue):
        # 初始化展示图片的窗口
        super(ShowImageThread, self).__init__()
        self.ui_obj = ui_obj
        self.img_queue = img_queue
        self.target_queue = target_queue
        self.show_img_lbl = QLabel(ui_obj)
        self.ui_obj.detect_show_img.addWidget(self.show_img_lbl)
        self._close = False

    def close(self):
        self._close = True

    def get_img(self):
        # 获取图像
        # if not self.target_queue.empty():    # 如果结果队列是空的，说明检测没有返回图片，那么就需要显示原图
        logger.info("展示检测后圖片:{} ".format(self.target_queue.qsize()))
        img = self.target_queue.get()
        logger.info("展示圖片维度:{} ".format(img.shape))
        # else:
        #     logger.info("展示原圖片")
        #     img = self.img_queue.get()
        return img

    @staticmethod
    def cv2img(cv_img):
        """
        将cv2的BGR转成qt使用的RGB
        :param cv_img: cvBGR图像
        :return: qt可以展示的图像
        """
        # img_cv_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_cv_rgb = cv_img
        img_pyqt = QImage(img_cv_rgb[:], img_cv_rgb.shape[1], img_cv_rgb.shape[0], img_cv_rgb.shape[1] * 3,
                          QImage.Format_RGB888)
        pixmap = QPixmap(img_pyqt)
        return pixmap

    def show(self):
        cv_img = self.get_img()
        w = self.show_img_lbl.width()
        h = self.show_img_lbl.height()
        pixmap = self.cv2img(cv_img)
        pixmap = pixmap.scaled(QSize(w, h), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.show_img_lbl.setPixmap(pixmap)
        # self.show_img_lbl.setScaledContents(True)

    def run(self):
        while not self._close:
            start_time = time.time()
            self.show()
            end_time = time.time()
            if end_time - start_time < 0.066:
                time.sleep(0.066 - (end_time - start_time))
        else:
            time.sleep(0.3)
