import json,sys
from .utils import *
from .moveableobject import Moveable_Object
from .objectsystem import objectManager


class Wall(Moveable_Object):

    # keep start and end point arguments in case i want to give the bullet some quirky pathing when shot
    def __init__(self):

        # Moveable_Object.__init__(self)
        
        super().__init__()
    
        
    def init(self):

        super().init()

    
    # handle collision damage etc
    # def handle_collision(self,game_object:object):

    #     # set damage variable by checking if there was a crit
    #     damage = 0
    #     crit = proc(self.critical_chance)

    #     if crit:
    #         damage = self.damage*self.critical_multiplier

    #     elif not crit:
    #         damage = self.damage

    #     # FOR PLAYER BULLETS
    #     if game_object.object_of_origin == 'Player':

    #         if game_object.movement[0] < 0:
    #             game_object.rect.left = self.hurtbox.right

    #         if game_object.movement[0] > 0:
    #             game_object.rect.right = self.hurtbox.left

    #        # dpeendong on which direction they are moving in on the y axis set the player to be at the top or bottom of that rect
    #         if game_object.movement[1] < 0:
    #             game_object.rect.top = self.hurtbox.bottom

    #         if game_object.movement[1] > 0:
    #             game_object.rect.bottom = self.hurtbox.top


    # def check for a collision
    # def collision_check(self):

    #     # find surrounding objects
    #     self.find_surrounding_game_objects()        

    #     # go through all possible game objects
    #     for game_object in self.surrounding_game_objects:

    #         # rect collision check
    #         if self.hitbox.colliderect(game_object.hitbox):

    #             # sprite collision check
    #             if self.mask.overlap(game_object.mask,(game_object.hitbox.left-self.hitbox.left,game_object.hitbox.top-self.hitbox.top)):

    #                 # handle collision
    #                 self.handle_collision(game_object=game_object)

    # combines movement and collision function
    def update(self):

        # only show the orbital and draw it if it is active
        if self.is_active:

            # print(self.hurtbox.topleft)

            # track current tile
            self.update_position()

            # find game objects
            # self.find_game_objects_in_area()

            # handle collisions with the wall and entities
            # self.enemy_collision_rects()

            # # movement
            # self.move2()

            # collision check
            # self.collision_check()

            # run on collisioin effects
            # self.run_on_collision_effects()

            # apply status effects
            # self.apply_status_effects()

            # draw surface
            self.submit_to_render()
            
            # self.draw_surface(position=self.spawnLocation)
            # self.draw_rect(position=self.spawnLocation)

            



