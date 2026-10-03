import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from ...statemachine import State
from ...utils import *
from ...objectsystem import objectManager


class Reset(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

        self.parent_node.interactingObj = None

        # reset timer
        self.parent_node.animationPlayer.timer_speed = 10
        self.parent_node.animationPlayer.currentFrameNumber = self.parent_node.animationPlayer.totalFrames - 1

        self.parent_node.animationPlayer.animationType = 'reverse'
        self.parent_node.animationPlayer.reset_timer()
        self.parent_node.animationPlayer.start_timer(startTime=1)

        self.parent_node.purchasingObj = None

    def update(self):

        # run timer
        self.run_timer()

        # set sprite sheet to be idle animation
        self.parent_node.update_position()  

        # run move and collide, end condition is in here
        self.parent_node.move_and_collide()  

        # draw surface
        self.parent_node.submit_to_render()
        # self.parent_node.draw_rect(position=self.parent_node.spawnLocation)

        # if timer is complete emit cycling
        if self.parent_node.animationPlayer.timer_complete:

            self.emit('IDLE')

    def collision_check(self,axis:str='y'):

        pass

    # handle collision once the check is confirmed
    def handle_collision(self,game_object:object,axis:str):

       pass