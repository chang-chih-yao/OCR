import time
from datetime import datetime
import numpy as np
import os
import cv2
import sys
from filecmp import cmp, dircmp
from PIL import ImageGrab
import matplotlib.pyplot as plt

from script.gen_dataset_fast import gen_data
from script.gen_dataset_fast import gen_data
from script.gen_training_data_fast import gen_train
from script.load_model import load_model
from script.cfg import build_cfg, load_cfg, modify_cfg
from script.windows_api import detect_nx, message_box
from script.keyboard_mouse_ctrl import my_type, mouse_click, open_vim, quit_vim
from script.inference_core import Inference

def same_dirs(a, b):
    """Check that structure and files are the same for directories a and b

    Args:
        a (str): The path to the first directory
        b (str): The path to the second directory
    """
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

def recursive_vim():
    my_type("find . | grep '[.][/][^.]' > ~/aaa.tmp")
    my_type('enter_key')
    while True:
        img = my_infer.screen(x1, y1, x2, y2 + 2*h)
        terminal_str, file_eof_, line_cou_ = my_infer.infer(vertical_num + 2, horizontal_num, img, 0, 1, vim_mode=False)
        # print('[-5]|' + terminal_str.split('\n')[-5] + '|')
        # print('[-4]|' + terminal_str.split('\n')[-4] + '|')
        # print('[-3]|' + terminal_str.split('\n')[-3] + '|')
        # print('[-2]|' + terminal_str.split('\n')[-2] + '|')
        if terminal_str.split('\n')[-2] == '':
            print('wait aaa.tmp...')
            time.sleep(1)
        else:
            break
    if terminal_str.split('\n')[-3].find('Permission denied') >= 0:
        print('Permission denied !!!')
        print('please cp -r this_dir/ to your dir')
        exit()
    
    open_vim('~/aaa.tmp', recursive_mode=True)
    my_type(':%s/\\.\\///g')
    my_type('enter_key')
    my_type(':g/aaa.tmp/d')
    my_type('enter_key')
    my_type(':g/\\/\\./d')
    my_type('enter_key')
    my_type(':1')
    my_type('enter_key')

def single_file_mode(name):
    file_name = name
    f = open(export_dir_name + file_name, 'w')
    open_vim(file_name)

    file_eof = 0
    line_cou = 1
    while(file_eof == 0):
        img = my_infer.screen(x1, y1, x2, y2)
        temp_str, file_eof, line_cou = my_infer.infer(vertical_num, horizontal_num, img, file_eof, line_cou)
        f.write(temp_str)
        my_type('pagedown_key')

    quit_vim()
    f.close()
'''
def screen(x1, y1, x2, y2, threshold=1):
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    ret, th1 = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
    return th1

def infer(vertical_num, horizontal_num, th1, file_eof, line_cou, vim_mode=True, draw_plot=False):
    global log_cou, wait_correct_num
    temp_s = ''
    x_start = w*0
    y_start = h*0

    y = y_start
    space_cou = 0

    if draw_plot:
        char_np_arr = np.array(list(char_list))
        temp_y_arr = np.random.randint(100, size=(95))
        plt.ion()
        fig = plt.figure()
        fig.set_size_inches(14, 8)
        ax = fig.add_subplot()
        line1, = ax.plot(char_np_arr, temp_y_arr)
        fig.canvas.draw()
        fig.canvas.flush_events()

    for i in range(vertical_num):
        x = x_start
        front_str = ''
        for j in range(horizontal_num):
            crop_img = th1[y:y+h, x:x+w]
            if crop_img.shape[0] != h or crop_img.shape[1] != w:
                return temp_s, file_eof, line_cou
            if (np.all((crop_img.flatten() == 0)) or np.all((crop_img.flatten() == 255))):   # skip space image
                result = 47                                                                  # char_list[47] == ' '
            else:
                mid = crop_img.copy()
                if (log_flag):
                    cv2.imwrite('log/{:04d}.png'.format(log_cou), mid)
                    log_cou += 1
                # cv2.imshow('mid', mid)
                # cv2.waitKey()
                mid = (mid/255).astype('int8')
                mid = mid.flatten()
                result_arr = np.absolute(img_arr - mid)
                result_sum = np.sum(result_arr, axis=1)                                      # (difference*category,)   int32
                result = np.argmin(result_sum) // difference
                if draw_plot:
                    line1.set_ydata(result_sum[::2])
                    fig.canvas.draw()
                    time.sleep(0.5)
                    fig.canvas.flush_events()

                #print(result, char_list[result])
            if j < vim_text_bias_width and vim_mode:
                front_str += char_list[result]
                if j == 7:
                    # print('|'+front_str+'|')
                    if front_str.replace(' ', '').isdigit():
                        # print(line_cou)
                        if front_str == '{:>7d} '.format(line_cou):
                            space_cou = 0
                            if wait_correct_num == 1:
                                wait_correct_num = 0
                            if line_cou != 1:
                                temp_s += '\n'
                        else:
                            wait_correct_num = 1
                            line_cou -= 1
                            # print('skip this line')
                            break
                    elif front_str == '@       ':
                        # print('\n', end='')
                        # print('line not complete')
                        return temp_s, file_eof, line_cou
                    elif front_str == '~       ':
                        print('\n', end='')
                        print('file end')
                        file_eof = 1
                        return temp_s, file_eof, line_cou
                    else:
                        line_cou -= 1
                        if wait_correct_num == 1:
                            break
                        # print('more than 1 line')
                        if space_cou == 0:
                            temp_s += front_str
                        else:
                            for t in range(space_cou):
                                temp_s += ' '
                            temp_s += front_str
                            space_cou = 0
            else:
                if(char_list[result] == ' '):
                    space_cou += 1
                else:
                    if(space_cou == 0):
                        temp_s += char_list[result]
                    else:
                        for t in range(space_cou):
                            temp_s += ' '
                        temp_s += char_list[result]
                        space_cou = 0
            x += w
        y += h
        line_cou += 1
        if not vim_mode:
            space_cou = 0
            temp_s += '\n'
        print('\r[{:>5d}/{:<5d}]'.format(i+1, vertical_num), end='')
        sys.stdout.flush()
    print('\n', end='')
    return temp_s, file_eof, line_cou
'''

