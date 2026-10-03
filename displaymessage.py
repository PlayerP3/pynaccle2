import pygame,os,re,math,random,string,sys
import numpy as np
import json
import moderngl
from .animatedsprite import AnimatedSprite
from pygame.math import Vector2
from pyglm import glm
from .globs import delta
# from .timer import Timer
from .screen import gameScreen



class DisplayMessage(AnimatedSprite):

    def __init__(self):
        
        AnimatedSprite.__init__(self)

        self.is_text = True
        self.img_path = 'E'
 
    def spawn(self,pos:tuple):
        
        self.hurtbox.center = (pos[0]+self.spawnOffsetX,pos[1]+self.spawnOffsetY)
        
    def update_message(self,txt:str):
        self.img_path = txt

    def init(self):

        super().init_sprite()

