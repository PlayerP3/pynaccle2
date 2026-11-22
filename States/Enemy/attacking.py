import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager

class Attacking(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

        # set sprite sheet to be idle animation

        # determine what is actually going to be attacked
        
        # remove pathing
        self.parent_node.pathing = []
        
        if 'pathing' in self.parent_node.movement_vectors:
            del self.parent_node.movement_vectors['pathing']

    def update(self):

        # submit event processing
        self.submit_event_processing()

        # # movement
        self.parent_node.move_and_collide()
        
        # draw surface
        self.parent_node.submit_to_render()
        
        # update position
        self.parent_node.update_position()
        
        self.emit('CHASING')
        
        



