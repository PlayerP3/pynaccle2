import pygame,random,os,string,numpy,math,json,copy,ast,sys
from pygame.math import Vector2
from .statemachine import StateMachine
from .hitbox import hitboxSystem
from .screen import gameScreen
from .objectsystem import objectManager
from .eventsystem import eventprocessor
from .pens import penHolder
from .tilemap import tilemapProcessor
from .hud import overlay
from .inventory import gameInventory
from .configs import configData
from .quest import questManager
# from .shaders import context


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


class Engine(GameStateMachine):

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
        self.inventory = gameInventory
        self.configData = configData 
        self.questManager = questManager

        # create vars
        self.tileSize = None

        self.gamePath = None

        


    # def init(self,states:dict={},beginningState:str='START',tilemapPath:str='',classMappings:dict={},player:object=None,tileSize:int=32):
    def init(self,states:dict={},beginningState:str='SPLASH',tilemapJSONDir:str='tilemaps',classMappings:dict={},
             windows:str='configs/config_window.json',hitboxMetadataJSON:str='',configs:list=[]):

        # set path to game
        # self.gamePath = gamePath

        # load shaders
        # self.context.load_shaders(shaderDir)

        # set states
        self.states = states

        # set parent node for player states
        for x in self.states:
            self.states[x].parent_node = self
    
        # set first state and enter
        self.state = self.states[beginningState]
        
        # store configs
        if configs:
            for f in configs:
    
                # add the config to the object
                self.configData.add_config(f)

        # add windows to screen
        with open(windows,'r') as winConfig:

            winParams = json.load(winConfig)

            for winName in winParams:
                
                self.screenManager.add_window(winName=winName,width=winParams[winName]["width"],height=winParams[winName]["height"],
                                              zoom=winParams[winName]["zoom"],pos=(self.screenManager.fullscreen_width//2,self.screenManager.fullscreen_height//2),
                                              stateZoom=winParams[winName]["stateZoom"])

        # process tilemap
        self.tilemapProcessor.load_tilemap(tileampJSONDir=tilemapJSONDir,classMappings=classMappings)


        # load hitbox meta data
        if hitboxMetadataJSON:
            with open(hitboxMetadataJSON,'r') as hitboxMetadataFile:

                boxMetadata = json.load(hitboxMetadataFile)

            hitboxSystem.metaData = boxMetadata

    def run(self):

        if self.playing:
            self.update()
        
        


        
            

