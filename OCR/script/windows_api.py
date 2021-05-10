import win32api
import win32gui
import win32ui
import win32con
import win32clipboard
import time
import cv2
import numpy as np
from PIL import ImageGrab

def screen(x1, y1, x2, y2, threshold=1):
    print(x1, y1, x2, y2)
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    return frame

def get_windows_handle(targetTitle):
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd),hWndList)
    for hwnd in hWndList:
        #clsname = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        #print(title)
        if (title.find(targetTitle) != -1):
            print(title)
            rect = win32gui.GetWindowRect(hwnd)
            print(rect)
            return hwnd
            '''
            if (title.find('screen') != -1):
                print('OK')
                print(title)
                # win32gui.SetWindowPos(hwnd,win32con.HWND_NOTOPMOST,10,10,1920, 1080, win32con.SWP_SHOWWINDOW)
                rect = win32gui.GetWindowRect(hwnd)
                print(rect)
                return hwnd
            '''
    return 0

def active_window(hwnd):
    win32gui.ShowWindow(hwnd, 3)
    win32gui.SetForegroundWindow(hwnd)

def get_windows_location(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    return rect[2]

def detect_nx(targetTitle='NoMachine'):
    another_monitor = False
    is_nx_active = False
    hwnd = get_windows_handle(targetTitle)
    active_window(hwnd)
    if hwnd == 0:
        print('not found NoMachine!!!')
        return hwnd, is_nx_active, another_monitor
    elif get_windows_location(hwnd) > 2000:
        another_monitor = True
        is_nx_active = True
        print('nx in second monitor')
        return hwnd, is_nx_active, another_monitor
    else:
        another_monitor = False
        is_nx_active = True
        print('nx in first monitor')
        return hwnd, is_nx_active, another_monitor

def win_clip(my_str=''):
    '''
    Copy the string to the windows clipboard.
    my_str : string
    '''
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, my_str)
    win32clipboard.CloseClipboard()

def background_screenshot(hwnd, width, height):
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(width, height) , dcObj, (0,0), win32con.SRCCOPY)
    print(dataBitMap.GetInfo())
    img = np.array(dataBitMap.GetBitmapBits(), dtype=np.uint8)
    img = np.reshape(img, (height, width, 4))
    img = img[:, :, 0:3].copy()
    # print(img)
    # print(img.shape)
    # print(img.dtype)

    #dataBitMap.SaveBitmapFile(cDC, 'screenshot.bmp')
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return frame

def active_window_title():
    return str(win32gui.GetWindowText(win32gui.GetForegroundWindow()))

def message_box(hwnd, my_str):
    choice = win32api.MessageBox(hwnd, my_str, 'Notation !', win32con.MB_YESNO)
    #print(choice)
    if choice == 6:
        print('user select yes')
        return 1
    elif choice == 7:
        print('user select no')
        return 0
    else:
        print('message_box select error')
        return -1

'''
def send_input_text(hwnd, my_str=''):
    win_clip(my_str)
    print('win_clip OK')
    time.sleep(1)
    # win32clipboard.OpenClipboard()
    # d = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    # print(d)
    #win32gui.SendMessage(hwnd, win32con.WM_PASTE, 0, 0)
    temp = win32gui.SendMessage(hwnd, win32con.WM_CHAR, ord('x'), 0)
    #print(temp)
    print('done')
    # win32clipboard.CloseClipboard()

def winfun(hwnd, lparam):
    s = win32gui.GetWindowText(hwnd)
    
    if len(s) > 3:
        send_input_text(hwnd, 'test\nfsdff\n')
        print("winfun, child_hwnd: %d   txt: %s" % (hwnd, s))
    return 1
'''

if __name__ == '__main__':
    # print(detect_nx())
    # win_clip('test\nhahahah\n\n\nzzz  \n')
    
    #time.sleep(1)
    hwnd = get_windows_handle('Notepad', active_window=True)
    #win32gui.EnumChildWindows(hwnd, winfun, None)

    #send_input_text(197734, 'test\nfsdff\n')
    # message_box(hwnd, 'test str')
    # start_time = time.time()
    # img1 = background_screenshot(hwnd, 200, 300)
    # print(time.time()-start_time)
    # img2 = screen(0, 0, 200, 300)
    # print(time.time()-start_time)
    # cv2.imshow("img1", img1)
    # cv2.imshow("img2", img2)
    # cv2.waitKey()
    # print(img1.shape)
    # print(img1.dtype)
    # print(img2.shape)
    # print(img2.dtype)
    # diff = img1 - img2
    # print(diff)
    # if np.all((diff.flatten() == 0)):
    #     print('same')
    
    #print(win32gui.GetWindowPlacement(hwnd))

    

    # while True:
    #     if active_window_title().find('NoMachine') != -1:
    #         print('active')
    #     else:
    #         print('non_active')
    #     time.sleep(1)