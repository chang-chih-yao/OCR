import time
from datetime import datetime
import numpy as np
import os
import sys

from PIL import ImageGrab
import tkinter as tk
import math
import numpy as np
import cv2
import base64
import wmi
import ctypes
from datetime import datetime, timedelta
import json
from getmac import get_mac_address
from requests import post
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from threading import Thread

from script.keyboard_mouse_ctrl import mouse_click, my_type, detect_stop_program_open, detect_stop_program_close, get_exit_flag
from script.windows_api import message_box, win_clip
from script.inference_core import Inference
from script.cfg import load_cfg
from script.background_utility import BG

VERSION = '1.0.0'

print(f'VERSION : {VERSION}')

if ctypes.windll.shell32.IsUserAnAdmin() == 0:   # 若不是用管理員權限開本程式的話
    MessageBox_Admin_Check = ctypes.windll.user32.MessageBoxW
    MessageBox_Admin_Check(None, '請用管理員權限開啟本軟體', '管理員權限偵測', 0)
    sys.exit()

class Variables:
    def __init__(self) -> None:
        self.CFG_JSON_FILE = 'data/cfg.json'
        self.NEED_TO_UPLOAD_ERROR_LOG = True
        self.is_exception = False
        self.on_closing_flag = False
        self.expiration_date = ''
        self.price_level = ''
        self.USER_ID = ''
        self.macaddr_UUID = ''

