# -*- coding: UTF-8 -*-
# Python 2.x引入httplib模块
# import httplib
# Python 3.x引入http.client模块
import http.client
import json

def process(request,  audioFile) :
    # 读取音频文件
    with open(audioFile, mode = 'rb') as f:
        audioContent = f.read()
    host = 'nls-gateway.cn-shanghai.aliyuncs.com'
    # 设置HTTP请求头部
    httpHeaders = {
        'Content-Length': len(audioContent)
        }
    # Python 2.x使用httplib
    # conn = httplib.HTTPConnection(host)

    # Python 3.x使用http.client
    conn = http.client.HTTPConnection(host)

    conn.request(method='POST', url=request, body=audioContent, headers=httpHeaders)
    response = conn.getresponse()
    print('Response status and response reason:')
    print(response.status ,response.reason)
    body = response.read()
    try:
        print('Recognize response is:')
        body = json.loads(body)
        print(body)
        status = body['status']
        if status == 20000000 :
            result = body['flash_result']
            # print(type(result['sentences']))
            # r=json.loads(result['sentences'])
            # print(r)
            # print(type(r))
            texts=''
            for sentence in result['sentences']:
                texts=texts+sentence['text']
            print('Recognize result: ' + texts)
            return texts
        else :
            print('Recognizer failed!')
            return '你好，很高兴认识你'
    except ValueError:
        print('The response is not json format string')
        return '你好，很高认识你'
    conn.close()


def getASR(audioFile):
    appKey = 'lSm58qjGSzcTf7rv'
    token = '339ce6edb65349dba710e8c9d1bc1e2d'

    # 服务请求地址
    url = 'https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/FlashRecognizer'

    # 音频文件，下载地址：https://aliyun-nls.oss-cn-hangzhou.aliyuncs.com/asr/fileASR/examples/nls-sample-16k.wav

    format = 'wav'
    sampleRate = 16000
    # print(type(sampleRate))
    enablePunctuationPrediction  = True
    enableInverseTextNormalization = True
    enableVoiceDetection  = False

    # 设置RESTful请求参数
    request = url + '?appkey=' + appKey
    request = request + '&token=' + token
    request = request + '&format=' + format
    request = request + '&sample_rate=' + str(sampleRate)
    print('Request: ' + request)
    process(request, audioFile)

text=getASR('/home/reed/Desktop/code/oldcare/audio/strangers_20210716_013035.wav')
print(text)