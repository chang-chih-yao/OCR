import win32gui, win32ui, win32con, win32api
import time
import cv2
import numpy as np
import sys
from .keyboard_mouse_ctrl import get_exit_flag, type_speed, cmd_speed
from .cfg import load_cfg

# 常用虛擬鍵碼 (VK_CODE)
VK_CODES = {
    # 字母鍵
    'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45,
    'F': 0x46, 'G': 0x47, 'H': 0x48, 'I': 0x49, 'J': 0x4A,
    'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E, 'O': 0x4F,
    'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
    'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58, 'Y': 0x59,
    'Z': 0x5A,
    
    # 數字鍵（主鍵盤）
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    
    # 功能鍵
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
    'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
    
    # 控制鍵
    'ENTER': 0x0D,
    'ESC': 0x1B,
    'SPACE': 0x20,
    'TAB': 0x09,
    'BACKSPACE': 0x08,
    'SHIFT': 0x10,
    'CTRL': 0x11,
    'ALT': 0x12,
    'DELETE': 0x2E,
    'HOME': 0x24,
    'END': 0x23,
    'PAGE_UP': 0x21,
    'PAGE_DOWN': 0x22,
    
    # 方向鍵
    'LEFT': 0x25,
    'UP': 0x26,
    'RIGHT': 0x27,
    'DOWN': 0x28,
    
    # 小鍵盤數字鍵
    'NUMPAD0': 0x60, 'NUMPAD1': 0x61, 'NUMPAD2': 0x62,
    'NUMPAD3': 0x63, 'NUMPAD4': 0x64, 'NUMPAD5': 0x65,
    'NUMPAD6': 0x66, 'NUMPAD7': 0x67, 'NUMPAD8': 0x68,
    'NUMPAD9': 0x69,
}

