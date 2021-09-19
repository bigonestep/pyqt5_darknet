import ctypes
import inspect
import sys
import time
from os.path import getsize, join
import cv2
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from yaml import load, FullLoader

yaml_file_path = os.path.join(os.path.dirname(__file__), '../conf/net_conf.yaml')  # 配置文件的路径


def get_yaml_data(yaml_file):
    """
    读取配置文件
    :param yaml_file:  路径
    :return:  配置文件内容
    """
    # 打开yaml文件
    # print("***获取yaml配置文件数据***")
    # print("配置文件路径：", yaml_file)
    if os.path.exists(yaml_file) and (".yaml" in yaml_file or ".yml" in yaml_file):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        # 将字符串转化为字典或列表
        # print("***转化yaml数据为字典或列表***")
        data = load(file_data, Loader=FullLoader)
        return data
    else:
        return None


yaml_data = get_yaml_data(yaml_file_path)


def get_project_path():
    return os.path.join(os.path.dirname(__file__), '../../')


def get_log_level():
    return yaml_data.get("log_level")


def get_log_path():
    cur_data = time.strftime("%Y-%m-%d", time.localtime())
    cur_time = time.strftime("%H_%M_%S", time.localtime())
    log_name = cur_data + "_" + cur_time + ".log"
    return os.path.join(os.path.dirname(__file__), '../db/log', log_name)


def kill_pid(pid):
    """
    杀死一个进程，原理模拟命令行杀死进程，先判断系统，然后调用杀死进程命令
    :param pid:   进程的pid
    :return:
    """
    if 'win' in sys.platform.lower():
        find_kill = 'taskkill -f -pid %s' % pid
    elif 'linux' in sys.platform.lower():
        find_kill = 'kill -9 %s' % pid
    else:
        raise OSError("请自行添加该系统下杀死进程的命令")
    print(find_kill)
    result = os.popen(find_kill)
    print(result)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid threads id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    """
    @profile:强制停掉线程函数
    :param thread:
    :return:
    """
    if thread == None:
        print('threads id is None, return....')
        return

    _async_raise(thread.ident, SystemExit)


def save_img(path, name, img):
    if not os.path.exists(path):
        os.mkdir(path)
    cv2.imwrite(os.path.join(path, name), img)


def get_distance(bbox1, bbox2, l):
    x1, y1, x2, y2 = bbox1
    x3, y3, x4, y4 = bbox2
    z1 = ((abs(x1 - x2)) ** 2 + (abs(y1 - y2)) ** 2) ** 0.5
    real_z1 = l / z1

    z2 = ((abs(x3 - x4)) ** 2 + (abs(y3 - y4)) ** 2) ** 0.5
    real_z2 = l / z2

    real_z = (real_z1 + real_z2) / 2

    center_x1 = (min(x1, x2) + abs(x1 - x2)) / 2
    center_y1 = (min(y1, y2) + abs(y1 - y2)) / 2

    center_x2 = (min(x3, x4) + abs(x3 - x4)) / 2
    center_y2 = (min(y3, y4) + abs(y3 - y4)) / 2

    center_z = ((abs(center_x1 - center_x2)) ** 2 + (abs(center_y1 - center_y2)) ** 2) ** 0.5

    return center_z * real_z


def get_file_folder_size(file_or_folder_path):
    """get size for file or folder"""
    total_size = 0

    if not os.path.exists(file_or_folder_path):
        return total_size

    if os.path.isfile(file_or_folder_path):
        total_size = os.path.getsize(file_or_folder_path)  # 5041481
        return total_size

    if os.path.isdir(file_or_folder_path):
        with os.scandir(file_or_folder_path) as dir_entry_list:
            for cur_sub_entry in dir_entry_list:
                cur_sub_entry_full_path = os.path.join(file_or_folder_path, cur_sub_entry.name)
                if cur_sub_entry.is_dir():
                    cur_sub_folder_size = get_file_folder_size(cur_sub_entry_full_path)  # 5800007
                    total_size += cur_sub_folder_size
                elif cur_sub_entry.is_file():
                    cur_sub_file_size = os.path.getsize(cur_sub_entry_full_path)  # 1891
                    total_size += cur_sub_file_size

            return total_size


def getdirsize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def open_unqualified_folders(path):
    if os.path.exists(path):
        os.system("nautilus %s" % path)
        return True
    else:
        return False


def set_back_color(ui, text, back_color, text_color):
    pe = QPalette()
    pe.setColor(QPalette.WindowText, text_color)
    ui.label.setAutoFillBackground(True)
    pe.setColor(QPalette.Window, back_color)
    ui.label.setPalette(pe)
    # ui.label.setFont(QFont(text, 20, QFont.Bold))
    ui.label.setText(text)


def clear_label_color(ui):
    pe = QPalette()
    pe.setColor(QPalette.Window, Qt.white)
    ui.label.setPalette(pe)
    ui.label.setText("")

