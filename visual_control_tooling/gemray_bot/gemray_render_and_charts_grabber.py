
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
from visual_control_tooling.core.screen_area_management import get_gemray_screen_area_params, get_window_screen_area_params, gemray_save_render_images_window_name, gemray_load_file_window_name
from visual_control_tooling.core.pc_interaction import Screenshotter, Cliquer
from visual_control_tooling.core.data_models import Rectangle, Point
from visual_control_tooling.core.im_manipulations import crop_im

"""
Example of how I automate softwares without API/command line interfaces

open gemray first and set the stone color to white, also open one of the diagram so that the open window goes into the correct folder
"""

diagrams_path = r"C:\checkout2\common-scripts\facet_diagrams\downloader\charles_covil_odd_series\diagrams"
gif_output_path = os.path.join(diagrams_path, "gemray", "renders")
static_output_path = os.path.join(diagrams_path, "gemray", "static")
create_path_if_not_exists(gif_output_path)
create_path_if_not_exists(static_output_path)

GEMRAY_OPEN_FILE_WINDOW_TEXTINPUT_AREA = Rectangle(Point(204, 649), Point(322, 665))
GEMRAY_SAVE_FILE_WINDOW_TEXTINPUT_AREA = Rectangle(Point(143, 581), Point(245, 592))

#################
## LOGGER INIT ##
#################
logger = Logger.get_instance()
logger.init_logger("gem_cut_studio_render_and_charts_grabber", "gemcutstudio_bot_logs")

def build_template_manager(template_name):
    return TemplateManager(gcs_screen_area_params, screenshotter, cliquer, f"templates2/{template_name}", "out_screenshots")

def is_textfield_filled(relative_rectangle: Rectangle, window_name):
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

def get_all_jpgs(path):
    all_files = get_all_files_from(path)
    absolute_paths = []
    for filename in all_files:
        if filename.endswith(".jpg"):
            absolute_paths.append(os.path.join(path, filename))
    return absolute_paths

def open_diagram(absolute_filename):
    smart_ui_clic(tm_open_diagram_button, tm_os_open_diagram_validate_button)
    time.sleep(0.2)
    tm_os_open_diagram_input_textfield.block_until_template_is_present(0.3, 5)
    paste_diagram_name(absolute_filename, GEMRAY_OPEN_FILE_WINDOW_TEXTINPUT_AREA, gemray_load_file_window_name)
    is_textfield_filled(GEMRAY_OPEN_FILE_WINDOW_TEXTINPUT_AREA, gemray_load_file_window_name)
    tm_os_save_textfield.clic_on_template_if_present_only_once()
    time.sleep(0.3)
    smart_ui_clic(tm_os_open_diagram_validate_button, tm_os_open_render_button)

def paste_diagram_name(diagram_filename, area: Rectangle, window_name):
    diagram_name = os.path.basename(diagram_filename)
    attempt = 0
    while True:
        logger.log_info("copy")
        pyperclip.copy(diagram_name)
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
            logger.log_info(f"Failed to paste {diagram_name} in {window_name}")
            raise Exception(f"Failed to paste {diagram_name} in {window_name}")

def open_and_save_render(diagram_filename):
    smart_ui_clic(tm_os_open_render_button, tm_generate_render_ims_button)
    smart_ui_clic(tm_generate_render_ims_button, tm_os_save_textfield)
    paste_diagram_name(diagram_filename.replace(".asc", "").replace(".gem", ""), GEMRAY_SAVE_FILE_WINDOW_TEXTINPUT_AREA, gemray_save_render_images_window_name)
    tm_os_save_textfield.clic_on_template_if_present_only_once()
    time.sleep(0.3)
    smart_ui_clic(tm_os_save_button, tm_gemray_render_close_button)
    smart_ui_clic(tm_gemray_render_close_button, tm_open_diagram_button)

def merge_files_into_gif_and_cleanup(diagrams_path, diagram_filename):
    diagram_name_no_ext = os.path.basename(diagram_filename.replace(".asc", "").replace(".gem", ""))
    jpgs = get_all_jpgs(diagrams_path)
    if len(jpgs) != 61:
        raise Exception(f"Did not found 61 jpgs, instead found {len(jpgs)}, {jpgs}")
    static_im_path = jpgs[30]
    shutil.copy(static_im_path, os.path.join(diagrams_path, "gemray", "static", f"{diagram_name_no_ext}.jpg"))
    gif_path = os.path.join(diagrams_path, "gemray", "renders", f"{diagram_name_no_ext}.gif")

    before_anim = []
    center_anim = jpgs[30]
    after_anim = []

    for i, im_path in enumerate(jpgs):
        if i < 30:
            before_anim.append(im_path)
        elif i > 30:
            after_anim.append(im_path)

    total_anim = [center_anim]
    total_anim.extend(after_anim)
    total_anim.extend(after_anim[::-1])
    total_anim.append(center_anim)
    total_anim.extend(before_anim[::-1])
    total_anim.extend(before_anim)

    images = []
    for filename in total_anim:
        images.append(imageio.imread(filename))
    fps = 30
    duration_per_frame = 1.0 / fps
    imageio.mimsave(gif_path, images, format='GIF', fps=30, loop=0)

    for filename in jpgs:
        try:
            os.unlink(filename)
        except PermissionError:
            print(f"{filename} is locked, waiting 2 secs")
            time.sleep(2)
            os.unlink(filename)



with mss.mss() as sct:
    MONITOR_NUM = 2
    gcs_screen_area_params = get_gemray_screen_area_params(sct, MONITOR_NUM)
    cliquer = Cliquer(gcs_screen_area_params)
    screenshotter = Screenshotter("gemray_render_bot", sct)

    # first window
    tm_open_diagram_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/308,38_1644,885_name=gemrayopenfilebutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_os_open_diagram_input_textfield = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/313,43_1896,970_name=gemrayopenfilefieldinput_precision=0.8_priority=7_clic_offset=50,0.png", "out_screenshots")
    tm_os_open_diagram_validate_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/252,49_1907,988_name=gemrayopenbutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_os_open_render_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/236,35_1769,864_name=gemraygotorenderbutton_precision=0.8_priority=7.png", "out_screenshots")

    # render window
    tm_generate_render_ims_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/214,33_1847,964_name=gemraygenerateimagesbuttons_precision=0.8_priority=7.png", "out_screenshots")
    tm_os_save_textfield = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/326,46_1908,1004_name=gemraysavefiletextinputfield_precision=0.8_priority=7_clic_offset=50,0.png", "out_screenshots")
    tm_os_save_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/221,33_1904,996_name=gemraysavebutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_gemray_render_close_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/181,20_1870,973_name=gemrayrenderclosebutton_precision=0.8_priority=7.png", "out_screenshots")

    diagrams_filenames = read_all_facet_diagrams_filenames(diagrams_path)
    for i, diagram_filename in enumerate(diagrams_filenames):
        logger.log_info(f"------------- Processing {i + 1}/{len(diagrams_filenames)} : {diagram_filename}")
        gif_file_name = diagram_name = os.path.basename(diagram_filename).replace(".asc", ".gif").replace(".gem", ".gif")
        if os.path.exists(os.path.join(gif_output_path, gif_file_name)):
            logger.log_info("  -- already done")
            continue
        open_diagram(diagram_filename)
        open_and_save_render(diagram_filename)
        merge_files_into_gif_and_cleanup(diagrams_path, diagram_filename)
