import time
from datetime import datetime
import numpy as np
import os
import sys

print('---------------------------')
while True:
    print('please input mode : 1.single file mode  2.recursive mode  3.terminal export  4.current opened file')
    choice = input()
    if choice != '1' and choice != '2' and choice != '3' and choice != '4':
        print('please input 1 or 2 or 3')
    elif choice == '1':
        print('please input file name :')
        target_name = input()
        break
    else:
        break

from script.keyboard_mouse_ctrl import mouse_click, my_type
from script.windows_api import message_box
from script.inference_core import Inference

my_infer = Inference(calibration=False)
export_file_root = 'export/'
now = datetime.now()
export_dir_name = export_file_root + now.strftime("%Y%m%d_%H_%M_%S") + '/'
os.mkdir(export_dir_name)
print('create folder : ' + export_dir_name)

print('---------------------------')
print('Start')
print('---------------------------')

my_infer.active_nx()

if choice == '1':
    temp_str = my_infer.single_file_mode(target_name)
    my_infer.write_in_file(export_dir_name, target_name, temp_str)
elif choice == '2':
    my_infer.recursive_mode(export_dir_name)
elif choice == '3':
    img = my_infer.screen(vim_mode=False)
    terminal_str = my_infer.infer(img, vim_mode=False)[0]
    print('-------------------- output -------------------------')
    print(terminal_str)
    f = open(export_dir_name + 'terminal.txt', 'w')
    f.write(terminal_str)
    f.close()
elif choice == '4':
    my_infer.current_opened_file(export_dir_name)

print('DONE')