# --------------------------- detect nx ------------------------ #
hwnd, is_nx_active, another_monitor = detect_nx()
if is_nx_active == False:
    print('not found NoMachine')
    exit()

# --------------------------- load cfg  ------------------------ #
config = load_cfg()
# for key in config['cust']:
#     print(key, config['cust'][key])
difference = int(config['cust']['difference'])

# --------------------------- create and load model ------------------------ #
if config['cust']['build_model'] == '0':          # no model inside your directory
    temp_img = cv2.imread('gen_dataset.png', cv2.IMREAD_GRAYSCALE)
    gen_data(temp_img, difference=2, img_from_png=True)
    gen_train()
    modify_cfg('build_model', 1)
char_list, difference, category, img_arr = load_model(difference)

# 1080p monitor size
x1 = int(config['DEFAULT']['x1'])
y1 = int(config['DEFAULT']['y1'])
x2 = int(config['DEFAULT']['x2'])
y2 = int(config['DEFAULT']['y2'])
if another_monitor:
    x1 += 1920
    x2 += 1920

# one char size
w = 9
h = 18

vim_text_bias_width = 8         # There are 8 chars(w*8 pixels) in front of the text after you use vim -u NONE open file and :set nu

vertical_num = (y2 - y1) // h
horizontal_num = (x2 - x1) // w

wait_correct_num = 0  # flag
log_flag = 0          # flag : log on -> log_flag = 1
log_cou = 0

file_name = 'calibration.txt'
export_file_root = 'export/'

my_infer = Inference(char_list, difference, img_arr, w, h, vim_text_bias_width, log_flag)

print('---------------------------')
print('3')
time.sleep(1)
print('2')
time.sleep(1)
print('1')
time.sleep(1)
print('Start')

