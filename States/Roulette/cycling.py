import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from ...statemachine import State
from ...utils import *
from ...objectsystem import objectManager


class Cycling(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

        self.parent_node.interactingObj = None
        self.parent_node.interactTimer.reset_timer()

        self.parent_node.interactTimer.timer_limit = self.parent_node.idleInteractTimerLimit

        self.parent_node.animationPlayer.timer_speed = 10
        self.parent_node.animationPlayer.animationType = 'forward'
        self.parent_node.animationPlayer.currentFrameNumber = 0
        self.parent_node.animationPlayer.reset_timer()
        self.parent_node.animationPlayer.start_timer()

        self.parent_node.filter_cycle_options()

        # reset timer
        self.reset_timer()
        self.start_timer()

        self.parent_node.cycleTimer.reset_timer()
        self.parent_node.cycleTimer.start_timer()
        self.parent_node.cycleTimer.elapsed_time = self.parent_node.cycleTimer.timer_limit #allos us to choose new sprite

        # get cycle options
        self.parent_node.predetermine_cycle_options()

        # set display item posiion
        self.parent_node.displayItem.hurtbox.center = self.parent_node.hurtbox.center

        # set sprite size as min
        self.parent_node.displayItem.zoom = self.parent_node.minDisplayItemZoom

        # reset lerp timer
        self.parent_node.displayItem.lerpTimer.reset_timer()
        
    def update(self):

        # run timer
        self.run_timer()

        # set sprite sheet to be idle animation
        self.parent_node.update_position()

        # run move and collide, end condition is in here
        self.parent_node.move_and_collide()  

        # display cycle options
        self.parent_node.cycle_through_options()

        # draw surface
        self.parent_node.submit_to_render()

        # if timer is complete emit cycling
        if self.timer_complete:

            self.emit('DISPLAY')


    def collision_check(self,axis:str='y'):

        pass

    # handle collision once the check is confirmed
    def handle_collision(self,game_object:object,axis:str):

       pass