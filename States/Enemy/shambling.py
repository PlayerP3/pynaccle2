import pygame,os,re,math,random,string,sys
import json
from pygame.math import Vector2
from pynaccle.statemachine import State
from pynaccle.objectsystem import objectManager
from pynaccle.tilemap import tilemapProcessor

class Shambling(State):

    def __init__(self):

        State.__init__(self)

    def enter(self):

        pass


    def update(self):

        # submit event processing
        self.submit_event_processing()

        self.parent_node.pathing_end_position_target = objectManager.player.hurtbox.center

        # update pathing and cache
        self.parent_node.update_pathing_and_cache()
        # self.parent_node.draw_pathing()

        # # movement
        self.parent_node.move_and_collide()

        # draw surface
        self.parent_node.submit_to_render()
        # self.parent_node.draw_surface(position=self.parent_node.hurtbox.center)
        # self.parent_node.draw_rect(position=self.parent_node.hurtbox.center)

        self.parent_node.update_position()

        if self.parent_node.health <= 0:
            self.emit('DEATH')

        elif objectManager.player.current_tile_position not in tilemapProcessor.accessible_tiles:
            self.emit('IDLE')