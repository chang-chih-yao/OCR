import tkinter as tk
from PIL import ImageGrab
import cv2
import numpy as np
import pynput
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput import keyboard
import time

def on_press(key):
    '''
    press backspace key on your keyboard anytime to stop program
    '''
    global my_event
    
    if key == Key.backspace:
        print('exit()')
        my_event = 1
        sys_out(None)
        cv.delete(rec)
        cv.place_forget()
        return False

def move(event):
    global x, y ,xstart,ystart
    new_x = (event.x-x)+canvas.winfo_x()
    new_y = (event.y-y)+canvas.winfo_y()
    s = "300x200+" + str(new_x)+"+" + str(new_y)    
    canvas.place(x = new_x - xstart,y = new_y -ystart)   
    print("s = ", s)
    print(root.winfo_x(), root.winfo_y())
    print(event.x, event.y)

def button_1(event):
    global x, y ,xstart,ystart
    global rec
    x, y = event.x, event.y
    xstart,ystart = event.x, event.y
    print("event.x, event.y = ", event.x, event.y)
    xstart,ystart = event.x, event.y  
    cv.configure(height=1)
    cv.configure(width=1)
    cv.config(highlightthickness=0) # 無邊框
    cv.place(x=event.x, y=event.y)
    rec = cv.create_rectangle(0,0,0,0,outline='red',width=8,dash=(4, 4))

def b1_Motion(event):
    global x, y,xstart,ystart
    x, y = event.x, event.y
    #print("event.x, event.y = ", event.x, event.y)
    cv.configure(height = event.y - ystart)
    cv.configure(width = event.x - xstart)
    cv.coords(rec,0,0,event.x-xstart,event.y-ystart)

def buttonRelease_1(event):
    global xstart,ystart,xend,yend, my_event
    xend, yend = event.x, event.y

    image = ImageGrab.grab(bbox=(xstart, ystart, xend, yend), all_screens=True)
    width, height = image.size
    print(width, height)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter('test.avi', fourcc, 10, (width, height))
    frame_cou = 0
    start_time = time.time()
    while True:
        img_rgb = ImageGrab.grab(bbox=(xstart, ystart, xend, yend), all_screens=True)
        img_bgr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
        video.write(img_bgr)
        #cv2.imshow('imm', img_bgr)
        #print(frame_cou)
        print(1/(time.time() - start_time))
        start_time = time.time()
        frame_cou += 1
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.waitKey(1)
        if my_event == 1:
            break

    video.release()
    #cv2.destroyAllWindows()
'''
def button_3(event):
    global xstart,ystart,xend,yend, my_event
    print('exit')
    my_event = 1
    cv.delete(rec)
    cv.place_forget()
    #img = pyautogui.screenshot(region=[xstart,ystart,xend-xstart,yend-ystart]) # x,y,w,h
    
    sys_out(None)
'''
def sys_out(even):
    root.destroy()

root = tk.Tk()
root.overrideredirect(True)         # 隱藏視窗的標題列
root.attributes("-alpha", 0.1)      # 視窗透明度10%
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.configure(bg="black")

# 再建立1個Canvas用於圈選
cv = tk.Canvas(root)
x, y = 0, 0
xstart,ystart = 0 ,0
xend,yend = 0, 0
rec = ''
my_event = 0

my_keyboard = pynput.keyboard.Controller()
my_mouse = pynput.mouse.Controller()

exit_flag = 0
listener = keyboard.Listener(on_press=on_press)
listener.start()

canvas = tk.Canvas(root)
canvas.configure(width=300)
canvas.configure(height=100)
canvas.configure(bg="yellow")
canvas.configure(highlightthickness=0)  # 高亮厚度
canvas.place(x=(root.winfo_screenwidth()-500),y=(root.winfo_screenheight()-300))
canvas.create_text(150, 50,font='Arial -20 bold',text='ESC退出，假裝工具條')

# 繫結事件
canvas.bind("<B1-Motion>", move)   # 滑鼠左鍵移動->顯示當前遊標位置
root.bind('<Escape>',sys_out)      # 鍵盤Esc鍵->退出
root.bind("<Button-1>", button_1)  # 滑鼠左鍵點選->顯示子視窗 
root.bind("<B1-Motion>", b1_Motion)# 滑鼠左鍵移動->改變子視窗大小
root.bind("<ButtonRelease-1>", buttonRelease_1) # 滑鼠左鍵釋放->記錄最後遊標的位置
#root.bind("<Button-3>",button_3)   #滑鼠右鍵點選->截圖並儲存圖片
root.mainloop()