import cv2
import numpy as np
import os

def load_model(w=9, h=18):
    print('\n------------ load model begin ------------')
    file_list = []
    file_list_binary = []
    char_list = 'abcdefghijklmnopqrstuvwxyz1234567890`-=[]\\;\',./ ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?'
    # char_list_binary = 'abcdef1234567890 ~'
    # char_list_binary = 'abcdefghijklmnopqrstuvwxyz1234567890/ ABCDEFGHIJKLMNOPQRSTUVWXYZ~+'   # base64
    char_list_binary = 'abcdefghijklmnopqrstuvwxyz1234567890`-=; ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|<>?' # base85, 包含空格, 共86個字元
    category = len(char_list)
    category_binary = len(char_list_binary)

    print('inference category number :', category)
    print('inference category_binary number :', category_binary)

    for dirPath, dirNames, fileNames in os.walk("training_data_fast/"):
        training_dir = dirPath.replace('\\', '/')
        # print('training_dir:', training_dir)
        for f in fileNames:
            idx = int(training_dir.split('/')[-1])
            if idx in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,42,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,92,93,94] and f == '0000.png':   # 只存 char_list_binary 的那幾個idx, 且不存bold data
                file_list_binary.append(training_dir + '/' + f)
            # print(training_dir + '/' + f, idx)
            file_list.append(training_dir + '/' + f)
        # print('-------------------------')

    data_set_num = int(len(file_list)/category)
    data_set_num_binary = int(len(file_list_binary)/category_binary)
    print('There are {:d} dataset'.format(data_set_num))
    print('There are {:d} dataset_binary'.format(data_set_num_binary))

    img_arr = np.array([cv2.imread(file, cv2.IMREAD_GRAYSCALE).flatten() for file in file_list])
    img_arr = (img_arr / 255).astype('uint8')
    img_arr = np.reshape(img_arr, (data_set_num*category, w*h))

    img_arr_binary = np.array([cv2.imread(file, cv2.IMREAD_GRAYSCALE).flatten() for file in file_list_binary])
    img_arr_binary = (img_arr_binary / 255).astype('uint8')
    img_arr_binary = np.reshape(img_arr_binary, (data_set_num_binary*category_binary, w*h))

    # img_arr = np.array([], dtype='uint8')
    # img_arr_binary = np.array([], dtype='uint8')

    # for file in file_list:
    #     img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    #     img = (img/255).astype('uint8')
    #     img = img.flatten()
    #     img_arr = np.append(img_arr, img)
    
    # for file in file_list_binary:
    #     img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    #     img = (img/255).astype('uint8')
    #     img = img.flatten()
    #     img_arr_binary = np.append(img_arr_binary, img)

    # img_arr = np.reshape(img_arr, (data_set_num*category, w*h))
    # img_arr_binary = np.reshape(img_arr_binary, (data_set_num_binary*category_binary, w*h))

    print('img_arr.shape (data_set_num*category, each image w*h) :', img_arr.shape)
    print('img_arr_binary.shape (data_set_num_binary*category_binary, each image w*h) :', img_arr_binary.shape)
    print('------------ model successfully loaded ------------\n')
    return char_list, data_set_num, category, img_arr, char_list_binary, data_set_num_binary, category_binary, img_arr_binary

