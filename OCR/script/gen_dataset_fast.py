import numpy as np
import cv2
import os
import shutil

def gen_data(img, difference=2, img_from_png=False, threshold_step=5, char_len=95):
    print('start gen dataset')
    
    width = 9     # every char on your monitor has same size
    height = 18   # every char on your monitor has same size

    dataset_dir = 'dataset_fast/'

    print(img.shape)

    if(os.path.isdir(dataset_dir)):
        shutil.rmtree(dataset_dir)
    os.mkdir(dataset_dir)

    for i in range(difference):
        os.mkdir(dataset_dir + 'binary_data_' + str(i*threshold_step+1) + '/')
        os.mkdir(dataset_dir + 'binary_data_' + str(i*threshold_step+1) + '/' + 'fast/')
        
        ret, th1 = cv2.threshold(img, i*threshold_step+1, 255, cv2.THRESH_BINARY)
        if img_from_png:
            x = width*4
        else:
            x = width*8
        y = height*0
        
        for j in range(char_len):
            crop_img = th1[y:y+height, x:x+width]
            cv2.imwrite('{:s}binary_data_{:d}/fast/{:04d}.png'.format(dataset_dir, i*threshold_step+1, j), crop_img)
            # cv2.imshow('reSize2', crop_img)
            # cv2.waitKey()
            x += width

    # cv2.destroyAllWindows()
    print('gen dataset finish')

if __name__ == '__main__':
    temp_img = cv2.imread('../gen_dataset.png', cv2.IMREAD_GRAYSCALE)
    gen_data(temp_img, difference=2, img_from_png=True)