import math
import time

import cv2
import numpy as np
import win32api
import win32con
from pykeyboard import PyKeyboard

import HandTrackingModule as HTM

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

k = PyKeyboard()


def click(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def showCam(img, fps):
    # cv2.line(img, (100, 100), (100, 900), (255, 0, 0), 1)
    # cv2.line(img, (700, 100), (700, 900), (255, 0, 0), 1)
    start = (80, 80)
    end = (880, 460)
    cv2.rectangle(img, start, end, (0, 0, 255), 1)
    cv2.putText(img, f'FPS: {str(int(fps))}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
    cv2.imshow('cam', img)
    cv2.waitKey(1)


def pressArrowButton(X_left, Y_left, press):
    if X_left < 80 and press:
        k.tap_key(k.right_key)
        #print('right')
        press = False
    if X_left > 880 and press:
        k.tap_key(k.left_key)
        #print('left')
        press = False
    if Y_left < 80 and press:
        k.tap_key(k.down_key)
        #print('down')
        press = False
    if Y_left > 460 and press:
        k.tap_key(k.up_key)
        #print('up')
        press = False
    if (X_left > 80 and X_left < 880) and (Y_left > 80 and Y_left < 460):
        press = True
        #print(press)
    return press


def main():
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0
    smoothening = 5
    if cap.isOpened():
        ptime = 0
        press = True
        while True:
            success, img = cap.read()
            if success:
                img = cv2.flip(img, 1)
                #print(img.shape)
                # caculate FPS
                ctime = time.time()
                fps = 1 / (ctime - ptime)
                ptime = ctime
                # get hands landmark
                detector = HTM.handDetector(detectionCon=0.7, trackCon=0.7)
                img, pos = detector.findHands(img, draw=True)
                # get camera size
                cw, ch, _ = img.shape
                # get screen size
                sw, sh = (1920, 1080)

                if len(pos) != 0:
                    # get finger postiton in camera coordinate
                    i, X_right, Y_right = pos[12]
                    i, X_left, Y_left = pos[8]
                    i, X_mid, Y_mid = pos[6]
                    i, X_base, Y_base = pos[0]

                    # caculate distance between postiton
                    # left_distance = math.hypot(X_left - X_base, Y_left - Y_base)
                    right_distance = math.hypot(X_right - X_base, Y_right - Y_base)
                    base_distance = math.hypot(X_mid - X_base, Y_mid - Y_base)

                    press = pressArrowButton(X_left,Y_left, press)
                    # normalization
                    if X_left > 880:
                        X_left = 880
                    if X_left < 80:
                        X_left = 80
                    if Y_left > 460:
                        Y_left = 460
                    if Y_left < 80:
                        Y_left = 80

                    # mapping tip finger from camera to creen coordinate
                    Y_left = np.interp(Y_left, [0 + 100, 460], [0, sh])
                    X_left = np.interp(X_left, [0 + 100, 880], [0, sw])

                    clocX = plocX + (X_left - plocX) / smoothening
                    clocY = plocY + (Y_left - plocY) / smoothening

                    # move cursor
                    # X_cursor = int(np.floor(int(X_left) / 10) * 10)
                    # Y_cursor = int(np.floor(int(Y_left) / 10) * 10)
                    X_cursor = int(clocX)
                    Y_cursor = int(clocY)
                    win32api.SetCursorPos((X_cursor, Y_cursor))
                    plocX, plocY = X_cursor, Y_cursor
                    # click condition
                    if (right_distance < base_distance):
                        click(int(X_cursor), int(Y_cursor))
                    # print(f'R:{X_left, Y_left}')
                    # print(f'L:{X_left, Y_left}')
                    # print(sw, sh)

                #print(int(fps))
                showCam(img, fps)


if __name__ == '__main__':
    main()