class Certificate_key:
    def __init__(self, my_var:Variables) -> None:
        self.my_var = my_var
        
        self.CPU_Name = ''
        self.CPU_ProcessorId = ''
        self.UUID = ''
        self.macaddr = ''

        self.get_macaddr()

        tmp_class = wmi.WMI()
        for i in tmp_class.Win32_Processor():
            try:
                self.CPU_Name = i.Name.strip()
            except:
                self.CPU_Name = 'None'
                
            try:
                self.CPU_ProcessorId = i.ProcessorId.strip()
            except:
                self.CPU_ProcessorId = 'None'

        for i in tmp_class.Win32_ComputerSystemProduct():
            try:
                self.UUID = i.UUID.strip().replace('-', '_')
            except:
                self.my_var.is_exception = True
                self.my_var.NEED_TO_UPLOAD_ERROR_LOG = False
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '錯誤! 無法取得此電腦認證', '權限檢查', 0)
                raise Exception('Certificate_exception')
            
        self.my_var.macaddr_UUID = f'{self.macaddr}_{self.UUID}'
        
        # print(f'CPU_Name:{self.CPU_Name}, CPU_ProcessorId:{self.CPU_ProcessorId}, UUID:{self.UUID}')

        self.post_url = f'https://m900054.pythonanywhere.com/certificate_key_NX_OCR'

        # self.get_now_key()
        self.header = b'CY_VISION_BOT_HEADER_1207'

        self.PASS_MSG =           'CERTIFICATE_KEY_CHECK_PASSED____'
        self.FAIL_MSG =           'CERTIFICATE_KEY_CHECK_FAILED____'
        self.VERSION_ERROR_MSG =  'VERSION_CHECK_ERROR_____________'
        self.NO_USER_ID_MSG =     'NO_USER_ID_ERROR________________'
        self.NO_KEY_MSG =         'NO_KEY_ERROR____________________'
        self.KEY_CHANGED_MSG =    'KEY_CHANGED_ERROR_______________'
        self.TIMEOUT_MSG = 'CERTIFICATE_KEY_CHECK_TIMEOUT'   # local 端自定義的MSG
        self.POST_ERROR_MSG = 'POST_ERROR_MSG'               # local 端自定義的MSG
        self.SERVER_ERROR_MSG = 'SERVER_ERROR_MSG'           # local 端自定義的MSG
        self.ENCRYPT_ERROR_MSG = 'Encrypt ERROR'             # local 端自定義的MSG
        self.DECRYPT_ERROR_MSG = 'Decrypt ERROR'             # local 端自定義的MSG

    def get_macaddr(self):
        try:
            self.macaddr = get_mac_address().replace(':', '')
        except:
            self.my_var.is_exception = True
            self.my_var.NEED_TO_UPLOAD_ERROR_LOG = False
            MessageBox = ctypes.windll.user32.MessageBoxW
            MessageBox(None, '錯誤! 無法取得此電腦認證', '權限檢查', 0)
            raise Exception('Certificate_exception')

    def get_now_key(self, now_time, retry=0):
        if retry == 0:
            GMT8_time = now_time
        elif retry == 1:
            GMT8_time = now_time - timedelta(minutes=1)
        else:
            GMT8_time = now_time + timedelta(minutes=1)
        GMT8_time_str = GMT8_time.strftime("%Y%m%d%H%M")
        key_str =  f'CY_VISION_BOT_1207_{GMT8_time_str}_'
        # self.key = key_str.encode(encoding='utf-8')
        return key_str.encode(encoding='utf-8')
    
    def now_time_check(self):
        post_url = f'https://m900054.pythonanywhere.com/get_now_time'
        check_pass = False
        try:
            GMT8_time = datetime.utcnow() + timedelta(hours=8)
            GMT8_time_str = GMT8_time.strftime("%Y%m%d%H%M")
            my_dict = {"now_time": GMT8_time_str}
            post_json_str = json.dumps(my_dict)
            result = post(post_url, json=post_json_str, timeout=10)
            if result.status_code == 200:
                # print(f'timing check: {result.text}')
                if result.text == 'PASS':
                    check_pass = True
                else:
                    check_pass = False
            elif result.status_code == 403:   # Forbidden, The client does not have access rights to the content
                print('403 Forbidden')
                check_pass = False
            elif result.status_code == 404:   # Not Found
                print('404 Not Found')
                check_pass = False
            else:
                print(f'POST_ERROR, status_code:{result.status_code}')
                check_pass = False
        except Exception as e:
            # self.logger.exception(e)
            print(f'Exception : post_to_url, error msg:{e}')
            check_pass = False
        
        return check_pass

    def check(self, begining:bool, **my_data):
        if self.now_time_check():
            # print(f'check(begining={begining}, my_data={my_data})')

            self.get_macaddr()
            
            # my_data['user'] = self.macaddr
            my_data['user'] = f'{self.macaddr}{self.CPU_Name}{self.CPU_ProcessorId}{self.UUID}'
            # my_data['new_certificate_key'] = f'{self.macaddr}{self.CPU_Name}{self.CPU_ProcessorId}{self.UUID}'
            
            result = self.post_to_url(my_data=my_data)

            if result.find(self.PASS_MSG) != -1:
                if my_data['status'] == 'login':
                    my_data['status'] = 'login_success'
                    result = self.post_to_url(my_data=my_data)
                # print('CHECK SUCCESS')
                # print('-------------------')
            elif result == self.FAIL_MSG:
                self.my_var.is_exception = True
                self.my_var.NEED_TO_UPLOAD_ERROR_LOG = False
                print('CERTIFICATE_KEY_CHECK_FAILED')
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '此電腦的權限還沒開通, 請聯絡開發人員協助開通', '權限檢查', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
            elif result == self.VERSION_ERROR_MSG:
                self.my_var.is_exception = True
                self.my_var.NEED_TO_UPLOAD_ERROR_LOG = False
                print('VERSION_CHECK_ERROR')
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, f'錯誤! 請使用最新版 (您當前的版本是{my_data["version"]}版)', '版本檢查', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
            elif result == self.TIMEOUT_MSG:
                self.my_var.is_exception = True
                print(self.TIMEOUT_MSG)
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '錯誤! 網路認證超時, 請檢察目前網路是否可上網', '網路連線檢查', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
            elif result == self.SERVER_ERROR_MSG:
                self.my_var.is_exception = True
                self.my_var.NEED_TO_UPLOAD_ERROR_LOG = False
                print(self.SERVER_ERROR_MSG)
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '錯誤! 伺服器目前沒有回應, 請稍後再試, 如果一直沒有回應, 請通知開發人員', '網路連線檢查', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
            elif result == self.POST_ERROR_MSG:
                self.my_var.is_exception = True
                print(self.POST_ERROR_MSG)
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '錯誤! 權限檢查無法順利運行, 請通知開發人員', '網路連線檢查', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
            elif result == self.ENCRYPT_ERROR_MSG:
                self.my_var.is_exception = True
                print(self.ENCRYPT_ERROR_MSG)
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '錯誤! Encrypt ERROR', '加密錯誤', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
            elif result == self.DECRYPT_ERROR_MSG:
                self.my_var.is_exception = True
                print(self.DECRYPT_ERROR_MSG)
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '錯誤! Decrypt ERROR', '加密錯誤', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
            else:
                self.my_var.is_exception = True
                print('UNKNOWN ERROR')
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, '錯誤! 未知錯誤, 請通知開發人員', '權限檢查', 0)
                # sys.exit()
                # raise Exception('certificate check ERROR')
        else:
            self.my_var.is_exception = True
            self.my_var.NEED_TO_UPLOAD_ERROR_LOG = False
            print("timing check FAIL")
            MessageBox = ctypes.windll.user32.MessageBoxW
            MessageBox(None, '錯誤! 您的電腦上的時間與標準時間差距過大(大於1分鐘), 請把時間對準後再試一次', '中原標準時間檢查', 0)
            raise Exception('timing check FAIL')

    def encrypt_data(self, data:str) -> str:
        GMT8_time = datetime.utcnow() + timedelta(hours=8)
        now_key = self.get_now_key(now_time=GMT8_time)
        result_str = self.ENCRYPT_ERROR_MSG
        try:
            cipher = AES.new(now_key, AES.MODE_GCM)
            cipher.update(self.header)

            cipher_text, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
            nonce = cipher.nonce
            # print(cipher_text, len(cipher_text))
            # print(tag)
            # print(nonce)
            post_dict = {}
            post_dict['1'] = b64encode(cipher_text).decode('utf-8')
            post_dict['2'] = b64encode(tag).decode('utf-8')
            post_dict['3'] = b64encode(nonce).decode('utf-8')
            post_json_str = json.dumps(post_dict)
            result_str = post_json_str
        except Exception as e:
            pass
            # print(e)
            # print(self.ENCRYPT_ERROR_MSG)
    
        return result_str

    def decrypt_data(self, encrypt_json_str:str) -> str:
        GMT8_time = datetime.utcnow() + timedelta(hours=8)
        result_str = self.DECRYPT_ERROR_MSG
        for i in range(3):
            now_key = self.get_now_key(now_time=GMT8_time, retry=i)
            try:
                encrypt_dict = json.loads(encrypt_json_str)
                cipher_text = b64decode(encrypt_dict['1'])
                tag = b64decode(encrypt_dict['2'])
                nonce = b64decode(encrypt_dict['3'])
                decrypt_cipher = AES.new(now_key, AES.MODE_GCM, nonce=nonce)
                decrypt_cipher.update(self.header)
                plain_text = decrypt_cipher.decrypt_and_verify(cipher_text, tag)
                # print(plain_text.decode('utf-8'))
                result_str = plain_text.decode('utf-8')
                
            except Exception as e:
                pass
                # print(e)
                # print(self.DECRYPT_ERROR_MSG)
        
        return result_str

    def post_to_url(self, my_data):
        json_str = json.dumps(my_data)
        try:
            post_json_str = self.encrypt_data(json_str)
            if post_json_str == self.ENCRYPT_ERROR_MSG:
                return self.ENCRYPT_ERROR_MSG
            result = post(self.post_url, json=post_json_str, timeout=15)
            if result.status_code == 200:
                decrypt_str = self.decrypt_data(result.text)     # result.text is encrypt json string
                # print(decrypt_str)
                return decrypt_str
            elif result.status_code == 403:   # Forbidden, The client does not have access rights to the content
                print(f'POST_ERROR, status_code:{result.status_code}')
                return self.POST_ERROR_MSG
            elif result.status_code == 404:   # Not Found
                print(f'POST_ERROR, status_code:{result.status_code}')
                return self.SERVER_ERROR_MSG
            else:
                print(f'POST_ERROR, status_code:{result.status_code}')
                return self.POST_ERROR_MSG
        except Exception as e:
            # self.logger.exception(e)
            print(f'Exception : post_to_url, error msg:{e}')
            return self.TIMEOUT_MSG

