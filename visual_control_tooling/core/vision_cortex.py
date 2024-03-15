# -*- coding: utf-8 -*

import cv2
import os
import time

import visual_control_tooling.core.im_manipulations as iman
from visual_control_tooling.core.data_models import Point
from visual_control_tooling.core.utils import create_path_if_not_exists
from visual_control_tooling.core.exceptions import UnrecoverableException, RecoverableException
from visual_control_tooling.core.log_system import Logger

# TODO : should be move into data_models
class Template:
    def __init__(self, filename):
        """
            filename : the filename that was used to load the im
            name : a name for this template, can be anything, will be used for logging
            im : an opencv bgr image
            search_area_topleft : Point(x, y) : top left of the area where the template is to be seached (relative to screenshot image)
            search_area_bottomright : Point(x, y) : bottom right of the area where the template is to be seached (relative to screenshot image)
            clic_delay : delay to wait after detection before clicquin (can be zero)
            clic_offset : Point(x, y) : offset relative to detection for clic, clic override has priority over this
            clic_override : Point(x, y) : position in the screenshot where to clic if detection happens, otherwhise clic in (template detection position + clic offset)
            precision : precision during the template search, 0 to 1 (1 = 100%)
        """
        self.im = cv2.imread(filename)
        if self.im is None:
            raise UnrecoverableException("Unrecoverable error : can't find template on drive")
        head, tail = os.path.split(filename)
        self.filename = tail
        self.name = None
        self.search_area_topleft = None
        self.search_area_bottomright = None
        self.clic_delay = None
        self.clic_offset = None
        self.clic_override = None
        self.precision = None
        self.post_delay = None
        self.make_disappear = None
        self.priority = 7  # default to 7
        self._init_according_to_filename(self.filename)

    
    def override_search_area(self, topleft_point, bottomright_point):
        """
        to bypass the filename, only for test, do not use
        yeah we can directly access the properties but using this makes it clear in the code that we are hacking
        and we then can use "find reference" to find all the code that uses it
        """
        self.search_area_topleft = topleft_point
        self.search_area_bottomright = bottomright_point

    def _init_according_to_filename(self, filename):
        filename = filename.replace('.png', '')
        splitted = filename.split("_")
        if len(splitted) < 2:
            raise UnrecoverableException(
                "On devrais au moins avoir la search area et la precision dans le nom de fichier : {}".format(filename))

        topleft_splitted = splitted[0].split(",")
        self.search_area_topleft = Point(int(topleft_splitted[0]), int(topleft_splitted[1]))
        bottomright_splitted = splitted[1].split(",")
        self.search_area_bottomright = Point(int(bottomright_splitted[0]), int(bottomright_splitted[1]))

        self.clic_delay = self._get_param(splitted, "clicDelay")
        self.clic_offset = self._get_param(splitted, "clicOffset")
        self.clic_override = self._get_param(splitted, "clicOverride")
        if self.clic_override is not None:
            xy = self.clic_override.split(",")
            self.clic_override = Point(int(xy[0]), int(xy[1]))
        self.precision = float(self._get_param(splitted, "precision"))
        self.name = self._get_param(splitted, "name")
        post_delay = self._get_param(splitted, 'postDelay')
        if post_delay is not None:
            self.post_delay = int(post_delay)
        make_disappear = self._get_param(splitted, 'makeDisappear')
        if make_disappear is not None:
            self.make_disappear = True
        else:
            self.make_disappear = False
        priority = self._get_param(splitted, "priority")
        if priority is not None:
            self.priority = int(priority)

    def _get_param(self, splitted, param):
        for block in splitted:
            if block.find(param) != -1:
                return block.split("=")[1]
        return None


