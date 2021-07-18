import cv2 as cv
import time
import subprocess as sp
import multiprocessing
import platform
import psutil

if __name__ == '__main__':
    # 根据不同的操作系统，设定读取哪个摄像头
    if platform.system() == 'Linux': # 如果是Linux系统
        # cap = cv.VideoCapture(0) # 绑定编号为0的摄像头
        # cap.set(3, 640) # 设置摄像头画面的宽
        # cap.set(4, 480) # 设置摄像头画面的高
        print('Linux')
    elif platform.system() == 'Darwin': # 如果是苹果的OS X系统
        # cap = cv.VideoCapture(0) #绑定编号为0的摄像头
        # cap.set(3, 640)
        # cap.set(4, 480)
        print('ios')
    elif platform.system() == 'Windows':  # 如果是windows系统
        # cap = cv.VideoCapture(0)  # 绑定编号为0的摄像头
        # cap.set(3, 640)
        # cap.set(4, 480)
        print('Windows')
    else: # 不存在其他系统，所以就不判断了
        exit(0)