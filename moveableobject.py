import pygame,os,re,sys
from pygame.math import Vector2
from .raycast import Raycast
from .animatedsprite import AnimatedSprite
from .globs import delta
from .objectsystem import objectManager
from .configs import configData
from .utils import *
from .hitbox import *
import random
import math
import json
import string
import copy
import numpy as np

# from A_star_search_algorithm import *

# pygame.font.init()
class Moveable_Object(AnimatedSprite):

    def __init__(self,
                 
                 health:float=1,acceleration:float=1,decceleration_rate:float=0,money:int=0,moneyOnHit:int=10,moneyOnKill:int=50,

                 knockback_resistance:float=5,knockback_strength:float=1,overlap_resolution_resistance=5,overlap_resolution_strength:float=1,

                 speed:float=1,damage:float=1,damage_multiplier:float=1,critical_chance:float=1,
                 critical_multiplier:float=1,health_state:dict={},allowed_collisions:list=['Bullet'],
                 can_collide:bool=True,movement_type:str='normal',stamina:int=3,

                 sine_amplitude:float=10,sine_frequency:float=10,

                 general_explosion_immunity:bool=None,self_explosion_immunity:bool=None,collision_type='rect',canRicochetOffWalls:bool=False,

                 x_metres_before_collision_detection:float=530,x_metres_before_homing_detection:float=1,collisionDetectionDistance:float=100,

                 is_immune_to:list=[],status_effect_immunity_tracker:dict={},can_gain_natural_immunity:bool=False,on_collision_effects:dict={},

                 is_target_for_homing:bool=False,damage_resistance:float=1,is_invincible:bool=False,on_shot_effects:dict={},
                 on_damage_taken_effects:dict={},status_effects:dict={},

                 stop_at_target_point_to_stop_at:bool=False,can_ricochet:bool=False,score:int=0,score_on_hit:int=0,score_on_kill:int=0,

                 max_acceleration:float=1,min_acceleration:float=0,invincibility_duration:float=0,

                 score_multiplier:int=1,action_every_X_frames:float=1,connectedChunk:str="0",

                 ranged_dot_effects:dict={},inaccessible:bool=True):

        
        # store quests
        self.quests = []

        # store tasks
        self.tasks = []
        
        
        # store base stats in a dict
        self.base_stats = {'x_metres_before_collision_detection':x_metres_before_collision_detection,
                           'x_metres_before_homing_detection':x_metres_before_homing_detection,
                           'invincibility_duration':invincibility_duration,
                           'acceleration':acceleration,
                           'knockback_strength':knockback_strength,
                           'knockback_resistance':knockback_resistance,
                           'health':health,
                           'damage':damage,
                           'damage_resistance':damage_resistance,
                           'speed':speed,
                           'score_multiplier':score_multiplier}


        # get target vars
        self.start_position = (0,0)
        self.target_position = (0,0)
        self.dist_to_target = None
        self.movement_type = movement_type

        # distance another game object has to be before we start considering collision detection
        self.x_metres_before_collision_detection = x_metres_before_collision_detection
        self.x_metres_before_homing_detection = x_metres_before_homing_detection

        # invincibility variable
        self.is_invincible = is_invincible
        self.invincibility_duration = invincibility_duration
        self.invincibility_timer = invincibility_duration

        # interacting vat
        self.is_interacting = False

        # ricochet variable
        self.can_ricochet = can_ricochet

        # stop moving when target point is reached
        self.stop_at_target_point_to_stop_at = stop_at_target_point_to_stop_at

        # set acceleration reduction
        self.acceleration = acceleration
        self.acceleration_reset = acceleration
        self.max_acceleration = max_acceleration
        self.min_acceleration = min_acceleration
        self.decceleration_rate = decceleration_rate
        self.stamina = stamina      

        # variable to determine whether things can bounce off walls
        self.canRicochetOffWalls = canRicochetOffWalls        

        # set knockback variable, if knocked back then accelration becomes this value
        self.knockback_strength = knockback_strength # this is what actually affects overlap, higher strength reduces overlap, lower strength increases overlap of colliding objects, assuming resistance is constant
        self.knockback_resistance = knockback_resistance # this can also affect overlap, if there is a higher resistance then increases the the overlap of collidiong object, when lower resistance then lower overlap between colliding objects, assuming knockback strength is constant, think of it as lower resistance to knockback

        # set overlap resolution variables
        self.overlap_resolution_resistance = overlap_resolution_resistance
        self.overlap_resolution_strength = overlap_resolution_strength

        # set health
        self.health = health
        
        # total health
        self.total_health = 1

        self.health_reset = health
        self.health_state = health_state # {100:1,40:2,0:3} # key is percentage of health remaining, value is the state which that leaves you in

        # set dmg
        self.damage = damage
        self.damage_multiplier = damage_multiplier
        self.damage_resistance = damage_resistance
        self.action_every_X_frames = action_every_X_frames/configData.loadedConfigs['params']['gameFPS']  # change this because we are not using FPS as globs
        self.critical_chance = critical_chance
        self.critical_multiplier = critical_multiplier

        # raycast vars
        self.movement_raycast = Raycast()
        self.movement_raycast_init = {}

        # set speed, this variable will never change,and it is the acceleration we will rather be changing
        self.speed = speed
        self.speed_reset = speed

        # direction vectors
        self.direction_vectorX = 0
        self.direction_vectorY = 0
        self.collision_vector = Vector2(0,0)
        self.movement = Vector2(0,0)

        # sine wave movement
        self.sine_amplitude = sine_amplitude
        self.sine_frequency = sine_frequency


        # money
        self.money = money
        self.moneyOnHit = moneyOnHit
        self.moneyOnKill = moneyOnKill

        # immunity/invulnerability
        self.general_explosion_immunity = general_explosion_immunity
        self.self_explosion_immunity = self_explosion_immunity


        # allowed collisions
        self.allowed_collisions = allowed_collisions
        self.can_collide = can_collide
        self.collision_type = collision_type
        self.inaccessible = inaccessible
        self.collisionDetectionDistance = collisionDetectionDistance

        # interactions
        # is interacting
        self.is_interacting = False
                
        # movement vectoirs stored here
        self.movement_vectors = {} # array of dictionary with keys direction vector X, direction vector Y, and acceleration

        # positional variables
        self.current_tile_position = (0,0)
        self.connectedChunk = connectedChunk

        # score variables
        self.score = score
        self.score_on_hit = score_on_hit
        self.score_on_kill = score_on_kill
        self.score_multiplier = score_multiplier


        # the times in the immunity tracker is dependent on a dict which gives us the time until loss or gain
        # self.status_effect_immunity_tracker = {'Bleed':{"TimerUntilImmunityGain":0,
        #                                                 "TimerUntilImmunityLoss":0,
        #                                                 "TimeUntilImmunityGain":1,
        #                                                 "TimeUntilImmunityLoss":10}}

        self.status_effect_immunity_tracker = status_effect_immunity_tracker

        self.can_gain_natural_immunity = can_gain_natural_immunity


        self.status_effect_immunity_tmrs = {}

        # collision variables
        self.game_objects_collided_with = {}
        self.is_target_for_homing = is_target_for_homing
        self.surroundingGameObjects  = []
        self._surroundingTiles = []
        self._surroundingGameObjects = []


        # effect variables
        self.status_effects = status_effects
        self.status_effects_applied_to_self = []

        self.is_immune_to = is_immune_to

        # on shot effect variables, things that only happen once the gun wielder shoots

        self.on_shot_effects = on_shot_effects
        self.on_damage_taken_effects = on_damage_taken_effects
        self.on_collision_effects = on_collision_effects

        self.ranged_dot_effects = ranged_dot_effects

        self.active_on_collision_effects = []

        self.possible_enemy_collisions = []
        self.overlap_resolution_collisions = []

        # init animated sprite
        AnimatedSprite.__init__(self)
        # super().__init__()

   
    # reinit
    def init(self):
           
        self.hurtbox.width = self.hurtbox_width
        self.hurtbox.height = self.hurtbox_height

        self.movement_raycast.init(attributes=self.movement_raycast_init)

        # set total health
        self.total_health = self.health

        # load hitboxes
        self.load_hitboxes()


        super().init_sprite()
        
    def spread_overlapping_game_objects2(self):

        collision_vector = Vector2(0,0)

        # print(f'My id is {id(self)}\nAll collisions:\n{self.surroundingGameObjects}\nDone')

        if self.surroundingGameObjects:
            for gObj in self.surroundingGameObjects:
                if self.hurtbox.colliderect(gObj.hurtbox):
                    collision_vector = Vector2(self.hurtbox.center) - Vector2(gObj.hurtbox.center)

                    self.collision_vector += (collision_vector/self.collision_vector_reduction)
                    self.direction_vectorX += self.collision_vector[0]
                    self.direction_vectorY += self.collision_vector[1]

                    # self.apply_knockback(gameObj=gObj,unique_id='overlapping_spread_knockback',direction_vectorX=self.direction_vectorX,direction_vectorY=self.direction_vectorY,
                    #                     acceleration=((gObj.knockback_strength/self.knockback_resistance)),acceleration_rate=self.decceleration_rate,acceleration_rate_change='negative',max_value=0,
                    #                     invert_direction_vectors_on_collision=True,delete_on_max_value=True)
                    # gObj.collision_vector -= (collision_vector/self.collision_vector_reduction)
                    # gObj.direction_vectorX -= self.collision_vector[0]
                    # gObj.direction_vectorY -= self.collision_vector[1]
                    break

    def spread_overlapping_game_objects(self):

        collision_vector = Vector2(0,0)

        if self.overlap_resolution_collisions:

            collisions = self.hurtbox.collideobjectsall(self.overlap_resolution_collisions, key=lambda gObj: gObj.hurtbox)

            collisions = [c for c in collisions if id(self)!=id(c)]

            if collisions:

                gameObj = collisions[0]
                collision_vector = Vector2(self.hurtbox.center) - Vector2(gameObj.hurtbox.center)

                self.collision_vector = collision_vector

                self.direction_vectorX += self.collision_vector[0]
                self.direction_vectorY += self.collision_vector[1]
                # sys.exit()
                # make the acceleration of the other object 1 so it actually moves
                # acceleration is usually triggered by the apply_knockback function
                # otherwise it is usually always 0
                # self.apply_knockback(gameObj_collided_with=gameObj,unique_id='overlapping_spread_knockback',direction_vectorX=self.direction_vectorX,direction_vectorY=self.direction_vectorY,
                #                             acceleration=((gameObj.knockback_strength/self.knockback_resistance)),acceleration_rate=self.decceleration_rate,acceleration_rate_change='negative',max_value=0,
                #                             invert_direction_vectors_on_collision=True,delete_on_max_value=True)


    def load_hitboxes(self):

        if self.img_path in hitboxSystem.metaData:

            # get new dict of frame and hitboxes
            boxes = {k:v for k,v in hitboxSystem.metaData[self.img_path].items()}
            out = {}

            # loop through each frame and the hitboxes it comes with
            for frame,storedHitboxes in boxes.items():

                # add new frame
                self.hitboxes[int(frame)] = []

                # add each hitbox to the boxes
                for indvBox in storedHitboxes:

                    splitvars = [float(x) for x in indvBox.split(',')]

                    newBox = Hitbox(*splitvars,frameNumber=int(frame))

                    self.hitboxes[int(frame)].append(newBox)

    # check for hitbox collision and return if collisioon true and the htibox that hit
    def hitbox_collision(self,game_object):

        collision = False
        hitbox = None

        # check for collision with hitboxes
        for hitBox in self.hitboxes[self.currentFrame]:
            
            if hitBox.collided(self.hurtbox.center,game_object):
                collision = True
                break

        return collision,hitbox
        
    # kill object
    def kill(self,active_pool:list,inactive_pool:list):

        active_pool.remove(self)
        inactive_pool.append(self)

    # self explanitory
    def update_position(self):

        old_tile_position = self.current_tile_position
        new_tile_position = self.find_tile_topleft(pos = self.hurtbox.center)

        # normal update if nothing has moved
        if old_tile_position == new_tile_position:
            
            if old_tile_position not in objectManager.object_positions:

                # add the coors and add the object
                objectManager.object_positions[old_tile_position] = [self]

            # if the coors are already present we just want to add to the list that is already there
            elif old_tile_position in objectManager.object_positions:

                if self not in objectManager.object_positions[old_tile_position]:
                    objectManager.object_positions[old_tile_position].append(self) 
    
        # if the position has changed   
        elif old_tile_position != new_tile_position:

            # remove instance of object in old tile position list
            if old_tile_position in objectManager.object_positions:

                if self in objectManager.object_positions[old_tile_position]:

                    objectManager.object_positions[old_tile_position].remove(self)

                if not objectManager.object_positions[old_tile_position]:
                    del objectManager.object_positions[old_tile_position]


            # add new position and set current tile pos
            # uses the weird division thing to determine the integer of the square the player is on, then multiply that by tile size to get what tile ti actually is
            self.current_tile_position = new_tile_position

            # update the object position
            # check if the coors are in the object position dict already
            if self.current_tile_position not in objectManager.object_positions:

                # add the coors and add the object
                objectManager.object_positions[self.current_tile_position] = [self]

            # if the coors are already present we just want to add to the list that is already there
            elif self.current_tile_position in objectManager.object_positions:

                if self not in objectManager.object_positions[self.current_tile_position]:
                    objectManager.object_positions[self.current_tile_position].append(self) 

    # move/teleport function
    def move_to(self,pos:tuple,vertice:str="center"):

        if vertice == "center":
            self.hurtbox.center = (pos[0]+self.spawnOffsetX,pos[1]-self.spawnOffsetY)
        
        elif vertice == "topleft":
            
            posAdjustemntX = 0
            posAdjustemntY = 0
            
            # if hurtbox size is bigger (or smaller) than the tile size of the game then we want to adjust the position so the sprite and everything still sits in the center
            
            # x adjust
            if self.hurtbox.size[0] > configData.loadedConfigs['params']['tileSize']:
                
                posAdjustemntX = self.hurtbox.size[0]/2 - configData.loadedConfigs['params']['tileSize']/2
                
            elif self.hurtbox.size[0] < configData.loadedConfigs['params']['tileSize']:
                            
                posAdjustemntX = (self.hurtbox.size[0]/2 - configData.loadedConfigs['params']['tileSize']/2) * -1
                
            # y adjust
            if self.hurtbox.size[1] > configData.loadedConfigs['params']['tileSize']:
                
                posAdjustemntY = self.hurtbox.size[1]/2 - configData.loadedConfigs['params']['tileSize']/2
                
            if self.hurtbox.size[1] < configData.loadedConfigs['params']['tileSize']:
                            
                posAdjustemntY = (self.hurtbox.size[1]/2 - configData.loadedConfigs['params']['tileSize']/2) * -1
            
            self.hurtbox.topleft = (pos[0]+self.spawnOffsetX-posAdjustemntX,pos[1]+self.spawnOffsetY-posAdjustemntY)
            
    # spawn function
    def spawn(self,pos:tuple,vertice:str="center"):

        self.is_active = True
        
        self.move_to(pos=pos,vertice=vertice)
        
    # get surrouinding tiles
    @property
    def surroundingTiles(self):
        # self._surroundingTiles = find_surrounding_tiles(pos=self.current_tile_position,tile_width=configData.loadedConfigs['params']['tileSize'],tile_height=configData.loadedConfigs['params']['tileSize'])
        
        # check if tile coors are within collision detection distance of obj
        tiles = []
        
        for coors in objectManager.object_positions:
        
            if find_dist_between_points(self.hurtbox.center,coors) <= self.collisionDetectionDistance:
                tiles.append(coors)
        
        self._surroundingTiles = tiles
        
        return self._surroundingTiles
    
    @surroundingTiles.setter
    def surroundingTiles(self,v):
        self._surroundingTiles = v
        
    # get surrounding game objects, i.e all the game objects on the surrounding tiles, so now we dont need to loop through a lot of stuff to find surrounding gameobjs
    @property
    def surroundingGameObjects(self):
    
        # reset surrounding objects
        gameObjs= []

        for coors in self.surroundingTiles:

            # possible entities that can collide with the bullet
            gameObjs.extend(objectManager.object_positions[coors])

        # filter out game objects based on if they are a target for the projectile, add if class name not wall
        self._surroundingGameObjects = list(set([x for x in gameObjs if x.is_active and id(x) != id(self) ]))
        
        return self._surroundingGameObjects
    
    @surroundingGameObjects.setter
    def surroundingGameObjects(self,v):
        self._surroundingGameObjects = v
        
    def get_filtered_surrounding_objects(self,classes:list,deep:bool=False):
     
        return [x for x in self.surroundingGameObjects if x.__class__.__name__ in classes]
    
    # find closest interactable to the moveable object
    def find_closest_interactable(self):
        pass
            
    # wall collision check
    def collision_check(self,axis:str='y'):

        if self.__class__.__name__ == "Wall":
            return
   
        # go through all possible game objects
        for game_object in self.surroundingGameObjects:

            if not game_object.can_collide:
                continue

            # if wall/door use hirtbox collision instead of hitbox
            if array_is_in_array(get_mro(gameObject=game_object),['Wall','Interactable']): 

                # rect collision check
                if self.hurtbox.colliderect(game_object.hurtbox):

                    # handle collision
                    self.handle_collision(game_object=game_object,axis=axis)


            else:
                collision = False
                
                # check for collision with hitboxes
                for hitBox in self.hitboxes[self.currentFrame]:
                    
                    if hitBox.collided(self.hurtbox.center,game_object):
                        collision = True
                        break

                if collision:

                    self.handle_collision(game_object=game_object,axis=axis)
                    
        # identify closest interactable to object
        self.find_closest_interactable()

                    


    # extra collision processing 
                

    # handle collision once the check is confirmed
    def handle_collision(self,game_object:object,axis:str):

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

                # self.is_active = False
        
    # update movement vectors array, use whenever setting both the direction vectors and acceleration
    # concept of unique id is that a single object can only apply a single vector to the moveable object
    def add_movement_vector(self,unique_id:int,direction_vectorX:float,direction_vectorY:float,acceleration:float=1,
                                acceleration_rate:float=1,acceleration_rate_change:str='positive',max_value:float=1,invert_direction_vectors_on_collision:bool=False,
                                inversion_collisionX:bool=False,inversion_collisionY:bool=False,delete_on_max_value:bool=False,target_point_to_stop_at:tuple = None) -> None:

        self.movement_vectors.update({unique_id:{"direction_vectorX":direction_vectorX,
                                        "direction_vectorY":direction_vectorY,
                                        "acceleration":acceleration,
                                        "acceleration_rate":acceleration_rate,
                                        "acceleration_rate_change":acceleration_rate_change,
                                        "max_value":max_value,"invert_direction_vectors_on_collision":invert_direction_vectors_on_collision,
                                        "delete_on_max_value":delete_on_max_value,
                                        "target_point_to_stop_at":target_point_to_stop_at,
                                        "inversion_collisionX":inversion_collisionX,
                                        "inversion_collisionY":inversion_collisionY}})

    # function for both movement and collisions
    def move_and_collide(self):
        
        # store position before movement
        position_before_movement = self.hurtbox.center
        target_point_to_stop_at = None

        # set final movement var
        self.movement = Vector2(0,0)

        # collision with objects
        # self.spread_overlapping_game_objects()

        # var of movements to delete

        # vectors to delete
        vectors_to_delete = []

        # if x direction vector is positive or negative return acceleration for that vector
        positiveXaccel = []
        negativeXaccel = []

        # for Y
        positiveYaccel = []
        negativeYaccel = []

        # all vectors that will be inverted upon collision with some obj
        movement_vectors_to_invert = []

        # loop through dictionary of vectors
        for unique_id,movement_info in self.movement_vectors.items():

            # set movement vars
            movementx = Vector2(0,0)
            movementy = Vector2(0,0)

            # unpack all variables
            direction_vectorX = movement_info["direction_vectorX"]
            direction_vectorY = movement_info["direction_vectorY"]
            acceleration = movement_info["acceleration"]
            acceleration_rate = movement_info["acceleration_rate"]
            acceleration_rate_change = movement_info["acceleration_rate_change"]
            max_value = movement_info["max_value"]
            delete_on_max_value = movement_info["delete_on_max_value"]
            invert_direction_vectors_on_collision = movement_info["invert_direction_vectors_on_collision"]
            inversionCollisionX = movement_info["inversion_collisionX"]
            inversionCollisionY = movement_info["inversion_collisionY"]
            target_point_to_stop_at = movement_info["target_point_to_stop_at"]

            # wall collision acceleration code
            # if invert_direction_vectors_on_collision:
            #     movement_vectors_to_invert.append(unique_id)
                
            if inversionCollisionX or inversionCollisionY:
                movement_vectors_to_invert.append(unique_id)
            # Actual movement function

             # if only xvel or yvel is changed then set the other axis movement to be 0 because we want to move left, then check for a collision, and then move right and do the same
            if direction_vectorX !=0:
                movementx = (Vector2(direction_vectorX,0).normalize()*configData.loadedConfigs['params']['gameDelta']*self.speed*acceleration)

            if direction_vectorY !=0:
                movementy = (Vector2(0,direction_vectorY).normalize()*configData.loadedConfigs['params']['gameDelta']*self.speed*acceleration)

            # if both x and y are pressed, normalise the x and y values the player is going to move in.
            # when both x and y are pressed, the normalised value is different from if only one of those was pressed
            if direction_vectorX != 0 and direction_vectorY != 0:

                move = Vector2(direction_vectorX,direction_vectorY).normalize()*configData.loadedConfigs['params']['gameDelta']*self.speed*acceleration

                # separate into only x movement and only y movement
                movementx = (move[0],0)
                movementy = (0,move[1])

            # adjust acceleration
            if acceleration_rate_change == 'positive':

                acceleration += (configData.loadedConfigs['params']['gameDelta']*acceleration_rate)

                # update dictionary
                movement_info["acceleration"] = acceleration

                if acceleration >= max_value:

                    # set to delete
                    if delete_on_max_value:
                        vectors_to_delete.append(unique_id)

                        if unique_id in movement_vectors_to_invert:
                            movement_vectors_to_invert.remove(unique_id)

                    elif not delete_on_max_value:
                        movement_info["acceleration"] = max_value


            elif acceleration_rate_change == 'negative':

                acceleration -= (configData.loadedConfigs['params']['gameDelta']*acceleration_rate)

                # update dictionary
                movement_info["acceleration"] = acceleration

                if acceleration <= max_value:

                    # set to delete
                    if delete_on_max_value:
                        vectors_to_delete.append(unique_id)

                        if unique_id in movement_vectors_to_invert:
                            movement_vectors_to_invert.remove(unique_id)

                    elif not delete_on_max_value:
                        movement_info["acceleration"] = max_value

            # add to final movement
            self.movement += movementx
            self.movement += movementy


            ### handling wall collision acceleration changes
            if not invert_direction_vectors_on_collision:

                # adding accelerations to appropriate lists
                if direction_vectorX > 0:
                    positiveXaccel.append(acceleration)

                if direction_vectorX < 0:
                    negativeXaccel.append(acceleration)

                if direction_vectorY > 0:
                    positiveYaccel.append(acceleration)

                if direction_vectorY < 0:
                    negativeYaccel.append(acceleration)

        ######################################


        #########
        # delete vectors that are complete
        if vectors_to_delete:
            for vector in vectors_to_delete:
                del self.movement_vectors[vector]
        
        #########

        # moving the objectz        
        self.hurtbox.centerx += self.movement[0]
        self.collision_check(axis='x')
        
        self.hurtbox.centery += self.movement[1]
        self.collision_check(axis='y')

        # stop reducing acceleration multiple times
        acceleration_reduced = False

        # go through all vectors
        for vec in movement_vectors_to_invert:

            if inversionCollisionX:
                self.movement_vectors[vec]["direction_vectorX"] *= -1

                # if negative
                if self.movement_vectors[vec]["direction_vectorX"] < 0:

                    # subtract accelerations belonging to all negative vectors
                    self.movement_vectors[vec]["acceleration"] -= sum(negativeXaccel)/5

                    # # stop acceleration going beyond its max value
                    if self.movement_vectors[vec]["max_value"] <= 0:
                        self.movement_vectors[vec]["acceleration"] = max(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                    if self.movement_vectors[vec]["max_value"] > 0:
                        self.movement_vectors[vec]["acceleration"] = min(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                # if positive
                elif self.movement_vectors[vec]["direction_vectorX"] > 0:

                    # if not acceleration_reduced:
                    # subtract accelerations belonging to all negative vectors
                    self.movement_vectors[vec]["acceleration"] -= sum(positiveXaccel)/5

                    # # stop acceleration going beyond its max value
                    if self.movement_vectors[vec]["max_value"] <= 0:
                        self.movement_vectors[vec]["acceleration"] = max(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                    if self.movement_vectors[vec]["max_value"] > 0:
                        self.movement_vectors[vec]["acceleration"] = min(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                # reset wall colision var
                self.movement_vectors[vec]['inversion_collisionX'] = False
                
                # if positive
            if inversionCollisionY:
                self.movement_vectors[vec]["direction_vectorY"] *= -1


                # if negative
                if self.movement_vectors[vec]["direction_vectorY"] < 0:

                    # if not acceleration_reduced:
                        # subtract accelerations belonging to all negative vectors
                    self.movement_vectors[vec]["acceleration"] -= sum(negativeYaccel)/5

                    # stop acceleration going beyond its max value
                    if self.movement_vectors[vec]["max_value"] <= 0:
                        self.movement_vectors[vec]["acceleration"] = max(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                    if self.movement_vectors[vec]["max_value"] > 0:
                        self.movement_vectors[vec]["acceleration"] = min(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                # if positive
                elif self.movement_vectors[vec]["direction_vectorY"] > 0:

                    # if not acceleration_reduced:
                    # subtract accelerations belonging to all negative vectors
                    self.movement_vectors[vec]["acceleration"] -= sum(positiveYaccel)/5

                    # stop acceleration going beyond its max value
                    if self.movement_vectors[vec]["max_value"] <= 0:
                        self.movement_vectors[vec]["acceleration"] = max(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                    if self.movement_vectors[vec]["max_value"] > 0:
                        self.movement_vectors[vec]["acceleration"] = min(self.movement_vectors[vec]["acceleration"],self.movement_vectors[vec]["max_value"])

                # reset wall collision var
                self.movement_vectors[vec]['inversion_collisionY'] = False
                            
        # handle if we have a target point to move towards
        if target_point_to_stop_at:
            if find_dist_between_points(target_point_to_stop_at,position_before_movement) <= find_dist_between_points(self.hurtbox.center,position_before_movement):
                self.hurtbox.center = target_point_to_stop_at
                
        # # reset vectors
        self.direction_vectorX = 0
        self.direction_vectorY = 0
        self.collision_vector = Vector2(0,0)


    # roaming function, uses move 2
    def roaming(self):

        # include random movement
        # if movement not in movmenet vectors, sample from circle and move to point
        if 'movement' not in self.movement_vectors:

            # sample random point from a circle
            # random_point = Creative_Mode.random_sample_circle2(radius=200,circle_center=self.hurtbox.center)
            random_point = self.find_point_on_circle_radius(radius=100,circle_center=self.hurtbox.center)
            direction_vectorX,direction_vectorY = Vector2(random_point) - Vector2(self.hurtbox.center)

            self.add_movement_vector(unique_id='movement',direction_vectorX=direction_vectorX,
                                            direction_vectorY=direction_vectorY,acceleration=self.acceleration,acceleration_rate=0,
                                            acceleration_rate_change='negative',
                                            max_value=self.acceleration,invert_direction_vectors_on_collision=False,delete_on_max_value=False,
                                            target_point_to_stop_at=random_point)

        elif 'movement' in self.movement_vectors:


            # if we have arrived at the point then change the vector
            if self.hurtbox.center == self.movement_vectors['movement']['target_point_to_stop_at']:

                # sample random point from a circle
                # random_point = Creative_Mode.random_sample_circle2(radius=200,circle_center=self.hurtbox.center)
                random_point = self.find_point_on_circle_radius(radius=100,circle_center=self.hurtbox.center)
                direction_vectorX,direction_vectorY = Vector2(random_point) - Vector2(self.hurtbox.center)

                self.add_movement_vector(unique_id='movement',direction_vectorX=direction_vectorX,
                                            direction_vectorY=direction_vectorY,acceleration=self.acceleration,acceleration_rate=0,
                                            acceleration_rate_change='negative',
                                            max_value=self.acceleration,invert_direction_vectors_on_collision=False,delete_on_max_value=False,
                                            target_point_to_stop_at=random_point)

            # implement a random chance that
            else:

                if self.trigger_chance(percentage_chance=3):

                    random_point = self.find_point_on_circle_radius(radius=100,circle_center=self.hurtbox.center)
                    direction_vectorX,direction_vectorY = Vector2(random_point) - Vector2(self.hurtbox.center)

                    self.add_movement_vector(unique_id='movement',direction_vectorX=direction_vectorX,
                                                direction_vectorY=direction_vectorY,acceleration=self.acceleration,acceleration_rate=0,
                                                acceleration_rate_change='negative',
                                                max_value=self.acceleration,invert_direction_vectors_on_collision=False,delete_on_max_value=False,
                                                target_point_to_stop_at=random_point)


        self.move2()


    

    

    # apply damage function, handles death too
    def apply_damage(self,gameobj,damage:float):

        gameobj.health -= damage
        gameobj.health = max(0,gameobj.health)

        # init damage number
        # if pynaccle.display_dmg_num == 1:
        #     dmgnum = pynaccle.inactive_pool['DamageNumber'][0]
        #     dmgnum.init(f"{damage}")
        #     dmgnum.spawn(gameobj.hurtbox.center)
        #     dmgnum.add_movement_vector(unique_id='movement',direction_vectorX=0,
        #                                     direction_vectorY=-1,acceleration=self.acceleration,acceleration_rate=0,
        #                                     acceleration_rate_change='negative',
        #                                     max_value=self.acceleration,invert_direction_vectors_on_collision=False,delete_on_max_value=False)
        #     pynaccle.inactive_pool['DamageNumber'].remove(dmgnum)
        #     pynaccle.active_pool.append(dmgnum)


    # functions that can be for calculations etc
    # enter radius, and circle center, get a point on the circles outer radius
    def find_point_on_circle_radius(self,radius:float,circle_center:tuple):

        random_angle = random.randint(0,359)

        # return point on circle at that angle
        return (circle_center[0] + (radius * math.cos(math.radians(random_angle))),circle_center[1] + (radius * math.sin(math.radians(random_angle))))

    # trigger chance
    # percentage chance below 1 and greater than 0
    def trigger_chance(self,percentage_chance:float):

        # dvidie by 100
        percentage_chance = percentage_chance/100

        if percentage_chance >= 1:
            percentage_chance = 1

        elif percentage_chance <= 0:
            percentage_chance = 0

        # random.random generates a random floating point number
        if random.random() < percentage_chance:
            return True

        return False

    def find_raycast_endpoints(self,start_pos:tuple,target_pos:tuple,number_of_casted_rays:int=3,
                               fov_depth:int=50,fov_width:int=45,main_shot_angle_offset=0):

        DEPTH = fov_depth

        # calculate distance from target to start , on the left is where the rays are pointing to, on the right is where the rays orgininate from
        direction_vectorX = target_pos[0] - start_pos[0]
        direction_vectorY = target_pos[1] - start_pos[1]

        # get the angle of the line going from the player center to the mouse
        center_angle = math.atan2(direction_vectorY,direction_vectorX)

        FOV_CENTER = center_angle # middle line, the fov width is then added and subtracted to this to get the full line of sight area
        FOV_WIDTH = math.radians(fov_width)
        STARTING_ANGLE = FOV_CENTER + FOV_WIDTH # this gets angle on the leftmost side
        ENDING_ANGLE = FOV_CENTER - FOV_WIDTH

        # CASTED RAYS varibale, number of rays we want in the FOV cone
        # CASTED_RAYS = self.weapon_fov_rays
        CASTED_RAYS = number_of_casted_rays

        # get step which is start - end divide by casted rays. the -1 makes sure the ray in the middle is always drawn
        STEP_ANGLE = (STARTING_ANGLE-ENDING_ANGLE)/(CASTED_RAYS-1)

        raynumber_endpoint = {}

        # # # draw all casted rays
        for ray in range(CASTED_RAYS):

            # regular target x and target y. The one before is for drawingf and ahs an offset, this is the true position of the TIP of the FOV rays
            endpoint_x = start_pos[0] + math.cos(STARTING_ANGLE)*DEPTH
            endpoint_y = start_pos[1] + math.sin(STARTING_ANGLE)*DEPTH
            endpoint = (endpoint_x,endpoint_y)

            # add the ray number and the end point to the dictionary
            raynumber_endpoint[ray] = endpoint # used for straight shot

            # increment starting angle by a single step until we reach end angle
            STARTING_ANGLE -= STEP_ANGLE

        return raynumber_endpoint
    
    def explode(self,radius:float):

        # look through surrounding objects
        for gobj in self.surroundingGameObjects:

            if (Vector2(self.hurtbox.center) - Vector2(gobj.hurtbox.center)).length() < radius:

                self.apply_damage(gameobj=gobj,damage=self.damage)
                
    # what to do with object when not in frame
    def out_of_frame(self):
        
        return 'kill'

    def apply_powerup_effect(self,pup:object):

        if pup == 'Double Points':


            pass


        pass


    # function to find the angle of start pos to target pos
    def find_angle_to_point(self,start_pos:tuple,target_pos:tuple) -> float:

        # calculate distance from target to start , on the left is where the rays are pointing to, on the right is where the rays orgininate from
        direction_vectorX = target_pos[0] - start_pos[0]
        direction_vectorY = target_pos[1] - start_pos[1]

        # get the angle of the line going from the player center to the mouse
        center_angle = math.atan2(direction_vectorY,direction_vectorX)

        # returns angle in radians
        return center_angle

    def create_fov_ray(self,start_pos:tuple,angle:float,depth:float=300) -> tuple:

        # regular target x and target y. The one before is for drawingf and ahs an offset, this is the true position of the TIP of the FOV rays
        endpoint_x = start_pos[0] + math.cos(angle)*depth
        endpoint_y = start_pos[1] + math.sin(angle)*depth

        return (start_pos,(endpoint_x,endpoint_y))

    # given a point, find the topleft coordinate of the rect it is within
    def find_tile_topleft(self,pos:int,tile_size:int = 32) -> tuple:

        return ((pos[0] // tile_size) * tile_size,(pos[1] // tile_size) * tile_size)

    # find position of game object
    def update_position2(self):

        # uses the weird division thing to determine the integer of the square the player is on, then multiply that by tile size to get what tile ti actually is
        self.current_tile_position = find_tile_topleft(point=self.hurtbox.center)

        # add current tile position to
        objectManager.update_object_positions(coors=self.current_tile_position,object_to_add=self)
    





# movement vector class
class Movement_Vector():
        
    def __init__(self,name:str='movement',direction_vectorX:float=0,direction_vectorY:float=0,acceleration:float=1,acceleration_rate:float=1,
                    acceleration_rate_change:str='positive',invert_direction_vectors_on_collision:bool=False,max_value:float=0,delete_on_max_value:bool='False',
                    target_point_to_stop_at:tuple=None):
        
        self.name = name
        self.direction_vectorX = direction_vectorX
        self.direction_vectorY = direction_vectorY
        self.acceleration = acceleration
        self.acceleration_rate = acceleration_rate
        self.acceleration_rate_change = acceleration_rate_change
        self.invert_direction_vectors_on_collision = invert_direction_vectors_on_collision
        self.max_value = max_value
        self.delete_on_max_value = delete_on_max_value
        self.target_point_to_stop_at = target_point_to_stop_at

# create damage number
class DamageNumber(Moveable_Object):

    def __init__(self):

        Moveable_Object.__init__(self)
        
    def init(self,text:str='1'):

        self.init_text_sprite(f"{text}")
        self.init_sprite()
        self.alpha = 1
        self.is_active = True
        self.hurtbox.center = (0,0)
        self.timer_speed = 4
        self.timer_limit = 6
        self.speed = 200
        self.zlayer_drawing = 2
        self.timer_init()
        

    def run_behaviour(self):

        self.reduce_alpha()

        self.move_and_collide()

        # draw surface
        self.draw_surface(position=self.hurtbox.center)
        

# add the card inactive pool to the object that stores all the pools for different projectiles/on shot effects
# objectManager.inactive_pool["DamageNumber"] = [DamageNumber() for _ in range(300)]


# code to show damage numbers
# event processing for shooting
# def display_dmg_num_event(event:pygame.Event):

#     # handling mouse clicks
#     if event.type == pygame.KEYDOWN:

#         if event.key == pygame.K_c:

#            pynaccle.display_dmg_num *= -1

# pynaccle.extra_event_processing.append(display_dmg_num_event)
