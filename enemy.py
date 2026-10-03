import pygame,json
from pygame.math import Vector2
from pynaccle.pathfinding import Pathfinding
from pynaccle.moveableobject import Moveable_Object
from pynaccle.utils import *
from pynaccle.statemachine import StateMachine
from pynaccle.objectsystem import objectManager
from .States.Enemy.idle import Idle
from .States.Enemy.chasing import Chasing
from .States.Enemy.roaming import Roaming
from .States.Enemy.death import Death

# from ItemBench import ItemPools,ItemPoolsReset,remove_from_itempool,add_to_itempool
pygame.font.init()

class Enemy(Moveable_Object,Pathfinding,StateMachine):

    def __init__(self):

        Moveable_Object.__init__(self)
        Pathfinding.__init__(self)
        StateMachine.__init__(self)

        # movement
        self.movementx = [0,0] # index 0 is no movememnt, -1 left, 1 right
        self.movementy = [0,0] # index 0 is no movement, -1 up, 1 down

        # self.starter_deck = {}
        # self.deck = Deck()

        # target position for shooting
        self.shooting_target_position = (0,0)

    # reinit
    def init(self):

        # init state machine
        self.states = {'IDLE':Idle(),
                       'CHASING':Chasing(),
                       'DEATH':Death()}
        
        # set parent node for player states
        for x in self.states:
            self.states[x].parent_node = self
        
        self.state = self.states['IDLE']

        super().init()


    def update(self):
    
        self.state.update()

        if self.state.done:
            self.transition_to_next_state()
    
    

    # handle collision once the check is confirmed
    def handle_collision(self,game_object:Moveable_Object,axis:str):

        # if inactive dont bother running code        
        if not self.is_active:
            return

        if game_object.object_of_origin == 'Game':

            if game_object.__class__.__name__ == 'Wall':

                if axis == 'x':
                    if self.movement[0] < 0:
                        self.hurtbox.left = game_object.hurtbox.right

                    elif self.movement[0] > 0:
                        self.hurtbox.right = game_object.hurtbox.left

                elif axis == 'y':
                    if self.movement[1] < 0:
                        self.hurtbox.top = game_object.hurtbox.bottom

                    if self.movement[1] > 0:
                        self.hurtbox.bottom = game_object.hurtbox.top

        if game_object.object_of_origin == 'Enemy':

            if game_object.__class__.__name__ == 'Enemy':

                collision_vectorX,collision_vectorY = Vector2(self.hurtbox.center) - Vector2(game_object.hurtbox.center)

                # collision_vectorX,collision_vectorY = (collision_vector/self.collision_vector_reduction)

                # apply a knockback
                self.update_movement_vectors(unique_id='overlapping_spread_knockback',direction_vectorX=collision_vectorX,direction_vectorY=collision_vectorY,
                                    acceleration=((game_object.overlap_resolution_strength/self.overlap_resolution_resistance)),Xcceleration_rate=self.decceleration_rate,Xcceleration_rate_change='negative',max_value=0,
                                    reduce_on_wall_collision=True,reset_on_max_value=True)


    def run_behaviour(self):
        
        # only show the orbital and draw it if it is active
        if self.is_active:

            # update position
            self.update_position()

            # find game objects
            # self.find_game_objects_in_area()

            # handle collisions with the wall and entities
            # self.enemy_collision_rects()
            # self.pathing_end_position_target = (48,-48)
            self.pathing_end_position_target = objectManager.player.hurtbox.center


            # determine the pathing the entity is going to be using
            # self.determine_pathing_type()

            # update pathing and cache
            self.update_pathing_and_cache()
            self.draw_pathing()

            # # movement
            self.move_and_collide()

            # draw surface
            self.draw_surface(position=self.hurtbox.center)
            self.draw_rect(position=self.hurtbox.center)
