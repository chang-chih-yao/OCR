import pynput
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput import keyboard
import time
from scripts.cfg import load_cfg
from scripts.windows_api import win_clip
import win32gui, win32ui, win32con, win32api


def on_press(key):
    '''
    press backspace key on your keyboard anytime to stop program
    '''
    global exit_flag
    if key == Key.backspace and detect_exit_flag == 1:
        print('exit()')
        exit_flag = 1
        return False

def my_type(my_str = '', nodelay=False):
    '''
    my_str : string
    '''
    no_shift_char = "abcdefghijklmnopqrstuvwxyz0123456789`-=[]\\;',./"      # 47 chars
    shift_char    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(~_+{}|:"<>?'       # 47 chars
    if(my_str != ''):
        if exit_flag == 1:
            exit()
        if (my_str == ' '):
            my_keyboard.type(' ')
            time.sleep(type_speed)
            # win32api.SendMessage(FrameArea_hwnd, win32con.WM_KEYDOWN, 0x20, 0)
            # time.sleep(0.01)
            # win32api.SendMessage(FrameArea_hwnd, win32con.WM_KEYUP, 0x20, 0)
            # time.sleep(0.01)
            return
        elif (my_str == 'pagedown_key'):
            my_keyboard.press(Key.ctrl)
            my_keyboard.press('f')
            my_keyboard.release('f')
            my_keyboard.release(Key.ctrl)
            if nodelay == False:
                time.sleep(cmd_speed)
            return
        elif (my_str == 'enter_key'):
            my_keyboard.press(Key.enter)
            my_keyboard.release(Key.enter)
            time.sleep(cmd_speed)
            return
        elif (my_str == 'enter_key_fast'):
            my_keyboard.press(Key.enter)
            my_keyboard.release(Key.enter)
            time.sleep(type_speed)
            return
        elif (my_str == 'new_tab'):
            my_keyboard.press(Key.ctrl)
            my_keyboard.press(Key.shift)
            my_keyboard.press('t')
            my_keyboard.release('t')
            my_keyboard.release(Key.shift)
            my_keyboard.release(Key.ctrl)
            time.sleep(cmd_speed)
            time.sleep(1)
            return
        elif (my_str == 'paste'):
            my_keyboard.press(Key.ctrl)
            my_keyboard.press(Key.shift)
            my_keyboard.press('v')
            my_keyboard.release('v')
            my_keyboard.release(Key.shift)
            my_keyboard.release(Key.ctrl)
            time.sleep(cmd_speed)
            return
        elif (my_str == 'esc_key'):
            my_keyboard.press(Key.esc)
            my_keyboard.release(Key.esc)
            time.sleep(type_speed)
            return
        
        for i in range(len(my_str)):
            if exit_flag == 1:
                exit()
            if my_str[i] in shift_char:
                my_keyboard.press(Key.shift)
                my_keyboard.type(no_shift_char[shift_char.find(my_str[i])])
                my_keyboard.release(Key.shift)
                time.sleep(type_speed)
            else:
                my_keyboard.type(my_str[i])
                time.sleep(type_speed)

def mouse_click(x, y):
    my_mouse.position = (x, y)
    time.sleep(cmd_speed)
    my_mouse.click(Button.left)
    time.sleep(type_speed)

def mouse_click_mid(x, y):
    my_mouse.position = (x, y)
    time.sleep(cmd_speed)
    my_mouse.click(Button.middle)
    time.sleep(type_speed)

def open_vim(my_str='', recursive_mode=False):
    if my_str != '':
        if not recursive_mode:
            cmd = 'vim -u NONE -R ' + my_str
        else:
            cmd = 'vim -u NONE ' + my_str
        # win_clip(cmd)
        # my_type('paste')
        my_type(cmd)
        my_type('enter_key')
        
        my_type(':set nu')
        my_type('enter_key')
        # my_type(':1')
        # my_type('enter_key')
        time.sleep(0.5)

def quit_vim():
    my_keyboard.press(Key.esc)
    my_keyboard.release(Key.esc)
    time.sleep(type_speed)
    my_type(':q!')
    time.sleep(type_speed)
    my_type('enter_key')
    time.sleep(cmd_speed)

def detect_stop_program_open():
    global detect_exit_flag
    detect_exit_flag = 1

def detect_stop_program_close():
    global detect_exit_flag
    detect_exit_flag = 0

def get_exit_flag():
    return exit_flag

config = load_cfg()
type_speed = float(config['cust']['type_speed'])
cmd_speed = float(config['cust']['cmd_speed'])

my_keyboard = pynput.keyboard.Controller()
my_mouse = pynput.mouse.Controller()

exit_flag = 0
detect_exit_flag = 1
# listener = keyboard.Listener(on_press=on_press)
# listener.start()