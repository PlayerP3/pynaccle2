import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager

class Idle(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

        # set sprite sheet to be idle animation

        # remove movement if it is in movement vectors
        # self.parent_nodemovement_vectors = {}

        # set acceleration to base
        # self.parent_node.acceleration = self.parent_node.original_vars['acceleration']
        # self.parent_node.movement_vectors['movement']['Xcceleration_rate'] = self.parent_node.slide_friction

        # change acceleration_timer

        pass

    def update(self):

        # submit event processing
        self.submit_event_processing()

        self.parent_node.pathing_end_position_target = objectManager.player.hurtbox.center

        # # movement
        self.parent_node.move_and_collide()

        if self.parent_node.health <= 0:
            self.emit('DEATH')

        elif self.parent_node.pathing_end_position_target:

            self.emit('CHASING')

        # draw surface
        self.parent_node.submit_to_render()
        # self.parent_node.draw_surface(position=self.parent_node.hurtbox.center)
        # self.parent_node.draw_rect(position=self.parent_node.hurtbox.center)

        # update position
        self.parent_node.update_position()


