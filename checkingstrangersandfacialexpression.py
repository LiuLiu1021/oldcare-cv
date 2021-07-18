# -*- coding: utf-8 -*-
'''
陌生人识别模型和表情识别模型的结合的主程序

用法：
python /home/reed/Desktop/code/oldcare/checkingstrangersandfacialexpression.py
python /home/reed/Desktop/code/oldcare/checkingstrangersandfacialexpression.py --filename /home/reed/Desktop/code/oldcare/tests/tests/room_01.mp4
'''

# 导入包
import argparse

from inserting import insert
from oldcare.facial import FaceUtil
from PIL import Image, ImageDraw, ImageFont
from oldcare.utils import fileassistant
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import cv2
import time
import numpy as np
import os
import imutils
import subprocess
import insertingcontrol
import threading as t


rtmp='rtsp://192.168.43.68/test2'

# 得到当前时间
current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
print('[INFO] %s 陌生人检测程序和表情检测程序启动了.' % (current_time))

# 传入参数
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=False, default='', help="")
args = vars(ap.parse_args())
input_video = args['filename']

# 全局变量
facial_recognition_model_path = '/home/reed/Desktop/code/oldcare/models/face_hog.pickle'
facial_expression_model_path = '/home/reed/Desktop/code/oldcare/models/mini/expression_mini_12800140sgd.hdf5'

output_stranger_path = '/home/reed/Desktop/code/oldcare/supervision'
output_smile_path = '/home/reed/Desktop/code/oldcare/supervision'

people_info_path = '/home/reed/Desktop/code/oldcare/info/people_info.csv'
facial_expression_info_path = '/home/reed/Desktop/code/oldcare/info/facial_expression_info.csv'
# your python path
# python_path = '/home/reed/anaconda3/envs/tensorflow/bin/python3.6'


# 全局常量
FACIAL_EXPRESSION_TARGET_WIDTH = 28
FACIAL_EXPRESSION_TARGET_HEIGHT = 28

VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480

ANGLE = 20

# 控制陌生人检测
strangers_timing = 0  # 计时开始
strangers_start_time = 0  # 开始时间
strangers_limit_time = 0.5  # if >= 2 seconds, then he/she is a stranger.

# 控制情感分析
facial_expression_timing = 0  # 计时开始
facial_expression_start_time = 0  # 开始时间
facial_expression_limit_time = 0.5  # if >= 2 seconds, he/she is smiling

# 得到 ID->姓名的map 、 ID->职位类型的map、
# 摄像头ID->摄像头名字的map、表情ID->表情名字的map
id_card_to_name, id_card_to_type = fileassistant.get_people_info(people_info_path)
facial_expression_id_to_name = fileassistant.get_facial_expression_info(facial_expression_info_path)
test=True
global_frame=None
running=False


# def getFrame():
#     global global_frame,vs,running
#     if not running:
#         vs = cv2.VideoCapture(0)
#         (grabbed, frame) = vs.read()
#         global_frame=frame
#     return global_frame



