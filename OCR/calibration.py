import time
from datetime import datetime
import os
import cv2
import sys
from filecmp import cmp, dircmp
from PIL import ImageGrab
import tkinter as tk
import math

from scripts.gen_dataset_fast import gen_data
from scripts.gen_training_data_fast import gen_train
# from scripts.load_model import load_model
from scripts.cfg import build_cfg, load_cfg, modify_cfg
from scripts.windows_api import message_box, win_clip
from scripts.keyboard_mouse_ctrl import my_type, mouse_click, open_vim, quit_vim
from scripts.inference_core import Inference
from scripts.background_utility import BG

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
            # motion_cv.place_forget()
            # root.attributes("-alpha", 0)
            #img = pyautogui.screenshot(region=[place_x1, place_y1, block_w, block_h]) # x,y,w,h
            img = ImageGrab.grab(bbox=(place_x1, place_y1, place_x1+block_w, place_y1+block_h), all_screens=True)
            print(place_x1, place_y1, place_x1+block_w, place_y1+block_h)
            my_infer.x1 = place_x1
            my_infer.y1 = place_y1
            my_infer.x2 = place_x1+block_w
            my_infer.y2 = place_y1+block_h
            #img.save('screenshot.png')
            # img_np = np.array(img)
            # frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            # # print(frame.shape)
            # # for i in range(int(frame.shape[0]/18)):
            # #     for j in range(int(frame.shape[1]/9)):
            # #         print(i*18, j*9)

            # ret, th1 = cv2.threshold(frame, 1, 255, cv2.THRESH_BINARY)
            
            # sys_out(None)
    else:
        motion_cv.place_forget()
        root.attributes("-alpha", 0)
        print('screen fail')
        sys_out(None)

def mouse_motion(event=None):
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

def down_key(even):
    global cfg_y1, cfg_y2
    cfg_y1 += 1

def up_key(even):
    global cfg_y1, cfg_y2
    if cfg_y1 > 0:
        cfg_y1 -= 1

def left_key(even):
    global cfg_x1, cfg_x2
    if cfg_x1 > 0:
        cfg_x1 -= 1

def right_key(even):
    global cfg_x1, cfg_x2
    cfg_x1 += 1


def sys_out(even):
    root.destroy()

def program_exit(even):
    root.destroy()
    sys.exit()


