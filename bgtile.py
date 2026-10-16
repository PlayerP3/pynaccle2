import json,sys
from .utils import *
from .moveableobject import Moveable_Object
from .objectsystem import objectManager


class BgTile(Moveable_Object):

    # keep start and end point arguments in case i want to give the bullet some quirky pathing when shot
    def __init__(self):

        super().__init__()
    
        
    def init(self):

        super().init()

    # combines movement and collision function
    def update(self):

        # only show the orbital and draw it if it is active
        if self.is_active:

            # draw surface
            self.submit_to_render()
            

