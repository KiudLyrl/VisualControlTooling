
import mss
import time
import os
import shutil

from visual_control_tooling.core.log_system import Logger
from visual_control_tooling.core.vision_cortex import TemplateManager
from visual_control_tooling.core.screen_area_management import get_gem_cut_studio_screen_area_params
from visual_control_tooling.core.pc_interaction import Screenshotter, Cliquer
from visual_control_tooling.core.data_models import Point

"""
Example of how I automate softwares without API/command line interfaces
"""

diagrams_path = r"C:\checkout2\common-scripts\facet_diagrams\facet_diagrams\ALL"
temp_folder_for_easy_load = r"C:\checkout2\common-scripts\facet_diagrams\facet_diagrams\temp_for_rendering"
animation_output_path = r"C:\Users\Oliver\Documents\GemCutStudio\Animations"
chart_output_path = r"C:\Users\Oliver\Documents\GemCutStudio\Designs"

file_button = Point(28, 36)
open_button = Point(41, 106)
first_file_tile = Point(223, 156)
open_file_button = Point(1690, 1012)

#################
## LOGGER INIT ##
#################
logger = Logger.get_instance()
logger.init_logger("gem_cut_studio_render_and_charts_grabber", "gemcutstudio_bot_logs")

def read_all_facet_diagrams_filenames(path):
    absolute_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".asc"):
                absolute_paths.append(os.path.join(root, file))
    logger.log_info(fr"Found {len(absolute_paths)} diagrams")
    return absolute_paths

def _erase_all_files_in_temp_folder():
    logger.log_info("emptying temp folder")
    for root, dirs, files in os.walk(temp_folder_for_easy_load):
        for file in files:
            os.remove(os.path.join(root, file))

def copy_file_in_temp_folder(filename, temp_folder_path):
    logger.log_info("Moving new diagram to temp folder")
    _erase_all_files_in_temp_folder()
    file_name = os.path.basename(filename)
    shutil.copy(filename, os.path.join(temp_folder_path, file_name))
    time.sleep(1)

def open_the_diagram_in_the_temp_folder(cliquer):
    logger.log_info("Opening the new diagram")
    cliquer.click_relative_to_screen_area_and_return_to_last_pos(file_button)
    time.sleep(0.5)
    cliquer.click_relative_to_screen_area_and_return_to_last_pos(open_button)
    time.sleep(0.5)
    cliquer.click_relative_to_screen_area_and_return_to_last_pos(first_file_tile)
    time.sleep(0.5)
    cliquer.click_relative_to_screen_area_and_return_to_last_pos(open_file_button)
    time.sleep(0.5)

def is_animation_already_saved(file_name):
    anim_file_name = file_name[:-4] + ".gif"
    anim_filename = animation_output_path + "\\" + anim_file_name
    logger.log_info(f"  - chacking {anim_filename}")
    return os.path.exists(anim_filename)

def is_chart_already_saved(file_name):
    chart_file_name = file_name[:-4] + "_graph.png"
    chart_filename = chart_output_path + "\\" + chart_file_name
    logger.log_info(f"  - chacking {chart_filename}")
    return os.path.exists(chart_filename)


## LOCATE GEMCUT STUDIO
gcs_screen_area_params = get_gem_cut_studio_screen_area_params()
cliquer = Cliquer(gcs_screen_area_params)

with mss.mss() as sct:
    screenshotter = Screenshotter("gemcut_studio_render_and_chart_bot", sct)

    # file > ... templates
    tm_top_menu_bar_file_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/7,4_61,55_name=menufilebutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_top_menu_bar_file_open_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/9,87_116,127_name=menuopenbutton_precision=0.8_priority=7.png", "out_screenshots")

    # tools > ... # templates
    tm_top_menu_bar_tools_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/201,10_275,55_name=menutoolbutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_top_menu_bar_tools_tiltperf_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/208,51_437,98_name=menutiltperfbutton_precision=0.8_priority=7.png", "out_screenshots")

    # tilt performances buttons
    tm_os_save_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/397,182_1720,1000_name=oswindowsavebutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_export_anim_button_1 = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/544,792_944,887_name=exportanimbutton1_precision=0.8_priority=7.png", "out_screenshots")
    tm_save_anim_button_2 = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/869,832_1058,912_name=animpopupsavebutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_anim_popup_close_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer,
                                                 "templates/1113,285_1179,331_name=animpopupclosebutton_precision=0.95_priority=7.png", "out_screenshots")
    tm_save_graph_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/1134,820_1366,881_name=tiltperfwindowsavegraphbutton_precision=0.8_priority=7.png", "out_screenshots")
    tm_tiltperf_close_button = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/1292,300_1387,375_name=tiltperfwindowclosebutton_precision=0.8_priority=7.png", "out_screenshots")

    tm_tilperf_creategif_dialog = TemplateManager(gcs_screen_area_params, screenshotter, cliquer, "templates/621,530_970,618_name=creategifdialog_precision=0.8_priority=7.png", "out_screenshots")


    diagrams_filenames = read_all_facet_diagrams_filenames(diagrams_path)
    for i, diagram_filename in enumerate(diagrams_filenames):
        logger.log_info(f"------------------- {i + 1}/{len(diagrams_filenames)}")
        logger.log_info(f"Processing {diagram_filename}")

        diagram_file_name = os.path.basename(diagram_filename)
        if is_animation_already_saved(diagram_file_name) and is_chart_already_saved(diagram_file_name):
            logger.log_info("  - Already processed")
            continue

        copy_file_in_temp_folder(diagram_filename, temp_folder_for_easy_load)
        open_the_diagram_in_the_temp_folder(cliquer)

        # open tilt perf
        tm_top_menu_bar_tools_button.clic_on_template_if_present_only_once()
        tm_top_menu_bar_tools_tiltperf_button.block_until_template_is_present(0.5, 5)
        tm_top_menu_bar_tools_tiltperf_button.clic_on_template_if_present_only_once()

        # save animation
        if not is_animation_already_saved(diagram_file_name):
            tm_export_anim_button_1.block_until_template_is_present(0.5, 5)
            tm_export_anim_button_1.clic_on_template_if_present_only_once()

            tm_save_anim_button_2.block_until_template_is_present(0.5, 30)
            tm_save_anim_button_2.clic_on_template_if_present_only_once()

            tm_os_save_button.block_until_template_is_present(0.5, 30)
            tm_os_save_button.clic_on_template_if_present_only_once()

            tm_tilperf_creategif_dialog.block_until_template_is_present(1, 30)

            tm_anim_popup_close_button.block_until_template_is_present(0.5, 30)
            tm_anim_popup_close_button.clic_on_template_if_present_only_once()
        else:
            logger.log_info("  - Animation already saved")

        # save graph
        if not is_chart_already_saved(diagram_file_name):
            tm_save_graph_button.block_until_template_is_present(0.5, 5)
            tm_save_graph_button.clic_on_template_if_present_only_once()

            tm_os_save_button.block_until_template_is_present(0.5, 30)
            tm_os_save_button.clic_on_template_if_present_only_once()
        else:
            logger.log_info("  - chart already saved")

        # close tilt perf
        tm_tiltperf_close_button.block_until_template_is_present(0.1, 5)
        tm_tiltperf_close_button.clic_on_template_if_present_only_once()
