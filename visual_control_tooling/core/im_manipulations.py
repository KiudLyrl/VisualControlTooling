# -*- coding: utf-8 -*

import cv2
import numpy as np

from visual_control_tooling.core.log_system import Logger
from visual_control_tooling.core.data_models import Point

def is_template_in_image(im: np.ndarray, template_im: np.ndarray, threshold=0.8) -> bool:
    return locate_template_in_image(im, template_im, threshold=threshold) is not None

def locate_template_in_image(im: np.ndarray, template_im: np.ndarray, threshold=0.8) -> Point | None:
    """
    Detect a template in an opencv bgr image

    :param im: the opencv bgr image
    :param template_im: the template to detect
    :param threshold: the detection threshold (0.8 = 80% confidence)
    :return: a point core.data_models.Point containing the coordinate of the dected template, None if no detection
    """
    cv2.imwrite("search_area.png", im)
    cv2.imwrite("template_im.png", template_im)
    res = cv2.matchTemplate(im, template_im, cv2.TM_CCOEFF_NORMED)
    h, w, channels = template_im.shape

    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        # use the first rectangle and ignore the other,
        # no problem car there is only one chest on the screen at any given moment
        x_center = pt[0] + w / 2
        y_center = pt[1] + h / 2
        return Point(x_center, y_center)
    return None


def resize_im_in_width(im: np.ndarray, new_width_px: int) -> np.ndarray:
    height, im_width, channels = im.shape
    factor = float(new_width_px / float(im_width))
    resized_image = cv2.resize(im, (0, 0), fx=factor, fy=factor)
    return resized_image


def resize_im(im: np.ndarray, width: int, height: int) -> np.ndarray:
    return cv2.resize(im, (width, height))


def create_empty_balck_im(height: int, width: int) -> np.ndarray:
    return np.zeros((height, width, 3), np.uint8)


def create_empty_colored_im(width: int, height: int, color: tuple[int, int, int]) -> np.ndarray:
    im = np.zeros((height, width, 3), np.uint8)
    im[:] = color
    return im


def put_image_in_image(big_im: np.ndarray, small_im: np.ndarray, topleft_in_big: Point) -> np.ndarray:
    x = topleft_in_big.x
    y = topleft_in_big.y
    big_im[y:y + small_im.shape[0], x:x + small_im.shape[1]] = small_im
    # useless because modified by param but I like functions that returns something
    return big_im


def get_pixel_value(im: np.ndarray, position: Point) -> tuple[int, int, int]:
    Logger.get_instance().log_info(f"Measuring pixel at position {position.toString()}")
    color_value = im[position.y][position.x]
    Logger.get_instance().log_info(f"color value {color_value}")
    return color_value


def is_pixel_same_color(pixel: tuple[int, int], color_bgr: tuple[int, int, int]) -> bool:
    return pixel[0] == color_bgr[0] and pixel[1] == color_bgr[1] and pixel[2] == color_bgr[2]


def is_pixel_same_color_aprox(current_pixel_color: tuple[int, int, int], color_bgr: tuple[int, int, int], tolerance: int) -> bool:
    Logger.get_instance().log_info("measured pixel color : {}".format(current_pixel_color))
    Logger.get_instance().log_info("target color : {}".format(color_bgr))
    Logger.get_instance().log_info("tolerance : {}".format(tolerance))
    p1 = color_bgr[0]-tolerance<current_pixel_color[0]<color_bgr[0]+tolerance
    p2 = color_bgr[1]-tolerance<current_pixel_color[1]<color_bgr[1]+tolerance
    p3 = color_bgr[2]-tolerance<current_pixel_color[2]<color_bgr[2]+tolerance
    is_same_color = p1 and p2 and p3
    Logger.get_instance().log_info("Same color? : {}".format(is_same_color))
    return is_same_color


def crop_im(im: np.ndarray, topleft_point: Point, bottomright_point: Point) -> np.ndarray:
    return im[topleft_point.y:bottomright_point.y, topleft_point.x:bottomright_point.x]
