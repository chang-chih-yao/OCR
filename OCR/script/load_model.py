import cv2
import numpy as np
import os

def load_model():
    print('\n------------ load model begin ------------')
    file_list = []
    char_list = 'abcdefghijklmnopqrstuvwxyz1234567890`-=[]\\;\',./ ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?'
    category = len(char_list)

    print('inference category number :', category)

    for dirPath, dirNames, fileNames in os.walk("training_data_fast/"):
        training_dir = dirPath.replace('\\', '/')
        for f in fileNames:
            file_list.append(training_dir + '/' + f)

    data_set_num = int(len(file_list)/category)
    print('There are {:d} dataset'.format(data_set_num))

    img_arr = np.array([], dtype='int8')

    for data in file_list:
        img = cv2.imread(data, cv2.IMREAD_GRAYSCALE)
        img = (img/255).astype('int8')
        img = img.flatten()
        img_arr = np.append(img_arr, img)

    img_arr = np.reshape(img_arr, (data_set_num*category, 18*9))
    print('img_arr.shape :', img_arr.shape)
    print('------------ model successfully loaded ------------\n')
    return char_list, data_set_num, category, img_arr