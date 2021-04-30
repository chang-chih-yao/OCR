import time
from datetime import datetime
import configparser
import numpy as np
import os
import shutil
import cv2
import sys
from filecmp import cmp
from PIL import Image
from PIL import ImageGrab
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput import keyboard
import pynput
import win32gui

from script.gen_dataset_fast import gen_data
from script.gen_training_data_fast import gen_train
from script.load_model import load_model
from script.cfg import load_cfg, build_cfg, modify_cfg

def on_press(key):
    global exit_flag
    if key == Key.backspace:
        print('exit()')
        exit_flag = 1
        return False

def my_type(my_str = ''):
    no_shift_char = "abcdefghijklmnopqrstuvwxyz0123456789`-=[]\\;',./"      # 47 chars
    shift_char    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?'       # 47 chars
    if(my_str != ''):
        if exit_flag == 1:
            exit()
        if (my_str == ' '):
            my_keyboard.type(' ')
            time.sleep(type_speed)
            return
        elif (my_str == 'pagedown_key'):
            my_keyboard.press(Key.ctrl)
            my_keyboard.press('f')
            my_keyboard.release('f')
            my_keyboard.release(Key.ctrl)
            time.sleep(cmd_speed)
            return
        elif (my_str == 'enter_key'):
            my_keyboard.press(Key.enter)
            my_keyboard.release(Key.enter)
            time.sleep(cmd_speed)
            return
        
        for i in range(len(my_str)):
            if exit_flag == 1:
                exit()
            if my_str[i] in shift_char:
                my_keyboard.press(Key.shift)
                my_keyboard.type(no_shift_char[shift_char.find(my_str[i])])
                my_keyboard.release(Key.shift)
                time.sleep(type_speed)
            else:
                my_keyboard.type(my_str[i])
                time.sleep(type_speed)

def mouse_click():
    my_mouse.position = ((x1+x2)//2, (y1+y2)//2)
    time.sleep(cmd_speed)
    my_mouse.click(Button.left)
    time.sleep(type_speed)

def open_vim(my_str='', recursive_mode=False):
    if my_str != '':
        if not recursive_mode:
            my_type('vim -u NONE -R ' + my_str)
        else:
            my_type('vim -u NONE ' + my_str)
        my_type('enter_key')
        my_type(':set nu')
        my_type('enter_key')
        # my_type(':1')
        # my_type('enter_key')
        time.sleep(0.5)

def quit_vim():
    my_keyboard.press(Key.esc)
    my_keyboard.release(Key.esc)
    time.sleep(type_speed)
    my_type(':q!')
    time.sleep(type_speed)
    my_type('enter_key')
    time.sleep(cmd_speed)

def screen(x1, y1, x2, y2, threshold=1):
    print(x1, y1, x2, y2)
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    ret, th1 = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
    return th1

def infer(vertical_num, horizontal_num, th1, file_eof, line_cou, vim_mode=True):
    global log_cou, wait_correct_num
    temp_s = ''
    x_start = w*0
    y_start = h*0

    y = y_start
    space_cou = 0
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


def detect_nx():
    hWndList = []
    win32gui.EnumWindows(lambda hWnd,param: param.append(hWnd),hWndList)
    for hwnd in hWndList:
        title = win32gui.GetWindowText(hwnd)
        # print(title)
        if (title.find('NoMachine') != -1):
            print('find NoMachine')
            left,top,right,bottom = win32gui.GetWindowRect(hwnd)
            # print(title)
            # print(left, top, right, bottom)
            win32gui.ShowWindow(hwnd,5)
            win32gui.SetForegroundWindow(hwnd)
            return right
    return -999


nx_handle = detect_nx()
another_monitor = False
if nx_handle == -999:
    print('not found NoMachine!!!')
elif nx_handle > 2000:
    another_monitor = True
    print('nx in another monitor')

# --------------------------- load cfg and model ------------------------ #
config = load_cfg()
# for key in config['cust']:
#     print(key, config['cust'][key])
difference = int(config['cust']['difference'])
if config['cust']['build_model'] == '0':          # no model inside your directory
    temp_img = cv2.imread('gen_dataset.png', cv2.IMREAD_GRAYSCALE)
    gen_data(temp_img, difference=2, img_from_png=True)
    gen_train()
    modify_cfg('build_model', 1)
char_list, difference, category, img_arr = load_model(difference)
# --------------------------- load cfg and model ------------------------ #

my_keyboard = pynput.keyboard.Controller()
my_mouse = pynput.mouse.Controller()

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

type_speed = float(config['cust']['type_speed'])
cmd_speed = float(config['cust']['cmd_speed'])

wait_correct_num = 0  # flag
log_flag = 0          # flag : log on -> log_flag = 1
log_cou = 0

file_name = 'calibration.txt'
export_file_root = 'export/'

exit_flag = 0
listener = keyboard.Listener(on_press=on_press)
listener.start()

print('---------------------------')
print('3')
time.sleep(1)
print('2')
time.sleep(1)
print('1')
time.sleep(1)
print('Start')

mouse_click()
open_vim('calibration.txt')

template = cv2.imread('template.png', cv2.IMREAD_GRAYSCALE)
img_gray = screen(x1, y1, x2, y2)
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



img = screen(x1, y1, x2, y2)
temp_str, file_eof_, line_cou_ = infer(1, len(char_list) + vim_text_bias_width, img, 0, 1)
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

    img = screen(x1, y1, x2, y2)
    temp_str, file_eof_, line_cou_ = infer(1, len(char_list) + vim_text_bias_width, img, 0, 1)
    print(temp_str)
    if temp_str == 'abcdefghijklmnopqrstuvwxyz1234567890`-=[]\\;\',./ ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?':
        print('char list correct')
    else:
        print('Error !!!!')
        quit_vim()
        exit()

mouse_click()

img = screen(x1, y1, x2, y2)
temp_str, file_eof_, line_cou_ = infer(9, len(char_list) + vim_text_bias_width, img, 0, 1)
a_len = len(temp_str.split('\n')[-1])                       # the number of 'a': len(char_list) + extra 'a's below(int(a_len) - len(char_list))
x2 = x1 + (219 - (int(a_len) - len(char_list))) * w         # line 8 in calibration.txt, there are 211 'a's
print('x2 : ' + str(x2))


img = screen(x1, y1, x2, y2)
file_eof = 0
line_cou = 1
temp_str, file_eof, line_cou = infer(y2//h, (x2-x1)//w, img, file_eof, line_cou)
# print(temp_str)
y2 = y1 + (line_cou - 1) * h
print('\ny2 : ' + str(y2))
quit_vim()


#------------------------- check and compare export file ---------------------------#
now = datetime.now()
export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
os.mkdir(export_dir_name)

f = open(export_dir_name + file_name, 'w')
open_vim(file_name)
file_eof = 0
line_cou = 1
while(file_eof == 0):
    img = screen(x1, y1, x2, y2)
    temp_str, file_eof, line_cou = infer((y2-y1)//h, (x2-x1)//w, img, file_eof, line_cou)
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
