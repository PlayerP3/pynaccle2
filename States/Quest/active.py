import pygame,os,re,math,random,string,sys
import json
from ...objectsystem import objectManager
from pygame.math import Vector2
from ...statemachine import State


class Active(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

       pass

    def update(self):

        self.parent_node.update_task()