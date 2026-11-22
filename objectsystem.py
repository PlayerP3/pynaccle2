import pygame,random,os,string,numpy,math,json,copy,ast
from .tilemap import tilemapProcessor
from .utils import *
pygame.font.init()

class ObjectSystem():

    def __init__(self):

        # position of game objects
        self.object_positions = {}

        # get active pools
        self.active_pool = {}
        self.inactive_pool = {}
        self.inactiveNoPool = []
        
        # store things killed in this frame
        

        # path cache for objs
        self.path_cache = {}

        # set player
        self.player = None
        
    # add game object to the active pool
    def add_game_object_to_active_pool(self,game_object):
        
        if game_object.__class__.__name__ not in self.active_pool:
            
            self.active_pool[game_object.__class__.__name__] = []
            self.active_pool[game_object.__class__.__name__].append(game_object)
            
            if game_object.__class__.__name__ in self.inactive_pool:
                
                if game_object in self.inactive_pool[game_object.__class__.__name__]:
                    self.inactive_pool[game_object.__class__.__name__].remove(game_object)
            
        elif game_object.__class__.__name__ in self.active_pool:
            
            if game_object not in self.active_pool[game_object.__class__.__name__]:
                self.active_pool[game_object.__class__.__name__].append(game_object)

            if game_object.__class__.__name__ in self.inactive_pool:
                
                if game_object in self.inactive_pool[game_object.__class__.__name__]:
                    self.inactive_pool[game_object.__class__.__name__].remove(game_object)                
            
    # run update function for all game objects that are not background 
    def update_game_objects(self):

        if self.active_pool:

            # list of objects to remove
            to_remove = []
            
            # build list of objects to update
            to_update = [g for gameObjType, gameObjs in self.active_pool.items() for g in gameObjs]
            
            # # build list of objects to update
            # for gameObjType, gameObjs in self.active_pool.items():
            #     to_update.extend(gameObjs)
            
            # update game objects
            for gameObj in to_update:
                
                # if not in current chunk then move past it
                # if gameobj.__class__.__name__ != 'Player':
                #     continue
                                
                gameObj.update()
                    
                if not gameObj.is_active:
                    to_remove.append(gameObj)

            # remove inactive game objects
            if to_remove:
                for gameObj in to_remove:

                    if gameObj.__class__.__name__ in self.inactive_pool:
                        gameObj.kill(self.active_pool[gameObj.__class__.__name__],self.inactive_pool[gameObj.__class__.__name__])
                        
                        # if active pool empty then remove it, important for priority list which checks if a class is a key in the active pool
                        if not self.active_pool[gameObj.__class__.__name__]:
                            del self.active_pool[gameObj.__class__.__name__]

                    else:
                        self.active_pool[gameObj.__class__.__name__].remove(gameObj)
                        self.inactiveNoPool.append(gameObj)
                        
                        
                    # # check if a key is empty
                    # if not self.active_pool[gameObj.__class__.__name__]:
                    #     del self.active_pool[gameObj.__class__.__name__]
                        
    # run update function for all game objects that are not background 
    # def update_game_objects(self):

    #     if self.active_pool:

    #         to_remove = []

    #         for gameobj in self.active_pool:
                
    #             # if not in current chunk then move past it
    #             # if gameobj.__class__.__name__ != 'Player':
    #             #     continue
                
    #             gameobj.update()
                    
    #             if not gameobj.is_active:
    #                 to_remove.append(gameobj)

    #         if to_remove:
    #             for gameobj in to_remove:

    #                 if gameobj.__class__.__name__ in self.inactive_pool:
    #                     gameobj.kill(self.active_pool,self.inactive_pool[gameobj.__class__.__name__])

    #                 else:
    #                     self.active_pool.remove(gameobj)
    #                     self.inactiveNoPool.append(gameobj)

    # update background objs
    def update_background_objects(self):

        # go through each open chunk
        for chunk in tilemapProcessor.openChunks:

            toRemove = []
            
            # go through each bj object in 
            for bgobj in tilemapProcessor.chunkObj[chunk]:

                bgobj.update()

                # print(bgobj.hurtbox.center)

                if not bgobj.is_active:
                    toRemove.append(bgobj)

            # remove inactive objects
            if toRemove:
                for bgobj in toRemove:

                    tilemapProcessor.inactiveObjs.append(bgobj)
                    tilemapProcessor.chunkObj[chunk].remove(bgobj)

    # get all objects of a certain class from the active pool
    def query_active_pool(self,query_class:str):
        
        find_class_in_array(query_class,array=self.active_pool)
    
        
        

        
objectManager = ObjectSystem()
