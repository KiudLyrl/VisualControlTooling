# import pygame
import pygame
import numpy as np
import cv2
import os
from os import listdir
from os.path import isfile, join
import shutil
import sys
import easygui

left_part = 442
right_part = 400
window_width = left_part + right_part
window_height = 1020
clock_tick_rate = 20
blue = 0, 0, 255
red = 255, 0, 0
white = 255, 255, 255
black = 0, 0, 0

images_path = "./GemRay_Options_screenshots/*.png"

class UiElement:
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.rect = pygame.Rect(left, top, width, height)

    def isMouseInElement(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
  
class TextField(UiElement):
    def __init__(self, screen, left, top, width, height, font, indications):
        UiElement.__init__(self, left, top, width, height)
        self.screen = screen
        self.text = ""
        self.font = font
        self.active = False
        self.indications = indications
        self.type = "textField"
    
    def draw_yourself(self):
        pygame.draw.rect(self.screen, white, self.rect)
        
        label_surface = myfont.render(self.text, 1, black)
        label_surface_width = label_surface.get_width()
        space_to_display_text_px = self.width
        space_remaining = space_to_display_text_px - label_surface_width
        text_side_space_to_center = space_remaining/2
        x = self.left + text_side_space_to_center

        label_surface_height = label_surface.get_height()
        space_to_display_text_px = self.height
        space_remaining = space_to_display_text_px - label_surface_height
        text_side_space_to_center = space_remaining/2
        y = self.top + text_side_space_to_center

        screen.blit(label_surface, (x, y))
    
    def reset(self):
        self.text = ""
        self.active = False

class Button(UiElement):
    def __init__(self, screen, left, top, width, height, text, font, indications):
        UiElement.__init__(self, left, top, width, height)
        self.screen = screen
        self.text = text
        self.font = font
        self.active = False
        self.coordinate_selected = "N/A"
        self.indications = indications
        self.type = "coordinate button"
    
    def reset(self):
        self.coordinate_selected = "N/A"
        self.active = False

    def draw_yourself(self):
        color = (0, 255, 0)
        if not self.active:
            color = (255, 0, 0)
        pygame.draw.rect(self.screen, color, self.rect)
        
        label_surface = myfont.render(self.text, 1, (255,255,0))
        label_surface_width = label_surface.get_width()
        space_to_display_text_px = self.width
        space_remaining = space_to_display_text_px - label_surface_width
        text_side_space_to_center = space_remaining/2
        x = self.left + text_side_space_to_center

        label_surface_height = label_surface.get_height()
        space_to_display_text_px = self.height
        space_remaining = space_to_display_text_px - label_surface_height
        text_side_space_to_center = space_remaining/2
        y = self.top + text_side_space_to_center

        screen.blit(label_surface, (x, y))
        
        coordinate_label_surface = myfont.render(str(self.coordinate_selected), 1, (255,255,0))
        x = self.left + self.width + 30
        screen.blit(coordinate_label_surface, (x, y))

def draw_separations(screen):
    point1 = left_part, 0
    point2 = left_part, window_height
    pygame.draw.line(screen, blue, point1, point2)

def draw_text_indication(screen, text):
    label_surface = myfont.render(text, 1, (255,255,0))
    label_surface_width = label_surface.get_width()
    label_surface_height = label_surface.get_height()
    space_to_display_text_px = right_part
    space_remaining = space_to_display_text_px - label_surface_width
    text_side_space_to_center = space_remaining/2
    x = left_part + text_side_space_to_center
    y = 5
    screen.blit(label_surface, (x, y))

def isMouseInLeftPart(mouse_pos):
    return mouse_pos[0] < left_part

def reset_all_uiElements(buttons):
    for button in buttons:
        button.reset()

def deactivate_all_uiElements(buttons):
    for button in buttons:
        button.active = False

def draw_area_selected(screen, color, topleft, bottomright):
    if topleft != "N/A":
        if bottomright != "N/A":
            #ligne du dessus
            pygame.draw.line(screen, color, topleft, (bottomright[0], topleft[1]), 2)
            #cote droit
            pygame.draw.line(screen, color, bottomright, (bottomright[0], topleft[1]), 2)
            #ligne du dessous
            pygame.draw.line(screen, color, bottomright, (topleft[0], bottomright[1]), 2)
            #cote gauche
            pygame.draw.line(screen, color, topleft, (topleft[0], bottomright[1]), 2)
            return
    
    if topleft != "N/A":
        pygame.draw.line(screen, color, topleft, (topleft[0]+10, topleft[1]), 2)
        pygame.draw.line(screen, color, topleft, (topleft[0], topleft[1]+10), 2)
        return
    
    if bottomright != "N/A":
        pygame.draw.line(screen, color, bottomright, (bottomright[0], bottomright[1]-10), 2)
        pygame.draw.line(screen, color, bottomright, (bottomright[0]-10, bottomright[1]), 2)

def draw_point(screen, color, coordinate):
    if coordinate is None or coordinate == "N/A":
        return
    
    pygame.draw.line(screen, color, coordinate, (coordinate[0]+10, coordinate[1]), 2)
    pygame.draw.line(screen, color, coordinate, (coordinate[0]-10, coordinate[1]), 2)
    pygame.draw.line(screen, color, coordinate, (coordinate[0], coordinate[1]+10), 2)
    pygame.draw.line(screen, color, coordinate, (coordinate[0], coordinate[1]-10), 2)

def generate_template_file(uiElements, im_path):
    for uiElement in uiElements:
        if uiElement.text == "SA_topleft":
            topleft_sa_str = str(uiElement.coordinate_selected).replace(")", "").replace("(", "").replace(" ", "")
        if uiElement.text == "SA_bottomright":
            bottomright_sa_str = str(uiElement.coordinate_selected).replace(")", "").replace("(", "").replace(" ", "")
        if uiElement.text == "template topleft":
            template_topleft = uiElement.coordinate_selected
        if uiElement.text == "template bottomright":
            template_bottomright = uiElement.coordinate_selected
        if uiElement.type == "textField":
            name = uiElement.text
        if uiElement.text == "clic pos (optional)":
            clic_pos = str(uiElement.coordinate_selected).replace(")", "").replace("(", "")
    
    if clic_pos == "N/A":
        template_name = "{}_{}_name={}_precision=0.8_priority=7.png".format(topleft_sa_str, bottomright_sa_str, name)
    else:
        template_name = "{}_{}_name={}_precision=0.8_clicOverride={}_priority=7.png".format(topleft_sa_str, bottomright_sa_str, name, clic_pos)
    
    print("Generation" + template_name)
    im = cv2.imread(im_path)
    template_im = im[template_topleft[1]:template_bottomright[1], template_topleft[0]:template_bottomright[0]]
    cv2.imwrite(template_name, template_im)

pygame.init()
size = (window_width, window_height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Vysor template creator")
dead=False
clock = pygame.time.Clock()

path_of_the_pic = None
original_pic_pygame_im = None
myfont = pygame.font.SysFont("monospace", 15)


button_height = 30
button_width = 200
button_left = left_part + 65

openfile_button = Button(screen, button_left, 50, button_width, button_height, "OPEN FILE", myfont, "Choose a file")

sa_topleft_button = Button(screen, button_left, 150, button_width, button_height, "SA_topleft", myfont, "Choose the search area topleft point")
sa_bottomright_button = Button(screen, button_left, 200, button_width, button_height, "SA_bottomright", myfont, "Choose the search bottom right point")
template_topleft_button = Button(screen, button_left, 250, button_width, button_height, "template topleft", myfont, "Choose the template topleft point")
template_bottomright_button = Button(screen, button_left, 300, button_width, button_height, "template bottomright", myfont, "Choose the template bottom right point")
clic_pos_button = Button(screen, button_left, 350, button_width, button_height, "clic pos (optional)", myfont, "Choose the point")
name_textfield = TextField(screen, button_left, 400, button_width, button_height, myfont, "Type a name")
generate_button = Button(screen, button_left, 450, button_width, button_height, "Generate", myfont, "Generating...")
uiElements = [sa_topleft_button, sa_bottomright_button, template_topleft_button, template_bottomright_button, clic_pos_button, name_textfield, generate_button, openfile_button]

draw_text_indication(screen, "Choose a button then clic on the image")
while(dead==False):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            dead = True

        if event.type == pygame.MOUSEBUTTONUP:
            screen.fill(pygame.Color("black")) # erases the entire screen surface
            if isMouseInLeftPart(pygame.mouse.get_pos()):
                pos = pygame.mouse.get_pos() # un tuple qui contient (x, y)
                for uiElement in uiElements:
                    if uiElement.active == True and uiElement.type == "coordinate button":
                        uiElement.coordinate_selected = pos
                        continue

            deactivate_all_uiElements(uiElements)
            for uiElement in uiElements:
                if uiElement.isMouseInElement(pygame.mouse.get_pos()):
                    uiElement.active = True
                    draw_text_indication(screen, uiElement.indications)
            
            if generate_button.active:
                generate_template_file(uiElements, path_of_the_pic)
                reset_all_uiElements(uiElements)
            elif openfile_button.active:
                path_of_the_pic = easygui.fileopenbox(default=images_path)
                original_pic_pygame_im = pygame.image.load(path_of_the_pic).convert()
                reset_all_uiElements(uiElements)

        if event.type == pygame.KEYDOWN:
            if name_textfield.active:
                if pygame.key.name(event.key) == 'backspace':
                    name_textfield.text = name_textfield.text[:-1]
                else:
                    name_textfield.text += pygame.key.name(event.key)

    if original_pic_pygame_im is not None:
        screen.blit(original_pic_pygame_im, [0, 0])
    draw_separations(screen)
    
    for uiElement in uiElements:
        uiElement.draw_yourself()

    draw_area_selected(screen, (255, 0, 0), sa_topleft_button.coordinate_selected, sa_bottomright_button.coordinate_selected)
    draw_area_selected(screen, (0, 255, 0), template_topleft_button.coordinate_selected, template_bottomright_button.coordinate_selected)
    draw_point(screen, (0, 0, 255), clic_pos_button.coordinate_selected)
    pygame.display.flip()
    clock.tick(clock_tick_rate)