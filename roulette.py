from pynaccle.utils import *
import json
from pynaccle.moveableobject import Moveable_Object
from pynaccle.interactable import Interactable
from .States.Roulette.cycling import Cycling
from .States.Roulette.display import Display
from .States.Roulette.reset import Reset
from .States.Roulette.idle import Idle
import sys
from .tilemap import tilemapProcessor
from .objectsystem import objectManager
from .pathfinding import *
from .animatedsprite import AnimatedSprite


class Roulette(Interactable):

    def __init__(self,options:dict={},idleInteractTimerLimit:float=0.4,displayInteractTimerLimit:float=0.4,nextOptionCycleTimeLimit:float=0.5,cycleSpeed:float=1.5,

                 randomSampleCount:float=5, maxDisplayItemZoom:float=1.5, minDisplayItemZoom:float=0.5, displayItemZoomChangeSpeed:float=0.1):

        # super().__init__()
        Interactable.__init__(self)
        
        # get options  i.e what it cycles through
        self.options = options
        self.filteredOptions = options
        
        # variables that are constant and do not change
        self.idleInteractTimerLimit = idleInteractTimerLimit
        self.displayInteractTimerLimit = displayInteractTimerLimit

        # obj that first interacted with the roulette oj
        self.purchasingObj = None

        # get item display object
        self.displayItem = AnimatedSprite()
        self.finalDisplay = None

        # vars for max and min display sprite zoom
        self.maxDisplayItemZoom = maxDisplayItemZoom
        self.minDisplayItemZoom = minDisplayItemZoom
        self.displayItem.zoom = self.minDisplayItemZoom
        self.displayItem.lerpTimer.timer_speed = displayItemZoomChangeSpeed

        # cycling variables
        # time limit for cycling to the next option
        self.nextOptionCycleTimeLimit = nextOptionCycleTimeLimit
        self.cycleSpeed = cycleSpeed
        self.cycleTimer = Timer(timer_speed=self.cycleSpeed,timer_limit=nextOptionCycleTimeLimit,timer_replay=True)
        self.cycleList = []

        
        
        self.displayItem.zlayer_drawing = self.zlayer_drawing + 1
        
        # how many replicates of each cycle option to make for rando smapling
        self.randomSampleCount = randomSampleCount 

    def init(self):

        super().init()

        # set states
        # init state machine
        self.states = {'IDLE':Idle(),
                       'CYCLING':Cycling(),
                       'DISPLAY':Display(),
                       'RESET':Reset()
                       }
        
        # set new vars for certain states
        self.states['CYCLING'].timer_limit = 4
        self.states['DISPLAY'].timer_limit = 8
        
        # set animation player to not replay
        self.animationPlayer.timer_replay = False

        
        # set parent node for player states
        for x in self.states:
            self.states[x].parent_node = self
        
        self.state = self.states['IDLE']
        # self.state.enter()

        

    # what happens when pickup is done like changing stats etc
    def pay(self,gameobj):

        if gameobj.money >= self.cost:

            gameobj.money -= self.cost

            # give item
            self.give_item(gameobj=self.interactingObj)


    # swap weapon function
    def give_item(self,gameobj):
        pass

        # # first end weapon state
        # gameobj.weapon.state.completed()

        # # find first element in list which is current weapon
        # current_weapon = gameobj.allWeapons[0]
        
        # # set weapon to give to player
        # weapon_to_give = self.buildableObject

        # if len(gameobj.allWeapons) < gameobj.weaponCarryLimit:

        #     # remove current weapon and add to end of list
        #     gameobj.allWeapons.insert(0,weapon_to_give)


        # elif len(gameobj.allWeapons) >= gameobj.weaponCarryLimit:

        #     # remove current weapon and add to end of list
        #     gameobj.allWeapons.remove(current_weapon)
        #     gameobj.allWeapons.insert(0,weapon_to_give)

        # # set new weapon
        # gameobj.weapon = guns[weapon_to_give]
        # gameobj.weapon.wielded_by = gameobj

        # # enter state
        # gameobj.weapon.state = gameobj.weapon.states['PICKUP']
        # gameobj.weapon.state.enter()

    # swap weapon function
    # def remove_item(self,gameobj):

    #     # first end weapon state
    #     gameobj.weapon.state.completed()

    #     # find first element in list which is current weapon
    #     next_weapon = gameobj.allWeapons[1]
        
    #     # set weapon to give to player
    #     weapon_to_remove = self.buildableObject

    #     # remove weapon
    #     gameobj.allWeapons.remove(weapon_to_remove)

    #     # set new weapon
    #     gameobj.weapon = guns[next_weapon]
    #     gameobj.weapon.wielded_by = gameobj

    #     # enter state
    #     gameobj.weapon.state = gameobj.weapon.states['PULLOUT']
    #     gameobj.weapon.state.enter()

    # collision check
    def collision_check(self,axis:str='y'):

        self.state.collision_check()
        pass

    def handle_collision(self,axis:str='y'):

        self.state.handle_collision()
        pass

    def update_data(self):

        self.update_position()


    def filter_cycle_options(self):
    
        pass

    def predetermine_cycle_options(self):

        # filter options, i.e removing wonder weapons etc
        self.filter_cycle_options()

        # reset cycle list
        self.cycleList = []

        # now based on length of cycle timer and speed find how many frames/sprites we need, + 1 because we start the cycle loop by skipping the first cycle
        totalFrames = int(self.states['CYCLING'].timer_limit//(self.nextOptionCycleTimeLimit/self.cycleSpeed)) + 1

        # get list of items to cycle through, for counts we are basically keeping 3 of each weapon 
        self.cycleList = random.sample(population=list(self.filteredOptions.keys()),k=totalFrames,counts=[self.randomSampleCount for x in range(0,len(list(self.filteredOptions.keys())))])

    # function to get the images we cycle through
    def cycle_through_options(self):

        # run cycle timer
        self.cycleTimer.run_timer()

        # if timer complete
        if self.cycleTimer.timer_complete:

            # change display item
            self.displayItem.img_path = self.filteredOptions[self.cycleList[0]]['img_path']

            # remove first item in cycle list
            self.cycleList = self.cycleList[1:]

        # display item
        self.displayItem.submit_to_render()

        # lerp sprite size
        self.displayItem.lerpTimer.start_timer()
        self.displayItem.lerpTimer.run_timer()
        self.displayItem.zoom = linear_lerp(self.minDisplayItemZoom,self.maxDisplayItemZoom,self.displayItem.lerpTimer.elapsed_time)

    # function to pick a final display
    def predetermine_final_display(self):

        # pick item to give, need to pass dict of item name and its weight only
        self.finalDisplay = proc_using_weights({k:v['weight'] for k,v in self.filteredOptions.items()})

    # function to control how the display item acts during cycling
    def update_display_item(self):

        pass

    # pick the final result based on the options
    def choose_final_display(self):

        pass
            



    
