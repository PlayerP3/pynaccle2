import pygame,os,re,sys
from pygame.math import Vector2
from .utils import *


class Inventory():

    def __init__(self):

        self.inventory = {}

    def add_item(self,k1:str='',k2:str='',v:str=''):

        # if not k2 it means we dont have a nested dict
        if not k2:
        
            # create key if one does not exist
            if not k1 in self.inventory:
                self.inventory[k1] = []

            # append to inventory list
            if v not in self.inventory[k1]:
                self.inventory[k1].append(v)

        # elif if we do have k2 then it means have a nestged dict structure
        elif k2:
        
            # create key if one does not exist
            if not k1 in self.inventory:
                self.inventory[k1] = {}
            
            # create k2 if it does not exist
            if not k2 in self.inventory[k1]:
                self.inventory[k1][k2] = []

            # append to inventory list
            if v not in self.inventory[k1][k2]:
                self.inventory[k1][k2].append(v)

    def remove_item(self,k1:str='',k2:str='',v:str=''):

        if not k2:
            self.inventory[k1].remove(v)

        elif k2:
            self.inventory[k1][k2].remove(v)


    def delete_item(self,key):

        del self.inventory[key]
        
    def get_inventory_item_size(self,k1:str='',k2:str=''):

        # if not k2 it means we dont have a nested dict
        if not k2:
        
            # create key if one does not exist
            if not k1 in self.inventory:
                return 0

            elif k1 in self.inventory:
                return len(self.inventory[k1])
            
        # elif if we do have k2 then it means have a nestged dict structure
        elif k2:
        
            # create key if one does not exist
            if not k1 in self.inventory:
                return 0
            
            # create k2 if it does not exist
            if not k2 in self.inventory[k1]:
                return 0
            
            elif k2 in self.inventory[k1]:
                return len(self.inventory[k1][k2])


    


gameInventory = Inventory()