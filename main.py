import math
import time

import cv2
import numpy as np
import pyautogui

import HandTrackingModule as HTM

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

ptime = 0
if cap.isOpened():
    while True:
        success, img = cap.read()
        if success:
            img = cv2.flip(img, 1)
            # caculate FPS
            ctime = time.time()
            fps = 1 / (ctime - ptime)
            ptime = ctime
            # get hands landmark
            detector = HTM.handDetector(detectionCon=0.7, trackCon=0.7)
            img = detector.findHands(img)
            pos = detector.findPosition(img)
            # get camera size
            cw, ch, _ = img.shape
            # get screen size
            sw, sh = pyautogui.size()

            if len(pos) != 0:
                # get finger postiton in camera coordinate
                i, X_right, Y_right = pos[12]
                i, X_left, Y_left = pos[8]
                i, X_mid, Y_mid = pos[13]
                i, X_base, Y_base = pos[0]

                # caculate distance between postiton
                left_distance = math.hypot(X_left - X_base, Y_left - Y_base)
                right_distance = math.hypot(X_right - X_base, Y_right - Y_base)
                base_distance = math.hypot(X_mid - X_base, Y_mid - Y_base)

                # mapping tip finger from camera to creen coordinate

                if Y_left < 100:
                    Y_left = 100
                if X_left < 100:
                    X_left = 100;

                Y_left = np.interp(Y_left, [0 + 100, 600], [0, sh])
                X_left = np.interp(X_left, [0 + 100, 1000], [0, sw])
                # move cursor 
                pyautogui.moveTo(X_left, Y_left)
                # click condition
                if (right_distance < base_distance):
                    pyautogui.leftClick()
                # print(f'R:{X_left, Y_left}')
                # print(f'L:{X_left, Y_left}')
                print(sw, sh)
            start = (100, 100)
            # end = (400, cw - cw / 10)
            end = (1000, 600)
            cv2.rectangle(img, start, end, (0, 0, 255), 1)
            cv2.putText(img, f'FPS: {str(int(fps))}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
            cv2.imshow('cam', img)
            cv2.waitKey(1)