def checkingstrangersandfacialexpression(grabbed, frame,faceutil,facial_expression_model):

    global strangers_timing,strangers_start_time,facial_expression_timing,facial_expression_start_time,id_card_to_name, id_card_to_type,facial_expression_id_to_name
    # 得到当前时间

    # if we are viewing a video and we did not grab a frame, then we
    # have reached the end of the video
    if not grabbed:
        return

    frame = imutils.resize(frame, width=VIDEO_WIDTH,height=VIDEO_HEIGHT)  # 压缩，加快识别速度
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # grayscale，情感分析

    face_location_list, names = faceutil.get_face_location_and_name(frame)

    # 得到画面的四分之一位置和四分之三位置，并垂直划线
    one_fourth_image_center = (int(VIDEO_WIDTH / 4),int(VIDEO_HEIGHT / 4))
    three_fourth_image_center = (int(VIDEO_WIDTH / 4 * 3),int(VIDEO_HEIGHT / 4 * 3))

    cv2.line(frame, (one_fourth_image_center[0], 0),(one_fourth_image_center[0], VIDEO_HEIGHT),(0, 255, 255), 1)
    cv2.line(frame, (three_fourth_image_center[0], 0),(three_fourth_image_center[0], VIDEO_HEIGHT),(0, 255, 255), 1)

    # 处理每一张识别到的人脸
    for ((left, top, right, bottom), name) in zip(face_location_list,names):

        # 将人脸框出来
        rectangle_color = (0, 0, 255)
        if id_card_to_type[name] == 'old_people':
            rectangle_color = (0, 0, 128)
        elif id_card_to_type[name] == 'employee':
            rectangle_color = (255, 0, 0)
        elif id_card_to_type[name] == 'volunteer':
            rectangle_color = (0, 255, 0)
        else:
            pass
        cv2.rectangle(frame, (left, top), (right, bottom),rectangle_color, 2)

        # 陌生人检测逻辑
        if 'Unknown' in names:  # alert
            if strangers_timing == 0:  # just start timing
                strangers_timing = 1
                strangers_start_time = time.time()
            else:  # already started timing
                strangers_end_time = time.time()
                difference = strangers_end_time - strangers_start_time

                current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

                if difference < strangers_limit_time:
                    print('[INFO] %s, 房间, 陌生人仅出现 %.1f 秒. 忽略.'% (current_time, difference))
                else:  # strangers appear
                    event_desc = '房间, 陌生人出现!!!'
                    event_location = '房间'
                    print('[EVENT] %s, 房间, 陌生人出现!!!'% (current_time))
                    now_time=time.strftime('%Y%m%d_%H%M%S')
                    path=os.path.join(output_stranger_path,'strangers_%s.jpg'% (now_time))
                    cv2.imwrite(path, frame)


                    # # insert into database
                    # command = '%s inserting.py --event_desc %s--event_type2 - -event_location % s'\
                    #           % (python_path, event_desc, event_location)
                    # p = subprocess.Popen(command, shell=True)
                    insert(event_desc,3,event_location,path='strangers_%s.jpg'%now_time,now_time=now_time,ospath=path,frame=frame)

                # 开始陌生人追踪
                unknown_face_center = (int((right + left) / 2),int((top + bottom) / 2))

                cv2.circle(frame, (unknown_face_center[0],unknown_face_center[1]), 4, (0, 255, 0), -1)

                direction = ''
                # face locates too left, servo need to turn right,
                # so that face turn right as well
                if unknown_face_center[0] <one_fourth_image_center[0]:
                    direction = 'right'
                elif unknown_face_center[0] >three_fourth_image_center[0]:
                    direction = 'left'

                    # adjust to servo
                if direction:
                    print('陌生人和老人情感检测摄像头需要 turn %s %d 度' % (direction, ANGLE))

                else:  # everything is ok
                    strangers_timing = 0

        # 表情检测逻辑
        # 如果不是陌生人，且对象是老人
        if name != 'Unknown' and id_card_to_type[name] == 'old_people':
            # 表情检测逻辑
            roi = gray[top:bottom, left:right]
            roi = cv2.resize(roi, (FACIAL_EXPRESSION_TARGET_WIDTH,FACIAL_EXPRESSION_TARGET_HEIGHT))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            # determine facial expression
            (neural, smile) = facial_expression_model.predict(roi)[0]
            if neural > smile:
                facial_expression_label = 'Neural'
            else:
                facial_expression_label = 'Smile'

            if facial_expression_label == 'Smile':  # alert
                if facial_expression_timing == 0:  # just start timing
                    facial_expression_timing = 1
                    facial_expression_start_time = time.time()
                else:  # already started timing
                    facial_expression_end_time = time.time()
                    difference = facial_expression_end_time - facial_expression_start_time

                    current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    if difference < facial_expression_limit_time:
                        print('[INFO] %s, 房间, %s仅笑了 %.1f 秒. 忽略'% (current_time,id_card_to_name[name], difference))
                    else:  # he/she is really smiling
                        event_desc = '房间, %s正在笑.'% (id_card_to_name[name])
                        event_location = '房间'
                        print('[EVENT] %s, 房间, %s正在笑.'% (current_time, id_card_to_name[name]))
                        now_time=time.strftime('%Y%m%d_%H%M%S')
                        ospath=os.path.join(output_smile_path,'smile_%s.jpg'% (now_time))
                        cv2.imwrite(ospath, frame)

                        # insert into database
                        # command = '%s inserting.py --event_desc %s--event_type0 - -event_location % s--old_people_id % d'% \
                        #           (python_path, event_desc,event_location, int(name))
                        # p = subprocess.Popen(command, shell=True)
                        insert(event_desc,1,event_location,"smile_%s.jpg"%now_time,int(name))

            else:  # everything is ok
                facial_expression_timing = 0

        else:  # 如果是陌生人，则不检测表情
            facial_expression_label = ''

        # 人脸识别和情感分析都结束后，把表情和人名写上
        # (同时处理中文显示问题)
        img_PIL = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))

        draw = ImageDraw.Draw(img_PIL)
        final_label = id_card_to_name[name]
        if facial_expression_label != '':
            final_label=final_label + ': '+ facial_expression_id_to_name[facial_expression_label]
        final_label=final_label
        draw.text((left, top - 30), final_label,font=ImageFont.truetype('NotoSansCJK-Black.ttc',40),fill=(255, 0, 0))  # linux

        # 转换回OpenCV格式
        frame = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)

    return frame


if __name__ == '__main__':
    # print('11111111')
    input_video=None
    # 初始化摄像头
    if input_video==None:
        vs = cv2.VideoCapture(0)
        time.sleep(2)
    else:
        vs = cv2.VideoCapture(input_video)
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('[INFO] %s 陌生人检测程序和表情检测程序启动了.' % (current_time))

    print('[INFO] 开始检测陌生人和表情...')
    faceutil = FaceUtil(facial_recognition_model_path)

    # 初始化人脸识别模型
    facial_expression_model = load_model(facial_expression_model_path)
    print('2222222')
    # 不断循环
    t5 = t.Thread(target=insertingcontrol.control)
    t5.start()

    while True:
        
        (grabbed, frame) = vs.read()
        global_frame=frame
        frame1 = checkingstrangersandfacialexpression(grabbed, frame, faceutil,facial_expression_model)

        # show our detected faces along with smiling/not smiling labels
        cv2.imshow("oldcare_system", frame1)

        # Press 'ESC' for exiting video
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    # cleanup the camera and close any open windows
    vs.release()
    cv2.destroyAllWindows()



