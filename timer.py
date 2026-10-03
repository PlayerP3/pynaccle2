import random,string
import pygame,math
from pygame.math import Vector2
from .globs import *

class Timer():

    def __init__(self,timer_speed:float=1,timer_limit:float=3,timer_replay:bool=False,timerReverse:bool=False):

        self.current_time = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.elapsed_time_fraction = 0
        self.timer_limit = timer_limit
        self.timeRemaining = timer_limit
        self.timeRemainingFraction = 0 if not self.timer_limit else 1
        self.timer_speed = timer_speed
        self.timer_running = True
        self.timer_complete = False
        self.paused_time = 0
        
        # time replaying
        self.timer_replay = timer_replay

    def reset_timer(self):

        self.elapsed_time = 0
        self.elapsed_time_fraction = 0
        self.timeRemaining = self.timer_limit
        self.timeRemainingFraction = 0 if not self.timer_limit else 1
        self.timer_running = False
        self.timer_complete = False


    def timer_init(self,startTime:float=0):
        
        # if self.timer_complete:
        # self.current_time = pygame.time.get_ticks()/1000
        # self.start_time = pygame.time.get_ticks()/1000

        self.elapsed_time = 0
        self.elapsed_time_fraction = 0
        self.timeRemaining = self.timer_limit
        self.timeRemainingFraction = 0 if not self.timer_limit else 1
        self.timer_running = True
        self.timer_complete = False

    def start_timer(self,startTime:float=0):

        if self.elapsed_time == 0:
            self.timer_init(startTime)

    def pause_timer(self):
        self.paused_time = self.start_time

    def resume_timer(self):
        self.elapsed_time += self.paused_time

    def run_timer(self):
        
        # if timer isnt complete
        if self.timer_running:

            # get elapsed time
            self.elapsed_time += (delta*self.timer_speed)
            self.timeRemaining = self.timer_limit - self.elapsed_time

            if self.timer_limit > 0 and self.timer_speed > 0:
                self.elapsed_time_fraction = self.elapsed_time/self.timer_limit
                self.timeRemainingFraction = self.timeRemaining/self.timer_limit


            if self.elapsed_time >= self.timer_limit:

                self.timer_running = False

                # if replay
                if self.timer_replay:

                    # set timer complete to false so it keeps on running 
                    self.timer_running = True
                    self.elapsed_time = 0
                    self.timeRemaining = self.timer_limit


                self.timer_complete = True

            else:
                self.timer_complete = False

    # use function and timer to map a variable to a sine function/wave
    def map_to_sine_wave(self):

        # sin wave returns value betywene -1 to 1, so we force it to return vales between 0 and 1
        # return (math.sin(self.elapsed_time) + 1)/2
        return (1-math.cos(self.elapsed_time))*0.5




class AnimationPlayer(Timer):
 
    def __init__(self,totalFrames:int=1,animationType:str='forward',animationDelay:float=1):

        Timer.__init__(self)

        self.totalFrames = totalFrames
        self.animationType = animationType
        self.animationDelay = animationDelay

        # replay timer is true
        self.timer_replay = True

        # depending on reverse or forward set current frame number
        self.find_current_frame_number()


    def find_current_frame_number(self):

        if self.animationType == 'forward':
            self.currentFrameNumber = (self.elapsed_time//self.animationDelay) % self.totalFrames
        
        elif self.animationType == 'reverse':
            self.currentFrameNumber = (self.timeRemaining//self.animationDelay) % self.totalFrames
        
        elif self.animationType == 'ping-pong-forward':
            self.currentFrameNumber = self.elapsed_time_fraction % self.totalFrames
        
        elif self.animationType == 'ping-pong-reverse':
            self.currentFrameNumber = self.elapsed_time_fraction % self.totalFrames
        

    def reset_timer(self):

        self.elapsed_time = 0
        self.elapsed_time_fraction = 0
        self.timeRemaining = self.timer_limit
        self.timeRemainingFraction = 0 if not self.timer_limit else 1
        self.timer_running = False
        self.timer_complete = False


    def timer_init(self,startTime:float=0):
        
        # if self.timer_complete:
        # self.current_time = pygame.time.get_ticks()/1000
        # self.start_time = pygame.time.get_ticks()/1000

        self.elapsed_time = startTime
        self.elapsed_time_fraction = startTime/self.timer_limit
        self.timeRemaining = self.timer_limit - startTime
        self.timeRemainingFraction = 0 if not self.timer_limit else self.timeRemaining/self.timer_limit
        self.timer_running = True
        self.timer_complete = False

    def start_timer(self,startTime:float=0):

        if self.elapsed_time == 0:
            self.timer_init(startTime)
        
    def pause_timer(self):
        self.paused_time = self.start_time

    def resume_timer(self):
        self.elapsed_time += self.paused_time

    def run_timer(self):

        # if timer isnt complete
        if self.timer_running:

            # calculate frame number
            self.find_current_frame_number()

            # get elapsed time
            self.elapsed_time += (delta*self.timer_speed)
            self.timeRemaining = self.timer_limit - self.elapsed_time

            if self.timer_limit > 0 and self.timer_speed > 0:
                self.elapsed_time_fraction = self.elapsed_time/self.timer_limit
                self.timeRemainingFraction = self.timeRemaining/self.timer_limit


            if self.elapsed_time >= self.timer_limit:

                self.timer_running = False

                # if replay
                if self.timer_replay:

                    # set timer complete to false so it keeps on running 
                    self.timer_running = True
                    self.elapsed_time = 0
                    self.timeRemaining = self.timer_limit


                self.timer_complete = True

            else:
                self.timer_complete = False

            
           

    # use function and timer to map a variable to a sine function/wave
    def map_to_sine_wave(self):

        # sin wave returns value betywene -1 to 1, so we force it to return vales between 0 and 1
        # return (math.sin(self.elapsed_time) + 1)/2
        return (1-math.cos(self.elapsed_time))*0.5

