import time
from datetime import datetime
import numpy as np
import os
import cv2
import sys
from filecmp import cmp, dircmp

from script.gen_dataset_fast import gen_data
from script.gen_training_data_fast import gen_train
from script.load_model import load_model
from script.cfg import build_cfg, load_cfg, modify_cfg
from script.windows_api import message_box
from script.keyboard_mouse_ctrl import my_type, mouse_click, open_vim, quit_vim
from script.inference_core import Inference

def same_dirs(a, b):
    '''Check that structure and files are the same for directories a and b
    Args:
        a (str): The path to the first directory
        b (str): The path to the second directory
    '''
    comp = dircmp(a, b)
    common = sorted(comp.common)
    left = sorted(comp.left_list)
    right = sorted(comp.right_list)
    if left != common or right != common:
        return False
    if len(comp.diff_files):
        return False
    for subdir in comp.common_dirs:
        left_subdir = os.path.join(a, subdir)
        right_subdir = os.path.join(b, subdir)
        return same_dirs(left_subdir, right_subdir)
    return True 


my_infer = Inference(calibration=True)
my_config = load_cfg()

target_name = 'calibration.txt'
export_file_root = 'export/'

if os.path.isdir(export_file_root):
    pass
else:
    os.mkdir(export_file_root)

print('---------------------------')
print('Start')
print('---------------------------')

my_infer.active_nx()
open_vim(target_name)

template = cv2.imread('template.png', cv2.IMREAD_GRAYSCALE)
img_gray = my_infer.screen()
print(img_gray.shape)
res = cv2.matchTemplate(img_gray, template, cv2.TM_SQDIFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
print('min_loc : ' + str(min_loc))
my_infer.x1 = min_loc[0]-68
my_infer.y1 = min_loc[1]-18
if my_infer.another_monitor:
    my_infer.x1 += 1920
print('x1 : ' + str(my_infer.x1))
print('y1 : ' + str(my_infer.y1))

# top_left = min_loc
# bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
# cv2.rectangle(img_gray, top_left, bottom_right, 255, 2)
# cv2.imshow("img", img_gray)
# cv2.waitKey()
# time.sleep(1)
# my_infer.active_nx()



img = my_infer.screen()
# cv2.imshow("img", img)
# cv2.waitKey()
# exit()
temp_str = my_infer.infer(img, vertical_num=1, horizontal_num=len(my_infer.char_list) + my_infer.vim_text_bias_width)[0]
print('detect :|' + temp_str + '|')
input_choise = ''
if temp_str == my_infer.char_list:
    print('char list correct')
    print('do you want build new model? (y/n)', end='')
    input_choise = input()
else:
    input_choise = 'y'

if (input_choise == 'y' or 'Y'):
    print('need to build new model')
    # cv2.imshow("img", img)
    # cv2.waitKey()
    # time.sleep(1)
    threshold = int(my_config['cust']['threshold'])
    gen_data(img, difference=2, threshold=threshold)
    gen_train()
    my_infer.char_list, my_infer.difference, my_infer.category, my_infer.img_arr = load_model(difference=2)
    modify_cfg('difference', my_infer.difference)

    img = my_infer.screen()
    temp_str = my_infer.infer(img, vertical_num=1, horizontal_num=len(my_infer.char_list) + my_infer.vim_text_bias_width)[0]
    print('detect :|' + temp_str + '|')
    if temp_str == my_infer.char_list:
        print('char list correct')
    else:
        print('Error !!!!')
        quit_vim()
        exit()


my_infer.active_nx()

img = my_infer.screen()
temp_str = my_infer.infer(img, vertical_num=9, horizontal_num=len(my_infer.char_list) + my_infer.vim_text_bias_width)[0]
print(temp_str)
a_len = len(temp_str.split('\n')[-1])                       # the number of 'a': len(char_list) + extra 'a's below(int(a_len) - len(char_list))
my_infer.x2 = my_infer.x1 + (219 - (int(a_len) - len(my_infer.char_list))) * my_infer.w         # line 8 in calibration.txt, there are 211 'a's
print('x2 : ' + str(my_infer.x2))


img = my_infer.screen()
temp_str, file_eof, line_cou = my_infer.infer(img, vertical_num=my_infer.y2//my_infer.h, horizontal_num=(my_infer.x2-my_infer.x1)//my_infer.w)
print(temp_str)
my_infer.y2 = my_infer.y1 + (line_cou - 1) * my_infer.h
print('\ny2 : ' + str(my_infer.y2))

my_infer.vertical_and_horizontal_num_update()
quit_vim()


#------------------------- check and compare export file ---------------------------#
now = datetime.now()
export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
os.mkdir(export_dir_name)

temp_str = my_infer.single_file_mode(target_name)
my_infer.write_in_file(export_dir_name, target_name, temp_str)

if cmp('compare_file/calibration.txt', export_dir_name + target_name):
    modify_cfg('x1', my_infer.x1)
    modify_cfg('y1', my_infer.y1)
    modify_cfg('x2', my_infer.x2)
    modify_cfg('y2', my_infer.y2)
    print('----------------')
    print('PASS !!!!')
    print('now you can use inference_fast.py script')
else:
    print('----------------')
    print('FAIL !!!!!!!')
    exit()

if message_box(my_infer.hwnd, 'Single file test success!\n Do you want continue for recursive test?') == 1:
    if os.path.isdir('compare_file/test2/'):
        pass
    else:
        os.mkdir('compare_file/test2/')
    
    my_infer.recursive_mode(export_dir_name)

    if same_dirs('compare_file/', export_dir_name):
        print('recursive test success')
    else:
        print('recursive test error!!')
        exit()

