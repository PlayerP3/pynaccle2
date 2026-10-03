import json,random,sys
from .moveableobject import Moveable_Object
from .animatedsprite import AnimatedSprite
from .displaymessage import DisplayMessage
from .utils import *
from .statemachine import StateMachine
from .objectsystem import objectManager
from .States.Interactable.idle import Idle
from .timer import Timer

class Interactable(StateMachine,Moveable_Object):

    def __init__(self,cost:float=0):

        # Moveable_Object.__init__(self)
        # super().__init__()
        Moveable_Object.__init__(self)
        StateMachine.__init__(self)
        

        # things an interactable needs:
        # a separate rect to handle its interaction window
        # a message to blit or not to blit when something is interacting
        # returning true if something has interacted with it in the required way

        # display message
        self.display_message = DisplayMessage()

        # cost, 0 for most things so you can interact regardless of money
        self.cost  = cost

        # interacting obj
        self.interactingObj = None

        # create interact timer
        self.interactTimer = Timer()
        
        # create dict that stores the state as key and the interaction time when in the state 
        self.stateInteractTimeLimit = {'IDLE':0.1}

        # store time limit for each state
        self.stateTimeLimit = {'IDLE':3}
        
        # super().__init__()
        
  

    def init(self):
        
        super().init()

        # display message init
        self.display_message.init()

        # init state machine
        self.states = {'IDLE':Idle()}

        # set parent node for player states
        for x in self.states:
            self.states[x].parent_node = self
            self.states[x].timer_limit = self.stateTimeLimit[x]
        
        # pick state to start in
        self.state = self.states['IDLE']

    # change spawn function to spawn 
    def spawn(self,pos:tuple,vertice:str="center",displayMessageOffsetX:int=10,displayMessageOffsetY:int=10):

        self.is_active = True

        if vertice == "center":
            self.hurtbox.center = (pos[0]+self.spawnOffsetX,pos[1]+self.spawnOffsetY)

        elif vertice == "topleft":
            self.hurtbox.topleft = (pos[0]+self.spawnOffsetX,pos[1]+self.spawnOffsetY)

        # set position of display message
        self.display_message.spawn(pos=(pos[0] + (self.spriteWidth//2 + displayMessageOffsetX),pos[1] - (self.spriteHeight//2 + displayMessageOffsetY)))

        # enter state
        self.state.enter()
    

    # collision check
    def collision_check(self,axis:str='y'):

        self.state.collision_check()
        pass

    def handle_collision(self,axis:str='y'):

        self.state.handle_collision()
        pass

    def update_data(self):
        pass
  
    def run_effect(self,gameobj:object):
        pass

    # paying for interactable
    def pay(self,gameobj:object):

        if gameobj.money >= self.cost:
            gameobj.money -= self.cost

            # run effect depending on interactable
            self.run_effect(gameobj=gameobj)

            


    # what happens when object is within interacting rnage but not colliding with the actual object
    def handle_interaction(self,gameobj:object):

        # if the game obj is interacting
        if gameobj.is_interacting:

            # run timer
            self.run_timer()

            if self.timer_complete:
               
               self.pay()

    # draw message
    def draw_message(self,pos:tuple):

        # init sprite
        self.display_message.init_sprite()
        
        # display message
        self.display_message.submit_to_render()


    # clear interactable
    def clear_interactingObj(self):

        if self.interactingObj:

            self.interactingObj.is_interacting = False
            self.interactingObj = None

    # start interaction timer which is the time the state lasts
    def run_interaction_timer(self):

        if self.interactingObj:
            self.interactTimer.start_timer()
            self.interactTimer.run_timer()

        elif not self.interactingObj:
            self.interactTimer.reset_timer()

    # some geenral updates
    def update_data(self):

        self.update_position()


# add the card inactive pool to the object that stores all the pools for different projectiles/on shot effects
objectManager.inactive_pool["Interactable"] = [Interactable() for _ in range(300)]


