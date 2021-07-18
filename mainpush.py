# -*- coding: utf-8 -*-
import argparse
import cv2
import time
import imutils
import numpy as np
import threading as t
# from checkingfalldetection import checkfalldetection, fall_model
from checkingstrangersandfacialexpression import faceutil, facial_expression_model
from checkingvolunteeractivity import checkvolunteeractivity
# from checkingfence import checkfence, fps, net
#
# rtmpsrc1 = "rtmp://123.57.6.153:8001/live/yhl"
# rtmpsrc2 = "rtmp://123.57.6.153:8001/live/yt2"
# rtmpsrc3 = "rtmp://123.57.6.153:8001/live/zkc"
# rtmpsrc4 = "rtmp://123.57.6.153:8001/live/shyfather"

rtmpsrc="rtmp://192.168.138.129:1935/stream/pupils_trace"
# rtmpsrc = "rtmp://192.168.138.129:1935/live/yjr"

global frame1, frame2, frame3, frame4

# vs1 = cv2.VideoCapture(rtmpsrc1)
# vs2 = cv2.VideoCapture(rtmpsrc2)
# vs3 = cv2.VideoCapture(rtmpsrc3)
# vs4 = cv2.VideoCapture(rtmpsrc4)
vs2=cv2.VideoCapture(rtmpsrc)
time.sleep(2)

#
# def checkstrangerthread():
#     print("11111")
#     while True:
#         frame1 = checkstrangersandfacial(vs1, faceutil, facial_expression_model)
#         cv2.imshow("1", frame1)
#

def checkvolunteerthread():
    print("22222")
    while True:
        frame2 = checkvolunteeractivity(vs2, faceutil)
#
#
# def checkfallthread():
#     print("33333")
#     while True:
#         frame3 = checkfalldetection(vs3, fall_model)
#
#
# def checkfencethread():
#     print("44444")
#     while True:
#         frame4 = checkfence(vs4, fps, net)


def insertingctrl():
    seconds = 1  # 每经过60秒才允许再次插入
    while True:
        f = open('/home/reed/Desktop/code/oldcare/allowinsertdatabase.txt', 'r')
        content = f.read()
        f.close()

        allow = content[11:12]

        if allow == '0':
            print('status: not allow')
            for i in range(seconds, 0, -1):
                print('wait %d seconds...' % (i))
                time.sleep(1)

            f = open('/home/reed/Desktop/code/oldcare/allowinsertdatabase.txt', 'w')
            f.write('is_allowed=1')
            f.close()

        elif allow == '1':
            print('status: allow')
            time.sleep(1)
        else:
            pass

#
# def showframe():
#     while True:
#         ret, video = vs5.read()
#         cv2.imshow("oldcare_system", video)


if __name__ == '__main__':
    # print('[INFO] 开始检测是否有人摔倒...')
    print('[INFO] 开始检测义工和老人是否有互动...')
    # print('[INFO] 开始检测陌生人和表情...')
    # print('[INFO] 开始检测禁止区域入侵...')

    # t1 = t.Thread(target=checkstrangerthread)
    t2 = t.Thread(target=checkvolunteerthread)
    # t3 = t.Thread(target=checkfallthread)
    # t4 = t.Thread(target=checkfencethread)
    t5 = t.Thread(target=insertingctrl)
    # t6 = t.Thread(target=showframe)

    # t1.start()
    t2.start()
    # t3.start()
    # t4.start()
    t5.start()
    # t6.start()
    #
    # t1.join()
    t2.join()
    # t3.join()
    # t4.join()
    t5.join()
    # t6.join()