def online_check():
    start_time = time.time()
    while(True):
        if my_var.is_exception == True or my_var.on_closing_flag == True:
            break
        if int(time.time() - start_time) >= 60*20:   # 20 min
            start_time = time.time()
            my_key.check(begining=False, status='online', version=VERSION)
        
        time.sleep(1)

def button_1(event):
    global x, y ,xstart, ystart, place_x1, place_y1, block_w, block_h
    global rec
    if cfg_x1 >= 1920:
        x = 1920 + root.winfo_pointerx() - root.winfo_rootx()
    else:
        x = root.winfo_pointerx() - root.winfo_rootx()
    y = root.winfo_pointery() - root.winfo_rooty()
    
    if x >= cfg_x1 and x < cfg_x2 and y >= cfg_y1 and y < cfg_y2:
        xstart, ystart = x, y
        #print("button 1 press : x, button 1 press : y = ", x, y)
        new_w = x - cfg_x1 + 1
        new_h = y - cfg_y1 + 1
        place_x1 = cfg_x1 + ((math.ceil(new_w/float(txt_w)) - 1) * txt_w)
        place_y1 = cfg_y1 + ((math.ceil(new_h/float(txt_h)) - 1) * txt_h)
        block_w = txt_w
        block_h = txt_h
        motion_cv.configure(width=block_w)
        motion_cv.configure(height=block_h)
        if cfg_x1 >= 1920:
            motion_cv.place(x=place_x1 - 1920, y=place_y1)
        else:
            motion_cv.place(x=place_x1, y=place_y1)
    else:
        motion_cv.place_forget()
        root.attributes("-alpha", 0)
        print('screen fail')
        sys_out(None)

