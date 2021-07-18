# -*- coding: utf-8 -*-
'''
摔倒检测模型主程序

用法：
python /home/reed/Desktop/code/oldcare/checkingfallnew.py
python /home/reed/Desktop/code/oldcare/checkingfalldetection.py --filename /home/reed/Desktop/code/oldcare/tests/corridor_01.avi
'''
# import the necessary packages
from math import sqrt
from AipBodyAnalysis import client
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import cv2
import os
import time
import subprocess
import argparse
import imutils
from inserting import insert

# 传入参数
# ap = argparse.ArgumentParser()
# ap.add_argument("-f", "--filename", required=False, default='', help="")
# args = vars(ap.parse_args())
input_video = None

# 控制陌生人检测
fall_timing = 0  # 计时开始
fall_start_time = 0  # 开始时间
fall_limit_time = 1  # if >= 1 seconds, then he/she falls.

# 全局变量
# model_path = '/home/reed/Desktop/code/oldcare/models/fall/fall_detection3200110.hdf5'
output_fall_path = '/home/reed/Desktop/code/oldcare/supervision'
# your python path
# python_path = '/home/reed/anaconda3/envs/tensorflow/bin/python3.6'

# 全局常量
TARGET_WIDTH = 64
TARGET_HEIGHT = 64

def checkfalldetection(vs):
    # grab the current frame
    global fall_timing, fall_start_time
    (grabbed, image) = vs.read()

    # if we are viewing a video and we did not grab a frame, then we
    # have reached the end of the video
    if input_video and not grabbed:
        return

    if not input_video:
        image = cv2.flip(image, 1)

    ret, jpeg = cv2.imencode('.jpg', image)
    """ 调用人体关键点识别 """
    msg = client.bodyAnalysis(jpeg)

    print(msg)
    print("------------------------------------------")
    str = 'person_info'
    if str in msg.keys():

        person_info = msg["person_info"]
        person_info = person_info[0]
        people_info = person_info["body_parts"]

        # 获取颈部坐标
        neck = people_info["neck"]
        neck_x = neck["x"]
        neck_y = neck["y"]

        # 获取左髋部坐标
        left_hip = people_info["left_hip"]
        left_hip_x = left_hip["x"]
        left_hip_y = left_hip["y"]

        # 获取右髋部坐标
        right_hip = people_info["right_hip"]
        right_hip_x = right_hip["x"]
        right_hip_y = right_hip["y"]

        # 获取左膝坐标
        left_knee = people_info["left_knee"]
        left_knee_x = left_knee["x"]
        left_knee_y = left_knee["y"]

        # 获取右膝坐标
        right_knee = people_info["right_knee"]
        right_knee_x = right_knee["x"]
        right_knee_y = right_knee["y"]

        print("颈部坐标：")
        print(neck_x, neck_y)

        print("左髋部坐标：")
        print(left_hip_x, left_hip_y)

        print("右髋部坐标：")
        print(right_hip_x, right_hip_y)

        print("左膝坐标：")
        print(left_knee_x, left_knee_y)

        print("右膝坐标：")
        print(right_knee_x, right_knee_y)

        center_hip_x = (right_hip_x + left_hip_x) / 2
        center_hip_y = (right_hip_y + right_hip_y) / 2

        cos_body = (center_hip_y - neck_y) / sqrt((neck_x - center_hip_x) ** 2 + (neck_y - center_hip_y) ** 2)

        label = "Fall" if cos_body > 0.7 else "Normal"

        cv2.putText(image, label, (image.shape[1] - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        print("---------")
        if cos_body > 0.7:
            print("走廊，正常！")
        else:
            if fall_timing == 0:  # just start timing
                fall_timing = 1
                fall_start_time = time.time()
            else:  # alredy started timing
                fall_end_time = time.time()
                difference = fall_end_time - fall_start_time

                current_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                             time.localtime(time.time()))

                if difference < fall_limit_time:
                    print('[INFO] %s, 走廊, 摔倒仅出现 %.1f 秒. 忽略.' % (current_time, difference))
                else:  # strangers appear
                    event_desc = '走廊，有人摔倒!!!'
                    event_location = '走廊'
                    print('[EVENT] %s, 走廊, 有人摔倒!!!' % (current_time))
                    cv2.imwrite(os.path.join(output_fall_path,
                                             'snapshot_%s.jpg' % (time.strftime('%Y%m%d_%H%M%S'))), image)  # snapshot
                    # insert into database
                    insert(event_desc,2,event_location,'fall_%s.jpg'% current_time)

    return image


if __name__ == '__main__':

    # 初始化摄像头
    if not input_video:
        vs = cv2.VideoCapture(0)
        time.sleep(2)
    else:
        vs = cv2.VideoCapture(input_video)

    print('[INFO] 开始检测是否有人摔倒...')
    # 不断循环
    while True:

        image = checkfalldetection(vs)
        image = imutils.resize(image, width=480, height=360)
        cv2.imshow("oldcare_system", image)
        # Press 'ESC' for exiting video
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    vs.release()
    cv2.destroyAllWindows()