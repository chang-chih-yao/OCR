import numpy as np
import os
import shutil

def gen_train(training_dir='training_data_fast/', dataset_dir='dataset_fast/'):
    print('start gen training data')

    if(os.path.isdir(training_dir)):
        shutil.rmtree(training_dir)
    os.mkdir(training_dir)

    for i in range(95):
        os.mkdir('{:s}{:04d}/'.format(training_dir, i))

    for dirPath, dirNames, fileNames in os.walk(dataset_dir):
        dataset_dir = dirPath.replace('\\', '/')
        # print(dataset_dir)
        # print(fileNames)
        for f in fileNames:
            # print(dataset_dir + '/' + f)
            num_str = f.split('.')[0]
            num_int = int(f.split('.')[0])
            shutil.copyfile(dataset_dir + '/' + f, '{:s}{:04d}/'.format(training_dir, int(num_str)) + '{:04d}.png'.format(len(os.listdir('{:s}{:04d}/'.format(training_dir, int(num_str))))))
    
    print('gen training data finish')

if __name__ == '__main__':
    gen_train(training_dir='../training_data_fast/', dataset_dir='../dataset_fast/')