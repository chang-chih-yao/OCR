import time
from datetime import datetime
import numpy as np
import os
import cv2
import sys
from PIL import ImageGrab

from script.load_model import load_model
from script.cfg import load_cfg
from script.windows_api import detect_nx
from script.keyboard_mouse_ctrl import my_type, mouse_click, open_vim, quit_vim

# ------------------------- def ---------------------------- #
def recursive_vim():
    my_type("find . | grep '[.][/][^.]' > ~/aaa.tmp")
    my_type('enter_key')
    while True:
        img = screen(x1, y1, x2, y2 + 2*h)
        terminal_str, file_eof_, line_cou_ = infer(vertical_num + 2, horizontal_num, img, 0, 1, vim_mode=False)
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

def screen(x1, y1, x2, y2, threshold=1):
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    ret, th1 = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
    return th1

def infer(vertical_num, horizontal_num, th1, file_eof, line_cou, vim_mode=True, vim_text_bias_width=8):
    '''
    vim_text_bias_width: There are 8 chars(w*8 pixels) in front of the text after you use vim -u NONE open file and :set nu
    '''
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
                            if wait_correct_num == True:
                                wait_correct_num = False
                            if line_cou != 1:
                                temp_s += '\n'
                        else:
                            wait_correct_num = True
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
                        if wait_correct_num == True:
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

def single_file_mode(name):
    file_name = name
    f = open(export_dir_name + file_name, 'w')
    open_vim(file_name)

    file_eof = 0
    line_cou = 1
    while(file_eof == 0):
        img = screen(x1, y1, x2, y2)
        temp_str, file_eof, line_cou = infer(vertical_num, horizontal_num, img, file_eof, line_cou)
        f.write(temp_str)
        my_type('pagedown_key')

    quit_vim()
    f.close()


# --------------------------- detect nx ------------------------ #
another_monitor, is_nx_active = detect_nx()
if is_nx_active == False:
    exit()


# --------------------------- load cfg and model ------------------------ #
config = load_cfg()
# for key in config['cust']:
#     print(key, config['cust'][key])
difference = int(config['cust']['difference'])
if config['cust']['build_model'] == '0':          # no model inside your directory
    print('please run calibration.py first')
    exit()
char_list, difference, category, img_arr = load_model(difference)


# --------------------------- init variables ------------------------ #
x1 = int(config['cust']['x1'])
y1 = int(config['cust']['y1'])
x2 = int(config['cust']['x2'])
y2 = int(config['cust']['y2'])

# one char size
w = 9
h = 18

vertical_num = (y2 - y1) // h
horizontal_num = (x2 - x1) // w

log_flag = 0          # flag : log on -> log_flag = 1
log_cou = 0
wait_correct_num = False  # flag

export_file_root = 'export/'


# --------------------------- START --------------------------- #
print('---------------------------')
while True:
    print('please input mode : 1.single file mode  2.recursive mode  3.terminal export')
    choice = input()
    if choice != '1' and choice != '2' and choice != '3':
        print('please input 1 or 2 or 3')
    elif choice == '1':
        print('please input file name :')
        file_name = input()
        break
    else:
        break

print('---------------------------')
print('Start')
print('---------------------------')

time.sleep(0.5)
mouse_click((x1+x2)//2, (y1+y2)//2)

now = datetime.now()
export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
os.mkdir(export_dir_name)
print('create folder : ' + export_dir_name)


if choice == '1':
    single_file_mode(file_name)
elif choice == '2':
    recursive_vim()
    dir_str = ''
    file_eof = 0
    line_cou = 1
    while(file_eof == 0):
        img = screen(x1, y1, x2, y2)
        temp_str, file_eof, line_cou = infer(vertical_num, horizontal_num, img, file_eof, line_cou)
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
        img = screen(x1, y1, x2, y2 + 2*h)
        terminal_str, file_eof_, line_cou_ = infer(vertical_num + 2, horizontal_num, img, 0, 1, vim_mode=False)
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
elif choice == '3':
    img = screen(x1, y1, x2, y2 + 2*h)
    terminal_str, file_eof_, line_cou_ = infer(vertical_num + 2, horizontal_num, img, 0, 1, vim_mode=False)
    print('-------------------- output -------------------------')
    print(terminal_str)
    f = open(export_dir_name + 'terminal.txt', 'w')
    f.write(terminal_str)
    f.close()

print('DONE')
