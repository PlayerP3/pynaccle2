import pygame,random,os,string,numpy,math,json,copy,ast,sys
from pygame.math import Vector2
from .statemachine import StateMachine
from .screen import gameScreen
from .objectsystem import objectManager
from .eventsystem import eventprocessor
from .pens import penHolder
from .tilemap import tilemapProcessor
from .hud import overlay

pygame.font.init()

class GameStateMachine(StateMachine):

    def __init__(self):

        StateMachine.__init__(self)

    def update(self):

        # get all events
        eventprocessor.events = pygame.event.get()

        # handle events
        eventprocessor.process_base_events()


        self.state.update()

        if self.state.done:
            self.transition_to_next_state()


class Pynaccle(GameStateMachine):

    def __init__(self):

        # vars for running the game
        self.playing = True

        self.clock = pygame.time.Clock()

        # get managers
        self.eventprocessor = eventprocessor
        self.objectManager = objectManager
        self.screenManager = gameScreen
        self.penHolder = penHolder
        self.tilemapProcessor = tilemapProcessor
        self.overlay = overlay
        
        # loaded configs stored here
        self.loadedConfigs = {}

        # create vars
        self.tileSize = None

    # def init(self,states:dict={},beginningState:str='START',tilemapPath:str='',classMappings:dict={},player:object=None,tileSize:int=32):
    def init(self,states:dict={},beginningState:str='SPLASH',tilemapJSON:str='',classMappings:dict={}):

        # set states
        self.states = states

        # set parent node for player states
        for x in self.states:
            self.states[x].parent_node = self
    
        # set first state and enter
        self.state = self.states[beginningState]

        self.tilemapProcessor.load_tilemap(tileampJSON=tilemapJSON,classMappings=classMappings)

    def run(self):

        if self.playing:
            self.update()


      
        


        
            

