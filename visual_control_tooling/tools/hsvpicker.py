#!/usr/bin/python

import cv2
import numpy as np

def pick(img):
    def nothing(x):
        pass

    cv2.namedWindow("image", 0)
    cv2.resizeWindow("image", img.shape[1]+500, img.shape[0]+500)

    # create trackbars for HSV Selection
    cv2.createTrackbar('HLow','image',0,255,nothing)
    cv2.createTrackbar('SLow','image',0,255,nothing)
    cv2.createTrackbar('VLow','image',0,255,nothing)

    cv2.createTrackbar('HHigh','image',0,255,nothing)
    cv2.createTrackbar('SHigh','image',0,255,nothing)
    cv2.createTrackbar('VHigh','image',0,255,nothing)

    HLow, SLow, VLow = 0, 0, 0
    HHigh, SHigh, VHigh = 255, 255, 255

    while True:
        print('recomputing')
        img = im
        HLow = cv2.getTrackbarPos('HLow','image')
        SLow = cv2.getTrackbarPos('SLow','image')
        VLow = cv2.getTrackbarPos('VLow','image')
        HHigh = cv2.getTrackbarPos('HHigh','image')
        SHigh = cv2.getTrackbarPos('SHigh','image')
        VHigh = cv2.getTrackbarPos('VHigh','image')

        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array([HLow, SLow, VLow])
        upper = np.array([HHigh, SHigh, VHigh])
        mask = cv2.inRange(imgHSV, lower, upper)
        imgProcessed = cv2.bitwise_or(img,img, mask= mask)
        cv2.imshow("image", imgProcessed)
        cv2.waitKey(10)

    cv2.destroyAllWindows()

if __name__ == '__main__':
    pic = r"path/to/some_png.png"
    im = cv2.imread(pic)
    pick(im)
