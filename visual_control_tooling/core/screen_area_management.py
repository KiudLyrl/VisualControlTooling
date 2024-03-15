
import win32gui

from visual_control_tooling.core.utils import list_all_windows_titles
from visual_control_tooling.core.data_models import Point, ScreenAreaParams
from visual_control_tooling.core.exceptions import UnrecoverableException
from visual_control_tooling.core.enums import Orientation

"""
Here I put the code required to locate softwares window, usefull as in 6 month I would have forgot
the window title or specifics needed to do it
"""


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
