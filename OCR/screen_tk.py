from PIL import ImageGrab
import tkinter as tk
import math
import numpy as np
import cv2

def move(event):
    global x, y ,xstart,ystart
    # new_x = (event.x-x)+canvas.winfo_x()
    # new_y = (event.y-y)+canvas.winfo_y()
    # s = "300x200+" + str(new_x)+"+" + str(new_y)    
    # canvas.place(x = new_x - xstart,y = new_y -ystart)
    canvas.place(x = event.x, y = event.y)
    # print("s = ", s)
    print(root.winfo_x(), root.winfo_y())
    print(event.x, event.y)

def button_1(event):
    global x, y ,xstart, ystart, place_x1, place_y1, block_w, block_h
    global rec
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
        motion_cv.place(x=place_x1, y=place_y1)
    else:
        motion_cv.place_forget()
        root.attributes("-alpha", 0)
        print('screen fail')
        sys_out(None)

def b1_Motion(event):
    global x, y, xstart, ystart, canvas_text_handle, canvas_text, place_x1, place_y1, block_w, block_h
    x = root.winfo_pointerx() - root.winfo_rootx()
    y = root.winfo_pointery() - root.winfo_rooty()
    if x >= cfg_x1 and x < cfg_x2 and y >= cfg_y1 and y < cfg_y2:
        #print("event.x, event.y = ", x, y)
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
    xend, yend = root.winfo_pointerx() - root.winfo_rootx(), root.winfo_pointery() - root.winfo_rooty()
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
            img_np = np.array(img)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            ret, th1 = cv2.threshold(frame, 1, 255, cv2.THRESH_BINARY)
            img.save('screenshot.png')
            # cv2.imshow("img", th1)
            # cv2.waitKey()
            sys_out(None)
    else:
        motion_cv.place_forget()
        root.attributes("-alpha", 0)
        print('screen fail')
        sys_out(None)

def button_3(event):
    global xstart,ystart,xend,yend
    root.attributes("-alpha", 0)
    #img = pyautogui.screenshot(region=[xstart,ystart,xend-xstart,yend-ystart]) # x,y,w,h
    img = ImageGrab.grab(bbox=(place_x1, place_y1, place_x1+block_w, place_y1+block_h), all_screens=True)
    img.save('screenshot.png')
    sys_out(None)

def my_motion_test(event=None):
    global place_x1, place_x2, place_y1, place_y2
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
        motion_cv.place(x=place_x1, y=place_y1)
    else:
        motion_cv.configure(width=1)
        motion_cv.configure(height=1)
    

def sys_out(even):
    root.destroy()


root = tk.Tk()
root.overrideredirect(True)         # 隱藏視窗的標題列
root.attributes("-alpha", 0.3)      # 視窗透明度30%
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
canvas.place(x=(root.winfo_screenwidth()-500), y=50)
canvas_text = 'press ESC to exit'
canvas_text_handle = canvas.create_text(60, 25,font='Arial -12 bold',text=canvas_text)


txt_w = 9
txt_h = 18
cfg_x1 = 1
cfg_y1 = 144
cfg_x2 = 1900
cfg_y2 = 972 + txt_h*2
place_x1 = 0
place_x2 = 0
place_y1 = 0
place_y2 = 0
block_w = 0
block_h = 0
motion_cv = tk.Canvas(root)
# motion_cv.configure(width=cfg_x2-cfg_x1)
# motion_cv.configure(height=cfg_y2-cfg_y1)
motion_cv.configure(width=txt_w)
motion_cv.configure(height=txt_h)
motion_cv.configure(bg="red")
motion_cv.config(highlightthickness=0) # 無邊框
motion_cv.place(x=cfg_x1, y=cfg_y1)

# 繫結事件
#root.bind("<B1-Motion>", move)   # 滑鼠左鍵移動->顯示當前遊標位置
root.bind('<Escape>',sys_out)      # 鍵盤Esc鍵->退出
root.bind("<Button-1>", button_1)  # 滑鼠左鍵點選->顯示子視窗 
root.bind("<B1-Motion>", b1_Motion)# 滑鼠左鍵移動->改變子視窗大小
root.bind("<ButtonRelease-1>", buttonRelease_1) # 滑鼠左鍵釋放->記錄最後遊標的位置
#root.bind("<Button-3>",button_3)   #滑鼠右鍵點選->截圖並儲存圖片
root.bind("<Motion>", my_motion_test)
root.mainloop()