import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager


class Roaming(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

        # set sprite sheet to be idle animation

        # remove movement if it is in movement vectors
        # self.parent_nodemovement_vectors = {}

        # set acceleration to base
        # self.parent_node.acceleration = self.parent_node.original_vars['acceleration']
        self.parent_node.movement_vectors['movement']['Xcceleration_rate'] = self.parent_node.slide_friction

        # change acceleration_timer

        pass

    def update(self):

        # submit event processing
        self.submit_event_processing()

        self.pathing_end_position_target = objectManager.player.hurtbox.center


        # determine the pathing the entity is going to be using
        # self.determine_pathing_type()

        # update pathing and cache
        self.parent_node.update_pathing_and_cache()
        # self.parent_node.draw_pathing()

        # # movement
        self.parent_node.move_and_collide()

        # draw surface
        self.parent_node.submit_to_render()
        # self.parent_node.draw_surface(position=self.parent_node.hurtbox.center)
        # self.parent_node.draw_rect(position=self.parent_node.hurtbox.center)

        self.end_condition()
    

    def end_condition(self):
        
        # if something happens send signal to transition to other state here by setting done to True and setting next state
        # if 'movement' in self.parent_node.movement_vectors:
        #     self.parent_node.emit('WALKING')

        if sum(self.parent_node.movementx) != 0 or sum(self.parent_node.movementy) != 0:

            self.emit('WALKING')

