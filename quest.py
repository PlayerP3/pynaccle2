import random,string
import pygame,math,sys
from pygame.math import Vector2
from .screen import gameScreen
from .utils import *
from enum import Enum,auto
from .animatedsprite import AnimatedSprite
from .statemachine import StateMachine
from .States.Quest.idle import Idle
from .States.Quest.active import Active
from .States.Quest.completed import Completed
from .task import Task


class Quest(StateMachine):

    def __init__(self,parentNodes:list=[],prerequisites:list=[],rewards=[],tasks:dict={},followOrder:bool=True,description:str='Description goes here.'):

        self.parentNodes = parentNodes
        self.tasks = tasks
        self.description = description
        self.prerequisites = prerequisites
        self.rewards = rewards
        self.followOrder = followOrder
        self.displayIcon = AnimatedSprite()
        self.currentTask = 0
        
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
        
    def activate(self):
        
        self.state.emit('ACTIVE')
        
        # start task
        self.start_task()
        
        
    def start_task(self):
        
        self.tasks[self.currentTask].activate()
        
    def move_to_next_task(self):
        
        if self.tasks[self.currentTask].currentState == 'COMPLETED':
            
            self.currentTask += 1
            
            if self.currentTask >= len(self.tasks):
                self.state.emit('COMPLETED')
                return            
            
            # start next task
            self.start_task()
            
            
        
    def add_task(self,taskPosition:int,task:Task):

        # init task 
        task.init()
        
        # add task to queue
        self.tasks[taskPosition] = task
       
    def remove_task(self,taskPosition:int):
        
        del self.tasks[taskPosition]
        
    def update_task(self):
        
        # if we are following an order than we just run the current one
        if self.followOrder:
            
            self.tasks[self.currentTask].update()
            
            # move to next task if complete
            self.move_to_next_task()

    # set description
    def set_description(self,value:str):
        
        self.description = value
        
    # set parent nodes
    def add_parent_nodes(self,nodes,copyToTasks:bool=False):
        
        if isinstance(nodes,list):
            self.parentNodes.extend(nodes.copy())
                
        else:
            self.parentNodes.append(nodes)
            
        if copyToTasks:
            for _,tsk in self.tasks.items():
                tsk.add_parent_nodes(nodes)


            
    # assign a quest
    # def assisgn_quest(self):
        
    #     for pn in self.parentNodes:
    #         pass


class QuestManager():
    
    def __init__(self):
        
        self.inactiveQuests = {}
        self.activeQuests = {}
        self.completedQuests = {}
        
    def start_quest(self,name):
        
        # move quest to active quests
        self.activeQuests[name] = self.inactiveQuests[name]
        
        # init quest
        self.activeQuests[name].init()
        
        # activate quest
        self.activeQuests[name].activate()
        
        # remove from inactive quests
        del self.inactiveQuests[name]

    def add_quest(self,name:str,quest:Quest):
        
        if name not in self.inactiveQuests:
            
            # add quest to dict
            self.inactiveQuests[name] = quest
            
    def remove_quest(self,name:str):
        
        # add to completed quest
        self.completedQuests[name] = self.activeQuests[name]
        
        # remove from active quests 
        del self.activeQuests[name]
    
    def update(self):
        
        if self.activeQuests:
            for _,quest in self.activeQuests.items():
                quest.update()


questManager = QuestManager()