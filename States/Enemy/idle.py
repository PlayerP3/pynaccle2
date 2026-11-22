import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager
from pynaccle.utils import *

class Idle(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

        # set sprite sheet to be idle animation

        # remove movement if it is in movement vectors
        # self.parent_nodemovement_vectors = {}

        # set acceleration to base
        # self.parent_node.acceleration = self.parent_node.original_vars['acceleration']
        # self.parent_node.movement_vectors['movement']['acceleration_rate'] = self.parent_node.slide_friction

        # change acceleration_timer

        pass

    def update(self):

        # submit event processing
        self.submit_event_processing()
    
        self.parent_node.set_pathing_end_pos()    
        
        # movement
        self.parent_node.move_and_collide()
        
        # draw surface
        self.parent_node.submit_to_render()
        
        # update position
        self.parent_node.update_position()
        
        # the state end condition        
        self.end_condition()


    def end_condition(self):
        
        if self.parent_node.health <= 0:
            self.emit('DEATH')
                    
        # if pathing position exists
        elif self.parent_node.pathing_end_pos:
            
            # check if we have a target game obejct
            if self.parent_node.targetGameObject:
                
                # check if we are in range of the target game object
                if find_dist_between_points(self.parent_node.targetGameObject.hurtbox.center,self.parent_node.hurtbox.center) <= self.parent_node.distanceToTriggerAttackState:
                    
                    # if some other thing maybe attack
                    self.emit('ATTACKING')
                    
            # if we attack not trigerred then go back to chasing if we have an end point
            self.emit('CHASING')
    
        
        return super().end_condition()