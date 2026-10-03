import pygame,os,re,math,random,string
import json

class EventSystem():

    def __init__(self):
       
        # get events
        self.events = None

        # get extra event processing
        self.extra_event_processing = []
    
    # handle base events
    def process_base_events(self):

        # loop through events
        for event in self.events:

            # if the actual X is clicked to close the tab
            if event.type == pygame.QUIT:
                pygame.quit()

            for processor in self.extra_event_processing:

                processor(event)

        # empty extra event processing
        self.extra_event_processing = []

eventprocessor = EventSystem()