def b1_Motion(event):
    global x, y, xstart, ystart, canvas_text_handle, canvas_text, place_x1, place_y1, block_w, block_h
    if cfg_x1 >= 1920:
        x = 1920 + root.winfo_pointerx() - root.winfo_rootx()
    else:
        x = root.winfo_pointerx() - root.winfo_rootx()
    y = root.winfo_pointery() - root.winfo_rooty()
    if x >= cfg_x1 and x < cfg_x2 and y >= cfg_y1 and y < cfg_y2:
        #print("event.x, event.y = ", x, y)
        if cfg_x1 >= 1920:
            canvas.place(x = x - 1920, y = y)
        else:
            canvas.place(x = x, y = y)
        canvas_text = 'press ESC to exit\n' + str(x - xstart) + ', ' + str(y - ystart)
        canvas.itemconfig(canvas_text_handle, text=canvas_text)

        new_w = x - place_x1 + 1
        new_h = y - place_y1 + 1
        block_w = math.ceil(new_w/float(txt_w)) * txt_w
        block_h = math.ceil(new_h/float(txt_h)) * txt_h
        if block_w >= cfg_x2-cfg_x1:
            block_w = cfg_x2-cfg_x1
        if block_h >= cfg_y2-cfg_y1:
            block_h = cfg_y2-cfg_y1
        motion_cv.configure(width=block_w)
        motion_cv.configure(height=block_h)

