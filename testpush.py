from sys import platform

import cv2
import time
import subprocess as sp
import multiprocessing
import psutil


class stream_pusher(object):
    def __init__(self, rtmp_url=None, raw_frame_q=None):
        self.rtmp_url = rtmp_url
        self.raw_frame_q = raw_frame_q

        fps = 20
        width = 640
        height = 480

        self.command = ['ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', "{}x{}".format(width, height),
                        '-r', str(fps),
                        '-i', '-',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'ultrafast',
                        '-f', 'flv',
                        self.rtmp_url]

    def __frame_handle__(self, raw_frame, text, shape1, shape2):
        return (raw_frame)

    def push_frame(self):
        p = psutil.Process()
        p.cpu_affinity([0, 1, 2, 3])
        p = sp.Popen(self.command, stdin=sp.PIPE)

        while True:
            if not self.raw_frame_q.empty():
                raw_frame, text, shape1, shape2 = self.raw_frame_q.get()
                frame = self.__frame_handle__(raw_frame, text, shape1, shape2)

                p.stdin.write(frame.tostring())
            else:
                time.sleep(0.01)

    def run(self):
        push_frame_p = multiprocessing.Process(target=self.push_frame, args=())
        push_frame_p.daemon = True
        push_frame_p.start()


if __name__ == '__main__':
    # # 根据不同的操作系统，设定读取哪个摄像头
    # if platform.system() == 'Linux':  # 如果是Linux系统
    #     cap = cv2.VideoCapture(0)  # 绑定编号为0的摄像头
    #     cap.set(3, 640)  # 设置摄像头画面的宽
    #     cap.set(4, 480)  # 设置摄像头画面的高
    # elif platform.system() == 'Darwin':  # 如果是苹果的OS X系统
    #     cap = cv2.VideoCapture(0)  # 绑定编号为0的摄像头
    #     cap.set(3, 640)
    #     cap.set(4, 480)
    # elif platform.system() == 'Windows':  # 如果是windows系统
    #     cap = cv2.VideoCapture(0)  # 绑定编号为0的摄像头
    #     cap.set(3, 640)
    #     cap.set(4, 480)
    # else:  # 不存在其他系统，所以就不判断了
    #     exit(0)
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    rtmpUrl = "rtmp://192.168.138.129:1935/stream/pupils_trace"
    # rtmpUrl = "rtmp://192.168.138.129:1935/live/yjr"
    raw_q = multiprocessing.Queue()

    my_pusher = stream_pusher(rtmp_url=rtmpUrl, raw_frame_q=raw_q)
    my_pusher.run()
    # while True:
    #     _, raw_frame = cap.read()
    #     info = (raw_frame, '2', '3', '4')
    #     if not raw_q.full():
    #         raw_q.put(info)
    #     cv2.waitKey(1)
    # cap.release()
    # print('finish')
    while (1):
        grabbed, image = cap.read()
        info = (image, '2', '3', '4')  # 把需要送入队列的内容进行封装
        if not raw_q.full():  # 如果队列没满
            raw_q.put(info)  # 送入队列
        cv2.waitKey(1)
        # k = cv.waitKey(1) & 0xff
        # if k == 27:
        # break
    cap.release()
    print('finish')
