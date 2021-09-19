from core.threads.camera import CameraThread
from core.threads.play_sound import PlaySound
from loguru import logger

from core.tools import get_log_level

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class ManageHardware:
    def __init__(self, ui_obj, img_queue, darknet_queue):
        self.ui_obj = ui_obj
        self.img_queue = img_queue
        self.darknet_queue = darknet_queue
        self.camera_thread = None
        self.sound_task_thread = None
        self.init_thread()

    def init_thread(self):
        self.camera_thread = CameraThread(self.img_queue, self.darknet_queue)
        self.camera_thread.daemon = True  # 设置为守护线程
        self.sound_task_thread = PlaySound(self.ui_obj)
        self.sound_task_thread.daemon = True
        # 默认都是睡眠的
        self.camera_thread.start()
        self.sound_task_thread.start()

    def close_thread(self):
        self.camera_thread.close()
        self.sound_task_thread.close()

    def pause_thread(self):
        self.camera_thread.pause()
        self.sound_task_thread.pause()

    def resume_thread(self):
        self.camera_thread.resume()
        self.sound_task_thread.resume()

    def is_pause(self):
        return self.camera_thread.is_pause() and self.camera_thread.is_pause()



