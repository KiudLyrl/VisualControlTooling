#-*- coding: utf-8 -*-

import win32gui

def list_all_windows_titles() -> list[str]:
    """A function that returns the titles of all the visible windows."""
    def callback(handle, titles):
        if win32gui.IsWindowVisible(handle) and win32gui.GetWindowText(handle):
            titles.append(win32gui.GetWindowText(handle))
    titles = []
    win32gui.EnumWindows(callback, titles)
    return titles

for title in list_all_windows_titles():
    print(title)
