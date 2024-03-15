# -*- coding: utf-8 -*

import cv2
import numpy as np
import pytesseract

from visual_control_tooling.core.im_manipulations import crop_im

def read_text_on_im(full_im, crop_topleft, crop_bottomright, lower_hsv: list[int, int, int], upper_hsv: list[int, int, int]):
    """
    read text with OCR, you need to download, extract, and add to path tesseract OCR before
    """

    im = crop_im(full_im, crop_topleft, crop_bottomright)

    lower = np.array(lower_hsv)
    upper = np.array(upper_hsv)
    imgHSV = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imgHSV, lower, upper)
    im_filtered = cv2.bitwise_or(im, im, mask=mask)
    black_text_on_white_background_im = cv2.bitwise_not(im_filtered)
    custom_config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(black_text_on_white_background_im, config=custom_config)
    return text
