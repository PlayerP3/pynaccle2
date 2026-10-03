import random,string
import pygame,math,sys
from pygame.math import Vector2
from .screen import gameScreen
from .utils import *
from enum import Enum,auto
from .animatedsprite import AnimatedSprite
from .statemachine import StateMachine
from .States.Task.idle import Idle
from .States.Task.active import Active
from .States.Task.completed import Completed


# class Tasks(Enum):
    
#     PLACEHOLDER = 'placeholder'
#     FILLSOULBOX = 'fillSoulBox'
#     PICKUPWEAPON = 'pickUpWeapon'
#     PLACEWEAPON = 'placeWeapon'
#     GOTOLOCATION = 'goToLocation'
#     INTERACTWITHITEM = 'interactWithItem'
    


class Task(StateMachine):

    def __init__(self,parentNodes:list=None,linkedNodes:list=None,targetValue=1,taskType:str='placeholder',description:str='Complete this task.'):

        self.description = description
        self.parentNodes = parentNodes or []
        self.linkedNodes = linkedNodes or []
        self.taskType = taskType
        self.targetValue = targetValue
        self.currentValue = 0
        self.displayIcon = AnimatedSprite()
        
        super().__init__()

    def init(self):

        # init state machine
        self.states = {'IDLE':Idle(),
                       'ACTIVE':Active(),
                       'COMPLETED':Completed()}

        # set parent node for player states
        for x in self.states:
            self.states[x].parent_node = self
            # self.states[x].timer_limit = self.stateTimeLimit[x]
        
        # pick state to start in
        self.state = self.states['IDLE']


    def run(self):
        pass

    def display_progress(self):
        pass

    # @property
    # def description(self):

    #     if self.taskType is Task.FILLSOULBOX:
    #         return  'Fill '

    def activate(self):
        
        self.state.emit('ACTIVE')

    def end_condition(self):

        if self.currentValue >= self.targetValue:
            self.done = True
            
    # set parent nodes
    def add_parent_nodes(self,nodes):
        
        if isinstance(nodes,list):
            self.parentNodes.extend(nodes.copy())
            
        else:
            self.parentNodes.append(nodes)
            
    # set linked nodes
    def add_linked_nodes(self,nodes):
        
        if isinstance(nodes,list):
            self.linkedNodes.extend(nodes.copy())
            
        else:
            self.linkedNodes.append(nodes)

    # set target value
    def set_target_value(self,value:float):
        
        self.targetValue = value
        
    # set description
    def set_description(self,value:str):
        
        self.description = value