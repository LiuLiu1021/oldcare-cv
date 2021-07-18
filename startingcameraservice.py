'''
启动摄像头主程序

用法: 
python /home/reed/Desktop/code/oldcare/startingcameraservice.py
python /home/reed/Desktop/code/oldcare/startingcameraservice.py --location room

直接执行即可启动摄像头，浏览器访问 http://192.168.1.156:5001/ 即可看到
摄像头实时画面

'''
import argparse
import csv
import os
import time
import json
import cv2
from flask import Flask, render_template, Response, request, send_from_directory, make_response
from flask.helpers import send_file
from flask_socketio import SocketIO, emit
from oldcare.camera.camerautil import VideoCamera
# from oldcare.facial import FaceUtil
# from keras.models import load_model
from collectingfaces import collectingfaces
import flask_cors
import redisinit
import sys
import os
interface_path = os.path.dirname(__file__)
sys.path.insert(0, interface_path)


from engineio.payload import Payload

# Payload.max_decode_packets = 100
# 传入参数
# ap = argparse.ArgumentParser()
# ap.add_argument("-f", "--location", required=False,default='room', help="")
# args = vars(ap.parse_args())
# location = args['location']
#
# if location not in ['room', 'yard', 'corridor', 'desk']:
#     raise ValueError('location must be one of room, yard, corridor or desk')

# recognition_model_path = '/home/reed/Desktop/code/oldcare/models/face_hog.pickle'
# faceutil=FaceUtil(recognition_model_path)
# facial_expression_model_path = '/home/reed/Desktop/code/oldcare/models/mini/expression_mini_6400140sgd.hdf5'
# facial_expression_model = load_model(facial_expression_model_path)

# API
app = Flask(__name__)
cors=flask_cors.CORS(app,resources={r"/*":{"origins":"*"}})

app.config['SECRET_KEY'] = 'secret!'
socketio=SocketIO(app,cors_allowed_origins='*')

global desk_video_camera
room_video_camera = None
room_global_frame = None
desk_video_camera = None
desk_global_frame = None
yard_video_camera = None
yard_global_frame = None
corridor_video_camera = None
corridor_global_frame = None

rtmpsrc1="rtsp://192.168.43.68/test2"
rtmpsrc2="rtsp://192.168.43.209/test2"
rtmpsrc3="rtsp://192.168.43.68/test2"
rtmpsrc4="rtsp://192.168.43.68/test2"

#正在看的是哪个监控画面，0房间，1桌面，2院子，3走廊
video_camera_state=int(0)
camera_state={0:'room',1:'desk',2:'yard',3:'corridor'}

global_event=None

# @ app.route('/')
# def index():
#     return render_template('room_camera.html')


@app.route('/record_status', methods=['POST'])
def record_status():
    print('inrecord')
    global room_video_camera,desk_video_camera,yard_video_camera,corridor_video_camera,video_camera_state

    status = request.form.get('status')
    print(status)

    if video_camera_state==0 and room_video_camera == None:
        room_video_camera = VideoCamera(rtmpsrc1)
    elif video_camera_state==1 and desk_video_camera == None:
        desk_video_camera = VideoCamera(rtmpsrc2)
    elif video_camera_state==3 and yard_video_camera == None:
        yard_video_camera = VideoCamera(rtmpsrc3)
    elif video_camera_state==4 and corridor_video_camera == None:
        corridor_video_camera = VideoCamera(rtmpsrc4)

    data={}

    if status == "true":
        current_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        save_video_path = '%s_%s.avi' % (camera_state[video_camera_state], current_time)

        # if video_camera_state==0:
        #     room_video_camera.start_record(save_video_path)
        # elif video_camera_state==1:
        #     desk_video_camera.start_record(save_video_path)
        # elif video_camera_state == 2:
        #     yard_video_camera.start_record(save_video_path)
        # elif video_camera_state == 3:
        #     corridor_video_camera.start_record(save_video_path)
        data['state']='start record'
        data['path']=save_video_path
    else:
        # save_video_path = request.form.get('path')
        # if video_camera_state==0:
        #     room_video_camera.stop_record()
        # elif video_camera_state==1:
        #     desk_video_camera.stop_record()
        # elif video_camera_state == 2:
        #     yard_video_camera.stop_record()
        # elif video_camera_state == 3:
        #     corridor_video_camera.stop_record()
        data['state']='stop record'

    print('data')
    print(data)

    return data



