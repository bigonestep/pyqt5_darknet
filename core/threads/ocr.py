import re
import time
from threading import Thread
import easyocr

from PyQt5.QtCore import QThread, pyqtSignal

from loguru import logger

from core.tools import get_log_level

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


def get_max_date(_s):
    logger.info("进入get_max_date函数")
    _s.replace(" ", "")
    _mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", _s)
    _count = 0
    _t1 = []
    while _s:
        _mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", _s)
        if _mat:
            _a = _mat.group()
            _t1.append(_a)
            _s = _s[_s.index(_a) + 12:]
        else:
            break
        _count += 1
        if _count > 4:
            break
    logger.debug("_t1:", _t1)
    _t2 = []
    for _i in _t1:
        try:
            _timeArray = time.strptime(_i, "%Y-%m-%d")
            _timeStamp = int(time.mktime(_timeArray))
            _t2.append(_timeStamp)
        except ValueError as e:
            logger.error(e)
    logger.debug("_t2:", _t2)
    return max(_t2) if len(_t2) > 0 else 0


class OcrBase:
    def __init__(self):
        logger.info("开始初始化ocr")
        self.reader = easyocr.Reader(lang_list=['ch_sim', 'en'])

    def get_text(self, img):
        logger.info("进入get_text")
        _text = ""
        result = self.reader.readtext(img)
        for _i in result:
            _text = _text + " " + _i[1]
        logger.info("_text:", _text)
        return _text


class DetectDateThread(QThread):
    date_signal = pyqtSignal(bool)

    def __init__(self, main_ui, ocr_net, img_queue, darknet_queue, target_queue):
        super(DetectDateThread, self).__init__()
        self.main_ui = main_ui
        self.ocr_net = ocr_net
        self.img_queue = img_queue
        self.darknet_queue = darknet_queue
        self.target_queue = target_queue
        self._show_close = False
        self._close = False
        self._is_show = True
        self._last_img = None

    def close(self):
        logger.info("进入ocr.close")
        self._close = True

    def run(self):
        logger.info("打开同步队列传输线程")
        self.show = Thread(target=self.img_to_target)
        self.show.daemon = True
        self.show.start()
        logger.info("同步队列传输线程开启")
        while not self._close:
            self.main_ui.hardware.sound_task_thread.label_text = "请把焊工证放置摄像机范围内"
            time.sleep(3)
            self._is_show = False
            logger.debug("ocr, img_queue, darknet_queue：{}， {}".format(self.img_queue.qsize(), self.darknet_queue.qsize()) )
            while self.img_queue.qsize() < self.darknet_queue.qsize():
                self.darknet_queue.get()
            while self.img_queue.qsize() > self.darknet_queue.qsize():
                self.img_queue.get()
            img = self.darknet_queue.get()
            # cv2.imshow("IMG", img)
            # result = self.ocr_net.get_text(img)
            # max_date = get_max_date(result)
            logger.debug("开始ocr")
            _st = time.time()
            ret = is_qualified_welder_license(self.ocr_net, img)
            logger.debug("结束ocr, 结果：{}, 共用了{}s".format(ret, int(time.time() - _st)))
            self.date_signal.emit(ret)

            self._is_show = True
            if ret:
                logger.info("如果满足，有两秒的时间等待")
                self._show_close = True
                time.sleep(2)
                break

    def img_to_target(self):
        while not self._show_close:
            if self._is_show:
                logger.info("ocr图片传送到界面展示")
                _st = time.time()
                logger.debug("img_queue, darknet_queue：{}， {}".format(self.img_queue.qsize(), self.darknet_queue.qsize()) )
                while self.img_queue.qsize() < self.darknet_queue.qsize():
                    self.darknet_queue.get()
                while self.img_queue.qsize() > self.darknet_queue.qsize():
                    self.img_queue.get()
                self._last_img = self.img_queue.get()
                self.darknet_queue.get()
                self.target_queue.put(self._last_img)
                if time.time() - _st < 0.066:
                    time.sleep(int(abs(0.066 - (time.time() - _st))))
            else:
                while self.img_queue.qsize() < self.darknet_queue.qsize():
                    self.darknet_queue.get()
                while self.img_queue.qsize() > self.darknet_queue.qsize():
                    self.img_queue.get()
                self.img_queue.get()
                self.darknet_queue.get()
                if self._last_img is not None:
                    self.target_queue.put(self._last_img)
                    time.sleep(0.5)


def is_qualified_welder_license(ocr_net, img):
    _text = ocr_net.get_text(img)
    if len(_text) != 0:
        logger.debug(_text)
        welder_date = get_max_date(_text)
        logger.debug(welder_date)
        if welder_date != 0 and int(time.time() > welder_date):
            return True
    return False


if __name__ == '__main__':
    st = time.time()
    o = OcrBase()
    print("模型加载完成,共用了{}！！！".format(time.time() - st))
    st = time.time()
    text = o.get_text("/home/wangzhihui/Document/pyqt5/pyqt5_darknet/db/img/11.jpg")
    t = []
    print(text)
    print(time.time() - st)
    print(get_max_date(text))
    print(type(get_max_date(text)))
    print(time.time() < get_max_date(text))
