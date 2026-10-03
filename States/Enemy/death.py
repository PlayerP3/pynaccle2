import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager


class Death(State):

    def __init__(self):

        
        State.__init__(self)
        self.timer_limit = 0

    def enter(self):

        # set sprite sheet to be death animation
        
        # start death countdown
       
        self.timer_init()

        # remove self from game positions
        if self.parent_node.current_tile_position in objectManager.object_positions:

            if self.parent_node in objectManager.object_positions[self.parent_node.current_tile_position]:
                objectManager.object_positions[self.parent_node.current_tile_position].remove(self.parent_node) 


    def update(self):

        self.run_timer()

        # draw surface
        self.parent_node.submit_to_render()
        # self.parent_node.draw_surface(position=self.parent_node.hurtbox.center)
        # self.parent_node.draw_rect(position=self.parent_node.hurtbox.center)

        if self.timer_complete:
            self.emit('IDLE')


    def completed(self):

        # if something then set new state
        self.next_state = None

        # set done to false
        self.done = False

        self.parent_node.is_active = False

        # remove self from game positions
        if self.parent_node.current_tile_position in objectManager.object_positions:

            if self.parent_node in objectManager.object_positions[self.parent_node.current_tile_position]:
                objectManager.object_positions[self.parent_node.current_tile_position].remove(self.parent_node) 