def video_stream():
    global room_video_camera,desk_video_camera,yard_video_camera,corridor_video_camera
    global room_global_frame,desk_global_frame,yard_global_frame,corridor_global_frame
    global video_camera_state
    print("video_stream")
    print(video_camera_state,room_video_camera,type(video_camera_state),video_camera_state==0 ,room_video_camera == None,video_camera_state==0 and room_video_camera == None)
    print(video_camera_state)
    if video_camera_state==0 and room_video_camera == None:
        print("v0 rnone")
        room_video_camera = VideoCamera(rtmpsrc1)
        print(room_video_camera)
        print("room——video")
    elif video_camera_state==1 and desk_video_camera == None:
        desk_video_camera = VideoCamera(rtmpsrc2)
    elif video_camera_state==3 and yard_video_camera == None:
        yard_video_camera = VideoCamera(rtmpsrc3)
    elif video_camera_state==4 and corridor_video_camera == None:
        corridor_video_camera = VideoCamera(rtmpsrc4)
    print(room_video_camera)
    frame=None
    global_frame=None
    while True:
        if video_camera_state==0:
            frame = room_video_camera.get_frame()
        elif video_camera_state==1:
            frame = desk_video_camera.get_frame()
        elif video_camera_state==2:
            frame = yard_video_camera.get_frame()
        elif video_camera_state==3:
            frame = corridor_video_camera.get_frame()
        # frame = checkingstrangersandfacialexpression(ret, frame, faceutil,facial_expression_model)
        # ret, jpeg = cv2.imencode('.jpg', frame)
        if frame is not None:
            global_frame = frame
            #global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame
                   + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n'
                   + global_frame + b'\r\n\r\n')


@app.route('/video_viewer',methods=['GET'])
def video_viewer():
    print('video_viewer')
    global video_camera_state
    video_camera_state = int(request.args.get('camera'))
    print(type(video_camera_state))
    #video_camera_state=1
    return Response(video_stream(),mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/sendVideo',methods=['GET'])
# def sendVideo():
#     print('in sendvideo')
#     time.sleep(2)
#     path=request.values.get('path')
#     print(path)
#     return send_file(path)
    # return send_file('/home/reed/Desktop/code/oldcare/tests/test.mp4', as_attachment=True)
def to_json(obj):
    return json.dumps(obj, ensure_ascii=False)
def file_iterator(file_path, chunk_size=512):
    """
        文件读取迭代器
    :param file_path:文件路径
    :param chunk_size: 每次读取流大小
    :return:
    """
    with open(file_path, 'rb') as target_file:
        while True:
            chunk = target_file.read(chunk_size)
            if chunk:
                yield chunk
            else:
                break

@app.route('/sendVideo', methods=['GET'])
def download():
    # file_path = request.values.get('tests/test.mp4')
    file_path='tests/test.mp4'
    if file_path is None:
        return to_json({'success': 0, 'message': '请输入参数'})
    else:
        if file_path == '':
            return to_json({'success': 0, 'message': '请输入正确路径'})
        else:
            if not os.path.isfile(file_path):
                return to_json({'success': 0, 'message': '文件路径不存在'})
            else:
                filename = os.path.basename(file_path)
                response = Response(file_iterator(file_path))
                response.headers['Content-Type'] = 'application/octet-stream'
                response.headers["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
                return response


@app.route('/display/img/<string:filename>', methods=['GET'])
def display_img(filename):
    print(filename)
    base_path = os.path.abspath(os.path.dirname(__file__))
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(base_path + '/faces/' + filename, "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/jpg'
            return response
    else:
        pass

@app.route('/display/event/<string:filename>', methods=['GET'])
def display_event(filename):
    print('in display '+filename)
    base_path = os.path.abspath(os.path.dirname(__file__))
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(base_path +'/supervision/'+ filename, "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/jpg'
            return response
    else:
        pass

def event_happen(data):
    global global_event
    print(data)
    global_event=data
    socketio.emit('eventhappen', json.dumps(data),namespace='/test')

def event_happen2(data):
    print('event2')
    global global_event
    print(data)
    global_event=data
    socketio.emit('eventhappen', json.dumps(data),namespace='/test2')


@socketio.on('my_ping', namespace='/test')
def myping():
    r=redisinit.get_connection()
    event=None
    if 'event' in r:
        js=r.get('event')
    else:
        return
    print(js)
    event=json.loads(js)
    print(event)
    if event!=None:
        emit('eventhappen',json.dumps(event),namespace='/test')
        r.delete('event')

@socketio.on('connect', namespace='/test')
def test_connect():
    data=json.dumps({'data': 'Connected'})
    emit('my response',data ,namespace='/test')
    print("connect successfully!")

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@socketio.on('collectingFace', namespace='/test')
def collecting_face(data):
    print('collectingFace')
    data=json.loads(data)
    print(data)
    id=data['id']
    name=data['name']
    type=data['type']
    idcard=data['id_card']
    collectingfaces(id,idcard)
    with open('/home/reed/Desktop/code/oldcare/info/people_info.csv', "a+", newline='') as file:  # 处理csv读写时不同换行符  linux:\n    windows:\r\n    mac:\r
        csv_file = csv.writer(file)
        datas = [id, name,type]
        csv_file.writerow(datas)
    file.close()


if __name__ == '__main__':
    # desk_video_camera = VideoCamera(rtmpsrc2)
    # room_video_camera = VideoCamera(rtmpsrc1)
    #app.run(host='0.0.0.0', threaded=True, port=5001)
    #
    # yard_video_camera = VideoCamera(rtmpsrc3)
    # corridor_video_camera = VideoCamera(rtmpsrc4)
    print("start")
    socketio.run(app, host='192.168.43.46',port=5001)
