import pygame,random,os,string,numpy,math,sys
from .animatedsprite import AnimatedSprite,GameSprites
from .screen import gameScreen
from pyglm import glm

class HUD_element(AnimatedSprite):

    def __init__(self,win_pos:tuple=(0,0),winPosWidthRatio:float=0,winPosHeightRatio:float=0,winPosWidthOffsetRatio:float=0,winPosHeightOffsetRatio:float=0):

        AnimatedSprite.__init__(self)

        # you can give a set of sprite objects to the hud element, and give a zlayer as well, and then it handles how it is drawn by the hud
        # the position is always 
        self.display = True

        # linked var or object that helps control what is displayed and how
        self.linked_obj = None
        self.linked_var = None

        self.win_pos = win_pos
        self.winPosWidthRatio = winPosWidthRatio
        self.winPosHeightRatio = winPosHeightRatio

        self.winPosWidthOffsetRatio = winPosWidthOffsetRatio
        self.winPosHeightOffsetRatio = winPosHeightOffsetRatio

        

        

        # list of functions we will execute
        self.extraProcessing = []

    # reinit
    def init(self,attributes:dict={}):

        for att,val in attributes.items():

            setattr(self,att,val)
        
        # init sprite variables
        self.init_sprite(SpriteCache=GameSprites)

        self.hurtbox.width = self.hurtbox_width
        self.hurtbox.height = self.hurtbox_height

        # calculate win pos based on xpercentage and ypercentage on screen, subtract 
        # so now width ratio and hgeight ratio ranges from -1 to 1 because it assumes (0,0) as the starting point
        x = ((- gameScreen.windows[self.surface_to_draw_on].win_width//2) + (gameScreen.windows[self.surface_to_draw_on].win_width * self.winPosWidthRatio))/gameScreen.windows[self.surface_to_draw_on].zoom
        y = ((- gameScreen.windows[self.surface_to_draw_on].win_height//2) + (gameScreen.windows[self.surface_to_draw_on].win_height * self.winPosHeightRatio))/gameScreen.windows[self.surface_to_draw_on].zoom

        self.win_pos = (x,y)

        self.hurtbox.center = self.win_pos

        self.original_vars = {k:v for k,v in self.__dict__.items()}

    # function to update some preoprty about the hud
    def update(self):

        if self.extraProcessing:

            for f in self.extraProcessing:

                f(self)

        # draw
        self.submit_to_render()
        
    def set_default_uniforms(self):

        gameScreen.shaderPrograms[self.shader]['memSlot'] = 0
        gameScreen.shaderPrograms[self.shader]['alpha'] = self.alpha
        gameScreen.shaderPrograms[self.shader]['screenSize'] = (gameScreen.windows[self.surface_to_draw_on].win_width,gameScreen.windows[self.surface_to_draw_on].win_height)
        gameScreen.shaderPrograms[self.shader]['spriteSize'] = self.sprite.get_size()
        gameScreen.shaderPrograms[self.shader]['spriteOffset'] = (self.sprite_offsetx,self.sprite_offsety)
        gameScreen.shaderPrograms[self.shader]['position'] = (self.hurtbox.center)
        gameScreen.shaderPrograms[self.shader]['rotation'] = math.radians(float(self.direction))
        gameScreen.shaderPrograms[self.shader]['bgOffset'] = (0,0)
        gameScreen.shaderPrograms[self.shader]['zoom'] = self.zoom
        gameScreen.shaderPrograms[self.shader]['screenZoom'] = gameScreen.windows[self.surface_to_draw_on].zoom


    def set_shader_dependent_uniforms(self):
        
        return
        

    def new_zoom_position(self):

        x = ((- gameScreen.windows[self.surface_to_draw_on].win_width//2) + (gameScreen.windows[self.surface_to_draw_on].win_width * self.winPosWidthRatio))/gameScreen.windows[self.surface_to_draw_on].zoom
        y = ((- gameScreen.windows[self.surface_to_draw_on].win_height//2) + (gameScreen.windows[self.surface_to_draw_on].win_height * self.winPosHeightRatio))/gameScreen.windows[self.surface_to_draw_on].zoom

        self.win_pos = (x,y)

        self.hurtbox.center = self.win_pos

class HUD():

    def __init__(self):

        self.hud_elements = {}
        self.active_elements = []


    def add_element(self,group:str,hud_element:HUD_element):

        if not group in self.hud_elements:

            self.hud_elements[group] = [hud_element]

        elif group in self.hud_elements:

            self.hud_elements[group].append(hud_element)
        

    def display_hud(self):

        # get active elemnets
        self.active_elements = []

        for group in self.hud_elements:

            for hud_element in self.hud_elements[group]:

                if hud_element.display:

                    hud_element.update()
                    # self.parent_node.submit_to_render()
                    # hud_element.draw_surface(position=hud_element.hurtbox.center)

                    # draw rect for debugging 
                    # hud_element.draw_rect()

                    self.active_elements.append(hud_element)

    # give list of hud element groups and they will be turned off
    def deactivate_hud_elements(self,groupNames:list):

        for group in groupNames:

            for hudElement in self.hud_elements[group]:

                hudElement.display = False


    # give list of hud element groups and they will be turned off
    def activate_hud_elements(self,groupNames:list):

        for group in groupNames:

            for hudElement in self.hud_elements[group]:

                hudElement.display = True

                hudElement.new_zoom_position()
        




  


# set hud
overlay = HUD()