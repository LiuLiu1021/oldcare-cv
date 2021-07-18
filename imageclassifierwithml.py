# -*- coding: utf-8 -*-

'''
image classification with knn，不保存模型，只是输出准确率和损失

'''

from oldcare.preprocessing import SimplePreprocessor 
from oldcare.datasets import SimpleDatasetLoader
from imutils import paths
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report


################################################3
# 第一部分：数据预处理

# 全局变量，之前收集的图片位置，将这里的图片进行模型训练和预测
dataset_path = '/home/reed/Desktop/code/oldcare/images/capturefaces'

# 全局常量
N_NEIGHBOURS = 5 # K近邻的邻居数量
TARGET_IMAGE_WIDTH = 32 # 重置图片大小
TARGET_IMAGE_HEIGHT = 32

# initialize the image preprocessor and datasetloader
sp = SimplePreprocessor(TARGET_IMAGE_WIDTH, TARGET_IMAGE_HEIGHT)
sdl = SimpleDatasetLoader(preprocessors=[sp])

# Load images
print("[INFO] loading images...")
image_paths = list(paths.list_images(dataset_path)) # path included
(X, y) = sdl.load(image_paths, verbose=500, grayscale = True)# X对应图片，y对应标签

# Flatten (reshape the data matrix)
# convert from (13164,32,32) into (13164,32*32)
X = X.reshape((X.shape[0], TARGET_IMAGE_WIDTH*TARGET_IMAGE_HEIGHT)) 

# Show some information on memory consumption of the images
print("[INFO] features matrix: {:.1f}MB".format(X.nbytes / (1024 * 1024.0)))

# Label encoder
le = LabelEncoder()
y = le.fit_transform(y)

# Split dataset
(X_train, X_test, y_train, y_test) = train_test_split(X, y, test_size=0.25, random_state=42)
# X_train,X_test, y_train, y_test =sklearn.model_selection.train_test_split(train_data,
# train_target,test_size=0.4, random_state=0,stratify=y_train)
# train_data：所要划分的样本特征集-图片
# train_target：所要划分的样本结果-标签
# test_size：样本占比，如果是整数的话就是样本的数量
# random_state：是随机数的种子。其实就是该组随机数的编号，在需要重复试验的时候，保证得到一组一样的随机数。
# 其中test_size：可以为浮点、整数或None，默认为None
# ①若为浮点时，表示测试集占总样本的百分比
# ②若为整数时，表示测试样本样本数
# ③若为None时，test size自动设置成0.25


################################################3
# 第二部分：训练模型

# Train model
print("[INFO] evaluating k-NN classifier...")
# 使用KNN模型
model = KNeighborsClassifier(n_neighbors= N_NEIGHBOURS,metric = 'minkowski', p = 2)
# metric ： 字符串或可调用，默认为’minkowski’。用于距离度量，默认度量是minkowski，也就是p=2的欧氏距离(欧几里德度量)
model.fit(X_train, y_train)# 传入训练集，开始训练


################################################
# 第三部分：评估模型

# Evaluate model
y_pred = model.predict(X_test)# 传入测试集，获得预测结果
# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)# 混淆矩阵，传入预测结果和正确结果，进行比较
print(cm)
# Report
print(classification_report(y_test, y_pred, target_names=le.classes_))# 在终端输出结果数据
