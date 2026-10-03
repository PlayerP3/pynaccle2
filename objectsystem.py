import pygame,random,os,string,numpy,math,json,copy,ast
from .tilemap import tilemapProcessor
pygame.font.init()

class ObjectSystem():

    def __init__(self):

        # position of game objects
        self.object_positions = {}

        # get active pools
        self.active_pool = []
        self.inactive_pool = {}
        self.inactiveNoPool = []
        
        # store things killed in this frame
        

        # path cache for objs
        self.path_cache = {}

        # set player
        self.player = None
                
    # run update function for all game objects that are not background 
    def update_game_objects(self):

        if self.active_pool:

            to_remove = []

            for gameobj in self.active_pool:
                
                # if not in current chunk then move past it
                # if gameobj.__class__.__name__ != 'Player':
                #     continue
                
                gameobj.update()
                    
                if not gameobj.is_active:
                    to_remove.append(gameobj)

            if to_remove:
                for gameobj in to_remove:

                    if gameobj.__class__.__name__ in self.inactive_pool:
                        gameobj.kill(self.active_pool,self.inactive_pool[gameobj.__class__.__name__])

                    else:
                        self.active_pool.remove(gameobj)
                        self.inactiveNoPool.append(gameobj)

    # update background objs
    def update_background_objects(self):

        # go through each open chunk
        for chunk in tilemapProcessor.openChunks:

            toRemove = []
            
            # go through eahch bj object in 
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


    

        
objectManager = ObjectSystem()
