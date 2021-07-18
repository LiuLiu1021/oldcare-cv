import types
from math import sqrt

from AipBodyAnalysis import client

""" 读取图片 """
# python /home/reed/Desktop/code/oldcare/testfall.py

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


image = get_file_content('/home/reed/Desktop/code/oldcare/tests/Home_01_36.jpg')


def dict_get(dict, objkey, default):
    tmp = dict
    for k, v in tmp.items():
        if k == objkey:
            return v
        else:
            if type(v) is types.DictType:
                ret = dict_get(v, objkey, default)
                if ret is not default:
                    return ret
    return default


""" 调用人体关键点识别 """
msg = client.bodyAnalysis(image)

print(msg)

print("------------------------------------------")

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

cos_body = (center_hip_y - neck_y) / sqrt((neck_x - center_hip_x)**2 + (neck_y - center_hip_y)**2)

print("---------")
if cos_body > 0.7:
    print("正常")
else:
    print("摔倒")
