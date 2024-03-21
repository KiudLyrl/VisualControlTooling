
import win32gui

from visual_control_tooling.core.utils import list_all_windows_titles
from visual_control_tooling.core.data_models import Point, ScreenAreaParams
from visual_control_tooling.core.exceptions import UnrecoverableException
from visual_control_tooling.core.enums import Orientation

"""
Here I put the code required to locate softwares window, usefull as in 6 month I would have forgot
the window title or specifics needed to do it
"""

gemray_main_window_name = "GemRay Options"
gemray_stone_color_window_name = "Edit Colors"
gemray_background_color_window_name = "Edit Colors"
gemray_load_file_window_name = "Choose a GemCad file"
gemray_render_window_name = "{you_file_name_without_path}"
gemray_save_render_images_window_name = "Save As JPEG file"
gemray_chart_window_name = "{you_file_name_without_path}"


def is_window_minimized(window_title):
    """Check if a window with a given title is minimized."""
    def enum_windows_callback(hwnd, resultList):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == window_title:
            resultList.append(hwnd)
    window_handles = []
    win32gui.EnumWindows(enum_windows_callback, window_handles)
    if window_handles:
        return win32gui.IsIconic(window_handles[0])
    else:
        raise UnrecoverableException(f"Window with title '{window_title}' not found.")


def get_gem_cut_studio_window_name():
    window_titles = list_all_windows_titles()
    for title in window_titles:
        if title.startswith("Gem Cut Studio"):
            return title

def get_window_screen_area_params(window_name):

    window_names = list_all_windows_titles()

    if window_name not in window_names:
        raise UnrecoverableException(f"{window_name} window not found")

    if is_window_minimized(window_name):
        raise UnrecoverableException(f"{window_name} is minimized")

    hwnd = win32gui.FindWindow(None, window_name)
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    topleft_point = Point(left, top)
    bottomright_point = Point(right, bottom)
    width = right - left
    height = bottom - top
    if width > height:
        orientation = Orientation.HORIZONTAL
    else:
        orientation = Orientation.VERTICAL

    screen_area_params = ScreenAreaParams(topleft_point, bottomright_point, width, height, orientation)
    print(f"{window_name} screen area params : ")
    print(screen_area_params.toString())

    return ScreenAreaParams(topleft_point, bottomright_point, width, height, orientation)

def get_gem_cut_studio_screen_area_params():

    window_name = get_gem_cut_studio_window_name()

    if window_name is None:
        raise UnrecoverableException("Gem cut studio window not found")

    if is_window_minimized(window_name):
        raise UnrecoverableException("Gem cut studio is minimized")

    hwnd = win32gui.FindWindow(None, window_name)
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    topleft_point = Point(left, top)
    bottomright_point = Point(right, bottom)
    width = right - left
    height = bottom - top
    if width > height:
        orientation = Orientation.HORIZONTAL
    else:
        orientation = Orientation.VERTICAL

    screen_area_params = ScreenAreaParams(topleft_point, bottomright_point, width, height, orientation)
    print("Gem cut studio screen area params : ")
    print(screen_area_params.toString())

    return ScreenAreaParams(topleft_point, bottomright_point, width, height, orientation)

def get_gemray_screen_area_params(sct, monitor_num):
    left = sct.monitors[monitor_num]['left']
    top = sct.monitors[monitor_num]['top']
    width = sct.monitors[monitor_num]['width']
    right = left + width
    height = sct.monitors[monitor_num]['height']
    bottom = top + height
    topleft_point = Point(left, top)
    bottomright_point = Point(right, bottom)
    width = right - left
    height = bottom - top
    if width > height:
        orientation = Orientation.HORIZONTAL
    else:
        orientation = Orientation.VERTICAL

    screen_area_params = ScreenAreaParams(topleft_point, bottomright_point, width, height, orientation)
    print("GemRay studio screen area params : ")
    print(screen_area_params.toString())

    return ScreenAreaParams(topleft_point, bottomright_point, width, height, orientation)

def print_all_window_names():
    window_titles = list_all_windows_titles()
    for title in window_titles:
        print(title)
