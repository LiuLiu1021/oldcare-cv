# 本份代码用于利用 Face++ 的人脸检测 API 进行表情检测
# 相关文档地址：https://console.faceplusplus.com.cn/documents/4888373

# 作者：蒲韬，putao3@mail2.sysu.edu.cn
#　所需依赖：Python 3 
# 最后更新时间：2019.07.22

import os
import time
import json
import base64
import requests
import numpy as np

import urllib
import urllib.request

class AverageMeter(object):
    '''Computes and stores the sum, count and average'''
    def __init__(self):
        self.reset()

    def reset(self):    
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, count=1):
        self.val = val
        self.sum += val 
        self.count += count
        if self.count==0:
            self.avg = 0
        else:
            self.avg = float(self.sum) / self.count

# 调用　API　进行人脸检测与属性分析
def useAPI(imgPath):
    request_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"

    data = {
        "api_key" : "0uEHLmhez7KZnFYfY-1a_hOA1yw-IMtx",
        "api_secret" : "ITzjaQdL2UBpwoFv2j2cXCUHgIB4tvKo",
        "return_attributes" : "emotion",
    }
    files = {"image_file": open(imgPath, "rb")}

    response = requests.post(request_url, data=data, files=files)
    content = response.content.decode('utf-8')
    content = json.loads(content)

    return content

if __name__=='__main__':
    # 七类基本表情 -> angry:愤怒 disgust:厌恶 fear:恐惧 happy:高兴 sad:伤心 surprise:惊讶 neutral:无情绪
    Label = {'Surprise':0, 'Fear':1, 'Disgust':2, 'Happy':3, 'Sad':4, 'Angry':5, 'Neutral':6}

    acc, prec, recall = AverageMeter(), [AverageMeter() for i in range(7)], [AverageMeter() for i in range(7)]

    pathName = ['Surprise','Fear','Disgust','Happy','Sad','Angry','Neutral']
    for i in range(7):
        Dirs = os.listdir('/home/reed/Desktop/code/oldcare/images/seven/'+pathName[i])
        for imgFile in Dirs:
            imgPath = '/home/reed/Desktop/code/oldcare/images/seven/'+pathName[i]+'/'+imgFile
            content = useAPI(imgPath)

            if 'faces' not in content.keys() or content['faces'] is None:
                continue

            for face in content['faces']:
                result = face['attributes']['emotion']
                pred = np.array([result['surprise'],result['fear'],result['disgust'],result['happiness'],result['sadness'],result['anger'],result['neutral']])
                pred = np.argmax(pred)

                if pred==i:
                    acc.update(1,1)
                    prec[i].update(1,1)
                    recall[i].update(1,1)
                else:
                    acc.update(0,1)
                    prec[pred].update(0,1)
                    recall[i].update(0,1)

            # 免费账号的　QPS 为 10。（QPS（query per second）指每秒向服务发送的请求数量峰值，相当于每个API每秒可以允许请求的最大上限数量。）
            time.sleep(0.11)

    print('''
    Sample {recall[0].count:d} {recall[1].count:d} {recall[2].count:d} {recall[3].count:d} {recall[4].count:d} {recall[5].count:d} {recall[6].count:d}\t
    Accuracy {acc.avg:.4f}\t
    Precision {prec[0].avg:.4f} {prec[1].avg:.4f} {prec[2].avg:.4f} {prec[3].avg:.4f} {prec[4].avg:.4f} {prec[5].avg:.4f} {prec[6].avg:.4f}\t
    Recall {recall[0].avg:.4f} {recall[1].avg:.4f} {recall[2].avg:.4f} {recall[3].avg:.4f} {recall[4].avg:.4f} {recall[5].avg:.4f} {recall[6].avg:.4f}\t
    '''.format(acc=acc,prec=prec,recall=recall))
