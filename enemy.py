import pygame,json
from pygame.math import Vector2
from .pathfinding import Pathfinding
from .moveableobject import Moveable_Object
from .utils import *
from .statemachine import StateMachine
from .objectsystem import objectManager
from .States.Enemy.idle import Idle
from .States.Enemy.chasing import Chasing
from .States.Enemy.roaming import Roaming
from .States.Enemy.death import Death
from .States.Enemy.attacking import Attacking
from .States.Enemy.distracted import Distracted

# from ItemBench import ItemPools,ItemPoolsReset,remove_from_itempool,add_to_itempool
pygame.font.init()

class Enemy(Moveable_Object,Pathfinding,StateMachine):

    def __init__(self,targetGameObjectTypePriorityList=None,distanceToTriggerAttackState:float=30):

        Moveable_Object.__init__(self)
        Pathfinding.__init__(self)
        StateMachine.__init__(self)

        # movement
        self.movementx = [0,0] # index 0 is no movememnt, -1 left, 1 right
        self.movementy = [0,0] # index 0 is no movement, -1 up, 1 down
        
        # game object that is a target for attack
        self._targetGameObject = None
        self.targetGameObjectTypePriorityList = targetGameObjectTypePriorityList or ['Distraction','Player']
        
        # distance to the target game object that triggers some state change
        self.distanceToTriggerAttackState = distanceToTriggerAttackState
        
        # target position for shooting
        self.shooting_target_position = (0,0)

    # reinit
    def init(self):

        # init state machine
        self.states = {'IDLE':Idle(),
                       'CHASING':Chasing(),
                       'DEATH':Death(),
                       'DISTRACTED':Distracted(),
                       'ATTACKING':Attacking()}
        
        # set parent node for player states
        for x in self.states:
            self.states[x].parent_node = self
        
        self.state = self.states['IDLE']

        super().init()


    def update(self):
    
        self.state.update()
        
        if self.state.done:
            self.transition_to_next_state()
                        
    # action to take whilst in idle
    def select_state(self):
        pass
    
    

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
                                    acceleration=((game_object.overlap_resolution_strength/self.overlap_resolution_resistance)),acceleration_rate=self.decceleration_rate,acceleration_rate_change='negative',max_value=0,
                                    invert_direction_vectors_on_collision=True,delete_on_max_value=True)

    # choose position that the enemy targets with its pathfinding
    def set_pathing_end_pos(self,pos:tuple=None):
        
        if not pos:
            if self.targetGameObject:
                self.pathing_end_pos = self.targetGameObject.hurtbox.center
                
            elif not self.targetGameObject:
                self.pathing_end_pos = None
                
        elif pos:
            self.pathing_end_pos = pos

    @property
    def priorityGameObjectType(self):
        
        if not self.targetGameObjectTypePriorityList:
            return None
        
        elif self.targetGameObjectTypePriorityList:
            
            # find if the top priority is in the list
            topPriorityInActivePool = [goType for goType in self.targetGameObjectTypePriorityList if goType in objectManager.active_pool][0]
            
            return topPriorityInActivePool
        
    @property
    def targetGameObject(self):
        
        # choose the closest game object of the priority
        if self.priorityGameObjectType:
            
            # subset and find the closest obj
            self._targetGameObject = min(objectManager.active_pool[self.priorityGameObjectType],key=lambda x:find_dist_between_points(self.hurtbox.center,x.hurtbox.center))

        elif not self.priorityGameObjectType:
            
            self._targetGameObject = None
            
        return self._targetGameObject
    
    @targetGameObject.setter
    def targetGameObject(self,value):
        self._targetGameObject = value
    

    
