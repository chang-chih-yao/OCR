from time import sleep
import win32gui, win32ui, win32con, win32api

def active_window(hwnd):
    win32gui.ShowWindow(hwnd, 3)
    win32gui.SetForegroundWindow(hwnd)

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

def main():
    #window_name = "test.txt"
    #hwnd = win32gui.FindWindow(None, window_name)
    hwnd = get_windows_handle('NoMachine')
    #active_window(hwnd)
    hwnd = get_inner_windows(hwnd)['QWidget']
    win = win32ui.CreateWindowFromHandle(hwnd)

    win.SendMessage(win32con.WM_CHAR, ord('A'), 0)
    sleep(0.5)
    win.SendMessage(win32con.WM_CHAR, ord('B'), 0)
    #win.SendMessage(win32con.WM_KEYDOWN, 0x1E, 0)
    #sleep(0.5)
    #win.SendMessage(win32con.WM_KEYUP, 0x1E, 0)
    for i in range(20):
        # key codes : https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x41, 0)
        sleep(0.1)
        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x41, 0)
        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x42, 0)
        sleep(0.1)
        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x42, 0)
        
    # send mouse click : https://stackoverflow.com/questions/59285854/is-there-a-way-to-send-a-click-event-to-a-window-in-the-background-in-python

def get_inner_windows(whndl):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            hwnds[win32gui.GetClassName(hwnd)] = hwnd
        return True
    hwnds = {}
    win32gui.EnumChildWindows(whndl, callback, hwnds)
    print(hwnds)
    return hwnds

main()