mouse_click((x1+x2)//2, (y1+y2)//2)
open_vim('calibration.txt')

template = cv2.imread('template.png', cv2.IMREAD_GRAYSCALE)
img_gray = my_infer.screen(x1, y1, x2, y2)
print(img_gray.shape)
res = cv2.matchTemplate(img_gray, template, cv2.TM_SQDIFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
print('min_loc : ' + str(min_loc))
x1 = min_loc[0]-68
y1 = min_loc[1]-18
if another_monitor:
    x1 += 1920
print('x1 : ' + str(x1))
print('y1 : ' + str(y1))

# top_left = min_loc
# bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
# cv2.rectangle(img_gray, top_left, bottom_right, 255, 2)
# cv2.imshow("img", img_gray)
# cv2.waitKey()
# cv2.destroyAllWindows()
# time.sleep(1)
# mouse_click()



img = my_infer.screen(x1, y1, x2, y2)
temp_str, file_eof_, line_cou_ = my_infer.infer(1, len(char_list) + vim_text_bias_width, img, 0, 1, draw_plot=False)
print('detect :|' + temp_str + '|')
if temp_str == 'abcdefghijklmnopqrstuvwxyz1234567890`-=[]\\;\',./ ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?':
    print('char list correct')
else:
    my_type(':8')
    my_type('enter_key')
    print('need to build new model')
    # cv2.imshow("img", img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # time.sleep(1)
    gen_data(img, difference=2)
    gen_train()
    char_list, difference, category, img_arr = load_model(difference=2)
    modify_cfg('difference', difference)

    img = my_infer.screen(x1, y1, x2, y2)
    temp_str, file_eof_, line_cou_ = my_infer.infer(1, len(char_list) + vim_text_bias_width, img, 0, 1)
    print(temp_str)
    if temp_str == 'abcdefghijklmnopqrstuvwxyz1234567890`-=[]\\;\',./ ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?':
        print('char list correct')
    else:
        print('Error !!!!')
        quit_vim()
        exit()

mouse_click((x1+x2)//2, (y1+y2)//2)

img = my_infer.screen(x1, y1, x2, y2)
temp_str, file_eof_, line_cou_ = my_infer.infer(9, len(char_list) + vim_text_bias_width, img, 0, 1)
a_len = len(temp_str.split('\n')[-1])                       # the number of 'a': len(char_list) + extra 'a's below(int(a_len) - len(char_list))
x2 = x1 + (219 - (int(a_len) - len(char_list))) * w         # line 8 in calibration.txt, there are 211 'a's
print('x2 : ' + str(x2))


img = my_infer.screen(x1, y1, x2, y2)
file_eof = 0
line_cou = 1
temp_str, file_eof, line_cou = my_infer.infer(y2//h, (x2-x1)//w, img, file_eof, line_cou)
# print(temp_str)
y2 = y1 + (line_cou - 1) * h
print('\ny2 : ' + str(y2))
quit_vim()


#------------------------- check and compare export file ---------------------------#
vertical_num = (y2 - y1) // h
horizontal_num = (x2 - x1) // w
now = datetime.now()
export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
os.mkdir(export_dir_name)

f = open(export_dir_name + file_name, 'w')
open_vim(file_name)
file_eof = 0
line_cou = 1
while(file_eof == 0):
    img = my_infer.screen(x1, y1, x2, y2)
    temp_str, file_eof, line_cou = my_infer.infer((y2-y1)//h, (x2-x1)//w, img, file_eof, line_cou)
    f.write(temp_str)
    my_type('pagedown_key')
f.close()
quit_vim()

if cmp('compare_file/calibration.txt', export_dir_name + file_name):
    modify_cfg('x1', x1)
    modify_cfg('y1', y1)
    modify_cfg('x2', x2)
    modify_cfg('y2', y2)
    print('----------------')
    print('success !!!!')
    print('now you can use inference_fast.py script')
else:
    print('----------------')
    print('fail !!!!!!!')
    exit()

if message_box(hwnd, 'recursive test?') == 1:
    if os.path.isdir('compare_file/test2/'):
        pass
    else:
        os.mkdir('compare_file/test2/')
    recursive_vim()
    dir_str = ''
    file_eof = 0
    line_cou = 1
    while(file_eof == 0):
        img = my_infer.screen(x1, y1, x2, y2)
        temp_str, file_eof, line_cou = my_infer.infer(vertical_num, horizontal_num, img, file_eof, line_cou)
        dir_str += temp_str
        my_type('pagedown_key')
    # print(dir_str)
    quit_vim()
    my_type('rm -f ~/aaa.tmp')
    my_type('enter_key')

    dir_arr = dir_str.split('\n')
    if len(dir_arr) > 50:
        print('detect {:d} files in this directory, continue !!!???(y/n) '.format(len(dir_arr)), end='')
        y_or_n = input()
        if y_or_n != 'y' and y_or_n != 'Y':
            print('end program')
            exit()

    print(dir_arr)
    mouse_click((x1+x2)//2, (y1+y2)//2)

    for item in dir_arr:
        my_type('wc -l < ' + item)
        my_type('enter_key')
        img = my_infer.screen(x1, y1, x2, y2 + 2*h)
        terminal_str, file_eof_, line_cou_ = my_infer.infer(vertical_num + 2, horizontal_num, img, 0, 1, vim_mode=False)
        # print('[-5]|' + terminal_str.split('\n')[-5] + '|')
        # print('[-4]|' + terminal_str.split('\n')[-4] + '|')
        # print('[-3]|' + terminal_str.split('\n')[-3] + '|')
        # print('[-2]|' + terminal_str.split('\n')[-2] + '|')
        if (terminal_str.split('\n')[-3] == '0'):
            if (terminal_str.split('\n')[-4].find('Is a directory') >= 0):
                os.mkdir(export_dir_name + item + '/')
                print('build dir')
            else:
                f = open(export_dir_name + item, 'w')
                f.close()
                print('it is empty file')
        else:
            print(int(terminal_str.split('\n')[-3]))
            single_file_mode(item)
    
    print('recursive DONE')
    if same_dirs('compare_file/', export_dir_name):
        print('recursive test success')
    else:
        print('recursive test error!!')