class BG:
    def __init__(self) -> None:
        self.FrameArea_hwnd = 0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.w = 0
        self.h = 0

        self.virtual_key = [0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5A, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0xC0, 0xBD, 0xBB, 0xDB, 0xDD, 0xDC, 0xBA, 0xDE, 0xBC, 0xBE, 0xBF, 0x20]
        self.no_shift_char = "abcdefghijklmnopqrstuvwxyz0123456789`-=[]\\;',./ "      # 48 chars  最後多一個空白鍵
        self.shift_char    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?'        # 47 chars
    
    def list_all_visible_windows(self):
        all_titles = []
        win32gui.EnumWindows(self.enum_all_visible_windows, all_titles)
        return all_titles
        
    def enum_all_visible_windows(self, hwnd, titles):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and title != '':
                titles.append(title)

    def MyCallback(self, hwnd, extra):
        windows = extra
        temp=[]
        temp.append(hex(hwnd))
        temp.append(win32gui.GetWindowText(hwnd))
        temp.append(win32gui.GetClassName(hwnd))
        windows[hwnd] = temp

    def Find_hwnd(self, title:str):
        windows = {}
        win32gui.EnumWindows(self.MyCallback, windows)
        # self.logger.info("Enumerated a total of  windows with %d classes" ,(len(windows)))
        # self.logger.info('------------------------------')
        #self.logger.info classes
        # self.logger.info('-------------------------------')
        for item in windows:
            if windows[item][1].startswith(title):
                # self.logger.info(f'{windows[item]}, {int(windows[item][0], 16)}')  # ['0x6f1078', 'BlueStacks App Player', 'Qt5154QWindowOwnDCIcon'], 7278712
                # print(f'{windows[item]}, {int(windows[item][0], 16)}')
                hwnd = int(windows[item][0], 16)
                if win32gui.IsIconic(hwnd):          # 如果該視窗被縮下去工作列
                    return -2
                else:
                    return hwnd
        return -1                                    # 沒找到該視窗標題
    
    def Find_Child_hwnd(self, hwnd):
        '''
        input: hwnd -> parent的hwnd
        return: child_handles -> 找到parent的所有hwnd
        '''
        child_handles = {}
        def all_ok(sub_hwnd, param):
            temp=[]
            if win32gui.IsWindowVisible(sub_hwnd):
                temp.append(hex(sub_hwnd))
                temp.append(win32gui.GetWindowText(sub_hwnd))
                temp.append(win32gui.GetClassName(sub_hwnd))
                # temp.append(win32gui.IsWindowVisible(sub_hwnd))
                child_handles[sub_hwnd] = temp
        
        win32gui.EnumChildWindows(hwnd, all_ok, None)
        # print(f'parent hwnd:')
        # print(f'{hwnd}: {hex(hwnd)}, {win32gui.GetWindowText(hwnd)}, {win32gui.GetClassName(hwnd)}')
        # print(f'child hwnd:')
        # print(child_handles)
        return child_handles

    def Find_One_Hierarchy_Level_Child_hwnd(self, hwnd):
        '''
        input: hwnd -> parent的hwnd
        return: child_handles -> 找到parent的下一層(不會遞迴往下)的所有可見hwnd
        '''
        child_handles = {}
        def all_ok(sub_hwnd, param):
            if win32gui.GetParent(sub_hwnd) == hwnd and win32gui.IsWindowVisible(sub_hwnd):
                temp=[]
                temp.append(hex(sub_hwnd))
                temp.append(win32gui.GetWindowText(sub_hwnd))
                temp.append(win32gui.GetClassName(sub_hwnd))
                temp.append(win32gui.IsWindowVisible(sub_hwnd))
                child_handles[sub_hwnd] = temp
        
        win32gui.EnumChildWindows(hwnd, all_ok, None)
        print(f'parent hwnd:')
        print(f'{hwnd}: {hex(hwnd)}, {win32gui.GetWindowText(hwnd)}, {win32gui.GetClassName(hwnd)}')
        print(f'child hwnd:')
        print(child_handles)

        return child_handles

    def screen(self, hwnd, cfg_x1, cfg_y1, cfg_x2, cfg_y2):
        '''
        output: img = cv2 bgr format
        '''

        rect = win32gui.GetWindowRect(hwnd)
        # print(rect)
        if rect[1] < -100:
            return None
        
        self.x1 = rect[0]
        self.y1 = rect[1]
        self.x2 = rect[2]
        self.y2 = rect[3]
        
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1

        # self.lock.acquire()
        if cfg_x1 >= self.x1 and cfg_y1 >= self.y1 and cfg_x2 <= self.x2 and cfg_y2 <= self.y2:
            # start_time = time.perf_counter()
            img = self.background_screenshot(hwnd, self.w, self.h)   # (hwnd, w, h)
            # print(f'background_screenshot time: {time.perf_counter() - start_time:.4f} sec')
            cfg_h = cfg_y2 - cfg_y1
            cfg_w = cfg_x2 - cfg_x1
            new_y1 = cfg_y1-self.y1
            new_x1 = cfg_x1-self.x1
            img = img[new_y1:new_y1+cfg_h, new_x1:new_x1+cfg_w].copy()
            # print(img.shape)
        else:
            return None
        # self.lock.release()
        
        return img

    def background_screenshot(self, hwnd, width, height):
        try:
            # print(width, height)
            # wDC = win32gui.GetDC(hwnd)         # GetDC 仅为客户区
            wDC   = win32gui.GetWindowDC(hwnd)     # GetWindowDC 函式會擷取整個視窗的 DC 裝置 (內容，包括標題列、功能表和捲軸。視窗裝置內容允許在視窗的任何位置繪製，因為裝置內容的原點是視窗左上角，而不是工作區。
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC   = dcObj.CreateCompatibleDC()
            
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, width, height)     # 为bitmap开辟適當空间
            # dataBitMap.CreateCompatibleBitmap(mfcDC, w, h)的理解：
            # 1.mfc相当于一个虚拟屏幕。这里的参数w和h决定了这个屏幕的大小。
            # 2.屏幕的初始状态是黑色，每个坐标都是#000000
            # 3.之前有 dcObj = win32ui.CreateDCFromHandle(wDC)，又有 wDC = win32gui.GetWindowDC(hwnd)
            #   dcObj和hwnd窗口之间建立了某种关联，可以将hwnd窗口中的图像放到虚拟屏幕上

            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0,0),(width, height) , dcObj, (0,0), win32con.SRCCOPY)
            # print(dataBitMap.GetInfo())
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            # img = np.array(dataBitMap.GetBitmapBits(), dtype=np.uint8)
            # img = np.fromstring(signedIntsArray, dtype='uint8')

            # 32bpp => 每像素 4 位元組（BGRA）；DDB 通常 bottom-up
            img = np.frombuffer(signedIntsArray, dtype=np.uint8).reshape((height, width, 4))

            # 轉成 top-down（Windows DDB 往往是 bottom-up）
            # img = np.flip(img, 0)            # O(1) 視圖翻轉，幾乎不拷貝

            # img = np.frombuffer(signedIntsArray, dtype='uint8').reshape((height, width, 4))
            img = img[:, :, 0:3].copy()
            # # # print(img)
            # # # print(img.shape)
            # # # print(img.dtype)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            #dataBitMap.SaveBitmapFile(cDC, 'screenshot.bmp')
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            return img
        except Exception as e:
            print(e)
            return None

    def find_nx_hwnd(self):
        win_hwnd = self.Find_hwnd('NoMachine')
        if win_hwnd == -1:
            print(f'找不到標題含有 "NoMachine" 的視窗, 請確認 NoMachine 已開啟')
            return False
        elif win_hwnd == -2:
            print(f'請勿把 "NoMachine" 視窗縮下去工具列')
            return False
        config = load_cfg()
        if config['cust']['framearea_hwnd'] != '-1':
            self.FrameArea_hwnd = int(config['cust']['framearea_hwnd'], 16)
            print(f'使用客製化 NoMachine FrameArea_hwnd: {self.FrameArea_hwnd}')
            return True
        child_handles = self.Find_Child_hwnd(win_hwnd)
        self.FrameArea_hwnd = 0
        success = False
        for key in child_handles:
            if child_handles[key][1] == 'FrameArea':
                self.FrameArea_hwnd = key
                success = True
                break
        if success == False:
            print('NoMachine 內找不到 FrameArea')
        return success

    def nx_bg_screen(self, x1, y1, x2, y2):
        '''
        return cv2 BGR image, if image is None -> no image
        '''
        return self.screen(self.FrameArea_hwnd, x1, y1, x2, y2)

    def nx_bg_type(self, my_str='', nodelay=False):
        if my_str != '':
            if get_exit_flag() == 1:
                sys.exit()
            if (my_str == ' '):
                # my_keyboard.type(' ')
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, self.virtual_key[self.no_shift_char.index(' ')], 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, self.virtual_key[self.no_shift_char.index(' ')], 0)
                time.sleep(0.01)
                # time.sleep(type_speed)
                return
            elif (my_str == 'pagedown_key'):
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, 0x11, 0)   # CTRL
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, 0x46, 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, 0x46, 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, 0x11, 0)
                time.sleep(0.01)
                # win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, VK_CODES['PAGE_DOWN'], 0)
                # time.sleep(0.01)
                # win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, VK_CODES['PAGE_DOWN'], 0)
                # time.sleep(0.01)
                # my_keyboard.press(Key.ctrl)
                # my_keyboard.press('f')
                # my_keyboard.release('f')
                # my_keyboard.release(Key.ctrl)
                if nodelay == False:
                    time.sleep(cmd_speed)
                return
            elif (my_str == 'enter_key'):
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, VK_CODES['ENTER'], 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, VK_CODES['ENTER'], 0)
                time.sleep(0.01)
                time.sleep(cmd_speed)
                return
            # elif (my_str == 'enter_key_fast'):
            #     my_keyboard.press(Key.enter)
            #     my_keyboard.release(Key.enter)
            #     time.sleep(type_speed)
            #     return
            elif (my_str == 'new_tab'):
                # my_keyboard.press(Key.ctrl)
                # my_keyboard.press(Key.shift)
                # my_keyboard.press('t')
                # my_keyboard.release('t')
                # my_keyboard.release(Key.shift)
                # my_keyboard.release(Key.ctrl)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, 0x11, 0)   # CTRL
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, 0x10, 0)   # SHIFT
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, self.virtual_key[self.no_shift_char.index('f')], 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, self.virtual_key[self.no_shift_char.index('f')], 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, 0x10, 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, 0x11, 0)
                time.sleep(0.01)
                time.sleep(cmd_speed)
                time.sleep(1)
                return
            # elif (my_str == 'paste'):
            #     my_keyboard.press(Key.ctrl)
            #     my_keyboard.press(Key.shift)
            #     my_keyboard.press('v')
            #     my_keyboard.release('v')
            #     my_keyboard.release(Key.shift)
            #     my_keyboard.release(Key.ctrl)
            #     time.sleep(cmd_speed)
            #     return
            elif (my_str == 'esc_key'):
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, 0x1B, 0)
                time.sleep(0.01)
                win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, 0x1B, 0)
                time.sleep(0.01)
                time.sleep(type_speed)
                return
            
            for i in range(len(my_str)):
                if get_exit_flag() == 1:
                    sys.exit()
                if my_str[i] in self.shift_char:
                    # my_keyboard.press(Key.shift)
                    win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, 0x10, 0)   # SHIFT
                    time.sleep(0.01)
                    # my_keyboard.type(self.no_shift_char[self.shift_char.find(my_str[i])])
                    win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, self.virtual_key[self.shift_char.index(my_str[i])], 0)
                    time.sleep(0.01)
                    win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, self.virtual_key[self.shift_char.index(my_str[i])], 0)
                    time.sleep(0.01)
                    # my_keyboard.release(Key.shift)
                    win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, 0x10, 0)
                    time.sleep(0.01)
                    # time.sleep(type_speed)
                else:
                    # my_keyboard.type(my_str[i])
                    win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYDOWN, self.virtual_key[self.no_shift_char.index(my_str[i])], 0)
                    time.sleep(0.01)
                    win32api.SendMessage(self.FrameArea_hwnd, win32con.WM_KEYUP, self.virtual_key[self.no_shift_char.index(my_str[i])], 0)
                    time.sleep(0.01)
                    # time.sleep(type_speed)

    def nx_bg_open_vim(self, my_str='', recursive_mode=False):
        if my_str != '':
            if not recursive_mode:
                cmd = 'vim -u NONE -R ' + my_str
            else:
                cmd = 'vim -u NONE ' + my_str
            # win_clip(cmd)
            # my_type('paste')
            self.nx_bg_type(cmd)
            self.nx_bg_type('enter_key')
            
            self.nx_bg_type(':set nu')
            self.nx_bg_type('enter_key')
            self.nx_bg_type(':hi LineNr ctermfg=white ctermbg=black')
            self.nx_bg_type('enter_key')
            self.nx_bg_type(':hi Normal ctermfg=white ctermbg=black')
            self.nx_bg_type('enter_key')
            # self.nx_bg_type(':1')
            # self.nx_bg_type('enter_key')
            time.sleep(0.5)

    def nx_bg_quit_vim(self):
        # my_keyboard.press(Key.esc)
        # my_keyboard.release(Key.esc)
        self.nx_bg_type('esc_key')
        time.sleep(type_speed)
        self.nx_bg_type(':q!')
        time.sleep(type_speed)
        self.nx_bg_type('enter_key')

