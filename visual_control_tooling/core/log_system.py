# -*- coding: utf-8 -*

import cv2
import datetime
import inspect
import os
import time
import shutil

from visual_control_tooling.core.utils import get_all_files_from, get_git_commit_hash, create_path_if_not_exists

TS_FORMAT = '%Y-%m-%d_%H.%M.%S.%f'

class Logger():

    _instance = None
    _is_initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def init_logger(self, name, log_dir, max_historic_log_fles=2):
        self.name = name
        ts = time.time()
        date_as_text = datetime.datetime.fromtimestamp(ts).strftime(TS_FORMAT)
        self.creation_ts = date_as_text
        self.log_dir = log_dir
        self.max_historic_log_fles = max_historic_log_fles
        create_path_if_not_exists(self.log_dir)
        self.log_filename = self.log_dir + "\\" + f"{self.creation_ts}_{name}.log"
        self.file = open(self.log_filename, "w+")
        # pour savoir sur quel commit tournais un log qu'on est en train de lire
        self.log_info(f"Running on commit {get_git_commit_hash()}")
        self.__class__._is_initialized = True
        self._clean_log_folder()


    def get_caller_infos(self):
        frame = inspect.currentframe()

        # we go up 2 levels because this is a function inside the logging function
        caller_frame = frame.f_back
        caller_caller_frame = caller_frame.f_back

        caller_info = inspect.getframeinfo(caller_caller_frame)
        file_name = caller_info.filename
        line_no = caller_info.lineno
        function_name = caller_info.function
        return file_name, function_name, line_no

    def log_info(self, s: str):
        if not self.__class__._is_initialized:
            return
        file_name, function_name, line_no = self.get_caller_infos()
        self._log(s, "[INFO ]", file_name, function_name, line_no)

    def log_error(self, s: str):
        if not self.__class__._is_initialized:
            return
        file_name, function_name, line_no = self.get_caller_infos()
        self._log(s, "[ERROR]", file_name, function_name, line_no)

    def _log(self, s, level, caller_file_name, caller_name, caller_lineo):
        if not self.__class__._is_initialized:
            return
        ts = time.time()
        date_as_text = datetime.datetime.fromtimestamp(ts).strftime(TS_FORMAT)
        msg = date_as_text + " : " + level + " : " + caller_file_name + " : " + caller_name + ": Line " + str(caller_lineo) + " : " + str(s)
        print(msg)
        self.file.write(msg + "\n")

    def _clean_log_folder(self):
        if not self.__class__._is_initialized:
            return
        file_names = get_all_files_from(self.log_dir)
        to_keep = []
        if len(file_names) > self.max_historic_log_fles:
            to_keep.append(file_names[-1])
            to_keep.append(file_names[-2])
        else:
            return
        for file_name in file_names:
            if not file_name in to_keep:
                self.log_info("Deleting " + file_name)
                try:
                    os.remove(os.path.join(self.log_dir, file_name))
                except:
                    self.log_error("Cannot delete " + file_name)

    def close_log_file(self):
        if not self.__class__._is_initialized:
            return
        self.file.close()

    def dumpError(self, subWindowManager, error_dir: str):

        if not self.__class__._is_initialized:
            return

        self.log_info("Dumping to error folder")

        # create pathes
        ts = time.time()
        creation_ts = datetime.datetime.fromtimestamp(ts).strftime(TS_FORMAT)
        error_folder = os.path.join(error_dir, creation_ts)
        create_path_if_not_exists(error_folder)

        # copy_logs
        shutil.copyfile(self.log_filename, os.path.join(error_folder, f"{creation_ts}_{self.name}.log"))

        # screenshot de l'ecran qui nous bloque
        subWindowManager.remeasureSubWindow()
        fresh_im = subWindowManager.take_screenshot_manually()
        cv2.imwrite(os.path.join(error_folder, "stuck_on_this_im_{}.png".format(creation_ts)), fresh_im)
