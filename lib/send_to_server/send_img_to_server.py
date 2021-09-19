# coding:utf-8
import requests
from loguru import logger

from core.tools import yaml_file_path, get_yaml_data, get_log_path, get_log_level

url = get_yaml_data(yaml_file_path).get("server_url")
logger.add(get_log_path(), format="{time}{level}{message}", filter="my_module", level=get_log_level())
'''
url = "http://127.0.0.1:5000/"
str000 = '/home/wangzhihui/Document/pyqt5/pyqt5_darknet/db/img/1_jpg.jpg'
new_name = str000.split('/')
print(new_name[len(new_name) - 1])
f = open(str000, "rb")
files = {'file': (new_name[len(new_name) - 1], f, 'image/jpg')}
r = requests.post(url, files=files)
result = r.text
print(result)
'''


def send(path, img_name):
    try:
        with open(path, "rb") as f:
            files = {'file': (img_name, f, 'image/jpg')}
            r = requests.post(url, files=files)
            result = r.text
            if result == "success":
                logger.debug("发送图片：{}".format(result))
            else:
                logger.error("发送图片失败：{}".format(result))
    except:
        logger.error("发送图片失败")

