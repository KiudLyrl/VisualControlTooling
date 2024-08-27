import mss
import time
import imageio.v2 as imageio
import os
import pyperclip
import shutil
import pyautogui

from visual_control_tooling.core.utils import create_path_if_not_exists, get_all_files_from
from visual_control_tooling.core.log_system import Logger
from visual_control_tooling.core.vision_cortex import TemplateManager, smart_ui_clic
from visual_control_tooling.core.screen_area_management import get_gemcad_screen_area_params, get_window_screen_area_params, gemray_save_render_images_window_name, gemray_load_file_window_name
from visual_control_tooling.core.pc_interaction import Screenshotter, Cliquer
from visual_control_tooling.core.data_models import Rectangle, Point
from visual_control_tooling.core.im_manipulations import crop_im

"""
Example of how I automate softwares without API/command line interfaces

open gemray first and set the stone color to white
"""

gem_files_path = r"C:\checkout2\common-scripts\facet_diagrams\downloader\charles_covil_odd_series\diagrams"
pdf_output_path = os.path.join(gem_files_path, "diagrams", "pdf")
cropped_pdf_for_ocr_output_path = os.path.join(gem_files_path, "diagrams", "cropped_for_ocr")
create_path_if_not_exists(pdf_output_path)
create_path_if_not_exists(cropped_pdf_for_ocr_output_path)

# coordinate relative to the 'open file' window inside the text field
GEMRAY_OPEN_FILE_WINDOW_TEXTINPUT_AREA = Rectangle(Point(93, 589), Point(213, 603))
GEMCAD_SAVE_PDF_WINDOW_TEXTINPUT_AREA = Rectangle(Point(137, 398), Point(210, 413))

#################
## LOGGER INIT ##
#################
logger = Logger.get_instance()
logger.init_logger("gemcad_make_pdf_diagram_and_decode_values", "gemcad_bot_logs")

def build_template_manager(template_name):
    return TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, f"templates2/{template_name}", "out_screenshots")

def is_textfield_filled(relative_rectangle: Rectangle, window_name):
    """
    screenshot the open file window and crop the content of a textfield (you have to provide the coordinates, they
    never change because they are relative to that subwindow), then if black pixels are detected inside it is filled
    :param relative_rectangle:
    :param window_name:
    :return:
    """
    screen_area_param = get_window_screen_area_params(window_name)
    window_screenshot = screenshotter.take_screenshot(screen_area_param)
    textfield_crop = crop_im(window_screenshot, relative_rectangle.top_left_xy, relative_rectangle.bottom_right_xy)
    for row in textfield_crop:
        for pixel in row:
            if pixel[0] < 200 or pixel[1] < 200 or pixel[2] < 200:
                return True
    return False

def read_all_facet_diagrams_filenames(path):
    absolute_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".asc") or file.endswith(".gem"):
                absolute_paths.append(os.path.join(root, file))
    logger.log_info(fr"Found {len(absolute_paths)} diagrams")
    return absolute_paths

def open_gem_file(absolute_gemfile_filename):
    smart_ui_clic(tm_menu_file_button, tm_menu_file_open_button)
    smart_ui_clic(tm_menu_file_open_button, tm_openfile_dialog_file_textfield)
    time.sleep(0.5)
    paste_diagram_name(absolute_gemfile_filename, GEMRAY_OPEN_FILE_WINDOW_TEXTINPUT_AREA, "Open")
    tm_openfile_dialog_open_button.clic_on_template_if_present_untill_it_disseapear()

def print_pdf_on_file(absolute_gemfile_filename):
    # won't select the pdf printer, do it yourself by printing a pdf before
    logger.log_info("printing pdf")
    smart_ui_clic(tm_menu_file_button, tm_menu_file_print_button)
    smart_ui_clic(tm_menu_file_print_button, tm_print_window_dropdow_list_icon)
    smart_ui_clic(tm_print_window_ok_button, tm_save_pdf_window_indicator)
    basename = os.path.basename(absolute_gemfile_filename)
    name = basename[:-4]
    pdf_name = name + ".pdf"
    paste_data_in_textfield(pdf_name, GEMCAD_SAVE_PDF_WINDOW_TEXTINPUT_AREA , "Save Print Output As")
    tm_save_pdf_window_save_button.clic_on_template_if_present_untill_it_disseapear()


