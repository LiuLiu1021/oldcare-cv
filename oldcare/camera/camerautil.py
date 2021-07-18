import cv2
import threading
from time import time,sleep

class RecordingThread(threading.Thread):
    def __init__(self, name, camera, save_video_path):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True

        self.cap = camera
        # 创建视频流写入对象，VideoWriter_fourcc为视频编解码器，20为帧播放速率，（640，480）为视频帧大小
        # fourcc意为四字符代码（Four-Character Codes），顾名思义，该编码由四个字符组成,下面是VideoWriter_fourcc对象一些常用的参数，注意：字符顺序不能弄混
        # cv2.VideoWriter_fourcc('I', '4', '2', '0'),该参数是YUV编码类型，文件名后缀为.avi
        # cv2.VideoWriter_fourcc('P', 'I', 'M', 'I'),该参数是MPEG-1编码类型，文件名后缀为.avi
        # cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),该参数是MPEG-4编码类型，文件名后缀为.avi
        # cv2.VideoWriter_fourcc('T', 'H', 'E', 'O'),该参数是Ogg Vorbis,文件名后缀为.ogv
        # cv2.VideoWriter_fourcc('F', 'L', 'V', '1'),该参数是Flash视频，文件名后缀为.flv
        print('11111111')
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # MJPG
        self.out = cv2.VideoWriter(save_video_path, fourcc, 20.0,(640, 480), True)
        print('22222222')

    def run(self):

        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                # 向视频文件写入一帧
                self.out.write(frame)

        self.out.release()
        print('after release')

    def stop(self):
        print('stop video')
        self.isRunning = False
        print("-------------------------")
        print(self.isRunning)

    def __del__(self):
        self.out.release()


#对recordingThread的封装
class VideoCamera(object):
    def __init__(self,url):
        # Open a camera
        self.cap = cv2.VideoCapture("/home/reed/Desktop/code/oldcare/tests/test.mp4")

        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
        self.startTime=time()
        self.fps=20
        self.maxDelay=5
        self.frames=0

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        self.frames=self.frames+1        
        # if self.frames>(time()-self.startTime-self.maxDelay)*self.fps:
        #     sleep(0.6)
        ret, frame = self.cap.read()
        if ret:
            # frame = cv2.flip(frame, 1)
            ret, jpeg = cv2.imencode('.jpg', frame)

            return jpeg.tobytes()

        else:
            return None

    def start_record(self, save_video_path):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread",self.cap, save_video_path)
        print('3333331')
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()
