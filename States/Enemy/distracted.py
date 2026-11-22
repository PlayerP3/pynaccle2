import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager
from pynaccle.tilemap import tilemapProcessor
from pynaccle.utils import *

class Distracted(State):

    def __init__(self):

        State.__init__(self)
        
        self.distractObj = None
        
    def enter(self):
        
        # find a random point around the distraction
        endPos = find_point_on_circle_radius(10,self.parent_node.targetGameObject.hurtbox.center)
        
        # set game object which is the distracted object
        self.parent_node.set_pathing_end_pos(endPos)
        
        # set distrcat obj
        self.distractObj = self.parent_node.targetGameObject


    def update(self):

        # submit event processing
        self.submit_event_processing()
        
        # update pathing and cache
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
            
        elif not self.distractObj.is_active:
            self.emit('CHASING')
            
    def completed(self):
        self.distractObj = None
        return super().completed()
