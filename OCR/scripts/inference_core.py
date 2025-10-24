import numpy as np
import time
import cv2
from PIL import ImageGrab
import sys
import os
import matplotlib.pyplot as plt
import base64
import lzma
import tarfile
import io
import shutil
# from multiprocessing import Array, Value
from threading import Thread, Lock
import ctypes

from scripts.gen_dataset_fast import gen_data
from scripts.gen_training_data_fast import gen_train
from scripts.load_model import load_model
from scripts.cfg import build_cfg, load_cfg, modify_cfg
from scripts.windows_api import detect_nx, message_box, active_window, win_clip, get_windows_location
from scripts.keyboard_mouse_ctrl import my_type, mouse_click, open_vim, quit_vim, get_exit_flag

class Inference:
    def __init__(self, calibration=False):
        # self.set_up(calibration)
        self.img_lock = Lock()
        self.img_is_new = False
        self.thread_img = ''

    def reset_var(self):
        self.img_is_new = False
        
    def check_nx_window(self):
        self.hwnd, self.is_nx_active, self.another_monitor = detect_nx()

    def set_up(self, calibration):
        # --------------------------- detect nx ------------------------ #
        self.hwnd, self.is_nx_active, self.another_monitor = detect_nx()
        if self.is_nx_active == False:
            # print('not found NoMachine')
            # sys.exit()
            return False

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
                sys.exit()
        if calibration:
            self.char_list = ''
            self.data_set_num = ''
            self.category = ''
            self.img_arr = ''
            self.char_list_binary = ''
            self.data_set_num_binary = ''
            self.category_binary = ''
            self.img_arr_binary = ''
        else:
            self.infer_load_model()

        # 1080p monitor size
        if calibration:
            self.x1 = int(config['DEFAULT']['x1'])
            self.y1 = int(config['DEFAULT']['y1'])
            self.x2 = int(config['DEFAULT']['x2'])
            self.y2 = int(config['DEFAULT']['y2'])
        else:
            self.x1 = int(config['cust']['x1'])
            self.y1 = int(config['cust']['y1'])
            self.x2 = int(config['cust']['x2'])
            self.y2 = int(config['cust']['y2'])

        if self.another_monitor:
            self.x1 += 1920
            self.x2 += 1920


        self.vim_text_bias_width = 8         # There are 8 chars(w*8 pixels) in front of the text after you use vim -u NONE open file and :set nu

        self.vertical_num = (self.y2 - self.y1) // self.h
        self.horizontal_num = (self.x2 - self.x1) // self.w

        self.wait_correct_num = 0            # flag
        self.log_flag = 0                    # flag : log on -> log_flag = 1
        self.log_cou = 0
        return True

    def set_bg_class(self, bg):
        self.bg = bg

    def infer_load_model(self):
        self.char_list, self.data_set_num, self.category, self.img_arr, self.char_list_binary, self.data_set_num_binary, self.category_binary, self.img_arr_binary = load_model(w=self.w, h=self.h)

    def vertical_and_horizontal_num_update(self):
        self.vertical_num = (self.y2 - self.y1) // self.h
        self.horizontal_num = (self.x2 - self.x1) // self.w

    def active_nx(self, sec=0.5):
        print(self.hwnd)
        # active_window(self.hwnd)
        if self.hwnd != ctypes.windll.user32.GetForegroundWindow():
            foreground_window = ctypes.windll.user32.GetForegroundWindow()
            current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
            target_thread = ctypes.windll.user32.GetWindowThreadProcessId(foreground_window, None)  # 獲取目標窗口的線程ID
            ctypes.windll.user32.AttachThreadInput(target_thread, current_thread, True)             # 附加線程輸入
            ctypes.windll.user32.SetForegroundWindow(self.hwnd)
            ctypes.windll.user32.BringWindowToTop(self.hwnd)
            ctypes.windll.user32.AttachThreadInput(target_thread, current_thread, False)            # 分離線程輸入
        time.sleep(sec)
    
    def mouse_click_in_middle_NX(self):
        tmp_rect = get_windows_location(self.hwnd)
        mouse_click(int((tmp_rect[0] + tmp_rect[2])/2), int((tmp_rect[1] + tmp_rect[3])/2))

    def current_opened_file(self, export_dir_name):
        self.bg.nx_bg_type('esc_key')
        self.bg.nx_bg_type('esc_key')
        self.bg.nx_bg_type(":echo expand('%:p')")
        self.bg.nx_bg_type('enter_key')
        img = self.screen(vim_mode=False)
        terminal_str = self.infer(img, vim_mode=False)[0]
        file_name = terminal_str.split('\n')[-2]
        self.bg.nx_bg_type('new_tab')
        my_str = self.single_file_mode(file_name)
        self.write_in_file(export_dir_name, 'current_opened_file.txt', my_str)

    # def delete_return_line(self, my_str, cmd):
    #     split_str = my_str.split('\n')
    #     target_line_return = 0
    #     for i in range(len(split_str)-1, 0, -1):
    #         if split_str[i] != '':
    #             target_line_return = i
    #             break
    #     result = ''
    #     for i in range(target_line_return+1):    # 0 ~ target_line_return
    #         result += split_str[i]
    #         result += '\n'
        
    #     target_line_cmd = 0
    #     for i in range(len(split_str)-1, 0, -1):
    #         if split_str[i].find(cmd) >=0:
    #             target_line_cmd = i
    #             break
    #     return result, target_line_cmd

    def recursive_vim(self):
        for t in range(50):
            my_type('enter_key_fast')
        my_type("find . | grep '[.][/][^.]' > ~/aaa.tmp")
        my_type('enter_key')
        while True:
            img = self.screen(vim_mode=False)
            terminal_str = self.infer(img, vim_mode=False)[0]
            # print('[-3]|' + terminal_str.split('\n')[-3] + '|')
            # print('[-2]|' + terminal_str.split('\n')[-2] + '|')
            # print('[-1]|' + terminal_str.split('\n')[-1] + '|')
            if terminal_str.split('\n')[-2] == '':
                print('wait aaa.tmp...')
                time.sleep(1)
            else:
                break
        # if terminal_str.split('\n')[-3].find('Permission denied') >= 0:
        #     print('Permission denied !!!')
        #     print('please cp -r this_dir/ to your dir')
        #     sys.exit()
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
                sys.exit()

        print(dir_arr)
        self.active_nx()

        for item in dir_arr:
            my_type('wc -l < ' + item)
            my_type('enter_key')
            img = self.screen(vim_mode=False)
            terminal_str = self.infer(img, vim_mode=False)[0]
            # print(terminal_str)
            # print('[-3]|' + terminal_str.split('\n')[-3] + '|')   # terminal 2nd to last line
            # print('[-2]|' + terminal_str.split('\n')[-2] + '|')   # terminal last        line
            # print('[-1]|' + terminal_str.split('\n')[-1] + '|')
            if (terminal_str.split('\n')[-2] == '0'):
                if (terminal_str.split('\n')[-3].find('Is a directory') >= 0):
                    os.mkdir(export_dir_name + item + '/')
                    print('build dir')
                else:
                    f = open(export_dir_name + item, 'w')
                    f.close()
                    print('it is empty file')
            else:
                # print((terminal_str.split('\n')[-2]))
                my_str = self.single_file_mode(item)
                self.write_in_file(export_dir_name, item, my_str)
        
        print('recursive DONE')

    def single_file_mode(self, name):
        self.bg.nx_bg_open_vim(name)
        file_eof = 0
        line_cou = 1
        my_str = ''
        while(file_eof == 0):
            if get_exit_flag() == 1:
                break
            img = self.screen()
            temp_str, file_eof, line_cou = self.infer(img, file_eof=file_eof, line_cou=line_cou)
            my_str += temp_str
            self.bg.nx_bg_type('pagedown_key')

        self.bg.nx_bg_quit_vim()
        return my_str

    def fast_screen(self):
        old_str = ''
        new_str = ''
        # idx = 0
        while True:
            if get_exit_flag() == 1:
                break
            # img = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2), all_screens=True)
            # img_np = np.array(img)
            # frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            # start_time = time.perf_counter()
            frame = self.screen(vim_mode=True)
            new_str = ''
            for i in range(7):
                crop_img = frame[0:self.h, i*self.w:(i+1)*self.w]  # 第1行前面7個char
                bg_color = crop_img[0, 0]   # assume [0, 0] is background color
                crop_img = np.where(crop_img == bg_color, 0, 255).astype('uint8')

                mid = (crop_img.flatten() / 255).astype('uint8')
                result_arr = np.abs(self.img_arr_binary - mid)
                result_sum = np.sum(result_arr, axis=1)
                result_idx = np.argmin(result_sum)
                new_str += self.char_list_binary[result_idx]
            # print(f'new_str: {new_str}')
            if new_str != old_str:
                crop_img = frame[self.h:self.h*2, 0:self.w]        # 第2行的第1個char
                bg_color = crop_img[0, 0]   # assume [0, 0] is background color
                crop_img = np.where(crop_img == bg_color, 0, 255).astype('uint8')

                mid = (crop_img.flatten() / 255).astype('uint8')
                result_arr = np.abs(self.img_arr_binary - mid)
                result_sum = np.sum(result_arr, axis=1)
                result_idx = np.argmin(result_sum)

                if self.char_list_binary[result_idx] == '~':       # 第2行的第1個char
                    # print('第2行的第1個char')
                    # if int(new_str) == 1:                          # 代表該文件只有一行
                    while True:
                        if not self.img_is_new:
                            self.img_lock.acquire()
                            self.thread_img = frame
                            self.img_is_new = True
                            self.img_lock.release()
                            break
                        else:
                            # print('wait detect img')
                            time.sleep(0.1)
                    # print('end')
                    break
                else:
                    old_str = new_str
                    # print('ready to send frame to shared_memory')
                    # print(f'fast_screen, infer time: {time.perf_counter() - start_time:.4f} sec')
                    while True:
                        if get_exit_flag() == 1:
                            break
                        if not self.img_is_new:
                            self.img_lock.acquire()
                            self.thread_img = frame
                            self.img_is_new = True
                            self.img_lock.release()
                            break
                        else:
                            # print('fast_screen, wait detect img')
                            time.sleep(0.1)
                    # cv2.imwrite(f'{idx}.png', frame)
                    # idx += 1
                    self.bg.nx_bg_type('pagedown_key', nodelay=True)
                    time.sleep(0.1)
            else:
                print('still same')
                time.sleep(0.1)

    def single_file_mode_binary(self, input_file, export_dir_name, output_file):
        self.reset_var()
        # shared_array = Array('I', original_array.flatten(), lock=False)

        # cmd = f'xxd -c 90 -p {input_file} > {input_file}.ttt'
        # cmd = f'xz -k -5 {input_file}'
        # my_type(cmd)
        # my_type('enter_key')

        # cmd = f'python to_binary.py 180 {input_file} {input_file}.ttt'
        # cmd = f'/rsc/R7227/.local/open/file_dump 180 {input_file} {input_file}.ttt'
        # cmd = f'/rsc/R7227/o/file_dump -f 180 {input_file}'
        cmd = f'python file_dump.py -f 180 {input_file}'
        self.bg.nx_bg_type(cmd)
        self.bg.nx_bg_type('enter_key')
        # idx = 0
        while True:
            img = self.screen(vim_mode=False)
            # print(img.shape)
            str_0 = ''
            str_1 = ''
            for i in range(13):
                crop_img = img[img.shape[0] - self.h*2 : img.shape[0] - self.h, i*self.w:(i+1)*self.w]
                bg_color = crop_img[0, 0]   # assume [0, 0] is background color
                crop_img = np.where(crop_img == bg_color, 0, 255).astype('uint8')

                mid = (crop_img.flatten() / 255).astype('uint8')
                result_arr = np.abs(self.img_arr - mid)
                result_sum = np.sum(result_arr, axis=1)
                result_idx = np.argmin(result_sum) // self.data_set_num
                str_0 += self.char_list[result_idx]

                
                crop_img = img[img.shape[0] - self.h : img.shape[0], i*self.w:(i+1)*self.w]
                bg_color = crop_img[0, 0]   # assume [0, 0] is background color
                crop_img = np.where(crop_img == bg_color, 0, 255).astype('uint8')

                mid = (crop_img.flatten() / 255).astype('uint8')
                result_arr = np.abs(self.img_arr - mid)
                result_sum = np.sum(result_arr, axis=1)
                result_idx = np.argmin(result_sum) // self.data_set_num
                str_1 += self.char_list[result_idx]
            
            # print('|' + str_0 + '|')
            # print('|' + str_1 + '|')
            if str_1 == ' '*13:
                print('wait file_dump cmd...')
                time.sleep(1)
            elif str_0 == 'No such file:':
                print(f'找不到輸入的檔案:"{input_file}"')
                return
            else:
                break

            # cv2.imwrite(f'check_{idx}.png', crop_img)
            # idx += 1
            # terminal_str = self.infer(img, vim_mode=False)[0]
            # print('[-3]|' + terminal_str.split('\n')[-3] + '|')
            # print('[-2]|' + terminal_str.split('\n')[-2] + '|')
            # print('[-1]|' + terminal_str.split('\n')[-1] + '|')
            # if terminal_str.split('\n')[-2] == '':
            #     print('wait file_dump cmd...')
            #     time.sleep(1)
            # else:
            #     break
        
        # open_vim(f'{input_file}.ttt')
        self.bg.nx_bg_type(':set nu')
        self.bg.nx_bg_type('enter_key')
        self.bg.nx_bg_type(':hi LineNr ctermfg=white ctermbg=black')
        self.bg.nx_bg_type('enter_key')
        self.bg.nx_bg_type(':hi Normal ctermfg=white ctermbg=black')
        self.bg.nx_bg_type('enter_key')
        time.sleep(0.2)

        t = Thread(target=self.fast_screen, daemon=True)
        t.start()

        file_eof = 0
        line_cou = 1
        my_str = ''
        while file_eof == 0:
            # start_time = time.perf_counter()
            # img = self.screen()
            if get_exit_flag() == 1:
                break
            if self.img_is_new:
                self.img_lock.acquire()
                img = self.thread_img.copy()
                self.img_is_new = False
                self.img_lock.release()
                # print(img.shape)
                # cv2.imwrite(f'target.png', img)
                temp_str, file_eof, line_cou = self.infer_binary(img, file_eof=file_eof, line_cou=line_cou)
                none_return_line_str = temp_str.replace('\n', '')
                # temp_str, file_eof, line_cou = self.infer(img, file_eof=file_eof, line_cou=line_cou)
                my_str += none_return_line_str
                # print(f'cost time:{time.perf_counter() - start_time}')
                # my_type('pagedown_key')
            else:
                print('wait new img')
                time.sleep(0.1)

        # my_type(f'rm -f {input_file}.ttt')
        # my_type('enter_key')

        print(my_str.strip())      # encoded string

        # binary_data_base64 = base64.b64decode(my_str.strip())
        binary_data_base85 = base64.b85decode(my_str.strip())
        # print(binary_data_base64)
        if binary_data_base85 != b'':
            # method 1: 不寫檔, 直接用byte string傳遞, 解壓縮
            binary_data = lzma.decompress(binary_data_base85)
            # print(binary_data)
            with open(export_dir_name + output_file, 'wb') as f_out:
                f_out.write(binary_data)
        else:
            with open(export_dir_name + output_file, 'w') as f_out:
                f_out.write('')

        t.join()
        self.bg.nx_bg_quit_vim()

        return binary_data_base85

    def folder_mode_binary(self, input_file, export_dir_name):
        self.reset_var()
        cmd = f'/rsc/R7227/o/file_dump -d 180 {input_file}'
        # cmd = f'python file_dump.py -d 180 {input_file}'
        self.bg.nx_bg_type(cmd)
        self.bg.nx_bg_type('enter_key')
        # idx = 0
        while True:
            img = self.screen(vim_mode=False)
            # print(img.shape)
            str_0 = ''
            str_1 = ''
            for i in range(13):
                crop_img = img[img.shape[0] - self.h*2 : img.shape[0] - self.h, i*self.w:(i+1)*self.w]
                bg_color = crop_img[0, 0]   # assume [0, 0] is background color
                crop_img = np.where(crop_img == bg_color, 0, 255).astype('uint8')

                mid = (crop_img.flatten() / 255).astype('uint8')
                result_arr = np.abs(self.img_arr - mid)
                result_sum = np.sum(result_arr, axis=1)
                result_idx = np.argmin(result_sum) // self.data_set_num
                str_0 += self.char_list[result_idx]

                
                crop_img = img[img.shape[0] - self.h : img.shape[0], i*self.w:(i+1)*self.w]
                bg_color = crop_img[0, 0]   # assume [0, 0] is background color
                crop_img = np.where(crop_img == bg_color, 0, 255).astype('uint8')

                mid = (crop_img.flatten() / 255).astype('uint8')
                result_arr = np.abs(self.img_arr - mid)
                result_sum = np.sum(result_arr, axis=1)
                result_idx = np.argmin(result_sum) // self.data_set_num
                str_1 += self.char_list[result_idx]
            
            # print('|' + str_0 + '|')
            # print('|' + str_1 + '|')
            if str_1 == ' '*13:
                print('wait file_dump cmd...')
                time.sleep(1)
            elif str_0 == 'No such file:':
                print(f'找不到輸入的檔案:"{input_file}"')
                return
            else:
                break
        
        self.bg.nx_bg_type(':set nu')
        self.bg.nx_bg_type('enter_key')
        self.bg.nx_bg_type(':hi LineNr ctermfg=white ctermbg=black')
        self.bg.nx_bg_type('enter_key')
        self.bg.nx_bg_type(':hi Normal ctermfg=white ctermbg=black')
        self.bg.nx_bg_type('enter_key')
        time.sleep(0.2)

        t = Thread(target=self.fast_screen, daemon=True)
        t.start()

        file_eof = 0
        line_cou = 1
        my_str = ''
        while file_eof == 0:
            # start_time = time.perf_counter()
            # img = self.screen()
            if get_exit_flag() == 1:
                break
            if self.img_is_new:
                # start_time = time.perf_counter()
                self.img_lock.acquire()
                img = self.thread_img.copy()
                self.img_is_new = False
                self.img_lock.release()
                # print(img.shape)
                # cv2.imwrite(f'target.png', img)
                temp_str, file_eof, line_cou = self.infer_binary(img, file_eof=file_eof, line_cou=line_cou)
                none_return_line_str = temp_str.replace('\n', '')
                # temp_str, file_eof, line_cou = self.infer(img, file_eof=file_eof, line_cou=line_cou)
                my_str += none_return_line_str
                # print(f'cost time:{time.perf_counter() - start_time}')
                # my_type('pagedown_key')
                # print(f'folder_mode_binary, infer time: {time.perf_counter() - start_time:.4f} sec')
            else:
                print('folder_mode_binary, wait new img')
                time.sleep(0.1)


        # print(my_str)

        # binary_data_base64 = base64.b64decode(my_str.strip())
        binary_data_base85 = base64.b85decode(my_str.strip())
        # print(binary_data_base64)
        if binary_data_base85 != b'':
            file_like_object = io.BytesIO(binary_data_base85)
            with tarfile.open(fileobj=file_like_object, mode='r:xz') as file:
                file.extractall(path=export_dir_name)

        else:
            print('empty')
            # with open(export_dir_name + output_file, 'w') as f_out:
            #     f_out.write('')

        t.join()
        self.bg.nx_bg_quit_vim()

        return binary_data_base85


    def write_in_file(self, export_dir_name, file_name, my_str=''):
        f = open(export_dir_name + file_name, 'w')
        f.write(my_str)
        f.close()
    
    def write_in_file_binary(self, export_dir_name, file_name, binary_data=b''):
        f = open(export_dir_name + file_name, 'wb')
        f.write(binary_data)
        f.close()
    
    def screen(self, threshold=None, vim_mode=True):
        # if threshold is None:
        #     threshold = self.threshold
        # start_time = time.perf_counter()
        if vim_mode == False:
            frame = self.bg.nx_bg_screen(self.x1, self.y1, self.x2, self.y2 + 1*self.h)
            
            # img = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2 + 1*self.h), all_screens=True)
            # img_np = np.array(img)
            # frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            # cv2.imshow('1', frame_)
            # cv2.waitKey(0)
            # cv2.imshow('2', frame)
            # cv2.waitKey(0)
        else:
            frame = self.bg.nx_bg_screen(self.x1, self.y1, self.x2, self.y2)
            # img = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2), all_screens=True)
        # img_np = np.array(img)
        # frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        # print(f'screen time:{time.perf_counter() - start_time}')
        # ret, th1 = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
        return frame

    def infer(self, input_img, vertical_num=None, horizontal_num=None, file_eof=0, line_cou=1, vim_mode=True, draw_plot=False):
        #global log_cou, wait_correct_num
        if vertical_num is None:
            vertical_num = self.vertical_num
            if vim_mode==False:
                vertical_num += 1
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
                    # if bg_color != 0:
                    #     print(f'bg_color != 0, {bg_color}')
                    for a in range(self.h):
                        for b in range(self.w):
                            if crop_img[a, b] == bg_color:
                                crop_img[a, b] = 0
                            else:
                                crop_img[a, b] = 255
                    ################## detect background color ##################
                    mid = crop_img.copy()
                    if self.log_flag == 1:
                        cv2.imwrite('log/{:04d}.png'.format(self.log_cou), mid)
                        self.log_cou += 1
                    # cv2.imshow('mid', mid)
                    # cv2.waitKey()
                    mid = (mid/255).astype('uint8')
                    mid = mid.flatten()
                    # print(mid.shape, mid.dtype)                        # (190,) uint8
                    # print(self.img_arr.shape, self.img_arr.dtype)      # (190, 190) uint8
                    result_arr = np.absolute(self.img_arr - mid)
                    # print(result_arr, result_arr.shape, result_arr.dtype)    # shape: (190, 190)   dtype: uint8
                    result_sum = np.sum(result_arr, axis=1)                                      # (data_set_num*category,)   int32
                    argmin_idx = np.argmin(result_sum)
                    result = argmin_idx // self.data_set_num
                    # if result_sum[argmin_idx] != 0:
                    #     print(result_sum)
                    #     print(result_sum[argmin_idx])
                    #     print(result, self.char_list[result])
                    if draw_plot:
                        if self.data_set_num == 1:
                            line1.set_ydata(result_sum)        # if data_set_num == 1
                        elif self.data_set_num == 2:
                            line1.set_ydata(result_sum[::2])  # if data_set_num == 2
                        fig.canvas.draw()
                        time.sleep(1)
                        fig.canvas.flush_events()

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



    def infer_binary(self, input_img, vertical_num=None, horizontal_num=None, file_eof=0, line_cou=1, vim_mode=True, draw_plot=False):
        #global log_cou, wait_correct_num
        if vertical_num is None:
            vertical_num = self.vertical_num
            if vim_mode==False:
                vertical_num += 1
        if horizontal_num is None:
            horizontal_num = self.horizontal_num
        temp_s = ''
        x_start = self.w*0
        y_start = self.h*0

        y = y_start
        space_cou = 0

        if draw_plot:
            char_np_arr = np.array(list(self.char_list_binary))
            temp_y_arr = np.random.randint(100, size=(20))
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
                
                
                ################## detect background color ##################
                bg_color = crop_img[0, 0]   # assume [0, 0] is background color
                crop_img = np.where(crop_img == bg_color, 0, 255).astype('uint8')
                ################## detect background color ##################
                mid = (crop_img.flatten() / 255).astype('uint8')

                # mid = crop_img.copy()
                # if self.log_flag:
                #     cv2.imwrite('log/{:04d}.png'.format(self.log_cou), mid)
                #     self.log_cou += 1
                # # cv2.imshow('mid', mid)
                # # cv2.waitKey()
                # mid = (mid/255).astype('uint8')
                # mid = mid.flatten()
                result_arr = np.absolute(self.img_arr_binary - mid)
                result_sum = np.sum(result_arr, axis=1)                                      # (data_set_num_binary*category_binary,)   int32
                result = np.argmin(result_sum)
                if draw_plot:
                    #line1.set_ydata(result_sum[::2])  # if data_set_num_binary == 2
                    line1.set_ydata(result_sum)        # if data_set_num_binary == 1
                    fig.canvas.draw()
                    time.sleep(1)
                    fig.canvas.flush_events()

                # print(result, self.char_list_binary[result])
                if j < self.vim_text_bias_width and vim_mode:
                    front_str += self.char_list_binary[result]
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
                        elif front_str == '~       ':
                            print('\n', end='')
                            print('file end')
                            file_eof = 1
                            return temp_s, file_eof, line_cou
                        # else:
                        #     print('gg')
                        #     line_cou -= 1
                        #     if self.wait_correct_num == 1:
                        #         break
                        #     # print('more than 1 line')
                        #     if space_cou == 0:
                        #         temp_s += front_str
                        #     else:
                        #         for t in range(space_cou):
                        #             temp_s += ' '
                        #         temp_s += front_str
                        #         space_cou = 0
                else:
                    if(self.char_list_binary[result] == ' '):
                        space_cou += 1
                    else:
                        if(space_cou == 0):
                            temp_s += self.char_list_binary[result]
                        else:
                            for t in range(space_cou):
                                temp_s += ' '
                            temp_s += self.char_list_binary[result]
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

