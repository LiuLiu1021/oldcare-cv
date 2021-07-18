# -*- coding: utf-8 -*-
'''
摔倒检测模型主程序

用法：
python /home/reed/Desktop/code/oldcare/checkingfalldetection.py
python /home/reed/Desktop/code/oldcare/checkingfalldetection.py --filename /home/reed/Desktop/code/oldcare/tests/corridor_01.avi
'''

# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import cv2
import os
import time
import subprocess
import argparse
import imutils
import threading as t

# 传入参数
import insertingcontrol
from inserting import insert

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=False, default='',help="")
args = vars(ap.parse_args())
input_video = args['filename']

# 控制陌生人检测
fall_timing = 0  # 计时开始
fall_start_time = 0  # 开始时间
fall_limit_time = 2  # if >= 1 seconds, then he/she falls.

# 全局变量
model_path = '/home/reed/Desktop/code/oldcare/models/fall/fall_detection3200110.hdf5'
output_fall_path = '/home/reed/Desktop/code/oldcare/supervision'
# your python path
# python_path = '/home/reed/anaconda3/envs/tensorflow/bin/python3.6'

# 全局常量
TARGET_WIDTH = 64
TARGET_HEIGHT = 64

# 传入参数
def checkingfalldetection(grabbed,image,model):
    global fall_timing,fall_start_time

    if not grabbed:
        return

    roi = cv2.resize(image, (TARGET_WIDTH, TARGET_HEIGHT))
    roi = roi.astype("float") / 255.0
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)

    # determine facial expression
    (fall, normal) = model.predict(roi)[0]
    if fall > normal:
        label = "Fall (%.2f)" % (fall)
    else:
        label = "Normal (%.2f)" % (normal)

    # display the label and bounding box rectangle on the output frame
    cv2.putText(image, label, (image.shape[1] - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    if fall > normal:
        if fall_timing == 0:  # just start timing
            fall_timing = 1
            fall_start_time = time.time()
        else:  # alredy started timing
            fall_end_time = time.time()
            difference = fall_end_time - fall_start_time

            current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

            if difference < fall_limit_time:
                print('[INFO] %s, 走廊, 摔倒仅出现 %.1f 秒. 忽略.'% (current_time, difference))
            else:  # strangers appear
                event_desc = '走廊, 有人摔倒!!!'
                event_location = '走廊'
                print('[EVENT] %s, 走廊, 有人摔倒!!!' % (current_time))
                path=os.path.join(output_fall_path,'fall_%s.jpg'% current_time)
                cv2.imwrite(path, image)
                # insert into database
                # command = '%s inserting.py --event_desc %s--event_type3 - -event_location % s'% (python_path, event_desc, event_location)
                # p = subprocess.Popen(command, shell=True)
                insert(event_desc,2,event_location,'fall_%s.jpg'% current_time)

    return image

if __name__ == '__main__':
    input_video="/home/reed/Desktop/code/oldcare/tests/testfall1.mp4"
    # 初始化摄像头
    if not input_video:
        vs = cv2.VideoCapture(0)
        time.sleep(2)
    else:
        vs = cv2.VideoCapture(input_video)

    print('[INFO] 开始检测是否有人摔倒...')
    fall_model = load_model(model_path)

    t5 = t.Thread(target=insertingcontrol.control)
    t5.start()
    # 不断循环
    while True:

        (grabbed, frame) = vs.read()
        image = checkingfalldetection(grabbed, frame,fall_model)
        image = imutils.resize(image, width=480, height=360)
        cv2.imshow("oldcare_system", image)
        # Press 'ESC' for exiting video
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    vs.release()
    cv2.destroyAllWindows()