if __name__ == '__main__':
    bg = BG()
    # print(bg.list_all_visible_windows())
    if bg.find_nx_hwnd():
        print(bg.FrameArea_hwnd)
    else:
        print('not found nx hwnd')
        sys.exit()
    # print(win_hwnd)
    # win_hwnd = 0x5A17F8
    # win_hwnd = 0xE70682
    # win_hwnd = 0x81644
    # win_hwnd = 0x71034
    # win_hwnd = 0x8D14A8
    # win32api.SendMessage(win_hwnd, win32con.WM_SETTEXT, None, 'Your String Here')

    # start_time = time.perf_counter()
    # for i in range(10):
    #     win32api.SendMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0x20, 0)
    #     time.sleep(0.01)
    #     win32api.SendMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0x20, 0)
    #     time.sleep(0.01)
    # print(time.perf_counter() - start_time)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xA0, 0)  # left shift
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xBA, 0)  # ;:
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xBA, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xBB, 0)  # =
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xBB, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xBC, 0)  # ,
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xBC, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xBD, 0)  # -
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xBD, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xBE, 0)  # .
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xBE, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xBF, 0)  # /?
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xBF, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xC0, 0)  # `~
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xC0, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xDB, 0)  # [{
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xDB, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xDC, 0)  # \|
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xDC, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xDD, 0)  # ]}
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xDD, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0xDE, 0)  # '"
    # time.sleep(0.01)
    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xDE, 0)
    # time.sleep(0.01)

    # win32api.PostMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0xA0, 0)   # left shift
    # time.sleep(0.01)

    # img = bg.screen(FrameArea_hwnd)
    # cv2.imshow('test', img)
    # cv2.waitKey(0)