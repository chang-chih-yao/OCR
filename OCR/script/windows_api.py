import win32api
import win32gui
import win32con

def detect_nx(targetTitle='NoMachine'):
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd),hWndList)
    #print(hWndList)
    for hwnd in hWndList:
        #clsname = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        #print(title)
        if (title.find(targetTitle) != -1):  #調整目標視窗到座標(600,300),大小設定為(600,600)
            rect = win32gui.GetWindowRect(hwnd)
            print(title)
            # print(rect)
            win32gui.ShowWindow(hwnd, 3)
            win32gui.SetForegroundWindow(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            print(rect)
            return rect[2]
            '''
            if (title.find('screen') != -1):
                print('OK')
                print(title)
                print(rect)
                # win32gui.SetWindowPos(hwnd,win32con.HWND_NOTOPMOST,10,10,1920, 1080, win32con.SWP_SHOWWINDOW)
                win32gui.ShowWindow(hwnd, 3)
                win32gui.SetForegroundWindow(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                print(rect)
                if rect[2] - rect[0] > 1940:
                    print('GG')
            '''
    return -9999

if __name__ == '__main__':
    print(detect_nx('NoMachine'))
