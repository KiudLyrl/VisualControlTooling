#-*- coding: utf-8 -*-

import subprocess
import time
import win32gui

from os import listdir
from pathlib import Path
from os.path import isfile, join
from visual_control_tooling.core.enums import OS
from visual_control_tooling.core.exceptions import UnrecoverableException

"""
Various functions that I use almost everywhere
"""

def get_git_commit_hash() -> str:
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
        return commit_hash.decode('utf-8')
    except subprocess.CalledProcessError:
        return "not_a_git_repository"

def clear_console(os=OS.WINDOWS) -> None:
    WINDOWS_COMMAND = 'cls'
    UNIX_COMMAND = 'clear'
    if os == OS.WINDOWS:
        os.system(WINDOWS_COMMAND)
    elif os == OS.UNIX:
        os.system(UNIX_COMMAND)
    else:
        raise UnrecoverableException(f"Unknow OS : {os}")

def get_all_files_from(my_path: str) -> list[str]:
    """return all filename in a folder, without their path"""
    file_list_without_path = [ f for f in listdir(my_path) if isfile(join(my_path,f)) and 'desktop.ini' not in f ]
    return file_list_without_path

def create_path_if_not_exists(path: str) -> None:
    path_to_create = Path(path)
    path_to_create.mkdir(parents=True, exist_ok=True)

def wait_and_print(seconds: int) -> None:
    for x in range(seconds+1):
        print("Waiting " + str(seconds-x) + "\r", end='')
        time.sleep(1)

def list_all_windows_titles() -> list[str]:
    """A function that returns the titles of all the visible windows."""
    def callback(handle, titles):
        if win32gui.IsWindowVisible(handle) and win32gui.GetWindowText(handle):
            titles.append(win32gui.GetWindowText(handle))
    titles = []
    win32gui.EnumWindows(callback, titles)
    return titles

def cut_sting_in_pieces_of_given_size(str_to_cut, size):
    if len(str_to_cut) < size:
        return []
    elif len(str_to_cut) == size:
        return [str_to_cut]
    else:
        return cut_sting_in_pieces_of_given_size(str_to_cut[:size], size) + cut_sting_in_pieces_of_given_size(str_to_cut[size:], size)

def make_number_human_readable(str_number: str) -> str:
    left_part = str_number
    right_part = None
    if str_number.find(".") != -1:
        left_part, right_part = str_number.split(".")

    if str_number.find(",") != -1:
        left_part, right_part = str_number.split(",")

    if len(left_part) <= 3:
        return str_number

    spaced_left_part = " ".join([left_part[::-1][i:i+3] for i in range(0, len(left_part), 3)])[::-1]

    if right_part is None:
        return spaced_left_part
    else:
        return spaced_left_part + '.' + right_part
