import pygame,os,re,math,random,string
import json
from pygame.math import Vector2
from pygame.event import Event
# from game import engine
from .eventsystem import eventprocessor
from .timer import Timer
# from States.Player.idle import Idle



class StateMachine():

    def __init__(self):

        self.initial_state:State = 'IDLE'
        self.state:State = None
        self.states = {}
        self.previous_state:State = None
        self.next_state:State = None


    # # init state machine
    # def init(self):

    #     pass

    def transition_to_next_state(self):

        old_state = self.state
        new_state = self.states[self.state.next_state]
        self.state.completed()
        self.state = new_state
        self.state.enter()

    def update(self):

        self.state.update()

        if self.state.done:
            self.transition_to_next_state()

    def unhandled_events(self,event):

        self.state.handle_event(event)
        
    @property
    def currentState(self):
        
        # get array of matched state
        matchedState = [k for k,v in self.states.items() if v == self.state]
        
        if not matchedState:
            return 'No State'
        
        else:
            return matchedState[0]

    
   
class State(Timer):

    def __init__(self):

        # node which is the obejct that the the state is attached to
        self.parent_node = None

        # the state to transition to on completion, this has to be a string
        self.next_state = None

        # signals for completion
        self.done = False
        
        Timer.__init__(self)
    
    def enter(self):
        pass

    def emit(self,state:str):

        if state == self.__class__.__name__.upper():
            return

        self.next_state = state
        self.done = True

    def completed(self):

        # if something then set new state
        self.next_state = None

        # set done to false
        self.done = False

    def update(self):
        pass

    def handle_event(self,event:Event):

        pass

    def submit_event_processing(self):

        eventprocessor.extra_event_processing.append(self.handle_event)

    def end_condition(self):

        pass

    @property
    def name(self):
        return self.__class__.__name__


# # set Dict of all states
# all_states = {'IDLE':Idle,
#           'RUNNING':Running,
#           'BUYING':Buying,
#           'GAMBLING':Gambling}
