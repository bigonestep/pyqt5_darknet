import time
from pprint import pprint

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from core.tools import get_yaml_data, yaml_file_path, get_log_level
import face_recognition
from loguru import logger

logger.add('runtime.log', format="{time} {level} {message}", filter="my_module", level=get_log_level())


class FaceDetectBase:
    def __init__(self):
        data = get_yaml_data(yaml_file_path)
        self.face = data.get("face")
        self.known_face_names = []
        self.known_face_encodings = []

        self.init_known_face()

    def init_known_face(self):
        # 初始化脸谱
        for cla in self.face:
            # 获取图片

            for j in self.face.get(cla).keys():
                self.known_face_names.append(j)
                known_face_img = face_recognition.load_image_file(self.face.get(cla).get(j))
                known_face_encoding = face_recognition.face_encodings(known_face_img)[0]
                self.known_face_encodings.append(known_face_encoding)

    @staticmethod
    def get_face_img(img_queue):
        img_bgr = img_queue.get()
        small_frame = cv2.resize(img_bgr, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        return img_bgr, rgb_small_frame

    def detect_face_task(self, rgb_small_frame):
        try:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.9)
                name = "Unknown"
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding, )
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

                face_names.append(name)
            return [face_locations, face_names]
        except:
            return [None, None]


class FaceDetectThread(QThread):
    detect_face_result_signal = pyqtSignal(list)

    def __init__(self, face_net, img_queue, target_queue):
        super(FaceDetectThread, self).__init__()
        self.face_net = face_net
        self.img_queue = img_queue
        self.target_queue = target_queue
        self._close = False
        self._count = 0

    def close(self):
        self.img_queue.queue.clear()
        self.target_queue.queue.clear()
        self._close = True

    def run(self):
        while not self._close:
            img_bgr, rgb_small_frame = self.face_net.get_face_img(self.img_queue)
            face_locations, face_names = self.face_net.detect_face_task(rgb_small_frame)
            if face_locations is not None and face_names is not None:
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    cv2.rectangle(img_bgr, (left, top), (right, bottom), (0, 0, 255), 2)
                    # Draw a label with a name below the face
                    cv2.rectangle(img_bgr, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(img_bgr, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                self.target_queue.put(img_bgr)

                logger.debug("檢測人脸完成")

                self._count += 1
                if self._count == 16:
                    self.detect_face_result_signal.emit(face_names)  # 这里只负责把结果发出去，具体操作由使用房控制
                    self._count = 0
            else:
                logger.debug("人脸识别失败")
                time.sleep(0.3)
