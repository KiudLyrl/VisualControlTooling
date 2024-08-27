# -*- coding: utf-8 -*

import cv2
import mss
import time
import datetime
from visual_control_tooling.core.utils import create_path_if_not_exists
from visual_control_tooling.core.screen_area_management import gemray_main_window_name, get_window_screen_area_params, gemray_save_render_images_window_name
from visual_control_tooling.core.pc_interaction import Screenshotter
from os.path import join

"""
prend une photo de l'ecran du haut qui devrais etre en 1080p pour cross compatibility
"""

def take_screenshot(screen_area_param, ts_format, screenshot_output_dir):
    ts = time.time()
    creation_ts_str = datetime.datetime.fromtimestamp(ts).strftime(ts_format)
    create_path_if_not_exists(screenshot_output_dir)

    with mss.mss() as sct:
        screenshotter = Screenshotter("simple_screenshotter_example", sct)
        screenshot_im = screenshotter.take_screenshot(screen_area_param)
        im_filename = join(screenshot_output_dir, "screenshot_" + creation_ts_str + ".png")
        cv2.imwrite(im_filename, screenshot_im)

if __name__ == '__main__':
    WINDOW_NAME = "Save Print Output As"
    TS_FORMAT = '%Y-%m-%d_%H.%M.%S.%f'
    SCREENSHOT_DIR = f"{WINDOW_NAME.replace(' ', '_')}_screenshots"
    screen_area_param = get_window_screen_area_params(WINDOW_NAME)
    take_screenshot(screen_area_param, TS_FORMAT, SCREENSHOT_DIR)
