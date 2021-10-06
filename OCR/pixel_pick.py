import numpy as np
import cv2
from PIL import Image
from PIL import ImageGrab

'''
left_top point on your monitor     : (x1, y1)
right_bottom point on your monitor : (x2, y2)

use keyboard esc or q to quit
use keyboard wsad to control left_top point,      w:up, s:down, a:left, d:right
use keyboard tgfh to control right_bottom point,  t:up, g:down, f:left, h:right
use keyboard z to switch tick number.
use keyboard x to save image to the current path (default image name 'save.png').
'''


def select_img():
    x1 = 0
    y1 = 0
    x2 = 100
    y2 = 100

    tick = 10

    max_img_size = ImageGrab.grab()
    print('your monitor resolution :')
    w_max = max_img_size.size[0]
    h_max = max_img_size.size[1]
    print(w_max)
    print(h_max)
    print('-------------------------')
    print('continue? please input y or n:', end='')
    choice = input()
    if choice != 'y' and choice != 'Y':
        exit()

    print('1. mouse click on opencv windows  2. now you can use keyboard control (esc or q to quit)')

    while True:
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))      # x1, y1, x2, y2   w: x1 to x2-1, h: y1 to y2-1
        img_np = np.array(img)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        cv2.imshow("img", img_gray)
        key = cv2.waitKey(10)
        
        if key == 27 or key == ord('q'):                 # press esc or q to quit
            print('-------------------------------')
            print('image shape :({:d}, {:d})'.format(img_gray.shape[0], img_gray.shape[1]))          # w: x1 to x2-1, h: y1 to y2-1
            print('left_top :({:d}, {:d}), right_bottom :({:d}, {:d})'.format(x1, y1, x2-1, y2-1))   # real monitor coordinate
            return img_gray
        elif key == ord('w'):
            y1 -= tick
            if y1 < 0:
                y1 += tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('s'):
            y1 += tick
            if y1 >= y2:
                y1 -= tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('a'):
            x1 -= tick
            if x1 < 0:
                x1 += tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('d'):
            x1 += tick
            if x1 >= x2:
                x1 -= tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('t'):
            y2 -= tick
            if y2 <= y1:
                y2 += tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('g'):
            y2 += tick
            if y2 > h_max:
                y2 -= tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('f'):
            x2 -= tick
            if x2 <= x1:
                x2 += tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('h'):
            x2 += tick
            if x2 > w_max:
                x2 -= tick
            print('{:d}, {:d}, {:d}, {:d}'.format(x1, y1, x2, y2))
        elif key == ord('z'):
            if tick == 10:
                tick = 1
            elif tick == 1:
                tick =10
            print('now tick :{:d}'.format(tick))
        elif key == ord('x'):
            #cv2.imwrite('save.png', img_gray)
            ret, th1 = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY)
            cv2.imwrite('save.png', th1)
            print('save.png')

def find_contour(img):
    ret, th1 = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY)
    # cv2.imshow("origin", th1) 
    contours, hierarchy = cv2.findContours(th1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(img,contours,-1,(0,255,255),1) 
    
    cnt = contours[0]
    M = cv2.moments(cnt)
    print( M )
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    print('------------')
    print(cx)
    print(cy)
    print('------------')
    area = cv2.contourArea(cnt)
    print(area)
    print('------------')
    perimeter = cv2.arcLength(cnt,True)
    print(perimeter)

    x,y,w,h = cv2.boundingRect(cnt)
    print('------------')
    print(x)
    print(y)
    print(w)
    print(h)
    # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
    # cv2.imshow("drawContours", img) 
    # cv2.waitKey(0)

#my_img = select_img()

img = cv2.imread("block_template.png")
my_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
find_contour(my_img)