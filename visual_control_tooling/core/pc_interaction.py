# -*- coding: utf-8 -*

import ctypes
import time
import cv2
import numpy as np
import win32api
import win32con
import win32gui

from ctypes import wintypes
from visual_control_tooling.core.data_models import Point, ScreenAreaParams
from visual_control_tooling.core.log_system import Logger

class KeyboardController:
    """
    Not needed for now
    """
    pass

class Cliquer():

    def __init__(self, screen_area_params: ScreenAreaParams):
        """
        will use the screen_are_params to know where is the position of the clic in the screen, we usually control
        a window inside a screen and all the position we pass are relative to that window for simplicity

        put None into screen_area_params if you don't want to use the function that use it
        """
        self.logger = Logger.get_instance()
        self.screen_area_params: ScreenAreaParams = screen_area_params
        # block input does not seem to work, I leave it for a fix later
        self.BlockInput = ctypes.windll.user32.BlockInput
        self.BlockInput.argtypes = [wintypes.BOOL]
        self.BlockInput.restype = wintypes.BOOL

    def _click(self, x, y):
        """
        clic with the absolute position, does not know your screen area/window
        """
        x = int(x) #pythonh 3.6 migration, somehow I'm passing floats now
        y = int(y)
        self.logger.log_info("blocking mouse (script must be launched in administrator mode)")
        self.BlockInput(True)
        time.sleep(0.1)
        flags, hcursor, (previous_x, previous_y) = win32gui.GetCursorInfo()

        self.logger.log_info("going to {},{}".format(x,y))
        win32api.SetCursorPos((x, y))

        self.logger.log_info("cliquing")
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.07)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.01)

        self.logger.log_info("Unblocking")
        self.BlockInput(False)

    def _click_and_return_to_last_pos(self, x, y):
        """
        clic with the absolute position, does not know your screen area/window, then return to the previous position
        """
        x = int(x) #pythonh 3.6 migration, somehow I'm passing floats now
        y = int(y)
        self.logger.log_info("blocking mouse (script must be launched in administrator mode)")
        self.BlockInput(True)
        time.sleep(0.1)
        flags, hcursor, (previous_x, previous_y) = win32gui.GetCursorInfo()

        self.logger.log_info("going to {},{}".format(x,y))
        win32api.SetCursorPos((x, y))

        self.logger.log_info("cliquing")
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.07)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.01)

        self.logger.log_info("going to {},{}".format(previous_x, previous_y))
        win32api.SetCursorPos((previous_x, previous_y))
        time.sleep(0.2)

        self.logger.log_info("Unblocking")
        self.BlockInput(False)

    def slide_down_100px_relative_to_screen_area(self, x, y):
        """
        slide down inside a window, the x and y are relative to the window you use, absolute position will be
        computed from the screen_area_params
        """
        x = int(x) #pythonh 3.6 migration, somehow I'm passing floats now
        y = int(y)
        
        x = self.screen_area_params.absolute_topleft_point.x + x
        y = self.screen_area_params.absolute_topleft_point.y + y
        
        self.logger.log_info("going to {},{}".format(x,y))
        win32api.SetCursorPos((x, y))

        self.logger.log_info("cliquing")
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.07)
        
        
        self.logger.log_info("sliding down during 100 ms")
        current_y = y
        for iteration in range(100):
            current_y = current_y - 2
            win32api.SetCursorPos((x, current_y))
            time.sleep(0.001)

        self.logger.log_info("realasing clic")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.01)

    def click_relative_to_screen_area_and_return_to_last_pos(self, point):
        """
        clic inside a window, the x and y are relative to the window you use, absolute position will be
        computed from the screen_area_params, 0,0 is the top left of your window

        then return the cursor to the previous position
        """
        x_clic = self.screen_area_params.absolute_topleft_point.x + point.x
        y_clic = self.screen_area_params.absolute_topleft_point.y + point.y
        self.logger.log_info("Cliquer : Clic at : {}, {}".format(x_clic, y_clic))
        self._click_and_return_to_last_pos(x_clic, y_clic)

    def click_relative_to_screen_area(self, point):
        """
        clic inside a window, the x and y are relative to the window you use, absolute position will be
        computed from the screen_area_params, 0,0 is the top left of your window
        """
        x_clic = self.screen_area_params.absolute_topleft_point.x + point.x
        y_clic = self.screen_area_params.absolute_topleft_point.y + point.y
        self.logger.log_info("Cliquer : Clic at : {}, {}".format(x_clic, y_clic))
        self._click(x_clic, y_clic)

class Screenshotter():
    """
    Prend une photo dans un des ecran (regarder sct.monitors en debug pour trouver l'ecran)
    """
    def __init__(self, name, sct):
        self.logger = Logger.get_instance()
        self.sct = sct
        self.last_pic_taken = None
        self.last_pic_taken_time = None
        self.logger.log_info(f"Created basic pc screenshotter : {name}")

    def take_screenshot(self, screen_area_param: ScreenAreaParams):
        self.last_pic_taken_time = time.time()
        screen_part = {
            "top": screen_area_param.absolute_topleft_point.y,
            "left": screen_area_param.absolute_topleft_point.x,
            "width": screen_area_param.width,
            "height": screen_area_param.height,
        }
        self.logger.log_info(f"Taking scrennshot in (sct absolute coordinates) : {screen_part}")
        sct_window_raw_im = self.sct.grab(screen_part)
        # this is not an open cv image
        window_raw_im_to_convert = np.array(sct_window_raw_im, dtype=np.uint8)
        # this is an open cv image
        opencv_im = cv2.cvtColor(window_raw_im_to_convert, cv2.COLOR_BGRA2BGR)
        # cv2.imwrite("last_screenshot_taken.png", opencv_im)
        self.last_pic_taken = opencv_im
        return opencv_im

    def take_screenshot_manually(self, monitor: int, relative_top_left: Point, width: int, height: int):
        """
        Take a screen shot relative to the monitor, so it does not matter what coordinate your monitor is, 0,0 will
        be the top left of the monitor

        :param monitor: the number of the monitor (debut and look into sct to find it)
        :param relative_top_left: the top left of the area in the monitor
        :param width: the width of the area in the monitor
        :param height: the height of the area in the monitor

        :return: an opencv BGR image
        """
        self.last_pic_taken_time = time.time()

        # we have to expressed the coordinate in the sct system, top left can be negative, which
        # is why we get the top left coordinates of the wanted monitor
        x = self.sct.monitors[monitor]['left'] + relative_top_left.x
        y = self.sct.monitors[monitor]['top'] + relative_top_left.y
        bottom_right = Point(relative_top_left.x + width, relative_top_left.y + height)
        self.logger.log_info(f"Taking scrennshot in monitor {monitor} : topleft : {relative_top_left.toString()}, bottom_right : {bottom_right.toString()}")
        screen_part = {
            "top": y,
            "left": x,
            "width": width,
            "height": height,
        }
        self.logger.log_info(f"Taking scrennshot in (sct absolute coordinates) : {screen_part}")
        sct_window_raw_im = self.sct.grab(screen_part)
        # this is not an open cv image
        window_raw_im_to_convert = np.array(sct_window_raw_im, dtype=np.uint8)
        # this is an open cv image
        opencv_im = cv2.cvtColor(window_raw_im_to_convert, cv2.COLOR_BGRA2BGR)
        # cv2.imwrite("last_screenshot_taken.png", opencv_im)
        self.last_pic_taken = opencv_im
        return opencv_im
