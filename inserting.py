'''
将事件插入数据库主程序

用法：

'''

import json
import datetime

import requests
import startingcameraservice
import redisinit
from recordaudio import record
import threading as t
from SMS import sendSMS
from aliasr import getASR
from PIL import Image, ImageDraw, ImageFont
import cv2

def add_event(data):
    url = 'http://121.196.111.9:5000/secs/addEvent'
    r=requests.post(url,data=data)

    r.encoding='utf-8'
    if r.status_code==200:
        print("11111")
        return True
    else:
        return False


#eventtype:1:老人笑；2：摔倒；3：陌生人出现；4：禁区闯入；5：义工和老人交互
def insert(event_desc,event_type,event_location,path,old_people_id=None,now_time=None,ospath=None,frame=None):
    global backendws,frontendws

    f = open('/home/reed/Desktop/code/oldcare/allowinsertdatabase.txt','r')
    content = f.read()
    f.close()
    allow = content[11:12]
    print("allow:"+allow)

    if allow == '1': # 如果允许插入

        f = open('/home/reed/Desktop/code/oldcare/allowinsertdatabase.txt','w')
        f.write('is_allowed=0')
        f.close()

        print('准备插入数据库')

        event_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        mes = {'event_desc':event_desc,
               'event_type':event_type,
               'event_date':event_date,
               'event_location':event_location,
               'oldperson_id':old_people_id,
               'img_dir':path}

        
        # startingcameraservice.event_happen(mes)
        # startingcameraservice.event_happen2(mes)
        
        if event_type==3:
            sendSMS(event_date+","+event_desc,'13520782708')
            # t1 = t.Thread(target=record,args=("/home/reed/Desktop/code/oldcare/audio/strangers_%s.wav"%now_time,))
            # t1.start()
            # t1.join()
            # text=getASR("/home/reed/Desktop/code/oldcare/audio/strangers_%s.wav"%now_time)
            # img_PIL = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
            # draw = ImageDraw.Draw(img_PIL)
            # draw.text((20, 400), text,font=ImageFont.truetype('NotoSansCJK-Black.ttc',40),fill=(255, 0, 0))
            # frame = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
            # cv2.imwrite(ospath, frame)
        
        add_event(mes)
        r=redisinit.get_connection()
        r.set('event',json.dumps(mes))
        print(r.get('event'))
        print('插入成功')
    else:
        print('just pass')
