#coding:utf-8
from flask import request, Flask
import time
import os
app = Flask(__name__)

@app.route("/", methods=['POST'])
def get_frame():
    start_time = time.time()
    upload_file = request.files['file']
    old_file_name = upload_file.filename
    if upload_file:
        file_path = os.path.join('/home/wangzhihui/Document/test', old_file_name)
        upload_file.save(file_path)
        print ("success")
        print('file saved to %s' % file_path)
        duration = time.time() - start_time
        print('duration:[%.0fms]' % (duration*1000))
        return 'success'
    else:
        return 'failed'


if __name__ == "__main__":
    app.run("127.0.0.1", port=5000)