def buttonRelease_1(event):
    global xend, yend, place_x1, place_y1, block_w, block_h
    if cfg_x1 >= 1920:
        xend = 1920 + root.winfo_pointerx() - root.winfo_rootx()
    else:
        xend = root.winfo_pointerx() - root.winfo_rootx()
    yend = root.winfo_pointery() - root.winfo_rooty()
    if xend >= cfg_x1 and xend < cfg_x2 and yend >= cfg_y1 and yend < cfg_y2:
        if xend <= place_x1 or yend <= place_y1:
            motion_cv.place_forget()
            root.attributes("-alpha", 0)
            print('screen fail')
            sys_out(None)
        else:
            motion_cv.place_forget()
            root.attributes("-alpha", 0)
            #img = pyautogui.screenshot(region=[place_x1, place_y1, block_w, block_h]) # x,y,w,h
            img = ImageGrab.grab(bbox=(place_x1, place_y1, place_x1+block_w, place_y1+block_h), all_screens=True)
            #img.save('screenshot.png')
            img_np = np.array(img)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            # print(frame.shape)
            # for i in range(int(frame.shape[0]/18)):
            #     for j in range(int(frame.shape[1]/9)):
            #         print(i*18, j*9)

            ret, th1 = cv2.threshold(frame, 1, 255, cv2.THRESH_BINARY)
            # cv2.imshow("img", th1)
            # cv2.waitKey()
            #print(th1.shape)
            terminal_str = my_infer.infer(frame, vertical_num=int(th1.shape[0]/txt_h), horizontal_num=int(th1.shape[1]/txt_w), vim_mode=False)[0]
            if terminal_str[len(terminal_str)-1] == '\n':
                terminal_str = terminal_str[:-1]
            win_clip(terminal_str)
            print('-------------------- output -------------------------')
            print(terminal_str)
            sys_out(None)
    else:
        motion_cv.place_forget()
        root.attributes("-alpha", 0)
        print('screen fail')
        sys_out(None)

def my_motion_test(event=None):
    global place_x1, place_y1
    if cfg_x1 >= 1920:
        x = 1920 + root.winfo_pointerx() - root.winfo_rootx()
    else:
        x = root.winfo_pointerx() - root.winfo_rootx()
    y = root.winfo_pointery() - root.winfo_rooty()
    if x >= cfg_x1 and x < cfg_x2 and y >= cfg_y1 and y < cfg_y2:
        new_w = x - cfg_x1 + 1
        new_h = y - cfg_y1 + 1
        place_x1 = cfg_x1 + ((math.ceil(new_w/float(txt_w)) - 1) * txt_w)
        place_y1 = cfg_y1 + ((math.ceil(new_h/float(txt_h)) - 1) * txt_h)
        #print(x, y, place_x1, place_y1)
        motion_cv.configure(width=txt_w)
        motion_cv.configure(height=txt_h)
        if cfg_x1 >= 1920:
            motion_cv.place(x=place_x1 - 1920, y=place_y1)
        else:
            motion_cv.place(x=place_x1, y=place_y1)
    else:
        motion_cv.configure(width=1)
        motion_cv.configure(height=1)
    
def sys_out(even):
    root.destroy()


