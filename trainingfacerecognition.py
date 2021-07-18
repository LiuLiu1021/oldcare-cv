# -*- coding: utf-8 -*-

'''
训练人脸识别模型-默认使用hog，判断是谁

用法：
python /home/reed/Desktop/code/oldcare/trainingfacerecognition.py
'''


# import the necessary packages
from imutils import paths
from oldcare.facial import FaceUtil

# global variable
dataset_path = '/home/reed/Desktop/code/oldcare/images/capturefaces'
output_encoding_file_path = '/home/reed/Desktop/code/oldcare/models/face_hog.pickle'
# 把模型文件保存到硬盘中。保存路径为models/face_hog.pickle

# grab the paths to the input images in our dataset
print("[INFO] quantifying faces...")
image_paths = list(paths.list_images(dataset_path))# 列出文件名，装入List

if len(image_paths) == 0:
    print('[ERROR] no images to train.')
else:
    faceutil = FaceUtil()
    print("[INFO] training face embeddings...")
    faceutil.save_embeddings(image_paths, output_encoding_file_path)

