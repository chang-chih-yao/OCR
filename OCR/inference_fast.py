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

from script.keyboard_mouse_ctrl import mouse_click, my_type, detect_stop_program_open, detect_stop_program_close, get_exit_flag
from script.windows_api import message_box, win_clip
from script.inference_core import Inference
from script.cfg import load_cfg

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

    print('Start\n')

    detect_stop_program_close()

    while True:
        print('please input mode : 1.single file mode  2.recursive mode  3.terminal export  4.current opened file  5.screen  6.exit')
        choice = input()
        if choice != '1' and choice != '2' and choice != '3' and choice != '4' and choice != '5' and choice != '6':
            print('please input 1 or 2 or 3 or 4 or 5 or 6')
            continue
        
        if choice == '6':
            break
        elif choice == '1':
            print('please input file name :')
            target_name = input()

        if choice != '5':
            now = datetime.now()
            export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
            os.mkdir(export_dir_name)
            print('create folder : ' + export_dir_name)

        detect_stop_program_open()
        my_infer.active_nx()

        if choice == '1':
            temp_str = my_infer.single_file_mode(target_name)
            my_infer.write_in_file(export_dir_name, target_name, temp_str)
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
            cfg_y2 = my_infer.y2 + txt_h*2

            root = tk.Tk()
            root.overrideredirect(True)         # ????????????????????????
            root.attributes("-alpha", 0.4)      # ???????????????30%
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
            canvas.configure(highlightthickness=0)  # ????????????
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
            motion_cv.config(highlightthickness=0) # ?????????
            motion_cv.place(x=0, y=0)

            # ????????????
            #root.bind("<B1-Motion>", move)   # ??????????????????->????????????????????????
            root.bind('<Escape>',sys_out)      # ??????Esc???->??????
            root.bind("<Button-1>", button_1)  # ??????????????????->??????????????? 
            root.bind("<B1-Motion>", b1_Motion)# ??????????????????->?????????????????????
            root.bind("<ButtonRelease-1>", buttonRelease_1) # ??????????????????->???????????????????????????
            #root.bind("<Button-3>",button_3)   #??????????????????->?????????????????????
            root.bind("<Motion>", my_motion_test)
            root.mainloop()
        
        print('------------------------------------------')
        if get_exit_flag() == 1:
            break
        detect_stop_program_close()