class TemplateManager:
    """
    Coontains the screen area parameters, sct, the conf, the template loaded im, is in charge of looking at the screen
    and cliquing or indicating where the template is.
    """
    def __init__(self, screen_area_params, screenshotter, cliquer, template_path, save_screenshot_path: str):
        """
        Constructor

        :param logger: the logger
        :param screen_area_manager : l'objet capable de prendre des screenshots et cliquer
        :param conf: the configuration
        :param template_path: the path of the template img used by this manager
        """
        self.logger = Logger.get_instance()
        self.screen_area_params = screen_area_params
        self.screenshotter = screenshotter
        self.template = Template(template_path)
        self.last_detection = None
        self.save_screenshot_path = save_screenshot_path
        self.cliquer = cliquer

    def get_position(self, screen_area_im):
        """
        Indicate the position of the template (relative to the screen area)

        screen_area_im : a screenshot of the screen area, allow you to analyse an old screenshot
        :return: a Point containing the coordinate of the template (relative to the screen area
        """
        self.logger.log_info("{}_manager : checking if '{}' is present in screen area".format(self.template.name, self.template.name))

        cropped_im = self._crop_search_area(screen_area_im)

        template_position = iman.locate_template_in_image(cropped_im, self.template.im, threshold=self.template.precision)
        if template_position is None:
            self.logger.log_info("{}_manager : '{}' is absent".format(self.template.name, self.template.name))
            return None
        else:
            self.logger.log_info("{}_manager : '{}' is present".format(self.template.name, self.template.name))
            self.last_detection = time.time()
            return Point(template_position.x + self.template.search_area_topleft.x, template_position.y + self.template.search_area_topleft.y)

    def is_present(self, screen_area_im):
        """
        Indicate if a template is present or not

        screen_area_im : a screenshot of the screen area, allow you to analyse an old screenshot
        :return: True if the template is present, False otherwhise
        """
        self.logger.log_info("{}_manager : checking if '{}' is present in screen area".format(self.template.name, self.template.name))

        cropped_im = self._crop_search_area(screen_area_im)

        template_position = iman.locate_template_in_image(cropped_im, self.template.im, threshold=self.template.precision)
        if template_position is None:
            self.logger.log_info("{}_manager : '{}' is absent".format(self.template.name, self.template.name))
            return False
        else:
            self.logger.log_info("{}_manager : '{}' is present".format(self.template.name, self.template.name))
            self.last_detection = time.time()
            return True

    def _crop_search_area(self, im):
        self.logger.log_info("{}_manager : cropping topleft : {}, bottomright : {}".format(self.template.name, self.template.search_area_topleft.toString(), self.template.search_area_bottomright.toString()))
        return iman.crop_im(im, self.template.search_area_topleft, self.template.search_area_bottomright)

    def getTimeSinceLastDetectionSec(self):
        if self.last_detection is None:
            return None

        return time.time() - self.last_detection

    def _clic_in_search_area(self, template_location):
        """
        As the image is cropped in the search area then the returned coordinates are relative to the screen area,
        this method convert the screen area coordinates to the regular window coordinates and then clic it

        :param template_location: a Point() containing the coordinate of the template in the search area
        """

        self.logger.log_info("{}_manager : template location in search area = {}, {}".format(self.template.name, template_location.x, template_location.y))

        if self.template.clic_override is None:
            x_clic = template_location.x + self.template.search_area_topleft.x
            y_clic = template_location.y + self.template.search_area_topleft.y
        else:
            x_clic = self.template.clic_override.x
            y_clic = self.template.clic_override.y
        self.logger.log_info("{}_manager : template location in screen area = {}, {}".format(self.template.name, x_clic, y_clic))
        self.cliquer.click_relative_to_screen_area_and_return_to_last_pos(Point(x_clic, y_clic))
        
        if self.template.post_delay is not None:
            self.logger.log_info("{}_manager : postDelay = {}, waiting".format(self.template.name, self.template.post_delay))
            for x in range(self.template.post_delay):
                print("Waiting {} seconds\r".format(self.template.post_delay-x), end='')
                time.sleep(1)

    def block_until_template_is_present(self, iteration_time, timeout):
        # loop that keep looking and cliquing every 0.3 sec in case the clic missed
        self.logger.log_info("{}_manager : blocking untill found".format(self.template.name))
        start = time.time()
        while True:
            time.sleep(iteration_time)
            fresh_im = self.screenshotter.take_screenshot(self.screen_area_params)
            fresh_cropped_im = self._crop_search_area(fresh_im)
            template_current_pos_point = iman.locate_template_in_image(fresh_cropped_im, self.template.im, threshold=self.template.precision)

            if template_current_pos_point is not None:
                return

            looping_since = time.time() - start
            if looping_since > timeout:
                raise RecoverableException("Stuck in infinite loop (more than " + str(timeout) + " sec) looking for : " + self.template.name)

    def _block_until_template_disseapear_while_recliquing_it_if_still_present(self, iteration_time, timeout):
        # loop that keep looking and cliquing every iteration_time sec in case the clic missed
        self.logger.log_info("{}_manager : blocking untill it disseapears".format(self.template.name))
        start = time.time()
        while True:
            time.sleep(iteration_time)
            fresh_im = self.screenshotter.take_screenshot(self.screen_area_params)
            fresh_cropped_im = self._crop_search_area(fresh_im)
            template_current_pos_point = iman.locate_template_in_image(fresh_cropped_im, self.template.im, threshold=self.template.precision)

            if template_current_pos_point is None:
                return

            self._clic_in_search_area(template_current_pos_point)
            looping_since = time.time() - start
            if looping_since > timeout:
                raise RecoverableException("Timeout (more than " + str(timeout) + " sec) looking for : " + self.template.name)
    
    def clic_on_template_auto(self, save_clic):
        self.logger.log_info("{}_manager : '{}' clic_on_template_auto()".format(self.template.name, self.template.name))
        if self.template.make_disappear:
            return self.clic_on_template_if_present_untill_it_disseapear(save_clic)
        else:
            return self.clic_on_template_if_present_only_once(save_clic)

    def clic_on_template_if_present_only_once(self, save_clic=False):
        self.logger.log_info("{}_manager : checking if '{}' is present on screen".format(self.template.name, self.template.name))
        cropped_im = self._crop_search_area(self.screenshotter.take_screenshot(self.screen_area_params))
        template_position_point = iman.locate_template_in_image(cropped_im, self.template.im, threshold=self.template.precision)
        if template_position_point is None:
            self.logger.log_info("{}_manager : no tmplate found".format(self.template.name))
            return False
        self.logger.log_info("{}_manager : detection success, processing".format(self.template.name))
        self._clic_in_search_area(template_position_point)
        if save_clic:
            path = os.path.join(self.save_screenshot_path, 'cliqued_screenshots')
            create_path_if_not_exists(path)
            filename = os.path.join(rf"{self.save_screenshot_path}\{str(self.screenshotter.last_pic_taken_date)}_{self.template.name}.png")
            cv2.imwrite(filename, self.screenshotter.last_pic_taken)
        return True

    def clic_on_template_if_present_untill_it_disseapear(self, save_clic=False, timeout_seconds=7):
        self.logger.log_info("{}_manager : checking if '{}' is present on screen".format(self.template.name, self.template.name))
        cropped_im = self._crop_search_area(self.screenshotter.take_screenshot(self.screen_area_params))
        template_position_point = iman.locate_template_in_image(cropped_im, self.template.im, threshold=self.template.precision)
        if template_position_point is None:
            return False
        self.logger.log_info("{}_manager : detection success, processing".format(self.template.name))
        self._clic_in_search_area(template_position_point)
        if save_clic:
            path = os.path.join(self.save_screenshot_path, 'cliqued_screenshots')
            create_path_if_not_exists(path)
            filename = os.path.join(rf"{self.save_screenshot_path}\{str(self.screenshotter.last_pic_taken_date)}_{self.template.name}.png")
            cv2.imwrite(filename, self.screenshotter.last_pic_taken)
        self._block_until_template_disseapear_while_recliquing_it_if_still_present(0.5, timeout_seconds)
        return True