def find_contour(img):
    img_copy = img.copy()
    bg_color = img_copy[0, 0]   # assume [0, 0] is bg color
    for a in range(img_copy.shape[0]):
        for b in range(img_copy.shape[1]):
            if img_copy[a, b] == bg_color:
                img_copy[a, b] = 0
            else:
                img_copy[a, b] = 255
    # cv2.imshow("origin", th1) 
    contours, hierarchy = cv2.findContours(img_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(img_copy,contours,-1,(0,255,255),1) 
    
    cnt = contours[0]
    M = cv2.moments(cnt)
    print( M )
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    print('------------')
    print(cx)
    print(cy)
    print('------------')
    area = cv2.contourArea(cnt)
    print(area)
    print('------------')
    perimeter = cv2.arcLength(cnt,True)
    print(perimeter)

    x,y,w,h = cv2.boundingRect(cnt)
    print('------------')
    print(x)
    print(y)
    print(w)
    print(h)
    # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
    # cv2.imshow("drawContours", img) 
    # cv2.waitKey(0)
    return x, y, w, h

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

def my_file_cmp(a, b):
    with open(a, 'r') as f_a:
        a_lines = f_a.readlines()
    with open(b, 'r') as f_b:
        b_lines = f_b.readlines()
    
    return a_lines == b_lines























def screen_button_1(event):
    global screen_x, screen_y ,screen_xstart,screen_ystart
    global screen_rec
    if cfg_x1 >= 1920:
        screen_x = 1920 + screen_root.winfo_pointerx() - screen_root.winfo_rootx()
    else:
        screen_x = screen_root.winfo_pointerx() - screen_root.winfo_rootx()
    screen_y = screen_root.winfo_pointery() - screen_root.winfo_rooty()
    
    screen_xstart,screen_ystart = event.x, event.y
    #print("event.x, event.y = ", event.x, event.y)
    screen_xstart,screen_ystart = event.x, event.y 
    screen_cv.configure(height=1)
    screen_cv.configure(width=1)
    screen_cv.config(highlightthickness=0) # 無邊框
    screen_cv.place(x=event.x, y=event.y)
    screen_rec = screen_cv.create_rectangle(0,0,0,0)

def screen_b1_Motion(event):
    global screen_x, screen_y, screen_xstart, screen_ystart
    if cfg_x1 >= 1920:
        screen_x = 1920 + screen_root.winfo_pointerx() - screen_root.winfo_rootx()
    else:
        screen_x = screen_root.winfo_pointerx() - screen_root.winfo_rootx()
    screen_y = screen_root.winfo_pointery() - screen_root.winfo_rooty()
    #print("event.x, event.y = ", event.x, event.y)
    screen_cv.configure(height = event.y - screen_ystart)
    screen_cv.configure(width = event.x - screen_xstart)
    screen_cv.coords(screen_rec,0,0,event.x-screen_xstart,event.y-screen_ystart)

def screen_buttonRelease_1(event):
    global screen_xend,screen_yend
    if cfg_x1 >= 1920:
        screen_xend = 1920 + screen_root.winfo_pointerx() - screen_root.winfo_rootx()
    else:
        screen_xend = screen_root.winfo_pointerx() - screen_root.winfo_rootx()
    screen_yend = screen_root.winfo_pointery() - screen_root.winfo_rooty()

def save_img(event):
    global screen_xstart,screen_ystart,screen_xend,screen_yend
    screen_cv.delete(screen_rec)
    screen_cv.place_forget()
    screen_root.attributes("-alpha", 0)
    #img = pyautogui.screenshot(region=[screen_xstart, screen_ystart, screen_xend-screen_xstart, screen_yend-screen_ystart]) # x,y,w,h
    img = ImageGrab.grab(bbox=(screen_xstart, screen_ystart, screen_xend, screen_yend), all_screens=True)
    img.save('block_template.png')
    print('block_template.png save completely')
    screen_root.destroy()

def screen_sys_out(even):
    screen_root.destroy()
    sys.exit()


infer_tmp = Inference(calibration=True)
bg = BG()
if bg.find_nx_hwnd():
    infer_tmp.set_bg_class(bg=bg)
else:
    sys.exit()

infer_tmp.active_nx()
txt_w = infer_tmp.w
txt_h = infer_tmp.h
cfg_x1 = infer_tmp.x1
cfg_y1 = infer_tmp.y1
cfg_x2 = infer_tmp.x2
cfg_y2 = infer_tmp.y2 + txt_h*2
my_type('cd /rsc/R7227/')
my_type('enter_key')
my_type('enter_key')
my_type('enter_key')
my_type('       ')
my_type('enter_key')
my_type('       ')

time.sleep(3)




screen_root = tk.Tk()
screen_root.overrideredirect(True)  # 隱藏視窗的標題列
screen_root.attributes("-alpha", 0.3) # 視窗透明度30%
screen_root.attributes('-topmost', True)
if cfg_x1 >= 1920:
    screen_root.geometry("{0}x{1}+1920+0".format(screen_root.winfo_screenwidth(), screen_root.winfo_screenheight()))
else:
    screen_root.geometry("{0}x{1}+0+0".format(screen_root.winfo_screenwidth(), screen_root.winfo_screenheight()))
screen_root.configure(bg="black")

# 再建立1個Canvas用於圈選
screen_cv = tk.Canvas(screen_root)
screen_cv.config(highlightthickness=0) # 無邊框
screen_x, screen_y = 0, 0
screen_xstart,screen_ystart = 0 ,0
screen_xend,screen_yend = 0, 0
screen_rec = ''

screen_root.bind('<Escape>',screen_sys_out) # 鍵盤Esc鍵->退出
screen_root.bind("<Button-1>", screen_button_1) # 滑鼠左鍵點選->顯示子視窗 
screen_root.bind("<B1-Motion>", screen_b1_Motion)# 滑鼠左鍵移動->改變子視窗大小
screen_root.bind("<ButtonRelease-1>", screen_buttonRelease_1) # 滑鼠左鍵釋放->記錄最後遊標的位置
screen_root.bind("<Return>",save_img) #滑鼠右鍵點選->截圖並儲存圖片
screen_root.mainloop()



time.sleep(1)



img = cv2.imread("block_template.png")
my_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
detect_bias_x, detect_bias_y, detect_w, detect_h = find_contour(my_img)
print('----------------')
print(screen_xstart, screen_ystart)
print(detect_bias_x, detect_bias_y)
print(detect_w, detect_h)
modify_cfg('w', detect_w)
modify_cfg('h', detect_h)



my_infer = Inference(calibration=True)
if bg.find_nx_hwnd():
    my_infer.set_bg_class(bg=bg)
else:
    sys.exit()
my_config = load_cfg()

my_infer.active_nx()

my_type('cd open/export_file')
my_type('enter_key')
my_type('vim -u NONE -R calibration.txt')
my_type('enter_key')

my_infer.x1 = (screen_xstart + detect_bias_x) % detect_w
my_infer.y1 = (screen_ystart + detect_bias_y) % detect_h
txt_w = my_infer.w
txt_h = my_infer.h
cfg_x1 = my_infer.x1
cfg_y1 = my_infer.y1
cfg_x2 = my_infer.x2
cfg_y2 = my_infer.y2 + txt_h*2






root = tk.Tk()
root.overrideredirect(True)         # 隱藏視窗的標題列
root.attributes("-alpha", 0.4)      # 視窗透明度40%
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
root.bind('<Escape>',program_exit)      # 鍵盤Esc鍵->退出
root.bind('<Return>',sys_out)      # 鍵盤Esc鍵->退出
root.bind("<Button-1>", button_1)  # 滑鼠左鍵點選->顯示子視窗 
root.bind("<B1-Motion>", b1_Motion)# 滑鼠左鍵移動->改變子視窗大小
root.bind("<ButtonRelease-1>", buttonRelease_1) # 滑鼠左鍵釋放->記錄最後遊標的位置
#root.bind("<Button-3>",button_3)   #滑鼠右鍵點選->截圖並儲存圖片
root.bind("<Motion>", mouse_motion)
root.bind("<Up>", up_key)
root.bind("<Down>", down_key)
root.bind("<Left>", left_key)
root.bind("<Right>", right_key)
root.mainloop()


quit_vim()

target_name = 'calibration.txt'
export_file_root = 'export/'

if os.path.isdir(export_file_root):
    pass
else:
    os.mkdir(export_file_root)


print('Start\n')


open_vim(target_name)
my_type(':4')
time.sleep(0.5)
img = my_infer.screen()
# cv2.imshow("img", img)
# cv2.waitKey()
# sys.exit()

my_infer.active_nx()

print('build new model')
threshold = int(my_config['cust']['threshold'])
# cv2.imshow("img", img)
# cv2.waitKey()
print(my_infer.x1, my_infer.x2, my_infer.y1, my_infer.y2, my_infer.w, my_infer.h)
gen_data(img, difference=my_infer.difference, threshold=threshold, w=my_infer.w, h=my_infer.h)
gen_train()
# my_infer.char_list, my_infer.data_set_num, my_infer.category, my_infer.img_arr = load_model(w=my_infer.w, h=my_infer.h)
my_infer.infer_load_model()

img = my_infer.screen()
temp_str = my_infer.infer(img, vertical_num=1, horizontal_num=len(my_infer.char_list) + my_infer.vim_text_bias_width)[0]
print('detect :|' + temp_str + '|')
if temp_str == my_infer.char_list:
    print('char list correct')
else:
    print('Error !!!!')
    quit_vim()
    sys.exit()


my_infer.vertical_and_horizontal_num_update()
quit_vim()


#------------------------- check and compare export file ---------------------------#
now = datetime.now()
export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
os.mkdir(export_dir_name)

temp_str = my_infer.single_file_mode(target_name)
my_infer.write_in_file(export_dir_name, target_name, temp_str)

if my_file_cmp('compare_file/calibration.txt', export_dir_name + target_name):
    modify_cfg('x1', my_infer.x1)
    modify_cfg('y1', my_infer.y1)
    modify_cfg('x2', my_infer.x2)
    modify_cfg('y2', my_infer.y2)
else:
    print('----------------')
    print('calibration FAIL !!!!!!!')
    sys.exit()

my_type('clear')
my_type('enter_key')
my_type('clear')
my_type('enter_key')
my_type('python bold_gen.py')
my_type('enter_key')
img = my_infer.screen(vim_mode=False)
# ret, th1 = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
gen_data(img[my_infer.h:, :], difference=my_infer.difference, threshold=threshold, append_new_data=True, dataset_name='binary_data_bold_', w=my_infer.w, h=my_infer.h)
gen_train()
# my_infer.char_list, my_infer.data_set_num, my_infer.category, my_infer.img_arr = load_model(w=my_infer.w, h=my_infer.h)
my_infer.infer_load_model()

temp_str = my_infer.infer(img, vim_mode=False)[0]
# temp_str, file_eof, line_cou = my_infer.infer(img, vertical_num=my_infer.y2//my_infer.h, horizontal_num=(my_infer.x2-my_infer.x1)//my_infer.w, vim_mode=False)
# temp_str, file_eof, line_cou = my_infer.infer(img, vertical_num=my_infer.y2//my_infer.h, horizontal_num=(my_infer.x2-my_infer.x1)//my_infer.w, vim_mode=False)
print(temp_str)
print('---------------------------')
print(temp_str.split('\n')[1])
print('---------------------------')
correct_str = '        abcdefghijklmnopqrstuvwxyz1234567890`-=[]\\;\',./ ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?'
if temp_str.split('\n')[1] == correct_str:
    print('\n----------------')
    print('calibration PASS !!!!')
    print('now you can use inference_fast.py script')
else:
    print('\n----------------')
    print('calibration FAIL !!!!!!!')
    for i in range(len(correct_str)):
        if temp_str.split('\n')[1][i] != correct_str[i]:
            print(temp_str.split('\n')[1][i], correct_str[i])
    sys.exit()

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
        sys.exit()

