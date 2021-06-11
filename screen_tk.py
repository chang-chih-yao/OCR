import pyautogui
import tkinter as tk

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
    print("event.x, event.y = ", event.x, event.y)
    cv.configure(height = event.y - ystart)
    cv.configure(width = event.x - xstart)
    cv.coords(rec,0,0,event.x-xstart,event.y-ystart)

def buttonRelease_1(event):
    global xend,yend
    xend, yend = event.x, event.y

def button_3(event):
    global xstart,ystart,xend,yend
    cv.delete(rec)
    cv.place_forget()
    img = pyautogui.screenshot(region=[xstart,ystart,xend-xstart,yend-ystart]) # x,y,w,h
    img.save('screenshot.png')
    sys_out(None)

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
root.bind("<Button-3>",button_3)   #滑鼠右鍵點選->截圖並儲存圖片
root.mainloop()