def paste_diagram_name(absolute_gemfile_filename, area: Rectangle, window_name):
    gemfile_name = os.path.basename(absolute_gemfile_filename)
    attempt = 0
    while True:
        logger.log_info("copy")
        pyperclip.copy(gemfile_name)
        time.sleep(0.1)
        logger.log_info("pasting")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        if is_textfield_filled(area, window_name):
            logger.log_info("Paste successfull")
            return

        attempt += 1
        time.sleep(0.3)
        if attempt > 3:
            logger.log_info(f"Failed to paste {gemfile_name} in {window_name}")
            raise Exception(f"Failed to paste {gemfile_name} in {window_name}")

def paste_data_in_textfield(data, area: Rectangle, window_name):
    attempt = 0
    while True:
        logger.log_info("copy")
        pyperclip.copy(data)
        time.sleep(0.1)
        logger.log_info("pasting")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        if is_textfield_filled(area, window_name):
            logger.log_info("Paste successfull")
            return

        attempt += 1
        time.sleep(0.3)
        if attempt > 3:
            logger.log_info(f"Failed to paste {data} in {window_name}")
            raise Exception(f"Failed to paste {data} in {window_name}")

def close_already_open_warning_if_present():
    time.sleep(0.5)
    if tm_already_open_warning_icon.template_is_present():
        logger.log_info("closing warning popup")
        tm_already_open_warning_yes_button.clic_on_template_if_present_untill_it_disseapear()
        time.sleep(1)

#
# YOU NEED TO OPEN MANUALLY A GEM FILE IN THE TARGETED FOLDER FIRST, ALMOST IMPOSSIBLE TO SET A FOLDER PROGRAMATICALLY
# won't select the pdf printer, do it yourself by printing a pdf before
# save a pdf where you want them to be saved, the bot won't select the folder
#

with mss.mss() as sct:
    MONITOR_NUM = 2
    gemcad_screen_area_params = get_gemcad_screen_area_params(sct, MONITOR_NUM)
    cliquer = Cliquer(gemcad_screen_area_params)
    screenshotter = Screenshotter("gemcad_render_bot", sct)

    # MAIN WINDOW
    tm_menu_file_button = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/3,3_72,70_name=menu-file-button_precision=0.8_priority=7.png", "out_screenshots")
    tm_menu_file_open_button = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/3,6_310,170_name=menu-file-open-button_precision=0.8_priority=7.png", "out_screenshots")
    tm_openfile_dialog_file_textfield = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/392,570_1496,1063_name=openfile-dialog-file-textfield_precision=0.8_priority=7.png", "out_screenshots")
    tm_openfile_dialog_open_button = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/1470,712_1905,1072_name=openfile-dialog-open-button_precision=0.8_priority=7.png", "out_screenshots")
    tm_menu_file_print_button = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/0,4_314,278_name=menu-file-print_precision=0.8_priority=7.png", "out_screenshots")

    # already opened popup warning
    tm_already_open_warning_icon = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/749,434_1174,598_name=already-open-warning-icon_precision=0.8_priority=7.png", "out_screenshots")
    tm_already_open_warning_yes_button = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/746,430_1188,600_name=already-open-warning-yes-button_precision=0.8_priority=7.png", "out_screenshots")

    # print window
    tm_print_window_dropdow_list_icon = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/729,333_1173,542_name=print-window-dropdow-list-icon_precision=0.8_priority=7.png", "out_screenshots")
    tm_print_window_ok_button = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/729,346_1184,685_name=print-window-ok-button_precision=0.8_priority=7.png", "out_screenshots")

    # save pdf window
    tm_save_pdf_window_indicator = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer, "templates/6,2_1649,886_name=save-pdf-window-indicator_precision=0.8_priority=7.png", "out_screenshots")
    tm_save_pdf_window_save_button = TemplateManager(gemcad_screen_area_params, screenshotter, cliquer,
                                                     "templates/400,400_1920,1080_name=save-pdf-window-save-button_precision=0.8_priority=7.png", "out_screenshots")

    diagrams_filenames = read_all_facet_diagrams_filenames(gem_files_path)
    for i, diagram_filename in enumerate(diagrams_filenames):
        logger.log_info(f"------------- Processing {i + 1}/{len(diagrams_filenames)} : {diagram_filename}")
        pdf_file_name = os.path.basename(diagram_filename).replace(".asc", ".pdf").replace(".gem", ".pdf")
        if os.path.exists(os.path.join(pdf_output_path, pdf_file_name)):
            logger.log_info("  -- already done")
            continue
        open_gem_file(diagram_filename)
        close_already_open_warning_if_present()
        print_pdf_on_file(diagram_filename)
        time.sleep(2)
