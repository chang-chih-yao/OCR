import numpy as np
import cv2
from PIL import ImageGrab
import sys

class Inference:
    def __init__(self, char_list, difference, img_arr, w, h, vim_text_bias_width, log_flag):
        self.wait_correct_num = 0
        self.char_list = char_list
        self.difference = difference
        self.img_arr = img_arr
        # self.x1 = x1
        # self.y1 = y1
        # self.x2 = x2
        # self.y2 = y2
        self.w = w
        self.h = h
        self.vim_text_bias_width = vim_text_bias_width
        self.log_flag = log_flag
    
    def screen(self, x1, y1, x2, y2, threshold=1):
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        ret, th1 = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
        return th1

    def infer(self, vertical_num, horizontal_num, th1, file_eof, line_cou, vim_mode=True, draw_plot=False):
        #global log_cou, wait_correct_num
        temp_s = ''
        x_start = self.w*0
        y_start = self.h*0

        y = y_start
        space_cou = 0

        if draw_plot:
            char_np_arr = np.array(list(self.char_list))
            temp_y_arr = np.random.randint(100, size=(95))
            plt.ion()
            fig = plt.figure()
            fig.set_size_inches(14, 8)
            ax = fig.add_subplot()
            line1, = ax.plot(char_np_arr, temp_y_arr)
            fig.canvas.draw()
            fig.canvas.flush_events()

        for i in range(vertical_num):
            x = x_start
            front_str = ''
            for j in range(horizontal_num):
                crop_img = th1[y:y+self.h, x:x+self.w]
                if crop_img.shape[0] != self.h or crop_img.shape[1] != self.w:
                    return temp_s, file_eof, line_cou
                if (np.all((crop_img.flatten() == 0)) or np.all((crop_img.flatten() == 255))):   # skip space image
                    result = 47                                                                  # char_list[47] == ' '
                else:
                    mid = crop_img.copy()
                    if (self.log_flag):
                        cv2.imwrite('log/{:04d}.png'.format(log_cou), mid)
                        log_cou += 1
                    # cv2.imshow('mid', mid)
                    # cv2.waitKey()
                    mid = (mid/255).astype('int8')
                    mid = mid.flatten()
                    result_arr = np.absolute(self.img_arr - mid)
                    result_sum = np.sum(result_arr, axis=1)                                      # (difference*category,)   int32
                    result = np.argmin(result_sum) // self.difference
                    if draw_plot:
                        line1.set_ydata(result_sum[::2])
                        fig.canvas.draw()
                        time.sleep(0.5)
                        fig.canvas.flush_events()

                    #print(result, self.char_list[result])
                if j < self.vim_text_bias_width and vim_mode:
                    front_str += self.char_list[result]
                    if j == 7:
                        # print('|'+front_str+'|')
                        if front_str.replace(' ', '').isdigit():
                            # print(line_cou)
                            if front_str == '{:>7d} '.format(line_cou):
                                space_cou = 0
                                if self.wait_correct_num == 1:
                                    self.wait_correct_num = 0
                                if line_cou != 1:
                                    temp_s += '\n'
                            else:
                                self.wait_correct_num = 1
                                line_cou -= 1
                                # print('skip this line')
                                break
                        elif front_str == '@       ':
                            # print('\n', end='')
                            # print('line not complete')
                            return temp_s, file_eof, line_cou
                        elif front_str == '~       ':
                            print('\n', end='')
                            print('file end')
                            file_eof = 1
                            return temp_s, file_eof, line_cou
                        else:
                            line_cou -= 1
                            if self.wait_correct_num == 1:
                                break
                            # print('more than 1 line')
                            if space_cou == 0:
                                temp_s += front_str
                            else:
                                for t in range(space_cou):
                                    temp_s += ' '
                                temp_s += front_str
                                space_cou = 0
                else:
                    if(self.char_list[result] == ' '):
                        space_cou += 1
                    else:
                        if(space_cou == 0):
                            temp_s += self.char_list[result]
                        else:
                            for t in range(space_cou):
                                temp_s += ' '
                            temp_s += self.char_list[result]
                            space_cou = 0
                x += self.w
            y += self.h
            line_cou += 1
            if not vim_mode:
                space_cou = 0
                temp_s += '\n'
            print('\r[{:>5d}/{:<5d}]'.format(i+1, vertical_num), end='')
            sys.stdout.flush()
        print('\n', end='')
        return temp_s, file_eof, line_cou