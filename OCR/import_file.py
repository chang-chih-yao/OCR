from win32api import ExitWindowsEx
from script.keyboard_mouse_ctrl import my_type, mouse_click, mouse_click_mid
from script.windows_api import detect_nx, active_window, win_clip, check_win_clip

import os
import time
import sys

hwnd, is_nx_active, another_monitor = detect_nx()
if is_nx_active == False:
    print('not found NoMachine')
    exit()

active_window(hwnd)

target_folder = r'D:\Cychang\Downloads\audio_data_path\5575_mix\gen\env'

for dirPath, dirNames, fileNames in os.walk(target_folder):
    dataset_dir = dirPath.replace('\\', '/')
    # print(dataset_dir)
    # print(fileNames)
    total_files_num = len(fileNames)
    cou = 1
    for f in fileNames:
        # print(dataset_dir + '/' + f, 'r')
        mouse_click(2500, 500)
        time.sleep(0.2)
        win_clip('gvim ' + f)
        while(check_win_clip('gvim ' + f) == False):
            mouse_click(2500, 500)
            time.sleep(0.2)
            win_clip('gvim ' + f)
        
        mouse_click(1200, 500)
        time.sleep(0.2)
        my_type('paste')
        my_type('enter_key')
        my_type('i')

        mouse_click(2500, 500)
        with open(dataset_dir + '/' + f, 'r') as fprt:
            my_txt = fprt.read()
            # print(my_txt)
        time.sleep(0.2)
        win_clip(my_txt)
        while(check_win_clip(my_txt) == False):    
            mouse_click(2500, 500)
            time.sleep(0.2)
            win_clip(my_txt)
        
        mouse_click(1200, 500)
        mouse_click_mid(1200, 500)
        time.sleep(0.5)
        my_type('esc_key')
        my_type('esc_key')
        my_type(':wq')
        my_type('enter_key')
        time.sleep(0.2)

        print('\r[{:>5d}/{:<5d}]'.format(cou, total_files_num), end='')
        sys.stdout.flush()
        cou += 1