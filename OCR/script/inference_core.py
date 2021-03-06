import numpy as np
import time
import cv2
from PIL import ImageGrab
import sys
import os
import matplotlib.pyplot as plt

from script.gen_dataset_fast import gen_data
from script.gen_training_data_fast import gen_train
from script.load_model import load_model
from script.cfg import build_cfg, load_cfg, modify_cfg
from script.windows_api import detect_nx, message_box, active_window, win_clip, get_windows_location
from script.keyboard_mouse_ctrl import my_type, mouse_click, open_vim, quit_vim

class Inference:
    def __init__(self, calibration=False):
        self.set_up(calibration)

    def set_up(self, calibration):
        # --------------------------- detect nx ------------------------ #
        self.hwnd, self.is_nx_active, self.another_monitor = detect_nx()
        if self.is_nx_active == False:
            print('not found NoMachine')
            exit()

        # --------------------------- load cfg  ------------------------ #
        config = load_cfg()
        # for key in config['cust']:
        #     print(key, config['cust'][key])
        self.difference = int(config['cust']['difference'])
        self.threshold = int(config['cust']['threshold'])

        # one char size
        self.w = int(config['cust']['w'])
        self.h = int(config['cust']['h'])

        # --------------------------- create and load model ------------------------ #
        if config['cust']['build_model'] == '0':          # no model inside your directory
            if calibration:
                temp_img = cv2.imread('gen_dataset.png', cv2.IMREAD_GRAYSCALE)
                gen_data(temp_img, difference=self.difference, img_from_png=True, threshold=self.threshold)
                gen_train()
                modify_cfg('build_model', 1)
            else:
                print('please run calibration.py first')
                exit()
        if calibration:
            self.char_list = ''
            self.data_set_num = ''
            self.category = ''
            self.img_arr = ''
        else:
            self.char_list, self.data_set_num, self.category, self.img_arr = load_model(w=self.w, h=self.h)

        # 1080p monitor size
        if calibration:
            self.x1 = int(config['DEFAULT']['x1'])
            self.y1 = int(config['DEFAULT']['y1'])
            self.x2 = int(config['DEFAULT']['x2'])
            self.y2 = int(config['DEFAULT']['y2'])
            if self.another_monitor:
                self.x1 += 1920
                self.x2 += 1920
        else:
            self.x1 = int(config['cust']['x1'])
            self.y1 = int(config['cust']['y1'])
            self.x2 = int(config['cust']['x2'])
            self.y2 = int(config['cust']['y2'])


        self.vim_text_bias_width = 8         # There are 8 chars(w*8 pixels) in front of the text after you use vim -u NONE open file and :set nu

        self.vertical_num = (self.y2 - self.y1) // self.h
        self.horizontal_num = (self.x2 - self.x1) // self.w

        self.wait_correct_num = 0            # flag
        self.log_flag = 0                    # flag : log on -> log_flag = 1
        self.log_cou = 0

    def vertical_and_horizontal_num_update(self):
        self.vertical_num = (self.y2 - self.y1) // self.h
        self.horizontal_num = (self.x2 - self.x1) // self.w

    def active_nx(self, sec=0.5):
        active_window(self.hwnd)
        time.sleep(sec)
    
    def mouse_click_in_middle_NX(self):
        tmp_rect = get_windows_location(self.hwnd)
        mouse_click(int((tmp_rect[0] + tmp_rect[2])/2), int((tmp_rect[1] + tmp_rect[3])/2))

    def current_opened_file(self, export_dir_name):
        my_type('esc_key')
        my_type('esc_key')
        my_type(":echo expand('%:p')")
        my_type('enter_key')
        img = self.screen(vim_mode=False)
        terminal_str = self.infer(img, vim_mode=False)[0]
        file_name = terminal_str.split('\n')[-2]
        my_type('new_tab')
        my_str = self.single_file_mode(file_name)
        self.write_in_file(export_dir_name, 'current_opened_file.txt', my_str)

    def delete_return_line(self, my_str, cmd):
        split_str = my_str.split('\n')
        target_line_return = 0
        for i in range(len(split_str)-1, 0, -1):
            if split_str[i] != '':
                target_line_return = i
                break
        result = ''
        for i in range(target_line_return+1):    # 0 ~ target_line_return
            result += split_str[i]
            result += '\n'
        
        target_line_cmd = 0
        for i in range(len(split_str)-1, 0, -1):
            if split_str[i].find(cmd) >=0:
                target_line_cmd = i
                break
        return result, target_line_cmd

    def recursive_vim(self):
        for t in range(50):
            my_type('enter_key_fast')
        my_type("find . | grep '[.][/][^.]' > ~/aaa.tmp")
        my_type('enter_key')
        while True:
            img = self.screen(vim_mode=False)
            terminal_str = self.infer(img, vim_mode=False)[0]
            terminal_str, target_line_cmd = self.delete_return_line(terminal_str, "~/aaa.tmp")
            # print('[-3]|' + terminal_str.split('\n')[-3] + '|')
            # print('[-2]|' + terminal_str.split('\n')[-2] + '|')
            if terminal_str.split('\n')[target_line_cmd+1] == '':
                print('wait aaa.tmp...')
                time.sleep(1)
            else:
                break
        # if terminal_str.split('\n')[-3].find('Permission denied') >= 0:
        #     print('Permission denied !!!')
        #     print('please cp -r this_dir/ to your dir')
        #     exit()
        
        open_vim('~/aaa.tmp', recursive_mode=True)
        my_type(':%s/\\.\\///g')
        my_type('enter_key')
        my_type(':g/aaa.tmp/d')
        my_type('enter_key')
        my_type(':g/\\/\\./d')
        my_type('enter_key')
        my_type(':wq')
        my_type('enter_key')

    def recursive_mode(self, export_dir_name):
        self.recursive_vim()
        dir_str = self.single_file_mode('~/aaa.tmp')
        my_type('rm -f ~/aaa.tmp')
        my_type('enter_key')

        dir_arr = dir_str.split('\n')
        if len(dir_arr) > 50:
            if message_box(self.hwnd, 'Detect {:d} files in this directory, continue ?'.format(len(dir_arr))) == 0:
                print('end program')
                exit()

        print(dir_arr)
        self.active_nx()

        for item in dir_arr:
            my_type('wc -l < ' + item)
            my_type('enter_key')
            img = self.screen(vim_mode=False)
            terminal_str = self.infer(img, vim_mode=False)[0]
            terminal_str, target_line_cmd = self.delete_return_line(terminal_str, 'wc -l <')
            # print('[-3]|' + terminal_str.split('\n')[-3] + '|')
            # print('[-2]|' + terminal_str.split('\n')[-2] + '|')
            # print('[-1]|' + terminal_str.split('\n')[-1] + '|')
            if (terminal_str.split('\n')[-4] == '0'):
                if (terminal_str.split('\n')[-5].find('Is a directory') >= 0):
                    os.mkdir(export_dir_name + item + '/')
                    print('build dir')
                else:
                    f = open(export_dir_name + item, 'w')
                    f.close()
                    print('it is empty file')
            else:
                print(int(terminal_str.split('\n')[-4]))
                my_str = self.single_file_mode(item)
                self.write_in_file(export_dir_name, item, my_str)
        
        print('recursive DONE')

    def single_file_mode(self, name):
        open_vim(name)
        file_eof = 0
        line_cou = 1
        my_str = ''
        while(file_eof == 0):
            img = self.screen()
            temp_str, file_eof, line_cou = self.infer(img, file_eof=file_eof, line_cou=line_cou)
            my_str += temp_str
            my_type('pagedown_key')

        quit_vim()
        return my_str

    def write_in_file(self, export_dir_name, file_name, my_str=''):
        f = open(export_dir_name + file_name, 'w')
        f.write(my_str)
        f.close()
    
    def screen(self, threshold=None, vim_mode=True):
        if threshold is None:
            threshold = self.threshold
        if vim_mode == False:
            img = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2 + 2*self.h), all_screens=True)
        else:
            img = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2), all_screens=True)
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        #ret, th1 = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
        return frame

    def infer(self, input_img, vertical_num=None, horizontal_num=None, file_eof=0, line_cou=1, vim_mode=True, draw_plot=False):
        #global log_cou, wait_correct_num
        if vertical_num is None:
            vertical_num = self.vertical_num
            if vim_mode==False:
                vertical_num += 2
        if horizontal_num is None:
            horizontal_num = self.horizontal_num
        temp_s = ''
        x_start = self.w*0
        y_start = self.h*0

        y = y_start
        space_cou = 0

        if draw_plot:
            char_np_arr = np.array(list(self.char_list))
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
                crop_img = input_img[y:y+self.h, x:x+self.w]
                
                if crop_img.shape[0] != self.h or crop_img.shape[1] != self.w:
                    return temp_s, file_eof, line_cou
                
                if (np.all((crop_img.flatten() == 0)) or np.all((crop_img.flatten() == 255))):   # skip space image
                    result = 47                                                                  # char_list[47] == ' '
                else:
                    ################## detect background color ##################
                    bg_color = crop_img[0, 0]   # assume [0, 0] is bg color
                    for a in range(self.h):
                        for b in range(self.w):
                            if crop_img[a, b] == bg_color:
                                crop_img[a, b] = 0
                            else:
                                crop_img[a, b] = 255
                    ################## detect background color ##################
                    mid = crop_img.copy()
                    if (self.log_flag):
                        cv2.imwrite('log/{:04d}.png'.format(self.log_cou), mid)
                        self.log_cou += 1
                    # cv2.imshow('mid', mid)
                    # cv2.waitKey()
                    mid = (mid/255).astype('int8')
                    mid = mid.flatten()
                    result_arr = np.absolute(self.img_arr - mid)
                    result_sum = np.sum(result_arr, axis=1)                                      # (data_set_num*category,)   int32
                    result = np.argmin(result_sum) // self.data_set_num
                    if draw_plot:
                        #line1.set_ydata(result_sum[::2])  # if data_set_num == 2
                        line1.set_ydata(result_sum)        # if data_set_num == 1
                        fig.canvas.draw()
                        time.sleep(1)
                        fig.canvas.flush_events()

                    #print(result, self.char_list[result])
                if j < self.vim_text_bias_width and vim_mode:
                    front_str += self.char_list[result]
                    if j == 7:
                        # print('|'+front_str+'|')
                        if front_str.replace(' ', '').isdigit():
                            # print(line_cou)
                            if front_str == '{:>7d} '.format(line_cou):
                                space_cou = 0
                                if self.wait_correct_num == 1:
                                    self.wait_correct_num = 0
                                if line_cou != 1:
                                    temp_s += '\n'
                            else:
                                self.wait_correct_num = 1
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
                            if self.wait_correct_num == 1:
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
                    if(self.char_list[result] == ' '):
                        space_cou += 1
                    else:
                        if(space_cou == 0):
                            temp_s += self.char_list[result]
                        else:
                            for t in range(space_cou):
                                temp_s += ' '
                            temp_s += self.char_list[result]
                            space_cou = 0
                x += self.w
            y += self.h
            line_cou += 1
            if not vim_mode:
                space_cou = 0
                temp_s += '\n'
            print('\r[{:>5d}/{:<5d}]'.format(i+1, vertical_num), end='')
            sys.stdout.flush()
        print('\n', end='')
        return temp_s, file_eof, line_cou