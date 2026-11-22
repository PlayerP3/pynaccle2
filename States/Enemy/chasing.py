import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager
from pynaccle.tilemap import tilemapProcessor
from pynaccle.utils import *

class Chasing(State):

    def __init__(self):

        State.__init__(self)

    def update(self):

        # submit event processing
        self.submit_event_processing()
        
        # set pathing end pos
        self.parent_node.set_pathing_end_pos()

        # update pathing and cache
        # self.parent_node.update_pathing_and_cache()
        self.parent_node.update_pathing_and_cache(start=self.parent_node.hurtbox.center,end=self.parent_node.pathing_end_pos)

        # # movement
        self.parent_node.move_and_collide()

        # draw surface
        self.parent_node.submit_to_render()

        self.parent_node.update_position()
        
        # end condition
        self.end_condition()

    def end_condition(self):
        
        if self.parent_node.health <= 0:
            self.emit('DEATH')
            
        # if a distraction object is thrown thrown then change to distract state
        elif self.parent_node.priorityGameObjectType in ['Distraction']:
            
            if self.parent_node.targetGameObject.currentState == 'DISTRACTING':
                self.emit('DISTRACTED')
            
        # # check if we have a target game obejct
        elif self.parent_node.targetGameObject:
            
            # check if we are in range of the target game object
            if find_dist_between_points(self.parent_node.targetGameObject.hurtbox.center,self.parent_node.hurtbox.center) <= self.parent_node.distanceToTriggerAttackState:
                
                # if some other thing maybe attack
                self.emit('ATTACKING')
    
        # no pathing means that it has reached the end point
        elif not self.parent_node.pathing:
            
            if not self.parent_node.targetGameObject:
                self.emit('IDLE')
                