if __name__ == '__main__':
    my_infer = Inference(calibration=False)
    export_file_root = 'export/'

    print('Checking\n')

    my_var = Variables()
    my_key = Certificate_key(my_var=my_var)
    my_key.check(begining=True, status='login', version=VERSION)
    if my_var.is_exception:
        sys.exit()

    detect_stop_program_close()

    print('Start\n')

    t = Thread(target=online_check, daemon=True)
    t.start()

    while True:
        print('please input mode : 1.single file mode  2.recursive mode  3.terminal export  4.current opened file  5.screen  6.exit  7. single file mode binary  8. folder binary')
        choice = input()
        if my_var.is_exception:
            break
        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8']:
            print('please input 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8')
            continue
        
        if choice == '6':
            break
        elif choice == '1' or choice == '7':
            print('please input file name :')
            try:
                target_name = input()
            except:
                continue
            if target_name == '':
                print('ERROR! empty file name')
                continue
        elif choice == '8':
            print('please input file name :')
            try:
                target_name = input()
            except:
                continue
            if target_name == '':
                target_name = 'archive.tar.xz'

        if choice != '5':
            now = datetime.now()
            export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
            os.mkdir(export_dir_name)
            print('create folder : ' + export_dir_name)

        detect_stop_program_open()
        if choice == '3' or choice == '5':
            my_infer.active_nx()

        bg = BG()
        # print(bg.list_all_visible_windows())
        if bg.find_nx_hwnd():
            my_infer.set_bg_class(bg=bg)
            # print(bg.FrameArea_hwnd)
        else:
            # print('not found nx hwnd')
            continue

        if choice == '1':
            temp_str = my_infer.single_file_mode(target_name)
            my_infer.write_in_file(export_dir_name, target_name, temp_str)
        elif choice == '7':
            # my_infer.mp_screen_binary()
            binary_data = my_infer.single_file_mode_binary(target_name, export_dir_name, target_name)
            # my_infer.write_in_file_binary(export_dir_name, target_name, binary_data)
            # binary_data = base64.b64decode(temp_str)
            # my_infer.write_in_file_binary(export_dir_name, target_name, binary_data)
            # with open(output_file_path, 'wb') as outfile:
            #     outfile.write(binary_data)
        elif choice == '8':
            binary_data = my_infer.folder_mode_binary(target_name, export_dir_name)
        elif choice == '2':
            my_infer.recursive_mode(export_dir_name)
        elif choice == '3':
            img = my_infer.screen(vim_mode=False)
            terminal_str = my_infer.infer(img, vim_mode=False)[0]
            if terminal_str[len(terminal_str)-1] == '\n':
                terminal_str = terminal_str[:-1]
            print('-------------------- output -------------------------')
            print(terminal_str)
            f = open(export_dir_name + 'terminal.txt', 'w')
            f.write(terminal_str)
            f.close()
        elif choice == '4':
            my_infer.current_opened_file(export_dir_name)
        elif choice == '5':
            txt_w = my_infer.w
            txt_h = my_infer.h
            cfg_x1 = my_infer.x1
            cfg_y1 = my_infer.y1
            cfg_x2 = my_infer.x2
            cfg_y2 = my_infer.y2 + txt_h*1

            root = tk.Tk()
            root.overrideredirect(True)         # 隱藏視窗的標題列
            root.attributes("-alpha", 0.4)      # 視窗透明度30%
            root.attributes('-topmost', True)
            if cfg_x1 >= 1920:
                root.geometry("{0}x{1}+1920+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
            else:
                root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
            #root.configure(bg="black")

            x, y = 0, 0
            xstart,ystart = 0 ,0
            xend,yend = 0, 0
            rec = ''

            canvas = tk.Canvas(root)
            canvas.configure(width=120)
            canvas.configure(height=50)
            canvas.configure(bg="yellow")
            canvas.configure(highlightthickness=0)  # 高亮厚度
            if cfg_x1 >= 1920:
                canvas.place(x=1920+(root.winfo_screenwidth()-500), y=50)
            else:
                canvas.place(x=(root.winfo_screenwidth()-500), y=50)
            canvas_text = 'press ESC to exit'
            canvas_text_handle = canvas.create_text(60, 25,font='Arial -12 bold',text=canvas_text)

            place_x1 = 0
            place_y1 = 0
            block_w = 0
            block_h = 0
            motion_cv = tk.Canvas(root)
            # motion_cv.configure(width=cfg_x2-cfg_x1)
            # motion_cv.configure(height=cfg_y2-cfg_y1)
            motion_cv.configure(width=txt_w)
            motion_cv.configure(height=txt_h)
            motion_cv.configure(bg="red")
            motion_cv.config(highlightthickness=0) # 無邊框
            motion_cv.place(x=0, y=0)

            # 繫結事件
            #root.bind("<B1-Motion>", move)   # 滑鼠左鍵移動->顯示當前遊標位置
            root.bind('<Escape>',sys_out)      # 鍵盤Esc鍵->退出
            root.bind("<Button-1>", button_1)  # 滑鼠左鍵點選->顯示子視窗 
            root.bind("<B1-Motion>", b1_Motion)# 滑鼠左鍵移動->改變子視窗大小
            root.bind("<ButtonRelease-1>", buttonRelease_1) # 滑鼠左鍵釋放->記錄最後遊標的位置
            #root.bind("<Button-3>",button_3)   #滑鼠右鍵點選->截圖並儲存圖片
            root.bind("<Motion>", my_motion_test)
            root.mainloop()
        
        print('------------------------------------------')
        if get_exit_flag() == 1:
            break
        detect_stop_program_close()

    my_var.on_closing_flag = True
