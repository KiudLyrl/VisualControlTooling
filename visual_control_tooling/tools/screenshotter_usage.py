# -*- coding: utf-8 -*

import cv2
import mss
import time
import datetime
from visual_control_tooling.core.utils import create_path_if_not_exists
from visual_control_tooling.core.data_models import Point
from visual_control_tooling.core.pc_interaction import Screenshotter
from os.path import join

"""
prend une photo de l'ecran du haut qui devrais etre en 1080p pour cross compatibility
"""

def take_screenshot(monitor_number, monitor_relative_top_left, width, height, ts_format, screenshot_output_dir):
    ts = time.time()
    creation_ts_str = datetime.datetime.fromtimestamp(ts).strftime(ts_format)
    create_path_if_not_exists(screenshot_output_dir)

    with mss.mss() as sct:
        screenshotter = Screenshotter("simple_screenshotter_example", sct)
        screenshot_im = screenshotter.take_screenshot_manually(monitor_number, monitor_relative_top_left, width, height)
        im_filename = join(screenshot_output_dir, "screenshot_" + creation_ts_str + ".png")
        cv2.imwrite(im_filename, screenshot_im)

if __name__ == '__main__':
    TS_FORMAT = '%Y-%m-%d_%H.%M.%S.%f'
    SCREENSHOT_DIR = "top_screen_screenshots"
    monitor_number = 2
    monitor_relative_top_left = Point(0, 0)
    width = 1920
    height = 1080
    take_screenshot(monitor_number, monitor_relative_top_left, width, height, TS_FORMAT, SCREENSHOT_DIR)
